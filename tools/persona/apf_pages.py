"""Focus the export on the Adaptive Peptide Foundation: single-product homepage, 20-step product page, focused menus.

usage: python3 -I apf_pages.py <export_dir> <images.json>
Runs in place on the persona export (after apply_persona.py), before the theme build.

- every page: desktop + mobile menus and the footer "Shop" column point only at the foundation; the product
  name becomes "Adaptive Peptide Foundation" in visible text (URLs and handles stay)
- index.html: the multi-product homepage body is replaced by apf_copy.home_sections()
- products/color-changing-foundation.html: buy box copy (steps 1-5) cleaned up (no "1M+ purchased", no
  countdown, no unverified survey numbers), everything below it replaced by apf_copy.pdp_sections() (steps 6-20)
- images.json maps each {img:slot} to a source image (+ optional crop box and aspect); each is written to
  assets/img/apf-<slot>-<hash>.jpg (content-hashed: NEXT's CDN caches by file name)
"""
import hashlib, html, io, json, re, sys
from pathlib import Path
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apf_copy

EXP, IMAGES = Path(sys.argv[1]), json.load(open(sys.argv[2]))
IMG = EXP / 'assets' / 'img'
PDP = 'products/color-changing-foundation.html'
missing, removed = [], []

# ------------------------------------------------------------------------------------------ helpers
def enclosing(t, idx, open_re):
    """Start/end of the innermost element matching open_re (a <div ...> opener) that contains position idx."""
    for m in sorted(re.finditer(open_re, t[:idx]), key=lambda m: -m.start()):
        depth, pos = 0, m.start()
        for tag in re.finditer(r'<(/?)div\b[^>]*>', t[pos:]):
            depth += -1 if tag.group(1) else 1
            if depth == 0:
                end = pos + tag.end()
                if end > idx: return m.start(), end
                break
    return None

