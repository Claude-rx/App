# Flash trial funnel (Adaptive Peptide Foundation)

The owner, 4 Nov 2026: a new campaign for the Adaptive Peptide Foundation that starts on a copy of the store's product
page, then a custom checkout, the upsells and downsells, and a thank-you page. The offer is a subscription at $39.97 a
month with 50% off the first month ($19.97), shown as a flash trial ("Trial offer, limited time, today only") whose
clock ends at her midnight.

**Live:** https://try.skinofab.com/adaptive-foundation-trial/

| Step | Page | What it sells |
|---|---|---|
| Product page | `/adaptive-foundation-trial/` | The store's foundation page, copied, with the flash trial box |
| Checkout | `/trial-checkout/` | 1 bottle: $19.97 today with FLASH50, then $39.97 every month; or 3 bottles $66.97 every 3 months, or 5 bottles $99.97 every 5 months |
| Offer 1 | `/trial-offer-1/` | 2 more bottles $39, or 6 + the Lymphatic Brush $99 (one-time) |
| Offer 2 / 2b | `/trial-offer-2/`, `/trial-offer-2b/` | One more bottle $19 / last chance $15 (one-time) |
| Offer 3 / 3b | `/trial-brush-offer/`, `/trial-brush-offer-b/` | The Lymphatic Brush $14 / last chance $9 (one-time) |
| Thank you | `/trial-thank-you/` | The order, what renews ($39.97 every month) and what does not |

Routing is the APF funnel's: offer 1 accepted goes to the brush offer; declined goes to offer 2, then its downsell.

## Commerce: campaign 2251

"SKINOFAB Adaptive Peptide Foundation Flash Trial", created on 4 Nov 2026 with the next-campaigns-create skill. The run
directory `next-campaigns-create-runs/skinofab-apf-trial/` is git-ignored because its manifest holds the campaign key.

| Ref | Package | Price |
|---|---|---|
| 1 | Adaptive Peptide Foundation, 1 bottle (SKF-APF-1) | $39.97, refills every month at $39.97 |
| 2 | 1 bottle add-on (SKF-APF-1-ADD) | $33.97 one-time |
| 3 | 2 bottles (SKF-APF-2) | $39 one-time |
| 4 | 6 bottles + free Lymphatic Brush (SKF-APF-6-BRUSH) | $99 one-time |
| 5 | Lymphatic Brush + travel case (SKF-LYB-1T) | $24.95 one-time |
| 6 | 3 bottles + free Blender (SKF-APF-3-BLENDER): buy 2, get 1 free | $66.97, refills every 3 months at $66.97 |
| 7 | 5 bottles + free Lymphatic Brush (SKF-APF-5-BRUSH): buy 3, get 2 free | $99.97, refills every 5 months at $99.97 |

The owner added packages 6 and 7 on 4 Nov 2026 ("put the offer also of buy 2 get 1 free and buy 3 get 2 free"). They
went in through the create skill's update path (two POSTs, approved), at the APF funnel's prices; the Cart API prices
them at $66.97 and $99.97. Their crossed-out prices are the bottles at $39.97 each ($119.91, $199.85). The gifts come
with the first order; refills are the bottles only.

Each offer is a code, and each code's price is checked through the Cart API:

| Code | Discount | Price |
|---|---|---|
| FLASH50 | 50% off package 1, .97 rounding | $19.97 (first order only; codes never reach refills) |
| APFT40 | 44% off package 2 | $19 |
| APFT50 | 55% off package 2 | $15 |
| BRUSHT40 | 40% off package 5 | $14 |
| BRUSHT60 | 60% off package 5 | $9 |

The campaign also has:
- free shipping;
- card, PayPal and Apple Pay, with PayPal and Apple Pay as express buttons;
- no Link and no Klarna.

The SDK works on try.skinofab.com. It was proven live on 4 Nov: the checkout prices $19.97 with FLASH50.

## The flash trial clock

The deadline is midnight, her local time, of the day she first saw the offer. It is stored in localStorage under
`sf_trial_end` on try.skinofab.com, and the product page and the checkout share it.

