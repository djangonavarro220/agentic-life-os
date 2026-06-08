# Hermes runtime adapter

Use this adapter whenever a Life OS skill needs Hermes-specific discovery, installation, scheduling, delivery, or skill visibility behavior.

## Check whether Life OS is already available

From the machine/profile where Hermes runs:

```bash
hermes skills list --source all | grep -E '(^| )life-os( |$)'
hermes skills list --source all | grep -E '(^| )tasks-todo( |$)'
hermes skills inspect life-os
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

Do not write into another Hermes profile unless the user explicitly selects that profile.

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

## Skill visibility rule

The umbrella `life-os` skill is the normal entrypoint. Subskills remain lazily loaded by the umbrella. If Hermes also discovers nested subskills such as `tasks-todo`, treat that as optional runtime visibility, not a reason to bypass the umbrella unless the user explicitly asks for that subskill.

## Runtime-owned boundaries

Hermes owns:

- cron jobs
- Telegram, Discord, and other delivery routing
- tool availability
- model/provider config
- memory and vault integrations
- profile selection

Life OS may record pointers and private tracking state under `$HOME/.life-os`, but it must not copy Hermes secrets, delivery targets, raw memory dumps, or credentials into the public repo or Life OS state.
