---
name: integrations-runtime
description: Discover and use runtime-owned capabilities without duplicating secrets, private data, or semantic decisions in helper scripts.
version: 0.2.0
author: Agentic Life OS contributors
license: MIT
---

# integrations-runtime

Bridge Life OS playbooks to runtime-owned capabilities without duplicating secrets or private data. Life OS is a helper/coordination layer: it records source decisions, pointers, access instructions, operational state, caches, and Life-OS-specific preferences; real user data usually stays in Hermes/OpenClaw or an external source.

## Trigger

Use when a Life OS workflow needs to inspect, use, bridge, import from, or configure a runtime-owned capability:

- skills and skill visibility
- tasks or background task ledgers
- cron jobs, schedules, reminders, hooks, heartbeats, standing orders
- delivery routes and messaging platforms
- tools, sandboxing, models, providers
- memory systems, vaults, credentials
- agents, profiles, workspaces, channel bindings
- mail/calendar or other external integrations

## Principle

Discovery and integration choices are semantic agent work. Do not encode them in helper scripts.

The LLM should inspect the active runtime with runtime-native commands and docs, explain what it found, choose or propose the source of truth, then record that decision in Life OS config. Helper scripts may validate files or create local state containers, but they must not decide which runtime system to use or migrate.

## Runtime adapters

Load the adapter matching the active runtime before making runtime-specific recommendations or changes:

- `runtimes/hermes.md`
- `runtimes/openclaw.md`

The adapters are central and apply to all Life OS skills. Individual subskills may add narrow runtime notes only when they differ from the central adapter.

## Runtime discovery loop

1. Identify the active runtime and scope:
   - Hermes profile
   - OpenClaw agent/workspace
   - other runtime, if neither adapter matches
2. Load the runtime adapter.
3. Run read-only native discovery commands.
4. Classify each capability:
   - not present
   - present and runtime-owned
   - present but disabled
   - present but ambiguous
   - missing facts require user/runtime docs
5. Decide the Life OS relationship:
   - ignore for this workflow
   - read when relevant
   - record a source pointer and bridge through runtime tools
   - store Life-OS-specific preference/technical state in config
   - create a runtime-native store when no suitable source exists, then record the pointer
   - migrate/reconnect references when moving runtimes, with approval before changes
6. Ask approval before any side effect.
7. Store source decisions, access notes, operational state, caches, and Life-OS-specific preferences in `$LIFEOS_DATA_DIR`. Do not store full real-domain data just to make Life OS the owner.

## Hermes native discovery helpers

Use current Hermes docs and CLI help as source of truth. Useful read-only commands:

```bash
hermes skills list --source all
hermes skills list --enabled-only | grep -E '(^|[[:space:]])life-os([[:space:]]|$)'
hermes skills config
hermes cron list --all
hermes cron status
hermes memory status
hermes tools list
hermes profile list
hermes gateway status
hermes status --all
hermes sessions list
hermes config path
hermes config check
hermes mcp list
hermes plugins list
```

Hermes ownership notes:

- `hermes skills` owns visibility and enablement.
- `hermes cron` owns scheduled jobs. Hermes cron definitions live under the active Hermes home at `cron/jobs.json`; cron output is saved under `cron/output/<job_id>/<timestamp>.md`. Prefer `hermes cron list --all` and `hermes cron status`; store pointers/access instructions in Life OS config.
- `hermes memory` owns external memory provider config; built-in memory remains Hermes-owned.
- `hermes tools` owns tool availability per platform/session.
- `hermes profile` owns profile scoping; each profile can have separate skills, config, memory, sessions, and cron jobs.
- `hermes gateway` owns Telegram/Discord/etc. delivery and platform state.
- `hermes config` owns model/provider/tools/security/runtime config.

Do not copy Hermes secrets, delivery targets, raw memory dumps, sessions, logs, or profile-private config into Life OS state. Life OS private state may still keep deliberate source pointers, last-checked timestamps, suppression windows, priority scores, and dated caches.

## OpenClaw native discovery helpers

Use current OpenClaw docs and CLI help as source of truth. Useful read-only commands:

```bash
openclaw skills list
openclaw skills info life-os
openclaw skills check
openclaw agents list --bindings
openclaw status --all
openclaw doctor
openclaw config file
openclaw config validate
openclaw cron list
openclaw tasks list
openclaw memory status
openclaw channels status
openclaw plugins list
```

For agent-scoped checks, add `--agent <id>` where supported:

```bash
openclaw skills list --agent <id>
openclaw skills info life-os --agent <id>
openclaw skills check --agent <id>
openclaw memory status --agent <id>
```

OpenClaw ownership notes:

- `openclaw skills` owns workspace/agent skill visibility.
- `openclaw agents list --bindings` shows agent/workspace/channel routing.
- `openclaw tasks` is an activity ledger for background work, not automatically a user task database.
- `openclaw cron` owns Gateway scheduled jobs and run history. Cron definitions live in `~/.openclaw/cron/jobs.json` by default, pending runtime state lives in `~/.openclaw/cron/jobs-state.json`, and run logs live under `~/.openclaw/cron/runs/<jobId>.jsonl`. Prefer `openclaw cron list` and `openclaw cron runs --id <job-id>`; store pointers/access instructions in Life OS config.
- `openclaw memory` owns semantic memory indexing/search/promote flows.
- `openclaw config` owns runtime configuration; use read-only `get/file/validate` by default.
- `openclaw doctor --repair` mutates runtime state. Do not run repair without approval.
- `openclaw channels`, plugins, secrets, and gateway config own delivery and credentials.

Do not copy OpenClaw secrets, channel targets, raw memory dumps, sessions, logs, or agent-private config into Life OS state. Life OS private state may still keep deliberate source pointers, last-checked timestamps, suppression windows, priority scores, and dated caches.

## Decision matrix

Use this language when explaining choices:

- **Leave runtime-owned:** best when the runtime already has a good system and Life OS only needs to read or reference it.
- **Bridge/reference:** default for most integrations. Life OS records where the data lives and how to access it, then uses runtime tools.
- **Create runtime-native store:** best when a new domain has no source yet. Put the real data in runtime memory/notes/tasks/calendar/contact system if possible, then record the pointer.
- **Store in Life OS:** only for Life-OS-specific preferences, technical state, operational caches, or notes explicitly created inside Life OS.
- **Migrate/reconnect references:** when moving between runtimes, the LLM should inspect old references, propose a new runtime-native mapping, and ask before changing or copying anything.

Default recommendation: leave real user data runtime-owned or external-source-owned, and keep Life OS as the coordination map.

## Approval boundaries

Safe without asking:

- read docs
- inspect command help
- run read-only status/list/show/check commands
- summarize discovered runtime capabilities
- propose a plan

Ask before:

- registering or globally enabling skills
- creating/editing/deleting cron jobs or reminders
- changing delivery routes, channel bindings, profiles, agents, or workspaces
- editing runtime config
- changing memory providers, vaults, or credentials
- creating a runtime-native store for new real-domain data
- importing/migrating/reconnecting references or data between sources
- deleting runtime or Life OS state
- running repair/fix commands

## Output contract

```text
Runtime integration:
- Runtime/scope: <Hermes profile|OpenClaw agent/workspace|unknown>
- Capabilities found: <tasks/cron/memory/delivery/tools/etc.>
- Ownership: <runtime-owned vs Life OS private state>
- Recommendation: <leave/bridge/import/migrate>
- Safe next action: <one step>
- Needs approval: <what and why>
```

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/integrations-runtime/data.json
```

Do not commit personal data, credentials, private runtime config, raw logs, transcripts, screenshots, audio, or real delivery targets.
