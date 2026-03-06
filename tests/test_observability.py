import tempfile
import unittest

from observability import JsonlEventStore, SimulationDebugger


class ObservabilityTests(unittest.TestCase):
    def test_recent_actions_order(self):
        dbg = SimulationDebugger()
        dbg.record_action("a1", "move", to="x1")
        dbg.record_action("a1", "gather", resource="wood")

        recent = dbg.recent_actions(limit=2)

        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0].details["action"], "gather")
        self.assertEqual(recent[1].details["action"], "move")

    def test_entity_inspector(self):
        dbg = SimulationDebugger()
        dbg.update_entity("e1", {"hp": 10, "x": 2})

        self.assertEqual(dbg.inspect_entity("e1"), {"hp": 10, "x": 2})

    def test_jsonl_persistence_and_replay(self):
        with tempfile.TemporaryDirectory() as td:
            store = JsonlEventStore(f"{td}/events.jsonl")
            dbg = SimulationDebugger(store)
            dbg.record_action("a2", "attack", target="slime")
            dbg.update_entity("slime", {"hp": 2})

            replayed = list(dbg.replay_events())

            self.assertEqual(len(replayed), 2)
            self.assertEqual(replayed[0].event_type, "action")
            self.assertEqual(replayed[1].event_type, "entity_update")


if __name__ == "__main__":
    unittest.main()
