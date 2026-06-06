# Piper Morgan × Cowork — config architecture memo

*Skunkworks PoC note. Author: xian + Claude (Cowork). Date: 2026-06-05.*

## TL;DR

The `meet-piper` cold-start works end-to-end in Claude Code but cannot complete its final write in Cowork, because the plugin persists user config as a dotfile under `~/.claude/plugins/config/dinp/...` and Cowork's agent has no write access to the real home filesystem. The fix that survives both surfaces is to **move config ownership into the Piper MCP server** rather than the agent's filesystem. Two fallbacks (connected-folder config; platform-sanctioned config dir) are weaker. The interview's strict-serial cadence has an analogous CLI-first assumption worth relaxing for enumerable inputs.

## What happened

Running `/piper-morgan:meet-piper` in Cowork, the interview itself ran fine — the limitation surfaced only at the write step:

- **Read** of `~/.claude/plugins/config/dinp/company-profile.md` → refused: "outside this session's connected folders."
- **Write** to the same path → refused: requires a prior Read, which is itself refused. Catch-22.
- **Shell** workaround unavailable: the Cowork bash sandbox is a separate Linux filesystem (`$HOME=/sessions/...`) that does not mount the user's macOS home, so `~/.claude` doesn't exist there either.

Net: the agent staged both files in the session outputs folder and handed the user a `cp` one-liner to install them at the canonical path. Functional, but it pushes a manual step onto the user and breaks the "setup just works" promise.

## Root cause

This is a design-environment mismatch, not a defect.

The dotfile-in-home pattern (`~/.claude/plugins/config/...`) is a **Claude Code idiom**. In the terminal, the agent owns the home filesystem; writing config there is trivial and the right call. Cowork is deliberately the inverse: file tools are scoped to user-connected folders plus an ephemeral session scratchpad, and the shell runs in an isolated sandbox with no view of the real home. A skill whose terminal step is "write to `~/.claude`" therefore has nowhere to land in Cowork.

The plugin was, reasonably, designed for the surface it was born on. The question is what design is portable across surfaces.

## Options

### Option 1 — Piper MCP server owns config (recommended)

The plugin already ships a local MCP server (Python, port 8001). Give it two tools — `get_profile` and `save_profile` (plus optionally `get_company_profile` / `save_company_profile`) — and have `meet-piper` finish by **calling `save_profile` instead of writing a file**. All other skills read via `get_profile`.

Why this wins:

- **Single source of truth, surface-independent.** The server can write its own config file wherever it likes (it has normal process filesystem access); the agent never touches `~/.claude`. Works identically from Claude Code, Cowork, or any MCP-connected client.
- **Queryable, not just parseable.** Skills ask for the fields they need rather than re-parsing a markdown file each run. Validation (placeholder detection, schema versioning) lives in one place.
- **Migration-friendly.** The "copy-forward from old cache path" logic in the current template becomes a server concern, invisible to skills.
- **Degradation is explicit.** If the server is down, skills get a clean tool error (honoring the no-silent-failures rule) instead of silently reading a stale or missing file.

Costs / risks:

- Requires the server to be running for setup *and* for every skill that reads config (today, skills can read the file even when the server is down). Mitigate with a thin local file cache the server maintains, that skills may read read-only as a fallback.
- Slightly more surface area in the server. Acceptable for a PoC whose whole thesis is server-mediated PM context.

### Option 2 — Config in a user-chosen connected folder

Cowork-native: user connects a folder once; config lives there; skills read from it.

- **Pro:** Uses Cowork's actual permission model; user can see and edit the file.
- **Con:** Breaks the single canonical path — every sibling Piper plugin must learn the chosen folder, and Claude Code would need to be told about it too. Fragments the "one path, all plugins" design that `company-profile.md` is built around.

### Option 3 — Platform-sanctioned config dir

Cowork allowlists a specific config directory its file tools may touch.

- **Pro:** Cleanest conceptually; preserves the dotfile design.
- **Con:** Not a plugin-side change — depends on the Cowork platform. Can't ship it from the plugin today.

## Recommendation

Pursue **Option 1**. It removes the filesystem dependency that caused the failure, it's implementable entirely within the plugin's existing server, and it strengthens the PoC's core bet (the server as the PM-context substrate) rather than working around the platform. Keep a read-only local file mirror so non-setup skills still degrade gracefully if the server is down.

Sequencing: (1) add `get/save_profile` to the server with a JSON or front-matter-markdown store; (2) repoint `meet-piper`'s write step at `save_profile`; (3) repoint skills' config read at `get_profile`, with the markdown file as read-only fallback; (4) drop the `cp` workaround.

## Adjacent finding — interview cadence

The same CLI-first assumption shows up in the interview's strict one-question-per-turn rule. That cadence is load-bearing for the **generative** questions (voice and posture) — it demonstrates the serial discipline it's collecting, and batching there would undercut the lesson. But it's over-applied for **enumerable** inputs (the integrations list, the per-project pace table), where Cowork's form / multiple-choice UI is strictly faster and the tester (xian) flagged exactly this in-session.

Suggested rule, now encoded in xian's profile: **serial for generative, form for enumerable.** A skill running in Cowork can detect the surface and offer a compact option-set for list-shaped questions while staying serial for the dispositional ones.

## Open questions

- Should `company-profile.md` (the cross-plugin shared profile) also move behind the server, or stay a file so non-Piper plugins can read it without an MCP dependency? Leaning: server owns it, exposes a read tool, keeps a file mirror.
- Does the server need a profile schema version now, before more sibling plugins depend on it? Cheap to add early, expensive to retrofit.
