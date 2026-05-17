# Subagent-2: PM Extraction Analysis — Distinctive Features → Plugin-Layer Mapping

**Author:** research subagent
**Date:** 2026-05-16
**For:** PA, informing the BYOC PoC build pass
**Sources:** Subagent-1 study (2026-05-16); ADR-054, ADR-060, ADR-061;
`composting-learning-architecture.md`; `methodology-27-TYPE-2-DREAMING-ANXIETY-DREAMS.md`;
`docs/internal/design/mux/` (objects-catalog, insight-surfacing-rules, provenance-display-patterns,
trust-learning-access-rules); `PDR-005 v0.3`; `anthropic-dreams-research-findings-2026-05-12.md`;
`five-layer-context-mapping.md`; PA cross-pollination scan (2026-05-10);
`piper-morgan-glossary-v1.1.md`.

Frame: per PM ratification, the canonical surface is **Claude Code** (plugin format shared
with Cowork, so Cowork support is mostly free); CMA cookbook + MCPB/Skill bundle for Claude
Chat as secondary/tertiary. The architectural prior is **claude-for-legal** (calibration-heavy:
thin skills over rich config + cold-start + shared profile), not the PM plugin (generic prompt
library with MCP shopping cart).

---

## TL;DR

1. PM's distinctiveness is **not** the PM-skill catalog (write-spec, sprint-planning, etc.);
   it is the **post-experience layer** — composting → Type 1 + Type 2 dreaming → InsightJournal
   → trust-graduated surfacing → object lifecycle (especially COMPOSTED) — plus the **boundary
   discipline** (LLM-touch four-element principle, redirect-context handoff, no-silent-failures,
   provenance tagging) that wraps everything.
2. Most distinctive value **does not naturally live in skills**. It lives in a per-user writable
   store (the InsightJournal), and accessing it requires *runtime state Claude Code does not
   provide as a primitive*. The plugin shape forces a choice: either fold state into a CLAUDE.md
   config file (legal pattern, file-only), or pin to a PM-API endpoint upstream (real DB/dreams
   pipeline), or accept a per-session in-memory degradation.
3. Floor-first routing (ADR-060) and the boundary enforcer (ADR-061) **invert** in the plugin
   world. Claude Code *is* the floor — there's no PM-controlled prompt path the user crosses
   first. Boundary enforcement at the input side becomes a skill-prefix prompt convention
   (acknowledged, not architecturally enforced); output-side filtering largely vanishes.
4. The PoC should pick a small distinctive feature set that **stresses the layering question**:
   `cold-start-as-founder-profile` + `insight-journal-as-config-file` + `composting-via-dreams-mcp`.
   Three features that together exercise (a) the writable user-owned config pattern, (b) where
   state lives, (c) whether Anthropic's Dreams API can stand in for PM's composting pipeline at
   the substrate layer.
5. The tension PA wants named: **PM's distinctive value lives in the spiral lifecycle** (each
   composting cycle deepens what Piper knows about *this user*). A per-session Claude Code plugin
   has no spiral. Either the spiral is held upstream (PM-API), or it's flattened into a config
   file the cold-start interview maintains by hand, or PM accepts that "the plugin Piper" is a
   diminished variant that doesn't actually compost — the spiral lives only in the canonical
   Piper service the plugin can call into.

---

## Q1. Inventory of distinctive PM features

I focused on what could **only** be Piper, not generic PM-assistant. The PM-skill list
(write-spec, sprint-planning, competitive-brief, etc.) is roughly the same surface that
ships in Anthropic's `product-management` plugin — generic and commodity. I skip those.

### A. Memory + cognition layer

| Feature | What's distinctive |
|---|---|
| **Composting (8th lifecycle stage)** | "Nothing disappears, it transforms." Deprecated objects decompose into patterns/insights/corrections/preferences. Triggered by AGE / IRRELEVANCE / MANUAL / SCHEDULED / CONTRADICTION. Five distinct triggers with priority order. |
| **Type 1 (filing) dreaming** | Past-looking consolidation. PM-architecture-spec'd; substrate-decision per CEO 2026-05-12 is "build own with Anthropic Dreams as reference, not substrate." |
| **Type 2 (anxiety) dreaming** | Forward-looking threat rehearsal. **No external equivalent surveyed** (Janus Apr 12, validated post-Anthropic May 6 release). Named, not yet specified. PM is claiming this publicly per CIO methodology-27 (filed 2026-05-15). |
| **Unihemispheric extension** | Partial-rotating consolidation cycles ("dolphin model"). PM-distinctive orchestration shape. Discussed Jan 11; not specified. |
| **Spiral lifecycle** | Each composting cycle has `spiral_depth`; each iteration carries learnings forward. The cycle is not a loop but a deepening helix. |
| **Cross-session memory (ADR-054)** | Three-layer model: 24-hour conversational window / all-time user history / composted learning. With privacy mode (per-session opt-out from memory + learning). |
| **Greeting context (PDR-001/002)** | Seven distinct conditions (SAME_DAY_RECENT, NEXT_DAY_ACTIVE, WEEK_GAP, MONTH_GAP, PREVIOUS_TRIVIAL, PREVIOUS_NEGATIVE, FIRST_SESSION) drive context-appropriate openers. |

