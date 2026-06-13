---
name: ask-piper
description: >
  Relay a natural-language PM question to the user's locally-running Piper
  Morgan (via the ask_piper MCP tool) and surface Piper's own answer plus its
  intent classification. Use when the user wants *Piper's* take on a PM task —
  priorities, drafting, status, next steps — rather than a generic answer.
  Requires the local Piper Morgan server running (python main.py, port 8001).
---

# /piper-morgan:ask-piper

This skill is the thin bridge from the agent to **Piper Morgan's conscious-floor engine**, via the
`ask_piper` MCP tool the plugin provides. It is deliberately a **passthrough**: it hands the user's PM
request to Piper, then relays Piper's own response. Piper does the PM thinking; this skill just routes
the question and surfaces the answer faithfully.

## When to use

- The user explicitly wants **Piper's** view ("ask Piper…", "what would Piper say…", "check with Piper").
- The request is **PM-shaped** — priorities, drafting an issue/update, status, what-to-focus-on,
  next-step framing — the kind of thing Piper's conscious floor is built to handle.
- **Not** for general questions you (the host agent) can already answer directly. If the user just
  wants an answer and doesn't care that it comes from Piper, you don't need this skill.

## How to use (the passthrough contract)

1. **Call the tool**: `ask_piper(message=<the user's PM request>)`. Pass the request verbatim, or lightly
   cleaned for clarity — but **do not reinterpret or expand it**. Piper should classify the user's
   actual words, not your paraphrase.
2. **Relay Piper's response.** Show the user what Piper said. Don't rewrite it in your own voice — the
   point of asking Piper is to get *Piper's* answer.
3. **Optionally note how Piper understood the request — in PLAIN language.** Piper's response includes
   internal fields (category / action / confidence / floor_hit / context_keys). These are OUR
   architecture vocabulary — do NOT show them to the user verbatim. If useful, say in plain words "Piper
   read this as a priorities question" — but drop the field names. When in doubt, just relay Piper's
   answer; the classification is rarely what the user came for.
4. **No silent failures.** If `ask_piper` returns the "couldn't reach Piper" message (the local server
   isn't running), tell the user plainly: the local Piper server isn't up; start it with
   `python main.py` (port 8001), then retry. **Never fabricate a Piper answer** when the server is down.

## Scope guard (read before editing this skill)

This skill is a **bare passthrough** by design (rung 2 of the thin-PoC, locked 2026-06-04). It does
**NOT**:
- read the PM profile (`~/.claude/plugins/config/dinp/piper-morgan/CLAUDE.md`) to shape the request,
- adapt voice or enact the trust-gradient,
- gather context from other tools (Calendar, Notion, etc.) to enrich Piper when it hits its floor.

Those are **later rungs** (rung 3+: "host enriches Piper at the floor", and profile-aware voice). The
gate run showed the host *can* do that spontaneously — but folding it into this skill is scope creep.
Keep this skill thin; build the richer behavior as its own increment.

## Note

The meet-piper skill (the cold-start interview) is the setup step that populates the PM profile; this skill does not
depend on it for rung 2 (passthrough needs no profile). Profile-aware behavior arrives in a later rung.
