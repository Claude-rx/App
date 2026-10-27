# The Adaptive Foundation Stick funnel

A full subscription funnel for the Adaptive Foundation Stick, served by the store itself on **try.skinofab.com**:

    listicle  ->  product page  ->  checkout  ->  special offers 1-4 (post-purchase, one click)  ->  thank you

| Page | Live URL | What it does |
|---|---|---|
| Listicle (entry) | https://try.skinofab.com/10-reasons-foundation-stick/ | "10 Reasons Why Women Over 45 Look Fresher With This 'Shade-Adapting' Foundation Stick": Facelove's listicle structure, SKINOFAB product and images |
| Product page | https://try.skinofab.com/foundation-stick-offer/ | gallery, 2 pack cards ($37 / 1 stick, $47 / 2 sticks + free Lymphatic Brush), refill terms, guarantee, science video, FAQ |
| Checkout | https://try.skinofab.com/stick-checkout/ | Apollo checkout, 2 pack cards (2-pack preselected), express PayPal / Apple Pay, Klarna, Link, exit pop STICK10 |
| Special offer 1 | https://try.skinofab.com/stick-special-1/ | one more stick, 50% off the first charge |
| Special offer 2 | https://try.skinofab.com/stick-special-2/ | the Lymphatic Brush + case, 20% off |
| Special offer 3 | https://try.skinofab.com/stick-special-3/ | the PDRN Plumping Balm, 20% off |
| Special offer 4 | https://try.skinofab.com/stick-special-4/ | the EGF + NAD+ Firming Serum, 20% off |
| Thank you | https://try.skinofab.com/stick-thank-you/ | receipt (the order and every accepted offer) and next steps |

Accept and decline both go to the next offer; offer 4 goes to the thank-you page. Every page is `noindex`.

**Proven live (27 Oct 2026):** test order **101449** on https://try.skinofab.com: checkout 2 sticks + brush $47, offer 1
accepted ($18), offer 2 declined ($19 shown), offer 3 accepted ($15), offer 4 declined ($22 shown), thank-you page with
each line's renewal; order total $80.00, confirmed by the campaign API (`tools/funnel/live_order.mjs`).

## Before launch (owner)

