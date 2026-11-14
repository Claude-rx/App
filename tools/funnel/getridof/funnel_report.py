#!/usr/bin/env python3
"""Get Rid Of — funnel report: what NextCommerce recorded, next to what the ad network billed. Read-only.

    python3 -I tools/funnel/getridof/funnel_report.py --since 2026-11-13 --applovin campaign.csv [--test-email a@b.c ...]

What the store can tell us (Admin API):
  carts   one per shopper who typed email + first + last name at the checkout ("checkout started"), with the landing
          page, device and UTM values the Campaign Cart SDK captured
  orders  completed purchases (the first order and each accepted post-purchase offer are separate orders)
What it cannot: page views, add-to-cart clicks, or people who left before typing a name. Those live in AppLovin
(Axon events page_view / view_item / add_to_cart / begin_checkout) and, once an id is set in campaigns.json, in
Microsoft Clarity / GA4 (gro_* events). Pass their counts with --views / --atc / --checkout-views to fill the top rows.

Test traffic is left out: QA addresses at the store's own domain, anything passed with --test-email, is_test orders.
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_store as store  # noqa: E402  (Admin API client with backoff)

QA = re.compile(r'(^qa[-.]|@getridof\.shop$)', re.I)


def pages(path):
    out = []
    while path:
        r = store.api('GET', path)
        out += r['results']
        nxt = r.get('next')
        path = nxt.split('/api/admin/')[1] if nxt else None
    return out


def money(v):
    return float(re.sub(r'[^0-9.]', '', v or '') or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', required=True, help='first day to include, YYYY-MM-DD (UTC)')
    ap.add_argument('--applovin', action='append', default=[], help='AppLovin campaign export (CSV); repeatable')
    ap.add_argument('--test-email', action='append', default=[], help='an address to treat as test traffic; repeatable')
    ap.add_argument('--funnel', default='Get Rid Of Mouse Repellent Pouches', help='next-funnel name of the campaign pages')
    for k in ('views', 'atc', 'checkout-views'):
        ap.add_argument('--' + k, type=int, help='count from AppLovin Axon / Clarity, if you have it')
    a = ap.parse_args()
    tests = {e.lower() for e in a.test_email}
    is_test = lambda email: not email or email.lower() in tests or bool(QA.search(email))

    clicks = spend = imps = 0
    for f in a.applovin:
        for row in csv.DictReader(open(f, newline='', encoding='utf-8-sig')):
            clicks += int(money(row.get('Clicks'))); imps += int(money(row.get('Impressions'))); spend += money(row.get('Spend'))

    carts = [c for c in pages('carts/?limit=100') if c['date_created'][:10] >= a.since]
    orders = [o for o in pages('orders/?limit=100') if (o.get('date_placed') or '')[:10] >= a.since]
    real_carts = [c for c in carts if not is_test((c.get('user') or {}).get('email')) and ((c.get('attribution') or {}).get('funnel') in (a.funnel, None, ''))]
    real_orders = [o for o in orders if not o.get('is_test') and not is_test((o.get('user') or {}).get('email'))]
    buyers = {(o.get('user') or {}).get('email', '').lower() for o in real_orders}
    revenue = sum(money(o.get('total_incl_tax')) for o in real_orders)

    rows = [('Ad impressions', imps or None), ('Ad clicks (billed)', clicks or None), ('Sales page views', a.views), ('Add to cart', a.atc),
            ('Checkout page views', a.checkout_views), ('Checkout started (email + name typed)', len(real_carts)),
            ('Buyers', len(buyers)), ('Orders incl. accepted offers', len(real_orders))]
    print(f'## Get Rid Of funnel since {a.since}\n')
    print('| Step | Count | % of clicks | % of previous known step |\n|---|---:|---:|---:|')
    prev = None
    for name, n in rows:
        if n is None:
            print(f'| {name} | not available | | |'); continue
        of_clicks = f'{n / clicks:.1%}' if clicks and name != 'Ad impressions' else ''
        of_prev = f'{n / prev:.1%}' if prev else ''
        print(f'| {name} | {n:,} | {of_clicks} | {of_prev} |')
        prev = n or prev
    print(f'\nSpend ${spend:,.2f} · revenue ${revenue:,.2f} · ROAS {revenue / spend:.2f}' if spend else f'\nRevenue ${revenue:,.2f}')
    if spend and real_carts: print(f'Cost per checkout started ${spend / len(real_carts):,.2f}')
    if spend and buyers: print(f'Cost per buyer ${spend / len(buyers):,.2f}')
    print(f'\nLeft out as test traffic: {len(carts) - len(real_carts)} carts, {len(orders) - len(real_orders)} orders.')
    if real_carts:
        meta = [((c.get('attribution') or {}).get('metadata') or {}) for c in real_carts]
        print('\nCheckout starts by device:', dict(Counter(m.get('device_type') or '?' for m in meta)))
        print('by bundle:', dict(Counter((re.search(r'forceBundleId=main(?::|%3A)(\w+)', m.get('landing_page') or '') or [None, '?'])[1] for m in meta)))
        print('by utm_source:', dict(Counter((c.get('attribution') or {}).get('utm_source') or '(none)' for c in real_carts)))
        print('abandoned (no order yet):', sum(1 for c in real_carts if ((c.get('user') or {}).get('email') or '').lower() not in buyers))


if __name__ == '__main__':
    main()
