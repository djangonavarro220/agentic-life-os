# Hermes adapter for tasks-todo

Use `skills/life-os/runtimes/hermes.md` as the central Hermes runtime adapter.

Check whether `tasks-todo` is already visible before registering it globally:

```bash
hermes skills list --source all | grep -E 'life-os|tasks-todo'
hermes skills inspect tasks-todo
```

If `tasks-todo` is not visible but `life-os` is visible, prefer using it through the umbrella skill unless the user explicitly wants `tasks-todo` globally callable. Any Hermes global registration should follow the same profile/symlink/copy rules as `life-os`.

Task storage and durable TODO integrations remain runtime-owned unless explicitly bridged through private Life OS state pointers.
