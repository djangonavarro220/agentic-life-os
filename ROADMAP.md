# Agentic Life OS roadmap

This roadmap tracks the remaining work for turning Agentic Life OS from an operational scaffold into a useful agent-native personal advisor OS.

## Guiding principle

The main product is the skill/playbook layer: Markdown instructions that teach an LLM what to inspect, how to reason, where each source of truth lives, when to ask, when to write private coordination state, and how to report. Scripts are only boring state helpers and should not become the product. Life OS is a helper over Hermes/OpenClaw/external sources, not a second database for the user's life.

## 1. Configurable autonomy modes

Current playbooks use fixed safety rules: safe internal state updates can run autonomously, external side effects require approval. In the future this should become configurable.

### Proposed modes

```text
approval-first
  Ask before every write, runtime change, external action, or state mutation.

safe-internal
  Default. Allow read-only inspection and Life OS private tracking writes.
  Ask before contacting people, changing external systems, runtime config, cron changes, deletion, publishing, or broad migrations.

trusted-local
  Allow local/runtime maintenance actions that are reversible and scoped.
  Ask before external communication, destructive changes, public publishing, or credential/account changes.

allow-all
  Do not ask for routine actions allowed by the configured runtime policy.
  Still refuse or escalate dangerous/legal/credential/destructive operations if the runtime's own safety layer requires it.
```

### Future config shape

Potential private config in `$HOME/.life-os/config.json` unless `LIFEOS_DATA_DIR` overrides it:

```json
{
  "autonomy": {
    "mode": "safe-internal",
    "overrides": {
      "routines-heartbeat": "safe-internal",
      "tasks-todo": "trusted-local",
      "people-followups": "approval-first"
    },
    "approval_required_for": [
      "contact_people",
      "external_calendar_write",
      "external_mail_write",
      "runtime_config_change",
      "cron_create_update_delete",
      "delete_private_state",
      "public_push_or_release",
      "broad_migration"
    ]
  }
}
```

### Playbook behavior

Every subskill should eventually phrase decisions like this:

- If mode is `approval-first`, ask before doing the action.
- If mode is `safe-internal`, perform read-only inspection and private Life OS tracking writes, ask before external or runtime-owned changes.
- If mode is `trusted-local`, perform reversible local maintenance, ask before irreversible/external/public changes.
- If mode is `allow-all`, proceed without asking for actions explicitly allowed by config and runtime policy.

This should be documented in the umbrella `life-os` skill and inherited by all subskills.

## 2. Finish the core Markdown playbooks

Priority subskills that need real LLM instructions:

Added baseline playbooks:

- `health-trends`: health signals, habits, clinician-prep questions, and no-diagnosis boundaries.
- `finance-checkup`: recurring costs, renewals, anomalies, savings goals, and pointer-only finance state.
- `household-maintenance`: home, vehicle, appliance, warranty, insurance, and service follow-ups.
- `documents-renewals`: identity documents, permits, contracts, domains, certificates, and expiry lead times.
- `travel-planning`: reservations, documents, packing, itinerary risks, and travel follow-ups.
- `purchase-decisions`: requirements, comparisons, total cost, risk, timing, and post-purchase tracking.
- `learning-projects`: learning goals, courses, practice sessions, notes, review cadence, and blockers.
- `work-portfolio`: achievement logs, portfolio evidence, interview stories, opportunities, and professional follow-ups.
- `digital-hygiene`: accounts, backups, 2FA, devices, domains, abandoned services, privacy, and security hygiene.
- `decision-journal`: decisions, options, tradeoffs, assumptions, review dates, and outcomes.
- `system-improvement`: retrospectives, skill candidates, routine tuning, and a lightweight improvement backlog.

Remaining priority subskills that need real LLM instructions:

- `core-config`: how to read/update private config safely, including autonomy modes.
- `core-install`: installer conversation, data-dir explanation, runtime skill visibility, runtime-owned system discovery, and approval-gated registration/bridging.
- `core-doctor`: diagnose repo, private state, runtime visibility, runtime-owned systems, and safe next actions without repair side effects.
- `integrations-runtime`: how to discover runtime capabilities with native commands/docs, classify ownership, and choose leave/bridge/import/migrate without hard-coding private state.

