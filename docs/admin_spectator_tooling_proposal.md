# Admin and Spectator Tooling Proposal (Prototype)

## 1) Admin panel scope for prototype

### Core principle
Ship a **single internal web console** focused on observability + safe intervention, not full content authoring.

### Prototype modules
1. **Live Entity Monitor**
   - Table of all active entities (players, NPCs, agents, projectiles, world objects).
   - Key columns: `entity_id`, type, zone/region, state, health/status flags, controlling agent, last update tick.
   - Filters: by zone, type, agent, and abnormal state (stuck, error, high latency).
   - Quick drill-down drawer with full component/state snapshot.

2. **Agent Decision Inspector**
   - Per-agent timeline: recent decisions, candidate actions, selected action, confidence/score, and reason string.
   - Link each decision to world snapshot hash + resulting event IDs.
   - Alert badges for repeated failures, no-op loops, invalid actions.

3. **World State Inspector**
   - Read-only region view with:
     - global sim tick/time,
     - active weather/environment modifiers,
     - resource counters,
     - top anomalies (desync risk, pathfinding hotspots).
   - JSON/raw inspector for precise state payloads.

4. **Intervention Console (Safe Ops)**
   - Spawn entity/event with guarded forms (schema-validated).
   - Agent controls: mute, disable, re-enable.
   - Parameter toggles for a short allowlist (spawn rate multiplier, day/night speed, event frequency caps).

5. **Recent Event Replay (Short Horizon)**
   - Last N minutes event stream with playback controls.
   - Jump from replay frame to associated entity/agent detail.

### Prototype non-goals
- Full map editor.
- Long-term analytics warehouse.
- Complex RBAC matrix (start with admin/operator split).

---

## 2) Spectator UX priorities

### Priority order
1. **Immediate readability**
   - Spectator should instantly understand “what is happening now.”
   - Keep default view to: major events, notable entities, and current world phase.

2. **Narrative event feed**
   - Human-readable event cards (battle started, boss enraged, faction objective captured).
   - Auto-cluster spammy low-level events.

3. **Multi-scale context**
   - Quick pivot between macro (world/region health) and micro (single agent/entity).
   - Mini-map + focus panel + event timeline should stay synchronized.

4. **Time controls for spectators**
   - 1x/2x playback on recent timeline.
   - “Go live” button always visible.

5. **Performance and trust**
   - Stable 60fps is less important than consistency and correctness in displayed state.
   - Show latency and data age indicators so spectators know freshness.

### UX defaults
- Default to curated highlights, with opt-in “expert mode” for raw internals.
- Color language: success/neutral/warning/error should match admin console semantics.

---

## 3) Debugging and replay tools

### A. Decision tracing
- Structured per-tick trace record:
  - `agent_id`, tick, observation summary, candidate actions, selected action, reason, expected outcome.
- Correlate with execution result event(s) and post-state diff.

### B. State diffing
- “Before vs after” snapshots around a selected event/decision.
- Highlight changed components only to reduce noise.

### C. Deterministic short replay
- Keep rolling buffer (e.g., 10–30 min) of:
  - input commands,
  - RNG seeds,
  - authoritative event log,
  - periodic checkpoints.
- Support replay from checkpoint + event stream for bug reproduction.

### D. Debug overlays
- Pathfinding heatmap.
- Contention hotspots (same resource targeted by many agents).
- Error overlay (entities failing updates, invalid transitions).

### E. Incident bundles
- One-click “export incident” package with:
  - timeline slice,
  - relevant traces,
  - world snapshot,
  - active parameter settings.
- Enables async debugging without live environment dependency.

---

## 4) Moderation controls

### Operational controls
1. **Agent lifecycle**
   - Mute (suppresses outward actions but keeps observing).
   - Disable (hard stop scheduling/decision loop).
   - Quarantine mode (agent runs in shadow, no world writes).

2. **Entity/event controls**
   - Spawn with audit trail.
   - Despawn/rollback recent admin-spawned entities when safe.
   - Cancel/expire active world events.

3. **Safety limits**
   - Rate-limit manual spawns.
   - Require reason code for high-impact actions.
   - Optional two-step confirmation for destructive operations.

4. **Auditability**
   - Immutable admin action log: who, what, when, before/after values, reason.
   - Filterable by operator and incident ID.

5. **Access model (prototype)**
   - `viewer`: read-only spectator + inspector.
   - `operator`: can mute/disable and tune allowlisted parameters.
   - `admin`: can spawn/cancel events and change safety settings.

---

## 5) What can be postponed

### Postpone to later phases
1. **Advanced analytics**
   - Cohort behavior analysis, long-term trend dashboards, ML anomaly detection.

2. **Full historical replay archive**
   - Keep only short rolling replay initially; cold storage + indexing can come later.

3. **Sophisticated permissions**
   - Fine-grained per-region or per-action policy engine beyond 3 roles.

4. **Complex scenario scripting UI**
   - For prototype, use validated “spawn event/entity” forms instead of full scenario composer.

5. **Custom theming and broadcast polish**
   - Prioritize debugging clarity over stream-ready visuals.

6. **Mobile/admin-on-the-go experience**
   - Desktop-first internal tool for initial rollout.

---

## Suggested implementation sequencing (practical)
1. Event + entity observability foundation (tables, filters, drill-down).
2. Agent decision inspector with trace schema.
3. Admin intervention controls with audit log.
4. Rolling replay + deterministic reproduction path.
5. Spectator quality layer (highlights, overlays, timeline polish).

This sequence ensures the team can operate the world safely before investing in presentation refinements.
