"""Build an offline, rebranded export of the smooche.com homepage.
usage: python3 -I build.py <capture_dir> <out_dir> <logo.svg>"""
import sys, os, re, json, hashlib, shutil, urllib.parse as up
import requests
from bs4 import BeautifulSoup, Comment

CAP, OUT, LOGO = sys.argv[1:4]
BASE = 'https://smooche.com/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36',
      'Referer': BASE}
shutil.rmtree(OUT, ignore_errors=True)
for d in ('css', 'js', 'img', 'fonts', 'media'):
    os.makedirs(f'{OUT}/assets/{d}', exist_ok=True)

captured = {x['url']: x['file'] for x in json.load(open(f'{CAP}/manifest.json'))}
cache, failed = {}, []
sess = requests.Session()

def absu(u, base=BASE):
    u = u.strip().replace('&amp;', '&')
    if u.startswith('//'): u = 'https:' + u
    return up.urljoin(base, u)

NPM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npm/x')
if not os.path.isdir(NPM):  # vendor libs come from the npm registry (public CDNs may be unreachable)
    import subprocess
    os.makedirs(NPM, exist_ok=True)
    for pkg in ('swiper@9.4.1', 'jquery@3.7.1', 'js-cookie@3.0.1', '@fortawesome/fontawesome-free@6.6.0'):
        tgz = subprocess.check_output(['npm', 'pack', pkg, '--silent'], cwd=os.path.dirname(NPM), text=True).split()[-1]
        dest = f'{NPM}/{tgz[:-4]}'; os.makedirs(dest, exist_ok=True)
        subprocess.check_call(['tar', 'xzf', f'{os.path.dirname(NPM)}/{tgz}', '-C', dest])
VENDOR = {  # CDN prefix -> npm package dir (CDNs are unreachable here; npm registry is)
    'https://cdn.jsdelivr.net/npm/swiper@9/': f'{NPM}/swiper-9.4.1/package/',
    'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/': f'{NPM}/jquery-3.7.1/package/dist/',
    'https://cdn.jsdelivr.net/npm/js-cookie@3.0.1/': f'{NPM}/js-cookie-3.0.1/package/',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/': f'{NPM}/fortawesome-fontawesome-free-6.6.0/package/',
}

def fetch(url):
    for pre, d in VENDOR.items():
        if url.startswith(pre):
            return open(d + url[len(pre):].split('?')[0], 'rb').read()
    if url in captured and os.path.exists(f'{CAP}/raw/{captured[url]}'):
        return open(f'{CAP}/raw/{captured[url]}', 'rb').read()
    r = sess.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return r.content

EXT_DIR = {'.css': 'css', '.js': 'js', '.woff': 'fonts', '.woff2': 'fonts', '.ttf': 'fonts', '.otf': 'fonts',
           '.eot': 'fonts', '.mp4': 'media', '.webm': 'media', '.mov': 'media'}

def local_name(url, kind=None):
    p = up.urlparse(url)
    name = os.path.basename(p.path) or 'file'
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    if kind == 'css' and ext != '.css': ext = '.css'
    sub = EXT_DIR.get(ext, 'img')
    q = up.parse_qs(p.query)
    tag = f"-{q['width'][0]}w" if 'width' in q else ''
    h = hashlib.md5(url.encode()).hexdigest()[:6]
    stem = re.sub(r'[^A-Za-z0-9_-]+', '-', stem)[:60]
    return f'assets/{sub}/{stem}{tag}-{h}{ext or ".bin"}'

LOGO_MAP = {}  # filled below: substring -> local path

def get(url, kind=None, prefix=''):
    """Download url once, return path relative to the referencing file."""
    url = absu(url)
    for key, path in LOGO_MAP.items():
        if key in url: return prefix + path
    if url in cache: return prefix + cache[url] if cache[url] else url
    rel = local_name(url, kind)
    try:
        data = fetch(url)
    except Exception as e:
        failed.append((url, str(e)[:80])); cache[url] = None; return url
    cache[url] = rel
    if rel.endswith('.css'):
        data = process_css(data.decode('utf-8', 'replace'), url).encode()
    open(f'{OUT}/{rel}', 'wb').write(data)
    return prefix + rel

