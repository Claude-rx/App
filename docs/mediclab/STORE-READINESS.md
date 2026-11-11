# Mediclab store: funnel readiness

Store `https://mediclab.29next.store` · audited 2026-11-11 06:31 UTC · `python3 -I tools/stores/nc_store.py audit mediclab`

| Level | Area | Finding |
|---|---|---|
| **BLOCKER** | store | Business contact address is empty (needed on checkout, receipts, policies and by gateways) |
| **BLOCKER** | payments | No payment gateway configured (Dashboard > Settings > Payments). Checkout cannot take money |
| **BLOCKER** | campaigns | No campaign in the Campaigns App: the funnel needs one (packages, offers, shipping, API key) |
| WARN | store | No support phone number on the store |
| WARN | store | No primary domain connected (store runs on *.29next.store) |
| WARN | catalog | 1 unpublished product(s): #7 DUPLICATE - delete me (Berberine import re-run) |
| WARN | catalog | 1 demo product(s) still public; delete or unpublish before launch |
| WARN | payments | No express methods (Apple Pay / Google Pay / PayPal) available |
| WARN | shipping | #1 Default (0.00 USD): no countries restricted (ships everywhere) |
| WARN | fulfillment | Fulfillment location has no address and no callback URL (no 3PL connected yet) |
| WARN | storefront | No storefront theme installed (fine for a standalone Page Kit funnel) |
| OK | catalog | 1 real product(s) |

## Inventory

| Object | Count |
|---|---|
| products | 3 |
| categories | 1 |
| campaigns | 0 |
| gateways | 0 |
| shipping_methods | 1 |
| locations | 1 |
| themes | 0 |
| pages | 3 |
| webhooks | n/a |
| orders | 0 |
| subscriptions | 0 |

Currencies: USD · Languages: en · Timezone: America/New_York
