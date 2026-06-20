# Piper Morgan — Hosted MCP Distribution: What We Know

**Audience**: PO (Piper Open / OpenLaws project), Janus, any cross-project reader
**Date**: 2026-06-19
**Author**: PA (Piper Alpha)
**Status**: Current as of Jun 19 — will be updated as we learn more

This is the cross-pollination guide for the hosted MCP distribution problem. It summarizes what we've tried, what works, what doesn't, and where we're still figuring things out.

---

## The problem we're solving

We want external users (not just xian) to be able to:
1. Find and install Piper Morgan
2. Have it connect to a hosted Piper backend (not a local server)
3. Use it across Claude Desktop surfaces (Chat, Cowork, Code)

---

## Distribution scenarios — the four valid states

A user can have any combination of skills and MCP connector installed. All four states are coherent; none is "broken." Each incomplete state points toward the complete one.

| Scenario | What's installed | Experience | Self-completion signal |
|---|---|---|---|
| **1 — Skills only** | Work skills (`.skill` files) | Claude-level PM help via slash commands; no Piper backend routing | Bridge skills not included — this package is complete for what it is |
| **2 — MCP only** | Plugin (`.mcpb`) | `ask_piper` and profile tools available; Claude may call them spontaneously | `ask_piper` response can hint that skills exist and offer install guidance |
| **3 — Skills + MCP** | Work skills + bridge skills + plugin | Full local experience: Piper's conscious floor + Claude PM execution + profile awareness | No recommendation needed — complete |
| **4 — Plugin bundle** | Single `.mcpb` containing skills + MCP | One-install = Scenario 3, in Cowork and Code | Marketplace target |

**The self-completing property**: each half-install recommends the other half.
- Skills-only → bridge skills detect absent connector → explain + offer install link
- MCP-only → `ask_piper` response signals that PM skills would unlock more → offer install
- Neither direction is a broken state, just an incomplete one that points toward the full experience.

**Skill categories within the collection:**

*Work skills* (`piper-draft-issue`, `piper-sprint-plan`, `piper-stakeholder-update`, `piper-draft-spec`, `piper-synthesize-feedback`) — standalone Claude-PM skills. Work without the plugin; optionally enhanced if `ask_piper` is present.

*Bridge skills* (`ask-piper`, `consult-piper`, `meet-piper`) — route through `ask_piper`. If connector absent, detect it and offer install; don't fail silently. Distributed alongside work skills in Scenario 3/4.

All skills follow the same distribution format (`.skill` files or manifest declaration) — the connector-presence check at runtime creates the capability tiers, not separate distribution paths.

**`meet-piper` note**: cold-start onboarding skill — run once to populate the PM profile. Likely better suited as a plugin onboarding step triggered on first `ask_piper` call with no profile, rather than a regular-use slash command. Deferred to a later rung.

---

## Layer 1: Skills (slash commands)

**What works:**
- `.skill` format — ZIP containing one skill directory with `SKILL.md` + optional `README.md`
- Install: double-click the `.skill` file → Claude Desktop opens "Add to library" dialog → click yes → skill appears as slash command
- Works in Chat, Cowork, and Code
- Skills install to `~/.claude/skills/`
- `SKILL.md` frontmatter: `name` (required, lowercase alphanumeric + hyphens) + `description` (required, max 1024 chars)

**Critical gotcha — YAML block scalar:**
Description fields containing colon-space (`: `) MUST use `>-` block scalar, NOT plain scalar. Example:
```yaml
description: >-
  Plan a sprint from your backlog. Trigger phrases: "let's plan the sprint",
  "help me scope this".
```
Plain scalar silently fails YAML parsing server-side — the upload dialog shows all skills correctly but the "Add to library" button fails with "Skill upload failed."

**What doesn't work:**
- Multi-skill bundles: uploading a ZIP with multiple `.skill` files fails. One `.skill` per skill, installed individually.
- Distribution workaround: put all `.skill` files in a ZIP for users to download + unzip + install one-by-one. Not ideal UX.

