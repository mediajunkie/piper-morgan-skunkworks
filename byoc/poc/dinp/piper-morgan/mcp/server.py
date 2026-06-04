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
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                INTENT_URL, json={"message": message, "session_id": SESSION_ID}
            )
    except httpx.ConnectError:
        # no-silent-failure: surface the connection problem rather than guess.
        return (
            f"Couldn't reach Piper at {INTENT_URL}. Is the local Piper Morgan server "
            f"running? Start it with `python main.py` (default port 8001), then retry."
        )
    except Exception as e:  # noqa: BLE001 — PoC: report any transport failure plainly
        return f"Error calling Piper /intent: {type(e).__name__}: {e}"

    if resp.status_code != 200:
        return f"Piper /intent returned HTTP {resp.status_code}: {resp.text[:500]}"

    try:
        data = resp.json()
    except Exception:
        return f"Piper responded (non-JSON):\n{resp.text[:1000]}"

    # Surface the most likely human-facing fields; always include the raw for the PoC.
    lead = data.get("response") or data.get("message") or data.get("content")
    intent = data.get("intent") or data.get("intent_type") or data.get("classification")
    parts = []
    if lead:
        parts.append(str(lead))
    if intent:
        parts.append(f"\n\n[intent: {intent}]")
    parts.append("\n\n--- full /intent response ---\n" + json.dumps(data, indent=2)[:2000])
    return "".join(parts)


if __name__ == "__main__":
    mcp.run()
