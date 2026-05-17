# Subagent-1: Anthropic Plugin Architecture Study

**Author:** research subagent
**Date:** 2026-05-16
**For:** PA, informing the BYOC PoC design
**Sources:** `byoc/priors/claude-for-legal/` (12 first-party + 1 vendor plugin, 5 cookbooks),
`byoc/priors/knowledge-work-plugins/product-management/` (1 plugin), Anthropic public docs
(`code.claude.com/docs/en/plugins`, `/skills`).

---

## TL;DR

1. A **plugin** is a directory with `.claude-plugin/plugin.json`; it bundles skills, agents, hooks, MCP, LSP, and monitors but contributes *no runtime logic of its own* — it is a namespaced installer.
2. **Skills are prompt files** (`SKILL.md` + frontmatter) that Claude loads inline (or in a forked subagent) when invoked by user `/name` or matched by description; the *only* code that ever runs is `!`shell injections` and optional bundled scripts.
3. **MCP** is the tool surface (remote HTTPS servers in practice), declared in `.mcp.json`; **skills** are the prompt surface; **agents** are presets for system prompt + tools + model; **hooks** fire on lifecycle events; the **CLAUDE.md template** is the practice-profile surface that survives plugin updates at `~/.claude/plugins/config/<marketplace>/<plugin>/CLAUDE.md`.
4. `claude-for-legal` and the PM plugin sit at opposite ends of one spectrum: legal = **stateful per-practice profile + workflow plugins + headless cookbooks**; PM = **generic prompt library with MCP shopping cart**, no per-user profile, no agents, no hooks.
5. The interesting shape question for Piper Morgan is *not* "skill or MCP or plugin?" — it's "what is the writable per-user state, who owns the calibration, and which runtime surface (Claude Code, Cowork, or PM-API headless) is canonical?"

---

## Q1. What ARE plugins, MCP bundles, and skills, mechanically?

### The five (six) layers

| Layer | File(s) | Role | Runtime semantics |
|---|---|---|---|
| **Plugin** | `.claude-plugin/plugin.json` | Identity + namespace; container for everything below | Loaded at session start when enabled; provides `name` used to prefix everything (`/<plugin>:<skill>`). Plugin itself does no work. |
| **Marketplace** | `.claude-plugin/marketplace.json` | A catalog (one per repo) listing N plugins by `name` + `source` path/URL | Read by `/plugin marketplace add <path>`; users then `/plugin install foo@<marketplace>`. |
| **Skill** | `skills/<name>/SKILL.md` (+ supporting files) | Prompt body Claude loads when triggered, with YAML frontmatter (`description`, `allowed-tools`, `disable-model-invocation`, `context: fork`, `agent`, `paths`, `model`, `hooks`, `argument-hint`) | Description always in context (within a per-session character budget — default 1% of model context). Body loads on invocation (`/name` or model-decided match) and **stays in context for the rest of the session**. `!`cmd` and ` ```! ` blocks run *before* Claude sees the rendered prompt. With `context: fork`, body becomes the prompt for a subagent of `agent:` type. |
| **Command** | `commands/<name>.md` | Legacy form of skill (flat MD file); merged into the skill system in 2026. Same frontmatter. | Same as a skill. Plugins may still ship `commands/` for compatibility (PM plugin does). |
| **Agent (subagent)** | `agents/<name>.md` | A preset for a delegated context: system prompt + `tools:` allowlist + `model:` | Not auto-invoked. Invoked by the orchestrator agent (or by a skill with `context: fork, agent: <name>`). Reads its own preloaded skills + CLAUDE.md, not the parent's conversation. |
| **MCP servers** | `.mcp.json` | Map of named servers (mostly `type: http`, OAuth or token) | Tool surface. Loaded when plugin is enabled; tool calls are model-decided. Servers are *configured*, but only *connected* on first successful call (a distinction the legal plugins enforce religiously). |
| **Hooks** | `hooks/hooks.json` | Event handlers (PreToolUse, PostToolUse, etc.) → shell commands | Deterministic, fire outside the model's decision loop. The harness executes them. Most legal plugins ship an empty stub. |
| **Monitors / LSP / bin / settings.json** | `monitors/monitors.json`, `.lsp.json`, `bin/`, `settings.json` | Background watchers (each stdout line = notification to Claude); LSP for code intel; `bin/` added to `PATH`; `settings.json` can pin the main-thread agent | Auxiliary; not used by either prior. |

### Where state lives

- **Plugin source tree** = read-only template, replaced on plugin update.
- **Cache** = `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/...` (gets replaced).
- **Config** = `~/.claude/plugins/config/<marketplace>/<plugin>/CLAUDE.md` — **version-independent, writable, owned by the user**. This is the legal plugins' load-bearing innovation; the PM plugin doesn't use it at all.
- **Shared profile** = `~/.claude/plugins/config/<marketplace>/company-profile.md` — one level up, shared across sibling plugins.

### Runtime order (best reading from docs + priors)

When a user types a message in a session where plugin P is enabled:

1. **Session start**: P's `.mcp.json` is loaded (servers configured), agents and skills indexed, hooks registered, `settings.json` applied, monitors started.
2. **Per turn**: Claude sees user message + all skill *descriptions* (truncated to fit the listing budget) + bundled-skill descriptions + CLAUDE.md memory + any `--add-dir` skills.
3. **Skill trigger**: Either user `/name` (always wins, even if `disable-model-invocation: true`) or model decision based on description. On trigger, `!`cmd` placeholders execute first; the rendered body is injected as one message that persists for the rest of the session (with re-attach behavior after compaction — last invocation of each skill, first 5K tokens, 25K combined budget).
4. **Tool use** inside the skill: MCP tools, Bash, Read/Write/Edit etc. as `allowed-tools` permits.
5. **Hooks**: fire deterministically on tool lifecycle events.
6. **Subagent**: if skill has `context: fork`, a new isolated thread is spawned with the named agent's system prompt + preloaded skills; results return as a single message.

