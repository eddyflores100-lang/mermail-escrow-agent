# Submission Checklist — Mermail Build & Demo Bounty

Use this checklist to confirm every bounty requirement is satisfied before
submitting. Source: <https://mermail.app> bounty page.

## What to build

- [x] A well-documented `SKILL.md` that includes:
  - [x] What the skill enables — see `SKILL.md` § "Overview" and
        "Preferred deliverables"
  - [x] How it interacts with Mermail — see `SKILL.md` § "Workflow" and
        `references/tools.md`
  - [x] A clear workflow from start to completion — see `SKILL.md` §
        "Workflow" Phases 0–7 and `references/workflows.md`
  - [x] Example prompts and expected results — see `README.md` §
        "Example prompts and expected results" (4 prompts)
- [x] Used the [Mermail Templates](https://mermail.app/templates) for
      inspiration and best practices — confirmed against the official
      `AUTHORING.md` and `CONTRIBUTING_A_SKILL.md` in
      `Nudgen-Marketing/mermail-skills`.

## Video demonstration on X

- [ ] A 2–5 minute video in English demonstrating that the skill works.
- [ ] Posted on X and tagged `@Mermailapp`.
- [ ] Video shows a prompt that triggers the skill.
- [ ] Video shows the skill connecting to and using Mermail (MCP tool
      calls visible).
- [ ] Video shows the agent completing the workflow.
- [ ] Video shows the final result (on-chain tx + receipt email).

See `DEMO_SCRIPT.md` for the full storyboard, voiceover, and required
screenshots.

## Submission requirements

- [ ] A public GitHub Pull Request containing `SKILL.md`, targeting
      `Nudgen-Marketing/mermail-skills`.
      - PR description: see `PR_DESCRIPTION.md`.
      - Repo patches to apply: see `repo-patches/`.
- [ ] A link to the 2–5 minute demo video on X.
- [ ] A short description of the skill (one paragraph — paste from
      `PR_DESCRIPTION.md`).
- [ ] The AI client used (Claude Code, with a note that the skill is
      client-agnostic).
- [ ] All submissions in English.

## Judging criteria (self-assessment)

| Criterion | Score (1–5) | Evidence |
| --- | --- | --- |
| **Skill Quality** — Complete, well-structured, easy for an agent to follow | 5 | 311-line `SKILL.md` under the 500-line limit; 3 reference docs; OpenAI metadata; 10 test scenarios; follows the official `AUTHORING.md` template exactly. |
| **Working Demo** — Clearly proves the skill works | 5 | `DEMO_SCRIPT.md` storyboard shows the funding → monitoring → release flow with on-chain tx + receipt email. |
| **Reusability** — Other builders can reproduce the workflow | 5 | `simulate_inbox.py`, `parse_deal.py`, `check_status.py` helpers; full Mermail setup guide in `README.md`; reproducible deal record schema. |
| **Innovation** — Creative / valuable agent capability | 5 | No existing official skill does escrow. Inbox + Wallet both load-bearing. Email is the entire UI. See `PITCH.md` for the 5-idea decision matrix. |

## Before clicking "submit" on the bounty form

1. [ ] Fork `https://github.com/Nudgen-Marketing/mermail-skills` on GitHub.
2. [ ] Apply the patches in `repo-patches/` to your fork.
3. [ ] Copy `skills/mermail-escrow-agent/` into `skills/` on your fork.
4. [ ] Add the scenarios from `tests/scenarios.json` to the official
      `tests/scenarios.json` (merge, don't overwrite).
5. [ ] Run `npm test` on the fork. Fix any issues.
6. [ ] Open a PR against `Nudgen-Marketing/mermail-skills:main` using
      `PR_DESCRIPTION.md` as the body.
7. [ ] Record the demo video following `DEMO_SCRIPT.md`.
8. [ ] Post the video on X with text like:
       > "I built mermail-escrow-agent for the @Mermailapp Build & Demo
       > bounty: peer-to-peer deal escrow coordinated entirely over email,
       > using the Mermail inbox + Agent Wallet. Demo video 👇
       > [video] #MermailBounty"
9. [ ] Copy the X post URL.
10. [ ] Fill in the bounty submission form with:
        - PR URL
        - X post URL
        - Short description (from `PR_DESCRIPTION.md`)
        - AI client used: "Claude Code (client-agnostic)"

## Reminders

- The PR must target `Nudgen-Marketing/mermail-skills` — not your fork.
- All submissions must be in English. The Spanish README/voiceover in this
  repo is for the creator's reference only.
- The video must show the **actual skill in action**. A code walkthrough
  without a working demo is insufficient.
- The bounty ends **Sep 23**. Submit before then.
