# App

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

### MCP server — `.mcp.json`

`nextcommerce` → `https://mcp.nextcommerce.com/mcp` (HTTP, OAuth). Approve it on first launch, then
authenticate via `/mcp`. Note: Next Commerce documents this gateway as an **operator-admitted private pilot** —
your store must be admitted for sign-in to succeed.

In Claude Code cloud sessions, add `mcp.nextcommerce.com` (and `*.29next.store` for store API calls) to the
environment's **Allowed domains**.
