# Hermes adapter for integrations-runtime

Use `skills/life-os/runtimes/hermes.md` as the central Hermes runtime adapter.

For this subskill, Hermes-specific work means discovering or using Hermes-owned capabilities without copying them into Life OS state:

- `hermes skills list/info/inspect` for skill availability
- `hermes cron` or the runtime cron tool for schedules
- Hermes platform delivery config for Telegram, Discord, and other channels
- Hermes profile and tool configuration for capability checks
- Hermes memory/vault/provider config as runtime-owned pointers only

Do not store Hermes secrets, delivery targets, raw memories, or profile-private config in this repo or in Life OS data files.
