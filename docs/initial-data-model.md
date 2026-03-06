# Initial Vertical Slice Data Model

## 1) Conceptual model

### Core principles
- **Server authoritative**: all mutating actions are commands validated and applied by the server.
- **Replay/debuggable**: every accepted command can emit one or more deterministic events.
- **Prototype-first**: minimal fields now, explicit extension points (`meta`, versioning, optional refs).

### Entity groups
- **Actors**: `character`, `npc`, `monster` share common shape through `EntityBase` + role-specific fields.
- **World**: `map`, `position` locate entities and define movement/combat context.
- **Progression & economy**: `item`, `inventory`, `equipment`, `trade`, `quest`.
- **Interaction**: `chat message`, `combat state`.
- **AI scaffolding**: `agent memory stub` for future behavior systems.
- **Observability**: `event log` as append-only source for replay and debugging.

### Simulation flow (prototype)
1. Client sends command (move, attack, chat, trade request).
2. Server validates against current authoritative state.
3. Server mutates aggregate roots (`character`, `combat state`, etc.).
4. Server emits `event log` entries with causal metadata.
5. Clients receive state deltas/snapshots derived from server state.

---

## 2) Type definitions / schema suggestions

Use these as TypeScript domain types plus optional runtime validation (e.g., zod/io-ts/JSON Schema).

