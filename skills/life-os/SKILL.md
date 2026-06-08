---
name: life-os
description: Portable personal advisor OS umbrella skill for lazy-loading Agentic Life OS subskills.
version: 0.1.0
license: MIT
---

# Life OS

Use this skill as the stable entrypoint for Agentic Life OS.

## Mission

Coordinate personal advisor routines through small, portable Agent Skills while keeping private state outside the repository.

## Operating model

1. Detect the current runtime.
2. Resolve the private data directory:
   - `LIFEOS_DATA_DIR` if set
   - otherwise the platform default data directory
3. Read `skill-index.yaml`.
4. Read `$LIFEOS_DATA_DIR/config.json` if it exists.
5. Load only the subskills needed for the current request or scheduled routine.
6. Write only Life OS routine state and tracking data to `$LIFEOS_DATA_DIR/<skill-name>/data.json`.

## Deterministic helper

Use the repo helper for state mechanics instead of improvising file layouts:

```bash
python3 scripts/lifeos.py install --runtime hermes
python3 scripts/lifeos.py doctor
python3 scripts/lifeos.py run pulse --summary "daily pulse completed"
python3 scripts/lifeos.py config
```

From the repo root, npm aliases are also available:

```bash
npm run lifeos -- install --runtime hermes
npm run lifeos -- doctor
npm run lifeos -- run pulse --summary "daily pulse completed"
npm run lifeos -- config
```

The helper owns:

- resolving the private data directory
- creating `installed.json`, `runtime.json`, and `config.json`
- creating per-subskill `data.json` files
- validating repo/private state with `doctor`
- recording routine runs in private state

The helper does not create/delete runtime crons, configure delivery routes, store credentials, or mutate runtime memory/vault/mail/calendar systems.

## Privacy boundary

Do not store these in the repo or Life OS data files:

- secrets or tokens
- real private memories
- raw mail/calendar credentials
- runtime delivery targets
- private chat IDs
- user logs unless explicitly exported and scrubbed

Runtime-owned systems stay in the runtime. Life OS may store pointers like tool names, adapter names, and last-checked tracking metadata.

## Subskill loading

Subskills live under:

```text
skills/life-os/skills/<subskill>/SKILL.md
```

Default: subskills are not globally registered. `tasks-todo` is the exception candidate: installers may ask whether to register it globally for the current runtime.

## Routine execution

For scheduled or manual routines:

1. Run `doctor` if install state is uncertain.
2. Load the matching routine subskill from `skill-index.yaml`.
3. Execute the playbook with runtime-native tools.
4. Record the run with `lifeos.py run <routine> --summary <short summary>`.
5. Surface only actionable output to the user.

Supported routine aliases in the helper:

- `heartbeat`
- `pulse`
- `daily-review`
- `weekly-review`
- `monthly-review`
- `quarterly-review`
- `now`