The plugin itself is never "running." It's a manifest that wires existing surfaces together. This is the most important mental model correction for the PoC: there is no plugin runtime, only a registration step.

---

## Q2. How does `claude-for-legal` organize functionality?

Twelve practice-area plugins + one vendor plugin + five cookbooks, sharing a tight set of conventions documented in the top-level `CLAUDE.md`. Per-plugin shape (using `product-legal/` as representative):

```
product-legal/
├── .claude-plugin/plugin.json     # identity, version, description
├── .mcp.json                       # 5 servers + recommendedCategories
├── CLAUDE.md                       # ← practice-profile TEMPLATE (not loaded as context)
├── README.md
├── hooks/hooks.json                # empty stub
├── agents/
│   └── launch-watcher.md           # subagent: tools allowlist, model: sonnet
├── skills/
│   ├── cold-start-interview/SKILL.md   # writes config CLAUDE.md
│   ├── customize/SKILL.md              # edits config CLAUDE.md
│   ├── launch-review/SKILL.md          # reads config CLAUDE.md
│   ├── marketing-claims-review/SKILL.md
│   ├── feature-risk-assessment/SKILL.md
│   ├── is-this-a-problem/SKILL.md
│   └── matter-workspace/SKILL.md       # multi-matter context switching
└── references/
    └── currency-watch.md           # shared with every skill
```

What lives where:

