"""Keep only SKINOFAB's five products in NEXT: delete every other product, the pages that sold only those products,
and the categories they leave empty. Everything deleted is saved first, in full, to <backup.json>.

usage: NEXT_API_TOKEN=... python3 -I prune_catalog.py <store_subdomain> <backup.json> [--apply]
- kept: the Adaptive Peptide Foundation (14), the Lymphatic Brush (169), the PDRN Plumping Balm (202), the EGF + NAD+
  Firming Serum (206) and the Adaptive Foundation Stick (235), with their variants
- pages: apply_persona.LEGACY_PAGES (the advertorials and quizzes for lip plumpers, brows, the collagen mask, the
  reverse-time serum, the old bundle builder and checkout funnel), when NEXT has a page with that slug
- categories: those with no product left once the others are gone (Lips, Lashes, Brows, Bundles …)
- dry run by default (prints the plan); --apply deletes. A product NEXT will not delete (an order may hold it) is set
  non-public instead, and reported
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

STORE, BACKUP = sys.argv[1], Path(sys.argv[2])
APPLY = '--apply' in sys.argv
API = f'https://{STORE}.29next.store/api/admin/'
HDR = {'Authorization': f"Bearer {os.environ['NEXT_API_TOKEN']}", 'X-29next-API-Version': '2024-04-01',
       'Content-Type': 'application/json', 'Accept': 'application/json'}
KEEP = {14, 169, 202, 206, 235}
# the same list as apply_persona.LEGACY_PAGES (the theme drops these pages; NEXT's page records go here)
LEGACY_PAGES = {'aging-brows', 'aging-brows2', 'facemask', 'srm01', 'srm01-2026-10-11-02-01-51-pm', 'page',
                'fuller-lips-without-fillers-copy-copy', 'fullerbutnatural', 'plumper-quiz', 'shadequiz',
                'lip-stain-restock-sign-up', 'top5stains', 'bundle-builder', 'skinofab-how-to-use', 'complete-your-order'}


def call(method, path, body=None):
    for attempt in range(4):
        req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                     method=method, headers=HDR)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read(); return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3: time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f'{method} {path} -> {e.code}: {e.read()[:400].decode("utf-8", "replace")}')


def every(path):
    out, url = [], f'{path}?limit=100'
    while url:
        page = call('GET', url); out += page.get('results', page if isinstance(page, list) else [])
        nxt = page.get('next') if isinstance(page, dict) else None
        url = nxt.split('/api/admin/', 1)[1] if nxt else None
    return out


products = every('products/')
pages = every('pages/')
categories = every('categories/')
drop_products = [p for p in products if p['id'] not in KEEP]
drop_pages = [p for p in pages if p.get('slug') in LEGACY_PAGES]
kept_cats = {c['id'] for p in products if p['id'] in KEEP for c in (p.get('categories') or [])}
drop_cats = [c for c in categories if c['id'] not in kept_cats]
missing = KEEP - {p['id'] for p in products}
if missing: sys.exit(f'not in the store: products {sorted(missing)} - nothing changed')

print(f"keep {len(products) - len(drop_products)} products: " + ', '.join(p['title'] for p in products if p['id'] in KEEP))
print(f'delete {len(drop_products)} products: ' + ', '.join(f"{p['id']} {p['title']}" for p in drop_products))
print(f'delete {len(drop_pages)} pages: ' + ', '.join(p['slug'] for p in drop_pages))
print(f'delete {len(drop_cats)} categories: ' + ', '.join(f"{c['id']} {c.get('name')}" for c in drop_cats))
if not APPLY:
    print('dry run: nothing changed (--apply to delete)'); sys.exit()

# the backup first: every record in full, as NEXT returns it
backup = {'store': STORE, 'saved': time.strftime('%Y-%m-%dT%H:%M:%S'),
          'products': [call('GET', f"products/{p['id']}/") for p in drop_products],
          'pages': [call('GET', f"pages/{p['id']}/") for p in drop_pages],
          'categories': [call('GET', f"categories/{c['id']}/") for c in drop_cats]}
prev = json.loads(BACKUP.read_text()) if BACKUP.exists() else []
BACKUP.write_text(json.dumps((prev if isinstance(prev, list) else [prev]) + [backup], indent=1, ensure_ascii=False))
print('saved', BACKUP)

hidden = []
for p in drop_products:
    try:
        call('DELETE', f"products/{p['id']}/"); print('deleted product', p['id'], p['title'])
    except RuntimeError as e:
        call('PATCH', f"products/{p['id']}/", {'is_public': False}); hidden.append(p['id'])
        print('could not delete product', p['id'], p['title'], '- set non-public:', str(e)[:160])
for p in drop_pages:
    call('DELETE', f"pages/{p['id']}/"); print('deleted page', p['slug'])
for c in drop_cats:
    try:
        call('DELETE', f"categories/{c['id']}/"); print('deleted category', c['id'], c.get('name'))
    except RuntimeError as e:
        print('could not delete category', c['id'], c.get('name'), str(e)[:160])
left = every('products/')
print('products now:', ', '.join(f"{p['id']} {p['title']}" + (' (hidden)' if not p.get('is_public') else '') for p in left))
if hidden: print('not deletable (non-public now):', hidden)
