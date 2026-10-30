# site-export

Reproducible pipeline that turns the live smooche.com storefront into the offline, SKINOFAB-branded static site in `skinofab-site/`.

| Script | What it does |
|---|---|
| `build.py` | Reads the storefront sitemap (products, pages, collections, blog articles) plus policies, cart, search and blog index. For each page it fetches the server HTML, removes trackers and third-party apps, downloads every image, video, font, stylesheet and theme script into one shared `assets/` store, swaps in the SKINOFAB logo, and rewrites internal links to the exported `.html` files. Writes `export-manifest.json`. |
| `verify.mjs` | Loads every exported page in headless Chromium with **all external network blocked** and fails if a page attempts an external request, throws a JS error, gets a 404, shows a broken image, still shows the old logo, or is missing the new one. Writes `qa-report*.json` and optional full-page screenshots. |
| `capture.mjs` | One-off Playwright capture of the rendered homepage plus every network response (for debugging and visual comparison). |
| `skinofab.svg` | Source logo. |

```bash
python3 -I tools/site-export/build.py skinofab-site tools/site-export/skinofab.svg      # add --only /products/x,/pages/y for a subset
node tools/site-export/verify.mjs skinofab-site [shots_dir]                           # desktop 1440px
node tools/site-export/verify.mjs skinofab-site --mobile                              # mobile 390px
```

Vendor libraries (Swiper 9.4.1, jQuery 3.7.1, js-cookie 3.0.1, Font Awesome 6.6.0) come from the npm registry into `npm/`, which is git-ignored and fetched on the first run. The public CDNs they normally load from may be unreachable.

## Rules worth knowing
- **Scripts kept:** the theme's own `/cdn/shop/t/<id>/assets/*.js` (except the IE11 polyfill and the geo-IP price lookup), the vendor libraries, and inline theme config. Everything else is dropped. That covers analytics, pixels, A/B testing, chat, review and bundle apps, and wallets. See `DROP_INLINE`.
- **`assets/js/offline-shim.js`** answers the theme's `/cart*.js`, section-rendering, recommendation, search-suggest and localization fetches locally (an empty cart), so drawers and add-to-cart degrade quietly instead of throwing.
- **Responsive images** keep two widths (about 800w and 1800w). Media URLs inside JSON blobs (variant galleries) are pointed at the local copies.
- **CSS custom-property `url()`s** are embedded as data URIs. Otherwise they resolve against whichever stylesheet uses the variable and break.
- **`futura-pt`** (Adobe Fonts, licensed and domain-locked) is aliased to **Jost** via `assets/css/futura-pt-fallback.css`.
- **Links:** internal links point to exported pages; anything not exported (checkout, account) becomes `#`; brand-owned social links become `#`.
