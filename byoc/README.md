# BYOC PoC — Plugin / MCP / Skills exploration

**Started**: 2026-05-16
**Plan**: `../../piper-morgan-product/dev/active/skunkworks-byoc-poc-plan-v0.2-2026-05-16.md`
**Status**: Step 0 — setup

## What this is

A rapid-experimentation proof-of-concept exploring how to express Piper Morgan's distinctive value as a mix of:

- **Anthropic plugin** (manifest layer)
- **MCP bundle** (Model Context Protocol server providing tools/resources)
- **Skills** (Anthropic's prompt-based capability augmentations)
- **PM API** (the upstream that handles uniquely-PM behavior)

The question this PoC aims to surface signal on: **"what lives where?"** — which pieces of Piper's value (composting, object models, ethics boundaries, trust graduation, Insight Journal, etc.) fit cleanly into which layer, and which need PM as upstream substrate.

This complements (does not duplicate) PDR-005 strategic BYOC work happening in the main repo with Architect, PPM, CXO leading.

## What this is NOT

- Not a production track
- Not gated on main-repo decisions
- Not committed to merge findings back unless we explicitly decide they're worth merging
- Not a single-shot deliverable — expect to iterate before producing viable signal

## Structure

- **`priors/`** — git submodules of Anthropic reference repos:
  - `claude-for-legal/` — architectural prior; fork target
  - `knowledge-work-plugins/` — comparison study (focus on `product-management/` subtree); pinned to `a0fda66`
- **`notes/`** — PA + subagent finding memos
- **`poc/`** — the actual experimental artifact
- **`tracker.md`** — daily status, subagent dispatch state, open questions, finding log

## Subagent work

This project uses subagents for execution under PA oversight. PA validates subagent output before propagating findings. Three formal PM gates (per the plan):

1. After PA synthesis of subagent 1 + 2 findings → PM ratifies PoC scope
2. After Step 4.b (first PM-distinctive feature expressed end-to-end) → PM reviews PoC behavior
3. End of project → PM reviews final state; decides leadership read-in / archive / extract findings

## Coordination with main-repo leadership

Light-touch three contact points (per plan):

- Heads-up to Architect pre-Step-0 (visibility only)
- Share PA synthesis post-Step-3 (flag-back if conflict with architectural commitments)
- Share PoC findings post-Step-4.b (real signal exists by then)
