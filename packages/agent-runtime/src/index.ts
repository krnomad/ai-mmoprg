import { nowMs } from "@ai-mmoprg/shared";

export class AgentRuntime {
  private tick = 0;
  private readonly startedAtMs = nowMs();

  nextTick(): number {
    this.tick += 1;
    return this.tick;
  }

  uptimeMs(): number {
    return nowMs() - this.startedAtMs;
  }
}
