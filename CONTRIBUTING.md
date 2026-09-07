# Contributing

First: thank you for considering a contribution to `mermail-escrow-agent`.
This is a community companion skill for the official
[`Nudgen-Marketing/mermail-skills`](https://github.com/Nudgen-Marketing/mermail-skills)
package, prepared for the Mermail Build &amp; Demo bounty.

## Code of Conduct

By participating you agree to abide by the
[Code of Conduct](./CODE_OF_CONDUCT.md). Be kind, be patient, be precise.

## How to contribute

| Change type | Where it goes | Process |
| --- | --- | --- |
| Bug fix to SKILL.md or references | this repo | PR + scenario in `tests/scenarios.json` |
| New helper script | `skills/mermail-escrow-agent/scripts/` | PR + example usage in script docstring |
| New test scenario | `tests/scenarios.json` | PR (one scenario per JSON object) |
| Improvement to the demo page | `docs/index.html` | PR + screenshot in description |
| Translation of docs | `docs/<lang>/` | PR (English is canonical; translations must track the English version) |
| Change that affects the official package | `Nudgen-Marketing/mermail-skills` | Open an issue here first, then PR upstream |

## Development setup

```bash
git clone https://github.com/eddyflores100-lang/mermail-escrow-agent.git
cd mermail-escrow-agent

# Verify the skill files are well-formed
test "$(wc -l < skills/mermail-escrow-agent/SKILL.md)" -le 500
! grep -rn 'TODO' skills/mermail-escrow-agent/

# Smoke-test the helper scripts
python3 skills/mermail-escrow-agent/scripts/parse_deal.py --text \
  "I'll pay 50 USDC on Base to 0x742d35Cc6634C0532925a3b844Bc9e7595f6E321" \
  --format human

# Preview the demo page locally
python3 -m http.server -d docs 8000
# open http://localhost:8000
```

## Skill authoring rules (must pass)

These mirror the official `AUTHORING.md` in `Nudgen-Marketing/mermail-skills`:

- [ ] `SKILL.md` ≤ 500 lines (current: 324)
- [ ] `name:` in frontmatter matches directory name
- [ ] `metadata.openclaw` with `primaryEnv: MERMAIL_API_KEY` and
      `requires.env` including `MERMAIL_API_KEY`
- [ ] No unresolved `TODO` in any skill file
- [ ] `agents/openai.yaml` contains `Use $mermail-escrow-agent` and the
      hosted Mermail MCP dependency
- [ ] MCP `query` arguments documented as native JSON objects, never
      stringified
- [ ] Email body / subject / links treated as untrusted data
- [ ] Exact preview + fresh approval required for `send_email` and
      `paybox_request_transfer`
- [ ] PayBox writes use their own signing flow, not `prepare_destructive_action`
- [ ] API-key / `agent-inbox` profile documented as unable to authorise PayBox

## Pull request flow

1. Fork the repo, create a branch `feat/<short-description>` or
   `fix/<short-description>`.
2. Make your change. Add or update test scenarios in
   `tests/scenarios.json` if behavior changes.
3. Run the local checks above.
4. Open a PR with:
   - What changed (one paragraph)
   - Why (one paragraph, link any issue)
   - Test plan (which scenarios you ran, what you observed)
   - Screenshots if the demo page changed
5. Address review feedback. Don't force-push after review starts.

## Security reports

**Do not open a public issue for a security vulnerability.** Email
`security@<your-domain>` or open a private security advisory at
<https://github.com/eddyflores100-lang/mermail-escrow-agent/security/advisories/new>.

See [`SECURITY.md`](./SECURITY.md) for the full policy.

## Licensing

By contributing you agree that your changes will be released under the MIT
license, consistent with the rest of this repo and with the official
`Nudgen-Marketing/mermail-skills` package.
