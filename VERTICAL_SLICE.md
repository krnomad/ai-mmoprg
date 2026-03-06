# First Playable Vertical Slice (Ruthless Scope)

## 1) Exact features included

### World and population (single shard)
- **One town map** (`Town_01`) with:
  - 1 spawn point
  - 1 healer NPC
  - 1 merchant NPC (buy/sell + trade broker role)
  - 1 gate/transition point to hunting field
- **One hunting field map** (`Field_01`) with:
  - 3 monster spawn clusters
  - 1 return gate to town
- **Characters in one instance only**:
  - 1 human-controlled player session
  - 3–5 AI-controlled player characters (“bot players”)
  - 3 NPC agents total (healer, merchant, guard flavor NPC)
  - 6–10 concurrent monsters alive via respawn

### Movement
- Click-to-move or WASD movement (choose one and ship only one).
- Server-authoritative position updates at fixed tick.
- Collision only against map bounds + blocking props (no complex physics).

### Combat
- Real-time basic attack only:
  - 1 default attack per character
  - single-target hit resolution
  - attack cooldown + damage + death/respawn rules
- Monsters auto-acquire nearest valid target in aggro radius.
- Bot players can patrol and attack monsters.
- No skills, no status effects, no party mechanics.

### Local chat
- One **local proximity chat channel**:
  - text only
  - max range in meters/tiles
  - no global/whisper/guild channels
  - profanity filter optional (can be postponed)

### Item drops
- Monsters drop from a tiny table:
  - gold (guaranteed small amount)
  - 1–2 common loot items (low probability)
- Ground drops visible to nearby players.
- Pickup interaction with simple ownership timeout (e.g., 3 seconds owner-only then free-for-all).

### Simple trading
- **Player ↔ merchant trade** only in vertical slice:
  - sell loot for gold
  - buy 2–3 consumables/basic items
- Optional if time remains: direct player-to-player trade modal with accept/confirm.
- No auction house, no mail, no escrow.

### Spectator view
- Read-only spectator mode in same shard:
  - free camera OR cycle through entities
  - can see movement/combat/chat feed
  - cannot interact, chat, trade, loot, or affect AI
- At minimum, one spectator client can connect and observe session state.

---

## 2) Features explicitly postponed

- Additional towns/fields/dungeons.
- Character creation/customization classes.
- Quest system, dialogue trees, story progression.
- Crafting, equipment upgrade, enchantments.
- Group/party/raid, guilds, social systems beyond local chat.
- PvP systems, duels, arenas, faction rules.
- Advanced monster AI behaviors, boss mechanics.
- Skill trees, multiple abilities, buffs/debuffs.
- Economy depth: auction house, player shops, taxes.
- Persistence hardening and anti-cheat.
- Matchmaking/lobbies/server browser.
- Audio polish, VFX polish, UI skinning beyond functional UX.
- Cross-platform packaging, scalability optimization.
- Live ops/admin tooling beyond minimal debug controls.

---

## 3) Core gameplay loop

1. Human player spawns in `Town_01`.
2. Player walks to gate and enters `Field_01`.
3. Player (plus bots) kills monsters using basic attack.
4. Monsters drop gold/items; player picks up loot.
5. Player returns to town and sells loot to merchant.
6. Player uses local chat to coordinate or banter with nearby entities/players.
7. Repeat loop for stronger cashflow/efficiency (not power progression-heavy yet).
8. Spectator can observe the full loop end-to-end in real time.

Loop target session length: **5–10 minutes of repeatable engagement** without crashes or dead time.

---

## 4) Minimum fun criteria

The slice is "fun enough" only if all are true:

- **Immediate agency**: player can move and fight within 10 seconds of spawn.
- **Constant activity**: in field, player sees a kill opportunity at least every 15 seconds.
- **Reward cadence**: average meaningful drop/reward event at least every 30–45 seconds.
- **Social texture**: local chat is used at least a few times during a 10-minute run.
- **Economic closure**: player can complete at least one full earn → sell → re-enter hunt cycle.
- **Readable spectacle**: spectator can clearly understand who is moving/fighting/winning.

If any criterion fails, cut scope further before adding features.

---

## 5) Acceptance criteria

### Functional acceptance
- Human player can connect, spawn, move, enter field, fight, loot, return, and trade.
- 3–5 bots run continuously without blocking core loop.
- NPC agents are present and responsive for their limited roles.
- Monster respawn sustains available combat targets.
- Local chat messages deliver only to nearby recipients.
- Spectator client can connect and watch with no gameplay permissions.

### Stability acceptance
- 30-minute soak test with:
  - 1 human session
  - 1 spectator session
  - bot + NPC + monster populations active
  - no server crash, no stuck world state, no hard desync.

### Playability acceptance
- New tester can learn controls and perform full loop without explanation in <= 2 minutes.
- Tester can complete 3 full hunt-and-sell loops in <= 15 minutes.
- At least 3/5 internal testers answer "yes" to: "Would you play this again for another 10 minutes?"

### Scope discipline acceptance
- No postponed feature ships unless it is required to unblock one listed acceptance criterion.

---

## 6) Suggested milestone order

### Milestone 1 — World backbone (Day 1–2)
- Load `Town_01` + `Field_01`.
- Spawn human, bots, NPC placeholders, monsters.
- Implement movement + map transition.
- Done when everyone moves and appears in correct zones.

### Milestone 2 — Combat and life cycle (Day 3–4)
- Basic attack, damage, death, respawn.
- Monster aggro + bot combat behavior.
- Done when field supports nonstop combat without manual resets.

### Milestone 3 — Loot and economy stub (Day 5)
- Monster drop tables, ground loot, pickup.
- Merchant buy/sell flow.
- Done when full kill → loot → sell loop works.

### Milestone 4 — Local chat + spectator (Day 6)
- Proximity chat.
- Read-only spectator client mode.
- Done when observer can follow session and chat locality is correct.

### Milestone 5 — Integration hardening (Day 7)
- 30-minute soak tests, bug triage, tuning spawn/reward cadence.
- Remove/disable non-essential UI and unfinished hooks.
- Done when all acceptance criteria pass.

### Milestone 6 — Vertical slice lock (Day 8)
- Freeze scope.
- Capture demo flow script (5-minute guided run).
- Ship internal build for decision gate.

---

## Ruthless scope rules (non-negotiable)
- If a feature does not improve the 5–10 minute core loop, **cut it**.
- Prefer hardcoded data over generic systems for this slice.
- Build only enough tooling to validate acceptance criteria.
- Polish only readability and responsiveness; defer aesthetic ambition.
