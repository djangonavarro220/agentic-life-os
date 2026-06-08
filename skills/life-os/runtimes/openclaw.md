# OpenClaw runtime adapter

Use this adapter whenever a Life OS skill needs OpenClaw-specific discovery, installation, scheduling, delivery, agent workspace, or skill visibility behavior.

OpenClaw docs are authoritative for OpenClaw behavior. Prefer `openclaw docs`, repo docs, and live CLI help over assumptions from this repo. Life OS should normally leave OpenClaw-owned data in OpenClaw and record config pointers/access instructions.

## Scope model

OpenClaw state is workspace/agent scoped. Different agents can have different:

- workspaces
- skill visibility
- channel bindings
- memory indexes
- tool/runtime settings
- model/provider config

Do not assume one global install is correct. Ask which agent/workspace/scope should own visibility when it matters.

## Read-only discovery

Use these commands to understand the current OpenClaw runtime before proposing changes:

```bash
openclaw --help
openclaw status --all
openclaw doctor
openclaw config file
openclaw config validate
openclaw skills list
openclaw skills info life-os
openclaw skills check
openclaw agents list --bindings
openclaw cron list
openclaw tasks list
openclaw memory status
openclaw channels status
openclaw plugins list
openclaw docs search skills
openclaw docs search cron
openclaw docs search tasks
```

If a command is unavailable in the installed OpenClaw version, run the closest `--help` command and adapt. Do not guess hidden paths.

## Check whether Life OS is already available

From the machine/profile where OpenClaw runs:

```bash
openclaw skills list | grep -E '(^|[[:space:]])life-os([[:space:]]|$)'
openclaw skills info life-os
openclaw skills check
```

For a specific OpenClaw agent, include `--agent <id>` where supported:

```bash
openclaw skills list --agent <id>
openclaw skills info life-os --agent <id>
openclaw skills check --agent <id>
```

If `life-os` is listed, do not re-register the skill. Run the state installer from the repo checkout instead:

```bash
cd <agentic-life-os-checkout>
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

## Where OpenClaw finds skills

OpenClaw can see skills from several locations. Current precedence from OpenClaw docs is:

1. `<workspace>/skills/`
2. `<workspace>/.agents/skills/`
3. `$HOME/.agents/skills/`
4. `$HOME/.openclaw/skills/`
5. bundled skills
6. `skills.load.extraDirs` from `$HOME/.openclaw/openclaw.json`

Use workspace skills when the install belongs to one agent/workspace. Use `$HOME/.openclaw/skills/<name>/` for a managed shared skill. Use `skills.load.extraDirs` only when the user intentionally wants a low-precedence external folder.

## Fresh local install from a repo checkout

If the user cloned `agentic-life-os` but OpenClaw cannot see `life-os`, ask whether they want a copy or a symlink, and ask which OpenClaw scope to use: active workspace, shared managed skill, or extra dir.

Workspace copy, safest default:

```bash
cd <agentic-life-os-checkout>
mkdir -p <openclaw-workspace>/skills
rm -rf <openclaw-workspace>/skills/life-os
cp -R skills/life-os <openclaw-workspace>/skills/life-os
openclaw skills list | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

Shared managed copy:

```bash
cd <agentic-life-os-checkout>
mkdir -p "$HOME/.openclaw/skills"
rm -rf "$HOME/.openclaw/skills/life-os"
cp -R skills/life-os "$HOME/.openclaw/skills/life-os"
openclaw skills list | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

Development symlink, only if the user wants live repo edits to affect OpenClaw immediately:

```bash
cd <agentic-life-os-checkout>
mkdir -p <openclaw-workspace>/skills
ln -sfn "$PWD/skills/life-os" <openclaw-workspace>/skills/life-os
openclaw skills list | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

Prefer copy if sandboxing, deployment packaging, or cross-machine sync is involved. Symlinks can be fragile when a runtime copies, sandboxes, or syncs workspaces.

## Agent visibility

If only some OpenClaw agents should see Life OS, configure visibility through OpenClaw agent skill settings such as `agents.defaults.skills` or `agents.list[].skills`. Do not solve per-agent visibility by duplicating private Life OS state or hard-coding agent IDs into this repo.

## Runtime-owned capabilities

OpenClaw owns:

- agents and workspaces
- skill visibility configuration
- channel routing and delivery
- cron or automation jobs
- task/background-work ledger
- tool availability and sandboxing
- model/provider config
- memory systems
- vault/secrets and credentials
- plugins and channel integrations
- sessions and usage/status data

Life OS may record pointers and private tracking state under `$HOME/.life-os`, but it must not copy OpenClaw secrets, channel targets, raw memory dumps, sessions, transcripts, logs, or credentials into the public repo or Life OS state. Dated caches/result snapshots are allowed in private Life OS state when useful, but never credentials or full raw dumps.

## Runtime-owned storage pointers

Record horizontal pointers/access instructions, such as tasks, memory/context, calendar, and routine run records, in global `config.json`. Record domain-specific pointers in the owning skill data file.

Cron:

```text
~/.openclaw/cron/jobs.json
~/.openclaw/cron/jobs-state.json
~/.openclaw/cron/runs/<jobId>.jsonl
```

Prefer CLI commands before direct file reads:

```bash
openclaw cron list
openclaw cron runs --id <job-id>
```

Tasks/background work ledger:

```bash
openclaw tasks list
openclaw tasks show <lookup>
openclaw tasks audit
```

Memory:

```bash
openclaw memory status
openclaw memory search <query>
```

Do not copy full OpenClaw cron output, task records, memory, transcripts, or logs into repo docs. Private Life OS state may keep pointers, last-checked timestamps, last-summary pointers, suppression windows, priority scores, and caches when useful.

## Integration guidance

Default recommendation: leave OpenClaw-owned systems in OpenClaw and bridge through OpenClaw tools/pointers.

Ask before:

- creating/editing/removing `openclaw cron` jobs
- changing channel bindings or delivery routes
- changing agent/workspace visibility or config
- enabling/disabling skills, plugins, tools, or sandbox settings
- changing memory providers or running memory promotions
- running `openclaw doctor --repair` or config fix modes
- importing, migrating, or reconnecting OpenClaw-owned data/references

Never build path-specific Python/JS detectors for OpenClaw internals in this repo. Use OpenClaw commands, docs, and LLM reasoning at install/doctor time.