def process_css(css, base):
    def rep(m):
        u = m.group(2).strip()
        if u.startswith(('data:', '#')) or not u: return m.group(0)
        return f'url("{get(absu(u, base), prefix="../../")}")'
    css = re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', rep, css)
    def imp(m): return f'@import url("{get(absu(m.group(2), base), "css", "../../")}")'
    css = re.sub(r'@import\s+([\'"])([^\'"]+)\1', imp, css)
    return css

# ---------- logo ----------
logo_svg = open(LOGO).read()
logo_svg = re.sub(r'<\?xml.*?\?>|<!--.*?-->', '', logo_svg, flags=re.S).strip()
# crop the artboard padding (glyphs span x 6-494, y 10-89) so the mark fills the header slot like the original
logo_svg = re.sub(r'viewBox="[^"]*"', 'viewBox="5 9 490 81"', logo_svg, count=1)
logo_svg = re.sub(r'\s(?:x|y)="0px"|\sstyle="enable-background:[^"]*"|\sxml:space="preserve"', '', logo_svg)
open(f'{OUT}/assets/img/skinofab-logo.svg', 'w').write(logo_svg)
white = logo_svg.replace('<g>', '<g fill="#ffffff">', 1)
open(f'{OUT}/assets/img/skinofab-logo-white.svg', 'w').write(white)
LOGO_MAP.update({'Smooche_LOGO_final_Black': 'assets/img/skinofab-logo.svg',
                 'Smooche_LOGO_final_White': 'assets/img/skinofab-logo-white.svg'})

# ---------- html ----------
soup = BeautifulSoup(open(f'{CAP}/server.html', encoding='utf-8').read(), 'lxml')

KEEP_SRC = ('swiper-bundle', 'jquery.min.js', '/assets/vendor.js', '/assets/theme.js', '/assets/figma-home.js',
            'js.cookie', 'smooche-routine-upgrade.js', 'smooche-subscription-card-prices.js')
DROP_INLINE = ('Shopify.MCP', 'webmcp', 'klaviyo', 'TriplePixel', 'TREKKIE', 'wpmLoader', 'sendBeacon',
               'ShopifyAnalytics', 'cvg', 'eabUserId', 'Alia', 'ALBSS', 'loox', 'kaching', 'window.Instant',
               'nb__', '_0x', 'ShopifyPay', 'SignInWithShop', 'featureAssets', 'asyncLoad', 'var __st',
               'performance.mark', 'Shopify.PaymentButton', 'portableWallets', 'shopify-a', 'Paypal', 'SimpleBundles',
               'originalFetch', 'northbeam', 'Shopify.modules', 'import(', 'jsdeliver.cloud',
               'Shopify.shop', 'eab_data', 'accessToken', 'storefrontAccessToken', 'shopifyDomain', 'n.q=o')
for s in soup.find_all('script'):
    src, typ, txt = s.get('src'), (s.get('type') or ''), (s.string or '')
    if src:
        if any(k in src for k in KEEP_SRC):
            s['src'] = get(src, 'js'); s.attrs.pop('integrity', None); s.attrs.pop('crossorigin', None)
        else: s.decompose()
    elif 'ld+json' in typ or 'speculationrules' in typ or not txt.strip() or any(k in txt for k in DROP_INLINE):
        s.decompose()
    elif typ in ('', 'text/javascript', 'module'):
        # theme config lazy-loads a few theme assets (photoswipe, smoothscroll, swatches): localize them
        s.string = re.sub(r"//smooche\.com/cdn/shop/t/\d+/assets/[^'\"]+\.(?:js|json)\?v=\d+",
                          lambda m: get(m.group(0), 'js'), txt)

for c in soup.find_all(string=lambda t: isinstance(t, Comment)): c.extract()
for t in soup.find_all(['iframe', 'noscript']): t.decompose()
for l in soup.find_all('link'):
    rel = ' '.join(l.get('rel', []))
    if 'stylesheet' in rel and 'typekit' in l.get('href', ''):
        l['href'] = 'assets/css/futura-pt-fallback.css'; continue
    if 'stylesheet' in rel:
        if 'portable-wallets' in l.get('href', ''): l.decompose(); continue
        l['href'] = get(l['href'], 'css'); l.attrs.pop('integrity', None); l.attrs.pop('crossorigin', None)
        if l.get('media') == 'print': l['media'] = 'all'
        l.attrs.pop('onload', None)
    elif 'icon' in rel:
        l['href'] = 'assets/img/skinofab-logo.svg'; l['type'] = 'image/svg+xml'
    else:
        l.decompose()
