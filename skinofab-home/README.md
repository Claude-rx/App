# SKINOFAB homepage — static export

Offline, self-contained copy of the smooche.com homepage front end (captured 2026-10-20), rebranded with the SKINOFAB logo.

**Open:** serve the folder and visit it, e.g. `python3 -m http.server -d skinofab-home 8000` → http://localhost:8000
(opening `index.html` directly via `file://` also works, but videos/fonts load more reliably over HTTP).

## What's included
| | |
|---|---|
| `index.html` | Full homepage markup — every section, product card, review, footer |
| `assets/img/` | All product, lifestyle, category, icon and payment images (2 sizes per responsive image: ~800w + ~1800w) |
| `assets/media/` | Hero / UGC / "Phenomenon" videos (mp4) |
| `assets/css/` | Theme CSS (Palo Alto 5.6 + custom), Swiper, Font Awesome 6.6 |
| `assets/fonts/` | Jost (all weights), Lora, Font Awesome webfonts |
| `assets/js/` | Theme JS (menus, drawers, sliders, tabs), jQuery 3.7.1, Swiper 9.4.1, js-cookie |
| `assets/img/skinofab-logo.svg` / `-white.svg` | Your logo — replaces the header, mobile drawer, footer, "The ___ Phenomenon" heading and favicon |

## What was changed vs. the live site
- **Logo:** every Smooche logo (black + white variants) → SKINOFAB SVG; `alt` → "SKINOFAB"; page title → "SKINOFAB".
- **Removed:** all tracking/marketing scripts and iframes (Shopify analytics & web pixels, Klaviyo, Northbeam, Triple Whale, Converge, Intercom, Loox, Elevate A/B, Kaching, AppLovin, Alia, etc.), the cookie banner, OG/Twitter meta, Shopify checkout/Shop Pay wallets.
- **Links:** internal store links point to `#` (no links back to smooche.com).
- **Font:** headings used `futura-pt` from Adobe Fonts (licensed, domain-locked) → aliased to **Jost**, the free geometric Futura-style face the theme already ships. Visually near-identical.

Verified in headless Chromium at 1440px and 390px with **all external network blocked**: 0 external requests, 0 JS errors, 0 missing files, 0 broken images.

## ⚠️ Before going live
The product photos, videos, reviews and copy (including "Smooche" in body text, address, email, product packaging in photos) belong to Smooche. Use this as a layout/template and swap in SKINOFAB content.

## Rebuild
`tools/site-export/` — `capture.mjs` (Playwright capture) → `build.py` (localize + rebrand) → `verify.mjs` (offline check + screenshot).
```bash
node tools/site-export/capture.mjs $PWD/tools/site-export/capture
python3 -I tools/site-export/build.py tools/site-export/capture skinofab-home tools/site-export/skinofab.svg
node tools/site-export/verify.mjs $PWD/skinofab-home /tmp/shot.png        # add `mobile` for 390px
```
