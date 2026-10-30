# SKINOFAB funnels

The SKINOFAB sales funnels as one [Campaign Page Kit](https://github.com/NextCommerceCo/next-campaign-page-kit) project:
static HTML, CSS and JS, with the [Campaign Cart SDK](https://cart-sdk.nextcommerce.com/latest/) taking the orders in
the browser. Any static host serves it.

| Funnel | Entry page | Campaigns App campaign |
|---|---|---|
| Adaptive Peptide Foundation | `/apf-funnel/10-reasons-adaptive-foundation/` (also `/` and `/apf`) | 2221 |
| Foundation Stick | `/stick-funnel/10-reasons-foundation-stick/` (also `/stick`) | 2211 |

Each funnel's pages, in order: listicle, sales page, checkout, the post-purchase offers, thank-you. Their sources are
in `src/<funnel>/` (one `.html` per page, `assets/` beside them, `assets/config.js` holds the campaign's public key).

## Hosting (one time)

1. **Connect the repo** to a static host. Build command `npm run build:static`, publish folder `_site`, Node 22.
   - **Netlify:** `netlify.toml` sets all of it. Import the repo, deploy.
   - **Vercel:** `vercel.json` sets all of it. Import the repo, framework "Other", deploy.
   - **Cloudflare Pages:** framework "None", build command `npm ci --omit=dev && npm run build:static`, output
     `_site`, environment variable `NODE_VERSION=22`.
2. **Add a domain** in the host's dashboard, for example `go.skinofab.com`, and the DNS record it asks for.
3. **Set `FUNNEL_HOST`** in the host's environment variables to that domain with `https://`
   (`https://go.skinofab.com`), then redeploy. Every page then sends a visitor on the host's own address
   (`*.netlify.app`, `*.vercel.app`, `*.pages.dev`) to the same page on your domain.
4. **Allow the domain on both campaigns** (the API cannot do this): Campaigns App > campaign 2221 > Settings >
   Allowed Domains, add `go.skinofab.com` as a Production domain; the same on campaign 2211. Without it the SDK
   refuses every call from the domain: no prices, no checkout.
5. **Check it:** open `https://go.skinofab.com/apf-funnel/foundation-checkout/`; the pack cards show their prices and
   PayPal / Apple Pay appear within a few seconds.

Until step 4, a preview build shows the pages but not the prices or the checkout.

The policy and contact links in the footers go to the store (`https://try.skinofab.com/privacy-policy/?from=offer`
…), set in `_data/campaigns.json`; the store keeps those pages.

## Changing the pages

The source of truth is `campaigns/skinofab` in the `Claude-rx/App` repo: its tools write parts of these pages (the
offer pages from `tools/funnel/apf/offer_pages.py`, the images from `tools/funnel/apf/images.py`) and check every
page (`tools/funnel/apf/check_apf.py`: prices, renewal terms, claims, layout rules). After a change there,
`tools/funnel/publish_funnels.sh` pushes this folder here, with its history, and the host rebuilds in about a
minute. Edit here directly only for a quick fix, and bring it back to `Claude-rx/App` the same day.

Locally: `npm ci`, then `npm run dev` (live preview; `localhost` is always allowed by the SDK) or
`npm run build:static` and serve `_site/`.

## What else is here

- `_data/campaigns.json`: each funnel's settings (SDK version, store links, AppLovin Axon key, `funnel_host`).
- `campaign-spec*.json`, `campaign-runtime.build.json`, `.campaign-runtime/`, `design-source*/`, `runs/`: the
  Campaigns OS records (spec, build packet, polish and QA evidence) that `npx campaigns-os` reads.
- `CLAUDE.md`: the Campaign Cart rules for an AI assistant working on these pages.
