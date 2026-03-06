from __future__ import annotations

from typing import Iterable, List

from .models import Action, ActionType, Event, EventType
from .systems.ai import plan_monster_actions
from .systems.combat import apply_attack
from .systems.movement import apply_movement
from .validation import validate_action
from .world import WorldState


class TickRunner:
    def __init__(self, world: WorldState):
        self.world = world

    def run_tick(self, player_actions: Iterable[Action] = ()) -> List[Event]:
        self.world.tick += 1
        queued_actions: List[Action] = [*player_actions, *plan_monster_actions(self.world)]

        for action in queued_actions:
            valid, reason = validate_action(self.world, action)
            if not valid:
                self.world.emit(
                    Event(
                        event_type=EventType.ACTION_REJECTED,
                        tick=self.world.tick,
                        payload={
                            "actor_id": action.actor_id,
                            "action_type": action.action_type.value,
                            "reason": reason,
                        },
                    )
                )
                continue

            if action.action_type == ActionType.MOVE:
                apply_movement(self.world, action)
            elif action.action_type == ActionType.ATTACK:
                apply_attack(self.world, action)

        self.world.emit(Event(event_type=EventType.TICK_COMPLETED, tick=self.world.tick, payload={}))
        return self.world.drain_events()
