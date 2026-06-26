# Piper Morgan — alpha tester quickstart

You're testing Piper Morgan as a Claude Desktop plugin. The plugin talks to a hosted Piper Morgan
server over the internet — you don't run anything locally.

## Install (2 steps)

### Step 1 — Open the plugin installer in Claude Desktop

In the Claude Desktop sidebar, look for **"Personal plugins"** with a **"+"** button next to it.
Click that **"+"**.

> **Important:** this is NOT the Skills "+" or the Connectors section — it's the Personal plugins line.
> If you see "Upload skill" or a 30MB size warning, you're in the wrong place. Close and look for the
> Personal plugins section in the left sidebar.

A file picker appears. Choose the file **`piper-morgan-v0.1.5.mcpb`** (the file you received or
downloaded). That's it — no Python, no uv, no server to start. Everything needed is bundled inside.

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
