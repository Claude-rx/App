"""Create the SKINOFAB catalog on NEXT through the Admin API (2024-04-01).

usage: NEXT_API_TOKEN=... python3 -I deploy_catalog.py <store_subdomain> <export_dir> <out_mapping.json> [--dry-run] [--replace-images] [--only=handle,...]

Idempotent: categories and pages are matched by slug, products by the handle -> id mapping of the previous
run (<out_mapping.json>, checked against the live product list; NEXT re-slugs products from their title and the list
API does not return the template key) with slug as a fallback, so a re-run never duplicates. Creates
  - categories from the design's collection pages (membership = products linked from each collection grid)
  - products with variant attributes, variants (SKU, USD price + compare-at, stock), template key = design handle,
    and the design's product images (base64 upload, variant images linked)
  - pages with template key = slug (existing pages with the same slug only get their template set)
--only=<handles> limits product writes to those handles (others keep their previous mapping).
--replace-images deletes each product's current images and uploads the export's again (after a rebrand of the
design's photos). Writes the handle -> product id / variant ids / category ids mapping used for the theme's Product Links settings.
"""
import base64, json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path
from bs4 import BeautifulSoup

STORE, EXPORT, OUT = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
DRY = '--dry-run' in sys.argv
REPLACE = '--replace-images' in sys.argv
ONLY = next((set(a.split('=', 1)[1].split(',')) for a in sys.argv if a.startswith('--only=')), None)
TOKEN = os.environ['NEXT_API_TOKEN']
API = f'https://{STORE}.29next.store/api/admin/'
LOG = []

def call(method, path, body=None, retries=4):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            'Authorization': f'Bearer {TOKEN}', 'X-29next-API-Version': '2024-04-01',
            'Content-Type': 'application/json', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            msg = e.read()[:600].decode('utf-8', 'replace')
            if e.code in (429, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f'{method} {path} -> {e.code}: {msg}')
        except urllib.error.URLError:
            if attempt < retries - 1: time.sleep(2 ** (attempt + 1)); continue
            raise

def list_all(path):
    out, url = [], f'{path}?page_size=100'
    while url:
        page = call('GET', url)
        out += page.get('results', [])
        nxt = page.get('next')
        url = nxt.split('/api/admin/', 1)[1] if nxt else None
    return out

def write(method, path, body, what):
    if DRY:
        LOG.append({'dry_run': what}); return {'id': None, 'variants': [], 'slug': body.get('slug')}
    res = call(method, path, body)
    LOG.append({'ok': what, 'id': res.get('id')})
    return res

# ---------------------------------------------------------------- design data
snaps = {f.stem: json.loads(f.read_text()) for f in sorted((EXPORT / 'products').glob('*.js'))}
handles = sorted(snaps)
IMG_DIR = EXPORT / 'assets' / 'img'

def local_image(path):
    """Snapshot image path -> local file (the optimizer may have changed the extension)."""
    if not path: return None
    name = Path(path.split('?')[0]).name
    f = IMG_DIR / name
    if f.exists(): return f
    stem = Path(name).stem
    hits = sorted(IMG_DIR.glob(stem + '.*'))
    return hits[0] if hits else None

def collection_members(c):
    s = BeautifulSoup((EXPORT / 'collections' / f'{c}.html').read_text(), 'lxml')
    main = s.select_one('#MainContent') or s
    found = []
    for a in main.find_all('a', href=True):
        m = re.search(r'products/([a-z0-9][a-z0-9-]*)\.html', a['href'])
        if m and m.group(1) in snaps and m.group(1) not in found: found.append(m.group(1))
    title = (main.find('h1') or s.title)
    name = re.sub(r'\s*[|–—-]\s*(Smooche|SKINOFAB).*$', '', title.get_text(' ', strip=True)) if title else c.replace('-', ' ').title()
    return name or c.replace('-', ' ').title(), found

money = lambda cents: f'{(cents or 0) / 100:.2f}'

# ---------------------------------------------------------------- categories
existing_cats = {c['slug']: c for c in list_all('categories/')}
cat_ids, cat_members = {}, {}
for f in sorted((EXPORT / 'collections').glob('*.html')):
    c = f.stem
    if c in ('all', 'all-products'): continue
    name, members = collection_members(c)
    cat_members[c] = members
    if c in existing_cats:
        cat_ids[c] = existing_cats[c]['id']; continue
    res = write('POST', 'categories/', {'name': name, 'slug': c, 'is_public': True, 'description': ''}, f'category {c}')
    cat_ids[c] = res.get('id')
product_cats = {h: [cat_ids[c] for c, m in cat_members.items() if h in m and cat_ids.get(c)] for h in handles}