for m in soup.find_all('meta'):
    if m.get('property', '').startswith(('og:', 'twitter:')) or m.get('name', '').startswith(('twitter:', 'shopify', 'google-site', 'facebook')):
        m.decompose()

def do_srcset(v):
    cands = [p.strip().split() for p in v.split(',') if p.strip()]
    ws = [(int(c[1][:-1]) if len(c) > 1 and c[1].endswith('w') else 0, c) for c in cands]
    if all(w for w, _ in ws) and len(ws) > 2:
        pick = {min(ws, key=lambda x: abs(x[0] - 800))[0], min(ws, key=lambda x: abs(x[0] - 1800))[0]}
        cands = [c for w, c in ws if w in pick]
    return ', '.join(' '.join([get(c[0])] + c[1:]) for c in cands)

URL_ATTRS = ('src', 'data-src', 'poster', 'data-poster', 'data-bgset', 'data-bg', 'data-image', 'data-video-src', 'data-mobile-src')
for el in soup.find_all(True):
    if el.get('src') and 'your-flame-image-url' in el['src']: el.decompose(); continue
    for a in URL_ATTRS:
        v = el.get(a)
        if v and not v.startswith(('data:', '#', 'javascript')) and el.name != 'script' and re.search(r'\.(jpe?g|png|gif|webp|avif|svg|mp4|webm|mov)|/cdn/|shopify', v, re.I):
            el[a] = get(v)
    for a in ('srcset', 'data-srcset'):
        if el.get(a): el[a] = do_srcset(el[a])
    if el.get('style') and 'url(' in el['style']:
        el['style'] = process_css(el['style'], BASE).replace('../../', '')
    if el.name == 'img' and el.get('alt', '').strip().lower() == 'smooche': el['alt'] = 'SKINOFAB'
    if el.name == 'a' and el.get('href'):
        h = el['href']
        if h.startswith(('/', BASE, 'https://www.smooche.com', '//smooche.com')): el['href'] = '#'
for st in soup.find_all('style'):
    if st.string and 'typekit' in st.string:  # licensed Adobe Fonts faces; replaced by futura-pt-fallback.css
        st.string = re.sub(r'@font-face\s*\{[^}]*typekit[^}]*\}', '', st.string)
    if st.string and 'url(' in st.string: st.string = process_css(st.string, BASE).replace('../../', '')

# Remove the cookie/privacy banner and app popups if present in server html
for sel in ['#shopify-pc__banner', '#shopify-pc__prefs', '[id^=klaviyo]', '.intercom-lightweight-app']:
    for e in soup.select(sel): e.decompose()

jost = sorted(f for f in os.listdir(f'{OUT}/assets/fonts') if f.startswith('jost_n') and f.endswith('.woff2'))
faces = []
for f in jost:
    w = int(re.match(r'jost_n(\d)', f).group(1)) * 100
    for fam in ('futura-pt', 'Futura PT Extra Bold' if w >= 800 else None, 'Futura Book' if w == 400 else None):
        if fam: faces.append(f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;font-display:swap;src:url("../fonts/{f}") format("woff2")}}')
open(f'{OUT}/assets/css/futura-pt-fallback.css', 'w').write('/* futura-pt (Adobe Fonts) -> Jost substitute */\n' + '\n'.join(faces) + '\n')
if soup.title: soup.title.string = 'SKINOFAB'
html = str(soup)
# Any remaining direct Smooche logo references (e.g. in JSON blobs)
html = re.sub(r'(?:https?:)?//smooche\.com/cdn/shop/files/Smooche_LOGO_final_Black-01\.svg[^"\' ]*', 'assets/img/skinofab-logo.svg', html)
html = re.sub(r'(?:https?:)?//smooche\.com/cdn/shop/files/Smooche_LOGO_final_White-02\.svg[^"\' ]*', 'assets/img/skinofab-logo-white.svg', html)
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(html)
print('assets', sum(1 for v in cache.values() if v), 'failed', len(failed))
for f in failed: print('  FAIL', *f)
