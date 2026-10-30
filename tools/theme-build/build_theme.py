"""Generate the SKINOFAB Next Commerce theme (Spark fork) from the static site export.

usage: python3 -I build_theme.py <export_dir> <spark_dir> <out_theme_dir> <handoff_dir>

The export (skinofab-site/) is the design source: every page's markup, CSS, JS, images, videos and icons.
Spark is the platform runtime: SEO, pixels, app hooks, GraphQL cart, side cart, preview indicator.
Commerce facts come from NEXT: product links, prices, variants and add-to-cart are bound with DTL.

Re-run after any design change; every template in the family is regenerated identically.
"""
import hashlib, html, json, os, posixpath, re, shutil, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment

EXPORT, SPARK, OUT, HANDOFF = (Path(p).resolve() for p in sys.argv[1:5])
HERE = Path(__file__).resolve().parent
VARIANT2HANDLE = {}  # Shopify variant/product id in the design markup -> product handle
SHIPPING_PROTECTION = 'smooche-premium-shipping-protection'
LOG = {'unbound_prices': [], 'missing_assets': set(), 'templates': [], 'unmapped_links': set()}

def must_replace(text, old, new, what):
    """str.replace that fails the build when the anchor is missing (a Spark or design update moved it)."""
    if old not in text: sys.exit(f'build: anchor for {what} not found')
    return text.replace(old, new, 1)

# ---------------------------------------------------------------- 1. Spark baseline
SPARK_KEEP = ['assets', 'configs', 'layouts', 'locales', 'partials', 'templates', 'css', 'scripts', 'Makefile',
              'manifest.json', 'theme-contract.json', 'LICENSE', 'DESIGN.md', 'config.example.yml', '.gitignore']
keep = (OUT / 'config.yml').read_bytes() if (OUT / 'config.yml').exists() else None  # ntk store binding
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
if keep is not None: (OUT / 'config.yml').write_bytes(keep)
for name in SPARK_KEEP:
    src = SPARK / name
    if src.is_dir(): shutil.copytree(src, OUT / name)
    elif src.exists(): shutil.copy2(src, OUT / name)

# ---------------------------------------------------------------- 2. assets
ASSET_RE = re.compile(r'(?:\.\./)*/?assets/(img|media|fonts|css|js)/([A-Za-z0-9._-]+\.[A-Za-z0-9]+)')
AMAP = {}  # 'img/x.png' -> 'sf/img/x.png'
for sub in ('img', 'media', 'fonts', 'css', 'js'):
    for f in sorted((EXPORT / 'assets' / sub).glob('*')):
        if f.is_file(): AMAP[f'{sub}/{f.name}'] = f'sf/{sub}/{f.name}'

def asset_dtl(sub, name):
    key = f'{sub}/{name}'
    if name.startswith('skinofab-logo'): key = f'img/{name}'
    if key not in AMAP:
        LOG['missing_assets'].add(key); return None
    return "{{ '%s'|asset_url }}" % AMAP[key]

# DTL escaping: content is literal; only openers need escaping. Placeholders carry generated DTL.
OPENERS = {'{%': '{% templatetag openblock %}', '{{': '{% templatetag openvariable %}', '{#': '{% templatetag opencomment %}'}
def dtl_escape(text):
    return re.sub(r'\{[%{#]', lambda m: OPENERS[m.group(0)], text)

# Generated DTL placed before a fragment has its Slots (clean_design runs on the whole page): one shared table,
# keyed by content, resolved by every Slots.render.
PAGE_DTL = {}
def page_dtl(dtl):
    key = hashlib.md5(dtl.encode()).hexdigest()[:10]
    PAGE_DTL[key] = dtl
    return f'SFDTL{key}X'

class Slots:
    """Collects generated DTL behind inert placeholders so escaping never touches it."""
    def __init__(self): self.items = []
    def put(self, dtl): self.items.append(dtl); return f'SFSLOT{len(self.items) - 1}X'
    def render(self, text):
        text = re.sub(r'SFSLOT(\d+)X', lambda m: self.items[int(m.group(1))], dtl_escape(text))
        return re.sub(r'SFDTL([0-9a-f]{10})X', lambda m: PAGE_DTL[m.group(1)], text)

def assetize(text, slots):
    """Replace every local asset path in `text` with a slot holding its asset_url tag."""
    def rep(m):
        d = asset_dtl(m.group(1), m.group(2))
        return slots.put(d) if d else m.group(0)
    return ASSET_RE.sub(rep, text)

FONT_FACES, CSS_VARS = [], {}
def css_rel_to_root(text):
    """Resolve url(...) paths relative to assets/css/ (e.g. ../fonts/x.woff2) to their assets/<dir>/ form."""
    def rep(m):
        q, u = m.group(1), m.group(2).strip()
        if re.match(r'^(data:|https?:|//|#|var\()', u) or u.startswith('assets/') or '/assets/' in u: return m.group(0)
        norm = posixpath.normpath(posixpath.join('assets/css', u))
        return f'url({q}{norm}{q})' if norm.startswith('assets/') else m.group(0)
    return re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', rep, text)

def strip_balanced_blocks(css, head_re):
    """Remove at-rule blocks whose prelude matches head_re, braces balanced."""
    out, i = [], 0
    for m in re.finditer(head_re, css):
        if m.start() < i: continue
        j = css.find('{', m.end() - 1)
        if j < 0: break
        depth, k = 0, j
        while k < len(css):
            if css[k] == '{': depth += 1
            elif css[k] == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        out.append(css[i:m.start()]); i = k + 1
    out.append(css[i:])
    return ''.join(out)

def balance_braces(css):
    """Drop closing braces with no opener (browsers ignore them; the platform's Sass compiler rejects them)."""
    out, depth, i, n = [], 0, 0, len(css)
    while i < n:
        c = css[i]
        if css.startswith('/*', i):
            j = css.find('*/', i + 2); j = n if j < 0 else j + 2
            out.append(css[i:j]); i = j; continue
        if c in '"\'':
            j = i + 1
            while j < n and css[j] != c:
                j += 2 if css[j] == '\\' else 1
            out.append(css[i:j + 1]); i = j + 1; continue
        if c == '{': depth += 1
        elif c == '}':
            if depth == 0: i += 1; continue
            depth -= 1
        out.append(c); i += 1
    return ''.join(out)

SASS_FN = re.compile(r'(?<![\w$-])(min|max|clamp|rgba?|hsla?|invert|grayscale|saturate|opacity|alpha)\(', re.I)

def split_args(inner):
    args, depth, cur = [], 0, ''
    for ch in inner:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == ',' and depth == 0: args.append(cur); cur = ''
        else: cur += ch
    return args + [cur]

ARITH = re.compile(r'\s[-+*/]\s|[\d.%a-z)]\s*[*/]\s*[\d.(]', re.I)

def sass_passthrough(css):
    """NEXT validates theme CSS with a Sass compiler but serves the file as written, so the CSS must be valid for
    both. Sass evaluates min()/max()/clamp()/rgb()/... itself and rejects var()/calc()/mixed units inside them, so
    those calls are emitted with a capitalised name (Min(, Clamp(, Rgba(...): CSS function names are
    case-insensitive for browsers, while Sass treats an unknown name as a plain CSS function. Arithmetic arguments
    of min/max/clamp are wrapped in calc() so neither side has to evaluate them."""
    out, i = [], 0
    while True:
        m = SASS_FN.search(css, i)
        if not m: out.append(css[i:]); break
        depth, k = 0, m.end() - 1
        while k < len(css):
            if css[k] == '(': depth += 1
            elif css[k] == ')':
                depth -= 1
                if depth == 0: break
            elif css[k] in '{};': k = -1; break
            k += 1
        if k < 0 or k >= len(css):
            out.append(css[i:m.end()]); i = m.end(); continue
        name = m.group(1).lower()
        args = []
        for a in split_args(css[m.end():k]):
            a = sass_passthrough(a)
            if name in ('min', 'max', 'clamp') and ARITH.search(a) and not re.fullmatch(r'\s*[\w-]+\(.*\)\s*', a, re.S):
                a = f'calc({a.strip()})'
            args.append(a)
        out.append(css[i:m.start()])
        out.append(name[0].upper() + name[1:] + '(' + ','.join(args) + ')')
        i = k + 1
    return ''.join(out)

def platform_safe_css(css):
    """NEXT compiles theme CSS with a Sass compiler. Keep the design CSS byte-for-byte equivalent for browsers while
    avoiding constructs Sass evaluates or cannot parse:
      - min()/max()/clamp()/rgb()/rgba()/hsl()/hsla() collide with Sass built-ins: CSS function names are
        case-insensitive, Sass's are not, so upper-casing them passes them through unevaluated;
      - @supports not (selector(...)) blocks (old-browser fallbacks Sass cannot parse) are dropped;
      - DTL openers get a space after the brace (equivalent CSS);
      - unmatched closing braces are dropped."""
    css = strip_balanced_blocks(css, r'@supports\s+not\s*\(\s*selector\(')
    css = sass_passthrough(css)
    css = re.sub(r'\{(?=[%{#])', '{ ', css)
    return balance_braces(css)

def process_css_asset(text, name):
    text = css_rel_to_root(text)
    def font_face(m):
        block = m.group(0)
        if not ASSET_RE.search(block): return block
        FONT_FACES.append(block); return ''
    text = re.sub(r'@font-face\s*\{[^}]*\}', font_face, text)
    def url_rep(m):
        inner = m.group(2).strip()
        am = ASSET_RE.search(inner)
        if not am or inner.startswith('data:'): return m.group(0)
        key = f'{am.group(1)}/{am.group(2)}'
        var = '--sfu-' + re.sub(r'[^a-z0-9]+', '-', posixpath.splitext(am.group(2))[0].lower())[:48]
        CSS_VARS[var] = key
        return f'var({var})'
    text = re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', url_rep, text)
    text = re.sub(r'/\*#\s*sourceMappingURL=[^*]*\*/', '', text)
    return platform_safe_css(text)

def process_js_asset(text):
    text = re.sub(r'//# sourceMappingURL=\S+', '', text)
    def esc(ch):
        o = ord(ch)
        if o < 0x10000: return '\\u%04x' % o
        o -= 0x10000
        return '\\u%04x\\u%04x' % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF))
    text = ''.join(c if ord(c) < 128 else esc(c) for c in text)
    return dtl_escape(text)

for key, dest in AMAP.items():
    src = EXPORT / 'assets' / key
    out = OUT / 'assets' / dest
    out.parent.mkdir(parents=True, exist_ok=True)
    if key.startswith('css/'):
        out.write_text(process_css_asset(src.read_text('utf-8', 'replace'), src.name), 'utf-8')
    elif key.startswith('js/'):
        out.write_text(process_js_asset(src.read_text('utf-8', 'replace')), 'utf-8')
    else:
        shutil.copy2(src, out)
for js in ('offline-shim.js',):  # replaced by the commerce adapter
    (OUT / 'assets' / 'sf' / 'js' / js).unlink(missing_ok=True)
shutil.copy2(HERE / 'static' / 'skinofab-commerce.js', OUT / 'assets' / 'js' / 'skinofab-commerce.js')
import hashlib
def static_asset(name):
    """Copy tools/theme-build/static/<name> into the theme under a content-hashed name (the CDN caches by name)."""
    data = (HERE / 'static' / name).read_bytes()
    stem, ext = posixpath.splitext(name)
    rel = f'sf/img/{stem}-{hashlib.md5(data).hexdigest()[:6]}{ext}'
    (OUT / 'assets' / rel).write_bytes(data)
    return rel
FAVICON = {n: static_asset(f'skinofab-favicon{n}') for n in ('.svg', '-32.png', '-180.png')}
# the product sheet's bottle views, which no page shows: Genjutsu reads them from the theme CDN as the swap references
# (tools/persona/queue/genjutsu-queue.json), so they keep their fixed names
for f in sorted((HERE.parents[1] / 'brand' / 'adaptive-peptide-foundation' / 'sheet').glob('*.jpg')):
    shutil.copy2(f, OUT / 'assets' / f'skf-sheet-{f.name}')
CART_BOTTLE = static_asset('skinofab-cart-bottle.png')
# the side cart's renderer (Spark's drawer keeps state and mutations; this draws it in SKINOFAB's look)
shutil.copy2(HERE / 'static' / 'skinofab-cart-drawer.js', OUT / 'assets' / 'js' / 'skinofab-cart-drawer.js')
# Spark's cart loader fetched the drawer's six scripts one after another, and only once the add had come back from the
# server: the drawer opened 1.5 s after the click (2.7 s on a phone). The scripts now download together (still run in
# order: async=false) and are fetched ahead: once the page is idle where it has a buy button, else on the first touch
# of a buy or cart control. skinofab-commerce.js opens the drawer at the click.
loader_f = OUT / 'assets' / 'js' / 'spark-cart-loader.js'
loader = loader_f.read_text()
loader = must_replace(loader, """        drawerPromise = loadCartClient()
            .then(function() { return loadScript('cartRewards', 'SparkCartRewards'); })
            .then(function() { return loadScript('cartRenderer', 'SparkCartDrawerRenderer'); })
            .then(function() { return loadScript('progressBar'); })
            .then(function() { return loadScript('upsellItem'); })
            .then(function() { return loadScript('cartDrawer'); })
            .then(waitForDrawerUpgrade)""", """        /* all at once: async=false scripts download in parallel and still run in insertion order */
        drawerPromise = Promise.all([
                loadCartClient(),
                loadScript('cartRewards', 'SparkCartRewards'),
                loadScript('cartRenderer', 'SparkCartDrawerRenderer'),
                loadScript('progressBar'),
                loadScript('upsellItem'),
                loadScript('cartDrawer')
            ])
            .then(waitForDrawerUpgrade)""", 'cart loader: parallel drawer stack')
loader = must_replace(loader, """    window.SparkCartLoader = {""", """    /* the drawer ready before the shopper asks for it: after load, when the page is idle (pages with a buy button),
       or on the first touch of a buy or cart control (any page) */
    var warmed = false;
    function warm() {
        if (warmed) return;
        warmed = true;
        ensureDrawer().catch(function(err) { warmed = false; reportError('drawer warm-up failed', err, 'warn'); });
    }
    var INTENT = '[data-add-to-cart], [data-cart-drawer-toggle], a[href="#cart-modal"], .cart__toggle, #cart-icon, a[href*="#apf-buy"]';
    ['pointerover', 'pointerdown', 'touchstart', 'focusin'].forEach(function(type) {
        document.addEventListener(type, function(e) {
            if (!warmed && e.target && e.target.closest && e.target.closest(INTENT)) warm();
        }, { passive: true, capture: true });
    });
    function whenIdle() {
        if (!document.querySelector('[data-add-to-cart], form[data-product-form]')) return;
        if (window.requestIdleCallback) requestIdleCallback(warm, { timeout: 2500 });
        else setTimeout(warm, 1200);
    }
    if (document.readyState === 'complete') whenIdle();
    else window.addEventListener('load', whenIdle);

    window.SparkCartLoader = {
        warm: warm,""", 'cart loader: warm-up')
loader_f.write_text(loader)
# A first add made two round trips (createCart, then addCartLines). The storefront API's createCart takes the lines:
# one request creates the cart with the item. A saved cart still takes addCartLines, a consumed one still recreates.
# The platform's /csrf/ (which sets the cookie the cart's requests carry) answered 502 now and then (2 loads in 85,
# review 5): one retry after a moment, so a first add to the cart still has its token
plat_f = OUT / 'assets' / 'js' / 'spark-platform.js'
plat_f.write_text(must_replace(plat_f.read_text(), "            var response = await fetch('/csrf/', { credentials: 'same-origin' });",
                               "            var response = await fetch('/csrf/', { credentials: 'same-origin' });\n"
                               "            if (!response.ok) {\n"
                               "                await new Promise(function(r) { setTimeout(r, 700); });\n"
                               "                response = await fetch('/csrf/', { credentials: 'same-origin' });\n"
                               "            }", 'platform: csrf retry'))
cart_f = OUT / 'assets' / 'js' / 'spark-cart.js'
cart_js = cart_f.read_text()
# The side cart's line photos: a 150 px cut, shown 88 px wide, was soft at 2x and 3x and its bottle's label smeared
# into "PDRH" (review 5): cut at 300 px
cart_js = must_replace(cart_js, "primaryImage { thumbnail: url(transform: { maxWidth: 150, maxHeight: 150, format: webp, crop: center }) }",
                       "primaryImage { thumbnail: url(transform: { maxWidth: 300, maxHeight: 300, format: webp, crop: center }) }",
                       'cart client: line photo size')
# A refused code came back as {success: false, errors: {nonFieldErrors: [[{message, code}]]}}: not a list, so the
# drawer took it for a success, redrew itself and the code's field closed with no word said (review 5); and the cart
# event went out as if it had changed. The errors are now a list of messages, in the store's words for an unknown code.
cart_js = must_replace(cart_js, """            var result = data.addVoucher;
            if (isCartNotFoundResult(result)) {
                clearCartId();
                return result;
            }
            if (result && result.cart) {
                self._dispatchCartUpdated(result.cart, 'voucher_add');
            }
            return result;""", """            var result = data.addVoucher;
            if (isCartNotFoundResult(result)) {
                clearCartId();
                return result;
            }
            if (result && result.success === false) {
                var msgs = [];
                (function walk(e) {
                    if (!e) return;
                    if (typeof e === 'string') msgs.push(e);
                    else if (Array.isArray(e)) e.forEach(walk);
                    else if (e.code === 'voucher_not_found') msgs.push('That code isn\u2019t valid. Check the spelling and try again.');
                    else if (e.message) msgs.push(e.message);
                    else Object.keys(e).forEach(function(k) { walk(e[k]); });
                })(result.errors);
                return { success: false, errors: msgs.length ? msgs : ['That code isn\u2019t valid.'], cart: null };
            }
            if (result && result.cart) {
                self._dispatchCartUpdated(result.cart, 'voucher_add');
            }
            return result;""", 'cart client: refused voucher')
