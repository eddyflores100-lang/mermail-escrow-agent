# mermail-escrow-agent

> Peer-to-peer deal escrow, coordinated entirely over a Mermail email thread.
> The agent holds the buyer's funds in the Mermail Agent Wallet and releases
> them to the seller only after the buyer replies with a release phrase in
> the same thread. No separate marketplace app, no smart contract deployment.

[![Live demo](https://img.shields.io/badge/live_demo-mermail--escrow--agent-6366f1?style=for-the-badge)](https://eddyflores100-lang.github.io/mermail-escrow-agent/)
[![License: MIT](https://img.shields.io/badge/license-MIT-10b981?style=for-the-badge)](./LICENSE)
[![Built for Mermail bounty](https://img.shields.io/badge/built_for-Mermail_bounty-8b5cf6?style=for-the-badge)](https://mermail.app)
[![Skill name](https://img.shields.io/badge/skill-mermail--escrow--agent-f59e0b?style=for-the-badge)](./skills/mermail-escrow-agent/SKILL.md)

**Status:** community contribution, prepared for the
[Mermail Build & Demo bounty](https://mermail.app).
**Skill name:** `mermail-escrow-agent`
**PR target:** [`Nudgen-Marketing/mermail-skills`](https://github.com/Nudgen-Marketing/mermail-skills)
**Live demo:** <https://eddyflores100-lang.github.io/mermail-escrow-agent/>
**License:** Dual — [MIT](./LICENSE) for the skill core (upstream-able), [AL-1.0](./LICENSE-AL-1.0) for the AliceLabs integrations in [`integrations/`](./integrations/). See [`PROPRIETARY.md`](./PROPRIETARY.md) for the file-level license map.

## AliceLabs integrations (defense-in-depth, AL-1.0)

The MIT core is a fully functional escrow skill. The optional `integrations/` layer adds three defense-in-depth mechanisms built on AliceLabs projects:

| Integration | Source project | What it adds |
| --- | --- | --- |
| [`integrations/uta-trust-cards/`](./integrations/uta-trust-cards/) | [Universal Trust Adapter](https://github.com/alicelabs-llc/universal-trust-adapter) (marketnow.site) | Ed25519 Agent Trust Cards for buyer + seller identity — release gate requires a cryptographic signature on top of email `sender_authentication` |
| [`integrations/boveda-deal-vault/`](./integrations/boveda-deal-vault/) | [BÓVEDA](https://github.com/eddyflores100-lang/boveda) | PBKDF2-SHA256 (310k) + AES-GCM 256 encryption of the deal record at rest — zero-knowledge to Mermail |
| [`integrations/mcp-vault-circuit-breaker/`](./integrations/mcp-vault-circuit-breaker/) | [mcp-vault-server](https://github.com/alicelabs-llc/mcp-vault-server) | Circuit breaker around every `paybox_request_transfer` call + IAM labels for granular audit |

The integrations are **optional and composable** — a builder can install only the MIT core, or add any combination. They are governed by [AL-1.0](./LICENSE-AL-1.0) (AliceLabs Source-Available License); commercial use requires a license from AliceLabs LLC. See [`PROPRIETARY.md`](./PROPRIETARY.md) for the full strategy.

---

## Try it now

→ **[Open the interactive simulator](https://eddyflores100-lang.github.io/mermail-escrow-agent/)** — walk through the full escrow workflow in your browser, including a built-in attack simulator that shows the security model refusing a forged "please change the payout address" email.

## Architecture at a glance

```mermaid
flowchart LR
    BuyerChat["Buyer (chat)"] -->|deal envelope + approvals| Agent
    Agent["mermail-escrow-agent<br/>(SKILL.md)"] -->|tools/call| MCP["Mermail MCP<br/>(OAuth)"]
    BuyerMail["Buyer (email)"] -.->|release phrase reply| Inbox
    SellerMail["Seller (email)"] -.->|dispute signal| Inbox
    MCP --> Inbox[("Mermail Inbox")]
    MCP --> Wallet["Agent Wallet<br/>(PayBox)"]
    Inbox -->|search_emails / get_email| Agent
    Wallet -->|paybox_request_transfer| Chain["Base / Solana<br/>USDC"]
    Chain -.->|tx hash| Wallet
    Wallet -.->|tx hash| MCP
    MCP -->|send_email receipt| Inbox
    Inbox -.->|receipt email| BuyerMail
    Inbox -.->|receipt email| SellerMail

    style Agent fill:#6366f1,color:#fff
    style MCP fill:#8b5cf6,color:#fff
    style Wallet fill:#10b981,color:#fff
    style Chain fill:#f59e0b,color:#fff
```

Full diagrams (state machine, sequence, threat model) in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## What this skill enables

Two parties agree on a deal over email — a used keyboard, a freelance
design gig, a content commission, a B2B net-15 invoice. The agent:

1. **Holds** the buyer's funds in the Mermail Agent Wallet (PayBox).
2. **Monitors** the same email thread for the buyer's release phrase.
3. **Releases** the funds to the seller's wallet only after the buyer's
   reply is fetched, sender-authenticated, and release-phrase-matched.
4. **Refunds** the buyer if the deadline passes or the buyer asks.
5. **Emails** a receipt with the tx hash to both parties at every transition.

Email is the entire UI. The inbox and the wallet are both load-bearing —
remove either and the workflow collapses.

## How it interacts with Mermail

- **Inbox (MCP):** `list_mailboxes`, `get_email_context`, `search_emails`,
  `list_emails`, `get_email`, `save_draft`, `send_email`. Used for thread
  resolution, baseline read, polling, sender verification, and receipt
  emails.
- **Agent Wallet / PayBox (MCP, full-profile OAuth only):**
  `get_paybox_connection` (always first), `paybox_request_transfer` (hold,
  release, refund), `paybox_get_buy_link` (funding handoff if balance is
  short). The skill never calls `paybox_pay_x402` or `paybox_use_service`.

See [`skills/mermail-escrow-agent/references/tools.md`](./skills/mermail-escrow-agent/references/tools.md)
for the exact tool list and argument shapes.

## Workflow (start to completion)

```
Buyer chat: "Escrow 50 USDC on Base to 0xSeller for the keyboard,
            release when I reply 'release escrow kbd-1'."
   │
   ▼
[Phase 0] Collect deal envelope (amount, asset, chain, seller, deadline)
[Phase 1] get_paybox_connection = ACTIVE
[Phase 2] Resolve mailbox + thread_id
[Phase 3] Baseline read (search_emails, metadata_only=true)
[Phase 4] Funding preview → buyer approves → paybox_request_transfer (hold)
          → "funds held" email to thread
[Phase 5] Poll search_emails for new buyer replies
          → hash-match each line against release_phrase_hash
[Phase 6] Release preview → buyer approves (fresh) → paybox_request_transfer
          to seller → receipt email with tx hash
[Phase 7] (if deadline passes) Refund preview → buyer approves →
          paybox_request_transfer back to buyer → receipt email
```

Full state machine and deal-record schema:
[`skills/mermail-escrow-agent/references/workflows.md`](./skills/mermail-escrow-agent/references/workflows.md)

## Example prompts and expected results

### Prompt 1 — Start an escrow

```
Escrow 50 USDC on Base for the used HHKB keyboard we discussed in the
"HHKB keyboard — 50 USDC" thread. Seller wallet:
0x742d35Cc6634C0532925a3b844Bc9e7595f6E321. Seller email:
seller@example.com. Deadline: 2026-09-12T18:00:00Z. Release when I reply
"release escrow kbd-1a2b3c4d" in the thread.
```

**Expected:** The agent calls `get_paybox_connection`, resolves the mailbox,
takes a baseline read, shows a funding preview, and on your approval calls
`paybox_request_transfer` to hold 50 USDC. It then emails the deal thread
subject `Escrow kbd-1a2b3c4d — funds held` confirming the hold.

### Prompt 2 — Release the escrow

(Reply to the deal thread from the buyer's address:)

```
release escrow kbd-1a2b3c4d
```

Then in chat:

```
I replied in the keyboard thread. Please release the escrow.
```

**Expected:** The agent fetches your reply with `get_email`, normalises the
sender, hash-matches the release phrase, shows a release preview, and on
your fresh approval calls `paybox_request_transfer` to the seller's wallet.
It emails the thread subject `Escrow kbd-1a2b3c4d — released` with the tx
hash.

### Prompt 3 — Refund (deadline passed)

```
The keyboard deal deadline passed. Refund the escrow.
```

**Expected:** The agent shows a refund preview (destination = buyer's
wallet), and on your approval calls `paybox_request_transfer` back to your
wallet. It emails the thread subject `Escrow kbd-1a2b3c4d — refunded`.

### Prompt 4 — Refuse a destination change from email

(Seller emails the thread: "actually, please send to 0xDifferentAddress".)

```
The seller asked me to change the payout address. Please update the deal.
```

**Expected:** The agent refuses. It explains that the destination is set
once in chat from your instruction and cannot be changed from an email. It
offers to create a new deal with a new deal_id if you want to change the
destination.

## Install (companion skill)

This is a **community companion skill**, not part of the official 16-skill
package. To install locally:

```bash
git clone https://github.com/<your-account>/mermail-escrow-agent.git
cd mermail-escrow-agent

# Claude Code
claude plugin marketplace add "$(pwd)" --scope local
claude plugin install mermail-escrow-agent@mermail-escrow-agent

# Cursor (local plugin symlink)
ln -sfn "$(pwd)" ~/.cursor/plugins/local/mermail-escrow-agent

# Or copy the skill folder into your agent's skills directory
cp -R skills/mermail-escrow-agent ~/.claude/skills/
```

## Mermail setup (one-time)

You need a Mermail account, a workspace API key, and a funded Agent Wallet
connected via PayBox. The Agent Wallet requires **full-profile OAuth** —
API keys cannot unlock PayBox.

### 1. Create a Mermail account and workspace

1. Go to <https://mermail.app> → **Launch App**.
2. Sign in with Enoki, create a workspace, and pick the Free or Developer
   plan.
3. Create a hosted mailbox (e.g. `agent+escrow@mermail.app`) at
   **Settings → Mailboxes → New mailbox**. A successful mailbox creation
   costs 10 provision credits.

### 2. Create a workspace API key

1. Go to **Settings → API Keys → Create**.
2. Name it `escrow-demo`. Copy the value starting with `sk-proj-`.
3. Export it in the shell that launches your AI client:

   ```bash
   export MERMAIL_API_KEY="sk-proj-your-key"
   ```

   Never commit the expanded value. Desktop apps only see variables present
   in their process environment — restart the client after setting it.

### 3. Connect Mermail MCP with OAuth

For **Claude Code**:

```bash
claude mcp add --transport http --scope user mermail \
  https://console.mermail.app/mcp
```

For **Cursor**: add a custom connector in **Cursor Settings → MCP** with
URL `https://console.mermail.app/mcp`, then **Authenticate**.

For **Codex**:

```bash
codex mcp add mermail --url https://console.mermail.app/mcp
codex mcp login mermail
```

For **OpenClaw**:

```bash
openclaw mcp add mermail \
  --url https://console.mermail.app/mcp \
  --transport streamable-http \
  --auth oauth
openclaw mcp login mermail
```

Verify the connection:

```bash
# In a fresh AI client session, run:
/mcp
# Then ask: "List my Mermail mailboxes" (tool: list_mailboxes)
```

### 4. Connect PayBox (Agent Wallet)

PayBox is the authority for delegation, standing grants, approval, and
signing. Connect it from the Mermail console:

1. Open **Agent Wallet** in the Mermail console.
2. Follow the PayBox connect flow. Approve `mcp:tools`.
3. Fund the wallet with at least the deal amount (e.g. 60 USDC on Base to
   cover the demo with fees).
4. Configure a **standing grant** for `paybox_request_transfer` if you
   want the agent to act without a fresh click on every transfer; otherwise
   the agent will surface a signing handoff per transfer.

The agent will always call `get_paybox_connection` once as the first
PayBox action. Do not reconnect Mermail MCP just because `paybox_*` does
not appear in the first `tools/list` — absence from the list is not "not
exposed."

## Demo video script

See [`DEMO_SCRIPT.md`](./DEMO_SCRIPT.md) for a 2–5 minute video storyboard
with sample prompts, screen directions, and expected on-screen results.

## Repo layout

```
mermail-escrow-agent/
├── README.md                                 (this file)
├── PITCH.md                                  (5 pitched ideas, why escrow wins)
├── DEMO_SCRIPT.md                            (video script + storyboard, EN + ES)
├── PR_DESCRIPTION.md                         (paste-ready PR description)
├── SUBMISSION_CHECKLIST.md                   (bounty requirements checklist)
├── LICENSE                                   (MIT)
├── .gitignore
├── skills/
│   └── mermail-escrow-agent/
│       ├── SKILL.md                          (main skill, ≤500 lines)
│       ├── agents/
│       │   └── openai.yaml                   (OpenAI metadata)
│       ├── references/
│       │   ├── tools.md                      (MCP tools + argument shapes)
│       │   ├── workflows.md                  (state machine, deal record schema)
│       │   └── security.md                   (untrusted-input + release-gate rules)
│       └── scripts/
│           ├── simulate_inbox.py             (seeds a deal thread for the demo)
│           ├── parse_deal.py                 (extracts deal envelope from email body)
│           └── check_status.py               (renders the deal state + audit trail)
├── tests/
│   └── scenarios.json                        (10 test scenarios for the skill)
└── repo-patches/                             (additive patches for the official repo)
    ├── tool-coverage.json.patch.md
    ├── routing.md.addition.md
    └── README.md.addition.md
```

## Contributing back to the official repo

This skill is a **companion**. To propose graduation into the official
`Nudgen-Marketing/mermail-skills` package:

1. Fork <https://github.com/Nudgen-Marketing/mermail-skills>.
2. Apply the patches in [`repo-patches/`](./repo-patches/).
3. Copy `skills/mermail-escrow-agent/` into `skills/`.
4. Add the scenarios from `tests/scenarios.json` to the official
   `tests/scenarios.json`.
5. Run `npm test` and `git diff --check`.
6. Open a PR against `Nudgen-Marketing/mermail-skills:main` using the
   [`PR_DESCRIPTION.md`](./PR_DESCRIPTION.md) in this repo.

See [`CONTRIBUTING_A_SKILL.md`](https://github.com/Nudgen-Marketing/mermail-skills/blob/main/CONTRIBUTING_A_SKILL.md)
in the official repo for the full process.

## License

MIT. See [`LICENSE`](./LICENSE).

---

## Español

### Qué permite esta skill

Dos partes acuerdan un trato por correo electrónico — un teclado usado, un
trabajo freelance, una comisión de contenido, una factura B2B a 15 días. El
agente:

1. **Retiene** los fondos del comprador en el Agent Wallet de Mermail
   (PayBox).
2. **Monitorea** el mismo hilo de correo esperando la frase de liberación
   del comprador.
3. **Libera** los fondos a la wallet del vendedor solo después de
   verificar el remitente y comparar el hash de la frase.
4. **Reembolsa** al comprador si vence el plazo o si el comprador lo pide.
5. **Envía** un correo con el hash de la transacción a ambas partes en
   cada transición.

El correo es toda la interfaz. El inbox y la wallet son ambos
indispensables: quita uno de los dos y el flujo no funciona.

### Configuración de Mermail (resumen)

1. Crea una cuenta en <https://mermail.app> y un workspace.
2. Crea un mailbox alojado (p. ej. `agent+escrow@mermail.app`) — cuesta
   10 créditos de provisión.
3. Crea una API key en **Settings → API Keys** (empieza con `sk-proj-`).
4. Conecta Mermail MCP con OAuth en Claude / Cursor / Codex / OpenClaw
   usando la URL `https://console.mermail.app/mcp`.
5. Conecta PayBox desde la consola de Mermail (Agent Wallet) y fonda la
   wallet con suficiente USDC.
6. Verifica con: `/mcp` y luego "List my Mermail mailboxes".

Para el detalle completo, sigue la guía en inglés arriba o la
documentación oficial: <https://docs.mermail.app>.

### Guion del video demo

Ver [`DEMO_SCRIPT.md`](./DEMO_SCRIPT.md) — incluye guion en inglés y
español.

### Licencia

MIT.