- **`plugin.json`** — just metadata. No tool config, no behavior.
- **`.mcp.json`** — connector menu: Slack, Drive, Linear, Jira, Asana. Each entry is a remote HTTPS MCP server. Plus a `recommendedCategories` array (not standard schema; appears to be an Anthropic extension for discoverability).
- **`agents/launch-watcher.md`** — declarative subagent: `tools: ["Read","Write","mcp__jira__*","mcp__linear__*","mcp__*__slack_send_message"]`, `model: sonnet`. Body is the system prompt. **Important: agents do not self-schedule** — README explicitly says "Set a morning reminder; Claude Code agents do not self-schedule." Cron is the user's problem.
- **`skills/*/SKILL.md`** — prompt bodies. The skills are *long* (`launch-review` is ~260 lines, `cold-start-interview` is ~490 lines). They embed framework tables, sector overlays, output templates, decision trees, and shared guardrails by reference (`see CLAUDE.md ## Outputs`).
- **Plugin `CLAUDE.md`** — a *template* that ships with the plugin. It is **not loaded as project context** (the top-level `CLAUDE.md` says `claude plugin validate` warns about this and the warning is expected). Instead, the `cold-start-interview` skill writes a populated copy to `~/.claude/plugins/config/claude-for-legal/<plugin>/CLAUDE.md`, and every other skill instructs Claude to *read from* that config path before doing work. Skills also reference a shared `company-profile.md` one level up.
- **Hooks** are mostly empty stubs. The deterministic enforcement story for these plugins is *prompt-discipline, not hook-discipline*.
- **Cookbooks** (`managed-agent-cookbooks/<name>/`) are a *parallel deployment surface*: each cookbook references the same plugin's system prompt and skills (`system.file: ../../product-legal/agents/launch-watcher.md`, `skills.from_plugin: ../../product-legal`) but ships an `agent.yaml` for the Claude Managed Agents API + `subagents/*.yaml` leaf workers with a three-tier security model (reader / analyzer / writer; only writer holds Write). One source of truth, two surfaces.

**Install-time vs runtime split:**

| Phase | What happens |
|---|---|
| Install | `/plugin install product-legal@claude-for-legal`; manifests indexed; MCP servers configured (not yet connected); user prompted to restart. |
| First run | Skill reads config CLAUDE.md → finds placeholders → halts → tells user to run `cold-start-interview`. |
| Setup | `/product-legal:cold-start-interview` runs, asks 2-15 min of questions, writes config CLAUDE.md + (if first plugin) `company-profile.md`. Probes connectors *for real* (does a list/search call) rather than trusting `.mcp.json` declarations. |
| Steady state | Every skill: (a) reads config, (b) walks framework from config, (c) calibrates against the user's risk table, (d) outputs in user's house format, (e) closes with decision tree. |
| Update | Plugin update replaces source + cache. Config survives. Skills have migration logic that copies forward from old cache paths if needed. |

The headline architectural move: **the plugin's behavior is parameterized at runtime by a user-owned plain-text file the plugin itself writes during setup.** Skills are thin wrappers around `read config → run framework → write output → flag for review`. Everything that varies practice-to-practice is in the config, not the skill.

---

## Q3. How does the product-management plugin differ?

Same plugin schema, completely different shape. The whole tree:

```
product-management/
├── .claude-plugin/plugin.json    # name, version, description, author — that's it
├── .mcp.json                      # 16 connectors: Slack, Linear, Asana, monday, ClickUp, Jira, Notion, Figma, Amplitude, Pendo, Intercom, Fireflies, GCal, Gmail, Similarweb
├── README.md
├── CONNECTORS.md
├── commands/
│   └── brainstorm.md              # one legacy-style command
└── skills/
    ├── competitive-brief/SKILL.md
    ├── metrics-review/SKILL.md
    ├── product-brainstorming/SKILL.md
    ├── roadmap-update/SKILL.md
    ├── sprint-planning/SKILL.md
    ├── stakeholder-update/SKILL.md
    ├── synthesize-research/SKILL.md
    └── write-spec/SKILL.md
```

What's *not* there: no `CLAUDE.md` template, no `agents/`, no `hooks/`, no `references/`, no `cookbooks`, no shared profile, no cold-start interview, no config-file pattern. **Zero per-user state.** Every skill reads the user's typed input and (optionally) pulls from connected MCP. The README says it's "primarily designed for Cowork" — Anthropic's desktop product — "though it also works in Claude Code." This matters: Cowork comes with the MCP fleet pre-wired through OAuth, so the plugin can assume connectors. In Claude Code, the same plugin works but you have to BYO connectors.

