# Technical Architecture for the Approved Vertical Slice

## 1) High-level system architecture

```text
┌────────────────────────────────────────────────────────────────────┐
│                         Browser Client (Web)                       │
│  Rendering/UI • Input • Prediction hints • Timeline/debug overlay  │
└───────────────────────────────┬────────────────────────────────────┘
                                │ WebSocket (real-time), HTTPS (REST)
┌───────────────────────────────▼────────────────────────────────────┐
│                   Game Server (Authoritative Core)                 │
│  Session manager • Tick scheduler • Deterministic simulation       │
│  Interest management • Validation • State snapshots/deltas         │
│  Event log writer • Replay hooks • Metrics/tracing emitters        │
└───────────────┬───────────────────────────────┬────────────────────┘
                │                               │
        Async task queue / pub-sub              │
                │                               │
┌───────────────▼──────────────┐      ┌────────▼─────────────────────┐
│      Agent Runtime Service    │      │      Admin / Dev Tools      │
│  LLM planning + tool policies │      │  GM console • Replay viewer │
│  Receives sanitized world     │      │  Tick inspector • Rule tools │
│  observations and sends       │      │  Ops dashboards              │
│  bounded intents/actions      │      └────────┬─────────────────────┘
└───────────────┬──────────────┘               │
                │                              │
                └───────────────┬──────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Storage / Telemetry │
                    │ PostgreSQL • Redis    │
                    │ Object storage logs   │
                    └───────────────────────┘
```

### Why this shape
- **Server-authoritative simulation** is preserved by making the simulation loop fully server-local and deterministic.
- **Browser-playable first** is supported with a lightweight web client over WebSocket/HTTPS.
- **Agent reasoning is separated** by isolating LLM planning in its own runtime service and allowing only intent-level communication.
- **Small-team practicality**: monorepo + modular services; start as one deployable backend process plus one agent worker process.

### Tradeoffs
- Splitting agent runtime from game server adds operational complexity, but strongly improves safety and debugability.
- Deterministic server simulation constrains implementation choices (e.g., fixed-step math), but pays off in replay and bug reproduction.

---

## 2) Responsibilities by component

## Client (browser)
- Render world state, entities, and UI.
- Collect player input and send **commands** (not state mutations).
- Interpolate/extrapolate visuals between authoritative updates.
- Provide debug overlays in dev mode (tick, RTT, reconciliation count).
- Cache only ephemeral session data.

**Not responsible for:** final hit resolution, economy balance, AI decisions, anti-cheat trust.

## Server (authoritative simulation)
- Own canonical world state and run fixed simulation ticks.
- Validate player commands and agent intents against game rules.
- Resolve physics/combat/interactions deterministically.
- Broadcast state deltas/events to clients.
- Record event logs and snapshot checkpoints for replay.
- Expose admin endpoints guarded by RBAC.

## Agent runtime
- Transform world observations + goals into candidate intents.
- Run tool-using reasoning, memory retrieval, and behavior policies.
- Return **bounded intents** (e.g., `MoveTo`, `UseAbility(slot=2,target=E17)`) with confidence/metadata.
- Enforce content/safety policies before sending intents upstream.

**Critical boundary:** runtime never mutates world state directly.

## Admin tools
- Live server dashboard: tick rate, lag, entity counts, queue depth.
- Replay viewer: step through ticks/events and inspect diffs.
- GM tools: spawn NPCs, force events, run scripted test scenarios.
- Configuration tools: tune rules via versioned config assets.

### Tradeoffs
- Putting rich debug tools in scope early costs time, but drastically shortens iteration and balancing cycles for small teams.

---

## 3) Networking model

## Protocols
- **WebSocket** for low-latency bidirectional gameplay stream.
- **HTTPS REST** for auth, matchmaking/session bootstrap, admin APIs.
- **Internal queue/pub-sub** (Redis streams/NATS-like abstraction) between server and agent runtime.

## Connection flow
1. Client authenticates via HTTPS.
2. Client receives session token + shard endpoint.
3. Client opens WebSocket and subscribes to its interest channels.
4. Server sends initial snapshot + current tick id.

## Message classes
- `ClientCommand`: player intent (`move`, `interact`, `chat`).
- `ServerDelta`: compact state delta from tick `T`→`T+1`.
- `ServerEvent`: discrete event (damage, loot drop, quest state change).
- `AgentObservation`: filtered world context for runtime.
- `AgentIntent`: structured action proposal from runtime.

## Reliability model
- Commands use sequence ids + ack.
- Deltas may be dropped if superseded; periodic keyframe snapshots heal drift.
- Critical events (inventory/economy) are idempotent and persisted before ack.

### Tradeoffs
- WebSocket is simple and browser-native, though less optimized than UDP-based custom protocols for twitch gameplay.

---

## 4) Simulation tick model

