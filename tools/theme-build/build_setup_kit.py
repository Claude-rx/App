"""Generate the NEXT store setup kit for the SKINOFAB theme from the design export.

usage: python3 -I build_setup_kit.py <export_dir> <theme_dir> <out_dir>

Writes:
  products.json      one entry per design product: title, slug, template key, description, options, design prices
  categories.json    design collections -> NEXT categories (+ the theme setting that links to each)
  pages.json         NEXT pages to create: title, slug, template key (Admin API payloads)
  blog-posts.json    blog posts with their article HTML
  create-pages.sh    Admin API script for pages.json (needs ADMIN_TOKEN with content:write)
  README.md          the store setup checklist
"""
import json, re, sys, html
from pathlib import Path
from bs4 import BeautifulSoup

EXPORT, THEME, OUT = (Path(p).resolve() for p in sys.argv[1:4])
OUT.mkdir(parents=True, exist_ok=True)
var = lambda h: re.sub(r'[^a-z0-9]+', '_', h.lower()).strip('_')

snaps = {f.stem: json.loads(f.read_text()) for f in (EXPORT / 'products').glob('*.js')}
templates = {p.name[len('product.'):-5] for p in (THEME / 'templates' / 'catalogue').glob('product.*.html')}
products = []
for h in sorted(templates):
    d = snaps.get(h, {})
    products.append({
        'design_handle': h,
        'title': d.get('title') or h.replace('-', ' ').title(),
        'slug': h,
        'template': h,
        'theme_setting': f'sf_p_{var(h)}',
        'description_html': d.get('description', ''),
        'options': [{'name': o.get('name'), 'values': o.get('values', [])} for o in d.get('options', []) if isinstance(o, dict)]
                   or [{'name': n, 'values': []} for n in d.get('options', []) if isinstance(n, str)],
        'variants': [{'title': v.get('title'), 'options': [v.get('option1'), v.get('option2'), v.get('option3')],
                      'design_price': (v.get('price') or 0) / 100, 'design_compare_at_price': (v.get('compare_at_price') or 0) / 100 or None,
                      'sku': v.get('sku') or ''} for v in d.get('variants', [])],
        'note': 'Design prices are a reference only. The storefront shows the prices you set in NEXT.',
    })
for prod in products:  # Shopify's placeholder option for single-variant products is not a NEXT variant
    if [o['name'] for o in prod['options']] in (['Title'], []) and len(prod['variants']) <= 1:
        prod['options'] = []
        for v in prod['variants']: v['options'] = []; v['title'] = prod['title']
(OUT / 'products.json').write_text(json.dumps(products, indent=2, ensure_ascii=False))

schema = json.loads((THEME / 'configs' / 'settings_schema.json').read_text())
cats = [{'design_handle': f['name'][5:].replace('_', '-'), 'title': f['label'], 'theme_setting': f['name'],
         'set_setting_to': 'the NEXT category URL, e.g. /catalogue/category/<slug>_<id>/'} for f in schema['SKINOFAB']['Collection Links']]
(OUT / 'categories.json').write_text(json.dumps(cats, indent=2, ensure_ascii=False))

pages = []
for p in sorted((THEME / 'templates' / 'pages').glob('page.*.html')):
    slug = p.name[len('page.'):-5]
    src = EXPORT / 'pages' / f'{slug}.html'
    if not src.exists(): src = EXPORT / 'policies' / f'{slug}.html'
    title = slug.replace('-', ' ').title()
    if src.exists():
        t = BeautifulSoup(src.read_text(), 'lxml').title
        if t and t.get_text(strip=True): title = re.sub(r'\s*[–—|-]\s*(Smooche|SKINOFAB)\s*$', '', t.get_text(strip=True))
    pages.append({'title': title, 'slug': slug, 'template': slug, 'content': '<p>Rendered by the theme template.</p>',
                  'meta_title': title, 'meta_description': ''})
(OUT / 'pages.json').write_text(json.dumps(pages, indent=2, ensure_ascii=False))

