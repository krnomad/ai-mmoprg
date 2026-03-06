# Server-Authoritative Simulation Core (Vertical Slice, v1)

This design is implementation-oriented for TypeScript and favors **simple, deterministic rules**.

## Goals and Non-Goals

### Goals
- Deterministic tick-based simulation on server.
- Clear action validation and rejection reasons.
- Replayable event log for debugging/observability.
- Minimal but complete MMO loop: movement, combat, aggro, loot, chat.

### Non-Goals (v1)
- Sophisticated pathfinding/steering.
- Physics collisions beyond simple blockers/grid checks.
- Advanced anti-cheat heuristics (beyond strict authority + validation).
- Distributed multi-zone architecture.

---

## 1) World State Model

Use plain data objects with stable IDs and integer/fixed-point values where practical.

```ts
// Branded ID helpers for type safety.
type EntityId = string & { readonly _brand: 'EntityId' };
type PlayerId = string & { readonly _brand: 'PlayerId' };
type Tick = number;
type Ms = number;
type ZoneId = string;

type Vec2 = { x: number; y: number }; // v1: 2D plane

enum EntityKind {
  Player = 'player',
  Npc = 'npc',
  Projectile = 'projectile', // optional v1; may be omitted if instant-hit only
  Loot = 'loot',
}

interface Stats {
  maxHp: number;
  hp: number;
  attackPower: number;
  defense: number;
  moveSpeedUnitsPerSec: number;
  attackRange: number;
  attackPeriodTicks: number; // cooldown
}

interface Cooldowns {
  nextBasicAttackTick: Tick;
}

interface ThreatEntry {
  sourceId: EntityId;
  threat: number;
  lastTick: Tick;
}

interface AggroState {
  targetId?: EntityId;
  table: ThreatEntry[]; // small list, sorted descending each update or lazily
  leashOrigin: Vec2;
  leashRadius: number;
}

interface EntityBase {
  id: EntityId;
  kind: EntityKind;
  zoneId: ZoneId;
  pos: Vec2;
  facing: Vec2;
  radius: number;
  alive: boolean;
  createdTick: Tick;
}

interface PlayerEntity extends EntityBase {
  kind: EntityKind.Player;
  playerId: PlayerId;
  stats: Stats;
  cooldowns: Cooldowns;
  inventory: Inventory;
  gold: number;
  inputSeqAck: number; // highest client input sequence accepted
}

interface NpcEntity extends EntityBase {
  kind: EntityKind.Npc;
  templateId: string;
  stats: Stats;
  cooldowns: Cooldowns;
  aggro: AggroState;
  respawnAtTick?: Tick;
}

interface LootEntity extends EntityBase {
  kind: EntityKind.Loot;
  ownerPlayerId?: PlayerId; // optional temporary ownership
  expiresAtTick: Tick;
  drops: ItemStack[];
  gold: number;
}

interface ItemStack {
  itemId: string;
  qty: number;
}

interface Inventory {
  slots: Array<ItemStack | null>;
  capacity: number;
}

interface WorldConfig {
  tickRate: number; // e.g. 20
  maxMovePerTick: number; // derived from speed + tolerance
  chatMaxLength: number;
  lootOwnershipTicks: number;
  corpseDespawnTicks: number;
  globalDropMultiplierPermille: number;
}

interface WorldState {
  tick: Tick;
  startedAtMs: Ms;
  rngSeed: number;
  config: WorldConfig;

  // Authoritative entity store.
  entities: Map<EntityId, EntityBase | PlayerEntity | NpcEntity | LootEntity>;

  // Fast subsets (optional denormalized indexes).
  playersById: Map<PlayerId, EntityId>;
  entitiesByZone: Map<ZoneId, Set<EntityId>>;

  // Static collision/nav info for v1.
  blockedCellsByZone: Map<ZoneId, Set<string>>; // key = "x:y" cell

  // Deterministic action queue keyed by execute tick.
  actionQueue: Map<Tick, ActionEnvelope[]>;

  // Append-only event log; rotate/snapshot in production.
  eventLog: SimEvent[];
}
```

