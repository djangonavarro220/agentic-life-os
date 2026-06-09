---
name: routines-daily-review
description: Daily briefing routine for same-day focus, waiting items, risks, and the next action.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# routines-daily-review

Run a short daily briefing. This is a compact note, not a guided meeting unless the user asks to go deeper.

## Trigger

Use for:

- daily morning or evening check-ins
- same-day focus
- quick review of waiting items and risks
- deciding the next action

Do not use this for weekly planning, monthly reset, or system-wide retrospectives.

## Behavior

Keep the daily briefing short. It may inspect configured task, calendar, memory/context, and recent routine pointers, but it should surface only what changes the user's day.

If an unfinished guided meeting is important today, mention it briefly and offer to resume it. Do not restart the whole meeting automatically.

## Output contract

```text
Daily briefing:
- Focus: ...
- Waiting on: ...
- Risk: ...
- Next action: ...
```

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/routines-daily-review/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
