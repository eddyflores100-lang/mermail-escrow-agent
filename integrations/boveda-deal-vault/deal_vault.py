#!/usr/bin/env python3
"""
SPDX-License-Identifier: AL-1.0
Copyright (c) 2026 AliceLabs LLC. All rights reserved.

deal_vault.py — PBKDF2-SHA256 (310k) + AES-GCM 256 encryption for the
mermail-escrow-agent deal record.

Inspired by BÓVEDA (https://github.com/eddyflores100-lang/boveda), which
uses the same algorithm in the browser with WebCrypto.

This integration is OPTIONAL. The MIT core works without it.

Commercial use of this file requires a license from AliceLabs LLC.
Contact: legal@alicelabs.site
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Optional

# AES-GCM requires the `cryptography` package (or pycryptodome).
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    AESGCM = None  # type: ignore


# OWASP 2023 recommendation for PBKDF2-SHA256.
KDF_ITERATIONS = 310_000
SALT_BYTES = 16
IV_BYTES = 12
KEY_BYTES = 32  # AES-256


class DealVaultError(Exception):
    """Base error for deal-vault operations."""


class DealVaultDecryptError(DealVaultError):
    """Raised when decryption fails (wrong passphrase, tampered ciphertext, etc.)."""


def derive_key(passphrase: str, salt: bytes, iterations: int = KDF_ITERATIONS) -> bytes:
    """Derive a 32-byte AES-256 key from a passphrase using PBKDF2-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode("utf-8"), salt, iterations, dklen=KEY_BYTES
    )


def encrypt_deal_record(
    deal_record: dict,
    passphrase: str,
    iterations: int = KDF_ITERATIONS,
) -> str:
    """Encrypt a deal record dict with PBKDF2 + AES-GCM.

    Returns a base64-encoded payload:
        salt(16) || iv(12) || ciphertext || tag(16)

    The tag is appended by AES-GCM (last 16 bytes of ciphertext).
    """
    if AESGCM is None:
        raise DealVaultError(
            "cryptography package not installed. Run: pip install cryptography"
        )

    salt = os.urandom(SALT_BYTES)
    iv = os.urandom(IV_BYTES)
    key = derive_key(passphrase, salt, iterations)

    plaintext = json.dumps(deal_record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, associated_data=None)

    payload = salt + iv + ciphertext
    return base64.b64encode(payload).decode("ascii")


def decrypt_deal_record(
    encrypted_payload: str,
    passphrase: str,
    iterations: int = KDF_ITERATIONS,
) -> dict:
    """Decrypt a payload produced by `encrypt_deal_record`.

    Raises DealVaultDecryptError on any failure (wrong passphrase,
    tampered ciphertext, corrupted payload).
    """
    if AESGCM is None:
        raise DealVaultError(
            "cryptography package not installed. Run: pip install cryptography"
        )

    try:
        payload = base64.b64decode(encrypted_payload, validate=True)
    except Exception as e:
        raise DealVaultDecryptError(f"invalid base64 payload: {e}") from e

    if len(payload) < SALT_BYTES + IV_BYTES + 16:
        raise DealVaultDecryptError("payload too short")

    salt = payload[:SALT_BYTES]
    iv = payload[SALT_BYTES:SALT_BYTES + IV_BYTES]
    ciphertext = payload[SALT_BYTES + IV_BYTES:]

    key = derive_key(passphrase, salt, iterations)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(iv, ciphertext, associated_data=None)
    except Exception as e:
        # AES-GCM raises InvalidTag on wrong passphrase OR tampered ciphertext.
        # We deliberately do not distinguish — that would leak information.
        raise DealVaultDecryptError(
            "decryption failed (wrong passphrase or tampered ciphertext)"
        ) from e

    try:
        return json.loads(plaintext.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise DealVaultDecryptError(f"decrypted payload is not valid JSON: {e}") from e


def main() -> int:
    """CLI for testing."""
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_enc = sub.add_parser("encrypt", help="Encrypt a deal record JSON file")
    p_enc.add_argument("--input", required=True, help="Path to deal record JSON")
    p_enc.add_argument("--passphrase", required=True, help="Encryption passphrase")

    p_dec = sub.add_parser("decrypt", help="Decrypt an encrypted payload")
    p_dec.add_argument("--input", required=True, help="Path to base64 payload file")
    p_dec.add_argument("--passphrase", required=True, help="Decryption passphrase")

    args = ap.parse_args()

    if args.cmd == "encrypt":
        with open(args.input) as f:
            record = json.load(f)
        payload = encrypt_deal_record(record, args.passphrase)
        print(payload)
        return 0

    if args.cmd == "decrypt":
        with open(args.input) as f:
            payload = f.read().strip()
        try:
            record = decrypt_deal_record(payload, args.passphrase)
        except DealVaultDecryptError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print(json.dumps(record, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
