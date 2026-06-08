---
name: core-install
description: Install and register Agentic Life OS for the current runtime.
version: 0.2.0
author: Agentic Life OS contributors
license: MIT
---

# core-install

Install Agentic Life OS private state for the current runtime.

## Procedure

1. Detect the runtime: Hermes or OpenClaw.
2. Load the matching runtime adapter:
   - `../../runtimes/hermes.md`
   - `../../runtimes/openclaw.md`
3. Check whether `life-os` is already visible to that runtime.
4. If it is already visible, do not re-register it. Run the state install from the repo checkout.
5. If it is not visible, ask where/how to register it using the runtime adapter: symlink or copy, workspace/profile/agent/shared scope.
6. Run install and doctor.
7. Verify using the runtime-native skills command.

## Existing installed skill

From the repo checkout:

```bash
python3 scripts/lifeos.py install --runtime <hermes|openclaw>
python3 scripts/lifeos.py doctor
```

## Hermes registration summary

Check availability:

```bash
hermes skills list --source all | grep -E 'life-os|tasks-todo'
hermes skills inspect life-os
```

Default local install target:

```text
$HOME/.hermes/skills/productivity/life-os/
```

Use `skills/life-os/runtimes/hermes.md` for the full symlink/copy flow and profile caveats.

## OpenClaw registration summary

Check availability:

```bash
openclaw skills list | grep -E 'life-os|tasks-todo'
openclaw skills info life-os
openclaw skills check
```

Common install targets:

```text
<workspace>/skills/life-os/
$HOME/.openclaw/skills/life-os/
```

Use `skills/life-os/runtimes/openclaw.md` for the full workspace/shared install flow, agent-scoped checks, and symlink/copy caveats.

## Options

Use `--data-dir <path>` only when the user wants a non-default private data directory.

Use `--global-tasks-todo` only after the user agrees that `tasks-todo` should be registered or exposed globally by the runtime.

Re-running install is idempotent and preserves existing `config.json` choices. It does not unset an earlier `--global-tasks-todo` choice.

## What install creates

- `$LIFEOS_DATA_DIR/installed.json`
- `$LIFEOS_DATA_DIR/runtime.json`
- `$LIFEOS_DATA_DIR/config.json`
- `$LIFEOS_DATA_DIR/<skill-name>/data.json` for every indexed subskill

## Boundaries

Install does not create runtime crons, delivery routes, credentials, memory entries, vault entries, mail config, or calendar config. Those are runtime-owned and require explicit user approval.

Skill registration is runtime-specific. Runtime-wide scheduling, delivery, and global registration policy remain explicit follow-up steps, not hidden installer side effects.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/core-install/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