```ts
// src/data-model.ts

export type ID = string;
export type UnixMs = number;

export type EntityKind = 'character' | 'npc' | 'monster';
export type ItemKind = 'consumable' | 'equipment' | 'quest' | 'currency' | 'misc';
export type EquipSlot =
  | 'head'
  | 'chest'
  | 'legs'
  | 'feet'
  | 'mainHand'
  | 'offHand'
  | 'ring1'
  | 'ring2';

export interface Position {
  mapId: ID;
  x: number;
  y: number;
  z?: number;
  heading?: number;
  cell?: string; // optional spatial partition key for quick lookup
}

export interface Stats {
  hp: number;
  maxHp: number;
  mp?: number;
  maxMp?: number;
  attack: number;
  defense: number;
  speed?: number;
}

export interface EntityBase {
  id: ID;
  kind: EntityKind;
  name: string;
  position: Position;
  stats: Stats;
  level?: number;
  faction?: string;
  tags?: string[];
  meta?: Record<string, unknown>; // extension point
  createdAt: UnixMs;
  updatedAt: UnixMs;
  version: number; // optimistic lock / change sequence
}

export interface Character extends EntityBase {
  kind: 'character';
  accountId: ID;
  classId?: string;
  xp?: number;
  gold: number;
  inventoryId: ID;
  equipmentId: ID;
  activeQuestIds?: ID[];
}

export interface Npc extends EntityBase {
  kind: 'npc';
  behaviorProfile: 'static' | 'vendor' | 'questGiver' | 'patrol';
  shopInventoryId?: ID;
  dialogueTreeId?: ID;
  questOfferIds?: ID[];
}

export interface Monster extends EntityBase {
  kind: 'monster';
  speciesId: string;
  aggroRange: number;
  leashRange?: number;
  respawnSeconds?: number;
  lootTableId?: ID;
}

export interface Item {
  id: ID;
  templateId: string;
  name: string;
  kind: ItemKind;
  stackable: boolean;
  maxStack?: number;
  rarity?: 'common' | 'uncommon' | 'rare' | 'epic';
  equipSlot?: EquipSlot;
  statMods?: Partial<Stats>;
  value?: number;
  bindOnPickup?: boolean;
  meta?: Record<string, unknown>;
  createdAt: UnixMs;
}

export interface InventorySlot {
  slot: number;
  itemId?: ID;
  quantity?: number;
}

export interface Inventory {
  id: ID;
  ownerEntityId: ID;
  capacity: number;
  slots: InventorySlot[];
  version: number;
  updatedAt: UnixMs;
}

export interface Equipment {
  id: ID;
  ownerEntityId: ID;
  slots: Partial<Record<EquipSlot, ID>>; // itemId by slot
  version: number;
  updatedAt: UnixMs;
}

export interface MapSpawnPoint {
  id: ID;
  position: Position;
  type: 'characterSpawn' | 'monsterSpawn' | 'npcSpawn';
  refId?: ID; // monster species, npc template, etc.
}

export interface MapZone {
  id: ID;
  name: string;
  minLevel?: number;
  maxLevel?: number;
  pvpEnabled?: boolean;
  bounds?: { x1: number; y1: number; x2: number; y2: number };
}

export interface MapData {
  id: ID;
  name: string;
  width: number;
  height: number;
  seed?: number;
  zones?: MapZone[];
  spawnPoints?: MapSpawnPoint[];
  version: number;
}

export type CombatStatus = 'idle' | 'engaged' | 'downed' | 'dead';

export interface CombatState {
  id: ID;
  participants: ID[]; // entity IDs
  threatTable?: Record<ID, number>;
  turnOrder?: ID[];
  statusByEntity: Record<ID, CombatStatus>;
  startedAt: UnixMs;
  lastActionAt: UnixMs;
  endedAt?: UnixMs;
  mapId: ID;
  version: number;
}

export type ChatChannel = 'say' | 'party' | 'guild' | 'system' | 'whisper';

export interface ChatMessage {
  id: ID;
  channel: ChatChannel;
  senderEntityId?: ID; // omitted for system
  recipientEntityId?: ID; // whisper target
  mapId?: ID;
  content: string;
  createdAt: UnixMs;
  moderation?: {
    filtered: boolean;
    reason?: string;
  };
}

export type TradeStatus = 'requested' | 'accepted' | 'locked' | 'completed' | 'cancelled';

export interface TradeOffer {
  entityId: ID;
  itemIds: ID[];
  gold: number;
  locked: boolean;
}

export interface Trade {
  id: ID;
  partyA: ID;
  partyB: ID;
  offerA: TradeOffer;
  offerB: TradeOffer;
  status: TradeStatus;
  createdAt: UnixMs;
  updatedAt: UnixMs;
  version: number;
}

export type QuestStatus = 'notStarted' | 'inProgress' | 'completed' | 'failed';

export interface QuestStub {
  id: ID;
  templateId: string;
  title: string;
  description?: string;
  giverNpcId?: ID;
  status: QuestStatus;
  objectiveCounters?: Record<string, number>;
  rewardPreview?: {
    xp?: number;
    gold?: number;
    itemIds?: ID[];
  };
  updatedAt: UnixMs;
}

export interface AgentMemoryStub {
  id: ID;
  agentEntityId: ID; // npc or monster
  memoryType: 'lastSeenEnemy' | 'homePosition' | 'dialogContext' | 'custom';
  payload: Record<string, unknown>;
  confidence?: number;
  expiresAt?: UnixMs;
  updatedAt: UnixMs;
}

export type EventType =
  | 'entity.spawned'
  | 'entity.moved'
  | 'combat.started'
  | 'combat.action'
  | 'combat.ended'
  | 'item.added'
  | 'item.removed'
  | 'trade.updated'
  | 'chat.sent'
  | 'quest.updated'
  | 'system.snapshot';

export interface EventLog {
  id: ID;
  seq: number; // monotonically increasing per shard/world
  eventType: EventType;
  actorEntityId?: ID;
  targetEntityId?: ID;
  mapId?: ID;
  timestamp: UnixMs;
  causationId?: ID; // command ID that produced this event
  correlationId?: ID; // group related events from same user action
  payload: Record<string, unknown>;
  schemaVersion: number;
}
```

### Server-authoritative + replay notes
- Keep **commands** separate from **events**. Events are append-only facts.
- Store `version` on mutable records to reject stale writes.
- Include `seq`, `causationId`, `correlationId` in event log for deterministic replay and debugging.
- Prefer deterministic simulation inputs (seeded RNG per encounter/map segment if random).

---

## 3) What can remain in-memory vs persisted

### Persist (required for continuity / auditing)
- `character`, `inventory`, `equipment`, `item` ownership state.
- `quest stub` progress.
- completed `trade` outcomes (at least summary + transferred assets).
- `event log` (full or sampled + periodic snapshots).
- durable `npc`/`monster` definitions (templates), even if runtime instances are ephemeral.

### In-memory (safe for prototype, recoverable)
- active `combat state` (can be reconstructed from recent events or reset on restart).
- transient `trade` sessions before completion.
- short-lived `chat message` buffers (unless moderation/compliance requires persistence).
- runtime `agent memory stub` entries with short TTL.
- current map occupancy cache / spatial index.

### Hybrid recommendation
- Persist periodic **world snapshots** (`system.snapshot` events or separate snapshot table) every N seconds/minutes.
- Keep hot simulation state in-memory for tick speed.
- On restart: load latest snapshot + replay subsequent events.
