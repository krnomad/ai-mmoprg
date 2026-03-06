# AI MMORPG Prototype Server

A simple **authoritative** WebSocket networking layer for prototype multiplayer gameplay.

## Features

- WebSocket-based communication
- Join-world flow (`join`)
- Player input handling (`input`) with server-side movement authority
- Delta-friendly events (`player_joined`, `player_moved`, `player_left`, `chat`) and periodic full snapshots (`snapshot`)
- Basic chat messages (`chat`)
- Simple connection/session handling with session IDs and idle timeout

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py --host 0.0.0.0 --port 8765
```

## Message protocol (JSON)

### Client -> Server

- `{"type":"join","name":"Alice"}`
- `{"type":"input","dx":1,"dy":0,"dt":0.1}`
- `{"type":"chat","text":"hello"}`
- `{"type":"ping","t":12345}`

### Server -> Client

- `welcome`
- `joined`
- `snapshot`
- `player_joined`
- `player_moved`
- `player_left`
- `chat`
- `error`
- `pong`

## Notes

- The server is authoritative over world state and position updates.
- Input values are clamped to avoid invalid movement bursts.
- World bounds are clamped to a small square (`-100..100`).