### Determinism Notes
- Use server-only RNG seeded by `world.rngSeed` + tick progression.
- Prefer integer math for combat and drop rates (`permille`, `basis points`).
- Process entities/actions in stable sorted order by `EntityId`.

---

## 2) Entity Update Loop

Single-threaded logical simulation loop (even if infrastructure is multi-threaded).

```ts
function simulationTick(world: WorldState): void {
  const tick = world.tick;

  // 1) Pull actions for this tick; sort deterministically.
  const actions = (world.actionQueue.get(tick) ?? []).sort(compareActionOrder);

  // 2) Validate and apply actions.
  for (const envelope of actions) {
    processActionEnvelope(world, envelope, tick);
  }

  // 3) AI/NPC updates (aggro decisions, movement intentions, attacks).
  const npcs = getEntitiesByKind<NpcEntity>(world, EntityKind.Npc);
  for (const npc of npcs.sort(compareEntityId)) {
    updateNpcBrain(world, npc, tick);
  }

  // 4) Resolve passive systems (regen optional), death, despawn, respawn.
  resolveDeaths(world, tick);
  resolveLootExpiry(world, tick);
  resolveRespawns(world, tick);

  // 5) Emit end-of-tick snapshot delta event(s).
  emitTickSummary(world, tick);

  // 6) Advance time.
  world.tick = tick + 1;
}
```

**Ordering principle (v1):**
1. Player actions
2. NPC AI decisions
3. System cleanups
4. Event flush

No rollback/reconciliation in server core; client handles prediction and correction from server state deltas.

---

## 3) Movement Processing

### Input Action
```ts
interface MoveAction {
  type: 'move';
  actorId: EntityId;
  inputSeq: number;
  desiredDir: Vec2; // normalized or near-normalized
  clientSentAtMs: Ms;
}
```

### Server Rules
- Actor must exist, be alive, controllable by sender.
- Reject if stunned/rooted (if status exists in v1).
- Clamp displacement per tick:
  - `maxStep = stats.moveSpeedUnitsPerSec / tickRate`
  - with small tolerance (e.g. +5%) for numeric noise.
- Proposed position = `pos + desiredDir * maxStep`.
- Collision check against blocked cell map + optional entity blocking.
- If blocked, either:
  - stop in place, or
  - slide along one axis (optional, still deterministic).

### Deterministic Move Function
```ts
function applyMove(world: WorldState, actor: PlayerEntity, action: MoveAction): void {
  const dir = normalizeOrZero(action.desiredDir);
  const step = actor.stats.moveSpeedUnitsPerSec / world.config.tickRate;
  const next = { x: actor.pos.x + dir.x * step, y: actor.pos.y + dir.y * step };

  const resolved = resolveCollision(world, actor.zoneId, actor.pos, next, actor.radius);
  if (resolved.x !== actor.pos.x || resolved.y !== actor.pos.y) {
    const from = actor.pos;
    actor.pos = resolved;
    emit(world, {
      type: 'EntityMoved',
      tick: world.tick,
      entityId: actor.id,
      from,
      to: resolved,
      inputSeq: action.inputSeq,
    });
  }

  actor.inputSeqAck = Math.max(actor.inputSeqAck, action.inputSeq);
}
```

---

## 4) Combat Processing

Keep v1 as deterministic instant-hit basic attack.

### Attack Action
```ts
interface BasicAttackAction {
  type: 'basic_attack';
  actorId: EntityId;
  targetId: EntityId;
  inputSeq: number;
}
```

### Validation
- Actor and target exist, same zone, both alive.
- Actor cooldown ready (`tick >= nextBasicAttackTick`).
- Target in range (`distance <= attackRange + target.radius`).
- Optional line-of-sight check via grid raycast.

### Damage Formula (simple)
```ts
const raw = attacker.stats.attackPower;
const mitigated = Math.max(1, raw - target.stats.defense);
const damage = mitigated; // no crits in v1
```

