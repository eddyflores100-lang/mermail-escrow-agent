#!/usr/bin/env python3
"""
simulate_inbox.py — Seed a Mermail mailbox with a sample escrow deal thread.

Used by the demo video to start from a realistic state: the buyer and seller
have already exchanged two emails agreeing on a deal, and the agent's job is
to hold funds and release on the buyer's reply.

Usage:
    export MERMAIL_API_KEY="sk-proj-..."
    python simulate_inbox.py \\
        --mailbox-agent agent+escrow@mermail.app \\
        --buyer buyer@example.com \\
        --seller seller@example.com \\
        --subject "Used HHKB keyboard — 50 USDC" \\
        --deal-id kbd-1a2b3c4d

The script sends two emails via the Mermail REST API:
  1. Buyer → Agent: "I'd like to escrow 50 USDC for the keyboard."
  2. Seller → Agent: "Sounds good. My wallet is 0xSellerAddress."

It does NOT send the release phrase — that is typed by the buyer during the
live demo to prove the release gate works.

Requires: requests (pip install requests)
"""
from __future__ import annotations

import argparse
import os
import sys
import json
from datetime import datetime, timezone

import requests  # type: ignore

MERMAIL_API_BASE = "https://api.mermail.app/v1"


def _auth_headers() -> dict[str, str]:
    key = os.environ.get("MERMAIL_API_KEY")
    if not key or not key.startswith("sk-proj-"):
        sys.exit(
            "MERMAIL_API_KEY must be set and start with 'sk-proj-'. "
            "Create one in Mermail Settings → API Keys."
        )
    return {"x-api-key": key, "Content-Type": "application/json"}


def _find_mailbox_public_id(agent_email: str) -> str:
    """Look up the mailbox public_id for the agent's email address."""
    r = requests.get(
        f"{MERMAIL_API_BASE}/mailboxes",
        headers=_auth_headers(),
        timeout=30,
    )
    r.raise_for_status()
    mailboxes = r.json().get("data", []) or r.json().get("mailboxes", [])
    for mb in mailboxes:
        if mb.get("email", "").lower() == agent_email.lower():
            return mb["public_id"]
    sys.exit(f"No mailbox found for {agent_email}. Create it in the Mermail console first.")


def _send_email(
    mailbox_public_id: str,
    *,
    from_addr: str,
    to_addr: str,
    subject: str,
    body: str,
    in_reply_to: str | None = None,
) -> str:
    """Send an email through the Mermail REST API. Returns the new email id."""
    payload: dict[str, object] = {
        "mailboxId": mailbox_public_id,
        "from": {"address": from_addr},
        "to": [{"address": to_addr}],
        "subject": subject,
        "text": body,
    }
    if in_reply_to:
        payload["inReplyTo"] = in_reply_to

    r = requests.post(
        f"{MERMAIL_API_BASE}/emails/send",
        headers=_auth_headers(),
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("id") or data.get("data", {}).get("id") or "<sent>"


def main() -> int:
    # Force UTF-8 on stdout for Windows cp1252 compatibility.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mailbox-agent", required=True, help="Agent's Mermail email address")
    ap.add_argument("--buyer", required=True, help="Buyer's email address")
    ap.add_argument("--seller", required=True, help="Seller's email address")
    ap.add_argument("--subject", required=True, help="Email subject for the deal thread")
    ap.add_argument("--deal-id", required=True, help="Short deal id, e.g. kbd-1a2b3c4d")
    ap.add_argument("--amount", default="50.00", help="Deal amount (human, default 50.00)")
    ap.add_argument("--token", default="USDC", help="Deal token (default USDC)")
    ap.add_argument("--chain", default="BASE", help="Deal chain (default BASE)")
    ap.add_argument("--seller-wallet", default="0xSellerAddressFromDealEnvelope",
                    help="Seller's wallet address (placeholder by default)")
    args = ap.parse_args()

    mailbox_id = _find_mailbox_public_id(args.mailbox_agent)
    print(f"[ok] mailbox {args.mailbox_agent} -> public_id {mailbox_id}")

    # Email 1: Buyer → Agent, asking to escrow.
    body1 = (
        f"Hi,\n\n"
        f"I'd like to escrow {args.amount} {args.token} on {args.chain} for the "
        f"used HHKB keyboard we discussed. Deal id: {args.deal_id}.\n\n"
        f"Please hold the funds and release to the seller when I confirm receipt.\n\n"
        f"Thanks,\nBuyer\n"
    )
    email1_id = _send_email(
        mailbox_id,
        from_addr=args.buyer,
        to_addr=args.mailbox_agent,
        subject=args.subject,
        body=body1,
    )
    print(f"[ok] email 1 sent (buyer → agent): id={email1_id}")

    # Email 2: Seller → Agent, confirming the deal and providing wallet.
    body2 = (
        f"Hi,\n\n"
        f"Confirmed — I'll ship the keyboard once funds are held. My payout wallet "
        f"is {args.seller_wallet} on {args.chain}.\n\n"
        f"Deal id: {args.deal_id}\n\n"
        f"Thanks,\nSeller\n"
    )
    email2_id = _send_email(
        mailbox_id,
        from_addr=args.seller,
        to_addr=args.mailbox_agent,
        subject=f"Re: {args.subject}",
        body=body2,
        in_reply_to=email1_id,
    )
    print(f"[ok] email 2 sent (seller → agent): id={email2_id}")

    print(
        f"\n[done] Inbox seeded. The agent now has a deal thread to monitor.\n"
        f"        deal_id: {args.deal_id}\n"
        f"        thread seed subject: {args.subject}\n"
        f"        next step: tell the agent in chat to escrow {args.amount} {args.token} "
        f"on {args.chain} to {args.seller_wallet}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
