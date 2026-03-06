export type EntityId = string;

export interface Timestamped {
  createdAtMs: number;
  updatedAtMs: number;
}

export const nowMs = (): number => Date.now();
