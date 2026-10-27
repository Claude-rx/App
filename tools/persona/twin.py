"""The second products' pages (the Lymphatic Brush, the PDRN Plumping Balm) in the Adaptive Peptide Foundation page's
structure: every section of the finished foundation page, in its order and in its own markup and styles, filled with
the product's copy and images (P.TWIN in brush_copy.py / balm_copy.py).

apply_persona.product_page() builds the buy box; sections() here gives everything under it. Section by section:

  review strip      the product's own verified reviews, or, until it has some, the foundation's, labelled as theirs
  "Loved by"        the text heading above the photo cards (twin['loved'])
  photo cards       the foundation's testimonial slider: the product in use (twin['moments']; not reviews: no name,
                    stars or "verified")
  problem/solution  apf_copy.problem_solution_html with twin['problem']
  expert            the foundation's dermatologist block: here the brand's own note (twin['note']), no invented expert
  science           apf_copy.kbeauty_html with twin['science']
  image + text x2   the before/after block and "How does it work?" (twin['iwt'])
  results           the stat cards: what to expect, in the same cards (twin['results'])
  compare           "Why skinofab?" table, the product's rows (twin['compare'])
  inside            the ingredient carousel (twin['inside'])
  video reviews     the foundation's customer clips: where and how it is used, photos or silent clips (twin['cards'])
  FAQ               the foundation's accordion, the product's questions (P.FAQ)
  review wall       the product's own reviews (hidden while there are none) and the honest "no reviews yet" box
  difference        "The skinofab difference" (twin['why'])

ctx (from apply_persona): img(name, size, centering) -> (src, w, h) for brand/<product>/<name>.jpg cropped to size;
media(path, sub, name) -> url; strip_own / strip_brand html; wall html; no_reviews html.
"""
import copy
import html
import re
from bs4 import BeautifulSoup

import apf_copy


def frag(h): return BeautifulSoup(h, 'html.parser')


def esc(s): return html.escape(s, quote=False)


def _set_text(el, text):
    el.clear(); el.append(frag(text))


def loved(sec, c):
    """'Loved by <span class="text-highlight">9,800+</span>' -> c['lead'] + the highlighted c['mark'] (same swash)."""
    s = frag(sec)
    brk = s.select_one('.text-highlight__break')
    hl = brk.select_one('.text-highlight')
    for node in list(brk.contents):
        if node is not hl: node.extract()
    brk.insert(0, c['lead'] + ' ')
    icon = hl.select_one('.text-highlight__icon')
    hl.clear(); hl.append(c['mark'])
    if icon:
        # the design's oval is sized from its width: round one word ("9,800+") it fits the line, round two ("after
        # 45") it grew taller than the line and crossed the one above. Stretched to the words' own box instead
        for svg in icon.select('svg'): svg['preserveAspectRatio'] = 'none'
        hl.append(icon)
        # (an ellipse clears a word's corners at ~1.35x its box; the heading's lines get the room for it)
        brk.append(frag('<style>main .text-highlight-wrapper--circle{line-height:1.32}'
                        'main .text-highlight-wrapper--circle .text-highlight__icon{width:136%;height:136%}'
                        'main .text-highlight-wrapper--circle .text-highlight__icon svg{width:100%;height:100%;transform:translate(-50%,-50%)}'
                        # a phone: the circled words on a line of their own, their oval's top ran into the line above
                        # (stick review 8); the lines get the oval's room
                        '@media(max-width:749px){main .text-highlight-wrapper--circle{line-height:1.6}}</style>'))
    return str(s)