cart_js = must_replace(cart_js, """            var input = {
                cartId: cartId,
                lines: [lineInput]
            };""", """            /* no cart yet: createCart takes the lines, one round trip instead of two */
            var create = !cartId;
            var input = create ? { lines: [lineInput] } : { cartId: cartId, lines: [lineInput] };""", 'cart client: create with lines')
cart_js = must_replace(cart_js, "return self._request(ADD_CART_LINES, { input: input }).then(function(data) {",
                       "return self._request(create ? CREATE_CART : ADD_CART_LINES, { input: input }).then(function(data) {",
                       'cart client: create mutation')
cart_js = must_replace(cart_js, "var result = outcome.data.addCartLines;",
                       "var result = create ? outcome.data.createCart : outcome.data.addCartLines;", 'cart client: create result')
cart_js = must_replace(cart_js, """        function recreateAndRetry() {
            clearCartId();
            return self.createCart().then(function(cart) {
                return doAdd(cart.id, false);
            });
        }""", """        function recreateAndRetry() {
            clearCartId();
            return doAdd(null, false);
        }""", 'cart client: recreate with lines')
cart_js = must_replace(cart_js, """        return this.createCart().then(function(cart) {
            return doAdd(cart.id, false);
        });""", """        return doAdd(null, false);""", 'cart client: first add')
# a line's product is the variant: its url is the store's primary domain's (another host, where the bag is empty) and
# the variant's page only redirects to the product's. The drawer links the product's page, on this host.
cart_js = must_replace(cart_js, "'    parent { pk title metadata }',", "'    parent { pk title url metadata }',", 'cart client: parent url')
cart_f.write_text(cart_js)

# product JSON snapshots (colour swatches on cards fetch /products/<handle>.js)
PRODUCT_JSON = {}
(OUT / 'assets' / 'sf' / 'data').mkdir(parents=True, exist_ok=True)
for f in sorted((EXPORT / 'products').glob('*.js')):
    data = json.loads(f.read_text())
    PRODUCT_JSON[f.stem] = data
    VARIANT2HANDLE[str(data.get('id'))] = f.stem
    for v in data.get('variants', []): VARIANT2HANDLE[str(v.get('id'))] = f.stem
    txt = json.dumps(data, ensure_ascii=True)
    txt = re.sub(r'(?:https?:)?/assets/(img|media)/([A-Za-z0-9._-]+)', lambda m: f'/assets/{m.group(1)}/{m.group(2)}', txt)
    (OUT / 'assets' / 'sf' / 'data' / f'product-{f.stem}.json').write_text(dtl_escape(txt))

# ---------------------------------------------------------------- 3. routing of design links to NEXT
EXPORTED = {str(p.relative_to(EXPORT)) for p in EXPORT.rglob('*.html')}
PAGE_SLUGS = {p[len('pages/'):-5] for p in EXPORTED if p.startswith('pages/')}
POLICY_ONLY = {p[len('policies/'):-5] for p in EXPORTED if p.startswith('policies/')} - PAGE_SLUGS
var = lambda h: re.sub(r'[^a-z0-9]+', '_', h.lower()).strip('_')

def link_dtl(href, page):
    if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'http://', 'https://', '//', 'data:')):
        return None
    path, _, frag = href.partition('#')
    path = path.split('?')[0]
    if path.startswith('/'):  # root-relative storefront paths in the design markup
        bare = path.strip('/')
        if bare in ('cart', 'cart/'): return '#cart-modal'
        if bare == 'checkout': return "{% url 'checkout:index' %}"
        if bare in ('', 'index'): return "{{ homepage_url|default:'/' }}"
        if bare == 'search': return "{% url 'search:search' %}"
        if bare == 'accounts' or bare.startswith('accounts/'): return "{% url 'customer:summary' %}"   # NEXT account pages (subscriptions live there)
        if re.fullmatch(r'(products|collections|pages|policies|blogs/news)/[a-z0-9][a-z0-9-]*|blogs/news', bare):
            path, page = bare + '.html', 'index.html'
        else:
            return None
    norm = posixpath.normpath(posixpath.join(posixpath.dirname(page), path)) if path else page
    frag = f'#{frag}' if frag else ''
    if norm in ('index.html', '.'): return "{{ homepage_url|default:'/' }}" + frag
    m = re.fullmatch(r'products/([a-z0-9][a-z0-9-]*)\.html', norm)
    if m:
        v = var(m.group(1))
        return ("{%% if settings.sf_p_%s %%}{{ settings.sf_p_%s.get_absolute_url }}{%% else %%}{%% url 'catalogue:index' %%}{%% endif %%}"
                % (v, v)) + frag
    m = re.fullmatch(r'collections/([a-z0-9][a-z0-9-]*)\.html', norm)
    if m:
        if m.group(1) in ('all', 'all-products'): return "{% url 'catalogue:index' %}" + frag
        return "{{ settings.sf_c_%s|default:'/catalogue/' }}" % var(m.group(1)) + frag
    m = re.fullmatch(r'(pages|policies)/([a-z0-9][a-z0-9-]*)\.html', norm)
    if m: return f'/{m.group(2)}/' + frag
    if norm == 'blogs/news.html': return "{% url 'blog:blog-list' %}" + frag
    m = re.fullmatch(r'blogs/news/([a-z0-9][a-z0-9-]*)\.html', norm)
    if m: return "{% url 'blog:blog-list' %}" + m.group(1) + '/' + frag
    if norm == 'cart.html': return '#cart-modal'
    if norm == 'search.html': return "{% url 'search:search' %}" + frag
    if norm.startswith('assets/'): return None
    LOG['unmapped_links'].add(norm)
    return '#' + frag.lstrip('#')

def handle_of(href, page):
    path = (href or '').split('#')[0].split('?')[0]
    if not path: return None
    norm = posixpath.normpath(posixpath.join(posixpath.dirname(page), path))
    m = re.fullmatch(r'products/([a-z0-9][a-z0-9-]*)\.html', norm)
    return m.group(1) if m else None

# ---------------------------------------------------------------- 4. fragment transform
PRICE_RE = re.compile(r'^\s*\$\s?\d[\d,]*(?:\.\d{2})?(?:\s*USD)?\s*$')
NEXT_PRICE = "{%% include 'partials/sf_price.html' with p=%s%s %%}"
# the other products sold with refills by default (Theme settings > Subscription Offer, slots 2 to 4): their own
# product, price texts and refill days
REFILL_SLOTS = (2, 3, 4)
def refill_slot(n, var='p'):
    return (f"{var} and settings.sf_refill_product_{n} and settings.sf_refill_price_text_{n} "
            f"and {var}.pk == settings.sf_refill_product_{n}.pk")
REFILL_NOTE = ("{% if product and settings.sf_refill_default_product and settings.sf_refill_price_text and product.pk == settings.sf_refill_default_product.pk %}"
               '<p class="sf-refill-note" style="margin:2px 0 0;font-size:12px;line-height:16px;color:#5a5a5a">with '
               '{{ settings.sf_subscription_interval_count }}-{{ settings.sf_subscription_interval }} refills, cancel anytime</p>'
               + ''.join("{%% elif %s %%}" % refill_slot(n, 'product')
                         + '<p class="sf-refill-note" style="margin:2px 0 0;font-size:12px;line-height:16px;color:#5a5a5a">with '
                         + "{{ settings.sf_refill_every_%d }}-day refills, cancel anytime</p>" % n for n in REFILL_SLOTS)
               + '{% endif %}')

def card_handle(el, page, current):
    """The product a price/form belongs to.

    Walk up from the element: the first ancestor that is (or holds exactly one) product link names it; a buy box
    form names it through its Shopify variant id; a mixed area (several products) on a PDP belongs to the page's
    product."""
    node = el
    for _ in range(10):
        node = node.parent
        if node is None or node.name in ('body', 'html'): break
        if node.name == 'form':
            vid = node.find('input', attrs={'name': 'id'})
            h = VARIANT2HANDLE.get(str(vid.get('value')) if vid else '')
            if h: return h
        links = ([node] if node.name == 'a' and node.get('href') else []) + node.find_all('a', href=True)
        handles = {handle_of(a.get('href'), page) for a in links} - {None}
        if len(handles) == 1: return handles.pop()
        if len(handles) > 1: return current
    return current

def product_ref(handle, current):
    if current and handle == current: return 'product'
    if handle == SHIPPING_PROTECTION: return 'settings.sf_shipping_protection'
    return f'settings.sf_p_{var(handle)}'

NATIVE_REVIEWS_DTL = (
    '{%% if product %%}{"write": "{%% if product|is_review_permitted:user %%}{%% url \'catalogue:reviews-add\' product_slug=product.slug product_pk=product.id %%}{%% endif %%}", '
    '"reviews": [{%% for sf_r in product.reviews.approved.all|slice:":300" %%}'
    '{"name": "{{ sf_r.reviewer_name|escapejs }}", "title": "{{ sf_r.title|escapejs }}", "body": "{{ sf_r.body|striptags|escapejs }}", '
    '"score": "{{ sf_r.score|escapejs }}", "date": "{{ sf_r.date_created|date:\'Y-m-d\' }}"}{%% if not forloop.last %%},{%% endif %%}'
    '{%% endfor %%}]}{%% else %%}{"write": "", "reviews": []}{%% endif %%}').replace('%%', '%')

def transform(root, page, slots, current=None):
    """Bind design markup to NEXT: assets, links, prices, add-to-cart ids. `current`: PDP handle."""
    for t in root.find_all(string=lambda s: isinstance(s, Comment)): t.extract()
    # review wall (tools/persona review_wall_html): NEXT's own approved reviews of the page's product, as JSON, and the
    # "write a review" link for shoppers NEXT lets review it
    for el in root.select('script[data-sf-native-reviews]'):
        el.string = slots.put(NATIVE_REVIEWS_DTL)
    # prices -> NEXT
    for el in list(root.find_all(True)):
        if el.find(True) or not PRICE_RE.match(el.get_text() or ''): continue
        if el.find_parent(attrs={'data-sf-offer-picker': True}) is not None: continue   # prices set by the offer table
        if el.find_parent(attrs={'data-sf-fixed-price': True}) is not None: continue    # a bundle's own price, as written
        if el.find_parent(['script', 'style', 'template']) is not None and el.name not in ('s', 'span', 'div'): continue
        h = card_handle(el, page, current)
        if not h and re.search(r'protection|protect your order', (el.find_parent(['p', 'li', 'div']) or el).get_text(' ', strip=True), re.I):
            h = SHIPPING_PROTECTION
        retail = el.name in ('s', 'del', 'strike') or any('compare' in c for c in el.get('class', []))
        if not h and re.search(r'shipping|delivery|dispatch', (el.find_parent(['p', 'li', 'div']) or el).get_text(' ', strip=True), re.I):
            el.string = slots.put("{{ settings.sf_shipping_fee_text|default:'' }}"); continue
        if not h:
            LOG['unbound_prices'].append(f'{page}: {el.get_text(strip=True)}')
            el.string = ''; continue
        quarter = el.find_parent('smooche-installments') is not None
        el.string = slots.put(NEXT_PRICE % (product_ref(h, current), (' retail=1' if retail else '') + (' quarter=1' if quarter else '')))
    # fees quoted inside shipping/protection prose come from the Shipping Fee setting
    for node in root.find_all(string=True):
        if node.parent is not None and node.parent.name in ('script', 'style'): continue
        txt = str(node)
        if re.search(r'\$\s?\d', txt) and re.search(r'(?i)shipping|protection|delivery', (node.parent.get_text(' ') if node.parent else txt)):
            new = re.sub(r'\$\s?\d[\d,]*(?:\.\d{2})?\s?USD', lambda m: slots.put("{{ settings.sf_shipping_fee_text|default:'' }}"), txt)
            if new != txt: node.replace_with(NavigableString(new))
    # client-side price rewriters carry the source prices in data attributes: drop them
    for el in root.find_all(True):
        for a in [a for a in el.attrs if re.match(r'data-subscription-card-.*price', a)]: del el[a]
    # add-to-cart ids -> NEXT product pk
    for inp in root.select('input[name="id"]'):
        form = inp.find_parent('form')
        h = card_handle(form or inp, page, current) if form else current
        if not h: continue
        ref = product_ref(h, current)
        pk = slots.put('{%% firstof %s.children.first.pk %s.pk %%}' % (ref, ref))
        inp['value'] = pk
        inp['data-sf-next-default'] = pk
    for form in root.find_all('form'):
        if form.get('action') in ('#', '', None) and form.find('input', attrs={'name': 'id'}):
            h = card_handle(form.find('input', attrs={'name': 'id'}), page, current)
            ref = product_ref(h, current) if h else 'product'
            if h:
                n = len(slots.items)
                form.insert_before(NavigableString(slots.put('{%% firstof %s.children.first.pk %s.pk as sf_atc_%d %%}' % (ref, ref, n))))
                form['action'] = slots.put("{%% url 'cart:add' pk=sf_atc_%d %%}" % n)
            else:
                form['action'] = '#cart-modal'
            form['data-sf-product-form'] = ''
    # links
    for el in root.find_all(['a', 'area']):
        d = link_dtl(el.get('href'), page)
        if d is not None: el['href'] = slots.put(d)
    for el in root.find_all('form'):
        if el.get('action') and not el['action'].startswith('SFSLOT') and el['action'] != '#cart-modal':
            d = link_dtl(el['action'], page)
            if d is not None: el['action'] = slots.put(d)
    # header/footer cart icons open the Spark side cart
    for el in root.select('[data-cart-drawer-toggle]'):
        el['href'] = '#cart-modal'
    # asset paths anywhere (attributes, inline CSS, inline JS, JSON blobs); the root node itself included
    everything = [root] + root.find_all(True)
    for el in everything:
        for a, v in list(el.attrs.items()):
            if isinstance(v, list): v = ' '.join(v)
            if isinstance(v, str) and 'assets/' in v:
                el[a] = assetize(v, slots)
    for el in [root] + root.find_all('script'):
        if el.name == 'script' and el.string and "'/cart/'" in el.string:
            el.string = re.sub(r"window\.location\.href\s*=\s*'/cart/'\s*\+\s*([A-Za-z_$][\w$]*)\s*;",
                               r"window.SFCommerce.addPermalink(\1);", el.string)
    for el in [e for e in everything if e.name in ('style', 'script')]:
        if el.string and 'assets/' in el.string:
            el.string = assetize(el.string, slots)
    return root

def frag_html(nodes, page, slots, current=None):
    return ''.join(str(transform(n, page, slots, current)) if hasattr(n, 'find_all') else str(n) for n in nodes)

# ---------------------------------------------------------------- 4b. design cleanup
# The export carries the Shopify store's runtime: checkout/app configuration, app data blobs, a contact-form
# captcha, and scripts for the Shopify cart drawer that the Spark side cart replaces. On NEXT none of it has
# anything to talk to; it only costs bytes, requests and parse time. Links to the old store become NEXT routes.
DEAD_SCRIPT_SRC = re.compile(r'(?:js-cookie-min|skinofab-cart-timer|skinofab-cart-gift-guard|skinofab-cart-upsell-purchase|'
                             r'skinofab-routine-upgrade|skinofab-subscription-card-prices|jquery-min|offline-shim)')
DEAD_LINK_HREF = re.compile(r'skinofab-routine-upgrade|cdn\.shopify\.com/')
DEAD_IDS = {'in-context-paypal-metadata', 'apple-pay-shop-capabilities', 'shop-js-analytics', 'captcha-bootstrap',
            'shopify-accelerated-checkout-cart', 'kaching-bundles-translations', 'replo-deps-shopify-store'}
DEAD_CLASSES = {'kaching-bundles-product', 'kaching-bundles-deal-block-settings'}
DEAD_INLINE = re.compile(r"\(o\.Shopify=o\.Shopify\|\|\{\}\)\.modules|document\.querySelector\('\[data-cart-drawer\]'\);\s*if \(!drawer\) return")
OLD_HOSTS = re.compile(r'^(?:https?:)?//(?:www\.)?(?:08f531-2\.myshopify\.com|skinofab\.com|smooche\.com)(?=/|$)', re.I)
THIRD_PARTY_IMG = re.compile(r'^https?://(?:www\.iubenda\.com|s3\.[a-z0-9-]+\.amazonaws\.com)/', re.I)
FLAG_IMG = re.compile(r'<img class="shipping-country-flag" src="https://cdn\.shopify\.com/static/images/flags/[^"]*"[^>]*>')
# Footer payment logos (design SVGs titled pi-<name>) -> the Payment logos setting's names (Spark's img/pay icons), so the
# footer and the cart drawer show the same, checkout-accurate set. Logos with no setting name are Shopify-only: removed.
PAY_LOGOS = {'pi-visa': 'visa', 'pi-master': 'mc', 'pi-american_express': 'amex', 'pi-discover': 'discover',
             'pi-apple_pay': 'applepay', 'pi-google_pay': 'googlepay', 'pi-paypal': 'ppal', 'pi-klarna': 'klarna',
             'pi-diners_club': 'diners', 'pi-jcb': 'jcb', 'pi-maestro': 'maestro', 'pi-dankort': 'dankort'}
