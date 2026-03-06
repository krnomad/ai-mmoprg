from __future__ import annotations

from .models import Action, ActionType
from .world import WorldState


def validate_action(world: WorldState, action: Action) -> tuple[bool, str | None]:
    actor = world.entities.get(action.actor_id)
    if actor is None:
        return False, "actor_not_found"
    if not actor.is_alive:
        return False, "actor_dead"

    if action.action_type == ActionType.MOVE:
        if action.destination is None:
            return False, "missing_destination"
        x, y = action.destination
        if not world.in_bounds(x, y):
            return False, "destination_out_of_bounds"
        return True, None

    if action.action_type == ActionType.ATTACK:
        if not action.target_id:
            return False, "missing_target"
        target = world.entities.get(action.target_id)
        if target is None:
            return False, "target_not_found"
        if not target.is_alive:
            return False, "target_dead"
        return True, None

    return False, "unsupported_action"
