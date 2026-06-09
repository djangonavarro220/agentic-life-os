---
name: core-config
description: Read and update Life OS private configuration safely.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# core-config

Read and update Life OS private configuration safely. Config is the coordination map for the skill, not a replacement for Hermes/OpenClaw/external data stores.

## Trigger

Use when the user asks to inspect or change Life OS settings, source decisions, pointers, access instructions, routine state, cache policy, or autonomy/approval preferences.

## Config location

Default:

```text
$HOME/.life-os/config.json
```

Override:

```text
$LIFEOS_DATA_DIR/config.json
```

## Config owns

Global config owns install-wide coordination plus horizontal core choices used by many skills:

- `enabled`
- active `runtime`
- `skills`: per-skill enablement/preferences
- `semantic_setup`: setup status and pointers
- `sources`: cross-skill source pointers such as tasks, memory/context, calendar, and routine run records
- `policies`: cross-skill policies such as schedule, delivery, trigger defaults, approval behavior, and review-item cadence defaults
- active or paused guided-meeting pointers when they are horizontal context rather than domain state

These horizontal choices belong in global config because `context-now`, `routines-pulse`, `routines-weekly-review`, `people-followups`, and domain skills may all need the same task or memory source. Forcing every skill to read `tasks-todo/data.json` as a pseudo-database is fake modularity.

Example global source ownership:

```json
{
  "sources": {
    "tasks": {
      "answer": "runtime task system",
      "semantic_key": "tasks_source",
      "access": "use the active runtime task tool; do not duplicate the full task list here"
    },
    "memory": {
      "answer": "runtime memory/context",
      "semantic_key": "memory_source"
    }
  },
  "policies": {
    "delivery_policy": { "answer": "runtime-owned delivery alias" },
    "review_cadence": { "answer": "weekly plus monthly" }
  }
}
```

Domain state belongs in the owning skill's data file:

```text
$LIFEOS_DATA_DIR/<skill-name>/data.json
```

Skill data may store:

- `source_decisions`: source choices only that domain owns
- `setup_decisions`: setup answers owned by that skill
- `internal_state`: last checks, suppression windows, priority scores, and pointers
- `caches`: dated or named result snapshots used by that skill
- `preferences`: Life-OS-specific preferences for that domain

Example task skill state:

```json
{
  "skill": "tasks-todo",
  "preferences": {
    "default_review_mode": "compact"
  },
  "internal_state": {
    "last_reviewed_at": "2026-01-01T09:00:00Z"
  },
  "caches": {}
}
```

## Config does not own

Do not put these in global config or skill data as the main source of truth:

- full birthday/contact/task lists
- raw runtime memories
- full chats, transcripts, logs, screenshots, or audio
- runtime secrets, tokens, vault entries, credentials, or real delivery targets
- runtime cron definitions or job IDs beyond pointers/access notes

If the user explicitly creates a Life OS note, preference, or technical state item, the owning skill data file may store it. Otherwise real domain data should live in the runtime or external source selected by the LLM.

## Retention and layout

Default retention is persistent. Do not auto-delete global config entries, skill data pointers, source decisions, suppression windows, priority scores, or caches unless the user or runtime policy explicitly says to clear them.

Organize durable caches and routine artifacts by dated folders or dated records, for example:

```text
$LIFEOS_DATA_DIR/caches/2026/01/01/<routine>.json
$LIFEOS_DATA_DIR/routines-pulse/2026/01/01/data.json
```

Caches and result snapshots do not have to be IDs/hashes only. They may include text when needed for the skill to function, but never credentials or secrets.

## Update policy

Safe without asking:

- read config
- add/update horizontal core sources and policies in global config after the user approved the setup choice or the choice is clearly part of the requested install/check
- add/update domain-specific source decisions in the owning skill data file
- update internal routine state after a routine runs
- update caches/result snapshots in private state

Ask before:

- changing where a domain's real data lives
- creating a runtime-native store
- reconnecting/migrating references between runtimes
- deleting config, caches, or source records
- writing secrets or real delivery targets, which should normally be refused or redirected to the runtime/vault

## Runtime move policy

When moving between runtimes, the LLM should inspect the relevant skill data files, load the new runtime adapter, attempt to map old references to new runtime-native sources, then ask before making changes. Do not silently discard old references.

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/core-config/data.json
```

Do not commit personal data, credentials, private runtime config, raw logs, transcripts, screenshots, audio, or real delivery targets.
