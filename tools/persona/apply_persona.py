"""Apply the 45+ persona layer to a (rebranded) export: copy rules, the offer picker and persona images.

usage: python3 -I apply_persona.py <src_export> <dst_export> <ccf-offers.json> [<images_dir>]

- copies src -> dst (binary files hard-linked, text files rewritten)
- applies tools/persona/ccf_copy.py: PAGE rules on their file, then GLOBAL rules on every HTML page; a rule that
  matches nothing fails the run (rules prefixed RE: are raw regexes)
- inserts the offer picker (1 bottle / 2 bottles + free gifts, and the Automatic Refills box) into the foundation's
  product form, and the "love it or your money back" trust row under its button; packs map to the NEXT variant
  pks in ccf-offers.json (written by setup_ccf_offers.py)
- writes sf-offer.json for the theme build's Cart Drawer settings: the 1 -> 2 bottle upgrade, add-ons and review
- builds products/the-lymphatic-brush.html (and its .js snapshot) from the foundation page's markup with the brush's
  page in it (brush_copy.py): gallery, bundle picker (pks in <work_dir>/brush-offers.json, setup_brush_offers.py),
  tabs and the sections below; images from brand/lymphatic-brush/, videos from <work_dir>/brush/media/
  (brush_assets.py)
- <images_dir>/<target file name> replaces that export image (persona images made by tools/persona/images.py)
  under a new content-hashed name, with every reference rewritten (NEXT's CDN caches by file name)
"""
import hashlib, html, json, os, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apf_copy, brush_copy, ccf_copy

SRC, DST, OFFERS = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), json.load(open(sys.argv[3]))
IMAGES = Path(sys.argv[4]).resolve() if len(sys.argv) > 4 else None
TEXT = {'.html', '.css', '.js', '.json', '.md', '.txt', '.xml', '.svg'}

def loose(text):
    out = []
    for ch in text:
        if ch.isspace(): out.append(r'\s+')
        elif ch in "'’": out.append(r"(?:'|’|&#39;|&#x27;|&rsquo;)")
        elif ch == '—': out.append(r'(?:—|&mdash;|&#8212;)')
        elif ch == '–': out.append(r'(?:–|&ndash;|&#8211;)')
        elif ch == '&': out.append(r'(?:&|&amp;)')
        else: out.append(re.escape(ch))
    return re.sub(r'(?:\\s\+)+', r'\\s+', ''.join(out))

def compile_rule(old, new):
    if old.startswith('RE:'):                     # raw regex rule: pattern and replacement used as written
        return re.compile(old[3:]), new
    if old.startswith('>') and old.endswith('<'):
        return re.compile(r'>\s*' + loose(old[1:-1]) + r'\s*<'), '>' + html.escape(new[1:-1], quote=False) + '<'
    return re.compile(loose(old)), html.escape(new, quote=False)

def money(v):
    f = float(v)
    return '$%d' % f if f == int(f) else '$%.2f' % f

GIFT_ICONS = Path(__file__).resolve().parent / 'assets'

def gift_icons():
    """Gift thumbnails, copied into the export under content-hashed names (NEXT's CDN caches by file name)."""
    out = {}
    for key in ('blender', 'mystery', 'shipping'):
        src = GIFT_ICONS / f'offer-gift-{key}.jpg'
        name = f"offer-gift-{key}-{hashlib.md5(src.read_bytes()).hexdigest()[:6]}.jpg"
        shutil.copy2(src, DST / 'assets' / 'img' / name)
        out[key] = '../assets/img/' + name
    return out

BRAND = Path(__file__).resolve().parents[2] / 'brand'

def section_image(src, name, size=(1000, 1250)):
    """A 4:5 crop of a brand image for the problem / solution sections, under a content-hashed name."""
    from PIL import Image, ImageOps
    im = ImageOps.fit(Image.open(src).convert('RGB'), size, Image.LANCZOS, centering=(0.5, 0.42))
    tmp = DST / 'assets' / 'img' / f'{name}.jpg'
    im.save(tmp, quality=85, optimize=True, progressive=True)
    final = tmp.with_name(f"{name}-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.jpg")
    tmp.rename(final)
    return '../assets/img/' + final.name, size[0], size[1]

def problem_solution():
    return apf_copy.problem_solution_html(
        section_image(BRAND / 'persona' / 'age-73.jpg', 'skinofab-problem-skin-after-45'),
        section_image(BRAND / 'adaptive-peptide-foundation' / '03-three-quarter-right.png', 'skinofab-solution-bottle'))

def crop_to(src_path, name, size, centering):
    """A crop of an export image at `size`, under a content-hashed name (NEXT's CDN caches by file name)."""
    from PIL import Image, ImageOps
    im = ImageOps.fit(Image.open(src_path).convert('RGB'), size, Image.LANCZOS, centering=centering)
    tmp = DST / 'assets' / 'img' / f'{name}.jpg'
    im.save(tmp, quality=86, optimize=True, progressive=True)
    final = tmp.with_name(f"{name}-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.jpg")
    tmp.rename(final)
    return '../assets/img/' + final.name, size[0], size[1]