1. **The domain (done, 27 Oct 2026).** The funnel's host is **`try.skinofab.com`** (`funnel.FUNNEL_HOST`): a
   Production domain in the Campaigns App (the only one the campaign's API answers), a CNAME `try` ->
   `dns.29next.store` at GoDaddy, and a domain of the NEXT store (SSL by the store). The store answers on its other
   domains too (skinofab.29next.store, skinofab.com), where the SDK is refused (CORS): every funnel page sends a visit
   there to the same page on try.skinofab.com, path and query kept (production builds only), and the checkout,
   offers and thank-you page say so if the SDK still can't load (`sf-failsafe.js`). Policy links point to
   try.skinofab.com. To move the funnel to another domain: allow it in the Campaigns App, link it to the store, set
   `FUNNEL_HOST` and `funnel_host` / `store_*` in `_data/campaigns.json`, run `campaign_spec.py`, rebuild.
2. **Cancel the 6 QA test orders**: 101436, 101437, 101439, 101440, 101445 (local QA) and 101449 (the live run) (test
   card, no charge, flagged as tests). They are real orders in the store and each started a subscription.
3. **Upsell 4's discount.** The brief named the serum without a discount; it is offered at 20% off (SERUM20) like
   offers 2 and 3 ($22 instead of $27.95). For full price, offer 4 would come off `special-4` in `funnel.py` and
   the page would show the package price (a small change in `upsell_pages.py` and `check_funnel.py`).
4. **Reviews.** The listicle, product page and checkout show the store's existing reviews of the **Adaptive Peptide
   Foundation** (the liquid foundation), each labelled as such, because the stick has no reviews of its own yet. Swap
   them for stick reviews as they come in; never relabel foundation reviews as stick reviews (FTC).
5. **Tracking (before paid traffic).** `gtm_id` and `fb_pixel_id` in `campaigns/skinofab/_data/campaigns.json` are
   empty, so no tags load and Meta gets no page views or purchases. Set them, and enable the matching providers in
   `src/stick-funnel/assets/config.js` (`analytics.providers.gtm` / `.facebook` with the pixel id; `storeName` is
   already `skinofab`, for Meta's purchase deduplication).
6. **The 2-stick refill ships a brush every time.** Package 2 is "2 sticks + free Lymphatic Brush" and every refill is
   that same package, so each 56-day refill includes a brush, and the FAQ says so ("Each refill is the same pack as
   your first order"). If refills should be sticks only, the 2-pack needs its own sticks-only refill package; tell me
   and the FAQ, the cards and the checks change with it.
7. **Offer cadence (your call).** Offer 1 adds a stick that refills every 28 days on its own, so a 2-pack buyer who
   accepts gets 4 sticks every 56 days; offer 2's brush refills every 90 days. Each page states its own renewal by
   its button. If you'd rather have offer 1 ride the order's own cycle, or show offer 2 only to 1-stick buyers (2-stick
   buyers already get a brush), that is a campaign change plus a page rule.

8. **Klarna and Link with refills.** Every package renews, and Klarna and Link are offered at checkout. Confirm with
   NEXT that an order paid with Klarna (or Link) can be charged again for its refills; if not, take them off the
   campaign's payment methods. The one-click offers are safe either way: an order the platform marks as unable to take
   them (`supports_post_purchase_upsells`) skips straight to the thank-you page (`sf-offer-gate.js`).

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
  in early. The offers' names are the shopper's ("10% off your stick pack today", "50% off your extra stick (first
  charge)"...): the order summary and receipt show them.
- Offer 4 (the serum) is not shown for delivery in the EU, the EEA, Switzerland or the UK: its EGF (sh-Oligopeptide-1)
  is not allowed in cosmetics there (`docs/egf-nad-serum.md`); such an order goes on to the thank-you page.
- Crossed-out prices compare with buying single sticks in this funnel (16 CFR 233): the 2-stick pack is $47 against two
  1-stick packs at $37 ("SAVE $27"); the 1-stick pack has none.

### The special offer pages

Each offer page, top to bottom (`tools/funnel/upsell_pages.py`):

1. **Hero band**: "Your order is placed", the offer and its price.
2. **The offer**: photos, bullets, today's price against the regular price, the button and the renewal terms.
3. **How it works / how to use it** (`_includes/sf-upsell-how.html`): a muted loop beside the product page's own
   numbered steps. Offer 1 plays the stick's explainer (`stick_science_video.py`); offers 2-4 play
   `brand/stick-funnel/videos/up<n>-how.*` (`upsell_videos.py`): the product pages' photos of it in use, one step a
   scene, a slow push-in, a dip through white between scenes and the step's line, numbered as the page's steps (the
   brush has no photo on a face, so its loop is the brush, its how-to card walked step by step, and its case). Nothing
   is generated motion, so no label is redrawn; every frame and the line under the steps say it is an illustration.
   With "reduce motion" set on her device, the loops don't autoplay and show their controls.
4. **Reserved for you** (`_includes/sf-upsell-reserved.html`): her first name when the order has one, the store's price
   for one beside today's (with what it renews at), and three plain reasons: it costs less than one in the store (and,
   for the brush, balm and serum, that the store's 2- and 3-packs cost less each: a store-wide "only here" would not
   be true of a 3-pack, funnel review 3), it goes on the order and payment she just made, and the 30-day guarantee. Then
   the button again (not pulsing: one pulsing button per screen), with the terms; the stick's and balm's terms end
   with the salmon-derived PDRN warning, so it sits by every button.
5. **Why / what's in it**: the brush's three reasons; the balm's and serum's first three ingredients, word for word from
   their product pages (`balm_copy.INGREDIENTS`, `serum_copy.INGREDIENTS`).
6. **Closing card**: the price, the button and "No thanks".

Store prices quoted (one at a time): stick $37.00 with refills; brush $24.95 with its case; balm $19.95 with refills
($24.95 one-time); serum $27.95 with refills ($34.95 one-time). The funnel never names SPF (the serum page's "SPF in the
morning" is left out; `check_funnel.py` fails on it).

Realistic motion clips (a woman using each product) can replace the loops once a video supplier has credit: 4SToken
and Kie.ai were out of balance on 27 Oct 2026, and Higgsfield needs the owner's go-ahead per spend. Use the start
frames in `upsell_videos.py`'s scene list, keep labels readable, and run `video_brand_gate.py`'s pink check on them.

## Versus the Facelove listicle

The listicle follows https://facelove-cosmetics.com/pages/10-reasons-why-foundating-stick-2026-new reason for reason
(same structure, same kinds of images, same CTA box and closing), with these deliberate differences:

- **Product and images**: the black SKINOFAB stick with its real wordmark, women 45+ on white, made with gpt-image-2
  (prompts in `tools/persona/image_prompts.json`, "stick-funnel").
- **Before/after**: every before/after image carries "AI illustration, not a customer photo", and shows only what a
  foundation does: the dry-skin "after" is its own "before" with the skin tone evened out (`funnel_images.even_tone`),
  every line kept. Generated "afters" that smoothed lines or lifted the jaw were dropped (funnel review 1).
- **Reason 5** (Facelove: SPF): "Made not to turn orange by the afternoon", with a verified review of the liquid.
- **Reason 9** (Facelove: "dermatologist recommended"): the liquid foundation's real ratings, 9,855 reviews averaging
  4.8, drawn on the page with the count per star, labelled as the liquid's (no expert, no borrowed endorsement).
- **Claims** follow the stick's spec rules (SKF-ADFS-001 section 8, see `docs/foundation-stick.md`): fair to medium
  skin, not "every skin tone"; "made not to settle", not "won't settle"; no SPF, no percentages, no "reverses aging",
  no doctor or expert endorsements, no scarcity counts. `check_funnel.py` fails the build on any of them.
- **Reviews**: the liquid foundation's published reviews from the earlier store, each card labelled "Verified buyer of our
  liquid foundation, from our earlier store", and only ones about the colour match (no wear-time or wrinkle claims a
  stick review couldn't back). Facelove shows stick reviews.
- **Headline**: Facelove's "10 Reasons Why..." form, kept as the brief asked; its "Look 35" and "Age-Reversing" are not.
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
| `upsell_videos.py` | the special offers' how-it-works loops (`brand/stick-funnel/videos/`, committed; rerun only to change a scene) |
| `deploy_theme.py` | turns the built pages into theme templates `templates/pages/page.<file>.html` and assets `assets/sfc/` |
| `store_pages.py` | creates or updates the 8 store pages that render those templates (Admin API, `$NEXT_API_TOKEN`) |
| `check_funnel.py` | offline checks (below); the store build fails on any problem |
| `funnel_check.mjs` | Playwright run of every page at 390 and 1440: screenshots, console errors, overflow, live prices |
| `live_order.mjs` | one real test order on the live host: checkout with NEXT's test card, each offer accepted or declined, the receipt's lines and renewals |
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
The store caches each page's HTML for 30 minutes by path (`cache-control: max-age=1800`; a query string doesn't
bypass it), so a pushed page can show its old version on the live host for up to half an hour;
`https://skinofab.29next.store/<page>/?preview_theme=34` shows the new one at once.

### Checks

- `python3 -I tools/funnel/check_funnel.py` (offline, every build): every page built with its SDK meta tags and
  linking only inside the funnel; one checkout card per package, one preselected, each stating "Then $X every N days"
  as the campaign has it; no coupon box and no post-purchase code on the checkout; the exit pop applies STICK10; each
  offer page adds its own package with its own voucher (upsell-scoped, never the live cart), states its renewal and
  falls back to its landed price; the product page's packs match the campaign; theme templates generated, with every
  asset on disk; and the claims rules above.
- `node tools/funnel/funnel_check.mjs <base-url> <out-dir> [--served]`: `http://127.0.0.1:<port>` for the local
  build, `https://try.skinofab.com --served` for the live pages.
- `node tools/funnel/live_order.mjs https://try.skinofab.com <out-dir> [--path accept,decline,accept,decline]`: one
  real test order through the live funnel (it lands in the store as a test order: cancel it). Campaigns OS's `qa run`
  can't do this on the store's host yet: it always adds the Page Kit slug to the URL, though the store serves the pages
  at the site root (logged as workflow finding wf_1793106901837_7d97c164).

### Campaigns OS

The funnel went through the Campaigns OS 1.60.0 lifecycle (brief, build, theme, Page Kit parity, polish capture,
deploy, QA resolve, QA run with 5 test orders on the local build; after each review round again, without orders):
verdict **ready_with_exceptions** (143 pass; the exception is offer coverage in a run without orders), commercial
parity pass. Run it from
`campaigns/skinofab` with:

    export LANG=C.UTF-8 CAMPAIGNS_OS_TELEMETRY=off NODE_USE_ENV_PROXY=1
    npx --no-install campaigns-os doctor --packet campaign-runtime.build.json
    npx --no-install campaigns-os qa run --packet campaign-runtime.build.json --base-url http://127.0.0.1:<port> --browser --test-order common

`LANG=C.UTF-8` because the container's default locale (`en_US@posix`) breaks the SDK's number formatting;
`NODE_USE_ENV_PROXY=1` so Node's fetch uses the session proxy; telemetry off keeps verdicts local. A `qa run` places
real test orders (up to 6) that need cancelling afterwards. QA runs on localhost; the live store needs step 1 first.
Remaining doctor advisories: wrapper tags inside the two design-source captures (references, not pages), and the
brief's payment code "card" (the campaign calls it "bankcard").
