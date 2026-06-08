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

Life OS config may store:

- `sources`: where each domain's real data lives and how to access it
- `internal_state`: operational state such as last checks, suppression windows, priority scores, and last-summary pointers
- `caches`: dated or named result snapshots used by routines; these may include text when useful and default to persistent retention
- `skills`: per-skill enablement/preferences
- Life-OS-specific preferences, such as silence/noise policy

Example:

```json
{
  "sources": {
    "birthdays": {
      "owner": "runtime",
      "runtime": "openclaw",
      "source": "calendar",
      "access": "use the runtime calendar tool; do not duplicate birthday records here"
    },
    "cron_records": {
      "owner": "runtime",
      "runtime": "hermes",
      "source": "cron.output",
      "access": "hermes cron list --all; output lives under active Hermes home/cron/output/<job_id>/<timestamp>.md"
    }
  },
  "internal_state": {
    "birthdays_last_checked_at": "2026-01-01T09:00:00Z",
    "last_pulse": { "pointer": "runtime cron output or Life OS dated cache path" },
    "last_summary_sent": { "pointer": "runtime message/session/output reference" },
    "do_not_alert_until": {},
    "priority_scores": {}
  },
  "caches": {
    "2026/01/01": {
      "pulse_candidates": []
    }
  }
}
```

## Config does not own

Do not put these in Life OS config as the main source of truth:

- full birthday/contact/task lists
- raw runtime memories
- full chats, transcripts, logs, screenshots, or audio
- runtime secrets, tokens, vault entries, credentials, or real delivery targets
- runtime cron definitions or job IDs beyond pointers/access notes

If the user explicitly creates a Life OS note, preference, or technical state item, config/private state may store it. Otherwise real domain data should live in the runtime or external source selected by the LLM.

## Retention and layout

Default retention is persistent. Do not auto-delete config entries, pointers, source decisions, suppression windows, priority scores, or caches unless the user or runtime policy explicitly says to clear them.

Organize durable caches and routine artifacts by dated folders or dated records, for example:

```text
$LIFEOS_DATA_DIR/caches/2026/01/01/<routine>.json
$LIFEOS_DATA_DIR/routines-pulse/2026/01/01/data.json
```

Caches and result snapshots do not have to be IDs/hashes only. They may include text when needed for the skill to function, but never credentials or secrets.

## Update policy

Safe without asking:

- read config
- add/update source decisions after the user approved the setup choice or the choice is clearly part of the requested install/check
- update internal routine state after a routine runs
- update caches/result snapshots in private state

Ask before:

- changing where a domain's real data lives
- creating a runtime-native store
- reconnecting/migrating references between runtimes
- deleting config, caches, or source records
- writing secrets or real delivery targets, which should normally be refused or redirected to the runtime/vault

## Runtime move policy

When moving between runtimes, the LLM should inspect existing `sources`, load the new runtime adapter, attempt to map old references to new runtime-native sources, then ask before making changes. Do not silently discard old references.

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/core-config/data.json
```

Do not commit personal data, credentials, private runtime config, raw logs, transcripts, screenshots, audio, or real delivery targets.
