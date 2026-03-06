from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, DefaultDict, Dict, Iterable, List, Optional

from .models import Entity, EntityType, Event, EventType

EventListener = Callable[[Event], None]


@dataclass
class EntityRegistry:
    _entities: Dict[str, Entity] = field(default_factory=dict)
    _by_type: DefaultDict[EntityType, set[str]] = field(default_factory=lambda: defaultdict(set))

    def add(self, entity: Entity) -> None:
        if entity.entity_id in self._entities:
            raise ValueError(f"Entity already exists: {entity.entity_id}")
        self._entities[entity.entity_id] = entity
        self._by_type[entity.entity_type].add(entity.entity_id)

    def remove(self, entity_id: str) -> Optional[Entity]:
        entity = self._entities.pop(entity_id, None)
        if entity is None:
            return None
        self._by_type[entity.entity_type].discard(entity_id)
        return entity

    def get(self, entity_id: str) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def all(self) -> Iterable[Entity]:
        return self._entities.values()

    def by_type(self, entity_type: EntityType) -> List[Entity]:
        return [self._entities[eid] for eid in self._by_type.get(entity_type, set())]


@dataclass
class WorldState:
    width: int
    height: int
    tick: int = 0
    entities: EntityRegistry = field(default_factory=EntityRegistry)
    _event_queue: List[Event] = field(default_factory=list)
    _listeners: List[EventListener] = field(default_factory=list)

    def add_listener(self, listener: EventListener) -> None:
        self._listeners.append(listener)

    def emit(self, event: Event) -> None:
        self._event_queue.append(event)
        for listener in self._listeners:
            listener(event)

    def drain_events(self) -> List[Event]:
        events = list(self._event_queue)
        self._event_queue.clear()
        return events

    def add_entity(self, entity: Entity) -> None:
        self.entities.add(entity)
        self.emit(
            Event(
                event_type=EventType.ENTITY_ADDED,
                tick=self.tick,
                payload={"entity_id": entity.entity_id, "entity_type": entity.entity_type.value},
            )
        )

    def remove_entity(self, entity_id: str) -> Optional[Entity]:
        removed = self.entities.remove(entity_id)
        if removed:
            self.emit(
                Event(
                    event_type=EventType.ENTITY_REMOVED,
                    tick=self.tick,
                    payload={"entity_id": entity_id},
                )
            )
        return removed

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
