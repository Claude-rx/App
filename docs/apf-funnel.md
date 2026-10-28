# The Adaptive Peptide Foundation funnel

A one-time-purchase funnel for the Adaptive Peptide Foundation (the liquid foundation), served by the store itself on
**try.skinofab.com** beside the stick funnel (`docs/stick-funnel.md`), both in Campaigns App campaign 2211:

    listicle  ->  sales page  ->  checkout  ->  offer 1 (supply)  ->  offer 2 / its downsell  ->  offer 3 (brush) / its downsell  ->  thank you

| Page | Live URL | What it does |
|---|---|---|
| Listicle (entry) | https://try.skinofab.com/10-reasons-adaptive-foundation/ | "10 Reasons Why Women Over 45 Look Fresher With This 'Shade-Adapting' Foundation": the Facelove listicle's structure, this foundation's reasons, photos and reviews |
| Sales page | https://try.skinofab.com/adaptive-foundation-offer/ | the 20-section long sales page (`docs/apf-funnel/copy-deck.md`): 3 packs ($39 / $57 + 2 gifts / $75 + 3 gifts incl. the Lymphatic Brush), problem, mechanism, solution, comparison, labelled before/afters, proof, demo clips, guarantee, value stack, reviews with photos, FAQ |
| Checkout | https://try.skinofab.com/foundation-checkout/ | Apollo checkout on trust (rating, promises, guarantee by the button, 10 reviews with photos, FAQ), 3 pack cards (2-pack preselected), express PayPal / Apple Pay, Klarna, Link, exit pop APF10 |
| Offer 1 | https://try.skinofab.com/foundation-offer-1/ | supply cards: 2 bottles for the price of one ($39, "Add 1, get 1 FREE") or 6 for the price of three with a free Lymphatic Brush ($99, "Buy 3, get 3 FREE") |
| Offer 2 | https://try.skinofab.com/foundation-offer-2/ | one more bottle, 40% off ($23) |
| Offer 2, downsell | https://try.skinofab.com/foundation-offer-2b/ | one more bottle, 50% off ($19), the lowest price for one bottle anywhere |
| Offer 3 | https://try.skinofab.com/lymphatic-brush-offer/ | the Lymphatic Brush + case, 40% off ($14), with the brush's product page under the offer |
| Offer 3, downsell | https://try.skinofab.com/lymphatic-brush-offer-b/ | the brush, 60% off ($9), last chance |
| Thank you | https://try.skinofab.com/foundation-thank-you/ | receipt (the order and every accepted offer, each line "One-time purchase. Nothing renews."), next steps, the rest of the range |

Routes (`tools/funnel/funnels/apf.py`): offer 1 accepted goes to the brush offer (she just bought more bottles; offer 2
would sell her one more), declined to offer 2; offer 2 accepted goes to the brush offer, declined to its downsell, which
goes to the brush offer either way; the brush offer accepted goes to the thank-you page, declined to its downsell, which
ends on the thank-you page either way. An order that already includes a brush (the 3-bottle pack, the 6-bottle pack) is
sent past both brush offers to the thank-you page by `js/sf-offer-gate.js` (it reads the order's SKUs from a hidden
order-items list). Every page is `noindex`. Nothing in this funnel recurs.

**Proven live:** <<LIVE PROOF: order number, path, totals>>

## Before launch (owner)

1. **Cancel the QA test orders** (test card, no charge, flagged as tests; real orders in the store):
   <<TEST ORDERS>>. The stick funnel's are listed in `docs/stick-funnel.md`.
2. **The gifts.** The 2- and 3-bottle packs promise a SKINOFAB Blender brush and a mystery gift; the 3-bottle pack and
   offer 1's 6-bottle pack a Lymphatic Brush with its travel case. Fulfilment must pack them: the campaign's packages
   name them in their titles (the store sees "2 bottles + free gifts"), nothing else tells the warehouse.
3. **"While our launch stock of brushes lasts."** The sales page's scarcity section says the brush ships with the
   3-bottle pack while launch stock lasts, after which the pack ships with the Blender brush and mystery gift only.
   When that happens, rename package 8 and change the pack copy (`adaptive-foundation-offer.html` packs / value /
   scarcity, `foundation-checkout.html` bundles, `funnels/apf.py` PACKS, `check_apf.py` BRUSH_SKUS) in one pass.
4. **Store prices quoted.** The pages say the store sells one bottle for $47 and the 2-pack for $57 without the brush,
   and the brush for $24.95 (the 3-pack of brushes at $16.63 each). If a store price changes, change `why_now` on the
   sales page and the "reserved for you" copy in `tools/funnel/apf/offer_pages.py`, and rebuild.