PAY_ICONS = [('visa', 'Visa'), ('mc', 'Mastercard'), ('amex', 'American Express'), ('discover', 'Discover'),
             ('applepay', 'Apple Pay'), ('googlepay', 'Google Pay'), ('ppal', 'PayPal'), ('klarna', 'Klarna'),
             ('diners', 'Diners Club'), ('jcb', 'JCB'), ('maestro', 'Maestro'), ('dankort', 'Dankort')]

FLAG_EMOJI = ('<span class="shipping-country-flag" aria-hidden="true">${String.fromCodePoint(...normalizedCountryCode.split(\'\')'
              '.map(c => 127397 + c.charCodeAt(0)))}</span>')
CLEAN = {'removed': 0, 'relinked': 0}

def clean_design(soup):
    for el in soup.find_all(['script', 'link', 'meta', 'style']):
        src, href, txt = el.get('src') or '', el.get('href') or '', el.string or ''
        if (el.get('id') in DEAD_IDS or DEAD_CLASSES & set(el.get('class') or [])
                or (el.name == 'script' and (DEAD_SCRIPT_SRC.search(src) or DEAD_INLINE.search(txt)))
                or (el.name == 'link' and DEAD_LINK_HREF.search(href))
                or (el.name == 'meta' and el.get('http-equiv') == 'X-UA-Compatible')):
            el.decompose(); CLEAN['removed'] += 1
    if not soup.find(lambda t: t.name == 'kaching-bundle' or any('kaching-bundles__' in c for c in (t.get('class') or []))):
        for el in soup.find_all('link', href=re.compile(r'kaching-bundles')):   # the bundles app's CSS, nothing to style
            el.decompose(); CLEAN['removed'] += 1
    for el in soup.select('shop-follow-button'):          # Shop app "follow" button: Shopify-only
        (el.find_parent(class_='follow-on-shop') or el).decompose(); CLEAN['removed'] += 1
    for el in soup.find_all('link', attrs={'fetchpriority': True}):
        if not re.fullmatch(r'high|low|auto', el['fetchpriority']): del el['fetchpriority']   # unrendered app snippet
    for li in soup.select('.payment-icon-list > li'):
        t = li.find('title')
        key = PAY_LOGOS.get(t.get('id') if t else None)
        if not key: li.decompose(); CLEAN['removed'] += 1; continue
        li.insert_before(NavigableString(page_dtl("{%% if '%s' in settings.sf_pay_icons %%}" % key)))
        li.insert_after(NavigableString(page_dtl('{% endif %}')))
    for el in soup.select('img.logo__image'):              # the header logo is the home link's only content
        if not el.get('alt'): el['alt'] = 'SKINOFAB'
    for el in soup.find_all('img', src=THIRD_PARTY_IMG):   # policy-generator provider favicons, hot-linked
        el.decompose(); CLEAN['removed'] += 1
    for el in soup.find_all(True):
        if OLD_HOSTS.match(el.get('data-instant-href') or ''):   # prefetch hint for the old store's pages
            del el['data-instant-href']; CLEAN['relinked'] += 1
        for a in ('href', 'src', 'action'):
            v = el.get(a)
            if isinstance(v, str) and OLD_HOSTS.match(v):
                el[a] = OLD_HOSTS.sub('', v) or '/'; CLEAN['relinked'] += 1
        h = el.get('href') or ''
        if re.match(r'https?://shopify\.com/\d+/account', h): el['href'] = '/accounts/'; CLEAN['relinked'] += 1
        elif re.match(r'https?://form\.typeform\.com/', h): el['href'] = '/pages/contact'; CLEAN['relinked'] += 1
        elif el.name == 'a' and re.match(r'https?://(?:www\.)?instagram\.com/p/', h):   # the old brand's posts
            del el['href']; el.attrs.pop('target', None); el.attrs.pop('rel', None); CLEAN['relinked'] += 1
    for sc in soup.find_all('script'):
        t = sc.string
        if not t: continue
        n = FLAG_IMG.sub(FLAG_EMOJI, t)
        n = re.sub(r'(shop_url:\s*)"https?:\\/\\/[^"]*"', r'\1"\\/"', n)
        n = re.sub(r'(base:\s*)"//(?:www\.)?skinofab\.com/cdn/shop/[^"]*"', r'\1"\\/"', n)
        n = re.sub(r'\\/\\/(?:www\.)?skinofab\.com\\/cdn\\/shop\\/', r'\\/cdn\\/shop\\/', n)
        if n != t: sc.string = n; CLEAN['relinked'] += 1

# ---------------------------------------------------------------- 5. page decomposition
HEAD_DROP = lambda el: (el.name == 'title' or (el.name == 'meta' and (el.get('charset') or el.get('name') in ('viewport', 'description')))
                        or (el.name == 'link' and 'icon' in (el.get('rel') or []))
                        or (el.name == 'script' and 'offline-shim' in (el.get('src') or '')))

def decompose(page):
    soup = BeautifulSoup((EXPORT / page).read_text('utf-8'), 'lxml')
    clean_design(soup)
    head = [el for el in soup.head.contents if not (getattr(el, 'name', None) and HEAD_DROP(el)) and str(el).strip()]
    body = soup.body
    kids = [k for k in body.contents if getattr(k, 'name', None)]
    hdr_idx = [i for i, k in enumerate(kids) if (k.get('id') or '').endswith(('__announcement-bar', '__header'))]
    ftr_idx = [i for i, k in enumerate(kids) if 'shopify-section-group-group-footer' in ' '.join(k.get('class', []))]
    main = body.find('main', id='MainContent')
    main_idx = kids.index(main) if main in kids else None
    lead = kids[:hdr_idx[0]] if hdr_idx else kids[:main_idx or 0]
    tail_start = (ftr_idx[-1] + 1) if ftr_idx else ((main_idx + 1) if main_idx is not None else len(kids))
    tail = [k for k in kids[tail_start:] if 'shopify-app-block' not in ' '.join(k.get('class', []))]
    title = soup.title.get_text() if soup.title else 'SKINOFAB'
    desc = soup.find('meta', attrs={'name': 'description'})
    return {'soup': soup, 'head': head, 'lead': lead, 'has_header': bool(hdr_idx), 'has_footer': bool(ftr_idx),
            'main': main, 'tail': tail, 'title': title, 'body_id': body.get('id', ''),
            'description': re.sub(r'\s+', ' ', desc.get('content', '')).strip() if desc else '',
            'body_class': ' '.join(body.get('class', []))}

def dtl_literal(value):
    """A design string emitted through DTL (a string literal), so it is data, not template text."""
    value = re.sub(r'\s+', ' ', value or '').strip().replace('\\', '').replace('"', "'")
    return '{%% firstof "%s" %%}' % value if value else ''

PRIVACY_CHOICES = (re.compile(r'(<a href="/cookie-policy/">Cookie policy</a>)(</nav>)'), r'\1<a href="/data-sharing-opt-out/">Your privacy choices</a>\2')

def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    # every copy of the store's policy links gets "Your privacy choices" (live review 12: the track-your-order page
    # carries its own copy of the footer from the export, without the link the main footer has)
    text = PRIVACY_CHOICES[0].sub(PRIVACY_CHOICES[1], text)
    p.write_text(text, 'utf-8')
    LOG['templates'].append(rel)

# "<meta title> | <store title>" unless the meta title already carries the store name (e.g. "... | SKINOFAB")
BRAND_TITLE = "{%% if store.name|upper in %s|upper %%}{{ %s }}{%% else %%}{{ %s }} | {{ block.super }}{%% endif %%}"

def page_template(page, parts, content_dtl, title_dtl=None, current=None, extra_head='', extra_tail=''):
    slots = Slots()
    head = frag_html(parts['head'], page, slots, current)
    lead = frag_html(parts['lead'], page, slots, current)
    tail = frag_html(parts['tail'], page, slots, current)
    t = ["{% extends 'layouts/base.html' %}",
         "{% block title %}" + (title_dtl or dtl_literal(parts['title'])) + "{% endblock %}",
         "{% block body_id %}" + dtl_literal(parts['body_id']) + "{% endblock %}",
         "{% block body_class %}" + dtl_literal(parts['body_class']) + "{% endblock %}",
         "{% block sf_head %}\n" + slots.render(head) + extra_head + "\n{% endblock sf_head %}",
         "{% block sf_lead %}" + slots.render(lead) + "{% endblock sf_lead %}"]
    if not parts['has_header']: t.append("{% block nav_header %}{% endblock nav_header %}")
    if not parts['has_footer']: t.append("{% block footer %}{% endblock footer %}")
    t.append("{% block content_wrapper %}\n" + content_dtl(slots) + "\n{% endblock content_wrapper %}")
    t.append("{% block sf_tail %}\n" + slots.render(tail) + extra_tail + "\n{% endblock sf_tail %}")
    return '\n'.join(t) + '\n'

def main_html(parts, page, slots, current=None, mutate=None):
    main = parts['main']
    if main is None: return ''
    if mutate: mutate(main, slots)
    return slots.render(str(transform(main, page, slots, current)))

# ---------------------------------------------------------------- 6. chrome partials (header / footer) from the homepage
home = decompose('index.html')
hsoup = home['soup']
slots = Slots()
hdr_nodes = [k for k in hsoup.body.find_all(recursive=False) if (k.get('id') or '').endswith(('__announcement-bar', '__header'))]
for n in hdr_nodes:
    for drawer in n.select('#cart-drawer'): drawer.decompose()
    for b in n.select('button.mobile-menu__button--burger'):
        b['data-toggle'] = 'mobile-nav'
    for t in n.select('a[data-cart-drawer-toggle]')[:1]:
        badge = hsoup.new_tag('span', id='cart-badge', attrs={'class': 'cart-badge', 'aria-live': 'polite', 'style': 'display: none;'})
        t.append(badge)
    ann = n.select_one('.announcement__text, [data-announcement-text], .announcement__bar-holder') if (n.get('id') or '').endswith('__announcement-bar') else None
    # a product's own line on its page ({handle: text}, tools/persona: the store's sale line does not fit every product)
    for sp in n.select('[data-sf-ann]'):
        own = json.loads(sp['data-sf-ann']); del sp['data-sf-ann']
        # a handle: its product page ('/<handle>_' in the path); a key starting with '/': that page's path
        cond = lambda h: f"request.path == '{h}'" if h.startswith('/') else f"'/{h}_' in request.path"
        branches = ''.join(f"{{% {'if' if not i else 'elif'} {cond(h)} %}}{html.escape(t)}" for i, (h, t) in enumerate(own.items()))
        sp.string = slots.put(f"{branches}{{% else %}}{html.escape(sp.get_text())}{{% endif %}}")
header_html = slots.render(frag_html(hdr_nodes, 'index.html', slots))
write('partials/header.html', "{# SKINOFAB header: design markup (announcement bar, navigation, mobile drawer). Cart opens the Spark side cart. #}\n" + header_html + '\n')
slots = Slots()
ftr_nodes = [k for k in hsoup.body.find_all(recursive=False) if 'shopify-section-group-group-footer' in ' '.join(k.get('class', []))]
# "Your privacy choices" beside the policies (live review 11: the privacy policy promises a privacy choices link; the
# page is /data-sharing-opt-out/, whose opt-out tools/persona/company.py makes work)
footer_html = slots.render(frag_html(ftr_nodes, 'index.html', slots))
footer_html, n_pc = re.subn(r'(<a href="/cookie-policy/">Cookie policy</a>)(</nav>)', r'\1<a href="/data-sharing-opt-out/">Your privacy choices</a>\2', footer_html, count=1)
assert n_pc == 1, 'the footer policies changed: place the privacy choices link again'
write('partials/footer.html', "{# SKINOFAB footer: design markup. #}\n" + footer_html + '\n')

# ---------------------------------------------------------------- 7. page families
MAIN_OPEN = lambda m: str(m).split('>', 1)[0] + '>'

def simple(page, template):
    parts = decompose(page)
    write(template, page_template(page, parts, lambda s: main_html(parts, page, s)))

# 7a homepage. Settings > SEO drives the home meta tags; until the store has a meta description, the design's
# description, the hero image and the store's WebSite/Organization data stand in (the platform tag would print empty ones).
def og_image(hero_rel):
    """The link-preview picture (1200 x 630 JPEG, the size Facebook, iMessage and Slack draw) from the hero: her, the
    bottle and the wall to their left, from the photo's right side. The hero itself is a 4096 px WebP, which several
    previewers do not read (the homepage's og:image was empty, review 5)."""
    from PIL import Image
    im = Image.open(OUT / 'assets' / hero_rel).convert('RGB')
    w = round(im.height * 1200 / 630)
    im = im.crop((im.width - w, 0, im.width, im.height)).resize((1200, 630), Image.LANCZOS)
    tmp = OUT / 'assets' / 'sf' / 'img' / 'skinofab-og.jpg'
    im.save(tmp, quality=86, optimize=True, progressive=True)
    final = tmp.with_name(f'skinofab-og-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.jpg'); tmp.rename(final)
    return 'sf/img/' + final.name

def home_seo(parts):
    hero = re.search(r"\{\{ '(sf/img/skinofab-hero-desktop-[^']*)'\|asset_url \}\}", (OUT / 'templates/index.html').read_text())
    if not hero: sys.exit('home: the hero photo for og:image not found')
    d = parts['description'].replace('"', '&quot;')
    img = "{{ '%s'|asset_url }}" % og_image(hero.group(1))
    return ('{% block seo %}{% if store.get_meta_description %}{{ block.super }}{% else %}'
            '<meta name="title" content="{{ store.name }}">\n<meta name="description" content="' + d + '">\n'
            '<meta property="og:title" content="{{ store.name }}">\n<meta property="og:description" content="' + d + '">\n'
            '<meta property="og:type" content="website">\n<meta property="og:url" content="https://{{ request.get_host }}/">\n'
            '<meta property="og:image" content="' + img + '">\n<meta name="twitter:card" content="summary_large_image">\n'
            '<script type="application/ld+json">{"@context": "https://schema.org", "@graph": ['
            '{"@type": "WebSite", "name": "{{ store.name|escapejs }}", "url": "https://{{ request.get_host }}/"}, '
            '{"@type": "Organization", "name": "{{ store.name|escapejs }}", "url": "https://{{ request.get_host }}/", '
            '"logo": "{{ \'SF_LOGO\'|asset_url }}"}]}</script>'
            '{% endif %}{% endblock seo %}\n').replace('SF_LOGO', FAVICON['-180.png'])
home_parts = decompose('index.html')
write('templates/index.html', page_template('index.html', home_parts, lambda s: main_html(home_parts, 'index.html', s)))
if home_parts['description']:
    t = (OUT / 'templates/index.html').read_text()
    (OUT / 'templates/index.html').write_text(t.replace("{% extends 'layouts/base.html' %}\n", "{% extends 'layouts/base.html' %}\n" + home_seo(home_parts), 1))

# 7b pages + policies. NEXT did not apply a page's custom template in testing (even a trivial one), so page.html
# dispatches on page.slug itself: each design page's blocks live in partials/sf_pages/<slug>/, and every
# page.<slug>.html just extends page.html, so selecting the template in the dashboard renders the same thing.
PAGE_PARTS = {}
def page_partials(page, slug):
    parts = decompose(page)
    slots = Slots()
    blocks = {'head': slots.render(frag_html(parts['head'], page, slots)),
              'lead': slots.render(frag_html(parts['lead'], page, slots)),
              'content': main_html(parts, page, slots),
              'tail': slots.render(frag_html(parts['tail'], page, slots))}
    for name, body in blocks.items():
        write(f'partials/sf_pages/{slug}/{name}.html', body + '\n')
    PAGE_PARTS[slug] = {'title': dtl_literal(parts['title']), 'body_id': dtl_literal(parts['body_id']),
                        'body_class': dtl_literal(parts['body_class']), 'header': parts['has_header'], 'footer': parts['has_footer']}
    write(f'templates/pages/page.{slug}.html',
          "{# Design page '%s': rendered by templates/pages/page.html (dispatch on page.slug). #}\n"
          "{%% extends 'templates/pages/page.html' %%}\n" % slug)
for slug in sorted(PAGE_SLUGS):
    page_partials(f'pages/{slug}.html', slug)
for slug in sorted(POLICY_ONLY):
    page_partials(f'policies/{slug}.html', slug)

