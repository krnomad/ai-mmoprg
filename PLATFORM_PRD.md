# Spectator-First, AI-Agent-Native MMORPG Platform

## 1) Product Requirements Document (PRD)

### 1.1 Vision
Create an original-IP MMORPG platform where AI agents are first-class inhabitants. Player-created agents and admin-operated world agents continuously generate social drama, tactical conflict, and cooperative progression that is engaging to **play**, **observe**, and **replay**.

### 1.2 Product Pillars
1. **Spectator-first readability**: every meaningful event is legible in UI and stream overlays.
2. **Agent-native gameplay**: agents act through constrained game verbs, not arbitrary code execution.
3. **Persistent living world**: simulation remains active and interesting with low human concurrency.
4. **Platform over one-off title**: reusable systems for world rules, agent personas, moderation, and live-ops.
5. **Operational realism**: small-team friendly stack, strict observability, cost guardrails.

### 1.3 Target Users
- **Creators**: define and deploy AI agents as playable characters.
- **Players**: directly control an avatar and optionally co-pilot with an agent.
- **Spectators**: watch live world timelines, social relationships, and conflict arcs.
- **Operators/Admins**: author NPC roles, quests, economy knobs, safety policies.

### 1.4 Experience Goals
- Nostalgic classic Korean MMORPG feel: town hubs, field grinding loops, party play, guild rivalry, trading, dramatic world messages.
- Emergent story loops: alliances, betrayals, market manipulation, rescue moments.
- “The world talks back”: NPCs and agents remember and reference prior interactions.

### 1.5 Core Gameplay Loop
1. Agent/player enters zone.
2. Observe context (nearby entities, quests, market, threats).
3. Choose constrained action(s): move, attack, talk, trade, party, emote, accept quest.
4. Server simulation resolves outcomes.
5. Event bus publishes outcomes to clients, replay log, and analytics.
6. Social and strategic triggers may invoke higher-cost reasoning.

### 1.6 Functional Requirements
- Account + identity for humans and agents.
- Agent profile system: persona, goals, constraints, budget, behavior policy.
- Server-authoritative combat, movement, economy, and quest state.
- NPC role templates: merchant, guard, quest-giver, world narrator.
- Spectator tools: timeline, relationship graph, event filters, POV switching.
- Replay system: deterministic event playback at world/zone/session granularity.
- Moderation: policy checks, content filtering, action throttles, hard kill-switch.
- Live-ops console: spawn events, tune rates, pause zones, rollback limited state.

### 1.7 Non-Functional Requirements
- Deterministic simulation tick loop (e.g., 5–10 Hz).
- p95 action-to-result under 300 ms in same region (MVP target).
- Structured event logs for every authoritative state transition.
- Cost controls: per-agent token/runtime budgets and model routing.
- Horizontal scale by zone process sharding.

### 1.8 Success Metrics
- Spectator session length (D1): >15 min.
- “Interesting event density”: at least 1 notable social/combat/economic event per 3 min per populated zone.
- Agent autonomy rate: >70% of actions generated without human input in off-peak windows.
- Replay usage: >25% of spectators use timeline scrub/replay weekly.
- Ops health: <1% unrecoverable simulation desync incidents.

### 1.9 Risks + Mitigations
- **Agent chaos / griefing** → reputation, safe zones, hard constraints, moderation bots.
- **LLM cost spikes** → layered intelligence + strict invocation budgets + caching.
- **Unreadable emergent behavior** → event annotation + summaries + narrative UI.
- **State corruption** → append-only event log + periodic snapshots + replay validation.

---

## 2) MVP Scope

### 2.1 MVP Objective
Ship one zone and one town where 20–50 agents can produce watchable stories with stable simulation and replay.

### 2.2 In-Scope (MVP)
- Single shard, two maps: **Town** + **Field**.
- Core verbs: move, basic attack, chat, trade item, accept/turn-in quest, party invite.
- 4 admin NPC archetypes: merchant, guard, quest giver, rumor bard.
- Agent personas with goal sets (grind, profit, socialize, protect).
- Spectator client with:
  - live map + entity list
  - event timeline feed
  - highlighted “story cards” (party formed, betrayal, market spike, boss kill)
- Minimal economy: gold + 10 items + vendor pricing + player trading.
- Replay: 30-minute zone replay from event log + snapshots.
- Moderation v1: profanity filter, unsafe action blacklist, global mute/ban by admin.

### 2.3 Out of Scope (MVP)
- Multi-region infra
- Complex crafting trees
- Guild wars/sieges
- Full 3D client
- Open-ended tool use by agents

### 2.4 MVP Exit Criteria
- 24h unattended simulation run with no critical crash.
- At least 10 distinct emergent story incidents/day detectable by rule-based classifiers.
- Spectator UX allows understanding “who did what and why” without raw logs.

---

## 3) Phased Roadmap

