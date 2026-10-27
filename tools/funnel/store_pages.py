"""Create (or update) the store pages that serve the funnel: one per funnel page, slug = template = its file name, so
<store>/<file>/ (on every store domain; the funnel's is funnel.FUNNEL_HOST) renders templates/pages/page.<file>.html
(deploy_theme.py).

usage: NEXT_API_TOKEN=... python3 -I tools/funnel/store_pages.py [--dry-run]

Idempotent: pages are matched by slug; an existing one only gets its template, title and meta fields set. The Admin
API token comes from the environment and is never printed or written anywhere.
"""
import json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funnel as F

API = F.STORE + '/api/admin/'
TITLES = {
    'listicle': ('10 Reasons Women Over 45 Look Fresher With This Shade-Adapting Foundation Stick',
                 'The foundation stick that goes on white and meets your own skin tone as you blend, with the brush built in.'),
    'offer': ('Adaptive Foundation Stick: choose your pack', 'One shade that adapts to fair to medium skin, brush built in. 30-day guarantee.'),
    'checkout': ('Secure checkout', 'Checkout for the Adaptive Foundation Stick.'),
    'special-1': ('Special offer 1', 'A one-time offer for your order.'),
    'special-2': ('Special offer 2', 'A one-time offer for your order.'),
    'special-3': ('Special offer 3', 'A one-time offer for your order.'),
    'special-4': ('Special offer 4', 'A one-time offer for your order.'),
    'thank-you': ('Thank you', 'Your order is confirmed.'),
}


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(4):
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            'Authorization': 'Bearer ' + os.environ['NEXT_API_TOKEN'], 'X-29next-API-Version': '2024-04-01',
            'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'skinofab-funnel/1'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt < 3: time.sleep(2 ** attempt); continue
            raise SystemExit(f'{method} {path}: {e.code} {e.read()[:300]!r}')
        except urllib.error.URLError:
            if attempt < 3: time.sleep(2 ** attempt); continue
            raise


def all_pages():
    out, path = [], 'pages/?limit=100'
    while path:
        res = call('GET', path)
        out += res['results']
        nxt = res.get('next')
        path = nxt.split('/api/admin/', 1)[1] if nxt else None
    return {p['slug']: p for p in out}


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    have = all_pages()
    for pg in F.PAGES:
        slug = pg['file']
        title, desc = TITLES[pg['id']]
        body = {'title': title, 'slug': slug, 'template': slug, 'meta_title': title + ' | SKINOFAB', 'meta_description': desc}
        cur = have.get(slug)
        if cur and all(str(cur.get(k)) == str(v) for k, v in body.items()):
            print('ok     ', F.FUNNEL_HOST + F.route(pg['id'], served=True)); continue
        if dry: print('would', 'update' if cur else 'create', slug); continue
        if cur: call('PATCH', f"pages/{cur['id']}/", {k: v for k, v in body.items() if k != 'slug'})
        else: call('POST', 'pages/', {**body, 'content': '<p>Rendered by the theme template.</p>'})
        print('updated' if cur else 'created', F.FUNNEL_HOST + F.route(pg['id'], served=True))
