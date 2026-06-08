# Agentic Life OS

A portable personal advisor OS built from Agent Skills.

It is designed to work across runtimes such as Hermes and OpenClaw without turning the user's whole life into one giant prompt blob or a second personal database. The public repo contains skills, schemas, runtime adapters, and examples. Private Life OS state stores pointers, source decisions, access notes, operational state, caches, and Life-OS-specific preferences. Real user data usually stays in the runtime or external source that already owns it.

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
- **Runtime-aware:** Hermes and OpenClaw adapters document how to discover existing runtime capabilities, install/register skills, schedule routines, and use delivery/memory/tasks without hard-coding private runtime state.
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

Runtime-owned capabilities stay in the runtime or external source. Life OS stores the map around them:

- source decisions, for example `birthdays -> calendar tool` or `tasks -> OpenClaw tasks`
- access notes or pointers needed to retrieve the source again
- internal routine state, for example last check time, last pulse pointer, last summary pointer, suppression windows, priority scores, and persistent dated caches
- Life-OS-specific preferences, for example silence/noise policy

Do not copy full birthdays, contacts, tasks, chats, memories, logs, or credentials into Life OS state unless the item is explicitly a Life OS note, preference, or technical state record. Private caches/result snapshots may include useful non-secret text and default to persistent retention; organize them as dated folders or dated records rather than throwing them into one swamp file.

## Runtime support

Hermes and OpenClaw are first-class supported runtimes. Runtime-specific instructions live in:

```text
skills/life-os/runtimes/hermes.md
skills/life-os/runtimes/openclaw.md
```

For every Life OS skill, check availability and install/register through the active runtime before assuming the skill is missing.

Hermes checks:

```bash
hermes skills list --source all | grep -E 'life-os|tasks-todo'
hermes skills list --enabled-only | grep -E 'life-os|tasks-todo'
```

OpenClaw checks:

```bash
openclaw skills list | grep -E 'life-os|tasks-todo'
openclaw skills info life-os
openclaw skills check
```

If `life-os` is already available, do not re-register it. Just run the state install from the repo checkout:

```bash
npm run lifeos -- install --runtime <hermes|openclaw>
npm run lifeos -- doctor
```

If the repo is cloned somewhere else and the runtime cannot see the skill yet, ask the user where to install it and whether they want a symlink for live development or a copy for a static snapshot.

## CLI helper

The repo includes a small deterministic helper for the state mechanics agents should not improvise:

```bash
npm run lifeos -- install --runtime <hermes|openclaw>
npm run lifeos -- doctor
npm run lifeos -- next-question
npm run lifeos -- answer <decision-key> '<answer or runtime pointer>'
npm run lifeos -- plan
npm run lifeos -- config
```

What it does:

- resolves `$HOME/.life-os` or `LIFEOS_DATA_DIR`
- creates `installed.json`, `runtime.json`, `config.json`
- initializes config containers for `sources`, `internal_state`, and `caches`
- initializes `semantic_setup`, a private checklist of required source, routine, delivery, and scheduling decisions
- creates per-subskill `$LIFEOS_DATA_DIR/<skill-name>/data.json`
- validates repo shape, private state, and semantic setup completeness with `doctor`
- shows the next required setup question with `next-question`
- saves approved setup answers with `answer <decision-key> '<answer>'`
- prints a no-side-effect install plan and cron templates with `plan`
- documents human-readable cron templates in `skills/life-os/templates/cron-jobs.md`
- keeps runtime-owned crons, delivery, credentials, memory, task systems, and semantic routine behavior out of the helper
- preserves existing `config.json` choices on re-run

What it deliberately does not do:

- create Telegram/Discord/email delivery routes
- create or delete runtime cron jobs without a saved user decision and explicit approval
- mark Life OS as fully installed while `doctor.semantic_health.complete` is false
- store secrets, raw memories, credentials, or private chat IDs
- replace the host runtime's memory, vault, calendar, or mail integrations

## Validation

```bash
npm run lint             # external scan + public-safety scan + local policy lint
npm run lint:external    # agent-skills-mcp scanner
npm run lint:public-safe # secret/token pattern scan only
npm run lint:local       # repo-specific skill policy checks
npm test                 # helper install/doctor/config smoke tests
```

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for autonomy modes, remaining Markdown playbooks, runtime adapters, schemas, examples, and non-goals.

## Status

Operational scaffold: install, doctor, config, semantic setup questions, answer persistence, skill linting, public-safety scanning, and CI are implemented. The domain routines are still playbooks; runtime-specific cron creation and external side effects remain runtime-owned and approval-gated.

## License

MIT
