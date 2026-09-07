# Architecture

> Visual reference for `mermail-escrow-agent`. All diagrams are written in
> [Mermaid](https://mermaid.js.org/) and render natively on GitHub, in
> VS Code, and on the demo page.

## Component map

```mermaid
flowchart LR
    subgraph User["User layer"]
        BuyerChat["Buyer<br/>(chat)"]
        BuyerMail["Buyer<br/>(email client)"]
        SellerMail["Seller<br/>(email client)"]
    end

    subgraph AgentHost["Agent host (Claude Code / Cursor / Codex / OpenClaw / Hermes)"]
        Skill["mermail-escrow-agent<br/>SKILL.md + references/"]
        AgentLoop["Agent loop<br/>(LLM + tool-call stream)"]
    end

    subgraph Mermail["Mermail (hosted)"]
        MCP["MCP server<br/>console.mermail.app/mcp<br/>Streamable HTTP + OAuth"]
        Inbox[("Inbox<br/>agent+escrow@mermail.app")]
        Wallet["Agent Wallet<br/>(PayBox)"]
    end

    subgraph Chain["On-chain"]
        EVM["Base / Ethereum / Polygon<br/>USDC transfer"]
        Sol["Solana<br/>USDC transfer"]
    end

    BuyerChat -->|"deal envelope<br/>+ approvals"| AgentLoop
    AgentLoop -->|"loads"| Skill
    AgentLoop -->|"tools/call"| MCP
    MCP --> Inbox
    MCP --> Wallet
    Inbox -->|"new replies"| MCP
    BuyerMail -.->|"release phrase reply"| Inbox
    SellerMail -.->|"dispute signal"| Inbox
    MCP -->|"search_emails / get_email"| AgentLoop
    Wallet -->|"paybox_request_transfer"| EVM
    Wallet -->|"paybox_request_transfer"| Sol
    EVM -.->|"tx hash"| Wallet
    Sol -.->|"tx hash"| Wallet
    Wallet -->|"tx hash"| MCP
    MCP -->|"send_email receipt"| Inbox
    Inbox -.->|"receipt email"| BuyerMail
    Inbox -.->|"receipt email"| SellerMail
```

## State machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Buyer chat: deal envelope
    DRAFT --> ARMED: get_paybox_connection = ACTIVE
    ARMED --> HELD: Buyer approves funding preview\npaybox_request_transfer (hold)
    ARMED --> BLOCKED: PayBox disconnected / funds insufficient\n/ address checksum fail
    HELD --> RELEASED: Buyer reply fetched + sender verified\n+ release_phrase hash match\n+ fresh approval\npaybox_request_transfer (to seller)
    HELD --> REFUNDED: Deadline passed OR buyer reply "refund"\n+ fresh approval\npaybox_request_transfer (to buyer)
    HELD --> AMBIGUOUS: Two release candidates in one poll window
    HELD --> DISPUTE: Seller reply contains dispute keywords
    HELD --> CANCELLED: Both parties reply "cancel escrow <deal-id>"
    AMBIGUOUS --> HELD: Buyer confirms canonical reply
    AMBIGUOUS --> REFUNDED: Buyer chooses refund
    DISPUTE --> HELD: Buyer chooses release anyway
    DISPUTE --> REFUNDED: Buyer chooses refund
    RELEASED --> [*]: Receipt email sent
    REFUNDED --> [*]: Receipt email sent
    CANCELLED --> [*]: No PayBox call if no funds held
    BLOCKED --> [*]: Incident report emailed
```

## End-to-end sequence (happy path)

```mermaid
sequenceDiagram
    autonumber
    actor Buyer
    actor Seller
    participant Agent as Agent (mermail-escrow-agent)
    participant MCP as Mermail MCP
    participant Inbox as Mermail Inbox
    participant PayBox as Agent Wallet / PayBox
    participant Chain as Base chain

    Note over Buyer, Seller: Phase 0 — Buyer + Seller agree over email
    Buyer->>Inbox: "I'd like to escrow 50 USDC for the keyboard"
    Seller->>Inbox: "Confirmed. My wallet is 0xSeller."

    Note over Buyer, Agent: Phase 0 — Buyer triggers skill in chat
    Buyer->>Agent: "Escrow 50 USDC on Base to 0xSeller, release when I reply 'release escrow kbd-1'"

    Note over Agent, PayBox: Phase 1 — PayBox probe
    Agent->>MCP: tools/call get_paybox_connection
    MCP->>PayBox: probe
    PayBox-->>MCP: ACTIVE
    MCP-->>Agent: { status: ACTIVE, wallet: **** 4821 }

    Note over Agent, Inbox: Phase 2 — Resolve mailbox + thread
    Agent->>MCP: tools/call list_mailboxes
    MCP-->>Agent: [agent+escrow@mermail.app]
    Agent->>MCP: tools/call get_email_context (seed message)
    MCP-->>Agent: { threadId: thr_xyz789 }

    Note over Agent, Inbox: Phase 3 — Baseline read
    Agent->>MCP: tools/call search_emails (metadata_only=true)
    MCP-->>Agent: [eml_001, eml_002] (baseline ids)

    Note over Buyer, Agent: Phase 4 — Funding preview + approval
    Agent->>Buyer: "Funding preview: 50 USDC on BASE, hold in **** 4821"
    Buyer->>Agent: "yes, fund it"
    Agent->>MCP: tools/call paybox_request_transfer (hold)
    MCP->>PayBox: transfer (self / standing grant)
    PayBox->>Chain: hold tx
    Chain-->>PayBox: tx hash
    PayBox-->>MCP: { status: success, tx: 0xHold }
    MCP-->>Agent: { funding_tx: 0xHold }
    Agent->>MCP: tools/call send_email (funds held)
    MCP->>Inbox: receipt email
    Inbox-->>Buyer: "Escrow kbd-1 — funds held"
    Inbox-->>Seller: "Escrow kbd-1 — funds held"

    Note over Buyer, Inbox: Phase 5 — Buyer replies with release phrase
    Buyer->>Inbox: "release escrow kbd-1a2b3c4d"

    Note over Agent, Inbox: Phase 5 — Monitor + match
    Agent->>MCP: tools/call search_emails (exclude baseline)
    MCP-->>Agent: [eml_003]
    Agent->>MCP: tools/call get_email (eml_003)
    MCP-->>Agent: { from: buyer, body: "release escrow kbd-1a2b3c4d" }
    Note right of Agent: sender_authentication.status === pass<br/>sha256(line) === release_phrase_hash

    Note over Buyer, Agent: Phase 6 — Release preview + fresh approval
    Agent->>Buyer: "Release preview: 50 USDC to 0xSeller"
    Buyer->>Agent: "yes, release it"
    Agent->>MCP: tools/call paybox_request_transfer (to seller)
    MCP->>PayBox: transfer to 0xSeller
    PayBox->>Chain: release tx
    Chain-->>PayBox: tx hash
    PayBox-->>MCP: { status: success, tx: 0xRelease }
    MCP-->>Agent: { release_tx: 0xRelease }
    Agent->>MCP: tools/call send_email (released)
    MCP->>Inbox: receipt email with tx hash
    Inbox-->>Buyer: "Escrow kbd-1 — released (0xRelease)"
    Inbox-->>Seller: "Escrow kbd-1 — released (0xRelease)"
```

## Threat model + defenses

```mermaid
flowchart TD
    subgraph Attacks["Attack vectors"]
        A1["Forge release<br/>from seller's email"]
        A2["Redirect payout<br/>via email request"]
        A3["Trigger auto-refund<br/>from forged buyer email"]
        A4["Broaden deal scope<br/>(amount, asset, chain)"]
        A5["Exhaust buyer<br/>with ambiguous replies"]
    end

    subgraph Defenses["Defenses (security.md)"]
        D1["Rule 2: Release-phrase hashing<br/>sha256(line) === stored hash"]
        D2["Rule 3: sender_authentication.status === pass<br/>+ normalised address match"]
        D3["Rule 4: Destination immutability<br/>only chat can change envelope"]
        D4["Rule 5: No auto-release, no auto-refund<br/>fresh approval required"]
        D5["Rule 9: Bounded read budget<br/>+ AMBIGUOUS state on multi-match"]
    end

    A1 --> D2
    A1 --> D1
    A2 --> D3
    A3 --> D4
    A4 --> D3
    A5 --> D5

    style Defenses fill:#0f9d5820,stroke:#0f9d58
    style Attacks fill:#db443720,stroke:#db4437
```

## Tool routing decision tree

```mermaid
flowchart TD
    Start["User request"] --> Q1{"Hold funds until<br/>confirmation, then<br/>release?"}
    Q1 -->|Yes| Q2{"Confirmation comes<br/>from an email reply<br/>in a Mermail thread?"}
    Q2 -->|Yes| Escrow["mermail-escrow-agent"]
    Q2 -->|No, from a webhook| Q3{"Need Agent Wallet<br/>to hold/refund?"}
    Q3 -->|Yes| Companion["Build a companion skill<br/>(not in official package)"]
    Q3 -->|No| Wallet["mermail-agent-wallet"]

    Q1 -->|No, immediate pay| Q4{"Pay a selected x402<br/>service, then continue?"}
    Q4 -->|Yes| X402["mermail-x402-agent"]
    Q4 -->|No| Q5{"Pay a vendor invoice<br/>from the inbox?"}
    Q5 -->|Yes| Invoice["mermail-invoice-pay-agent<br/>(if added) or mermail-agent-wallet"]
    Q5 -->|No| Wallet

    style Escrow fill:#4285f420,stroke:#4285f4
```

## Data flow — deal record

```mermaid
flowchart LR
    subgraph Inputs["Inputs (chat only — never email)"]
        I1["amount_decimal"]
        I2["token, chain"]
        I3["seller_destination"]
        I4["deadline_iso"]
        I5["seller_email"]
    end

    subgraph Record["Deal record (JSON, stored as mailbox draft)"]
        R1["deal_id<br/>kbd-1a2b3c4d"]
        R2["state: DRAFT → ARMED → HELD → RELEASED"]
        R3["release_phrase_hash<br/>(sha256, not plaintext)"]
        R4["baseline_email_ids[]<br/>(excluded from polling)"]
        R5["funding_tx / release_tx / refund_tx"]
        R6["audit_log[]<br/>(ts + event + email_id)"]
    end

    subgraph Never["Never in record"]
        N1["private keys"]
        N2["signing URLs"]
        N3["raw signed payloads"]
        N4["release_phrase (plaintext)"]
        N5["MERMAIL_API_KEY"]
    end

    Inputs --> Record
    Record -.->|"never"| Never

    style Never fill:#db443720,stroke:#db4437
    style Record fill:#0f9d5820,stroke:#0f9d58
```

## MCP profile matrix

```mermaid
flowchart TD
    Use["Skill: mermail-escrow-agent"] --> Needs{"Needs PayBox?"}
    Needs -->|Yes, always| Full["Full-profile OAuth<br/>console.mermail.app/mcp"]
    Needs -->|No, inbox-only| AgentInbox["agent-inbox profile<br/>?profile=agent-inbox"]
    Needs -->|No, automation| APIKey["API key<br/>x-api-key: sk-proj-..."]

    Full --> CanDo["Can: hold, release, refund"]
    Full --> Cannot["Cannot: share private keys<br/>(never exposed)"]

    AgentInbox --> ReadOnly["Can: list, search, get email<br/>Cannot: send, PayBox"]
    APIKey --> Limited["Can: list, search, send email<br/>Cannot: PayBox"]

    style Full fill:#0f9d5820,stroke:#0f9d58
    style AgentInbox fill:#f4b40020,stroke:#f4b400
    style APIKey fill:#db443720,stroke:#db4437
```

## Why this design (decisions log)

| Decision | Rationale |
| --- | --- |
| Email is the entire UI | No marketplace app, no smart contract deployment. Maximises "inbox + wallet both load-bearing" criterion. |
| Hold funds in buyer's own Agent Wallet (not a separate escrow contract) | Avoids deploying new smart contracts. Uses PayBox's existing delegation + standing grants as the policy boundary. |
| Release-phrase hashing (not plaintext storage) | Prevents the phrase from leaking via logs that quote email bodies. The hash is computed locally; only the hash is persisted. |
| Destination immutability from email | The #1 attack vector is a forged "please send to a different address" email. Hard rule: only chat can set/ change `seller_destination`. |
| Fresh approval for release (funding approval ≠ release approval) | Prevents a "approve once, drain wallet" attack if the buyer's chat session is hijacked mid-deal. |
| No auto-refund on deadline | Auto-refund on deadline would let an attacker who can delay the buyer's release phrase trigger a refund. The agent surfaces the deadline and asks the buyer to approve. |
| Composable, not duplicative (no new tool ownership) | Maximises chance of graduation into the official package. The `tool-coverage.json` patch only adds a `composes` entry. |
| 3 reference docs (tools, workflows, security) | Keeps `SKILL.md` under the 500-line AUTHORING.md limit while still being complete enough to re-implement from scratch. |