### Apply
- Subtract HP, clamp to `[0, maxHp]`.
- Set attacker cooldown.
- Emit `CombatHit` event.
- If HP reaches 0, mark dead and emit `EntityDied`; defer drop generation to death resolver phase (same tick).

---

## 5) Aggro/Targeting Rules

### Threat Model
- NPC maintains threat table of recent hostile entities.
- Threat sources:
  - Damage dealt to NPC: `+damage * 100` threat.
  - Heal on NPC enemy target (optional v1): can skip initially.
  - Proximity pull: on enter aggro radius, add baseline threat.

### Selection
- Pick highest threat alive target in leash radius.
- Tie-breaker: nearest distance, then lower `EntityId` lexical.

### Leash/Reset
- NPC has `leashOrigin` and `leashRadius`.
- If NPC is pulled beyond leash radius:
  - clear target/table,
  - return to leash origin,
  - optional full HP reset once disengaged.

### Decay (optional simple)
- Every N ticks, multiply threat by 0.9 (fixed-point integer).
- Remove entries not updated for M ticks.

---

## 6) Loot/Drop Processing

Perform drop generation on confirmed death in deterministic resolver.

### NPC Drop Table
```ts
interface DropRow {
  itemId: string;
  chancePermille: number; // 0..1000
  minQty: number;
  maxQty: number;
}

interface NpcDropTable {
  guaranteedGoldMin: number;
  guaranteedGoldMax: number;
  rows: DropRow[];
}
```

### Algorithm
1. Resolve killer/owner (last hitter or top threat).
2. Roll gold with deterministic RNG.
3. For each row, roll once vs `chancePermille`.
4. Spawn one `LootEntity` at death position.
5. Set `ownerPlayerId` for short duration (`lootOwnershipTicks`).
6. Emit `LootSpawned` event with full payload.

### Pickup Rules
- Player must be within pickup radius.
- If ownership active and player != owner, reject.
- Add to inventory atomically; if full, reject or partial-by-stack (define one and keep stable).
- On success emit `LootPicked` and remove loot entity if empty.

---

## 7) Chat Event Handling

Treat chat as validated game action with separate rate limits.

### Chat Action
```ts
interface ChatAction {
  type: 'chat';
  actorId: EntityId;
  channel: 'say' | 'party' | 'system'; // v1 keep small
  text: string;
}
```

### Validation
- Actor exists and maps to authenticated player session.
- Text length `1..chatMaxLength`.
- UTF-8/control-char sanitization.
- Rate limit per player token bucket (e.g., 3 msgs / 5 sec burst 5).

### Delivery
- Emit `ChatMessageAccepted` simulation event.
- Fan-out to recipients by channel scope:
  - `say`: same zone and within chat radius,
  - `party`: party members,
  - `system`: server only.

For replay, persist original sanitized text and recipient set hash (or explicit list for v1).

---

## 8) Action Validation Pipeline

Use a strict, composable pipeline returning typed failure reasons.

```ts
enum ActionRejectCode {
  UnknownActor = 'UnknownActor',
  NotAuthorized = 'NotAuthorized',
  DeadActor = 'DeadActor',
  BadState = 'BadState',
  OutOfRange = 'OutOfRange',
  Cooldown = 'Cooldown',
  InvalidTarget = 'InvalidTarget',
  RateLimited = 'RateLimited',
  SchemaInvalid = 'SchemaInvalid',
}

interface ActionEnvelope {
  actionId: string; // idempotency key
  senderPlayerId: PlayerId;
  receivedAtTick: Tick;
  executeAtTick: Tick;
  action: AnyAction;
}

interface ValidationResult<T> {
  ok: boolean;
  value?: T;
  reject?: { code: ActionRejectCode; details?: string };
}
```