5. **Tracking (before paid traffic).** `gtm_id` and `fb_pixel_id` on the `apf-funnel` entry of
   `campaigns/skinofab/_data/campaigns.json` are empty, so no tags load. Set them, and enable the matching providers in
   `src/apf-funnel/assets/config.js`.
6. **Shipping promise.** The pages promise "ships within 1 business day, free and tracked: 2–4 business days in the US,
   6–9 to Europe, 8–12 elsewhere" (the store's shipping policy). Keep the policy and the pages in step.
7. **The mystery gift** is "a mystery gift from our range", valued at $15 on the value stack. Decide what ships (a
   deluxe sample of the balm or the serum fits) and keep its value honest.

## Commerce (Campaigns App campaign 2211)

Every package is bought once (no subscription; the store offers refills only when she asks). The values below are the
campaign's; `campaign_spec.py` reads them live (`FUNNEL=apf`) into `campaign-spec.apf.json` and the pages are checked
against them on every build.

| Package ref | SKU | Sells | Price | Compare (list $59 a bottle) |
|---:|---|---|---:|---:|
| 6 | SKF-APF-1 | Adaptive Peptide Foundation, 1 bottle | $39.00 | $59 |
| 7 | SKF-APF-2-GIFTS | 2 bottles + free Blender brush + free mystery gift | $57.00 | $118 |
| 8 | SKF-APF-3-GIFTS | 3 bottles + both gifts + free Lymphatic Brush | $75.00 | $177 |
| 9 | SKF-APF-2 | 2 bottles (offer 1: "Add 1, get 1 FREE") | $39.00 | $78 (2 × $39) |
| 10 | SKF-APF-6-BRUSH | 6 bottles + free Lymphatic Brush (offer 1: "Buy 3, get 3 FREE") | $99.00 | $234 (6 × $39) |
| 11 | SKF-LYB-1T | The Lymphatic Brush + free travel case | $24.95 | — |

| Offer ref | Code | Package | Off | Lands at (rounded down to the dollar) |
|---:|---|---:|---:|---|
| 6 | APF10 | 6, 7, 8 | 10% | the checkout's exit pop: $35 / $51 / $67 |
| 7 | APF40 | 6 | 40% | $23.00 (shown as 41% off) |
| 8 | APF50 | 6 | 50% | $19.00 (51% off) |
| 9 | BRUSH40 | 11 | 40% | $14.00 (44% off) |
| 10 | BRUSH60 | 11 | 60% | $9.00 (64% off) |

- Offer 1 has no voucher: each supply card is its own package at its own price, so what the SDK adds is exactly the
  card she pressed. The 2-bottle card compares with two bottles at the funnel's $39, the 6-bottle card with six.
- Whole-dollar rounding (the owner's choice) makes the shown discounts a little larger than the codes'; the pages show
  the SDK's real `{discount}`, never a fixed "40%".
- Shipping: one method (ref 1), free. Payment: card, Klarna, Link, PayPal; express PayPal and Apple Pay. Every charge is
  once, so Klarna and Link raise no renewal question here.
- The post-purchase codes never appear on the checkout, and the checkout has no coupon box, so they can't be typed
  in early.
- The sales page's packs link to the checkout with `?forceBundleId=apf-1|apf-2|apf-3`; the page writes nothing to the
  cart.

### The sales page

Twenty sections in the long-sales-page order, written for Linda, 56 (`docs/apf-funnel/persona.md`), from the page's
frontmatter (`src/apf-funnel/adaptive-foundation-offer.html`); `tools/funnel/apf/copy_deck.py` renders that frontmatter
as `docs/apf-funnel/copy-deck.md` and validates it with the skill's validator (PASS; one accepted warning, a long table
row). Sections 1–5 sell on their own above the fold: hero with the how-it-works loop, headline, summary, seven benefits
with the guarantee, the three packs with gifts and the button. Then the problem (her day, hour by hour), its mechanism
("the fixed-shade trap"), the solution (encapsulated pigments in a serum base), the comparison table, the complaints the
formula answers, four before/afters (persona photos with the skin tone evened and every line kept, each labelled "AI
illustration, not a customer photo"), proof (the imported reviews' numbers, the actives on the label, what we don't
claim), the promise, four steps with four demo clips of women 45+ (the first with sound), the 30-Day Daylight Promise,
the value stack ($225.95 of value for $75, and why the price is only here), what is limited (the launch brush), the
review wall with the buyers' own photos and nine reviews (two of them four stars), eleven questions, how to reach us,
and the packs again. A sticky bar on phones follows the chosen pack.

### The checkout

