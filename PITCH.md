# Pitch: 5 Hybrid Mermail Skills (Inbox + Wallet)

This document pitches five creative skills that combine Mermail's **inbox** and
**Agent Wallet** primitives. Each idea was screened against the 16 skills already
shipped in `Nudgen-Marketing/mermail-skills` to avoid duplication and to maximise
the **Innovation** and **Reusability** bounty criteria.

The winner (Idea #2) is shipped in this repository as `mermail-escrow-agent`.

---

## Idea #1 — `mermail-subscription-cancel-agent`

**What it does.** Watches the agent inbox for "your subscription renews in N days"
emails, drafts a cancellation reply for the user to approve, then chases a
pro-rated refund if the vendor's policy allows it. When the vendor requests a
wallet address for the refund, the agent supplies the Agent Wallet address and
reconciles the inbound refund against the wallet's transaction history.

**Why it's interesting.** Subscription fatigue is a universal pain. No existing
Mermail skill cancels subscriptions or chases refunds. The wallet is used as a
*receiver*, not a sender — a rare angle that showcases the wallet's
bidirectional nature.

**Why not ship it.** Refund policy is highly vendor-specific, the cancellation
step often requires browser interaction (the Mermail docs explicitly warn that
agents must stop before clicking third-party links), and the refund reconciliation
depends on chain-specific finality. Hard to demo cleanly in 2–5 minutes.

---

## Idea #2 — `mermail-escrow-agent`  **← SHIPPED**

**What it does.** Two parties agree on a deal entirely over email ("I'll pay
50 USDC for the used keyboard, you ship it, I'll confirm when it arrives").
The agent holds the buyer's funds in the Agent Wallet, monitors the same email
thread for both parties' confirmation messages, and releases payment to the
seller's wallet only when the buyer explicitly replies with an escrow release
phrase. If the deal falls through, the agent refunds the buyer.

**Why it's interesting.**

- **No existing Mermail skill does escrow.** The 16 official skills cover
  scheduling, GTM outreach, support, x402 micropayments, and wallet
  inspect/transfer/swap — but none of them coordinate *multi-party
  confirmation* over email before releasing funds.
- **Email is the entire UI.** No separate marketplace app, no smart contract
  deployment, no Discord bot. The buyer, seller, and agent all live in one
  thread.
- **Inbox + Wallet are both load-bearing.** Remove the inbox and there's no
  coordination channel. Remove the wallet and there's no value transfer.
  Hybrid by construction.
- **Reproducible.** Any builder can fork the workflow for freelance work,
  used-gear sales, content commissions, or B2B net-15 invoicing.
- **Demo-friendly.** Four emails + one on-chain transfer tells the whole story
  in under three minutes.

**Why ship it.** Hits all four judging criteria cleanly: complete SKILL.md,
obviously working demo, easy to reproduce, and a genuinely novel agent
capability.

---

## Idea #3 — `mermail-invoice-pay-agent`

**What it does.** Scans the inbox for unpaid invoices (PDF + HTML), extracts
vendor / amount / due date / payment address, builds a daily digest email, and
pays the invoices the user approves by replying ("pay INV-001", "pay all under
$100"). After each pay, replies to the vendor's email with the tx hash.

**Why it's interesting.** Real B2B pain point. Inbox + wallet hybrid with a
clear digest UX.

**Why not ship it.** Too close to the existing `mermail-research-agent` pattern
(owner-verified orders, same-thread follow-ups) and to `mermail-x402-agent`
(pay a selected resource). Innovation score would be moderate, not high.

---

## Idea #4 — `mermail-tip-bot-agent`

**What it does.** Anyone emails the agent's Mermail address with
`tip @alice 5 USDC for the great thread`. The agent parses the command, looks
up `@alice`'s wallet in a curated creator directory, sends 5 USDC via
`paybox_request_transfer`, and emails a receipt to both parties.

**Why it's interesting.** Turns a Mermail inbox into a programmable tip surface
for the creator economy.

**Why not ship it.** Requires a curated creator directory to be useful, which
is out of scope for a single skill. Without the directory, every tip stalls on
"what is @alice's wallet address?" — not demo-friendly.

---

## Idea #5 — `mermail-carbon-offset-agent`

**What it does.** Email the agent your flight itinerary. The agent extracts
miles, calculates CO₂, discovers a vetted offset provider via
`paybox_discover_services` + `paybox_pay_x402`, pays the offset, and emails
you a receipt + certificate.

**Why it's interesting.** End-to-end climate action in one email. Strong
narrative for the demo video.

**Why not ship it.** Carbon offset providers are inconsistent across x402
catalogs today, so the demo would be brittle. The CO₂ calculation also
introduces a non-Mermail dependency that distracts from the skill's core
inbox+wallet story.

---

## Decision matrix

| Idea | Innovation | Reproducible | Demo ≤ 5 min | Hybrid (inbox+wallet) | Verdict |
| --- | --- | --- | --- | --- | --- |
| #1 Subscription cancel/refund | High | Medium | Hard | Yes (wallet as receiver) | Skip — brittle demo |
| **#2 Email escrow** | **High** | **High** | **Easy** | **Yes (both load-bearing)** | **Ship** |
| #3 Invoice digest + pay | Medium | High | Easy | Yes | Skip — too close to existing |
| #4 Tip bot | Medium | Low (needs directory) | Medium | Yes | Skip — directory out of scope |
| #5 Carbon offset | High | Low (catalog brittle) | Medium | Yes | Skip — too many non-Mermail deps |

---

## The shipped skill

`mermail-escrow-agent` — **peer-to-peer email escrow using Mermail's inbox and
Agent Wallet**. See [`skills/mermail-escrow-agent/SKILL.md`](./skills/mermail-escrow-agent/SKILL.md)
for the full skill contract, and [`DEMO_SCRIPT.md`](./DEMO_SCRIPT.md) for the
2–5 minute video script.
