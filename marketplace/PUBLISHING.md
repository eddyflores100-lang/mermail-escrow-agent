# Marketplace publishing notes

This document describes how to publish `mermail-escrow-agent` to each
marketplace / registry supported by the Mermail ecosystem. The skill is
intended as a **community companion** to the official
[`Nudgen-Marketing/mermail-skills`](https://github.com/Nudgen-Marketing/mermail-skills)
package.

## 1. skills.sh (portable Agent Skills CLI)

The official `skills` CLI is the primary distribution channel for portable
Mermail skills.

```bash
# From the repo root:
npx --yes skills publish
```

Before publishing, verify the skill passes the Mermail AUTHORING rules:

```bash
# Frontmatter present and valid
jq '.name, .description, .metadata.openclaw' \
  <(awk '/^---$/{n++; next} n==1' skills/mermail-escrow-agent/SKILL.md | yq -p yaml -o json)

# name matches directory name
test "$(basename skills/mermail-escrow-agent)" = "mermail-escrow-agent"

# SKILL.md ≤ 500 lines
test "$(wc -l < skills/mermail-escrow-agent/SKILL.md)" -le 500

# No unresolved TODOs
! grep -rn 'TODO' skills/mermail-escrow-agent/
```

The `package.json` at the repo root is the skills.sh manifest.

## 2. ClawHub (OpenClaw)

The ClawHub manifest is `marketplace/clawhub.json`. To publish:

```bash
npm i -g clawhub
clawhub login
clawhub publish eddyflores100-lang/mermail-escrow-agent
```

After publishing, the skill is installable from any OpenClaw client:

```bash
clawhub install eddyflores100-lang/mermail-escrow-agent
```

## 3. GitHub (companion repo)

The repo itself is the canonical source. Anyone can install locally:

```bash
git clone https://github.com/eddyflores100-lang/mermail-escrow-agent.git
cd mermail-escrow-agent

# Claude Code
claude plugin marketplace add "$(pwd)" --scope local
claude plugin install mermail-escrow-agent@mermail-escrow-agent

# Cursor (local plugin symlink)
ln -sfn "$(pwd)" ~/.cursor/plugins/local/mermail-escrow-agent

# Generic
cp -R skills/mermail-escrow-agent ~/.claude/skills/
```

## 4. Graduation to the official package

This companion skill is a candidate for graduation into
`Nudgen-Marketing/mermail-skills`. The graduation process is documented in
[MAINTAINERS.md](https://github.com/Nudgen-Marketing/mermail-skills/blob/main/MAINTAINERS.md#graduation)
of the official repo. See [`PR_DESCRIPTION.md`](../PR_DESCRIPTION.md) and
[`repo-patches/`](../repo-patches/) for the integration patches.

## 5. Not published to (and why)

- **NPM**: not a Node package. The `package.json` is for the skills CLI
  metadata only.
- **PyPI**: the helper scripts are not a Python distribution.
- **Docker**: the skill runs inside an AI client, not as a service.

## Versioning

This companion repo follows semver:

- `1.0.0` — initial public release for the Mermail Build & Demo bounty.
- `1.0.x` — patch fixes to docs, scripts, demo page.
- `1.1.0` — minor feature additions (new helper scripts, new test scenarios).
- `2.0.0` — breaking changes to the deal record schema or the state machine.
