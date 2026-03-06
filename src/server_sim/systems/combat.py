from __future__ import annotations

from ..models import Action, Event, EventType
from ..world import WorldState


def apply_attack(world: WorldState, action: Action) -> None:
    attacker = world.entities.get(action.actor_id)
    target = world.entities.get(action.target_id or "")
    if attacker is None or target is None:
        return

    raw_damage = attacker.stats.attack - target.stats.defense
    damage = max(1, raw_damage)
    target.hp = max(0, target.hp - damage)

    world.emit(
        Event(
            event_type=EventType.DAMAGE_APPLIED,
            tick=world.tick,
            payload={
                "attacker_id": attacker.entity_id,
                "target_id": target.entity_id,
                "damage": damage,
                "target_hp": target.hp,
            },
        )
    )

    if not target.is_alive:
        world.emit(
            Event(
                event_type=EventType.ENTITY_DIED,
                tick=world.tick,
                payload={"entity_id": target.entity_id},
            )
        )