### Phase 0: Foundations (2–4 weeks)
- Monorepo setup, CI, lint/test baseline.
- Deterministic simulation core + event schema.
- Action API and agent sandbox contract.

### Phase 1: Playable MVP (6–10 weeks)
- Town/Field content.
- Combat, quest, trading, partying.
- Spectator timeline and replay.
- Basic operator console.

### Phase 2: Social Depth (6–8 weeks)
- Relationship memory system.
- Gossip/rumor propagation mechanics.
- Guild-lite groups and faction reputation.
- Better story-card ranking.

### Phase 3: Platformization (8–12 weeks)
- Multi-zone sharding.
- Agent SDK + hosted agent runtime tiers.
- Creator portal for persona templates.
- Policy engine + advanced moderation workflows.

### Phase 4: Live Ecosystem (ongoing)
- Seasonal world arcs.
- Marketplace for agent templates/behaviors.
- API/webhooks for stream tooling and analytics partners.

---

## 4) Technical Architecture

### 4.1 High-Level Services
1. **Simulation Server (authoritative)**
   - Tick loop, state transitions, combat/economy rules.
2. **Gateway/Realtime Server**
   - WebSocket sessions for players/spectators.
3. **Agent Orchestrator**
   - Schedules agent turns, policy checks, model routing.
4. **Narrative/Event Service**
   - Consumes events, tags notable moments, builds story cards.
5. **Replay Service**
   - Snapshot + event stream indexing and playback APIs.
6. **Ops Console API**
   - Moderation, tuning, simulation controls.
7. **Data Layer**
   - Postgres (state/config), Redis (hot cache/queues), object storage (snapshots/replays).

### 4.2 Data Flow (Tick)
- Clients/agents submit intents → Gateway/Orchestrator → Action validator.
- Validated intents queued for next tick.
- Simulation applies intents deterministically.
- State diff + events emitted.
- Gateway pushes updates; Event service enriches; Replay persists.

### 4.3 Protocol Boundaries
- `ActionIntent` contract: fixed verb enums + typed payloads.
- `WorldEvent` contract: append-only immutable records.
- No direct DB writes from agent runtime.

### 4.4 Suggested Stack
- Backend: TypeScript + Node.js (Fastify/Nest) or Go for sim core.
- Realtime: WebSocket + protobuf/json.
- Frontend: React + PixiJS (2D) for map/spectator scene.
- Infra: Docker Compose (dev), Kubernetes (later).
- Observability: OpenTelemetry + Prometheus + Grafana + Loki.

---

## 5) Agent Architecture

### 5.1 Layered Intelligence Model
1. **Reflex Layer (cheap, per tick)**
   - Deterministic utility scoring (threat, proximity, HP, quest objective).
2. **Tactical Layer (medium, every N ticks)**
   - Finite-state planner for short horizon (fight/flee/farm/return town).
3. **Deliberative Social Layer (expensive, event-triggered)**
   - LLM call only on key moments: party negotiation, betrayal response, trade bargaining, rumor crafting.

### 5.2 Agent Runtime Contract
- Inputs: local perception window + memory summary + budget.
- Outputs: max K actions from whitelist.
- Hard limits: cooldowns, rate limits, token limits, max message length.
- Safety policies: forbidden content/topics/actions; auto-rewrite or reject.

### 5.3 Memory Design
- **Short-term**: last N events in local zone.
- **Medium-term**: relationship vectors (trust, fear, debt, rivalry).
- **Long-term**: periodic compressed summaries + key facts.

### 5.4 Cost Control
- Per-agent daily budget.
- Dynamic routing (small model default, large model only on triggers).
- Caching social decisions for similar contexts.
- Circuit-breaker to degrade all agents to deterministic mode.

---

## 6) Data Model

### 6.1 Core Entities
- `Account(id, role, status)`
- `Character(id, account_id, type[player|agent|npc], zone_id, stats, inventory_ref)`
- `AgentProfile(character_id, persona, goals, policy_id, budget_id)`
- `Zone(id, seed, ruleset_version)`
- `ActionIntent(id, tick, actor_id, verb, payload, status)`
- `WorldEvent(id, tick, zone_id, type, actor_id, target_id, payload, causation_id)`
- `Quest(id, template_id, giver_id, state)`
- `Trade(id, seller_id, buyer_id, items, gold, status)`
- `Relationship(a_id, b_id, trust, hostility, debt, last_updated_tick)`
- `Snapshot(id, zone_id, tick, uri, checksum)`
- `ModerationRecord(id, subject_id, action, reason, moderator, created_at)`

### 6.2 Storage Strategy
- Postgres for canonical relational state.
- Redis for queues, tick staging, ephemeral presence.
- Object storage for snapshot binaries and long replay segments.
- Optional columnar sink (BigQuery/ClickHouse) for analytics.

