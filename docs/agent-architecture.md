# Agent Architecture (Vertical Slice)

This document proposes a practical layered architecture for two game agent classes:

1. **User-owned player agents** (companions, helpers, autopilot characters)
2. **Admin-owned NPC agents** (shopkeepers, quest givers, guards, ambient world actors)

It is optimized for a first vertical slice where reliability, abuse prevention, and cost control matter more than maximum intelligence.

---

## 1) Core Layered Model (shared)

All agents use four layers. Keep each layer independently testable.

## Reactive layer (fast, deterministic)

**Purpose**
- Handle immediate safety and gameplay-critical responses.
- Execute low-latency event-response rules.

**Examples**
- Stop movement on collision.
- Evade hazard tile.
- Auto-retaliate if in combat mode.
- Reject impossible actions (no stamina, out of range).

**Tick cadence**
- **Every tick** (or every simulation frame group, e.g. 5–10 Hz).

**Implementation style**
- Deterministic finite-state or behavior rules.
- No LLM required.

---

## Goal layer (planner/executor)

**Purpose**
- Maintain short-horizon intent and task queues.
- Decompose goals into deterministic actions.

**Examples**
- “Gather 10 wood” => pathfind -> harvest loop -> return.
- “Patrol zone A/B/C” => route + watch points.

**Tick cadence**
- **Frequent but not every tick** (e.g. 1–2 Hz).
- Replan only on trigger events (task complete, blocked path, threat change).

**Implementation style**
- Primarily deterministic utility scoring + HTN/GOAP-lite.
- Optional LLM usage for rare task synthesis (“convert player request to task graph”).

---

## Social/dialogue layer

**Purpose**
- Interpret and generate conversational behavior.
- Choose dialogue acts (inform, ask, refuse, emote, trade prompt).

**Examples**
- NPC quest dialogue branching.
- Player-agent natural language command interpretation.
- Relationship-sensitive tone.

**Tick cadence**
- **Event-driven / occasional**.
- Triggered on chat input, proximity interaction, scripted scene events.

**Implementation style**
- Deterministic dialogue trees/templates for common paths.
- LLM only for low-risk “flavor” generation or intent extraction fallback.

---

## Memory layer

**Purpose**
- Store short-term working context + long-term facts.
- Provide filtered context back to other layers.

**Memory types**
- **Working memory** (current target, last attacker, current conversation thread).
- **Episodic summary** (recent events summary every N minutes).
- **Semantic profile** (faction, preferences, role constraints).

**Tick cadence**
- Writes on significant events.
- Compaction/summarization **occasionally** (e.g. every 2–5 minutes or session end).

**Implementation style**
- Deterministic schema + retention policy.
- Optional LLM summarization at coarse intervals only.

---

## 2) Design A: User-owned Player Agents

These agents are controlled by user policy, but must never bypass core game fairness.

## Layer responsibilities

### Reactive layer (player agents)
- Enforce player-mode policy (aggressive/passive/follow-only).
- Resolve immediate combat and movement safety.
- Respect hard constraints: inventory capacity, stamina, map access, PVP flags.

### Goal layer (player agents)
- Execute owner-assigned task queue (“follow me”, “gather iron in zone X”).
- Handle interruption priorities:
  1. survival
  2. owner direct command
  3. active task
- Maintain bounded autonomy window (e.g. max roam radius or max unsupervised minutes).

### Social/dialogue layer (player agents)
- Parse owner commands (slash commands first, NL optional).
- Reply with short status summaries (“I can’t mine there; area is restricted”).
- Ignore or rate-limit commands from non-owner players unless explicitly shared.

### Memory layer (player agents)
- Track owner preferences (loot filters, combat stance).
- Track “recently failed actions” to avoid loops.
- Session memory default; longer retention opt-in by owner.

## Tick vs occasional

**Every tick**
- Threat checks, collision/safety, cooldown gating, action legality.

**1–2 Hz**
- Goal progress checks, target selection, path correction.

**Occasional/event**
- NL command parse, recap messages, memory summarization.

## Deterministic vs LLM

**Deterministic is enough for vertical slice**
- Navigation, combat rotation, harvesting loops, legality checks.
- Owner command grammar via strict command parser (`/agent gather iron`).

**LLM useful later / optional now**
- Fuzzy natural language to command translation.
- Friendly conversational responses.
- Summarizing long event history for owner.

## Perception limits

- Limit sensing to same rules as normal players (line-of-sight, fog-of-war, range).
- No hidden metadata exposure (true HP of unseen targets, spawn timers, invisible entities).
- Event bus should deliver only permitted observation objects by ownership and visibility.

## Action API boundaries

Provide a narrow server-side API, e.g.:
- `move_to(nav_target)`
- `interact(entity_id, action_type)`
- `use_ability(slot, target_id?)`
- `set_mode(mode_enum)`
- `send_owner_message(text_template_id, vars)`

**Do not expose raw DB/world mutation calls.**
All requests pass through standard gameplay validators and cooldown gates.

## Cooldowns and anti-abuse

