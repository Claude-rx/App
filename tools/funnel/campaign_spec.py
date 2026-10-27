"""Write the funnel's CampaignSpec (campaigns/skinofab/campaign-spec.json) from funnel.py and the live campaign.

usage: python3 -I tools/funnel/campaign_spec.py [--read <campaign-read.json>]

The commerce values are never typed: they come from one read of the campaign through NEXT's public proxy
(https://campaign-map.nextcommerce.com/api/campaign, header X-Campaign-Key), the read Campaigns OS doctor and QA
repeat (docs/build-packet.md, "Reading package, offer and shipping refs"). The key is the campaign's public
Campaigns API key, read from the Page Kit config.js; it is not written to the spec. --read takes a saved read
instead (for an offline rebuild). curl makes the request because it honours the session's proxy settings.

The spec is a local spec (spec_identity.local_spec_id, no saved Map): Campaigns OS keeps its verdicts local.
"""
import json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funnel as F

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'campaigns' / 'skinofab'
CONFIG_JS = PROJECT / 'src' / F.SLUG / 'assets' / 'config.js'
OUT = PROJECT / 'campaign-spec.json'
PROXY = 'https://campaign-map.nextcommerce.com/api/campaign'
STORE_FIELDS = {
    'store_url': F.STORE, 'store_name': 'SKINOFAB',
    'store_contact': f'{F.STORE}/contact/', 'store_terms': f'{F.STORE}/terms-of-service/',
    'store_shipping': f'{F.STORE}/shipping-policy/', 'store_privacy': f'{F.STORE}/privacy-policy/',
    'store_returns': f'{F.STORE}/refund-policy/', 'store_phone': None, 'store_phone_tel': None,
}
PACKAGE_KEYS = ['ref_id', 'name', 'qty', 'price', 'price_retail', 'image', 'product_name', 'product_sku',
                'product_variant_name', 'product_purchase_availability', 'product_inventory_availability',
                'is_recurring', 'price_recurring', 'interval', 'interval_count']


def public_key():
    m = re.search(r"apiKey:\s*['\"]([^'\"]+)['\"]", CONFIG_JS.read_text())
    if not m: sys.exit(f'no apiKey in {CONFIG_JS}')
    return m.group(1)


def read_campaign(saved=None):
    if saved: body = json.loads(Path(saved).read_text())
    else:
        out = subprocess.run(['curl', '-sS', '-m', '60', '-H', 'Accept: application/json', '-H',
                              f'X-Campaign-Key: {public_key()}', f'{PROXY}?ref_id={F.CAMPAIGN_REF}'],
                             capture_output=True, text=True, check=True).stdout
        body = json.loads(out)
    if not body.get('ok'): sys.exit(f"campaign read failed: {body.get('status')} {body.get('error')}")
    data = body['data']
    if isinstance(data, list): data = next(c for c in data if c['id'] == F.CAMPAIGN_REF)
    if data['id'] != F.CAMPAIGN_REF: sys.exit(f"the key serves campaign {data['id']}, not {F.CAMPAIGN_REF}")
    return data


def spec(c):
    pkgs = {p['ref_id']: p for p in c['packages']}
    offers = {o['ref_id']: o for o in c['offers']}

    def package(ref, **flags):
        p = {k: pkgs[ref].get(k) for k in PACKAGE_KEYS if k in pkgs[ref]}
        return {**p, 'is_upsell': False, 'is_order_bump': False, 'default_selected': False, **flags}

    pages = []
    for i, pg in enumerate(F.PAGES, 1):
        page = {'id': pg['id'], 'type': pg['type'], 'order': i, 'label': pg['label'], 'is_entry': bool(pg.get('entry')),
                'page_url': pg['file'] + '/', 'sdk_hints': {'sdk_page_type': pg['sdk'], 'meta_tags': F.meta_tags(pg),
                                                            'template_family': 'apollo'}}
        routing = {}
        if pg.get('next'):
            page['next_page'] = pg['next']; routing.update(next_page=pg['next'], next_page_route=F.route(pg['next']))
        if pg.get('success'):
            page['success_url'] = pg['success']; routing.update(success=pg['success'], success_route=F.route(pg['success']))
        if pg.get('accept'):
            page['on_accept'], page['on_decline'] = pg['accept'], pg['decline']
            routing.update(accept=pg['accept'], accept_route=F.route(pg['accept']),
                           decline=pg['decline'], decline_route=F.route(pg['decline']))
        if routing: page['resolved_routing'] = routing
        if pg['type'] == 'checkout':
            page['packages'] = [package(r, default_selected=r == pg['default_package']) for r in pg['packages']]
            page['exit_intent'] = {'enabled': True, 'offer_ref_id': pg['exit_offer'], 'offer_code': offers[pg['exit_offer']]['code'],
                                   'notes': 'Once per visit, on leaving the checkout: 10% off the stick packs.'}
            page['offers'] = [{'ref_id': pg['exit_offer']}]
        if pg['type'] == 'upsell':
            page['packages'] = [package(pg['package'], is_upsell=True, default_selected=True)]
            page['offers'] = [{'ref_id': pg['offer']}]
        if pg['type'] in ('presell', 'landing'):
            # the product page links each pack to the checkout (?forceBundleId=); neither page writes the cart
            page['packages'] = [package(r) for r in BY_CHECKOUT['packages']]
        pages.append(page)

    return {
        'schema_version': '5.0',
        'spec_identity': {'source': 'hand-authored', 'local_spec_id': F.LOCAL_SPEC_ID, 'public_route_slug': F.SLUG,
                          'template_family': 'apollo', 'authority': 'tools/funnel/funnel.py + the live campaign read'},
        'campaign': {'ref_id': c['id'], 'name': c['name'], 'currency': c['currency'], 'language': c['language'],
                     'payment_env_key': c.get('payment_env_key'),
                     'available_payment_methods': c.get('available_payment_methods', []),
                     'available_express_payment_methods': c.get('available_express_payment_methods', []),
                     'available_currencies': c.get('available_currencies', []),
                     'available_shipping_countries': c.get('available_shipping_countries', []),
                     'preferred_template_family': 'apollo', **STORE_FIELDS},
        'global_config': {'sdk_version': SDK_VERSION},
        'funnels': [{'id': 'stick', 'name': 'Foundation Stick: listicle to thank you', 'weight': 100, 'pages': pages}],
        'offers': [offers[k] for k in sorted(offers)],
        'shipping_methods': [{k: s.get(k) for k in ('ref_id', 'code', 'price')} for s in c['shipping_methods']],
    }


BY_CHECKOUT = F.BY_ID['checkout']
SDK_VERSION = json.loads((PROJECT / '_data' / 'campaigns.json').read_text())[F.SLUG]['sdk_version']

if __name__ == '__main__':
    saved = sys.argv[sys.argv.index('--read') + 1] if '--read' in sys.argv else None
    s = spec(read_campaign(saved))
    OUT.write_text(json.dumps(s, indent=2, ensure_ascii=False) + '\n')
    pk = sum(len(p.get('packages', [])) for p in s['funnels'][0]['pages'])
    print(f"{OUT.relative_to(ROOT)}: {len(s['funnels'][0]['pages'])} pages, {pk} page packages, {len(s['offers'])} offers")
