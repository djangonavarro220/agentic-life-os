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

Use `python3 scripts/lifeos.py context-sources` only when the agent needs a cheap wiring diagnostic. The helper reports configured pointer presence and runtime inventory freshness. It must not inspect a live runtime, infer Hermes/OpenClaw from filesystem heuristics, expose cached capabilities as current truth, rank priorities, choose sources for the request, or decide what matters.

If inventory is absent or stale, the agent should use the active harness/runtime-native tools or runtime adapter to inspect the live sources needed for the current question. The helper should not pretend to know every possible runtime.

Inspect only relevant, runtime-owned sources and Life OS private tracking pointers:

- current conversation/request
- Life OS `config.json` and recent routine records
- runtime TODO/task system, if configured
- calendar/mail/session/memory pointers only when relevant and available
- active blockers or recent decisions from loaded subskills
- in-progress guided meetings recorded in Life OS private state or the runtime task system

Do not dump raw history. Distill.

## Source ladder

Use this order unless the user's request clearly narrows the scope:

1. Current conversation and explicit user ask.
2. Life OS config/source pointers and paused meeting state.
3. Runtime-owned task/follow-up source.
4. Runtime-owned routine records or cron output pointers.
5. Calendar/mail/session/memory sources only when the configured pointers say they are relevant.
6. Domain subskill state only for domains that are active, due, blocked, or explicitly named.

Stop when the answer is good enough. Loading every source is prompt sludge with a nicer hat.

## Freshness rules

- Prefer live runtime state over stale summaries when the next action depends on timing or status.
- Treat cached routine output as a clue, not truth, if it is older than the horizon the user asked for.
- If a source is unavailable, say which category is missing and continue with the best grounded context.
- Do not resurrect old completed work just because it appears in history.

## Evidence

For every surfaced item, know why it is present:

- `explicit`: named by the user or current conversation
- `due`: date/cadence says it needs attention
- `blocked`: waiting on a person/system/decision
- `risk`: deadline, failure, or high cost of ignoring
- `recent`: changed since the last relevant check

Do not show evidence labels by default, but use them internally to avoid vibes.

## Reasoning steps

1. Identify the user horizon: next 30 minutes, today, this week, or strategic.
2. Separate facts from guesses.
3. Classify items into:
   - focus now
   - waiting on others
   - waiting on user decision
   - risks/deadlines
   - can ignore for now
4. Pick a default recommendation when one clearly wins.
5. Include a next action only when it is genuinely actionable.
6. If ambiguity changes the next tool/action, ask one lightweight question.

## Output contract

Produce the shortest useful current-context answer. Do not force a dashboard, table, or fixed headings. Let the agent choose the shape that fits the question.

Default bias:

- one clear recommendation beats a full status report
- mention blockers/risks only when they affect what to do now
- include a next action when it is useful and grounded
- ask one question only when the next action truly depends on it

Avoid turning `context-now` into a corporate dashboard with fresher paint.

## State update

Do not write state by default. A normal `context-now` answer is an ephemeral view, not a record worth keeping.

Write only when the run discovers durable coordination state, for example:

- a guided meeting is paused or resumed
- a new stable user decision or preference was made
- a configured source pointer is missing, stale, or broken
- a reusable setup/routine improvement should be proposed
- a runtime-owned task/follow-up must be created or updated under the configured task policy

Do not save every “what should I do now?” output. That creates archival sludge and trains future agents on stale noise. Do not use helper scripts for semantic routine decisions.

## Data

Private state belongs in:

```text
$LIFEOS_DATA_DIR/context-now/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