Skill bodies are also notably *generic* — `write-spec` is a high-quality PRD-author template with PRD structure, MoSCoW, success-metric frameworks, etc. There's nothing about *your* PRD format, *your* prioritization rubric, *your* roadmap shape. It's prompt-quality work, not a learning system. Compare to `product-legal/skills/launch-review/SKILL.md` which explicitly will not run until the user has spent 15 minutes telling it what blocks at this specific company.

**Sibling knowledge-work plugins** (`engineering/`, `legal/`, `sales/`, etc.) follow the PM shape, not the legal shape — flat `skills/` + flat `.mcp.json` + flat README, no config, no agents. The legal marketplace is the *outlier*.

### What the difference suggests

The two plugins are fitting two different problem shapes:

| Axis | PM plugin | claude-for-legal |
|---|---|---|
| Variability across users | Frameworks are widely shared (PRDs, RICE, JTBD) | Risk calibration is the *whole job*; varies by company |
| Source of truth for behavior | The skill body | A user-owned config file the plugin wrote |
| Headless deployment | None | Cookbooks (CMA) with 3-tier security model |
| State across sessions | Connected tools only | Config + per-matter workspaces + verification log |
| First-run friction | None | 2-15 min interview required |
| Failure mode if generic | "Generic but useful PRD" | "Confidently wrong launch clearance — career-ending" |

For Piper Morgan (PM-as-founder-assistant), the legal shape is the better prior. Founder context, calibration, risk posture, mailbox routing, and project-specific conventions are exactly the "won't-work-generic" axis. The PM plugin is the right *scope-of-tasks* prior; legal is the right *runtime-state* prior.

---

## Q4. Developer surface

### What an author writes

For a plugin like PM's (the minimum viable shape):

1. `<plugin>/.claude-plugin/plugin.json` — 4-6 fields.
2. `<plugin>/.mcp.json` — array of `mcpServers` (HTTP-streaming/SSE, OAuth optional).
3. `<plugin>/skills/<name>/SKILL.md` files with YAML frontmatter + markdown body.
4. `<plugin>/README.md`.

That's enough to ship. A plugin without any skills/agents/hooks is technically valid but does nothing.

For a plugin like legal's (the full shape), add:

5. `<plugin>/CLAUDE.md` template with `[PLACEHOLDER]` markers.
6. `<plugin>/skills/cold-start-interview/SKILL.md` to populate the config.
7. `<plugin>/agents/<name>.md` for any long-running watcher.
8. `<plugin>/hooks/hooks.json` (even if empty).
9. `<plugin>/references/<shared>.md` for cross-skill tables.
10. A marketplace entry in `.claude-plugin/marketplace.json` (alpha-sorted modulo curation).
11. If headless: `managed-agent-cookbooks/<name>/{agent.yaml, subagents/*.yaml, steering-examples.json}`.

### What the framework provides

- **Namespacing** — `/plugin-name:skill-name` automatically; conflicts impossible across plugins.
- **Discovery** — descriptions auto-injected into Claude's context within a token budget; user `/skill-name` always wins.
- **Lifecycle** — `--plugin-dir` for local dev, `--plugin-url` for ZIP-on-CDN, `/reload-plugins` for live edit, marketplace + `/plugin install` for distribution.
- **MCP plumbing** — OAuth flow handled by client; `.mcp.json` is the only surface needed.
- **Subagent execution** — `context: fork` or `agents/*.md` invoked by orchestrator; subagent results return as a single message.
- **Config path convention** — `~/.claude/plugins/config/<marketplace>/<plugin>/...` is well-known; survives updates; the cookbook deploy script knows it.
- **Validation** — `claude plugin validate <dir>` enforces schema + marketplace invariants I1-I11 (name regex, no shell metachars in source paths, no hidden Unicode, etc.).
- **Permissions** — `allowed-tools` in skill frontmatter, plus user-level deny rules; skill access can be globally killed (`Skill` in deny list).

### What's missing (or you have to BYO)

