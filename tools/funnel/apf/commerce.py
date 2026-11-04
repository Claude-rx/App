"""The Adaptive Peptide Foundation funnel's commerce in campaign 2211, idempotent: the store variants its packs need, one
one-time package per pack, and the vouchers its offers apply. Prints what it finds or creates; writes nothing but the
store. The Admin token comes from $NEXT_API_TOKEN and is never printed.

usage: NEXT_API_TOKEN=... python3 -I tools/funnel/apf/commerce.py [--dry-run] [--variants-only] [--verify]

The campaign is the funnel's own, 2221 "SKINOFAB Adaptive Peptide Foundation Funnel" (created 28 Oct 2026 by the
next-campaigns-create skill from next-campaigns-create-runs/skinofab-apf/campaign-plan.json, which also verified every
price; this script finds those packages and offers in place and creates nothing twice). Its Allowed Domains
(try.skinofab.com) are a dashboard setting. The three main packs are subscriptions since 29 Oct 2026 (the owner:
"make sure all is subscription"; renewals at the same price every 28 days a bottle: 1 bottle every 28, 2 bottles every
56, 3 bottles every 84; the free gifts ship with the first order only, which fulfilment is told); the post-purchase
offers stay one-time. Their recurrence and the add-on package are set through the next-campaigns-create plan
(next-campaigns-create-runs/skinofab-apf/), which owns the campaign; this script only makes the store variants they
need (--variants-only) and verifies prices. A campaign takes one package per store variant:
- the store's own "1 bottle" (15) and "2 bottles + free gifts" (103) carry the funnel's first two packs at the
  funnel's prices (a package's price is the campaign's, not the store's);
- the 3-bottle pack, the offer-1 packs (2 bottles; 6 bottles + free brush) are new variants of product 14, named for
  what the warehouse packs, with the store's $47 for one bottle times the bottles as their compare-at;
- the brush's variant 170 is already package 3 (the stick funnel's, recurring every 90 days), so the one-time brush
  offer gets its own variant on product 169, "1 brush + free travel case", the same contents.
Vouchers are percentages off one package, rounded down to the dollar (the campaign's convention), named as the order
summary shows them.
--verify prices every pack and offer through the Cart API (campaigns.apps.29next.com, the public campaign key from the
funnel's config.js) and compares with the prices the pages state (funnels/apf.py).
"""
import json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'funnel'))
STORE = 'https://skinofab.29next.store'
CAMPAIGN = 2221
API = STORE + '/api/admin/'
CART = 'https://campaigns.apps.29next.com/api/v1/carts/calculate/'
DRY = '--dry-run' in sys.argv
HDR = {'Authorization': 'Bearer ' + os.environ.get('NEXT_API_TOKEN', ''), 'X-29next-API-Version': '2024-04-01',
       'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'skinofab-funnel/1'}
FOUNDATION, BRUSH = 14, 169
LIST_PRICE = 47.00                       # what the store charges for one bottle, bought once

# the store variants the funnel's packs need (variant attribute "Pack" on the foundation, "Bundle" on the brush)
VARIANTS = {
    FOUNDATION: [
        {'sku': 'SKF-APF-3-GIFTS', 'value': '3 bottles + free gifts + free Lymphatic Brush', 'price': '75.00', 'retail': '177.00'},
        {'sku': 'SKF-APF-2', 'value': '2 bottles', 'price': '39.00', 'retail': '118.00'},
        {'sku': 'SKF-APF-6-BRUSH', 'value': '6 bottles + free Lymphatic Brush', 'price': '99.00', 'retail': '354.00'},
        # offers 2 and 2b's one more bottle, bought once: the main 1-bottle pack (variant 15) is a subscription now, and a
        # campaign takes one package per variant
        {'sku': 'SKF-APF-1-ADD', 'value': '1 bottle (add-on)', 'price': '39.00', 'retail': '47.00'},
        # the 30 Oct 2026 offer (the owner): Buy 2 Get 1 Free with the Blender, Buy 3 Get 2 Free with the Lymphatic Brush
        {'sku': 'SKF-APF-3-BLENDER', 'value': '3 bottles + free Blender', 'price': '66.97', 'retail': '141.00'},
        {'sku': 'SKF-APF-5-BRUSH', 'value': '5 bottles + free Lymphatic Brush', 'price': '99.97', 'retail': '235.00'},
    ],
    BRUSH: [
        {'sku': 'SKF-LYB-1T', 'value': '1 brush + free travel case', 'price': '24.95', 'retail': '24.95'},
    ],
}
# the packages: key -> (product, variant sku, campaign price); the name is the product's (the API appends the variant)
PACKAGES = [
    ('apf-1', FOUNDATION, 'SKF-APF-1', '33.97'),
    ('apf-3-blender', FOUNDATION, 'SKF-APF-3-BLENDER', '66.97'),       # Buy 2 Get 1 Free: under 2 x $33.97
    ('apf-5-brush', FOUNDATION, 'SKF-APF-5-BRUSH', '99.97'),           # Buy 3 Get 2 Free: under 3 x $33.97, $19.99 a bottle
    ('apf-2', FOUNDATION, 'SKF-APF-2', '39.00'),
    ('apf-6-brush', FOUNDATION, 'SKF-APF-6-BRUSH', '99.00'),
    ('brush-1', BRUSH, 'SKF-LYB-1T', '24.95'),
    ('apf-1-add', FOUNDATION, 'SKF-APF-1-ADD', '33.97'),
    # the packs before 30 Oct 2026 ($57 and $75, packages 2 and 3) were deleted on 1 Nov 2026 with the owner's approval,
    # after checking that no subscription renews on them; their variants stay in the catalogue for the earlier orders
]
# the vouchers: code -> (name as the order summary, the receipt and the order emails show it, % off, package keys). The
# offers' names say the price she pays, not the voucher's percentage: rounded down to the dollar, 40% off $39 is $23,
# which the page rightly calls 41% off, and a receipt line "40% off" contradicted it (live review 12)
OFFERS = [
    ('APF10', '10% off your foundation today', '10.00', ['apf-1', 'apf-3-blender', 'apf-5-brush']),
    # the add-on bottle is $33.97 since 30 Oct 2026, the checkout's own bottle: 44% off rounds down to $19, 55% to $15
    ('APF40', 'One more bottle at $19', '44.00', ['apf-1-add']),
    ('APF50', 'One more bottle at $15', '55.00', ['apf-1-add']),
    ('BRUSH40', 'Lymphatic Brush at $14', '40.00', ['brush-1']),
    ('BRUSH60', 'Lymphatic Brush at $9', '60.00', ['brush-1']),
]


def call(method, path, body=None, absolute=False):
    data = json.dumps(body).encode() if body is not None else None
    url = path if absolute else API + path
    for attempt in range(4):
        req = urllib.request.Request(url, data=data, method=method, headers=HDR)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3: time.sleep(2 ** (attempt + 1)); continue
            raise SystemExit(f'{method} {path}: {e.code} {e.read()[:400]!r}')
        except urllib.error.URLError:
            if attempt < 3: time.sleep(2 ** attempt); continue
            raise
        finally: time.sleep(0.3)         # the Admin API's 4 requests a second


def listing(path):
    out, nxt = [], path
    while nxt:
        res = call('GET', nxt)
        if isinstance(res, list): return out + res
        out += res.get('results', [])
        nxt = res.get('next'); nxt = nxt.split('/api/admin/', 1)[1] if nxt else None
    return out


def ensure_variants():
    """The store variants, by SKU; new ones are added to the product's attribute values and created."""
    by_sku = {}
    for pid, wanted in VARIANTS.items():
        prod = call('GET', f'products/{pid}/')
        attr = prod['variant_attributes'][0]
        have = {v['sku']: v for v in prod['variants']}
        values = list(attr['values'])
        for w in wanted:
            if w['sku'] in have: print(f'variant {w["sku"]:<18} exists  id {have[w["sku"]]["id"]}'); continue
            if w['value'] not in values: values.append(w['value'])
        if values != attr['values']:
            if DRY: print(f'would add attribute values on product {pid}: {values}')
            else: call('PATCH', f'products/{pid}/', {'variant_attributes': [{'name': attr['name'], 'values': values}]})
        for w in wanted:
            if w['sku'] in have: continue
            body = {'sku': w['sku'], 'variant_attribute_values': [{'name': attr['name'], 'value': w['value']}],
                    'prices': [{'currency': 'USD', 'price': w['price'], 'retail': w['retail']}],
                    'track_stock': False, 'allow_backorders': True, 'requires_shipping': True,
                    'stockrecords': [{'location_id': 1, 'num_in_stock': 1000, 'low_stock_threshold': 0}]}
            if DRY: print(f'would create variant {w["sku"]} on product {pid}: {w["value"]}'); continue
            call('POST', f'products/{pid}/variants/', body)      # (its answer is a list; the variant is read back by SKU)
            v = next(x for x in call('GET', f'products/{pid}/')['variants'] if x.get('sku') == w['sku'])
            have[w['sku']] = v
            print(f'variant {w["sku"]:<18} created id {v["id"]}')
        for v in call('GET', f'products/{pid}/')['variants']: by_sku[v['sku']] = v
    return by_sku


def ensure_packages(by_sku):
    live = listing(f'campaigns/{CAMPAIGN}/packages/')
    by_variant = {p['product_variant_id']: p for p in live}
    ids = {}
    for key, pid, sku, price in PACKAGES:
        if DRY and sku not in by_sku: print(f'would create package {key} ({sku}) at ${price}'); continue
        vid = by_sku[sku]['id']
        p = by_variant.get(vid)
        if p:
            got = next((x['price'] for x in p['prices'] if x['currency'] == 'USD'), None)
            if got != price:
                if DRY: print(f'would reprice package {p["id"]} {key}: ${got} -> ${price}')
                else: call('PATCH', f'campaigns/{CAMPAIGN}/packages/{p["id"]}/', {'prices': [{'currency': 'USD', 'price': price}]}); got = price
            print(f'package {p["id"]:>3} {key:<12} exists  {p["name"]}  ${got}' + ('  RECURRING' if p.get('is_recurring') else ''))
            ids[key] = p['id']; continue
        body = {'name': call('GET', f'products/{pid}/')['title'], 'product_id': pid, 'product_variant_ids': [vid], 'price': price}
        if DRY: print(f'would create package {key}: {body}'); continue
        res = call('POST', f'campaigns/{CAMPAIGN}/packages/', body)
        p = res[0] if isinstance(res, list) else res
        print(f'package {p["id"]:>3} {key:<12} created {p["name"]}  ${price}  image {"yes" if p.get("image") else "NONE"}')
        ids[key] = p['id']
    return ids


def ensure_offers(ids):
    live = {o['code']: o for o in listing(f'campaigns/{CAMPAIGN}/offers/') if o.get('code')}
    out = {}
    for code, name, pct, keys in OFFERS:
        want = {'name': name, 'offer_type': 'voucher', 'code': code,
                'condition': {'type': 'any', 'all_packages': False, 'package_ids': [ids[k] for k in keys if k in ids]},
                'benefit': {'type': 'package_percentage', 'value': pct, 'price_rounding': '0.00'}}
        o = live.get(code)
        if o:
            full = call('GET', f'campaigns/{CAMPAIGN}/offers/{o["id"]}/')
            got = sorted(p['id'] for p in full['condition'].get('packages', []))
            patch = {}
            if full['name'] != name: patch['name'] = name
            if float(full['benefit']['value']) != float(pct) or full['benefit'].get('price_rounding') != '0.00': patch['benefit'] = want['benefit']
            if got != sorted(want['condition']['package_ids']): patch['condition'] = want['condition']
            if patch and not DRY: call('PATCH', f'campaigns/{CAMPAIGN}/offers/{o["id"]}/', patch)
            print(f'offer {o["id"]:>3} {code:<8} exists  {pct}% off packages {got}' + (f'  patched {list(patch)}' if patch else ''))
            out[code] = o['id']; continue
        if DRY or len(want['condition']['package_ids']) != len(keys): print(f'would create offer {code}: {want}'); continue
        o = call('POST', f'campaigns/{CAMPAIGN}/offers/', want)
        print(f'offer {o["id"]:>3} {code:<8} created {pct}% off packages {want["condition"]["package_ids"]}')
        out[code] = o['id']
    return out


def verify(ids):
    """Every pack and offer priced by the Cart API, against funnels/apf.py's stated prices."""
    cfg = next(p for p in (ROOT / 'campaigns/skinofab/src/apf-funnel/assets/config.js', ROOT / 'campaigns/skinofab/src/stick-funnel/assets/config.js') if p.exists())
    key = re.search(r"apiKey:\s*'([^']+)'", cfg.read_text()).group(1)      # the same campaign's public key
    hdr = {'Authorization': key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    import funnels.apf as A
    ok = True
    def calc(lines, voucher=None, upsell=False):
        body = {'lines': lines, 'currency': 'USD'}
        if voucher: body['vouchers'] = [voucher]
        req = urllib.request.Request(CART + ('?upsell=true' if upsell else ''), data=json.dumps(body).encode(), method='POST', headers=hdr)
        with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())
    for pack in A.PACKS:
        res = calc([{'package_id': ids[pack['key']], 'quantity': 1}])
        total = float(res.get('total_incl_tax', res.get('total', 0)))
        flag = 'ok' if abs(total - pack['price']) < 0.005 else 'MISMATCH'
        if flag != 'ok': ok = False
        print(f'  calculate {pack["key"]:<12} ${total:.2f}  (page says ${pack["price"]:.2f})  {flag}')
    for off in A.OFFER_PAGES.values():
        for tier in off['tiers']:
            res = calc([{'package_id': ids[tier['package']], 'quantity': 1}], tier.get('voucher'), upsell=True)
            total = float(res.get('total_incl_tax', res.get('total', 0)))
            flag = 'ok' if abs(total - tier['price']) < 0.005 else 'MISMATCH'
            if flag != 'ok': ok = False
            print(f'  calculate {off["id"]:<22} {tier["package"]:<12} {str(tier.get("voucher") or ""):<8} ${total:.2f}  (page says ${tier["price"]:.2f})  {flag}')
    return ok


if __name__ == '__main__':
    if not os.environ.get('NEXT_API_TOKEN'): sys.exit('NEXT_API_TOKEN is not set')
    by_sku = ensure_variants()
    if '--variants-only' in sys.argv: sys.exit(0)
    ids = ensure_packages(by_sku)
    offers = ensure_offers(ids)
    print('packages', json.dumps(ids), 'offers', json.dumps(offers))
    if '--verify' in sys.argv and not verify(ids): sys.exit('prices differ from the pages')
