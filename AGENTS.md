# Agent guidance

This repo contains a portable Agent Skills based personal advisor OS.

## Rules

- Always use the [`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) review pattern for non-trivial product/design changes: interview the plan one question at a time, recommend an answer for each question, inspect the repo instead of asking when code/docs can answer it, and walk the decision tree until the design is clear enough to implement. Keep the questions about the public repo/product, not the user's personal install.
- Keep the repo public-safe: no personal data, real chat IDs, secrets, tokens, local logs, or private runtime config.
- Private state belongs in `$HOME/.life-os` by default, or `LIFEOS_DATA_DIR` when explicitly set. Never commit private state files.
- Life OS is a helper/coordination layer over the active runtime, not the owner of the user's life data. By default, real data stays in Hermes/OpenClaw/external sources; each Life OS skill stores its own source decisions, pointers, access notes, operational state, caches, and Life-OS-specific preferences.
- Runtime credentials, delivery routing, memory, vault, mail/calendar credentials, tasks, contacts, birthdays, and cron ownership belong to the runtime or external source unless the user explicitly created a Life OS note/preference/state item.
- Prefer small skills and lazy loading over one giant prompt.
- Validate Markdown, JSON, YAML, frontmatter, and schemas before committing.
- Add runtime-specific instructions under `runtimes/` only after checking the actual runtime docs or code.
- Treat Hermes and OpenClaw as first-class supported runtimes. For any workflow that mentions skill availability, install/register paths, scheduling, delivery, or global skill visibility, document both runtime paths or explicitly mark the missing runtime path as pending with the fact that must be verified.
- Keep scripts strictly mechanical and deterministic: validation, schema/frontmatter checks, public-safety scans, boring file-layout/state creation, and smoke tests. Do not encode semantic product decisions in scripts.
- Runtime discovery and integration decisions belong to the agent playbooks, not helper scripts. The LLM should inspect the active runtime with runtime-native tools/docs, then decide where tasks, crons/schedules, reminders, memory, delivery routes, birthdays, contacts, or other systems live, and record each domain source decision in the owning skill's data file. Ask the user before changing any runtime-owned system.
- When tempted to add a script, first classify it: mechanical guardrail or state helper is acceptable; heuristic discovery, policy choice, prioritization, migration strategy, routing, or integration ownership is agent semantics and should be written as skill instructions instead.

## Current architecture

- `skills/life-os/SKILL.md` is the umbrella entrypoint.
- `skills/life-os/skill-index.yaml` maps routines/tasks to subskills.
- Subskills live under `skills/life-os/skills/<subskill>/`.
- Subskills are normally reached through the umbrella skill. Any runtime-level visibility/global registration is an explicit runtime adapter decision, not a helper-script side effect.

## Current product decisions

- A Life OS install has two layers:
  - **mechanical install:** repo/private files exist and skills are visible;
  - **semantic install:** source, schedule, delivery, routine, review-cron, and record-keeping decisions have been asked and answered. Horizontal core choices live in global `config.json`; domain-specific choices live in the owning skill data files.
- Do not say Life OS is fully installed unless `lifeos.py doctor` reports `semantic_health.complete: true` and `safe_to_claim_fully_installed: true`. Review meeting crons must be either installed/reused or explicitly declined by the user before setup is complete.
- If `doctor` reports `install_claim: mechanical_only` or `setup_completion.status: incomplete`, say that plainly, show/propose the completion checklist, inspect the active runtime for the next pending item, and continue the setup loop instead of hand-waving. “Looks installed” is not enough.
- Horizontal core choices belong in `$LIFEOS_DATA_DIR/config.json`: task source, memory/context source, routine run records, schedule/delivery policy, and trigger defaults/overrides. Domain-specific answers belong in the owning skill data file. Store pointers and access notes, not full personal data. Avoid mixed prompt context by loading only the active runtime's Markdown adapter, not by splitting config into one file per runtime.
- Review meetings are containers for due review items, not fixed monoliths. Larger reviews should run as guided conversations that ask one focused question at a time, record paused/in-progress state, and let current context resurface unfinished meetings. Each review item may have its own cadence: daily, weekly, every two weeks, monthly, quarterly, manual only, or change-triggered. System-improvement is a monthly-by-default review item inside that meeting flow, not necessarily a standalone meeting; development-heavy setups may choose weekly. When due, it reviews the whole setup map, stays silent when nothing needs input, and surfaces only newly discovered or changed items that need a decision.
- Cron jobs are runtime-owned. Life OS may provide templates and plans, but must not create, delete, enable, disable, or reschedule crons without explicit user approval.
- Delivery routing is runtime-owned. Store a delivery pointer/alias only after the user chooses it; never commit private chat IDs or runtime config.
- The helper script may track required questions, saved answers, install claims, and no-side-effect plans. It must not decide priorities, infer private preferences, or silently connect runtime systems.
- The heartbeat product direction is dynamic runtime discovery, capability inventory, active/candidate watch targets, and dynamic skill loading. Do not collapse it into a static checklist of hard-coded checks.
- Public repo content must stay generic and language-neutral. Do not hard-code one user's phrasing, language, chats, tasks, or workflow into skills, tests, docs, or examples.

## Helper command guide

Run these from the repo root.

```bash
npm run lifeos -- install --runtime <hermes|openclaw|unknown>
```

Creates or refreshes private state files in `$HOME/.life-os` by default. It also initializes `semantic_setup`. It does not create crons, delivery routes, memory entries, credentials, or migrations.

```bash
npm run lifeos -- doctor
```

Checks repo/private-state health and semantic setup status. Important fields:

- `semantic_health.complete`: whether all required setup questions are answered.
- `install_claim`: `mechanical_only` or `fully_configured`.
- `safe_to_claim_fully_installed`: only true when it is safe to say the install is complete.
- `semantic_health.pending_questions`: remaining questions to ask.

```bash
npm run lifeos -- next-question
```

Returns exactly the next required semantic setup question plus a command hint for saving the answer. Use this for conversational setup loops.

```bash
npm run lifeos -- answer <decision-key> '<answer>' --kind <reuse_existing|manual_only|propose_change|disabled|custom>
```

Saves one user-approved setup decision. Horizontal core decisions are stored in global config; domain-specific decisions are stored in the owning skill data file. Keep answers as pointers/access notes when possible, not raw data dumps. Prefer structured `--kind` values so future agents can distinguish reused runtime systems, manual-only choices, proposed changes, disabled routines, and custom policies without parsing prose.

```bash
npm run lifeos -- plan
```

Prints the remaining setup plan and cron templates. This command has no side effects and must not create runtime crons.

```bash
npm run lifeos -- config
```

Shows private runtime/config state. Treat output as private and do not copy secrets, raw personal data, or runtime delivery targets into repo docs.

## Semantic setup loop

1. Run `npm run lifeos -- install --runtime <runtime>` if state may be missing.
2. Run `npm run lifeos -- doctor`.
3. Run `npm run lifeos -- discover-runtime --runtime <runtime>` to populate the read-only capability inventory before proposing watch targets or runtime changes.
4. Run `npm run lifeos -- define-heartbeat` to identify the single main heartbeat. If none exists, it records the creation template; do not create or edit the runtime cron until the user approves.
5. Run `npm run lifeos -- propose-watch-targets` only when the user wants to review additional watches; the heartbeat itself is the main product, not a cron-inventory UI.
6. If `semantic_health.complete` is false, run `npm run lifeos -- next-question`.
7. Ask the user that question in the active setup conversation.
8. Save the approved answer with `npm run lifeos -- answer <key> '<answer>'`.
9. Repeat doctor -> discover-runtime -> define-heartbeat -> next-question -> answer until complete, or until the user stops setup.
10. Review meeting crons are part of setup completion: either create/reuse the approved runtime cron jobs for the review meetings, or save the user's explicit opt-out/manual-only decision. Do not claim setup complete while this is undecided.
11. Only after semantic setup is complete and the user approves, turn any remaining `plan` cron templates into runtime-owned jobs.
12. Re-run runtime visibility/status checks after any runtime-owned change.