- Per-action cooldowns (same as players).
- Global “decision cooldown” (e.g. cannot retarget >2/sec).
- Command spam limit from owner chat (e.g. 6 commands / 10 sec).
- Anti-bot parity: player agents obey same economy caps, AFK rules, and market limits.
- Auto-disable on repeated policy violations or stuck loops.

## Cost-control strategies

- Default to deterministic command mode for vertical slice.
- LLM off by default; enable only for explicit “chatty mode”.
- Cache command interpretations for repeated owner phrases.
- Hard token budget per agent/day.
- Batch summarization and truncate context to structured memory slots.

---

## 3) Design B: Admin-owned NPC Agents

These agents create world believability and live operations flexibility, while staying lore-safe.

## Layer responsibilities

### Reactive layer (NPC agents)
- Immediate world reactions: flee, call guards, resume post.
- Enforce invulnerability/authority flags where needed (e.g. quest giver cannot be grief-locked).

### Goal layer (NPC agents)
- Execute role schedule/state machine:
  - shopkeeper: open/close/shop emotes
  - guard: patrol/investigate/chase boundary
  - villager: day-night routines
- Handle dynamic live-ops directives (“festival mode”).

### Social/dialogue layer (NPC agents)
- Primary path: authored dialogue trees + stateful variables.
- Secondary path: templated dynamic barks using tags (weather, local threat).
- Optional LLM for non-critical ambient chatter with strict guardrails.

### Memory layer (NPC agents)
- Store world-facing state (who recently stole, who has active quest stage).
- Keep per-player interaction notes where gameplay-relevant.
- Periodically snapshot to support shard restarts.

## Tick vs occasional

**Every tick**
- Safety/post constraints, combat interrupts, scripted trigger checks.

**0.5–1 Hz**
- Routine progression, patrol node updates, utility arbitration.

**Event-driven/occasional**
- Dialogue generation, ambient bark selection, memory summarization.

## Deterministic vs LLM

**Deterministic is enough for vertical slice**
- All quest-critical dialogue.
- Patrol/guard/shop behaviors.
- Reward and state transitions.

**LLM useful later / optional now**
- Flavor-only ambient lines.
- GM tools: “generate 5 lore-consistent bark variants”.

## Perception limits

- NPC perception tied to configured senses (radius, LOS, hearing).
- No global omniscience by default, except explicit admin-role NPCs.
- Investigation uses sensed evidence, not hidden engine truth, unless gameplay requires.

## Action API boundaries

NPC action API similar to player agents plus controlled admin hooks:
- `move_to`, `interact`, `speak_template`, `start_dialogue_node`
- `set_world_state_flag` only through whitelisted script actions
- `emit_event(topic, payload)` for quest systems

All world-changing actions should be auditable and permission-scoped.

## Cooldowns and anti-abuse

- Dialogue initiation cooldown per player/NPC pair.
- Trade/shop open attempts rate-limited.
- Guard chase timeout to prevent map-wide grief chains.
- LLM-generated text must pass profanity/lore/policy filter and max-length checks.

## Cost-control strategies

- Prefer authored templates and parameterized barks.
- Precompute daily schedule transitions.
- Use shard-level cache for common NPC utterances.
- Centralize any LLM calls through a queue with per-shard budget caps.

---

## 4) First Vertical Slice (recommended)

Build only what proves architecture viability:

1. **Player agent v0**
   - Deterministic command set: follow, gather, defend, stop.
   - No free-form LLM required.
   - Basic memory: owner preferences + failure backoff.

2. **NPC agent v0**
   - One guard NPC + one shopkeeper NPC.
   - Authored dialogue tree only.
   - Patrol + investigate behavior with strict boundaries.

3. **Shared infra v0**
   - Unified perception filter service.
   - Unified action validator + cooldown service.
   - Agent telemetry: tick time, action rejects, stuck count, LLM spend.

4. **Safety gates v0**
   - Per-agent and per-shard call budgets.
   - Circuit breaker: if LLM latency/error spikes, degrade to deterministic templates.

---

## 5) Minimal Runtime Topology

- **Simulation thread/process**: reactive layer + action execution.
- **Agent logic worker**: goal updates at lower frequency.
- **Dialogue worker**: event-driven, can call LLM gateway.
- **Memory service**: structured store + summarization jobs.
- **Policy gateway**: validates permissions, cooldowns, anti-abuse.

Keep cross-service contracts explicit and versioned (JSON schema/protobuf). For vertical slice, these can still run in one process with logical module boundaries.

---

## 6) Practical Defaults (copy/paste)

- Tick rate: simulation 10 Hz, goal update 1 Hz.
- Max perceived entities per agent tick: 32 nearest relevant.
- Max queued goals: 5.
- Repath cooldown: 1.5s.
- Retarget cooldown: 0.5s.
- Dialogue reply cooldown: 2s.
- LLM budget (if enabled):
  - player agent: 20 calls/day
  - NPC ambient: 200 calls/shard/day
- Memory summarization: every 3 minutes or 30 events.
- Fallback mode on budget exhaustion: deterministic templates only.

These defaults are intentionally conservative to ship a stable first slice.
