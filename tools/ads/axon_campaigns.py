#!/usr/bin/env python3
"""The SKINOFAB Adaptive Peptide Foundation funnel's AppLovin (Axon) web campaigns, over the Axon Campaign Management API
(https://support.axon.ai/en/growth/promoting-your-websites/api).

Two campaigns, one per entry page of the funnel, each with every ACTIVE video and playable (HTML) asset already in the
ad account, in new creative sets that send to the campaign's own URL (no creative-set URL override):
  1. the listicle   https://try.skinofab.com/10-reasons-adaptive-foundation/
  2. the sales page https://try.skinofab.com/adaptive-foundation-offer/
Each: WEB, US, a daily budget, a CPP (cost per purchaser) goal, auto bidding with CPM billing, no end date.

usage:
  python3 -I tools/ads/axon_campaigns.py plan  --account-id <id> [--budget 100] [--cpp 31] [--out <plan.json>]
  python3 -I tools/ads/axon_campaigns.py apply --account-id <id> --plan <plan.json> --plan-sha256 <hash> --yes
  python3 -I tools/ads/axon_campaigns.py status --account-id <id> --manifest <manifest.json>
  python3 -I tools/ads/axon_campaigns.py pause  --account-id <id> --manifest <manifest.json> --yes

The key is read from APPLOVIN_CAMPAIGN_MANAGEMENT_API_KEY and never printed. `plan` only reads (assets, creative sets,
campaigns) and writes the plan with its sha256; `apply` sends exactly that plan and refuses any other. The API blocks a key
for 24 hours after 100 error responses in five minutes, so every write stops at its first error (no blind retries) and
validates the plan before sending anything."""
import argparse, datetime, hashlib, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

API = 'https://api.ads.axon.ai/manage/v1'
HOST = 'https://try.skinofab.com'
CAMPAIGNS = [   # key, name, entry page
    ('listicle', 'SKINOFAB APF - Listicle', '/10-reasons-adaptive-foundation/'),
    ('sales', 'SKINOFAB APF - Sales page', '/adaptive-foundation-offer/'),
]
VIDEO = ('VID_LONG_P', 'VID_SHORT_P')
PER_TYPE = 10                       # a V2 creative set holds up to 10 assets of each type
COUNTRIES = ['US']                  # the funnel's offer, prices and shipping promise are US


def key():
    k = os.environ.get('APPLOVIN_CAMPAIGN_MANAGEMENT_API_KEY', '')
    if not k: sys.exit('APPLOVIN_CAMPAIGN_MANAGEMENT_API_KEY is not set')
    return k


def call(method, path, account, params=None, body=None):
    q = urllib.parse.urlencode({'account_id': account, **(params or {})})
    req = urllib.request.Request(f'{API}/{path}?{q}', method=method, headers={'Authorization': key(), 'Accept': 'application/json'})
    if body is not None:
        req.data = json.dumps(body).encode(); req.add_header('Content-Type', 'application/json')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode() or 'null'
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            code, msg, trace = e.code, e.headers.get('x-al-error-message', ''), e.headers.get('x-trace-id', '')
            detail = e.read().decode(errors='replace')[:300]
            # a read may wait out a rate limit or a server error once or twice; a write never repeats
            if method == 'GET' and code in (429, 500, 502, 503) and attempt < 2: time.sleep(5 * (attempt + 1)); continue
            sys.exit(f'{method} {path}: HTTP {code} {e.headers.get("x-al-error-code", "")} {msg} (trace {trace}) {detail}')


def pages(path, account, **params):
    out, page = [], 1
    while True:
        got = call('GET', path, account, {**params, 'page': page, 'size': 100}) or []
        out += got
        if len(got) < 100: return out
        page += 1


def landing(entry, key_):
    utm = {'utm_source': 'applovin', 'utm_medium': 'paid', 'utm_campaign': f'apf-{key_}'}
    # the Axon macros are written raw: the ad server fills them per click
    return f'{HOST}{entry}?{urllib.parse.urlencode(utm)}&utm_content={{CREATIVE_SET_ID}}&utm_term={{CAMPAIGN_ID}}'


