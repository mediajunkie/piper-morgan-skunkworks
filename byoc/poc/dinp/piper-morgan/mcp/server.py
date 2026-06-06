# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0", "httpx>=0.27"]
# ///
"""Piper Morgan BYOC PoC — MCP server (thin plugin PoC).

Tools:
- ask_piper(message)         — forward a NL message to local Piper /api/v1/intent (rung 1/2/3).
- get_profile / save_profile — PM profile config, OWNED BY THE SERVER (#1157 fix).
- get_company_profile / save_company_profile — shared cross-context profile.

Why config lives here (#1157): the plugin used to have the AGENT write config to ~/.claude/...,
which works in Claude Code (agent owns the FS) but breaks in Cowork (sandboxed FS, no real $HOME).
The SERVER has normal process FS access on any surface, so it owns config; the agent calls tools.
The canonical file is kept as a human-editable + down-server-fallback MIRROR.

Tracking: mediajunkie/piper-morgan-product#1145, #1157.
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
PLACEHOLDER_MARKER = "[PLACEHOLDER]"

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


@mcp.tool()
async def ask_piper(message: str) -> str:
    """Ask Piper Morgan (a PM assistant) to interpret a natural-language PM request and
    say how it would handle it — intent-classified and offer-first.

    Use this for conversational PM questions ("what should I focus on?", "draft an issue
    about X", "what's the status of Y?") where you want *Piper's* take, grounded in its
    own context, rather than answering as generic Claude. Requires a local Piper Morgan
    server running on :8001 (`python main.py`).

    Args:
        message: the natural-language request to send to Piper.
    """
    # --- Failure-mode attribution (so test failures are distinguishable from real Piper
    # behavior). Each branch tags WHICH layer failed: transport / HTTP / Piper-internal.
    # Motivated by the 2026-06-04 "AI service unavailable" run: a HTTP-200 body that LOOKED
    # like success but was a Piper-side reasoning-engine error — previously indistinguishable
    # from a real answer. ---
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                INTENT_URL, json={"message": message, "session_id": SESSION_ID}
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
