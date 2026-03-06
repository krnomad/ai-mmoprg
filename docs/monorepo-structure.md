# Monorepo Structure Blueprint

This layout is designed for a game-oriented AI MMO project with clear boundaries between UI apps, backend services, and reusable packages.

## Proposed Directory Layout

```text
.
├── apps/
│   ├── client/
│   ├── server/
│   └── admin/
├── packages/
│   ├── shared/
│   ├── agent-runtime/
│   ├── protocol/
│   └── config/
└── docs/
```

---

## Folder-by-Folder Guidance

### `apps/client`

**Purpose**
- Player-facing application (web or desktop shell) for gameplay UI, sessions, chat, inventory, map, and combat interfaces.

**Key modules**
- `src/app`: app bootstrapping, routing, layout shell
- `src/features/*`: gameplay domain features (chat, party, inventory, combat)
- `src/network`: protocol client adapters, websocket/http clients
- `src/state`: global client state, caching, and synchronization
- `src/ui`: shared UI components and design-system wrappers

**What should not go there**
- Backend business logic or data persistence code
- Admin-only tools and dashboards
- Runtime agent orchestration logic
- Protocol schema source-of-truth files (consume from `packages/protocol`)

### `apps/server`

**Purpose**
- Core backend for game simulation, authentication, player state, matchmaking, and real-time event distribution.

**Key modules**
- `src/bootstrap`: server startup, DI/container wiring
- `src/modules/auth`: auth/session APIs
- `src/modules/game`: simulation loop, world state, combat resolution
- `src/modules/player`: progression, inventory, economy services
- `src/transport`: REST, websocket, RPC adapters
- `src/infrastructure`: db adapters, message brokers, external services

**What should not go there**
- Client rendering/UI code
- Shared type definitions duplicated from `packages/protocol`
- Admin frontend code
- Test fixture data that belongs in dedicated test directories

### `apps/admin`

**Purpose**
- Internal operations console for moderation, telemetry, economy controls, content publishing, and support tooling.

**Key modules**
- `src/app`: admin app shell and route guards
- `src/features/moderation`: user sanctions, chat audits, reports
- `src/features/ops`: live ops controls, server toggles, announcements
- `src/features/content`: quests/items/event configuration forms
- `src/features/analytics`: KPI dashboards and drill-down views

**What should not go there**
- Direct DB scripts bypassing backend APIs
- Player-facing UX flows
- Core server domain logic (must stay in `apps/server`)

### `packages/shared`

**Purpose**
- Cross-cutting utilities and primitives used by multiple apps/packages.

**Key modules**
- `src/types`: generic utility types and value-object interfaces
- `src/utils`: pure functions (dates, IDs, formatting, math helpers)
- `src/errors`: normalized error classes/codes
- `src/logging`: logging contracts and common wrappers

**What should not go there**
- App-specific logic (client or server only)
- Protocol message contracts (belongs in `packages/protocol`)
- Environment loading logic (belongs in `packages/config`)

### `packages/agent-runtime`

**Purpose**
- Runtime abstractions for AI agent orchestration: decision loops, tool adapters, memory, and execution safeguards.

**Key modules**
- `src/runtime`: agent lifecycle manager and execution loop
- `src/planning`: planning strategies and task decomposition
- `src/tools`: tool registry, adapters, and permission policies
- `src/memory`: context stores, retrieval strategies, TTL policies
- `src/safety`: guardrails, output validation, fallback handlers

**What should not go there**
- Frontend-specific code
- Network protocol schema definitions
- Game server persistence concerns unrelated to agent runtime

### `packages/protocol`

**Purpose**
- Source of truth for inter-service and app-to-server contracts.

**Key modules**
- `src/schema`: API schemas, event payloads, versioned contracts
- `src/messages`: command/query/event type definitions
- `src/codegen`: generated clients/servers (if used)
- `src/compat`: compatibility and migration helpers

**What should not go there**
- Business logic implementation
- HTTP framework-specific route handlers
- Random shared utilities unrelated to contracts

### `packages/config`

**Purpose**
- Centralized configuration loading, validation, and environment profile management.

**Key modules**
- `src/env`: schema validation per app/runtime
- `src/profiles`: dev/stage/prod profile composition
- `src/feature-flags`: typed feature flag definitions
- `src/secrets`: secret access interfaces (not raw secret files)

**What should not go there**
- App runtime side effects unrelated to config parsing
- Business rules or domain logic
- Hard-coded secrets

### `docs`

**Purpose**
- Human-facing documentation: architecture, runbooks, RFCs, onboarding, and operational playbooks.

**Key modules**
- `architecture/`: system diagrams and bounded contexts
- `runbooks/`: production incident and maintenance procedures
- `rfc/`: proposal templates and accepted decisions
- `onboarding/`: setup and local development guides

**What should not go there**
- Source code intended for production runtimes
- Generated artifacts that can be rebuilt automatically
- Private credentials or sensitive dumps

---

## Naming Conventions

- **Packages and apps**: kebab-case (`agent-runtime`, `game-server`)
- **TypeScript files**: kebab-case (`combat-engine.ts`)
- **React components/classes**: PascalCase (`InventoryPanel.tsx`)
- **Variables/functions**: camelCase (`computeDamage`)
- **Constants/env keys**: UPPER_SNAKE_CASE (`MAX_PARTY_SIZE`, `DATABASE_URL`)
- **Events/messages**: domain-scoped dot naming (`player.inventory.updated`, `chat.message.sent`)
- **Database tables**: snake_case plural (`player_profiles`, `guild_members`)

---

## Environment Variable Strategy

- Keep a root `.env.example` with shared variables and per-app examples:
  - `apps/client/.env.example`
  - `apps/server/.env.example`
  - `apps/admin/.env.example`
- Use `packages/config` to validate env vars at startup with strict schemas.
- Prefix by ownership to reduce collisions:
  - `CLIENT_*`, `SERVER_*`, `ADMIN_*`, `AGENT_*`
- Separate **build-time** and **runtime** variables explicitly.
- Never read `process.env` directly in app code outside config package.
- Fail fast on missing/invalid required variables.

---

## Local Development Workflow

1. **Install dependencies** from repo root using a workspace-aware package manager.
2. **Bootstrap shared packages** first (`shared`, `protocol`, `config`, `agent-runtime`).
3. **Run code generation** for protocol clients/types if enabled.
4. **Start backend services** (`apps/server`) and dependencies (DB/queue/cache).
5. **Start frontend apps** (`apps/client`, `apps/admin`) against local server.
6. **Run full checks** before committing:
   - lint
   - typecheck
   - unit/integration tests
   - protocol compatibility checks

Recommended scripts at root:
- `dev:server`, `dev:client`, `dev:admin`
- `build`, `test`, `lint`, `typecheck`
- `dev` (orchestrates all required services via workspace tooling)

---

## Suggested Implementation Order

1. **`packages/protocol`**: establish stable contracts first.
2. **`packages/shared`**: add common types and utility foundations.
3. **`packages/config`**: enforce typed env/config management early.
4. **`packages/agent-runtime`**: define agent orchestration primitives.
5. **`apps/server`**: implement APIs and real-time backend on top of packages.
6. **`apps/client`**: integrate player UX with server + protocol contracts.
7. **`apps/admin`**: build operational tooling after server capabilities exist.
8. **`docs`**: continuously evolve architecture docs and runbooks in parallel.

This ordering minimizes rework by locking contracts and shared abstractions before app-specific implementation.