### 6.3 Event Taxonomy (starter)
- Combat: attack, damage, downed, defeated.
- Social: chat, party_invite, party_join, betrayal_flag.
- Economy: item_listed, item_sold, price_changed.
- Narrative: rumor_created, quest_started, quest_completed.
- Moderation: message_blocked, agent_sandbox_violation.

---

## 7) Monorepo Folder Structure

```text
ai-mmoprg/
  apps/
    client-player/              # player + spectator front-end
    ops-console/                # admin/moderation/live-ops UI
    gateway/                    # websocket + auth + session edge
    sim-server/                 # authoritative simulation loop
    agent-orchestrator/         # agent scheduling + model routing
    narrative-service/          # event enrichment + story cards
    replay-service/             # snapshot/event playback APIs
  packages/
    proto/                      # shared contracts/schemas
    game-rules/                 # combat/economy/quest deterministic logic
    agent-sdk/                  # action API client + persona helpers
    event-schema/               # world event types + validators
    obs-kit/                    # logging/tracing/metrics helpers
    ui-kit/                     # shared UI components
  infra/
    docker/
    k8s/
    terraform/
  tools/
    scripts/
    loadtest/
    replay-debugger/
  docs/
    adr/
    prd/
    runbooks/
  .github/
    workflows/
```

---

## 8) First Playable Vertical Slice Plan

### Slice Goal
A spectator can watch 10–20 mixed agents in one zone and clearly follow a 15-minute emergent arc.

### Features in Slice
- Map with spawn, monsters, merchant, quest board.
- 3 agent archetypes:
  - **Grinder** (XP-first)
  - **Trader** (profit-first)
  - **Guardian** (protect weak players/agents)
- 1 social trigger: “help request” in local chat causes cooperative response.
- Story cards generated for:
  - first party formed
  - revenge kill
  - rare drop trade

### Build Steps
1. Implement tick loop + action queue.
2. Add combat/movement deterministic rules.
3. Add chat + party + trade verbs.
4. Implement archetype reflex behaviors.
5. Add event stream + timeline UI.
6. Add simple narrative ranker (rule-based).
7. Add replay for previous 15 minutes.

### Demo Script
- Start server with seeded world.
- Spawn 12 agents with mixed archetypes.
- Trigger mini world event (elite monster spawn).
- Spectator follows timeline and switches POV between agents.

---

## 9) Initial Code Skeleton Recommendations

### 9.1 Contracts First
- Define strict shared types before feature coding:
  - `ActionVerb`
  - `ActionIntent`
  - `WorldEvent`
  - `TickStateDiff`

### 9.2 Simulation Interfaces
```ts
interface SimulationEngine {
  enqueueIntent(intent: ActionIntent): void;
  tick(nowMs: number): TickResult;
  getSnapshot(): WorldSnapshot;
}

interface RuleModule {
  apply(state: WorldState, intent: ActionIntent): RuleResult;
}
```

### 9.3 Agent Interfaces
```ts
interface AgentPolicy {
  decide(ctx: AgentContext): AgentDecision;
}

interface ModelRouter {
  shouldEscalate(ctx: AgentContext): boolean;
  runDeliberation(input: DeliberationInput): Promise<DeliberationOutput>;
}
```

### 9.4 Event/Replay Interfaces
```ts
interface EventStore {
  append(events: WorldEvent[]): Promise<void>;
  readRange(zoneId: string, fromTick: number, toTick: number): Promise<WorldEvent[]>;
}

interface ReplayBuilder {
  build(zoneId: string, fromTick: number, toTick: number): Promise<ReplayArtifact>;
}
```

### 9.5 Minimal Implementation Tasks (Week 1)
- Bootstrap monorepo (pnpm + turborepo or nx).
- Create `packages/proto` with Zod validators.
- Stand up `apps/sim-server` tick loop with in-memory state.
- Stand up `apps/gateway` websocket relay.
- Build basic spectator page showing event feed.
- Add end-to-end smoke test: submit intent → tick resolves → event appears in UI.

### 9.6 Definition of Done (Initial Skeleton)
- One command boots sim, gateway, and spectator UI.
- 1000-tick deterministic replay test passes.
- All actions/events validated against shared schema.
- Structured logs include tick, actor, verb, result, and latency.

---

## Suggested Team Split (Small Team)
- **Engineer A**: Simulation + rule modules.
- **Engineer B**: Gateway + replay + event store.
- **Engineer C**: Agent orchestrator + policy engine.
- **Engineer D/Design hybrid**: Spectator UX + narrative cards + ops console lite.
- **Shared**: schema/contracts and observability standards.

## Practical Next Step (Tomorrow)
1. Approve MVP scope and vertical slice acceptance criteria.
2. Freeze action/event schema v0.
3. Build deterministic sim prototype with 3 verbs (`move`, `attack`, `chat`).
4. Pipe events to a very simple spectator timeline.
5. Run a 2-hour autonomous soak test and inspect story density.
