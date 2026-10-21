"""Generate the SKINOFAB Next Commerce theme (Spark fork) from the static site export.

usage: python3 -I build_theme.py <export_dir> <spark_dir> <out_theme_dir> <handoff_dir>

The export (skinofab-site/) is the design source: every page's markup, CSS, JS, images, videos and icons.
Spark is the platform runtime: SEO, pixels, app hooks, GraphQL cart, side cart, preview indicator.
Commerce facts come from NEXT: product links, prices, variants and add-to-cart are bound with DTL.

Re-run after any design change; every template in the family is regenerated identically.
"""
import json, os, posixpath, re, shutil, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment

EXPORT, SPARK, OUT, HANDOFF = (Path(p).resolve() for p in sys.argv[1:5])
HERE = Path(__file__).resolve().parent
VARIANT2HANDLE = {}  # Shopify variant/product id in the design markup -> product handle
SHIPPING_PROTECTION = 'smooche-premium-shipping-protection'
LOG = {'unbound_prices': [], 'missing_assets': set(), 'templates': [], 'unmapped_links': set()}

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

class Slots:
    """Collects generated DTL behind inert placeholders so escaping never touches it."""
    def __init__(self): self.items = []
    def put(self, dtl): self.items.append(dtl); return f'SFSLOT{len(self.items) - 1}X'
    def render(self, text):
        return re.sub(r'SFSLOT(\d+)X', lambda m: self.items[int(m.group(1))], dtl_escape(text))

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

def sass_passthrough(css):
    """Emit CSS functions that share a name with Sass built-ins as interpolated strings (#{"min(...)"}), which
    Sass outputs verbatim instead of evaluating (it rejects var()/calc()/mixed units inside them)."""
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
        call = css[m.start():k + 1]
        q = '"' if '"' not in call else ("'" if "'" not in call else None)
        out.append(css[i:m.start()])
        out.append(f'#{{{q}{call}{q}}}' if q else call)
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

def transform(root, page, slots, current=None):
    """Bind design markup to NEXT: assets, links, prices, add-to-cart ids. `current`: PDP handle."""
    for t in root.find_all(string=lambda s: isinstance(s, Comment)): t.extract()
    # prices -> NEXT
    for el in list(root.find_all(True)):
        if el.find(True) or not PRICE_RE.match(el.get_text() or ''): continue
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

# ---------------------------------------------------------------- 5. page decomposition
HEAD_DROP = lambda el: (el.name == 'title' or (el.name == 'meta' and (el.get('charset') or el.get('name') in ('viewport', 'description')))
                        or (el.name == 'link' and 'icon' in (el.get('rel') or []))
                        or (el.name == 'script' and 'offline-shim' in (el.get('src') or '')))

def decompose(page):
    soup = BeautifulSoup((EXPORT / page).read_text('utf-8'), 'lxml')
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
    return {'soup': soup, 'head': head, 'lead': lead, 'has_header': bool(hdr_idx), 'has_footer': bool(ftr_idx),
            'main': main, 'tail': tail, 'title': title, 'body_id': body.get('id', ''),
            'body_class': ' '.join(body.get('class', []))}

def dtl_literal(value):
    """A design string emitted through DTL (a string literal), so it is data, not template text."""
    value = re.sub(r'\s+', ' ', value or '').strip().replace('\\', '').replace('"', "'")
    return '{%% firstof "%s" %%}' % value if value else ''

def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, 'utf-8')
    LOG['templates'].append(rel)

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
header_html = slots.render(frag_html(hdr_nodes, 'index.html', slots))
write('partials/header.html', "{# SKINOFAB header: design markup (announcement bar, navigation, mobile drawer). Cart opens the Spark side cart. #}\n" + header_html + '\n')
slots = Slots()
ftr_nodes = [k for k in hsoup.body.find_all(recursive=False) if 'shopify-section-group-group-footer' in ' '.join(k.get('class', []))]
write('partials/footer.html', "{# SKINOFAB footer: design markup. #}\n" + slots.render(frag_html(ftr_nodes, 'index.html', slots)) + '\n')

# ---------------------------------------------------------------- 7. page families
MAIN_OPEN = lambda m: str(m).split('>', 1)[0] + '>'

def simple(page, template):
    parts = decompose(page)
    write(template, page_template(page, parts, lambda s: main_html(parts, page, s)))

# 7a homepage
simple('index.html', 'templates/index.html')

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
                        title_dtl='{{ product.get_meta_title }} | {{ block.super }}', current=handle,
                        extra_tail='\n' + VARIANT_JSON + '\n{% app_hook "view_product" %}\n{% app_hook "add_to_cart" %}'))