def moments(sec, cards, img):
    """The foundation's testimonial slider as photo cards: image, a short title in the name's place, one line. Stars,
    "verified" and "read more" go: these are not reviews."""
    s = frag(sec)
    root = s.select_one('section.skinofab-testimonials')
    if root and root.get('id') == 'sf-reviews': del root['id']          # the foundation's rating link target
    # the photos at their own 4:3 at every width (a fixed 220 px height made them nearly square at 1024 and cut a
    # face out of the two friends, stick review 6)
    if root: root.insert(0, frag('<style>.skinofab-testimonials .skinofab-testimonials__image:has(img[src*="-960x720-"])'
                                 '{height:auto!important;aspect-ratio:4/3}</style>'))
    slides = s.select('.swiper-slide')
    for k, sl in enumerate(slides):
        if k >= len(cards): sl.decompose(); continue
        name, title, text, alt = cards[k]
        # 960 x 720: a card is 266 px wide on a phone, 798 device pixels at 3x (640 px was short, stick review 5)
        src, w, h = img(name, (960, 720), (0.5, 0.35))
        im = sl.select_one('.skinofab-testimonials__image img')
        im['src'], im['alt'], im['width'], im['height'] = src, alt, str(w), str(h)
        sl.select_one('.skinofab-testimonials__name').string = title
        for sel in ('.skinofab-testimonials__stars', '.skinofab-testimonials__verified', '.skinofab-testimonials__read-more'):
            for el in sl.select(sel): el.decompose()
        p = sl.select_one('.skinofab-testimonials__text p')
        p.string = text
    # on a tablet, 2.2 cards, not 2.5: the half card at the screen's edge cut a face in two (stick review 5); the
    # card that peeks in now shows its first fifth (each photo's own margin, before the face)
    # on a computer, three cards, not four: at 1440 a card was 315 px wide, the stick's wordmark 4 to 6 px tall
    # (stick review 7); the arrows show the fourth
    return (str(s).replace('767: { slidesPerView: 2.5,', '767: { slidesPerView: 2.2,')
            .replace('1000: { slidesPerView: 4', '1000: { slidesPerView: 3'))


# line icons for the twin pages, drawn to say what their line says (the design's icons were the foundation's own: a
# paw-print heart beside "30-day money-back guarantee", a sunrise beside "Brush in the stick", review 6); a line names
# one as its last item, else the design's icon stays
_SVG = {
    'shield': '<path d="M12 3l7 3v5c0 4.6-3 8.4-7 10-4-1.6-7-5.4-7-10V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'brush': '<path d="M7 11a5 5 0 0 1 10 0v1H7z"/><path d="M9.5 12v8h5v-8"/>',
    'drop': '<path d="M12 3.5c3.2 4 5.5 7 5.5 10a5.5 5.5 0 0 1-11 0c0-3 2.3-6 5.5-10z"/>',
    'tones': '<circle cx="8" cy="12" r="4"/><circle cx="16" cy="12" r="4"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'sparkle': '<path d="M12 4l1.8 5.2L19 11l-5.2 1.8L12 18l-1.8-5.2L5 11l5.2-1.8z"/>',
    'stick': '<rect x="9" y="3" width="6" height="18" rx="2"/><path d="M9 8h6"/>',
    'leaf': '<path d="M5 19c0-8 6-13 14-14-1 8-6 14-14 14z"/><path d="M5 19l7-7"/>',
}
def icon_src(name):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#151515" stroke-width="1.6" '
           f'stroke-linecap="round" stroke-linejoin="round">{_SVG[name]}</svg>')
    return 'data:image/svg+xml,' + svg.replace('"', "'").replace('<', '%3C').replace('>', '%3E').replace('#', '%23')


def image_with_text(sec, c, img):
    """One of the design's image + text blocks: the photo, the heading (with its highlighted part), the paragraphs and
    the two icon lines (the foundation's icons kept)."""
    s = frag(sec)
    src, w, h = img(c['img'], (1080, 1080), (0.5, 0.45))
    im = s.select_one('.skinofab-iwt__image img')
    im['src'], im['alt'] = src, c['alt']
    im['width'], im['height'] = str(w), str(h)
    h2 = s.select_one('.skinofab-iwt__heading')
    hl = h2.select_one('.skinofab-iwt__highlight')
    h2.clear(); h2.append(c['lead'] + (' ' if c.get('mark') else ''))
    if c.get('mark'):
        hl = hl or s.new_tag('span', attrs={'class': 'skinofab-iwt__highlight'})
        hl.clear(); hl.append(c['mark']); h2.append(hl)
    _set_text(s.select_one('.skinofab-iwt__text'), ''.join(f'<p>{p}</p>' for p in c['paras']))
    for u, t in zip(s.select('.skinofab-iwt__usp'), c['usps']):
        text, name = (t, None) if isinstance(t, str) else t
        _set_text(u.select_one('.skinofab-iwt__usp-text'), f'<p>{esc(text)}</p>')
        if name and u.find('img'): u.find('img')['src'] = icon_src(name)
    # c['note']: a line under the photo (an AI illustration says so in the page's own text, not only in the picture)
    if c.get('note'):
        box = s.select_one('.skinofab-iwt__image')
        box['class'] = box.get('class', []) + ['sf-has-note']
        box.append(frag(f'<p class="sf-illustration-note">{esc(c["note"])}</p>'))
    return str(s)


