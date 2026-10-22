"""Fetch a product's published Loox reviews from the store's public Loox widget, as a CSV for import_reviews.py.

usage: python3 -I fetch_loox.py <loox client id> <shopify product id> <out.csv> [--pages N]
- the client id is in the store's Loox loader (https://loox.io/widget/loox.js?shop=<shop>.myshopify.com: LOOX.clientId)
- reads what the widget shows shoppers, 20 reviews a page, newest pages first: name, Loox's "Verified" badge, rating,
  text and photos (the widget shows no review date; a photo review's date is the day its photo was uploaded, read
  from the photo's address)
- use it for a store you own (here: the owner's Smooche store, the same foundation formula); a dashboard export
  (Loox > Reviews > Export) has the same fields and can be used instead
"""
import csv, html, json, re, sys, time, urllib.request
from bs4 import BeautifulSoup

CLIENT, PRODUCT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PAGES = int(sys.argv[sys.argv.index('--pages') + 1]) if '--pages' in sys.argv else 50


def page(n):
    """One widget page; retried with backoff (a long fetch meets slow or dropped responses). None when it keeps failing."""
    url = f'https://loox.io/widget/{CLIENT}/reviews/{PRODUCT}?h=&variant=visible&language=en&page={n}'
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r: return r.read().decode('utf-8', 'replace')
        except Exception as e:
            print(f'page {n}: {e}', file=sys.stderr); time.sleep(2 ** (attempt + 1))
    return None


rows, seen = [], set()
for n in range(1, PAGES + 1):
    raw = page(n)
    if raw is None: print(f'stopped at page {n}: it keeps failing; saving what was read', file=sys.stderr); break
    soup = BeautifulSoup(raw, 'html.parser')
    items = soup.select('.grid-item-wrap[data-id]')
    fresh = 0
    for it in items:
        rid = it['data-id']
        if rid in seen: continue
        seen.add(rid); fresh += 1
        title = it.select_one('.block.title')
        badge = title.select_one('.verified-badge-and-text') if title else None
        if badge: badge.extract()
        name = ' '.join(title.get_text(' ', strip=True).split()) if title else ''
        stars = it.select_one('.block.stars [aria-label]')
        m = re.search(r'(\d)\s*/\s*5', stars['aria-label']) if stars else None
        text = it.select_one('.main-text')
        photos = []
        for img in it.select('.item-img img[src]'):
            src = img['src']
            photos.append(('https:' + src) if src.startswith('//') else src)
        when = ''
        for p in photos:
            d = re.search(r'/uploads/(\d{4})/(\d{1,2})/(\d{1,2})/', p)
            if d: when = f'{d.group(1)}-{int(d.group(2)):02d}-{int(d.group(3)):02d}'; break
        rows.append({'id': rid, 'title': '', 'body': text.get_text('\n', strip=True) if text else '',
                     'rating': m.group(1) if m else '', 'review_date': when, 'reviewer_name': name,
                     'product_handle': PRODUCT, 'picture_urls': ','.join(photos),
                     'verified': 'true' if badge else 'false', 'media_type': it.get('data-media-type', ''), 'curated': 'ok'})
    if not items or not fresh: break
    time.sleep(0.25)
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['id'])
    w.writeheader(); w.writerows(rows)
dated = sorted(r['review_date'] for r in rows if r['review_date'])
print(json.dumps({'fetched': len(rows), 'pages': n, 'verified': sum(r['verified'] == 'true' for r in rows),
                  'with_photos': sum(bool(r['picture_urls']) for r in rows), 'videos': sum(r['media_type'] == 'video' for r in rows),
                  'photo_dates': [dated[0], dated[-1]] if dated else None,
                  'ratings': {s: sum(r['rating'] == str(s) for r in rows) for s in (5, 4, 3, 2, 1)}}))
