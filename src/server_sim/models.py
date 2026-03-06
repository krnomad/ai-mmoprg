from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

Position = Tuple[int, int]


class EntityType(str, Enum):
    PLAYER = "player"
    MONSTER = "monster"


@dataclass(slots=True)
class Stats:
    max_hp: int
    attack: int
    defense: int


@dataclass(slots=True)
class Entity:
    entity_id: str
    entity_type: EntityType
    position: Position
    hp: int
    stats: Stats

    @property
    def is_alive(self) -> bool:
        return self.hp > 0


class EventType(str, Enum):
    ENTITY_ADDED = "entity_added"
    ENTITY_REMOVED = "entity_removed"
    ENTITY_MOVED = "entity_moved"
    DAMAGE_APPLIED = "damage_applied"
    ENTITY_DIED = "entity_died"
    ACTION_REJECTED = "action_rejected"
    TICK_COMPLETED = "tick_completed"


@dataclass(slots=True)
class Event:
    event_type: EventType
    tick: int
    payload: Dict[str, Any] = field(default_factory=dict)


class ActionType(str, Enum):
    MOVE = "move"
    ATTACK = "attack"


@dataclass(slots=True)
class Action:
    actor_id: str
    action_type: ActionType
    target_id: Optional[str] = None
    destination: Optional[Position] = None


@dataclass(slots=True)
class TickContext:
    tick: int
