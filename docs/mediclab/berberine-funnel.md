# MedicLab Berberine funnel (Next Commerce)

**Sales page → checkout → upsell (same product) → thank you**, served at **https://try.mediclab.us/glp1-support/**,
campaign only (Campaigns App cart, checkout and upsell; no storefront), in the mediclab.us brand.

| Step | Page (`campaigns/mediclab/src/berberine-glp1/`) | What it does |
|---|---|---|
| 1 | `glp1-support.html` → `/berberine-glp1/glp1-support/` | The copy deck's 20 sections, verbatim (`copy-deck.md`, `persona-weight-segment.md`). Offer picker: Monthly plan (default) or One bottle; every CTA opens checkout with that card selected (`?forceBundleId=plan\|one`) |
| 2 | `berberine-checkout.html` | Two plan cards, details, shipping, payment, summary with refill frequency. Monthly plan terms + required consent checkbox next to the button (`js/ml-plan-consent.js`) |
| 3 | `berberine-offer.html` | One more bottle, one-time, **$29.97** (45% off $52.97). One tap, no card re-entry. No timer, no ratings |
| 4 | `berberine-thank-you.html` | Order receipt, what happens next (shipping, how to take it, refill reminder), the Empty-Bottle Promise |

## The offer (copy deck section 05)

| Card / line | Store variant | Campaign package | Price |
|---|---|---|---|
| Monthly GLP-1 Support Plan | `JTP4BERB-SUB` (id 6) | `plan-6`, recurring | **$20.97** first bottle, then **$42.97 every 30 days** |
| One bottle, one-time | `JTP4BERB` (id 5) | `hero-5` | **$52.97** |
| Upsell: one more bottle | `JTP4BERB` (id 5) | `hero-5` + voucher `BERBERINE45` | **$29.97** |

Free US shipping on everything (store method `default`, $0). A campaign takes one package per variant, so the monthly plan
has its own variant; both variants ship the same bottle.

The **3-month minimum** is a policy (stated on the sales page, at checkout and in the subscription terms). The platform
does not enforce it; support does, on cancellation requests.

## Product import (done)

`tools/mediclab/import_berberine.py` copied Berberine from mediclab.us (Shopify product 7806645436625): title, full
description, SKU `JTP4BERB`, $52.97, 8 gallery images. Next product **#4**. Idempotent (finds the product by SKU).
Ids: `tools/mediclab/berberine-ids.json`.

> Product **#7** is a duplicate from a re-run before the SKU lookup existed. It is **unpublished** and renamed
> "DUPLICATE - delete me". Delete it in Dashboard > Products (the API delete was not allowed from this session).

## Brand (mediclab.us)

Fustat · forest green `#1D503A` pill buttons · deep green `#0B2A1B` header with the white logo · cream `#F5F1E8`
sections · lime `#E3F6A4` CTA on dark sections · sale red `#C4301C` badge. The deck's Jost / `#1F3D2C` / orange were
replaced to match the live store. `assets/css/sales.css` (sales page) and `assets/css/mediclab-funnel.css` (the rest).

## Launch runbook

Blocked on one Dashboard step today: **the store has no payment gateway**, so the gateway group "Default" carries no
currency and the Campaigns App refuses a campaign on it.

1. **Dashboard > Settings > Payments**: add the card gateway (a Test gateway is enough to QA). Also: business address and
   support phone in Settings > General.
2. Build and review the campaign plan (nothing is sent):
   ```bash
   bash .claude/skills/next-campaigns-create/next-campaigns-create.sh discover --store mediclab
   python3 -I tools/mediclab/campaign_plan.py
   ```
   Check the 3 landed prices: $20.97 · $52.97 · $29.97 (upsell). Copy the printed `Plan SHA-256`.
3. Create it (the token is read from `.env`, gitignored, `MEDICLAB_NEXT_ADMIN_API_TOKEN=`):
   ```bash
   bash .claude/skills/next-campaigns-create/next-campaigns-create.sh apply --plan next-campaigns-create-runs/mediclab/campaign-plan.json --yes --plan-sha256 <hash>
   bash .claude/skills/next-campaigns-create/next-campaigns-create.sh verify --manifest next-campaigns-create-runs/mediclab/run-manifest.json --plan next-campaigns-create-runs/mediclab/campaign-plan.json
   ```
4. Wire the pages to the campaign and rebuild:
   ```bash
   python3 -I tools/mediclab/wire_funnel.py
   cd campaigns/mediclab && npm run build:static && cd ../.. && python3 -I tools/mediclab/check_funnel.py --live
   ```
5. Publish to **https://try.mediclab.us** (the store's primary domain), campaign only:
   ```bash
   tools/mediclab/publish.sh            # build, gates, theme templates, ntk push to theme "MedicLab Funnels" (#1)
   ```
   Each funnel page is a standalone template in theme #1 (`mediclab-theme/`): no storefront layout, cart, checkout or
   scripts, only the Campaign Cart SDK. Every other storefront route (home, catalogue, cart, search, 404, other pages)
   goes to the sales page with its query string kept (UTMs, click ids). Store pages `glp1-support`,
   `berberine-checkout`, `berberine-offer`, `berberine-thank-you` render them (`FUNNEL=mediclab tools/funnel/store_pages.py`).
   Then: **Dashboard > Storefront > Themes > publish "MedicLab Funnels"**, and add `try.mediclab.us` to the campaign's
   **Allowed Domains** (Campaigns App > campaign > Settings).
6. Place a test order with the Test gateway on both cards and accept the upsell; confirm the recurring line shows
   "every 30 days" on the receipt.

## Checks

```bash
python3 -I tools/mediclab/test_wire_funnel.py     # plan shaping + page wiring (6 tests)
cd campaigns/mediclab && npm run build:static && npm test   # build + funnel gates
```

The gates (`tools/mediclab/check_funnel.py`, also in CI) fail on starter demo content (demo API key, fake review counts,
placeholder copy), Shopify cart links, missing FDA disclaimer, a missing copy-deck section, the upsell code on checkout,
undisclosed plan terms or a missing consent box, and a countdown on the upsell.

## Not done, on purpose

- **Express shipping ($5.97)**: the API token cannot create store shipping methods, so the FAQ line was removed. Add the
  method in Dashboard > Settings > Shipping, then put it back on the campaign and the FAQ.
- **Apple Pay / Google Pay / PayPal**: shown automatically once the gateway offers them.
- **Analytics (GTM, Meta, AppLovin)**: keys are empty in `_data/campaigns.json`; the adapters ship with the template.
- **Reviews**: the deck's six are labelled example reviews; replace with verified buyer reviews after 30 to 60 days.
- **Clinician photo**: a model, disclosed on the page; replace with a consenting, named professional.
