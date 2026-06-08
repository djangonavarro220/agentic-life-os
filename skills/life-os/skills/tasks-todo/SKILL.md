---
name: tasks-todo
description: Manage tasks and todos; may optionally be registered globally by a runtime.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# tasks-todo

Manage Life OS task state and pointers without replacing the runtime's native task systems unless the user explicitly chooses that integration.

## Install behavior

`tasks-todo` is part of Life OS. During install, ask whether the user also wants this skill registered globally for the current runtime.

Record the preference with:

```bash
python3 scripts/lifeos.py install --runtime hermes --global-tasks-todo
```

The helper records the preference but does not mutate runtime skill registration by itself. Runtime-specific registration remains an adapter step.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/tasks-todo/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
