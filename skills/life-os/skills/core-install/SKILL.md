---
name: core-install
description: Install and register Agentic Life OS for the current runtime.
version: 0.3.0
author: Agentic Life OS contributors
license: MIT
---

# core-install

Install Agentic Life OS private state and make the umbrella skill visible to the current runtime. Install is a conversation and inspection workflow, not a blind script. Life OS is a helper over the runtime: it records where things live and how to access them, rather than becoming the owner of calendars, tasks, memory, crons, vaults, or delivery.

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
2. Load only the matching runtime adapter for the active runtime:
   - shared runtime adapter: `../../runtimes/<runtime>.md`
   - core-install adapter: `runtimes/<runtime>.md`
3. Do not load both Hermes and OpenClaw adapters for a single install. Keep runtime-specific instructions in those Markdown files, not inline here.
4. Check whether the umbrella `life-os` skill is already visible to that runtime.
5. If it is visible, do not re-register it. Run only private state install/doctor from the repo checkout.
6. If it is not visible, ask the user which registration scope and install mode they want using the runtime adapter:
   - symlink for live development
   - copy for a static snapshot
   - profile/workspace/agent/shared scope depending on runtime
7. Before proposing any integration, investigate runtime-owned systems with native runtime commands or docs:
   - tasks or background-task ledger
   - crons, schedules, heartbeat, reminders, hooks, standing orders
   - memory and vault/secrets systems
   - delivery routes and messaging channels
   - tools, sandboxing, model/provider config
   - profiles, agents, workspaces, or channel bindings
8. Present options before changing anything:
   - leave the runtime system alone and only read it when relevant
   - record a pointer/reference and bridge through runtime-native tools
   - import selected pointers, access notes, or Life-OS-specific state into config
   - migrate/reconnect references when moving between runtimes, using runtime-native stores for real data where possible
9. Ask approval before creating any bridge, import, migration, cron, delivery route, global skill registration, config edit, or destructive change.
10. Run private state install and doctor.
11. If `doctor.semantic_health.complete` is false, ask the next pending setup question from `python3 scripts/lifeos.py next-question`.
12. Save each approved answer with `python3 scripts/lifeos.py answer <key> '<answer or runtime pointer>'`.
13. Repeat doctor -> next-question -> ask -> answer until semantic health is complete, or until the user explicitly stops setup.
14. Use `python3 scripts/lifeos.py plan` to show runtime cron templates and remaining steps without creating jobs.
15. Verify with runtime-native skill visibility commands and `lifeos.py doctor`.

## Private state install

From the repo checkout:

```bash
python3 scripts/lifeos.py install --runtime <hermes|openclaw|unknown>
python3 scripts/lifeos.py doctor
python3 scripts/lifeos.py next-question
python3 scripts/lifeos.py answer <decision-key> '<answer or runtime pointer>'
python3 scripts/lifeos.py plan
```

Use `--data-dir <path>` only when the user explicitly wants a non-default private data directory. Default private state is `$HOME/.life-os`; `LIFEOS_DATA_DIR` is an explicit override.

`doctor` includes `semantic_health`. Treat `semantic_health.complete: false` as “installed, but setup is not semantically complete”. Ask the next pending question through `next-question`, save the answer, and check again. Do not claim a total install while required semantic decisions are missing.

`plan` returns no-side-effect cron templates for daily pulse, quiet heartbeat, and weekly review. These are examples for the runtime adapter to turn into real jobs only after the user has approved cadence and delivery.

## Runtime-owned system discovery

Discovery is read-only by default. Use it to inform the user, not to auto-migrate. After the LLM decides where a domain should live, record that source decision in `config.json` so later runs do not rediscover from scratch.

Config may store source records such as:

```json
{
  "sources": {
    "birthdays": {
      "owner": "runtime",
      "runtime": "<active-runtime>",
      "source": "calendar",
      "access": "use the active runtime calendar tool; do not duplicate birthday records here"
    },
    "cron_records": {
      "owner": "runtime",
      "runtime": "<active-runtime>",
      "source": "cron.run_logs",
      "access": "use the active runtime adapter to find routine run records"
    }
  }
}
```

Do not store the actual full birthday/contact/task list just to remember where it is.

### Runtime-specific discovery checklists

Do not inline Hermes and OpenClaw discovery instructions in this generic skill. That forces unrelated runtime context into the same prompt, which is exactly the mess this skill pack is trying to avoid.

Load only the adapter for the active runtime:

- Hermes install flow: `runtimes/hermes.md`, plus shared adapter `../../runtimes/hermes.md`
- OpenClaw install flow: `runtimes/openclaw.md`, plus shared adapter `../../runtimes/openclaw.md`

Those Markdown files own the runtime-specific commands, storage pointers, and caveats. This file owns only the generic install contract.

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
- `$LIFEOS_DATA_DIR/config.json` with mechanical containers for `sources`, `internal_state`, `caches`, and `semantic_setup`
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
