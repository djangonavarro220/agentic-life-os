# OpenClaw adapter for integrations-runtime

Use `skills/life-os/runtimes/openclaw.md` as the central OpenClaw runtime adapter.

For this subskill, OpenClaw-specific work means discovering or using OpenClaw-owned capabilities without copying them into Life OS state.

## Read-only discovery

```bash
openclaw skills list
openclaw skills info life-os
openclaw skills check
openclaw agents list --bindings
openclaw status --all
openclaw doctor
openclaw config file
openclaw config validate
openclaw cron list
openclaw tasks list
openclaw memory status
openclaw channels status
openclaw plugins list
```

For agent-scoped checks, add `--agent <id>` where supported.

## Ownership

OpenClaw owns:

- workspace/agent skill visibility
- agents and channel bindings
- cron schedules and Gateway automation
- task/background-work ledger
- delivery routes and channel plugins
- tools and sandboxing
- memory/vault/provider config
- sessions and transcripts

Life OS should usually bridge through OpenClaw tools/pointers. Do not store OpenClaw secrets, channel targets, raw memories, transcripts, logs, sessions, or agent-private config in this repo or in Life OS data files.

Ask before any OpenClaw config edit, cron change, delivery change, memory promotion/write, skill registration, plugin/tool change, repair command, or migration/import.