### Stages
1. **Schema validation** (zod/io-ts).
2. **Authentication/ownership** (`senderPlayerId` controls `actorId`).
3. **Actor state** (alive, in-world, not stunned).
4. **Action-specific constraints** (range/cooldown/LOS).
5. **Anti-replay/idempotency** (reject duplicate `actionId`).
6. **Apply mutation** (single source of truth).
7. **Emit accepted/rejected event**.

Every reject should emit an `ActionRejected` event for observability and client feedback.

---

## 9) Event Emission for Replay/Observability

Use an append-only event stream emitted from simulation only.

```ts
type SimEvent =
  | { type: 'ActionAccepted'; tick: Tick; actionId: string; actorId: EntityId }
  | { type: 'ActionRejected'; tick: Tick; actionId: string; code: ActionRejectCode }
  | { type: 'EntityMoved'; tick: Tick; entityId: EntityId; from: Vec2; to: Vec2; inputSeq?: number }
  | { type: 'CombatHit'; tick: Tick; attackerId: EntityId; targetId: EntityId; damage: number; hpAfter: number }
  | { type: 'EntityDied'; tick: Tick; entityId: EntityId; killerId?: EntityId }
  | { type: 'LootSpawned'; tick: Tick; lootId: EntityId; at: Vec2; ownerPlayerId?: PlayerId }
  | { type: 'LootPicked'; tick: Tick; lootId: EntityId; pickerId: EntityId }
  | { type: 'ChatMessageAccepted'; tick: Tick; actorId: EntityId; channel: string; text: string }
  | { type: 'TickSummary'; tick: Tick; entityCount: number };
```

### Requirements
- Monotonic sequence number per event (`eventSeq`).
- Include tick on every event.
- Persist to durable log (Kafka/Postgres/outbox) after simulation step commit.
- Snapshot world every N ticks to accelerate replay, then apply events from snapshot tick.

### Replay Model
- Start from seed snapshot + same RNG seed.
- Re-apply action envelopes in recorded order.
- Assert resulting hash of critical state (`hp`, `pos`, `alive`, inventories).

---

## 10) Boundaries for Agent-Issued Actions

Assume “agent” means automated actors (bot/AI assistant/controller) issuing actions through same API.

### Hard Boundaries
- Agent actions must use **same action schema** and **same validation pipeline** as human players.
- Agent bound to one or more explicit `PlayerId` identities; no raw entity mutation access.
- Enforce per-agent quotas:
  - actions/sec,
  - concurrent sessions,
  - chat/sec.
- Disallow privileged channels unless explicitly scoped (e.g., no `system` chat writes).
- No direct item grant/spawn APIs in live simulation path.

### Safety/Abuse Controls
- Feature flags to disable an agent quickly.
- Audit trail fields on envelopes:
  - `issuedBy: 'human' | 'agent'`,
  - `agentId?`,
  - `decisionTraceId?`.
- Dedicated reject code for policy failures (`NotAuthorized` + detail or `PolicyViolation`).

### Recommended Interface
```ts
interface ActionIngress {
  submit(envelope: ActionEnvelope): Promise<{ accepted: boolean; reason?: string }>;
}
```

Only `submit` is exposed to agents; no backdoor world handles.

---

## Minimal v1 Module Layout (TypeScript)

```txt
src/sim/
  types.ts               // world/entity/action/event types
  tick.ts                // simulationTick loop
  validation.ts          // action validation pipeline
  movement.ts            // move processing
  combat.ts              // basic attack + death marking
  aggro.ts               // threat + target selection
  loot.ts                // drop generation + pickup
  chat.ts                // chat validation + fan-out
  events.ts              // emit/persist adapters
  rng.ts                 // deterministic PRNG wrappers
  snapshot.ts            // snapshot/hash/replay helpers
```

## Suggested First Implementation Milestones
1. Tick loop + movement + accepted/rejected action events.
2. Basic attack + death + loot spawn/pickup.
3. NPC aggro with leash + NPC basic attack behavior.
4. Chat validation/rate-limit + zone fan-out.
5. Snapshot + replay hash checker in integration test.

This sequence keeps vertical slice playable while preserving deterministic foundations.
