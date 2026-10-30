"""Rename Smooche -> SKINOFAB in the NEXT store data (Admin API 2024-04-01).

usage: NEXT_API_TOKEN=... python3 -I migrate_next.py <store_subdomain> [--apply]
Dry run by default (prints the planned PATCHes). Touches only text fields that contain the old brand:
products (title, slug, template, description, meta), categories (name, slug, description), pages (title, slug,
template, content, meta). Slugs/templates follow the theme's renamed handles (smooche-blender -> skinofab-blender,
about-smooche -> about-skinofab), so page.html's slug dispatch and product.<handle>.html templates keep resolving.
"""
import json, os, re, sys, time, urllib.request, urllib.error

STORE, APPLY = sys.argv[1], '--apply' in sys.argv
API = f'https://{STORE}.29next.store/api/admin/'
TOKEN = os.environ['NEXT_API_TOKEN']
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)
def brand(m):
    s = m.group(0)
    return 'SKINOFAB' if s.isupper() else ('Skinofab' if s[0].isupper() else 'skinofab')

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
            raise RuntimeError(f'{method} {path} -> {e.code}: {e.read()[:400].decode("utf-8", "replace")}')

def list_all(path):
    out, url = [], f'{path}?page_size=100'
    while url:
        page = call('GET', url); out += page.get('results', [])
        nxt = page.get('next'); url = nxt.split('/api/admin/', 1)[1] if nxt else None
    return out

plan = []
def patch(kind, path, obj, fields):
    body = {f: BRAND.sub(brand, obj[f]) for f in fields if isinstance(obj.get(f), str) and BRAND.search(obj[f])}
    if body: plan.append((kind, path, body))

for p in list_all('products/'):
    full = call('GET', f"products/{p['id']}/")
    patch('product', f"products/{p['id']}/", full, ('title', 'slug', 'template', 'description', 'meta_title', 'meta_description'))
for c in list_all('categories/'):
    patch('category', f"categories/{c['id']}/", c, ('name', 'slug', 'description', 'meta_title', 'meta_description'))
for pg in list_all('pages/'):
    full = call('GET', f"pages/{pg['id']}/")
    patch('page', f"pages/{pg['id']}/", full, ('title', 'slug', 'template', 'content', 'meta_title', 'meta_description'))

errors = 0
for kind, path, body in plan:
    short = {k: (v if len(v) < 70 else v[:67] + '...') for k, v in body.items()}
    if APPLY:
        try: call('PATCH', path, body); status = 'ok'
        except RuntimeError as e: status = f'ERROR {e}'; errors += 1
    else: status = 'dry-run'
    print(kind, path, status, json.dumps(short, ensure_ascii=False))
print(f'{len(plan)} objects {"patched" if APPLY else "to patch"}, errors {errors}')
