#!/usr/bin/env python3
"""Watch the store for new payment attempts and orders, one line each (no customer data).

usage: python3 -I tools/funnel/watch_payments.py [--since-tx N] [--since-order N] [--once] [--interval S]
The Admin token comes from $SKINOFAB_ADMIN_TOKEN (or $NEXT_API_TOKEN) and is never printed.
"""
import json, os, sys, time, urllib.request

BASE = 'https://skinofab.29next.store/api/admin'
TOKEN = os.environ.get('SKINOFAB_ADMIN_TOKEN') or os.environ.get('NEXT_API_TOKEN')
CODES = {'2000': 'Do Not Honor', '2001': 'Insufficient Funds', '2002': 'Limit Exceeded', '2003': 'Processor Declined',
         '2004': 'Authorization Required', '2005': 'Processing Error', '3000': 'Additional Authorization Required',
         '3001': 'AVS Failed', '3002': 'Invalid Card', '3003': 'CVC Invalid', '3004': 'Expiry Invalid',
         '3005': 'Card Number Invalid', '3006': 'Expired Card', '3007': 'Invalid Transaction', '3009': 'Fraudulent',
         '3010': 'Hard Decline', '3011': 'Merchant Error', '3013': 'Issuer Error', '3016': '3DS Failed',
         '3017': 'Blocked by Block List', '5000': 'Method Unsupported', '5001': 'Method Failed', '5004': 'Invalid Parameter'}


def get(path):
    req = urllib.request.Request(BASE + path, headers={'Authorization': 'Bearer ' + TOKEN})
    data = json.load(urllib.request.urlopen(req, timeout=20))
    return data.get('results', data) if isinstance(data, dict) else data


def latest():
    tx, orders = get('/transactions/?page_size=1'), get('/orders/?page_size=1')
    return (tx[0]['id'] if tx else 0), (int(orders[0]['number']) if orders else 0)


def tx_line(t):
    code = str(t.get('response_code') or '')
    order = t.get('order')
    number = order.get('number') if isinstance(order, dict) else order
    return (f"TX #{t['id']} {t.get('status')} {t.get('type')} ${t.get('amount')} via {t.get('payment_method')}"
            f" code={code or '-'} {CODES.get(code, '')} order={number}").rstrip()


def order_line(o):
    user = o.get('user') or {}
    lines = [line.get('sku') for line in o.get('lines') or []]
    return (f"ORDER #{o['number']} {'TEST' if o.get('is_test') else 'real'} {o.get('payment_status')} ${o.get('total_incl_tax')}"
            f" funnel={(o.get('attribution') or {}).get('funnel')} email_on_order={bool(user.get('email'))} lines={lines}")


def main(argv):
    if not TOKEN:
        sys.exit('watch_payments: set SKINOFAB_ADMIN_TOKEN')
    arg = lambda name, default: int(argv[argv.index(name) + 1]) if name in argv else default
    tx0, order0 = latest()
    last_tx, last_order = arg('--since-tx', tx0), arg('--since-order', order0)
    print(f'watching: after transaction #{last_tx}, order #{last_order}', flush=True)
    while True:
        try:
            for t in sorted((t for t in get('/transactions/?page_size=20') if t['id'] > last_tx), key=lambda t: t['id']):
                print(tx_line(t), flush=True); last_tx = t['id']
            for o in sorted((o for o in get('/orders/?page_size=20') if int(o['number']) > last_order), key=lambda o: int(o['number'])):
                print(order_line(get(f"/orders/{o['number']}/")), flush=True); last_order = int(o['number'])
        except Exception as e:  # one failed poll must not end the watch
            print(f'poll error: {type(e).__name__}', flush=True)
        if '--once' in argv:
            return
        time.sleep(arg('--interval', 20))


if __name__ == '__main__':
    main(sys.argv[1:])
