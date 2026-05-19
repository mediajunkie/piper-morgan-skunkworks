# Piper Morgan Skunkworks

This repository hosts rapid-experimentation projects that complement (not duplicate) the production-oriented development cycle of [piper-morgan-product](https://github.com/mediajunkie/piper-morgan-product).

## What lives here

Each top-level directory is a separate skunkworks project. Projects are:

- **Rapid-experimentation shaped** — built to learn, not to ship
- **Not production-compatible by default** — no commitment to the main codebase
- **Build-less first** — iterate before viable; cut ruthlessly when polish is uncalled-for
- **Backseat to core duties** — agents working on these stay primary on their main responsibilities; skunkworks gets attention when there's bandwidth

## Active projects

### `byoc/` — Bring Your Own Chat plugin / MCP / skills PoC
Proof-of-concept exploring how to express Piper Morgan's distinctive value (composting, object models, ethics boundaries, etc.) as a mix of Anthropic plugin + MCP bundle + skills, with the PM API as the upstream for unique PM behavior. Parallel to PDR-005 (BYOC) strategic work in the main repo.

**Started**: 2026-05-16
**Plan**: `piper-morgan-product/dev/active/skunkworks-byoc-poc-plan-v0.2-2026-05-16.md`
**Status**: Sub-pass 4.a shipped (plugin scaffold + cold-start-as-pm-profile skill); PM gate test in progress

## Conventions

- **`{project}/priors/`** — git submodules of external reference repos pinned to specific commits for reproducibility
- **`{project}/notes/`** — finding memos from PA + subagent work
- **`{project}/poc/`** — the actual experimental artifact
- **`{project}/tracker.md`** — daily status + subagent dispatch state + open questions
- **`{project}/README.md`** — project framing + current status

## Repo discipline

Skunkworks projects are not held to the main repo's full discipline (no mandatory ADR/PDR shape, no mandatory commit-and-push norm, no cross-agent mailbox routing). They DO inherit:

- Sensible commit hygiene (descriptive messages, small commits where practical)
- Reproducibility via submodule pinning for external references
- Visible tracker docs so anyone can see project state

## Relationship to piper-morgan-product

- PA (Piper Alpha) oversees skunkworks projects per PM directive 2026-05-16
- Subagents execute substantive work with PA validation gates
- Leadership read-in happens after meaningful signal — typically after a feature is expressed end-to-end in the PoC
- Findings flow back into main-repo work via PA memos and discussion with leadership

## Cross-project lore worth keeping

Findings that survive their originating PoC and apply to future skunkworks work:

- **PoC Finding 001 — Claude Code CLI plugin install paths** (`byoc/notes/poc-finding-001-cli-install-paths.md`). For local-dev plugin install, use `claude --plugin-dir <plugin-root>`. The `/plugin marketplace add` path requires public-catalog publishing that isn't available for local-only development. Applies to any future skunkworks plugin work, not just byoc.
