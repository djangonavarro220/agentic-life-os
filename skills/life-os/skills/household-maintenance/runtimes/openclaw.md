# OpenClaw adapter for household-maintenance

Load this file only when the active runtime is OpenClaw.

## Read-only discovery

Use OpenClaw-native tools and docs available to the active agent/workspace. Prefer runtime tools over path guesses. Useful discovery classes:

- OpenClaw tasks or activity ledger for follow-ups
- memory/status/search for durable context
- cron/automation state for routine history
- channel bindings, delivery aliases, docs, vault, mail, calendar, or browser tools when enabled and relevant
- agent/workspace visibility checks when the domain depends on agent scope

## Write policy

Ask before changing OpenClaw jobs, channel routes, agent/workspace config, memory providers, vault entries, mail/calendar state, or external services. Store domain pointers in `$LIFEOS_DATA_DIR/household-maintenance/data.json`; global `config.json` should keep only setup status and pointers, not domain state. Do not write private pointers to public repo files.

## Output

Return a compact summary, the source consulted, and the next action. Stay silent for scheduled runs when the saved policy says no actionable change should be delivered.
