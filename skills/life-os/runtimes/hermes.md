# Hermes runtime adapter

Use this adapter whenever a Life OS skill needs Hermes-specific discovery, installation, scheduling, delivery, or skill visibility behavior.

Hermes docs are authoritative for Hermes behavior. Prefer the live CLI help and docs over assumptions from this repo. Life OS should normally leave Hermes-owned data in Hermes and record config pointers/access instructions.

## Scope model

Hermes state is profile-scoped. Each Hermes profile can have its own:

- skills
- config
- cron jobs
- plugins and tools
- memories and sessions
- gateway/platform routing

Do not write into another Hermes profile unless the user explicitly selected that profile.

## Read-only discovery

Use these commands to understand the current Hermes runtime before proposing changes:

```bash
hermes --help
hermes status --all
hermes doctor
hermes config path
hermes config check
hermes profile list
hermes skills list --source all
hermes skills inspect life-os
hermes skills config
hermes cron list --all
hermes cron status
hermes memory status
hermes tools list
hermes gateway status
hermes plugins list
hermes mcp list
hermes sessions list
```

If a command is unavailable in the installed Hermes version, run the closest `--help` command and adapt. Do not guess hidden paths.

## Check whether Life OS is already available

From the machine/profile where Hermes runs:

```bash
hermes skills list --source all | grep -E '(^|[[:space:]])life-os([[:space:]]|$)'
hermes skills inspect life-os
```

Optional subskill visibility check:

```bash
hermes skills list --source all | grep -E '(^|[[:space:]])tasks-todo([[:space:]]|$)'
```

If `life-os` is listed, do not re-register the skill. Run the state installer from the repo checkout instead:

```bash
cd <agentic-life-os-checkout>
npm run lifeos -- install --runtime hermes
npm run lifeos -- doctor
```

## Where Hermes installs local skills

Hermes local skills live under:

```text
$HERMES_HOME/skills/<category>/<skill-name>/
```

Default profile example:

```text
$HOME/.hermes/skills/productivity/life-os/
```

Named profiles use that profile's Hermes home, for example:

```text
$HOME/.hermes/profiles/<profile>/skills/productivity/life-os/
```

## Fresh local install from a repo checkout

If the user cloned `agentic-life-os` but Hermes cannot see `life-os`, ask whether they want a symlink or a copy.

Symlink, best for active development:

```bash
cd <agentic-life-os-checkout>
mkdir -p "$HOME/.hermes/skills/productivity"
ln -sfn "$PWD/skills/life-os" "$HOME/.hermes/skills/productivity/life-os"
hermes skills list --source local | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime hermes
npm run lifeos -- doctor
```

Copy, best for a static snapshot:

```bash
cd <agentic-life-os-checkout>
mkdir -p "$HOME/.hermes/skills/productivity"
rm -rf "$HOME/.hermes/skills/productivity/life-os"
cp -R skills/life-os "$HOME/.hermes/skills/productivity/life-os"
hermes skills list --source local | grep -E 'life-os|tasks-todo'
npm run lifeos -- install --runtime hermes
npm run lifeos -- doctor
```

If the target is a named profile, replace `$HOME/.hermes` with that profile's Hermes home after the user selects it.

## Skill visibility rule

The umbrella `life-os` skill is the normal entrypoint. Subskills remain lazily loaded by the umbrella. If Hermes also discovers nested subskills such as `tasks-todo`, treat that as optional runtime visibility, not a reason to bypass the umbrella unless the user explicitly asks for that subskill.

## Runtime-owned capabilities

Hermes owns:

- skills and skill enablement
- cron jobs and scheduled jobs
- Telegram, Discord, and other delivery routing
- gateway/platform state
- tools and tool availability
- model/provider config
- memory provider config and built-in memory
- vault/secrets integrations
- plugins and MCP servers
- profile selection
- session history

Life OS may record pointers and private tracking state under `$HOME/.life-os`, but it must not copy Hermes secrets, delivery targets, raw memory dumps, sessions, transcripts, logs, or credentials into the public repo or Life OS state. Dated caches/result snapshots are allowed in private Life OS state when useful, but never credentials or full raw dumps.

## Runtime-owned storage pointers

Record pointers/access instructions in Life OS config when a skill needs to find Hermes-owned records later.

Cron, verified against Hermes cron docs (`/docs/user-guide/features/cron`) and `cron/jobs.py` in Hermes Agent:

```text
active Hermes home/cron/jobs.json
active Hermes home/cron/output/<job_id>/<timestamp>.md
```

Use `hermes config path` to identify the active profile/config context, then prefer:

```bash
hermes cron list --all
hermes cron status
```

Memory:

```bash
hermes memory status
```

Sessions:

```bash
hermes sessions list
```

Do not copy full Hermes cron output, memory, transcripts, or logs into repo docs. Private Life OS state may keep pointers, last-checked timestamps, last-summary pointers, suppression windows, and caches when useful.

## Integration guidance

Default recommendation: leave Hermes-owned systems in Hermes and bridge through Hermes tools/pointers.

Ask before:

- creating/editing/removing `hermes cron` jobs
- changing gateway delivery routes or channel prompts
- changing profile config or switching the default profile
- enabling/disabling tools, plugins, MCP servers, or skills
- changing memory providers or writing durable Hermes memories
- importing, migrating, or reconnecting Hermes-owned data/references

Never build path-specific Python/JS detectors for Hermes internals in this repo. Use Hermes commands, docs, and LLM reasoning at install/doctor time.
