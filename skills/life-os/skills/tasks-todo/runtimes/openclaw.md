# OpenClaw adapter for tasks-todo

Use `skills/life-os/runtimes/openclaw.md` as the central OpenClaw runtime adapter.

Check whether `tasks-todo` is already visible before registering it globally:

```bash
openclaw skills list | grep -E 'life-os|tasks-todo'
openclaw skills info tasks-todo
openclaw skills check
```

For agent-scoped checks, add `--agent <id>`. If `tasks-todo` is not visible but `life-os` is visible, prefer using it through the umbrella skill unless the user explicitly wants `tasks-todo` exposed to an OpenClaw workspace, shared skill folder, or agent-specific skill list.

Task storage and workspace TODO conventions remain OpenClaw-owned unless explicitly bridged through private Life OS state pointers.
