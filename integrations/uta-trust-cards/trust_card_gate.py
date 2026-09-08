#!/usr/bin/env python3
"""
SPDX-License-Identifier: AL-1.0
Copyright (c) 2026 AliceLabs LLC. All rights reserved.

trust_card_gate.py — ATC/1.0 verification helper for mermail-escrow-agent.

Wraps the `agent-trust-card` NPM package (ATC/1.0 SDK) to issue, verify,
and sign-with Agent Trust Cards from the Universal Trust Adapter (UTA).

This integration is OPTIONAL. The MIT core of mermail-escrow-agent works
without it. When installed and configured, it adds a cryptographic
identity layer on top of email sender_authentication.

Commercial use of this file requires a license from AliceLabs LLC.
Contact: legal@alicelabs.site
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


# The agent-trust-card SDK is an NPM package. We shell out to it.
# If the MCP server (marketnow-mcp) is connected instead, the agent can
# call its tools directly — this helper is for the non-MCP path.
ATC_CLI = "npx"
ATC_CLI_ARGS = ["--yes", "agent-trust-card"]


@dataclass
class ATCVerification:
    """Result of verifying an Agent Trust Card."""
    valid: bool
    controls_passed: list[str]
    controls_failed: list[str]
    subject: Optional[str]      # the agent_id from the card
    public_key_pem: Optional[str]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "controls_passed": self.controls_passed,
            "controls_failed": self.controls_failed,
            "subject": self.subject,
            "public_key_pem": self.public_key_pem,
            "error": self.error,
        }


def issue_trust_card(agent_id: str, public_key_pem: str) -> dict:
    """Issue an ATC/1.0 card for the given agent_id and public key.

    Requires the UTA CA to be reachable (or a local CA for testing).
    Returns the card as a dict.
    """
    # In production this calls the UTA CA endpoint. For development,
    # it can self-sign using the agent-trust-card CLI.
    result = subprocess.run(
        [ATC_CLI, *ATC_CLI_ARGS, "issue",
         "--agent-id", agent_id,
         "--public-key", public_key_pem,
         "--format", "json"],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ATC issue failed: {result.stderr}")
    return json.loads(result.stdout)


def verify_trust_card(atc_json: dict | str) -> ATCVerification:
    """Verify an ATC/1.0 card. Returns the verification result.

    Runs the 8 verification controls defined in the ATC/1.0 spec:
      1. Signature valid
      2. CA trusted
      3. Card not expired
      4. Card not revoked
      5. Subject matches expected agent_id (if provided)
      6. Public key is Ed25519
      7. Canonical form (RFC 8785 JCS)
      8. Schema valid
    """
    if isinstance(atc_json, str):
        atc_json = json.loads(atc_json)

    result = subprocess.run(
        [ATC_CLI, *ATC_CLI_ARGS, "verify", "--format", "json", "-"],
        input=json.dumps(atc_json), capture_output=True, text=True,
        timeout=30, check=False,
    )
    if result.returncode != 0:
        return ATCVerification(
            valid=False, controls_passed=[], controls_failed=["cli-error"],
            subject=None, public_key_pem=None,
            error=result.stderr.strip() or "unknown CLI error",
        )
    data = json.loads(result.stdout)
    return ATCVerification(
        valid=data.get("valid", False),
        controls_passed=data.get("controls_passed", []),
        controls_failed=data.get("controls_failed", []),
        subject=data.get("subject"),
        public_key_pem=data.get("public_key_pem"),
        error=data.get("error"),
    )


def verify_signature(message: str, signature_b64: str, public_key_pem: str) -> bool:
    """Verify an Ed25519 signature of `message` against `public_key_pem`.

    Returns True if the signature is valid.
    """
    result = subprocess.run(
        [ATC_CLI, *ATC_CLI_ARGS, "verify-sig",
         "--message", message,
         "--signature", signature_b64,
         "--public-key", public_key_pem],
        capture_output=True, text=True, timeout=15, check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def check_release_gate(
    *,
    buyer_reply_body: str,
    release_phrase_hash: str,        # sha256 hex, stored in deal record
    buyer_atc_public_key_pem: str,
    buyer_atc_signature_b64: str,
    sender_authentication_status: str,
) -> dict:
    """The full release-gate check with ATC.

    This is called by the agent AFTER the MIT core's sender_auth check
    passes, but BEFORE the release preview is shown.

    Returns a dict with:
      - passed: bool
      - email_auth: bool
      - atc_signature_valid: bool
      - phrase_hash_match: bool
      - reason: str (if not passed)
    """
    import hashlib

    # 1. Email auth (the MIT core already checked this, but re-verify)
    email_auth = sender_authentication_status == "pass"

    # 2. Release phrase hash match (the MIT core also does this)
    #    The integration re-hashes each line and compares.
    phrase_match = False
    for line in buyer_reply_body.splitlines():
        line = line.strip()
        if not line:
            continue
        h = hashlib.sha256(line.encode("utf-8")).hexdigest()
        if h == release_phrase_hash:
            phrase_match = True
            matched_line = line
            break

    if not phrase_match:
        return {
            "passed": False,
            "email_auth": email_auth,
            "atc_signature_valid": False,
            "phrase_hash_match": False,
            "reason": "release phrase not found in reply body",
        }

    # 3. ATC signature verification
    atc_valid = verify_signature(
        message=matched_line,
        signature_b64=buyer_atc_signature_b64,
        public_key_pem=buyer_atc_public_key_pem,
    )

    if not email_auth:
        return {
            "passed": False,
            "email_auth": False,
            "atc_signature_valid": atc_valid,
            "phrase_hash_match": True,
            "reason": "sender_authentication.status !== pass",
        }

    if not atc_valid:
        return {
            "passed": False,
            "email_auth": True,
            "atc_signature_valid": False,
            "phrase_hash_match": True,
            "reason": "ATC signature invalid — buyer private key not used",
        }

    return {
        "passed": True,
        "email_auth": True,
        "atc_signature_valid": True,
        "phrase_hash_match": True,
        "reason": "all three gates passed",
    }


def main() -> int:
    """CLI entry point for testing."""
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_verify = sub.add_parser("verify", help="Verify an ATC card")
    p_verify.add_argument("--card", required=True, help="Path to ATC JSON file")

    p_gate = sub.add_parser("gate", help="Run the release-gate check")
    p_gate.add_argument("--reply", required=True, help="Path to buyer reply text file")
    p_gate.add_argument("--phrase-hash", required=True, help="sha256 hex of release phrase")
    p_gate.add_argument("--buyer-key", required=True, help="Path to buyer public key PEM")
    p_gate.add_argument("--signature", required=True, help="Base64 signature of the release phrase")
    p_gate.add_argument("--sender-auth", default="pass",
                        choices=["pass", "fail", "unknown", "missing"])

    args = ap.parse_args()

    if args.cmd == "verify":
        with open(args.card) as f:
            card = json.load(f)
        result = verify_trust_card(card)
        print(json.dumps(result.to_dict(), indent=2))
        return 0 if result.valid else 1

    if args.cmd == "gate":
        with open(args.reply) as f:
            reply_body = f.read()
        with open(args.buyer_key) as f:
            buyer_key = f.read()
        result = check_release_gate(
            buyer_reply_body=reply_body,
            release_phrase_hash=args.phrase_hash,
            buyer_atc_public_key_pem=buyer_key,
            buyer_atc_signature_b64=args.signature,
            sender_authentication_status=args.sender_auth,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
