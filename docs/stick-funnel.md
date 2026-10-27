# The Adaptive Foundation Stick funnel

A full subscription funnel for the Adaptive Foundation Stick, served by the store itself:

    listicle  ->  product page  ->  checkout  ->  special offers 1-4 (post-purchase, one click)  ->  thank you

| Page | Live URL | What it does |
|---|---|---|
| Listicle (entry) | https://skinofab.29next.store/10-reasons-foundation-stick/ | "10 Reasons Why Women Over 45 Look Fresher With This 'Shade-Adapting' Foundation Stick": Facelove's listicle structure, SKINOFAB product and images |
| Product page | https://skinofab.29next.store/foundation-stick-offer/ | gallery, 2 pack cards ($37 / 1 stick, $47 / 2 sticks + free Lymphatic Brush), refill terms, guarantee, science video, FAQ |
| Checkout | https://skinofab.29next.store/stick-checkout/ | Apollo checkout, 2 pack cards (2-pack preselected), express PayPal / Apple Pay, Klarna, Link, exit pop STICK10 |
| Special offer 1 | https://skinofab.29next.store/stick-special-1/ | one more stick, 50% off the first charge |
| Special offer 2 | https://skinofab.29next.store/stick-special-2/ | the Lymphatic Brush + case, 20% off |
| Special offer 3 | https://skinofab.29next.store/stick-special-3/ | the PDRN Plumping Balm, 20% off |
| Special offer 4 | https://skinofab.29next.store/stick-special-4/ | the EGF + NAD+ Firming Serum, 20% off |
| Thank you | https://skinofab.29next.store/stick-thank-you/ | receipt (the order and every accepted offer) and next steps |

Accept and decline both go to the next offer; offer 4 goes to the thank-you page. Every page is `noindex`.

## Before launch (owner)

1. **Allow the store's domain on the campaign (one dashboard step, required).** Campaigns App -> campaign
   **2211 "SKINOFAB Foundation Stick Funnel"** -> Settings -> Allowed Domains -> add `skinofab.29next.store`
   (Production). Until then the browser blocks the SDK's calls (CORS) on the live pages: prices, checkout and offers
   stay empty. `localhost` is already a Development domain, which is how the funnel was tested. The Admin API has no
   endpoint for this setting. Then run the live check (below, "Checks").
2. **Cancel the 5 QA test orders**: 101436, 101437, 101439, 101440, 101445 (test card, no charge; the checkout with
   offers accepted and declined). They are real orders in the store and each started a subscription.
3. **Upsell 4's discount.** The brief named the serum without a discount; it is offered at 20% off (SERUM20) like
   offers 2 and 3 ($22 instead of $27.95). For full price, offer 4 would come off `special-4` in `funnel.py` and
   the page would show the package price (a small change in `upsell_pages.py` and `check_funnel.py`).
4. **Reviews.** The listicle, product page and checkout show the store's existing reviews of the **Adaptive Peptide
   Foundation** (the liquid foundation), each labelled as such, because the stick has no reviews of its own yet. Swap
   them for stick reviews as they come in; never relabel foundation reviews as stick reviews (FTC).
5. **Tracking.** `gtm_id` and `fb_pixel_id` in `campaigns/skinofab/_data/campaigns.json` are empty (no tags). Set
   them, and the matching providers in `src/stick-funnel/assets/config.js`, before sending paid traffic.

## Commerce (Campaigns App campaign 2211)

Every package is a subscription ("all subscription"). The values below are the campaign's; `campaign_spec.py` reads
them live and the pages are checked against them on every build.

| Package ref | Sells | First charge | Then |
|---:|---|---:|---|
| 1 | Adaptive Foundation Stick, 1 stick | $37.00 | $37.00 every 28 days |
| 2 | 2 sticks + free Lymphatic Brush | $47.00 | $47.00 every 56 days |
| 3 | The Lymphatic Brush + free case | $24.95 | $24.95 every 90 days |
| 4 | PDRN Plumping Balm | $19.95 | $19.95 every 28 days |
| 5 | EGF + NAD+ Firming Serum | $27.95 | $27.95 every 56 days |

| Offer ref | Code | Package | Off | Lands at (rounded down to the dollar) |
|---:|---|---:|---:|---|
| 1 | STICK50 | 1 | 50% | $18.00 (shown as 51% off) |
| 2 | BRUSH20 | 3 | 20% | $19.00 (24% off) |
| 3 | BALM20 | 4 | 20% | $15.00 (25% off) |
| 4 | SERUM20 | 5 | 20% | $22.00 (21% off) |
| 5 | STICK10 | 1, 2 | 10% | the checkout's exit pop, once per visit |

- An offer's discount is on its **first charge only**; renewals are at the package's recurring price. Each offer
  page says so in a sentence ("After that, $X every N days for this one until you cancel") next to its button.
