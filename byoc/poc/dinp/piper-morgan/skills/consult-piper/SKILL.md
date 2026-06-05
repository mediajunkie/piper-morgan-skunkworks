---
name: consult-piper
description: >
  The fuller working session with Piper Morgan: ask Piper a PM question, and when
  Piper floors for lack of context (no visibility into your projects, sprint, or
  todos), gather exactly what it said it's missing — starting with your GitHub
  issues — re-ask Piper enriched, and present a grounded answer with visible
  provenance. Use for "what should I focus on?"-style questions where Piper needs
  your current work to answer well. For a quick one-shot relay with no gathering,
  use ask-piper instead. Requires the local Piper server (python main.py, :8001).
---

# /piper-morgan:consult-piper

This skill is the **composed** counterpart to `ask-piper`. Where `ask-piper` is a thin primitive (relay
one question to the `ask_piper` MCP tool, show the answer), `consult-piper` orchestrates around that same
tool: it notices when Piper hits its floor for lack of context, **gathers exactly the gap Piper
declared**, re-asks Piper with that context, and synthesizes a grounded answer.

Governing principle: **honesty is the ground; your fluency is the finish.** The handoff is explicit and
provenance-tracked; you elaborate naturally around that honest spine — never fabricate, never launder
host-gathered data as Piper's own reasoning.

## Behavioral contract (read every time)

### 1. Ask Piper first
Call the `ask_piper` MCP tool with the user's question (verbatim or lightly cleaned). Read Piper's
response and its intent classification.

### 2. Did Piper floor for lack of context?
Detect a **missing-context floor**: Piper classified the request (e.g. PRIORITY / get_top_priority) but
its prose says it lacks the user's data — phrasings like *"I don't have visibility into your current
projects / sprint commitments / todo list"*, *"I'd need to understand what's on your plate"*, *"what
projects are you juggling?"*.

- **If NO floor** → just relay Piper's answer (same as ask-piper). You're done. Don't gather.
- **If floor** → continue to step 3.

> This prose-detection is a Stage-1 heuristic (inference), not a structured signal from Piper yet. That's
> deliberate — see the scope note. Because it's inference, step 3 makes your interpretation **visible and
> correctable** rather than silently acting on a guess.

### 3. State your interpretation of the gap — visibly, correctably
Before gathering, tell the user what you think Piper needs and where you'll get it. E.g.:

> "Piper floored — it said it doesn't have visibility into your current projects and priorities. I'm
> reading that as: pull your open GitHub issues. (Tell me if that's not what it meant.)"

Keep it one or two sentences. The point is honesty: you're showing your read of Piper's gap, not
pretending to know it exactly.

### 4. Gather exactly that gap (GitHub, for now)
Pull the user's current open work from GitHub — targeted to the declared gap, not a fishing trip:
- **Prefer a GitHub MCP tool** if the host has one connected.
- **Otherwise fall back to the `gh` CLI** (the host has shell access): e.g.
  `gh issue list --repo <user's active repo> -s open -L 15 --json number,title,labels,assignees`.
  A "priority slice" (open issues, maybe filtered to assigned / high-priority) is plenty — don't dump
  hundreds of issues.
- If you don't know the user's active repo, ask (one question), don't guess.

### 5. Re-ask Piper, enriched
Call `ask_piper` again with the original question **plus** the gathered context folded into the message:

> "Here's my current open work: [concise list of the gathered issues]. Given that, what should I focus
> on today?"

Now Piper has what it floored for, and can give a grounded answer.

### 6. Present with visible provenance
Show the user Piper's enriched answer. Make clear **what came from where**:
- what **Piper** reasoned/recommended,
- what **you gathered** from GitHub and handed it,
- any synthesis **you** added on top.

Don't blur these. The user should always be able to see that the grounding came from their own GitHub
data via the host, and the prioritization reasoning came from Piper.

### 7. No silent failures (throughout)
- Honor `ask_piper`'s failure tags (`SERVER-DOWN`, `PIPER-INTERNAL-ERROR`, `TIMEOUT`, etc.) — relay them
  plainly, don't fabricate a Piper answer.
- If the **GitHub gather fails** (auth, no repo, MCP error), say so plainly and still relay Piper's
  original un-enriched answer. A failed enrichment degrades to a bare ask, honestly — it never invents
  context.

## Scope (read before editing)

This is a **Stage-1 probe** of the host-enriches-Piper-at-the-floor payoff loop:
- **GitHub-only** gathering for now. Calendar / Notion / Gmail / Slack are later increments — do NOT add
  them here yet.
- **Inference-stage**: gap detected from Piper's prose, not a structured "needed-but-lacked" signal.
  Stage 2 (Piper emits structured missing-context; consumes its own connected GitHub directly — see
  product issue #1155) supersedes the prose heuristic later.
- **Provenance always visible**: the whole point is honesty. Never present host-gathered data as Piper's.
- Built on the **`ask_piper` MCP tool** (shared with `ask-piper`); this skill adds orchestration, not a
  new tool.

Name is a probe-stage working name; expect refactor as we learn what this skill really is.
