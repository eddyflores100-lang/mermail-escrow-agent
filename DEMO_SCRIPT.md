# Demo Video Script — `mermail-escrow-agent`

**Duration:** 3 min 30 s (within the 2–5 min bounty window)
**Format:** Single-take screen recording with voiceover
**Language:** English (bounty requires English submissions). A Spanish
voiceover translation is provided at the bottom for the creator's reference
only — the posted video must be in English.
**Required on-screen:** (1) a prompt that triggers the skill, (2) the skill
connecting to and using Mermail, (3) the agent completing the workflow,
(4) the final result.

## Pre-recording checklist

- [ ] Mermail workspace created, mailbox `agent+escrow@mermail.app` provisioned
- [ ] `MERMAIL_API_KEY` exported in the shell that launches the AI client
- [ ] Mermail MCP connected with OAuth in Claude Code (or Cursor / Codex / OpenClaw)
- [ ] PayBox connected from the Mermail console; wallet funded with ≥ 60 USDC on Base
- [ ] A standing grant for `paybox_request_transfer` configured (so the demo
      doesn't stall on a per-transfer click) — OR be ready to click through
      one PayBox signing prompt per transfer
- [ ] The `mermail-escrow-agent` skill installed locally (see README.md)
- [ ] The `simulate_inbox.py` script run, so the mailbox has a seeded deal thread
- [ ] Terminal + AI client + Mermail console open in three visible panes
- [ ] Screen recording software tested (OBS / QuickTime / Loom)

## Storyboard

### 0:00 — 0:20  ·  Hook (no Mermail yet)

**On screen:** Your face (small webcam circle) over a blank desktop.

**Voiceover:**
> "Most peer-to-peer deals online still need a human in the middle to hold
> the money. What if your AI agent could be that middleman — over plain
> email, with no separate marketplace app? I built a Mermail skill that
> does exactly that. Here's a three-minute demo."

**Cut to:** full-screen capture of the AI client (Claude Code recommended).

### 0:20 — 0:50  ·  Show the seeded deal thread (uses Mermail inbox)

**On screen:** Open the Mermail console at
`https://console.mermail.app/mailboxes` in a browser pane. Click the
`agent+escrow@mermail.app` mailbox. Show the seeded thread:

> Subject: HHKB keyboard — 50 USDC
>
> From: buyer@example.com — "I'd like to escrow 50 USDC on BASE for the
> used HHKB keyboard we discussed. Deal id: kbd-1a2b3c4d."
>
> From: seller@example.com — "Confirmed — I'll ship once funds are held.
> My payout wallet is 0x742d35Cc...E321 on BASE."

**Voiceover:**
> "Here's the deal thread in my agent's Mermail inbox. The buyer and seller
> have already agreed over email. My agent's job is to hold the funds and
> release them when the buyer confirms receipt — all in this same thread."

### 0:50 — 1:40  ·  Trigger the skill (prompt + Mermail connection)

**On screen:** Switch to the AI client. Type the trigger prompt:

```
Use $mermail-escrow-agent to escrow 50 USDC on Base for the used HHKB
keyboard thread. Seller wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f6E321.
Seller email: seller@example.com. Deadline: 2026-09-12T18:00:00Z. Release
when I reply "release escrow kbd-1a2b3c4d" in the thread.
```

**On screen:** Show the agent's response. It should:

1. Acknowledge the skill is being used.
2. Call `get_paybox_connection` (visible in the tool-call stream — point to
   it: "Here's the PayBox probe").
3. Call `list_mailboxes` and pick `agent+escrow@mermail.app`.
4. Call `get_email_context` on the seeded thread to record `thread_id`.
5. Call `search_emails` for the baseline read.
6. Show the **funding preview**:

   ```
   Deal ID:        kbd-1a2b3c4d
   Hold amount:    50.00 USDC on BASE
   Held by:        Your Agent Wallet (**** 4821)
   Seller payout:  0x742d...E321 (on release only)
   Deadline:       2026-09-12T18:00:00Z (auto-refund after)
   Release phrase: "release escrow kbd-1a2b3c4d"
   ```

7. Ask for approval.

**Voiceover:**
> "I trigger the skill with one prompt. The agent first probes PayBox with
> `get_paybox_connection` — that's the gate. Then it lists my mailboxes,
> resolves the deal thread, takes a baseline read so it doesn't re-process
> old emails, and shows me a funding preview. Nothing has moved yet."

**Approve** in chat ("yes, fund it").

**On screen:** The agent calls `paybox_request_transfer` (visible in the
tool stream). PayBox signs the hold. The agent calls `send_email` to post
the "funds held" receipt to the deal thread.

**Voiceover:**
> "I approve. The agent holds 50 USDC in my Agent Wallet — funds stay with
> me, not with the seller yet — and emails the deal thread to confirm."

### 1:40 — 2:30  ·  Release the escrow (workflow completion)

**On screen:** Switch to the Mermail console. Show the new "funds held"
email at the top of the thread. Then switch to a different email client
(the buyer's) and reply to the thread with the release phrase:

```
release escrow kbd-1a2b3c4d
```

Switch back to the AI client. Type:

```
I replied in the keyboard thread. Please release the escrow.
```

**On screen:** The agent:

1. Calls `search_emails` (excluding baseline ids).
2. Calls `get_email` on the new reply.
3. Normalises the sender, hash-matches the release phrase (the agent can
   show: "Sender authenticated ✓, release phrase matched ✓").
4. Shows the **release preview**:

   ```
   Release deal:   kbd-1a2b3c4d
   Send:           50.00 USDC on BASE
   From:           Your Agent Wallet (**** 4821)
   To:             0x742d...E321
   Trigger:        Your reply "release escrow kbd-1a2b3c4d" at 2026-09-10T14:22Z
   ```

5. Asks for fresh approval.

**Voiceover:**
> "Now I reply in the deal thread with the release phrase. The agent
> fetches my reply with `get_email`, authenticates the sender, hash-matches
> the phrase, and shows me a release preview. Note: funding approval did
> not authorise release — I have to approve again, fresh."

**Approve** in chat ("yes, release it").

**On screen:** The agent calls `paybox_request_transfer` to the seller's
wallet. PayBox signs. The agent calls `send_email` to post the "released"
receipt with the tx hash.

### 2:30 — 3:10  ·  Show the final result (on-chain + email)

**On screen:** Three-pane split:
- Left: Mermail console mailbox — the "released" receipt email with tx hash.
- Center: Basescan (https://basescan.org) — paste the tx hash, show the
  on-chain transfer from the agent wallet to the seller's wallet.
- Right: The agent's chat — final summary message from the agent.

**Voiceover:**
> "Three things happened: (1) the seller's wallet received 50 USDC on
> Base — here's the on-chain tx; (2) the deal thread got a receipt email
> with the tx hash; (3) the agent printed a final summary. End-to-end,
> the entire workflow was driven by two prompts and one email reply."

### 3:10 — 3:30  ·  Close

**On screen:** Cut back to your face.

**Voiceover:**
> "That's peer-to-peer escrow, coordinated entirely over email, with
> Mermail's inbox and Agent Wallet. The skill is open source — link in the
> description. Tag @Mermailapp. Thanks for watching."

**On screen:** End card with:
- GitHub repo URL
- "Built for the Mermail Build & Demo bounty"
- "@Mermailapp"
- Your handle

## Required screenshots for the PR

Capture these as PNGs and attach to the PR description:

1. The funding preview shown by the agent (Phase 4).
2. The release preview shown by the agent (Phase 6).
3. The "funds held" email in the Mermail console.
4. The "released" email in the Mermail console.
5. The on-chain tx on Basescan (or Solana Explorer for SOL deals).
6. The agent's final summary message.

## Voiceover script — clean text

```
[0:00] Most peer-to-peer deals online still need a human in the middle to
hold the money. What if your AI agent could be that middleman — over plain
email, with no separate marketplace app? I built a Mermail skill that does
exactly that. Here's a three-minute demo.

[0:20] Here's the deal thread in my agent's Mermail inbox. The buyer and
seller have already agreed over email. My agent's job is to hold the funds
and release them when the buyer confirms receipt — all in this same thread.

[0:50] I trigger the skill with one prompt. The agent first probes PayBox
with get_paybox_connection — that's the gate. Then it lists my mailboxes,
resolves the deal thread, takes a baseline read so it doesn't re-process
old emails, and shows me a funding preview. Nothing has moved yet.

[1:40] I approve. The agent holds 50 USDC in my Agent Wallet — funds stay
with me, not with the seller yet — and emails the deal thread to confirm.

[1:55] Now I reply in the deal thread with the release phrase. The agent
fetches my reply with get_email, authenticates the sender, hash-matches
the phrase, and shows me a release preview. Note: funding approval did
not authorise release — I have to approve again, fresh.

[2:30] Three things happened: the seller's wallet received 50 USDC on
Base — here's the on-chain tx; the deal thread got a receipt email with
the tx hash; the agent printed a final summary. End-to-end, the entire
workflow was driven by two prompts and one email reply.

[3:10] That's peer-to-peer escrow, coordinated entirely over email, with
Mermail's inbox and Agent Wallet. The skill is open source — link in the
description. Tag @Mermailapp. Thanks for watching.
```

---

## Guion en español (referencia del creador — no publicar)

El video publicado debe estar en inglés (reglas del bounty). Esta
traducción es solo para que el creador prepare la toma.

```
[0:00] La mayoría de los tratos entre dos personas en internet todavía
necesitan un humano en el medio que guarde el dinero. ¿Y si tu agente de
IA pudiera ser ese intermediario — por correo electrónico, sin una app de
mercado aparte? Construí una skill de Mermail que hace justo eso. Aquí
una demo de tres minutos.

[0:20] Este es el hilo del trato en el inbox de Mermail de mi agente. El
comprador y el vendedor ya se pusieron de acuerdo por correo. El trabajo
de mi agente es retener los fondos y liberarlos cuando el comprador
confirme la recepción — todo en este mismo hilo.

[0:50] Disparo la skill con un solo prompt. El agente primero prueba
PayBox con get_paybox_connection — esa es la compuerta. Luego lista mis
mailboxes, resuelve el hilo del trato, hace una lectura basal para no
reprocesar correos viejos, y me muestra un preview de financiamiento. Nada
se ha movido todavía.

[1:40] Aprobaro. El agente retiene 50 USDC en mi Agent Wallet — los fondos
se quedan conmigo, no con el vendedor todavía — y envía un correo al hilo
para confirmar.

[1:55] Ahora respondo en el hilo con la frase de liberación. El agente
obtiene mi respuesta con get_email, autentica el remitente, compara el
hash de la frase, y me muestra un preview de liberación. Ojo: aprobar el
financiamiento no autoriza la liberación — tengo que aprobar de nuevo,
fresco.

[2:30] Pasaron tres cosas: la wallet del vendedor recibió 50 USDC en
Base — aquí está la transacción on-chain; el hilo recibió un correo con
el hash de la transacción; el agente imprimió un resumen final. De
principio a fin, todo el flujo se disparó con dos prompts y una respuesta
de correo.

[3:10] Eso es escrow peer-to-peer, coordinado completamente por correo,
con el inbox y la Agent Wallet de Mermail. La skill es open source — link
en la descripción. Etiqueten a @Mermailapp. Gracias por ver.
```
