"""Point a NEXT order webhook at the deployed TikTok relay (run once, after the Netlify site exists).

    python3 -I tools/tiktok-events/create_webhook.py https://<site>.netlify.app/tiktok-events?key=<RELAY_KEY>
    python3 -I tools/tiktok-events/create_webhook.py --list
    python3 -I tools/tiktok-events/create_webhook.py --delete <webhook id>

Uses the store's Admin API (the token is the one this environment's proxy injects; elsewhere set NEXT_ADMIN_TOKEN).
Subscribes to order.created and order.updated: the relay sends the purchase on the first and the upsells on the next
ones (TikTok drops repeats of the same event_id). Re-running with the same URL updates the existing webhook. The
printed target hides the key."""
import json, os, re, sys, urllib.error, urllib.request

STORE = os.environ.get('NEXT_STORE_URL', 'https://getridof.29next.store')
NAME = 'TikTok Events API relay'


def api(method, path, body=None):
    req = urllib.request.Request(f'{STORE}/api/admin/{path}', method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + os.environ.get('NEXT_ADMIN_TOKEN', 'proxy-injected'),
                                          'X-29next-API-Version': '2024-04-01', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        sys.exit(f'{method} {path}: HTTP {e.code} {e.read().decode()[:300]}')


def hide(url):
    return re.sub(r'([?&]key=)[^&]+', r'\1…', url or '')


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        sys.exit(__doc__)
    hooks = api('GET', 'webhooks/').get('results', [])
    if argv[0] == '--list':
        for h in hooks:
            print(h['id'], h.get('name'), hide(h.get('target')), h.get('events'), 'active' if h.get('active') else 'off')
        return
    if argv[0] == '--delete':
        api('DELETE', f'webhooks/{int(argv[1])}/')
        print('deleted', argv[1])
        return
    target = argv[0]
    if not re.match(r'^https://[^/]+/.+[?&]key=[A-Za-z0-9_-]{24,}', target):
        sys.exit('target must be https://…/tiktok-events?key=<RELAY_KEY> (a key of 24+ letters/digits)')
    body = {'name': NAME, 'target': target, 'events': ['order.created', 'order.updated'], 'active': True}
    mine = [h for h in hooks if h.get('name') == NAME]
    h = api('PATCH', f"webhooks/{mine[0]['id']}/", body) if mine else api('POST', 'webhooks/', body)
    print('webhook', h.get('id'), hide(h.get('target')), h.get('events'), 'active' if h.get('active') else 'off')


if __name__ == '__main__':
    main(sys.argv[1:])
