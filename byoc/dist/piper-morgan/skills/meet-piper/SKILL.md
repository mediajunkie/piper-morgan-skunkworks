---
name: meet-piper
description: >
  Setup and maintenance for the piper-morgan plugin's PM profile. On a fresh
  install it runs a serial, one-question-at-a-time cold-start interview to learn
  how you work as a PM — voice/posture rules, project portfolio, decision-making
  patterns, routing conventions. On a returning (already-configured) user it
  switches to maintenance mode: a compact, scoped update of just the sections
  that drifted, using a form where the surface offers one. Saves the PM profile
  (plus, on first install, the shared company profile) via the Piper MCP server's
  save_profile / save_company_profile tools, so it works on every surface (Claude
  Code AND Cowork). Run on fresh install, when the profile has real placeholders,
  to patch a section, or any time the profile feels stale.
argument-hint: "[--redo re-interview from scratch | --update [section] patch one section]"
---

# /piper-morgan:meet-piper

This skill is the load-bearing setup step for the piper-morgan plugin. Every other skill in the plugin reads from the PM profile file this skill writes. Without it, the plugin can't give PM-shaped output for this specific user — it can only give generic PM-shaped output.

## Two modes — name the split, don't arbitrate it silently

This skill has **two distinct shapes**, and most invocations after install are the second one:

- **Cold start** (fresh install / `--redo` / genuine placeholders / resumed pause): the full **serial,
  one-question-at-a-time** interview. Serial is right here because the interview *demonstrates* the
  voice rule it's collecting — the conduct of the interview is part of the calibration.
- **Maintenance** (already-configured user, no `--redo`): a **compact, scoped update** of just the
  sections that drifted. Serial-one-at-a-time is too heavy for patching one thing; use a **form** where
  the surface offers an elicitation affordance (Desktop/Cowork), or a compact serial pass where it
  doesn't (CLI).

If a surface elicitation hook says "use a form" and this skill's cold-start text says "always serial,"
that is **not** a contradiction to silently arbitrate: **form wins for maintenance, serial wins for
cold start.** The "Mode routing" step below decides which you're in; honor that mode's contract.

## Behavioral contract

These rules are **always** honored (both modes):

- **Anti-sycophancy.** Do not open with "Great question!", "You're absolutely right!", or any
  affirmation-of-the-user's-character framing. State what you heard, confirm if useful, move on. The
  user will read sycophancy as evidence the plugin doesn't honor the voice rules it collects.
- **No silent failures.** If the user skips a field, mark it explicitly (`[SKIPPED — user declined]`);
  if a field doesn't apply (e.g., escalation for a solo founder), capture `[N/A — reason]` rather than
  forcing an answer or leaving something that looks unasked.
- **Don't pre-populate from inferred context.** Don't read the user's personal memory or
  home-directory `CLAUDE.md` to fill answers. The only inputs are typed answers and documents the user
  explicitly points at.
- **Pause and resume.** Tell the user they can say "pause" / "stop" / "come back to this." On pause,
  save a partial profile with `<!-- SETUP PAUSED AT: [section] -->` at the top and `[PENDING]` on
  unanswered fields. A later run that finds a pause comment greets: "You paused at [section]. Resume or
  start over?"

These two rules are **mode-aware** (this is the reconciliation of the confirm-vs-bias-to-action tension):

- **Question cadence.**
  - *Cold start:* **one question per turn**, sub-topics also serial. Never batch 2-3 and ask the user
    to "answer in any order." The serial cadence is itself part of the calibration demo.
  - *Maintenance:* prefer a **compact form** (core items shown, deeper sections revealed on request)
    where the surface supports elicitation; otherwise a brief serial pass over just the changed
    section(s). Don't re-run the whole 15-minute interview to patch one field.
