"""Export the smooche.com storefront (every page in its sitemap + policies) as an offline, SKINOFAB-branded static site.

usage: python3 -I build.py <out_dir> <logo.svg> [--only /path,/path]

Pipeline per page: fetch server HTML -> strip trackers/apps -> localize every image, video, font, stylesheet and theme
script into a shared assets/ store -> swap the logo -> rewrite internal links to the exported .html files.
"""
import sys, os, re, json, hashlib, shutil, subprocess, time, urllib.parse as up
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup, Comment

OUT, LOGO = sys.argv[1], sys.argv[2]
ONLY = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://smooche.com/'
HOSTS = ('smooche.com', 'www.smooche.com')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36',
      'Referer': BASE}
LOCALES = r'^/(?:de-de|en-de|en-nl|nl-nl)(?=/|$)'
sess = requests.Session()
sess.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=16, max_retries=3))

def http(url):
    for attempt in range(4):
        try:
            r = sess.get(url, headers=UA, timeout=90)
            if r.status_code in (429, 503): raise requests.HTTPError(str(r.status_code))
            r.raise_for_status()
            return r
        except Exception:
            if attempt == 3: raise
            time.sleep(2 ** attempt)

# ---------------------------------------------------------------- pages
EXTRA = ['/', '/blogs/news', '/cart', '/search', '/policies/terms-of-service', '/policies/privacy-policy',
         '/policies/refund-policy', '/policies/shipping-policy', '/policies/contact-information']

def discover():
    paths = set(EXTRA)
    for sm in re.findall(r'<loc>([^<]+)</loc>', http(BASE + 'sitemap.xml').text):
        sm = sm.replace('&amp;', '&')
        if re.search(r'smooche\.com/sitemap_(products|pages|collections|articles)_', sm):
            for loc in re.findall(r'<loc>([^<]+)</loc>', http(sm).text):
                p = up.urlparse(loc).path
                if p.startswith(('/products/', '/pages/', '/collections/', '/blogs/')): paths.add(p.rstrip('/'))
    return sorted(paths, key=lambda p: (p != '/', p))

def out_path(path):
    return 'index.html' if path == '/' else path.strip('/') + '.html'

# ---------------------------------------------------------------- assets
NPM = os.path.join(HERE, 'npm/x')
VENDOR_PKGS = ('swiper@9.4.1', 'jquery@3.7.1', 'js-cookie@3.0.1', '@fortawesome/fontawesome-free@6.6.0')
if not os.path.isdir(NPM):  # vendor libs come from the npm registry (public CDNs may be unreachable)
    os.makedirs(NPM, exist_ok=True)
    for pkg in VENDOR_PKGS:
        tgz = subprocess.check_output(['npm', 'pack', pkg, '--silent'], cwd=os.path.dirname(NPM), text=True).split()[-1]
        dest = f'{NPM}/{tgz[:-4]}'; os.makedirs(dest, exist_ok=True)
        subprocess.check_call(['tar', 'xzf', f'{os.path.dirname(NPM)}/{tgz}', '-C', dest])
VENDOR = {  # CDN prefix -> npm package dir
    'https://cdn.jsdelivr.net/npm/swiper@9/': f'{NPM}/swiper-9.4.1/package/',
    'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/': f'{NPM}/jquery-3.7.1/package/dist/',
    'https://cdn.jsdelivr.net/npm/js-cookie@3.0.1/': f'{NPM}/js-cookie-3.0.1/package/',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/': f'{NPM}/fortawesome-fontawesome-free-6.6.0/package/',
}
EXT_DIR = {'.css': 'css', '.js': 'js', '.json': 'js', '.woff': 'fonts', '.woff2': 'fonts', '.ttf': 'fonts',
           '.otf': 'fonts', '.eot': 'fonts', '.mp4': 'media', '.webm': 'media', '.mov': 'media', '.m4v': 'media'}
LOGO_MAP = {'Smooche_LOGO_final_Black': 'assets/img/skinofab-logo.svg',
            'Smooche_LOGO_final_White': 'assets/img/skinofab-logo-white.svg'}
cache, failed, by_base = {}, {}, {}

def absu(u, base=BASE):
    u = u.strip().replace('&amp;', '&')
    if u.startswith('//'): u = 'https:' + u
    return up.urljoin(base, u)