- **No scheduling.** Agents don't self-schedule; user runs cron or sets a morning reminder. Cookbooks expect an external event bus.
- **No state primitive beyond filesystem.** Config is plain markdown in a known path. No KV, no DB, no key management primitive.
- **No cross-plugin handoff protocol.** Skills can reference `/other-plugin:skill` and it works, but there's no typed handoff schema; cookbooks invent `handoff_request` as a convention.
- **No first-class "memory."** CLAUDE.md is the memory; no API for "remember this fact."
- **Agents are one-level-deep.** Cookbook README notes: "callable_agents supports one delegation level. An orchestrator can call workers; workers cannot call further subagents."

### Install/distribute flow (the short version)

1. Author plugin locally; iterate with `claude --plugin-dir ./<plugin>` + `/reload-plugins`.
2. Add to a `marketplace.json` (own repo or shared).
3. User: `/plugin marketplace add <path-or-url>` → `/plugin install <plugin>@<marketplace>` → restart.
4. First-run setup (cold-start) writes user config.
5. Updates: marketplace pulls new version; cache rotates; config survives.

---

## Q5. What translates to PM-as-plugin? What doesn't?

Confidence here is low; this is the question PA is actually trying to answer. Initial reads only.

### Clearly translates

- **The "thin skills over rich config" pattern.** PM-the-PM-assistant is calibration-heavy in exactly the legal-plugin sense — what counts as "review-ready," when to escalate to xian, what xian's serial-decisions rule means, what "PM-on-CC" routing rules look like, what counts as a Lead Dev escalation. These are practice-profile facts, not generic prompt facts.
- **Cold-start interview as setup.** Piper has months of accumulated MEMORY.md memos that read exactly like a cold-start interview output. Translating those into `~/.claude/plugins/config/piper-morgan/founder-profile.md` would let any skill in the plugin honor "no silent failures," "serial decisions," "PM-addressed memos with PA on CC," etc., without re-deriving them per session.
- **Shared profile + per-plugin profile split.** Piper's project-conceptual-integrity memo and sibling-projects memo are *company-level*; PA-launch-context and Kind/OpenLaws focus are *plugin-level*. The legal `company-profile.md` + per-plugin practice profile maps cleanly.
- **`!`cmd injection`** for dynamic context. Piper's mailbox check, editorial calendar, BRIEFING-CURRENT-STATE — these are all good candidates for skill-prefix `!`cat ...` injections so Claude doesn't have to remember to Read them.
- **Skill = role + procedure.** `/piper-morgan:check-mailbox`, `/piper-morgan:close-issue-properly`, `/piper-morgan:audit-cascade` already exist as Piper skills; lifting them into a plugin is mostly mechanical.
- **MCP shopping cart.** Granola, Slack, Notion, Drive, Github, Figma — Piper's existing MCP surface fits the legal-plugin `.mcp.json` pattern directly.
- **The provenance-tagging discipline.** `[verify]` / `[user provided]` / `[model knowledge]` / `[settled — last confirmed YYYY-MM-DD]` from the legal plugins is the same discipline as Piper's "no silent failures." Worth lifting wholesale.

### Probably translates with adaptation

- **Cookbook / CMA pattern** for headless PM-API. If "PM API" means "PA running unsupervised on cron, posting to PM's inbox," that's a cookbook. But the cookbook's three-tier reader/analyzer/writer security model is built for adversarial input (court filings, vendor contracts); the PM analog is less adversarial. The structural pattern (orchestrator with no Write, leaves with scoped tools) probably still fits as defense-in-depth, but it's overbuilt for the most likely PM-API uses.
- **Matter workspaces.** Legal `matter-workspace` skill lets a practice juggle multiple clients with cross-matter isolation. For Piper, the analog could be project workspaces (PA, Klatch, Atlas, Globe, Kind/OpenLaws as the active one). Mechanically similar. But Piper's sibling-projects discipline is about *avoiding cross-pollination of mechanism without verification*, not about confidentiality walls — different goal, similar machinery.
- **Decision-tree close-out.** Legal skills close with a "pick one and I'll build it out" decision tree. Piper's serial-decisions rule means this would need to be one option at a time, not a 5-option menu. Adaptable.