### B. Object model + lifecycle

| Feature | What's distinctive |
|---|---|
| **8-stage lifecycle on every Hard Object** | EMERGENT → DERIVED → NOTICED → PROPOSED → RATIFIED → DEPRECATED → ARCHIVED → COMPOSTED. Six PM Hard Objects already carry `lifecycle_state` columns. |
| **Soft-vs-Hard distinction** | Hard = DB-persistent with identity; Soft = computed/transient. ~15 Hard, ~10+ Soft. The distinction is load-bearing for "what gets composted." |
| **NATIVE vs FEDERATED ownership (ADR-045)** | 13 NATIVE objects (Piper creates and owns) vs 2 FEDERATED (windows into external systems — Repository, Place). Plus an implied SYNTHETIC tier (reasoning-constructed). |
| **Entity / Moment / Place / Situation grammar** | Conceptual substrate; PlaceType distinguishes `InteractionSpace` (where user↔Piper happens) from `PlaceType` (where Piper observes federated data). |
| **COMPOSTED-state UX** | UI/conceptual treatment of objects in COMPOSTED stage — what user sees when reviewing the journal. Distinct from ARCHIVED. |

### C. Ethics + boundary enforcement (ADR-061 v1.0 + v1.1)

| Feature | What's distinctive |
|---|---|
| **Four-element LLM-touch principle** | Permissive input + schema validation at consumption + safe-fallback + audit envelope. **Generalized to ~23 surfaces** under #1016. |
| **Two-layer detector (literal-trigger + semantic)** | Substring fast-path (~10ms) + LLM-classifier slow-path (~2-4s) with confidence tiers (≥0.85 block / 0.6-0.85 ambiguous / <0.6 pass). LRU cache. |
| **Floor-as-de-facto-ethics-layer** | The conversational floor LLM handles naturally-phrased input that misses both detectors. Architectural acknowledgment of implicit ethics work. |
| **redirect_context typed handoff** | Category-only, audit-safe by construction, never user content. Canonical pattern for layer-to-layer enforcement-voice handoff. |
| **Output filter (#1017)** | `LLMClient.complete()` decorator with profile dispatch by `task_type`, three-tier detection (PII regex + boundary-on-outputs + deferred), severity→action matrix with regenerate-on-violation, hash-only audit invariant (Pattern-071 candidate). |
| **Floor-first routing (ADR-060)** | LLM is the default response path; structured handlers are *enhancements*, not the capability surface. Three-path: fast (deterministic, narrow), action (side effects), floor (default). |

### D. Trust + surfacing

| Feature | What's distinctive |
|---|---|
| **Four-stage trust gradient** | NEW → BUILDING → ESTABLISHED → TRUSTED. Gates *what learning surfaces*, not what runs. |
| **Insight surfacing rules (D4 mux spec)** | Three modes (Pull / Passive / Push); Push requires Stage 3+ AND confidence ≥0.75 AND contextual relevance AND ≥24h since last push AND user not in focus. Contradiction-discovery can override timing. |
| **Provenance display ("colleague test")** | Cite when asked / surprising / uncertain / contradicting / high-stakes; don't over-explain natural application. |
| **Anti-flattening discipline** | Composting must be transformation, not deletion. Moments must not become tasks. Filed as named anti-pattern. |

### E. InsightJournal as durable structure

| Feature | What's distinctive |
|---|---|
| **InsightJournal** | Per-user repository of learnings, distinct from session journal (audit log) and conversation history. Entries carry: type (Pattern / Insight / Correction / Preference), confidence, derived-from references, trust-level-required, visibility (pull / passive / push), framing string. |
| **Confidence-tier behavior** | Predictive Pattern >0.8 creates Predicted Moment; Strong Preference >0.85 sets default; Correction >0.75 updates affected objects; Insight Cluster of 3+ creates Synthesized Rule. |
| **Confirmation loop** | High-impact learnings prompt user; confirmed → boost confidence; corrected → new learning entry; rejected → confidence×0.5. |

### F. Multi-source synthesis + provenance discipline

| Feature | What's distinctive |
|---|---|
| **Five-layer context model (PA Mar 31 mapping)** | L1 kit briefing / L2 project instructions / L3 project memory / L4 channel addendum / L5 entity prompt. PM's L4 (in-memory dict, dies on restart) is the named critical gap. |
| **Context assembler (ADR-060)** | Per-intent `gather_context()` functions returning structured data for floor injection; declarative + fail-graceful + cached. |
| **Mailbox/cohort coordination patterns** | File-based async messaging (`mailboxes/<role>/{inbox,read,sent}/`); 13 role directories; per-memo commit-and-push norm; mailbox writes always to main; check-branch hook enforcement. Not user-facing — agent-internal — but a load-bearing coordination shape that has no equivalent in plugin land. |
| **No silent failures** | Absence must be signaled (null/denial/empty/fail explicitly surfaced). Both a methodology and a UX rule. Sibling of legal-plugin "provenance tagging" but with stronger surfacing claim. |
| **Serial decisions (not batched)** | One salient question at a time. Inverts the legal-plugin cold-start interview's "ask 2-3 questions at once" pattern. |

### G. PM-internal-only (won't translate to plugin form)

| Feature | Why it stays internal |
|---|---|
| Multi-agent coordination (13 roles, mailbox, omnibus, session logs, audit cascades) | Plugin = single-user surface; no role plurality. |
| Sign-off discipline, branch/worktree/merge-keeper | Git-discipline for a multi-agent dev team; doesn't ship to end users. |
| ADR/PDR/methodology infrastructure | Internal artifact graph; could be referenced *by* a plugin but isn't *of* the plugin. |
| Anti-pattern catalog (Patterns 045 / 062 / 064 / 070 / 071) | Same — internal architectural discipline. |
| Inchworm, 75% pattern, cathedral building | Internal methodology discipline. |

---

## Q2. Candidate layer mapping (legal-plugin slot vocabulary)

Slot vocabulary from subagent-1: `plugin.json` (metadata) / `.mcp.json` (MCP servers) /
`skills/<name>/SKILL.md` (prompt body) / `agents/<name>.md` (subagent preset) /
`hooks/hooks.json` / **plugin `CLAUDE.md` template** (cold-start writes to
`~/.claude/plugins/config/piper-morgan/<plugin>/CLAUDE.md`; shared profile one level up) /
`references/<shared>.md` / `bin/`. Plus implied: **pinned to PM-API endpoint upstream**.

| # | Feature | Candidate slot(s) | Rationale |
|---|---|---|---|
| **A.1** | Composting pipeline | **MCP server (preferred)** with optional fallback to **PM-API endpoint upstream**. CompostBin/Decomposer/LearningExtractor run remote-side. Plugin skills call `mcp__piper__compost(...)`. | The pipeline is stateful, long-running, and shapes user-owned data. It cannot live in a per-session prompt. Whether the MCP server *contains* the pipeline or *wraps* a PM-API call is a downstream choice. |
| **A.2** | Type 1 dreaming | **MCP tool wrapping Anthropic Dreams API** (`mcp__piper__dream_type1`), OR upstream PM-API endpoint that calls Dreams. | Anthropic's Dreams API is the natural substrate per the May 12 findings. CEO directive says "build own with Dreams as reference"; for a Claude-Code-canonical surface this is more "delegate where viable." |
| **A.3** | Type 2 (anxiety) dreaming | **MCP tool** (`mcp__piper__dream_type2`), prompt-engineered atop Anthropic Dreams with adversarial instructions. **Or PM-API** if PM ships its own Type 2 pipeline. | PA's research findings note Dreams API could be used with Type 2 instructions ("identify failure modes…") to produce a different output store. Worth probing in PoC. PM-distinctive concept; preserved IP. |
| **A.4** | Unihemispheric orchestration | **PM-API endpoint upstream**, OR **agent (subagent)** that handles scheduling. | Cross-session orchestration logic doesn't live in a stateless plugin. Could be a CMA cookbook (headless) that calls Dreams on a partial-rotation schedule. |
| **A.5** | Spiral lifecycle | **PM-API state** primarily (`spiral_depth` is a DB column). Plugin observes via MCP read tools. | The spiral is what makes Piper *the* Piper across time; it lives where the data does. |
| **A.6** | Cross-session memory (ADR-054 Layers 1-2) | **Skill prompt convention + plugin `CLAUDE.md` config** (Layer 1 — recent topics inline) for the lightweight version; **MCP server** for the full version (Layer 2 — full searchable history). | Legal-plugin pattern: skills read from config CLAUDE.md before doing work. Equivalent here: skill prefix `!`cat ~/.claude/plugins/config/piper-morgan/piper/recent-window.md` for Layer 1; MCP `mcp__piper__search_history` for Layer 2. |
| **A.7** | Greeting context | **Skill** (`/piper:greet`) with `!`cmd injection of last-session summary + a small decision tree in the body for the seven conditions. | Pure prompt logic; no state primitive needed beyond a small local file the previous session wrote. |
| **B.1** | 8-stage lifecycle + soft/hard | **Plugin `CLAUDE.md` template** documents the model; **MCP tools** for queries (`mcp__piper__get_object_state`, `mcp__piper__transition`); object state lives in **PM-API or MCP server-side storage**. | Lifecycle state isn't prompt-shaped — it's data shape. Plugin documents the vocabulary; server holds it. |
| **B.2** | NATIVE / FEDERATED ownership | **MCP server** (and downstream tool surface for the federated bits — Github/Slack/etc. via existing connectors). | FEDERATED objects naturally live in `.mcp.json` connector entries; NATIVE objects in PM's own MCP server. |
| **B.3** | Entity / Moment / Place / Situation grammar | **`references/grammar.md`** loaded by every skill. Optionally **plugin `CLAUDE.md`** so it survives plugin updates. | This is shared vocabulary; reference-file pattern from legal plugins fits. (Note: subagent-1 flagged that `references/` may not actually ship inside plugin dirs in legal-plugin practice — a known gap. Worth verifying in PoC.) |
| **B.4** | COMPOSTED-state UX | **Skill** (`/piper:show-compost`) that reads InsightJournal + renders confidence-tiered output per the D4 spec. | Pure rendering; the data comes from MCP. |
| **C.1** | Four-element LLM-touch principle (inputs) | **Skill prompt convention + reference doc** (`references/llm-touch-discipline.md`). | Claude Code IS the LLM consuming user input — there's no PM-controlled enforcement gate the input crosses first. The principle becomes prompt-discipline ("when handling user input within this skill, validate at consumption…"). Legal plugins enforce by prompt rather than by hook; same shape applies here. |
| **C.2** | Two-layer detector | **MCP tool** (`mcp__piper__check_boundary`) that skills can call when handling sensitive input; OR **agent** subagent. | If you want the detector at every input, it'd need to be wired as a `PreToolUse` hook (deterministic). But ADR-061's whole architecture acknowledges floor LLM as de-facto layer — Claude Code's floor competence may make this redundant in practice. **Worth probing in PoC.** |
| **C.3** | Floor-as-de-facto-ethics-layer | **N/A — Claude Code IS the floor.** Acknowledgement-only; nothing to ship. | This is the inversion: in PM's product the floor is a PM-controlled prompt path inside `conversational_floor.py`. In Claude Code the floor is Claude itself, with its own ethics training. PM's specific ethics calibration (redirect_context, denial_mode framing) doesn't have a place to live unless wrapped in a skill or subagent. |
| **C.4** | redirect_context typed handoff | **Skill output convention** + audit log via MCP write tool. | The pattern (typed minimal handoff, no raw content) transfers directly; the *infrastructure* (Pydantic schema, audit envelope) becomes prompt-and-MCP. |
| **C.5** | Output filter (#1017) | **Hook** (`PostToolUse` on text-producing tools), OR **subagent that proxies all output**. | Claude Code doesn't expose a clean "filter every LLM completion" hook the way PM's `LLMClient.complete()` decorator does — Claude is the LLM. The closest analog is `PostToolUse` for tool outputs, which is much narrower than what #1017 covers. **This may be the largest architectural compromise.** |
| **C.6** | Floor-first routing (ADR-060) | **N/A — Claude Code's whole architecture IS floor-first.** Plugins are enhancements that wire skills/MCP/agents around Claude's default conversational competence. | Convergence with PM's own choice; no migration work. |
| **D.1** | Trust gradient | **Plugin `CLAUDE.md` config** (cold-start interview populates `trust_stage: <NEW|BUILDING|ESTABLISHED|TRUSTED>`); **skills check** the value before pushing. | Static-config version of the dynamic gradient. The *computation* of trust (via TrustEvents) doesn't translate to per-session; the *gate* does. |
| **D.2** | Insight surfacing rules (D4) | **Skill body** for the decision tree; **MCP tool** (`mcp__piper__should_surface`) optionally callable for the timing check. | The "5 prerequisites for Push" decision tree is a small enough prompt to live in skill body. The "≥24h since last push" check needs persistent state — MCP-side. |
| **D.3** | Provenance display (colleague test) | **Skill prompt convention + `references/provenance.md`**. | Pure prompt discipline; reference-file pattern. |
| **D.4** | Anti-flattening | **`references/anti-flattening.md`** + skill prompt convention. | Reminder pattern; no infrastructure. |
| **E.1** | InsightJournal | **MCP server resource** (`mcp__piper__journal_read` + `mcp__piper__journal_write`); **OR** Anthropic Memory Store accessed via the Anthropic Dreams pathway; **OR** flat-file in plugin config (`~/.claude/plugins/config/piper-morgan/piper/journal.md`). | Three credible options, each with tradeoffs. PoC should pick one and surface what the other two would require. The flat-file option is closest to legal-plugin shape; the MCP option closest to PM's current product; the Anthropic Memory Store option is the Anthropic-native shape. |
| **E.2** | Confidence-tier behavior | **Inside the MCP server / PM-API**, surfaced via tool return values. | The confidence-tier→emergent-object mapping is server-side logic. |
| **E.3** | Confirmation loop | **Skill body** (the prompt asks the user); **MCP write** for the confidence update. | Pure conversational pattern; storage via tool. |
| **F.1** | Five-layer context model | **Plugin documentation + reference doc.** The plugin shape inherently expresses the five layers: `.mcp.json` ≈ L1, plugin CLAUDE.md ≈ L2, config + user data ≈ L3, session ≈ L4, founder-profile ≈ L5. | The mapping isn't 1:1 but is closer than you'd expect; subagent-1 noted PM's L4 (the critical gap) is exactly what Claude Code's per-session context does well, by accident. |
| **F.2** | Context assembler | **Skill `!`cmd injection** for the cheap reads (briefing, calendar, mailbox); **MCP tool** for the expensive reads (project list, github metadata). | Legal-plugin pattern: skills inject context at top via `!`cmd; Piper does the same. |
| **F.3** | Mailbox/cohort coordination | **PM-internal-only.** Doesn't translate to plugin form (single-user surface). | If multi-agent comes back via something like CMA orchestrator/worker cookbook, it'd live there. Out of scope. |
| **F.4** | No silent failures | **Skill prompt convention + `references/no-silent-failures.md`**. | Prompt discipline; reference pattern. |
| **F.5** | Serial decisions | **Plugin `CLAUDE.md` + cold-start interview override.** Specifically inverts the legal cold-start pattern (which batches 2-3 questions). | This is a load-bearing voice rule; if the cold-start interview asks five questions at once, it violates xian's stated rule. Need to inherit legal's structure but invert its pacing. |

---

## Q3. Per-feature: confidence, extraction shape, load-bearing-ness, translatability

Compact table. **Confidence** = how sure am I about the mapping. **Extraction** = lift / refactor /
rebuild. **Load-bearing** = essential to "this is Piper, not generic PM-assistant"? **Translatable** =
can it exist in plugin form at all?

| # | Feature | Conf | Extraction | Load-bearing | Translatable |
|---|---|---|---|---|---|
| A.1 | Composting pipeline | med | rebuild (per-session degradation) or pin to PM-API | YES | partial — only if pinned upstream |
| A.2 | Type 1 dreaming | med | refactor (wrap Anthropic Dreams) | yes | yes |
| A.3 | Type 2 dreaming | **low** | rebuild (prompt engineering on Dreams API; unproven) | YES (PM IP) | unknown — needs PoC |
| A.4 | Unihemispheric | low | rebuild as scheduling logic | medium | only if CMA cookbook or PM-API holds the schedule |
| A.5 | Spiral lifecycle | high | pin to PM-API (it's a DB column) | YES | only via upstream |
| A.6 | Cross-session memory (L1-2) | med | refactor (legal-plugin config pattern + MCP fallback) | yes | yes, with degradation |
| A.7 | Greeting context | high | lift (small skill + injected file) | medium | yes |
| B.1 | 8-stage lifecycle | high | documentation lift + MCP tools | yes | yes |
| B.2 | NATIVE/FEDERATED | high | lift (already maps onto MCP shopping cart) | medium | yes |
| B.3 | Entity/Moment/Place grammar | high | lift to reference file | medium | yes |
| B.4 | COMPOSTED-state UX | med | rebuild as skill (renders journal data) | yes | yes |
| C.1 | LLM-touch principle (inputs) | high | lift as prompt convention | YES (discipline) | yes, weakened |
| C.2 | Two-layer detector | low | rebuild as MCP tool or accept floor competence | medium | unclear — may be redundant given Claude floor |
| C.3 | Floor-as-de-facto-ethics-layer | high | **n/a (Claude IS the floor)** | YES (acknowledged) | implicit, free |
| C.4 | redirect_context handoff | high | lift as skill convention | yes | yes |
| C.5 | Output filter (#1017) | **low** | rebuild as PostToolUse hook (much narrower) | YES (ethics) | **mostly NO** — major compromise |
| C.6 | Floor-first routing | high | n/a — convergent | YES | free convergence |
| D.1 | Trust gradient | high | refactor (dynamic→static via cold-start) | YES | yes, with degradation (no learning loop) |
| D.2 | Insight surfacing rules | med | refactor (skill body + MCP timing check) | YES | yes |
| D.3 | Provenance display | high | lift as prompt convention | YES (discipline) | yes |
| D.4 | Anti-flattening | high | lift as reference file | yes | yes |
| E.1 | InsightJournal | med | three credible substrates (MCP / Anthropic memory store / flat file); PoC picks one | YES | yes — substrate choice is the question |
| E.2 | Confidence-tier behavior | med | rebuild server-side; surface via tool returns | yes | yes if E.1 is upstream |
| E.3 | Confirmation loop | high | lift as skill body + MCP write | yes | yes |
| F.1 | Five-layer context model | high | n/a — implicit in plugin shape | n/a (analytical) | implicit |
| F.2 | Context assembler | high | lift as skill `!`cmd injection | yes | yes |
| F.3 | Mailbox/cohort | high | **PM-internal-only** | n/a | NO (single-user surface) |
| F.4 | No silent failures | high | lift as prompt convention | YES (discipline) | yes |
| F.5 | Serial decisions | high | lift to plugin CLAUDE.md; **invert** legal's batching cold-start | YES (voice rule) | yes |

**Patterns in the table:**

- **Disciplines lift cleanly.** C.1, C.4, D.3, D.4, F.4, F.5 — the load-bearing prompt-discipline
  features all translate to skill conventions + reference files. This is the legal-plugin shape's
  strength and matches the calibration-heavy frame.
- **State doesn't lift.** A.1, A.5, D.1, E.1, E.2 — every load-bearing stateful feature needs
  either PM-API upstream or substantive substrate compromise.
- **The boundary enforcer (C.5) is the largest single architectural casualty.** Claude Code doesn't
  expose a clean hook for filtering its own outputs the way PM's `LLMClient.complete()` decorator
  does. The four-element principle on the *output* side has to be re-architected or accepted as
  out-of-scope for the plugin variant.

---

## Q4. "What lives where" tensions the PoC build pass will surface

PA asked these be named, not pre-resolved.

### T1. Where does conversation state live?

PM's product holds it in `ConversationContext` (in-memory dict, the critical L4 gap from the
five-layer mapping). In a plugin, three options:

- **(a) Skill context** — the per-session context Claude Code holds; dies on session end.
- **(b) MCP server** — PM-controlled, persistent, but every read is a round-trip and adds
  latency to floor-style conversational flow.
- **(c) PM-API upstream** — fully persistent and matches PM's product, but requires PM running
  somewhere reachable from the user's Claude Code session.

The legal plugins implicitly chose **(a)+(small (b))**: per-matter workspaces are in the config
file Claude Code rewrites; ephemeral session state is per-session. PM might want **(a)+(c)** for
the spiral lifecycle to actually work. PoC should pick one and demonstrate what (a) loses without
the others.

### T2. How does composting work in a per-session model?

PM's composting runs in quiet hours (default 2-5 AM). A Claude Code session in front of a user
is the *opposite* of quiet hours; it's the foreground. Three resolutions:

- **(a) Composting doesn't run from the plugin.** It runs out-of-band (PM-API scheduler or CMA
  cookbook on cron). The plugin only *reads* the InsightJournal.
- **(b) Composting runs at session-end** as a `Stop` hook firing an Anthropic Dreams call.
  Inverts the quiet-hours framing but matches what the user actually does.
- **(c) Composting runs on a `SessionStart` hook** at the *start* of the next session, before
  the greeting. ("Having had some time to reflect…" maps cleanly.)

The greeting framing favors (c). Performance favors (a) — async-batch is what Dreams is for.
Substrate-aligned with Anthropic Dreams favors a mix. PoC should pick one and surface what the
others would look like.

### T3. Where does the floor live when Claude IS the model?

In PM's product the floor is a PM-controlled system prompt with the four-element discipline
baked in. In Claude Code, the floor is Claude's general competence with PM's plugin skills
indexed for triggering. PM's *specific* floor disciplines — redirect_context, denial_mode,
fabrication guardrails (ADR-060 Apr 11 amendment) — don't have a clean place to live. Options:

- **(a) Accept the loss.** Claude's general competence is the de-facto floor; PM's specific
  calibration is best-effort via reference docs + skill descriptions.
- **(b) Insert a "Piper voice" agent (subagent) as the conversational orchestrator.** Every
  user message routes through it (via skill-with-`context: fork`). High overhead.
- **(c) A `/piper:respond` skill the user invokes whenever they want Piper-shaped output**
  rather than vanilla Claude. Forces explicit invocation.

This is one of the genuinely hard architectural questions. (a) is closest to legal-plugin shape;
(b) is closest to PM's product behavior; (c) is the most honest about what the plugin is.

### T4. Where does the audit trail go?

PM's product writes to `ethics_audit_log` (PostgreSQL); the #1017 hash-only invariant matters
because audit logs as raw content become Pattern-071 attack surface. In a plugin:

- **(a) MCP server write** — PM-controlled, durable, but adds a tool call to every flagged
  interaction. The hash-only invariant is server-enforceable.
- **(b) Local file** in plugin config — survives updates, user-owned, **but the hash-only
  invariant becomes prompt-discipline, not schema-discipline** (and per ADR-061 v1.1 reasoning,
  this is exactly the wrong direction — schema-enforced is the load-bearing claim).
- **(c) No audit trail** — the plugin variant accepts diminished accountability.

PoC should at minimum surface (b)'s prompt-vs-schema regression so PM understands the tradeoff.

### T5. How does the spiral deepen without per-user state across sessions?

ADR-045's `spiral_depth` is a DB integer that increments each composting cycle. In a plugin,
unless state is held upstream, "the second cycle has spiral_depth: 2" can't be expressed.
Either:

- **(a) Spiral lives upstream** (PM-API holds it; plugin reads it).
- **(b) Spiral becomes a config-file scalar** the cold-start writes and skills increment by
  appending to the file (legal-plugin pattern; brittle).
- **(c) Spiral is faked** — the plugin claims first-cycle behavior every session.

This is the cleanest concrete case of "the spiral is what makes Piper *the* Piper" colliding
with the per-session shape of the plugin. (c) is the honest degradation; (a) is the honest
full-fidelity; (b) is the compromise.

### T6. How does cold-start NOT batch its questions?

xian's stated rule is one decision at a time. The legal-plugin cold-start interview ships
2-15 minutes of questions, batched 2-3 at a time. For Piper, the cold-start would need to
invert that — one question, write that section, ask the next. Means cold-start is longer in
wall-clock (more turn-taking) but lower in cognitive load. Worth being explicit about in
the skill body.

### T7. How does federation work?

PM's FEDERATED objects (Repository, Place) are windows into external systems. Plugin shape
naturally maps these to `.mcp.json` connectors (Slack, Notion, Github, Drive, etc.). Tension:
PM's PlaceConfidence (HIGH/MEDIUM/LOW) display-mode logic lives in PM's UI, not in MCP
returns. Plugin variant either (a) re-derives confidence per call (expensive), (b) inherits
whatever the MCP server returns (loses Piper's confidence-tier discipline), or (c) holds the
confidence-tiering in a wrapper skill.

### T8. Output filtering (#1017) — most acute architectural casualty

PM's product wraps `LLMClient.complete()` in a decorator that runs every model output through
the OutputFilter. In Claude Code, the LLM IS Claude; PM doesn't own the inference call. The
closest analogs are:

- **PostToolUse hook** on text-producing tools — narrower scope (only tool outputs, not
  conversational replies).
- **Subagent proxy** — fork every response through a subagent that filters. Doubles latency
  + cost; unclear how it interacts with Claude Code's conversational loop.
- **Accept the loss** for the plugin variant and assert that the upstream OutputFilter only
  applies when calls flow through PM-API.

This is the case where "the plugin Piper" is most visibly a diminished variant. Worth flagging
loudly so PM understands the tradeoff.

---

## Q5. Minimum-viable PoC scope

PA's framing: pick 2-3 distinctive features whose **combination** demonstrates the layering
question, leave the rest as "would extend similarly."

### Proposed: the "calibration + memory + reflection" triangle

**Feature 1 — `cold-start-as-founder-profile` (skill + plugin CLAUDE.md template)**
- Direct fork of legal `cold-start-interview` shape, with two distinctive PM inversions:
  - **Serial decisions** (one question at a time, not batched 2-3)
  - **Founder-profile** vocabulary (anti-sycophancy, anti-silent-failure, serial-decisions,
    PM-CC-on-memo routing, sibling-projects, write-now-proceed-when-aligned, etc. —
    literally lift PM's MEMORY.md memo set as the cold-start output schema)
- Writes to `~/.claude/plugins/config/piper-morgan/piper/founder-profile.md` + shared
  `~/.claude/plugins/config/piper-morgan/company-profile.md`.
- **Exercises**: T6 (serial cold-start inversion), the writable per-user config pattern,
  the shared profile pattern.

**Feature 2 — `insight-journal-flat-file` (skill + reference + the file itself)**
- Implements the InsightJournal as a flat markdown file at
  `~/.claude/plugins/config/piper-morgan/piper/insight-journal.md`.
- `/piper:journal` skill reads + renders per D4 surfacing rules (Pull mode minimum;
  Passive mode if the file is structured enough to nav).
- `/piper:reflect` skill appends new insights (the user-facing write path).
- **Exercises**: T1 (state location), T4 (audit-trail substrate), E.1 (substrate choice),
  E.3 (confirmation loop in prompt form).
- **Substrate choice resolved as "flat file" for the PoC**, with explicit notes on what
  MCP server / Anthropic Memory Store would change. Cheapest substrate; surfaces the most
  tradeoffs.

**Feature 3 — `composting-via-dreams-mcp` (MCP tool wrapping Anthropic Dreams)**
- Single MCP tool: `mcp__piper__compost(scope='last-N-sessions')`.
- Calls Anthropic Dreams API with a Type 1 (filing) instructions string steered toward
  PM's composting vocabulary ("merge duplicates; extract preference patterns; surface
  corrections to founder-profile.md; produce insight-journal-delta.md").
- Result: a new memory store with the consolidation output, **plus** an adopt-gate step
  the user runs to merge into the InsightJournal flat file (Feature 2).
- **Exercises**: T2 (composting trigger placement — proposed: `SessionStart` hook for the
  greeting framing), A.2 (delegation viability), the input/output store + review-then-adopt
  pattern from AC-3.
- **Plus a stretch goal**: a second `mcp__piper__dream_type2` tool with adversarial
  instructions ("identify failure modes…"). Even a low-fidelity Type 2 PoC produces signal
  about whether prompt-engineering atop Dreams is viable as the Type 2 substrate.

### What this combination demonstrates

- **Feature 1 + Feature 2** together exercise the legal-plugin pattern of *cold-start writes
  config → every skill reads config → skills can also write back to user-owned files*. This is
  the "calibration-heavy thin-skills-over-rich-config" shape. If this works for Piper, the
  legal-plugin prior is validated for PM's calibration discipline.
- **Feature 2 + Feature 3** together exercise the harder question: can the InsightJournal
  (PM's distinctive memory shape) be reconstructed from (config file + Anthropic Dreams +
  adopt-gate)? If yes, Type 1 substrate delegation is real. If no, PM needs to own the
  composting pipeline (PM-API), and the plugin is fundamentally a thin client.
- **Feature 3 alone** stresses T2 (where composting runs) and T5 (does the spiral deepen?).
  The first run produces depth-1 output; a second run of `mcp__piper__compost` over a
  larger session set should produce visibly deeper insights — if it does, that's evidence
  the spiral *can* survive substrate delegation.
- **Feature 1 + Feature 2 + Feature 3** as a triangle exercises T1 (state location across
  all three substrate options), T3 (where the floor lives — answered implicitly: Claude is
  the floor; PM's voice is a thin overlay via the skills' prompt bodies), and T6 (serial
  cold-start).

### Explicitly OUT-of-scope (per "would extend similarly")

- **Output filter / #1017** — surface T8 as a memo finding, don't try to build it. The
  architectural casualty is the finding.
- **Two-layer boundary detector** — surface T8's cousin (T C.2): probe-test whether Claude's
  general floor competence is sufficient for PM's input-side ethics work. Memo, don't build.
- **Type 2 dreaming beyond the stretch goal** — stretch only.
- **Unihemispheric orchestration** — out-of-scope; CMA cookbook territory.
- **All the F.3-class internal coordination machinery** (mailboxes, sign-off discipline,
  branch worktree, merge-keeper sweep, audit cascade) — single-user plugin doesn't carry it.
- **The full PM-skill catalog** (write-spec, sprint-planning, etc.) — these are commodity per
  Anthropic's PM plugin; not what makes PM distinctive. A small handful (`/piper:greet`,
  `/piper:check-mailbox`, `/piper:close-issue-properly`) might be worth adding as the second
  build-pass to test extension, but not for the first PoC.

### Build sequencing within the PoC

1. **Plugin scaffold + `cold-start-as-founder-profile`** (Feature 1). One full end-to-end pass
   demonstrates the calibration-heavy shape works for PM. PM-gate.
2. **`insight-journal-flat-file`** (Feature 2). Adds the writable-by-Piper file pattern. PM-gate.
3. **`composting-via-dreams-mcp`** (Feature 3). Adds the substrate question. PM-gate.
4. **Optional stretch**: Type 2 probe + boundary-detector probe + output-filter (T8) memo.

If any step exceeds the build-less discipline, stop at the prior PM-gate and write findings.

---

## What I'm uncertain about

- **Whether MCP tools called from inside a Claude Code skill can hold conversational state
  the way PM's `ConversationContext` does.** Subagent-1 implies MCP servers are tool surfaces
  per turn, not stateful sessions. If true, T1 collapses harder than I've written it.
- **Whether Anthropic Dreams' Research Preview gating** (form-required access, beta headers,
  rate limits) makes Feature 3 viable as a same-week PoC, or whether the PoC needs to mock
  Dreams initially. Worth a PA check before subagent-3 dispatch.
- **Whether the InsightJournal-as-flat-file is structured enough for Passive mode browsing**
  (D4's organized-by-topic + recency-secondary display). Flat markdown can carry headings
  and confidence tags; whether Claude reading + rendering it can hit the D4 spec is unclear
  without trying.
- **How much PM-API exists today as a callable surface.** I assumed plugin skills could
  call into PM-API as a stretch option; if PM-API is currently a FastAPI server on localhost
  not exposed beyond xian's dev box, the "pin to PM-API" mappings in Q2 are aspirational.
  Worth a Lead Dev check.
- **Whether Claude Code's hook system supports `SessionStart` hooks** that can make API
  calls (for T2 option (c)). Subagent-1 lists `hooks/hooks.json` with PreToolUse / PostToolUse
  events; SessionStart wasn't enumerated. If absent, T2(c) is harder than I implied.
- **The CMA cookbook three-tier security model's relevance for headless Piper.** Subagent-1
  said it's overbuilt for PM's less-adversarial surface. If a Type 1 nightly composting
  cookbook is the right shape for substrate delegation, the security model might still
  apply (orchestrator with no Write, writer-leaf composts). Worth thinking about in PoC.
- **Whether the cold-start should be one skill or a sequence.** Legal's is one long skill
  (490 lines) that batches questions. If serial-decisions demands one question per skill
  invocation, the cold-start becomes 8-15 separate `/piper:cold-start-question-N` skills
  the user invokes in sequence — verbose. Or one long skill that does serial questioning
  via internal loop. PA + PM should call this.
- **Whether the redirect_context handoff is meaningful when there's no PM-controlled floor
  to hand off TO.** ADR-061 v1.0's pattern is enforcement-layer → voice-layer. In the plugin,
  the voice layer is Claude itself. Whether the typed-handoff discipline retains value as a
  prompt convention in this configuration is unclear without trying.

---

## What I deliberately did NOT do

- **I did not exhaustively inventory every PM feature.** Per the brief, I focused on what's
  distinctive vs commodity. The PM-skill catalog (write-spec, sprint-planning, etc.), routine
  CRUD on Projects/Todos/Features, FastAPI route inventory, infrastructure plumbing,
  test/CI/deploy machinery, and the bulk of internal coordination machinery are all skipped.
- **I did not pre-resolve the tensions in Q4.** PA asked them named, not solved. The PoC is
  where they get exercised.
- **I did not produce code or pseudocode.** This is an extraction-analysis memo, not a
  design spec.
- **I did not re-litigate the canonical-surface decision** (Claude Code per PM ratification).
  Took the framing as load-bearing input.
- **I did not validate the layer-mapping claims against the Anthropic plugin docs directly.**
  I relied on subagent-1's extraction. If there are mechanical errors in my mapping (e.g.,
  what SessionStart hooks support, what MCP tools can hold state), those are inherited from
  subagent-1 or from my reading of it.
- **I did not estimate PoC effort in hours.** That's a subagent-3 / Lead Dev call after
  PA + PM ratify scope.
- **I did not address the cookbook / CMA path in depth.** PM ratified Claude Code as
  canonical; CMA is secondary/tertiary. The Type 1 nightly-composting cookbook is mentioned
  but not designed. A follow-up memo could cover it if PM wants the headless story.
- **I did not address the MCPB+Skill bundle for Claude Chat.** Same reason — tertiary surface.
  Mechanically simpler than the plugin shape (no per-user CLAUDE.md config; bundle ships
  static); most Q3 features map worse there. Out of scope here.

---

*subagent-2 | 2026-05-16 | for PA*
