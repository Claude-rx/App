# SKINOFAB storefront: static HTML export

The complete smooche.com storefront front end (captured October 2026), rebranded with the SKINOFAB logo and fully self-contained: **all pages, images, videos, icons, fonts, CSS and JS are local.**

## Open it
```bash
cd skinofab-site
python3 -m http.server 8000      # then open http://localhost:8000
```
Serve the folder **from its root** (any static host works: Netlify, Vercel, S3, nginx). Pages also open by double-click (`file://`), but browsers block the `fetch()` calls that power color swatches, upsells and "You may also like" under `file://`.

## What's inside
| Folder | Contents |
|---|---|
| `index.html` | Homepage |
| `products/*.html` | All product pages (PDPs), each with a `products/<handle>.js` product-JSON snapshot used by swatches, quick add and upsells |
| `collections/*.html` | Shop All, Face, Lips, Lashes, Brows, Bundles, Sale, Essentials, Serums… |
| `pages/*.html` | About, Contact, FAQ, Terms of service, Privacy, Cookie policy, Guarantee, Careers, Reviews, quizzes, landing and advertorial pages |
| `policies/*.html` | Terms, Privacy, Refund, Shipping, Contact information |
| `blogs/news.html`, `blogs/news/*.html` | Blog index and articles |
| `cart.html`, `search.html` | Cart and search templates |
| `recommendations/*.html` | Snapshots of each PDP's "You may also like" section |
| `assets/img`, `assets/media` | Every image (product, lifestyle, icons, payment badges) and video |
| `assets/css`, `assets/fonts`, `assets/js` | Theme (Palo Alto 5.6 + custom), Swiper, jQuery, Font Awesome, Jost |
| `export-manifest.json`, `qa-report*.json` | Page list, any assets that could not be downloaded, QA results |

## What was changed vs. the live site
- **Logo:** every Smooche logo (header, mobile menu, footer, in-content wordmarks, favicon) is now the SKINOFAB SVG. Image alt text and page titles say SKINOFAB.
- **Links:** all internal links point to the exported pages. Checkout, account, and brand social links point to `#`.
- **Removed:** tracking and marketing scripts (Shopify analytics, pixels, Klaviyo, Northbeam, Triple Whale, Intercom, Loox, A/B testing, bundle apps, wallets, cookie banner, geo-pricing).
- **Cart:** `assets/js/offline-shim.js` answers cart requests locally (an empty cart), so drawers and add-to-cart don't throw. Wire it to your own store or checkout to make it functional.
- **Font:** headings used `futura-pt` from Adobe Fonts, which is licensed and can't be redistributed. It is replaced with **Jost**, a free face that looks nearly identical.
- **Images:** oversized PNG photos were converted to high-quality JPEG and capped at 2000px wide.

## ⚠️ Before going live
Product photos, videos, reviews and copy (including the "Smooche" name in body text and on packaging in photos, the address and the email) belong to Smooche. Use this export as the layout and template, and replace the content with SKINOFAB's own.
