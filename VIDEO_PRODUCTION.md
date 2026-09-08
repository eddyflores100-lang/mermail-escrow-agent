# Video Production Package — `mermail-escrow-agent`

> **Professional broadcast-quality production package for the Mermail Build &
> Demo bounty video.** This document contains everything you need to record
> the 2–5 minute demo video in a single take: voiceover script (timed),
> shot-by-shot storyboard, on-screen captions, technical specs, and
> pre/post-production checklists.

## ⚠️ Read this first — what this video MUST show

The Mermail bounty rules are explicit:

> *"The video must show the actual skill in action. A presentation or code
> walkthrough without a working demonstration is not sufficient."*

This means your video **must** capture:

1. A real prompt typed into a real AI client (Claude Code recommended)
2. The skill connecting to and calling real Mermail MCP tools (`get_paybox_connection`, `list_mailboxes`, `search_emails`, `get_email`, `paybox_request_transfer`, `send_email`)
3. The agent completing the funding → monitoring → release workflow end-to-end
4. The final result: a real on-chain USDC transfer on Base (visible on Basescan) + a real receipt email in the Mermail inbox

**What is NOT acceptable:**
- A video of only the demo page simulator (that's an explainer, not a demo)
- A code walkthrough without running the skill
- A slide presentation
- The `walkthrough.mp4` in this folder (that's a simulator recording, included only as visual reference)

The `walkthrough.mp4` and screenshots in this folder are **B-roll reference** — use them to plan your shots, not as the final video.

---

## Pre-production checklist

### Environment (one-time, ~30 min)

- [ ] Mermail workspace created at https://mermail.app
- [ ] Mailbox `agent+escrow@mermail.app` provisioned (10 credits)
- [ ] `MERMAIL_API_KEY` exported in the shell that launches Claude Code
- [ ] Mermail MCP connected with OAuth: `claude mcp add --transport http --scope user mermail https://console.mermail.app/mcp`
- [ ] PayBox connected from the Mermail console (Agent Wallet)
- [ ] Wallet funded with ≥ 60 USDC on Base (covers the 50 USDC deal + fees)
- [ ] Standing grant for `paybox_request_transfer` configured (so the demo doesn't stall on per-transfer clicks) — OR be ready to click through one PayBox signing prompt per transfer
- [ ] `mermail-escrow-agent` skill installed locally (see README.md → Install)
- [ ] `simulate_inbox.py` run, so the mailbox has a seeded deal thread
- [ ] Basescan open in a browser tab (https://basescan.org) — you'll paste the tx hash here
- [ ] A second email account open (the buyer's) to send the release phrase reply

### Recording setup

- [ ] **OBS Studio** installed (or QuickTime on macOS, Loom, or ScreenStudio)
- [ ] **Resolution:** 1920×1080 (1080p) — do NOT record in 4K, file size will be huge
- [ ] **FPS:** 30
- [ ] **Format:** MP4 (H.264), AAC audio
- [ ] **Audio:** USB microphone or headset (NO laptop built-in mic — it sounds amateur)
- [ ] **Mic gain:** set so your voice peaks at -12 dB to -6 dB (test with OBS meter)
- [ ] **Room:** quiet, no echo, no fan noise. Record a 5-second silence sample and listen back
- [ ] **Webcam:** optional small circle in bottom-right (128×128 px) — adds personality
- [ ] **Desktop:** clean, no notifications, no messy tabs. Use a neutral wallpaper
- [ ] **Browser:** hide bookmarks bar, disable notifications, dark mode
- [ ] **Claude Code:** full-screen terminal, font size 14-16 (legible on 1080p)

### Voiceover setup

- [ ] **Language:** English (bounty requires English submissions)
- [ ] **Tone:** professional, calm, technical — NOT salesy, NOT hyped
- [ ] **Pace:** ~150 words per minute (slower than conversational)
- [ ] **Hydrate:** drink water 15 min before recording
- [ ] **Warm up:** read the script aloud once before hitting record

---

## Voiceover script (timed, English, broadcast quality)

**Total runtime: 3 min 40 s** (within the 2–5 min bounty window)

Read this exactly. Pauses are marked with `[pause]` (1 second) and `[beat]` (0.5 second).

---

### [0:00 – 0:20] Hook

> Most peer-to-peer deals online still need a human in the middle to hold
> the money. [pause] What if your AI agent could be that middleman — over
> plain email, with no separate marketplace app? [beat] I built a Mermail
> skill that does exactly that. Here's a three-minute demo.

**On-screen:** Your face (small webcam circle) over a blank desktop. Cut to
full-screen capture of Claude Code at 0:08.

---

### [0:20 – 0:50] The deal thread (Mermail inbox)

> Here's the deal thread in my agent's Mermail inbox. [pause] The buyer
> and seller have already agreed over email — fifty USDC for a used
> keyboard. [beat] My agent's job is to hold the funds and release them
> when the buyer confirms receipt — all in this same thread.

**On-screen:** Mermail console open at `console.mermail.app/mailboxes`.
Click the `agent+escrow@mermail.app` mailbox. Show the seeded thread:
- Email 1 from buyer: "I'd like to escrow 50 USDC..."
- Email 2 from seller: "Confirmed — I'll ship once funds are held..."

---

### [0:50 – 1:40] Trigger the skill (prompt + Mermail connection)

> I trigger the skill with one prompt. [pause] The agent first probes
> PayBox with `get_paybox_connection` — that's the gate. [beat] Then it
> lists my mailboxes, resolves the deal thread, takes a baseline read so
> it doesn't re-process old emails, and shows me a funding preview.
> [pause] Nothing has moved yet.

**On-screen:** Switch to Claude Code. Type the trigger prompt exactly:

```
Use $mermail-escrow-agent to escrow 50 USDC on Base for the used HHKB
keyboard thread. Seller wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f6E321.
Seller email: seller@example.com. Deadline: 2026-09-12T18:00:00Z.
Release when I reply "release escrow kbd-1a2b3c4d" in the thread.
```

**Point the camera at** (do NOT narrate each one, just let them appear):
- `get_paybox_connection` tool call → `ACTIVE`
- `list_mailboxes` → picks `agent+escrow@mermail.app`
- `get_email_context` → `threadId: thr_xyz789`
- `search_emails` (baseline) → `[{id: eml_001}, {id: eml_002}]`
- Funding preview appears:

```
Deal ID:        kbd-1a2b3c4d
Hold amount:    50.00 USDC on BASE
Held by:        Your Agent Wallet (**** 4821)
Seller payout:  0x742d...E321 (on release only)
Deadline:       2026-09-12T18:00:00Z (auto-refund after)
Release phrase: "release escrow kbd-1a2b3c4d"
```

---

### [1:40 – 2:00] Approve funding

> I approve. [pause] The agent holds fifty USDC in my Agent Wallet —
> funds stay with me, not with the seller yet — and emails the deal
> thread to confirm.

**On-screen:** Type `yes, fund it` in Claude Code. The agent calls
`paybox_request_transfer` (hold). PayBox signs. The agent calls
`send_email`. Switch to Mermail console — show the new "funds held"
email at the top of the thread.

---

### [2:00 – 2:50] Release the escrow (workflow completion)

> Now I reply in the deal thread with the release phrase. [pause] The
> agent fetches my reply with `get_email`, authenticates the sender,
> hash-matches the phrase, and shows me a release preview. [beat] Note:
> funding approval did not authorize release — I have to approve again,
> fresh.

**On-screen:** Switch to the buyer's email client. Reply to the deal
thread with exactly:

```
release escrow kbd-1a2b3c4d
```

Switch back to Claude Code. Type:

```
I replied in the keyboard thread. Please release the escrow.
```

**Let the camera capture** (do NOT narrate each):
- `search_emails` (excluding baseline) → new candidate `eml_004`
- `get_email` → fetches the reply
- Agent prints: "Security checks passed: sender_authentication.status === pass, sha256 match, etc."
- Release preview appears:

```
Release deal:   kbd-1a2b3c4d
Send:           50.00 USDC on BASE
From:           Your Agent Wallet (**** 4821)
To:             0x742d...E321
Trigger:        Your reply "release escrow kbd-1a2b3c4d" at 2026-09-10T14:22Z
```

Type `yes, release it`. Agent calls `paybox_request_transfer` to seller.
PayBox signs. Agent calls `send_email` with the receipt.

---

### [2:50 – 3:20] Show the final result (on-chain + email)

> Three things happened. [pause] One: the seller's wallet received fifty
> USDC on Base — here's the on-chain transaction. [beat] Two: the deal
> thread got a receipt email with the tx hash. [beat] Three: the agent
> printed a final summary. [pause] End-to-end, the entire workflow was
> driven by two prompts and one email reply.

**On-screen:** Three-pane split (or quick cuts):
1. **Left:** Mermail console mailbox — the "released" receipt email with tx hash
2. **Center:** Basescan (https://basescan.org) — paste the tx hash, show the on-chain transfer from agent wallet to seller wallet
3. **Right:** Claude Code — the agent's final summary message

---

### [3:20 – 3:40] Close

> That's peer-to-peer escrow, coordinated entirely over email, with
> Mermail's inbox and Agent Wallet. [pause] The skill is open source —
> link in the description. [beat] Tag Mermail app. Thanks for watching.

**On-screen:** Cut back to your face. End card with:
- GitHub repo URL: `github.com/eddyflores100-lang/mermail-escrow-agent`
- "Built for the Mermail Build & Demo bounty"
- "@Mermailapp"
- Your handle

---

## Shot list (quick reference)

| # | Time | Shot | Duration |
| --- | --- | --- | --- |
| 1 | 0:00 | Face cam, hook | 20 s |
| 2 | 0:20 | Mermail console — deal thread | 30 s |
| 3 | 0:50 | Claude Code — type trigger prompt | 10 s |
| 4 | 1:00 | Claude Code — tool calls stream (silent) | 30 s |
| 5 | 1:30 | Claude Code — funding preview, type "yes, fund it" | 10 s |
| 6 | 1:40 | Mermail console — "funds held" email | 20 s |
| 7 | 2:00 | Buyer email client — type release phrase reply | 10 s |
| 8 | 2:10 | Claude Code — type "I replied, please release" | 5 s |
| 9 | 2:15 | Claude Code — tool calls + release preview | 25 s |
| 10 | 2:40 | Claude Code — type "yes, release it" | 5 s |
| 11 | 2:45 | Mermail console — "released" email | 10 s |
| 12 | 2:55 | Basescan — paste tx hash, show transfer | 15 s |
| 13 | 3:10 | Claude Code — final summary | 10 s |
| 14 | 3:20 | Face cam — close + end card | 20 s |

---

## On-screen captions (lower-third, white text on semi-transparent black bar)

Add these in post-production (OBS text source or your editor):

| Time | Caption (bottom-center, 18 pt, fade in/out 0.3 s) |
| --- | --- |
| 0:08 | `mermail-escrow-agent · peer-to-peer deal escrow` |
| 0:20 | `Mermail inbox · agent+escrow@mermail.app` |
| 0:50 | `Skill trigger · $mermail-escrow-agent` |
| 1:00 | `MCP: get_paybox_connection = ACTIVE` |
| 1:30 | `Funding preview · 50.00 USDC on BASE` |
| 1:40 | `paybox_request_transfer (hold) · tx 0xHold...` |
| 2:00 | `Buyer reply · release phrase matched` |
| 2:15 | `Release preview · fresh approval required` |
| 2:45 | `paybox_request_transfer (release) · tx 0xRelease...` |
| 2:55 | `On-chain · basescan.org` |
| 3:20 | `github.com/eddyflores100-lang/mermail-escrow-agent` |

---

## Technical specs (OBS settings)

```
Output:
  Format: MP4 (or MKV, remux to MP4 after)
  Encoder: NVIDIA NVENC H.264 (or x264 if no GPU)
  Rate control: CBR
  Bitrate: 6000 Kbps
  Keyframe: 2 s
  Preset: P4 (balanced)

Video:
  Resolution: 1920×1080
  FPS: 30
  Color space: 709

Audio:
  Encoder: AAC
  Bitrate: 192 Kbps
  Sample rate: 48 kHz
  Channels: Stereo (mono is fine if single mic)

Sources:
  Display Capture: 1920×1080, primary monitor
  Audio Input Capture: your USB mic
  Video Capture Device (optional): webcam, 320×320, bottom-right, with chroma key or circular mask

Filters (on mic):
  Noise Suppression: RNNoise
  Compressor: threshold -18 dB, ratio 3:1, attack 6 ms, release 60 ms
  Gain: +6 dB (adjust to peak at -6 dB)
```

---

## Pre-roll / post-roll

- **0.5 s of silence** at the start (before the hook)
- **2 s of end card** at the end (GitHub URL + @Mermailapp, hold after voiceover ends)
- **No music bed** — the bounty is technical, music makes it feel commercial. Pure voice + screen is more professional.

---

## Post-production checklist

- [ ] Watch the full recording once, no pauses — note any stumbles
- [ ] If you stumbled, re-record only that segment and splice in post
- [ ] Add the on-screen captions (lower-third)
- [ ] Add the end card (last 2 seconds)
- [ ] Export as MP4 (H.264, 1080p, 30 fps)
- [ ] File size target: 50–150 MB (under X's 512 MB limit)
- [ ] Watch the exported video on a phone (most viewers are mobile) — is the text legible?
- [ ] Check audio levels: peaks at -6 dB, no clipping, no background hum
- [ ] Upload to X as a new post (NOT a reply)
- [ ] In the X post text, tag `@Mermailapp` and include the GitHub URL

---

## X post template (English)

```
I built mermail-escrow-agent for the @Mermailapp Build & Demo bounty:

Peer-to-peer deal escrow coordinated entirely over email. The agent
holds buyer funds in the Agent Wallet, monitors the same thread for the
buyer's release phrase, and pays the seller only after sender auth +
phrase hash + fresh approval.

Email is the entire UI. Inbox + wallet, both load-bearing.

Demo video ↓
github.com/eddyflores100-lang/mermail-escrow-agent

#MermailBounty #AgentSkills #MCP
```

Keep the post text under 280 characters if possible (X's classic limit).
If you need more, use a thread (first post = video + hook, reply = GitHub
link + details).

---

## B-roll reference (this folder)

The following files in this folder are **visual reference only** — they
show the demo page simulator, NOT the real skill. Use them to plan your
shots, not as the final video.

| File | What it shows |
| --- | --- |
| `00-hero.png` | Hero section with live deal card |
| `01-demo-idle.png` | Simulator in idle state |
| `02-funding-preview.png` | Funding preview shown by the simulator |
| `03-funds-held.png` | Funds held state (inbox + wallet + on-chain panels) |
| `04-release-preview.png` | Release preview with sender auth checks passed |
| `05-released.png` | Final released state with tx hash |
| `06-attack-refused.png` | Attack refusal (security model in action) |
| `07-how-flow.png` | "How it works" — animated deal flow tab |
| `08-how-phases.png` | "How it works" — phase explorer tab |
| `09-how-states.png` | "How it works" — state machine tab |
| `walkthrough.mp4` | 40-second walkthrough of the simulator (B-roll reference) |
| `walkthrough.webm` | Same as mp4, WebM format |
| `how-flow.webm` | Animated deal flow auto-play (12 s) |
| `how-phases.webm` | Phase explorer auto-play (12 s) |
| `how-states.webm` | State machine auto-cycling (8 s) |

---

## Final reminders

1. **The video must be in English** (bounty rule)
2. **The video must show the actual skill in action** against the real Mermail MCP — not just the simulator
3. **Tag @Mermailapp** in the X post
4. **Duration: 2–5 minutes** (this script is 3 min 40 s — within the window)
5. **Record in one take if possible** — splicing is fine but one take feels more authentic
6. **No music** — pure voice + screen. More professional for a technical bounty.
7. **Test the audio first** — record 10 seconds, play it back, check for hum/echo/level
8. **Have the tx hash ready** — after the release, immediately copy it from the agent's output and paste it into Basescan so the on-chain proof shot is smooth

Good luck.
