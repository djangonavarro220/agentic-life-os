---
name: routines-weekly-review
description: Weekly review routine for commitments, priorities, stale tasks, and system-improvement candidates.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# routines-weekly-review

Run a weekly review. This is the medium-speed loop: slower than heartbeat/pulse, faster than monthly planning. It should produce a small set of decisions and next actions, not a dashboard dump.

## Trigger

Use for:

- scheduled weekly review routines
- weekly commitment and task review
- checking stale waiting items and blockers
- reviewing people/follow-up obligations
- identifying repeated friction that should feed `system-improvement`

Do not use this for deep quarterly direction setting or tiny status checks.

## Inputs to inspect

Use configured runtime-owned sources and Life OS pointers, for example:

- active and waiting tasks
- commitments and follow-ups
- recent pulse and heartbeat outputs
- calendar/deadline summaries if configured
- decision-journal items due for review
- system-improvement backlog or recent friction notes

Read enough to decide what changed. Do not copy raw private logs into state.

## Reasoning steps

1. Identify commitments due, overdue, or blocked.
2. Prune stale tasks and waiting items.
3. Surface 1-5 decisions or next actions for the coming week.
4. Detect repeated manual steering, failed routines, noisy alerts, or missing playbooks.
5. If system issues exist, hand off a short section to `system-improvement` instead of burying them in generic review text.

## Output contract

Default shape:

```text
Weekly review:
- Done / moved: ...
- Waiting / blocked: ...
- Decisions: ...
- Next week: ...
- System improvement: ...
```

Omit empty sections. The system-improvement section should be short: skill candidates, routine tuning, or setup gaps only.

## State update

After a review, record safe tracking metadata when useful: review date, source pointers inspected, decisions made, stale items pruned, and links/pointers to follow-up records. Put system-improvement backlog entries in `$LIFEOS_DATA_DIR/system-improvement/data.json`, not in the weekly review data file.

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/routines-weekly-review/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
