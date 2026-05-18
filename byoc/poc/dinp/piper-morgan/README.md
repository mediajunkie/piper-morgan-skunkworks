# piper-morgan plugin (PoC v0.1)

Calibration-heavy PM plugin. Built as a skunkworks PoC to test whether Piper Morgan's distinctive value — the calibration and voice that make outputs feel like a colleague who knows you, not generic PM templates — can be expressed as an Anthropic plugin with a thin-skills-over-rich-config shape.

This is **sub-pass 4.a** of the BYOC PoC build. It ships the plugin scaffold + Feature 1 (`cold-start-as-pm-profile`) only. Features 2 (insight-journal-flat-file) and 3 (composting-via-dreams-mcp) are deliberately not built yet — separate sub-passes.

## What's in this version

- `.claude-plugin/plugin.json` — plugin manifest
- `CLAUDE.md` — plugin root template (the structure the cold-start populates, with `[PLACEHOLDER]` markers)
- `skills/cold-start-interview/SKILL.md` — the single load-bearing skill in v0.1
- `.mcp.json` — empty `mcpServers` shell, ready for sub-pass 4.c to extend
- `README.md` — this file

## What this plugin does NOT have yet

- `/piper-morgan:journal` and `/piper-morgan:reflect` — sub-pass 4.b
- `/piper-morgan:compost` MCP tool wrapping Anthropic Dreams API — sub-pass 4.c
- `--check-integrations` flag on cold-start — deferred (no real integration probing in v0.1)
- Any real MCP server connections — `.mcp.json` is a shell

These are deliberate cuts per the BYOC scope synthesis (build-less discipline: scaffold + Feature 1 first, gate on whether the calibration shape holds, only then add features).

## Install (local development)

From the directory containing the plugin:

```
/plugin marketplace add /Users/xian/Development/piper-morgan-skunkworks/byoc/poc/piper-morgan
```

(For PoC iteration. For real distribution we'd add a `marketplace.json` and install via marketplace name.)

Then in a Claude Code session:

```
/plugin install piper-morgan@<marketplace-name>
```

Restart the session. The plugin will be available.

## First run

```
/piper-morgan:cold-start-interview
```

The interview takes ~10-15 minutes. It asks ONE question per turn (serial, not batched) and writes:

- `~/.claude/plugins/config/dinp/piper-morgan/CLAUDE.md` — your PM profile
- `~/.claude/plugins/config/dinp/company-profile.md` — cross-context profile (shared with any future sibling Piper plugins)

Both are plain-text files you can edit directly for small changes. Re-run with `--redo` to re-interview from scratch (the prior version is backed up).

## Design notes (PoC-specific)

- **Serial questions, not batched.** This inverts the legal-prior cold-start's batching pattern. The PoC is testing whether serial-decisions actually works as a conversational pattern in plugin form. Either-outcome-is-signal: if it works, basis for refinement; if it doesn't, finding is "batching might be load-bearing for plugin-shape interviews."
- **PM-profile vocabulary, not founder-profile.** The synthesis spec's earlier draft used "founder-profile"; PM ratified the more general "PM profile" framing on 2026-05-17. Founder-PM is treated as one role-shape among several captured in Q1.2.
- **No PM-API dependency.** The plugin is self-contained. State lives in the plugin's config files. The "pin to PM-API upstream" mappings from sub-agent 2's analysis are future-direction notes, not built dependencies for this PoC.
- **Anti-sycophancy in the cold-start itself.** The interview demonstrates the voice rules it's collecting. If the cold-start opens with "Great question!" while collecting the user's anti-sycophancy preference, that's a tell.

## Path conventions

The plugin uses `dinp/piper-morgan` as its config path (`~/.claude/plugins/config/<marketplace>/<plugin>/CLAUDE.md`). The marketplace slug is `dinp` (designinproduct — xian's umbrella org); the plugin slug is `piper-morgan`. If the marketplace ships under a different slug later, every reference in the plugin needs the path updated.

## Reporting issues

This is a PoC. Findings live in `/Users/xian/Development/piper-morgan-skunkworks/byoc/notes/`. If something doesn't work, the value is in the finding — surface it.