# 7c default page template: design page layout with NEXT page title + content
def generic_page():
    page = 'pages/careers.html' if 'pages/careers.html' in EXPORTED else 'pages/faq.html'
    parts = decompose(page)
    def content(slots):
        main = parts['main']
        title = main.find(['h1'])
        rte = main.select_one('.rte') or main.find('div')
        if title: title.string = slots.put('{% firstof page.title flatpage.title %}')
        if rte:
            rte.clear(); rte.append(slots.put('{% if page.content %}{{ page.content|safe }}{% else %}{{ flatpage.content|safe }}{% endif %}'))
        return slots.render(str(transform(main, page, slots)))
    generic = page_template(page, parts, content, title_dtl='{% firstof page.title flatpage.title %} | {{ block.super }}')
    # Wrap each generic block in a slug dispatch: design pages first, the generic layout as the fallback.
    slugs = sorted(PAGE_PARTS)
    def dispatch(block, per_slug, fallback):
        branches = ''.join("{%% %s sf_slug == '%s' %%}%s" % ('if' if i == 0 else 'elif', sl, per_slug(sl)) for i, sl in enumerate(slugs))
        return '{%% block %s %%}%s{%% else %%}%s{%% endif %%}{%% endblock %s %%}' % (block, branches, fallback, block)
    def gen_block(name):
        m = re.search(r'\{%% block %s %%\}(.*?)\{%% endblock(?: %s)? %%\}' % (name, name), generic, re.S)
        return m.group(1) if m else ''
    inc = lambda part: (lambda sl: "{%% include 'partials/sf_pages/%s/%s.html' %%}" % (sl, part))
    out = ["{% extends 'layouts/base.html' %}",
           "{# Pages: dispatch on page.slug to the design page partials (partials/sf_pages/<slug>/); generic layout otherwise. #}",
           dispatch('title', lambda sl: PAGE_PARTS[sl]['title'], gen_block('title')),
           dispatch('body_id', lambda sl: PAGE_PARTS[sl]['body_id'], gen_block('body_id')),
           dispatch('body_class', lambda sl: PAGE_PARTS[sl]['body_class'], gen_block('body_class')),
           dispatch('sf_head', inc('head'), gen_block('sf_head')),
           dispatch('sf_lead', inc('lead'), gen_block('sf_lead')),
           dispatch('content_wrapper', inc('content'), gen_block('content_wrapper')),
           dispatch('sf_tail', inc('tail'), gen_block('sf_tail'))]
    no_header = [sl for sl in slugs if not PAGE_PARTS[sl]['header']]
    no_footer = [sl for sl in slugs if not PAGE_PARTS[sl]['footer']]
    if no_header:
        out.append("{%% block nav_header %%}{%% if %s %%}{%% else %%}{{ block.super }}{%% endif %%}{%% endblock nav_header %%}"
                   % ' or '.join("sf_slug == '%s'" % sl for sl in no_header))
    if no_footer:
        out.append("{%% block footer %%}{%% if %s %%}{%% else %%}{{ block.super }}{%% endif %%}{%% endblock footer %%}"
                   % ' or '.join("sf_slug == '%s'" % sl for sl in no_footer))
    text = '\n'.join(out) + '\n'
    # sf_slug: the page slug, available in every block (with-blocks would not span block boundaries)
    text = text.replace('sf_slug ==', 'page.slug ==')
    write('templates/pages/page.html', text)
generic_page()

# 7d product pages: one template per design product (template key = handle), bound to NEXT `product`
VARIANT_JSON = ("<script type=\"application/json\" id=\"sf-variant-options\">[{% for field in variant_form %}{% if 'attr' in field.id_for_label %}"
                "{\"code\": \"{{ field.html_name|slice:'5:'|escapejs }}\", \"label\": \"{{ field.label|escapejs }}\", \"choices\": ["
                "{% for c in field.field.choices %}[\"{{ c.0|escapejs }}\", \"{{ c.1|escapejs }}\"]{% if not forloop.last %},{% endif %}{% endfor %}]},"
                "{% endif %}{% endfor %}null]</script>\n{{ product.data|json_script:'product-data' }}")
PDP_HEAD = "{% purchase_info_for_product request product as session %}"

def bind_pdp(main, slots):
    for h1 in main.select('.product__title, h1.product__title, [data-product-title]')[:2]:
        h1.string = slots.put('{{ product.get_title }}')

for f in sorted(EXPORTED):
    m = re.fullmatch(r'products/([a-z0-9][a-z0-9-]*)\.html', f)
    if not m: continue
    handle = m.group(1)
    parts = decompose(f)
    write(f'templates/catalogue/product.{handle}.html',
          page_template(f, parts, lambda s, p=parts, f=f, h=handle: '<div data-template="product.%s">' % h + main_html(p, f, s, h, bind_pdp) + '</div>',
                        title_dtl=BRAND_TITLE % (('product.get_meta_title',) * 3), current=handle,
                        extra_tail='\n' + VARIANT_JSON + '\n{% app_hook "view_product" %}\n{% app_hook "add_to_cart" %}'))

# default product template: the flagship PDP layout, product section only, gallery from NEXT images
def default_product():
    f = 'products/color-changing-foundation.html'
    parts = decompose(f)
    def content(slots):
        main = parts['main']
        keep = main.select_one('[id$="__main"].shopify-section--product')
        for sec in [c for c in main.find_all(recursive=False) if c is not keep]: sec.decompose()
        # the foundation's offer picker sets the foundation's own variant ids: never on another product's page
        for el in keep.select('[data-sf-offer-picker]'): el.decompose()
        # so are its FrontrowMD badge loader, star rating and purchase count
        for el in keep.select('[data-sf-frontrow]'): el.decompose()
        for el in keep.select('.sf-rating, .social-proof-container'):
            (el.find_parent(class_='product__block') or el).decompose()
        bind_pdp(main, slots)
        desc = keep.select_one('.product__description, [data-product-description], .rte')
        if desc:
            desc.clear(); desc.append(slots.put('{{ product.get_description|safe }}'))
        slides = keep.select('[data-media-slide], .product__slide, [data-product-media-type-image]')
        if slides:
            first = slides[0]
            for s_ in slides[1:]: s_.decompose()
            for img in first.find_all('img'):
                for a in ('srcset', 'data-srcset', 'sizes'): img.attrs.pop(a, None)
                img['src'] = slots.put('{{ sf_img.url }}'); img['alt'] = slots.put('{{ product.get_title }}')
            loop_open = slots.put('{% for image in product.get_all_images %}{% image_thumbnail image.original "1200x1200" crop="center" as sf_img %}')
            first.insert_before(NavigableString(loop_open)); first.insert_after(NavigableString(slots.put('{% endfor %}')))
        return '<div data-template="product.default">' + slots.render(str(transform(main, f, slots, 'color-changing-foundation'))) + '</div>'
    write('templates/catalogue/product.html',
          page_template(f, parts, content, title_dtl=BRAND_TITLE % (('product.get_meta_title',) * 3), current='color-changing-foundation',
                        extra_tail='\n' + VARIANT_JSON + '\n{% app_hook "view_product" %}\n{% app_hook "add_to_cart" %}'))
default_product()

# 7e catalogue: design collection grid, cards rendered from NEXT products
CARD_PARTIAL = None
def build_card(card):
    global CARD_PARTIAL
    slots = Slots()
    for t in card.select('template, product-grid-item-swatch, .product-grid-item__rating, .product__badge'): t.decompose()
    for a in card.find_all('a'):
        a['href'] = slots.put('{{ product.get_absolute_url }}')
        if a.get('aria-label'): a['aria-label'] = slots.put('{{ product.get_title }}')
    title = card.select_one('.product-grid-item__title')
    if title: title.string = slots.put('{{ product.get_title }}')
    imgs = card.find_all('img')
    for i, img in enumerate(imgs[:2]):
        for a in ('srcset', 'data-srcset', 'sizes', 'loading', 'fetchpriority'): img.attrs.pop(a, None)
        img['src'] = slots.put('{{ sf_card_img%d.url }}' % i)
        img['srcset'] = slots.put('{{ sf_card_img%ds.url }} 360w, {{ sf_card_img%d.url }} 720w' % (i, i))
        img['sizes'] = '(min-width: 1024px) 25vw, (min-width: 768px) 33vw, 50vw'
        img['width'], img['height'] = '720', '720'
        # first row eager (LCP on collection pages), the rest and every hover image lazy
        img['loading'] = slots.put('{% if forloop.counter > 4 %}lazy{% else %}eager{% endif %}') if i == 0 else 'lazy'
        img['decoding'] = 'async'
        img['alt'] = slots.put('{{ product.get_title }}')
    for s in card.select('.visually-hidden'): s.string = slots.put('{{ product.get_title }}')
    price = card.select_one('.product-grid-item__price')
    if price:
        price.clear(); price.append(slots.put("{% include 'partials/sf_was.html' with p=product %}{% include 'partials/sf_price.html' with p=product %}"))
        # the refills-by-default product's card shows its refill price (sf_price.html): say so under it, as the
        # homepage's cards do
        price.insert_after(NavigableString(slots.put(REFILL_NOTE)))
    card['id'] = slots.put('product-item-{{ product.pk }}')
    body = slots.render(str(card))
    CARD_PARTIAL = ("{# SKINOFAB product card (design markup) for NEXT products. Usage: include with product=product #}\n"
                    "{# Cards are at most ~360 CSS px wide: 360/720 px crops at quality 80 (the tag defaults to 95) #}\n"
                    "{% with images=product.get_all_images %}"
                    "{% if images %}{% image_thumbnail images.0.original \"360x360\" crop=\"center\" quality=80 as sf_card_img0s %}"
                    "{% image_thumbnail images.0.original \"720x720\" crop=\"center\" quality=80 as sf_card_img0 %}{% endif %}"
                    "{% if images.1 %}{% image_thumbnail images.1.original \"360x360\" crop=\"center\" quality=80 as sf_card_img1s %}"
                    "{% image_thumbnail images.1.original \"720x720\" crop=\"center\" quality=80 as sf_card_img1 %}"
                    "{% elif images %}{% image_thumbnail images.0.original \"360x360\" crop=\"center\" quality=80 as sf_card_img1s %}"
                    "{% image_thumbnail images.0.original \"720x720\" crop=\"center\" quality=80 as sf_card_img1 %}{% endif %}\n"
                    + body + "\n{% endwith %}\n")
    write('partials/sf_product_card.html', CARD_PARTIAL)

def catalogue(template, title_var):
    f = 'collections/all.html'
    parts = decompose(f)
    def content(slots):
        main = parts['main']
        # the export's "Sort by" bar and filter drawer: Shopify's sort values, which NEXT's listing ignores (the same
        # four products in the same order for each), and while it is on the page the theme unpins the header (it
        # pins the bar instead): both go, the header stays pinned as on every other page
        for el in main.select('[data-collection-sticky-bar], [data-collection-filters]'):
            if not el.select('[data-product-block]'): el.decompose()
        cards = main.select('[data-product-block]')
        if cards:
            grid = cards[0].parent
            build_card(BeautifulSoup(str(cards[0]), 'lxml').find(attrs={'data-product-block': True}))
            for c in cards: c.decompose()
            grid.append(slots.put("{% for product in products %}{% include 'partials/sf_product_card.html' with product=product %}{% endfor %}"))
            grid.insert_after(NavigableString(slots.put("{% include 'partials/pagination.html' %}")))
        for h in main.find_all(['h1'])[:1]:
            h.string = slots.put(title_var)
        # the banner over the grid said "Bestsellers" on every listing (the export's collection): the listing's name
        for h in main.select('.banner-image__heading .text-highlight__break')[:1]:
            h.string = slots.put(title_var)
        # "24 products": the export's own count, not the listing's; NEXT's page shows its products, no count
        for c in main.select('.collection__products-count'): c.decompose()
        # the banner's photo shows our four products, each in a woman's hand: a category with fewer of them shows
        # its name without the photo. Hidden, not left out: the section's script animates that element and threw a
        # TypeError (handleImageAnimation) when it was missing (review 5)
        if template.endswith('category.html'):
            for box in main.select('.banner-image__image-container')[:1]:
                box['data-sf-few'] = slots.put('{% if products|length < 4 %}true{% else %}false{% endif %}')
        return slots.render(str(transform(main, f, slots)))
    write(template, page_template(f, parts, content, title_dtl='{% firstof category.get_meta_title category.name "Shop all" %} | {{ block.super }}'))
catalogue('templates/catalogue/category.html', '{{ category.name }}')
catalogue('templates/catalogue/index.html', "{% t 'navigation.main.shop' %}")

# 7f search: design search page, results from NEXT
def search():
    f = 'search.html'
    parts = decompose(f)
    def content(slots):
        main = parts['main']
        target = main.select_one('[data-search-results], .search__results, .grid--uniform, .collection__products') or main.find('div')
        if target is not None:
            target.clear()
            target.append(slots.put("{% if page.object_list %}<div class=\"grid grid--uniform\">{% for result in page.object_list %}"
                                    "{% include 'partials/sf_product_card.html' with product=result.object %}{% endfor %}</div>"
                                    "{% include 'partials/pagination.html' with page_obj=page %}{% elif query %}<p class=\"text-center\">"
                                    "{% t 'search.no_results' %}</p>{% endif %}"))
        for inp in main.select('input[type="search"], input[name="q"]'):
            inp['value'] = slots.put('{{ query|default:"" }}')
        return slots.render(str(transform(main, f, slots)))
    write('templates/search.html', page_template(f, parts, content))
if 'search.html' in EXPORTED: search()

# 7g blog: design article + listing layouts, content from NEXT posts
def blog():
    art = sorted(p for p in EXPORTED if p.startswith('blogs/news/'))[0]
    parts = decompose(art)
    def post_content(slots):
        main = parts['main']
        h1 = main.find('h1')
        if h1: h1.string = slots.put('{{ post.title }}')
        body = main.select_one('.article__content, .rte, [data-article-content]')
        if body: body.clear(); body.append(slots.put('{{ post.content|safe }}'))
        for t in main.select('time'): t.string = slots.put('{{ post.created_at|date:"F j, Y" }}')
        hero = main.select_one('.article__image img, .article__hero img, figure img')
        if hero:
            for a in ('srcset', 'data-srcset', 'sizes'): hero.attrs.pop(a, None)
            hero['src'] = slots.put('{% if post.featured_image %}{% image_thumbnail post.featured_image "1600x" upscale=False as sf_post_img %}{{ sf_post_img.url }}{% endif %}')
        return slots.render(str(transform(main, art, slots)))
    write('templates/blog/post.html', page_template(art, parts, post_content, title_dtl=BRAND_TITLE % (('post.get_meta_title',) * 3)))
    lst = 'blogs/news.html'
    parts2 = decompose(lst)
    def list_content(slots):
        main = parts2['main']
        items = main.select('.article, .blog__article, [data-article], .article-item, .grid__item')
        if items:
            proto = items[0]; grid = proto.parent
            pslots = slots
            for a in proto.find_all('a'): a['href'] = pslots.put('{{ post.get_absolute_url }}')
            for h in proto.find_all(['h2', 'h3', 'h4'])[:1]: h.string = pslots.put('{{ post.title }}')
            for t in proto.select('time'): t.string = pslots.put('{{ post.created_at|date:"F j, Y" }}')
            for img in proto.find_all('img')[:1]:
                for a in ('srcset', 'data-srcset', 'sizes'): img.attrs.pop(a, None)
                img['src'] = pslots.put('{% if post.featured_image %}{% image_thumbnail post.featured_image "800x" upscale=False as sf_li %}{{ sf_li.url }}{% endif %}')
            proto_html = str(proto)
            for it in items: it.decompose()
            grid.append(pslots.put('{% for post in posts %}' + pslots.render(proto_html) + '{% endfor %}'))
        return slots.render(str(transform(main, lst, slots)))
    write('templates/blog/index.html', page_template(lst, parts2, list_content, title_dtl='{% t "navigation.main.blog" %} | {{ block.super }}'))
blog()

# ---------------------------------------------------------------- 8. shared partials + base layout
write('partials/sf_price.html',
      "{# NEXT price for product p in the design's format ($49 USD). retail=1: compare-at price, only when higher. quarter=1: pay-in-4 instalment. #}\n"
      "{# The subscription-only product (Theme settings > Subscription Offer) shows its plan price text instead, with no compare-at or instalment price. #}\n"
      "{# The refills-by-default product shows the price its page shows first (refills ticked), and its was-price. #}\n"
      "{% if p and settings.sf_subscription_product and settings.sf_subscription_price_text and p.pk == settings.sf_subscription_product.pk %}"
      "{% if not retail and not quarter %}{{ settings.sf_subscription_price_text }}{% endif %}"
      "{% elif p and not quarter and settings.sf_refill_default_product and settings.sf_refill_price_text and p.pk == settings.sf_refill_default_product.pk %}"
      "{% if retail %}{{ settings.sf_refill_compare_text }}{% else %}{{ settings.sf_refill_price_text }}{% endif %}"
      + ''.join("{%% elif not quarter and %s %%}" % refill_slot(n)
                + "{%% if retail %%}{{ settings.sf_refill_compare_text_%d }}{%% else %%}{{ settings.sf_refill_price_text_%d }}{%% endif %%}" % (n, n)
                for n in REFILL_SLOTS) +
      "{% elif p %}{% purchase_info_for_product request p as sf_s %}{% if sf_s.price.exists %}"
      "{% if retail %}{% if sf_s.price.price_retail > sf_s.price.price %}{% currency_symbol sf_s.price.currency %}{{ sf_s.price.price_retail|floatformat:'-2' }} {{ sf_s.price.currency }}{% endif %}"
      "{% elif quarter %}{% currency_symbol sf_s.price.currency %}{{ sf_s.price.price|dividedby:4|floatformat:'-2' }}"
      "{% else %}{% currency_symbol sf_s.price.currency %}{{ sf_s.price.price|floatformat:'-2' }} {{ sf_s.price.currency }}{% endif %}"
      "{% endif %}{% endif %}")

