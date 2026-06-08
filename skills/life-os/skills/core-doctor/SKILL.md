---
name: core-doctor
description: Check Agentic Life OS installation, config, schemas, and runtime adapters.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# core-doctor

Validate the public repo shape and the private Life OS state directory.

## Procedure

From the repo root:

```bash
python3 scripts/lifeos.py doctor
```

Doctor checks:

- `skills/life-os/skill-index.yaml` exists and references real subskills
- every indexed subskill has `SKILL.md`
- every indexed subskill has `schemas/data.schema.json`
- JSON schemas parse
- private data dir exists, if installed
- `installed.json`, `runtime.json`, and `config.json` exist, if installed
- per-subskill private data files exist, if installed

## Interpreting results

- `errors`: fix before using routines.
- `warnings`: usually means Life OS is not installed yet or per-skill data has not been created.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/core-doctor/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
