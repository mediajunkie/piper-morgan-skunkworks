# Piper Morgan — alpha tester quickstart

You're testing Piper Morgan as a Claude Desktop plugin. The plugin talks to a hosted Piper Morgan
server over the internet — you don't run anything locally.

## Install (2 steps)

### Step 1 — Install the MCP bundle in Claude Desktop

**Easiest:** double-click the `.mcpb` file — Claude Desktop will open and prompt you to install.

**Alternatively:** in Claude Desktop, go to **Connectors** in the left sidebar, click **"+"**, then
choose the `.mcpb` file from the file picker.

> **Note:** this is NOT Skills (which has an "Upload skill" flow limited to 30MB zip files).
> It's the **Connectors** section — MCP bundles install there, not under Skills or Personal plugins.

That's it — no Python, no uv, no server to start. Everything needed is bundled inside.

### Step 2 — Authenticate once

After the plugin appears in your sidebar, start a new conversation and run:

```
connect [shared password]
```

Replace `[shared password]` with the password from the Piper team. You only need to do this once.

## Try it

Once connected:

- `ask_piper "what should I focus on today?"` — ask Piper a PM question
- `get_profile` — see your PM profile (empty until you fill it)
- `save_profile` — update your profile so Piper knows your context

## Found something off?

That's the point of an alpha — note it and send it back. Anything unexpected (errors, confusing
messages, "can't reach Piper") is useful feedback. The shared password goes through the `connect`
tool only — don't paste it into a chat message directly.
