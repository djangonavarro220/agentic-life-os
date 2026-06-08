# Hermes adapter for core-doctor

Use `skills/life-os/runtimes/hermes.md` as the central Hermes runtime adapter.

Core-doctor should validate both Life OS state and Hermes visibility:

```bash
hermes skills list --source all | grep -E 'life-os|tasks-todo'
hermes skills inspect life-os
python3 scripts/lifeos.py doctor
```

Report missing Hermes visibility as a runtime registration issue, not as missing Life OS private state. Do not change Hermes config, tools, cron jobs, delivery routes, or profiles during doctor unless the user explicitly asks.
