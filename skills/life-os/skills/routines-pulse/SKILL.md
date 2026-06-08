---
name: routines-pulse
description: Daily proactive briefing routine.
version: 0.2.0
author: Agentic Life OS contributors
license: MIT
---

# routines-pulse

Produce the daily proactive briefing. Pulse is not a giant summary; it is a short decision surface for the day.

## Trigger

Use for:

- daily scheduled briefing
- “give me my pulse”
- morning/evening catch-up when the user wants proactive synthesis

Do not use Pulse for tiny status checks. Use `routines-heartbeat` for silent monitoring and `context-now` for immediate focus.

## Inputs to inspect

Use enabled runtime-owned sources and Life OS pointers, for example:

- current task/TODO state
- upcoming calendar/deadlines if configured
- commitments/follow-ups
- recent heartbeat changes
- user-approved mail/inbox summaries
- project or routine state in `$LIFEOS_DATA_DIR`

Never copy raw private content into the public repo. Avoid large transcript dumps. Read enough to decide what matters.

## Reasoning steps

1. Determine the briefing horizon: today by default.
2. Find hard constraints: meetings, deadlines, due commitments, time-sensitive tasks.
3. Find soft opportunities: follow-ups, gifts, health/life admin, project momentum.
4. Drop stale/noisy items unless they changed or block something.
5. Choose 1-3 concrete next actions.
6. Mark uncertainty explicitly when source data is thin.

## Output contract

Default shape:

```text
Pulse:
- Today: ...
- Actions: ...
- Waiting/blockers: ...
- Watch: ...
```

Rules:

- Keep it compact.
- Prefer actions over trivia.
- Do not include “nothing to report” sections.
- If no actionable changes exist, return a short no-op or silence, depending on runtime policy.

## State update

After producing or intentionally skipping a pulse, record a safe summary:

```bash
python3 scripts/lifeos.py run pulse --summary "<short pulse summary>"
```

The summary should be tracking metadata, not raw mail/calendar/memory content.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/routines-pulse/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
