# Session log: 2026-05-17 prog-code-opus (sub-pass 4.a)

**Role**: Coding subagent, BYOC PoC sub-pass 4.a (plugin scaffold + Feature 1)
**Workspace**: `/Users/xian/Development/piper-morgan-skunkworks/byoc/poc/piper-morgan/`
**Dispatched by**: PA (Piper Alpha)
**Spec input**: `/Users/xian/Development/piper-morgan/piper-morgan-product-skunkworks-coord/dev/active/skunkworks-byoc-step-3-poc-scope-synthesis-2026-05-17.md` (v1.1)

---

## What I read first

1. The full PoC scope synthesis v1.1 — confirmed 4.a scope is scaffold + Feature 1 (`cold-start-as-pm-profile`) only.
2. Subagent-1's plugin architecture study — confirmed:
   - Plugin = directory with `.claude-plugin/plugin.json`; no plugin runtime, just a manifest.
   - Skills are prompt files in `skills/<name>/SKILL.md`.
   - Config path convention: `~/.claude/plugins/config/<marketplace>/<plugin>/CLAUDE.md` — version-independent, user-owned.
   - Shared profile one level up: `~/.claude/plugins/config/<marketplace>/company-profile.md`.
   - Plugin root `CLAUDE.md` is a TEMPLATE, not loaded as context; the cold-start writes a populated copy to the config path; every other skill reads from config.
3. Legal-prior `product-legal` plugin:
   - `plugin.json` (4-6 fields per shape) — lifted shape.
   - `CLAUDE.md` template with `[PLACEHOLDER]` markers + CONFIGURATION LOCATION HTML comment block — lifted shape, adapted path.
   - `cold-start-interview/SKILL.md` — uses YAML frontmatter (`name`, `description`, `argument-hint`), batches questions 2-3 at a time (our PoC inverts this).
4. xian's MEMORY.md memos — extracted the PM-profile schema source: anti-sycophancy, no-silent-failures, serial-decisions, write-now-proceed-when-aligned, fully-qualified-paths, PM-CC-on-memo routing, project-pace, sibling-projects, project-conceptual-integrity, backlog-hygiene, lead-dev-estimates, PM-CEO-mailbox, CC-distribution-is-manual, PA-worktree-default, PM-Kind-OpenLaws-focus.

## What I built

Directory tree at `/Users/xian/Development/piper-morgan-skunkworks/byoc/poc/piper-morgan/`:

```
piper-morgan/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── CLAUDE.md
├── README.md
└── skills/
    └── cold-start-interview/
        └── SKILL.md
```

5 files, no agents, no hooks, no references. Deliberately less-is-more.

### Design calls I made

1. **PM-profile, not founder-profile.** Q1.2 captures role-shape (founder-PM / scaleup-PM / enterprise-PM / agency-PM / product-counsel-adjacent / other) so the future founder-subprofile direction stays open. The spec endorsed this framing explicitly (v1.1 supersedes v1.0).
2. **Serial questions, deliberately demonstrated in the interview itself.** Every question (Q1.1-Q6.1) is its own turn. The skill's behavioral contract section spells out *why* — the interview is also a demonstration of the conduct rule it's collecting.
3. **5 cross-context questions + 11 plugin-specific questions = 16 question turns.** Targets ~10-15 min if user is willing to type/paste. Some can short-circuit (e.g., Q5.0 "do you have memo routing at all?" → if no, skip Q5.1-5.3).
4. **`[N/A]` and `[SKIPPED]` distinct from `[PLACEHOLDER]`.** Honors the no-silent-failures rule. Skipped sections won't trigger the cold-start prompt again on next skill run; placeholders will. Important for the cold-start-check pattern.
5. **Confirm-before-write step explicit.** Section "Part 7" walks through summary → user OK → write file. Prevents the failure mode of writing a profile the user hasn't actually endorsed.
6. **CONFIGURATION LOCATION block lifted verbatim from legal prior, with path adapted to `~/.claude/plugins/config/piper-morgan/piper-morgan/CLAUDE.md` and `piper-morgan` as both marketplace and plugin name.** Flagged this assumption in README under "Path conventions" — if the marketplace name turns out to be different, every reference needs updating.
7. **`.mcp.json` is `{"mcpServers": {}}` only — no `recommendedCategories`.** Subagent-1 flagged uncertainty on whether `recommendedCategories` is public schema or Anthropic-internal. Sub-pass 4.c will populate `mcpServers` with the Dreams API tool.
8. **No `agents/` or `hooks/` directories at all.** v0.1 doesn't need them. Build-less.

