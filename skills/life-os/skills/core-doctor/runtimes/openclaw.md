# OpenClaw adapter for core-doctor

Use `skills/life-os/runtimes/openclaw.md` as the central OpenClaw runtime adapter.

Core-doctor should validate both Life OS state and OpenClaw visibility:

```bash
openclaw skills list | grep -E 'life-os|tasks-todo'
openclaw skills info life-os
openclaw skills check
python3 scripts/lifeos.py doctor
```

For agent-scoped checks, add `--agent <id>` to OpenClaw skill commands. Report missing OpenClaw visibility as a runtime registration issue, not as missing Life OS private state. Do not change OpenClaw agents, workspaces, channel routes, automation, or config during doctor unless the user explicitly asks.
