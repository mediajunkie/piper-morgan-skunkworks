# BYOC PoC Tracker

PA daily status + subagent dispatch state + open questions + finding log for the BYOC skunkworks project.

---

## Status

**Phase**: Step 1 — hosted endpoint connection (no auth for now; OAuth deferred)
**Last PA touch**: 2026-06-20
**Current PoC**: `byoc/poc/dinp/piper-morgan/` — plugin.json v0.4.0, MCPB v0.1.1, all 5 tools register
**Product version**: v0.8.8 on `production` branch; `alpha.pipermorgan.ai` hosting on DigitalOcean Droplet (PM-owned); deploy pending Lead Dev
**Next gate**: Droplet deploy → PM tests `ask_piper` against hosted backend
**Alpha skills**: `piper-morgan-skills.zip` ready on PM's Desktop; tester email v5 ready to send
**Repo**: https://github.com/mediajunkie/piper-morgan-skunkworks (private)

### Phase summary

Step 0 (May 2026): Setup, subagent research, cold-start scaffold — complete.
Step 1 (now): Connect the existing PoC plugin to a hosted backend endpoint rather than localhost. No auth needed yet — that's a separate issue. Gated on Fly.io hosting (#1278 in product repo) or a temporary hosted endpoint.

The BYOC key-passing question (user provides their own Anthropic API key) is NOT the current blocker. That can be added later. What we need first: a non-localhost `PIPER_BASE_URL` the plugin can connect to. Once that works, the PoC proves the full client → hosted backend chain.

---

## Open questions for PM

1. **Hosted endpoint** — PM's DigitalOcean Droplet confirmed as hosting target (not Fly.io). Lead Dev working on deploy mechanism. Options to unblock PoC test before Droplet is live: ngrok or Tailscale to `localhost:8001`.
2. **MCPB clean-machine test** — PM needs to run this: macOS, no system Python, current Claude Desktop. Gate for #1282 marketplace submissions.
3. **Piper Open cross-pollination mechanism** — proposed: shared `hosted-mcp/` surface in skunkworks. Is Janus still active as cross-project coordinator, or is PM the only bridge right now?
4. **1.0 scoping questions** — metering/rate-limiting, subscription model, GDPR. See identity decision doc.

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

### 2026-06-19 (evening — v0.1.1 clean install confirmed)

- v0.1.1 install: uninstall of v0.1.0 required (mcpb does NOT upgrade in place — uninstall first, then double-click). After uninstall + reinstall: **server connects, all 5 tools register, permissions UI renders correctly**.
- **Tool permissions finding**: all 5 tools (ask_piper, get_profile, save_profile, get_company_profile, save_company_profile) appear in the "Tool permissions" panel with auto/approval/deny controls per tool. This works correctly with mcpb. PM noted PO has struggled with this in their plugin bundle — mcpb format handles it correctly. Cross-pollination note sent to PO.
- **Next gate**: test `ask_piper` with Piper server running at localhost:8001.

### 2026-06-20 (Saturday morning — alpha skills packaged + tester email ready)

- **v0.8.8 released** (shipped Jun 19–20): tags pushed, GitHub Release live, `production` branch at v0.8.8. ALPHA_QUICKSTART prose updated. Deployment to `alpha.pipermorgan.ai` pending Lead Dev (Droplet hosting confirmed — not Fly.io; Lead Dev working on deploy mechanism tonight).
- **#1289 standup skill**: MCP standup skill migrated to honest engine (`build_user_standup_summary`); 62/62 tests pass. Remaining callers (route + handler) tracked for later migration.
- **Alpha tester email v5 ready** (`dev/2026/06/19/alpha-tester-email-draft.md`): curl-path scope clarified (Claude Code only — the .skill zip works everywhere). Email can now go out.
- **`piper-morgan-skills.zip` packaged** on Desktop (30K, 5 skills: sprint-plan, stakeholder-update, draft-issue, draft-spec, synthesize-feedback). Verified all 5 .skill files in `~/Desktop/piper-morgan-skills/` open correctly; README descriptions are clean.
- **curl install path verified live**: `https://raw.githubusercontent.com/mediajunkie/piper-morgan-product/main/.claude/skills/piper-sprint-plan/SKILL.md` returns correctly.
- **`cut-release` skill created** (`.claude/skills/cut-release/SKILL.md`) — prevents "bumped version but left prose body stale" failure mode; splits doc updates into explicit version-string + prose-body tasks.
- **PA role portfolio filed** (`docs/briefing/ROLE-PORTFOLIO-PA.md`) — self-authored v0.1 against the trust framework. Sent to Exec/HOST/PM.
- **Blocked**: MCPB plugin → hosted backend test (waiting on Droplet deploy); MCPB clean-machine test (PM to run); Fly.io (#1278) Lead Dev backlog.
- **Last PA touch**: 2026-06-20

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

### Gate 3 — Identity approach (Jun 19, 2026)
**Decision**: PM-ratified.
- PoC: no auth (open endpoint)
- MVP / beta (0.9.0): UUID bearer — generated at first MCP connect, scoped per device, persisted in plugin config
- Production (1.0): email + magic link, Piper-native — email is account recovery + multi-device bridge; UUID becomes account ID after verification
- Post-1.0: "Login with..." as optional convenience overlay, NOT the foundation
- Principle: no building identity on another company's ID
- Full decision doc: `byoc/notes/identity-decision-2026-06-19.md`

---

## Finding log

### Finding #5 — Piper Open's hosted MCP implementation (reference for Piper Morgan)
**Date**: Jun 19, 2026 | **Source**: openlaws-research-agent repo, PR #154 + server.py

The openlaws-research-agent just shipped a complete Streamable HTTP hosted MCP server on Fly.io. This is a reference implementation for Piper Morgan's same problem. Key patterns:

**Multi-tenant token pass-through (the core pattern):**
```python
_caller_token: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "openlaws_caller_token", default=None
)
```
`InboundAuth` (pure-ASGI middleware — NOT Starlette's `BaseHTTPMiddleware`) extracts the bearer token from each request and stores it in a `ContextVar`. The tool handlers read it via `_caller_token.get()`. This is how one process serves many customers without a shared credential.

**Critical: pure-ASGI, not BaseHTTPMiddleware.** BaseHTTPMiddleware runs the downstream app in a separate task, so context vars don't propagate. Must use pure-ASGI middleware for this pattern to work.

**No server-side stored API keys.** For OpenLaws, the customer's OpenLaws API key IS the bearer token — the MCP passes it upstream per-request. No secrets stored server-side. For Piper Morgan, our UUID bearer plays the same role: the UUID IS the per-customer credential.

**DNS rebinding protection:** `TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=[...])` — must set `OPENLAWS_ALLOWED_HOSTS` env var on Fly.io. FastMCP `stateless_http=True` mode.

**Fly.io hardening patterns:**
- `/health` endpoint answers 200 without auth (Fly's health check may not send the app hostname)
- Graceful shutdown: `uvicorn.run(..., timeout_graceful_shutdown=25)` 
- Structured access log with `hashlib.sha256(token).hexdigest()[:8]` fingerprint (never logs raw token)
- `OPENLAWS_ALLOWED_HOSTS` + `OPENLAWS_ALLOWED_ORIGINS` env vars for host-protection

**Applicable to Piper Morgan:** Our `mcp/server.py` (currently stdio/local) can adopt the same `main_http()` entry point + `InboundAuth` pattern for the hosted path. UUID bearer replaces the OpenLaws API key as the pass-through credential. See `byoc/notes/piper-morgan-hosted-distribution-guide-2026-06-19.md` for updated guide.
