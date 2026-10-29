# The Adaptive Peptide Foundation funnel

A one-time-purchase funnel for the Adaptive Peptide Foundation (the liquid foundation), served by the store itself on
**try.skinofab.com** beside the stick funnel (`docs/stick-funnel.md`), in its own Campaigns App campaign, **2221
"SKINOFAB Adaptive Peptide Foundation Funnel"** (one campaign per product funnel; the stick keeps 2211):

    listicle  ->  sales page  ->  checkout  ->  offer 1 (supply)  ->  offer 2 / its downsell  ->  offer 3 (brush) / its downsell  ->  thank you

| Page | Live URL | What it does |
|---|---|---|
| Listicle (entry) | https://try.skinofab.com/10-reasons-adaptive-foundation/ | "10 Reasons Why Women Over 45 Look Fresher With This 'Shade-Adapting' Foundation": the Facelove listicle's structure, this foundation's reasons, photos and reviews |
| Sales page | https://try.skinofab.com/adaptive-foundation-offer/ | v2 (28 Oct 2026): hero promise ("Even, fresh skin in about a minute. No shade to guess.") with bullets and the wow image; the problem with emotional images; the root cause with an animated skin diagram; the root solution with the science loop; one pump instead of four products; the comparison table; feature badges; the ingredients; "Formulated in Korea" with the doctor image captioned as an illustration; the one-shade objection graphic; before/afters; proof; demo clips; green-star reviews; FAQ; the offer with the value stack, honest urgency and the pack chooser (`docs/apf-funnel/copy-deck.md`) |
| Checkout | https://try.skinofab.com/foundation-checkout/ | v2: the form first (packs with their names and prices from the first paint, details, address, payment), the guarantee line and one-time terms by the order button, four badges under it, three green-star reviews after it on a phone, the proof column beside it on a computer; express PayPal / Apple Pay, Klarna, Link; exit pop APF10 (on a phone too) |
| Offer 1 | https://try.skinofab.com/foundation-offer-1/ | "just for you, right now" with the honest 10-minute clock: supply cards, 2 bottles for $39 ("Add 1, get 1 FREE") or 6 for $99 ($16.50 a bottle) with a free Lymphatic Brush |
| Offer 2 | https://try.skinofab.com/foundation-offer-2/ | one more bottle, 40% off ($23), 10-minute clock |
| Offer 2, downsell | https://try.skinofab.com/foundation-offer-2b/ | one more bottle, 50% off ($19), the lowest price for one bottle anywhere, 5-minute clock |
| Offer 3 | https://try.skinofab.com/lymphatic-brush-offer/ | the Lymphatic Brush + case, 40% off ($14): the brush's loop plays above the fold, the short product page under it, 10-minute clock |
| Offer 3, downsell | https://try.skinofab.com/lymphatic-brush-offer-b/ | the brush, 60% off ($9), last chance, 5-minute clock |
| Thank you | https://try.skinofab.com/foundation-thank-you/ | receipt (the order and every accepted offer, each line "One-time purchase. Nothing renews.", the gifts in her box named from the order), next steps, the rest of the range at one-time prices |

Routes (`tools/funnel/funnels/apf.py`): offer 1 accepted goes to the brush offer (she just bought more bottles; offer 2
would sell her one more), declined to offer 2; offer 2 accepted goes to the brush offer, declined to its downsell, which
goes to the brush offer either way; the brush offer accepted goes to the thank-you page, declined to its downsell, which
ends on the thank-you page either way. An order that already includes a brush (the 3-bottle pack, the 6-bottle pack) is
sent past both brush offers to the thank-you page by `js/sf-offer-gate.js` (it reads the order's SKUs from a hidden
order-items list). Every page is `noindex`. Nothing in this funnel recurs.

**The campaign (28 Oct 2026).** Created with the `next-campaigns-create` skill from a hand-authored plan
(`next-campaigns-create-runs/skinofab-apf/campaign-plan.json`, gitignored with its run manifest, which holds the
campaign key): six one-time packages on the existing store variants, one free shipping method, five whole-dollar
vouchers, payment methods card, Klarna, Link, PayPal and Apple Pay (no Affirm or Afterpay: the pages never offered
them). The skill's `verify` read every object back and priced every pack and voucher through the Cart API: 13 cart
cases, all PASS ($39 / $57 / $75; $35 / $51 / $67 with APF10; $39 and $99 for offer 1; $23, $19, $14, $9 on the
offers). **Live on try.skinofab.com the same day:** the campaign's SDK answered on that host at once (campaign read
and cart calculations 200 with the new key, 249 shipping countries on the new checkout), so no Allowed Domains step
stood in the way; check the campaign's Settings > Allowed Domains in the Campaigns App anyway and add
`try.skinofab.com` as a Production domain if the list is empty, since the API cannot write it. Localhost is always
allowed, so the local build and Campaigns OS QA run regardless. The campaign has no shipping-country restriction
(every country the store ships to), which matches the pages' shipping promise. Campaign 2211 still carries the foundation's
old packages (refs 6–11) and vouchers (offers 6–10); nothing uses them now and they can be deleted in the dashboard.

**Proven live on campaign 2211 (28 Oct 2026, before the move, `tools/funnel/live_order.mjs` on try.skinofab.com, NEXT's test card):** order **101534**,
the 2-bottle pack ($57) at the checkout, offer 1's 2-bottle card accepted with a real click on its Buy now ($39 added,
$96), the brush offer and its downsell declined, the thank-you page with both lines and their one-time terms. Order
**101536**, the same checkout, offer 1's 6-bottle card accepted ($99 added, $156): the brush offer's gate read the
order's `SKF-APF-6-BRUSH` line and sent it past both brush offers to the thank-you page. Campaigns OS's QA placed the
other paths on the local build (below): declines on offer 1, offer 2, its downsell and both brush pages, the brush
offer accepted ($14) and the accept-accept path ($57 + $39 + $14 = $110).

## Before launch (owner)

0. **Check the domain on campaign 2221.** Campaigns App > campaign "SKINOFAB Adaptive Peptide Foundation Funnel" >
   Settings > Allowed Domains: the live host answered the new campaign's key straight away (28 Oct 2026), but the API
   cannot read or write that list, so confirm `try.skinofab.com` is there as a Production domain.
1. **Cancel the QA test orders** (test card, no charge, flagged as tests; real orders in the store):
   101520 to 101525 and 101527, 101528, 101530, 101531 (Campaigns OS QA, `qa-test@campaigns-os.test`), 101534 and
   101536 (the live proofs, `qa-live@skinofab.test`), all on campaign 2211; on campaign 2221: 101552, 101554, 101555,
   101557, 101558, 101561, 101563 (Campaigns OS and the local proof, both test emails), **101565** (the live proof
   on try.skinofab.com, `qa-live@skinofab.test`) and the AppLovin walks of 29 Oct: **101586, 101588, 101594**
   (101588 carries a doubled $150 line from the cart bug fixed that morning, see "AppLovin Axon"). The storefront's
   AppLovin proof is **101593** (`qa-live@example.com`, store checkout), and it started test subscription **100**:
   cancel both. The stick funnel's are listed in `docs/stick-funnel.md`.
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
5. **Tracking (before paid traffic).** AppLovin Axon is on, on every page (see "AppLovin Axon" below). `gtm_id` and
   `fb_pixel_id` on the `apf-funnel` entry of `campaigns/skinofab/_data/campaigns.json` are still empty, so no GTM or
   Meta tags load. Set them, and enable the matching providers in `src/apf-funnel/assets/config.js`.
   **Tell whoever reads the AppLovin dashboard:** Axon has no custom event names, so each accepted offer is reported
   as one more `purchase`, with its own transaction id (`<order ref>-US1`, `-US2`). Revenue is right; the purchase
   count is higher than the order count.
