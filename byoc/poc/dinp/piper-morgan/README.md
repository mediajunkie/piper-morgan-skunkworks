# Piper Morgan plugin (BYOC PoC v0.2)

**Bring your PM assistant into your own chat.** This is a thin proof-of-concept that packages Piper
Morgan — a product-management assistant — as a Claude Code / Claude Desktop plugin: three small skills
over a local connection to a running Piper Morgan server. The idea (Bring Your Own Chat) is that you
don't need a separate Piper app — you talk to Piper inside the Claude you already use.

> **A couple of concepts, introduced** (so the rest reads clearly):
> - **MCP server** — a small local program that lets Claude call out to another system. This plugin
>   includes one that forwards your questions to your running Piper Morgan.
> - **Piper's "Conscious Floor"** — when Piper doesn't have the information to answer well, it's designed
>   to *say so honestly and ask for what it needs*, rather than guess. You'll see this below: the
>   `consult-piper` skill notices when Piper hits that limit and fills the gap from your GitHub.

## The three skills

| Skill | What it does |
|---|---|
| **`/piper-morgan:meet-piper`** | A one-question-at-a-time interview that learns how *you* work as a PM (voice, escalation, project portfolio, pace) and writes it to a profile the plugin reuses. Run this first. |
| **`/piper-morgan:ask-piper`** | Relays a single PM question to your locally-running Piper and shows you Piper's own answer. Thin and literal — a quick consult. |
| **`/piper-morgan:consult-piper`** | The fuller working session: asks Piper, and if Piper says it lacks the context to answer (e.g. "I don't have your current projects"), it gathers exactly that from your GitHub, re-asks Piper, and gives you a grounded answer — clearly labeling what came from Piper vs. what it gathered for you. |

The skills are **layered**: `consult-piper` builds on the same underlying connection `ask-piper` uses.

## Prerequisites

1. **A local Piper Morgan server running.** The plugin talks to Piper at `http://localhost:8001`. Start
   it from the Piper Morgan repo: `python main.py` (default port 8001). If it's not running, the skills
   will tell you so plainly rather than make something up.
2. **`uv`** installed (the MCP server self-bootstraps its Python dependencies via `uv` — no separate
   virtualenv to manage).
3. For `consult-piper`'s GitHub gathering: a connected GitHub MCP **or** the `gh` CLI authenticated
   (`gh auth status`).

## Install

### Claude Code (CLI) — the tested path
Start Claude Code with the plugin loaded:

```bash
claude --plugin-dir /path/to/piper-morgan-skunkworks/byoc/poc/dinp/piper-morgan
```

Each new `claude` session needs the flag. Optional convenience alias:

```bash
alias claude-piper="claude --plugin-dir /path/to/.../byoc/poc/dinp/piper-morgan"
```

### Claude Desktop (from a zip) — newer test surface
The plugin can also be packaged as a zip and installed in Claude Desktop. This path is **less battle-
tested** than the CLI: the MCP server's file path resolution (`${CLAUDE_PLUGIN_ROOT}/mcp/server.py`) and
the `uv` / local-Piper prerequisites may behave differently from a zip install. **If something doesn't
resolve, that's a finding, not a failure** — capture it (see "Reporting findings").

> **Why not `/plugin marketplace add`?** The marketplace install path needs public-catalog publishing,
> which isn't set up for this PoC. `--plugin-dir` (and the zip) are the canonical install paths for an
> unpublished plugin. Full lore: `byoc/notes/poc-finding-001-cli-install-paths.md`.

## First run

```
/piper-morgan:meet-piper
```

~10–15 minutes, one question per turn. It writes two plain-text files you can edit directly:
- `~/.claude/plugins/config/dinp/piper-morgan/CLAUDE.md` — your PM profile
- `~/.claude/plugins/config/dinp/company-profile.md` — a shared cross-context profile

Re-run with `--redo` to start over (the prior version is backed up first).

Then try:
```
/piper-morgan:ask-piper        e.g. "ask Piper what's the status of issue 1142"
/piper-morgan:consult-piper    e.g. "ask what I should focus on today"
```

`consult-piper` is the one that shows the payoff loop: watch it notice Piper's gap, gather your GitHub
issues, and come back with a grounded answer + honest provenance.

## What's in this version (v0.2)

- `.claude-plugin/plugin.json` — manifest
- `CLAUDE.md` — plugin profile template (populated by `meet-piper`)
- `skills/meet-piper/`, `skills/ask-piper/`, `skills/consult-piper/` — the three skills
- `mcp/server.py` + `.mcp.json` — the local MCP server (`ask_piper` tool → Piper's `/api/v1/intent`)
- `mcp/README.md` — MCP server details + test recipe

## Deliberately not here yet (roadmap, not gaps)

- Gathering context from sources beyond GitHub (Calendar, Notion, Gmail, Slack) — later increments.
- A structured "here's exactly what I'm missing" signal from Piper (today `consult-piper` infers the
  gap from Piper's prose; a structured version comes later).
- Profile-aware voice shaping; insight-journal and composting features.

These are sequencing choices (build the thin slice, prove it, then extend), not missing pieces.

## Reporting findings

This is a PoC — when something doesn't work, the **finding is the value**. Capture it in
`byoc/notes/`, or as a tracked issue in the Piper Morgan product repo. Install-path quirks (especially
on the Desktop/zip path) are exactly the kind of thing worth writing down.
