# First Playable Vertical Slice — Step-by-Step Plan

## Planning Assumptions
- Team: 3–5 people (design, gameplay/programming, backend/full-stack, art/audio support).
- Cadence: short weekly iterations with a playable build at the end of each sprint.
- Scope for vertical slice: one small map/zone, one core progression loop, one enemy type, one quest, one reward path, one multiplayer interaction.
- Technical strategy: prefer simple, testable features first and defer scale/perf optimization until slice is fun and stable.

## Milestone 0 — Foundation and Working Loop Skeleton (1–2 days)
### Goal
Set up repository structure, build/run workflow, and a “graybox boot flow” where a player can spawn into a test scene and move.

### Files/modules likely involved
- `README.md` (local run instructions)
- `docs/architecture.md` (high-level module boundaries)
- `client/` bootstrap (scene load + input + camera)
- `server/` bootstrap (optional at this stage, can be local mock)
- `shared/` common types (player state, entity ids)
- CI script(s): `.github/workflows/ci.yml` or equivalent

### Dependencies
- Engine/framework choice finalized
- Basic dev tooling agreed (lint/test format)

### Definition of done
- New developer can clone, run one command, and enter a controllable character in a graybox scene.
- CI validates lint + build on main branch.
- Basic architecture doc exists to reduce merge conflicts and design drift.

---

## Milestone 1 — Core Movement + Camera + Interaction Stub (2–3 days)
### Goal
Make movement feel acceptable and add one visible interaction (e.g., interact prompt with placeholder object).

### Files/modules likely involved
- `client/player/movement.*`
- `client/player/camera.*`
- `client/ui/interact_prompt.*`
- `client/world/interactable.*`
- `shared/input_actions.*`

### Dependencies
- Milestone 0 bootstrap in place
- Input mapping scheme decided (keyboard/gamepad minimum)

### Definition of done
- Player can move, look around, and trigger an interact action near an object.
- At least one visible feedback signal exists (UI prompt, sound, animation placeholder).
- Movement/camera settings are data-driven (easy tweaking without code edits).

---

## Milestone 2 — Combat Micro-Loop (Player vs 1 Enemy) (3–5 days)
### Goal
Implement the first fun loop: find enemy → attack → enemy dies → get reward feedback.

### Files/modules likely involved
- `client/combat/player_attack.*`
- `client/combat/hit_detection.*`
- `client/enemies/basic_enemy_controller.*`
- `client/ui/health_bar.*`, `client/ui/damage_numbers.*` (optional)
- `shared/combat_types.*` (damage events, hp values)
- `data/enemies/basic_enemy.json`

### Dependencies
- Milestone 1 interaction + movement
- Placeholder enemy art/rig or capsule proxy

### Definition of done
- Enemy can spawn, chase/engage in simple behavior, take damage, and die.
- Player gets immediate reward signal (loot text popup, xp increment, or currency counter).
- Combat values are configurable in data files for rapid balancing.

---

## Milestone 3 — Minimal Quest Loop (Talk → Objective → Turn-in) (3–4 days)
### Goal
Add one complete guided loop that gives players purpose and a clear success condition.

### Files/modules likely involved
- `client/npc/npc_interaction.*`
- `client/quests/quest_tracker_ui.*`
- `server/quests/quest_state_service.*` (or local temporary service)
- `shared/quests/quest_definitions.*`
- `data/quests/first_hunt_quest.json`
- `data/dialogue/*.json`

### Dependencies
- Milestone 2 combat and enemy kill event
- Basic UI layer available for objective text

### Definition of done
- Player can accept quest from NPC, complete objective (e.g., kill 3 enemies), and turn it in.
- Quest state survives at least scene reload/session restart (even if local persistence).
- Quest progress is visible at all times in a simple tracker.

---

## Milestone 4 — Reward + Inventory Slice (2–3 days)
### Goal
Make rewards meaningful by adding a tiny inventory/equipment flow.

### Files/modules likely involved
- `client/inventory/inventory_ui.*`
- `client/items/item_instance.*`
- `server/inventory/inventory_service.*` (or local service)
- `shared/items/item_defs.*`
- `data/items/starter_weapon.json`, `data/items/quest_reward.json`

