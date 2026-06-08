# Hermes adapter for core-install

Use `skills/life-os/runtimes/hermes.md` as the central Hermes install and skill-visibility adapter.

Core-install should:

1. Check `hermes skills list --source all` before registering anything.
2. If `life-os` is already visible, run only `lifeos.py install --runtime hermes` and `lifeos.py doctor` from the repo checkout.
3. If `life-os` is not visible, ask symlink vs copy and install into the selected Hermes profile's local skills directory.
4. Verify with `hermes skills list --source local` and `lifeos.py doctor`.

Do not create Hermes crons, delivery routes, credentials, memory entries, or profile changes during core-install.
