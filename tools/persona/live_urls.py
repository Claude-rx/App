"""Resolve the public URL NEXT serves for each theme image right now.

NEXT keeps the first upload under the plain file name and stores later re-uploads under a suffixed name
(name_AbC12dE.jpg), so the plain CDN path can still serve a pre-rebrand version. The storefront HTML always
references the current one; this reads it from the live preview pages.

usage: python3 -I live_urls.py <store_url> <theme_id> <out.json> [path ...]
"""
import json, re, sys, urllib.request, http.cookiejar

store, theme, out = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3]
paths = sys.argv[4:] or ['/']
jar = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.open(f'{store}/?preview_theme={theme}').read()
found = {}
rx = re.compile(r'https://cdn\.29next\.store/media/[^/]+/themes/%s/assets/([^"\'\s?,]+)' % theme)
for p in paths:
    html = op.open(store + p).read().decode('utf-8', 'ignore')
    for m in rx.finditer(html):
        served = m.group(1)
        plain = re.sub(r'_[A-Za-z0-9]{7}(\.[a-z0-9]+)$', r'\1', served)
        found[plain] = m.group(0)
json.dump(found, open(out, 'w'), indent=1)
print(len(found), 'assets resolved')