def local_name(url, kind=None):
    p = up.urlparse(url)
    stem, ext = os.path.splitext(os.path.basename(p.path) or 'file')
    ext = '.css' if kind == 'css' else ext.lower()
    q = up.parse_qs(p.query)
    tag = f"-{q['width'][0]}w" if 'width' in q else ''
    h = hashlib.md5(url.encode()).hexdigest()[:6]
    stem = re.sub(r'[^A-Za-z0-9_-]+', '-', stem)[:60]
    return f'assets/{EXT_DIR.get(ext, "img")}/{stem}{tag}-{h}{ext or ".bin"}'

def get(url, kind=None):
    """Download url once into the shared store; returns site-root-relative path (or the url if it failed)."""
    url = absu(url)
    for key, path in LOGO_MAP.items():
        if key in url: return path
    if url in cache: return cache[url] or url
    if 'your-flame-image-url' in url: cache[url] = None; return url
    rel = local_name(url, kind)
    try:
        vend = next((d + url[len(pre):].split('?')[0] for pre, d in VENDOR.items() if url.startswith(pre)), None)
        data = open(vend, 'rb').read() if vend else http(url).content
    except Exception as e:
        failed[url] = str(e)[:80]; cache[url] = None; return url
    cache[url] = rel
    if rel.endswith('.css'):
        data = process_css(data.decode('utf-8', 'replace'), url, '../../').encode()
    with open(f'{OUT}/{rel}', 'wb') as f: f.write(data)
    by_base.setdefault(up.urlparse(url).path, rel)
    return rel

def prefetch(urls):
    with ThreadPoolExecutor(12) as ex: list(ex.map(lambda u: get(u), {absu(u) for u in urls}))

def inline_var_urls(css, base):
    """url() inside a custom property resolves against the stylesheet that *uses* the var, not the page that
    declares it - so page-level `--icon: url(...)` would break. Embed those (small icons) as data URIs."""
    import base64
    def rep(m):
        u = m.group(3).strip()
        if u.startswith('data:'): return m.group(0)
        rel = get(absu(u, base))
        if not rel.startswith('assets/'): return m.group(0)
        data = open(f'{OUT}/{rel}', 'rb').read()
        mime = 'image/svg+xml' if rel.endswith('.svg') else 'image/' + rel.rsplit('.', 1)[-1].replace('jpg', 'jpeg')
        return f'{m.group(1)}url("data:{mime};base64,{base64.b64encode(data).decode()}")'
    return re.sub(r'(--[\w-]+\s*:\s*)url\(\s*([\'"]?)([^\'")]+)\2\s*\)', rep, css)

def process_css(css, base, prefix):
    css = re.sub(r'@font-face\s*\{[^}]*typekit[^}]*\}', '', css)  # licensed Adobe Fonts -> futura-pt-fallback.css
    css = inline_var_urls(css, base)
    def rep(m):
        u = m.group(2).strip()
        if not u or u.startswith(('data:', '#')): return m.group(0)
        r = get(absu(u, base))
        return f'url("{prefix + r if r.startswith("assets/") else r}")'
    css = re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', rep, css)
    def imp(m):
        r = get(absu(m.group(2), base), 'css')
        return f'@import url("{prefix + r if r.startswith("assets/") else r}")'
    return re.sub(r'@import\s+([\'"])([^\'"]+)\1', imp, css)

