import unittest

from agent_runtime import (
    ActionSpec,
    ActionType,
    AgentKind,
    AgentPerception,
    AgentScheduler,
    PerceivedEntity,
    PlayerMirrorPolicy,
    RuntimeAgent,
    VillagerRoutinePolicy,
    MonsterAggroPolicy,
)


class AgentRuntimeTests(unittest.TestCase):
    def test_scheduler_is_deterministic_and_non_mutating(self):
        scheduler = AgentScheduler(think_interval_ticks=2)
        agent = RuntimeAgent(
            agent_id="npc1",
            kind=AgentKind.NPC,
            action_spec=ActionSpec((ActionType.MOVE, ActionType.WAIT)),
            policy=VillagerRoutinePolicy(),
        )
        scheduler.register(agent)
        perception = AgentPerception(
            tick=1,
            self_id="npc1",
            self_kind=AgentKind.NPC,
            self_position=(0, 0),
            self_hp=10,
            self_max_hp=10,
        )

        # Tick 1 skipped because interval=2
        r1 = scheduler.run_tick(1, {"npc1": perception})
        self.assertEqual({}, r1.decisions)

        # Tick 2 processed and outputs allowed action only
        r2 = scheduler.run_tick(
            2,
            {
                "npc1": AgentPerception(
                    tick=2,
                    self_id="npc1",
                    self_kind=AgentKind.NPC,
                    self_position=(0, 0),
                    self_hp=10,
                    self_max_hp=10,
                )
            },
        )
        self.assertIn("npc1", r2.decisions)
        self.assertEqual(ActionType.MOVE, r2.decisions["npc1"].action.action_type)

    def test_monster_attacks_non_monster(self):
        monster = RuntimeAgent(
            agent_id="m1",
            kind=AgentKind.NPC,
            action_spec=ActionSpec((ActionType.ATTACK, ActionType.MOVE, ActionType.WAIT)),
            policy=MonsterAggroPolicy(),
        )
        p = AgentPerception(
            tick=10,
            self_id="m1",
            self_kind=AgentKind.NPC,
            self_position=(1, 1),
            self_hp=8,
            self_max_hp=8,
            nearby_entities=(
                PerceivedEntity("p1", "players", (2, 1), 10, 10, ("player",)),
                PerceivedEntity("m2", "monsters", (1, 2), 8, 8, ("monster",)),
            ),
        )
        d = monster.think(p)
        self.assertEqual(ActionType.ATTACK, d.action.action_type)
        self.assertEqual("p1", d.action.target_id)

    def test_player_policy_filters_to_allowed_actions(self):
        player = RuntimeAgent(
            agent_id="player1",
            kind=AgentKind.PLAYER,
            action_spec=ActionSpec((ActionType.MOVE, ActionType.WAIT)),
            policy=PlayerMirrorPolicy(),
        )
        p = AgentPerception(
            tick=3,
            self_id="player1",
            self_kind=AgentKind.PLAYER,
            self_position=(0, 0),
            self_hp=10,
            self_max_hp=10,
            map_notes={"requested_action": "attack", "target_id": "x"},
        )
        d = player.think(p)
        self.assertEqual(ActionType.WAIT, d.action.action_type)


if __name__ == "__main__":
    unittest.main()
