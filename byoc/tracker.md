# BYOC PoC Tracker

PA daily status + subagent dispatch state + open questions + finding log for the BYOC skunkworks project.

---

## Status

**Phase**: Step 1 — hosted endpoint connection (no auth for now; OAuth deferred)
**Last PA touch**: 2026-06-19
**Current PoC**: `byoc/poc/dinp/piper-morgan/` — plugin.json v0.4.0, MCP server working against local backend
**Next gate**: PM runs hosted-endpoint test once Fly.io backend is reachable
**Repo**: https://github.com/mediajunkie/piper-morgan-skunkworks (private)

### Phase summary

Step 0 (May 2026): Setup, subagent research, cold-start scaffold — complete.
Step 1 (now): Connect the existing PoC plugin to a hosted backend endpoint rather than localhost. No auth needed yet — that's a separate issue. Gated on Fly.io hosting (#1278 in product repo) or a temporary hosted endpoint.

The BYOC key-passing question (user provides their own Anthropic API key) is NOT the current blocker. That can be added later. What we need first: a non-localhost `PIPER_BASE_URL` the plugin can connect to. Once that works, the PoC proves the full client → hosted backend chain.

---

## Open questions for PM

1. **Fly.io timing** — #1278 gates the hosted endpoint. Is this being frontloaded before M5, or should we use a different temporary hosted endpoint for the PoC?
2. **Subagent 3 gate test still owed** — the cold-start-as-PM-profile scaffold in `byoc/poc/piper-morgan/` (commit `a018b4d`) has never been run as a behavioral test by PM. Low urgency now that v0.4.0 exists in `dinp/`, but worth noting.
3. **Piper Open cross-pollination** — both Piper Morgan and Piper Open are solving the hosted MCP problem in parallel. Need a mechanism to share notes (see Finding #4).

---

## Subagent dispatch state

| Subagent | Status | Started | Returned | Validated | Notes |
|---|---|---|---|---|---|
| 1 — Anthropic plugin architecture study | **complete + PA-validated** | 2026-05-16 ~14:00 | ~14:05 | 2026-05-16 ~14:30 | Memo at `notes/subagent-1-anthropic-plugin-architecture-study-2026-05-16.md`. |
| 2 — PM codebase extraction analysis | **complete + PA-validated** | 2026-05-16 ~14:35 | ~14:42 | 2026-05-16 ~14:55 | Memo at `notes/subagent-2-pm-extraction-analysis-2026-05-16.md`. Proposed PoC triangle: cold-start-as-founder-profile + insight-journal-flat-file + composting-via-dreams-mcp. |
| 3 (sub-pass 4.a) — scaffold + cold-start-as-pm-profile | **shipped; PM gate test still owed** | 2026-05-17 ~08:00 | ~08:08 | structural ✓; behavioral = PM gate | Code at `byoc/poc/piper-morgan/`; commit `a018b4d`. Superseded in practice by v0.4.0 in `dinp/`. |

---

## Daily log

### 2026-05-16 (Saturday)

- 13:15 — PA created local repo + byoc/ structure scaffold
- 13:25 — gh found pre-installed; authenticated as mediajunkie
- 13:27 — GitHub repo created via gh
- 13:30 — Anthropic priors cloned as git submodules (claude-for-legal, knowledge-work-plugins)
- 13:45 — Architect heads-up memo shipped
- ~14:00–14:55 — Subagents 1 + 2 dispatched and validated (plugin architecture + PM codebase extraction)

### 2026-05-17 (Sunday)

- ~08:00–08:15 — Subagent 3: scaffold + cold-start-as-pm-profile shipped (`a018b4d`). Awaits PM gate test.

### 2026-06-00s (intervening — reconstructed from dist/ artifacts)

Significant PoC evolution happened off-tracker. Evidence in `byoc/poc/dist/`:
- `piper-morgan-plugin-v0.2.0.zip` through `v0.4.0.zip` — four plugin iterations
- `piper-morgan-alpha-DISTRIBUTION.zip` — alpha distribution package
- `piper-morgan-alpha-byoc-poc.zip` — tagged BYOC PoC snapshot
- `piper-morgan-alpha-hosted.zip` — hosted variant snapshot

Current state of `byoc/poc/dinp/piper-morgan/` (plugin.json v0.4.0):
- MCP server at `mcp/server.py` (FastMCP, uv, PEP-723 inline deps)
- Tools: ask_piper, get_profile, save_profile, get_company_profile, save_company_profile
- Config: server-owned at `~/.claude/plugins/config/dinp/` (fixes #1157 Cowork FS access)
- Backend: `PIPER_BASE_URL` env var, defaults to `http://localhost:8001`
- Skills: meet-piper, ask-piper (in `skills/`)
- **Gap**: PIPER_BASE_URL is localhost only — no hosted endpoint yet

### 2026-06-18–19 (PA sessions — skills alpha + BYOC planning)

- Skills alpha: 5 piper-* skills shipped to 11 external alpha testers (Jun 19). Skills are a separate distribution path from the plugin — they install via .skill files, not the plugin.
- Plugin naming: CXO ratified big-endian convention (`piper-ask`, `piper-consult`, `piper-meet` for plugin tools; `piper-sprint-plan` etc. for PM-facing skills)
- MCPB: Python/uv confirmed by Arch (Jun 18). BYOC-DIST epic filed as #1282 in product repo.
- Credential decoupling (#1162) must ship before Fly.io (#1278). Order: #1162 → #1278 → #1282.
- **PM decision on auth**: skip auth for now; get hosted infrastructure working first. OAuth is the mechanism for metering + returning-user-identity (Piper Open finding — see Finding #4), but that's a separate issue. The immediate PoC goal is a working plugin ↔ hosted backend connection without auth.
- **Piper Open parallel track flagged**: PM surfaced that Piper Open / OpenLaws project is solving the same hosted MCP problem independently. Cross-pollination mechanism needed.

---

## Finding log

### Finding #1 — Plugin config must be server-owned (not agent-owned)
**Date**: May 2026 | **Source**: Subagent 3 + #1157

Plugin config cannot be written by the Claude Code agent in Cowork (sandboxed FS). Solution: MCP server owns the config at `~/.claude/plugins/config/dinp/`. Server has normal process FS access on any surface. Implemented in server.py v0.4.0.

### Finding #2 — .skill format: one file per skill, YAML block scalar required
**Date**: Jun 18–19, 2026 | **Source**: PA alpha skills work

Claude Desktop upload accepts one .skill file per skill. Multi-skill bundles fail silently. YAML description fields containing colon-space sequences (`: `) MUST use `>-` block scalar — plain scalar breaks YAML parsing with "mapping values are not allowed here." Fixed in all 5 alpha skills.

### Finding #3 — MCP server runs via `uv run server.py` (no venv needed)
**Date**: May 2026 | **Source**: server.py PEP-723 inline deps

The plugin's MCP server uses uv's inline script metadata for dependency declaration. `uv run server.py` self-bootstraps — no separate venv or install step. This is the distribution model for the MCPB bundle.

### Finding #4 — Piper Open: OAuth needed for metering + returning-user-identity, NOT for basic key-passing
**Date**: Jun 19, 2026 | **Source**: PM cross-project update

Piper Open / OpenLaws project worked through the same problem. Key-passing works technically. The OAuth challenge surfaced when trying to meter usage and identify returning users (same customer across sessions). Without OAuth, you can pass a key but you can't associate it with a persistent user identity or enforce rate limits per customer. This is a separate problem from the basic BYOC mechanic — it matters for the hosted multi-tenant product but not for the PoC. **Decision**: no auth for the PoC; OAuth for metering/identity is a later issue.

---

## Gate decisions

### Gate 1 — PoC scope (ratified May 2026)
**Decision**: Cold-start-as-founder-profile + insight-journal-flat-file + composting-via-dreams-mcp triangle. Confirmed by subagent 2 analysis.

### Gate 2 — Auth for PoC (Jun 19, 2026)
**Decision**: Skip auth for now. No BYOC API key field in user_config needed for the PoC. The PoC just needs a non-localhost hosted endpoint. OAuth deferred to a separate issue.