The checkout sells on trust, not on the product (`foundation-checkout.html`, `_includes/sf-checkout-trust.html`), as the
stick funnel's does: the rating in one sentence that says whose it is ("of this foundation, at our earlier store"), four
promises, three reviews before the payment step on a phone, the guarantee in one line right above the order button, the
proof column (ratings by stars, ten reviews with photos, the guarantee card, "Before you order"), and by the button one
box with the live pay line ("$57.00 today, once, for 2 bottles with a free Blender brush and a free mystery gift. Nothing
renews.") and the one-time terms. Three pack cards (2-pack preselected, "Most popular"; 3-pack "Best value"), each
"One-time. Free shipping" with its gifts. The exit pop offers APF10. `check_apf.py` fails the build on a card that does
not say it is bought once or does not name its gifts, a coupon box, a post-purchase code, a missing guarantee line,
fewer than 8 review cards or one without a photo, or a rating other than the foundation's.

### The offer pages

`tools/funnel/apf/offer_pages.py` writes the five pages from `funnels/apf.py` and the CampaignSpec.

1. **Offer 1, the supply cards** (`_includes/sf-supply-cards.html`, `js/sf-supply.js`, `css/sf-offers.css`): two cards
   in the Obvi "month supply" style, the 2-bottle card first and preselected ("Most popular, SAVE 50%": the smaller
   step, and the one a first-offer accept adds), the 6-pack beside it ("Best value, SAVE 58%"), each with its badge, the
   pack image, the deal ("Add 1, get 1 FREE"; "Buy 3, get 3 FREE" + the free brush), the per-day and per-bottle price, the
   stars, the crossed-out and the live price, BUY NOW, and "Charged once". The cards are the SDK's bundle selector
   inside the one offer, scoped with `data-next-upsell-context` (it never touches a live cart). Every BUY NOW is the
   offer's own add action (the SDK adds the selected card); a real click on a card that is not selected is stopped,
   the card is selected and the button clicked again for her (`js/sf-supply.js`), so the order gets the card she
   pressed, while the closing card's proxied click adds the selection. Proven with the upsell request intercepted:
   card 2 sends package 9, card 1 package 10, the closing card the selected one. Under the cards: the guarantee row,
   the decline link, the foundation's how-it-works loop beside its four parts, why women stock up, and the closing
   card priced from the selected card.
2. **Offer 2 and its downsell**: Apollo's single offer with the voucher on a hidden upsell-scoped selector (as the stick
   funnel's), four photos, the bullets, today's price against $39, the button and the terms ("$23.00 today (41% off),
   charged once… Nothing renews"), then the how-it-works loop, "reserved for you" (the store's $47 for one beside
   today's, charged once), three reasons to keep a second bottle, the closing card. The downsell says it is the lowest
   price for one bottle anywhere.
3. **Offer 3, the brush, and its downsell**: the same offer layout with the brush's gallery and bullets, then the brush's
   four sweeps beside its loop, then the brush's own product page (`_includes/sf-brush-pdp.html`, from
   `tools/persona/brush_copy.py`'s claims: the look of morning puffiness, a light dry massage, no draining or lifting):
   the problem, its root, the solution, how to use it, what to expect, versus stones and rollers, what's in the box, the
   questions; then "reserved for you" ($24.95 in the store) and the closing card. The downsell is the last chance at
   60% off. Both skip an order that already has a brush.

Every offer page carries the gate (`js/sf-offer-gate.js`): an order the platform marks as unable to take a one-click
offer goes straight to the thank-you page; her first name follows "Reserved for you".

## Versus the Facelove listicle and the stick's

The listicle follows the Facelove structure reason for reason, as the stick funnel's does, for this product:

- **Product and images**: the liquid foundation's own approved photos from the store (women past 45 with the real
  bottle, the white dots, the infographics), the product sheet's renders for the packs, the buyers' own review photos,
  four vetted demo clips of women 45+. No new AI generation (no image model had credit on 27 Oct 2026).
- **Before/after**: persona photos with the skin tone evened and nothing else, each labelled "AI illustration, not a
  customer photo" (`funnel_images.even_tone`).
- **Reason 5** (Facelove: SPF): "made not to turn orange by the afternoon", with a note that it has no SPF by design.
- **Reason 9** (Facelove: "dermatologist recommended"): the foundation's real ratings, 9,855 reviews averaging 4.8,
  drawn with the count per star and labelled as imported from our earlier store.
- **Reviews**: this foundation's own published reviews, word for word, each "Verified buyer, from our earlier store"
  (they are its reviews: no sister-product label needed, unlike the stick's).
- **Claims**: "adapts to your skin tone", never every or all tones; "designed not to settle"; no SPF, no percentages, no
  "reverses aging", no doctor or expert, no scarcity counts, no renewal wording; `check_apf.py` fails the build on any.

## How it is built

The pages are a second slug of the same Campaign Page Kit project (`campaigns/skinofab/src/apf-funnel/`, Apollo family,
Campaign Cart SDK 0.4.43, its own `config.js` with the campaign's public key), with:

    campaigns/skinofab/
      _data/campaigns.json            the apf-funnel entry (store fields, SDK pin)
      src/apf-funnel/                 the pages, layouts, includes, assets
      campaign-spec.apf.json          the CampaignSpec (local spec; tools/funnel/campaign_spec.py with FUNNEL=apf)
      campaign-build-brief.apf.json   the operator brief for Campaigns OS
      design-source-apf/              the Facelove listicle and the store's own foundation page, with screenshots

| Tool | Does |
|---|---|
| `funnels/apf.py` | the funnel's pages, routes, packages, vouchers, packs and offer tiers (loaded by `funnel.py` with `FUNNEL=apf`) |
| `apf/commerce.py` | the campaign setup, idempotent: the store variants, packages 6–11, offers 6–10; `--verify` checks the Cart API against `funnels/apf.py` |
| `apf/images.py` | the images and clips: the store's photos, pack cards, labelled before/afters, review crops, demo clips, the thank-you page's range cards |
| `apf/offer_pages.py` | the five offer pages (supply cards, offer 2 and its downsell, the brush offer and its downsell) |
| `apf/copy_deck.py` | `docs/apf-funnel/copy-deck.md` from the sales page's frontmatter, validated |
| `apf/check_apf.py` | the offline checks (below); the store build fails on any problem |
| `campaign_spec.py`, `deploy_theme.py`, `store_pages.py`, `design_source.py`, `funnel_check.mjs`, `live_order.mjs` | the shared tools, with `FUNNEL=apf` |

### Rebuild and deploy

`tools/build_store.sh` runs both funnels after the theme. To rebuild only this one:

    python3 -I tools/funnel/apf/images.py <work dir>
    python3 -I tools/funnel/apf/offer_pages.py && python3 -I tools/funnel/apf/copy_deck.py
    (cd campaigns/skinofab && npx --no-install campaign-build)
    FUNNEL=apf python3 -I tools/funnel/deploy_theme.py campaigns/skinofab/_site/apf-funnel skinofab-theme
    python3 -I tools/funnel/apf/check_apf.py skinofab-theme

then push the changed theme files with ntk and, for new pages, `FUNNEL=apf python3 -I tools/funnel/store_pages.py`.
After a campaign change, run `FUNNEL=apf python3 -I tools/funnel/campaign_spec.py` first: the offer pages and the
checks take their numbers from the spec. The theme serves this funnel's assets from `assets/sfa/` (the stick's from
`assets/sfc/`); the hosting notes in `docs/stick-funnel.md` (30-minute page cache, `?preview_theme=34`) apply.

### Checks

- `python3 -I tools/funnel/apf/check_apf.py` (offline, every build): every page built with its SDK meta tags and
  linking only inside the funnel; the checkout's three cards (one per package, one preselected, each bought once with
  its gifts named), the pay line, no coupon box, no post-purchase code, the exit pop on APF10, the guarantee line above
  the button, the reviews; the sales page's packs (price, crossed-out list price × bottles, saving) against the
  campaign; offer 1's cards (package, price, crossed-out, per-bottle and per-day arithmetic, charged once, an add and a
  skip action in one upsell-scoped offer); offers 2 and 3 (package, voucher, landed fallback price, charged once, the
  brush skip rule on the brush offers only); the thank-you page's terms per SKU; the host redirect and policy links;
  the theme templates and assets; the claims rules, nothing recurring, no timer, AI labels, the reviews' origin, SPF
  only ever as absent.
- `FUNNEL=apf node tools/funnel/funnel_check.mjs <base-url> <out-dir> [--served]`: every page at 390 and 1440,
  screenshots (long pages in parts), console errors, overflow, live prices; `ORDER_REF=<ref_id>` opens the offer and
  thank-you pages with a real order.
- `FUNNEL=apf node tools/funnel/live_order.mjs https://try.skinofab.com <out-dir> [--path accept,decline,…] [--tier
  supply-b3g3]`: one real test order through the live funnel, following the routes from each page's own meta tags.

### Campaigns OS

<<CAMPAIGNS OS: lifecycle run and verdict>>

The project holds one Build Packet at a time (`campaign-runtime.build.json` and `.campaign-runtime/` are written per
`start`): the stick funnel's run is kept under `campaigns/skinofab/runs/stick-funnel/`; to run its lifecycle again,
`start` it from its own spec, source and brief as `docs/stick-funnel.md` describes.
