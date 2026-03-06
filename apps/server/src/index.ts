import { AgentRuntime } from "@ai-mmoprg/agent-runtime";
import { createHeartbeat } from "@ai-mmoprg/protocol";

// Placeholder service bootstrap; replace with real transport (HTTP/WebSocket) during server implementation.
const runtime = new AgentRuntime();
const heartbeat = createHeartbeat(runtime.nextTick());

console.log("[server] bootstrap heartbeat", heartbeat);
