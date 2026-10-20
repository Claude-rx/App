# SKINOFAB live-site handoff: notes

## Evidence origin
- **Fresh extraction:** every capture in `captures.json` (7 routes × 1440/768/390, `static` state, `preload_scroll`) was taken on 2026-10-20 by running `next-theme-design/scripts/capture-page.js` in headless Chromium (Playwright, `--autoplay-policy=no-user-gesture-required`, DPR 1). The page source is the operator-supplied static export of smooche.com (`skinofab-site/`), served from localhost with **all external network blocked**. Driver: `tools/theme-handoff/capture-routes.mjs`. Package author: `tools/theme-handoff/author-package.py`.
- **Operator statements (prior input):** the rights statement in `design-handoff.json` (SKINOFAB owns or is licensed to reuse the content), and approval of both divergence-ledger entries (claims and promotions) on 2026-10-20.
- **Manual observation:** carousel motion (`*.slider` behaviors). It is driven by theme JavaScript (Swiper/Flickity), not CSS animations, so the capture script cannot read it. It was observed by interacting with the export.

## Routes vs. the full site
These 7 routes are one representative per theme template type: home, PDP, collection, page, policy, blog article, page-builder lander. The theme generator builds all 109 exported pages from the same export, one template per page (`templates/pages/page.<slug>.html`, `templates/catalogue/product.<handle>.html`). The other pages share the chrome and section system captured here.

## Inferred entries
None. Every geometry and style entry cites a static capture of its own route and viewport.

## Blocked sections and next actions
- `lander.s*` (page-builder landers): **blocked** on 30 images hosted on `assets.replocdn.com` / `cdn.instant.so`. Those hosts are blocked in the build environment. Next action: the operator allows the hosts (agreed 2026-10-20), the export is re-run, and the assets become `downloaded`.
- All other sections are READY.

## Commerce truth
- Prices, compare-at prices and currency **always come from NEXT** (`{% purchase_info_for_product %}`). Every captured price string is `omit`.
- Promotional copy (Fall Sale 60% OFF, SAVE x%, free mystery gift) ships as source text in Theme settings. **The operator must create matching NEXT Offers** before publishing, or checkout will not honor the copy.
- Social-proof and performance claims are reused with the operator's approval. Substantiation is the merchant's responsibility.

## Limits of automated capture on this export
- Text inside UGC/review videos is not readable. No media-frame captures were taken (gap `sf-video-frame-text`).
- Lazy videos report no `current_src`. Their sources were resolved from the supplied HTML by element id.
- Captured text has CSS `text-transform` applied (for example, uppercase CTAs).
- Header-hidden layouts on landers: page-builder pages render without the global header.
