# Licensing strategy — dual-license by file

This repository uses a **dual-license by file** strategy to satisfy two
goals at once:

1. **Bounty compliance.** The Mermail Build &amp; Demo bounty requires a
   public GitHub Pull Request against
   [`Nudgen-Marketing/mermail-skills`](https://github.com/Nudgen-Marketing/mermail-skills).
   The official repo's
   [CONTRIBUTING.md](https://github.com/Nudgen-Marketing/mermail-skills/blob/main/CONTRIBUTING.md)
   says: *"Prefer MIT (or another OSI license) if you hope to graduate
   later."* So everything that goes into the upstream PR must be MIT.

2. **IP protection.** AliceLabs has invested years building the
   **Universal Trust Adapter (UTA)**, **BÓVEDA**, and the **mcp-vault-server**
   circuit breaker. Those differentiators should not be relicensed away
   for free. They stay under **AL-1.0** (AliceLabs Source-Available
   License), which permits source review and non-commercial use but
   forbids commercial use, redistribution, and forking without written
   authorization.

## File-level license map

| Path | License | Upstreamed to official repo? |
| --- | --- | --- |
| `LICENSE` (root) | MIT | ✓ |
| `skills/mermail-escrow-agent/SKILL.md` | MIT | ✓ |
| `skills/mermail-escrow-agent/agents/openai.yaml` | MIT | ✓ |
| `skills/mermail-escrow-agent/references/*.md` | MIT | ✓ |
| `skills/mermail-escrow-agent/scripts/*.py` | MIT | ✓ |
| `tests/scenarios.json` | MIT | ✓ |
| `README.md`, `ARCHITECTURE.md`, `DEMO_SCRIPT.md`, etc. | MIT | ✓ |
| `docs/index.html` (demo page) | MIT | ✓ |
| `repo-patches/` | MIT | ✓ |
| **`LICENSE-AL-1.0`** | AL-1.0 | ✗ (governs `integrations/`) |
| **`integrations/uta-trust-cards/**`** | AL-1.0 | ✗ |
| **`integrations/boveda-deal-vault/**`** | AL-1.0 | ✗ |
| **`integrations/mcp-vault-circuit-breaker/**`** | AL-1.0 | ✗ |
| **`PROPRIETARY.md`** (this file) | CC-BY 4.0 (doc) | ✗ |

## What this means in practice

### For the bounty judges

- The PR submitted to `Nudgen-Marketing/mermail-skills` contains **only
  MIT-licensed files**. It is 100% MIT, OSI-compliant, and ready to
  graduate into the official package.
- The companion repo (this one) ships **extra integrations** under
  AL-1.0. These are not part of the PR. They are AliceLabs'
  differentiator on top of the open skill.
- The skill works **without** the integrations. A builder who installs
  only the MIT core gets a fully functional escrow skill. The
  integrations add defense-in-depth (cryptographic identity, encrypted
  deal records, circuit breaker) but are not required.

### For other builders

- **MIT core:** clone, fork, modify, ship commercially, no strings
  attached. Just keep the copyright notice.
- **AL-1.0 integrations:** read the source, run them locally for
  evaluation, submit PRs back to this repo. Commercial use (including
  shipping them inside a paid product) requires a commercial license
  from AliceLabs. Contact `legal@alicelabs.site`.

### For AliceLabs (you)

- The idea and the basic workflow are public (MIT) — this is
  unavoidable for the bounty. But the **secret sauce** (UTA Trust
  Cards, BÓVEDA encryption, the circuit breaker pattern) stays
  AL-1.0. Anyone who wants to commercialize those needs to license
  them from you.
- This protects the IP through the bounty deadline (Sep 23) and
  beyond. After the bounty, you can decide whether to relicense the
  integrations to MIT, keep them AL-1.0, or offer them as a paid
  product.

## Why not just use AL-1.0 for everything?

Three reasons:

1. **The official repo requires MIT for graduation.** A skill under
   AL-1.0 cannot be merged into `Nudgen-Marketing/mermail-skills`
   because AL-1.0 is not OSI-approved and forbids forking.
2. **The bounty's "Reusability" criterion** says "Other builders can
   reproduce the demonstrated workflow." AL-1.0's no-commercial-use
   clause would make this harder.
3. **Defensive publication.** By publishing the core under MIT, we
   establish prior art. Nobody can patent "email-coordinated escrow
   with a release phrase" after Sep 23, 2026, because we published it
   first.

## Why not just use MIT for everything?

Because the integrations with UTA, BÓVEDA, and the circuit breaker are
the differentiator that makes this skill better than a naive escrow.
If we MIT them, anyone (including competitors) can take them, rename
them, and ship them commercially without giving anything back. AL-1.0
keeps that option open while still allowing source review and
non-commercial use.

## Trademark notices

- "Mermail" is a trademark of Nudgen LLC. This skill is a community
  companion, not an official Mermail product.
- "AliceLabs", "MarketNow", "Universal Trust Adapter", "UTA", "ATC",
  "Agent Trust Credential", "UTS", "Universal Trust Schema" are
  trademarks of AliceLabs LLC.
- Use of AliceLabs trademarks in connection with the AL-1.0 integrations
  requires written authorization from AliceLabs. The MIT core does not
  use any AliceLabs trademark.

## Adding a new integration

If you add a new integration (e.g. `integrations/opengravity-risk-score/`),
follow this checklist:

1. Create the directory under `integrations/`.
2. Add a header to every file:
   ```text
   SPDX-License-Identifier: AL-1.0
   Copyright (c) 2026 AliceLabs LLC. All rights reserved.
   ```
3. Reference this file (`PROPRIETARY.md`) in the integration's README.
4. Do **not** include the integration in `repo-patches/` — it must not
   be part of the upstream PR.
5. Update the file-level license map above.

## Questions

- Commercial licensing: `legal@alicelabs.site`
- Bounty submission questions: open an issue on this repo
- Upstream contribution questions: see
  [CONTRIBUTING.md](https://github.com/Nudgen-Marketing/mermail-skills/blob/main/CONTRIBUTING.md)
  in the official repo
