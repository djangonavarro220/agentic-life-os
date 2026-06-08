---
name: context-now
description: Build the current actionable context. Use when the user asks for current context, immediate focus, what to look at now, a catch-up, next action, or what is active/waiting.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# context-now

Build a compact view of what matters now. This is the user-facing “where am I and what should I do next?” skill.

## Trigger

Use when the user asks for a compact current-context or next-action view, including:

- what should I focus on?
- what should I look at now?
- catch me up
- where are we?
- what is active now?
- what am I waiting on?
- what should the next action be?

Keep triggers language-neutral in spirit: examples may be English, but the intent is current context, immediate focus, catch-up, and next action in any user language.

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

If this was a meaningful context rebuild, record a short summary in Life OS private state or runtime-native state only when the current runtime policy allows it. Do not use helper scripts for semantic routine decisions.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/context-now/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
