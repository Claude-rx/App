# SKINOFAB on NEXT: store setup kit

The theme renders the full design. These records make it **functional**: real products, prices, cart and checkout.

## 1. Products (26), `products.json`
For each entry:
1. Create the product in **Dashboard > Catalogue > Products**: title, description, images, price.
   If it has `options` (for example Color: Espresso, Hazelnut…), make it a parent product with one child per variant.
   **Use the exact option value names**: the design's swatches match variants by name.
2. Set the product's **Template** to the `template` value (for example `color-changing-foundation`). This selects
   `templates/catalogue/product.<template>.html`, the full design PDP. Products without a template use the default PDP.
3. In **Theme Editor > SKINOFAB > Product Links**, pick the product for its `theme_setting`. Every link, price and
   add-to-cart in the design that points to that product resolves through this setting.

The `design_price` values are the source site's prices, a reference only. The storefront always shows the NEXT price.

## 2. Categories (14), `categories.json`
Create the categories, assign products, then paste each category URL into **Theme Editor > SKINOFAB > Collection Links**.

## 3. Pages (55), `pages.json`
Each page needs a NEXT page with the same **slug** and **template** (`templates/pages/page.<slug>.html`).
With an Admin API token (`content:write`): `STORE=<subdomain> ADMIN_TOKEN=... ./create-pages.sh`.
Pages route at `/<slug>/`. Verify one with `curl -I https://<store>.29next.store/<slug>/?preview_theme=<theme_id>`.

## 4. Blog (6 posts), `blog-posts.json`
Create the posts in **Dashboard > Content > Blog** (title, slug, content). The theme's `blog/post.html` renders them in the design layout.

## 5. Offers that the design's copy promises (operator-approved ledger)
- **Fall Sale: 60% OFF + FREE Mystery Gift** (announcement bar), **SAVE x%** badges, and bundle savings need matching
  Offers in **Dashboard > Marketing > Offers**. Without them checkout charges full price.
- **Shipping:** the delivery copy quotes the Theme setting *Shipping Fee*; keep it equal to your shipping rate.
- **Shipping protection:** create the product and pick it under **SKINOFAB > Checkout Add-ons**.

## 6. Checklist before publishing
- [ ] All Product Links set (the Theme Editor shows each by its design title)
- [ ] Each product's Template set
- [ ] Pages created with their templates
- [ ] Offers configured for every promo the design advertises
- [ ] Add to cart → side cart → checkout tested on the preview URL
