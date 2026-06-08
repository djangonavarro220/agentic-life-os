---
name: integrations-runtime
description: Bridge to runtime-owned capabilities without duplicating secrets or private data.
version: 0.1.0
author: Agentic Life OS contributors
license: MIT
---

# integrations-runtime

Bridge Life OS playbooks to runtime-owned capabilities without duplicating secrets or private data.

## Runtime policy

Hermes and OpenClaw are first-class supported runtimes. For every Life OS skill and workflow, runtime-specific instructions must answer these questions for both runtimes:

1. How does the runtime check whether `life-os` and any relevant subskill are already available?
2. Where does the runtime install or register a skill?
3. Is this a workspace-scoped, profile-scoped, agent-scoped, or shared install?
4. Should a repo checkout be symlinked or copied, and does that require user choice?
5. Which runtime system owns scheduling, delivery, memory, vault, credentials, tools, and external side effects?
6. How does the user verify the install with native runtime commands?

Do not document a Hermes-only answer and call the workflow done. Add the OpenClaw equivalent, or explicitly mark the OpenClaw path as pending with the exact missing fact to verify.

## Runtime adapters

Load the adapter matching the active runtime before making runtime-specific recommendations or changes:

- `runtimes/hermes.md`
- `runtimes/openclaw.md`

The adapters are central and apply to all Life OS skills. Individual subskills may add narrow runtime notes only when they differ from the central adapter.

## Runtime-owned capabilities

Life OS can ask the runtime to inspect or operate capabilities, but ownership stays with the runtime:

- skills and skill visibility
- cron jobs or scheduled jobs
- delivery routes and messaging platforms
- tool availability and sandboxing
- model/provider configuration
- memory systems
- vaults and credentials
- mail/calendar integrations
- agent/profile/workspace routing

Life OS may store short pointers and tracking metadata in `$HOME/.life-os`. It must not copy runtime secrets, private chat IDs, credentials, raw memories, sessions, logs, transcripts, screenshots, or audio into the public repo or Life OS state.

## Data

Private state, if needed, belongs in:

```text
$LIFEOS_DATA_DIR/integrations-runtime/data.json
```

Do not commit personal data, credentials, private runtime config, or raw logs.