## 3. Flesh out routine skills

Current MVP playbooks exist for heartbeat, pulse, now, todo, and people follow-ups. Remaining routines need the same treatment:

- `routines-daily-review`
- `routines-weekly-review`
- `routines-monthly-review`
- `routines-quarterly-review`

Each should define:

- trigger conditions
- sources to inspect
- reasoning steps
- output contract
- state update rules
- autonomy/approval behavior
- no-op/silence behavior where appropriate

## 4. Flesh out domain skills

Needed next:

- `context-inbox`: triage inbox-like signals without becoming an email scraper by default.
- `context-commitments`: detect promises, waiting items, and user obligations.
- `events-reminders`: events, lead times, reminders, and calendar pointers.
- `people-contacts`: contact/source-of-truth policy without storing sensitive raw contact data.
- `gifts`: gift lead times, taste pointers, budget, delivery windows, and approval gates.

## 5. Runtime adapters

Runtime docs should be lazy-loaded and adapter-specific. Hermes and OpenClaw are both first-class support targets. The central adapters now include native discovery commands for skills, cron/schedules, tasks/background ledgers, memory, delivery, tools/plugins, profiles/agents/workspaces, and config/doctor checks.

Central adapters now exist at:

- `skills/life-os/runtimes/hermes.md`
- `skills/life-os/runtimes/openclaw.md`

For every Life OS skill, runtime docs should cover both runtimes whenever the workflow touches:

- checking whether the skill is already visible
- where to install/register the skill
- symlink vs copy choices
- profile/workspace/agent/shared scope
- cron creation/listing/status
- memory/profile/workspace boundaries
- tool availability and sandboxing
- Telegram/Discord/channel delivery ownership
- approval before gateway/runtime config changes

If one runtime path is not known yet, mark exactly what needs verification. Do not leave generic `Pending` stubs without the missing fact.

## 6. Output contracts and examples

Add examples for each subskill with fake data only:

- Pulse output
- Heartbeat alert output
- Now context output
- Task capture/review output
- Follow-up/gift output
- Doctor report
- Installer conversation

Examples should be short and public-safe.

## 7. Private data schema improvements

Current schemas are intentionally permissive. Future schemas should become useful without overfitting:

- source-decision records: owner/runtime/tool/access instructions
- operational state: last check time, suppression windows, last-summary pointer, priority score
- dated caches/result snapshots
- runtime-owned tool/source pointers
- autonomy config schema
- task/follow-up/gift minimal schemas for Life-OS-created notes only

Do not store full raw private dumps just because the schema can represent them. Caches may contain text when needed, but they should be deliberate, dated, private-state only, and never include credentials or secrets.

## 8. Cron and routine install design

Future installer should propose schedules but not silently create runtime crons.

Default recommendation:

- heartbeat: every few hours, silent unless actionable
- pulse: daily
- daily review: daily, optional
- weekly review: weekly, including system-improvement candidates
- monthly review: monthly
- quarterly review: quarterly

Installer should ask lightly:

```text
Do you want the recommended schedule? You can say yes, no, less often, mornings only, weekends, etc.
```

Cron delivery targets and concrete job IDs remain runtime-owned. Life OS may store pointers and tracking metadata.

## 9. CI and validation

Keep two lint layers:

- external Agent Skills scanner (`agent-skills-mcp`)
- local repo policy lint

Future validation ideas:

- Markdown structure checks for required playbook sections
- fake-data example validation
- schema validation against fixtures
- no personal-data fixture scan
- docs link checks

## 10. Non-goals

Avoid these until explicitly approved:

- turning Life OS into a standalone app
- adding more scripts as the primary behavior
- storing secrets or runtime credentials
- copying runtime memory/mail/calendar data into Life OS
- silently creating or deleting crons
- globally registering every subskill
- making noisy heartbeat/pulse outputs
- turning self-improvement into endless refactoring instead of small shipped improvements
