# Speed, cleanup and cart drawer

How the SKINOFAB theme is kept fast and clean, and how to check it. All of it runs in the build, so every
rebuild keeps it: `tools/build_store.sh <work_dir>` (persona copy → theme build → speed pass → gates).

## What the build does

**Design cleanup** (`tools/theme-build/build_theme.py`, `clean_design`). The design export still carried the
old Shopify store's runtime. Removed on every page:
- Shopify/app configuration and data: PayPal/Apple Pay metadata, the contact-form hCaptcha bootstrap, Shopify
  module flags, Kaching bundle data blobs (~25 KB per product page), the Replo store blob, the Shop app follow
  button. The Kaching stylesheet goes too on pages without Kaching markup.
- Scripts for the Shopify cart drawer that the Spark side cart replaces (cart timer, gift guard, upsell
  purchase, routine upgrade, subscription card prices), js-cookie and jQuery (nothing uses either).
- Links to the old store become NEXT routes (`08f531-2.myshopify.com`, `skinofab.com`, Shopify account URLs).
  The guarantee page's Typeform goes to the contact page. Links to the previous brand's Instagram posts are
  unlinked. Hot-linked third-party icons on the policy pages are dropped, and the shipping country flag
  (from `cdn.shopify.com`) is now an emoji.
- `window.SFHandlePk` lists only the products a page references. Each entry is a settings-product lookup on
  every render, and the homepage needed none of its 26.

**Speed pass** (`tools/theme-build/optimize_theme.py`, after the build):

| Step | What it does | Safety check |
|---|---|---|
| Unused CSS | Drops selectors whose classes/ids appear in no template, partial, layout, script or product JSON | Classes built at runtime are protected by the prefixes found in script strings; `:not()`/`:is()` arguments never count against a rule |
| One stylesheet | The 7 design stylesheets every page links become one content-hashed bundle | Stylesheets that move past inline `<style>` blocks may share no subject and property with them, or they stay put |
| Fonts | Unused and duplicate `@font-face` rules dropped, text fonts swap; landing-page Google Fonts self-hosted (Latin) | — |
| Swiper | Loads with `defer`; inline slider scripts run on DOMContentLoaded (`defer_inline.mjs`, same global names) | Fails closed: stays render-blocking if any script doesn't parse or a late global is read elsewhere |
| Images | srcsets use CDN-resized candidates of the largest source (`&width=`, cdn.29next.store) sized from `sizes` | Without the parameter the CDN serves the full image |
| Gates | Every changed stylesheet compiles with libsass (the platform's CSS compiler); no multi-line DTL comments | Build fails |

Report: `theme-optimize-report.json`.

**Cart drawer** (`tools/theme-build/static/skinofab-cart-drawer.js`). Spark's `<spark-cart-drawer>` keeps cart
state, mutations, focus and events. This file is its renderer (same API as `spark-cart-drawer-renderer.js`)
and styles it through its open shadow root. The text lives in Theme settings → SKINOFAB → Cart Drawer.

## Results (live preview, theme 34)

| | Before | After |
|---|---|---|
| Lighthouse mobile performance, home | 56 | 62–64 |
| Lighthouse mobile performance, PDP | 52 | 68–77 |
| Lighthouse best practices / SEO, home | 96 / 75 | 100 / 83 |
| Render-blocking requests | 10–11 | 2–3 |
| PDP LCP (mobile, unthrottled) | 1.96 s | 1.00 s |
| PDP weight (mobile) | 2.3 MB | 1.5 MB |
| Shared design CSS | 7 files, 120 KB gzip | 1 file, 47 KB gzip |
| Font Awesome CSS | 92 KB | 2 KB |

What's left is mostly platform-side: the root document takes ~0.7–1.5 s on the preview domain (the mapped domain's
page cache is faster), and NEXT injects a ~80 KB New Relic browser agent into every page.

## Checking it

```bash
# speed: requests, bytes by type/host, render-blocking, FCP/LCP/CLS, external hosts
node tools/theme-qa/perf-audit.mjs https://skinofab.29next.store 34 out.json --routes /,/catalogue/adaptive-peptide-foundation_14/

# pixel comparison of two local renders (tools/theme-qa/render.py), before vs after a change
python3 tools/theme-qa/render.py <theme_before> <export> before/ && python3 tools/theme-qa/render.py skinofab-theme <export> after/
node tools/theme-qa/visual-diff.mjs before/ after/ shots/ && python3 tools/theme-qa/diff.py shots/

# cart drawer (mocked NEXT cart): opens on add, header above the sticky site header, screenshots
node tools/theme-qa/qa.mjs after/ shots/ --only /products/color-changing-foundation/ --cart [--mobile]

# live subscription flow: both bases, the no-plan add path, cart page, checkout
node tools/theme-qa/offer-e2e.mjs https://skinofab.29next.store 34 /catalogue/adaptive-peptide-foundation_14/ shots/
```

Checkout itself is NEXT's page. See `docs/checkout-setup.md` for the dashboard settings.
