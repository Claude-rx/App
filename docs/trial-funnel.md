# Flash trial funnel (Adaptive Peptide Foundation)

The owner, 4 Nov 2026: a new campaign for the Adaptive Peptide Foundation that starts on a copy of the store's product
page, then a custom checkout, the upsells and downsells, and a thank-you page. The offer is a subscription at $39.97 a
month with 50% off the first month ($19.97), shown as a flash trial ("Trial offer, limited time, today only") whose
clock ends at her midnight.

**Live:** https://try.skinofab.com/adaptive-foundation-trial/

| Step | Page | What it sells |
|---|---|---|
| Product page | `/adaptive-foundation-trial/` | The store's foundation page, copied, with the flash trial box |
| Checkout | `/trial-checkout/` | 1 bottle: $19.97 today with FLASH50, then $39.97 every month |
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

## The product page box (the owner's reference, image 2)

The box has, in order:
1. The title and clock: "⚡ Flash trial offer · Limited time, today only" and "Ends at midnight: HH:MM:SS".
2. One selected plan card: the radio, "1 bottle", **$19.97** with ~~$39.97~~, then three lines: "+ 50% off your first
   month", "+ Then $39.97/mo, cancel any time" and "+ Free shipping".
3. "1 bottle · delivered monthly".
4. The button **START MY TRIAL →**.
5. "Love it or your money back", then three icons: Refill reminder · Cancel any time · Renews at $39.97/mo.

Nothing else sits in the box. The owner removed the card subtitle at the checkout ("no need of this", 4 Nov), so the
checkout card shows only the bottle, its price and the SDK's savings line. The checkout keeps the full refill terms
by the order button.

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
| First offer page | purchase: the funnel's Route C, the same code that proved purchases on the APF funnel (101594) |

Two notes on the product page:
- The store's AppLovin app loads the pixel with the same event key, but sends page_view and view_item only on its own
  templates (product, home), not on a store page. So the trial page sends them itself.
- The public page cache (30 minutes) served the version without page_view for its first half hour.

**The purchase on this funnel is not yet proven.** It needs one test order through the funnel (NEXT's test card, no
charge). The session's permission system held that order for the owner's go-ahead:

    FUNNEL=trial node tools/funnel/live_order.mjs https://try.skinofab.com <out> --entry '?debugger=true&nfdebug=true' --track --path accept

The run writes `tracking.json`. Its `checks` include `purchase`, `upsell_purchase` and `applovin_accepted_every_post`
(every AppLovin post answered 2xx). Cancel the test order and its subscription afterwards.

## Owner items

- Approve the one test order above, so the purchase event is proven green. Then cancel that order and its
  subscription.
- The Clinicians' Choice badge on the checkout is the APF checkout's (task 157 still applies).
