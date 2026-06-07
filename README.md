# Agentic Life OS

A portable personal advisor OS built from Agent Skills.

It is designed to work across runtimes such as Hermes and OpenClaw without turning the user's whole life into one giant prompt blob. The public repo contains skills, schemas, runtime adapters, and examples. Private state lives outside the repo in a user data directory.

## Core shape

```text
user or scheduled runtime job
  -> life-os umbrella skill
    -> detect runtime and data directory
    -> read skill-index.yaml
    -> read $LIFEOS_DATA_DIR/config.json
    -> load only the needed subskills
    -> run the routine or manual task
    -> persist private state in $LIFEOS_DATA_DIR/<skill-name>/data.json
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

- Linux: `$XDG_DATA_HOME/agentic-life-os` or `~/.local/share/agentic-life-os`
- macOS: `~/Library/Application Support/agentic-life-os`
- Windows: `%LOCALAPPDATA%\\agentic-life-os`
- Override: `LIFEOS_DATA_DIR`

Per-skill state follows:

```text
$LIFEOS_DATA_DIR/<skill-name>/data.json
```

Runtime-owned capabilities stay in the runtime. Life OS can store pointers and tracking metadata, not copied credentials or private memory dumps.

## Status

Early design scaffold. The repository is public-safe and intentionally light until the implementation decisions settle.

## License

MIT
