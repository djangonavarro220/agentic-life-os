# OpenClaw runtime adapter

Use this adapter whenever a Life OS skill needs OpenClaw-specific discovery, installation, scheduling, delivery, agent workspace, or skill visibility behavior.

## Check whether Life OS is already available

From the machine/profile where OpenClaw runs:

```bash
openclaw skills list | grep -E '(^| )life-os( |$)'
openclaw skills info life-os
openclaw skills check
```

For a specific OpenClaw agent, include `--agent <id>`:

```bash
openclaw skills list --agent <id>
openclaw skills info life-os --agent <id>
openclaw skills check --agent <id>
```

If `life-os` is listed, do not re-register the skill. Run the state installer from the repo checkout instead:

```bash
cd <agentic-life-os-checkout>
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

## Where OpenClaw finds skills

OpenClaw can see skills from several locations. Current precedence from OpenClaw docs is:

1. `<workspace>/skills/`
2. `<workspace>/.agents/skills/`
3. `$HOME/.agents/skills/`
4. `$HOME/.openclaw/skills/`
5. bundled skills
6. `skills.load.extraDirs` from `$HOME/.openclaw/openclaw.json`

Use workspace skills when the install belongs to one agent/workspace. Use `$HOME/.openclaw/skills/<name>/` for a managed shared skill. Use `skills.load.extraDirs` only when the user intentionally wants a low-precedence external folder.

## Fresh local install from a repo checkout

If the user cloned `agentic-life-os` but OpenClaw cannot see `life-os`, ask whether they want a copy or a symlink, and ask which OpenClaw scope to use: active workspace, shared managed skill, or extra dir.

Workspace copy, safest default:

```bash
cd <agentic-life-os-checkout>
mkdir -p <openclaw-workspace>/skills
rm -rf <openclaw-workspace>/skills/life-os
cp -R skills/life-os <openclaw-workspace>/skills/life-os
openclaw skills list | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

Shared managed copy:

```bash
cd <agentic-life-os-checkout>
mkdir -p "$HOME/.openclaw/skills"
rm -rf "$HOME/.openclaw/skills/life-os"
cp -R skills/life-os "$HOME/.openclaw/skills/life-os"
openclaw skills list | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

Development symlink, only if the user wants live repo edits to affect OpenClaw immediately:

```bash
cd <agentic-life-os-checkout>
mkdir -p <openclaw-workspace>/skills
ln -sfn "$PWD/skills/life-os" <openclaw-workspace>/skills/life-os
openclaw skills list | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime openclaw
npm run lifeos -- doctor
```

Prefer copy if sandboxing, deployment packaging, or cross-machine sync is involved. Symlinks can be fragile when a runtime copies, sandboxes, or syncs workspaces.

## Agent visibility

If only some OpenClaw agents should see Life OS, configure visibility through OpenClaw agent skill settings such as `agents.defaults.skills` or `agents.list[].skills`. Do not solve per-agent visibility by duplicating private Life OS state or hard-coding agent IDs into this repo.

## Runtime-owned boundaries

OpenClaw owns:

- agents and workspaces
- channel routing and delivery
- cron or automation jobs
- tool availability and sandboxing
- model/provider config
- memory, vault, and credentials

Life OS may record pointers and private tracking state under `$HOME/.life-os`, but it must not copy OpenClaw secrets, channel targets, raw memory dumps, sessions, or credentials into the public repo or Life OS state.
