---
name: learning-projects
description: Track learning goals, courses, books, practice sessions, notes, review cadence, and blockers.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# learning-projects

Track learning as a set of goals, practice loops, notes, projects, blockers, and review cadence. This skill keeps momentum without pretending every interest needs a huge curriculum.

## Trigger

Use when the user asks to:

- track a course, book, topic, skill, or practice habit
- plan a learning session or next exercise
- review notes and schedule spaced repetition or project work
- identify blockers or prerequisites
- decide what to learn next based on goals and available energy

## Operating model

1. Resolve the active runtime and private data directory.
2. Read `$LIFEOS_DATA_DIR/config.json` when available.
3. If source ownership for this domain is unknown, inspect runtime-owned systems read-only and propose a source decision before writing anything.
4. Load only `runtimes/<active-runtime>.md` if runtime-specific commands, storage pointers, delivery, scheduling, or integration behavior are needed.
5. Do not load other runtime adapters for the same task.
6. Prefer pointers, access notes, review dates, and short operational state over duplicated raw data.
7. Ask before changing external systems, creating reminders, contacting people, importing data, broad migrations, or destructive cleanup.
8. Record useful Life OS coordination state under `$LIFEOS_DATA_DIR/learning-projects/data.json` when the user/runtime policy allows it.

## Source decision

Store the source choice in Life OS config when useful:

```json
{
  "sources": {
    "learning_records": {
      "owner": "runtime|external|life-os",
      "runtime": "<active-runtime>",
      "source": "<tool-or-system>",
      "access": "<short pointer or retrieval instruction>"
    }
  }
}
```

Use Life OS as the source of truth only for Life-OS-specific preferences, technical state, or notes explicitly created inside Life OS. Do not silently create a second private database when the runtime or an external system already owns the real data.

## Output contract

Keep output compact and action-oriented:

```text
Summary:
- Signal: ...
- Risk: ...
- Next action: ...
- Review date: ...
```

If nothing changed, say so briefly or stay silent when running as a scheduled routine and the saved policy allows silence.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/learning-projects/data.json
```

Acceptable state:

- source decisions and access pointers
- last review/check timestamps
- suppression windows
- dated summaries or caches when useful
- non-secret user-approved notes for this domain
- follow-up pointers into runtime-owned tasks, reminders, calendar, mail, docs, or memory

Do not store credentials, raw account exports, full mail/chat logs, private delivery targets, raw medical records, bank credentials, identity document numbers, or secrets.

## Runtime adapters

Runtime-specific commands and caveats live in separate Markdown files:

```text
runtimes/hermes.md
runtimes/openclaw.md
```

Load only the adapter for the active runtime. Generic skill text must not inline both Hermes and OpenClaw command blocks.

## Safety boundaries

Safe autonomously:

- read Life OS private state
- inspect available runtime state with read-only tools
- summarize already available information
- propose next actions, review dates, and source mappings
- write Life OS operational state when it does not alter external systems

Ask before:

- writing to external systems
- creating or changing runtime crons, reminders, calendar events, contacts, mail, tasks, or delivery routes
- importing, exporting, or migrating data
- deleting records or clearing caches broadly
- handling sensitive identity, medical, financial, or credential material

## Common pitfalls

- Duplicating the runtime's real data into Life OS instead of storing a pointer.
- Loading multiple runtime adapters and polluting the prompt with irrelevant commands.
- Turning a light review into a heavyweight system of record.
- Alerting on every tiny change instead of respecting quiet policy.

## Verification checklist

- [ ] Active runtime identified.
- [ ] Source owner recorded or explicitly deferred.
- [ ] Only the active runtime adapter was loaded when runtime details were needed.
- [ ] No secrets, raw exports, or private identifiers were written to repo files.
- [ ] Any external side effect had explicit user approval.
