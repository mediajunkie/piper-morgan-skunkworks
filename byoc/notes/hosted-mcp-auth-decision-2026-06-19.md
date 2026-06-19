# Hosted MCP: Auth Decision + Piper Open Finding

**Date**: 2026-06-19
**Author**: PA (Piper Alpha)
**Decision**: PM Jun 19 — skip auth for now; get infrastructure working first

---

## What the auth-less PoC looks like

The current PoC plugin (v0.4.0 at `byoc/poc/dinp/piper-morgan/`) is structurally correct. It:
- Has an MCP server that forwards requests to a Piper backend
- Owns config server-side (solves Cowork FS access problem, per #1157)
- Has skills (meet-piper, ask-piper) and the ask_piper / profile tools

The only thing missing for the hosted PoC: `PIPER_BASE_URL` defaults to `http://localhost:8001`. That needs to become a real hosted endpoint.

**What "no auth" means concretely for the PoC**:
- The hosted backend is open — anyone who knows the URL can call it
- No per-user API keys passed from Claude Desktop
- No session/user identity — all requests land in the same context
- This is fine for a single-user PoC (xian testing against their own hosted Piper)
- This is NOT fine for multi-user / public release (see OAuth section below)

**The PoC gate**: PM runs the plugin against a hosted Piper endpoint (not localhost). One successful `ask_piper` call from Claude Desktop to a hosted backend proves the chain. That's it.

---

## What Fly.io (#1278) unlocks

The hosted endpoint comes from Fly.io deployment. Current blocker: credential decoupling (#1162) must ship first (hardcoded localhost assumptions in server config). Order:

```
#1162 cred decoupling → #1278 Fly.io deploy → hosted endpoint available for PoC test
```

Alternative for the PoC: ngrok or Tailscale tunnel to the local server. Lets PM test the hosted chain WITHOUT waiting for Fly.io. Low stakes — just proves the plugin ↔ hosted backend connection.

---

## Piper Open finding: what OAuth is actually for

From PM's Jun 19 update (Piper Open / OpenLaws parallel research):

Key-passing itself works. The OAuth challenge surfaced when trying to do two things:
1. **Metering** — counting and rate-limiting API usage per customer
2. **Returning-user identity** — recognizing the same user across sessions

Without OAuth, you can pass a key (and calls succeed), but you can't tie those calls to a persistent customer account. Every session is anonymous from the backend's perspective.

**Why this matters for the product (not the PoC)**:

| Concern | Auth-less | BYOC key only | OAuth |
|---|---|---|---|
| Basic tool calls work | ✓ | ✓ | ✓ |
| User's LLM costs | PM pays | User pays | User pays |
| Rate limiting per customer | ✗ | ✗ (key ≠ identity) | ✓ |
| Returning user recognized | ✗ | ✗ | ✓ |
| Persistent profile across sessions | Manual | Fragile | ✓ |

**Implication**: the auth-less PoC proves the pipeline. BYOC key-passing is a billing improvement. Neither is a substitute for OAuth if we want real multi-tenant identity. OAuth is the M5+ problem, not the skunkworks problem.

---

## What comes next (after PoC proves hosted chain)

1. **BYOC key field in user_config** — add `anthropic_api_key` to plugin.json user_config (sensitive: true). Backend receives it per-request, uses it for LLM calls. This is the "you bring your own key" feature. Needed before any external user can use their own Anthropic account.

2. **OAuth for metering/identity** — separate issue, filed as #1061/#373 in product repo. Needed for public multi-tenant product. Not needed for alpha.

3. **Connector OAuth flows** — GitHub, Notion, Calendar. Wave P / #1229. Separate from user identity OAuth.

---

## Cross-project note

Piper Open / OpenLaws is working through the same hosted MCP problem. The key finding above (#4 in the tracker) came from their parallel research. Need a mechanism for ongoing notes-sharing — see tracker open question #3.
