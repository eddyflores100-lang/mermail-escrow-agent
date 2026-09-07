#!/usr/bin/env python3
"""
check_status.py — Print the current state of an escrow deal.

Reads the deal record (either from a local JSON file or from a Mermail
mailbox draft) and prints a one-line state summary plus the audit trail.

Used by the demo video to show that the agent's state machine is real and
recoverable, not just chat-time hallucination.

Usage:
    python check_status.py --file /tmp/deal-kbd-1a2b3c4d.json
    python check_status.py --deal-id kbd-1a2b3c4d --mailbox-id mbx_abc123

The mailbox-draft path requires MERMAIL_API_KEY and calls the Mermail REST
API to search the mailbox drafts for a deal record matching the deal_id.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

STATE_COLORS = {
    "DRAFT":      "\033[90m",   # grey
    "ARMED":      "\033[36m",   # cyan
    "HELD":       "\033[33m",   # yellow
    "RELEASED":   "\033[32m",   # green
    "REFUNDED":   "\033[35m",   # magenta
    "CANCELLED":  "\033[90m",   # grey
    "AMBIGUOUS":  "\033[31m",   # red
    "DISPUTE":    "\033[31m",   # red
    "BLOCKED":    "\033[31m",   # red
}
RESET = "\033[0m"


def _colour(state: str) -> str:
    return STATE_COLORS.get(state, "") + state + RESET


def _format_age(iso: str) -> str:
    try:
        created = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return "?"
    age = datetime.now(timezone.utc) - created
    hours = int(age.total_seconds() // 3600)
    minutes = int((age.total_seconds() % 3600) // 60)
    if hours >= 1:
        return f"{hours}h{minutes}m"
    return f"{minutes}m"


def render(deal: dict) -> str:
    deal_id = deal.get("deal_id", "?")
    state = deal.get("state", "?")
    age = _format_age(deal.get("created_iso", "")) or "?"
    amount = deal.get("amount_decimal", "?")
    token = deal.get("token", "?")
    chain = deal.get("chain", "?")
    seller = (deal.get("seller_destination") or "?")
    seller_short = seller[:6] + "..." + seller[-4:] if len(seller) > 12 else seller
    funding_tx = deal.get("funding_tx") or "—"
    release_tx = deal.get("release_tx") or "—"
    refund_tx = deal.get("refund_tx") or "—"
    audit = deal.get("audit_log", [])
    last_event = audit[-1]["event"] if audit else "—"

    lines = [
        f"┌─ deal {deal_id} ─────────────────────────────────────",
        f"│ state:        {_colour(state):<32} age: {age}",
        f"│ amount:       {amount} {token} on {chain}",
        f"│ seller:       {seller_short}",
        f"│ funding_tx:   {funding_tx}",
        f"│ release_tx:   {release_tx}",
        f"│ refund_tx:    {refund_tx}",
        f"│ last_event:   {last_event}",
        f"└─ audit ({len(audit)} entries) ──────────────────────",
    ]
    for entry in audit[-8:]:
        ts = entry.get("ts", "")[:19].replace("T", " ")
        ev = entry.get("event", "")
        lines.append(f"  {ts}  {ev}")
    if len(audit) > 8:
        lines.append(f"  ... ({len(audit) - 8} earlier entries omitted)")
    return "\n".join(lines)


def _load_from_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_from_mailbox(deal_id: str, mailbox_id: str) -> dict:
    """Fetch the deal record draft from a Mermail mailbox.

    Searches the mailbox drafts for a JSON document whose `deal_id` matches.
    Requires MERMAIL_API_KEY.
    """
    import requests  # type: ignore

    key = os.environ.get("MERMAIL_API_KEY")
    if not key or not key.startswith("sk-proj-"):
        sys.exit("MERMAIL_API_KEY must be set and start with 'sk-proj-'.")

    r = requests.get(
        f"https://api.mermail.app/v1/mailboxes/{mailbox_id}/drafts",
        headers={"x-api-key": key},
        timeout=30,
    )
    r.raise_for_status()
    drafts = r.json().get("data", []) or r.json().get("drafts", [])
    for d in drafts:
        try:
            body = json.loads(d.get("text") or d.get("body") or "{}")
        except Exception:
            continue
        if body.get("deal_id", "").lower() == deal_id.lower():
            return body
    sys.exit(f"No deal record draft found for deal_id={deal_id} in mailbox {mailbox_id}.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", help="Local JSON file containing the deal record")
    ap.add_argument("--deal-id", help="Deal id (when reading from mailbox draft)")
    ap.add_argument("--mailbox-id", help="Mailbox public_id (when reading from draft)")
    args = ap.parse_args()

    if args.file:
        deal = _load_from_file(args.file)
    elif args.deal_id and args.mailbox_id:
        deal = _load_from_mailbox(args.deal_id, args.mailbox_id)
    else:
        ap.error("Provide --file OR both --deal-id and --mailbox-id")

    print(render(deal))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
