# Life OS runtime cron templates

These are templates only. Do not create runtime cron jobs until the user has answered the semantic setup questions and approved cadence plus delivery.

Use `python3 scripts/lifeos.py plan` for the machine-readable version.

## Daily briefing

- name: `life-os-daily-briefing`
- schedule: `0 9 * * *`
- skills: `life-os`, `routines-pulse`
- delivery: runtime-owned destination selected during setup
- no-news behavior: follow saved delivery policy, silence is valid

Prompt:

```text
Run the Life OS daily briefing. Read semantic_setup first. If setup is incomplete, report the next missing decision instead of pretending the routine is live. Keep it short: today focus, waiting items, risks, and next action. If there is no actionable change, stay silent according to the saved delivery policy.
```

## Quiet heartbeat

- name: `life-os-quiet-heartbeat`
- schedule: `every 3h`
- skills: `life-os`, `routines-heartbeat`
- delivery: runtime-owned destination selected during setup
- no-news behavior: `[SILENT]`

Prompt:

```text
Run the Life OS quiet heartbeat. Read semantic_setup first, then check only active watch targets configured in the relevant skill data files. Candidate watch targets must be approved before becoming active. Return [SILENT] unless the saved policy says a change is actionable.
```

## Weekly review

- name: `life-os-weekly-review`
- schedule: `0 18 * * 0`
- skills: `life-os`, `routines-weekly-review`, `system-improvement`
- delivery: runtime-owned destination selected during setup

Prompt:

```text
Run the Life OS weekly review as a guided meeting. Read semantic_setup and the relevant skill-owned source pointers, gather due review items, ask one focused question at a time, and record paused/in-progress meeting state so context-now can resurface it. Summarize decisions, risks, waiting items, next actions, and a small system-improvement section with skill candidates or routine tuning only when useful.
```

## Monthly reset

- name: `life-os-monthly-reset`
- schedule: `0 18 1 * *`
- skills: `life-os`, `routines-monthly-review`, `system-improvement`
- delivery: runtime-owned destination selected during setup

Prompt:

```text
Run the Life OS monthly reset as a guided meeting. Gather due monthly review items, review slow-moving domains and stale routines, ask one focused question at a time, and record paused/in-progress meeting state instead of sending a dashboard dump.
```

## Quarterly reset

- name: `life-os-quarterly-reset`
- schedule: `0 18 1 */3 *`
- skills: `life-os`, `routines-quarterly-review`, `system-improvement`
- delivery: runtime-owned destination selected during setup

Prompt:

```text
Run the Life OS quarterly reset as a guided meeting. Gather due quarterly review items, review strategic direction and stale system assumptions, ask one focused question at a time, and record paused/in-progress meeting state instead of sending a dashboard dump.
```
