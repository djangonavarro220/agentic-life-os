---
name: tasks-todo
description: Manage tasks and todos; may optionally be registered globally by a runtime.
version: 0.2.0
author: Agentic Life OS contributors
license: MIT
---

# tasks-todo

Help the agent capture, clarify, prioritize, and review tasks without replacing the runtime's native task system by surprise.

## Trigger

Use when the user wants to:

- capture a task
- review or prioritize tasks
- convert a vague intention into next actions
- decide what can be done now vs later
- inspect tasks suitable for a context, such as voice/walking/screen-free work

## Task handling rules

For each task, distinguish:

- desired outcome
- next physical/digital action
- owner
- deadline or review date
- dependency/blocker
- context needed: screen, phone, errands, deep work, voice-only, waiting

If a task is vague, ask at most one lightweight clarification unless a safe default exists.

## Integration policy

Runtime task systems stay runtime-owned. This skill may:

- read runtime tasks when the runtime exposes them
- write Life OS tracking/pointers
- propose task updates
- update runtime tasks only when the user explicitly asked and the runtime tool is available

Do not silently migrate all tasks into Life OS data. That is how you create a second todo swamp. Terrible idea.

## Output contract

For capture:

```text
Captured:
- Task: ...
- Next action: ...
- Context: ...
```

For review:

```text
Tasks:
- Do now: ...
- Decide: ...
- Waiting: ...
- Later: ...
```

## Install behavior

`tasks-todo` is part of Life OS. During install, ask whether the user also wants this skill registered globally for the current runtime.

Record the preference with:

```bash
python3 scripts/lifeos.py install --runtime <hermes|openclaw> --global-tasks-todo
```

The helper records the preference but does not mutate runtime skill registration by itself. Runtime-specific registration remains an adapter step. Load the matching runtime adapter before telling the user how to expose `tasks-todo` globally.

## State update

When a task review materially changes the user's active plan, record a short summary in private state. Do not store raw private task dumps unless the runtime/user explicitly chose Life OS as the task store.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/tasks-todo/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