# a listing card's was-price, struck through before its price, only when it has one: the homepage's cards show the
# compare-at price and the listing pages showed none (review 3). The refills-by-default product's is its page's.
write('partials/sf_was.html',
      "{# Card was-price for product p: <s> with the compare-at price, or nothing. #}\n"
      "{% if p and settings.sf_subscription_product and settings.sf_subscription_price_text and p.pk == settings.sf_subscription_product.pk %}"
      "{% elif p and settings.sf_refill_default_product and settings.sf_refill_price_text and p.pk == settings.sf_refill_default_product.pk %}"
      "{% if settings.sf_refill_compare_text %}<s class=\"sf-was\" style=\"color:#8a8a8a;font-weight:400;margin-right:6px\">{{ settings.sf_refill_compare_text }}</s>{% endif %}"
      + ''.join("{%% elif %s %%}" % refill_slot(n)
                + "{%% if settings.sf_refill_compare_text_%d %%}<s class=\"sf-was\" style=\"color:#8a8a8a;font-weight:400;margin-right:6px\">{{ settings.sf_refill_compare_text_%d }}</s>{%% endif %%}" % (n, n)
                for n in REFILL_SLOTS) +
      "{% elif p %}{% purchase_info_for_product request p as sf_s %}{% if sf_s.price.exists and sf_s.price.price_retail > sf_s.price.price %}"
      "<s class=\"sf-was\" style=\"color:#8a8a8a;font-weight:400;margin-right:6px\">{% currency_symbol sf_s.price.currency %}{{ sf_s.price.price_retail|floatformat:'-2' }} {{ sf_s.price.currency }}</s>"
      "{% endif %}{% endif %}")

# the same, with the product's purchase info already looked up (sf_s): a page that shows one product's price several
# times looks it up once (8c)
write('partials/sf_price_pi.html', (OUT / 'partials' / 'sf_price.html').read_text()
      .replace("{% purchase_info_for_product request p as sf_s %}", "")
      .replace("{# NEXT price for product p", "{# sf_price.html with sf_s, the purchase info of p, passed in. NEXT price for product p", 1))

