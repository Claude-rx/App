"""Focus the NEXT store on one product: the Adaptive Peptide Foundation (formerly Color Changing Foundation).

usage: NEXT_API_TOKEN=... python3 -I focus_catalog.py <store_subdomain> <ccf-offers.json> <undo.json> [--apply | --undo | --unhide [--apply]]
- renames the foundation and its Duo, gives them new slugs and persona descriptions
- sets every other product non-public (kept: the foundation only; it is sold as a monthly refill, so the
  one-time Duo and Complexion Set are hidden too)
- dry run by default; --apply writes and saves the previous values to <undo.json>; --undo restores them
- --unhide makes the hidden products public again (not the Duo / Complexion Set), keeping the rename
"""
import json, os, sys, time, urllib.request, urllib.error

STORE, OFFERS, UNDO = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
APPLY, REVERT = '--apply' in sys.argv, '--undo' in sys.argv
API = f'https://{STORE}.29next.store/api/admin/'
HDR = {'Authorization': f"Bearer {os.environ['NEXT_API_TOKEN']}", 'X-29next-API-Version': '2024-04-01',
       'Content-Type': 'application/json', 'Accept': 'application/json'}

def call(method, path, body=None):
    for attempt in range(4):
        req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method=method, headers=HDR)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read(); return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3: time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f'{method} {path} -> {e.code}: {e.read()[:400].decode("utf-8", "replace")}')

def all_products():
    out, url = [], 'products/?page_size=100'
    while url:
        page = call('GET', url); out += page['results']
        nxt = page.get('next'); url = nxt.split('/api/admin/', 1)[1] if nxt else None
    return out

FOUNDATION, DUO, SET = OFFERS['foundation']['pk'], OFFERS['color-changing-foundation-duo']['pk'], OFFERS['complexion-set']['pk']
DESC = ('<p>The color-adapting serum foundation made for skin after 45. It goes on white and turns into your skin tone '
        'as you blend, inside the base you choose (Light–Medium or Medium–Deep). A hydrating serum base with PDRN, '
        'peptides and hyaluronic acid evens out sun spots and redness and blurs the look of fine lines without settling '
        'into them. Fragrance-free. 30 mL / 1.01 fl oz. Backed by a 30-day shade-match guarantee.</p>')
RENAME = {
    FOUNDATION: {'title': 'Adaptive Peptide Foundation', 'slug': 'adaptive-peptide-foundation', 'description': DESC,
                 'meta_title': 'Adaptive Peptide Foundation | Color-adapting serum foundation for skin after 45 | SKINOFAB',
                 'meta_description': 'Stop guessing your shade after 45. Goes on white, turns into your skin, hydrates with PDRN and peptides and won\'t settle into lines. 30-day shade-match guarantee.'},
    DUO: {'title': 'Adaptive Peptide Foundation Duo', 'slug': 'adaptive-peptide-foundation-duo',
          'description': '<p>Two bottles of the Adaptive Peptide Foundation, the color-adapting serum foundation made for skin after 45. Keep one at home and one in your bag, or pick one of each base.</p>'},
}
KEEP = {FOUNDATION}

if REVERT:
    for path, body in json.load(open(UNDO)): call('PATCH', path, body); print('restored', path)
    sys.exit()
if '--unhide' in sys.argv:
    # back to the full catalog the persona design links to, keeping the rename; the one-time Duo and Complexion Set
    # stay hidden (the foundation is sold as a monthly refill only)
    paths = {path for path, body in json.load(open(UNDO)) if body.get('is_public') is True}
    paths -= {f'products/{DUO}/', f'products/{SET}/'}
    for path in sorted(paths, key=lambda s: int(s.split('/')[1])):
        if not call('GET', path).get('is_public'):
            if '--apply' in sys.argv: call('PATCH', path, {'is_public': True})
            print('show' if '--apply' in sys.argv else 'plan show', path)
    sys.exit()
plan, undo = [], []
for p in all_products():
    full = call('GET', f"products/{p['id']}/")
    body = {k: v for k, v in RENAME.get(p['id'], {}).items() if full.get(k) != v}
    if p['id'] not in KEEP and full.get('is_public'):
        body['is_public'] = False; print('hide', p['id'], full['title'])
    if body:
        plan.append((f"products/{p['id']}/", body)); undo.append((f"products/{p['id']}/", {k: full.get(k) for k in body}))
for path, body in plan:
    if APPLY: call('PATCH', path, body)
    print('PATCH' if APPLY else 'plan', path, {k: (str(v)[:60]) for k, v in body.items()})
if APPLY and undo:
    prev = json.load(open(UNDO)) if os.path.exists(UNDO) else []
    json.dump(prev + undo, open(UNDO, 'w'), indent=1, ensure_ascii=False)
print(len(plan), 'changes', 'applied' if APPLY else '(dry run)')
