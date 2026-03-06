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
  cell?: string;
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
  meta?: Record<string, unknown>;
  createdAt: UnixMs;
  updatedAt: UnixMs;
  version: number;
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
  slots: Partial<Record<EquipSlot, ID>>;
  version: number;
  updatedAt: UnixMs;
}

export interface MapSpawnPoint {
  id: ID;
  position: Position;
  type: 'characterSpawn' | 'monsterSpawn' | 'npcSpawn';
  refId?: ID;
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
  participants: ID[];
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
  senderEntityId?: ID;
  recipientEntityId?: ID;
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
  agentEntityId: ID;
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
  seq: number;
  eventType: EventType;
  actorEntityId?: ID;
  targetEntityId?: ID;
  mapId?: ID;
  timestamp: UnixMs;
  causationId?: ID;
  correlationId?: ID;
  payload: Record<string, unknown>;
  schemaVersion: number;
}
