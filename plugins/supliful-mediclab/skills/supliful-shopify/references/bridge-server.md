# Always-on bridge (optional)

Cowork tools run when the user asks. For hands-off operation (every paid order sent to Supliful
automatically and tracking pushed back as parcels ship), the same code runs as a small web service:
`tools/supliful/server.mjs` in the Claude-rx/App repository.

- Routes: `POST /webhooks/shopify/orders-paid` (Shopify `orders/paid` topic), `POST /webhooks/supliful`
  (Supliful connection -> Manage -> Webhooks -> Add endpoint), `GET /health`.
- Hosting: any Node 22 host serving public `https://` with a persistent disk (Render, Fly.io, Railway, a
  VM behind Caddy). Set the same variables as the settings file, plus `SUPLIFUL_WEBHOOK_SECRETS` and
  `SHOPIFY_WEBHOOK_SECRET`.
- Signatures are verified over the raw body, deliveries are deduplicated, and test deliveries change nothing.
- Supliful switches an endpoint off after three days without a successful delivery. After switching it back on,
  run `supliful_reconcile`.

Full guide: `docs/supliful-integration.md` in the repository.
