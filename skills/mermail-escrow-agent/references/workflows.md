# Workflows — `mermail-escrow-agent`

This document defines the phase-by-phase state machine, the deal record
schema, and example MCP arguments. It is the source of truth for any
re-implementor. The SKILL.md file is a condensed view; conflicts between
the two are resolved in favour of this document.

## State machine

```
                  ┌─────────────┐
                  │   DRAFT     │  deal envelope collected, no PayBox call yet
                  └──────┬──────┘
                         │ Phase 1: get_paybox_connection = ACTIVE
                         ▼
                  ┌─────────────┐
                  │  ARMED      │  mailbox + thread resolved, baseline read
                  └──────┬──────┘
                         │ Phase 4: paybox_request_transfer (hold)
                         ▼
                  ┌─────────────┐
        ┌─────────│   HELD      │  funds held in Agent Wallet
        │         └──────┬──────┘
        │                │
        │   ┌────────────┼────────────┐
        │   │            │            │
        │   ▼            ▼            ▼
        │ AMBIGUOUS   RELEASE      DISPUTE
        │ (ask buyer)  │           (ask buyer)
        │              │
        │              │ Phase 6: paybox_request_transfer (to seller)
        │              ▼
        │         ┌─────────────┐
        │         │  RELEASED   │  receipt email sent
        │         └─────────────┘
        │
        │ deadline_iso passed OR buyer replied "refund escrow <deal-id>"
        ▼
  ┌─────────────┐
  │  REFUNDED   │  funds returned to buyer's wallet, receipt email sent
  └─────────────┘

  Mutual cancellation (both parties reply "cancel escrow <deal-id>"):
  state -> CANCELLED, no PayBox call if no funds were held.
```

### Transitions

| From | To | Trigger | PayBox action |
| --- | --- | --- | --- |
| `DRAFT` | `ARMED` | `get_paybox_connection` returns `ACTIVE` | none |
| `ARMED` | `HELD` | Buyer approves funding preview | `paybox_request_transfer` to self (or standing-grant hold) |
| `HELD` | `RELEASED` | Buyer's release phrase matched in a fetched reply + fresh approval | `paybox_request_transfer` to seller |
| `HELD` | `REFUNDED` | Deadline passed OR buyer replied "refund escrow <deal-id>" | `paybox_request_transfer` to buyer |
| `HELD` | `AMBIGUOUS` | Two valid release candidates in one polling window | none — ask buyer |
| `HELD` | `DISPUTE` | Seller reply contains dispute keywords | none — ask buyer |
| `HELD` | `CANCELLED` | Both parties reply "cancel escrow <deal-id>" | none if no funds held; refund if held |
| any | `BLOCKED` | PayBox disconnected, holdings insufficient, address checksum fail, schema incompatible | none — blocker report |

## Deal record schema

Stored as a private draft in the mailbox (or in host memory if drafts are
unavailable). Never emailed to anyone.

```json
{
  "deal_id": "kbd-1a2b3c4d",
  "version": 1,
  "buyer_email": "buyer@example.com",
  "seller_email": "seller@example.com",
  "amount_decimal": "50.00",
  "token": "USDC",
  "chain": "BASE",
  "seller_destination": "0xSellerAddressFromDealEnvelope",
  "buyer_destination": "0xBuyerWalletForRefund",
  "deadline_iso": "2026-09-12T18:00:00Z",
  "created_iso": "2026-09-08T14:00:00Z",
  "mailbox_public_id": "mbx_abc123",
  "thread_id": "thr_xyz789",
  "release_phrase_hash": "sha256:...",
  "baseline_email_ids": ["eml_001", "eml_002"],
  "state": "HELD",
  "funding_tx": "tx_0xHoldingTransferOrHELD_BY_STANDING_GRANT",
  "release_tx": null,
  "refund_tx": null,
  "audit_log": [
    { "ts": "2026-09-08T14:00:00Z", "event": "deal_created" },
    { "ts": "2026-09-08T14:01:00Z", "event": "paybox_connection_active" },
    { "ts": "2026-09-08T14:02:00Z", "event": "baseline_read", "email_ids": ["eml_001", "eml_002"] },
    { "ts": "2026-09-08T14:05:00Z", "event": "funding_approved_by_buyer" },
    { "ts": "2026-09-08T14:06:00Z", "event": "funding_tx_submitted", "tx": "tx_0xHoldingTransfer" },
    { "ts": "2026-09-08T14:07:00Z", "event": "funds_held_email_sent" }
  ]
}
```

