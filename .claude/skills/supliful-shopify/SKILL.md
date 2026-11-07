---
name: supliful-shopify
description: Run Mediclab's Supliful private-label pipeline - design label artwork, sync Supliful products into the Shopify store (mediclab.us), forward paid Shopify orders to Supliful for fulfilment and push tracking back. Use when the user mentions Supliful, private label, label design for supplements, pushing Supliful products to Shopify, or Supliful order/tracking sync. For raw API questions read the supliful-api skill.
---

# Supliful -> Shopify (Mediclab)

Code: `tools/supliful/` (Node 22, no dependencies). Full guide: `docs/supliful-integration.md`.
API contract: the vendored `supliful-api` skill (official, from Supliful). Read it before changing the client.

## What can and cannot be automated

| Step | Where | How |
|---|---|---|
| Label artwork | here | `node tools/supliful/cli.mjs labels` -> print PDFs + proofs |
| Create the product + upload the label | **Supliful app only** | the public API has no product-create or label endpoint |
| Publish to the API connection | **Supliful app only** | My Products -> Publish -> "Supliful API" row |
| Product -> Shopify | here | `sync` (dry run) then `sync --apply` |
| Paid Shopify order -> Supliful | here | `server.mjs` webhook, or `push-order <id>` |
| Tracking -> Shopify fulfillment | here | Supliful webhook, or `shipments` / `reconcile` |

Never tell the user a product or label was created in Supliful by this code: it cannot do that.

## Workflow

1. `node tools/supliful/cli.mjs doctor`. Every FAIL names the missing variable or setting. Secrets
   (`SUPLIFUL_API_KEY`, `SHOPIFY_ADMIN_TOKEN`, webhook secrets) live in a gitignored `.env` or the
   host's secret store. Never print, commit or paste them; ask the user to set them.
2. Labels: edit `tools/supliful/labels/specs.json` (front-panel facts) and `brand.json`; copy for
   directions and warnings is read from the product's own store text (`catalog.json`). Render,
   then open `labels/out/index.html` and read `report.json`: every `issues` entry needs a person
   (inferred net quantity, provisional size, missing distributor address, type under 6 pt).
   Look at the proofs before calling a label done.
3. Hand the PDFs to the user for Supliful's label editor; they publish the product to the API connection.
4. `sync` (dry run) -> show the table -> `sync --apply` only after the user agrees. New products land
   as DRAFT unless `--publish`. Existing products matched by SKU are **linked** (metafield
   `supliful.product_id`), their copy and price untouched. `conflict` rows need a person.
5. Orders: `push-order <shopifyOrderId> --dry-run` first. Orders are `testMode` until
   `SUPLIFUL_LIVE_ORDERS=1`; a live order is charged to the merchant at creation. Never switch
   it on without the user's explicit go-ahead.
6. `rehearse` walks a sandbox order through accept -> ship -> complete; `test-webhook order.created`
   proves the receiver.

## Guard rails

- Dry run first, always, for `sync` and `push-order`.
- Do not read customer orders in bulk through the Shopify MCP; work from a single order id the user gives.
- GLP-1 / prescription products in the store are not Supliful's: the bridge forwards only lines whose
  product carries `supliful.product_id`.
- Tests: `npm run test:supliful` must pass before any push.
