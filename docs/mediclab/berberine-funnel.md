# MedicLab Berberine funnel (Next Commerce)

**Sales page → checkout → upsell (same product) → thank you**, served at **https://try.mediclab.us/berberine/**,
campaign only (Campaigns App cart, checkout and upsell; no storefront), in the mediclab.us brand.

**Campaign 2475 "MedicLab Berberine Funnel"** (created and verified 2026-11-11: 39/39 PASS, Cart API $20.97 / $52.97 /
$29.97). **One product, two entry pages, one checkout:**

| Entry | Angle | Copy source |
|---|---|---|
| `/berberine/` | healthy glucose metabolism (the store's own positioning) | the live mediclab.us product page |
| `/weight-support/` | weight management, "natural GLP-1 support" | the delivered copy deck (`natural-glp1/copy-deck.md`), with its compliance lines: FDA disclaimer, "not a GLP-1 medication" FAQ, no pounds promised, example-review and model labels |

Both go to the same `/berberine-checkout/` → `/berberine-offer/` → `/berberine-thank-you/`, whose copy is angle-neutral.
The gates keep GLP-1 / weight wording off the glucose page and the shared pages, and require the weight page's
compliance lines. Note: the mediclab.us product page FAQ says Berberine is not sold as a weight-loss product; update it
so the store and the weight page agree.

| Step | Page (`campaigns/mediclab/src/berberine/`) | What it does |
|---|---|---|
| 1a | `berberine.html` → `/berberine/` | 24 sections from the live mediclab.us Berberine product page (the Slow Door, the Open-Door Meal Routine, research cards with doses, pharmacist checklist, label math, comparison, guarantee, offer, honest no-reviews block, objections, FAQ). Copy source: `berberine/source-mediclab-us-pdp.txt`, `source-faq.json`; images are the PDP's own. Offer picker: Monthly plan (default) or One bottle; every CTA opens checkout with that card selected (`?forceBundleId=plan\|one`), keeping the visit's query string |
| 1b | `weight-support.html` → `/weight-support/` | The copy deck's 20 sections, verbatim (`tools/mediclab/build_sales_page.py` from `natural-glp1/`), images in `images/ml/weight/` |
| 2 | `berberine-checkout.html` | Two plan cards, details, shipping, payment, summary with refill frequency. Monthly plan terms + required consent checkbox next to the button (`js/ml-plan-consent.js`) |
| 3 | `berberine-offer.html` | One more bottle, one-time, **$29.97** (43% off $52.97; voucher BERBERINE45 is 45% with .97 rounding). One tap, no card re-entry. No timer, no ratings |
| 4 | `berberine-thank-you.html` | Order receipt, what happens next (shipping, how to take it, refill reminder), the Empty-Bottle Promise |

## The offer (as on mediclab.us)

| Card / line | Store variant | Campaign package | Price |
|---|---|---|---|
| Monthly refill plan | `JTP4BERB` (id 6, option "Monthly refill plan") | `plan-6`, recurring | **$20.97** first bottle, then **$42.97 every 30 days** |
| One bottle, one-time | `JTP4BERB` (id 5, option "One-time purchase") | `hero-5` | **$52.97** |
| Upsell: one more bottle | `JTP4BERB` (id 5) | `hero-5` + voucher `BERBERINE45` | **$29.97** |

Free US shipping on everything (store method `default`, $0). A campaign takes one package per variant, so the monthly plan
has its own variant. **Both variants carry the exact Shopify SKU `JTP4BERB`** (what the warehouse ships); the import
tells them apart by their "Purchase" option, never by SKU.

The **3-month minimum** comes from the mediclab.us subscription terms (50% first-order refill plans: first order plus 2
refills). It is stated on the sales page, at checkout and in the terms. The platform does not enforce it; support does,
on cancellation requests.

## Product import (done)

`tools/mediclab/import_berberine.py` copies Berberine from mediclab.us (Shopify product 7806645436625) and keeps it in
sync: title, full description, SKU `JTP4BERB`, $52.97. Next product **#4** ("Berberine for Weight Management, 800 mg
Extract, 60 Capsules", as on Shopify). Idempotent: re-run it after any Shopify change; it corrects drift in title,
description, SKU and price, and fails if the Shopify SKU itself changes.
Ids: `tools/mediclab/berberine-ids.json`.

> Product **#7** is a duplicate from a re-run before the SKU lookup existed. It is **unpublished** and renamed
> "DUPLICATE - delete me". Delete it in Dashboard > Products (the API delete was not allowed from this session).

## Label (Weight Management*, 2026-11-11)

The bottle now reads **Berberine · Weight Management*** with the pills METABOLISM / CRAVINGS / GLUCOSE.

- Next product #4 gallery: the 8 delivered store images (`wm-01` … `wm-08`, ids in `tools/mediclab/berberine-ids.json`).
- Checkout gallery (`images/ml/product/berberine-1..6`) and pack shots (`images/ml/berberine/bottle-*`): the delivered mockups.
- Lifestyle photos that showed the old label (weight page: hero, doctor, review1-6, usage, solution; glucose page:
  with-meals, couple-cooking) were relabelled in place, the rest of each photo untouched:
  `tools/mediclab/relabel.py crop|paste` (bottle crop → image edit with the new pack shot as reference → feathered paste)
  and, where the model redrew the bottle at another size, `tools/mediclab/relabel_transplant.py` (label-only transplant
  aligned on the heart logo, light matched). Boxes and parameters: `tools/mediclab/relabel-boxes.json`.

## Brand (mediclab.us)

Fustat · forest green `#1D503A` pill buttons · deep green `#0B2A1B` header with the white logo · cream `#F5F1E8`
sections · lime `#E3F6A4` CTA on dark sections · sale red `#C4301C` badge. The deck's Jost / `#1F3D2C` / orange were
replaced to match the live store. `assets/css/sales.css` + `berberine.css` (sales page) and `assets/css/mediclab-funnel.css` (the rest).

## Launch runbook

Steps 1 to 4 are done (Stripe gateway group 1: card, Apple Pay, PayPal; campaign 2475 created, verified and wired).
Theme "MedicLab Funnels" is published (active) on try.mediclab.us. Left: **Allowed Domains** (step 5, Dashboard only),
then a test order (step 6).

> 2026-11-11: campaign 2475 had lost `bankcard` from its payment methods (only Apple Pay and PayPal were left), so
> `verify` failed. Restored through the skill's update path (one PATCH, journalled in the run manifest); verify passes
> again: card, Apple Pay, PayPal; express Apple Pay, PayPal; $20.97 / $52.97 / $29.97. Re-run `verify` after any
> Dashboard change to the campaign or the gateway.

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
   goes to the sales page with its query string kept (UTMs, click ids). Store pages `berberine`,
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
placeholder copy), Shopify cart links, missing FDA disclaimer, GLP-1 or weight-loss wording, missing honesty lines
(staged-models note, no-reviews block, medicine FAQ, the 73 mg math), a radio group with two pre-checked inputs, the upsell
code on checkout, undisclosed plan terms or a missing consent box, and a countdown on the upsell.

## Not done, on purpose

- **Express shipping ($5.97)**: the API token cannot create store shipping methods, so the FAQ line was removed. Add the
  method in Dashboard > Settings > Shipping, then put it back on the campaign and the FAQ.
- **Apple Pay / Google Pay / PayPal**: shown automatically once the gateway offers them.
- **Analytics (GTM, Meta, AppLovin)**: keys are empty in `_data/campaigns.json`; the adapters ship with the template.
- **Reviews**: none yet, and the page says so (as mediclab.us does); add verified buyer reviews as they arrive.
- **Old address**: `/glp1-support/` (the first build) now goes to `/berberine/`; its store page record can be deleted in
  the Dashboard.
