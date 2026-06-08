# Hermes adapter for core-doctor

Use `skills/life-os/runtimes/hermes.md` as the central Hermes runtime adapter.

Core-doctor validates both Life OS private state and Hermes visibility. It is read-only unless the user explicitly asks for a repair.

## Read-only checks

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
python3 scripts/lifeos.py doctor
```

## Interpretation

- Missing `life-os` in Hermes is a profile/skill visibility issue, not a private-state failure.
- Hermes cron, memory, gateway, tools, profiles, plugins, config, and sessions remain Hermes-owned.
- Report runtime-owned systems and source decisions, then recommend leave/bridge/reference/create runtime-native store/reconnect references as appropriate. Do not change anything without approval.
- Do not use hard-coded Hermes paths as doctor logic; use native commands and docs.