def balanced_end(t, start, tag):
    depth = 0
    for m in re.finditer(r'<(/?)%s\b[^>]*>' % tag, t[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0: return start + m.end()
    raise ValueError('unbalanced ' + tag)

def loose(text):
    out = []
    for ch in text:
        if ch.isspace(): out.append(r'\s+')
        elif ch in "'’": out.append(r"(?:'|’|&#39;|&#x27;|&rsquo;)")
        elif ch == '—': out.append(r'(?:—|&mdash;)')
        elif ch == '–': out.append(r'(?:–|&ndash;)')
        elif ch == '&': out.append(r'(?:&|&amp;)')
        else: out.append(re.escape(ch))
    return re.sub(r'(?:\\s\+)+', r'\\s+', ''.join(out))

def text_rule(t, old, new, where):
    if old.startswith('>') and old.endswith('<'):
        rx, rep = re.compile(r'>\s*' + loose(old[1:-1]) + r'\s*<'), '>' + html.escape(new[1:-1], quote=False) + '<'
    else:
        rx, rep = re.compile(loose(old)), html.escape(new, quote=False)
    t, n = rx.subn(lambda m: rep, t)
    if not n: missing.append((where, old[:70]))
    return t

def visible_rename(t):
    """Product name in text nodes only (never inside tags, so hrefs/handles/srcs are untouched)."""
    def fix(seg):
        seg = re.sub(r'\bColor[ -]Changing Foundation\b', 'Adaptive Peptide Foundation', seg)
        seg = re.sub(r'\bCOLOR[ -]CHANGING FOUNDATION\b', 'ADAPTIVE PEPTIDE FOUNDATION', seg)
        seg = re.sub(r'\bcolor changing foundation\b', 'Adaptive Peptide Foundation', seg)
        return seg
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)', t, flags=re.S | re.I)
    return ''.join(p if (p.startswith('<')) else fix(p) for p in parts)

# ------------------------------------------------------------------------------------------ images
def make_images():
    out = {}
    for slot, spec in IMAGES.items():
        src = Path(spec['src'])
        if not src.exists(): missing.append(('image', str(src))); continue
        im = Image.open(src).convert('RGB')
        if spec.get('crop'):
            x0, y0, x1, y1 = spec['crop']; W, H = im.size
            im = im.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
        if spec.get('aspect'):                      # centre-crop to a:b at the largest size that fits
            a, b = spec['aspect']
            size = (im.width, round(im.width * b / a)) if im.width * b / a <= im.height else (round(im.height * a / b), im.height)
            im = ImageOps.fit(im, size, Image.LANCZOS, centering=tuple(spec.get('center', (0.5, 0.5))))
        mw = spec.get('max', 1600)
        if im.width > mw: im = im.resize((mw, round(im.height * mw / im.width)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=86, optimize=True, progressive=True)
        name = f"apf-{slot}-{hashlib.md5(buf.getvalue()).hexdigest()[:6]}.jpg"
        (IMG / name).write_bytes(buf.getvalue()); out[slot] = (name, im.size)
    return out

def fill(t, imgs, prefix):
    def rep(m):
        slot = m.group(1)
        if slot not in imgs: missing.append(('slot', slot)); return ''
        return prefix + 'assets/img/' + imgs[slot][0]
    t = re.sub(r'\{img:([a-z0-9-]+)\}', rep, t)
    return t

# ------------------------------------------------------------------------------------------ navigation
NAV = [('The Foundation', PDP), ('How it works', PDP + '#apf-how'), ('Reviews', PDP + '#apf-reviews'),
       ('Guarantee', PDP + '#apf-guarantee'), ('About', 'pages/about-skinofab.html')]
FOOT = [('Adaptive Peptide Foundation', PDP), ('Monthly refill', PDP + '#apf-offer'), ('Base quiz', 'pages/ccf-quiz.html'),
        ('Love it or your money back', PDP + '#apf-guarantee'), ('My account', '/accounts/')]

def focus_nav(t, prefix, where):
    # desktop: the primary menu__items row
    m = re.search(r'<div class="menu__items"[^>]*>', t)
    if m:
        end = balanced_end(t, m.start(), 'div')
        items = ''.join(f'<div class="menu__item child" data-hover-disclosure-toggle="" data-nav-item=""> <a class="navlink navlink--toplevel caps" data-top-link="" href="{prefix}{h}"> <span class="navtext">{n}</span> </a></div>' for n, h in NAV)
        t = t[:m.start()] + m.group(0) + items + '</div>' + t[end:]
    else: missing.append((where, 'desktop menu'))
    # mobile drawer: replace the top-level items, keep account/login entries
    m = re.search(r'<ul class="mobile-nav[^"]*">', t)
    if m:
        end = balanced_end(t, m.start(), 'ul'); inner = t[m.end():end - 5]
        keep, pos = [], 0
        for li in re.finditer(r'<li\b', inner):
            if li.start() < pos: continue
            e = balanced_end(inner, li.start(), 'li'); seg = inner[li.start():e]; pos = e
            if re.search(r'(?i)account|log in', re.sub(r'<[^>]+>', ' ', seg)): keep.append(seg)
        items = ''.join(f'<li class="mobile-menu__item mobile-menu__item--level-1"> <a class="mobile-navlink mobile-navlink--level-1" data-nav-link-mobile="" href="{prefix}{h}">{n}</a></li>' for n, h in NAV)
        items += f'<li class="mobile-menu__item mobile-menu__item--level-1"> <a class="mobile-navlink mobile-navlink--level-1" data-nav-link-mobile="" href="{prefix}pages/contact.html">Contact</a></li>'
        t = t[:m.end()] + items + ''.join(keep) + '</ul>' + t[end:]
    else: missing.append((where, 'mobile menu'))
    # footer shop column
    m = re.search(r'<summary class="sf__menu-title">Shop</summary><ul>', t)
    if m:
        end = t.find('</ul>', m.end())
        t = t[:m.end()] + ' ' + ''.join(f'<li><a href="{prefix}{h}">{n}</a></li>' for n, h in FOOT) + ' ' + t[end:]
    return t

# ------------------------------------------------------------------------------------------ cart drawer
def focus_cart_drawer(t):
    """The drawer's upsells were other products (now hidden on NEXT): hide "complementary products", keep only the
    foundation among the empty-cart best sellers. Its price binds to NEXT, which shows the plan price."""
    t = t.replace('<complementary-products class="complementary-products" data-complementary-products="">',
                  '<complementary-products class="complementary-products" data-complementary-products="" hidden style="display:none">')
    m = re.search(r'<div class="cart-drawer__bestsellers"[^>]*>', t)
    if not m: return t
    end = balanced_end(t, m.start(), 'div'); box = t[m.start():end]
    pos, kept = 0, []
    for h in re.finditer(r'<div class="product-upsell__holder"', box):
        if h.start() < pos: continue
        e = balanced_end(box, h.start(), 'div'); card = box[h.start():e]; pos = e
        kept.append((h.start(), e, 'products/color-changing-foundation.html' in card))
    for s, e, keep in reversed(kept):
        if not keep:
            # the holder sits in its own complementary-products__item wrapper when there is one
            w = box.rfind('<div class="complementary-products__item">', 0, s)
            if w >= 0 and balanced_end(box, w, 'div') >= e and box[w:s].count('<div') == 1:
                e, s = balanced_end(box, w, 'div'), w
            box = box[:s] + box[e:]
    box = box.replace('<p class="complementary-products__title">Our best sellers', '<p class="complementary-products__title">Start your monthly refill', 1)
    return t[:m.start()] + box + t[end:]

# ------------------------------------------------------------------------------------------ product gallery
# The PDP gallery shows the product sheet's bottle (and 45+ women without any product), never the old packaging.
GALLERY = [('g-front', 'front'), ('g-threequarter', 'three-quarter view'), ('g-bases', 'Light–Medium and Medium–Deep'),
           ('g-pump', 'airless pump'), ('g-done', 'even, fresh skin after 45'), ('g-left', 'side view'), ('g-promise', 'women 45+')]
OLD_PACKSHOT = re.compile(r'((?:\.\.\\?/)*)assets(\\?/)img\\?/KoreanColorChangingFoundation-Productimages_1_[^"\'\s,)?&\\]+')   # plain and JSON-escaped paths

def rebuild_gallery(t, imgs):
    """Slides and thumbnails regenerated from the first slide / thumbnail of the design (same markup, new images)."""
    out = t
    for box_re, item_re in ((r'<div class="product-single__media-slider" data-product-single-media-slider="">', r'<div class="product-single__media-slide[" ]'),
                            (r'<div class="product-single__thumbnails" data-product-single-media-thumbs="" id="ProductThumbs">', r'<div class="product-single__thumbnail"')):
        m = re.search(box_re, out)
        if not m: missing.append(('pdp gallery', box_re[:40])); return t
        end = balanced_end(out, m.start(), 'div'); inner = out[m.end():end - len('</div>')]
        items, pos = [], 0
        for it in re.finditer(item_re, inner):
            if it.start() < pos: continue
            e = balanced_end(inner, it.start(), 'div'); items.append(inner[it.start():e]); pos = e
        rest = inner
        for it in items: rest = rest.replace(it, '', 1)
        if not items or rest.strip():
            missing.append(('pdp gallery', 'unexpected markup in ' + box_re[:40])); return t
        proto = items[0]; old_id = re.search(r'data-id="(\d+)"', proto).group(1)
        new = []
        for i, (slot, label) in enumerate(GALLERY):
            s = proto.replace(old_id, old_id if i == 0 else str(9100000000000 + i))   # first keeps the variant's featured media id
            if i:
                s = s.replace('class="product-single__media-slide"', 'class="product-single__media-slide media--hidden"', 1)
                s = s.replace('fetchpriority="high" ', '').replace('loading="eager"', 'loading="lazy"')
            src = '../assets/img/' + imgs[slot][0]
            s = re.sub(r'\bsrc="[^"]*"', f'src="{src}"', s); s = re.sub(r'\bsrcset="[^"]*"', f'srcset="{src} {imgs[slot][1][0]}w"', s)
            s = re.sub(r'(alt|aria-label)="[^"]*"', lambda a: f'{a.group(1)}="{html.escape(apf_copy.PRODUCT + ", " + label)}"', s)
            new.append(s)
        out = out[:m.end()] + ''.join(new) + out[end - len('</div>'):]
    return out

# ------------------------------------------------------------------------------------------ pages
def homepage(t, imgs):
    s = t.find('<section class="shopify-section fh-section" id="shopify-section-template--22228899201180__hero">')
    e = t.find('</main>', s)
    if s < 0 or e < 0: missing.append(('index', 'template sections')); return t
    body = apf_copy.home_sections(PDP)
    return t[:s] + '<section class="shopify-section" id="shopify-section-apf-home">' + fill(body, imgs, '') + '</section>' + t[e:]

def product_page(t, imgs):
    for old, new in apf_copy.BUYBOX: t = text_rule(t, old, new, 'pdp buy box')
    t = rebuild_gallery(t, imgs)
    # the price under the title is the plan price (rendered by the theme); the design script must not rewrite it
    # from the variant data (the $39 list price), so its hooks come off
    m = re.search(r'<div class="product__block product__price-and-badge"[^>]*>', t)
    if m:
        end = balanced_end(t, m.start(), 'div')
        block = t[m.start():end].replace(' data-product-price=""', '').replace(' data-compare-price=""', '')
        block = re.sub(r'<s class="product__price--compare">.*?</s>', '', block, flags=re.S)   # a plan has no compare-at price
        t = t[:m.start()] + block + t[end:]
    else: missing.append(('pdp', 'price block'))
    # the design script resets the button label from theme.strings on load
    t, n = re.subn(r'add_to_cart: "Add to Cart"', 'add_to_cart: "Start my monthly refill"', t)
    if n != 1: missing.append(('pdp', 'theme.strings.add_to_cart'))
    # "or 4 interest-free payments of ..." does not apply to a monthly plan
    t, n = re.subn(r'<skinofab-installments\b.*?</skinofab-installments>\s*(?:<script[^>]*skinofab-installments[^>]*></script>)?', '', t, flags=re.S)
    if not n: missing.append(('pdp', 'installments'))
    # attributes can come before class, so match class anywhere in the opener
    for marker, opener in (('Selling out fast', r'<div\b[^>]*\bclass="product__block"[^>]*>'),
                           ('12-week customer survey', r'<div\b[^>]*\bclass="product__block customer-survey-results"[^>]*>')):
        i = t.find(marker)
        box = enclosing(t, i, opener) if i >= 0 else None
        if box and box[1] - box[0] < 40000: t = t[:box[0]] + t[box[1]:]; removed.append((marker, box[1] - box[0]))
        else: missing.append(('pdp', marker))
    s = t.find('id="shopify-section-template--20029865361564__section_text_rLDa4j"')
    s = t.rfind('<div', 0, s)
    e = t.find('</main>', s)
    if s < 0 or e < 0: missing.append(('pdp', 'below-the-fold sections')); return t
    return t[:s] + '<section class="shopify-section" id="shopify-section-apf-pdp">' + fill(apf_copy.pdp_sections(), imgs, '../') + '</section>' + t[e:]

def main():
    imgs = make_images()
    pages = sorted(EXP.rglob('*.html'))
    for p in pages:
        rel = p.relative_to(EXP).as_posix()
        t = p.read_text(encoding='utf-8', errors='surrogateescape')
        prefix = '../' * rel.count('/')
        t = focus_nav(t, prefix, rel)
        if rel == 'index.html': t = homepage(t, imgs)
        if rel == PDP: t = product_page(t, imgs)
        t = focus_cart_drawer(t)
        if 'g-front' in imgs: t = OLD_PACKSHOT.sub(lambda m: m.group(1) + 'assets' + m.group(2) + 'img' + m.group(2) + imgs['g-front'][0], t)
        t = re.sub(r'alt="KoreanColorChangingFoundation-Productimages_1_[^"]*"', f'alt="{apf_copy.PRODUCT}"', t)
        t = visible_rename(t)
        p.write_text(t, encoding='utf-8', errors='surrogateescape')
    nav_missing = [m for m in missing if m[1] in ('desktop menu', 'mobile menu')]
    real = [m for m in missing if m not in nav_missing]
    print(json.dumps({'pages': len(pages), 'images': {k: v[0] for k, v in imgs.items()},
                      'pages_without_menus': len(nav_missing), 'pdp_removed': removed, 'missing': real}, indent=1))
    if real: sys.exit(1)

main()
