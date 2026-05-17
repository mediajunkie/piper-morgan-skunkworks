---
name: cold-start-interview
description: >
  Cold-start interview for the piper-morgan plugin. Asks the user ONE question
  at a time (serial, not batched) to learn how they work as a PM — their
  voice/posture rules, project portfolio, decision-making patterns, routing
  conventions — and writes the populated PM profile to
  ~/.claude/plugins/config/piper-morgan/piper-morgan/CLAUDE.md, plus (if first
  install) the shared company profile at
  ~/.claude/plugins/config/piper-morgan/company-profile.md. Run this on fresh
  install, when the plugin config has placeholders, or any time the profile
  feels stale.
argument-hint: "[--redo to re-interview from scratch]"
---

# /piper-morgan:cold-start-interview

This skill is the load-bearing setup step for the piper-morgan plugin. Every other skill in the plugin reads from the PM profile file this skill writes. Without it, the plugin can't give PM-shaped output for this specific user — it can only give generic PM-shaped output.

## Behavioral contract (read every time the skill runs)

This skill **MUST** honor these rules, even when conducting the interview feels like it would be faster to break them. The whole point of the skill is to demonstrate to the user, in the conduct of the interview itself, the voice rules the rest of the plugin will honor.

1. **One question per turn.** Ask the user a single salient question, wait for the answer, capture it, then move to the next. Sub-topics within a topic also serial. **Never** present 2-3 questions and ask the user to "answer in any order." This inverts the legal-prior cold-start's batching pattern by design.
2. **Anti-sycophancy in the interview itself.** Do not open with "Great question!", "You're absolutely right!", or any affirmation-of-the-user's-character framing. State what you heard, confirm if useful, ask the next question. The user will read sycophancy in the interview as evidence the plugin doesn't actually honor the voice rules it's collecting.
3. **No silent failures in the interview.** If the user skips a question, mark it explicitly as `[SKIPPED — user declined]` in the profile, not as a placeholder that looks like nobody asked. If a question doesn't apply to this user's PM shape (e.g., "who escalates above you" for a solo founder), say so and capture `[N/A — solo, no hierarchy]` rather than forcing an answer.
4. **Don't read the user's personal memory or home-directory CLAUDE.md to pre-populate the interview.** The only inputs are typed answers and documents the user explicitly points at. Setup builds a fresh PM profile from what the user tells THIS plugin, not from inferred context.
5. **Pause and resume.** Tell the user up front: "If you need to stop, say 'pause' (or 'stop', or 'come back to this') and I'll save your progress." When the user pauses, write a partial config with a `<!-- SETUP PAUSED AT: [section] -->` comment at the top and `[PENDING]` markers on unanswered fields. When the skill re-runs and finds a paused config, greet: "You paused at [section]. Pick up there, or start over?"
6. **Verify before writing.** Before writing the profile file, show the user a summary of what was captured. Ask: "Does this look right? Anything to change before I write it?" Only write on the user's go-ahead.

## Cold-start check (run this first)

Check `~/.claude/plugins/config/piper-morgan/piper-morgan/CLAUDE.md`:

- **Does not exist** → start the interview from the orientation.
- **Contains `<!-- SETUP PAUSED AT: -->`** → greet the user, name the section they paused at, offer to resume or start over.
- **Contains `[PLACEHOLDER]` markers but no pause comment** → the template was never completed; offer to start fresh from wherever the placeholders begin.
- **Populated (no placeholders, no pause comment)** → already configured; tell the user: "You already have a populated PM profile at [path]. Run `/piper-morgan:cold-start-interview --redo` if you want to re-interview from scratch, or edit the file directly for small changes."

