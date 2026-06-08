# Hermes adapter for integrations-calendar

Use `skills/life-os/runtimes/hermes.md` as the central Hermes runtime adapter.

Calendar access is Hermes-owned. Before using calendar capabilities, inspect the active Hermes tools/config and use runtime-native calendar tools when available. Store only pointers and tracking metadata in Life OS state.

Ask before creating, editing, deleting, or sending calendar events. Do not copy Hermes calendar credentials, raw event dumps, private delivery targets, or tokens into this repo or Life OS data files.

Missing fact to verify before implementing deeper behavior: the exact Hermes calendar tool or adapter available in the target Hermes profile.