## Core model
- Fixed-step authoritative loop, e.g. **10–20 Hz** for prototype (50–100 ms tick).
- Single-writer world mutation per shard/process.
- Tick phases:
  1. Drain inbound command queues up to cutoff.
  2. Validate and enqueue accepted intents.
  3. Run deterministic systems in strict order.
  4. Emit events/deltas.
  5. Persist log + optional checkpoint.

## Determinism controls
- Seeded RNG per match/shard and tick-scoped substreams.
- Stable iteration order (entity ids sorted/partitioned deterministically).
- Avoid non-deterministic wall-clock calls inside simulation.

## Backpressure strategy
- If overloaded: cap per-tick command processing and degrade gracefully (late command for next tick).
- Maintain simulation time integrity; avoid variable timestep physics.

### Tradeoffs
- Lower tick rates are easier for a small team and reduce cost, but increase input-to-action latency.

---

## 5) Event/message flow

## Player action flow
1. Player clicks action in browser.
2. Client sends `ClientCommand(seq, tick_hint, payload)`.
3. Server validates schema/auth/rules.
4. On tick `T`, command is applied.
5. Server emits resulting `ServerEvent` + `ServerDelta`.
6. Client reconciles local prediction with authoritative state.

## Agent action flow
1. Server assembles `AgentObservation` from filtered state (no hidden internals unless allowed).
2. Observation published to agent runtime.
3. Runtime reasons and returns `AgentIntent`.
4. Server validates intent identically to player commands.
5. Intent applied on next eligible tick.

## Admin intervention flow
1. Admin sends tool command through secure API.
2. Server marks source as `admin` and applies policy checks.
3. Action recorded in immutable audit log and replay stream.

### Tradeoffs
- Unified validation path for players and agents reduces special-case bugs, at the cost of stricter adapter design for agent outputs.

---

## 6) Storage strategy (prototype vs MVP)

## Prototype
- **PostgreSQL**: accounts, session metadata, durable economy tables, config versions.
- **Redis**: ephemeral session presence, rate-limit counters, transient queues.
- **Object storage (or local files in dev)**: compressed event logs + periodic snapshots.

Use append-only event records for gameplay-critical transitions where possible.

## MVP evolution
- Partition event logs by shard/day.
- Add materialized read models for analytics dashboards.
- Introduce online schema versioning for events (`event_type`, `version`, `payload`).
- Move long-lived replay data to cheaper cold storage lifecycle tiers.

### Tradeoffs
- Event logging increases write volume, but enables replay/debug and future analytics without re-instrumenting core systems.

---

## 7) Replay and observability design

## Replay
- Record:
  - inbound commands/intents with sequence ids,
  - RNG seeds,
  - system outputs/events,
  - periodic world checkpoints (e.g., every N ticks).
- Replay modes:
  - **Deterministic re-sim** from checkpoint + command stream,
  - **Fast-forward event playback** for support/debug timelines.

## Observability
- Structured logs with correlation ids (`session_id`, `tick_id`, `entity_id`).
- Metrics: tick duration p50/p95, queue lag, command reject rate, ws fanout size.
- Distributed traces spanning client command → server tick → agent inference → server apply.
- “Black box” capture toggle for problematic sessions.

### Debug-first defaults
- Every authoritative decision should be attributable to one tick and one input record.
- Build a tick inspector UI early to diff entity state between ticks.

### Tradeoffs
- Strong observability adds upfront instrumentation work, but pays for itself quickly in live-ops and balancing.

---

## 8) Safety boundaries between agents and game state

## Hard boundaries
- Agent runtime has **no DB write credentials** for core world state.
- Agent API contract allows only typed intents from a strict schema.
- Server performs complete re-validation (cooldowns, LOS, economy rules, permissions).
- Rate limits and budget caps per agent/entity.

## Data minimization
- Observation payloads are filtered by role/team/fog-of-war policies.
- Sensitive internals (hidden player data, moderation flags, exploit heuristics) are excluded unless necessary.

## Execution safety
- Timeouts for agent responses (fallback behavior if missed window).
- Circuit breaker: if runtime degraded, NPCs switch to deterministic fallback behavior tree.
- Policy firewall checks text/tool outputs before intent translation.

## Audit and governance
- Every accepted/rejected agent intent stored with policy reason.
- Version pinning for model, prompt, and tool policy bundles per session.
- Rollback switches for bad agent behavior deployments.

### Tradeoffs
- Strict boundaries may reduce peak agent creativity in the short term, but are essential for fairness, security, and maintainable operations.

---

## Suggested phased implementation (small team)

1. **Phase A (vertical slice hardening)**
   - Single shard server loop, browser client, basic WebSocket protocol, minimal agent runtime.
2. **Phase B (debug maturity)**
   - Add replay logs, tick inspector, stronger metrics/traces.
3. **Phase C (MVP readiness)**
   - Shard orchestration, richer admin tools, storage partitioning, safer rollout controls.

This sequence keeps the prototype playable quickly while establishing the architectural guardrails needed for future scale and agent sophistication.