- **Write contract.**
  - *Cold start:* **confirm before writing.** Show the captured summary, ask "does this look right?",
    write only on the user's go-ahead. (A fresh profile reflects ~15 min of input; the confirm step
    also demonstrates the carefulness the interview is about.)
  - *Maintenance:* the write is **reversible** — `save_profile` auto-backs-up the prior version — so if
    the user's own profile asserts a bias-to-action / don't-wait-for-a-nod posture, **write the change,
    then show the diff and invite correction**, rather than gating on a nod. Honor the user's stated
    posture; don't impose a confirm gate the user has explicitly said they don't want. (If the profile
    says the opposite — confirm-first — then confirm first, even in maintenance.)

## Mode routing (run this first)

**Call the `get_profile` MCP tool** (do NOT read `~/.claude/...` directly — config is owned by the
Piper MCP server now, so this works on every surface including Cowork; the agent never needs filesystem
access to the user's home). Then route:

- **`--redo` passed** → **cold start.** Ignore the existing profile, start fresh from the orientation.
  (`save_profile` backs up the prior version, so a redo never silently destroys the old config.)
- **`--update [section]` passed** (and a populated profile exists) → **maintenance**, jumping straight
  to that section. See the Maintenance-mode section.
- **`[profile: NOT-CONFIGURED]`** → **cold start** from the orientation.
- **Result contains `<!-- SETUP PAUSED AT: -->`** → greet, name the paused section, offer resume or
  start-over (a resume continues the **cold-start** serial flow).
- **`[profile: HAS-PLACEHOLDERS]`** → genuine unfilled fields remain → **cold start**, offering to start
  fresh from wherever the placeholders begin. (Note: the server now distinguishes *real* placeholders
  from the template's own instructional mentions of the token, so this no longer false-fires on a
  complete profile.)
- **Populated profile (no placeholders, no pause comment), no `--redo`** → **maintenance.** Do NOT
  dead-end at "run `--redo` or edit by hand." Go to the Maintenance-mode section and offer a scoped
  update.

> Requires the Piper MCP server to be running (it serves these tools + `ask_piper`). If `get_profile`
> isn't available, tell the user the local Piper server isn't connected and setup needs it — don't fall
> back to writing files directly (that's the portability bug this design fixes).

# Maintenance mode (returning, already-configured user)

This is the common case after install: the profile exists and the user wants to patch what drifted, not
re-do the whole interview. Keep it light.

1. **Orient in one line, honestly.** Read the profile you already fetched. Say what's current and flag
   staleness if you see it — e.g., "You're configured; profile last patched [date from the provenance
   line]. Anything changed?" If a date or a fact looks out of step with what the user just said, name it
   (no silent failures) and offer that section as the likely thing to update.

2. **Offer a scoped update — compact, not the full interview.**
   - If the surface offers a **form / elicitation affordance** (Desktop, Cowork): present a **compact
     form** showing the **core, most-drift-prone items** — project portfolio / primary attention /
     project pace — with the deeper sections (voice rules, decision-making, routing, integrations)
     available only if the user asks to expand them. This is the progressive-disclosure shape: core
     shown, rest on request.
   - If the surface has **no form affordance** (CLI): ask a brief serial pass over just the section(s)
     the user names — not all six parts. Drop the demonstrative "one question at a time, here's why"
     framing; the user has already seen it.
   - If `--update [section]` was passed, jump straight to that section.

3. **Route each change to the right file.** Identity / role-shape / portfolio / primary-attention /
   sibling-projects live in the **company profile** (`save_company_profile`) — shared by sibling Piper
   plugins. Voice rules, decision-making, routing/CC, integrations live in the **PM profile**
   (`save_profile`). A single update can touch both (e.g., re-framing a client as an "anchor client"
   updates the portfolio in *both* files). Update only the files that actually changed.

4. **Preserve everything you didn't touch.** Rebuild the file from the existing content with only the
   changed fields replaced. Keep the CONFIGURATION-LOCATION HTML comment block verbatim. Update the
   provenance line's "patched [date]" stamp so the next maintenance run can orient. Do not drop sections
   the user didn't mention.

5. **Write per the maintenance write contract** (see Behavioral contract). The write is reversible
   (auto-backup), so if the profile asserts a bias-to-action posture: **write, then show the diff and
   invite correction** rather than gating on a nod. If the profile asks for confirm-first, confirm first.

6. **Close briefly.** State what changed (scoped to what the user gave), note that the prior versions
   were backed up automatically, and stop. No re-litigating untouched sections.

> Why a separate mode: serial-one-at-a-time earns its keep in cold start because it *demonstrates* the
> voice rule it's collecting. For a returning user patching one field it's pure friction. Same skill,
> two shapes — matched to whether the user is being onboarded or doing maintenance.

---

# Cold-start interview (fresh install / `--redo` / resumed pause / genuine placeholders)

## Shared company profile check

**Call the `get_company_profile` MCP tool.**

- **Returns populated content:** Show a one-line confirmation: "You're [name], working on [primary projects]. Right? (Say 'update' to revise.)" If confirmed, skip the cross-context identity questions — go straight to the plugin-specific ones.
- **Returns `[company-profile: NOT-CONFIGURED]`:** This is the first piper-morgan-marketplace plugin the user has set up. After the orientation, ask the cross-context questions and save them via `save_company_profile` (template below), then continue with the plugin-specific questions. Tell the user: "I've saved your cross-context profile — any sibling Piper plugins you install later will read it and skip these questions."

The cross-context questions that belong in the shared profile (and should NOT be re-asked if it exists): name, role-shape, working-style-in-one-line, primary attention, sibling projects.

The plugin-specific questions that stay per-plugin: voice/posture rules, decision-making and escalation, routing/CC discipline, integrations.

---

## Orientation (show this first; wait for the user before continuing)

> **`piper-morgan` is a calibration-heavy PM plugin.** It works like a colleague who already knows how you work — not like a generic PM checklist. To get there, I need to learn (1) who you are and what you ship, (2) the conduct rules you want me to honor, (3) the projects you're working across, (4) how you make decisions and escalate, and (5) how you route outbound work.
>
> This will take ~10-15 minutes. I'll ask **one question at a time** — not 2-3 at a time. Sub-topics also one at a time. That's a deliberate inversion of how most setup interviews work; it's also one of the conduct rules I'm collecting, so I want to demonstrate it in the interview itself.
>
> If you need to stop, say "pause" and I'll save what we have. You can come back to it any time.
>
> Ready? Type "ready" or "go" to start, or "pause" if now isn't the moment.

Wait for the user's response. Do not show the first question until they've said go.

## Part 1 — Cross-context identity (skip if a company profile already exists, per the check above)

These five questions are saved via `save_company_profile` and will be reused by any sibling plugins.

**Q1.1.** What name should I use for you? (First name is fine; or whatever you'd want a colleague to call you.)

→ wait for answer; record as `name`.

**Q1.2.** What's your role shape? Pick the closest, or describe it in your own words:
- founder-PM (you run the product AND the company)
- scaleup-PM (you run product at a company that's past founding, before enterprise scale)
- enterprise-PM (you run a slice of product inside a large org)
- agency-PM (you run product engagements for clients)
- product-counsel-adjacent (you do PM work where legal/risk calibration is load-bearing)
- something else

I'm asking because the rest of the plugin's defaults shift slightly by role shape. Don't worry about getting it perfectly right; you can change it later.

→ wait for answer; record as `role_shape`. If "something else," ask a brief clarifying question (still serial).

**Q1.3.** In one sentence: where do you work, and what do you ship? (A link to your company / product / portfolio is fine if it's easier than typing.)

→ wait for answer; record as `where_what`.

**Q1.4.** In one line: what's your working style? Examples (don't copy these — they're calibration anchors):
- "Direct, anti-sycophancy, collegial; serial decisions; absolute paths in chat"
- "Async by default; long-form memos over meetings; comfortable with uncertainty"
- "Hands-off until I'm not; I want the agent to act unless something's risky"

→ wait for answer; record as `working_style_one_line`. This becomes the load-bearing summary the rest of the plugin honors.

**Q1.5.** What projects are you working across right now, and which one has primary attention? (Naming the secondary ones is useful too — the plugin will know when you mention them in a session.)

→ wait for answer; record as `project_portfolio`. Capture both the list AND which has primary attention.

→ Before continuing: **call `save_company_profile`** with the Q1.1-Q1.5 content (template at the end of this skill). Confirm to the user: "Saved your cross-context profile. Any sibling Piper plugins you install will read it." Then continue. (The server owns the write — no filesystem access needed; works on Cowork.)

## Part 2 — Voice and posture rules (the load-bearing section)

These are the conduct rules the rest of the plugin's skills will honor. The user has probably been training Claude on these implicitly for a long time; this is where they get written down explicitly. Ask them ONE AT A TIME, even though it's tempting to batch.

**Q2.1.** Sycophancy. Some users want Claude to open responses with affirmation ("Great question!", "You're absolutely right!"); some find it actively annoying and want it gone. Where are you on this? (If you want it gone, do you want me to also flag when I notice myself doing it, or just stop?)

→ wait for answer; record as `voice.anti_sycophancy`. Capture the full statement, not a yes/no.

**Q2.2.** Silent failures. When a skill can't do something — can't read a file, can't reach a connector, can't complete the task — do you want it to (a) say so explicitly even if it's a small thing, (b) try to recover quietly and only surface if it's blocking, or (c) something else? Why does this matter to you?

→ wait for answer; record as `voice.no_silent_failures`. The "why does this matter to you" question often produces the most useful framing — capture it.

**Q2.3.** Questions and batching. When I need information from you, do you want me to ask one question at a time and wait, or batch 2-3 related questions per turn? (You're seeing how serial-question works in this interview; if it feels right, that's the answer.)

→ wait for answer; record as `voice.serial_or_batched`. If user says "serial," capture how strict — "always one question, never batch" vs. "usually one, batches OK for clearly-paired questions."

**Q2.4.** Drafts and execution. When alignment is clear on a next step — drafting a memo, updating a file, applying triage — do you want me to execute and report, or queue "I'll do X next" and wait for the next turn? Where's the line between "just do it" and "ask first"?

→ wait for answer; record as `voice.write_now_proceed_when_aligned`. Capture both the default AND the line (push/PR/external comms vs. local drafts).

**Q2.5.** Path citation in chat. When I cite files in chat responses, do you want absolute paths (clickable in your interface) or repo-relative paths (cleaner-looking but not clickable)?

→ wait for answer; record as `voice.path_citation`.

→ Pause and confirm: "Here's what I captured for voice and posture: [show 5 bullets]. Does any of this need tuning before we move on?" Wait for response. Apply any edits. Then continue.

## Part 3 — Decision-making and escalation

**Q3.1.** When something needs a decision above your authority — a launch risk above your calibration, a novel issue, a big spend — who does that go to? Give me a name, a role, or "I decide myself" / "no formal hierarchy." (The plugin uses this to know when to say "you can handle this" vs. "loop in [X].")

→ wait for answer; record as `decision.escalation_to`. If the user says no hierarchy or solo, record `[N/A — solo / no formal hierarchy]` and note that escalation questions don't apply.

**Q3.2.** When the people you work with give you time estimates — engineering, design, ops, whoever — do those estimates tend to (a) run conservative (delivery beats them), (b) run optimistic (delivery slips), (c) be roughly calibrated, or (d) depend on the person? How should I use their estimates when something downstream depends on them?

→ wait for answer; record as `decision.estimate_calibration`. Capture the rule the user wants applied (e.g., "treat as upper bound, ask the person whether the fallback is worth it").

**Q3.3.** Backlog hygiene. If you have stale tickets (no movement in 30/45/60+ days), is that usually (a) neglect, (b) anticipatory drafting that hasn't been reached yet, (c) shifting priorities, or (d) something else? When I notice staleness, should I flag it as a problem or treat it as expected?

→ wait for answer; record as `decision.backlog_hygiene`. The user's framing here usually tells you whether they want activity-based or attention-based metrics.

## Part 4 — Project pace and cross-project integrity

**Q4.1.** What's the realistic pace of your work on these projects? Is there a project that runs at "production sprint pace" (multiple agents pushing daily) vs. one that runs at "keep-the-lights-on pace" (multi-day gaps are normal)? When I notice a quiet period on a given project, should I treat it as a problem to flag or as expected operating reality?

→ wait for answer; record as `project_pace`. Capture both the per-project pace AND the meta-rule about how to interpret quiet periods.

**Q4.2.** Cross-project vocabulary integrity. When I'm working on Project A and I notice something from Project B that "sounds applicable" — a framing, a vocabulary, a mechanism — do you want me to (a) cross-pollinate freely, (b) flag the pattern but verify the mechanism maps before importing the framing, or (c) keep projects strictly separate? If you've been bitten by cross-pollination drift, what did it look like?

→ wait for answer; record as `project_vocabulary_integrity`. The "if you've been bitten" question often produces the most useful framing.

## Part 5 — Routing and CC discipline (skip if the user's PM shape doesn't involve memo-style routing)

This part may not apply if the user is a solo founder who doesn't deal with formal memo routing. Ask Q5.0 first; if no, skip Q5.1-Q5.3.

**Q5.0.** Does your PM work involve formal memo or message routing — inboxes, CC discipline, sign-off chains? Or is most of your work direct synchronous conversation?

→ wait for answer. If "no formal routing," record the routing section as `[N/A — direct synchronous; no formal memo routing]` and skip to Part 6. If yes, continue.

**Q5.1.** What's your primary inbox or mailbox convention? Give me the literal path or format if you have one. (Example from one user: `mailboxes/xian (ceo)/inbox/` — literal space and parens.) Any pitfalls I should know about (e.g., look-alike paths that aren't canonical)?

→ wait for answer; record as `routing.primary_inbox`.

**Q5.2.** CC-on-memo semantics. When a memo is addressed to you with someone else on CC, is that (a) shared situational awareness — the CC'd party isn't expected to act, (b) routing — the CC'd party should also act, or (c) varies and the memo body says? When YOU are the CC'd party on someone else's memo to a colleague, what should I assume about whether the memo is actionable for you?

→ wait for answer; record as `routing.cc_semantics`.

**Q5.3.** CC distribution mechanics. When you write a memo with multiple recipients in a `cc:` field, does an underlying system auto-fan-out the memo to each recipient's inbox, or is fan-out a manual step (cp each file)? I want to know whether to treat `cc:` as routing or just as documentation.

→ wait for answer; record as `routing.cc_distribution_mechanism`.

## Part 6 — Integrations (light touch in v0.1)

**Q6.1.** Which tools / connectors do you use that this plugin should know about? Examples: meeting transcript tools (Granola, Fireflies), doc systems (Notion, Drive, Confluence), trackers (GitHub, Linear, Jira), comms (Slack, email), design (Figma). Just name them; v0.1 doesn't probe connections, it just records what you said.

→ wait for answer; record as `integrations.user_named`. Mark each as `[user-named, not probed]` — don't pretend to verify what you can't verify.

→ Surface honestly: "v0.1 of this plugin records what you named but doesn't probe whether the connectors are actually wired up. Future sub-passes will add real probing. The plugin will fall back to manual / paste-the-content workflows for anything that isn't actually wired."

## Part 7 — Confirm and save

Before saving the profile:

1. Show the user a summary of what was captured, organized by the profile's section structure. Use the headings from the template. Skipped/N-A sections shown as `[SKIPPED]` or `[N/A — reason]`, not as if nobody asked.
2. Ask: "Does this look right? Anything to change before I save your PM profile?"
3. Apply any edits the user requests. Re-confirm after edits.
4. On user go-ahead, **call `save_profile`** with the full profile content. Build it from the plugin's root `CLAUDE.md` template structure, substituting the user's answers for `[PLACEHOLDER]` markers. (The server owns the write + backs up any prior version — works on every surface, no filesystem access needed. This is the #1157 fix: meet-piper completes in Cowork now.)
5. Confirm to the user that the profile is saved and that they can edit it directly for small changes (the server keeps it as a human-editable file).

## Part 8 — Close

After saving, say one of:

- If this was a fresh first install: "Done — your PM profile is saved (the Piper server keeps it as a plain-text file you can edit directly). Re-run `/piper-morgan:meet-piper --redo` for a full re-interview. Two more skills are ready to use now: `/piper-morgan:ask-piper` (relay a question to Piper) and `/piper-morgan:consult-piper` (Piper + I gather context when it's missing). Future sub-passes will add journaling + composting."

- If `--redo`: "Done — your PM profile has been re-saved. The server backed up the prior version automatically."

Then: "One note — this is a PoC. The plugin's value lives in the calibration this interview captures; the other skills (ask-piper, consult-piper) consume it. If the calibration feels off, the fix is here."

---

# Templates

## Company profile template

Pass this structure as the `content` to `save_company_profile`:

```markdown
# Cross-context profile
*Written by piper-morgan:meet-piper on [DATE]. Shared by any sibling Piper plugins. Edit directly for small changes.*

**Name:** [from Q1.1]
**Role shape:** [from Q1.2]
**Where you work / what you ship:** [from Q1.3]
**Working style in one line:** [from Q1.4]

## Project portfolio

[from Q1.5 — preserve the user's framing of primary vs. secondary attention]
```

## PM profile template

Pass to `save_profile` as `content`: mirror the structure of the plugin's root `CLAUDE.md` template (the one this skill is shipped alongside), substituting the user's answers for the `[PLACEHOLDER]` markers. Preserve the CONFIGURATION LOCATION HTML comment block at the top — every skill in the plugin depends on it.

For sections where the user said "N/A" or skipped, write `[N/A — <reason>]` or `[SKIPPED — user declined at <date>]` rather than leaving `[PLACEHOLDER]` (which would trigger the cold-start prompt again on next skill run).

---

# Failure modes for the skill itself

- **In cold start, don't batch even when it feels efficient.** If you find yourself wanting to ask 2-3 related questions in one turn "to save time," stop — the serial cadence is part of the calibration demo. (In *maintenance* a compact form/serial-pass is correct; this bullet is about the cold-start interview.)
- **Don't invent answers.** If a user gives a thin or ambiguous answer, ask a follow-up rather than filling in the gap with what you think they probably meant. The user's exact phrasing is often load-bearing for downstream skills.
- **Don't pretend to verify what you can't verify.** Integrations are user-named, not probed, in v0.1. Say so.
- **Don't read the user's home-directory `~/CLAUDE.md` or other personal memory to pre-populate the interview.** The skill builds a fresh PM profile from typed answers. Pre-populating from inferred context defeats the calibration exercise.
- **Don't apply the wrong mode's write contract.** In cold start, never write the profile without showing the captured summary first — silent write of a fresh profile is the exact failure the voice rules forbid. In maintenance, the inverse risk: don't impose a confirm-gate the user's own bias-to-action profile has told you to skip — write the reversible change and show the diff. Match the contract to the mode (see Behavioral contract).
- **Don't re-run the full interview to patch one field.** A returning user who wants to update one section should get a scoped update, not all six parts. Routing a populated profile into the cold-start interview (absent `--redo`) is the maintenance-gap failure this version fixes.
