# hosted/ — Phase 2 skunkworks: hosted distribution experiments

This directory tracks experiments toward a publicly-listable Piper Morgan plugin distribution.
The goal: a tester installs once from a marketplace URL and gets updates automatically,
with no shared credentials in any publishable file.

## What's here

**P1 — auth-decoupled plugin** (`byoc/dist/piper-morgan/`):
The `.mcp.json` no longer embeds credentials. The MCP server reads `PIPER_BASE_URL` from the
environment (defaulting to `http://localhost:8001` if unset). Testers supply their own endpoint;
no secret lives in the repo.

**P2 — GitHub-source marketplace scaffold** (`byoc/poc/dinp/.claude-plugin/marketplace.json`):
The marketplace entry now uses `git-subdir` source pointing at this repo, so Claude Code can
install and auto-update the plugin directly from GitHub — no zip hand-off required.

**P3 — MCP-server-owns-config** (in progress separately, tracked in piper-morgan-product#1157):
Config lives with the MCP server process, not in agent-writable paths — making the plugin
work correctly on both Claude Code and Claude Cowork surfaces.

## How these relate to the plan

Marketplace listing (public GitHub repo) → `PIPER_BASE_URL` points at `alpha.pipermorgan.ai`
→ tester supplies the URL in their shell environment → no embedded credentials anywhere.
This is the on-ramp to the BYO-key / hosted-alpha flow documented in #1162.
