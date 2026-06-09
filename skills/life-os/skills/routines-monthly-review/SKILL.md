---
name: routines-monthly-review
description: Monthly reset routine for slow-moving domains, stale routines, and due review items.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# routines-monthly-review

Run the monthly reset as a guided meeting when multiple meaningful review items are due. It should inspect slower-moving areas without becoming a giant report.

## Trigger

Use for:

- scheduled monthly reset routines
- monthly cleanup of stale tasks, routines, and source decisions
- review items whose cadence is monthly
- domains that do not need daily or weekly attention

## Behavior

A monthly reset is a container for due review items. Ask one focused question at a time, allow pause/resume, and record paused/in-progress guided meetings in private state so `context-now` can resurface them.

Possible review items:

- stale routine cleanup
- slow-moving personal or operational domains
- subscriptions, renewals, documents, household, finance, learning, or work areas when configured
- watch targets that should be reviewed monthly instead of weekly
- system-improvement backlog pruning

## Output contract

Opening shape:

```text
Monthly reset:
- Starting with: ...
- Question: ...
```

Closing shape:

```text
Monthly reset complete:
- Decisions: ...
- Cleanup: ...
- Next actions: ...
```

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/routines-monthly-review/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
