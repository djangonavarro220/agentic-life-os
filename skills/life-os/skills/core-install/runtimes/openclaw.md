# OpenClaw adapter for core-install

Use `skills/life-os/runtimes/openclaw.md` as the central OpenClaw install and skill-visibility adapter.

Core-install should:

1. Check `openclaw skills list` before registering anything.
2. Use `--agent <id>` for agent-specific checks when the user names an OpenClaw agent.
3. If `life-os` is already visible, run only `lifeos.py install --runtime openclaw` and `lifeos.py doctor` from the repo checkout.
4. If `life-os` is not visible, ask workspace vs shared managed install, then ask copy vs symlink.
5. Verify with `openclaw skills list`, `openclaw skills info life-os`, `openclaw skills check`, and `lifeos.py doctor`.

Do not create OpenClaw automation jobs, channel routes, credentials, memory entries, or agent config changes during core-install.
