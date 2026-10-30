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

**Files:** `sfa-axon-adapter-3194de.js` (patched) · `.orig.js` (live copy before the fix, for rollback) · `axon-adapter.test.mjs`

**Test:** `npm run test:axon` → 16/16 pass on the patch; the original fails the 4 user_data tests.

**Deploy (single file, theme 34):**
```bash
mkdir -p /tmp/push34/assets/sfa && cp fixes/axon-purchase-user-data/sfa-axon-adapter-3194de.js /tmp/push34/assets/sfa/
cd /tmp/push34 && ntk push -a "$SKINOFAB_ADMIN_TOKEN" -s https://skinofab.29next.store -t 34 assets/sfa/sfa-axon-adapter-3194de.js
```
Rollback: push `.orig.js` under the same name.

**Upstream:** also apply the change to `_shared/analytics/js/axon.adapter.js` so `npm run sync:shared` doesn't revert it.
`sfa-axon-adapter-9a3ab4.js` is an older, unreferenced build (no live funnel page loads it).
