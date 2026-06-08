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

First check whether the runtime already has the `life-os` skill installed. If it is installed, do not re-register it. Run the state install from the existing checkout:

```bash
python3 scripts/lifeos.py install --runtime hermes
python3 scripts/lifeos.py doctor
```

For a fresh local Hermes install where the skill is not installed yet, clone the repo, then ask the user whether they prefer a symlink or a copied skill. Symlink is best for development because updates to the checkout immediately update the installed skill. Copy is safer if the user wants a static local snapshot.

Hermes symlink option:

```bash
git clone https://github.com/djangonavarro220/agentic-life-os.git
cd agentic-life-os
mkdir -p "$HOME/.hermes/skills/productivity"
ln -sfn "$PWD/skills/life-os" "$HOME/.hermes/skills/productivity/life-os"
python3 scripts/lifeos.py install --runtime hermes
python3 scripts/lifeos.py doctor
hermes skills list --source local | grep -E 'life-os|tasks-todo'
```

Hermes copy option:

```bash
git clone https://github.com/djangonavarro220/agentic-life-os.git
cd agentic-life-os
mkdir -p "$HOME/.hermes/skills/productivity"
cp -R skills/life-os "$HOME/.hermes/skills/productivity/life-os"
python3 scripts/lifeos.py install --runtime hermes
python3 scripts/lifeos.py doctor
hermes skills list --source local | grep -E 'life-os|tasks-todo'
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

Symlink/copy registration is Hermes-specific. Other runtimes should use their own skill-install mechanism and then run the helper from the repo checkout. Runtime-wide scheduling, delivery, and global registration policy remain explicit follow-up steps, not hidden installer side effects.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/core-install/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
