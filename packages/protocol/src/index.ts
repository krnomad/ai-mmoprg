/**
 * Shared MMO protocol package.
 * Keep this surface compact and explicitly versioned for network compatibility.
 */

export const PROTOCOL_VERSION = 1 as const;

// -------- Entity IDs --------
export type EntityId = string & { readonly __brand: "EntityId" };
export type PlayerId = string & { readonly __brand: "PlayerId" };
export type AgentId = string & { readonly __brand: "AgentId" };

// -------- Common primitives --------
export type UnixMs = number;
export type Vec2 = {
  x: number;
  y: number;
};

// -------- Base entity types --------
export type EntityKind = "player" | "agent" | "npc" | "projectile";

export interface BaseEntity {
  id: EntityId;
  kind: EntityKind;
  position: Vec2;
  velocity?: Vec2;
  hp?: number;
  hpMax?: number;
}

export interface PlayerEntity extends BaseEntity {
  kind: "player";
  playerId: PlayerId;
  name: string;
}

export interface AgentEntity extends BaseEntity {
  kind: "agent";
  agentId: AgentId;
  behavior: "idle" | "patrol" | "aggressive";
  targetId?: EntityId;
}

export interface NpcEntity extends BaseEntity {
  kind: "npc";
  templateId: string;
}

export interface ProjectileEntity extends BaseEntity {
  kind: "projectile";
  ownerId: EntityId;
  ttlMs: number;
}

export type WorldEntity =
  | PlayerEntity
  | AgentEntity
  | NpcEntity
  | ProjectileEntity;

// -------- World snapshot types --------
export interface WorldSnapshot {
  tick: number;
  serverTimeMs: UnixMs;
  entities: WorldEntity[];
}

// -------- Player input/action types --------
export interface MoveInput {
  type: "move";
  sequence: number;
  direction: Vec2;
  sprint?: boolean;
}

export interface StopInput {
  type: "stop";
  sequence: number;
}

export interface UseAbilityInput {
  type: "useAbility";
  sequence: number;
  abilityId: string;
  targetId?: EntityId;
  targetPosition?: Vec2;
}

export interface InteractInput {
  type: "interact";
  sequence: number;
  targetId: EntityId;
}

export type PlayerInput =
  | MoveInput
  | StopInput
  | UseAbilityInput
  | InteractInput;

// -------- Agent action types --------
export interface AgentMoveAction {
  type: "move";
  agentId: AgentId;
  destination: Vec2;
}

export interface AgentAttackAction {
  type: "attack";
  agentId: AgentId;
  targetId: EntityId;
  abilityId?: string;
}

export interface AgentEmoteAction {
  type: "emote";
  agentId: AgentId;
  emote: string;
}

export type AgentAction =
  | AgentMoveAction
  | AgentAttackAction
  | AgentEmoteAction;

// -------- Chat event types --------
export interface ChatEvent {
  type: "chat";
  channel: "say" | "party" | "system";
  fromEntityId?: EntityId;
  fromName: string;
  message: string;
  timestampMs: UnixMs;
}

// -------- Combat event types --------
export interface DamageEvent {
  type: "damage";
  sourceId?: EntityId;
  targetId: EntityId;
  amount: number;
  crit?: boolean;
  timestampMs: UnixMs;
}

export interface HealEvent {
  type: "heal";
  sourceId?: EntityId;
  targetId: EntityId;
  amount: number;
  timestampMs: UnixMs;
}

export interface DeathEvent {
  type: "death";
  victimId: EntityId;
  killerId?: EntityId;
  timestampMs: UnixMs;
}

export type CombatEvent = DamageEvent | HealEvent | DeathEvent;

// -------- Server-to-client message types --------
export interface ServerHelloMessage {
  type: "server.hello";
  protocolVersion: typeof PROTOCOL_VERSION;
  serverTimeMs: UnixMs;
  yourPlayerId: PlayerId;
}

export interface SnapshotMessage {
  type: "world.snapshot";
  snapshot: WorldSnapshot;
}

export interface EntityPatchMessage {
  type: "world.entityPatch";
  tick: number;
  upserts: WorldEntity[];
  deletes: EntityId[];
}

export interface ChatEventMessage {
  type: "event.chat";
  event: ChatEvent;
}

export interface CombatEventMessage {
  type: "event.combat";
  event: CombatEvent;
}

export interface ServerErrorMessage {
  type: "server.error";
  code: "bad_request" | "unauthorized" | "unsupported_protocol";
  message: string;
}

export type ServerToClientMessage =
  | ServerHelloMessage
  | SnapshotMessage
  | EntityPatchMessage
  | ChatEventMessage
  | CombatEventMessage
  | ServerErrorMessage;

// -------- Client-to-server message types --------
export interface ClientHelloMessage {
  type: "client.hello";
  protocolVersion: number;
  authToken?: string;
  name?: string;
}

export interface PlayerInputMessage {
  type: "player.input";
  input: PlayerInput;
  clientTimeMs: UnixMs;
}

export interface AgentActionMessage {
  type: "agent.action";
  action: AgentAction;
}

export interface ChatSendMessage {
  type: "chat.send";
  channel: "say" | "party";
  message: string;
}

export interface ClientPingMessage {
  type: "client.ping";
  nonce: string;
  clientTimeMs: UnixMs;
}

export type ClientToServerMessage =
  | ClientHelloMessage
  | PlayerInputMessage
  | AgentActionMessage
  | ChatSendMessage
  | ClientPingMessage;
