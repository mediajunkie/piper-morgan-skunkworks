# Piper Morgan — alpha tester quickstart

You're testing Piper Morgan as a Claude Desktop plugin. The plugin's local helper routes requests to
a Piper Morgan server — either a hosted alpha instance or your own local dev server.

## One-time prerequisites

### 1. Install `uv`
The plugin's small local helper runs through it:

    curl -LsSf https://astral.sh/uv/install.sh | sh

### 2. Set `PIPER_BASE_URL`
The plugin needs to know where your Piper Morgan server lives. Set this in your shell environment
**before** launching Claude Desktop:

    export PIPER_BASE_URL="https://<your-hosted-piper-instance>"

If you're running Piper locally (dev mode), you can omit `PIPER_BASE_URL` entirely — the plugin
defaults to `http://localhost:8001`. Start your local server with `python main.py` first.

> **Note for alpha testers**: if you received a hosted endpoint URL from the Piper team, use that
> as your `PIPER_BASE_URL` value. Do not commit or share this URL publicly.

## Install
Install this plugin zip in Claude Desktop (plugin install → from file).

## Try it
- `/piper-morgan:meet-piper`    — one-time ~10-min setup; learns how you work as a PM. Stays on your machine.
- `/piper-morgan:ask-piper`     — ask Piper a PM question (e.g. "what should I focus on today?").
- `/piper-morgan:consult-piper` — fuller working session; gathers context (from your GitHub) when Piper needs it.

`meet-piper` and `ask-piper` need nothing but `uv`. `consult-piper` additionally uses your GitHub
(`gh` CLI or a connected GitHub) for its context-gathering.

## Found something off?
That's the point of an alpha — note it and send it back. Empty/failed/"can't reach Piper" states are
all useful findings.
