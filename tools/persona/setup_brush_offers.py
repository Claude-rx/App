"""The Lymphatic Brush on NEXT: the product, its three bundles and their prices. Idempotent.

usage: NEXT_API_TOKEN=... python3 -I setup_brush_offers.py <store_subdomain> <work_dir> [copy_module]
copy_module: brush_copy (default) or balm_copy (the PDRN Plumping Balm: 1, 2 or 3 sticks); everything below reads
the module's BUNDLES, CATEGORIES and texts, and writes its OFFERS_FILE.
- one product (slug and template key the-lymphatic-brush), public, one-time purchase (no refills), with a Bundle
  attribute: 1 brush + free case ($24.95), 2 brushes + 2 free cases ($39.95), 3 brushes + 3 free cases + free body
  brush ($49.90); each compare-at is the single-brush price times the brushes (brush_copy.BUNDLES)
- the free cases and the body brush are named in the variant, so the order shows what to pack (not cart lines)
- in the same collections as the other face tools (brush_copy.CATEGORIES: Accessories, Face, Skin, Bestsellers)
- matched by slug on re-runs; variants by SKU
- writes <work_dir>/brush-offers.json (product and variant pks for the bundle picker and the cart drawer) and adds
  the product to <work_dir>/catalog-rb.json (the theme build's handle -> NEXT product mapping)
Images: upload_gallery.py <store> <pk> <undo.json> brand/lymphatic-brush/gallery-{1..7}.jpg
"""
import importlib, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
P = importlib.import_module(sys.argv[3] if len(sys.argv) > 3 else 'brush_copy')
BUNDLES, CATEGORIES, DESCRIPTION, HANDLE = P.BUNDLES, P.CATEGORIES, P.DESCRIPTION, P.HANDLE
META_DESCRIPTION, META_TITLE, TITLE = P.META_DESCRIPTION, P.META_TITLE, P.TITLE

STORE, WORK = sys.argv[1], Path(sys.argv[2])
API = f'https://{STORE}.29next.store/api/admin/'
HDR = {'Authorization': f"Bearer {os.environ['NEXT_API_TOKEN']}", 'X-29next-API-Version': '2024-04-01',
       'Content-Type': 'application/json', 'Accept': 'application/json'}
ATTR = 'Bundle'


def call(method, path, body=None):
    for attempt in range(4):
        req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method=method, headers=HDR)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read(); return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3: time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f'{method} {path} -> {e.code}: {e.read()[:600].decode("utf-8", "replace")}')


def all_products():
    out, url = [], 'products/?page_size=100'
    while url:
        page = call('GET', url); out += page['results']
        nxt = page.get('next'); url = nxt.split('/api/admin/', 1)[1] if nxt else None
    return {p['slug']: p for p in out}


def variant_body(b):
    return {'sku': b['sku'], 'variant_attribute_values': [{'name': ATTR, 'value': b['variant']}],
            'prices': [{'currency': 'USD', 'price': b['price'], 'retail': b['compare']}],
            'track_stock': False, 'allow_backorders': True, 'requires_shipping': True,
            'stockrecords': [{'location_id': 1, 'num_in_stock': 1000, 'low_stock_threshold': 0}]}


cats = {c['slug']: c['id'] for c in call('GET', 'categories/?page_size=100')['results']}
missing = [c for c in CATEGORIES if c not in cats]
if missing: raise SystemExit(f'categories not found: {missing}')
fields = {'title': TITLE, 'slug': HANDLE, 'categories': [cats[c] for c in CATEGORIES], 'description': DESCRIPTION, 'is_public': True, 'template': HANDLE,
          'meta_title': META_TITLE, 'meta_description': META_DESCRIPTION, 'enable_subscription': False,
          'variant_attributes': [{'name': ATTR, 'values': [b['variant'] for b in BUNDLES]}]}
found = all_products().get(HANDLE)
if found:
    pk = found['id']
    call('PATCH', f'products/{pk}/', fields)
    print('updated product', pk)
else:
    created = call('POST', 'products/', {**fields, 'variants': [variant_body(b) for b in BUNDLES]})
    pk = created['id']
    print('created product', pk)
prod = call('GET', f'products/{pk}/')
by_sku = {v.get('sku'): v for v in prod['variants']}
for b in BUNDLES:
    body = variant_body(b)
    v = by_sku.get(b['sku'])
    if v: call('PATCH', f"products/variants/{v['id']}/", {k: body[k] for k in ('sku', 'variant_attribute_values', 'prices')})
    else: call('POST', f'products/{pk}/variants/', body)
prod = call('GET', f'products/{pk}/')
by_sku = {v.get('sku'): v for v in prod['variants']}
extra = [v['id'] for v in prod['variants'] if v.get('sku') not in {b['sku'] for b in BUNDLES}]
if extra: raise SystemExit(f'unexpected extra variants on product {pk}: {extra}')
offers = {'pk': pk, 'variants': {b['key']: by_sku[b['sku']]['id'] for b in BUNDLES}}
(WORK / P.OFFERS_FILE).write_text(json.dumps(offers, indent=1))
cat_path = WORK / 'catalog-rb.json'
cat = json.loads(cat_path.read_text())
ids = [offers['variants'][b['key']] for b in BUNDLES]
cat['mapping']['products'][HANDLE] = {'id': pk, 'variants': ids, 'first_variant': ids[0], 'categories': prod.get('categories', [])}
cat_path.write_text(json.dumps(cat, indent=1, ensure_ascii=False))
print(json.dumps(offers))