def subject_center_x(path):
    """Horizontal center of the person in a studio photo (columns that differ from the backdrop)."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert('L')).astype(int)
    bg = int(np.median(a[:, :20]))
    cols = (np.abs(a - bg) > 28).sum(0)
    xs = np.where(cols > a.shape[0] * 0.08)[0]
    return (xs.min() + xs.max()) / 2 / a.shape[1] if len(xs) else 0.5

def home_section(home, key):
    m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+__%s"' % key, home)
    if not m: return None
    return home[m.start():home.find('</section>', m.start())]

def dermatologist(home):
    """The homepage dermatologist (her photo, words, name and role) as a product page section."""
    sec = home_section(home, 'experts')
    if not sec: return None
    copy = re.search(r'<div class="fh-expert-copy">(.*?)</div>', sec, re.S).group(1)
    name = re.search(r'<h3>(.*?)</h3>', copy).group(1)
    role = re.search(r'<p class="fh-expert-role">(.*?)</p>', copy).group(1)
    paras = [p for p in re.findall(r'<p>(.*?)</p>', copy, re.S)]
    photo = re.search(r'class="fh-expert-photo"><img[^>]*src="assets/img/([^"]+)"', sec).group(1)
    avatar = re.search(r'role="tab"[^>]*>\s*<picture[^>]*><img[^>]*src="assets/img/([^"]+)"', sec).group(1)
    path = DST / 'assets' / 'img' / photo
    from PIL import Image
    w, h = Image.open(path).size
    pw = int(h * 0.8)
    ph = crop_to(path, 'skinofab-dermatologist-portrait', (pw, h), (min(max(subject_center_x(path), 0), 1), 0.5))
    lead, mark = 'Trusted by leading', 'dermatologists'
    hit = re.search(r'what I recommend most (to [^.]+\.)', ' '.join(paras))
    if hit: lead, mark = '&hellip;what I recommend most', hit.group(1)
    return apf_copy.dermatologist_html({'name': name, 'role': role.replace(' SkinClinic', ', SkinClinic'), 'paragraphs': paras,
                                        'photo': ph, 'avatar': '../assets/img/' + avatar,
                                        'headline_lead': lead, 'headline_mark': mark})

def video_reviews(home):
    """The homepage customer reviews (poster photos, words, names) as a product page section."""
    sec = home_section(home, 'reviews')
    if not sec: return None
    eyebrow = re.search(r'class="fh-eyebrow">.*?<span>(.*?)</span>', sec, re.S).group(1)
    title = re.search(r'<h2>(.*?)</h2>', sec, re.S).group(1)
    out = []
    for a in re.findall(r'<article class="fh-review">(.*?)</article>', sec, re.S):
        name = re.search(r'fh-review-name"><span>(.*?)</span>', a).group(1)
        if name in ccf_copy.PDP_REVIEW_SKIP: continue
        poster = re.search(r'<img[^>]*class="fh-social-poster"[^>]*src="assets/img/([^"]+)"|<img[^>]*src="assets/img/([^"]+)"[^>]*class="fh-social-poster"', a)
        poster = poster.group(1) or poster.group(2)
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        out.append({'title': re.search(r'<h3>(.*?)</h3>', a).group(1), 'text': re.search(r'</h3><p>(.*?)</p>', a, re.S).group(1),
                    'name': name, 'photo': crop_to(DST / 'assets' / 'img' / poster, f'skinofab-review-{slug}', (720, 900), (0.5, 0.32))})
    return apf_copy.pdp_reviews_html(eyebrow, title, out) if out else None

def faq_more(t):
    """The product page FAQ (two columns): the skin questions after "How to apply?", then Automatic Refills, buying
    once and SPF where the second column starts. Items are clones of the design's own (same markup, same
    collapsible behaviour)."""
    m = re.search(r'<div class="shopify-section" id="shopify-section-template--[0-9]+__section_accordions_[^"]+">', t)
    if not m: return t, False
    end = balanced_end(t, m.start(), 'div')
    sec = t[m.start():end]
    items = re.findall(r'<li aria-haspopup="true" class="accordion__item accordion__item--padded"[^>]*>.*?</li>', sec, re.S)
    if not items: return t, False
    tpl = items[0]
    def item(k, q, a):
        li = re.sub(r'id="Accordion--[^"]+"', f'id="Accordion--sf_{k}"', tpl, count=1)
        li = re.sub(r'Accordions-item--\d+-', f'Accordions-item--sf{k}-', li)
        li = re.sub(r'(<span class="accordion__item__title__text">).*?(</span>)', lambda mm: mm.group(1) + html.escape(q) + mm.group(2), li, count=1, flags=re.S)
        return re.sub(r'(<div class="accordion__item__text rte" data-collapsible-content="">).*?(</div>)',
                      lambda mm: mm.group(1) + '<p>' + html.escape(a) + '</p>' + mm.group(2), li, count=1, flags=re.S)
    skin = ''.join(item(k, q, a) for k, (q, a) in enumerate(ccf_copy.PDP_FAQ_SKIN))
    orders = ''.join(item(10 + k, q, a) for k, (q, a) in enumerate(ccf_copy.pdp_faq_orders()))
    # one list, shown in two columns by the theme's CSS: the skin questions after the first item, the order questions
    # where the second column starts (the money-back question), so both columns stay balanced
    lis = [mm.start() for mm in re.finditer(r'<li aria-haspopup="true" class="accordion__item', sec)]
    if len(lis) < 2: return t, False
    second_col = next((i for i in lis if 'money back' in sec[i:sec.find('</li>', i)].lower()), lis[len(lis) // 2])
    first_end = sec.find('</li>', lis[0]) + len('</li>')
    sec = sec[:second_col] + orders + sec[second_col:]
    sec = sec[:first_end] + skin + sec[first_end:]
    return t[:m.start()] + sec + t[end:], True

REVIEWS = Path(sys.argv[3]).resolve().parent / 'reviews'   # tools/reviews/import_reviews.py output (work dir)

SHIP = 1000   # reviews in the wall's data file; the totals cover every imported review

def review_data(reviews=REVIEWS):
    """The imported reviews in <reviews>/reviews.json (tools/reviews/import_reviews.py), or None: the list the wall
    ships (every photo review, every review under 4 stars, then the rest in the importer's order, up to SHIP), the
    totals of all of them, and short 5-star picks for the strip near the top of the page."""
    data = reviews / 'reviews.json'
    if not data.exists(): return None
    d = json.loads(data.read_text())
    rs = d['reviews']
    keep = set(i for i, r in enumerate(rs) if r.get('photos') or r['rating'] <= 3)
    for i in range(len(rs)):
        if len(keep) >= SHIP: break
        keep.add(i)
    ship = [rs[i] for i in sorted(keep)][:max(SHIP, len(keep))]
    picks = [r for r in rs if r['rating'] == 5 and r.get('verified') and 70 <= len(r['body']) <= 210 and '\n' not in r['body']][:10]
    return {'ship': ship, 'summary': {'count': d['count'], 'average': d['average'], 'distribution': d['distribution']},
            'picks': [{'name': r['name'], 'body': r['body']} for r in picks]}

def review_wall(reviews=REVIEWS):
    """The review wall after the FAQ: NEXT's own reviews (the theme fills them in) plus the imported ones in
    <reviews>/reviews.json, if any (the foundation: <work_dir>/reviews, the brush: <work_dir>/reviews-brush)."""
    d = review_data(reviews)
    if not d: return apf_copy.review_wall_html()
    photos = {}
    for r in d['ship']:
        for p in r.get('photos', []):
            src = reviews / 'photos' / p
            if not src.exists(): continue
            name = f"review-{src.stem}-{hashlib.md5(src.read_bytes()).hexdigest()[:6]}.jpg"
            from PIL import Image, ImageOps
            im = ImageOps.exif_transpose(Image.open(src)).convert('RGB'); im.thumbnail((1200, 1200))
            im.save(DST / 'assets' / 'img' / name, quality=84, optimize=True, progressive=True)
            photos[p] = '../assets/img/' + name
    # a data script (theme JS assets run through the template engine: ASCII only, no template openers)
    slim = [{k: r[k] for k in ('name', 'rating', 'title', 'body', 'date', 'verified', 'photos') if r.get(k)} for r in d['ship']]
    payload = json.dumps({'summary': d['summary'], 'reviews': slim}, ensure_ascii=True, separators=(',', ':'))
    payload = payload.replace('{%', '{\\u0025').replace('{{', '{\\u007b').replace('{#', '{\\u0023')
    body = 'window.SFReviewsData=' + payload + ';\n'
    name = f"sf-reviews-{hashlib.md5(body.encode()).hexdigest()[:8]}.js"
    (DST / 'assets' / 'js').mkdir(parents=True, exist_ok=True)
    (DST / 'assets' / 'js' / name).write_text(body)
    return apf_copy.review_wall_html('../assets/js/' + name, photos)

def review_strip(reviews=REVIEWS):
    """The short-review strip for the top of the product page (None without imported reviews)."""
    d = review_data(reviews)
    if not d or not d['picks']: return None
    s = d['summary']
    return apf_copy.review_strip_html(float(s['average']), int(s['count']), d['picks'])

def picker():
    """The offer, as on the old store: 1 bottle or 2 bottles + free gifts, each a "temporary deal" off the compare-at
    price, and an Automatic Refills box that drops both to their refill price. ccf_copy.REFILL decides whether the
    box starts ticked ('default') and whether it is shown ('show_box'); hidden and ticked, the product page sells
    refills only, and the refill terms under the button say so.

    Prices come from ccf_copy.PACKS, the same table setup_ccf_offers.py writes to NEXT. The box is
    data-sf-offer-picker, so the theme build keeps these prices as written instead of binding them to the product."""
    packs, refill, icons = ccf_copy.PACKS, ccf_copy.REFILL, gift_icons()
    variants = OFFERS['foundation']['variants']
    table = {p['key']: {'pk': variants[p['key']], 'price': float(p['price']), 'refill': float(p['refill']),
                        'compare': float(p['compare'])} for p in packs}
    first = packs[0]
    pct = round((float(first['compare']) - float(first['refill'])) / float(first['compare']) * 100)
    on = bool(refill.get('default'))
    cards = []
    for i, p in enumerate(packs):
        gifts = ''.join(
            f'<li><img src="{icons[k]}" alt="" width="40" height="40" loading="lazy" decoding="async">'
            f'<span>+ {html.escape(label)}</span>' + (f'<s>{money(value)}</s>' if value else '') + '<b>FREE</b></li>'
            for k, label, value in p['gifts'])
        cards.append(
            f'<label class="sfo-card{" sfo-card--gifts" if gifts else ""}">'
            + (f'<em class="sfo-tab">{html.escape(p["badge"])}</em>' if p.get('badge') else '')
            + f'<span class="sfo-row"><input type="radio" name="sf_pack" value="{p["key"]}"{" checked" if i == 0 else ""}>'
            f'<span class="sfo-main"><span class="sfo-name">{html.escape(p["name"])}'
            f'<span class="sfo-save" data-sfo-save>SAVE {money(float(p["compare"]) - float(p["refill" if on else "price"]))}</span></span>'
            f'<small>{html.escape(p["note"])}</small></span>'
            f'<span class="sfo-price"><b data-sfo-now>{money(p["refill" if on else "price"])}</b><s>{money(p["compare"])}</s></span></span>'
            + (f'<ul class="sfo-gifts">{gifts}</ul>' if gifts else '') + '</label>')
    perks = ' <i>|</i> '.join(html.escape(x) for x in refill['perks'])
    box = (f'<input type="checkbox" name="sf_purchase" value="subscribe" data-interval="{refill["interval"]}" '
           f'data-interval-count="{refill["every"]}"{" checked" if on else ""}')
    if refill.get('show_box', True):
        box = (f'<label class="sfo-refill">{box}>\n<span><strong>Save <span data-sfo-pct>{pct}%</span> with '
               f'{html.escape(refill["name"])}</strong><small>{perks}</small></span></label>')
    else:
        # inline !important: the design's stylesheets give inputs display:block, which beats the hidden attribute
        box += ' hidden style="display:none !important" aria-hidden="true" tabindex="-1">'
    return f"""<div class="sfo" id="apf-buy" data-sf-offer-picker data-packs='{json.dumps(table)}'>
<style>{apf_copy.OFFER_PICKER_CSS}</style>
<fieldset><legend>Choose your pack</legend>{''.join(cards)}</fieldset>
{box}
<script>
(function () {{
  var root = document.currentScript.parentNode;
  var form = root.closest('form');
  var packs = JSON.parse(root.getAttribute('data-packs'));
  var box = root.querySelector('input[name=sf_purchase]');
  function money(v) {{ return '$' + (v % 1 ? v.toFixed(2) : String(v)); }}
  // the price under the product title (the nearest one above the picker)
  var scope = root, head = null;
  while (scope && !head) {{ scope = scope.parentElement; head = scope && scope.querySelector('.product__price-and-badge'); }}
  var now = head && head.querySelector('.product__price--regular');
  var was = head && head.querySelector('.product__price--compare');
  var unit = now && / USD\\s*$/.test(now.textContent) ? ' USD' : '';
  function sync() {{
    var key = (root.querySelector('input[name=sf_pack]:checked') || {{}}).value || '1';
    var sub = box.checked, pick = packs[key];
    var id = form && form.querySelector('input[name=id]');
    if (id) id.value = pick.pk;
    Array.prototype.forEach.call(root.querySelectorAll('input[name=sf_pack]'), function (r) {{
      var p = packs[r.value], card = r.closest('.sfo-card'), v = sub ? p.refill : p.price;
      card.querySelector('[data-sfo-now]').textContent = money(v);
      card.querySelector('[data-sfo-save]').textContent = 'SAVE ' + money(p.compare - v);
    }});
    var pct = root.querySelector('[data-sfo-pct]');
    if (pct) pct.textContent = Math.round((pick.compare - pick.refill) / pick.compare * 100) + '%';
    if (now) now.textContent = money(sub ? pick.refill : pick.price) + unit;
    if (was) was.textContent = money(pick.compare) + unit;
    // the trust row under the button (parsed after this script): refill facts while refills are on
    Array.prototype.forEach.call(document.querySelectorAll('[data-sf-trust-row]'), function (r) {{
      r.hidden = (r.getAttribute('data-sf-trust-row') === 'refill') !== sub;
    }});
    Array.prototype.forEach.call(document.querySelectorAll('[data-sf-renew]'), function (e) {{ e.textContent = money(pick.refill); }});
    var terms = document.querySelector('[data-sf-refill-terms]');
    if (terms) {{
      terms.hidden = !sub;
      terms.textContent = terms.getAttribute('data-sf-refill-terms').replace(/\\{{amount\\}}/g, money(pick.refill));
    }}
  }}
  root.addEventListener('change', sync);
  // deep links from the page sections (#apf-buy) scroll here
  function fromHash() {{
    if (!/^#apf-buy(?:-[a-z]+)?$/.test(window.location.hash || '')) return;
    root.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}
  window.addEventListener('hashchange', fromHash);
  document.addEventListener('click', function (e) {{
    var a = e.target.closest && e.target.closest('a[href*="#apf-buy"]');
    if (!a || a.pathname.replace(/\\/$/, '') !== window.location.pathname.replace(/\\/$/, '')) return;
    e.preventDefault(); history.replaceState(null, '', a.hash); fromHash();
  }});
  fromHash();
  sync();
  // the trust block (with the refill terms) comes after the button: sync again once it is parsed
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', sync);
}})();
</script>
</div>"""

def cart_offer():
    """The cart drawer's settings for this offer (read by the theme build into Theme settings > Cart Drawer): the
    1 -> 2 bottle upgrade with its price difference, the add-ons and the review."""
    one, two = ccf_copy.PACKS[0], ccf_copy.PACKS[1]
    variants = OFFERS['foundation']['variants']
    diffs = {float(two['price']) - float(one['price']), float(two['refill']) - float(one['refill'])}
    extras = ['a second bottle'] + ['a free ' + label.replace('FREE ', '') for k, label, value in two['gifts'] if value]
    what = ', '.join(extras[:-1]) + ' and ' + extras[-1]
    text = (f'Just {money(diffs.pop())} more for {what}.' if len(diffs) == 1 else f'Get {what}.')
    cart = ccf_copy.CART
    brush = json.loads((WORK / 'brush-offers.json').read_text())['variants']
    b1, b2 = brush_copy.BUNDLES[0], brush_copy.BUNDLES[1]
    b_text = (f"Just {money(round(float(b2['price']) - float(b1['price']), 2))} more for a second brush and a second free case.")
    return {'product': cart['product'], 'addons': cart['addons'],
            'upgrades': [{'from': variants[one['key']], 'to': variants[two['key']], 'title': cart['upgrade_title'],
                          'text': text, 'button': cart['upgrade_button']},
                         {'from': brush[b1['key']], 'to': brush[b2['key']], 'title': brush_copy.CART_UPGRADE['title'],
                          'text': b_text, 'button': brush_copy.CART_UPGRADE['button']}],
            'review': {'text': cart['review_text'], 'name': cart['review_name']},
            # refills on by default: every add of the foundation that names no purchase type is the refill plan
            'refill': {'default': bool(ccf_copy.REFILL.get('default')), 'interval': ccf_copy.REFILL['interval'],
                       'every': ccf_copy.REFILL['every']},
            'frontrow': getattr(ccf_copy, 'FRONTROW_PRODUCT_ID', None)}

STAR = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>')

def rating_block(t, real=None):
    """The design's Loox rating badge renders nothing without Loox (a Shopify app): the same stars, color and text
    from its own data attributes, as plain markup, linking to the reviews section. real: the imported reviews' totals
    ({'average', 'count'}), which replace the badge's own text (the design's pattern carried an inflated count)."""
    m = re.search(r'<div class="loox-rating loox-widget"[^>]*></div>', t)
    if not m: return t, False
    tag = m.group(0)
    attr = lambda k, d='': (re.search(r'\b%s="([^"]*)"' % k, tag) or [None, d])[1]
    rating = float(attr('data-rating', '5') or 5)
    text = attr('data-pattern') or f'{rating}/5'
    if real:
        rating = round(float(real['average']), 1)
        text = f"{rating:g}/5 ({int(real['count']):,} reviews)"
    color = attr('data-color-star') or '#000000'
    stars = ''
    for i in range(5):
        fill = max(0.0, min(1.0, round((rating - i) * 2) / 2))   # half stars, as Loox draws them
        stars += (f'<span class="sf-star" style="--f:{int(fill * 100)}%">{STAR}{STAR}</span>')
    block = (f'<span class="sf-rating" style="--sf-star:{html.escape(color)}">'
             f'<span class="sf-rating__stars" role="img" aria-label="Rated {rating:g} out of 5">{stars}</span>'
             f'<span class="sf-rating__text">{html.escape(text)}</span></span>'
             '<style>.sf-rating{display:inline-flex;align-items:center;gap:10px;color:#151515;font-size:17px;line-height:1}'
             '.sf-rating__stars{display:inline-flex;gap:2px}'
             '.sf-star{position:relative;display:inline-block;width:20px;height:20px;color:#d8d8d8}'
             '.sf-star svg{position:absolute;left:0;top:0}'
             '.sf-star svg+svg{color:var(--sf-star);clip-path:inset(0 calc(100% - var(--f)) 0 0)}</style>')
    t = t.replace(tag, block, 1)
    # the badge scrolls to the reviews
    t = re.sub(r'<a aria-label="Scroll to reviews">', '<a aria-label="Scroll to reviews" href="#sf-reviews" style="text-decoration:none">', t, count=1)
    t = t.replace('<section class="skinofab-testimonials">', '<section class="skinofab-testimonials" id="sf-reviews">', 1)
    return t, True

FRONTROW_CSS = (
    # the sticker sits on the gallery's top-left corner, over the first slide (as on the original store)
    '#frontrow-sticker{position:absolute;z-index:3;border-radius:0 !important;max-width:unset !important;left:0 !important;top:0 !important}'
    '@media only screen and (max-width:480px){#frontrow-sticker{transform:scale(.7) !important;transform-origin:0 0 !important}}'
    # narrow phones: a little smaller, so it clears the flag badge in the first photo
    '@media only screen and (max-width:400px){#frontrow-sticker{transform:scale(.66) !important}}'
    # FrontrowMD's own script appends its modals to <body> and shows them on click (their documents draw the backdrop)
    '.iframe-modal-frontrow{display:none;position:fixed;z-index:99999999;inset:0;width:100%;height:100%;overflow:hidden}'
    '.iframe.frontrow{display:none;position:fixed;left:0;top:0;z-index:99999997;right:0;bottom:0;width:100%;height:100%;overflow:hidden}')

def frontrow_block():
    """FrontrowMD's "Clinicians' Choice" sticker on the product gallery, top-left, while the first slide shows; a
    click opens its clinicians and FAQ. Same loader as the original store; the listing comes from Theme settings >
    SKINOFAB > Product Page (window.SFFrontrowId), and without one nothing loads."""
    return ('<script data-sf-frontrow>(function () {'
            'var id = String(window.SFFrontrowId || "");'
            'if (!/^[0-9]+$/.test(id)) return;'
            'var base = "https://app.thefrontrowhealth.com/api/widgets";'
            'function firstSlideOnly(iframe, gallery) {'
            'var slider = gallery.querySelector("[data-product-single-media-slider]");'
            'if (!slider) return;'
            'function first() {'
            'var slides = slider.querySelectorAll("[data-product-single-media-wrapper]");'
            'if (slides.length < 2) return true;'
            'var selected = slider.querySelector("[data-product-single-media-wrapper].is-selected");'
            'if (selected) return selected === slides[0];'
            'var r0 = slides[0].getBoundingClientRect(), rs = slider.getBoundingClientRect();'
            'return Math.abs(r0.left - rs.left) < r0.width / 2; }'
            'function update() { iframe.style.display = first() ? "" : "none"; }'
            'if (typeof MutationObserver === "function") new MutationObserver(update).observe(slider, { attributes: true, subtree: true, attributeFilter: ["class"] });'
            'slider.addEventListener("scroll", update, { passive: true });'
            'window.addEventListener("resize", update);'
            'update(); }'
            'function mount() {'
            'var s = document.createElement("script"); s.async = true;'
            's.src = base + "/script?presentation_type=sticker&product_id=" + id; document.head.appendChild(s);'
            'var f = document.createElement("iframe"); f.id = "frontrow-sticker"; f.className = "iframe-frontrow-sticker";'
            'f.setAttribute("data-state", "max"); f.frameBorder = "0"; f.title = "Clinicians’ Choice on FrontrowMD";'
            'f.src = base + "?presentation_type=sticker&product_id=" + id;'
            'var gallery = document.querySelector("[data-product-single-media-group]");'
            'if (!gallery) return;'
            'if (getComputedStyle(gallery).position === "static") gallery.style.position = "relative";'
            'gallery.appendChild(f); firstSlideOnly(f, gallery); }'
            # after the page has loaded and gone idle: its third-party scripts stay off the critical path
            'function later() { (window.requestIdleCallback || function (f) { setTimeout(f, 1) })(mount, { timeout: 3000 }); }'
            'if (document.readyState === "complete") later(); else window.addEventListener("load", later);'
            '})();</script>')


def trust_block():
    """Under the add-to-cart button: love it or your money back, free shipping / 30-day guarantee / secure checkout,
    and the refill terms (shown by the picker only while Automatic Refills is ticked)."""
    return f'<div class="product__block sfp-trust"><style>{apf_copy.TRUST_CSS}</style>{apf_copy.trust_html()}</div>'

# ---------------------------------------------------------------- the Lymphatic Brush's product page
WORK = Path(sys.argv[3]).resolve().parent
BRUSH_IMG = Path(__file__).resolve().parents[2] / 'brand' / 'lymphatic-brush'   # tools/persona/brush_assets.py

def hashed_copy(src, sub, name, size=None):
    """src copied into the export (assets/<sub>/) as <name>-<hash><ext>, resized to fit `size` if given."""
    from PIL import Image
    out = DST / 'assets' / sub
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / (name + src.suffix)
    if size:
        im = Image.open(src).convert('RGB'); im.thumbnail(size, Image.LANCZOS)
        im.save(tmp, quality=86, optimize=True, progressive=True)
    else:
        shutil.copy2(src, tmp)
    final = tmp.with_name(f"{name}-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}{src.suffix}")
    tmp.rename(final)
    return f'../assets/{sub}/{final.name}'

def brush_rating(imported=None):
    """Stars and count from the product's approved NEXT reviews and its imported ones (count and sum of their ratings),
    shown only once there are some."""
    n0, s0 = (imported or {}).get('count', 0), sum(int(k) * v for k, v in ((imported or {}).get('distribution') or {}).items())
    stars = ''.join(f'<span class="sf-star" style="--f:100%">{STAR}{STAR}</span>' for _ in range(5))
    return ('<a class="sfb-rating" href="#sf-review-wall" data-sfb-rating hidden style="text-decoration:none">'
            f'<span class="sf-rating" style="--sf-star:#000000"><span class="sf-rating__stars" role="img">{stars}</span>'
            '<span class="sf-rating__text"></span></span></a>'
            '<style>.sfb-rating[hidden]{display:none}.sf-rating{display:inline-flex;align-items:center;gap:10px;color:#151515;font-size:17px;line-height:1}'
            '.sf-rating__stars{display:inline-flex;gap:2px}'
            '.sf-star{position:relative;display:inline-block;width:20px;height:20px;color:#d8d8d8}'
            '.sf-star svg{position:absolute;left:0;top:0}'
            '.sf-star svg+svg{color:var(--sf-star);clip-path:inset(0 calc(100% - var(--f)) 0 0)}</style>'
            '<script>(function () {'
            'var badge = document.currentScript.previousElementSibling.previousElementSibling;'
            'function show() {'
            'var el = document.querySelector("[data-sf-native-reviews]"), d = null;'
            'try { d = JSON.parse(el ? el.textContent : "{}"); } catch (e) { return; }'
            'var rs = (d && d.reviews || []).filter(function (r) { return +r.score >= 1 && +r.score <= 5; });'
            f'var n = rs.length + {int(n0)}, sum = rs.reduce(function (s, r) {{ return s + +r.score; }}, {int(s0)});'
            'if (!n) return;'
            'var avg = sum / n;'
            'Array.prototype.forEach.call(badge.querySelectorAll(".sf-star"), function (s, i) {'
            's.style.setProperty("--f", Math.max(0, Math.min(1, Math.round((avg - i) * 2) / 2)) * 100 + "%"); });'
            'badge.querySelector(".sf-rating__stars").setAttribute("aria-label", "Rated " + avg.toFixed(1) + " out of 5");'
            'badge.querySelector(".sf-rating__text").textContent = avg.toFixed(1) + "/5 \\u00b7 " + n.toLocaleString("en-US") + " review" + (n === 1 ? "" : "s");'
            'badge.hidden = false; }'
            'if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", show); else show();'
            '})();</script>')

def brush_page(base):
    """products/the-lymphatic-brush.html: the foundation page's chrome and buy box markup with Solena's brush page
    (brush_copy) in it, and the brush's sections below. Prices, the bundle picker's variants and the cart come from
    NEXT (brush-offers.json, written by setup_brush_offers.py)."""
    import copy
    from bs4 import BeautifulSoup, NavigableString
    offers = json.loads((WORK / 'brush-offers.json').read_text())
    soup = BeautifulSoup(base, 'html.parser')
    frag = lambda h: BeautifulSoup(h, 'html.parser')
    main = soup.find('main')
    prod = main.select_one('[id$="__main"].shopify-section--product')
    faq_src = main.select_one('[id*="__section_accordions_"]')
    faq_src = copy.copy(faq_src) if faq_src else None
    for sec in [c for c in main.find_all(recursive=False) if c is not prod and 'section_custom_html' not in (c.get('id') or '')]:
        sec.decompose()
    img = lambda k, w: hashed_copy(BRUSH_IMG / f'gallery-{k}.jpg', 'img', f'skinofab-lymphatic-brush-{k}-{w}w', (w, w))
    # gallery: Solena's seven images, the first one eager
    slider = prod.select_one('[data-product-single-media-slider]')
    slides = slider.select('[data-product-single-media-wrapper]')
    thumbs = prod.select_one('[data-product-single-media-thumbs]')
    t_slides = [copy.copy(slides[0]), copy.copy(slides[1])]
    t_thumb = copy.copy(thumbs.select('[data-thumbnail-id]')[0])
    for s_ in slides: s_.decompose()
    for t_ in thumbs.select('[data-thumbnail-id]'): t_.decompose()
    for k in range(1, 8):
        mid = str(9300000000000 + k)
        big, mid_src, small = img(k, 1080), img(k, 753), img(k, 178)
        sl = copy.copy(t_slides[0 if k == 1 else 1])
        sl['data-id'], sl['data-media-id'] = mid, f'brush-{mid}'
        sl['id'] = f'FeaturedMedia-brush-{mid}'
        im = sl.find('img')
        im['src'], im['srcset'] = big, f'{mid_src} 753w, {big} 1080w'
        im['alt'], im['data-image-id'] = brush_copy.TITLE, mid
        if k > 1: im['fetchpriority'] = 'low'
        slider.append(sl)
        th = copy.copy(t_thumb)
        th['data-id'], th['data-thumbnail-id'] = mid, f'brush-{mid}'
        th.find('a')['aria-label'] = brush_copy.TITLE
        ti = th.find('img')
        ti['src'], ti['srcset'], ti['alt'] = small, f'{big} 1080w', brush_copy.TITLE
        ti['loading'] = 'eager' if k <= 5 else 'lazy'
        thumbs.append(th)
    # the buy box, top to bottom
    blocks = prod.select('.product__block')
    def text_of(b): return ' '.join(b.get_text(' ', strip=True).split())
    for b in blocks:
        cls = b.get('class') or []
        t = text_of(b)
        if 'Korean beauty' in t or 'product__subheading' in str(b)[:200] or 'countdown-timer-wrapper' in cls \
           or b.get('data-default-usp') is not None or b.select_one('[data-serum-subscription-usps]') or b.select_one('hr') \
           or {'product__features', 'product-suitability', 'customer-survey-results'} & set(cls):
            b.decompose()
    social = prod.select_one('.social-proof-container')
    for n, pi in enumerate(social.select('.profile-image'), 1):
        pi['style'] = f"background-image:url('{hashed_copy(BRUSH_IMG / f'buyer-{n}.jpg', 'img', f'skinofab-brush-buyer-{n}')}')"
    social.select_one('.text1').string = ''
    social.select_one('.text1').append(frag(f'<strong>{brush_copy.esc(brush_copy.BUYERS["name"])}</strong>'))
    social.select_one('.text2').string = brush_copy.BUYERS['text']
    brush_reviews = WORK / 'reviews-brush'      # tools/reviews/import_reviews.py ... --product the-lymphatic-brush --out reviews-brush
    stats = json.loads((brush_reviews / 'reviews.json').read_text()) if (brush_reviews / 'reviews.json').exists() else None
    app = prod.select_one('.product__block.standard__app')
    app.clear(); app.append(frag(brush_rating(stats)))
    price = prod.select_one('.product__price-and-badge [data-price-wrapper]')
    price.select_one('.product__price--compare').string = brush_copy.money(brush_copy.COMPARE)
    reg = price.select_one('.product__price--regular')
    reg.string = brush_copy.money(brush_copy.PRICE)
    off = price.select_one('.product__price--off')
    if off: off.decompose()
    reg.insert_after(frag(f'<span class="sfb-ship">{brush_copy.esc(brush_copy.SHIPPING_BADGE)}</span>'))
    usp = prod.select_one('.skinofab-usp-grid')
    usp.replace_with(frag(f'<style>{brush_copy.BUYBOX_CSS}</style>' + brush_copy.chips_html()))
    form = prod.select_one('form[data-product-form]')
    form.select_one('input[name=id]')['value'] = str(brush_copy.SHOPIFY_VARIANT)
    for el in form.select('.shop-pay-terms'): el.decompose()
    for el in prod.select('skinofab-installments'): el.decompose()   # the foundation's pay-in-4 line
    for el in soup.select('script.kaching-bundles-product, script.kaching-bundles-deal-block-settings'): el.decompose()
    btn = form.select_one('[data-add-to-cart]')
    label = btn.select_one('[data-add-to-cart-text]') if btn else None
    if label: label.insert_after(frag('<span class="sfb-btn-price" data-sfb-btn-price></span>'))
    if btn and btn.get('data-notification-popup'):
        btn['data-notification-popup'] = btn['data-notification-popup'].replace('Adaptive Peptide Foundation', brush_copy.TITLE).replace('Color Changing Foundation', brush_copy.TITLE)
    gift_imgs = {k: hashed_copy(BRUSH_IMG / f'gift-{f}.jpg', 'img', f'skinofab-brush-gift-{f}') for k, f in (('case', 'case'), ('body', 'body-brush'))}
    form.select_one('[data-subscription-watch-price]').insert_before(
        frag(brush_copy.picker_html(offers['variants'], gift_imgs, apf_copy.OFFER_PICKER_CSS)))
    cta = form.select_one('#CTA_kopstorm')
    guar = frag(f'<div class="product__block sfb-guar-block"><p class="sfb-guar">{brush_copy._CHECK}<span>{brush_copy.esc(brush_copy.GUARANTEE)}</span></p></div>')
    cta.insert_after(guar)
    # the five tabs, in the design's accordion markup
    accs = prod.select('.product__block.product__accordions')
    tpl, anchor = copy.copy(accs[0]), accs[-1]
    media = WORK / 'brush' / 'media'
    tutorial = (hashed_copy(media / 'brush-how-to.mp4', 'media', 'skinofab-brush-how-to'),
                hashed_copy(media / 'brush-how-to.jpg', 'img', 'skinofab-brush-how-to-poster'))
    for k, (title, body) in reversed(list(enumerate(brush_copy.tabs(tutorial)))):
        a = copy.copy(tpl)
        a['id'] = f'Block--sfb_tab_{k}'
        a.select_one('[data-collapsible-trigger]')['aria-controls'] = f'ProductAccordion--sfb-tab-{k}'
        a.select_one('[data-collapsible-container]')['id'] = f'ProductAccordion--sfb-tab-{k}'
        span = a.select_one('#accordionbefore'); span.clear(); span.append(frag(title))
        inner = a.select_one('[data-collapsible-content]'); inner.clear(); inner.append(frag(body))
        anchor.insert_after(a)
    for a in accs: a.decompose()
    # the sticky bar: the brush, its price, back to the bundles
    sticky = prod.select_one('#sticky_atcs')
    if sticky:
        wraps = sticky.select('.wrap')
        for w in wraps[1:]: w.decompose()
        w = wraps[0]
        im = w.find('img'); im['src'], im['alt'] = hashed_copy(BRUSH_IMG / 'gallery-1.jpg', 'img', 'skinofab-lymphatic-brush-180w', (180, 180)), brush_copy.TITLE
        w.find('h5').string = brush_copy.TITLE
        w.select_one('.product__price--sale').string = brush_copy.money(brush_copy.PRICE)
        w.select_one('.product__price--compare').string = brush_copy.money(brush_copy.COMPARE)
        go = w.select_one('a.product__submit__add'); go['href'] = '#apf-buy'; go.string = brush_copy.STICKY_BUTTON
    # the foundation's FrontrowMD sticker styles do not belong here
    for st in prod.find_all('style'):
        if '#frontrow-sticker' in (st.string or ''): st.decompose()
    for node in prod.find_all(string=True):
        if 'Color Changing Foundation' in node or 'Adaptive Peptide Foundation' in node:
            node.replace_with(node.replace('Color Changing Foundation', brush_copy.TITLE).replace('Adaptive Peptide Foundation', brush_copy.TITLE))
    for el in prod.find_all(alt=True):
        el['alt'] = el['alt'].replace('Color Changing Foundation', brush_copy.TITLE).replace('Adaptive Peptide Foundation', brush_copy.TITLE)
    # the sections below, in Solena's order
    clips = [(hashed_copy(media / f'brush-review-{k}.mp4', 'media', f'skinofab-brush-review-{k}'),
              hashed_copy(media / f'brush-review-{k}.jpg', 'img', f'skinofab-brush-review-{k}-poster')) for k in range(1, 7)]
    how = [hashed_copy(BRUSH_IMG / f'how-{k}.jpg', 'img', f'skinofab-brush-how-{k}') for k in range(1, 4)]
    cmp_ = [hashed_copy(BRUSH_IMG / f'compare-{k}.jpg', 'img', f'skinofab-brush-compare-{k}') for k in ('ours', 'copy')]
    strip = review_strip(brush_reviews)
    out = ([f'<div class="shopify-section" id="shopify-section-sf-review-strip">{strip}</div>'] if strip else []) + [
           f'<div class="shopify-section" id="shopify-section-sf-brush-videos"><style>{brush_copy.SECTIONS_CSS}</style>{brush_copy.videos_html(clips)}</div>',
           f'<div class="shopify-section" id="shopify-section-sf-brush-how">{brush_copy.how_html(how)}</div>',
           f'<div class="shopify-section" id="shopify-section-sf-brush-compare">{brush_copy.compare_html(*cmp_)}</div>']
    if faq_src:
        lst = faq_src.select('.accordion__list')
        items = lst[0].select('li.accordion__item')
        li_tpl = copy.copy(items[0])
        for l in lst:
            for li in l.select('li.accordion__item'): li.decompose()
        for k, (q, a) in enumerate(brush_copy.FAQ['items']):
            li = copy.copy(li_tpl)
            li['id'] = f'Accordion--sfb_{k}'
            li['class'] = [c for c in li.get('class', []) if c != 'accordion__item--first'] + (['accordion__item--first'] if k == 0 else [])
            li.select_one('[data-collapsible-trigger]')['aria-controls'] = f'Accordions-item--sfb{k}'
            li.select_one('[data-collapsible-container]')['id'] = f'Accordions-item--sfb{k}'
            li.select_one('.accordion__item__title__text').string = q
            body = li.select_one('[data-collapsible-content]'); body.clear(); body.append(frag(f'<p>{a}</p>'))
            lst[0].append(li)
        # one centered column, as on Solena's page
        cols = faq_src.select('.accordion__column')
        for c in cols[1:]: c.decompose()
        if cols: cols[0]['style'] = 'width:100%;max-width:760px;margin:0 auto;flex:1 1 100%'
        h2 = faq_src.select_one('.section__heading')
        h2.string = brush_copy.FAQ['title']
        h2.insert_before(frag(f'<span class="sfb-eyebrow" style="display:block;font-size:13px;font-weight:600;letter-spacing:.12em;'
                              f'text-transform:uppercase;color:#6a6a6a;margin:0 0 12px">{brush_copy.esc(brush_copy.FAQ["eyebrow"])}</span>'))
        faq_src['id'] = 'shopify-section-sf-brush-faq'
        out.append(str(faq_src))
    out.append(f'<div class="shopify-section" id="shopify-section-sf-brush-risk-free">{brush_copy.risk_free_html()}</div>')
    out.append(f'<div class="shopify-section" id="shopify-section-sf-review-wall">{review_wall(brush_reviews)}</div>')
    prod.insert_after(frag(''.join(out)))
    # the design's product JSON (the theme's product script reads prices and variants from it)
    gallery = [s_.find('img')['src'] for s_ in slider.select('[data-product-single-media-wrapper]')]
    pj = soup.select_one('script[data-product-json]')
    if pj: pj.string = json.dumps(brush_snapshot(['/' + g.lstrip('./') for g in gallery]), ensure_ascii=True)
    # head and body: the brush's own title, description and page id
    text = str(soup)
    text = re.sub(r'<title>.*?</title>', f'<title>{html.escape(brush_copy.META_TITLE)}</title>', text, count=1, flags=re.S)
    text = re.sub(r'<meta content="[^"]*" name="description"/>', f'<meta content="{html.escape(brush_copy.META_DESCRIPTION)}" name="description"/>', text, count=1)
    text = text.replace('id="color-adapting-foundation-for-flawless-skin-skinofab"', 'id="the-lymphatic-brush-skinofab"', 1)
    return text

def brush_shelf(home):
    """The homepage product shelf: the brush's card in the default list (the Bestsellers view) and in the Bestsellers,
    New and Face tabs, after the product brush_copy.SHELF names (first when None), in each place's own card markup."""
    m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+__bestsellers"', home)
    if not m: return home, False
    end = home.find('</section>', m.start())
    sec = home[m.start():end]
    sh, title, href = brush_copy.SHELF, html.escape(brush_copy.TITLE), f'products/{brush_copy.HANDLE}.html'
    big = hashed_copy(BRUSH_IMG / 'card.jpg', 'img', 'skinofab-lymphatic-brush-card-1080w', (1080, 1080))[3:]
    small = hashed_copy(BRUSH_IMG / 'card.jpg', 'img', 'skinofab-lymphatic-brush-card-720w', (720, 720))[3:]
    price = f'<div class="fh-price"><s>{brush_copy.money(brush_copy.COMPARE)} USD</s><span>{brush_copy.money(brush_copy.PRICE)} USD</span></div>'
    rich = (f'<article class="fh-product">\n<a aria-label="{title}" class="fh-product-image" href="{href}">\n'
            f'<picture class=""><img alt="{title}" class="fh-upload" height="1080" loading="lazy" sizes="100vw" src="{big}" '
            f'srcset="{small} 720w, {big} 1080w" width="1080"/>\n</picture>\n'
            f'<span class="fh-badges"><span>{html.escape(sh["badge"])}</span><span class="fh-saving">{html.escape(sh["saving"])}</span></span></a>\n'
            f'<div class="fh-product-info"><h3><a href="{href}">{title}</a></h3>\n{price}'
            '<div class="fh-benefits-tags">' + ''.join(f'<span>{html.escape(x)}</span>' for x in sh['tags']) + '</div></div>\n</article>\n')
    plain = (f'<article class="fh-product"><a class="fh-product-image" href="{href}"><img alt="{title}" height="720" loading="lazy" '
             f'sizes="(min-width: 750px) 25vw, 66vw" src="{small}" srcset="{small} 720w" width="720"/></a>'
             f'<div class="fh-product-info"><h3><a href="{href}">{title}</a></h3>\n{price}</div></article>')
    def place(block, card, after):
        """block with card inserted after the article linking to products/<after>.html (first when None)."""
        arts = [(a.start(), block.find('</article>', a.start()) + len('</article>')) for a in re.finditer(r'<article class="fh-product">', block)]
        if not arts: return None
        if after is None: pos = arts[0][0]
        else:
            hit = [e for s_, e in arts if f'products/{after}.html"' in block[s_:e]]
            if not hit: return None
            pos = hit[0]
        return block[:pos] + card + block[pos:]
    ok = True
    for key, after in sh['after'].items():
        if key == 'list':
            mm = re.search(r'<div class="fh-product-list"[^>]*>', sec)
            card = rich
        else:
            mm = re.search(r'<div class="fh-tab-products" data-fh-panel="%s"[^>]*>' % key, sec)
            card = plain
        if not mm: ok = False; continue
        close = balanced_end(sec, mm.start(), 'div')
        new = place(sec[mm.start():close], card, after)
        if new is None: ok = False; continue
        sec = sec[:mm.start()] + new + sec[close:]
    return home[:m.start()] + sec + home[end:], ok

def brush_snapshot(gallery):
    """products/the-lymphatic-brush.js: the Shopify product JSON shape the theme build reads (handle, ids, prices)."""
    cents = lambda v: int(round(float(v) * 100))
    v = {'id': brush_copy.SHOPIFY_VARIANT, 'title': 'Default Title', 'option1': 'Default Title', 'option2': None, 'option3': None,
         'sku': 'SKF-LYB-1', 'requires_shipping': True, 'taxable': True, 'featured_image': None, 'available': True,
         'name': brush_copy.TITLE, 'public_title': None, 'options': ['Default Title'], 'price': cents(brush_copy.PRICE),
         'compare_at_price': cents(brush_copy.COMPARE), 'requires_selling_plan': False, 'selling_plan_allocations': []}
    return {'id': brush_copy.SHOPIFY_ID, 'title': brush_copy.TITLE, 'handle': brush_copy.HANDLE, 'description': brush_copy.DESCRIPTION,
            'vendor': 'Skinofab', 'type': '', 'tags': [], 'price': v['price'], 'price_min': v['price'], 'price_max': v['price'],
            'available': True, 'price_varies': False, 'compare_at_price': v['compare_at_price'],
            'compare_at_price_min': v['compare_at_price'], 'compare_at_price_max': v['compare_at_price'], 'compare_at_price_varies': False,
            'variants': [v], 'images': gallery, 'featured_image': gallery[0],
            'options': [{'name': 'Title', 'position': 1, 'values': ['Default Title']}], 'url': f'/products/{brush_copy.HANDLE}',
            'media': [], 'requires_selling_plan': False, 'selling_plan_groups': []}

def honest_counts(texts, summary):
    """The design's review and customer counts were far above what its review app records (the foundation showed
    351,837 reviews; Loox counts 10,512; the serum 61,583 for 22). Every count becomes a real one: the imported
    reviews' total for the foundation and the store-wide lines, each other product's own Loox count. Returns hits."""
    n, five, avg = int(summary['count']), int(summary['distribution'].get('5', summary['distribution'].get(5, 0))), float(summary['average'])
    floor = lambda v: f'{(v // 1000) * 1000:,}' if v >= 1000 else str(v)
    reps = [
        (r'Loved by 50,000\+', f'Loved by {floor(n)}+'),
        (r'50,000\+ customers', f'{floor(n)}+ customers'),
        (r'Over 50,000 5-star reviews', f'Over {floor(five)} 5-star reviews'),
        (r'Trusted by 1,000,000\+ women who finally found something that works', 'From verified buyers who finally found something that works'),
        (r'Backed by over 1,000,000 customers, 50,000 five-star reviews and data from independent panels run with real customers',
         f'Backed by over {floor(n)} verified reviews, {avg:.1f} out of 5 on average'),
        (r'4\.8 \(351,837 reviews\)', f'{avg:.1f} ({n:,} reviews)'),
    ]
    hits = {}
    # each product's own Loox count, from its rating badge (data-raters), for its badge pattern and its cards
    real = {}
    for p, txt in texts.items():
        for m in re.finditer(r'<div class="loox-rating loox-widget"[^>]*>', txt):
            tag = m.group(0)
            pat = re.search(r'data-pattern="([^"]*)"', tag); raters = re.search(r'data-raters="(\d+)"', tag); rating = re.search(r'data-rating="([\d.]+)"', tag)
            if pat and raters and rating:
                old = re.search(r'\(([\d,]+) reviews\)', pat.group(1))
                if old and old.group(1) != '351,837': real[old.group(1)] = (float(rating.group(1)), int(raters.group(1)))
    for p in list(texts):
        txt = texts[p]
        for rx, rep in reps:
            txt, k = re.subn(rx, rep, txt)
            if k: hits[rx[:30]] = hits.get(rx[:30], 0) + k
        # the cards' "4.8 (61,583 reviews)" lines: that product's own count
        def card(m):
            r = real.get(m.group(1))
            return f'{r[0]:.1f} ({r[1]:,} reviews)' if r else m.group(0)
        txt = re.sub(r'4\.8 \(([\d,]+) reviews\)', card, txt)
        # badge patterns: the real count (only the foundation's badge is drawn, by rating_block)
        txt = re.sub(r'(<div class="loox-rating loox-widget"[^>]*?)data-pattern="[^"]*"([^>]*?data-raters="(\d+)"[^>]*?data-rating="([\d.]+)")',
                     lambda m: f'{m.group(1)}data-pattern="{float(m.group(4)):.1f}/5 ({int(m.group(3)):,} reviews)"{m.group(2)}', txt)
        texts[p] = txt
    return hits

def faster_home(home):
    """Homepage speed (measured on a throttled phone: LCP 7.2 s). The hidden second hero slide loaded its 1,680-px image
    at once and competed with the first; the shelf cards asked for 1,920-px images (sizes 100vw) for a ~260-px card;
    the phone hero downloaded the whole 1,800-px banner although only a quarter of it shows. Returns (html, changes)."""
    from PIL import Image, ImageFilter
    import numpy as np
    n = {}
    home, n['lazy hero slides'] = re.subn(r'(<img[^>]*fetchpriority="low"[^>]*?)loading="eager"', r'\1loading="lazy"', home)
    home, n['card sizes'] = re.subn(r'(<img[^>]*class="fh-upload"[^>]*?)sizes="100vw"', r'\1sizes="(min-width: 990px) 300px, 270px"', home)
    # phone hero: the same banner at the same size, with everything outside the part a phone shows (62% to 88% of its
    # width; the layout scales with the screen) flattened into the backdrop, so it compresses to a fraction
    m = re.search(r'(<picture class="fh-hero-image">\s*)(<img[^>]*class="fh-original"[^>]*fetchpriority="high"[^>]*src="assets/img/([^"]+)")', home)
    if m:
        src = DST / 'assets' / 'img' / m.group(3)
        im = Image.open(src).convert('RGB'); im = im.resize((2400, round(im.height * 2400 / im.width)), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32)
        w = a.shape[1]; x = np.arange(w) / w
        keep = np.clip(np.minimum((x - 0.58) / 0.04, (0.92 - x) / 0.04), 0, 1)[None, :, None]
        flat = np.asarray(im.filter(ImageFilter.GaussianBlur(60))).astype(np.float32)
        out = Image.fromarray(np.clip(a * keep + flat * (1 - keep), 0, 255).astype(np.uint8))
        tmp = DST / 'assets' / 'img' / 'skinofab-hero-phone.jpg'
        out.save(tmp, quality=80, optimize=True, progressive=True)
        final = tmp.with_name(f"skinofab-hero-phone-2400w-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.jpg"); tmp.rename(final)
        sizes = re.search(r'sizes="\(max-width: 749px\) ([0-9.]+vw)', m.group(2))
        source = (f'<source media="(max-width: 749px)" sizes="{sizes.group(1) if sizes else "349vw"}" '
                  f'srcset="assets/img/{final.name} 2400w" width="{out.width}" height="{out.height}">')
        home = home[:m.start(2)] + source + home[m.start(2):]
        n['phone hero KB'] = round(final.stat().st_size / 1024)
    return home, n

def balanced_end(t, start, tag):
    depth = 0
    for m in re.finditer(r'<(/?)%s\b[^>]*>' % tag, t[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0: return start + m.end()
    raise ValueError('unbalanced ' + tag)

def main():
    if DST.exists(): shutil.rmtree(DST)
    for d, dirs, files in os.walk(SRC):
        out = DST / Path(d).relative_to(SRC); out.mkdir(parents=True, exist_ok=True)
        for f in files:
            s, t = Path(d) / f, out / f
            if s.suffix.lower() in TEXT: shutil.copy2(s, t)
            else: os.link(s, t)
    hits, missing = {}, []
    # page rules first: they rewrite whole blocks that the global rules would otherwise half-change
    rules = [(f, o, n) for f, rs in ccf_copy.PAGE.items() for o, n in rs] + [(None, o, n) for o, n in ccf_copy.GLOBAL + brush_copy.GLOBAL]
    pages = sorted(DST.rglob('*.html'))
    texts = {p: p.read_text(encoding='utf-8', errors='surrogateescape') for p in pages}
    for scope, old, new in rules:
        rx, rep = compile_rule(old, new)
        n = 0
        for p in ([DST / scope] if scope else pages):
            texts[p], k = (rx.subn(rep, texts[p]) if old.startswith('RE:') else rx.subn(lambda m: rep, texts[p])); n += k
        hits[old[:60]] = n
        if not n: missing.append((scope or '*', old[:90]))
    snap = DST / 'products' / 'color-changing-foundation.js'
    data = json.loads(snap.read_text())
    imgs = data.get('images', [])
    ordered = []
    for prefix in getattr(ccf_copy, 'GALLERY', []):
        hit = next((u for u in imgs if Path(u.split('?')[0]).name.startswith(prefix) and u not in ordered), None)
        if hit: ordered.append(hit)
        else: missing.append(('gallery', prefix))
    data['images'] = ordered + [u for u in imgs if u not in ordered]
    snap.write_text(json.dumps(data))
    pdp = DST / 'products' / 'color-changing-foundation.html'
    base_pdp = texts[pdp]   # the brush page starts from the foundation page before its own sections go in
    anchor = '<span data-subscription-watch-price=""></span>'
    if texts[pdp].count(anchor) < 1: missing.append(('picker', anchor))
    texts[pdp] = texts[pdp].replace(anchor, picker() + anchor, 1)
    # the original store's FrontrowMD styles, with the sticker's mobile scale and the modal rules (FRONTROW_CSS); the
    # loader goes after the title block (it mounts the sticker on the gallery)
    texts[pdp], n = re.subn(r'<style>\s*#frontrow-sticker\s*\{.*?</style>', '<style>' + FRONTROW_CSS + '</style>', texts[pdp], count=1, flags=re.S)
    if not n: missing.append(('frontrow', 'sticker styles'))
    title = re.search(r'<div class="product__block product__title-and-price"[^>]*>', texts[pdp])
    if not title: missing.append(('frontrow', 'title block'))
    else:
        end = balanced_end(texts[pdp], title.start(), 'div')
        texts[pdp] = texts[pdp][:end] + frontrow_block() + texts[pdp][end:]
    # a strip of short verified reviews right after the buy box
    strip = review_strip()
    main_sec = re.search(r'<div class="shopify-section shopify-section--product" id="shopify-section-template--[0-9]+__main">', texts[pdp])
    if strip and main_sec:
        end = balanced_end(texts[pdp], main_sec.start(), 'div')
        texts[pdp] = texts[pdp][:end] + '<div class="shopify-section" id="shopify-section-sf-review-strip">' + strip + '</div>' + texts[pdp][end:]
    elif strip: missing.append(('review strip', 'buy box section'))
    # problem -> root cause -> solution, right after the first customer reviews
    rev = re.search(r'<div[^>]*id="shopify-section-[^"]*kopstorm_testomonials[^"]*"[^>]*>', texts[pdp])
    if not rev: missing.append(('problem/solution', 'reviews section'))
    else:
        end = balanced_end(texts[pdp], rev.start(), 'div')
        texts[pdp] = texts[pdp][:end] + '<div class="shopify-section" id="shopify-section-sf-problem-solution">' + problem_solution() + '</div>' + texts[pdp][end:]
    # the homepage's dermatologist after the solution, its customer reviews before the FAQ, more FAQ answers
    home = texts.get(DST / 'index.html', '')
    derm = dermatologist(home)
    ps_end = texts[pdp].find('id="shopify-section-sf-problem-solution"')
    if not derm or ps_end < 0: missing.append(('dermatologist', 'homepage section or anchor'))
    else:
        start = texts[pdp].rfind('<div', 0, ps_end)
        end = balanced_end(texts[pdp], start, 'div')
        texts[pdp] = texts[pdp][:end] + '<div class="shopify-section" id="shopify-section-sf-dermatologist">' + derm + '</div>' + texts[pdp][end:]
        # the K-beauty skin science after the dermatologist (apf_copy.KBEAUTY: the actives on the label, no person)
        kb = section_image(BRAND / 'adaptive-peptide-foundation' / 'composites' / 'label-detail.jpg', 'skinofab-kbeauty-label', (465, 581))
        d_at = texts[pdp].find('id="shopify-section-sf-dermatologist"')
        d_end = balanced_end(texts[pdp], texts[pdp].rfind('<div', 0, d_at), 'div')
        texts[pdp] = texts[pdp][:d_end] + '<div class="shopify-section" id="shopify-section-sf-kbeauty">' + apf_copy.kbeauty_html(kb) + '</div>' + texts[pdp][d_end:]
    revs = video_reviews(home)
    faq = re.search(r'<div class="shopify-section" id="shopify-section-template--[0-9]+__section_accordions_', texts[pdp])
    if not revs or not faq: missing.append(('reviews', 'homepage section or FAQ anchor'))
    else:
        texts[pdp] = texts[pdp][:faq.start()] + '<div class="shopify-section" id="shopify-section-sf-reviews">' + revs + '</div>' + texts[pdp][faq.start():]
    texts[pdp], ok = faq_more(texts[pdp])
    if not ok: missing.append(('faq', 'accordion columns'))
    # the review wall after the FAQ, before "The skinofab difference"
    why = re.search(r'<div class="shopify-section" id="shopify-section-template--[0-9]+__kopstorm_why_', texts[pdp])
    if not why: missing.append(('review wall', 'anchor'))
    else:
        texts[pdp] = texts[pdp][:why.start()] + '<div class="shopify-section" id="shopify-section-sf-review-wall">' + review_wall() + '</div>' + texts[pdp][why.start():]
    found = review_data()
    texts[pdp], ok = rating_block(texts[pdp], found and found['summary'])
    if not ok: missing.append(('rating', 'loox badge'))
    cta = texts[pdp].find('<div id="CTA_kopstorm">')
    if cta < 0: missing.append(('trust block', 'CTA_kopstorm'))
    else:
        end = balanced_end(texts[pdp], cta, 'div')
        texts[pdp] = texts[pdp][:end] + trust_block() + texts[pdp][end:]
    # real review and customer counts everywhere (the foundation's imported reviews are the store's real total)
    if found:
        print('honest counts', honest_counts(texts, found['summary']))
    # homepage speed: lazy hidden hero slides, right-sized shelf cards, a phone hero that only carries what shows
    if DST / 'index.html' in texts:
        texts[DST / 'index.html'], sp = faster_home(texts[DST / 'index.html'])
        print('home speed', sp)
    # the Lymphatic Brush in the homepage's product shelf, like the other products
    if DST / 'index.html' in texts:
        texts[DST / 'index.html'], ok = brush_shelf(texts[DST / 'index.html'])
        if not ok: missing.append(('brush', 'homepage shelf list or tab'))
    # the Lymphatic Brush's page (brush_copy) and its product snapshot
    brush = DST / 'products' / f'{brush_copy.HANDLE}.html'
    texts[brush] = brush_page(base_pdp)
    gallery = sorted(set(re.findall(r'\.\./assets/img/(skinofab-lymphatic-brush-\d-1080w-[0-9a-f]{6}\.jpg)', texts[brush])),
                     key=lambda g: int(g.split('-')[3]))
    (DST / 'products' / f'{brush_copy.HANDLE}.js').write_text(json.dumps(brush_snapshot(['/assets/img/' + g for g in gallery])))
    for p, t in texts.items(): p.write_text(t, encoding='utf-8', errors='surrogateescape')
    # the theme build turns this into the Cart Drawer theme settings (upgrade, add-ons, review)
    (DST / 'sf-offer.json').write_text(json.dumps(cart_offer(), indent=1, ensure_ascii=False))
    # Replaced images get a new, content-hashed file name and every reference is rewritten: NEXT's CDN keeps
    # serving a cached copy for a re-uploaded file name, so a changed image must never reuse its old name.
    replaced, renames = 0, {}
    if IMAGES and IMAGES.exists():
        for img in sorted(IMAGES.iterdir()):
            target = DST / 'assets' / 'img' / img.name
            if not target.exists(): missing.append(('image target', img.name)); continue
            digest = hashlib.md5(img.read_bytes()).hexdigest()[:6]
            stem, ext = os.path.splitext(img.name)
            new = (re.sub(r'-[0-9a-f]{6}$', '', stem) + f'-p{digest}{ext}')
            shutil.copy2(img, target.with_name(new)); renames[img.name] = new; replaced += 1
    if renames:
        rx = re.compile('|'.join(re.escape(k) for k in sorted(renames, key=len, reverse=True)))
        for p in DST.rglob('*'):
            if p.is_file() and p.suffix.lower() in TEXT:
                t = p.read_text(encoding='utf-8', errors='surrogateescape')
                n = rx.sub(lambda m: renames[m.group(0)], t)
                if n != t: p.write_text(n, encoding='utf-8', errors='surrogateescape')
    print(json.dumps({'rules': len(rules), 'replacements': sum(hits.values()), 'images': replaced, 'missing': missing}, ensure_ascii=False, indent=1))
    if missing: sys.exit(1)

main()
