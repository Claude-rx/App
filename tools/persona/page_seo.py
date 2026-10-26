"""The store pages' search and link-preview descriptions, set on the NEXT pages themselves (Admin API).

usage: NEXT_API_TOKEN=... python3 -I tools/persona/page_seo.py <store-subdomain> <undo_dir>

The pages were created with the placeholder content "Rendered by the theme template." (build_setup_kit.py) and no
meta description, so the platform's {% seo %} tag used that line as every page's description: what search results
and link previews showed for About, FAQ, Track, the policies (review 5). Each page in DESCRIPTIONS gets its own
meta description (155 characters at most: the platform cuts it at 160); the previous values are written to
<undo_dir>/page-seo-undo.json first.
"""
import json, os, sys, time, urllib.request
from pathlib import Path

DESCRIPTIONS = {
    'about-skinofab': 'Skincare-first beauty for skin after 45: an adaptive foundation in a bottle or a stick, a firming '
                      'serum, a plumping balm and a lymphatic brush.',
    'faq': 'Answers about SKINOFAB orders, free shipping, refills and returns, how the Adaptive Peptide Foundation '
           'adapts to your skin, and our 30-day guarantee.',
    'contact': 'Questions about an order, a refill, a return or our products? Email hello@skinofab.com and the SKINOFAB '
               'team will help.',
    'postflows-track-your-order': 'Track your SKINOFAB order with its tracking number. Every order ships free and '
                                  'tracked, within 1 business day.',
    'shipping-policy': 'SKINOFAB ships every order free and tracked within 1 business day. Delivery times for the US, '
                       'the UK, Canada, Australia, the EU and the world.',
    'refund-policy': "SKINOFAB's 30-day money-back guarantee: email us within 30 days of delivery for a full refund, "
                     'even opened. How refunds and exchanges work.',
    'privacy-policy': 'How SKINOFAB collects, uses and protects your personal information when you visit our store '
                      'and place an order.',
    'cookie-policy': 'The cookies and similar technologies the SKINOFAB store uses, what each one does, and how to '
                     'manage them.',
    'terms-of-service': 'The terms that apply when you use the SKINOFAB store and buy our products.',
}


def api(store, path, method='GET', body=None):
    req = urllib.request.Request(f'https://{store}.29next.store/api/admin/{path}', method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': f'Bearer {os.environ["NEXT_API_TOKEN"]}',
                                          'X-29next-API-Version': '2024-04-01', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b'null')


def main():
    store, undo_dir = sys.argv[1], Path(sys.argv[2])
    pages, url = [], 'pages/?limit=100'
    while url:
        d = api(store, url)
        pages += d['results']
        url = d['next'].split('/api/admin/', 1)[1] if d.get('next') else None
    by_slug = {p['slug']: p for p in pages}
    too_long = [s for s, d in DESCRIPTIONS.items() if len(d) > 155]
    if too_long: sys.exit(f'descriptions over 155 characters: {too_long}')
    missing = [s for s in DESCRIPTIONS if s not in by_slug]
    if missing: sys.exit(f'pages not found: {missing}')
    undo = undo_dir / 'page-seo-undo.json'
    if not undo.exists():
        undo.write_text(json.dumps({'saved_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                                    'pages': [{k: by_slug[s][k] for k in ('id', 'slug', 'meta_title', 'meta_description')}
                                              for s in DESCRIPTIONS]}, indent=1))
    for slug, desc in DESCRIPTIONS.items():
        p = by_slug[slug]
        if p.get('meta_description') == desc:
            print('same   ', slug); continue
        out = api(store, f'pages/{p["id"]}/', 'PATCH', {'meta_description': desc})
        print('updated', slug, out.get('meta_description') == desc)


if __name__ == '__main__':
    main()
