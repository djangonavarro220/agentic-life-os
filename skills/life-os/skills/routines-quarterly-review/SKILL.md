---
name: routines-quarterly-review
description: Quarterly reset routine for strategic direction, slow assumptions, and larger Life OS cleanup.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# routines-quarterly-review

Run the quarterly reset as a guided meeting for slower, larger questions. This is not a daily focus note and not a weekly task cleanup.

## Trigger

Use for:

- scheduled quarterly reset routines
- strategic direction checks
- slow assumptions and stale commitments
- larger Life OS cleanup or routine architecture review
- review items whose cadence is quarterly

## Behavior

A quarterly reset should gather due review items and walk through them one at a time. It should allow pause/resume and record paused/in-progress guided meetings in private state so `context-now` can resurface them.

Possible review items:

- strategic priorities
- major commitments and stale assumptions
- long-running domains that drift slowly
- skill set health and routine mix
- whether monthly/weekly/daily cadences still fit

## Output contract

Opening shape:

```text
Quarterly reset:
- Starting with: ...
- Question: ...
```

Closing shape:

```text
Quarterly reset complete:
- Decisions: ...
- Direction: ...
- Next actions: ...
```

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/routines-quarterly-review/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
