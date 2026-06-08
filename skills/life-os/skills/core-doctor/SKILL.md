---
name: core-doctor
description: Check Agentic Life OS installation, config, schemas, runtime visibility, and runtime-owned integration boundaries.
version: 0.2.0
author: Agentic Life OS contributors
license: MIT
---

# core-doctor

Diagnose Agentic Life OS repo state, private state, runtime visibility, source-decision config, and integration readiness. The script doctor validates boring files; the LLM doctor interprets what it means and what is safe to do next.

## Trigger

Use when the user asks to check, diagnose, verify, repair, or explain a Life OS install.

## Principle

Doctor is read-only by default. It may run validators and native status commands, but it must not repair, migrate, register skills, create crons, edit config, or touch runtime-owned systems unless the user explicitly asks.

## Inputs to inspect

1. Current repo state and files.
2. Life OS private state directory:
   - `$HOME/.life-os` by default
   - `LIFEOS_DATA_DIR` if explicitly set
3. Runtime adapter for the active runtime:
   - `../../runtimes/hermes.md`
   - `../../runtimes/openclaw.md`
4. Runtime-native health and visibility commands.
5. Relevant subskills if the reported issue names one.

## Base private-state check

From the repo root:

```bash
python3 scripts/lifeos.py doctor
```

The helper checks:

- `skills/life-os/skill-index.yaml` exists and references real subskills
- every indexed subskill has `SKILL.md`
- every indexed subskill has `schemas/data.schema.json`
- JSON schemas parse
- private data dir exists, if installed
- `installed.json`, `runtime.json`, and `config.json` exist, if installed
- per-subskill private data files exist, if installed
- `semantic_health`: whether required source, schedule, delivery, and routine decisions have been asked and saved

If `semantic_health.complete` is false, the install is mechanically present but semantically incomplete. The helper persists the semantic checklist into private `config.json`, then the agent should ask the next pending question with `python3 scripts/lifeos.py next-question`, save it with `python3 scripts/lifeos.py answer <key> '<answer>'`, and run doctor again.

## Hermes doctor checklist

Load `../../runtimes/hermes.md`, then use native Hermes commands as available:

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
hermes config check
python3 scripts/lifeos.py doctor
```

Interpretation:

- Missing `life-os` in `hermes skills list` is a runtime registration/visibility issue, not a private-state failure.
- Doctor warnings about missing private files usually mean install has not run for this data dir.
- Hermes profile selection matters. A skill visible in one profile may be missing in another.
- Cron, memory, tools, provider config, gateway status, and delivery are Hermes-owned. Report them as runtime systems, not Life OS files.
- If the user wants a fix, propose a specific action and ask before changing profile config, skill registration, cron jobs, delivery routes, or memory.

## OpenClaw doctor checklist

Load `../../runtimes/openclaw.md`, then use native OpenClaw commands as available:

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
python3 scripts/lifeos.py doctor
```

For a named OpenClaw agent:

```bash
openclaw skills list --agent <id>
openclaw skills info life-os --agent <id>
openclaw skills check --agent <id>
openclaw memory status --agent <id>
```

Interpretation:

- Missing `life-os` in `openclaw skills list` is a workspace/agent/shared visibility issue, not a private-state failure.
- `openclaw tasks` is a background work ledger, not necessarily the user's task list.
- `openclaw cron` owns schedules and run history.
- `openclaw agents list --bindings` explains agent/workspace/channel routing boundaries.
- `openclaw doctor --repair` and config edits can mutate runtime state. Do not run repair modes unless the user asks.

## Diagnosis categories

Classify every finding as one of these:

- `repo`: public repo files, skill index, schemas, docs, CI metadata
- `private-state`: `$LIFEOS_DATA_DIR` install/config/data files, including `sources`, `internal_state`, and `caches`
- `source-decisions`: where each domain lives and how future runs should access it
- `runtime-visibility`: runtime can or cannot see `life-os` or subskills
- `runtime-owned`: cron, tasks ledger, memory, delivery, tools, config, profiles, agents, workspaces, plugins
- `approval-needed`: any proposed change with side effects
- `unknown`: missing facts that require runtime docs, command output, or user choice

## Output contract

```text
Doctor:
- Repo: <ok|error|warning>
- Private state: <ok|missing|warning>
- Runtime: <Hermes|OpenClaw|unknown>
- Skill visibility: <visible|missing|ambiguous>
- Source decisions: <configured|missing|ambiguous>
- Semantic setup: <complete|pending, next question>
- Runtime-owned systems: <summary>
- Issues: <short list>
- Safe next action: <one action>
- Needs approval: <yes/no, why>
```

Keep it compact. Do not paste raw command dumps unless the user asks.

## Repair policy

Safe without asking:

- read repo files
- run read-only validators/status commands
- run `python3 scripts/lifeos.py doctor`
- run `python3 scripts/lifeos.py install` only when the user explicitly asked to install or state files are clearly the requested target

Ask before:

- symlink/copy skill registration
- runtime config edits
- cron/job creation, deletion, or schedule changes
- memory/vault/provider changes
- delivery route changes
- OpenClaw `doctor --repair` / Hermes repair-like commands
- migrations/imports/bridges
- deleting or rewriting private state

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/core-doctor/data.json
```

Do not commit personal data, credentials, private runtime config, raw logs, transcripts, screenshots, audio, or real delivery targets.
