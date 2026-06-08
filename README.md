# Agentic Life OS

A portable personal advisor OS built from Agent Skills.

It is designed to work across runtimes such as Hermes and OpenClaw without turning the user's whole life into one giant prompt blob. The public repo contains skills, schemas, runtime adapters, and examples. Private state lives outside the repo in a user data directory.

## Core shape

```text
user or scheduled runtime job
  -> life-os umbrella skill
    -> detect runtime and data directory
    -> read skill-index.yaml
    -> read <data-dir>/config.json
    -> load only the needed subskills
    -> run the routine or manual task
    -> persist private state in <data-dir>/<skill-name>/data.json
```

## Design principles

- **Portable:** built around Agent Skills, not one vendor runtime.
- **Token-efficient:** the `life-os` umbrella skill lazy-loads subskills and runtime docs only when needed.
- **Private by default:** personal data, secrets, memory, mail, calendar credentials, and delivery routing stay in the runtime or local data directory, not in this repo.
- **Runtime-aware:** Hermes and OpenClaw adapters document how to install, schedule, and call the skills without hard-coding private runtime state.
- **Composable:** routines, people, gifts, events, mail, calendar, tasks, and reviews are separate skills with their own schemas.

## Initial skill layout

```text
skills/
  life-os/
    SKILL.md
    skill-index.yaml
    install.yaml
    skills/
      core-install/
      core-doctor/
      core-config/
      routines-heartbeat/
      routines-pulse/
      routines-daily-review/
      routines-weekly-review/
      routines-monthly-review/
      routines-quarterly-review/
      context-now/
      context-inbox/
      context-commitments/
      events-reminders/
      people-contacts/
      people-followups/
      gifts/
      tasks-todo/
      integrations-runtime/
      integrations-calendar/
      integrations-mail/
```

## Data location

Private state should live outside the repo:

- Default: `$HOME/.life-os`
- Override: `LIFEOS_DATA_DIR`

Per-skill state follows:

```text
$HOME/.life-os/<skill-name>/data.json
```

When `LIFEOS_DATA_DIR` is set, use:

```text
$LIFEOS_DATA_DIR/<skill-name>/data.json
```

Runtime-owned capabilities stay in the runtime. Life OS can store pointers and tracking metadata, not copied credentials or private memory dumps.

## CLI helper

The repo includes a small deterministic helper for the state mechanics agents should not improvise:

Fresh local Hermes install:

```bash
git clone https://github.com/djangonavarro220/agentic-life-os.git
cd agentic-life-os
mkdir -p "$HOME/.hermes/skills/productivity"
ln -sfn "$PWD/skills/life-os" "$HOME/.hermes/skills/productivity/life-os"
npm run lifeos -- install --runtime hermes
npm run lifeos -- doctor
hermes skills list --source local | grep -E 'life-os|tasks-todo'
```

Existing checkout:

```bash
npm run lifeos -- install --runtime hermes
npm run lifeos -- doctor
npm run lifeos -- run pulse --summary "daily pulse completed"
npm run lifeos -- config
```

What it does:

- resolves `$HOME/.life-os` or `LIFEOS_DATA_DIR`
- creates `installed.json`, `runtime.json`, `config.json`
- creates per-subskill `$LIFEOS_DATA_DIR/<skill-name>/data.json`
- validates repo shape and private state with `doctor`
- records routine runs without touching runtime-owned crons, delivery, credentials, or memory
- preserves existing `config.json` choices on re-run, including any earlier optional global skill selection

What it deliberately does not do:

- create Telegram/Discord/email delivery routes
- create or delete runtime cron jobs
- store secrets, raw memories, credentials, or private chat IDs
- replace the host runtime's memory, vault, calendar, or mail integrations

## Validation

```bash
npm run lint          # external Agent Skills scan + local policy lint
npm run lint:external # agent-skills-mcp scanner
npm run lint:local    # repo-specific skill policy checks
npm test              # helper install/doctor/run smoke tests
```

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for autonomy modes, remaining Markdown playbooks, runtime adapters, schemas, examples, and non-goals.

## Status

Operational scaffold: install, doctor, config, routine-run recording, skill linting, and CI are implemented. The domain routines are still playbooks; runtime-specific cron creation and external side effects remain runtime-owned and approval-gated.

## License

MIT
