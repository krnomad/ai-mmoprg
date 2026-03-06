from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "src")

from server_sim import Action, ActionType, Entity, EntityType, Stats, TickRunner, WorldState


class SimulationCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.world = WorldState(width=10, height=10)
        self.runner = TickRunner(self.world)

        self.player = Entity(
            entity_id="player-1",
            entity_type=EntityType.PLAYER,
            position=(1, 1),
            hp=20,
            stats=Stats(max_hp=20, attack=5, defense=1),
        )
        self.monster = Entity(
            entity_id="monster-1",
            entity_type=EntityType.MONSTER,
            position=(2, 1),
            hp=10,
            stats=Stats(max_hp=10, attack=3, defense=0),
        )
        self.world.add_entity(self.player)
        self.world.add_entity(self.monster)
        self.world.drain_events()

    def test_move_action_updates_position_and_emits_event(self) -> None:
        events = self.runner.run_tick(
            [Action(actor_id="player-1", action_type=ActionType.MOVE, destination=(1, 2))]
        )

        self.assertEqual((1, 2), self.player.position)
        self.assertTrue(any(e.event_type.value == "entity_moved" for e in events))

    def test_attack_action_applies_damage_and_monster_ai_attacks_adjacent_player(self) -> None:
        events = self.runner.run_tick(
            [Action(actor_id="player-1", action_type=ActionType.ATTACK, target_id="monster-1")]
        )

        self.assertLess(self.monster.hp, 10)
        self.assertLess(self.player.hp, 20)
        self.assertTrue(any(e.event_type.value == "damage_applied" for e in events))

    def test_invalid_action_is_rejected(self) -> None:
        events = self.runner.run_tick(
            [Action(actor_id="player-1", action_type=ActionType.MOVE, destination=(99, 99))]
        )

        rejected = [e for e in events if e.event_type.value == "action_rejected"]
        self.assertEqual(1, len(rejected))
        self.assertEqual("destination_out_of_bounds", rejected[0].payload["reason"])


if __name__ == "__main__":
    unittest.main()
