---
name: core-install
description: Install and register Agentic Life OS for the current runtime.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# core-install

Install Agentic Life OS private state for the current runtime.

## Procedure

For a fresh local Hermes install from the public repo:

```bash
git clone https://github.com/djangonavarro220/agentic-life-os.git
cd agentic-life-os
mkdir -p "$HOME/.hermes/skills/productivity"
ln -sfn "$PWD/skills/life-os" "$HOME/.hermes/skills/productivity/life-os"
python3 scripts/lifeos.py install --runtime hermes
python3 scripts/lifeos.py doctor
hermes skills list --source local | grep -E 'life-os|tasks-todo'
```

If the repo is already checked out and the skill is already installed, run from the repo root:

```bash
python3 scripts/lifeos.py install --runtime hermes
python3 scripts/lifeos.py doctor
```

Use `--data-dir <path>` only when the user wants a non-default private data directory. Use `--global-tasks-todo` only after the user agrees that `tasks-todo` should be registered globally by the runtime.

Re-running install is idempotent and preserves existing `config.json` choices. It does not unset an earlier `--global-tasks-todo` choice.

## What install creates

- `$LIFEOS_DATA_DIR/installed.json`
- `$LIFEOS_DATA_DIR/runtime.json`
- `$LIFEOS_DATA_DIR/config.json`
- `$LIFEOS_DATA_DIR/<skill-name>/data.json` for every indexed subskill

## Boundaries

Install does not create runtime crons, delivery routes, credentials, memory entries, vault entries, mail config, or calendar config. Those are runtime-owned and require explicit user approval.

The symlink above registers only the `life-os` skill with Hermes. Runtime-wide scheduling, delivery, and global registration policy remain explicit follow-up steps, not hidden installer side effects.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/core-install/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