### What I deliberately did NOT do

- No `commands/` directory. Skills only. (PM prior uses commands; legal uses skills; we follow legal-shape per the synthesis.)
- No `references/` directory. Cold-start references the plugin root CLAUDE.md template directly. Subagent-1 noted "references/ lives only at repo root and is not shipped inside any plugin directory" was a known gap in legal — we sidestep by not relying on it.
- No `--check-integrations` flag implementation. Q6.1 captures user-named integrations as `[user-named, not probed]`. Sub-pass 4.b or 4.c will need real probing.
- No `--redo` argument-handling beyond a mention in argument-hint and a behavioral contract note ("make a backup copy first"). The skill's logic for handling `--redo` is described in prose; no separate script.
- No tests beyond the manual test sequence I'll write up in the report.
- No marketplace.json yet. Install instructions in README use the local `--plugin-dir` shape; a marketplace can be added later.
- No `.claude-plugin/marketplace.json` — the synthesis explicitly says single-plugin, no marketplace needed for the PoC.
- No agents (no launch-watcher analog). Out of scope per synthesis.
- No hooks. Out of scope per synthesis.

## Tensions I noticed during the build

- **The skill is ~280 lines.** That's not "short and thin" by the bare-skill standard. But the synthesis specifies "one long skill with internal serial loop" — the length is in the serial loop, not in shared boilerplate. Compare to legal's cold-start at ~490 lines (which DOES batch). Within the "long skill" framing, ours is shorter.
- **Q6.1 (integrations) is awkward in v0.1.** Without real probing, capturing user-named integrations runs the risk of pretending verification we didn't do. I flagged this in the Q6.1 prompt itself ("v0.1 doesn't probe connections, it just records what you said") and in the integrations table footnote. Future sub-passes need to actually probe.
- **Q5 (routing/CC) is heavily shaped by xian's specific workflow** (mailboxes/xian (ceo)/, CC-as-documentation, fan-out-is-manual). I tried to generalize the wording but the Q5.1 example uses xian's literal path as illustration. May feel too-specific for a different PM. Trade-off: specificity gives the user a concrete anchor; generalization risks the question becoming vague enough to skip.
- **No probe-test for whether bare Claude could replace PM-specific calibration.** The synthesis says don't build that probe in v0.1; just "note whether voice-of-Piper feels recognizable when only the config is in play." That's the gate check after running the skill end-to-end, not a built-in feature.
- **The skill doesn't read MEMORY.md to pre-populate.** Deliberate per spec ("don't read the user's home-directory CLAUDE.md or other personal memory"). This means xian (the most natural test user) will have to type/paste a lot of context that's already written down in `~/.claude/projects/-Users-xian-Development-piper-morgan/memory/*.md`. The interview is testing whether the cold-start CAN extract calibration from someone who hasn't already written memos for it; testing on xian undersells the difficulty for a real first-time user. Surface for PA to consider as a finding.

## Time spent

~2.5 hours equivalent. Under the 3-5 hour budget. Most time was in the SKILL.md body — getting the serial-question framing right and choosing which memos to translate as Q-prompts.

## Open questions I'm leaving for PA / PM

1. **Marketplace name.** The plugin's config path assumes `piper-morgan` is both marketplace name and plugin name. If the marketplace ships as something different (e.g., `piper-morgan-marketplace`, or it gets bundled into a broader `mediajunkie` marketplace), every reference needs updating. v0.1 holds the assumption; PA should decide before distribution.
2. **Whether `~/.claude/plugins/config/piper-morgan/company-profile.md` should be sibling-Piper-shared or piper-morgan-only.** I went with "shared across any sibling Piper plugins" matching legal's `claude-for-legal/company-profile.md` pattern. If Piper-as-plugin stays N=1 forever, the company-profile shape adds setup cost without benefit. Reversible later.
3. **Whether to add a fork-first preamble (like legal's "is this your area?").** Legal does this because there are 12 sibling plugins; the user might be in the wrong one. PM has N=1, so no fork to make. Skipped, but if Piper grows skill families (founder-mode / PA-mode / publishing-mode as separate plugins later), this preamble becomes useful.

## Status at handoff

Built. Not yet tested end-to-end (no install attempted from this session — the test invocation is for PA per the report's (b) section). Committed and pushed to skunkworks repo.
