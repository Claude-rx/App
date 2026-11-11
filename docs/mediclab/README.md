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

## Where the store stands

See **[STORE-READINESS.md](STORE-READINESS.md)** (generated). The store is brand new: only the demo product, no
gateway, no campaign, no orders. Four blockers before a funnel can take an order:

| # | Blocker | Who / where |
|---|---|---|
| 1 | **Products** — only `Example Product` (DEMO-SKU-123). Create the Mediclab SKUs (title, SKU, price, images, subscription intervals if any) | Admin API (`next-campaigns-create` can read them once they exist) or Dashboard |
| 2 | **Payment gateway** — none (only `bankcard` method listed). Add card processor; add PayPal / Apple Pay for express | Dashboard > Settings > Payments (not API) |
| 3 | **Business address + support phone** — empty | Dashboard > Settings > General |
| 4 | **Campaign** — none in the Campaigns App. Packages (Buy 1/2/3), offers, shipping, API key for the funnel | `next-campaigns-create` skill |

Then the funnel itself: scaffold with `next-campaigns-setup` (Campaign Page Kit, same stack as `campaigns/skinofab/`),
build → polish → QA (`next-campaigns-build`, `-polish`, `-qa`), host standalone (Vercel/Netlify) and add the domain to
the campaign's Allowed Domains.

Also worth fixing before launch: delete the demo product/category, restrict the `Default` $0 shipping method to the
countries you ship to, connect the fulfillment location to the 3PL (a Supliful plugin for Mediclab exists in this
workspace), and connect a primary domain.

## Existing webhook

`Nexus Report Webhook` → `accounts.29next.com/reports/webhook/receiver/` (order, transaction, fulfillment, dispute
events). Platform reporting; leave it.