# ---------------------------------------------------------------- static extras
def write_static():
    shutil.rmtree(OUT, ignore_errors=True)
    for d in ('css', 'js', 'img', 'fonts', 'media'): os.makedirs(f'{OUT}/assets/{d}', exist_ok=True)
    svg = re.sub(r'<\?xml.*?\?>|<!--.*?-->', '', open(LOGO).read(), flags=re.S).strip()
    # crop the artboard padding (glyphs span x 6-494, y 10-89) so the mark fills the logo slot like the original
    svg = re.sub(r'viewBox="[^"]*"', 'viewBox="5 9 490 81"', svg, count=1)
    svg = re.sub(r'\s(?:x|y)="0px"|\sstyle="enable-background:[^"]*"|\sxml:space="preserve"', '', svg)
    open(f'{OUT}/assets/img/skinofab-logo.svg', 'w').write(svg)
    open(f'{OUT}/assets/img/skinofab-logo-white.svg', 'w').write(svg.replace('<g>', '<g fill="#ffffff">', 1))
    # Offline storefront shim: answer the theme's cart / section / recommendation XHRs locally so drawers,
    # add-to-cart and quick views degrade gracefully instead of throwing.
    open(f'{OUT}/assets/js/offline-shim.js', 'w').write(r'''/* SKINOFAB static export: local stand-ins for Shopify storefront endpoints */
(function () {
  var cart = {token: "", note: null, attributes: {}, original_total_price: 0, total_price: 0, total_discount: 0,
    total_weight: 0, item_count: 0, items: [], requires_shipping: false, currency: "USD", items_subtotal_price: 0,
    cart_level_discount_applications: []};
  function res(body, type) { return Promise.resolve(new Response(body, {status: 200, headers: {"Content-Type": type}})); }
  var native = window.fetch && window.fetch.bind(window);
  window.fetch = function (input, init) {
    var u = typeof input === "string" ? input : (input && input.url) || "";
    if (/[?&]sections?=/.test(u)) return res("{}", "application/json");
    if (/\/cart(\/(add|change|update|clear))?(\.js)?(\?|$)/.test(u)) return res(JSON.stringify(cart), "application/json");
    if (/\/(recommendations|search\/suggest)|[?&]section_id=/.test(u)) return res("", "text/html");
    if (/browsing_context_suggestions\.json/.test(u)) return res("{}", "application/json");
    return native(input, init);
  };
})();
''')

def write_font_fallback():
    jost = sorted(f for f in os.listdir(f'{OUT}/assets/fonts') if re.match(r'jost_n\d.*\.woff2$', f))
    faces = []
    for f in jost:
        w = int(re.match(r'jost_n(\d)', f).group(1)) * 100
        for fam in ('futura-pt', 'Futura PT Extra Bold' if w >= 800 else None, 'Futura Book' if w == 400 else None):
            if fam: faces.append(f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;'
                                 f'font-display:swap;src:url("../fonts/{f}") format("woff2")}}')
    open(f'{OUT}/assets/css/futura-pt-fallback.css', 'w').write(
        '/* futura-pt (Adobe Fonts, licensed) -> Jost substitute */\n' + '\n'.join(faces) + '\n')

# ---------------------------------------------------------------- html
THEME_JS = re.compile(r'/cdn/shop/t/\d+/assets/[^?]+\.js')
DROP_THEME_JS = ('ie11.js', 'smooche-california-msrp')  # IE polyfill; geo-IP price lookup
DROP_INLINE = ('Shopify.MCP', 'webmcp', 'klaviyo', 'TriplePixel', 'TREKKIE', 'wpmLoader', 'sendBeacon',
               'ShopifyAnalytics', 'cvg', 'eabUserId', 'Alia', 'ALBSS', 'loox', 'kaching', 'window.Instant',
               'nb__', '_0x', 'ShopifyPay', 'SignInWithShop', 'featureAssets', 'asyncLoad', 'var __st',
               'performance.mark', 'Shopify.PaymentButton', 'portableWallets', 'shopify-a', 'Paypal', 'SimpleBundles',
               'originalFetch', 'northbeam', 'Shopify.modules', 'import(', 'jsdeliver.cloud',
               'Shopify.shop', 'eab_data', 'accessToken', 'storefrontAccessToken', 'shopifyDomain', 'n.q=o',
               'gtag(', 'fbq(', 'ttq.', 'dataLayer', 'hotjar', 'clarity', 'pintrk', 'snaptr', 'rdt(', 'intercom',
               'Intercom', 'attentive', 'postscript', 'okendo', 'yotpo', 'judge.me', 'gorgias', 'rebuy', 'checkoutchamp',
               'thefrontrowhealth', 'nfcube', 'instafeed')
URL_ATTRS = ('src', 'data-src', 'poster', 'data-poster', 'data-bgset', 'data-bg', 'data-image', 'data-video-src',
             'data-mobile-src', 'data-desktop-src', 'data-zoom', 'data-zoom-src', 'data-large', 'href')
