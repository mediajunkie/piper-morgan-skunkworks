# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0", "httpx>=0.27"]
# ///
"""Piper Morgan BYOC PoC — MCP server (thin plugin PoC).

Tools:
- ask_piper(message)         — forward a NL message to Piper /api/v1/intent (rung 1/2/3).
- connect(credential)        — store the shared Caddy basic-auth password (#1300).
- get_profile / save_profile — PM profile config, OWNED BY THE SERVER (#1157 fix).
- get_company_profile / save_company_profile — shared cross-context profile.

Why config lives here (#1157): the plugin used to have the AGENT write config to ~/.claude/...,
which works in Claude Code (agent owns the FS) but breaks in Cowork (sandboxed FS, no real $HOME).
The SERVER has normal process FS access on any surface, so it owns config; the agent calls tools.
The canonical file is kept as a human-editable + down-server-fallback MIRROR.

Credential design (#1300): the shared Caddy basic-auth password is stored server-side in
credential.json (never in .mcp.json or any plugin-distributed file). PIPER_BASE_URL carries
only the bare host. ask_piper() reads the credential and sends it as HTTP Basic Auth on each
request. If no credential is stored, ask_piper returns a NOT-CONNECTED message with instructions
to run the connect() tool.

Tracking: mediajunkie/piper-morgan-product#1145, #1157, #1295, #1300.
Python + uv (PEP-723 inline deps; `uv run server.py` self-bootstraps — no venv).
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

PIPER_BASE = os.environ.get("PIPER_BASE_URL", "http://localhost:8001")
INTENT_URL = f"{PIPER_BASE}/api/v1/intent"
SESSION_ID = "byoc-poc"

# --- Config storage (server-owned; canonical path kept as human-editable mirror) ---
# Overridable for tests / non-default homes. Default = the canonical plugin config path,
# which the SERVER can write (normal process FS access) even when the agent can't.
SCHEMA_VERSION = 1
CONFIG_ROOT = Path(
    os.environ.get(
        "PIPER_CONFIG_ROOT",
        str(Path.home() / ".claude" / "plugins" / "config" / "dinp"),
    )
)
PROFILE_PATH = CONFIG_ROOT / "piper-morgan" / "CLAUDE.md"
COMPANY_PROFILE_PATH = CONFIG_ROOT / "company-profile.md"
CREDENTIAL_PATH = CONFIG_ROOT / "piper-morgan" / "credential.json"
PLACEHOLDER_MARKER = "[PLACEHOLDER]"

# Fixed username for Caddy basic-auth on alpha.pipermorgan.ai (#1300).
# Only the password changes between deployments; the username is baked here, not in config.
PIPER_AUTH_USERNAME = "piperalpha"

mcp = FastMCP("piper-morgan")


# --- Config helpers (shared by the profile tools) ---
def _read_profile(path: Path, label: str) -> str:
    """Read a profile file; return a clear not-configured signal instead of raising."""
    try:
        if not path.exists():
            return (
                f"[{label}: NOT-CONFIGURED] No profile found at {path}. "
                f"Run /piper-morgan:meet-piper to create one."
            )
        text = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001 — report plainly rather than crash the tool
        return f"[{label}: READ-ERROR] {type(e).__name__}: {e} (path: {path})"
    if not text.strip():
        return f"[{label}: EMPTY] File exists but is empty: {path}. Run /piper-morgan:meet-piper."
    if _has_real_placeholders(text):
        return f"[{label}: HAS-PLACEHOLDERS] Profile exists but is incomplete:\n\n{text}"
    return text


def _has_real_placeholders(text: str) -> bool:
    """True only if the marker appears as an actual unfilled field value.

    The shipped template's CONFIGURATION-LOCATION comment block and the italic
    subtitle both *mention* the literal token in instructional prose ("If you see
    `[PLACEHOLDER]`, run ...", "still contains [PLACEHOLDER] markers"). The skill
    requires preserving that comment block, so a naive `MARKER in text` check
    false-positives on every fully-populated profile. Strip HTML comments and
    inline-code spans first; a genuine unfilled field (e.g. `**Name:** [PLACEHOLDER]`)
    lives in neither and is still detected.
    """
    stripped = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)  # HTML comment blocks
    stripped = re.sub(r"`[^`]*`", "", stripped)                   # inline-code spans
    return PLACEHOLDER_MARKER in stripped


def _write_profile(path: Path, content: str, label: str) -> str:
    """Write a profile file (server-owned); back up any prior version; report plainly."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            backup = path.with_suffix(path.suffix + f".bak.{stamp}")
            backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        path.write_text(content, encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return f"[{label}: WRITE-ERROR] {type(e).__name__}: {e} (path: {path})"
    return f"[{label}: SAVED] Wrote {len(content)} chars to {path} (schema v{SCHEMA_VERSION})."


# --- Credential helpers (#1300) ---

def _read_credential() -> str | None:
    """Return the stored Caddy basic-auth password, or None if not configured.

    Format: JSON {"password": "<value>"} — simple and human-editable if needed.
    Returns None on any read/parse error (caller handles as NOT-CONNECTED).
    """
    try:
        if not CREDENTIAL_PATH.exists():
            return None
        data = json.loads(CREDENTIAL_PATH.read_text(encoding="utf-8"))
        return data.get("password") or None
    except Exception:  # noqa: BLE001 — credential absent → NOT-CONNECTED, not crash
        return None


def _write_credential(password: str) -> str:
    """Persist the Caddy basic-auth password to server-owned config.

    Returns a success or error string (same pattern as _write_profile).
    """
    try:
        CREDENTIAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        CREDENTIAL_PATH.write_text(
            json.dumps({"password": password}, indent=2), encoding="utf-8"
        )
    except Exception as e:  # noqa: BLE001
        return f"[connect: WRITE-ERROR] {type(e).__name__}: {e} (path: {CREDENTIAL_PATH})"
    return (
        f"[connect: SAVED] Credential stored at {CREDENTIAL_PATH}. "
        f"ask_piper() will now authenticate as '{PIPER_AUTH_USERNAME}'."
    )


@mcp.tool()
async def connect(credential: str) -> str:
    """Store the shared Piper Morgan alpha server password so ask_piper() can authenticate.

    The alpha server (alpha.pipermorgan.ai) uses Caddy HTTP Basic Auth. The password is
    shared out-of-band (ask PM). Once stored, ask_piper() sends it automatically on every
    request — you never need to pass it again.

    Args:
        credential: the shared basic-auth password for alpha.pipermorgan.ai.

    Returns a confirmation on success, or an error message if the write fails.
    """
    if not credential or not credential.strip():
        return "[connect: INVALID] credential must not be empty."
    return _write_credential(credential.strip())


@mcp.tool()
async def ask_piper(message: str) -> str:
    """Ask Piper Morgan (a PM assistant) to interpret a natural-language PM request and
    say how it would handle it — intent-classified and offer-first.

    Use this for conversational PM questions ("what should I focus on?", "draft an issue
    about X", "what's the status of Y?") where you want *Piper's* take, grounded in its
    own context, rather than answering as generic Claude. When connecting to the alpha
    server (alpha.pipermorgan.ai), run connect(credential="<password>") first — the
    password is stored once and used automatically on every subsequent call.

    Args:
        message: the natural-language request to send to Piper.
    """
    # --- Credential check (#1300) ---
    # Only required when PIPER_BASE_URL points at the alpha server (or any Basic-Auth-
    # protected host). If no credential is stored, fail fast with clear instructions.
    password = _read_credential()
    if password is None and "localhost" not in PIPER_BASE and "127.0.0.1" not in PIPER_BASE:
        return (
            "[ask_piper: NOT-CONNECTED] No credential stored — run the connect tool first: "
            "connect(credential=\"<your password>\"). "
            "Ask PM for the shared alpha server password. "
            "PM skills are also available separately — install from "
            "https://github.com/mediajunkie/piper-morgan-product or ask PM for the "
            "piper-morgan-skills.zip."
        )

    auth = (PIPER_AUTH_USERNAME, password) if password else None

    # Safety net: truncate oversized messages before they hit the server's POST limit.
    # Motivated by #1244 Bug B: consult-piper re-asks with a large issues list and the
    # enriched payload can exceed /api/v1/intent's body limit.
    MAX_MESSAGE_CHARS = 8_000
    if len(message) > MAX_MESSAGE_CHARS:
        message = (
            message[:MAX_MESSAGE_CHARS]
            + "\n[… message truncated to 8000 chars by ask_piper safety limit]"
        )

    # --- Failure-mode attribution (so test failures are distinguishable from real Piper
    # behavior). Each branch tags WHICH layer failed: transport / HTTP / Piper-internal.
    # Motivated by the 2026-06-04 "AI service unavailable" run: a HTTP-200 body that LOOKED
    # like success but was a Piper-side reasoning-engine error — previously indistinguishable
    # from a real answer. ---
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                INTENT_URL,
                json={"message": message, "session_id": SESSION_ID},
                auth=auth,
            )
    except httpx.ConnectError:
        return (
            f"[ask_piper: SERVER-DOWN] Couldn't reach Piper at {INTENT_URL} (connection "
            f"refused). The local Piper Morgan server isn't running — start it with "
            f"`python main.py` (default port 8001), then retry. (If you expected it to be "
            f"up, another process may have just restarted it.)"
        )
    except httpx.TimeoutException:
        return (
            f"[ask_piper: TIMEOUT] Piper at {INTENT_URL} accepted the connection but didn't "
            f"respond within 30s. The server is up but slow/stuck — likely a downstream "
            f"(LLM) call hanging. Retry; if it persists, check Piper's logs."
        )
    except Exception as e:  # noqa: BLE001 — PoC: report any other transport failure plainly
        return f"[ask_piper: TRANSPORT-ERROR] {type(e).__name__}: {e} (calling {INTENT_URL})"

    if resp.status_code == 401:
        return (
            "[ask_piper: AUTH-FAILED] Credential rejected by the Piper server (HTTP 401). "
            "Update it with connect(credential=\"<new password>\") and ask PM if unsure."
        )

    if resp.status_code != 200:
        return (
            f"[ask_piper: HTTP-{resp.status_code}] Piper's server responded but with an "
            f"error status. Body: {resp.text[:500]}"
        )

    try:
        data = resp.json()
    except Exception:
        return f"[ask_piper: NON-JSON] Piper responded (HTTP 200) but not JSON:\n{resp.text[:1000]}"

    # HTTP 200 + valid JSON — but Piper itself may report an INTERNAL failure in the body
    # (e.g. the reasoning/LLM engine being unavailable). Detect + tag it so it doesn't read
    # as a successful answer. Heuristic: scan the human-facing text for known error phrasings.
    lead = data.get("response") or data.get("message") or data.get("content") or ""
    lead_str = str(lead)
    internal_error_markers = (
        "ai service is temporarily unavailable",
        "temporarily unavailable",
        "trouble connecting to my reasoning engine",
        "reasoning engine",
        "please try again",
    )
    is_internal_error = any(m in lead_str.lower() for m in internal_error_markers)

    intent = data.get("intent") or data.get("intent_type") or data.get("classification")

    if is_internal_error:
        # Routing succeeded (Piper classified the request) but its downstream engine failed.
        parts = [
            "[ask_piper: PIPER-INTERNAL-ERROR] Piper received and classified the request, "
            "but its downstream reasoning/LLM engine reported a temporary failure — this is "
            "NOT a real answer and NOT a problem with this plugin. Retry in a moment; if it "
            "persists, check Piper's server logs.\n\nPiper's verbatim message:\n",
            lead_str,
        ]
        if intent:
            parts.append(f"\n\n[intent (routing succeeded): {intent}]")
        parts.append("\n\n--- full /intent response ---\n" + json.dumps(data, indent=2)[:2000])
        return "".join(parts)

    # Genuine success.
    parts = ["[ask_piper: OK] "]
    if lead_str:
        parts.append(lead_str)
    if intent:
        parts.append(f"\n\n[intent: {intent}]")
    parts.append("\n\n--- full /intent response ---\n" + json.dumps(data, indent=2)[:2000])
    return "".join(parts)


# --- Config tools (server-owned config; the #1157 fix) ---

@mcp.tool()
async def get_profile() -> str:
    """Return the user's Piper Morgan PM profile (how they work as a PM).

    Call this at the start of meet-piper (to check if setup is needed) and from any skill
    that wants the user's calibration. Returns the profile content, or a clear
    NOT-CONFIGURED / HAS-PLACEHOLDERS / EMPTY signal if setup hasn't completed — so the
    caller can route to /piper-morgan:meet-piper instead of guessing. Works on any surface
    (the server reads the file; the agent never needs filesystem access to ~/.claude).
    """
    return _read_profile(PROFILE_PATH, "profile")


@mcp.tool()
async def save_profile(content: str) -> str:
    """Persist the user's Piper Morgan PM profile. Call this at the END of meet-piper
    instead of writing a file directly — the server owns the write, so it works on any
    surface (Cowork included, where the agent can't reach ~/.claude). Backs up any prior
    version first. Pass the full profile markdown (mirror the plugin's CLAUDE.md template).
    """
    return _write_profile(PROFILE_PATH, content, "profile")


@mcp.tool()
async def get_company_profile() -> str:
    """Return the shared cross-context company profile (reused by any sibling Piper plugins).
    Same NOT-CONFIGURED / HAS-PLACEHOLDERS signaling as get_profile.
    """
    return _read_profile(COMPANY_PROFILE_PATH, "company-profile")


@mcp.tool()
async def save_company_profile(content: str) -> str:
    """Persist the shared cross-context company profile. Server-owned write (works on any
    surface); backs up any prior version. Pass the full company-profile markdown.
    """
    return _write_profile(COMPANY_PROFILE_PATH, content, "company-profile")


if __name__ == "__main__":
    mcp.run()