### Probably doesn't translate

- **Privilege headers, jurisdiction recognition, citation tiering.** Legal-specific; the analogous discipline for PM is different (provenance + uncertainty surfacing).
- **Cookbook's adversarial-input model.** Piper's input surface (Granola transcripts, PM's own mailbox memos, Github issues) isn't an adversary surface. Some prompt-injection hygiene is still warranted but the full three-tier model is over-engineered.
- **Cold-start interview's "ask 2-3 questions at a time" pacing.** Piper has the *opposite* rule from xian — serial decisions one at a time. The legal cold-start interview's batching pattern would need to be inverted.
- **The 12-plugin marketplace surface.** Piper-as-plugin is one plugin, not a marketplace. The marketplace value (catalog browsing, cross-plugin discovery) doesn't apply at N=1; might apply later if Piper grows skill families (founder-mode / PA-mode / publishing-mode as separate plugins).

### The shape question PA actually needs to answer (not in this memo's scope)

If Piper-as-plugin ships, which surface is canonical?

- **Claude Code** (terminal, $HOME-installed) — closest to current Piper workflow, what xian uses daily.
- **Cowork** (desktop app, OAuth MCP fleet) — closest to the PM-plugin assumption; "PM-as-Cowork-plugin" would inherit Slack/Notion/Drive without configuration.
- **CMA / cookbooks** (headless, Anthropic-hosted) — what "PM API" likely means; lets PA run on a schedule without an attended terminal.

These are not mutually exclusive (legal ships all three from one source tree), but the PoC has to pick a canonical one to optimize for. That's a different question from the shape questions in this memo.

---

## What I'm uncertain about

- **Whether `recommendedCategories` in `.mcp.json` is a public schema field** or an Anthropic-internal extension for the Cowork connector picker. Couldn't find it in the public docs I checked.
- **Exact CMA / `POST /v1/agents` surface.** I read the cookbook README's translation table but didn't fetch the public CMA docs. The "research preview, one delegation level" constraint is from the cookbook README; whether that's still current is unclear.
- **Whether Cowork actually treats the PM plugin's `.mcp.json` differently from Claude Code** (e.g., auto-OAuth at install vs prompt-on-use). The plugin author clearly designed for Cowork; the runtime difference is implied but not documented in the prior.
- **Hook-vs-prompt deterministic enforcement.** Legal plugins ship empty hooks and do all their enforcement in prompt ("destination check," "no silent supplement," "currency trigger"). I don't know whether that's a design choice (prompt is sufficient) or a maturity choice (hooks are coming). For a PoC, prompt-only is likely fine.
- **Plugin update + config migration in practice.** The cold-start skill has migration logic for copying forward from old cache paths "for any version." Whether this is well-tested or aspirational, I can't tell from source. The `## Things to leave alone` section in `claude-for-legal/CLAUDE.md` flags known gaps; would want PA to read that section before extending the pattern.
- **Whether `references/` actually ships inside installed plugin directories.** The repo's `CLAUDE.md` says: "`references/` lives only at repo root and is not shipped inside any plugin directory. Several plugin `CLAUDE.md` templates reference it as if it were — that's a known gap." So skills *think* they're reading from `references/` but the file isn't there at runtime. This is either a known bug or a gap intended to be closed; PoC shouldn't repeat the mistake.
- **Whether the PM plugin's lack of `CLAUDE.md` is "we haven't gotten there yet" or "intentional shape."** If the former, the legal pattern is the asymptote and the PM plugin will grow toward it. If the latter, the two shapes are stable and reflect real differences in problem domain. Resolving this would meaningfully reframe Q5.
- **Single-plugin vs marketplace decision for Piper.** I have weak intuition that Piper is one plugin, but if PA splits into mode-plugins later, the marketplace overhead pays off. Out of scope for this memo.
