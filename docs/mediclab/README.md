# Mediclab on Next Commerce

Store: **https://mediclab.29next.store** (store name `Mediclab`, USD, English, America/New_York).
Connected over the Admin API (`2024-04-01`) on 2026-11-11.

## Connect

The Admin API token lives in **`MEDICLAB_ADMIN_TOKEN`**, never in the repo. Best: save it as a network secret on the
cloud environment for host `mediclab.29next.store` (the proxy injects it, so no session needs the value). Otherwise:

```bash
export MEDICLAB_ADMIN_TOKEN=...            # Dashboard > Settings > API Access
```

```bash
npm run store:check:mediclab               # connection test
```

```bash
npm run store:audit:mediclab               # refreshes STORE-READINESS.md + store-snapshot.json
```

`tools/stores/nc_store.py` is read-only; it scrubs secrets (webhook keys, payment environment keys) and page bodies
from the snapshot and never prints the token. Stores are registered in `tools/stores/stores.json`.
Exit codes: `0` ready · `1` blockers · `2` cannot connect.

## Funnel

**[berberine-funnel.md](berberine-funnel.md)**: Berberine sales page → checkout → upsell → thank you, the offer, and the
launch runbook. Product imported from mediclab.us (Next product #4).

## Where the store stands

See **[STORE-READINESS.md](STORE-READINESS.md)** (generated). Berberine is imported (product #4); no gateway, no
campaign and no orders yet. Blockers before the funnel can take an order:

| # | Blocker | Who / where |
|---|---|---|
| 1 | ~~Products~~ — **done**: Berberine imported from mediclab.us (`tools/mediclab/import_berberine.py`) | — |
| 2 | **Payment gateway** — none (only `bankcard` method listed). Add card processor; add PayPal / Apple Pay for express | Dashboard > Settings > Payments (not API) |
| 3 | **Business address + support phone** — empty | Dashboard > Settings > General |
| 4 | **Campaign** — planned and validated, waits on the gateway (runbook in [berberine-funnel.md](berberine-funnel.md)) | `tools/mediclab/campaign_plan.py` + `next-campaigns-create` |

Then the funnel itself: scaffold with `next-campaigns-setup` (Campaign Page Kit, same stack as `campaigns/skinofab/`),
build → polish → QA (`next-campaigns-build`, `-polish`, `-qa`), host standalone (Vercel/Netlify) and add the domain to
the campaign's Allowed Domains.

Also worth fixing before launch: delete the demo product/category, restrict the `Default` $0 shipping method to the
countries you ship to, connect the fulfillment location to the 3PL (a Supliful plugin for Mediclab exists in this
workspace), and connect a primary domain.

## Existing webhook

`Nexus Report Webhook` → `accounts.29next.com/reports/webhook/receiver/` (order, transaction, fulfillment, dispute
events). Platform reporting; leave it.
