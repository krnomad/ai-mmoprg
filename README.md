# AI MMORPG Prototype Observability

This repository now includes a lightweight observability module for simulation debugging:

- **Event log viewer** via `SimulationDebugger.view_event_log()`
- **Entity inspector** via `SimulationDebugger.inspect_entity()`
- **Recent action list** via `SimulationDebugger.recent_actions()`
- **Agent decision trace stub** via `SimulationDebugger.decision_trace_stub()`
- **Replay-ready event persistence interface** via `EventPersistence` with in-memory and JSONL implementations

## Quick use

```python
from observability import SimulationDebugger, JsonlEventStore

debugger = SimulationDebugger(JsonlEventStore("./debug/events.jsonl"))
debugger.record_action("agent-1", "move", to="(4,5)")
debugger.update_entity("npc-7", {"hp": 12, "x": 4, "y": 5})

print(debugger.view_event_log())
print(debugger.inspect_entity("npc-7"))
print(debugger.recent_actions(limit=5))
```
