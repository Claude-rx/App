"""Fetch a product's published Judge.me reviews from the store's public review widget, as a Judge.me-style CSV export
for import_reviews.py (same columns as Judge.me's own export, plus `verified`).

usage: python3 -I fetch_judgeme.py <shop>.myshopify.com <shopify product id> <out.csv>
- use it for a store you own whose dashboard export is not at hand (here: the owner's Solena store, the same Lymphatic
  Brush); a dashboard export (Judge.me > Reviews > Export) has the same columns and can be used instead
- reads only what the widget shows shoppers: published reviews, their rating, date, name, title, text, photos and
  Judge.me's verified-buyer flag; nothing is changed
"""
import csv, html, json, re, sys, time, urllib.parse, urllib.request

SHOP, PRODUCT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
URL = 'https://judge.me/reviews/reviews_for_widget?'


def page(n):
    q = urllib.parse.urlencode({'url': SHOP, 'shop_domain': SHOP, 'platform': 'shopify', 'page': n, 'per_page': 30,
                                'product_id': PRODUCT})
    req = urllib.request.Request(URL + q, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())


def text(fragment):
    fragment = re.sub(r'<br\s*/?>', '\n', fragment or '')
    fragment = re.sub(r'</p>\s*<p[^>]*>', '\n\n', fragment)
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def attr(block, name):
    m = re.search(r"%s='([^']*)'" % re.escape(name), block) or re.search(r'%s="([^"]*)"' % re.escape(name), block)
    return html.unescape(m.group(1)) if m else ''


rows, seen, n, total = [], set(), 1, None
while True:
    d = page(n)
    total = d.get('total_count', total)
    blocks = re.split(r"<div class='jdgm-rev ", d.get('html') or '')[1:]
    if not blocks: break
    for b in blocks:
        rid = attr(b, 'data-review-id')
        if not rid or rid in seen: continue
        seen.add(rid)
        body = re.search(r"<div class='jdgm-rev__body'>(.*?)</div>", b, re.S)
        title = re.search(r"<b class='jdgm-rev__title'>(.*?)</b>", b, re.S)
        name = re.search(r"<span class='jdgm-rev__author'>(.*?)</span>", b, re.S)
        pics = [html.unescape(u) for u in re.findall(r"data-mfp-src='([^']+)'", b)]
        rows.append({'id': rid, 'title': text(title.group(1) if title else ''), 'body': text(body.group(1) if body else ''),
                     'rating': attr(b, 'data-score'), 'review_date': attr(b, 'datetime'),
                     'reviewer_name': text(name.group(1) if name else ''),
                     'product_handle': attr(b, 'data-product-url').rstrip('/').rsplit('/', 1)[-1],
                     'picture_urls': ','.join(pics), 'verified': 'true' if attr(b, 'data-verified-buyer') == 'true' else 'false',
                     'curated': 'ok'})
    n += 1
    time.sleep(0.6)
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['id'])
    w.writeheader(); w.writerows(rows)
print(json.dumps({'fetched': len(rows), 'widget_total': total, 'with_photos': sum(1 for r in rows if r['picture_urls']),
                  'verified': sum(1 for r in rows if r['verified'] == 'true')}))
