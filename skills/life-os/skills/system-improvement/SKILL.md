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
- reviewing heartbeat candidates and deciding which proposed checks deserve to become active watch targets
- reviewing review-item cadence so each recurring check runs daily, weekly, monthly, quarterly, manually, or only on change as appropriate
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

Default cadence: every two weeks. It can also run manually when the user asks how Life OS is working or after repeated friction.

The self-improvement meeting should review the whole setup map each time, but it should not report every source that still looks fine. Stay silent when nothing needs user input.

A lightweight review should ask internally:

1. What did Life OS help with this period?
2. Where did it create noise, miss context, or require repeated manual steering?
3. Which repeated tasks deserve a new skill, template, checklist, or runtime adapter?
4. Which routines should be quieter, louder, paused, or deleted?
5. Does the full setup map still match available tools, skills, memory/context, routine records, delivery options, and source pointers?
6. What is the smallest next improvement that would reduce future steering?

## Setup review

Self-improvement must treat semantic setup as revisable. Setup is not a one-time ceremony: the self-improvement meeting is where the agent deliberately reviews whether the saved setup map still matches the runtime.

During the self-improvement meeting, inspect the tools, skills, memory/context capabilities, routine records, delivery options, and configured source pointers that the active runtime exposes. Compare what is available now with the saved `semantic_setup`, `sources`, `policies`, and owning skill data.

Do not wait for random runtime discovery to notice this. The review itself should actively look for better sources or stale mappings.

Classify each setup finding:

- `same_source`: already covered, no action.
- `better_source`: likely replacement for an existing pointer.
- `new_source`: useful source not yet mapped.
- `obsolete_source`: saved pointer no longer works or is no longer preferred.
- `new_memory`: new runtime memory/context capability that may change where durable context lives.

For findings that would affect future behavior:

1. Explain the change in plain language.
2. Ask whether to update the setup map.
3. Do not silently rewrite source-of-truth decisions.
4. Save approved changes only after approval, using structured setup decisions such as `reuse_existing`, `propose_change`, `manual_only`, or `disabled`.
5. If the user rejects the change, record a short suppression note so the same proposal does not keep resurfacing.

Only surface items that are newly discovered, changed, broken, obsolete, or need user input. In other words, report only newly discovered or changed setup items that require a decision. Do not output a checklist of unchanged setup sources just to prove the review ran.

Plain-language output should say what changed and why it matters, for example: “I found a better place to read current tasks. Do you want Life OS to use it instead of the old pointer?” Do not expose raw config unless asked.

## Routine tuning

System improvement may propose heartbeat candidates, but it should not silently turn them into active monitoring. For each candidate, decide:

- what would be checked;
- why the user would care;
- how often it should run;
- what counts as a real change;
- when silence is preferred;
- when to revisit or delete the check.

Treat review-item cadence as a normal design object. A weekly review does not have to contain every weekly-ish activity forever. It can gather whichever review items are due, while each item keeps its own cadence and skip policy.

## Output contract

If nothing changed and nothing needs input, output nothing. Silence is the success path for a scheduled self-improvement review.

When there are changes needing input, report only those items:

```text
System improvement needs input:
- Changed: ...
- Why it matters: ...
- Suggested choice: keep current / update setup / ignore for now
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
