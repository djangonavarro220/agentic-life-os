# Agent guidance

This repo contains a portable Agent Skills based personal advisor OS.

## Rules

- Keep the repo public-safe: no personal data, real chat IDs, secrets, tokens, local logs, or private runtime config.
- Private state belongs in `$HOME/.life-os` by default, or `LIFEOS_DATA_DIR` when explicitly set. Never commit private state files.
- Life OS is a helper/coordination layer over the active runtime, not the owner of the user's life data. By default, real data stays in Hermes/OpenClaw/external sources; Life OS stores source decisions, pointers, access notes, operational state, caches, and Life-OS-specific preferences.
- Runtime credentials, delivery routing, memory, vault, mail/calendar credentials, tasks, contacts, birthdays, and cron ownership belong to the runtime or external source unless the user explicitly created a Life OS note/preference/state item.
- Prefer small skills and lazy loading over one giant prompt.
- Validate Markdown, JSON, YAML, frontmatter, and schemas before committing.
- Add runtime-specific instructions under `runtimes/` only after checking the actual runtime docs or code.
- Treat Hermes and OpenClaw as first-class supported runtimes. For any workflow that mentions skill availability, install/register paths, scheduling, delivery, or global skill visibility, document both runtime paths or explicitly mark the missing runtime path as pending with the fact that must be verified.
- Keep scripts strictly mechanical and deterministic: validation, schema/frontmatter checks, public-safety scans, boring file-layout/state creation, and smoke tests. Do not encode semantic product decisions in scripts.
- Runtime discovery and integration decisions belong to the agent playbooks, not helper scripts. The LLM should inspect the active runtime with runtime-native tools/docs, then decide where tasks, crons/schedules, reminders, memory, delivery routes, birthdays, contacts, or other systems live, and record that source decision in Life OS config. Ask the user before changing any runtime-owned system.
- When tempted to add a script, first classify it: mechanical guardrail or state helper is acceptable; heuristic discovery, policy choice, prioritization, migration strategy, routing, or integration ownership is agent semantics and should be written as skill instructions instead.

## Current architecture

- `skills/life-os/SKILL.md` is the umbrella entrypoint.
- `skills/life-os/skill-index.yaml` maps routines/tasks to subskills.
- Subskills live under `skills/life-os/skills/<subskill>/`.
- Subskills are normally reached through the umbrella skill. Any runtime-level visibility/global registration is an explicit runtime adapter decision, not a helper-script side effect.
