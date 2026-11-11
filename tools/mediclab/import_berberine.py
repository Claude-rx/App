"""Import MedicLab Berberine from the Mediclab Shopify store (mediclab.us) into the Next Commerce store
(mediclab.29next.store). Idempotent: finds the product by slug and the variants by SKU, creates only what is missing.

usage: MEDICLAB_ADMIN_TOKEN=... python3 -I tools/mediclab/import_berberine.py [--dry-run]

Source of truth is the public Shopify product JSON (https://mediclab.us/products/berberine.json): title, description,
SKU, price, weight and the 8 gallery images (downloaded from cdn.shopify.com and uploaded base64).

A Next campaign takes one package per store variant, and the funnel sells the same bottle two ways, so the product
carries two variants with the attribute "Purchase":
  JTP4BERB      "One-time purchase"     $52.97   (the Shopify variant; the one-bottle offer and the upsell)
  JTP4BERB-SUB  "Monthly refill plan"   $52.97   (the campaign package prices it $20.97 first, $42.97 every 30 days)
Both ship the same bottle; the warehouse packs JTP4BERB for either.
Writes tools/mediclab/berberine-ids.json (product and variant ids for the campaign plan). The token is never printed.
"""
import base64, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = 'https://mediclab.29next.store'
API = STORE + '/api/admin/'
SHOPIFY = 'https://mediclab.us/products/berberine.json'
DRY = '--dry-run' in sys.argv
TOKEN = os.environ.get('MEDICLAB_ADMIN_TOKEN') or os.environ.get('MEDICLAB_NEXT_ADMIN_API_TOKEN') or ''
HDR = {'Authorization': 'Bearer ' + TOKEN, 'X-29next-API-Version': '2024-04-01',
       'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'mediclab-import/1'}
SLUG = 'berberine'
ATTR = 'Purchase'
VARIANTS = [
    {'sku': 'JTP4BERB', 'value': 'One-time purchase', 'price': '52.97'},
    {'sku': 'JTP4BERB-SUB', 'value': 'Monthly refill plan', 'price': '52.97'},
]


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(4):
        req = urllib.request.Request(API + path, data=data, method=method, headers=HDR)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** (attempt + 1)); continue
            raise SystemExit(f'{method} {path}: {e.code} {e.read()[:600]!r}')
        finally:
            time.sleep(0.3)


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'mediclab-import/1'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def variant_body(v):
    return {'sku': v['sku'], 'variant_attribute_values': [{'name': ATTR, 'value': v['value']}],
            'prices': [{'currency': 'USD', 'price': v['price']}],
            'track_stock': False, 'allow_backorders': True, 'requires_shipping': True,
            'stockrecords': [{'location_id': 1, 'num_in_stock': 1000, 'low_stock_threshold': 0}]}


def main():
    if not TOKEN:
        sys.exit('MEDICLAB_ADMIN_TOKEN is not set')
    src = json.loads(fetch(SHOPIFY))['product']
    sv = src['variants'][0]
    assert sv['sku'] == 'JTP4BERB' and sv['price'] == '52.97', (sv['sku'], sv['price'])
    fields = {'title': src['title'], 'slug': SLUG, 'description': src['body_html'], 'is_public': True,
              'enable_subscription': True, 'interval': 'day', 'interval_counts': [30],
              'meta_title': 'MedicLab Berberine, 800 mg Extract, 60 Capsules',
              'meta_description': 'Berberine for healthy glucose metabolism. 800 mg extract per serving, 60 capsules. '
                                  'Made in the USA. 60-day empty-bottle guarantee.',
              'variant_attributes': [{'name': ATTR, 'values': [v['value'] for v in VARIANTS]}]}
    # Next re-slugs a product from its title, so the import finds its product by SKU, never by slug; a public product
    # wins over an unpublished one (product 7, a duplicate from the first re-run, is unpublished pending deletion)
    mine = [p for p in call('GET', 'products/?limit=100')['results']
            if any(v.get('sku') == 'JTP4BERB' for v in p.get('variants', []))]
    found = next((p for p in mine if p.get('is_public')), mine[0] if mine else None)
    if found:
        pk = found['id']
        print('product exists', pk)
    elif DRY:
        print('would create product', SLUG, 'with', [v['sku'] for v in VARIANTS]); return
    else:
        pk = call('POST', 'products/', {**fields, 'variants': [variant_body(v) for v in VARIANTS]})['id']
        print('created product', pk)
    prod = call('GET', f'products/{pk}/')
    have = {v['sku'] for v in prod['variants']}
    for v in VARIANTS:
        if v['sku'] in have: continue
        if DRY: print('would create variant', v['sku']); continue
        call('POST', f'products/{pk}/variants/', variant_body(v)); print('created variant', v['sku'])
    prod = call('GET', f'products/{pk}/')
    if not prod.get('images') and not DRY:
        for order, img in enumerate(src['images'][:10]):
            data = fetch(img['src'])
            name = img['src'].split('/')[-1].split('?')[0]
            call('POST', f'products/{pk}/images/', {'attachment': base64.b64encode(data).decode(), 'file_name': name,
                                                     'display_order': order, 'caption': img.get('alt') or src['title']})
            print('uploaded image', order, name)
        prod = call('GET', f'products/{pk}/')
    by_sku = {v['sku']: v for v in prod['variants']}
    ids = {'product_id': pk, 'title': prod['title'],
           'variants': {s: by_sku[s]['id'] for s in (v['sku'] for v in VARIANTS)},
           'images': [i.get('attachment') for i in prod.get('images', [])]}
    (HERE / 'berberine-ids.json').write_text(json.dumps(ids, indent=2) + '\n')
    print(json.dumps(ids, indent=2))


if __name__ == '__main__':
    main()
