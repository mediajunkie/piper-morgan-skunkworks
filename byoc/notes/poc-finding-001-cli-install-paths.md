# PoC Finding 001 — Claude Code CLI plugin install paths

**Filed**: 2026-05-18 (lore captured after sub-pass 4.a install debugging)
**Surfaced by**: PA + PM iteration on 2026-05-17 trying to install the sub-pass 4.a plugin
**Status**: Stable knowledge — survives this PoC; useful for any future skunkworks plugin work

---

## TL;DR

For **local-dev plugin install in Claude Code CLI**, the working path is:

```bash
claude --plugin-dir /path/to/plugin/root
```

`/plugin marketplace add` requires a public catalog (`marketplace.json` + git-accessible source) that doesn't yet work for unpublished local marketplaces. Even Anthropic's own first-party plugin testing (OpenLaws Surveyor, Surveyor MCP, etc.) uses `--plugin-dir` as the canonical CLI path — their published install guides document marketplace install as `[PENDING]` pending public catalog publish.

---

## What we tried (the path of escalation)

### Attempt 1 — `/plugin marketplace add <plugin-dir>` (no marketplace.json)

Failed: `Marketplace file not found at .../piper-morgan/.claude-plugin/marketplace.json`. Plugin directories don't double as marketplace directories; marketplace.json is a separate required file.

**Fix attempted**: created marketplace.json at the plugin's `.claude-plugin/` directory.

### Attempt 2 — marketplace.json with `"source": "."` (plugin = marketplace)

Failed: `This plugin uses a source type your Claude Code version does not support`. Claude Code interpreted `"source": "."` as a remote-plugin reference shape.

**Fix attempted**: restructured to legal-prior shape — marketplace at parent directory, plugin in subdirectory.

### Attempt 3 — marketplace.json at `dinp/.claude-plugin/marketplace.json` with `"source": "./piper-morgan"`

Failed: same "source type not supported" error. The restructure matched the legal prior's shape exactly (verified field-by-field via Python json inspection) but Claude Code still rejected install.

**Fix attempted**: tried object-form `"source": {"source": "local", "path": "./piper-morgan"}`. Same error.

### Resolution — `claude --plugin-dir <plugin-root>` (skip marketplace entirely)

Found via grep through OpenLaws install guide at `/Users/xian/Development/openlaws/workdesk/bet-1-workers-comp/install-guide-code-2026-05-11.md`. Vergil's canonical guide documents:

> **Path A — Install via `--plugin-dir` (primary recommendation)**
>
> ```bash
> claude --plugin-dir <path-to-plugin-dir>
> ```
>
> This loads the plugin for the current session. Each new `claude` session needs the same flag.
>
> **Path B — Install from the marketplace (forthcoming; not yet available)**
>
> > **[PENDING v0.3.5 OR LATER]** The marketplace install path becomes available once OpenLaws publishes the marketplace catalog file (`marketplace.json`) and makes the `openlaws-research-agent` repo publicly accessible.

So even OpenLaws — which has been shipping the Surveyor plugin for weeks — hit the same wall and works around it identically.

---

## What this means for skunkworks plugin work

**Use `--plugin-dir` for local-dev CLI testing.** Don't waste cycles on `/plugin marketplace add` — the marketplace install path requires public-repo + Anthropic-recognized catalog publishing that's not available for local-only development.

**Optional convenience**: shell alias for daily use:

```bash
echo 'alias claude-{plugin-slug}="claude --plugin-dir /path/to/plugin/root"' >> ~/.zshrc
source ~/.zshrc
# then just: claude-{plugin-slug}
```

Use a distinct alias name (e.g., `claude-piper`) rather than overriding `claude` so non-plugin sessions still work.

**Plugin packaging shape is correct.** The shape that works is the canonical legal-prior pattern:

```
<plugin-root>/
├── .claude-plugin/
│   └── plugin.json          # 4-field manifest (name, version, description, author)
├── .mcp.json                 # MCP server map (empty {} object if no servers yet)
├── CLAUDE.md                 # template with [PLACEHOLDER] markers + CONFIGURATION LOCATION comment
├── README.md                 # install + usage instructions
└── skills/
    └── <skill-name>/
        └── SKILL.md          # skill body with YAML frontmatter
```

No marketplace.json needed for `--plugin-dir` install. The plugin loads, skills become available as `/{plugin-slug}:<skill-name>` (or in the autocomplete just as `/<skill-name>` if Claude Code's UI strips the namespace prefix when unambiguous).

---

## When marketplace install becomes relevant

The marketplace path will matter if/when:
1. The plugin needs to be installable by users who don't have local repo access
2. We want one-command install (`/plugin install <plugin>@<marketplace>`)
3. We're shipping multiple plugins from one source repo (marketplace organizes them)

For all three: requires either a publicly accessible git repo + Anthropic-published catalog OR a private internal catalog mechanism Anthropic hasn't shipped yet.

None of these are PoC-blocking. Skunkworks plugins distribute via `--plugin-dir` until shipping graduates.

---

## Related references

- **OpenLaws canonical install guide**: `/Users/xian/Development/openlaws/workdesk/bet-1-workers-comp/install-guide-code-2026-05-11.md`
- **OpenLaws install-paths matrix** (all surfaces — Code CLI, Code Desktop, Cowork, Chat): `/Users/xian/Development/openlaws/workdesk/bet-1-workers-comp/install-paths-matrix-2026-05-12.md`
- **Subagent-1 architectural study** (where the `--plugin-dir` flag was first noted): `byoc/notes/subagent-1-anthropic-plugin-architecture-study-2026-05-16.md` §Q4
- **Anthropic public docs**: `https://platform.claude.com/docs/en/plugins` (canonical, but doesn't currently document the local-vs-marketplace install split as clearly as the OpenLaws guide does)

---

## What this finding is NOT

- Not a critique of Anthropic's plugin tooling — local-dev install via `--plugin-dir` is the *intentional* design for plugin authoring; marketplace is for distribution
- Not a permanent block — the marketplace install path will work fine when we're ready to publish
- Not specific to Piper Morgan — applies to any Claude Code plugin in local-dev iteration

— PA, 2026-05-18
