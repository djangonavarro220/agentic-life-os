# Life OS runtime cron templates

These are templates only. Do not create runtime cron jobs until the user has answered the semantic setup questions and approved cadence plus delivery.

Use `python3 scripts/lifeos.py plan` for the machine-readable version.

## Daily pulse

- name: `life-os-daily-pulse`
- schedule: `0 9 * * *`
- skills: `life-os`, `routines-pulse`
- delivery: runtime-owned destination selected during setup
- no-news behavior: follow saved delivery policy, silence is valid

Prompt:

```text
Run the Life OS daily pulse. Read semantic_setup first. If setup is incomplete, report the next missing decision instead of pretending the routine is live. If there is no actionable change, stay silent according to the saved delivery policy.
```

## Quiet heartbeat

- name: `life-os-quiet-heartbeat`
- schedule: `every 3h`
- skills: `life-os`, `routines-heartbeat`
- delivery: runtime-owned destination selected during setup
- no-news behavior: `[SILENT]`

Prompt:

```text
Run the Life OS quiet heartbeat. Read semantic_setup first, then check only the sources configured in the relevant skill data files. Return [SILENT] unless the saved policy says a change is actionable.
```

## Weekly review

- name: `life-os-weekly-review`
- schedule: `0 18 * * 0`
- skills: `life-os`, `routines-weekly-review`
- delivery: runtime-owned destination selected during setup

Prompt:

```text
Run the Life OS weekly review. Read semantic_setup and the relevant skill-owned source pointers. Summarize only decisions, risks, waiting items, and next actions.
```
