# App

SKINOFAB on Next Commerce: the funnel sources and build (`campaigns/skinofab/`), the store theme (`skinofab-theme/`),
tooling (`tools/`), and the agent setup. **Start with [docs/NEXT-COMMERCE-HANDOFF.md](docs/NEXT-COMMERCE-HANDOFF.md).**

## Next Commerce AI tooling

This repo ships the [Next Commerce](https://nextcommerce.com) agent skills and MCP server
config at **project scope**, so every Claude Code session opened here (local or cloud) loads them.

### Skills — `.claude/skills/` (19)

| Source | Skills |
|---|---|
| [NextCommerceCo/skills](https://github.com/NextCommerceCo/skills) | `next-theme-figma`, `next-theme-design`, `next-theme-dev`, `next-bulk-fulfill`, `next-bulk-move`, `next-bulk-subscription`, `next-ops-scan`, `next-campaigns-setup`, `next-campaigns-create` |
| [NextCommerceCo/campaigns-os](https://github.com/NextCommerceCo/campaigns-os) (`@nextcommerce/campaigns-os` 1.60.0) | `next-campaigns-os`, `next-campaigns-os-setup`, `next-campaigns-build`, `next-campaigns-polish`, `next-campaigns-qa`, `next-campaigns-sdk-bump`, `campaign-lifecycle-orientation`, `campaign-run-evidence`, `campaign-readback-classification`, `contribution-intake` |

Ask in plain language, e.g. *"Run the daily ops risk scan for my store"* or *"Bulk-fulfill these tracking numbers"*.
Store-ops skills need a store Admin API token; they prompt for it — never commit it.

**Update:** `scripts/update-nextcommerce-skills.sh [campaigns-os-version]` (needs git, npm, rsync).
It refuses to overwrite locally edited skills; review, then rerun the upstream installer with `--force`.

### CLI — `@nextcommerce/campaigns-os` (pinned 1.60.0, devDependency)

Next Commerce recommends driving everything headless via the CLI + APIs (the MCP gateway is experimental and adds nothing).

```bash
npm ci                                              # installs the pinned CLI
npm run nc:status                                   # READY check: pin, skills, login
npx --no-install campaigns-os login --store <sub>   # <sub>.29next.store — device-code browser sign-in
```

- `login` is optional: it only lets `spec derive --from-store` fill the Store Profile (`campaign.store_*`).
  Packages, offers and shipping are read with the campaign's **public Campaigns API key**.
- Break-glass alternative: an Admin API token (`store:read`, `content:read`) in an env var, passed as
  `--store-token-source env:<VAR>` — never on the command line, never committed.
- Keep `--no-install` so npx can't fetch an unpinned package.

### What stays in the Dashboard

Campaigns can be driven 100% by API once products exist (Shopify sync, or create products via the Admin API).
Payment gateways, users and general settings still need **Dashboard → Settings**
([general settings & branding](https://docs.nextcommerce.com/docs/start-here/get-started/general-settings-and-branding)).

## Clipcat — AI TikTok selling videos

Skill: **`.claude/skills/clipcat/`** ([clipcat.ai](https://clipcat.ai), CLI v1.0.49). Ask in plain language, e.g.
*"Make a 15s UGC video from these product photos"*, *"Replicate this viral TikTok with our serum"*,
*"Find top-selling skincare videos this week"*, or invoke it directly with `/clipcat`.

```bash
npm run clipcat:setup    # installs the CLI to ~/.local/bin + saves the key from $CLIPCAT_API_KEY (idempotent)
npm run clipcat:check    # exit 0 = CLI installed and API key configured
npm run clipcat:update   # re-download the latest binary
```

- **API key:** add `CLIPCAT_API_KEY` as an **environment secret** (claude.ai → Code → environment settings).
  Get one at https://clipcat.ai/workspace?modal=settings&tab=apikeys. Never commit it.
- **Cloud sessions:** add `bash scripts/clipcat-setup.sh` to the environment's **setup script** so every session starts ready.
- Generation spends Clipcat credits — check cost first with `clipcat quote` / `clipcat models`.

### Agent docs

- https://campaigns.nextcommerce.com/ — campaign build guide (point your agent here)
- https://developers.nextcommerce.com/ — all APIs, agent-ready

### Cloud sessions

Add these to the environment's **Allowed domains**: `*.nextcommerce.com`, `*.29next.store`
(npm is allowed by default).
