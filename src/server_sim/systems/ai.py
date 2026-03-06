from __future__ import annotations

from typing import List

from ..models import Action, ActionType, EntityType
from ..world import WorldState


def plan_monster_actions(world: WorldState) -> List[Action]:
    """Very small AI stub.

    Current behavior:
    - If a monster is adjacent to any player, attack the first one.
    - Otherwise, do nothing.
    """
    actions: List[Action] = []
    players = [p for p in world.entities.by_type(EntityType.PLAYER) if p.is_alive]
    if not players:
        return actions

    for monster in world.entities.by_type(EntityType.MONSTER):
        if not monster.is_alive:
            continue
        for player in players:
            mx, my = monster.position
            px, py = player.position
            manhattan = abs(mx - px) + abs(my - py)
            if manhattan == 1:
                actions.append(
                    Action(
                        actor_id=monster.entity_id,
                        action_type=ActionType.ATTACK,
                        target_id=player.entity_id,
                    )
                )
                break
    return actions
