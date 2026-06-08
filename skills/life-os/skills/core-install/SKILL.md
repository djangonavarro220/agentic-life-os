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

From the repo root:

```bash
python3 scripts/lifeos.py install --runtime hermes
```

Use `--data-dir <path>` only when the user wants a non-default private data directory. Use `--global-tasks-todo` only after the user agrees that `tasks-todo` should be registered globally by the runtime.

## What install creates

- `$LIFEOS_DATA_DIR/installed.json`
- `$LIFEOS_DATA_DIR/runtime.json`
- `$LIFEOS_DATA_DIR/config.json`
- `$LIFEOS_DATA_DIR/<skill-name>/data.json` for every indexed subskill

## Boundaries

Install does not create runtime crons, delivery routes, credentials, memory entries, vault entries, mail config, or calendar config. Those are runtime-owned and require explicit user approval.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/core-install/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
