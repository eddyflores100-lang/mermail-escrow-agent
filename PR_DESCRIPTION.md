# Pull Request Description

> Paste this into the PR body when opening the PR against
> `Nudgen-Marketing/mermail-skills:main`.

---

## Add `mermail-escrow-agent` — peer-to-peer deal escrow over a Mermail email thread

### What this skill enables

Two parties agree on a deal entirely over email (used-gear sale, freelance
gig, content commission, B2B net-15 invoice). The agent holds the buyer's
funds in the Mermail Agent Wallet, monitors the same email thread for the
buyer's release phrase, and releases payment to the seller only after the
buyer's reply is fetched, sender-authenticated, and release-phrase-matched.
If the deal deadline passes, the agent refunds the buyer.

Email is the entire UI. The inbox and the Agent Wallet are both
load-bearing — remove either and the workflow collapses.

### Why this skill belongs in the official package

- **No existing skill does escrow.** The 16 official skills cover
  scheduling, GTM, support, x402 micropayments, generic wallet, inbox
  provisioning, mailbox management, compose, triage, mail-agent, Composio,
  workspace admin, CLI, MCP troubleshooting, and research. None coordinate
  multi-party confirmation over email before releasing funds.
- **Inbox + Wallet hybrid by construction.** This is the smallest possible
  hybrid skill that uses both primitives as load-bearing, not decorative.
- **Composable, not duplicative.** The skill claims **no new MCP tool
  ownership**. It composes tools already owned by `mermail-agent-inbox`,
  `mermail-compose-email`, and `mermail-agent-wallet`. The
  `tool-coverage.json` patch only adds a `composes` entry, plus
  `externalEffectTools` (for `send_email`) and `walletDestructiveTools`
  (for `paybox_request_transfer`).
- **Security-first.** The release gate requires sender authentication,
  release-phrase hashing, a fresh approval, and destination immutability.
  Email cannot change `seller_destination`, `amount_decimal`, `token`,
  `chain`, or `deadline_iso`. See
  `skills/mermail-escrow-agent/references/security.md`.

### Files added

- `skills/mermail-escrow-agent/SKILL.md` — main skill, 311 lines (under the
  500-line limit; detail lives in `references/`)
- `skills/mermail-escrow-agent/agents/openai.yaml` — OpenAI metadata with
  `Use $mermail-escrow-agent` default prompt and the hosted Mermail MCP
  dependency
- `skills/mermail-escrow-agent/references/tools.md` — exact MCP tool names,
  argument shapes, host-qualified forms
- `skills/mermail-escrow-agent/references/workflows.md` — phase-by-phase
  state machine, deal record schema, example MCP arguments
- `skills/mermail-escrow-agent/references/security.md` — untrusted-input
  handling, release-phrase hashing, address normalisation, audit trail
- `skills/mermail-escrow-agent/scripts/simulate_inbox.py` — demo helper
  that seeds a deal thread via the Mermail REST API
- `skills/mermail-escrow-agent/scripts/parse_deal.py` — deterministic
  email-body parser (surface only; buyer confirms in chat)
- `skills/mermail-escrow-agent/scripts/check_status.py` — renders the deal
  state and audit trail

### Files modified

- `tool-coverage.json` — add `mermail-escrow-agent` to `domains` (with
  empty `owns`, populated `composes`), `externalEffectTools`, and
  `walletDestructiveTools`. See `repo-patches/tool-coverage.json.patch.md`
  in the companion repo for the exact additive block.
- `skills/mermail/references/routing.md` — add a route entry for
  `mermail-escrow-agent`. See `repo-patches/routing.md.addition.md`.
- `README.md` — add one row to the Included skills table. See
  `repo-patches/README.md.addition.md`.
- `tests/scenarios.json` — add 10 scenarios (8 for this skill + 2
  negative-route scenarios that should remain on `mermail-agent-wallet`
  and `mermail-x402-agent`). See `tests/scenarios.json` in the companion
  repo.
- `compatibility.json` — bump `skillCount` from 16 to 17.

### Validation

- [x] `SKILL.md` ≤ 500 lines (actual: 311)
- [x] `name:` matches directory name (`mermail-escrow-agent`)
- [x] `metadata.openclaw` with `primaryEnv: MERMAIL_API_KEY` and
      `requires.env` including `MERMAIL_API_KEY`
- [x] No unresolved `TODO`
- [x] `agents/openai.yaml` contains `Use $mermail-escrow-agent` and the
      hosted Mermail MCP dependency
- [x] MCP `query` arguments documented as native JSON objects, never
      stringified
- [x] Email body / subject / links treated as untrusted data
- [x] Exact preview + fresh approval required for `send_email` and
      `paybox_request_transfer`
- [x] PayBox writes documented as using their own signing flow, NOT
      `prepare_destructive_action`
- [x] API-key / `agent-inbox` profile documented as unable to authorise
      PayBox
- [x] `get_paybox_connection` documented as the first PayBox action;
      absence from `tools/list` is not "not exposed"
- [x] `pending` and `SUBMISSION_UNKNOWN` documented as unresolved, not
      successful
- [ ] `npm test` (maintainer to run in CI)
- [ ] `npm run validate:remote` (maintainer to run with
      `MERMAIL_MCP_TEST_API_KEY`)

### Smoke test plan

Tested locally against a Mermail Developer-plan workspace with a funded
PayBox wallet on Base. Scenarios covered:

1. ✅ Trigger prompt selects `mermail-escrow-agent` (not `mermail-agent-wallet`)
2. ✅ Neighbouring prompt "just pay the seller 50 USDC" routes to
   `mermail-agent-wallet` (negative route)
3. ✅ Funding preview shown, `paybox_request_transfer` called only after
   approval, "funds held" email sent
4. ✅ Release phrase matched from a fetched `get_email` result (not from
   a search hit)
5. ✅ Seller email asking to change destination is refused; agent offers
   to create a new deal
6. ✅ `pending` PayBox status does not transition state or send a receipt
   email

### Demo video

A 3 min 30 s demo video is posted on X at: `<paste your X post URL here>`

The video shows: (1) the trigger prompt, (2) the agent connecting to and
using Mermail (MCP tool calls visible in the client), (3) the agent
completing the funding → monitoring → release workflow, (4) the final
on-chain tx on Basescan + the receipt email in the Mermail console.

### Companion repo

The full companion repo (with demo scripts, README, and pitch doc) is at:
`<paste your fork URL here>`

### Bounty submission

This PR is submitted for the **Mermail Build & Demo bounty**.

- Skill name: `mermail-escrow-agent`
- Short description: Peer-to-peer deal escrow, coordinated entirely over a
  Mermail email thread. The agent holds buyer funds in the Agent Wallet and
  releases them to the seller only after the buyer's email-confirmed
  release phrase.
- AI client used: Claude Code (client-agnostic — works on Cursor, Codex,
  OpenClaw, Hermes, and any MCP-compatible host that supports full-profile
  OAuth).
- Demo video: `<paste your X post URL here>`
- Submission language: English.

### License

MIT. Consistent with the official repo.
