---
name: routines-heartbeat
description: Low-noise routine for checking signals and updating tracking state.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# routines-heartbeat

Run a quiet, frequent check for actionable changes. This routine exists to prevent dropped commitments and stale state, not to send “I checked and nothing happened” spam.

## Trigger

Use for:

- scheduled frequent checks
- “watch this quietly” requests
- follow-up monitoring where silence is acceptable
- detecting changed state since the last run

Do not use for deep weekly review, full daily briefing, or open-ended life planning. Those belong to `routines-pulse`, `routines-weekly-review`, or `context-now`.

## Inputs to inspect

Load only sources enabled in `$LIFEOS_DATA_DIR/config.json`. Runtime-owned sources may include:

- runtime TODO/task system
- runtime cron/job state
- recent Life OS private state
- user-provided watch targets
- mail/calendar only if explicitly configured by the runtime/user

Do not scrape every possible source. Cheap and relevant beats exhaustive and noisy.

## Decision rules

Send visible output only when at least one is true:

- a commitment is newly overdue or about to become expensive
- a watched item changed materially
- a runtime job failed or delivery broke
- a task needs user decision to unblock
- a previously recorded blocker cleared

Stay silent when:

- nothing changed
- all changes are non-actionable
- the only output would be “still waiting”

## Output contract

If visible output is needed:

```text
Heartbeat:
- Change: ...
- Why it matters: ...
- Suggested action: ...
```

Keep it short. One concrete alert is better than a dashboard dump.

## State update

After a run, record a short summary with:

```bash
python3 scripts/lifeos.py run heartbeat --summary "<short status>"
```

The summary should be safe tracking metadata, not raw private content.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/routines-heartbeat/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
