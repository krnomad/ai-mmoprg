import type { EntityId } from "@ai-mmoprg/shared";

export const protocolVersion = "0.1.0";

export interface HeartbeatMessage {
  kind: "heartbeat";
  protocolVersion: string;
  tick: number;
  source: EntityId;
}

export const createHeartbeat = (tick: number): HeartbeatMessage => ({
  kind: "heartbeat",
  protocolVersion,
  tick,
  source: "server-core"
});