- **Before midnight:** the product page shows "⚡ Flash trial offer · Limited time, today only", the countdown, and
  $19.97 with $39.97 crossed out. The button goes to `/trial-checkout/?forceBundleId=trial`. The checkout card "trial"
  carries `data-next-bundle-vouchers="FLASH50"`.
- **After midnight:** both pages show $39.97/mo and the trial words are gone. The button goes to
  `?forceBundleId=trial-regular`. On the checkout, an inline script switches the URL to the regular card, which has no
  code, before the SDK reads the URL. The regular card is package 1 at $39.97.
- **If midnight passes while she is on the checkout:** `js/sf-trial.js` clicks the regular card, and the SDK removes
  FLASH50 with it.

This was proven on a local build on 4 Nov. Before midnight: $19.97, with "Flash trial: 50% off your first month
−$20.00" in the summary. After midnight: $39.97, with no code.

## The product page box

The owner's reference was image 2, and on 4 Nov the owner removed the "+" lines from the plan card and asked for the
packs. The box now has, in order:
1. The title and clock: "⚡ Flash trial offer · Limited time, today only" and "Ends at midnight: HH:MM:SS".
2. Three selectable plan cards, styled as in image 2 (radio, name, price with the crossed-out price, one pill):
   - **1 bottle**, pill "⚡ Flash trial · 50% off": **$19.97** ~~$39.97~~. It is selected by default.
   - **3 bottles + free Blender sponge**, pill "Buy 2, get 1 FREE": **$66.97** ~~$119.91~~.
   - **5 bottles + free Lymphatic Brush**, pill "Buy 3, get 2 FREE": **$99.97** ~~$199.85~~.
3. The button (the line under the cards went on 4 Nov: "Renews at" already says it), which follows the chosen plan:
   - START MY TRIAL → goes to `?forceBundleId=trial` (or `trial-regular` after midnight);
   - GET MY 3 BOTTLES → goes to `trial-3`;
   - GET MY 5 BOTTLES → goes to `trial-5`.
4. "Love it or your money back", then Refill reminder · Cancel any time · Renews at $39.97/mo, $66.97 / 3 mo or
   $99.97 / 5 mo, following the chosen plan.

After midnight, only the 1-bottle card changes (to $39.97/mo, with no pill); the packs keep their prices. The checkout
shows the same three plans under "Step 1: Choose your plan", with the card the button named already selected. The
clock turns only the trial card into the regular one, so a pack she chose stays chosen.

Proven live on 4 Nov 2026 at 390 and 1440 px:
- each plan's button and "Renews at" amount follow the plan she picks;
- the 5-bottle plan lands on the checkout at $99.97 ("Refills: Every 5 months", the brush on a first-order line);
- picking 3 bottles at the checkout gives $66.97 every 3 months, and the trial gives $19.97, then $39.97/mo;
- AppLovin answered 200 to page_view, view_item, add_to_cart and begin_checkout.

## How it is built

- `tools/funnel/funnels/trial.py` is the funnel module (FUNNEL=trial): the pages, routes, packages, codes and titles.
- `tools/funnel/trial/pdp_copy.py` writes `templates/pages/page.adaptive-foundation-trial.html` from the theme's product
  template. It runs on every build, so the copy follows every change to the store page. Here is what it does:
  - It runs each product-reading block inside `{% with product=settings.sf_p_color_changing_foundation %}`, so the
    photos, the review wall (9,855 ratings, 8 cards) and the app hooks keep working.
  - It replaces the buy box with the trial box (it keeps `id="apf-buy"`, so every "Start my flash trial" link and the
    sticky bar find it).
  - It sets the price under the title, the sticky bar and the two price FAQs to the trial's prices.
  - It hides the store's sale bar, menus, cart and footer menus (the theme's `sf-from-offer` look).
  - It switches off links into the store, except the checkout and the policy pages.
  - It sends AppLovin page_view and view_item on load, and add_to_cart on the trial buttons.
  - It fails on any store price or buy-box residue left in the copy.
- `campaigns/skinofab/src/trial-funnel/` holds the Campaign Page Kit pages: checkout, five offers and thank-you.
  - Campaign 2251's public key is in `assets/config.js`.
  - The `trial-funnel` entry in `_data/campaigns.json` carries the same AppLovin event key as the APF funnel.