# default product template: the flagship PDP layout, product section only, gallery from NEXT images
def default_product():
    f = 'products/color-changing-foundation.html'
    parts = decompose(f)
    def content(slots):
        main = parts['main']
        keep = main.select_one('[id$="__main"].shopify-section--product')
        for sec in [c for c in main.find_all(recursive=False) if c is not keep]: sec.decompose()
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
          page_template(f, parts, content, title_dtl='{{ product.get_meta_title }} | {{ block.super }}', current='color-changing-foundation',
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
        for a in ('srcset', 'data-srcset', 'sizes'): img.attrs.pop(a, None)
        img['src'] = slots.put('{{ sf_card_img%d.url }}' % i)
        img['alt'] = slots.put('{{ product.get_title }}')
    for s in card.select('.visually-hidden'): s.string = slots.put('{{ product.get_title }}')
    price = card.select_one('.product-grid-item__price')
    if price: price.clear(); price.append(slots.put("{% include 'partials/sf_price.html' with p=product %}"))
    card['id'] = slots.put('product-item-{{ product.pk }}')
    body = slots.render(str(card))
    CARD_PARTIAL = ("{# SKINOFAB product card (design markup) for NEXT products. Usage: include with product=product #}\n"
                    "{% with images=product.get_all_images %}"
                    "{% if images %}{% image_thumbnail images.0.original \"1080x1080\" crop=\"center\" as sf_card_img0 %}{% endif %}"
                    "{% if images.1 %}{% image_thumbnail images.1.original \"1080x1080\" crop=\"center\" as sf_card_img1 %}"
                    "{% elif images %}{% image_thumbnail images.0.original \"1080x1080\" crop=\"center\" as sf_card_img1 %}{% endif %}\n"
                    + body + "\n{% endwith %}\n")
    write('partials/sf_product_card.html', CARD_PARTIAL)

def catalogue(template, title_var):
    f = 'collections/all.html'
    parts = decompose(f)
    def content(slots):
        main = parts['main']
        cards = main.select('[data-product-block]')
        if cards:
            grid = cards[0].parent
            build_card(BeautifulSoup(str(cards[0]), 'lxml').find(attrs={'data-product-block': True}))
            for c in cards: c.decompose()
            grid.append(slots.put("{% for product in products %}{% include 'partials/sf_product_card.html' with product=product %}{% endfor %}"))
            grid.insert_after(NavigableString(slots.put("{% include 'partials/pagination.html' %}")))
        for h in main.find_all(['h1'])[:1]:
            h.string = slots.put(title_var)
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
    write('templates/blog/post.html', page_template(art, parts, post_content, title_dtl='{{ post.get_meta_title }} | {{ block.super }}'))
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
      "{% if p %}{% purchase_info_for_product request p as sf_s %}{% if sf_s.price.exists %}"
      "{% if retail %}{% if sf_s.price.price_retail > sf_s.price.price %}{% currency_symbol sf_s.price.currency %}{{ sf_s.price.price_retail|floatformat:'-2' }} {{ sf_s.price.currency }}{% endif %}"
      "{% elif quarter %}{% currency_symbol sf_s.price.currency %}{{ sf_s.price.price|dividedby:4|floatformat:'-2' }}"
      "{% else %}{% currency_symbol sf_s.price.currency %}{{ sf_s.price.price|floatformat:'-2' }} {{ sf_s.price.currency }}{% endif %}"
      "{% endif %}{% endif %}")

