# Hermes adapter for documents-renewals

Load this file only when the active runtime is Hermes.

## Read-only discovery

Use Hermes-native tools and commands available in the active profile. Prefer runtime tools over path guesses. Useful discovery classes:

- memory/profile lookup for existing source decisions or durable context
- task/TODO tools for follow-ups
- cron/job status for routine history
- calendar, mail, docs, vault, or browser tools when enabled and relevant
- session search for prior decisions when the user references earlier work

## Write policy

Ask before changing Hermes cron jobs, gateway delivery, channel prompts, profile config, memory providers, vault entries, mail/calendar state, or external services. Store domain pointers in `$LIFEOS_DATA_DIR/documents-renewals/data.json`; global `config.json` should keep only setup status and pointers, not domain state. Do not write private pointers to public repo files.

## Output

Return a compact summary, the source consulted, and the next action. Stay silent for scheduled runs when the saved policy says no actionable change should be delivered.