def results(sec, c):
    """The stat cards (a grid on a computer, a slider on a phone: both sets)."""
    s = frag(sec)
    s.select_one('.section__heading').string = c['title']
    for group in (s.select('.skinofab-results__grid > .skinofab-results__card'),
                  s.select('.skinofab-results__slider .skinofab-results__card')):
        for card, (big, title, sub) in zip(group, c['cards']):
            card.select_one('.skinofab-results__percentage').string = big
            card.select_one('.skinofab-results__title').string = title
            card.select_one('.skinofab-results__subtitle').string = sub
    return str(s)


def compare(sec, c):
    """'Why skinofab?': SKINOFAB (the logo column) against c['others'], one row per c['rows']."""
    s = frag(sec)
    s.select_one('.section__heading').string = c['title']
    ths = s.select('thead th')
    if len(ths) > 2: ths[2].string = c['others']
    body = s.select_one('tbody')
    rows = body.select('tr')
    tpl = copy.copy(rows[0])
    for r in rows: r.decompose()
    # a row may be (label, True): the other one has it too, ticked in grey (stick review 7: every row crossed out
    # against "your old foundation", a creamy row included)
    yes = ('<svg aria-label="Yes" fill="none" height="20" role="img" viewBox="0 0 20 20" width="20" xmlns="http://www.w3.org/2000/svg">'
           '<circle cx="10" cy="10" fill="#8a8a8a" r="10"></circle><path d="M6 10.4l2.7 2.7L14.2 7.4" stroke="white" '
           'stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>')
    for row in c['rows']:
        label, both = (row, False) if isinstance(row, str) else row
        r = copy.copy(tpl)
        r.select('td')[0].string = label
        if both:
            for td in r.select('td')[2:]:
                icon = td.select_one('.compare-icon')
                if icon: icon.clear(); icon.append(frag(yes))
        body.append(r)
    return str(s)


def inside(sec, c, img):
    """The ingredient carousel: heading, intro and one card per c['cards'] (photo 3:4, name, line)."""
    s = frag(sec)
    s.select_one('.si__heading').string = c['title']
    _set_text(s.select_one('.si__intro'), f'<p>{esc(c["intro"])}</p>')
    track = s.select_one('.si__track')
    cards = track.select('article.si__card')
    tpl = copy.copy(cards[0])
    for a in cards: a.decompose()
    for name, title, text in c['cards']:
        a = copy.copy(tpl)
        src, w, h = img(name, (800, 1067), (0.5, 0.5))
        im = a.select_one('img')
        im['src'], im['alt'], im['width'], im['height'] = src, title, str(w), str(h)
        for attr in ('srcset', 'sizes'):
            if im.has_attr(attr): del im[attr]
        a.select_one('.si__name').string = title
        a.select_one('.si__body').string = text
        track.append(a)
    return str(s)


def faq(sec, items):
    """The foundation's accordion (two columns) with the product's questions, half in each column."""
    s = frag(sec)
    lists = s.select('.accordion__list')
    all_items = s.select('li.accordion__item')
    tpl = copy.copy(next(li for li in all_items if 'accordion__item--first' not in (li.get('class') or [])))
    for li in all_items: li.decompose()
    half = (len(items) + 1) // 2 if len(lists) > 1 else len(items)
    for k, (q, a) in enumerate(items):
        li = copy.copy(tpl)
        li['id'] = f'Accordion--sfp_{k}'
        if k == 0: li['class'] = (li.get('class') or []) + ['accordion__item--first']
        li.select_one('[data-collapsible-trigger]')['aria-controls'] = f'Accordions-item--sfp{k}'
        li.select_one('[data-collapsible-container]')['id'] = f'Accordions-item--sfp{k}'
        li.select_one('.accordion__item__title__text').string = q
        _set_text(li.select_one('[data-collapsible-content]'), f'<p>{a}</p>')
        (lists[0] if k < half or len(lists) == 1 else lists[1]).append(li)
    return str(s)


