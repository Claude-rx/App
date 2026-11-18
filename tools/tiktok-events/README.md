# TikTok Events API (server-to-server) for Get Rid Of

The browser pixel (`DBUORJRC77UCDH70RUD0`) runs on every page of the four funnels. This relay sends the same purchases
from the server, so TikTok still gets them when an ad blocker, Safari's tracking limits or a closed tab stops the
browser pixel. TikTok keeps one copy of each purchase because both sides use the same `event_id`.

```
buyer pays ──► NEXT order ──► webhook (order.created / order.updated) ──► Netlify function ──► TikTok Events API
                    ▲                                                        │ reads the order from the Admin API
                    └────────────────────────────────────────────────────────┘ (the webhook body is not trusted)
```

## What is sent

| Event | `event_id` | Same id as the pixel's | Value |
|---|---|---|---|
| `Purchase` (the order) | order number, e.g. `100629` | `dl_purchase` transaction_id | order total minus upsells |
| `Purchase` (each upsell) | `{ref_id}-US{n}`, n = 1, 2… in the order they were added | `dl_upsell_purchase` id | that line's price |

User data: email and phone, normalised and SHA-256 hashed; `external_id` (hashed customer id); IP and browser user agent
from the order; `ttclid` / `ttp` when the order's attribution carries them. Contents: SKU (`cdkh-16-1s`), name, quantity,
unit price — the same `content_id` the pixel sends.

**Repeats are safe.** NEXT sends `order.updated` several times per order. TikTok drops an Events API event whose
event + event_id it already received in the past 48 hours, so the relay sends every purchase of an order on each
webhook, for orders placed in the last 40 hours, and sends nothing for older orders (e.g. a fulfillment update weeks
later). Test orders (`is_test`) are skipped unless a test event code is set. Canceled orders are skipped.

## Set it up (about 10 minutes)

1. **Netlify site.** Netlify → Add new site → Import from Git → this repository → **Base directory
   `tools/tiktok-events`** (the `netlify.toml` there does the rest; there is no build).
2. **Environment variables** (Site configuration → Environment variables). Never put them in the repository:

   | Name | Value |
   |---|---|
   | `TIKTOK_ACCESS_TOKEN` | the Events API access token (TikTok Events Manager → the pixel → Settings) |
   | `NEXT_ADMIN_TOKEN` | a NEXT Admin API token that can read orders (NEXT dashboard → Settings → API access) |
   | `RELAY_KEY` | a long random string, e.g. `openssl rand -hex 24` |
   | `TIKTOK_PIXEL_ID` | optional, default `DBUORJRC77UCDH70RUD0` |
   | `TIKTOK_TEST_EVENT_CODE` | optional, while testing: Events Manager → Test Events code |

   Redeploy after setting them.
3. **Webhook.** Point the store at the function (from a machine with a NEXT Admin token, or this repo's agent session):
   ```bash
   python3 -I tools/tiktok-events/create_webhook.py "https://<your-site>.netlify.app/tiktok-events?key=<RELAY_KEY>"
   ```
4. **Test.** With `TIKTOK_TEST_EVENT_CODE` set, place a test order, or replay a recent order:
   ```bash
   NEXT_ADMIN_TOKEN=… TIKTOK_ACCESS_TOKEN=… node tools/tiktok-events/send-order.mjs <order number> --send --test-code <CODE>
   ```
   It shows in Events Manager → Test Events with source "Server". Then remove `TIKTOK_TEST_EVENT_CODE` and redeploy.
5. **Check.** Events Manager → the pixel → Overview: Purchase shows both "Browser" and "Server", with deduplication.
   Netlify → Logs → Functions shows one line per webhook: the order number, the event_ids and `sent`.

## Files

- `lib/relay.mjs` — order → TikTok events, hashing, the Events API call, the Admin API read (no dependencies).
- `netlify/functions/tiktok-events.mjs` — the webhook endpoint (`POST /tiktok-events?key=…`). Non-2xx on a failed
  order lookup or a TikTok refusal, so NEXT retries.
- `send-order.mjs` — preview (default) or send one order's events by hand.
- `create_webhook.py` — create / update / list / delete the store webhook.
- `test/relay.test.mjs` — `node --test tools/tiktok-events/test/*.test.mjs` (synthetic orders only).

The browser side lives with the funnels: `campaigns.json` `tiktok_pixel_id` (checkout, offer and thank-you pages, via the
page kit's `tiktok.adapter.js`) and `tools/funnel/getridof/tiktok-head.js` (the four sales pages: page view,
ViewContent, AddToCart). `tools/funnel/getridof/items-fix.js` corrects a Campaign Cart SDK labelling bug (the 3-pack
reported as "Package Protection") before the pixel sends checkout events.
