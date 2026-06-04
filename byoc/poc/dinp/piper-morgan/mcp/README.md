# Piper Morgan BYOC PoC — MCP server (rung 1)

The thinnest end-to-end proof of the BYOC stack: **skill → MCP → real Piper API.**
Tracking: `mediajunkie/piper-morgan-product#1145`. Scope sketch:
`piper-morgan-product/dev/active/pa-skunkworks-thin-poc-scope-sketch-2026-06-03.md`.

## What it is

One MCP tool — `ask_piper(message)` — forwards a natural-language message to a locally-running
Piper Morgan via `POST /api/v1/intent` (auth-optional, `localhost:8001`). Python; deps are inline
(PEP-723), so `uv run server.py` self-bootstraps `mcp` + `httpx` — no separate venv to manage.

## Rung-1 acceptance test (the gate)

**Prereqs**: `uv` installed; Piper Morgan running locally —
`cd piper-morgan-product && python main.py` (port 8001).

1. **Server runs standalone** (sanity):
   `uv run byoc/poc/dinp/piper-morgan/mcp/server.py` — should start an MCP stdio server (no crash;
   Ctrl-C to exit).
2. **Plugin install** (CLI path, per sub-pass 4.a):
   `claude --plugin-dir /Users/xian/Development/piper-morgan-skunkworks/byoc/poc/dinp/piper-morgan/`
3. **In that Claude session**: confirm the `piper-morgan` MCP server connects and exposes `ask_piper`,
   then ask a conversational PM question and verify the response routes **MCP → `/intent` → Piper**
   (the `--- full /intent response ---` block confirms it hit the real API, not generic Claude).

If the path in `.mcp.json` (`${CLAUDE_PLUGIN_ROOT}/mcp/server.py`) doesn't resolve on install,
capture it as the next install-iteration lore (cf. 4.a's `notes/poc-finding-001-cli-install-paths.md`)
— that's exactly the kind of finding this rung exists to surface.

## Scope guard

Conversational **ask/propose** only (not full-engine execution). No auth, no remote, no `/insights`
(rung 2). The skill on top (`ask_piper` passthrough → later the profile-reading B+C version) is the
next increment once this rung passes.