def why(sec, c, img):
    """'The skinofab difference': the photo (a background), three features, the button to the buy box."""
    s = frag(sec)
    src, _, _ = img(c['img'], (1500, 1500), (0.5, 0.3))
    box = s.select_one('.skinofab-why__image')
    box['style'] = re.sub(r'url\("[^"]*"\)', f'url("{src}")', box.get('style', ''))
    s.select_one('.section__heading').string = c['title']
    for f, (title, desc, *name) in zip(s.select('.skinofab-why__feature'), c['features']):
        f.select_one('.skinofab-why__feature-title').string = title
        f.select_one('.skinofab-why__feature-icon img')['alt'] = ''      # decorative: the title says it
        if name: f.select_one('.skinofab-why__feature-icon img')['src'] = icon_src(name[0])
        _set_text(f.select_one('.skinofab-why__feature-desc'), f'<p>{esc(desc)}</p>')
    a = s.select_one('.skinofab-why__cta a')
    a.string, a['href'] = c['button'], '#apf-buy'
    return str(s)


def sections(found_main, P, ctx):
    """The finished foundation page's <main> children after its buy box, each one rebuilt for P, in order."""
    t, img = P.TWIN, ctx['img']
    out, seen_iwt = [], 0
    wrap = lambda sid, h: f'<div class="shopify-section" id="shopify-section-{sid}">{h}</div>'
    for sec in found_main:
        sid = sec.get('id') or ''
        raw = str(sec)
        if sid.endswith('__main') or 'section_custom_html' in sid:
            continue
        if sid == 'shopify-section-sf-review-strip':
            strip = ctx['strip_own'] or ctx['strip_brand']
            if strip: out.append(wrap('sf-review-strip', strip))
        elif '__section_text_' in sid:
            out.append(loved(raw, t['loved']))
        elif '__kopstorm_testomonials_' in sid:
            out.append(moments(raw, t['moments'], img))
        elif sid == 'shopify-section-sf-problem-solution':
            c = t['problem']
            out.append(wrap('sf-problem-solution', apf_copy.problem_solution_html(
                img(c['img_problem'], (1000, 1250), (0.5, 0.42)), img(c['img_solution'], (1000, 1250), (0.5, 0.5)), c=c)))
        elif sid == 'shopify-section-sf-kbeauty':
            # the product's note ("Why we made it") first, where the foundation's page once had its dermatologist
            n = dict(t['note'])
            # 1000 px wide: a phone at 3x shows it about 1074 px wide (800 was enlarged 1.34x, stick review 4)
            n['photo'] = img(n['photo'], (1000, 1250), (0.5, 0.4))
            n['avatar'] = ctx['avatar']
            out.append(wrap('sf-note', apf_copy.dermatologist_html(n)))
            k = t['science']
            out.append(wrap('sf-kbeauty', apf_copy.kbeauty_html(img(k['img'], (930, 1162), (0.5, 0.45)), k=k)))
        elif '__section_image_with_text_' in sid:
            out.append(image_with_text(raw, t['iwt'][seen_iwt], img)); seen_iwt += 1
        elif '__kopstorm_results_' in sid:
            out.append(results(raw, t['results']))
        elif '__kopstorm_compare_' in sid:
            out.append(compare(raw, t['compare']))
        elif '__kopstorm_ingredients_' in sid:
            out.append(inside(raw, t['inside'], img))
        elif sid == 'shopify-section-sf-korea':
            continue                                    # the foundation's own (its bottle in the photo)
        elif sid == 'shopify-section-sf-reviews':
            c = t['cards']
            if not c: continue                          # no clips or photos of the product in use yet
            items = []
            for it in c['items']:
                d = {'title': it['title'], 'text': it['text'], 'alt': it['alt'], 'name': ''}
                if it.get('video'): d['video'] = ctx['clip'](it['video'])
                else: d['photo'] = img(it['img'], (720, 900), it.get('focus', (0.5, 0.4)))
                items.append(d)
            out.append(wrap('sf-reviews', apf_copy.pdp_reviews_html(esc(c['eyebrow']), esc(c['title']), items, plain=True)))
        elif '__section_accordions_' in sid:
            out.append(faq(raw, P.FAQ['items']))
        elif sid == 'shopify-section-sf-review-wall':
            out.append(wrap('sf-review-wall', ctx['wall']))
            if ctx['no_reviews']: out.append(wrap(f'sf-{P.KEY}-no-reviews', ctx['no_reviews']))
        elif '__kopstorm_why_' in sid:
            out.append(why(raw, t['why'], img))
        else:
            out.append(raw)                 # the design's empty app block keeps its spacing
    return out