### Dependencies
- Milestone 3 quest completion event
- Existing reward trigger hooks from combat/quest systems

### Definition of done
- Quest/combat can grant item(s) into inventory.
- Player can equip one item and see a visible stat or damage change.
- Inventory data model supports future expansion (stackables/equipment slots) without rewrite.

---

## Milestone 5 — Multiplayer Presence Lite (2–4 days)
### Goal
Prove the game feels multiplayer: two players can coexist and see each other moving and fighting.

### Files/modules likely involved
- `server/network/session_manager.*`
- `server/network/state_replication.*`
- `client/network/remote_player_proxy.*`
- `shared/network/messages.*`
- `shared/network/snapshots.*`

### Dependencies
- Milestone 1 movement and Milestone 2 combat events
- Decision on transport (WebSocket/UDP engine-native)

### Definition of done
- Two clients can join same zone and observe each other movement/attacks.
- Basic reconciliation/interpolation prevents severe jitter.
- Critical events (enemy death, quest progress increments) stay consistent across clients.

---

## Milestone 6 — One Curated Playable Zone (3–5 days)
### Goal
Package all systems into one 10–15 minute “mini-adventure” with a start and end.

### Files/modules likely involved
- `client/world/zone_vertical_slice.*`
- `data/spawns/*.json`
- `data/encounters/*.json`
- `client/ui/hud_slice_polish.*`
- `audio/events/*.json` (if applicable)

### Dependencies
- Milestones 2–5 functional
- Basic art pass and landmarks for navigation

### Definition of done
- New player can start, get quest, fight enemies, complete objective, earn/equip reward, and see at least one other player in-zone (if multiplayer mode enabled).
- Full loop completes in <=15 minutes without developer intervention.
- Internal team can demo this reliably to stakeholders.

---

## Milestone 7 — Stability + Metrics + Iteration Hooks (2–3 days)
### Goal
Reduce demo risk and make iteration data-driven for subsequent slices.

### Files/modules likely involved
- `server/telemetry/event_logger.*`
- `client/telemetry/session_events.*`
- `docs/playtest_checklist.md`
- `docs/balance_tuning_sheet.md`
- Test harness scripts in `tools/` or `scripts/`

### Dependencies
- End-to-end slice from Milestone 6

### Definition of done
- Crash/error logging catches top runtime failures.
- Key metrics captured: time-to-first-combat, quest completion rate, death count, session length.
- Team has a repeatable playtest script and triage process.

---

## Recommended Execution Order (for low risk + high visible progress)
1. Milestone 0 (setup + spawnable character)
2. Milestone 1 (movement + interaction)
3. Milestone 2 (combat loop)
4. Milestone 3 (quest loop)
5. Milestone 4 (reward/inventory meaning)
6. Milestone 6 (curated zone integration)
7. Milestone 5 (multiplayer presence lite)
8. Milestone 7 (stability + metrics)

> Note: Milestone 5 is intentionally moved after core single-player fun is proven. This keeps early playability high and integration risk lower while still landing multiplayer inside the first slice window.

## Team Split Suggestion (Small Team Friendly)
- **Gameplay dev:** Milestones 1–3 implementation owner
- **Backend/network dev:** Milestones 5 + persistence aspects of 3/4
- **Content/designer:** quest data, encounter tuning, zone flow (Milestones 3, 6)
- **Shared responsibility:** Milestones 0 and 7 (quality gates + docs)

## AI-Assisted Coding Opportunities
- Generate data schemas and JSON templates for quests/items/enemies early.
- Auto-scaffold UI panels (quest tracker, inventory list, reward toast).
- Create unit tests for deterministic systems (damage calculation, quest state transitions).
- Produce balancing scripts to run simulation batches (TTK, xp progression curves).

## Lightweight Weekly Rhythm
- **Day 1:** lock milestone scope + acceptance criteria
- **Day 2–4:** implementation + daily playable check-ins
- **Day 5:** playtest, bug bash, adjust data, freeze build

This keeps the slice always runnable and maximizes visible progress each week.
