---
name: routines-heartbeat
description: Low-noise routine for checking signals and updating tracking state.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# routines-heartbeat

Run a quiet, frequent check for actionable changes. This routine exists to prevent dropped commitments and stale state, not to send “I checked and nothing happened” spam.

This is a dynamic heartbeat, not a fixed checklist. It should discover the runtime's current capability inventory, choose relevant active watch targets, perform dynamic skill loading for the adapters needed in this run, and stay silent unless something actionable changed.

## Trigger

Use for:

- scheduled frequent checks
- “watch this quietly” requests
- follow-up monitoring where silence is acceptable
- detecting changed state since the last run

Do not use for deep weekly review, full daily briefing, or open-ended life planning. Those belong to `routines-pulse`, `routines-weekly-review`, or `context-now`.

## Inputs to inspect

Load only sources configured in the relevant skill data files under `$LIFEOS_DATA_DIR/<skill-name>/data.json` and the global `runtime_inventory` in `$LIFEOS_DATA_DIR/config.json`. Runtime-owned sources may include:

- runtime TODO/task system
- runtime cron/job state
- recent Life OS private state
- active watch targets approved by the user or runtime policy
- user-provided watch targets
- mail/calendar only if explicitly configured by the runtime/user

Do not scrape every possible source. Cheap and relevant beats exhaustive and noisy. Also do not hard-code a universal list of checks: the heartbeat should look at configured watch targets and the capability inventory, then select the smallest useful set for this run.

## Capability inventory and dynamic loading

The capability inventory records what the active runtime can do and how to reach it:

- skill sources and skill names, for example mail, calendar, tasks, cron, memory, health, finance, or travel adapters;
- tool sources, if the runtime exposes tools separately from skills;
- source pointers and access notes;
- active watch targets with cadence, alert condition, no-news policy, and last-observed pointer;
- missing capabilities that should be proposed to the user instead of guessed.

Execution pattern:

1. Read `runtime_inventory` and active watch targets.
2. Pick the watch targets due or changed enough to inspect now.
3. Dynamically load only the skills/adapters needed for those targets.
4. If a needed skill, toolset, permission, or source is missing, record/report the gap and propose a setup or cron update; do not improvise from memory.
5. Run the selected checks and update safe tracking state.

For example, mail/calendar access should be done by a runtime mail/calendar adapter, not by copying Gmail rules into this skill. Tasks should use the runtime task adapter. Cron/service health should use the runtime operations/governance adapter. Life OS coordinates; runtime adapters execute access.

## Watch target lifecycle

Heartbeat should distinguish candidate watch targets from active watch targets:

- candidate watch targets are proposals produced by `system-improvement`, reviews, or user discussion;
- active watch targets are approved checks with a source, cadence, alert condition, no-news policy, and last-observed pointer;
- candidate watch targets do not run automatically unless the user or saved runtime policy approves them;
- active watch targets should be removed, paused, or retuned when they stop producing useful alerts.

Heartbeat executes active checks. It does not decide that a whole new domain should be monitored by itself, but it may discover a missing useful capability and propose it as a candidate watch target.

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

When a heartbeat observes a meaningful change, record safe tracking metadata only when the current runtime policy allows it. Use Life OS private state or runtime-native state as appropriate; do not use helper scripts to decide or perform semantic monitoring behavior.

The summary should be safe tracking metadata, not raw private content.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/routines-heartbeat/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