6. **Shipping promise.** The pages promise "ships within 1 business day, free and tracked: 2–4 business days in the US,
   6–9 to Europe, 8–12 elsewhere" (the store's shipping policy). Keep the policy and the pages in step.
7. **The mystery gift** is "a mystery gift from our range", valued at $15 on the value stack. Decide what ships (a
   deluxe sample of the balm or the serum fits) and keep its value honest.

## AppLovin Axon

One AppLovin event key (`a156ae42-…-0d43c77eda18`, the key in the store's AppLovin app) tracks the funnels and the
store. Proven live on 29 Oct 2026 with the funnel walks below and a storefront order.

**Funnels (both).** `axon_event_key` is set on the `apf-funnel` and `stick-funnel` entries of
`campaigns/skinofab/_data/campaigns.json`; GTM and Meta keys are untouched. The build then puts the Axon base code in
the head of every page (`_includes/analytics-head.html`, production builds only) and loads two scripts after it:
`js/next-forwarder-core.js` (reads the SDK's `dl_*` events) and `js/axon.adapter.js` (sends them to Axon). Both are
the starter templates' Route C files, generated upstream: edit them there, never here
(reference: NextCommerceCo/campaign-cart-starter-templates, `_shared/analytics/README.md`).
`deploy_theme.py` copies the two scripts into the theme as hashed assets (`sfa-…`, `sfc-…`), rewrites their tags,
and stops the deploy when any page, upsells and thank-you included, lacks the base code or either script, or loads
the adapter before the core.

| Page | Events sent to Axon |
|---|---|
| Listicle | page_view |
| Sales page | view_item (the featured pack, from its `next-analytics-view-item` tag), page_view, add_to_cart (the pack the checkout button names) |
| Checkout | page_view, begin_checkout, add_payment_info |
| First offer page | page_view, purchase (the order: value, currency, transaction id = order number, tax, shipping) |
| Each offer page | page_view, view_item; an accepted offer sends another purchase with transaction id `<order ref>-US<n>` |
| Thank-you | page_view |

**Add to cart never touches the cart.** The checkout buttons call `next.trackAddToCart(package, 1)` (the SDK's
tracking call) and then follow the link. A cart add there (`next.addItem`) doubles the order, because the
checkout's pack selector keeps every line it did not add itself and then adds the pack `forceBundleId` names: on
29 Oct a $75 pack reached the checkout as $150 for eight minutes after a push (test order 101588; no real order was
placed in that window). `check_apf.py` and `check_funnel.py` now fail on a cart call in the funnel scripts, on a
checkout button that is not reported, and on a sales page without its view-item tag.

**Testing.** Open the listicle with `?debugger=true` (add `&nfdebug=true` for the forwarder's console lines) in a
fresh tab, with the AppLovin Pixel Helper open. **Do not add `?ignore=true`:** it turns the SDK's analytics off for
the whole tab session, so no event reaches Axon at all. The store's page cache (30 minutes) can serve the previous
build after a push; the `preview_theme=34` cookie skips it. The walk tool records the same thing headless:

    FUNNEL=apf node tools/funnel/live_order.mjs https://try.skinofab.com <out> \
      --entry '?debugger=true&nfdebug=true' --track --path accept --cookie preview_theme=34

It writes `tracking.json` (every `axon()` call per page, AppLovin's requests, and pass/fail per event). Live proofs:
**101594** (APF: page_view, view_item 57, add_to_cart 75, begin_checkout 75, purchase 75, purchase 39 `…-US1`) and
**101596** (stick: the same events, purchase 47 and 18 `…-US1`). Funnel test orders are reported to AppLovin as
purchases: the adapter has no test-order filter.

**Store front.** The AppLovin app covers it with no theme code: it loads the pixel in the head of every store page
and runs a tracker in the platform's customer-event frame (`/pixels/customer-events/1/`, rendered by the theme's
`{% pixels %}` block). It sends page_view, view_item (product page), add_to_cart and remove_from_cart (cart drawer),
begin_checkout (store checkout) and purchase (order status page). Proven on 29 Oct: home, product page, add to cart,
checkout and test order 101593 sent every event but purchase. The purchase was held back on purpose: the app's
**Skip test orders** setting is on, so a test order sends none; a real order does. To see a storefront purchase in
the Pixel Helper with a test card, switch that setting off in the app for the test, then on again. Funnel pages do
not load the app's code, so nothing is counted twice.

## Commerce (Campaigns App campaign 2221)

Every package is bought once (no subscription; the store offers refills only when she asks). The values below are the
campaign's; `campaign_spec.py` reads them live (`FUNNEL=apf`) into `campaign-spec.apf.json` and the pages are checked
against them on every build. The refs are campaign 2221's (`funnels/apf.py` PACKAGE and VOUCHER).

| Package ref | SKU | Sells | Price | Compare (the store's $47 a bottle) |
|---:|---|---|---:|---:|
| 1 | SKF-APF-1 | Adaptive Peptide Foundation, 1 bottle | $39.00 | $47 |
| 2 | SKF-APF-2-GIFTS | 2 bottles + free Blender brush + free mystery gift | $57.00 | $94 |
| 3 | SKF-APF-3-GIFTS | 3 bottles + both gifts + free Lymphatic Brush | $75.00 | $141 |
| 4 | SKF-APF-2 | 2 bottles (offer 1: "Add 1, get 1 FREE") | $39.00 | $78 (2 × $39) |
| 5 | SKF-APF-6-BRUSH | 6 bottles + free Lymphatic Brush (offer 1: $16.50 a bottle) | $99.00 | $234 (6 × $39) |
| 6 | SKF-LYB-1T | The Lymphatic Brush + free travel case | $24.95 | — |

| Offer ref | Code | Package | Off | Lands at (rounded down to the dollar) |
|---:|---|---:|---:|---|
| 1 | APF10 | 1, 2, 3 | 10% | the checkout's exit pop: $35 / $51 / $67 |
| 2 | APF40 | 1 | 40% | $23.00 (shown as 41% off) |
| 3 | APF50 | 1 | 50% | $19.00 (51% off) |
| 4 | BRUSH40 | 6 | 40% | $14.00 (44% off) |
| 5 | BRUSH60 | 6 | 60% | $9.00 (64% off) |

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
formula answers, the before/after (a generated split portrait: the same woman of 58 with her lines, sun spots and
redness bare on the left and the foundation on, even and luminous, on the right, labelled "AI illustration, not a
customer photo"), proof (the imported reviews' numbers, the actives on the label, what we don't
claim), the promise, four steps with four demo clips of women 45+ (the first with sound), the 30-Day Daylight Promise,
the value stack ($189.95 of value for $75, and why the price is only here), what is limited (the launch brush), the
review wall with the buyers' own photos and nine reviews (two of them four stars), eleven questions, how to reach us,
and the packs again. A sticky bar on phones follows the chosen pack.

### The checkout

v2 (the owner's brief: "simplify, give directly the shipping info and the payment, with some badges and
Trustpilot-style reviews"): the form comes first (`foundation-checkout.html`, `_includes/sf-checkout-trust.html`). One
rating line above the pack cards (green boxed stars, no review site named; "4.8 out of 5 from 9,855 reviews of this
foundation, at our earlier store"), then Step 1 the three pack cards (2-pack preselected, "Most popular"; 3-pack "Best
value"; each "One-time. Free shipping" with its gifts, and each with its name and price in the markup so the cards are
never blank while the SDK loads), Step 2 her details, Step 3 her address, Step 4 payment with the live pay line
("$57.00 today, once, for 2 bottles with a free Blender brush and a free mystery gift. Nothing renews."), the express
buttons and the card form; the order summary; the one-time terms (with the fish-allergy note); the guarantee in one line
right above the order button; four badges right under it (guarantee, free shipping, one-time, secure); then, on a
phone, three buyers' reviews with their own photos and a link to the rest. On a computer the proof column (ratings by
stars, ten reviews, the guarantee card, "Before you order") sits beside the form. No review ever sits between the
address and the payment step. The exit pop offers APF10 with the bottle, says the offer once, and also fires on a phone
(a scroll back up toward the address bar); the coupon badge on a card reads "EXTRA 10% OFF". `check_apf.py` fails the
build on a card that does not say it is bought once, does not name its gifts or has no name and price in the markup, a
coupon box, a post-purchase code, a missing guarantee line, reviews between the address and the payment, the featured
reviews not after the button, fewer than 8 review cards or one without a photo, or a rating other than the
foundation's.

### The offer pages

`tools/funnel/apf/offer_pages.py` writes the five pages from `funnels/apf.py` and the CampaignSpec. v2 (the owner's
brief: "an exclusive offer just for her, now, with a timer and more urgency; simpler; only the brush needs a short
product page with an autoplaying clip above the fold"):

**The hero and the clock** (`_includes/sf-upsell-hero.html`, `js/sf-offer-timer.js`, `css/sf-offers.css`): every offer
page opens with its H1 ("Just for you, right now: more bottles at half price or less"; "One more bottle, 41% off, just
for you"; "Add the Lymphatic Brush, 44% off, just for you"; the downsells "Last chance: …"), one line on the offer,
"Reserved for you, <her first name>" and a countdown: 10 minutes on an offer, 5 on a last chance. The clock is honest:
its deadline is set the first time she sees the page for that order and kept in sessionStorage, so a reload or Back
does not restart it, and at 0:00 the page declines the offer itself (the SDK's own skip action, which goes where a
decline goes with her order reference; if the SDK is not there, the page goes to the decline URL itself) and the hero
says so under the clock: "When the clock reaches 0:00 this page moves on and the offer is gone: it is not in our store
and we won't email it." If she is mid-accept when it runs out, the page waits for the SDK rather than pull the offer
away. `check_apf.py` allows a countdown only with that consequence wired (`data-sf-timer-expires="skip"`, the script,
the sentence), only on offer pages, and still refuses the kit's timers. The percentage in a hero is the SDK's own
({discount}: 41%, not the voucher's 40%), so a page never shows two numbers for one discount.

1. **Offer 1, the supply cards** (`_includes/sf-supply-cards.html`, `js/sf-supply.js`): two cards in the Obvi "month
   supply" style, the 2-bottle card first and preselected ("Most popular, SAVE 50%", "Add 1, get 1 FREE": $39 for two,
   one bottle being $39), the 6-pack beside it ("Best value, SAVE 58%", "$16.50 a bottle" + the free brush), each with
   its badge, the pack image, the per-day and per-bottle price, the green stars ("4.8 · 9,855 reviews, earlier store"),
   the crossed-out and the live price, BUY NOW, and "Charged once". The cards are the SDK's bundle selector inside the
   one offer, scoped with `data-next-upsell-context` (it never touches a live cart); the card is the SDK's own click
   target and carries no button role (its BUY NOW is the one button). Every BUY NOW is the offer's own add action (the
   SDK adds the selected card); a real click on a card that is not selected is stopped, the card is selected and the
   button clicked again for her (`js/sf-supply.js`), so the order gets the card she pressed, while the closing card's
   proxied click adds the selection, and the closing card's picture follows the selected card. Under the cards: the
   guarantee row, the decline link, why women stock up (three reasons), the closing card priced from the selected
   card. No "lowest price we will ever offer" (the downsells go lower), no "six for the price of three" (no shown
   price backs it).
2. **Offer 2 and its downsell**: Apollo's single offer with the voucher on a hidden upsell-scoped selector (as the stick
   funnel's), three photos, the bullets, today's price against $39, the button and the terms ("$23.00 today, charged
   once… Nothing renews"), three reasons ("Less than any bottle in our store": $47 there, bought once; $39 on the page
   she came from; $23 here), the closing card. The downsell says it is the lowest price for one bottle anywhere (it
   is). No how-it-works loop and no "reserved for you" block any more: she knows the product, and the hero carries her
   name and the clock.
3. **Offer 3, the brush, and its downsell**: the offer with the brush's loop (its four sweeps and the case, 720 × 900)
   playing muted in the media column above the fold, the bullets, the price and the button; then the brush's short
   product page (`_includes/sf-brush-pdp.html`, from `tools/persona/brush_copy.py`'s claims: the look of morning
   puffiness, a light dry massage, no draining or lifting): the problem with an illustration of the look it is for
   (captioned as an illustration, not a customer photo), the solution, how to use it (the four sweeps, said once),
   versus stones and rollers, what's in the box (the "fluid channels" diagram is gone), the questions; the closing
   card. The downsell is the last chance at 60% off. Both skip an order that already has a brush.

Every offer page carries the gate (`js/sf-offer-gate.js`, hidden from screen readers): an order the platform marks as
unable to take a one-click offer goes straight to the thank-you page; her first name follows "Reserved for you". The
payment logos row never shows Affirm or Afterpay (the campaign offers neither); the decline links and the footer's
policy links are 44 px targets.

## Versus the Facelove listicle and the stick's

The listicle follows the Facelove structure reason for reason, as the stick funnel's does, for this product:

- **Product and images**: the liquid foundation's own approved photos from the store (women past 45 with the real
  bottle, the white dots, the infographics), the product sheet's renders for the packs, the buyers' own review photos,
  four vetted demo clips of women 45+. No new AI generation (no image model had credit on 27 Oct 2026).
- **Before/after** (the owner's brief of 28 Oct 2026: a before with wrinkles, dark spots and uneven tone, an after
  with glowing, even skin, always a woman of 45+): generated split portraits, one woman twice in one frame so both
  halves are the same person (`brand/adaptive-peptide-foundation/gen/README.md`: Gemini 3.1 Flash Image through
  Figma, the only route with credit that evening), cut and labelled by `images.py` (`split_pair`). Two exist: the
  sales page's close-up (58) and the listicle's first reason (64, the silver bob). The listicle's lines, dry-skin and
  ages reasons show a persona photo on its own (`reason-lines/dry/ages.jpg`) and the shade panel keeps its
  evened-tone afters until their six pairs are made: every image wallet was empty afterwards (Kie.ai, Higgsfield,
  4SToken; Figma's AI credits reset on 1 Nov 2026). The README lists the six prompts to run.
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
| `apf/commerce.py` | the campaign's commerce, idempotent (the `next-campaigns-create` plan created it; this finds it in place): the store variants, packages 1–6, offers 1–5; `--verify` checks the Cart API against `funnels/apf.py` |
| `apf/images.py` | the images and clips: the store's photos, pack cards, the labelled before/afters cut from the generated split portraits, review crops, demo clips, the thank-you page's range cards |
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

then push the changed theme files with ntk (`ntk push -a "$NEXT_API_TOKEN" <files>` from `skinofab-theme/`; the
kit has no remove command, so a hashed asset that a rebuild retired stays on the store theme unreferenced) and, for
new pages, `FUNNEL=apf python3 -I tools/funnel/store_pages.py`.
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
  brush skip rule on the brush offers only); the thank-you page's terms per SKU and its gift line; the host redirect
  and policy links; the theme templates and assets; the claims rules (now also the unhedged "nothing sitting in your
  lines" and the "lowest ever / lowest anywhere" superlatives the downsells contradict), nothing recurring, no
  countdown but the offers' honest one, AI labels, the reviews' origin, SPF only ever as absent.
- `FUNNEL=apf node tools/funnel/funnel_check.mjs <base-url> <out-dir> [--served]`: every page at 390 and 1440,
  screenshots (long pages in parts), console errors, overflow, live prices; `ORDER_REF=<ref_id>` opens the offer and
  thank-you pages with a real order.
- `FUNNEL=apf node tools/funnel/live_order.mjs https://try.skinofab.com <out-dir> [--path accept,decline,…] [--tier
  supply-b3g3] [--cookie preview_theme=<theme id>]`: one real test order through the live funnel, following the routes
  from each page's own meta tags. The store caches every page for 30 minutes (`cache-control: max-age=1800`,
  `app-cache: HIT`), so for half an hour after a theme push the live pages are still the old ones; `--cookie
  preview_theme=34` (the theme's id, the same value `?preview_theme=34` takes in a browser) sets the store's preview
  cookie on the first page, and every page after it is served from the theme as pushed.

### Campaigns OS

**Run 5, after live review 7 (29 Oct 2026):** build, theme and Page Kit parity recorded on the development render, polish capture READY with no hidden eager media, polish recorded (`completed_with_warnings`: the three owner decisions listed under review 7), deploy recorded on the served build, then `qa run --browser --test-order off` (no test orders: none approved since run 4): verdict `MVTESAIYGUQ0GE9LS74IKN3JE6`, **ready_with_exceptions**, 154 pass, 7 skipped, 6 warn, 1 manual_review. Five of the warnings were `policy.presence` (the pages linked the policies with `?from=offer`, the spec without it), so the marker now lives in the configured URLs themselves (`campaigns.json` for both funnels and `STORE_FIELDS` in `tools/funnel/campaign_spec.py`) and the templates link `campaign.store_*` as configured; `check_funnel.py` and `check_apf.py` fail a policy link without the marker (their old pattern only matched a link ending in `/`, so a query hid the link from the check). The rendered pages are byte-identical, so Campaigns OS holds the build as owed after the spec change (`output_unchanged_after_input_change`, also after a fresh `start --force`): recording it needs `record build --deviation-reason`, which takes the owner's own reason.

**Run 4, after the AppLovin wiring (29 Oct 2026):** Campaigns OS proves a local build in its development render, and
since the Axon base code is production-only the two renders now differ, so the lifecycle runs on
`CPK_ENV=development npx --no-install campaign-build` and the theme deploy on the production build (`npm run build`;
`deploy_theme.py` refuses a page without the base code, so a development render cannot reach the store). Build
recorded, polish capture READY (the production render's capture fails here only because this sandbox cannot reach
AppLovin's `re.applovin.com`), polish recorded, Page Kit parity passed with the Axon lines as the only
environment-gated difference, deploy recorded on the served build, then `qa run --browser` without test orders:
verdict `MVT375YGKUMEV7UA4LCKL68DO5`, **ready_with_exceptions**, 159 pass, 7 skipped, 1 manual_review, 1 warn. The
manual review is the offer-page action coverage that only test orders exercise (the three live walks above did); the
warning is the pre-existing `price-claim-mismatch:offer-1` explained under run 2.

**Run 3, on campaign 2221 and the v2 pages (28 Oct 2026):** the lifecycle started again from the new CampaignSpec
(`start --force`, setup, doctor, build and theme recorded, Page Kit parity, polish capture READY with no hidden eager
media, deploy on the served build, QA resolve with every gate passing), then `qa run --browser --test-order common
--max-test-orders 6`: verdict `MVSAFX9DEITLQA20U1HQNCARHJ`, **ready_with_exceptions**, 198 pass, 4 skipped, 1
manual_review, 1 warn, **6 test orders on campaign 2221** (101554, 101555, 101557, 101558, 101561, 101563, all
`qa-test@campaigns-os.test`), every terminal path under the cap, so every offer page's accept and decline were
clicked and every receipt rendered. The two exceptions, reported and not waived: `qc.tracking.order` on the
accept-decline-decline path reads "tracking.order unexercised (extractor_failed)": the harness's own attribution
extractor did not run on that one order, while every UTM and affiliate field it did read on the request and on the
read-back was equal on that path and on the other five; and `price-claim-mismatch:offer-1` is the pre-existing
sum-of-both-cards reading explained under run 2. Before that run, `tools/funnel/live_order.mjs` placed order **101552** on campaign
2221 through the local build (checkout, offer 1's 2-bottle card accepted, both brush offers declined, the receipt
with both lines and the gifts named): the first proof of the new campaign end to end.

**Independent live review 1 (28 Oct 2026, evening, the nine pages on try.skinofab.com at 390/768/1024/1440, 322
captures):** verdict "fix first", 2 blockers, 8 major, 14 minor. Fixed the same evening: offer 2b's feature card
printed a raw `{discount}` token (titles now go through the same substitution as texts, and `check_apf.py` fails on
any raw token); the checkout showed an empty red pill, "Instant savings:" with nothing after it and an empty summary
frame for ~4 s and flashed "$0.00 today" on the pay line (the pill waits for the SDK's `next-discounts-has-items`,
the savings line hides while its amount is empty, the summary waits behind "Loading your pack and total…" until the
SDK fills it, the pay line's fallback is the pack the URL asks for and the live total is shown only while the cart
has items); at 1024 the proof column sat beside a 296 px form (stacked below the form between 992 and 1199 px; beside
it from 1200); the listicle's "CLAIM YOUR LAUNCH OFFER" landed on a page preselecting the 2-bottle pack (it now
lands on the pack chooser with the 3-bottle pack selected, `?pack=apf-3#offer`, read by `sf-apf.js`); "the price you
see is the price you pay" and "this price is gone" contradicted the exit pop and the cheaper last chance (now
"nothing is added at checkout", "no pack costs more than it says here", "this offer is gone"); the sales hero's AI
line was grey on skin (on a white band); the shade bar ran to very deep (ends at deep, as the words say); the brush
infographic said "built to target morning puffiness" (its top band redrawn: "for the look of morning puffiness"), its
before/after showed no difference (the morning-mirror photo instead) and the brush is named a facial massage brush;
4.8 is drawn as 4.8 (`sf-stars.html` lights part of the fifth star); 44 px targets; one line of bar text at 390; the
same shipping times in both FAQs; no "printed on the bottle"; "9,855 reviews", not "women"; the comparison table's
unsourced complaints dropped; the footer names the women pictured as illustrations; one savings row in the summary;
offer 1's cards built alike with the charge the biggest number; "Reserved for you, Jane · 09:47 left"; "Confirming
your order…" under the clock until the SDK has the order. The campaign's pack packages now carry the pack renders as
their images (`PUT /packages/{id}/image/`, packages 2, 3, 4, 5), so the summary and receipt show two, three or six
bottles. Not a defect after reading the SDK: the mobile exit pop fires when the page has been scrolled past half its
height (`mobileScrollTrigger` in `campaign-cart@0.4.43`), not on a fast scroll up, and it does on the live checkout
at 52% in an iPhone profile; the reviewer's scrolls stopped short of that. Still open: the six before/after pairs
that need image credit (above), and the hidden payment-logo markup for methods the campaign does not offer (the
family's partial; invisible).

**Independent live review 2 (28 Oct 2026, night, the nine pages with the preview cookie, 1,090 captures):** verdict
"fix first, then ship", no blockers, 5 major, 17 minor; technically clean (every page 200 at four widths, no console
error, no overflow, every price in the campaign's set, the exit pop and coupon, the countdowns, the receipt and the
`?pack=apf-3` landing all verified). Fixed the same night: the family's offer box rode 96 px up over the hero and hid
the line that says what the clock does on four pages (`.upsell-box{margin-top:0}`); a pack tapped in the first ~3 s,
before the SDK had bound the cards, was lost (the tap is shown at once and replayed on the card at `next:initialized`,
and a tap after that shows the card's price at once instead of 0.7 s later); the crossed-out $59 a bottle was above
the $47 the pages say the store charges (the store's $47 is now the only reference: $47 / $94 / $141 crossed out,
SAVE $8 / $37 / $66, $189.95 of value; `LIST_PRICE` in `funnels/apf.py`, held by `check_apf.py`); the hero's fifth
star painted transparent (a grey base star with the lit 80% clipped over it); the shade panel is a tone diagram (a
white drop blending into a fair, a medium and a deep swatch under the bar) instead of filtered faces. Minors: the
offer pages carry the funnel's own footer with the illustration disclosure (the offer-2 woman was unlabelled) and
offer 2's third slide is the brush photo (two silver-haired women read as a duplicate); `#offer` lands clear of the
bar (`scroll-margin-top`); "Loading the address form…" under Step 3 while the SDK builds it; the old-routine card
no longer stretches to its neighbour; the bottle's detached shadow cleaned (`bottle()`); the brush cards use the
clean product shots (the infographic and the case photo's baked text were illegible at card size); 44 px carousel
arrows and review links; the short bar text up to 900 px and shorter still; the listicle's promise about the next
page's reviews matches the nine cards; "expression-line creams" without "firming", "is made not to crack", "made
to layer without pilling", "9,855 reviews say"; the doctor caption at 14.5 px in ink; the skin diagram's labels at
17 px; the receipt's section titles are h2s; sharper demo posters (the sharpest of the first two seconds); the
science and all-day loops re-encoded as yuv420p VP9 (an RGB VP9 painted blank in some captures). Left as they are,
documented: the brush loop's baked "Illustration" pill on its hand-held frames (they are illustrations; the loop is
the stick funnel's render), the "3 ★ 0" row (the imported data), the sticky bar at 390 (measured 43 px clear of the
footer's last line; its room is now 150 px), and the cropped hairlines in two square store portraits.

**Campaigns OS after live review 2's fixes (28 Oct 2026, night):** build recorded, polish READY (18 captures, no
console error, no overflow), deploy recorded, QA resolve passing, browser QA verdict `MVSJF307HQN95L5BHOF7GPB5EJ`
ready_with_exceptions: 159 pass, the two known exceptions (no typed orders on an image-and-copy run; offer 1's
sum-of-both-cards price read) and one new warn, `browser-request-failures:checkout`: one `carts/calculate` request
ending `net::ERR_ABORTED`. That is the SDK cancelling its own superseded calculation when the card the URL names is
applied right after init (reviewer 2 saw the same aborted fetch on the previous build, where the QA run happened not
to catch it); no page request fails, and the final total is right on every path. Not waived, recorded.

**Independent live review 3 (28 Oct 2026, night, the nine pages with the preview cookie):** verdict "fix first, then
ship", no blockers, 7 major, 31 minor; technically clean again (zero console or page errors and no failed request at
four widths, every price in the campaign's set, the exit pop's $67/$51/$35, the countdowns' wording true of their
script, the `?pack=apf-3#offer` landing). Fixed the same night, in the tools and the source: the five offer pages'
footer had no styles at all (they load `sf-offers.css`, not `sf-funnel.css`: the footer rules now live there too);
the exit pop's 800 px dialog overflowed a 768 px viewport (`min(800px, 100vw - 32px)`); the skin diagram's SVG
captions were clipped at both ends and 8 px tall at 390 (the titles and captions are HTML text beside the drawing);
offer 1 said "these prices exist on this page only / half price or less" while offer 2b sells a bottle for $19 (offer
1 now promises its two packs, "from $16.50 each", and 2b names the $39 it strikes as the page-you-came-from price,
$47 in the store); the serum cross-section glowed blue down through the dermis, a penetration claim the words avoid
(the serum stays in the surface layer in the poster and the loop, the dermis below borrowed from the cream block; the
pages say "melts into the surface", "keeps dry skin comfortable", "be kind to the skin underneath"; no "treats");
the checkout's first phone screen was a three-line promo bar, the logo and three stacked badges with Step 1 below
the fold (the bar on one line, the header badges hidden below 768 px: Step 1 now starts 270 px down); the checkout
at 1024 measured as one 760 px column centred on the local build and live, so the review's 480 px column was
re-checked and not reproduced. Minors: the review wall flows in two CSS columns (no card stretched to its tallest
neighbour); the footer's copyright beside the links; email, terms and policy links are 44 px without a taller line
box; the receipt's "Order details" toggle and the checkout's payment notes and reviewer names are no longer
headings (one H1, then H2s); "after you place your order"; the redundant "See the other 7 reviews" link removed;
an early pack tap repaints every live total; "Phone (optional)" before the SDK relabels it; the phone's promo bar;
three "why" cards in one row from 900 px; four-column steps and proof only from 1024 px; the sales page's top bar
scrolls away on a phone once the sticky checkout bar is on; the listicle's bar fits "Gifts with 2+ bottles" on one
line at 390; "3 bottles + brush + 2 gifts" in the sticky bar; the next-page promise says nine reviews carry a
photo without implying those nine span 54 to 81; Michele W.'s excerpt starts with an ellipsis; the brush page's
grammar, a FAQ on why it is called the Lymphatic Brush (a massage brush, no drainage claim), the case row dropped
from the comparison (the box section says it comes with one), "What you get, and where it works" over the tiles,
its mirror caption at 14 px in ink; the 2 PM loop's disclosure once (the page's caption; the baked line removed);
the hero triptych's middle panel on her face, not the seam through her eye; the closing card of offers 2 and 2b
shows the bottle (the portrait's crown was cut); the mirror photo's cheek pigment softened (it read as a bruise at
page size; `soften_patch` in `images.py`); the shade panel's long sentence out of the image (its bullets say it)
and Darla H.'s car selfie replaced by Susan B., 70 on the sales page and the listicle. Left as they are, documented:
the brush loop and the "where it works" tile are sketches of a younger face (the stick funnel's render and a
generated diagram; no image credit to redraw them), the crowns cut in two store portraits and the duo photo (in the
sources), the listicle's reason-4 crop (the source), the 33,712 px sales page at 390 (its length is the page), the
"Lymphatic Brush" product name (the merchant's; the FAQ says what it is and is not), and the wordmark missing from
one 2 s capture at 1440 (not reproduced: present at 2 s in three loads).

**Campaigns OS after live review 3's fixes (28 Oct 2026, night):** build recorded, polish READY (18 captures, no
hidden eager media), polish completed with the evidence file, deploy recorded on the served route root, browser QA
`MVSMVUMJU56ELT8AS8F5BRT6IH` ready_with_exceptions (the same two exceptions as before: the checkout's upsell-action coverage is a
manual review, offer 1's bundle price claim reads the live package).

**Independent live review 4 (28 Oct 2026, night, the nine pages with the preview cookie, 493 captures):** verdict "fix
first (three quick layout fixes), then ship", no blockers, 3 major, 19 minor; the prices, the checkout's first
seconds, the exit pop's coupon, the `?pack=apf-3` landing, the countdown wording, the receipt's gifts, autoplay,
headings and the claims rules all verified again. Fixed the same night: the exit pop's two columns clipped its terms
at 768 (it stacks below 992 px now); the hero's fifth star wrapped to a second line at 390 (the star row never
wraps); the "EMAIL HELLO@SKINOFAB.COM" button had lost its pill padding to the 44 px email-link rule of review 3
(the rule skips buttons). Minors: the brush how-to image's "Repeat on the other side." line sat above its title
(cut off in `copies()`); the sticky bar steps aside while the pack chooser is on screen and the footer's room under
it is static (one scroll to the end fell 110 px short while the room was added); on a phone the exit offer is no
longer the SDK's 50%-depth trigger in the middle of the form: it is armed by a fast scroll back up (a flick of 220 px
or more) once she has been past the pay step, and fires on that gesture (`sf-checkout.js`); the coupon row says
"10% off your foundation today" once; the empty "Billing Address" heading waits for the SDK; the listicle's wide
loops and the serum render are 680 px at most and the guarantee seal 360 px; the solution loop is centred beside
its cards and the old-routine card fills its row with its time line at the foot; the listicle's offer box centres
its pack image on the value table; "Formulated in Korea" is a pill in the page's type instead of the laurel
sprigs; the two review-wall photos that read younger are Dotty and Patricia now; the listicle's promise says the
reviews sit beside their own photos (no count against the wall); "Two months’ supply" instead of "Most popular" on
offer 1's page-only pack, and its closing card says the 2-pack is what it adds unless changed; no payment-logo
strip on the one-tap offers; the brush loop is level with its text; "Contact Us" on the receipt is 44 px; the H1's
highlighted phrase never breaks; the offer pages' feature cards read left beside their number. Left, documented:
the AI bottles carry a "PDRN" line the packaging renders do not (no credit to regenerate either), and the receipt's
gift line for 1- and 3-bottle orders and the brush offer's skip for buyers who already get the brush remain
exercised only by the gate's code and the earlier proof orders. Lifecycle on the fix build: build recorded, polish READY
and completed, deploy recorded on the served route root, browser QA `MVSOULLREEJ3RA25BUU105L0A2` and, after the stacked
pop was widened to `min(800px, 100vw - 32px)`, `MVSP1U2XN433DFPFFH0G4EJ959`, both ready_with_exceptions (the two known
exceptions; the first run also warned once about the SDK aborting a superseded `carts/calculate`, the timing artefact
noted after review 2). Verified live with the preview cookie at 390/768/1024/1440: the pop 736 px at 768 and 358 px at
390 with nothing clipped, the star row on one line, the email pill padded, the footer's last line 83 px clear of the
bar after one scroll, the coupon row named once, zero console errors.

**No disclaimer or illustration line (28 Oct 2026, night, the owner's instruction: "remove all disclaimer and
illustration text from the images and the text"):** every such line is gone from the nine pages and the images, in
the tools and the source: the before/after pairs and the hero's split portrait carry no "AI illustration, not a
customer photo" band, the shade panel no "Illustration … Results vary" note, the brush loop and its poster no
"Illustration" pill (painted out of every frame in `copies()`); the pages carry no footer disclosure ("This page is
an advertisement … AI illustrations … Individual results vary"), no "Illustration of the skin's layers, not to
scale", "not a measurement", "The video is an illustration", "not an endorsement", "not paid endorsers" or
"Results vary" line, and no "(AI illustration)" in an alt or aria-label; the doctor figure and the brush's mirror
photo have no caption. `check_apf.py` now fails any page that carries one of those lines instead of requiring the
AI label. Kept, because they are not disclaimers: the fish-allergy warning (a safety line), the guarantee terms,
the countdown's own sentence, and the reviews' provenance ("from our earlier store"). The owner was told once that
unlabelled AI before/afters and no results-vary line carry an ad-compliance risk in the US and UK.
Lifecycle on that build: build recorded, polish READY and completed, deploy recorded on the served route root, browser QA
`MVSNOLCU080Q3069M343O69O9O` ready_with_exceptions (the same two exceptions); verified live with the preview cookie: no such
line in any page's text, alt or aria-label, the new image hashes served, zero console errors.

**Independent live review 5 and the CRO pass before ads (29 Oct 2026):** review 5 (the nine pages at
390/768/1024/1440 with the preview cookie) found no blocker, 3 major and 15 minor defects; the owner then sent three
before/after pairs and a photo of the SKINOFAB doctor in her clinic, and asked for more CRO before the ads. Done in
the tools and the source, deployed, verified live:

- **The owner's before/after pairs** (`brand/adaptive-peptide-foundation/owner/ba-{car,kitchen,garden}.webp`: fair,
  olive and medium-deep skin, each the same woman before and after) are the sales page's "One bottle, three skin
  tones" row (three across from 900 px, stacked below at 560 px at most so the Before / After words stay legible).
  `split_pair()` now cuts at the whole white divider. The generated close-up pair is retired (review 5: its "after"
  erased forehead lines, more than a foundation does); the listicle keeps its shade pair and the persona photos.
- **The doctor photo** (`owner/doctor-clinic.webp`) is the "Formulated in Korea" picture. The image model misspelt
  the small print ("PORN", "PEPTIOE"); `doctor_photo()` paints that block out with the bottle's own black and sets
  ADAPTIVE PEPTIDE / FOUNDATION / PDRN / 30 mL / 1.01 fl oz again in the label's sizes. She is not named or called a
  doctor on the page, and the proof card now says "No clinical study, no medical claim" (it said "no doctor" next to
  her photo, review 5).
- **One label everywhere** (review 5's M2): the bottles held in the photos print a PDRN line, as the store's label
  and the product-sheet render do; the funnel's bottle on white (the pack cards, the offer image) lacked it. `bottle()`
  now takes that line from `01-front.png` onto the render, at its own place and size.
- **The phone exit pop** (M1) opened on any 220 px upward scroll past 45 % depth, however slow. It now opens only on a
  fast flick (300 px within 400 ms), after she has seen the order button, once she is above it again; the page opens
  the SDK's pop itself (the SDK's own trigger fires only below half the page, and the button sits at 35-43 %). Tested:
  a slow scroll up from the reviews, a fast scroll back to the button and a flick before the button never open it; a
  flick toward the top after the button does.
- **The countdown** (M3) on offer 2 and the brush offer no longer says the offer "is gone" at 0:00 (their downsell
  sells the same item for less next): "When the clock reaches 0:00 this page moves on. This offer isn't in our store
  or in an email." Offers 2 and 2b call $39 the "Sales page price", not the "Regular price" (the store's is $47).
- **Minors:** the all-day clip says "made not to turn orange" / "can turn orange by noon" at 12 px on a phone; the
  hero's split-face seam is spread over 40 px each side (no step at the chin); the listicle hero is two whole square
  photos (no face cut) and one on a phone (360 px tall instead of a 140 px strip); the comparison table has no bare
  dash and no sweeping claim about other brands ("can", "varies", "check the label"); the checkout form is centred
  and 640 px wide at 992-1199 px; the order summary shows the chosen pack, free shipping and the total from the first
  paint instead of "Loading…"; the brush page says its four sweeps once (the infographic is gone); a link to
  `#offer` stays on the offer while the page above settles; footer, legal and email links are 44 px; "Nothing to take
  on faith: the label, the reviews, the guarantee."; the listicle's buttons say "SEE THE LAUNCH OFFER" and "SEE
  OFFER" (they open the sales page, nothing is claimed). The empty checkout heading review 5 saw did not reproduce.
- **CRO, the sales page's first screen on a phone:** the photo 5:4, the headline, the 4.8 rating with its link to the
  reviews right under it, then "CHOOSE MY PACK" and the price line, then the line about the foundation and the five
  bullets: the button is on the first screen of an iPhone SE (615 px), an iPhone 13 (664 px) and a Pixel 7. It was on
  the second screen of all three.

`check_apf.py: 9 pages ok`, `check_funnel.py` OK, `copy_deck.py` PASS (it failed since 28 Oct on the retired
before/after label). Verified live with the preview cookie: no horizontal scroll, no empty heading and no console
error on the changed pages; the summary stand-in showed the 3-bottle pack at $75 0.7 s after the page began and gave
way to the SDK's; offer 2 shows the new clock line and "Sales page price"; `#offer` held at 84 px from 1 s to 4 s.
Lifecycle on this build (development render, as run 4): build recorded, polish READY and completed, parity passed
(the Axon lines the only gated difference), deploy recorded, browser QA `MVT575T3RRMFFAENF3TIHN9Q9V` ready_with_exceptions
(the same two exceptions).

**Owner's changes, 29 Oct 2026 (before the ads):** *Buy 2, get 1 FREE* (since reworded to "3 bottles for $75, $25 a bottle": see review 7, B1). The 3-bottle pack is framed as buy 2, get 1 free, which is true as priced: it is $75 and two single bottles are $78. The sales page opens on it (its frontmatter `selected`; the buy button's and sticky bar's first href and price follow the selected pack in Liquid, so nothing jumps before `sf-apf.js` runs). It says so in the offer bar, a deal line above the hero button, the pack's gold "Buy 2, get 1 FREE" tab with a "3rd bottle FREE ($39)" row in its gifts, the offer box's lead, the value stack ("Buy 2, get the 3rd bottle FREE" and the $78-versus-$75 line) and `offer-3.jpg` (a ribbon over the three badges and a "+1 FREE" tag beside the third bottle's cap, drawn in `pack_cards()`). For message match, the checkout's 3-bottle card badge and pay line and the listicle's offer bar and offer box carry the same words. No price or offer changed in the campaign. *Support contacts.* Every customer-support contact is now **info@skinofab.com** and **+1 (563) 239-5520**: `tools/persona/company.py` (`EMAIL`, `PHONE`; its rewrite turns any `hello@` left into `info@`, and the store build fails on a `hello@`), `campaigns.json` (`store_email`, `store_phone`, `store_phone_tel`) and the CampaignSpec. The phone is on the store's footer, contact page, contact-information page, FAQ, Impressum and order-tracking help, and in both funnels' footers, checkout help lines, failsafes and the sales page's "how to reach us" (a Call us card and a call button). No calling hours are stated because none were given. Set the same two in the NEXT dashboard (`docs/company-details.md`). *The listicle's offer box* (the owner: "put the lower price possible or just send them the sales page") shows the deal in four lines and the lowest price, **from $25 a bottle** (or 1 bottle for $39). The $189.95 value table and the $75 total are gone. Every listicle button (the bar, the mid-article button, the box and the closing button) now opens the sales page itself, no longer its offer box, so the sales page makes the case before she picks a pack. *PDRN on the pack shots:* every pack image is shown 300–470 px wide, where the label's PDRN line was 3–4 px tall on a 1x screen and read "PORN". `bottle()` now draws it at twice the label's size, centred where it was (`pdrn=2.0`), in the listicle's `offer.jpg`, the sales page's `offer-3.jpg`, the pack cards and the exit pop's bottle.

**Owner's fixes, 29 Oct 2026 (after the CRO pass):** the listicle's first before/after is the owner's olive-skin
kitchen pair (`ba-glow` retired); the how-it-works loop (`howto_loop()` in `images.py`) is cropped clear of its baked
"Illustration" pill and its bottle label carries the PDRN line, as every other bottle on the funnel does; and a wide
(one-column) reason's media no longer sticks: `position: sticky` stays only where the media stands beside its text
(two columns), because in one column the stuck science and all-day loops slid over the text under them (the owner's
screenshots of reasons 5 and 6). `check_apf.py` fails a build whose wide-reason media is sticky; the live probe at
390/768/1024/1440 found no media over text on either listicle.

**Independent live review 7 (29 Oct 2026, after Buy 2, get 1 FREE):** 1 blocker, 4 major, 16 minor. Fixed in the tools
and the source, built, pushed and checked live (every page at 390/768/1024/1440, no console error, failed request,
broken image or overflow; `r7-fixes.mjs` in the session's scratchpad checks each item below):
- **Store claims** (M1, M2): the sales page's why-now line says only what is true of the store (no 3-bottle pack, no
  pack with the Lymphatic Brush, one bottle $47 bought once); the brush offer quotes "$24.95 in our store" instead of
  "Not sold in our store"; offer 1 says "These prices are only here" with the store's own prices beside them.
- **Rating badges** (M4): no Trustpilot green or "Excellent" label; the stars are the brand's black (`--sf-star`) and
  the label reads "Rated". The 2-bottle packs say "2 months' supply", not "Most popular" (minor 12).
- **Offer 1's hero** (minor 2) is its accept button ("YES, ADD 2 BOTTLES · $39", which presses the 2-bottle card's
  own buy button, `sf-supply.js`), with a link down to the 6-bottle pack; it sits inside the first screen at 375x667.
- **Checkout** (minors 3, 15): the exit pop needs a flick in the top 60 % of the screen with no field focused or
  left in the last 3 s; it is a labelled dialog (focus moves into it, Escape closes it, focus comes back); the card
  expiry selects are named; the field labels are #6b6b6b.
- **Thank-you without an order** (minor 4): the confirmation head and both summaries are hidden (`[hidden]` now wins
  over their `display:flex`), so only the "We couldn't find an order" banner shows. The cross-sell (minor 5) shows both
  store prices (with refills and bought once) and leaves the EGF serum out for a European address.
- **Policy pages from the funnel** (minor 6): every policy and contact link in both funnels carries `?from=offer`, and
  the store theme (`build_theme.py`, the base layout's head) then hides the sale bar, the menus and the cart before the
  first paint. Opened from the store, the same pages keep the store's chrome.
- **The science loop** (minor 7): the bottle prints its PDRN line, and the drop, its stream and the pool on the skin
  are the foundation's milky white in every frame and in the poster (the pool's glassy rim had stayed clear);
  "sink in" and "melts into" are gone from the copy (minor 8).
- **Before/after pairs** (minor 9): each after is brought to its before's scale and both are cropped closer on the face
  (`face=1.12`); the clothes and backgrounds of the owner's own photos still differ, which only new photos can change.
- **Also:** Susan's 230 px review photo is off the listicle (Vicki M.'s review instead) and trimmed on the sales page
  (minor 10); a tapped clip with sound pauses once scrolled off (minor 11); the 1440 sales intro and listicle top
  column are centred (minor 13); US spellings in brand copy (minor 14); the brush offer's how-to steps are page text
  under the loop, 15 px (minor 16).
- **B1, decided by the owner (29 Oct 2026, before the AppLovin ads): reworded.** The 3-bottle pack is "3 bottles for
  $75, $25 a bottle" with the free Lymphatic Brush and gifts, its tab and checkout badge "Best value"; the offer bars,
  the hero deal line, the pack's rows, the value stack ("Your price today"; "$25 a bottle: one bottle is $39 here and
  $47 bought once in our store"), the listicle's offer box and `offer-3.jpg` (ribbon "3 BOTTLES FOR $75", a "$25 a
  bottle" tag) no longer say "buy 2, get 1 free", "pay for 2" or "3rd bottle free", and `check_apf.py` fails any page
  that does. No price changed. Offer 1's "Add 1, get 1 FREE" stays: two bottles there cost $39, one bottle's price.
- **For the owner** (not changed here): *M3*, the white-coat clinic photo reads as a clinician presenting the product;
  *minor 1*, offer 2b's $19 bottle is cheaper than offer 1's $19.50 a bottle.

**Owner's changes, 29 Oct 2026 (with the AppLovin launch):** *Green stars.* Every rating on the listicle, sales page, checkout and offer 1 is a row of green boxed stars (`--sf-star` / `--brand--color--rating-star`, #00b67a, the Trustpilot look), the gold text stars are gone (`sf-stars.html` everywhere) and the rating bars are green; no review site's name or logo, the label stays "Rated" and the reviews say "from our earlier store". *The checkout's order button* comes straight after the payment options; the guarantee line, the one-time terms and the order summary follow it (`check_apf.py` fails a build that puts anything between them). *The Clinicians' Choice badge* (the store's FrontrowMD listing for the foundation, product 4694, confirmed by the owner on 22 Oct) is under the sales hero's button and under the checkout's rating: as a badge, no link (the owner's word), the laurel mark from `clinicians_badge()` in `images.py` and the line "700+ clinicians share this on FrontrowMD without compensation." (FrontrowMD counted 704). `check_apf.py` reads FrontrowMD's live count on every build and fails if it falls under the badge's number; when FrontrowMD cannot be reached it says so and goes on.

**Live proof on try.skinofab.com (28 Oct 2026, after review 2's fixes were pushed):** order **101565** on campaign
2221, placed by `live_order.mjs` with `--path decline,accept,decline --cookie preview_theme=34` (the store's page
cache was still serving the previous template; the preview cookie is the theme as pushed): the v2 checkout with the
2-bottle pack ($57), offer 1 declined, offer 2 accepted (one more bottle, $23), both brush offers declined, the
receipt with both lines, "Free" shipping, the $80 total and the gifts line, no console errors on any of the nine
steps. The campaign's SDK answered on the live host without any dashboard change.

**Independent review 2 (28 Oct 2026, the v2 pages on the local build, order 101552):** verdict "fix first, then
ship", no blockers, 4 major, 9 minor, every one fixed in the same round: the checkout's pack cards are in the page
from the first paint (no await skeleton; the preselected card marked; the campaign's own names so nothing jumps when
the SDK answers); the exit pop on a phone takes the screen's width and scrolls inside it (the SDK's fixed wrapper had
shrunk to 195 px); offer 2b and the brush downsell say "last chance" and the SDK's own percentage, never "lowest
price anywhere" (offer 1 sells bottles for less in its packs) or a second figure for the same discount; the sales
hero's tag sits at the top of the picture, off its "AI illustration" note; the receipt's "Thank you" is its H1 and
the summary label is no heading, the payment notes are h3; the sticky bar reads the buy button's position on every
scroll (it stayed on after a jump back to the top); the rating line's link and the gallery arrows are 44 px targets;
the receipt's range no longer re-offers the brush she just declined; the brush loop carries its VP9 source beside the
H.264 one (the reviewer's Chromium has no H.264); the clock's line says "this price is gone", not "the offer is not
in our store". Left as it is, documented: the offers' names in the campaign ("40% off one more bottle") carry the
voucher's percentage while the pages show the landed one (41%, the whole-dollar rounding); upstream copy should quote
the price, not a percentage. The reviewer verified: no console errors or failed requests on 36 captures, no
horizontal scroll, every price the campaign's, the compliance copy clean, the brush downsell's countdown moving the
page on at 0:00 and again at once on a reopen, offer 1's closing card following the selected card, the receipt's
gifts and "Free" shipping. Not verifiable there: the mobile exit trigger on a real touch scroll (the SDK's own), the
10-minute clocks to 0:00 (same markup as the 5-minute one it watched).

The earlier runs, on campaign 2211 and the v1 pages: the funnel went through the Campaigns OS 1.60.0 lifecycle on
28 Oct 2026 (brief, build, theme, Page Kit parity, polish capture, deploy, QA resolve, QA run with typed-card test
orders on the local build), twice. Run 1 (verdict
`MVRWKIACPRQD983L4KSP6P6R3I`, 6 orders) was **blocked**: 186 pass, 4 fail, all of them offer 1's accept action (the
supply cards' Buy now buttons were not the SDK's add action, so the harness could not accept the offer). After the fix
(each card's Buy now is `data-next-upsell-action="add"`; `js/sf-supply.js` selects the card in the capture phase
before the SDK handles the click), run 2 (verdict `MVRXCDNA3MJV4LVHEK4IOTPM5S`, 4 orders under `--max-test-orders 4`:
checkout, accept, decline, accept-accept) gave **ready_with_exceptions**: 184 pass, 4 skipped (optional Apollo
checkout selectors this checkout does not use), 2 warnings, both pre-existing, reported here and not waived:

- `browser-test-order:upsell-action-coverage`: no order of run 2 clicked the decline on offer 2, its downsell, the
  brush offer or its downsell (the 4-order cap went to the checkout, offer 1 accepted and declined, and accept-accept,
  which takes the brush offer). Run 1's six orders declined every page; its decline-decline-decline-accept order
  ended on the thank-you page at $71 (the 2-bottle pack plus the brush at $14).
- `price-claim-mismatch:offer-1:bundle.supply.price` (claimed $39.00, calculated $138.00): the harness prices a page
  as one cart holding every package on it, and offer 1 carries two alternative cards (package 9 at $39, package 10
  at $99), so its "representative total" is their sum. The page's $39 is the selected card's price, which the SDK
  renders live and the orders confirm (accept: $57 + $39 = $96; accept-accept: $96 + $14 = $110).

Commercial parity reports that one finding; the theme gate and the route probe pass. The Run Record is
`.campaign-runtime/run-records/run_1793180219231_d5a6e5d9.json` (telemetry off: nothing left the machine). Run the
lifecycle from `campaigns/skinofab` with the commands `docs/stick-funnel.md` gives, with `--base-url
http://127.0.0.1:<port>` serving `_site` (QA resolves the funnel under `/apf-funnel/`), and `--spec
./campaign-spec.apf.json --source ./design-source-apf --brief ./campaign-build-brief.apf.json` on `start`.

The project holds one Build Packet at a time (`campaign-runtime.build.json` and `.campaign-runtime/` are written per
`start`): the stick funnel's run is kept under `campaigns/skinofab/runs/stick-funnel/`; to run its lifecycle again,
`start` it from its own spec, source and brief as `docs/stick-funnel.md` describes.