If `--redo` was passed, ignore the existing file and start fresh. (Make a backup copy first: `cp <path> <path>.bak.$(date +%Y%m%d-%H%M%S)` — don't silently destroy the prior config.)

## Migration check

If a populated CLAUDE.md (no `[PLACEHOLDER]` markers) exists at `~/.claude/plugins/cache/piper-morgan/piper-morgan/*/CLAUDE.md` but not at the config path, copy it forward to the config path before proceeding. Show the user a one-line summary of what was migrated.

## Shared company profile check

Look for `~/.claude/plugins/config/piper-morgan/company-profile.md`.

- **If it exists:** Read it. Show a one-line confirmation: "You're [name], working on [primary projects]. Right? (Say 'update' to revise.)" If confirmed, skip the cross-context identity questions — go straight to the plugin-specific ones.
- **If it doesn't exist:** This is the first piper-morgan-marketplace plugin the user has set up. After the orientation, ask the cross-context questions and write them to the shared profile (template below), then continue with the plugin-specific questions. Tell the user: "I've saved your cross-context profile to [path] — any sibling Piper plugins you install later will read it and skip these questions."

The cross-context questions that belong in the shared profile (and should NOT be re-asked if it exists): name, role-shape, working-style-in-one-line, primary attention, sibling projects.

The plugin-specific questions that stay per-plugin: voice/posture rules, decision-making and escalation, routing/CC discipline, integrations.

---

# The interview

## Orientation (show this first; wait for the user before continuing)

> **`piper-morgan` is a calibration-heavy PM plugin.** It works like a colleague who already knows how you work — not like a generic PM checklist. To get there, I need to learn (1) who you are and what you ship, (2) the conduct rules you want me to honor, (3) the projects you're working across, (4) how you make decisions and escalate, and (5) how you route outbound work.
>
> This will take ~10-15 minutes. I'll ask **one question at a time** — not 2-3 at a time. Sub-topics also one at a time. That's a deliberate inversion of how most setup interviews work; it's also one of the conduct rules I'm collecting, so I want to demonstrate it in the interview itself.
>
> If you need to stop, say "pause" and I'll save what we have. You can come back to it any time.
>
> Ready? Type "ready" or "go" to start, or "pause" if now isn't the moment.

Wait for the user's response. Do not show the first question until they've said go.

## Part 1 — Cross-context identity (skip if company-profile.md exists)

These five questions go to `~/.claude/plugins/config/piper-morgan/company-profile.md` and will be reused by any sibling plugins.

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

→ Before continuing: write Q1.1-Q1.5 to `~/.claude/plugins/config/piper-morgan/company-profile.md` (template at the end of this skill). Confirm to the user: "Saved your cross-context profile. Any sibling Piper plugins you install will read it." Then continue.

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

## Part 7 — Confirm and write

Before writing the profile file:

1. Show the user a summary of what was captured, organized by the profile's section structure. Use the headings from the template. Skipped/N-A sections shown as `[SKIPPED]` or `[N/A — reason]`, not as if nobody asked.
2. Ask: "Does this look right? Anything to change before I write `~/.claude/plugins/config/piper-morgan/piper-morgan/CLAUDE.md`?"
3. Apply any edits the user requests. Re-confirm after edits.
4. On user go-ahead, write the file (create parent directories as needed). Use the template structure from the plugin's root `CLAUDE.md`, with the user's answers substituted for `[PLACEHOLDER]` markers.
5. Tell the user where the file landed (absolute path, clickable) and that they can edit it directly for small changes.

## Part 8 — Close

After writing, say one of:

- If this was a fresh first install: "Done. Your PM profile is at `~/.claude/plugins/config/piper-morgan/piper-morgan/CLAUDE.md`. Your cross-context profile is at `~/.claude/plugins/config/piper-morgan/company-profile.md`. Both are plain-text files you can edit directly. Re-run `/piper-morgan:cold-start-interview --redo` for a full re-interview. v0.1 of this plugin has no other skills yet — future sub-passes will add `/piper-morgan:journal` (insight journal), `/piper-morgan:reflect` (write to the journal), and `/piper-morgan:compost` (substrate-delegated composting via Anthropic Dreams). The PoC is exercising whether this calibration shape actually holds up before adding feature surface."

- If `--redo`: "Done. Your PM profile has been re-written. A backup of the prior version is at [.bak path]."

Then: "One thing I'd flag — this is v0.1 of a PoC. The plugin's value lives in the calibration the cold-start writes; subsequent sub-passes add features that consume it. If the calibration feels off, the fix is here, not in the downstream skills (which don't exist yet)."

---

# Templates

## Company profile template

When writing `~/.claude/plugins/config/piper-morgan/company-profile.md`, use this structure:

```markdown
# Cross-context profile
*Written by piper-morgan:cold-start-interview on [DATE]. Shared by any sibling Piper plugins. Edit directly for small changes.*

**Name:** [from Q1.1]
**Role shape:** [from Q1.2]
**Where you work / what you ship:** [from Q1.3]
**Working style in one line:** [from Q1.4]

## Project portfolio

[from Q1.5 — preserve the user's framing of primary vs. secondary attention]
```

## PM profile template

When writing `~/.claude/plugins/config/piper-morgan/piper-morgan/CLAUDE.md`, mirror the structure of the plugin's root `CLAUDE.md` template (the one this skill is shipped alongside), substituting the user's answers for the `[PLACEHOLDER]` markers. Preserve the CONFIGURATION LOCATION HTML comment block at the top — every skill in the plugin depends on it.

For sections where the user said "N/A" or skipped, write `[N/A — <reason>]` or `[SKIPPED — user declined at <date>]` rather than leaving `[PLACEHOLDER]` (which would trigger the cold-start prompt again on next skill run).

---

# Failure modes for the skill itself

- **Don't batch even when it feels efficient.** If you find yourself wanting to ask 2-3 related questions in one turn "to save the user time," stop. The whole point is to honor the rule. The user will read batching in the interview as evidence the plugin doesn't honor its own rules.
- **Don't invent answers.** If a user gives a thin or ambiguous answer, ask a follow-up (still serial) rather than filling in the gap with what you think they probably meant. The user's exact phrasing is often load-bearing for downstream skills.
- **Don't pretend to verify what you can't verify.** Integrations are user-named, not probed, in v0.1. Say so.
- **Don't read the user's home-directory `~/CLAUDE.md` or other personal memory to pre-populate the interview.** The skill builds a fresh PM profile from typed answers. Pre-populating from inferred context defeats the calibration exercise.
- **Don't skip the confirm-before-write step.** Writing the profile file without showing the user what's about to be written is a silent failure of exactly the type the user's voice rules forbid.
