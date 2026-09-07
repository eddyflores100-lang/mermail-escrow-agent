# Repo patch — `README.md` Included skills table

Add the following row to the **Included skills** table in the root
`README.md` of `Nudgen-Marketing/mermail-skills`:

```markdown
| `mermail-escrow-agent` | Coordinate peer-to-peer deal escrow over a Mermail email thread; hold buyer funds in Agent Wallet and release to the seller only after the buyer's email-confirmed release phrase |
```

Suggested placement: after `mermail-research-agent` and before
`mermail-x402-agent`, to keep wallet-affecting skills grouped.

## `compatibility.json` bump

If the contribution is merged, bump the skill count in `compatibility.json`:

```diff
- "skillCount": 16,
+ "skillCount": 17,
```

(Check the current count at merge time — the official repo may have
graduated other community skills in the meantime.)
