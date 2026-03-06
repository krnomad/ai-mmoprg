from __future__ import annotations

from ..models import Action, Event, EventType
from ..world import WorldState


def apply_movement(world: WorldState, action: Action) -> None:
    actor = world.entities.get(action.actor_id)
    if actor is None or action.destination is None:
        return

    old_position = actor.position
    actor.position = action.destination
    world.emit(
        Event(
            event_type=EventType.ENTITY_MOVED,
            tick=world.tick,
            payload={
                "entity_id": actor.entity_id,
                "from": old_position,
                "to": actor.position,
            },
        )
    )
