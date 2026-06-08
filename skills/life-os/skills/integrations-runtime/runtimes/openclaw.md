# OpenClaw adapter for integrations-runtime

Use `skills/life-os/runtimes/openclaw.md` as the central OpenClaw runtime adapter.

For this subskill, OpenClaw-specific work means discovering or using OpenClaw-owned capabilities without copying them into Life OS state:

- `openclaw skills list/info/check` for skill availability
- OpenClaw agents and workspace config for skill visibility
- OpenClaw cron or automation mechanisms for schedules
- OpenClaw channel routing for delivery
- OpenClaw memory/vault/provider config as runtime-owned pointers only

Do not store OpenClaw secrets, channel targets, raw memories, sessions, or agent-private config in this repo or in Life OS data files.