MEDIA_RE = re.compile(r'\.(jpe?g|png|gif|webp|avif|svg|mp4|webm|mov|m4v)(\?|$)|/cdn/shop/(files|products|videos|t/)', re.I)
CDN_MEDIA = re.compile(r'(?:https?:)?(?:\\?/){2}(?:smooche\.com|cdn\.shopify\.com)(?:\\?/)[^"\'\s<>)]+?'
                       r'\.(?:jpe?g|png|gif|webp|avif|svg|mp4|webm|mov|m4v)(?:\?[^"\'\s<>)]*)?(?=["\'\s<>)])', re.I)

def asset_urls(soup):
    urls = set()
    for el in soup.find_all(True):
        for a in URL_ATTRS:
            v = el.get(a)
            if a == 'href' and el.name != 'link': continue
            if v and not v.startswith(('data:', '#', 'javascript', 'mailto')) and MEDIA_RE.search(v): urls.add(v)
        for a in ('srcset', 'data-srcset'):
            if el.get(a): urls.update(c[0] for c in pick_srcset(el[a]))
    return urls

def pick_srcset(v):
    """Keep at most two candidates (~800w for mobile, ~1800w for desktop) to keep the export lean."""
    cands = [p.strip().split() for p in v.split(',') if p.strip()]
    ws = [(int(c[1][:-1]) if len(c) > 1 and re.fullmatch(r'\d+w', c[1]) else 0, c) for c in cands]
    if all(w for w, _ in ws) and len(ws) > 2:
        keep = {min(ws, key=lambda x: abs(x[0] - 800))[0], min(ws, key=lambda x: abs(x[0] - 1800))[0]}
        cands = [c for w, c in ws if w in keep]
    return cands

def build_page(path, html, pages):
    page_file = out_path(path)
    root = os.path.relpath('.', os.path.dirname(page_file) or '.')
    pre = '' if root == '.' else root + '/'
    def L(rel): return pre + rel if rel.startswith('assets/') else rel

    soup = BeautifulSoup(html, 'lxml')
    for s in soup.find_all('script'):
        src, typ, txt = s.get('src'), (s.get('type') or ''), (s.string or '')
        if src:
            a = absu(src)
            if (THEME_JS.search(a) and not any(k in a for k in DROP_THEME_JS)) or any(a.startswith(p) for p in VENDOR):
                s['src'] = L(get(a, 'js'))
                for k in ('integrity', 'crossorigin'): s.attrs.pop(k, None)
            else: s.decompose()
        elif 'ld+json' in typ or 'speculationrules' in typ or not txt.strip() or any(k in txt for k in DROP_INLINE):
            s.decompose()
        else:
            # theme config lazy-loads a few theme assets (photoswipe, smoothscroll, swatches): localize them
            s.string = re.sub(r"//smooche\.com/cdn/shop/t/\d+/assets/[^'\"]+\.(?:js|json)\?v=\d+",
                              lambda m: L(get(m.group(0), 'js')), txt)
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)): c.extract()
    for t in soup.find_all(['iframe', 'noscript']): t.decompose()
    for m in soup.find_all('meta'):
        if (m.get('property', '').startswith(('og:', 'twitter:')) or
                m.get('name', '').startswith(('twitter:', 'shopify', 'google-site', 'facebook', 'apple-itunes'))):
            m.decompose()

    prefetch(asset_urls(soup))
    for l in soup.find_all('link'):
        rel = ' '.join(l.get('rel', []))
        href = l.get('href', '')
        if 'stylesheet' in rel and 'typekit' in href:
            l['href'] = L('assets/css/futura-pt-fallback.css')
        elif 'stylesheet' in rel and 'portable-wallets' not in href:
            l['href'] = L(get(href, 'css'))
            for k in ('integrity', 'crossorigin', 'onload'): l.attrs.pop(k, None)
            if l.get('media') == 'print': l['media'] = 'all'
        elif 'icon' in rel:
            l['href'] = L('assets/img/skinofab-logo.svg'); l['type'] = 'image/svg+xml'
        else:
            l.decompose()

    for el in soup.find_all(True):
        if el.attrs is None: continue
        if el.name == 'img' and 'your-flame-image-url' in el.get('src', ''): el.decompose(); continue
        for a in URL_ATTRS:
            v = el.get(a)
            if a == 'href': continue
            if v and not v.startswith(('data:', '#', 'javascript')) and MEDIA_RE.search(v): el[a] = L(get(v))
        for a in ('srcset', 'data-srcset'):
            if el.get(a): el[a] = ', '.join(' '.join([L(get(c[0]))] + c[1:]) for c in pick_srcset(el[a]))
        if el.get('style') and 'url(' in el['style']: el['style'] = process_css(el['style'], BASE, pre)
        if el.name == 'img' and el.get('alt', '').strip().lower() == 'smooche': el['alt'] = 'SKINOFAB'
        if el.name == 'a' and el.get('href'): el['href'] = map_link(el['href'], page_file, pages)
        if el.name == 'form' and el.get('action'): el['action'] = map_link(el['action'], page_file, pages)
    for st in soup.find_all('style'):
        if st.string and ('url(' in st.string or 'typekit' in st.string):
            st.string = process_css(st.string, BASE, pre)

    for sel in ('#shopify-pc__banner', '#shopify-pc__prefs', '[id^=klaviyo]', '.intercom-lightweight-app',
                'shopify-accelerated-checkout', 'shopify-accelerated-checkout-cart', '.shopify-payment-button'):
        for e in soup.select(sel): e.decompose()
    head = soup.head or soup
    shim = soup.new_tag('script', src=L('assets/js/offline-shim.js'))
    head.insert(0, shim)
    if soup.title and soup.title.string:
        soup.title.string = re.sub(r'(?i)smooche', 'SKINOFAB', soup.title.string)
    return page_file, pre, str(soup)

