---
name: context-now
description: Build the current actionable context.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# context-now

Build a compact view of what matters now. This is the user-facing “where am I and what should I do next?” skill.

## Trigger

Use when the user asks:

- what should I focus on?
- catch me up
- where are we?
- what is active now?
- what am I waiting on?
- what should the next action be?

## Context sources

Inspect only relevant, runtime-owned sources and Life OS private tracking pointers:

- current conversation/request
- Life OS `config.json` and recent routine records
- runtime TODO/task system, if configured
- calendar/mail/session/memory pointers only when relevant and available
- active blockers or recent decisions from loaded subskills

Do not dump raw history. Distill.

## Reasoning steps

1. Identify the user horizon: next 30 minutes, today, this week, or strategic.
2. Separate facts from guesses.
3. Classify items into:
   - focus now
   - waiting on others
   - waiting on user decision
   - risks/deadlines
   - can ignore for now
4. Pick a default next action if one clearly wins.
5. If ambiguity changes the next tool/action, ask one lightweight question.

## Output contract

Default shape:

```text
Now:
- Focus: ...
- Waiting on: ...
- Risk: ...
- Next action: ...
```

Keep it short. If the user wants detail, expand from the private/source pointers.

## State update

If this was a meaningful context rebuild, record it:

```bash
python3 scripts/lifeos.py run now --summary "<short now summary>"
```

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/context-now/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
