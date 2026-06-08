---
name: system-improvement
description: Improve the Life OS system itself through retrospectives, skill backlog triage, new-skill proposals, and safe maintenance planning.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# system-improvement

Improve Life OS itself without turning every annoyance into a refactor. This skill is the system's own feedback loop: inspect how the last period went, identify missing playbooks or broken routines, decide what should become a skill, and propose small safe improvements.

## Trigger

Use for:

- system self-improvement reviews
- retrospectives about how Life OS has worked recently
- sprint-review-style summaries of the last week or cycle
- deciding whether repeated work should become a new skill, template, routine, or runtime adapter
- reviewing stale, noisy, missing, or low-value routines
- maintaining a Life OS improvement backlog

Do not use this for normal user tasks, product hype, or broad rewrites. A good system review produces a small number of concrete improvements, not a manifesto.

## Inputs to inspect

Use only configured and approved sources. Useful inputs may include:

- recent Life OS routine run records or pointers
- user feedback captured in runtime-owned memory, tasks, notes, or issue trackers
- repeated manual requests that look like reusable workflows
- doctor warnings, failed cron/routine runs, or stale setup questions
- skill-index gaps and missing playbooks
- public repo issues or local improvement backlog if configured
- private state under `$LIFEOS_DATA_DIR/system-improvement/data.json`

Do not copy raw chats, logs, transcripts, or private runtime exports into Life OS state. Store pointers and distilled observations.

## Review cadence

Default cadence: weekly, often as a section inside the weekly review. Monthly or quarterly reviews can include a deeper system-health pass.

A lightweight weekly review should ask:

1. What did Life OS help with this period?
2. Where did it create noise, miss context, or require repeated manual steering?
3. Which repeated tasks deserve a new skill, template, checklist, or runtime adapter?
4. Which routines should be quieter, louder, paused, or deleted?
5. What is the smallest next improvement that would reduce future steering?

## Output contract

Default shape:

```text
System review:
- Worked: ...
- Friction: ...
- Skill candidates: ...
- Routine changes: ...
- Proposed next improvement: ...
```

Keep it brutally small. Prefer one improvement that will actually ship over ten clever ideas that rot.

## Skill candidate policy

A repeated workflow may become a skill when at least one is true:

- the user repeated the same steering several times
- the task needs 5+ steps or a known pitfall checklist
- the workflow crosses runtime tools and needs source-of-truth rules
- an error was fixed through a non-obvious procedure worth reusing
- a routine needs a stable output contract or safety boundary

Before creating or editing a public skill:

- keep examples generic and language-neutral
- avoid private names, paths, chat IDs, schedules, credentials, or exact user phrasing
- prefer patching an existing umbrella or subskill before adding a narrow sibling
- add validation or regression checks for leak classes when relevant
- ask before public pushes, broad refactors, runtime config changes, or history rewrites

## State update

After a system review, record only safe tracking metadata when useful:

- review date and horizon
- pointers to source records inspected
- small improvement backlog items
- accepted/rejected skill candidates with rationale
- routine tuning decisions and suppression windows
- links or pointers to issues/PRs if the runtime owns them

Do not store raw private conversations or full logs.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/system-improvement/data.json
```

Do not commit personal data, credentials, private runtime config, raw logs, transcripts, screenshots, audio, or real delivery targets.
