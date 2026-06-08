# OpenClaw adapter for core-doctor

Use `skills/life-os/runtimes/openclaw.md` as the central OpenClaw runtime adapter.

Core-doctor validates both Life OS private state and OpenClaw visibility. It is read-only unless the user explicitly asks for a repair.

## Read-only checks

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
python3 scripts/lifeos.py doctor
```

For agent-scoped checks, add `--agent <id>` where supported:

```bash
openclaw skills list --agent <id>
openclaw skills info life-os --agent <id>
openclaw skills check --agent <id>
openclaw memory status --agent <id>
```

## Interpretation

- Missing `life-os` in OpenClaw is an agent/workspace/shared visibility issue, not a private-state failure.
- `openclaw tasks` is a background work ledger, not automatically a user task list.
- OpenClaw cron, agents, workspaces, channel routing, memory, plugins, config, and sessions remain OpenClaw-owned.
- Report runtime-owned systems and recommend leave/bridge/import/migrate, but do not change anything without approval.
- Do not run `openclaw doctor --repair` unless the user asks.
- Do not use hard-coded OpenClaw paths as doctor logic; use native commands and docs.
