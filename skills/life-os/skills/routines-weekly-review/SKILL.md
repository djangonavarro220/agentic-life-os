---
name: routines-weekly-review
description: Weekly review routine for commitments, priorities, due review items, and system-improvement candidates.
version: 0.2.0
author: Agentic Life OS contributors
license: MIT
---

# routines-weekly-review

Run the weekly review as a guided meeting, not as a dashboard dump. This is the medium-speed loop: slower than heartbeat or a daily briefing, faster than monthly or quarterly resets.

The weekly review should gather due review items, ask one focused question at a time, and end with a compact set of decisions and next actions.

## Trigger

Use for:

- scheduled weekly review routines
- weekly commitment and task review
- checking stale waiting items and blockers
- reviewing people/follow-up obligations
- reviewing review items whose cadence makes them due this week
- identifying repeated friction that should feed `system-improvement`

Do not use this for deep quarterly direction setting or tiny status checks.

## Review items

A weekly review is a container for due review items, not a fixed monolith. Review items may include:

- review what happened since the last review
- decide what should happen next week
- review active and waiting commitments
- inspect stale tasks or blockers
- review heartbeat candidates and noisy active watch targets
- inspect weekly-only domains or skills
- hand off repeated friction to `system-improvement`

Each review item should have its own cadence, skip policy, and rough size. If a user changes heartbeat tuning from weekly to monthly, the weekly review should stop asking about it until it is due again.

## Inputs to inspect

Use configured runtime-owned sources and Life OS pointers, for example:

- active and waiting tasks
- commitments and follow-ups
- recent daily briefing and heartbeat outputs
- calendar/deadline summaries if configured
- decision-journal items due for review
- review-item cadence and due-item records
- system-improvement backlog or recent friction notes

Read enough to decide what changed. Do not copy raw private logs into state.

## Guided meeting behavior

Prefer a multi-step guided meeting over one huge message when more than one meaningful review item is due.

1. Start with a short opening and the first focused question.
2. After the user answers, update private meeting state and move to the next due review item.
3. Ask one question at a time.
4. Allow skip, pause, resume, or stop.
5. If the meeting is paused or the user stops replying, record paused/in-progress guided meetings in private state or the runtime task system.
6. Let `context-now` resurface paused meetings later as active context, rather than losing them.
7. Finish with a compact closing summary: decisions, waiting items, next actions, and any routine tuning.

A weekly review should feel like a useful meeting, not like a report the user must parse.

## Reasoning steps

1. Identify which review items are due.
2. Rank them by urgency and expected value.
3. Ask only the first useful question if interaction is needed.
4. Identify commitments due, overdue, or blocked.
5. Prune stale tasks and waiting items only through the configured runtime source and approval policy.
6. Surface 1-5 decisions or next actions for the coming week.
7. Detect repeated manual steering, failed routines, noisy alerts, or missing playbooks.
8. If system issues exist, hand off a short section to `system-improvement` instead of burying them in generic review text.

## Output contract

Opening shape:

```text
Weekly review:
- Starting with: ...
- Question: ...
```

Closing shape:

```text
Weekly review complete:
- Decisions: ...
- Waiting / blocked: ...
- Next week: ...
- Routine changes: ...
```

Omit empty sections. The system-improvement section should be short: heartbeat candidates, skill candidates, routine tuning, or setup gaps only.

## State update

After each step, record safe tracking metadata when useful:

- meeting id and status: active, paused, complete, expired
- current review item
- due review items remaining
- source pointers inspected
- decisions made
- next question
- pause/resume hints

Put system-improvement backlog entries in `$LIFEOS_DATA_DIR/system-improvement/data.json`, not in the weekly review data file.

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/routines-weekly-review/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
