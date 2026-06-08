---
name: routines-pulse
description: Daily proactive briefing routine.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# routines-pulse

Create a compact proactive daily briefing using runtime-owned sources and Life OS private tracking state.

## Procedure

1. Run `python3 scripts/lifeos.py doctor` if install state is uncertain.
2. Inspect configured runtime-owned pointers in `$LIFEOS_DATA_DIR/config.json`.
3. Gather only actionable signals from enabled sources.
4. Avoid copying raw mail/calendar/memory contents into Life OS data.
5. Write a short routine record:

```bash
python3 scripts/lifeos.py run pulse --summary "<short summary>"
```

## Output style

Surface only concrete next actions, blockers, and decisions. No noisy “all good” digests unless the user requested a heartbeat.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/routines-pulse/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
