# AppLovin AXON: `purchase` missing `user_data` (fixed 29 Oct 2026)

**Symptom:** AppLovin Pixel Helper / Events Manager flags `purchase` on try.skinofab.com:
`user_data: NULL (Required)` / "User Email — Missing" (order #101614).

**Root cause:** the funnel's AXON adapter (`theme 34: assets/sfa/sfa-axon-adapter-3194de.js`, generated from
`_shared/analytics/js/axon.adapter.js`) never sent `user_data` — its header said enhanced matching was out of scope.
The Campaign Cart SDK (0.4.43) already puts the buyer on every checkout/purchase event as
`user_properties.customer_email / customer_phone / customer_id` (on `dl_purchase` taken from `order.user`).

**Fix:** map those to AXON `user_data` on `purchase`, `begin_checkout`, `add_payment_info`:
- `email`: trimmed + lowercased plaintext (AXON `pixel.js` hashes it client-side; same as Next Commerce's own AXON app)
- `phone`: E.164 digits without `+`; `user_id`: only when ≥ 6 chars
- browse events and `page_view` unchanged; kill switch `window.__axonSendUserData = false`

**Follow-up (30 Oct 2026):** Pixel Helper still showed an orange warning per item on view_item / add_to_cart /
begin_checkout. AXON requires a numeric `item_category_id` on every item; the SDK's category is the campaign name, which
was being dropped. Every item now gets `window.__axonItemCategoryId`, falling back to **2765** (Google product taxonomy:
Cosmetics > Makeup > Face Makeup > Foundations & Concealers). A numeric SDK category still wins.

**Follow-up 2 (30 Oct 2026):** still one orange warning per item. Read from the AXON Pixel Helper 1.3.6 rules
(`https://s.axon.ai/_assets/pixel-helper/structures.yaml` and the extension's image check): `image_url` must end in
`.png/.jpg/.jpeg`, and the SDK sends `.webp` package thumbnails. Every store variant now maps to its product JPG on
`cdn.29next.store` (`IMAGE_BY_VARIANT`, from the Admin API; add new variants there). Also: `item_brand` defaults to
SKINOFAB, and `user_data` (email/phone/user_id: the only keys AXON's pixel accepts) rides on every ecommerce event once
the shopper is known. Purchase: `user_data.email` required, `phone` and `user_id` recommended.

**Follow-up 3 (30 Oct 2026):** `add_payment_info` was orange: `payment_type` must be one of AXON's enum values
(`credit_card`, `redeemable`, `deferred`, `payment_on_delivery`, `wallet`, `other`) and the SDK sends labels such as
"Credit Card". All 17 SDK labels are mapped (cards → credit_card; Apple/Google Pay, PayPal, Shop Pay, Link → wallet;
Klarna/Affirm → deferred; bank redirects → other). Upsell items the SDK builds from the package (SKU, no variant) now get
`item_variant_id` and the JPG from `VARIANT_BY_SKU`. `fixtures/` holds AXON's own Pixel Helper rules; the test replays
the whole funnel (view_item → add_to_cart → begin_checkout → add_payment_info → purchase → upsell purchase) through them
and expects no errors and no warnings.

**Follow-up 4 (2 Nov 2026):** a live replay showed the APF funnel orange again: `image_url missing` on a bundle added
to campaign 2221 on 1 Nov (variant 335, SKF-APF-5-BRUSH) that the variant map did not have. The maps are refreshed
(334, 335) and the lookup no longer depends on them being complete: variant → SKU family (SKF-APF-*, SKF-AFS-*, …) →
`window.__axonItemImage` → store default, and an unmapped SKU stands in for `item_variant_id`. A new bundle can no
longer turn the event orange. `tools/funnel/axon_live_replay.cjs` is the browser replay used to check this.

**Follow-up 5 (2 Nov 2026):** first live order through the fixed funnel (#101763, $33.97) showed purchase orange on
`user_data`: email and phone were sent, but `user_id` (recommended) was missing because the store's customer ids are 3
digits and AXON wants 6+. `user_id` is now `'sf-' + cyrb53(normalised email)` (14 hex), identical on every event and
visit for the same shopper; a 6+ char customer id is used only when there is no email.

**Follow-up 6 (4 Nov 2026): the flash trial funnel** (campaign 2251, `src/trial-funnel`, theme `assets/sft/`), built
in another session from sources without these fixes, shipped the original adapter (orange on every event). It now
carries the same adapter, and its product page (a store page, `tools/funnel/trial/pdp_copy.py`) sends a complete item
(SKF-APF-1, variant 15, category 2765, store JPG) instead of `item_id: "1"`. `check_trial.py` fails a build that loses
any of it; the live guard covers its 8 pages.

**Follow-up 7 (4 Nov 2026): two sessions, one funnel.** The other funnel session (`claude/brave-bohr-31qzeq`) wrote its
own item fix (38a1878: variant, .jpg image, Google category by SKU, the brush as 543597) and redeployed all three funnels
with it, dropping user_data (purchase goes red: AXON requires it), user_id and the payment_type enum. Merged here: the
adapter keeps every fix plus that branch's brush category (`CATEGORY_BY_SKU_FAMILY`), built through its deploy_theme.py
(content-hashed names: `sf{a,c,t}-axon-adapter-523362.js`) and pushed (3 adapters + 24 pages, only the script name
changed). The trial page is that branch's (per-plan SKU, variant, category, JPG). **Until that branch merges this one,
its next deploy will undo this again.**

**Files:** `sfa-axon-adapter-3194de.js` (patched) · `.orig.js` (live copy before the fix, for rollback) · `axon-adapter.test.mjs`

**Test:** `npm run test:axon` → 19/19 pass on the patch; the original fails the 4 user_data tests.

**Deploy (single file, theme 34):**
```bash
mkdir -p /tmp/push34/assets/sfa && cp fixes/axon-purchase-user-data/sfa-axon-adapter-3194de.js /tmp/push34/assets/sfa/
cd /tmp/push34 && ntk push -a "$SKINOFAB_ADMIN_TOKEN" -s https://skinofab.29next.store -t 34 assets/sfa/sfa-axon-adapter-3194de.js
```
Rollback: push `.orig.js` under the same name.

**Upstream:** also apply the change to `_shared/analytics/js/axon.adapter.js` so `npm run sync:shared` doesn't revert it.
`sfa-axon-adapter-9a3ab4.js` is an older, unreferenced build (no live funnel page loads it).