def map_link(h, page_file, pages):
    if h.startswith(('#', 'mailto:', 'tel:', 'javascript:')): return h
    u = up.urlparse(absu(h))
    if u.netloc not in HOSTS:
        return '#' if 'smooche' in u.netloc + u.path.lower() else h  # brand-owned socials/apps
    p = re.sub(LOCALES, '', u.path).rstrip('/') or '/'
    p = re.sub(r'^/collections/[^/]+(?=/products/)', '', p)
    if p in pages:
        rel = os.path.relpath(out_path(p), os.path.dirname(page_file) or '.')
        return rel + (f'#{u.fragment}' if u.fragment else '')
    return '#'

def finalize(html, pre):
    """Localize media URLs embedded in JSON/JS blobs (product galleries, variant images) and stray logo refs."""
    def rep(m):
        raw = m.group(0)
        u = absu(raw.replace('\\/', '/'))
        for key, path in LOGO_MAP.items():
            if key in u: return pre + path
        hit = cache.get(u) or by_base.get(up.urlparse(u).path)
        if not hit: return raw
        return (pre + hit).replace('/', '\\/') if '\\/' in raw else pre + hit
    return CDN_MEDIA.sub(rep, html)

def main():
    write_static()
    pages = discover()
    if ONLY: pages = [p for p in pages if p in ONLY or p == '/']
    pageset = set(pages)
    print(f'{len(pages)} pages')
    built, errors = [], {}
    for i, path in enumerate(pages, 1):
        try:
            html = http(BASE.rstrip('/') + path).text
            page_file, pre, out = build_page(path, html, pageset)
            built.append((page_file, pre, out))
            print(f'[{i}/{len(pages)}] {path} -> {page_file}', flush=True)
        except Exception as e:
            errors[path] = repr(e)[:120]; print(f'[{i}/{len(pages)}] {path} FAILED {e}', flush=True)
        if i == 1: write_font_fallback()
    for page_file, pre, out in built:
        os.makedirs(os.path.dirname(f'{OUT}/{page_file}'), exist_ok=True)
        with open(f'{OUT}/{page_file}', 'w', encoding='utf-8') as f: f.write(finalize(out, pre))
    json.dump({'pages': [b[0] for b in built], 'page_errors': errors, 'asset_failures': failed},
              open(f'{OUT}/export-manifest.json', 'w'), indent=1)
    print(f'pages {len(built)}  page errors {len(errors)}  assets {sum(1 for v in cache.values() if v)}  '
          f'asset failures {len(failed)}')
    for u, e in list(failed.items())[:20]: print('  FAIL', u[:110], e)

main()