fonts = []
for block in FONT_FACES:
    fonts.append(re.sub(ASSET_RE, lambda m: asset_dtl(m.group(1), m.group(2)) or m.group(0),
                        re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', lambda m: 'url("%s")' % m.group(2), block)))
vars_css = ':root{' + ''.join('%s:url("%s");' % (k, asset_dtl(*v.split('/', 1)) or '') for k, v in sorted(CSS_VARS.items())) + '}'
write('partials/sf_asset_styles.html',
      "{# Fonts and stylesheet images. Theme CSS cannot hold relative url()s on NEXT (CSS and media are served from different hosts), so they resolve here via asset_url. #}\n"
      "<style>\n" + '\n'.join(dict.fromkeys(fonts)) + '\n' + vars_css + "\n</style>\n")

handle_pk = ','.join('"%s":"{%% firstof settings.sf_p_%s.children.first.pk settings.sf_p_%s.pk %%}"' % (h, var(h), var(h))
                     for h in sorted({m.group(1) for f in EXPORTED for m in [re.fullmatch(r'products/([a-z0-9][a-z0-9-]*)\.html', f)] if m}))
product_json = ','.join('"%s":"{{ \'sf/data/product-%s.json\'|asset_url|escapejs }}"' % (h, h) for h in sorted(PRODUCT_JSON))
base = (SPARK / 'layouts' / 'base.html').read_text()
base = base.replace('<link rel="stylesheet" type="text/css" href="{{ \'main.css\'|asset_url }}">',
                    "{% block spark_css %}{% endblock spark_css %}\n        {% include 'partials/sf_asset_styles.html' %}")
base = base.replace("{% endblock styles %}",
    "{% endblock styles %}\n    {# Spark side cart in the design's look: black controls, design body font. #}\n"
    "    <style>:root{--primary-color:#000000;--primary-color-darker:#000000;--primary-color-lighter:#333333;--accent-color:#000000;"
    "--font-body:var(--FONT-STACK-BODY, 'Jost', sans-serif);}</style>", 1)
base = base.replace("{% block extrahead %}{% endblock extrahead %}",
    "{% block extrahead %}{% endblock extrahead %}\n"
    "    {% url 'storefrontapi:graphql' as sf_graphql_url %}\n"
    "    <script>window.SFStore = { currency: \"{{ request.CURRENCY_CODE|default:'USD'|escapejs }}\", symbol: \"{% filter escapejs %}{% currency_symbol request.CURRENCY_CODE|default:'USD' %}{% endfilter %}\", graphqlUrl: \"{{ sf_graphql_url|default:'/api/graphql/'|escapejs }}\" };\n"
    "    window.SFProductJson = {" + product_json + "};\n"
    "    window.SFHandlePk = {" + handle_pk + "};\n"
    "    window.SFVariantHandle = " + json.dumps(VARIANT2HANDLE, sort_keys=True) + ";</script>\n"
    "    <script src=\"{{ 'js/skinofab-commerce.js'|asset_url }}\"></script>\n"
    "    {% block sf_head %}{% endblock sf_head %}")
base = base.replace('<a href="#main-content" class="skip-to-content">', '{% block sf_lead %}{% endblock sf_lead %}\n    <a href="#MainContent" class="skip-to-content visually-hidden">')
# Spark's own theme.js (Spark header/menu/search widgets) would collide with the design's window.theme; the design ships its own.
base = base.replace("<script type=\"text/javascript\" src=\"{{ 'js/theme.js'|asset_url }}\"></script>", "")
base = base.replace("{% block extrascripts %}{% endblock %}", "{% block sf_tail %}{% endblock sf_tail %}\n    {% block extrascripts %}{% endblock %}")
write('layouts/base.html', base)

# Spark-native templates keep Spark styling (Tailwind main.css) inside the SKINOFAB chrome
for t in ['templates/cart.html', 'templates/403.html', 'templates/404.html', 'templates/500.html',
          *[str(p.relative_to(OUT)) for p in (OUT / 'templates').rglob('*.html') if p.parts[-2] in ('reviews', 'support')]]:
    p = OUT / t
    if not p.exists(): continue
    s = p.read_text()
    if '{% block spark_css %}' not in s:
        s = s.replace("{% extends 'layouts/base.html' %}", "{% extends 'layouts/base.html' %}\n{% block spark_css %}<link rel=\"stylesheet\" type=\"text/css\" href=\"{{ 'main.css'|asset_url }}\">{% endblock spark_css %}", 1)
        s = s.replace('{% extends "layouts/base.html" %}', '{% extends "layouts/base.html" %}\n{% block spark_css %}<link rel="stylesheet" type="text/css" href="{{ \'main.css\'|asset_url }}">{% endblock spark_css %}', 1)
        p.write_text(s)

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
    'Collection Links': [{'name': f'sf_c_{var(c)}', 'type': 'url', 'label': c.replace('-', ' ').title(), 'default': '/catalogue/',
                          'help_text': f'Where the design\'s "{c}" collection links go (a NEXT category URL).'} for c in collections],
}, **schema}
(OUT / 'configs' / 'settings_schema.json').write_text(json.dumps(schema, indent=2, ensure_ascii=False) + '\n')
data = json.loads((OUT / 'configs' / 'settings_data.json').read_text())
for group in schema['SKINOFAB'].values():
    for field in group:
        data.setdefault(field['name'], field.get('default') if field['type'] != 'product' else None)
catalog = os.environ.get('SF_CATALOG')  # deploy mapping (tools/next-deploy) -> Product / Collection Links
if catalog and Path(catalog).exists():
    m = json.loads(Path(catalog).read_text())['mapping']
    for h, v in m.get('products', {}).items():
        if v.get('id'): data[f'sf_p_{var(h)}'] = v['id']
    for c, cid in m.get('categories', {}).items():
        if cid: data[f'sf_c_{var(c)}'] = f'/catalogue/category/{c}_{cid}/'
(OUT / 'configs' / 'settings_data.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

# ---------------------------------------------------------------- 9b. platform CSS gate (the store compiles CSS with Sass)
try:
    import sass
    for f in sorted((OUT / 'assets').rglob('*.css')):
        try: sass.compile(string=f.read_text('utf-8'))
        except Exception as e: LOG.setdefault('css_compile_errors', []).append(f'{f.relative_to(OUT)}: {str(e).splitlines()[0][:160]}')
except ImportError:
    LOG['css_compile_errors'] = ['libsass not installed (pip install libsass): CSS gate skipped']

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