**Naming convention:**
- Big-endian, namespace-first: `piper-sprint-plan`, `piper-draft-issue`, etc.
- Rationale: appears in slash command as `/piper-sprint-plan` — clear namespace, discoverable

**Shipped:**
- 5 `piper-*` skills to 11 alpha testers Jun 19
- Install script also available: `curl -sSL [url] | bash` installs to `~/.claude/skills/`

---

## Layer 2: Plugin (.mcpb)

**Current state:** provisional, not yet submitted to marketplace. Version v0.4.0 in `byoc/poc/dinp/piper-morgan/`.

**Format:**
- Python/uv approach (confirmed by Arch)
- PEP-723 inline deps: `# dependencies = ["mcp>=1.0", "httpx>=0.27"]` in server.py
- `uv run server.py` self-bootstraps — no separate venv install needed
- `manifest.json` specifies: tools, skills, `user_config`

**`user_config` for API keys:**
```json
"user_config": {
  "anthropic_api_key": {
    "type": "string",
    "description": "Your Anthropic API key",
    "sensitive": true
  }
}
```
`sensitive: true` creates a password-field UX during plugin install. Key is passed to MCP server with each call.

**Server config ownership:**
The MCP server MUST own file-system config (profiles, etc.) — NOT the Claude agent. In Cowork, the agent runs in a sandboxed FS with no real `$HOME`. The server runs as a normal process and can write to `~/.claude/plugins/config/...`. This is the fix for cross-surface compatibility (issue #1157).

**Known mcpb bug:**
- GitHub issues #84/#96 on `modelcontextprotocol/mcpb`: compatibility checker rejects Python/uv bundles on machines without `uv` in PATH, even when uv IS installed (PATH detection failure)
- Closed "not planned" by mcpb maintainers
- Workaround: clean-machine test on current Claude Desktop (pending PM action). If it fails, fallback is Node.js rewrite (Arch pre-authorized, ~3-5hr effort)

**Backend connection:**
- `PIPER_BASE_URL` env var defaults to `http://localhost:8001`
- For hosted: needs to point at the hosted endpoint
- Current blocker: credential decoupling (#1162) + Fly.io hosting (#1278) + Caddy gate-removal decision (Arch/LD)

**Marketplace targets:**
- Smithery listing (smithery.yaml ready)
- Claude Desktop Extensions directory
- MCP Registry / Anthropic's community catalog
- All gated on: clean-machine test + package finalized

---

## Layer 3: Hosted backend

**Current state:**
- Server runs locally at `localhost:8001` (Flask/FastAPI)
- Also runs at `alpha.pipermorgan.ai` (PM's personal VPS — fine for alpha, not for beta)
- Target: Fly.io (`server.pipermorgan.ai`)

**Dependency chain:**
```
#1162 (cred decoupling) → #1278 (Fly.io) → #1282 (marketplace)
```

**Caddy gate:**
There's a Caddy gate-removal decision pending (Lead Dev 6/17 memo). Caddy currently acts as a reverse proxy / auth gate. Decision: whether to remove it for the hosted deployment. Arch/LD need to make this call before Fly.io work can proceed.

**What Fly.io work involves:**
- `fly.toml` committed to repo
- Fly secrets for environment variables (Anthropic key, PostgreSQL connection)
- Domain: `server.pipermorgan.ai` → Fly.io app
- Health check at `/health`
- PostgreSQL on Fly Postgres or stay on current DB
- Redis + ChromaDB: confirm if stateless-enough to skip
- Estimated effort: ~2-4 hours (specced as coding agent work once Caddy decision is made)

**Reference implementation — Piper Open (openlaws-research-agent, PR #154):**

Piper Open just shipped a complete hosted Streamable HTTP MCP on Fly.io. Their pattern is directly applicable to our MCP server (`byoc/poc/dinp/piper-morgan/mcp/server.py`).

The multi-tenant auth pattern (copy-paste adapted for Piper Morgan):
```python
import contextvars, hashlib, time
from starlette.responses import JSONResponse

_caller_token = contextvars.ContextVar("piper_caller_token", default=None)

class InboundAuth:
    """Pure-ASGI front door — NOT Starlette BaseHTTPMiddleware (contextvars don't propagate in BMH)."""
    def __init__(self, app): self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send); return
        if scope.get("path") == "/health":
            await JSONResponse({"status": "ok"})(scope, receive, send); return
        auth = dict(scope.get("headers") or []).get(b"authorization", b"").decode()
        token = auth.split(" ", 1)[1].strip() if auth.lower().startswith("bearer ") else None
        if not token:
            await JSONResponse({"error": "missing bearer token"}, status_code=401)(scope, receive, send)
            return
        reset = _caller_token.set(token)
        try:
            await self.app(scope, receive, send)
        finally:
            _caller_token.reset(reset)
```

Then in `ask_piper` and any tool that calls the Piper backend:
```python
token = _caller_token.get()  # the UUID bearer; scopes all data to this customer
headers = {"X-Piper-User-ID": token} if token else {}
```

And the `main_http()` entry point:
```python
def main_http():
    import uvicorn
    mcp = FastMCP("piper-morgan", stateless_http=True, transport_security=_transport_security())
    # ... register tools ...
    app = InboundAuth(mcp.streamable_http_app())
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), timeout_graceful_shutdown=25)
```

**Critical learnings from PO's implementation:**
1. Pure-ASGI middleware is REQUIRED for contextvars to propagate — BaseHTTPMiddleware spawns a separate task and breaks it
2. `/health` must answer without auth (Fly's health check may not include the customer hostname)
3. Never log the raw token — use `hashlib.sha256(token.encode()).hexdigest()[:8]` as a caller fingerprint
4. Set `OPENLAWS_ALLOWED_HOSTS` (→ `PIPER_ALLOWED_HOSTS` for us) for DNS rebinding protection
5. `uvicorn timeout_graceful_shutdown=25` handles Fly rolling deploys cleanly

---

## Layer 4: Auth + Identity

**What we decided (Jun 19):**

| Release | Approach |
|---|---|
| PoC (now) | No auth — open endpoint |
| MVP / beta 0.9.0 | UUID bearer — generated at first MCP connect |
| Production 1.0 | Email + magic link, Piper-native |
| Post-1.0 | "Login with..." optional overlay |

**Principle**: no building identity on another company's ID. Piper-native all the way.

**UUID bearer mechanics:**
- MCP server generates UUID at first `ask_piper` call if none exists
- Persisted at `~/.claude/plugins/config/.../user-id`
- Sent as `X-Piper-User-ID` header with every MCP call
- Backend scopes profile + data to UUID

**UUID bearer limitations (acceptable for MVP):**
- Device-scoped: reinstall = new identity
- No account recovery
- No metering/rate-limiting per customer

**The Piper Open finding:**
Passing API keys works technically. But without OAuth, you can't meter usage per customer or recognize a returning user across sessions. This is the wall PO ran into. For Piper Morgan, we're accepting this limitation at MVP and addressing it at 1.0 via email account.

**Open at 1.0:**
- Metering/rate-limiting without OAuth?
- Subscription model (per-seat, usage-based, flat)?
- GDPR compliance (right-to-deletion needs verified identity)

---

## What we don't know yet

- Does the mcpb compatibility checker pass on a clean macOS machine? (PM to test)
- Caddy gate: remove or keep in hosted deployment? (Arch/LD decision pending)
- MCP pricing model: nobody has answered this yet for Piper Morgan either
- PO / OpenLaws approach to OAuth for MCP: John's implementation — what shape?

---

## Stack diagram

Full HTML diagram at: `docs/internal/architecture/current/diagrams/byoc-stack-2026-06-19.html` (in piper-morgan-product repo, which PO has access to per PM Jun 19).

---

*This guide will be updated as we learn more. Last touch: 2026-06-19.*