- `tools/funnel/trial/sync_from_apf.py` copies the APF funnel's layouts, includes, styles, scripts and pictures over
  the trial's on every build. Two things stay the trial's own:
  - its pages, `config.js` and the clock files;
  - one line in `sf-checkout.js` (no exit pop: the trial checkout has none).
- `FUNNEL=trial tools/funnel/apf/offer_pages.py` writes the five offer pages from the APF code, with the trial's refs
  and codes. The one-bottle offers compare with prices the trial's buyer has seen: $39.97 a month, and $47 bought once
  in the store. The struck $33.97 is labelled "Bottle price", not "Sales page price".
- `tools/funnel/trial/check_trial.py [--live]` is the gate. It checks:
  - the CampaignSpec (`campaign-spec.trial.json`);
  - the product page box and its tracking;
  - the two checkout cards and their codes, with no exit pop, coupon box, Link or Klarna;
  - every offer's routes, packages, codes and prices, with no APF residue;
  - the thank-you renewal;
  - that the trial uses its own key.

  `--live` also prices everything through the Cart API.
- `tools/build_store.sh` and `.work/build-funnel.sh` run all of it.
- `tools/funnel/push_theme.py` now sends a store image or font only when no committed theme file already references it.
  Before, the new page would have re-sent 267 live store files, and that breaks cached store pages for 30 minutes.

## AppLovin (Axon): proven live on 4 Nov 2026

AppLovin answered **200 to every event**, at 390, 768, 1024 and 1440 px:

| Page | Events (AppLovin's answer) |
|---|---|
| Product page | page_view 200, view_item 200 ($19.97), add_to_cart 200 (on START MY TRIAL) |
| Checkout | page_view 200, view_item 200, begin_checkout 200 ($19.97) |
| Offer 1 | page_view 200, purchase 200 ($19.97, transaction 101882) |
| Brush offer | page_view 200, view_item 200, purchase 200 ($39, `…-US1`: offer 1 accepted) |
| Brush last chance, thank-you | page_view 200, view_item 200 |

**Test order 101882** (4 Nov 2026, the owner's go-ahead, NEXT's test card, no charge) proved the purchase. The run went
through the product page, START MY TRIAL and the checkout at $19.97, accepted offer 1 (2 bottles, $39), declined
the brush offers, and reached the thank-you page:
- Total $58.97. The trial bottle reads "Then $39.97 every month", and the 2 bottles read "One-time purchase".
- AppLovin received 31 posts and answered **200 to every one**.
- Every check in `tracking.json` passed: init and page_view on every page, view_item, add_to_cart, begin_checkout,
  purchase, upsell purchase, value/currency/id on each purchase, and every post accepted.

The run:

    FUNNEL=trial node tools/funnel/live_order.mjs https://try.skinofab.com <out> --entry '?debugger=true&nfdebug=true' --track --path accept --cookie preview_theme=34

Funnel test orders are reported to AppLovin as purchases (the adapter has no test-order filter).

The store's AppLovin app loads the pixel with the same event key, but sends page_view and view_item only on its own
templates (product, home), not on a store page. So the trial page sends them itself. The public page cache (30
minutes) served the version without page_view for its first half hour.


**Item fields (4 Nov 2026, the owner's Pixel Helper screenshot).** AppLovin's Pixel Helper flagged 3 issues on each
item of View Item and Add to Cart. Axon requires seven fields on every item: item_id, item_name, price, quantity,
item_variant_id, image_url (.png, .jpg or .jpeg) and an integer item_category_id (a Google product category).
- **The cause.** The trial page sent no variant, image or category. The SDK sends the campaign's `.webp` thumbnail as
  the image and the campaign's name as the category, which the adapter dropped.
- **The fix on the trial page.** Its own events now send all seven fields: the SKU as item_id, variants 15, 334 and
  335, the product's store photo, and category 2765.
- **The fix in the adapter.** `js/axon.adapter.js` (shared by all three funnels: a LOCAL PATCH, keep it when
  re-syncing) fills the category and a .jpg photo by SKU:
  - 2765 Foundations & Concealers, with the foundation's or the stick's photo;
  - 543597 Manual Massage Tools for the brush, with its photo.
- **Proven live.** view_item, add_to_cart and begin_checkout on the trial and APF funnels carry all seven fields, and
  AppLovin answers 200. A purchase payload run through the adapter does too.


**Payment methods (4 Nov 2026).** Only methods that can charge a refill are offered: card, plus PayPal and Apple Pay
as the express buttons (Apple Pay shows on Apple devices). The owner briefly added Affirm, Afterpay and Link to
campaigns 2221 and 2251, then asked for "just the one supporting subscription". So both campaigns were set back to
apple_pay, bankcard and paypal through the create skill's update path (one approved PATCH each), and both checkouts
show only those.
- **Why not the others.** Pay-later methods do not renew subscriptions, and Link was already off for that reason on
  1 Nov. Afterpay is not in the Campaign Cart SDK at all.
- **Proven live.** The trial checkout (1 and 5 bottles) and the APF checkout show only the card form, PayPal and
  Apple Pay, with no errors.
- **The gates.** check_apf and check_trial fail on any Affirm, Afterpay, Klarna or Link radio or showing logo.


**Black Friday flash sale (5 Nov 2026, the owner: "add the black friday flash sales now").** The offer and the midnight
clock are unchanged; they are now named the Black Friday flash sale:
- **Top bar.** A black bar at the very top of the product page, above the store's header (the sf_lead block):
  "BLACK FRIDAY FLASH SALE · Up to 50% off · Ends in HH:MM:SS · Shop now".
- **The box.** Its title is a black banner, "⚡ BLACK FRIDAY FLASH SALE · Limited time, today only · Ends at
  midnight", and the 1-bottle pill reads "Black Friday · 50% off".
- **The checkout.** The bar reads "⚡ Black Friday Flash Sale · Limited time, today only", the trial card's badge
  reads "⚡ Black Friday", and the page title names the sale.

"Up to 50%" is the trial bottle's 50% and the 5-bottle pack's $99.97 against $199.85. Like the old trial words, the
bar and banner go at her midnight. To end the sale, put the flash trial words back in `pdp_copy.py` (BF_*) and in
`trial-checkout.html` (trial.title, badge_text).


**The sale keeps the $19.97 until Nov 30 (5 Nov 2026, the owner: "get back the price of 19.97 with black friday offer
trial and keep it").** The per-visitor clock (midnight of her first visit, in localStorage) had taken the price away
from returning visitors. It is replaced by one end date for everyone, `SALE_END` in `funnels/trial.py`: midnight at the
end of Monday, Nov 30 2026 (Cyber Monday), in each visitor's own time zone.
- **What changed.** The product page and the checkout read the same date. The old `sf_trial_end` value is ignored, and
  the clock shows the days left ("25d 17:49:33"). The wording is "Limited time · Ends Mon, Nov 30" and the checkout FAQ
  names the date. A clock that restarts every midnight would be fake urgency; this one ends when it says.
- **After the end.** The page and checkout turn to the regular $39.97/mo by themselves.
- **To extend or end the sale.** Change `SALE_END` and `SALE_END_LABEL` in `funnels/trial.py`, and the end in
  `trial-checkout.html`'s first script; check_trial fails if those two disagree.
- **Proven live.** A returning visitor whose old deadline had passed, and a new visitor, both see $19.97 on the page
  and at the checkout.

## The APF sales page sells this offer too (since 5 Nov 2026)

The owner asked for "the same offer" on https://try.skinofab.com/adaptive-foundation-offer/. That sales page and its
listicle now show this funnel's three plans with the same Black Friday clock (`SALE_END`), and every button opens
`/trial-checkout/` on the chosen card. So this funnel's checkout, offers and thank-you page take that traffic too. Moving
`SALE_END` also means changing `src/apf-funnel/_includes/sf-bf.html`; check_apf fails until it matches. Details are in
`docs/apf-funnel.md`, "Black Friday on the sales page".

## Owner items

- Cancel test order **101882** and the monthly subscription it started (Adaptive Peptide Foundation, $39.97/mo).
- The Clinicians' Choice badge on the checkout is the APF checkout's (task 157 still applies).
