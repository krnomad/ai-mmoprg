#!/usr/bin/env python3
"""Prototype authoritative MMORPG server networking layer.

Features:
- WebSocket transport
- Join world flow
- Authoritative player movement input handling
- Delta-friendly broadcast events + periodic snapshots
- Basic chat
- Simple connection/session handling
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed

TICK_RATE_HZ = 10
MAX_NAME_LENGTH = 24
MAX_CHAT_LENGTH = 256
MAX_INPUT_MAGNITUDE = 1.0
SPEED_UNITS_PER_SEC = 6.0
WORLD_BOUNDS = (-100.0, 100.0)
SESSION_IDLE_TIMEOUT_S = 45


@dataclass
class Player:
    player_id: str
    name: str
    session_id: str
    x: float = 0.0
    y: float = 0.0


@dataclass
class Session:
    session_id: str
    ws: ServerConnection
    player_id: str | None = None
    last_seen: float = field(default_factory=time.time)


class WorldServer:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._players: dict[str, Player] = {}
        self._lock = asyncio.Lock()

    async def run(self, host: str, port: int) -> None:
        async with serve(self._on_connection, host, port, ping_interval=20, ping_timeout=20):
            logging.info("WebSocket server listening at ws://%s:%s", host, port)
            await asyncio.gather(self._snapshot_loop(), self._reap_idle_sessions_loop())

    async def _on_connection(self, ws: ServerConnection) -> None:
        session = Session(session_id=secrets.token_hex(8), ws=ws)
        async with self._lock:
            self._sessions[session.session_id] = session

        await self._send(
            ws,
            {
                "type": "welcome",
                "session_id": session.session_id,
                "message": "Connected. Send {'type':'join','name':'...'} to enter the world.",
            },
        )

        try:
            async for raw_message in ws:
                try:
                    payload = json.loads(raw_message)
                except json.JSONDecodeError:
                    await self._send_error(ws, "invalid_json", "Expected JSON message")
                    continue
                session.last_seen = time.time()
                await self._handle_message(session, payload)
        except ConnectionClosed:
            pass
        finally:
            await self._disconnect(session.session_id)

    async def _handle_message(self, session: Session, payload: dict[str, Any]) -> None:
        message_type = payload.get("type")
        if message_type == "join":
            await self._handle_join(session, payload)
        elif message_type == "input":
            await self._handle_input(session, payload)
        elif message_type == "chat":
            await self._handle_chat(session, payload)
        elif message_type == "ping":
            await self._send(session.ws, {"type": "pong", "t": payload.get("t")})
        else:
            await self._send_error(session.ws, "unknown_type", "Unsupported message type")

    async def _handle_join(self, session: Session, payload: dict[str, Any]) -> None:
        raw_name = str(payload.get("name", "")).strip()
        if not raw_name:
            await self._send_error(session.ws, "bad_name", "Name is required")
            return

        name = raw_name[:MAX_NAME_LENGTH]

        async with self._lock:
            if session.player_id:
                await self._send_error(session.ws, "already_joined", "Session already joined")
                return

            player_id = f"p_{secrets.token_hex(4)}"
            player = Player(player_id=player_id, name=name, session_id=session.session_id)
            self._players[player_id] = player
            session.player_id = player_id

            snapshot = self._build_snapshot()

        await self._send(
            session.ws,
            {
                "type": "joined",
                "player_id": player_id,
                "snapshot": snapshot,
            },
        )
        await self._broadcast(
            {
                "type": "player_joined",
                "player": self._serialize_player(player),
            },
            exclude_session_id=session.session_id,
        )

    async def _handle_input(self, session: Session, payload: dict[str, Any]) -> None:
        if not session.player_id:
            await self._send_error(session.ws, "not_joined", "Join first")
            return

        try:
            dx = float(payload.get("dx", 0.0))
            dy = float(payload.get("dy", 0.0))
            dt = float(payload.get("dt", 0.1))
        except (TypeError, ValueError):
            await self._send_error(session.ws, "bad_input", "dx, dy, dt must be numbers")
            return

        dx = max(-MAX_INPUT_MAGNITUDE, min(MAX_INPUT_MAGNITUDE, dx))
        dy = max(-MAX_INPUT_MAGNITUDE, min(MAX_INPUT_MAGNITUDE, dy))
        dt = max(0.0, min(0.25, dt))

        async with self._lock:
            player = self._players.get(session.player_id)
            if not player:
                return
            player.x = self._clamp_to_world(player.x + dx * SPEED_UNITS_PER_SEC * dt)
            player.y = self._clamp_to_world(player.y + dy * SPEED_UNITS_PER_SEC * dt)
            updated = self._serialize_player(player)

        await self._broadcast(
            {
                "type": "player_moved",
                "player": updated,
            }
        )

    async def _handle_chat(self, session: Session, payload: dict[str, Any]) -> None:
        if not session.player_id:
            await self._send_error(session.ws, "not_joined", "Join first")
            return

        text = str(payload.get("text", "")).strip()
        if not text:
            return

        text = text[:MAX_CHAT_LENGTH]

        async with self._lock:
            player = self._players.get(session.player_id)
            if not player:
                return
            chat_event = {
                "type": "chat",
                "from": {
                    "player_id": player.player_id,
                    "name": player.name,
                },
                "text": text,
                "ts": int(time.time() * 1000),
            }

        await self._broadcast(chat_event)

    async def _disconnect(self, session_id: str) -> None:
        async with self._lock:
            session = self._sessions.pop(session_id, None)
            if not session:
                return

            player = None
            if session.player_id:
                player = self._players.pop(session.player_id, None)

        if player:
            await self._broadcast(
                {
                    "type": "player_left",
                    "player_id": player.player_id,
                }
            )

    async def _snapshot_loop(self) -> None:
        tick_interval = 1 / TICK_RATE_HZ
        while True:
            await asyncio.sleep(tick_interval)
            async with self._lock:
                snapshot = self._build_snapshot()
            await self._broadcast({"type": "snapshot", "snapshot": snapshot})

    async def _reap_idle_sessions_loop(self) -> None:
        while True:
            await asyncio.sleep(5)
            now = time.time()
            stale_session_ids: list[str] = []

            async with self._lock:
                for session_id, session in self._sessions.items():
                    if now - session.last_seen > SESSION_IDLE_TIMEOUT_S:
                        stale_session_ids.append(session_id)

            for session_id in stale_session_ids:
                session = self._sessions.get(session_id)
                if session:
                    await session.ws.close(code=4000, reason="Session timeout")

    async def _broadcast(self, payload: dict[str, Any], exclude_session_id: str | None = None) -> None:
        encoded = json.dumps(payload)

        async with self._lock:
            sessions = list(self._sessions.values())

        send_tasks = []
        for session in sessions:
            if exclude_session_id and session.session_id == exclude_session_id:
                continue
            send_tasks.append(self._safe_send(session.ws, encoded))

        if send_tasks:
            await asyncio.gather(*send_tasks)

    async def _send(self, ws: ServerConnection, payload: dict[str, Any]) -> None:
        await self._safe_send(ws, json.dumps(payload))

    async def _safe_send(self, ws: ServerConnection, encoded_payload: str) -> None:
        try:
            await ws.send(encoded_payload)
        except ConnectionClosed:
            # Connection cleanup happens in _on_connection finally block.
            return

    async def _send_error(self, ws: ServerConnection, code: str, message: str) -> None:
        await self._send(
            ws,
            {
                "type": "error",
                "code": code,
                "message": message,
            },
        )

    def _serialize_player(self, player: Player) -> dict[str, Any]:
        return {
            "player_id": player.player_id,
            "name": player.name,
            "x": round(player.x, 3),
            "y": round(player.y, 3),
        }

    def _build_snapshot(self) -> dict[str, Any]:
        return {
            "players": [self._serialize_player(player) for player in self._players.values()],
            "server_time_ms": int(time.time() * 1000),
        }

    @staticmethod
    def _clamp_to_world(value: float) -> float:
        return max(WORLD_BOUNDS[0], min(WORLD_BOUNDS[1], value))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Authoritative prototype MMORPG WebSocket server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    server = WorldServer()
    await server.run(args.host, args.port)


if __name__ == "__main__":
    asyncio.run(main())
