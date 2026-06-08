---
name: tasks-todo
description: Help with task capture/review while keeping the task source in the runtime or selected external store.
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

Runtime task systems stay runtime-owned unless the user explicitly chooses a different source. This skill may:

- discover where tasks live
- record `sources.tasks` in Life OS config, including access instructions
- read runtime/external tasks when the runtime exposes them
- write Life OS operational state such as last review time, priority scores, suppression windows, and caches
- propose task updates
- update runtime/external tasks only when the user explicitly asked and the runtime tool is available

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

During install, do not globally register this subskill by default. If the user wants `tasks-todo` directly callable, ask first and handle it as a runtime adapter visibility decision. The helper does not record or perform global registration; it only creates private Life OS state containers.

Runtime-specific registration remains an adapter step. Load the matching runtime adapter before telling the user how to expose `tasks-todo` globally.

## State update

When a task review materially changes the user's active plan, record operational state and pointers in private state/config. Do not store raw private task dumps unless the item is explicitly a Life OS note or the user chose Life OS as the task source.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/tasks-todo/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
