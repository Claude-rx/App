"""Crawl the preview theme: every page template, category and visible product; report non-200s and server errors.

usage: python3 -I crawl.py <store_url> <theme_id> <catalog_mapping.json> [extra paths...]
"""
import concurrent.futures as cf, http.cookiejar, json, re, sys, urllib.request, urllib.error

store, theme, mapping = sys.argv[1].rstrip('/'), sys.argv[2], json.load(open(sys.argv[3]))['mapping']
jar = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.open(f'{store}/?preview_theme={theme}').read()
home = op.open(store + '/').read().decode('utf-8', 'ignore')
paths = {'/', '/cart/', '/search/?q=foundation', '/catalogue/'} | {f'/{s}/' for s in mapping.get('pages', {})}
paths |= set(re.findall(r'href="(/(?:catalogue|blog)/[^"#?]+)"', home)) | set(sys.argv[4:])
for c, cid in mapping.get('categories', {}).items(): paths.add(f'/catalogue/category/{c}_{cid}/')
def get(p):
    try:
        r = op.open(store + p, timeout=60); body = r.read().decode('utf-8', 'ignore')
        err = 'TemplateSyntaxError' in body or 'Server Error' in body[:2000]
        return p, r.status, err
    except urllib.error.HTTPError as e: return p, e.code, e.code >= 500
    except Exception as e: return p, str(e)[:40], True
with cf.ThreadPoolExecutor(6) as ex: res = sorted(ex.map(get, sorted(paths)))
bad = [r for r in res if r[1] != 200 or r[2]]
print(len(res), 'pages;', len(bad), 'not OK')
for r in bad: print('  ', r)
