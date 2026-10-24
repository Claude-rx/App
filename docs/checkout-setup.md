# SKINOFAB checkout setup (NEXT dashboard)

The checkout page (`/checkout/`) is rendered by NEXT, not by the theme. NEXT rejects theme checkout templates
(`checkout/checkout.html` → "This directory is not supported"), and the Admin API has no write access to
branding, checkout or policy settings. These steps are dashboard-only. Everything in the storefront (the cart
drawer, the cart page, the hand-off to checkout) is done in the theme.

State found on 21 Oct 2026 (Admin API + a live checkout render):

| Item | Now | Why it matters |
|---|---|---|
| Payment gateway | Gateway group "Default" offers Bankcard, but **no gateway is connected** (`/api/admin/gateways/` is empty, `card_types: []`) | Card payments can't be charged until a processor is connected |
| Checkout colors | NEXT default blue `#3366fc` (links, Pay Now button, selected rows) | Off-brand next to the black storefront |
| Checkout header | Plain text "Skinofab" | No logo |
| Terms & Conditions modal | NEXT demo text: "This website is operated by demo.29next.store …" | Legally wrong for this store |
| Privacy Policy modal | Generic template text | Should be the store's own policy |
| Subscription Terms modal | Generic "Subscribe & Save … contact customer service" | Doesn't state the Automatic Refills terms (price, every 28 days) shoppers agree to |
| Shipping | One rate, "Default", $0.00 per order | Free shipping, so the cart drawer says "Free" |
| Store contact address / tagline | Empty | Used in receipts and the page title |

## 1. Connect a payment gateway (blocking)

In the dashboard's payment settings, connect your processor (Stripe, NMI, Authorize.net, …) and add it to the
"Default" gateway group with Visa, Mastercard, Amex and Discover enabled. Then place a test order on the
preview theme with the processor's test card and refund it.

## 2. Checkout look

Dashboard → Settings → Branding:
- **Logo**: `brand/checkout/skinofab-logo-1200.png` (black wordmark on transparent, 1200 × 198; made from the owner's
  vector file `brand/logo/skinofab-wordmark.svg` by `tools/persona/brand_logo.py`).
- **Icon**: `brand/checkout/skinofab-icon-512.png` (favicon and checkout tab icon, the wordmark's own S; the theme uses it instead of its own once set).
- **Primary color** and **Accent color**: `#151515`.

In the dashboard's checkout settings (the source of the page's "Checkout Color Setting" block): button and link
color `#151515`, logo position left.

## 3. Checkout policies

Dashboard → Settings → Policies. Replace the demo text. The subscription terms below match the storefront
copy, word for word (the terms the product page shows under the button while Automatic Refills is on, and the
guarantee in the cart drawer):

> **Subscription Terms**
>
> Packs bought on the product page come with Automatic Refills at the refill price. 1 bottle: you pay
> $37 today, then $37 every 28 days until you cancel. 2 bottles + free gifts: you pay $47 today, then $47 every
> 28 days until you cancel. We email you before every refill. To skip or cancel, just email hello@skinofab.com.
> No minimum, no fees.
>
> Wear it in your own daylight for 30 days. If you don't love it, we'll refund you.

The free gifts in the 2-bottle pack (Skinofab Blender, Mystery Gift) are not cart lines: the variant is named
"2 bottles + free gifts" so the order shows them. Make sure fulfilment packs both with every such order. The same
goes for the Lymphatic Brush bundles: "1 brush + free case", "2 brushes + 2 free cases", "3 brushes + 3 free cases
+ free body brush" ([lymphatic-brush.md](lymphatic-brush.md)). The brush is a one-time purchase; the subscription
terms above only apply to the foundation.

For Terms & Conditions and Privacy Policy, use the store's own legal texts (the storefront has
`/terms-of-service/` and `/privacy-policy/` pages from the previous site; have them reviewed before reuse,
since they still describe the previous store's apps and cookies).

## 4. Renewal reminders

Enable NEXT's **Upcoming Renewal** subscription notification (dashboard notification settings) so the "We email
you before every refill" promise is kept automatically.

## 5. Check

1. Preview: https://skinofab.29next.store/?preview_theme=34
2. Pick 1 bottle (Automatic Refills is on by default, its box hidden), add it, open the bag, press **Secure checkout**.
3. The checkout should show the logo, black buttons, `Schedule: Every 28 Days` at $37.00, Shipping $0.00, and
   the three policy links with the texts above.

Refills are the default on every button that adds the foundation, not only the product page (Theme settings →
Subscription Offer → Refills by default); the cart page's frequency menu still offers One Time.

Whether the refills box is shown, and whether it starts ticked, is `REFILL['show_box']` / `REFILL['default']` in
`tools/persona/ccf_copy.py` (rebuild with `tools/build_store.sh`). Shown and unticked, the page sells one-time first.

`node tools/theme-qa/offer-e2e.mjs https://skinofab.29next.store 34 /catalogue/adaptive-peptide-foundation_14/ shots/`
runs all of this (and the cart drawer's upgrade and add-ons) without placing an order.
