# SKINOFAB: Next Commerce theme

The complete SKINOFAB storefront design, built on NEXT's **Spark** runtime:
- **From the design:** every page's markup, CSS, JS, images, videos, fonts and icons.
- **From NEXT:** products, prices, variants, cart and checkout.

Generated from the static site export by `tools/theme-build/build_theme.py`. **Do not hand-edit generated templates.**
Change the design or the generator, then regenerate the whole family.

## What's in it
| Area | Files | Data from NEXT |
|---|---|---|
| Homepage | `templates/index.html` | product links, prices, add to cart via *SKINOFAB > Product Links* |
| 26 design PDPs | `templates/catalogue/product.<handle>.html` (product template key = handle) | `product`: title, price, compare-at, variants, add to cart |
| Default PDP | `templates/catalogue/product.html` | the same, plus NEXT gallery images and description |
| Collections | `templates/catalogue/category.html`, `index.html` | `products`, rendered with the design card (`partials/sf_product_card.html`) |
| 55 pages | `templates/pages/page.<slug>.html` (page template key = slug), `page.html` for any other page | `page` |
| Blog | `templates/blog/index.html`, `post.html` | `posts`, `post` |
| Search | `templates/search.html` | `page.object_list` |
| Cart / account / support / errors | Spark templates (Spark styling) | Spark |
| Chrome | `partials/header.html`, `partials/footer.html` | the cart icon opens the Spark side cart |

## How commerce works
- **Prices:** `partials/sf_price.html` renders `{% purchase_info_for_product %}` in the design's format (`$49 USD`).
  It also renders compare-at prices (`retail=1`) and pay-in-4 instalments (`quarter=1`). No source price is hardcoded.
- **Add to cart:** `assets/js/skinofab-commerce.js` routes the design's own forms and its Shopify-style AJAX cart calls
  (`/cart/add.js`, `/cart.js`, `/cart/change.js`, cart permalinks) to NEXT's GraphQL cart through Spark's `SparkCartClient`.
  It then opens the Spark side cart (`<spark-cart-drawer>`). Design variant ids are translated to the NEXT products chosen in settings.
- **Variants:** on PDPs the adapter re-keys the design's `ProductJson` to NEXT children from `product.data` and `variant_form`,
  matching by option value name. Create NEXT variant values with the same names (for example Espresso).
- **CSS/font assets:** NEXT serves CSS and media from different hosts, so stylesheets contain no relative `url()`.
  Fonts and stylesheet images resolve in `partials/sf_asset_styles.html` via `asset_url`.

## Store setup
Follow `next-setup-kit/README.md`. It covers products with template keys, Product Links settings, categories, pages
(Admin API script), blog posts, and the Offers the design's promotions require.

## Verify
```bash
python3 scripts/check-dtl.py --require     # all templates compile under Django 4.2 with the platform tag inventory
python3 scripts/check-templates.py         # includes, url names, routes, cart PK rules
python3 scripts/check-theme-contract.py    # Spark runtime hooks (pixels, cart badge, side cart, mobile nav)
python3 scripts/check-settings-parity.py
```
For offline browser QA of rendered pages, see `tools/theme-qa/` in the project (`render.py`, `qa.mjs`, `geometry.mjs`).

## Upload (unpublished theme)
```bash
NTK_APIKEY="$THEME_API_KEY" ntk init --name="SKINOFAB" --store="https://<store>.29next.store"
ntk list    # confirm the new theme id and that it is NOT (Active)
for dir in assets configs layouts locales partials templates; do find "$dir" -type f; done \
  | grep -v '^configs/settings_data.json$' | while IFS= read -r f; do ntk push "$f" || exit 1; done
# preview: https://<store>.29next.store/?preview_theme=<theme_id>
```
