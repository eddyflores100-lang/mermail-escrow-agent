#!/usr/bin/env python3
"""
parse_deal.py — Extract a deal envelope from an email body.

The agent uses this helper to SURFACE candidate deal terms from the inbox.
The buyer must still confirm every field in chat before the deal record is
written. This script never authorises a PayBox call.

It is deterministic and conservative: when a field cannot be parsed with
high confidence, it returns None for that field rather than guessing.

Usage:
    cat email_body.txt | python parse_deal.py
    python parse_deal.py --file email_body.txt
    python parse_deal.py --text "I'll pay 50 USDC on Base to 0xabc... for the keyboard."
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Optional


# Regexes are intentionally conservative. They prefer false negatives
# (return None) over false positives (return a wrong value).

AMOUNT_RE = re.compile(
    r"(?:pay|escrow|hold|send|transfer|release|refund)\s+"
    r"(?P<amount>\d{1,6}(?:\.\d{1,6})?)\s+"
    r"(?P<token>USDC|USDT|ETH|SOL|BTC|DAI|GHO)",
    re.IGNORECASE,
)

CHAIN_RE = re.compile(
    r"\b(?:on\s+)?(?P<chain>BASE|ETHEREUM|MAINNET|SOLANA|POLYGON|ARBITRUM|OPTIMISM)\b",
    re.IGNORECASE,
)

# EVM address (40 hex chars, optional 0x prefix, optional EIP-55 mixed case).
EVM_ADDR_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
# Solana address (base58, 32 bytes -> 43-44 chars).
SOL_ADDR_RE = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{43,44}\b")

DEADLINE_RE = re.compile(
    r"(?:deadline|by|expires?|auto[- ]?refund(?:\s+after)?)"
    r"[:\s]+"
    r"(?P<iso>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)",
    re.IGNORECASE,
)

DEAL_ID_RE = re.compile(
    r"(?:deal[- ]?id[:\s]+)?(?P<id>[a-z]{3,6}-[a-f0-9]{6,12})",
    re.IGNORECASE,
)


def _pick_address(text: str) -> Optional[str]:
    """Return the first plausible wallet address in the text."""
    m = EVM_ADDR_RE.search(text)
    if m:
        return m.group(0)
    # Solana addresses are ambiguous (any 43-44 char base58 string); only
    # accept them if the surrounding text mentions "sol" or "solana".
    if re.search(r"\bsol(?:ana)?\b", text, re.IGNORECASE):
        m = SOL_ADDR_RE.search(text)
        if m:
            return m.group(0)
    return None


def parse_deal(text: str) -> dict:
    """Parse a deal envelope from free-form email body text.

    Returns a dict with keys: amount_decimal, token, chain, destination,
    deadline_iso, deal_id. Any field that cannot be parsed with high
    confidence is None.
    """
    amount_match = AMOUNT_RE.search(text)
    chain_match = CHAIN_RE.search(text)
    address = _pick_address(text)
    deadline_match = DEADLINE_RE.search(text)
    deal_id_match = DEAL_ID_RE.search(text)

    return {
        "amount_decimal": amount_match.group("amount") if amount_match else None,
        "token": amount_match.group("token").upper() if amount_match else None,
        "chain": chain_match.group("chain").upper() if chain_match else None,
        "destination": address,
        "deadline_iso": deadline_match.group("iso") if deadline_match else None,
        "deal_id": deal_id_match.group("id").lower() if deal_id_match else None,
        # Always None — the buyer's chat instruction is the only source for
        # this field, never an email.
        "release_phrase": None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", help="Path to a text file containing the email body")
    ap.add_argument("--text", help="Email body as a command-line argument")
    ap.add_argument("--format", choices=["json", "human"], default="json")
    args = ap.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        sys.exit("No input. Provide --file, --text, or pipe via stdin.")

    deal = parse_deal(text)

    if args.format == "json":
        print(json.dumps(deal, indent=2))
    else:
        print("Parsed deal envelope (SURFACE ONLY — buyer must confirm in chat):")
        for k, v in deal.items():
            print(f"  {k:>16}: {v if v is not None else '<unparsed>'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
