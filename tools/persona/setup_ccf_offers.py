"""Adaptive Peptide Foundation offer structure on NEXT. Idempotent.

usage: NEXT_API_TOKEN=... python3 -I setup_ccf_offers.py <store_subdomain> <out.json>
- the foundation (product 14) is one adaptive shade for every skin tone, sold in two packs (ccf_copy.PACKS):
  1 bottle ($47, or $37 with Automatic Refills) and 2 bottles + free gifts ($57, or $47 with refills); the retail
  price is the compare-at price, and the subscription price is what each refill costs
- refills ship every 28 days (ccf_copy.REFILL); the customer opts in on the product page, one-time is the default
- the Duo / Complexion Set bundles from the first offer structure stay hidden (focus_catalog.py); they are only
  looked up, never re-created, so their pks stay stable
Writes the product / variant pks the theme's offer picker needs.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ccf_copy import PACKS, REFILL

STORE, OUT = sys.argv[1], sys.argv[2]
API = f'https://{STORE}.29next.store/api/admin/'
TOKEN = os.environ['NEXT_API_TOKEN']
CCF = 14
ATTR = 'Pack'

def call(method, path, body=None):
    for attempt in range(4):
        req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method=method,
                                     headers={'Authorization': f'Bearer {TOKEN}', 'X-29next-API-Version': '2024-04-01',
                                              'Content-Type': 'application/json', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read(); return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3: time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f'{method} {path} -> {e.code}: {e.read()[:600].decode("utf-8", "replace")}')

def price(p, retail=None, sub=None):
    d = {'currency': 'USD', 'price': p, 'retail': retail}   # retail None clears an old compare-at price
    if sub: d['subscription'] = sub
    return [d]

def attr_value(v):
    vals = v.get('attributes') or v.get('variant_attribute_values') or []
    return vals[0]['value'] if vals else None

def variant_body(pack):
    return {'sku': pack['sku'], 'variant_attribute_values': [{'name': ATTR, 'value': pack['variant']}],
            'prices': price(pack['price'], pack['compare'], pack['refill']),
            'track_stock': False, 'allow_backorders': True, 'requires_shipping': True,
            'stockrecords': [{'location_id': 1, 'num_in_stock': 1000, 'low_stock_threshold': 0}]}

out = {}
# 1. the foundation: one shade, two packs, each with its refill price, refills every 28 days
call('PATCH', f'products/{CCF}/', {'variant_attributes': [{'name': ATTR, 'values': [p['variant'] for p in PACKS]}],
                                     'enable_subscription': True, 'interval': REFILL['interval'], 'interval_counts': [REFILL['every']]})
prod = call('GET', f'products/{CCF}/')
# variants are matched by SKU first (re-runs), then reused in order (the old base variants 15 and 103), then created
by_sku = {v.get('sku'): v for v in prod['variants']}
spare = [v for v in sorted(prod['variants'], key=lambda v: v['id']) if v.get('sku') not in {p['sku'] for p in PACKS}]
for pack in PACKS:
    body = variant_body(pack)
    v = by_sku.get(pack['sku']) or (spare.pop(0) if spare else None)
    if v: call('PATCH', f"products/variants/{v['id']}/", {k: body[k] for k in ('sku', 'variant_attribute_values', 'prices')})
    else: call('POST', f'products/{CCF}/variants/', body)
if spare: raise SystemExit(f'unexpected extra variants on product {CCF}: {[v["id"] for v in spare]}')
prod = call('GET', f'products/{CCF}/')
by_sku = {v.get('sku'): v for v in prod['variants']}
out['foundation'] = {'pk': CCF, 'variants': {p['key']: by_sku[p['sku']]['id'] for p in PACKS}}

def all_products():
    out, url = [], 'products/?page_size=100'
    while url:
        page = call('GET', url); out += page['results']
        nxt = page.get('next'); url = nxt.split('/api/admin/', 1)[1] if nxt else None
    return {p['slug']: p for p in out}

# 2/3. the hidden bundle products (matched by their first slug or the one focus_catalog.py renamed them to)
RENAMED = {'color-changing-foundation-duo': 'adaptive-peptide-foundation-duo'}
existing = all_products()
for slug in ('color-changing-foundation-duo', 'complexion-set'):
    found = existing.get(slug) or existing.get(RENAMED.get(slug, ''))
    if not found: continue
    full = call('GET', f"products/{found['id']}/")
    out[slug] = {'pk': full['id'], 'variants': {attr_value(v): v['id'] for v in full['variants']}}
json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False))
