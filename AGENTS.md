# Agent guidance

This repo contains a portable Agent Skills based personal advisor OS.

## Rules

- Keep the repo public-safe: no personal data, real chat IDs, secrets, tokens, local logs, or private runtime config.
- Private state belongs in `$HOME/.life-os` by default, or `LIFEOS_DATA_DIR` when explicitly set. Never commit private state files.
- Runtime credentials, delivery routing, memory, vault, mail/calendar credentials, and cron ownership belong to the runtime.
- Prefer small skills and lazy loading over one giant prompt.
- Validate Markdown, JSON, YAML, frontmatter, and schemas before committing.
- Add runtime-specific instructions under `runtimes/` only after checking the actual runtime docs or code.
- Treat Hermes and OpenClaw as first-class supported runtimes. For any workflow that mentions skill availability, install/register paths, scheduling, delivery, or global skill visibility, document both runtime paths or explicitly mark the missing runtime path as pending with the fact that must be verified.
- Keep scripts strictly mechanical and deterministic: validation, schema/frontmatter checks, public-safety scans, boring file-layout/state creation, and smoke tests. Do not encode semantic product decisions in scripts.
- Runtime discovery and integration decisions belong to the agent playbooks, not helper scripts. The LLM should inspect the active runtime with runtime-native tools/docs, then decide whether tasks, crons/schedules, reminders, memory, delivery routes, or other existing systems should be left alone, bridged, imported, or migrated. Ask the user before changing any runtime-owned system.
- When tempted to add a script, first classify it: mechanical guardrail or state helper is acceptable; heuristic discovery, policy choice, prioritization, migration strategy, routing, or integration ownership is agent semantics and should be written as skill instructions instead.

## Current architecture

- `skills/life-os/SKILL.md` is the umbrella entrypoint.
- `skills/life-os/skill-index.yaml` maps routines/tasks to subskills.
- Subskills live under `skills/life-os/skills/<subskill>/`.
- `tasks-todo` may optionally be registered globally by a runtime during install, but subskills are not globally exposed by default.
