---
name: core-install
description: Install and register Agentic Life OS for the current runtime.
version: 0.3.0
author: Agentic Life OS contributors
license: MIT
---

# core-install

Install Agentic Life OS private state and make the umbrella skill visible to the current runtime. Install is a conversation and inspection workflow, not a blind script.

## Trigger

Use when the user asks to install, set up, register, enable, connect, or try Agentic Life OS in Hermes, OpenClaw, or another agent runtime.

## Principle

The helper may create private Life OS state files. The LLM owns the install decision flow:

- detect the active runtime
- check whether the skill is already visible
- discover existing runtime-owned systems
- explain bridge/import/migration choices
- ask before changing runtime-owned config, crons, delivery, skills, or memory

Do not add helper-script heuristics for runtime discovery. Runtime installations differ too much, and a script guessing paths is how you build a brittle little monster.

## Procedure

1. Detect the current runtime from command availability, session context, repo docs, and user request.
2. Load the matching runtime adapter:
   - `../../runtimes/hermes.md`
   - `../../runtimes/openclaw.md`
3. Check whether the umbrella `life-os` skill is already visible to that runtime.
4. If it is visible, do not re-register it. Run only private state install/doctor from the repo checkout.
5. If it is not visible, ask the user which registration scope and install mode they want using the runtime adapter:
   - symlink for live development
   - copy for a static snapshot
   - profile/workspace/agent/shared scope depending on runtime
6. Before proposing any integration, investigate runtime-owned systems with native runtime commands or docs:
   - tasks or background-task ledger
   - crons, schedules, heartbeat, reminders, hooks, standing orders
   - memory and vault/secrets systems
   - delivery routes and messaging channels
   - tools, sandboxing, model/provider config
   - profiles, agents, workspaces, or channel bindings
7. Present options before changing anything:
   - leave the runtime system alone and only read it when relevant
   - bridge to it through runtime-native tools/pointers
   - import a selected subset into Life OS private state
   - migrate ownership to Life OS private state
8. Ask approval before creating any bridge, import, migration, cron, delivery route, global skill registration, config edit, or destructive change.
9. Run private state install and doctor.
10. Verify with runtime-native skill visibility commands and `lifeos.py doctor`.

## Private state install

From the repo checkout:

```bash
python3 scripts/lifeos.py install --runtime <hermes|openclaw|unknown>
python3 scripts/lifeos.py doctor
```

Use `--data-dir <path>` only when the user explicitly wants a non-default private data directory. Default private state is `$HOME/.life-os`; `LIFEOS_DATA_DIR` is an explicit override.

## Runtime-owned system discovery

Discovery is read-only by default. Use it to inform the user, not to auto-migrate.

### Hermes discovery checklist

Load `../../runtimes/hermes.md`, then use native Hermes commands as available:

```bash
hermes skills list --source all
hermes skills inspect life-os
hermes skills config
hermes cron list --all
hermes cron status
hermes memory status
hermes tools list
hermes profile list
hermes gateway status
hermes status --all
hermes config path
hermes config check
```

Notes:

- `hermes cron` owns scheduling. Life OS may propose jobs, but should not create or edit them without approval.
- Hermes profiles have separate homes and skills. Do not edit another profile unless the user selected it.
- Hermes memory and user profile are runtime-owned. Store only pointers or safe tracking metadata in Life OS private state.
- Telegram, Discord, and other delivery routes are runtime-owned. Do not copy raw chat IDs into repo docs or public examples.

### OpenClaw discovery checklist

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
```

For agent-scoped OpenClaw installs, add `--agent <id>` where supported:

```bash
openclaw skills list --agent <id>
openclaw skills info life-os --agent <id>
openclaw skills check --agent <id>
openclaw memory status --agent <id>
```

Notes:

- OpenClaw `tasks` are an activity ledger, not a task-list replacement by default.
- OpenClaw cron runs inside the Gateway and owns schedule definitions and run history.
- OpenClaw agents/workspaces can have different skill visibility and routing bindings.
- OpenClaw memory, secrets, channel routing, and plugin config are runtime-owned.

## Installer response contract

Report compactly:

```text
Install:
- Runtime: <Hermes|OpenClaw|unknown>
- Skill visibility: <visible|missing|ambiguous>
- Private state: <installed|missing|warnings>
- Runtime-owned systems found: <tasks/cron/memory/delivery/etc.>
- Safe next action: <what to do next>
- Needs approval: <registration/bridge/migration/cron/etc.>
```

If runtime detection is ambiguous, ask one concrete question: which runtime, profile, workspace, or agent should own this install?

## What the helper creates

- `$LIFEOS_DATA_DIR/installed.json`
- `$LIFEOS_DATA_DIR/runtime.json`
- `$LIFEOS_DATA_DIR/config.json`
- `$LIFEOS_DATA_DIR/<skill-name>/data.json` for every indexed subskill

## Boundaries

Install does not create runtime crons, delivery routes, credentials, memory entries, vault entries, mail config, calendar config, skill registrations, or migrations. Those are runtime-owned and require explicit user approval.

Skill registration is runtime-specific. Runtime-wide scheduling, delivery, and global registration policy remain explicit follow-up steps, not hidden installer side effects.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/core-install/data.json
```

Do not commit personal data, credentials, private runtime config, raw logs, transcripts, screenshots, audio, or real delivery targets.
