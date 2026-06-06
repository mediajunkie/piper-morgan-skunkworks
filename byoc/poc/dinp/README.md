# Design in Product (dinp) — plugin marketplace

This directory is the **Design in Product plugin marketplace**: the umbrella catalog for xian's
PM-shaped and product-ops Claude plugins. A *marketplace* is the wrapper level above an individual
plugin — one `.claude-plugin/marketplace.json` lists multiple plugins, each living in its own
subdirectory with its own `.claude-plugin/plugin.json`.

> **Status:** skunkworks-staged (under `byoc/poc/`). The structure is canonical and used going forward;
> the *location* is interim. Graduation out of `byoc/poc/` and to a hosted marketplace is planned — see
> "Graduation & hosting" below.

## Plugin roster

| Plugin | Status | What it is |
|---|---|---|
| **piper-morgan** | 🟢 live (v0.4) | Piper Morgan as a Claude plugin — PM calibration profile + ask/consult skills over a local MCP server. |
| **klatch** | ⚪ planned | A Klatch plugin (the "side project to the side project"). Not yet scaffolded. |
| **cross-pollinator** | ⚪ planned | A cross-pollination plugin (the daily agent-newsletter / insight-sharing discipline). Not yet scaffolded. |

Only **live** plugins are registered in `marketplace.json` — registering a plugin whose source dir
doesn't exist breaks validation/install. Planned siblings are documented here and added to the manifest
when they're real.

## Conventions for adding a sibling plugin

The structure is designed so adding klatch or cross-pollinator is mechanical:

1. **One directory per plugin** under `dinp/`: `dinp/<plugin-name>/`.
2. Each plugin dir contains: `.claude-plugin/plugin.json` (manifest), `.mcp.json` (if it ships an MCP
   server), `skills/<name>/SKILL.md` (one dir per skill), `mcp/server.py` (the server), `README.md`.
3. **Plugin `name` = lowercase-hyphenated slug** — it's the identifier, tied to the config path and the
   skill namespace (`/<plugin-name>:<skill>`). Don't change it after release.
4. **Manifest `description` stays short** (≤ ~480 chars). Claude Desktop enforces a description
   max-length (cap is between 486 and 578 chars) that the CLI `claude plugin tag` validator does NOT —
   a long description installs fine via CLI but fails "Plugin validation failed" in Desktop. Test on
   Desktop, not just CLI.
5. **Register it in `marketplace.json`** with `source: { source: "local", path: "./<plugin-name>" }`.

## Shared cross-context profile

Sibling plugins share a single **company profile** at
`~/.claude/plugins/config/dinp/company-profile.md` (one level above each plugin's own config dir,
`~/.claude/plugins/config/dinp/<plugin-name>/`). It holds cross-plugin facts — who you are, the projects
you work across, your relationship to your team — so a second DinP plugin you install reads it and skips
the identity questions. Per-plugin config (voice rules, routing, integrations) stays in each plugin's own
`<plugin-name>/CLAUDE.md`. Config is **owned and read/written by each plugin's MCP server** (not the
agent touching `~/.claude` directly), which is what makes setup work on sandboxed surfaces like Cowork.

## Install paths

| Path | Status | Notes |
|---|---|---|
| `claude --plugin-dir dinp/<plugin>` | ✅ works | Canonical CLI install of a single plugin (per session). |
| Desktop zip (single plugin) | ✅ works | Zip a single plugin dir; install in Claude Desktop. The tested distribution path today. |
| `/plugin marketplace add <dir-or-url>` | 🔴 not yet | The marketplace/remote-source install path. Fails on current CLI ("source type your Claude Code version does not support") and needs published-catalog hosting. This is what graduation/hosting unlocks. |

## Graduation & hosting

This marketplace is the structure we use from now on, but two moves are still ahead (tracked as
exploration, not yet built):

1. **Graduate out of `byoc/poc/`** to a stable home (its own repo or a top-level path) once the PoC
   framing no longer fits.
2. **Hosting** — part of the MVP distribution work: hosting the MCP server(s), the plugins, and the
   marketplace catalog itself so `/plugin marketplace add` works against a real URL and users don't each
   need a local server + `--plugin-dir`. See the product-repo exploration doc for the hosted-solutions
   plan.
