# ai-mmoprg monorepo scaffold

Initial TypeScript workspace layout:

- `apps/client`: player-facing client placeholder
- `apps/server`: backend service entrypoint
- `apps/admin`: operations/admin placeholder
- `packages/shared`: common types/utilities
- `packages/protocol`: wire protocol contracts
- `packages/agent-runtime`: runtime primitives for autonomous agents

## Quick start

```bash
npm install
npm run dev:server
```

Additional scripts:

- `npm run dev` runs all workspace dev scripts in parallel.
- `npm run build` compiles all workspaces.
- `npm run typecheck` runs TypeScript checks across workspaces.
