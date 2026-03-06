# Vertical Slice Gap Review (Prototype)

## Scope and evidence
Repository inspection indicates there is currently no shipped prototype code, assets, scene data, configuration, or design docs beyond a placeholder file.

Observed repository contents at review time:
- `.gitkeep`

Given that state, this review focuses on the minimum requirements to reach a first playable MMORPG-style vertical slice and identifies the highest-risk decisions that should be resolved first.

## 1) What is already sufficient
At the moment, only foundational repository initialization appears sufficient:
- Git repository exists and is clean.
- Placeholder file exists, indicating repository bootstrap is complete.

No gameplay, backend, content, build, test, or deployment capabilities appear present yet.

## 2) What is missing
A first playable vertical slice typically needs an end-to-end loop that one player can actually run and evaluate. The following are currently missing:

### Core runtime architecture
- Game client application shell (project setup, scenes/screens, build/run instructions).
- Backend service(s) for session/login and authoritative game state.
- Shared schema/protocol for client-server communication.

### Playable loop
- A controllable player character.
- At least one zone/map with collision/navigation boundaries.
- Combat or interaction mechanic (targeting, ability, feedback).
- Enemy/NPC behavior sufficient for one repeatable encounter.
- Reward/progression micro-loop (XP, currency, or loot).

### Online essentials (vertical-slice level)
- Account/session flow (even lightweight guest auth).
- State persistence for minimal progress (inventory/loadout/progression stub).
- Basic replication/state sync for movement and encounter outcomes.

### UX and content essentials
- Minimal HUD (health/resource/target/ability cooldown).
- Input mapping + rebinding defaults documentation.
- Placeholder art/audio/content pack for one coherent test scenario.

### Delivery and quality
- Local runbook (`README`) with one-command startup for client+server.
- Basic telemetry/logging for client/server errors.
- Smoke tests (startup, connect, enter zone, complete encounter).

## 3) Highest-risk weak points
These are the most likely to block “first playable” despite rapid coding progress:

1. **No established client/server contract**
   - Without a stable network protocol and authority model, all gameplay features risk rework.

2. **Unbounded vertical-slice scope**
   - Attempting multiple classes/zones/systems before a single complete loop causes schedule collapse.

3. **Missing observability from day one**
   - Multiplayer bugs become extremely expensive without structured logs and deterministic repro steps.

4. **No persistence boundary definition**
   - If save/load shape changes late, both backend schema and client state handling churn.

5. **Lack of executable developer workflow**
   - If team members cannot run end-to-end locally in minutes, integration cadence stalls.

## 4) Next 5 implementation tasks (priority order)

1. **Define and freeze the vertical-slice acceptance criteria + thin architecture decision record**
   - Explicitly constrain to one zone, one class/loadout, one enemy archetype, one reward loop.
   - Define authoritative server boundaries and packet/message schema v0.

2. **Stand up runnable client-server skeleton with one-command local startup**
   - Add root `README` with exact commands.
   - Implement connection handshake and heartbeat with visible in-client connection status.

3. **Implement a single end-to-end playable loop**
   - Spawn player in zone -> move -> engage one enemy -> resolve combat -> award reward -> persist result.
   - Keep mechanics intentionally simple; optimize for completeness over depth.

4. **Add persistence + recovery for one progress artifact**
   - Save one canonical progression field (e.g., XP or inventory item) and reload on reconnect.
   - Include migration/version marker even if trivial.

5. **Add automated smoke checks + logging baseline**
   - Script checks: boot services, client connect, run encounter simulation, verify persisted state.
   - Add structured logs with correlation/session IDs in both client and server.

## 5) Refactoring recommendations (only necessary)
Given the current near-empty state, broad refactoring is premature. Only apply these guardrails now:

- **Necessary now:** establish module boundaries early (`client`, `server`, `shared-protocol`, `tools/tests`) to prevent hard coupling.
- **Necessary now:** enforce message/schema versioning from v0 to avoid fragile ad-hoc payloads.
- **Not necessary yet:** performance optimization, ECS rewrites, large-scale architecture redesign, or asset pipeline overhauls.

## Suggested exit criteria for “first playable vertical slice”
- A new developer can run one command and play the loop locally within 10 minutes.
- Player can complete one encounter and see persisted progression after reconnect.
- Core path is covered by at least one automated smoke check.
- Known issues are tracked; no blocker-class crash in the core loop.