# ---------------------------------------------------------------- products
live = list_all('products/')
existing = {p['slug']: p for p in live}
by_id = {p['id']: p for p in live}
prior = json.loads(OUT.read_text()).get('mapping', {}).get('products', {}) if OUT.exists() else {}
for h, m in prior.items():
    if m.get('id') in by_id:   # the previous run's product for this handle, full record (variants, images)
        existing[h] = call('GET', f"products/{m['id']}/")
mapping = {'store': STORE, 'categories': cat_ids, 'products': {}}
for h in handles:
    if ONLY is not None and h not in ONLY and h in prior:   # --only: leave the other products untouched
        mapping['products'][h] = prior[h]; continue
    d = snaps[h]
    options = [o for o in d.get('options', []) if isinstance(o, dict) and o.get('name') != 'Title']
    variants = []
    for i, v in enumerate(d.get('variants', [])):
        entry = {
            'sku': v.get('sku') or f'SKF-{h}-{i + 1}'.upper()[:64],
            'track_stock': False, 'allow_backorders': True, 'requires_shipping': True,
            'prices': [{'currency': 'USD', 'price': money(v.get('price')),
                        **({'retail': money(v['compare_at_price'])} if (v.get('compare_at_price') or 0) > (v.get('price') or 0) else {})}],
            'stockrecords': [{'location_id': 1, 'num_in_stock': 1000, 'low_stock_threshold': 0}],
        }
        if options:
            entry['variant_attribute_values'] = [{'name': o['name'], 'value': v.get(f'option{n + 1}')} for n, o in enumerate(options)]
        variants.append(entry)
    if not options: variants = variants[:1]
    body = {'title': d.get('title') or h, 'slug': h, 'description': d.get('description') or '', 'is_public': True,
            'template': h, 'categories': product_cats.get(h, []), 'variants': variants,
            **({'variant_attributes': [{'name': o['name'], 'values': o['values']} for o in options]} if options else {})}
    if h in existing:
        prod = existing[h]
        if prod.get('template') != h:
            write('PATCH', f"products/{prod['id']}/", {'template': h}, f'product {h} template')
        LOG.append({'exists': f'product {h}', 'id': prod['id']})
    else:
        prod = write('POST', 'products/', body, f'product {h}')
    pid = prod.get('id')
    # images (only for products created now, or products without images; all of them with --replace-images)
    if pid and not DRY and REPLACE:
        for img in prod.get('images') or []:
            call('DELETE', f"products/{pid}/images/{img['id']}/")
        LOG.append({'ok': f'images {h} cleared', 'count': len(prod.get('images') or [])})
    if pid and not DRY and (REPLACE or not prod.get('images')):
        by_value = {}
        for v_src, v_res in zip(d.get('variants', []), prod.get('variants', [])):
            src = (v_src.get('featured_image') or {}).get('src')
            if src: by_value.setdefault(src, []).append(v_res['id'])
        for order, src in enumerate(d.get('images', [])[:10]):
            f = local_image(src)
            if not f: LOG.append({'missing_image': f'{h}: {src}'}); continue
            img = {'attachment': base64.b64encode(f.read_bytes()).decode(), 'file_name': f.name, 'display_order': order,
                   'caption': d.get('title', '')[:200]}
            if by_value.get(src): img['variants'] = by_value[src]
            try:
                call('POST', f'products/{pid}/images/', img)
                LOG.append({'ok': f'image {h} #{order}'})
            except RuntimeError as e:
                LOG.append({'image_error': f'{h} #{order}: {str(e)[:200]}'})
    mapping['products'][h] = {'id': pid, 'variants': [v.get('id') for v in prod.get('variants', [])],
                              'first_variant': (prod.get('variants') or [{}])[0].get('id'), 'categories': product_cats.get(h, [])}

# ---------------------------------------------------------------- pages
setup = json.loads((Path(__file__).resolve().parents[2] / 'next-setup-kit' / 'pages.json').read_text())
existing_pages = {p['slug']: p for p in list_all('pages/')}
mapping['pages'] = {}
for page in setup:
    slug = page['slug']
    if slug in existing_pages:
        cur = existing_pages[slug]
        if cur.get('template') != page['template']:
            write('PATCH', f"pages/{cur['id']}/", {'template': page['template']}, f'page {slug} template (content kept)')
        mapping['pages'][slug] = cur['id']; continue
    res = write('POST', 'pages/', {'title': page['title'][:200], 'slug': slug, 'template': page['template'],
                                   'content': page['content'], 'meta_title': page['meta_title'][:200]}, f'page {slug}')
    mapping['pages'][slug] = res.get('id')

OUT.write_text(json.dumps({'mapping': mapping, 'log': LOG}, indent=1))
errors = [l for l in LOG if any(k.endswith('error') for k in l)]
print(f"categories {len(cat_ids)}  products {len(mapping['products'])}  pages {len(mapping['pages'])}  "
      f"images {sum(1 for l in LOG if str(l.get('ok','')).startswith('image'))}  errors {len(errors)}  dry_run={DRY}")
for e in errors[:10]: print('  ', e)
