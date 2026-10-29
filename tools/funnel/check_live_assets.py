"""After a push: every asset the funnel's public pages reference answers 200, as a visitor without the preview cookie
gets them (the store's cached copy, up to 30 minutes old, included).

usage: python3 -I tools/funnel/check_live_assets.py [https://try.skinofab.com] [--funnel apf|stick]

A deploy that re-sends an unchanged asset makes the store drop its old copy while cached pages still point at it: on
29 Oct 2026 the sales hero's mobile picture answered 403 to public visitors for 16 minutes (live review 10). Run this
right after a push and again 30 minutes later; tools/funnel/push_theme.py is what keeps it from happening.
"""
import importlib, re, sys, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
BASE = (ARGS[0] if ARGS else 'https://try.skinofab.com').rstrip('/')
FUNNEL = sys.argv[sys.argv.index('--funnel') + 1] if '--funnel' in sys.argv else 'apf'
F = importlib.import_module(f'funnels.{FUNNEL}')
UA = {'User-Agent': 'Mozilla/5.0 (skinofab asset check)'}
ASSET = re.compile(r'(?:src|href|poster|data-sf-poster|srcset)="([^"]+)"')


def get(url, method='GET'):
    req = urllib.request.Request(url, headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, (r.read() if method == 'GET' else b'')
    except urllib.error.HTTPError as e: return e.code, b''
    except Exception as e: return f'error {type(e).__name__}', b''


def assets(page_url, html):
    out = set()
    for raw in ASSET.findall(html):
        for part in unescape(raw).split(','):                     # srcset: "a.jpg 760w, b.jpg 1080w"
            u = part.strip().split(' ')[0]
            if not u or u.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')): continue
            full = urljoin(page_url, u)
            if re.search(r'\.(?:jpe?g|png|webp|avif|gif|svg|mp4|webm|css|js|woff2?)(?:\?|$)', full): out.add(full)
    return out


def main():
    bad, seen = [], {}
    for p in F.PAGES:
        url = f'{BASE}/{p["file"]}/'
        code, body = get(url)
        if code != 200: bad.append(f'{url}: page answered {code}'); continue
        for a in assets(url, body.decode('utf-8', 'replace')): seen.setdefault(a, url)
    with ThreadPoolExecutor(12) as ex:
        codes = dict(zip(seen, ex.map(lambda u: get(u, 'GET')[0], seen)))
    for a, code in sorted(codes.items()):
        if code != 200: bad.append(f'{seen[a]}: {a} answered {code}')
    print(f'check_live_assets: {len(F.PAGES)} pages, {len(codes)} assets, {len(bad)} broken')
    for b in bad: print('  ' + b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
