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
| Subscription Terms modal | Generic "Subscribe & Save … contact customer service" | Doesn't state the $33/month terms shoppers agree to |
| Shipping | One rate, "Default", $0.00 per order | Free shipping, so the cart drawer says "Free" |
| Store contact address / tagline | Empty | Used in receipts and the page title |

## 1. Connect a payment gateway (blocking)

In the dashboard's payment settings, connect your processor (Stripe, NMI, Authorize.net, …) and add it to the
"Default" gateway group with Visa, Mastercard, Amex and Discover enabled. Then place a test order on the
preview theme with the processor's test card and refund it.

## 2. Checkout look

Dashboard → Settings → Branding:
- **Logo**: `brand/checkout/skinofab-logo-1200.png` (black wordmark on transparent, 1200 × 198).
- **Icon**: `brand/checkout/skinofab-icon-512.png` (favicon and checkout tab icon; the theme uses it instead of its own once set).
- **Primary color** and **Accent color**: `#151515`.

In the dashboard's checkout settings (the source of the page's "Checkout Color Setting" block): button and link
color `#151515`, logo position left.

## 3. Checkout policies

Dashboard → Settings → Policies. Replace the demo text. The subscription terms below match the storefront
copy, word for word (the PDP terms under the buy button and the cart drawer's plan card):

> **Subscription Terms**
>
> Adaptive Peptide Foundation is sold as a monthly refill. You pay $33 today, then $33 every month until you
> cancel. We email you before every refill. To switch base, skip a month or cancel, just email
> hey@skinofab.com. No minimum, no fees.
>
> Wear it in your own daylight for 30 days. If your base isn't right, we'll swap it for the other base. If you
> don't love it, we'll refund you, and your monthly refill cancels with one email.

For Terms & Conditions and Privacy Policy, use the store's own legal texts (the storefront has
`/terms-of-service/` and `/privacy-policy/` pages from the previous site; have them reviewed before reuse,
since they still describe the previous store's apps and cookies).

## 4. Renewal reminders

Enable NEXT's **Upcoming Renewal** subscription notification (dashboard notification settings) so the "We email
you before every refill" promise is kept automatically.

## 5. Check

1. Preview: https://skinofab.29next.store/?preview_theme=34
2. Add the foundation, open the bag, press **Secure checkout**.
3. The checkout should show the logo, black buttons, `Schedule: Every 1 Month`, Shipping $0.00, and the
   three policy links with the texts above.
