# Repo patch — `skills/mermail/references/routing.md`

Add the following route entry to the root router's routing table in
`skills/mermail/references/routing.md`:

```markdown
## mermail-escrow-agent

**When to route:** The user's request involves holding funds until a
confirmation condition is met, then releasing those funds to a third party.
The condition is monitored in a Mermail email thread (e.g. the buyer's
release-phrase reply). Both the inbox and the Agent Wallet are load-bearing.

**Do not route here when:**
- The user wants an immediate one-shot payment → `mermail-agent-wallet`
- The user wants to pay a selected x402 service → `mermail-x402-agent`
- The user wants to scan invoices and pay them → `mermail-invoice-pay-agent`
  (if present) or `mermail-agent-wallet`
- The user wants to schedule, do GTM outreach, or triage support →
  `mermail-scheduling-agent`, `mermail-gtm-agent`, `mermail-support-agent`

**Required inputs (collected in chat, never inferred from email):**
- `amount_decimal`, `token`, `chain`
- `seller_destination` (checksum-validated)
- `seller_email` (for Cc on receipts)
- `deadline_iso`
- optional `release_phrase` (default: `release escrow <deal-id>`)

**Required MCP profile:** full OAuth (`https://console.mermail.app/mcp`).
The `agent-inbox` profile and `MERMAIL_API_KEY` cannot run escrow because
PayBox tools are unavailable.

**First PayBox action:** always `get_paybox_connection`. See
`skills/mermail-escrow-agent/references/security.md` for the full
release-gate and refund-gate contract.
```

## Routing keyword hints (for the router's prompt)

Add these keyword hints to the router's selection rubric:

- "escrow", "hold funds until", "release when I confirm", "refund if not
  delivered", "deal thread", "buyer + seller", "P2P deal"
