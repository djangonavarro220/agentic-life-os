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
      "semantic_key": "memory_source",
      "usage": "follow the active runtime's memory instructions; read compact memory first, then curated pointers as needed; do not duplicate raw memory into Life OS"
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
- domain-specific knowledge/context source pointers
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
- raw knowledge-base dumps or exports

If the user explicitly creates a Life OS note, preference, or technical state item, the owning skill data file may store it. Otherwise real domain data should live in the runtime or external source selected by the LLM.

## Knowledge and context sources

Life OS should adapt to the user's existing setup. Do not impose a Life OS knowledge structure on top of an agent/runtime that already owns memory, notes, tasks, calendars, or canonicals.

Config should store source pointers plus short usage instructions: how to read the source, whether writes are allowed, what not to duplicate, and which runtime/tool owns it. Real user data stays in the existing source.

Config stores pointers and access notes only. Do not paste the whole knowledge store into config. Global sources used by many skills belong in `sources`; domain-specific sources belong in `$LIFEOS_DATA_DIR/<skill-name>/data.json`. Do not bulk-convert or move an existing notes/wiki/memory system just to match Life OS.

For setup questions, discover before deciding. If a semantic setup key is missing, inspect the active runtime first and record what already exists. Example: before deciding `quiet_heartbeat`, list existing heartbeat/watch crons and their delivery/no-news behavior; before deciding `delivery_policy`, inspect existing routine delivery routes. Then recommend whether Life OS should reuse, ignore, or propose a change.

## Source usage instructions

A source record should say more than where the source lives when the access pattern matters. Store short, flexible, agent-facing instructions such as:

- `usage`: how agents should read or update the source;
- `read_policy`: preferred order of sources or retrieval rules;
- `write_policy`: whether writes are allowed, approval-gated, or forbidden;
- `do_not`: duplication, raw export, or privacy boundaries.

For memory/context, this is usually essential. Different runtimes have different memory rules, injected profiles, canonical files, notes, or topic context. Life OS should preserve those instructions as pointers/policy, not flatten them into a fake universal memory database.

Example:

```json
{
  "sources": {
    "memory": {
      "answer": "current runtime memory/context system",
      "semantic_key": "memory_source",
      "usage": "follow the active runtime's memory instructions; use compact injected memory first; follow canonical/topic pointers only when relevant",
      "write_policy": "do not duplicate raw memories into Life OS; store only pointers and setup decisions"
    }
  }
}
```

Reading policy:

1. Open `index.md` if present.
2. Search concept frontmatter and body.
3. Follow links selectively.
4. Treat `log.md` as provenance, not latest truth.
5. Prefer curated concepts over raw archives.

Ask before bulk conversion, deletion, moving documents, or publishing a private bundle.

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
