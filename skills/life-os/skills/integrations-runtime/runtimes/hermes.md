# Hermes adapter for integrations-runtime

Use `skills/life-os/runtimes/hermes.md` as the central Hermes runtime adapter.

For this subskill, Hermes-specific work means discovering or using Hermes-owned capabilities without copying them into Life OS state.

## Read-only discovery

```bash
hermes skills list --source all
hermes skills inspect life-os
hermes skills config
hermes cron list --all
hermes cron status
hermes memory status
hermes tools list
hermes profile list
hermes gateway status
hermes status --all
hermes config check
hermes plugins list
hermes mcp list
```

## Ownership

Hermes owns:

- skill visibility and enablement
- cron schedules and jobs
- delivery routes and gateway/platform state
- profiles
- tools and plugins
- MCP servers
- memory/vault/provider config
- sessions and transcripts

Life OS should usually bridge through Hermes tools/pointers. Do not store Hermes secrets, delivery targets, raw memories, transcripts, logs, or profile-private config in this repo or in Life OS data files.

Ask before any Hermes config edit, cron change, delivery change, memory write, skill registration, plugin/tool change, or migration/import.
