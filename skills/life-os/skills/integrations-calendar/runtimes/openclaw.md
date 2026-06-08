# OpenClaw adapter for integrations-calendar

Use `skills/life-os/runtimes/openclaw.md` as the central OpenClaw runtime adapter.

Calendar access is OpenClaw-owned. Before using calendar capabilities, inspect the active OpenClaw tools/plugins/config and use runtime-native calendar tools when available. Store only pointers and tracking metadata in Life OS state.

Ask before creating, editing, deleting, or sending calendar events. Do not copy OpenClaw calendar credentials, raw event dumps, channel targets, sessions, or tokens into this repo or Life OS data files.

Missing fact to verify before implementing deeper behavior: the exact OpenClaw calendar tool or plugin available in the target OpenClaw agent/workspace.