def build_sets(assets):
    """The assets in creative sets of at most 10 per type; a set must hold a playable, or an end-card image and a video."""
    by = {t: [a for a in assets if a.get('asset_type') == t] for t in ('HOSTED_HTML', 'IMG_INTER_P', 'IMG_BANNER', *VIDEO)}
    videos = by['VID_LONG_P'] + by['VID_SHORT_P']
    n = max(1, -(-len(by['HOSTED_HTML']) // PER_TYPE), -(-len(videos) // PER_TYPE))
    sets = []
    for i in range(n):
        chunk = lambda lst: lst[i * PER_TYPE:(i + 1) * PER_TYPE]
        html, vids = chunk(by['HOSTED_HTML']), chunk(videos)
        # every set gets the end cards and banners (they are few); a set of videos needs one end card or a playable
        imgs, banners = by['IMG_INTER_P'][:PER_TYPE], by['IMG_BANNER'][:PER_TYPE]
        if not html and not by['HOSTED_HTML'] and vids and not imgs:
            sets.append({'invalid': f'{len(vids)} videos and no playable or end-card image (IMG_INTER_P) in the account'}); continue
        if not html and by['HOSTED_HTML']: html = by['HOSTED_HTML'][:1]     # lend a playable so a video-only chunk is valid
        sets.append({'assets': [a['id'] for a in html + vids + imgs + banners],
                     'names': [f"{a.get('asset_type')}:{a.get('name')}" for a in html + vids + imgs + banners]})
    return sets


def plan(a):
    account = a.account_id
    assets = pages('asset/list', account)
    active = [x for x in assets if x.get('status') == 'ACTIVE' and x.get('asset_type') in ('HOSTED_HTML', 'IMG_INTER_P', 'IMG_BANNER', *VIDEO)]
    sets = pages('creative_set/list', account)
    camps = pages('campaign/list', account)
    taken = {c['name'] for c in camps}
    built = build_sets(active)
    bad = [s['invalid'] for s in built if 'invalid' in s]
    start = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT00:00:00')
    out = {'account_id': str(account), 'created_for': 'SKINOFAB Adaptive Peptide Foundation funnel',
           'inventory': {'assets_total': len(assets), 'assets_active_used': len(active),
                         'assets_skipped': sorted({f"{x.get('asset_type')}:{x.get('status')}" for x in assets if x not in active}),
                         'creative_sets_existing': [{'id': s.get('id'), 'name': s.get('name'), 'campaign_id': s.get('campaign_id'),
                                                     'status': s.get('status'), 'assets': len(s.get('assets') or [])} for s in sets],
                         'campaigns_existing': [{'id': c.get('id'), 'name': c.get('name'), 'status': c.get('status'),
                                                 'website_url': c.get('website_url')} for c in camps]},
           'campaigns': []}
    for k, name, entry in CAMPAIGNS:
        if name in taken: sys.exit(f'a campaign named "{name}" already exists in the account: rename or remove it first')
        out['campaigns'].append({'key': k, 'campaign': {
            'name': name, 'type': 'WEB', 'start_date': start, 'is_continuous_delivery': True, 'targeting': [{'country_code': c} for c in COUNTRIES],
            'budget': {'daily_budget_for_all_countries': f'{a.budget:g}'},
            'goal': {'goal_type': 'CPP', 'goal_value_for_all_countries': f'{a.cpp:g}', 'roas_day_target': a.window},
            'bidding_strategy': 'AUTO_BIDDING_WITH_CPM_BILLING', 'audience_strategy': 'UNIVERSAL',
            'website_url': landing(entry, k), 'is_dynamic_ads_enabled': False},
            'creative_sets': [{'name': f'{name} - set {i + 1}', 'type': 'WEB', 'countries': COUNTRIES, 'assets': [{'id': x} for x in s['assets']],
                               '_asset_names': s['names']} for i, s in enumerate(x for x in built if 'assets' in x)]})
    if bad: out['blocked'] = bad
    text = json.dumps(out, indent=2, sort_keys=True)
    Path(a.out).write_text(text)
    print(json.dumps({'plan': a.out, 'sha256': hashlib.sha256(text.encode()).hexdigest(), 'assets_active_used': len(active),
                      'creative_sets_per_campaign': len(out['campaigns'][0]['creative_sets']), 'blocked': bad}, indent=2))


def apply(a):
    text = Path(a.plan).read_text()
    if hashlib.sha256(text.encode()).hexdigest() != a.plan_sha256: sys.exit('the plan changed since it was approved: run plan again')
    if not a.yes: sys.exit('apply sends real campaigns that spend budget: pass --yes with the approved --plan-sha256')
    p = json.loads(text)
    if p.get('blocked'): sys.exit(f'the plan is blocked: {p["blocked"]}')
    if str(p['account_id']) != str(a.account_id): sys.exit('the plan was made for another account')
    for c in p['campaigns']:
        if not c['creative_sets']: sys.exit(f'{c["campaign"]["name"]}: no creative set to send')
    manifest = {'account_id': str(a.account_id), 'plan_sha256': a.plan_sha256, 'campaigns': []}
    out = Path(a.plan).with_name('axon-manifest.json')
    for c in p['campaigns']:
        cid = call('POST', 'campaign/create', a.account_id, body=c['campaign'])['id']
        entry = {'key': c['key'], 'id': str(cid), 'name': c['campaign']['name'], 'creative_sets': []}
        manifest['campaigns'].append(entry); out.write_text(json.dumps(manifest, indent=2))   # written after every write
        for s in c['creative_sets']:
            body = {k: v for k, v in s.items() if not k.startswith('_')}; body['campaign_id'] = str(cid)
            entry['creative_sets'].append(str(call('POST', 'creative_set/create', a.account_id, body=body)['id']))
            out.write_text(json.dumps(manifest, indent=2))
        print(f'created campaign {cid} ({entry["name"]}) with {len(entry["creative_sets"])} creative set(s)')
    print(f'manifest: {out}')
    status(argparse.Namespace(account_id=a.account_id, manifest=str(out)))


def status(a):
    m = json.loads(Path(a.manifest).read_text())
    ids = ','.join(c['id'] for c in m['campaigns'])
    for c in call('GET', 'campaign/list', a.account_id, {'ids': ids}) or []:
        print(json.dumps({k: c.get(k) for k in ('id', 'name', 'status', 'budget', 'goal', 'targeting', 'website_url', 'start_date', 'bidding_strategy')}))
    got = call('GET', 'creative_set/list_by_campaign_id', a.account_id, {'ids': ids}) or {}
    for cid, sets in (got.get('campaigns') or {}).items():
        for s in sets:
            print(json.dumps({'campaign': cid, 'set': s.get('id'), 'name': s.get('name'), 'status': s.get('status'),
                              'assets': [f"{x.get('type') or x.get('asset_type')}:{x.get('status')}" for x in s.get('assets') or []]}))


def pause(a):
    if not a.yes: sys.exit('pass --yes to pause the manifest\'s campaigns')
    m = json.loads(Path(a.manifest).read_text())
    for c in m['campaigns']:
        call('POST', 'campaign/update', a.account_id, body={'id': c['id'], 'type': 'WEB', 'status': 'PAUSED'})
        print(f'paused {c["id"]} ({c["name"]})')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for n in ('plan', 'apply', 'status', 'pause'):
        s = sub.add_parser(n); s.add_argument('--account-id', required=True)
        if n == 'plan':
            s.add_argument('--budget', type=float, default=100.0, help='daily budget per campaign, USD')
            s.add_argument('--cpp', type=float, default=31.0, help='cost-per-purchaser goal, USD')
            s.add_argument('--window', default='DAY7', choices=['DAY0', 'DAY7'], help='purchases counted within this window')
            s.add_argument('--out', default='axon-plan.json')
        if n == 'apply': s.add_argument('--plan', required=True); s.add_argument('--plan-sha256', required=True); s.add_argument('--yes', action='store_true')
        if n in ('status', 'pause'): s.add_argument('--manifest', required=True)
        if n == 'pause': s.add_argument('--yes', action='store_true')
    a = ap.parse_args()
    {'plan': plan, 'apply': apply, 'status': status, 'pause': pause}[a.cmd](a)