- Whole-dollar rounding (the owner's choice) makes the shown discounts a little larger than the codes'; the pages show
  the SDK's real `{discount}`, never a fixed "50%".
- Shipping: one method (ref 1), free. Payment: card, Klarna, Link, PayPal; express PayPal and Apple Pay.
- The post-purchase codes never appear on the checkout, and the checkout has no coupon box, so they can't be typed
  in early.

## Versus the Facelove listicle

The listicle follows https://facelove-cosmetics.com/pages/10-reasons-why-foundating-stick-2026-new reason for reason
(same structure, same kinds of images, same CTA box and closing), with these deliberate differences:

- **Product and images**: the black SKINOFAB stick with its real wordmark, women 45+ on white, made with gpt-image-2
  (prompts in `tools/persona/image_prompts.json`, "stick-funnel").
- **Before/after**: every before/after image carries "AI illustration, not a customer photo".
- **Claims** follow the stick's spec rules (SKF-ADFS-001 section 8, see `docs/foundation-stick.md`): fair to medium
  skin, not "every skin tone"; "made not to settle", not "won't settle"; no SPF, no percentages, no "reverses aging",
  no doctor or expert endorsements, no scarcity counts. `check_funnel.py` fails the build on any of them.
- **Reviews**: the store's real foundation reviews, labelled (Facelove shows stick reviews).
- **Prices and terms**: SKINOFAB's subscription offer, with the refill terms stated on every page that sells.

## How it is built

The pages are a [Campaign Page Kit](https://github.com/NextCommerceCo/next-campaign-page-kit) project on the Apollo
template family, using the Campaign Cart SDK 0.4.43:

    campaigns/skinofab/
      _data/campaigns.json            store fields, SDK pin, og_image
      src/stick-funnel/               the pages, layouts, includes, assets (config.js holds the public campaign key)
      campaign-spec.json              the CampaignSpec (local spec; written by tools/funnel/campaign_spec.py)
      campaign-build-brief.json       the operator brief Campaigns OS recorded
      design-source/                  what the listicle and product page were designed from, with screenshots

`tools/funnel/` holds everything that writes or checks them; nothing under `_site/` or `skinofab-theme/` is edited by
hand.

| Tool | Does |
|---|---|
| `funnel.py` | the one source of the pages, their order, routes, packages, offers and SDK meta tags |
| `campaign_spec.py` | writes `campaign-spec.json` from `funnel.py` and one live read of campaign 2211 |
| `copy_includes.py` | the product page's tabs and FAQ includes from `tools/persona/stick_copy.py` |
| `upsell_pages.py` | the four special-offer pages (frontmatter from the spec: package, voucher, prices, terms) |
| `funnel_images.py` | the listicle and product images (collages, labelled before/afters, review photos, video) |
| `deploy_theme.py` | turns the built pages into theme templates `templates/pages/page.<file>.html` and assets `assets/sfc/` |
| `store_pages.py` | creates or updates the 8 store pages that render those templates (Admin API, `$NEXT_API_TOKEN`) |
| `check_funnel.py` | offline checks (below); the store build fails on any problem |
| `funnel_check.mjs` | Playwright run of every page at 390 and 1440: screenshots, console errors, overflow, live prices |
| `design_source.py` | the design-source manifest Campaigns OS reads |

### Rebuild and deploy

`tools/build_store.sh` runs the funnel after the theme: includes, offer pages, images, the Page Kit build,
`deploy_theme.py`, then `check_funnel.py`. To rebuild only the funnel:

    python3 -I tools/funnel/copy_includes.py && python3 -I tools/funnel/upsell_pages.py
    python3 -I tools/funnel/funnel_images.py <work dir>
    (cd campaigns/skinofab && npx --no-install campaign-build)
    python3 -I tools/funnel/deploy_theme.py campaigns/skinofab/_site/stick-funnel skinofab-theme
    python3 -I tools/funnel/check_funnel.py skinofab-theme

then push the changed theme files with ntk as for the rest of the theme. After a campaign change (price, interval,
voucher), run `campaign_spec.py` first: the offer pages and the checks take their numbers from the spec.

Hosting notes: the store serves a page at `/<slug>/` (not `/pages/<slug>/`) and renders `page.<template>.html`; the
theme CDN flattens asset folders, so `deploy_theme.py` gives each asset a unique `sfc-<name>-<hash>` name; NEXT
compiles theme CSS with libsass, which rejects `min()`/`max()` with mixed units, so they are written `MIN()`/`MAX()`
(CSS functions are case-insensitive). Templates are wrapped in `{% verbatim %}` so the SDK's `{tokens}` survive.

### Checks

- `python3 -I tools/funnel/check_funnel.py` (offline, every build): every page built with its SDK meta tags and
  linking only inside the funnel; one checkout card per package, one preselected, each stating "Then $X every N days"
  as the campaign has it; no coupon box and no post-purchase code on the checkout; the exit pop applies STICK10; each
  offer page adds its own package with its own voucher (upsell-scoped, never the live cart), states its renewal and
  falls back to its landed price; the product page's packs match the campaign; theme templates generated, with every
  asset on disk; and the claims rules above.
- `node tools/funnel/funnel_check.mjs <base-url> <out-dir> [--served]`: `http://127.0.0.1:<port>/stick-funnel/`
  for the local build, `https://skinofab.29next.store --served` for the live pages (after step 1 above).

### Campaigns OS

The funnel went through the Campaigns OS 1.60.0 lifecycle (brief, build, theme, Page Kit parity, polish capture,
deploy, QA resolve, QA run with 5 test orders): verdict **ready_with_exceptions**, commercial parity pass. Run it from
`campaigns/skinofab` with:

    export LANG=C.UTF-8 CAMPAIGNS_OS_TELEMETRY=off NODE_USE_ENV_PROXY=1
    npx --no-install campaigns-os doctor --packet campaign-runtime.build.json
    npx --no-install campaigns-os qa run --packet campaign-runtime.build.json --base-url http://127.0.0.1:<port> --browser --test-order common

`LANG=C.UTF-8` because the container's default locale (`en_US@posix`) breaks the SDK's number formatting;
`NODE_USE_ENV_PROXY=1` so Node's fetch uses the session proxy; telemetry off keeps verdicts local. A `qa run` places
real test orders (up to 6) that need cancelling afterwards. QA runs on localhost; the live store needs step 1 first.
Remaining doctor advisories: wrapper tags inside the two design-source captures (references, not pages), and the
brief's payment code "card" (the campaign calls it "bankcard").