fonts = []
for block in FONT_FACES:
    fonts.append(re.sub(ASSET_RE, lambda m: asset_dtl(m.group(1), m.group(2)) or m.group(0),
                        re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', lambda m: 'url("%s")' % m.group(2), block)))
vars_css = ':root{' + ''.join('%s:url("%s");' % (k, asset_dtl(*v.split('/', 1)) or '') for k, v in sorted(CSS_VARS.items())) + '}'
write('partials/sf_asset_styles.html',
      "{# Fonts and stylesheet images. Theme CSS cannot hold relative url()s on NEXT (CSS and media are served from different hosts), so they resolve here via asset_url. #}\n"
      "<style>\n" + '\n'.join(dict.fromkeys(fonts)) + '\n' + vars_css + "\n</style>\n")

product_json = ','.join('"%s":"{{ \'sf/data/product-%s.json\'|asset_url|escapejs }}"' % (h, h) for h in sorted(PRODUCT_JSON))
base = (SPARK / 'layouts' / 'base.html').read_text()
# No dangling " - " when the store has no tagline; the store icon from Settings > Branding wins over the theme's.
# Global Privacy Control, or the opt-out on /data-sharing-opt-out/ (a cookie for every skinofab.com host, or this
# browser's storage): no AppLovin pixel on any store page, as the privacy policy promises (live review 12: the store's
# AppLovin app loaded it on the policy pages, the opt-out page itself included). The app's Axon snippet, at the end of
# <head>, loads only while window.axon is undefined, so a no-op one set first stops it; the funnels' layouts do the same.
base = must_replace(base, '    <meta charset="UTF-8" />\n',
    '    <meta charset="UTF-8" />\n'
    "    <script>(function () { var out = navigator.globalPrivacyControl === true || /(?:^|;\\s*)sf_optout=1/.test(document.cookie);"
    " try { out = out || localStorage.getItem('sf_optout') === '1'; } catch (e) {}"
    " if (out) { window.axon = function () {}; window.__sfGPC = true; } })();</script>\n", 'privacy gate')
base = must_replace(base, '{% block title %}{{ store.get_meta_title }} - {{ store.tagline }}{% endblock %}',
                    '{% block title %}{{ store.get_meta_title }}{% if store.tagline %} - {{ store.tagline }}{% endif %}{% endblock %}', 'title')
base = must_replace(base, """                <link rel="shortcut icon" href="{{ thumb_store_icon.url }}" />
            {% endwith %}
        {% endif %}""", """                <link rel="shortcut icon" href="{{ thumb_store_icon.url }}" />
            {% endwith %}
        {% else %}
            <link rel="icon" type="image/svg+xml" href="{{ 'FAV_SVG'|asset_url }}">
            <link rel="icon" type="image/png" sizes="32x32" href="{{ 'FAV_32'|asset_url }}">
            <link rel="apple-touch-icon" href="{{ 'FAV_180'|asset_url }}">
        {% endif %}""".replace('FAV_SVG', FAVICON['.svg']).replace('FAV_32', FAVICON['-32.png']).replace('FAV_180', FAVICON['-180.png']), 'favicon')
# Media (images, fonts, video) come from cdn.29next.store, the theme's CSS and scripts from NEXT's static host on
# CloudFront: open both connections before the HTML asks for them (the render-blocking CSS waited ~150 ms for its own
# DNS, TCP and TLS handshake after the HTML arrived).
base = must_replace(base, "{% block critical_preloads %}{% endblock critical_preloads %}",
                    '<link rel="preconnect" href="https://d1lrxs4saq89c.cloudfront.net">\n'
                    '    <link rel="preconnect" href="https://cdn.29next.store">\n    <link rel="preconnect" href="https://cdn.29next.store" crossorigin>\n'
                    "    {% block critical_preloads %}{% endblock critical_preloads %}", 'preconnect')
base = base.replace('<link rel="stylesheet" type="text/css" href="{{ \'main.css\'|asset_url }}">',
                    "{% block spark_css %}{% endblock spark_css %}\n        {% include 'partials/sf_asset_styles.html' %}")
# One feel for every filled button. The design's .btn hover laid a grey wash over the black (it read as disabled), the
# home and sticky buttons had no hover at all, and nothing answered a press. Now: hover lifts (mouse only), a press sinks
# at once (touch too), keyboard focus shows a ring that reads on light and dark, and an add in flight spins.
BTN_DARK = ('.product__submit__add', '.btn--primary.btn--solid', '.btn--dark', '.input-group__btn', '.fh-button',
            '.sfps-btn', '.sfb-btn:not(.sfb-btn--light)', '.sf-sticky__btn')
BTN_ALL = ':is(' + ', '.join(BTN_DARK + ('.sfb-btn--light',)) + ')'
BTN_CSS = (
    BTN_ALL + '{transition:background-color .2s ease,color .2s ease,border-color .2s ease,box-shadow .2s ease,transform .14s ease!important;'
    '-webkit-tap-highlight-color:transparent;touch-action:manipulation}'
    + BTN_ALL + '::before{display:none!important}'
    '@media (hover:hover) and (pointer:fine){'
    # (white text on the black: the outline "Shop now" of "Beauty is a celebration" kept its black text, review 5)
    ':is(' + ', '.join(BTN_DARK) + '):hover{background-color:#000!important;border-color:#000!important;color:#fff!important;transform:translateY(-1px);'
    'box-shadow:0 12px 24px -12px rgba(0,0,0,.6)}'
    '.sfb-btn--light:hover{background-color:#f4f2ee!important;transform:translateY(-1px);box-shadow:0 12px 24px -14px rgba(0,0,0,.4)}}'
    + BTN_ALL + ':active{transform:translateY(0) scale(.97)!important;box-shadow:0 2px 8px -4px rgba(0,0,0,.5)!important;transition-duration:.06s!important}'
    + BTN_ALL + ':focus-visible{outline:2px solid #151515!important;outline-offset:3px!important;box-shadow:0 0 0 3px #fff!important}'
    + BTN_ALL + '[aria-busy="true"]{position:relative;pointer-events:none;color:transparent!important}'
    + BTN_ALL + '[aria-busy="true"] *{visibility:hidden}'
    + BTN_ALL + '[aria-busy="true"]::after{content:"";position:absolute;top:50%;left:50%;width:18px;height:18px;margin:-9px 0 0 -9px;'
    'border:2px solid rgba(255,255,255,.35);border-top-color:#fff;border-radius:50%;animation:sf-btn-spin .7s linear infinite}'
    '.sfb-btn--light[aria-busy="true"]::after{border-color:rgba(21,21,21,.2);border-top-color:#151515}'
    '@keyframes sf-btn-spin{to{transform:rotate(360deg)}}'
    '@media (prefers-reduced-motion:reduce){' + BTN_ALL + '{transition:none!important;transform:none!important}}')
base = base.replace("{% endblock styles %}",
    "{% endblock styles %}\n    {# Spark side cart in the design's look: black controls, design body font. #}\n"
    "    <style>:root{--primary-color:#000000;--primary-color-darker:#000000;--primary-color-lighter:#333333;--accent-color:#000000;"
    "--font-body:var(--FONT-STACK-BODY, 'Jost', sans-serif);}" + BTN_CSS + "</style>\n"
    "    {# A policy page opened from a funnel's footer (?from=offer, the funnels' sf-footer.html) keeps the store's sale bar and menus out of it, set before the first paint (live review 7). Django comments are one line. #}\n"
    "    {# On such a page every link to another legal or contact page keeps ?from=offer, and any other link into the store is switched off (live review 9: one tap on a footer link opened the full store; a page's link to itself too). #}\n"
    "    <script>if (/[?&]from=offer(?:&|$)/.test(location.search)) { document.documentElement.classList.add('sf-from-offer');"
    " document.addEventListener('DOMContentLoaded', function () { var keep = /^\\/(?:[a-z]{2}\\/)?(?:privacy-policy|terms-of-service|refund-policy|shipping-policy|cookie-policy|data-sharing-opt-out|contact|contact-information|postflows-track-your-order)\\/?$/;"
    " document.querySelectorAll('a[href]').forEach(function (a) { var u; try { u = new URL(a.getAttribute('href'), location.href); } catch (e) { return; }"
    " if (u.origin !== location.origin || a.getAttribute('href').charAt(0) === '#') return;"
    " if (keep.test(u.pathname)) { u.searchParams.set('from', 'offer'); a.setAttribute('href', u.pathname + u.search + u.hash); }"
    " else { a.removeAttribute('href'); a.setAttribute('aria-disabled', 'true'); a.classList.add('sf-off-link'); } }); }); }</script>"
    "<style>.sf-from-offer{--announcement-height:0px!important}.sf-from-offer .announcement-bar-static,.sf-from-offer #SiteHeader .menu__items,"
    ".sf-from-offer #SiteHeader .menu__item--icons,.sf-from-offer #SiteHeader .mobile-menu,.sf-from-offer #SiteHeader .mobile-menu__button,"
    # (live review 8: the footer's shop and customer-care menus and the newsletter sign-up led into the store mid-purchase)
    ".sf-from-offer #SiteFooter .sf__signup,.sf-from-offer #SiteFooter .sf__menu{display:none!important}"
    # (live review 11: the track-your-order page showed the store's "You might like these too" cards and prices, its links switched off)
    ".sf-from-offer #shopify-section-sf-more,.sf-from-offer .sf-more{display:none!important}"
    ".sf-from-offer #SiteFooter .sf__logo,.sf-from-offer #SiteHeader a[href=\"/\"]{pointer-events:none;cursor:default}"
    ".sf-from-offer .sf-off-link{pointer-events:none;color:inherit;text-decoration:none}"
    # (live review 16, F3: the policy links were 43 px, the email and phone links 24 px, the opt-out button 43.6 px; an
    # inline link's vertical padding grows its tap box without moving the lines around it: 12 px, as 10 left a 23 px
    # line at 43)
    ".sf-from-offer #SiteFooter .sf__policies a{display:inline-flex;align-items:center;min-height:44px;padding:0 4px}"
    ".sf-from-offer a[href^=\"mailto:\"],.sf-from-offer a[href^=\"tel:\"]{padding-top:12px;padding-bottom:12px}"
    ".sf-from-offer [data-sf-optout-btn]{min-height:44px}</style>", 1)
base = base.replace("{% block extrahead %}{% endblock extrahead %}",
    "{% block extrahead %}{% endblock extrahead %}\n"
    "    {% url 'storefrontapi:graphql' as sf_graphql_url %}\n"
    "    <script>window.SFStore = { currency: \"{{ request.CURRENCY_CODE|default:'USD'|escapejs }}\", symbol: \"{% filter escapejs %}{% currency_symbol request.CURRENCY_CODE|default:'USD' %}{% endfilter %}\", graphqlUrl: \"{{ sf_graphql_url|default:'/api/graphql/'|escapejs }}\" };\n"
    "    window.SFProductJson = {" + product_json + "};\n"
    "    {# Design handle -> NEXT product pk, for the Shopify variant ids design scripts carry. Each page lists only the products it references (block sf_handle_pk): every entry is a settings product lookup per render. #}\n"
    "    window.SFHandlePk = { {% block sf_handle_pk %}{% endblock sf_handle_pk %} };\n"
    "    window.SFVariantHandle = " + json.dumps(VARIANT2HANDLE, sort_keys=True) + ";\n"
    "    {# Theme settings > Subscription Offer: every add of this product (any variant, any button) is the plan below. #}\n"
    "    window.SFSubscriptionOnly = {% if settings.sf_subscription_product %}{ pks: [{% for sf_v in settings.sf_subscription_product.children.all %}\"{{ sf_v.pk }}\", {% endfor %}\"{{ settings.sf_subscription_product.pk }}\"], interval: \"{{ settings.sf_subscription_interval|default:'month'|escapejs }}\", intervalCount: \"{{ settings.sf_subscription_interval_count|default:'1'|escapejs }}\" }{% else %}null{% endif %};\n"
    "    {# Theme settings > Product Page: FrontrowMD listing for the Clinicians' Choice badge. #}\n"
    "    window.SFFrontrowId = \"{{ settings.sf_frontrow_product_id|default:''|escapejs }}\";\n"
    "    {# Theme settings > Subscription Offer: adds of this product that name no purchase type are the plan below. #}\n"
    "    window.SFDefaultPlan = {% if settings.sf_refill_default_product %}{ pks: [{% for sf_v in settings.sf_refill_default_product.children.all %}\"{{ sf_v.pk }}\", {% endfor %}\"{{ settings.sf_refill_default_product.pk }}\"], interval: \"{{ settings.sf_subscription_interval|default:'month'|escapejs }}\", intervalCount: \"{{ settings.sf_subscription_interval_count|default:'1'|escapejs }}\" }{% else %}null{% endif %};</script>\n"
    "    {# defer: runs before the design's deferred scripts (document order), after every inline script, never blocks paint #}\n"
    "    <script defer src=\"{{ 'js/skinofab-commerce.js'|asset_url }}\"></script>\n"
    "    {% block sf_head %}{% endblock sf_head %}")
base = base.replace('<a href="#main-content" class="skip-to-content">', '{% block sf_lead %}{% endblock sf_lead %}\n    <a href="#MainContent" class="skip-to-content visually-hidden">')
# The design header script reads [data-main] (first section, transparent header); Spark-native pages use this main.
base = base.replace('<main id="main-content" tabindex="-1">', '<main id="main-content" tabindex="-1" data-main>', 1)
# Spark's own theme.js (Spark header/menu/search widgets) would collide with the design's window.theme; the design ships its own.
base = base.replace("<script type=\"text/javascript\" src=\"{{ 'js/theme.js'|asset_url }}\"></script>", "")
# Side cart: SKINOFAB renderer in place of Spark's, configured from Theme settings > SKINOFAB > Cart Drawer
base = must_replace(base, "cartRenderer: \"{{ 'js/spark-cart-drawer-renderer.js'|asset_url|escapejs }}\"",
                    "cartRenderer: \"{{ 'js/skinofab-cart-drawer.js'|asset_url|escapejs }}\"", 'cart renderer')
# the products sold with Automatic Refills (sf-offer.json, by page slug): the drawer says "One-time purchase" on a
# line of one bought once (stick review 8)
_ro_path = EXPORT / 'sf-offer.json'
REFILL_HANDLES = (json.loads(_ro_path.read_text()).get('refill_handles') or []) if _ro_path.exists() else []
# a pack that comes with another of the store's products (by variant pk, the product pks): the drawer offers no add-on
# of it (the 2-stick pack's free Lymphatic Brush)
GIFT_INCLUDES = (json.loads(_ro_path.read_text()).get('gift_includes') or {}) if _ro_path.exists() else {}
SF_CART = ('''        <script>
        window.SFCart = {
            shippingFree: {% if settings.sf_cart_free_shipping %}true{% else %}false{% endif %},
            shippingNote: "{{ settings.sf_cart_shipping_note|default:''|escapejs }}",
            guaranteeTitle: "{{ settings.sf_cart_guarantee_title|default:''|escapejs }}", guaranteeText: "{{ settings.sf_cart_guarantee_text|default:''|escapejs }}",
            reviewText: "{{ settings.sf_cart_review_text|default:''|escapejs }}", reviewName: "{{ settings.sf_cart_review_name|default:''|escapejs }}",
            reviewPk: "{% if settings.sf_cart_review_product %}{{ settings.sf_cart_review_product.pk }}{% endif %}",
            upsellPks: [{% if settings.sf_cart_upsell_1 %}"{{ settings.sf_cart_upsell_1.pk }}", {% endif %}{% if settings.sf_cart_upsell_2 %}"{{ settings.sf_cart_upsell_2.pk }}", {% endif %}{% if settings.sf_cart_upsell_3 %}"{{ settings.sf_cart_upsell_3.pk }}"{% endif %}],
            upsellTitle: "{{ settings.sf_cart_upsell_title|default:''|escapejs }}", upsellButton: "{{ settings.sf_cart_upsell_button|default:'Add'|escapejs }}",
            upgrades: [{ from: "{{ settings.sf_cart_upgrade_from|default:''|escapejs }}", to: "{{ settings.sf_cart_upgrade_to|default:''|escapejs }}",
                title: "{{ settings.sf_cart_upgrade_title|default:''|escapejs }}", text: "{{ settings.sf_cart_upgrade_text|default:''|escapejs }}",
                button: "{{ settings.sf_cart_upgrade_button|default:'Upgrade'|escapejs }}", every: "{{ settings.sf_cart_upgrade_every|default:''|escapejs }}" },
              { from: "{{ settings.sf_cart_upgrade2_from|default:''|escapejs }}", to: "{{ settings.sf_cart_upgrade2_to|default:''|escapejs }}",
                title: "{{ settings.sf_cart_upgrade2_title|default:''|escapejs }}", text: "{{ settings.sf_cart_upgrade2_text|default:''|escapejs }}",
                button: "{{ settings.sf_cart_upgrade2_button|default:'Upgrade'|escapejs }}", every: "{{ settings.sf_cart_upgrade2_every|default:''|escapejs }}" },
              { from: "{{ settings.sf_cart_upgrade3_from|default:''|escapejs }}", to: "{{ settings.sf_cart_upgrade3_to|default:''|escapejs }}",
                title: "{{ settings.sf_cart_upgrade3_title|default:''|escapejs }}", text: "{{ settings.sf_cart_upgrade3_text|default:''|escapejs }}",
                button: "{{ settings.sf_cart_upgrade3_button|default:'Upgrade'|escapejs }}", every: "{{ settings.sf_cart_upgrade3_every|default:''|escapejs }}" },
              { from: "{{ settings.sf_cart_upgrade4_from|default:''|escapejs }}", to: "{{ settings.sf_cart_upgrade4_to|default:''|escapejs }}",
                title: "{{ settings.sf_cart_upgrade4_title|default:''|escapejs }}", text: "{{ settings.sf_cart_upgrade4_text|default:''|escapejs }}",
                button: "{{ settings.sf_cart_upgrade4_button|default:'Upgrade'|escapejs }}", every: "{{ settings.sf_cart_upgrade4_every|default:''|escapejs }}" },
              { from: "{{ settings.sf_cart_upgrade5_from|default:''|escapejs }}", to: "{{ settings.sf_cart_upgrade5_to|default:''|escapejs }}",
                title: "{{ settings.sf_cart_upgrade5_title|default:''|escapejs }}", text: "{{ settings.sf_cart_upgrade5_text|default:''|escapejs }}",
                button: "{{ settings.sf_cart_upgrade5_button|default:'Upgrade'|escapejs }}", every: "{{ settings.sf_cart_upgrade5_every|default:''|escapejs }}" },
              { from: "{{ settings.sf_cart_upgrade6_from|default:''|escapejs }}", to: "{{ settings.sf_cart_upgrade6_to|default:''|escapejs }}",
                title: "{{ settings.sf_cart_upgrade6_title|default:''|escapejs }}", text: "{{ settings.sf_cart_upgrade6_text|default:''|escapejs }}",
                button: "{{ settings.sf_cart_upgrade6_button|default:'Upgrade'|escapejs }}", every: "{{ settings.sf_cart_upgrade6_every|default:''|escapejs }}" }],
            payIcons: [PAY_ICONS_JS],
            checkoutText: "{{ settings.sf_cart_checkout_text|default:''|escapejs }}",
            cartUrl: "/cart/", changeText: "{{ settings.sf_cart_change_text|default:'Change'|escapejs }}",
            refillHandles: REFILL_HANDLES_JS, onceText: "One-time purchase", giftIncludes: GIFT_INCLUDES_JS,
            secureText: "{{ settings.sf_cart_secure_text|default:''|escapejs }}",
            couponToggle: "{{ settings.sf_cart_coupon_toggle|default:'Have a discount code?'|escapejs }}",
            removeText: "{{ settings.sf_cart_remove_text|default:'Remove'|escapejs }}",
            emptyTitle: "{{ settings.sf_cart_empty_title|default:''|escapejs }}",
            emptyText: "{{ settings.sf_cart_empty_text|default:''|escapejs }}",
            emptyImage: "{{ 'CART_BOTTLE'|asset_url|escapejs }}",
            shopUrl: "{% if settings.sf_cart_empty_product %}{{ settings.sf_cart_empty_product.get_absolute_url|escapejs }}{% else %}{% url 'catalogue:index' %}{% endif %}",
            shopText: "{% if settings.sf_cart_empty_cta %}{{ settings.sf_cart_empty_cta|escapejs }}{% elif settings.sf_cart_empty_product %}Shop {{ settings.sf_cart_empty_product.get_title|escapejs }}{% endif %}"
        };
        </script>
''').replace('CART_BOTTLE', CART_BOTTLE).replace('REFILL_HANDLES_JS', json.dumps(REFILL_HANDLES)).replace('GIFT_INCLUDES_JS', json.dumps(GIFT_INCLUDES)).replace('PAY_ICONS_JS', ''.join(
    "{%% if '%s' in settings.sf_pay_icons %%}{ src: \"{{ 'img/pay/%s.svg'|asset_url|escapejs }}\", alt: \"%s\" }, {%% endif %%}" % (k, k, alt)
    for k, alt in PAY_ICONS))
base = must_replace(base, "        <script type=\"text/javascript\" src=\"{{ 'js/spark-cart-loader.js'|asset_url }}\"></script>",
                    SF_CART + "        <script type=\"text/javascript\" src=\"{{ 'js/spark-cart-loader.js'|asset_url }}\"></script>", 'cart config')
base = base.replace("{% block extrascripts %}{% endblock %}", "{% block sf_tail %}{% endblock sf_tail %}\n    {% block extrascripts %}{% endblock %}")
write('layouts/base.html', base)

# Spark-native templates keep Spark styling (Tailwind main.css) inside the SKINOFAB chrome
# Spark pages under the design stylesheets: the design's .grid{grid-template-columns:var(--grid)} loads after Tailwind
# and beats its grid-cols utilities, and its list styles number Spark's breadcrumb <ol>. Restore both inside Spark's main.
SPARK_FIXES = ('<style>#main-content .grid-cols-1{grid-template-columns:repeat(1,minmax(0,1fr))}'
               '@media (min-width:40rem){ #main-content .sm\\:grid-cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}}'
               '@media (min-width:48rem){ #main-content .md\\:grid-cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}'
               '#main-content .md\\:grid-cols-3{grid-template-columns:repeat(3,minmax(0,1fr))}}'
               '#main-content nav ol{list-style:none;margin:0;padding:0}#main-content nav ol li{list-style:none}'
               '#main-content nav ol li::before,#main-content nav ol li::marker{content:none}'
               # form fields on these pages (review form, cart, support) were white on white: a visible border
               '#main-content form input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=submit]),'
               '#main-content form textarea{border:1px solid #cfcfcf !important;border-radius:10px !important;background:#fff !important}'
               # selects drew no arrow (the cart's quantity and refill choice did not look like they open, review 5)
               '#main-content form select{border:1px solid #cfcfcf !important;border-radius:10px !important;-webkit-appearance:none;appearance:none;padding-right:34px !important;'
               'background:#fff url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%2712%27 height=%278%27 viewBox=%270 0 12 8%27%3E%3Cpath d=%27M1 1.5l5 5 5-5%27 fill=%27none%27 stroke=%27%23151515%27 stroke-width=%271.6%27/%3E%3C/svg%3E") no-repeat right 12px center/12px 8px !important}'
               '#main-content form select{min-width:140px}'
               # Spark's light grey small print (Remove, Shipping, the breadcrumb) was 2.6:1 on white: slate-600, 7.6:1
               '#main-content .text-slate-400{color:#475569}#main-content a.text-slate-400:hover{color:#151515}'
               # the cart's lines on a phone: quantity, refill choice and Remove wrap onto a second line, and the
               # selects drop the 140 px minimum above (same id, so they need the higher specificity), so the line
               # total and Remove stay on screen (they were pushed 100 px past its right edge)
               '#cart_formset .flex.items-center.mt-3{flex-wrap:wrap;row-gap:8px}'
               '#main-content #cart_formset select{min-width:0;max-width:100%}'
               # a line's title and its total share a row: when the title wraps on a phone the total ran into it
               # ("Foundation - 1$37.00 bottle"); a gap, and the total never wraps or shrinks
               '#cart_formset .flex.items-start.justify-between{gap:16px}'
               '#cart_formset .flex.items-start.justify-between>div:last-child{white-space:nowrap;flex-shrink:0}'
               # the page's width and margins as the header's and footer's (it started 104 px in on a desktop)
               '#main-content .container{width:calc(100% - 64px);max-width:1440px;margin-left:auto;margin-right:auto;padding-left:0;padding-right:0}'
               '@media (max-width:749px){ #main-content .container{width:calc(100% - 32px)}}'   # "{ #": "{#" opens a DTL comment
               '#main-content form input:focus,#main-content form select:focus,#main-content form textarea:focus{border-color:#151515 !important;outline:none}'
               # the design's buttons are black with white text: Spark's secondary hover (slate-50) left the label white on
               # white (the cart's ADD COUPON, review 5)
               '#main-content .btn-secondary:hover,#main-content .btn-secondary:focus-visible{background:#333 !important;border-color:#333 !important;color:#fff !important}</style>')

for t in ['templates/cart.html', 'templates/403.html', 'templates/404.html', 'templates/500.html',
          *[str(p.relative_to(OUT)) for p in (OUT / 'templates').rglob('*.html') if p.parts[-2] in ('reviews', 'support')]]:
    p = OUT / t
    if not p.exists(): continue
    s = p.read_text()
    if '{% block spark_css %}' not in s:
        s = s.replace("{% extends 'layouts/base.html' %}", "{% extends 'layouts/base.html' %}\n{% block spark_css %}<link rel=\"stylesheet\" type=\"text/css\" href=\"{{ 'main.css'|asset_url }}\">{% endblock spark_css %}", 1)
        s = s.replace('{% extends "layouts/base.html" %}', '{% extends "layouts/base.html" %}\n{% block spark_css %}<link rel="stylesheet" type="text/css" href="{{ \'main.css\'|asset_url }}">{% endblock spark_css %}', 1)
        p.write_text(s)
    # The layout's design header/footer need the design's stylesheets and scripts, which Spark-native pages don't
    # carry: borrow a plain design page's head and tail (contact; every simple page has the same ones).
    # The header script reads the body class on load (hide-header etc.), so the body class and lead come along too.
    if '{% block sf_head %}' not in s and 'contact' in PAGE_PARTS:
        s = s.replace('{% endblock spark_css %}', "{% endblock spark_css %}"
                      "\n{% block body_class %}" + PAGE_PARTS['contact']['body_class'] + "{% endblock body_class %}"
                      "\n{% block sf_head %}{% include 'partials/sf_pages/contact/head.html' %}" + SPARK_FIXES + "{% endblock sf_head %}"
                      "\n{% block sf_lead %}{% include 'partials/sf_pages/contact/lead.html' %}{% endblock sf_lead %}"
                      "\n{% block sf_tail %}{% include 'partials/sf_pages/contact/tail.html' %}{% endblock sf_tail %}", 1)
        p.write_text(s)

# Review form: the score was a plain select of "---------", 0, 1 ... 5 (a 0-star review was one choice): five stars
# to click instead (1-5, required; radio inputs, so it works without script and by keyboard)
SCORE_FIELD = "{% include 'partials/form_field.html' with field=form.score %}"
SCORE_STARS = ('<fieldset class="sf-score"><legend class="block text-sm font-medium text-slate-700 mb-1">{{ form.score.label }} '
               '<span class="text-red-500">*</span></legend><div class="sf-stars">'
               '{% for v in "54321" %}<input type="radio" id="sf-score-{{ v }}" name="{{ form.score.html_name }}" value="{{ v }}" required'
               '{% if form.score.value == v %} checked{% endif %}><label for="sf-score-{{ v }}" title="{{ v }} of 5 stars">&#9733;</label>{% endfor %}</div>'
               '{% for error in form.score.errors %}<p class="text-xs text-red-500 mt-1">{{ error }}</p>{% endfor %}</fieldset>'
               '<style>.sf-score{border:0;margin:0;padding:0}.sf-stars{display:inline-flex;flex-direction:row-reverse;gap:6px}'
               '.sf-stars input{position:absolute;opacity:0;width:1px;height:1px}'
               '.sf-stars label{font-size:34px;line-height:1;color:#d6d6d6;cursor:pointer}'
               '.sf-stars input:checked~label,.sf-stars label:hover,.sf-stars label:hover~label{color:#151515}'
               '.sf-stars input:focus-visible+label{outline:2px solid #151515;outline-offset:2px;border-radius:4px}</style>')
p_form = OUT / 'templates' / 'reviews' / 'form.html'
if p_form.exists():
    s = p_form.read_text()
    if s.count(SCORE_FIELD) != 1: sys.exit('templates/reviews/form.html: score field not found once')
    p_form.write_text(s.replace(SCORE_FIELD, SCORE_STARS))

# Review pages (the list, the form, one review): a product's first category is a NEXT grouping that is not a shop
# section (the foundation's is "B2G5"), so the breadcrumb goes Home / Shop / product; the product's base price is not
# what its page sells it for (refill and pack prices), so they show none; and "no reviews yet" spoke over the imported
# reviews the product page shows, so it points there.
REVIEW_CRUMB = re.compile(r'\{% with category=product\.categories\.all\.0 %\}.*?\{% endwith %\}', re.S)
REVIEW_PRICE = re.compile(r'\{% purchase_info_for_product request product as session %\}\s*\{% if session\.price\.exists %\}.*?'
                          r'\{% endif %\}\s*\{% endif %\}\s*', re.S)
SHOP_CRUMB = ('<li><a href="{% url \'catalogue:index\' %}" class="hover:text-slate-600">Shop</a></li>\n            <li>/</li>')
NO_REVIEWS = '<p class="text-slate-500">{% t "store.review.no_reviews" %}</p>'
SEE_REVIEWS = ('<p class="text-slate-600">Read what customers say on the <a href="{{ product.get_absolute_url }}#sf-review-wall" '
               'class="underline">{{ product.get_title }} page</a>.</p>')
for name in ('index.html', 'review.html'):
    f = OUT / 'templates' / 'reviews' / name
    if not f.exists(): continue
    s = f.read_text()
    s, a = REVIEW_CRUMB.subn(SHOP_CRUMB, s, count=1)
    s, b = REVIEW_PRICE.subn('', s, count=1)
    if not (a and b): sys.exit(f'templates/reviews/{name}: breadcrumb or price block not found')
    if name == 'index.html':
        if s.count(NO_REVIEWS) != 1: sys.exit('templates/reviews/index.html: empty state not found once')
        s = s.replace(NO_REVIEWS, SEE_REVIEWS)
    f.write_text(s)

# Cart page: Spark's per-line frequency select offers "One Time"; a line of the subscription-only product
# (Theme settings > Subscription Offer) keeps the plan instead, as a fixed label + hidden value.
SUB_ONLY_IF = ("{% if settings.sf_subscription_product and product.parent.pk == settings.sf_subscription_product.pk"
               " or settings.sf_subscription_product and product.pk == settings.sf_subscription_product.pk %}")
SUB_FIXED = ('<input type="hidden" name="{{ form.subscription_range.html_name }}" value="{{ settings.sf_subscription_interval_count|default:\'1\' }}-{{ settings.sf_subscription_interval|default:\'month\' }}">'
             '<span class="text-xs text-slate-600">Automatic refill &middot; cancel any time</span>')
for rel, old_field in (('templates/cart.html', '{{ form.subscription_range }}'),
                       ('partials/cart_content.html', "{% include 'partials/form_field.html' with field=form.subscription_range nolabel=True %}")):
    p = OUT / rel
    if not p.exists(): continue
    s = p.read_text()
    if 'sf_subscription_product' in s: continue
    if s.count(old_field) != 1: sys.exit(f'{rel}: subscription_range field not found once')
    # (with the line's SKU beside the select: REFILL_LABELS keeps the pack's own refill schedule)
    s = s.replace(old_field, SUB_ONLY_IF + SUB_FIXED + '{% else %}' + old_field
                  + '<i hidden data-sf-sku="{{ product.sku }}"></i>{% endif %}')   # both bind `product` to the line's
    p.write_text(s)

# Cart page: Spark's frequency select read "One Time" / "28 Days", a bare number with nothing saying it repeats. The
# options say what they are ("One-time purchase", "Refill every 28 days") and a refill line says, under it, that it
# ships and is charged on that schedule until cancelled (the cart may redraw its lines: the observer relabels them).
# A refill pack (sf-offer.json's pack_every, by SKU) offers one-time or its own schedule only: NEXT keeps one list of
# intervals per product, so a 2-stick pack could be set to the 1-stick schedule at the same price (stick review 2).
_oc_path = EXPORT / 'sf-offer.json'
PACK_EVERY = (json.loads(_oc_path.read_text()).get('pack_every') or {}) if _oc_path.exists() else {}
# each pack's [one-time, refill] price, by SKU: the two options say what each costs ("One-time purchase · $59",
# "Refill every 56 days · $47"; stick review 7: the one-time choice named no price)
PACK_PRICES = (json.loads(_oc_path.read_text()).get('pack_prices') or {}) if _oc_path.exists() else {}
REFILL_LABELS = ('<script data-sf-refill-labels>(function () {'
    f'var EVERY = {json.dumps(PACK_EVERY)}, PRICES = {json.dumps(PACK_PRICES)};'
    'function money(v) { return " · $" + (v % 1 ? v.toFixed(2) : String(v)); }'
    'function set(el, prop, v) { if (el[prop] !== v) el[prop] = v; }'
    'function sku(s) { for (var p = s.parentNode, k = 0; p && k < 3; p = p.parentNode, k++) {'
    ' var m = p.querySelector("[data-sf-sku]"); if (m) return m.getAttribute("data-sf-sku"); } return ""; }'
    'function label() {'
    ' Array.prototype.forEach.call(document.querySelectorAll(\'select[name$="subscription_range"]\'), function (s) {'
    # a product with no refill plan had a select with its one option: the words instead
    '  if (s.options.length < 2) { if (!s.getAttribute("data-sf-single")) { s.setAttribute("data-sf-single", "1"); s.style.display = "none";'
    '   var w = document.createElement("span"); w.className = "text-xs text-slate-600"; w.textContent = "One-time purchase";'
    '   s.parentNode.insertBefore(w, s.nextSibling); } return; }'
    '  var every = EVERY[sku(s)], pr = PRICES[sku(s)];'
    '  if (every) Array.prototype.slice.call(s.options).forEach(function (o) {'
    '   var d = (o.textContent.match(/(\\d+)\\s*day/i) || [])[1];'
    '   if (d && +d !== every && !o.selected) s.removeChild(o); });'
    '  Array.prototype.forEach.call(s.options, function (o) {'
    '   var t = o.textContent.trim(), m = t.match(/^(\\d+)\\s+(day|week|month|year)s?$/i);'
    '   if (/^one time$/i.test(t)) set(o, "textContent", "One-time purchase" + (pr ? money(pr[0]) : ""));'
    '   else if (m) set(o, "textContent", "Refill every " + (m[1] === "1" ? "" : m[1] + " ") + m[2].toLowerCase() + (m[1] === "1" ? "" : "s")'
    '    + (pr ? money(pr[1]) : ""));'
    '  });'
    '  var row = s.parentNode, note = row.querySelector(".sf-refill-note");'
    '  if (!note) { note = document.createElement("p"); note.className = "sf-refill-note text-xs text-slate-600";'
    '   note.style.cssText = "flex-basis:100%;margin:0"; row.appendChild(note); }'
    '  var o = s.options[s.selectedIndex], on = !!o && /^Refill every/.test(o.textContent);'
    '  set(note, "textContent", on ? "Automatic refill: we ship and charge it " + o.textContent.replace("Refill every", "every").replace(/ · .*$/, "")'
    '   + " until you cancel. Skip or cancel any time by email." : "");'
    '  set(note, "hidden", !on);'
    '  if (!s.getAttribute("data-sf-refill")) { s.setAttribute("data-sf-refill", "1"); s.addEventListener("change", label); }'
    ' });'
    '}'
    'label();'
    'var queued = false;'
    'new MutationObserver(function () { if (queued) return; queued = true;'
    ' requestAnimationFrame(function () { queued = false; label(); }); }).observe(document.body, { childList: true, subtree: true });'
    '})();</script>')
p_cart = OUT / 'templates/cart.html'
if p_cart.exists():
    t = p_cart.read_text()
    if 'data-sf-refill-labels' not in t:
        p_cart.write_text(must_replace(t, '                </form>', '                </form>' + REFILL_LABELS, 'templates/cart.html refill labels'))

# Cart page: the checkout button's words on one line (at 768 px the summary column wrapped "Proceed to checkout"
# onto two, review 7)
if p_cart.exists():
    t = p_cart.read_text()
    old_btn = 'class="btn btn-primary w-full mt-6 py-3 text-base">'
    if 'data-sf-checkout-nowrap' not in t:
        p_cart.write_text(must_replace(t, old_btn, old_btn[:-1] + ' data-sf-checkout-nowrap style="white-space:nowrap">',
                                       'templates/cart.html checkout button'))

# Cart page: the lines and the summary side by side from 1024 px, not 768: at 768 the summary column was 171 px and
# its one-line "Proceed to checkout" (above) ran out of the button ("PROCEED TO CHECK", store audit 8). Under 1024 px
# the summary goes under the lines, full width.
if p_cart.exists():
    t = p_cart.read_text()
    if 'sf-cart-grid' not in t:
        t = must_replace(t, '<div class="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">',
                         # ("{ #": "{#" opens a template comment)
                         '<style>@media (min-width:64rem){ #main-content .sf-cart-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:3rem}'
                         '#main-content .sf-cart-lines{grid-column:span 2/span 2}}</style>'
                         '<div class="grid grid-cols-1 gap-8 sf-cart-grid">', 'templates/cart.html grid')
        p_cart.write_text(must_replace(t, '<div class="md:col-span-2">', '<div class="sf-cart-lines">', 'templates/cart.html lines column'))

# Cart page: the layout already shows the page's messages above its content; the cart's own copy showed each one twice
# (an unknown coupon: the same error at the top and above the lines, review 5). The AJAX partial keeps its own.
if p_cart.exists():
    t = p_cart.read_text()
    if t.count('{% include "partials/alert_messages.html" %}') == 1:
        p_cart.write_text(re.sub(r'[ \t]*\{% include "partials/alert_messages\.html" %\}\n?', '', t, count=1))
    elif '{% include "partials/alert_messages.html" %}' in t: sys.exit('templates/cart.html: alert messages included more than once')

# Product thumbnails on Spark's pages were cut at their display size (the cart's 100 px, the AJAX cart's 80 px, the
# reviews' 180 px tall): a phone or tablet scaled them up 2-3x and the bottle's label smeared (review 5). Cut at 3x
# (2x for the reviews' 112 px box); the pages still show them at the same size (their width/height or classes).
for rel, old, new in (('templates/cart.html', '"100x100" crop="center"', '"300x300" crop="center"'),
                      ('partials/cart_content.html', '"80x80" crop="center"', '"240x240" crop="center"'),
                      ('templates/reviews/index.html', 'image.original "x180"', 'image.original "x360"'),
                      ('templates/reviews/review.html', 'image.original "x180"', 'image.original "x360"')):
    p = OUT / rel
    if not p.exists(): continue
    t = p.read_text()
    if new not in t: p.write_text(must_replace(t, old, new, rel + ' thumbnail size'))

# Cart page: free shipping said plainly when the store ships for free (Theme settings > SKINOFAB > Cart Drawer)
FREE_SHIP = "{% if settings.sf_cart_free_shipping %}<span class=\"text-xs font-semibold\" style=\"color:#1f7a3f\">{% t 'store.catalogue.free' %}</span>{% else %}"
for rel, old_span in (('templates/cart.html', '<span class="text-xs">{% t "order.cart.calculated_at_checkout" %}</span>'),
                      ('partials/cart_summary.html', '<span class="text-xs text-slate-400">{% t "order.cart.calculated_at_checkout" %}</span>')):
    p = OUT / rel
    if not p.exists(): continue
    t = p.read_text()
    if 'sf_cart_free_shipping' not in t:
        p.write_text(must_replace(t, old_span, FREE_SHIP + old_span + '{% endif %}', rel + ' shipping'))

# ---------------------------------------------------------------- 8b. per-page product lookups (window.SFHandlePk)
# Design scripts carry Shopify variant ids (permalinks, bundle builders, product JSON); the commerce adapter maps them
# to NEXT through window.SFHandlePk. Each entry resolves a settings product (and its first child) on every render,
# so a page lists only the handles whose ids occur in its own markup, plus the header/footer's.
def handles_in(text):
    return {VARIANT2HANDLE[i] for i in re.findall(r'(?<!\d)(\d{11,16})(?!\d)', text) if i in VARIANT2HANDLE}

def handle_entries(handles):
    return ','.join('"%s":"{%% firstof settings.sf_p_%s.children.first.pk settings.sf_p_%s.pk %%}"' % (h, var(h), var(h))
                    for h in sorted(handles))

CHROME_HANDLES = handles_in((OUT / 'partials/header.html').read_text() + (OUT / 'partials/footer.html').read_text())
if CHROME_HANDLES:
    b = (OUT / 'layouts/base.html').read_text()
    (OUT / 'layouts/base.html').write_text(b.replace('{% block sf_handle_pk %}{% endblock sf_handle_pk %}',
                                                     '{% block sf_handle_pk %}' + handle_entries(CHROME_HANDLES) + '{% endblock sf_handle_pk %}'))
for p in sorted((OUT / 'templates').rglob('*.html')):
    s = p.read_text()
    if not s.startswith("{% extends 'layouts/base.html' %}") or '{% block sf_handle_pk %}' in s: continue
    if p.name == 'page.html' and p.parent.name == 'pages':
        per = {sl: handles_in(''.join(f.read_text() for f in (OUT / 'partials/sf_pages' / sl).glob('*.html'))) - CHROME_HANDLES
               for sl in sorted(PAGE_PARTS)}
        per = {sl: h for sl, h in per.items() if h}
        if not per: continue
        body = ''.join("{%% %s page.slug == '%s' %%}%s" % ('if' if i == 0 else 'elif', sl, handle_entries(h | CHROME_HANDLES))
                       for i, (sl, h) in enumerate(per.items())) + '{% else %}{{ block.super }}{% endif %}'
    else:
        h = handles_in(s) - CHROME_HANDLES
        if not h: continue
        body = handle_entries(h | CHROME_HANDLES)
    p.write_text(s.replace("{% extends 'layouts/base.html' %}", "{% extends 'layouts/base.html' %}\n{% block sf_handle_pk %}" + body + "{% endblock sf_handle_pk %}", 1))
    LOG.setdefault('handle_pk_pages', {})[str(p.relative_to(OUT))] = len(h) if p.name != 'page.html' else sum(map(len, per.values()))

# ---------------------------------------------------------------- 8c. one lookup per product setting and block
# A page names a product setting (settings.sf_p_<handle>) wherever it links to the product or shows its price: the
# homepage did it 140 times, and each one fetched the product again while NEXT rendered the page (its server time
# was 0.3 s above the other pages'). Each block now fetches each product once ({% with %}) and uses it throughout,
# and looks up each product's purchase info (its price) once for all of its prices.
def one_lookup(t):
    out, pos = [], 0
    for m in re.finditer(r'\{% block (\w+) %\}', t):
        if m.start() < pos: continue
        depth, i = 1, m.end()
        for n in re.finditer(r'\{% (block \w+|endblock(?: \w+)?) %\}', t[m.end():]):
            depth += 1 if n.group(1).startswith('block') else -1
            if depth == 0:
                end, close = m.end() + n.start(), m.end() + n.end(); break
        else:
            continue
        body = t[m.end():end]
        names = sorted(set(re.findall(r'settings\.sf_p_(\w+)', body)))
        if names and len(re.findall(r'settings\.sf_p_\w+', body)) > len(names):
            body = re.sub(r'settings\.sf_p_(\w+)', r'sf_pp_\1', body)
            # a product whose price shows more than once: its purchase info once, for every one of its prices
            inc = lambda n: re.compile(r"\{% include 'partials/sf_price\.html' with p=sf_pp_" + n + r"\b")
            priced = [n for n in names if len(inc(n).findall(body)) > 1]
            for n in priced:
                body = inc(n).sub(lambda m: "{% include 'partials/sf_price_pi.html' with p=sf_pp_" + n + " sf_s=sf_pi_" + n, body)
            infos = ''.join('{% if sf_pp_' + n + ' %}{% purchase_info_for_product request sf_pp_' + n + ' as sf_pi_' + n + ' %}{% endif %}' for n in priced)
            body = '{% with ' + ' '.join(f'sf_pp_{n}=settings.sf_p_{n}' for n in names) + ' %}' + infos + body + '{% endwith %}'
        out.append(t[pos:m.end()] + body + t[end:close]); pos = close
    out.append(t[pos:])
    return ''.join(out)
LOG['one_lookup'] = 0
for tpl in sorted((OUT / 'templates').rglob('*.html')):
    t0 = tpl.read_text(encoding='utf-8')
    t1 = one_lookup(t0)
    if t1 != t0: tpl.write_text(t1, encoding='utf-8'); LOG['one_lookup'] += 1

# ---------------------------------------------------------------- 9. settings
schema = json.loads((OUT / 'configs' / 'settings_schema.json').read_text())
titles = {h: (d.get('title') or h) for h, d in PRODUCT_JSON.items()}
handles = sorted({m.group(1) for f in EXPORTED for m in [re.fullmatch(r'products/([a-z0-9][a-z0-9-]*)\.html', f)] if m})
collections = sorted({m.group(1) for f in EXPORTED for m in [re.fullmatch(r'collections/([a-z0-9][a-z0-9-]*)\.html', f)] if m} - {'all', 'all-products'})
schema = {'SKINOFAB': {
    'Product Links': [{'name': f'sf_p_{var(h)}', 'type': 'product', 'label': titles.get(h, h),
                       'help_text': f'NEXT product shown wherever the design links to "{h}": links, prices and add to cart. Also set this product\'s template to "{h}".'}
                      for h in handles],
    'Checkout Add-ons': [{'name': 'sf_shipping_protection', 'type': 'product', 'label': 'Premium Shipping Protection',
                          'help_text': 'NEXT product whose price the design quotes for shipping protection (FAQ and buy-box copy).'},
                         {'name': 'sf_shipping_fee_text', 'type': 'text', 'label': 'Shipping Fee (as shown in delivery copy)', 'default': '$2.99 USD',
                          'help_text': 'Must match the shipping rate configured in Dashboard > Settings > Shipping.'}],
    'Product Page': [{'name': 'sf_frontrow_product_id', 'type': 'text', 'label': 'FrontrowMD product ID', 'default': '',
                      'help_text': "Shows FrontrowMD's Clinicians' Choice badge under the product title (its clinicians and FAQ open on click). Leave empty to hide."}],
    'Subscription Offer': [{'name': 'sf_refill_default_product', 'type': 'product', 'label': 'Refills by default',
                            'help_text': 'Every add to cart of this product that names no purchase type is the plan below; one-time stays available where a button or the cart page offers it.'},
                           {'name': 'sf_refill_price_text', 'type': 'text', 'label': 'Refills by default: price text', 'default': '',
                            'help_text': 'Shown as that product\'s price on cards and listings, e.g. $37 USD: the price its page shows first, with refills ticked. Empty: its NEXT price.'},
                           {'name': 'sf_refill_compare_text', 'type': 'text', 'label': 'Refills by default: was-price text', 'default': '',
                            'help_text': 'Shown struck through next to it, e.g. $59 USD. Empty: none.'},
                           *[s for k in REFILL_SLOTS for s in (
                               {'name': f'sf_refill_product_{k}', 'type': 'product', 'label': f'Refills by default ({k})',
                                'help_text': 'Another product sold with refills by default (its product page adds it as a refill): its cards and listings show the texts below.'},
                               {'name': f'sf_refill_price_text_{k}', 'type': 'text', 'label': f'Refills by default ({k}): price text', 'default': ''},
                               {'name': f'sf_refill_compare_text_{k}', 'type': 'text', 'label': f'Refills by default ({k}): was-price text', 'default': ''},
                               {'name': f'sf_refill_every_{k}', 'type': 'text', 'label': f'Refills by default ({k}): days between refills', 'default': ''})],
                           {'name': 'sf_subscription_product', 'type': 'product', 'label': 'Subscription-only product',
                            'help_text': 'Sold by subscription only: every add to cart of this product is the plan below, and its prices show the plan price text. Leave empty to sell everything normally.'},
                           {'name': 'sf_subscription_interval', 'type': 'text', 'label': 'Plan interval', 'default': 'month',
                            'help_text': 'day, week or month. Must be enabled on the product in NEXT.'},
                           {'name': 'sf_subscription_interval_count', 'type': 'text', 'label': 'Plan interval count', 'default': '1',
                            'help_text': 'Every how many intervals the refill ships (1 = every month). Must be one of the product\'s interval counts.'},
                           {'name': 'sf_subscription_price_text', 'type': 'text', 'label': 'Plan price text', 'default': '',
                            'help_text': 'Shown wherever the product\'s price appears, e.g. $33/mo. Must match the subscription price on the product variants.'}],
    'Cart Drawer': [
        {'name': 'sf_cart_free_shipping', 'type': 'checkbox', 'label': 'Shipping is free', 'default': True,
         'help_text': 'Shows "Free" for shipping in the cart. Tick only while every rate in Dashboard > Settings > Shipping is $0.'},
        {'name': 'sf_cart_shipping_note', 'type': 'text', 'label': 'Note under the cart title', 'default': 'Free shipping on every order',
         'help_text': 'Leave empty to hide. Must match your shipping rates.'},
        {'name': 'sf_cart_upgrade_from', 'type': 'text', 'label': 'Upgrade: variant in the bag', 'default': '',
         'help_text': 'NEXT variant ID. While the bag has it (and not the upgrade), the drawer offers the upgrade. Empty: no upgrade.'},
        {'name': 'sf_cart_upgrade_to', 'type': 'text', 'label': 'Upgrade: variant it becomes', 'default': '',
         'help_text': 'NEXT variant ID. Same quantity and the same refill choice as the line it replaces.'},
        {'name': 'sf_cart_upgrade_title', 'type': 'text', 'label': 'Upgrade: title', 'default': ''},
        {'name': 'sf_cart_upgrade_text', 'type': 'text', 'label': 'Upgrade: text', 'default': '',
         'help_text': 'Name the real price difference; it must match the two variants\' prices.'},
        {'name': 'sf_cart_upgrade_button', 'type': 'text', 'label': 'Upgrade: button', 'default': 'Upgrade'},
        {'name': 'sf_cart_upgrade_every', 'type': 'text', 'label': 'Upgrade: refill days of the bigger pack', 'default': '',
         'help_text': 'A refill line upgraded to the bigger pack ships every this many days (it lasts longer). Empty: as often as before.'},
        {'name': 'sf_cart_upgrade2_from', 'type': 'text', 'label': 'Second upgrade: variant in the bag', 'default': '',
         'help_text': 'A second product\'s upgrade (NEXT variant IDs), shown when the first one does not apply. Empty: none.'},
        {'name': 'sf_cart_upgrade2_to', 'type': 'text', 'label': 'Second upgrade: variant it becomes', 'default': ''},
        {'name': 'sf_cart_upgrade2_title', 'type': 'text', 'label': 'Second upgrade: title', 'default': ''},
        {'name': 'sf_cart_upgrade2_text', 'type': 'text', 'label': 'Second upgrade: text', 'default': '',
         'help_text': 'Name the real price difference; it must match the two variants\' prices.'},
        {'name': 'sf_cart_upgrade2_button', 'type': 'text', 'label': 'Second upgrade: button', 'default': 'Upgrade'},
        {'name': 'sf_cart_upgrade2_every', 'type': 'text', 'label': 'Second upgrade: refill days of the bigger pack', 'default': '',
         'help_text': 'A refill line upgraded to the bigger pack ships every this many days (it lasts longer). Empty: as often as before.'},
        {'name': 'sf_cart_upgrade3_from', 'type': 'text', 'label': 'Third upgrade: variant in the bag', 'default': '',
         'help_text': 'A third product\'s upgrade (NEXT variant IDs), shown when the first two do not apply. Empty: none.'},
        {'name': 'sf_cart_upgrade3_to', 'type': 'text', 'label': 'Third upgrade: variant it becomes', 'default': ''},
        {'name': 'sf_cart_upgrade3_title', 'type': 'text', 'label': 'Third upgrade: title', 'default': ''},
        {'name': 'sf_cart_upgrade3_text', 'type': 'text', 'label': 'Third upgrade: text', 'default': '',
         'help_text': 'Name the real price difference; it must match the two variants\' prices.'},
        {'name': 'sf_cart_upgrade3_button', 'type': 'text', 'label': 'Third upgrade: button', 'default': 'Upgrade'},
        {'name': 'sf_cart_upgrade3_every', 'type': 'text', 'label': 'Third upgrade: refill days of the bigger pack', 'default': '',
         'help_text': 'A refill line upgraded to the bigger pack ships every this many days (it lasts longer). Empty: as often as before.'},
        {'name': 'sf_cart_upgrade4_from', 'type': 'text', 'label': 'Fourth upgrade: variant in the bag', 'default': '',
         'help_text': 'A fourth product\'s upgrade (NEXT variant IDs), shown when the first three do not apply. Empty: none.'},
        {'name': 'sf_cart_upgrade4_to', 'type': 'text', 'label': 'Fourth upgrade: variant it becomes', 'default': ''},
        {'name': 'sf_cart_upgrade4_title', 'type': 'text', 'label': 'Fourth upgrade: title', 'default': ''},
        {'name': 'sf_cart_upgrade4_text', 'type': 'text', 'label': 'Fourth upgrade: text', 'default': '',
         'help_text': 'Name the real price difference; it must match the two variants\' prices.'},
        {'name': 'sf_cart_upgrade4_button', 'type': 'text', 'label': 'Fourth upgrade: button', 'default': 'Upgrade'},
        {'name': 'sf_cart_upgrade4_every', 'type': 'text', 'label': 'Fourth upgrade: refill days of the bigger pack', 'default': '',
         'help_text': 'A refill line upgraded to the bigger pack ships every this many days (it lasts longer). Empty: as often as before.'},
        {'name': 'sf_cart_upgrade5_from', 'type': 'text', 'label': 'Fifth upgrade: variant in the bag', 'default': '',
         'help_text': 'A fifth product\'s upgrade (NEXT variant IDs), shown when the first four do not apply. Empty: none.'},
        {'name': 'sf_cart_upgrade5_to', 'type': 'text', 'label': 'Fifth upgrade: variant it becomes', 'default': ''},
        {'name': 'sf_cart_upgrade5_title', 'type': 'text', 'label': 'Fifth upgrade: title', 'default': ''},
        {'name': 'sf_cart_upgrade5_text', 'type': 'text', 'label': 'Fifth upgrade: text', 'default': '',
         'help_text': 'Name the real price difference; it must match the two variants\' prices.'},
        {'name': 'sf_cart_upgrade5_button', 'type': 'text', 'label': 'Fifth upgrade: button', 'default': 'Upgrade'},
        {'name': 'sf_cart_upgrade5_every', 'type': 'text', 'label': 'Fifth upgrade: refill days of the bigger pack', 'default': '',
         'help_text': 'A refill line upgraded to the bigger pack ships every this many days (it lasts longer). Empty: as often as before.'},
        {'name': 'sf_cart_upgrade6_from', 'type': 'text', 'label': 'Sixth upgrade: variant in the bag', 'default': '',
         'help_text': 'One more upgrade (NEXT variant IDs), such as a 2-pack to a 3-pack, shown when the others do not apply. Empty: none.'},
        {'name': 'sf_cart_upgrade6_to', 'type': 'text', 'label': 'Sixth upgrade: variant it becomes', 'default': ''},
        {'name': 'sf_cart_upgrade6_title', 'type': 'text', 'label': 'Sixth upgrade: title', 'default': ''},
        {'name': 'sf_cart_upgrade6_text', 'type': 'text', 'label': 'Sixth upgrade: text', 'default': '',
         'help_text': 'Name the real price difference; it must match the two variants\' prices.'},
        {'name': 'sf_cart_upgrade6_button', 'type': 'text', 'label': 'Sixth upgrade: button', 'default': 'Upgrade'},
        {'name': 'sf_cart_upgrade6_every', 'type': 'text', 'label': 'Sixth upgrade: refill days of the bigger pack', 'default': '',
         'help_text': 'A refill line upgraded to the bigger pack ships every this many days (it lasts longer). Empty: as often as before.'},
        {'name': 'sf_cart_upsell_1', 'type': 'product', 'label': 'Add-on 1', 'help_text': 'Two add-ons not yet in the bag are offered under the bag lines, in this order.'},
        {'name': 'sf_cart_upsell_2', 'type': 'product', 'label': 'Add-on 2'},
        {'name': 'sf_cart_upsell_3', 'type': 'product', 'label': 'Add-on 3'},
        {'name': 'sf_cart_upsell_title', 'type': 'text', 'label': 'Add-ons title', 'default': 'Complete your routine'},
        {'name': 'sf_cart_upsell_button', 'type': 'text', 'label': 'Add-on button', 'default': 'Add'},
        {'name': 'sf_cart_guarantee_title', 'type': 'text', 'label': 'Guarantee title', 'default': '30-day money-back guarantee'},
        {'name': 'sf_cart_guarantee_text', 'type': 'text', 'label': 'Guarantee text', 'default': "Try it for 30 days. If you don't love it, we'll refund you.",
         'help_text': 'Must match your refund policy.'},
        {'name': 'sf_cart_review_text', 'type': 'text', 'label': 'Review quote', 'default': '',
         'help_text': 'A real customer review, word for word. Leave empty to hide.'},
        {'name': 'sf_cart_review_name', 'type': 'text', 'label': 'Review name', 'default': ''},
        {'name': 'sf_cart_review_product', 'type': 'product', 'label': 'Review is about',
         'help_text': 'The quote shows only while this product is in the bag. Empty: always.'},
        {'name': 'sf_cart_checkout_text', 'type': 'text', 'label': 'Checkout button', 'default': 'Secure checkout'},
        {'name': 'sf_cart_change_text', 'type': 'text', 'label': 'Refill line: link to change it', 'default': 'Change',
         'help_text': 'After "Refills every 28 days": opens the bag page, where the shopper picks One Time or refills.'},
        {'name': 'sf_pay_icons', 'type': 'text', 'label': 'Payment logos (cart and footer)', 'default': 'visa, mc, amex, discover',
         'help_text': 'Any of: visa, mc, amex, discover, applepay, googlepay, ppal, klarna, diners, jcb, maestro, dankort. List only what your checkout accepts.'},
        {'name': 'sf_cart_secure_text', 'type': 'text', 'label': 'Under the checkout button', 'default': 'Secure, encrypted payment'},
        {'name': 'sf_cart_coupon_toggle', 'type': 'text', 'label': 'Discount code link', 'default': 'Have a discount code?'},
        {'name': 'sf_cart_remove_text', 'type': 'text', 'label': 'Remove link', 'default': 'Remove'},
        {'name': 'sf_cart_empty_title', 'type': 'text', 'label': 'Empty cart title', 'default': 'Your bag is empty'},
        {'name': 'sf_cart_empty_text', 'type': 'text', 'label': 'Empty cart text',
         'default': 'Free shipping and a 30-day money-back guarantee on every order.'},
        {'name': 'sf_cart_empty_product', 'type': 'product', 'label': 'Empty cart button goes to'},
        {'name': 'sf_cart_empty_cta', 'type': 'text', 'label': 'Empty cart button', 'default': '',
         'help_text': 'Leave empty for "Shop <product above>".'},
    ],
    'Collection Links': [{'name': f'sf_c_{var(c)}', 'type': 'url', 'label': c.replace('-', ' ').title(), 'default': '/catalogue/',
                          'help_text': f'Where the design\'s "{c}" collection links go (a NEXT category URL).'} for c in collections],
}, **schema}
(OUT / 'configs' / 'settings_schema.json').write_text(json.dumps(schema, indent=2, ensure_ascii=False) + '\n')
data = json.loads((OUT / 'configs' / 'settings_data.json').read_text())
for group in schema['SKINOFAB'].values():
    for field in group:
        data.setdefault(field['name'], field.get('default') if field['type'] != 'product' else None)
data.setdefault('cart_header_title', 'Your bag')
# the empty bag's old line was the foundation's ("Your shade is about a minute away."): every product's page shows it
# (stick review 9)
if data.get('sf_cart_empty_text') == 'Your shade is about a minute away.':
    data['sf_cart_empty_text'] = 'Free shipping and a 30-day money-back guarantee on every order.'
# a product or collection link the theme no longer has (the store dropped it): its old value goes too
_names = {f['name'] for group in schema['SKINOFAB'].values() for f in group}
for k in [k for k in data if k.startswith(('sf_p_', 'sf_c_')) and k not in _names]: del data[k]
catalog = os.environ.get('SF_CATALOG')  # deploy mapping (tools/next-deploy) -> Product / Collection Links
if catalog and Path(catalog).exists():
    m = json.loads(Path(catalog).read_text())['mapping']
    # only what the theme still has a setting for: the catalog also lists products and categories the store dropped
    names = _names
    for h, v in m.get('products', {}).items():
        if v.get('id') and f'sf_p_{var(h)}' in names: data[f'sf_p_{var(h)}'] = v['id']
    for c, cid in m.get('categories', {}).items():
        if cid and f'sf_c_{var(c)}' in names: data[f'sf_c_{var(c)}'] = f'/catalogue/category/{c}_{cid}/'
offer_cfg = EXPORT / 'sf-offer.json'   # written by tools/persona/apply_persona.py: the cart drawer's offer settings
if offer_cfg.exists():
    oc = json.loads(offer_cfg.read_text())
    pid = lambda h: data.get(f'sf_p_{var(h)}')
    missing_pids = [h for h in [oc['product'], *oc['addons']] if not pid(h)]
    if missing_pids: sys.exit(f'sf-offer.json: no NEXT product mapped for {missing_pids} (set SF_CATALOG)')
    data.update({'sf_cart_empty_product': pid(oc['product']), 'sf_cart_review_product': pid(oc['product']),
                 'sf_cart_review_text': oc['review']['text'], 'sf_cart_review_name': oc['review']['name']})
    if oc.get('guarantee_text'): data['sf_cart_guarantee_text'] = oc['guarantee_text']
    for n, up in enumerate(oc.get('upgrades') or [oc['upgrade']]):
        key = 'sf_cart_upgrade' + (str(n + 1) if n else '')
        data.update({f'{key}_from': str(up['from']), f'{key}_to': str(up['to']), f'{key}_title': up['title'],
                     f'{key}_text': up['text'], f'{key}_button': up['button'], f'{key}_every': str(up.get('every') or '')})
    for n, h in enumerate(oc['addons'][:3], 1): data[f'sf_cart_upsell_{n}'] = pid(h)
    if oc.get('frontrow'): data['sf_frontrow_product_id'] = str(oc['frontrow'])
    for k, rp in zip(REFILL_SLOTS, oc.get('refill_products', [])):
        if not pid(rp['handle']): sys.exit(f"sf-offer.json: no NEXT product mapped for {rp['handle']} (set SF_CATALOG)")
        data.update({f'sf_refill_product_{k}': pid(rp['handle']), f'sf_refill_price_text_{k}': rp['price_text'],
                     f'sf_refill_compare_text_{k}': rp['compare_text'], f'sf_refill_every_{k}': str(rp['every'])})
    if oc.get('refill', {}).get('default'):
        data.update({'sf_refill_default_product': pid(oc['product']), 'sf_subscription_interval': oc['refill']['interval'],
                     'sf_subscription_interval_count': str(oc['refill']['every']),
                     'sf_refill_price_text': oc['refill'].get('price_text', ''), 'sf_refill_compare_text': oc['refill'].get('compare_text', '')})
# optional: a subscription-only product (Theme settings > Subscription Offer); the current persona sells one-time or
# with Automatic Refills, chosen on the product page, so it writes no sf-subscription.json
sub_cfg = EXPORT / 'sf-subscription.json'
if sub_cfg.exists():
    sc = json.loads(sub_cfg.read_text())
    pid = data.get(f"sf_p_{var(sc['handle'])}")
    if pid:
        data.update({'sf_subscription_product': pid, 'sf_subscription_interval': sc['interval'],
                     'sf_subscription_interval_count': str(sc['every']), 'sf_subscription_price_text': sc['text']})
    else:
        sys.exit(f"sf-subscription.json: no NEXT product mapped for {sc['handle']} (set SF_CATALOG)")
(OUT / 'configs' / 'settings_data.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

# ---------------------------------------------------------------- 9b. platform CSS gate (the store compiles CSS with Sass)
try:
    import sass
    for f in sorted((OUT / 'assets').rglob('*.css')):
        try: sass.compile(string=f.read_text('utf-8'))
        except Exception as e: LOG.setdefault('css_compile_errors', []).append(f'{f.relative_to(OUT)}: {str(e).splitlines()[0][:160]}')
except ImportError:
    LOG['css_compile_errors'] = ['libsass not installed (pip install libsass): CSS gate skipped']

# ---------------------------------------------------------------- 9c. DTL comment gate: {# #} must open and close on one line (else it renders as text)
for f in sorted(OUT.rglob('*.html')):
    for n, line in enumerate(f.read_text('utf-8', errors='replace').splitlines(), 1):
        if re.search(r'\{#(?![^\n]*#\})', line):
            LOG.setdefault('css_compile_errors', []).append(f'{f.relative_to(OUT)}:{n}: multi-line {{# #}} comment renders as text')
        if re.search(r'SF(?:SLOT\d+|DTL[0-9a-f]{10})X', line):   # a placeholder no Slots.render resolved
            LOG.setdefault('css_compile_errors', []).append(f'{f.relative_to(OUT)}:{n}: unresolved DTL placeholder')

# ---------------------------------------------------------------- 10. report
report = {'templates': sorted(LOG['templates']), 'unbound_prices': LOG['unbound_prices'],
          'missing_assets': sorted(LOG['missing_assets']), 'unmapped_links': sorted(LOG['unmapped_links']),
          'font_faces': len(FONT_FACES), 'css_url_vars': len(CSS_VARS), 'product_json': len(PRODUCT_JSON),
          'css_compile_errors': LOG.get('css_compile_errors', [])}
(OUT.parent / 'theme-build-report.json').write_text(json.dumps(report, indent=1))
print(f"templates {len(report['templates'])}  unbound prices {len(report['unbound_prices'])}  "
      f"missing assets {len(report['missing_assets'])}  unmapped links {len(report['unmapped_links'])}  "
      f"fonts {len(FONT_FACES)}  css vars {len(CSS_VARS)}  css compile errors {len(LOG.get('css_compile_errors', []))}")
for e in LOG.get('css_compile_errors', []): print('  CSS', e)
if LOG.get('css_compile_errors'): sys.exit('build gate failed: see the CSS lines above')