posts = []
for a in sorted((EXPORT / 'blogs' / 'news').glob('*.html')):
    s = BeautifulSoup(a.read_text(), 'lxml')
    body = s.select_one('.article__content, .rte, [data-article-content]')
    h1 = s.find('h1')
    posts.append({'title': h1.get_text(strip=True) if h1 else a.stem, 'slug': a.stem,
                  'content_html': ''.join(str(c) for c in body.contents) if body else ''})
(OUT / 'blog-posts.json').write_text(json.dumps(posts, indent=2, ensure_ascii=False))

(OUT / 'create-pages.sh').write_text('''#!/usr/bin/env bash
# Create every SKINOFAB page in NEXT with its theme template (Admin API, needs a token with content:write).
# usage: STORE=<subdomain> ADMIN_TOKEN=<token> ./create-pages.sh
set -euo pipefail
: "${STORE:?set STORE to the store subdomain}" "${ADMIN_TOKEN:?set ADMIN_TOKEN}"
cd "$(dirname "$0")"
python3 - <<'PY'
import json, os, urllib.request
store, token = os.environ["STORE"], os.environ["ADMIN_TOKEN"]
for page in json.load(open("pages.json")):
    req = urllib.request.Request(f"https://{store}.29next.store/api/admin/pages/", method="POST",
        data=json.dumps(page).encode(), headers={"Authorization": f"Bearer {token}",
        "X-29next-API-Version": "2024-04-01", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r: print("created", page["slug"], r.status)
    except urllib.error.HTTPError as e:
        print("FAILED", page["slug"], e.code, e.read()[:200])
PY
''')
(OUT / 'create-pages.sh').chmod(0o755)

(OUT / 'README.md').write_text(f'''# SKINOFAB on NEXT: store setup kit

The theme renders the full design. These records make it **functional**: real products, prices, cart and checkout.

## 1. Products ({len(products)}), `products.json`
For each entry:
1. Create the product in **Dashboard > Catalogue > Products**: title, description, images, price.
   If it has `options` (for example Color: Espresso, Hazelnut…), make it a parent product with one child per variant.
   **Use the exact option value names**: the design's swatches match variants by name.
2. Set the product's **Template** to the `template` value (for example `color-changing-foundation`). This selects
   `templates/catalogue/product.<template>.html`, the full design PDP. Products without a template use the default PDP.
3. In **Theme Editor > SKINOFAB > Product Links**, pick the product for its `theme_setting`. Every link, price and
   add-to-cart in the design that points to that product resolves through this setting.

The `design_price` values are the source site's prices, a reference only. The storefront always shows the NEXT price.

## 2. Categories ({len(cats)}), `categories.json`
Create the categories, assign products, then paste each category URL into **Theme Editor > SKINOFAB > Collection Links**.

## 3. Pages ({len(pages)}), `pages.json`
Each page needs a NEXT page with the same **slug** and **template** (`templates/pages/page.<slug>.html`).
With an Admin API token (`content:write`): `STORE=<subdomain> ADMIN_TOKEN=... ./create-pages.sh`.
Pages route at `/<slug>/`. Verify one with `curl -I https://<store>.29next.store/<slug>/?preview_theme=<theme_id>`.

## 4. Blog ({len(posts)} posts), `blog-posts.json`
Create the posts in **Dashboard > Content > Blog** (title, slug, content). The theme's `blog/post.html` renders them in the design layout.

## 5. Offers that the design's copy promises (operator-approved ledger)
- **Fall Sale: Up to 67% OFF + FREE Gifts** (announcement bar), **SAVE x%** badges, and bundle savings need matching
  Offers in **Dashboard > Marketing > Offers**. Without them checkout charges full price.
- **Shipping:** the delivery copy quotes the Theme setting *Shipping Fee*; keep it equal to your shipping rate.
- **Shipping protection:** create the product and pick it under **SKINOFAB > Checkout Add-ons**.

## 6. Checklist before publishing
- [ ] All Product Links set (the Theme Editor shows each by its design title)
- [ ] Each product's Template set
- [ ] Pages created with their templates
- [ ] Offers configured for every promo the design advertises
- [ ] Add to cart → side cart → checkout tested on the preview URL
''')
print(f'products {len(products)}  categories {len(cats)}  pages {len(pages)}  posts {len(posts)}')
