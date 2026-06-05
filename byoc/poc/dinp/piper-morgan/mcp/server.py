# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0", "httpx>=0.27"]
# ///
"""Piper Morgan BYOC PoC — minimal MCP server (rung 1 of the thin plugin PoC).

Exposes ONE tool, `ask_piper`, that forwards a natural-language message to a
locally-running Piper Morgan via POST /api/v1/intent (auth-optional, localhost:8001).
This is the thinnest end-to-end proof of the BYOC stack: skill -> MCP -> real Piper API.

Tracking: mediajunkie/piper-morgan-product#1145
Scope (locked PM 2026-06-03): conversational ask/propose only; Python + uv (PEP-723 inline
deps, so `uv run server.py` self-bootstraps mcp + httpx — no separate venv).
"""
import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

PIPER_BASE = os.environ.get("PIPER_BASE_URL", "http://localhost:8001")
INTENT_URL = f"{PIPER_BASE}/api/v1/intent"
SESSION_ID = "byoc-poc"

mcp = FastMCP("piper-morgan")


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


if __name__ == "__main__":
    mcp.run()
