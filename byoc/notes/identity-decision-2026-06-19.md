# Identity Decision — BYOC / Hosted Release

**Date**: 2026-06-19
**Decided by**: PM (xian)
**Status**: RATIFIED

---

## Decision

| Release | Identity approach | Auth mechanism |
|---|---|---|
| PoC (now) | No auth | None — open endpoint |
| MVP / beta (0.9.0) | UUID bearer | UUID issued at first MCP connect; passed with every request |
| Production (1.0) | Email + magic link | Piper-native account; UUID reissued after email verification |
| Post-1.0 | "Login with..." overlay | Optional convenience; NOT the foundation |

---

## Principles

**1. No building identity on another company's ID.**
Piper-native identity only. UUID bearer for MVP, email account for 1.0. "Login with Google/GitHub" is a post-1.0 convenience feature that sits OVER our own identity system — not under it.

**2. OAuth for metering/identity is a separate problem from connector OAuth.**
- Connector OAuth (GitHub, Notion, Calendar) = how users grant Piper access to their data. Wave P / #1229. Needed for connectors.
- Identity OAuth (Login with Google) = how users authenticate to Piper. Post-1.0. NOT needed for MVP.
These are different things. Piper Open ran into the conflation: the metering/identity OAuth challenge is real but it doesn't block basic hosted function.

**3. PoC is auth-free by design.**
The PoC proves the plugin ↔ hosted backend chain. Auth adds complexity without adding proof. Deferred to MVP.

---

## UUID Bearer — how it works (MVP)

1. User installs the plugin. On first `ask_piper` (or `get_profile`) call, the MCP server checks for a UUID in config.
2. If none exists, the server generates a UUID and persists it at `~/.claude/plugins/config/dinp/piper-morgan/user-id` (or similar).
3. UUID is sent with every subsequent MCP call as a header or field: `X-Piper-User-ID: <uuid>`.
4. Backend uses UUID to scope profile, conversation history, and data.
5. UUID persists across sessions (same device, same user).

**Limitations** (acceptable for MVP, addressed at 1.0):
- Device-scoped: reinstall = new UUID = new profile (no recovery)
- Single-device: UUID not shared across user's devices
- No metering: can't rate-limit or bill per customer (Piper Open finding)

---

## Email + Magic Link — how it works (1.0)

1. During onboarding (meet-piper or first connect), user is prompted for email.
2. Piper sends a magic link to that email.
3. On click, the server creates a Piper account, links the existing UUID to that email, and issues a new signed bearer token.
4. The signed token is stored in plugin config (replacing the raw UUID).
5. UUID is now the account ID; email is the recovery mechanism and multi-device bridge.

**This gives us**:
- Account recovery: email → reissue bearer token on reinstall
- Multi-device: same email = same Piper account = same profile
- Billing hook: email is the billing identity for subscriptions
- No third-party dependency: Piper issues and validates the tokens

**"Login with Google" (post-1.0)**: can be added later as a convenience path that claims an existing Piper account. Not the auth foundation.

---

## What this defers

- **OAuth for metering/rate-limiting**: Piper Open finding — you can't meter usage per customer without OAuth. Deferred. For MVP, the backend either has no rate limiting or uses a coarse server-side limit.
- **Multi-tenant billing**: Needs 1.0 email account + a billing integration (Stripe or similar). Out of scope for MVP.
- **GDPR/right-to-deletion**: Needs email account to tie all data to a person. 1.0+ requirement.

---

## Open questions (for 1.0 scoping)

1. Does 1.0 need metering/rate-limiting? If yes, what's the mechanism without full OAuth?
2. Subscription model: per-seat, usage-based, or flat? Affects billing identity requirements.
3. Is there a compliance requirement (GDPR, CCPA) that requires verified identity at 1.0?

---

## Related

- byoc/tracker.md Gate 3
- Product repo #1185 (BYO-KEY-MULTI-TENANT)
- Product repo #1061/#373 (INFRA-OAUTH-MULTI — post-1.0)
- Piper Open finding: `byoc/notes/hosted-mcp-auth-decision-2026-06-19.md` §Piper Open finding
