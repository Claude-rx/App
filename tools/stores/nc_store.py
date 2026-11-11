#!/usr/bin/env python3
"""Connect to a Next Commerce store's Admin API and audit it for funnel readiness. Read-only.

usage:
  MEDICLAB_ADMIN_TOKEN=... python3 -I tools/stores/nc_store.py check  <store>
  MEDICLAB_ADMIN_TOKEN=... python3 -I tools/stores/nc_store.py audit  <store> [--json OUT] [--md OUT]

<store> is a key of tools/stores/stores.json (e.g. mediclab). The token comes from the env var that
store names (`token_env`), falling back to $NEXT_API_TOKEN. It is never printed or written to disk;
the audit snapshot also drops secret fields (webhook secret keys, payment environment keys).

Exit codes: 0 = connected (check) / no blockers (audit), 1 = blockers found, 2 = cannot connect.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(HERE, 'stores.json')
SECRET_KEYS = {'secret_key', 'environment_key', 'certificate_token', 'api_key', 'token', 'password'}
EXAMPLE_SKUS = {'DEMO-SKU-123'}


class ApiError(Exception):
    def __init__(self, status, path):
        super().__init__(f'HTTP {status} on {path}')
        self.status = status


def load_store(key, registry=REGISTRY):
    with open(registry) as f:
        stores = json.load(f)
    if key not in stores or key.startswith('_'):
        known = ', '.join(k for k in stores if not k.startswith('_'))
        sys.exit(f'unknown store "{key}" (known: {known})')
    return stores[key]


def token_for(store, env=os.environ):
    return env.get(store['token_env']) or env.get('NEXT_API_TOKEN') or ''


class Client:
    def __init__(self, base_url, token, api_version='2024-04-01', timeout=30):
        self.base = base_url.rstrip('/') + '/api/admin/'
        self.headers = {'Authorization': 'Bearer ' + token, 'X-29next-API-Version': api_version,
                        'Accept': 'application/json', 'User-Agent': 'nc-store-audit/1.0'}
        self.timeout = timeout

    def get(self, path):
        url = self.base + path.lstrip('/')
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                body = r.read()
                if 'json' not in (r.headers.get('Content-Type') or ''):
                    raise ApiError(r.status, path)
                return json.loads(body)
        except urllib.error.HTTPError as e:
            raise ApiError(e.code, path) from None

    def list_all(self, path, cap=1000):
        out, url = [], path + ('&' if '?' in path else '?') + 'limit=100'
        while url and len(out) < cap:
            page = self.get(url)
            out.extend(page.get('results', []))
            nxt = page.get('next')
            url = nxt.split('/api/admin/', 1)[1] if nxt else None
        return out


def scrub(obj):
    if isinstance(obj, dict):
        return {k: ('***' if k in SECRET_KEYS and v else scrub(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub(x) for x in obj]
    return obj


def snapshot(client):
    snap = {'store': client.get('store/')}
    for key, path in [('products', 'products/'), ('categories', 'categories/'), ('campaigns', 'campaigns/'),
                      ('gateways', 'gateways/'), ('shipping_methods', 'shipping-methods/'),
                      ('locations', 'locations/'), ('themes', 'themes/'), ('pages', 'pages/'),
                      ('webhooks', 'webhooks/'), ('orders', 'orders/'), ('subscriptions', 'subscriptions/')]:
        try:
            snap[key] = client.list_all(path, cap=200 if key in ('orders', 'subscriptions') else 1000)
        except ApiError as e:
            snap[key] = {'error': str(e)}
    for p in snap.get('pages') or []:
        if isinstance(p, dict):
            p.pop('content', None)
    return scrub(snap)


def _ok(v):
    return isinstance(v, list)


def evaluate(snap):
    """Return a list of checks: (level, area, message). level is BLOCKER, WARN or OK."""
    c = []
    st = snap.get('store', {})
    addr = st.get('contact_address') or {}
    if not (addr.get('line1') and addr.get('city') and addr.get('country')):
        c.append(('BLOCKER', 'store', 'Business contact address is empty (needed on checkout, receipts, policies and by gateways)'))
    else:
        c.append(('OK', 'store', f"Contact address: {addr.get('city')}, {addr.get('country')}"))
    if not addr.get('phone_number'):
        c.append(('WARN', 'store', 'No support phone number on the store'))
    if not st.get('primary_domain'):
        c.append(('WARN', 'store', 'No primary domain connected (store runs on *.29next.store)'))
    else:
        c.append(('OK', 'store', f"Primary domain: {st['primary_domain']}"))

    prods = snap.get('products')
    if _ok(prods):
        real = [p for p in prods if not all(v.get('sku') in EXAMPLE_SKUS for v in p.get('variants', [])) and p.get('slug') != 'example-product']
        demo = len(prods) - len(real)
        if not real:
            c.append(('BLOCKER', 'catalog', 'No real products, only the demo "Example Product". Create the Mediclab products before a campaign can sell them'))
        else:
            c.append(('OK', 'catalog', f'{len(real)} real product(s)'))
            noimg = [p['title'] for p in real if not p.get('images')]
            if noimg:
                c.append(('WARN', 'catalog', f'Products without images: {", ".join(noimg[:5])}'))
            noprice = [p['title'] for p in real for v in p.get('variants', []) if not v.get('prices')]
            if noprice:
                c.append(('BLOCKER', 'catalog', f'Variants without a price: {", ".join(noprice[:5])}'))
        if demo:
            c.append(('WARN', 'catalog', f'{demo} demo product(s) still public; delete or unpublish before launch'))

    gws = snap.get('gateways')
    if _ok(gws):
        live = [g for g in gws if g.get('is_active', g.get('active', True))]
        if not live:
            c.append(('BLOCKER', 'payments', 'No payment gateway configured (Dashboard > Settings > Payments). Checkout cannot take money'))
        else:
            c.append(('OK', 'payments', f'{len(live)} active gateway(s)'))
    express = (st.get('payments') or {}).get('available_express_payment_methods') or []
    if not express:
        c.append(('WARN', 'payments', 'No express methods (Apple Pay / Google Pay / PayPal) available'))

    ship = snap.get('shipping_methods')
    if _ok(ship):
        if not ship:
            c.append(('BLOCKER', 'shipping', 'No shipping methods'))
        else:
            for m in ship:
                price = ', '.join(f"{p['price_per_order']} {p['currency']}" for p in m.get('prices', []))
                c.append(('OK' if m.get('countries') else 'WARN', 'shipping',
                          f"#{m['id']} {m['name']} ({price})" + ('' if m.get('countries') else ': no countries restricted (ships everywhere)')))

    locs = snap.get('locations')
    if _ok(locs) and locs and not any(l.get('address') for l in locs):
        c.append(('WARN', 'fulfillment', 'Fulfillment location has no address and no callback URL (no 3PL connected yet)'))

    camps = snap.get('campaigns')
    if _ok(camps):
        if not camps:
            c.append(('BLOCKER', 'campaigns', 'No campaign in the Campaigns App: the funnel needs one (packages, offers, shipping, API key)'))
        else:
            c.append(('OK', 'campaigns', f'{len(camps)} campaign(s): ' + ', '.join(f"#{x.get('id')} {x.get('name')}" for x in camps[:5])))

    themes = snap.get('themes')
    if _ok(themes) and not themes:
        c.append(('WARN', 'storefront', 'No storefront theme installed (fine for a standalone Page Kit funnel)'))

    for k in ('products', 'gateways', 'campaigns', 'shipping_methods'):
        v = snap.get(k)
        if isinstance(v, dict) and 'error' in v:
            c.append(('WARN', k, f'Could not read: {v["error"]} (token scope?)'))
    return c


def render_md(store, snap, checks, when):
    st = snap['store']
    lines = [f"# {store['name']} store: funnel readiness", '',
             f"Store `{store['base_url']}` · audited {when} · `python3 -I tools/stores/nc_store.py audit {store['subdomain']}`", '',
             '| Level | Area | Finding |', '|---|---|---|']
    order = {'BLOCKER': 0, 'WARN': 1, 'OK': 2}
    for lvl, area, msg in sorted(checks, key=lambda x: order[x[0]]):
        lines.append(f'| {"**BLOCKER**" if lvl == "BLOCKER" else lvl} | {area} | {msg.replace("|", "/")} |')
    counts = {k: (len(v) if isinstance(v, list) else 'n/a') for k, v in snap.items() if k != 'store'}
    lines += ['', '## Inventory', '', '| Object | Count |', '|---|---|']
    lines += [f'| {k} | {v} |' for k, v in counts.items()]
    lines += ['', f"Currencies: {', '.join(c['code'] for c in st.get('available_currencies', []))} · "
              f"Languages: {', '.join(l['code'] for l in st.get('available_languages', []))} · Timezone: {st.get('timezone')}", '']
    return '\n'.join(lines)


def main(argv):
    if len(argv) < 3 or argv[1] not in ('check', 'audit'):
        sys.exit(__doc__)
    cmd, key = argv[1], argv[2]
    store = load_store(key)
    tok = token_for(store)
    if not tok:
        print(f'{store["token_env"]} is not set', file=sys.stderr)
        return 2
    client = Client(store['base_url'], tok, store.get('api_version', '2024-04-01'))
    try:
        info = client.get('store/')
    except (ApiError, urllib.error.URLError) as e:
        print(f'cannot connect to {store["base_url"]}: {e}', file=sys.stderr)
        return 2
    if cmd == 'check':
        print(f"connected: {info.get('name')} ({store['base_url']}) · currencies "
              f"{','.join(c['code'] for c in info.get('available_currencies', []))} · tz {info.get('timezone')}")
        return 0
    snap = snapshot(client)
    checks = evaluate(snap)
    when = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    args = argv[3:]
    if '--json' in args:
        with open(args[args.index('--json') + 1], 'w') as f:
            json.dump({'audited_at': when, 'store': key, 'checks': checks, 'snapshot': snap}, f, indent=2)
    md = render_md(store, snap, checks, when)
    if '--md' in args:
        with open(args[args.index('--md') + 1], 'w') as f:
            f.write(md)
    print(md)
    return 1 if any(c[0] == 'BLOCKER' for c in checks) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
