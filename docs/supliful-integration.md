# Supliful integration (Mediclab)

Private-label supplements from [Supliful](https://supliful.com), sold on the Mediclab Shopify store
(`mediclab-2.myshopify.com`, mediclab.us). Code: `tools/supliful/`. Agent skills:
`supliful-shopify` (this workflow) and `supliful-api` (Supliful's official API skill, vendored).

## How it fits together

```
 labels (this repo)         Supliful app (manual)              this repo                     Shopify
 ─────────────────          ─────────────────────              ─────────                     ───────
 specs.json + copy ──PDF──> create product, upload label
                            publish to "Supliful API" ──API──> sync ───────── productSet ──> product (DRAFT)
                                                                                              │ paid order
                            order (charged to merchant) <───── bridge <── orders/paid webhook ┘
                            parcel shipped ──webhook────────> bridge ───── fulfillmentCreate ──> tracking email
```

**What the Supliful API cannot do:** create products, design or upload labels, or publish products.
Its nine endpoints read products and place, read and cancel orders, and give you a sandbox
(source: the API's own spec, `GET https://public-api.supliful.com/v1/openapi.json`). Product creation,
the label editor and publishing stay in the Supliful app; everything either side of them is automated here.

## One-time setup

### Supliful (needs a Pro or Enterprise membership)
1. **Stores → "Supliful API" card → Create connection** (name it "Mediclab Shopify bridge"). Copy the
   key, shown once, into `SUPLIFUL_API_KEY`.
2. **Manage → Webhooks → Add endpoint**: `https://<bridge host>/webhooks/supliful`. Copy the signing
   secret into `SUPLIFUL_WEBHOOK_SECRETS`.
3. Before publishing products, the app wants a saved label, a payment method, a verified email,
   a connected store and an active membership.

### Shopify
1. **Settings → Apps → Develop apps → Create app**, Admin API scopes: `read_products`, `write_products`,
   `read_orders`, `write_orders`, `read_merchant_managed_fulfillment_orders`,
   `write_merchant_managed_fulfillment_orders`. Install it; the Admin token goes in `SHOPIFY_ADMIN_TOKEN`,
   the API secret key in `SHOPIFY_WEBHOOK_SECRET`.
2. **Settings → Notifications → Webhooks**, or the app's webhook subscription: topic `orders/paid`, URL
   `https://<bridge host>/webhooks/shopify/orders-paid`, JSON.

### Secrets
Copy `tools/supliful/.env.example` to `.env` at the repo root (gitignored) or set the variables in
the host's secret store. Then run:

```bash
npm run supliful -- doctor
```

Every line must read PASS. `doctor` never prints a secret; it identifies the key by the
connection `GET /v1/me` returns.

## Daily use

| Task | Command |
|---|---|
| Health check | `npm run supliful -- doctor` |
| Products on the connection | `npm run supliful -- products` |
| Preview the product sync | `npm run supliful -- sync --out sync-report.md` |
| Apply it | `npm run supliful -- sync --apply` (add `--publish` to make new products ACTIVE) |
| Send one order by hand | `npm run supliful -- push-order <shopifyOrderId> --dry-run`, then without `--dry-run` |
| Order status | `npm run supliful -- order shopify-<shopifyOrderId>` |
| Cancel (first ~2 h only) | `npm run supliful -- cancel shopify-<shopifyOrderId>` |
| Push tracking by hand | `npm run supliful -- shipments <suplifulOrderId>` |
| Catch up after downtime | `npm run supliful -- reconcile` |
| Sandbox walk-through | `npm run supliful -- rehearse` |
| Test webhook delivery | `npm run supliful -- test-webhook order.created` |
| Run the bridge | `npm run supliful:server` (port `PORT`, default 8787) |

### Product sync rules
- **Matched by SKU, not linked yet → `link`**: the Shopify product gets metafields
  `supliful.product_id` and `supliful.updated_at`. Title, copy, images and price are **left alone**,
  because the Mediclab pages are hand-written. The 24 `MLX-*` products should link this way once their
  Supliful SKUs match.
- **Not in Shopify → `create`**: DRAFT product from Supliful's name, description, mockups, SKU, weight and
  `retailPrice`. Override prices with `--prices prices.json` (`{"MLX-ASHW": 35}` or by Supliful id).
- **Linked and changed in Supliful → `update`**: refreshes the link; `--update-content` also rewrites the
  title, description and images.
- **Discontinued or unavailable → `hide`**: the Shopify product goes to DRAFT. It is never deleted, because
  orders reference it.
- **One SKU on several Shopify products → `conflict`**: a person picks the product, adds the metafield, and re-runs the sync.
- Inventory is not tracked in Shopify (Supliful holds the stock); `inventoryPolicy` is CONTINUE.

### Order rules
- Only lines whose product carries `supliful.product_id` are sent. The store's GLP-1 and prescription
  products are never forwarded.
- Only `PAID` / `PARTIALLY_REFUNDED`, uncancelled orders are forwarded; quantities are net of refunds.
- `externalOrderId` is `shopify-<order id>`, so a retried webhook can never place a second order.
  Conflicts adopt the existing order.
- **Sandbox until you say otherwise.** Orders carry `testMode: true` (never charged, never shipped,
  deleted after 2 h) until `SUPLIFUL_LIVE_ORDERS=1`. A live order is charged to the merchant at creation.
- Forwarded orders are tagged `supliful-sent` (`supliful-test` in sandbox). Holds add `supliful-on-hold`
  and `supliful-hold:<reason>`; Supliful cancellations add `supliful-canceled`, and someone then has to refund the customer
  in Shopify.
- A shipment with a tracking number or URL becomes a Shopify fulfillment, covering only that parcel's lines,
  and the customer is notified. Parcels without tracking wait for the next event or `reconcile`.

### Webhook receiver
Follows Supliful's rules: HMAC over the raw bytes (`x-supliful-signature`, any `v1` during a rotation,
5-minute tolerance), dedupe on `x-supliful-idempotency-key` (a rejected delivery never blocks a valid
retry), answer 200 at once and process afterwards, log every delivery to `.supliful-state/*.jsonl`.
Shopify deliveries are verified with `X-Shopify-Hmac-Sha256` and deduped on `X-Shopify-Webhook-Id`.
Test deliveries (`data.testMode: true`) are logged and change nothing.
`SUPLIFUL_PROCESS_TEST_EVENTS=1` lets them through, for rehearsals against a development store only.

Host it anywhere that serves Node 22 over public `https://` (Render, Fly.io, Railway, a VM behind
Caddy). The state directory must persist. Supliful switches off an endpoint after 3 days without a
successful delivery; after switching it back on, run `reconcile`.

## Labels

```bash
npm run supliful:labels      # -> brand/mediclab-labels/
```

Per SKU: `<sku>-print.pdf` (vector, fonts embedded, trim + bleed, no guides) to upload in Supliful's
label editor, and `<sku>-proof.jpg` showing trim (magenta), safe area (cyan) and the zone Supliful fills with
its Supplement Facts panel and barcode. `index.html` is the contact sheet and `report.json` the checklist.

- **Front-panel facts** (name, claim, key amount, net quantity, accent): `tools/supliful/labels/specs.json`.
- **Directions and warnings** come from the product's own store copy (`labels/catalog.json`, exported
  from Shopify), so the label and the product page say the same thing. Serious cautions are never dropped,
  and the label always ends with "Keep out of reach of children."
- **Brand** (wordmark, colours, disclaimer, distributor line): `labels/brand.json`.
- Type auto-fits; anything under 6 pt (21 CFR 101.105) or overflowing is flagged.

### Before printing (`report.json` lists each item per SKU)
1. **Label sizes are provisional** (bottle 7.5×3 in, gummy bottle 8×3.25 in, dropper 5×2 in, pouch
   5.5×7.5 in). Set each container to the dimensions shown in Supliful's label editor for that product
   and mark it `verified: true`.
2. **Net quantities marked `netVerified: false`** were inferred from the daily serving. Confirm them on the
   Supliful product page.
3. **`brand.json` → `distributorAddress`** is empty. FDA labeling requires the distributor's name and
   place of business.
4. **Droppers** (Methylene Blue, Lymphatic Support) carry too much safety copy for a 2 oz label at 6 pt.
   Use a fold-out (booklet) label or an outer carton, or take the larger size Supliful offers.
5. Claims are structure/function claims with the FDA disclaimer. Have them reviewed before printing.

## Tests

```bash
npm run test:supliful
```

37 tests, also run in CI. They cover the client (auth, retry policy, pagination, idempotency and
conflict adoption, problem parsing, a key-free log), signatures (checked against Supliful's
reference signer), product planning and sync, order forwarding, partial shipments into fulfillments,
event handling, the HTTP receiver, and label extraction and rendering. They run against in-memory fakes
of both APIs (`tools/supliful/test/fakes.mjs`); nothing touches the network.

## Updating the Supliful skill

```bash
npm run supliful:skill:update
```

Same content as `npx skills add supliful/agent-skills`, vendored so every session loads it.
