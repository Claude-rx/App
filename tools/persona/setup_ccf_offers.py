"""Color Changing Foundation offer structure on NEXT (from the 45+ persona report, section 10). Idempotent.

usage: NEXT_API_TOKEN=... python3 -I setup_ccf_offers.py <store_subdomain> <out.json>
- Color Changing Foundation (product 14): two adaptive bases (Light-Medium, Medium-Deep), sold as a
  month-to-month refill (ccf_copy.SUBSCRIPTION: $33 every 1 month); the $39 list price stays on the variants
  but the theme never sells it one-time (Theme settings > Subscription Offer)
- Color Changing Foundation Duo / Complexion Set: created for the first offer structure; now hidden by
  focus_catalog.py (subscription only), kept so their pks stay stable
Writes the product / variant pks the theme's offer picker needs.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ccf_copy import SUBSCRIPTION as SUB

STORE, OUT = sys.argv[1], sys.argv[2]
API = f'https://{STORE}.29next.store/api/admin/'
TOKEN = os.environ['NEXT_API_TOKEN']
CCF = 14
LM, MD = 'Light–Medium', 'Medium–Deep'

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

def variant_body(sku, base, prices):
    return {'sku': sku, 'variant_attribute_values': [{'name': 'Base', 'value': base}], 'prices': prices,
            'track_stock': False, 'allow_backorders': True, 'requires_shipping': True,
            'stockrecords': [{'location_id': 1, 'num_in_stock': 1000, 'low_stock_threshold': 0}]}

out = {}
# 1. the foundation: bases + list price + the month-to-month plan
call('PATCH', f'products/{CCF}/', {'variant_attributes': [{'name': 'Base', 'values': [LM, MD]}],
                                     'enable_subscription': True, 'interval': SUB['interval'], 'interval_counts': [SUB['every']]})
prod = call('GET', f'products/{CCF}/')
by_base = {attr_value(v): v for v in prod['variants']}
first = prod['variants'][0]
if LM not in by_base:
    call('PATCH', f"products/variants/{first['id']}/", {'sku': 'SKF-CCF-LM', 'variant_attribute_values': [{'name': 'Base', 'value': LM}]})
call('PATCH', f"products/variants/{(by_base.get(LM) or first)['id']}/", {'prices': price('39.00', sub=SUB['price'])})
if MD not in by_base:
    call('POST', f'products/{CCF}/variants/', variant_body('SKF-CCF-MD', MD, price('39.00', sub=SUB['price'])))
prod = call('GET', f'products/{CCF}/')
out['foundation'] = {'pk': CCF, 'variants': {attr_value(v): v['id'] for v in prod['variants']}}

# 2/3. bundle products (matched by slug)
def all_products():
    out, url = [], 'products/?page_size=100'
    while url:
        page = call('GET', url); out += page['results']
        nxt = page.get('next'); url = nxt.split('/api/admin/', 1)[1] if nxt else None
    return {p['slug']: p for p in out}

cats = [c['id'] if isinstance(c, dict) else c for c in prod.get('categories') or []]
# matched by their first slug or the one focus_catalog.py renamed them to, so a re-run never creates a duplicate
RENAMED = {'color-changing-foundation-duo': 'adaptive-peptide-foundation-duo'}
BUNDLES = [
    ('color-changing-foundation-duo', 'Color Changing Foundation Duo', '64.00', '78.00',
     ['2 × ' + LM, '2 × ' + MD, '1 of each'],
     '<p>Two bottles of the color-adapting serum foundation made for skin after 45. Keep one at home and one in your bag, or pick one of each base.</p>'),
    ('complexion-set', 'Complexion Set', '79.00', '97.00', [LM, MD],
     "<p>The Color Changing Foundation in your base, the Liquid Blender Brush that sweeps it on in a minute, and the Under-Eye Reset Patches for the area foundation alone can't fix.</p>"),
]
def find(existing, slug):
    return existing.get(slug) or existing.get(RENAMED.get(slug, ''))

existing = all_products()
for slug, title, p, retail, bases, desc in BUNDLES:
    if not find(existing, slug):
        call('POST', 'products/', {'title': title, 'slug': slug, 'description': desc, 'is_public': True, 'categories': cats,
                                   'variant_attributes': [{'name': 'Base', 'values': bases}],
                                   'variants': [variant_body(f'SKF-{slug.upper()[:20]}-{i + 1}', b, price(p, retail))
                                                for i, b in enumerate(bases)]})
existing = all_products()
for slug, *_ in BUNDLES:
    full = call('GET', f"products/{find(existing, slug)['id']}/")
    out[slug] = {'pk': full['id'], 'variants': {attr_value(v): v['id'] for v in full['variants']}}
json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False))