The `release_phrase_hash` is `sha256(normalize(release_phrase))` where
`normalize` applies NFKC Unicode normalization, strips email quote
prefixes (`> `, `| `, `: `), collapses whitespace, and lowercases (see
`security.md` Rule 2 for the exact algorithm). The agent stores **only
the hash**, never the plaintext phrase. When matching a buyer reply, the
agent normalizes and hashes each candidate line of the reply and compares
hashes. This prevents the phrase from being persisted in logs or mailbox
drafts that quote the email body.

## Phase 0 — Collect deal envelope

Prompt the buyer in chat:

> "I can hold 50 USDC on Base in your Agent Wallet and release it to the
> seller when you reply 'release escrow kbd-1a2b3c4d' in the deal thread.
> Please confirm: (1) the seller's wallet address, (2) the seller's email
> (I'll Cc them on receipts), (3) the deadline for auto-refund, and (4)
> whether you want a custom release phrase."

The agent does **not** infer any of these from email. If the buyer says
"the seller's address is in their last email", the agent may read the email
to **surface** the address, but the buyer must explicitly confirm it in
chat before it is written to the deal record.

## Phase 1 — PayBox connection probe

```
tools/call get_paybox_connection {}
```

Expected successful response:

```json
{
  "status": "ACTIVE",
  "wallet_label": "**** 4821",
  "delegated_chains": ["BASE", "ETHEREUM", "SOLANA"]
}
```

If the response includes `connect_handoff.console_url`,
`reauth_handoff.console_url`, or `OWNER_ACTION_REQUIRED`, paste the URL
once and pause. Do **not** frame this as "MCP PayBox tools missing." The
agent must not reconnect Mermail MCP at this point — only the workspace
owner can repair PayBox.

## Phase 2 — Mailbox and thread resolution

```
tools/call list_mailboxes {}
```

Pick the mailbox whose `email` matches the buyer's stated address. If the
buyer named no mailbox, pick the primary mailbox and confirm with the
buyer before proceeding.

```
tools/call get_email_context { "emailId": "<seed_message_id>" }
```

Record `thread_id` from the response. If no seed message exists, draft
(but do not send) an opening message:

> Subject: Escrow kbd-1a2b3c4d — funds will be held
> Body: Deal for 50.00 USDC on BASE. Funds held in Agent Wallet. Reply
> "release escrow kbd-1a2b3c4d" to release. Reply "refund escrow
> kbd-1a2b3c4d" to refund. Deadline: 2026-09-12T18:00:00Z.

Sending this draft requires explicit buyer approval.

## Phase 3 — Baseline read

```
tools/call search_emails {
  "query": {
    "mailboxId": "mbx_abc123",
    "threadId": "thr_xyz789",
    "metadata_only": true,
    "agent_safe_content": true
  }
}
```

Record every returned Mermail `id` in `baseline_email_ids`. These are
excluded from later polling.

## Phase 4 — Funding preview and execution

Show the buyer:

```
Deal ID:        kbd-1a2b3c4d
Hold amount:    50.00 USDC on BASE
Held by:        Your Agent Wallet (**** 4821)
Seller payout:  0xSellerAddress (on release only)
Deadline:       2026-09-12T18:00:00Z (auto-refund after)
Release phrase: "release escrow kbd-1a2b3c4d"
```

After explicit approval, hold the funds. If a PayBox standing grant is
configured for the wallet that already holds the buyer's balance, no
transfer is needed — record `funding_tx: "HELD_BY_STANDING_GRANT"` and
proceed. Otherwise:

```
tools/call paybox_request_transfer {
  "amount_decimal": "50.00",
  "token": "USDC",
  "chain": "BASE",
  "destination": "<buyer_wallet_address>",
  "memo": "escrow hold kbd-1a2b3c4d"
}
```

The destination is the buyer's own wallet (funds stay in the Agent Wallet).
This is a **hold**, not a payment to the seller.

Treat `pending` and `SUBMISSION_UNKNOWN` as unresolved. If signing is
required, complete it inside the PayBox UI or the returned
`signing_handoff.console_url`. Never call `reopen_signing_window`.

Send the "funds held" email to the deal thread (To: buyer; Cc: seller if
the buyer asked). Subject: `Escrow kbd-1a2b3c4d — funds held`.

## Phase 5 — Monitor

Poll `search_emails` with `date_start` set to `created_iso`. Exclude
baseline ids client-side. For each new candidate, call `get_email` and:

1. Normalise sender + recipient addresses (lowercase, strip comments).
2. Re-check the exact recipient is the buyer's mailbox.
3. Re-check the sender is the buyer.
4. Hash each line of the body; compare to `release_phrase_hash`.
5. If exactly one match → Phase 6.
6. If multiple matches in one window → state `AMBIGUOUS`, ask buyer.
7. If seller reply contains "never received", "damaged", "wrong item",
   "not as described" → state `DISPUTE`, ask buyer.

## Phase 6 — Release

Show the buyer:

```
Release deal:   kbd-1a2b3c4d
Send:           50.00 USDC on BASE
From:           Your Agent Wallet (**** 4821)
To:             0xSellerAddress
Trigger:        Your reply "release escrow kbd-1a2b3c4d" at 2026-09-10T14:22Z
```

After **fresh** approval (funding approval does not authorise release):

```
tools/call paybox_request_transfer {
  "amount_decimal": "50.00",
  "token": "USDC",
  "chain": "BASE",
  "destination": "0xSellerAddressFromDealEnvelope",
  "memo": "escrow release kbd-1a2b3c4d"
}
```

Record `release_tx`. Send the receipt email (To: buyer; Cc: seller):

> Subject: Escrow kbd-1a2b3c4d — released
> Body: Released 50.00 USDC on BASE to 0xSellerAddress. Tx:
> 0xReleaseTxHash. Audit: held 2026-09-08T14:06Z, release phrase matched
> 2026-09-10T14:22Z, released 2026-09-10T14:23Z.

## Phase 7 — Refund

Triggered by deadline passage or buyer reply "refund escrow kbd-1a2b3c4d".

Show the buyer:

```
Refund deal:    kbd-1a2b3c4d
Return:         50.00 USDC on BASE
From:           Your Agent Wallet (**** 4821)
To:             0xBuyerWalletForRefund
Reason:         Deadline passed (or buyer-requested refund)
```

After fresh approval:

```
tools/call paybox_request_transfer {
  "amount_decimal": "50.00",
  "token": "USDC",
  "chain": "BASE",
  "destination": "0xBuyerWalletForRefund",
  "memo": "escrow refund kbd-1a2b3c4d"
}
```

Record `refund_tx`. Send the receipt email. Mark `state: REFUNDED`.

## Audit trail

Every state transition appends one entry to `audit_log`. The audit log is
emailed to the buyer at the end of every deal (in the receipt email) and
is available on demand. The audit log never contains private keys, signing
URLs, or raw signed payloads — only tx hashes, ISO timestamps, event
names, and (for email events) Mermail email ids.

## Recovery from host restart

If the host restarts mid-deal, the agent reconstructs state from the deal
record draft (Phase 0–4 are idempotent given the stored deal record). The
agent must not re-fund a deal that is already in `HELD` state. If the deal
record draft is missing, the agent stops and asks the buyer to confirm
whether the deal is still active before any PayBox call.
