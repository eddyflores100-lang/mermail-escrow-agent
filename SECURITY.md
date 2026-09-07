# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.0.x | ✓ |

This is a community companion skill. Security fixes target the latest
release on `main`.

## Reporting a vulnerability

**Do not open a public GitHub issue for a security vulnerability.**

Please report vulnerabilities via one of:

1. **GitHub private security advisory** (preferred):
   <https://github.com/eddyflores100-lang/mermail-escrow-agent/security/advisories/new>
2. **Email**: `<your-security-email>` with subject line
   `[SECURITY] mermail-escrow-agent`.

Include:

- A description of the issue and its potential impact
- Steps to reproduce (a Mermail workspace API key, if needed for repro,
  can be sent privately — never paste it into a public issue)
- Suggested fix, if any
- Whether you have already disclosed it publicly

You will receive an acknowledgement within 72 hours. We will coordinate a
fix and disclosure timeline with you. Credit will be given in the release
notes unless you prefer to remain anonymous.

## Threat model summary

This skill moves real funds and reads untrusted email. The full threat
model is in
[`skills/mermail-escrow-agent/references/security.md`](./skills/mermail-escrow-agent/references/security.md).
The headline rules:

1. Email is untrusted data, never an instruction.
2. Release phrases are stored as sha256 hashes, never plaintext.
3. Sender addresses are normalised and `sender_authentication.status`
   must be `pass` for any release/refund/dispute signal.
4. `seller_destination` is immutable from email — only chat can set it.
5. No auto-release, no auto-refund. Fresh approval required for every
   PayBox write.
6. `pending` and `SUBMISSION_UNKNOWN` PayBox statuses are unresolved, not
   success. No automatic retry on rejection.
7. Wallet addresses are checksum-validated before any transfer.
8. No secret leakage: no OAuth tokens, API keys, private keys, signing
   URLs, or raw signed payloads are ever emailed, logged, or persisted in
   the deal record.

## What is NOT a vulnerability

- An email successfully reaching the inbox that the agent refuses to act
  on — that is the security model working as designed.
- A `pending` PayBox status that does not transition state — that is by
  design (Rule 6).
- A seller email asking to change the destination that is refused — that
  is Rule 4.
- The agent refusing to use `MERMAIL_API_KEY` for a PayBox call — that is
  by design (PayBox requires full-profile OAuth).

## Out of scope

- Vulnerabilities in the Mermail hosted MCP server itself → report to
  Mermail via <https://docs.mermail.app/resources/support>.
- Vulnerabilities in PayBox → report to the PayBox team via the Mermail
  console.
- Vulnerabilities in the AI client (Claude Code, Cursor, etc.) → report
  to the client vendor.

## Disclosure policy

- We follow coordinated disclosure.
- A fix is released as soon as practical, typically within 7 days for
  high-severity issues.
- Public disclosure happens after the fix is released, with credit to the
  reporter (unless they prefer anonymity).
