"""Prototype observability and debugging tools for a simulation.

This module intentionally stays lightweight and dependency-free. It provides:
- Event log viewer
- Entity inspector
- Recent action list
- Agent decision trace stub
- Replay-ready event persistence interface
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict, Iterable, List, Optional, Protocol


@dataclass
class SimulationEvent:
    """A normalized event emitted by the simulation."""

    timestamp: str
    event_type: str
    actor_id: Optional[str] = None
    entity_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def now(event_type: str, actor_id: Optional[str] = None, entity_id: Optional[str] = None, **details: Any) -> "SimulationEvent":
        return SimulationEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            actor_id=actor_id,
            entity_id=entity_id,
            details=details,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "entity_id": self.entity_id,
            "details": self.details,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SimulationEvent":
        return SimulationEvent(
            timestamp=data["timestamp"],
            event_type=data["event_type"],
            actor_id=data.get("actor_id"),
            entity_id=data.get("entity_id"),
            details=data.get("details", {}),
        )


class EventPersistence(Protocol):
    """Persistence interface for replay-ready event history."""

    def append(self, event: SimulationEvent) -> None:
        ...

    def load_all(self) -> List[SimulationEvent]:
        ...


class InMemoryEventStore:
    """Simple in-memory event persistence implementation."""

    def __init__(self) -> None:
        self._events: List[SimulationEvent] = []

    def append(self, event: SimulationEvent) -> None:
        self._events.append(event)

    def load_all(self) -> List[SimulationEvent]:
        return list(self._events)


class JsonlEventStore:
    """JSONL-backed event persistence for replay and debugging sessions."""

    def __init__(self, file_path: str | Path) -> None:
        self.path = Path(file_path)

    def append(self, event: SimulationEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    def load_all(self) -> List[SimulationEvent]:
        if not self.path.exists():
            return []
        events: List[SimulationEvent] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                events.append(SimulationEvent.from_dict(json.loads(line)))
        return events


class SimulationDebugger:
    """High-level observability helper for simulation state and activity."""

    def __init__(self, event_store: Optional[EventPersistence] = None) -> None:
        self.event_store: EventPersistence = event_store or InMemoryEventStore()
        self.entity_snapshots: Dict[str, Dict[str, Any]] = {}

    def record_event(self, event: SimulationEvent) -> None:
        self.event_store.append(event)

    def record_action(self, actor_id: str, action: str, target_entity_id: Optional[str] = None, **details: Any) -> None:
        event = SimulationEvent.now(
            event_type="action",
            actor_id=actor_id,
            entity_id=target_entity_id,
            action=action,
            **details,
        )
        self.record_event(event)

    def update_entity(self, entity_id: str, state: Dict[str, Any]) -> None:
        self.entity_snapshots[entity_id] = dict(state)
        self.record_event(SimulationEvent.now("entity_update", entity_id=entity_id, state=state))

    def inspect_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Entity inspector: return the latest known snapshot for an entity."""
        return self.entity_snapshots.get(entity_id)

    def recent_actions(self, limit: int = 20) -> List[SimulationEvent]:
        """Recent action list: return newest action events first."""
        actions = [e for e in self.event_store.load_all() if e.event_type == "action"]
        return list(reversed(actions[-limit:]))

    def view_event_log(self, limit: int = 200) -> List[str]:
        """Event log viewer: human-readable lines for recent events."""
        events = self.event_store.load_all()[-limit:]
        rendered: List[str] = []
        for ev in events:
            rendered.append(
                f"{ev.timestamp} | type={ev.event_type} actor={ev.actor_id or '-'} entity={ev.entity_id or '-'} details={ev.details}"
            )
        return rendered

    def decision_trace_stub(self, agent_id: str, context: Dict[str, Any], considered_actions: Iterable[str], selected_action: str) -> Dict[str, Any]:
        """Agent decision trace stub.

        This is intentionally minimal and not an explanation engine.
        """
        trace = {
            "agent_id": agent_id,
            "decision_time": datetime.now(timezone.utc).isoformat(),
            "context": context,
            "considered_actions": list(considered_actions),
            "selected_action": selected_action,
            "notes": "prototype decision trace stub",
        }
        self.record_event(SimulationEvent.now("decision_trace", actor_id=agent_id, trace=trace))
        return trace

    def replay_events(self) -> Iterable[SimulationEvent]:
        """Replay-ready stream for driving simulation reconstruction."""
        for event in self.event_store.load_all():
            yield event
