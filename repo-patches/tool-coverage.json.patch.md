# Repo patch — `tool-coverage.json`

This file is a **patch description**, not a drop-in JSON file. The official
`tool-coverage.json` in `Nudgen-Marketing/mermail-skills` uses a canonical
schema; the maintainer will integrate the addition below into that schema
during review.

## Intent

Add a new domain entry for `mermail-escrow-agent` that **does not claim any
new MCP tool**. The escrow skill composes tools already owned by other
skills; it must not duplicate ownership.

## Patch (additive)

Add the following entry under the appropriate section of `tool-coverage.json`:

```json
{
  "domains": {
    "mermail-escrow-agent": {
      "owns": [],
      "composes": [
        "list_mailboxes",
        "get_mailbox",
        "get_email_context",
        "get_thread",
        "search_emails",
        "list_emails",
        "get_email",
        "save_draft",
        "send_email",
        "get_paybox_connection",
        "paybox_request_transfer",
        "paybox_get_buy_link"
      ],
      "notes": "Escrow composes tools owned by mermail-agent-inbox, mermail-compose-email, and mermail-agent-wallet. No new tool ownership. Escrow never calls paybox_pay_x402, paybox_use_service, or prepare_destructive_action on PayBox writes."
    }
  },
  "externalEffectTools": {
    "mermail-escrow-agent": [
      "send_email"
    ]
  },
  "walletDestructiveTools": {
    "mermail-escrow-agent": [
      "paybox_request_transfer"
    ]
  }
}
```

## Risk classification rationale

| Tool | Classification | Why |
| --- | --- | --- |
| `send_email` | `externalEffectTools` | Sends an email to external recipients; requires exact preview + fresh approval. |
| `paybox_request_transfer` | `walletDestructiveTools` | Moves funds; uses PayBox's own signing flow, NOT `prepare_destructive_action`. |
| `save_draft` | (none) | Internal write; reversible. |
| `search_emails`, `list_emails`, `get_email` | (none) | Read-only. |
| `get_paybox_connection` | (none) | Read-only probe. |

## What NOT to add

- Do **not** add `paybox_pay_x402` or `paybox_use_service` to this skill —
  they are forbidden (x402 routes to `mermail-x402-agent`).
- Do **not** add `prepare_destructive_action` to this skill's PayBox writes —
  PayBox writes use their own signing flow.
- Do **not** add any tool that is already owned by another focused skill.
  Use the `composes` array, not `owns`.
