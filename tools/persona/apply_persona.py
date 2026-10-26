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
- puts the foundation's photos on pure white like the other products' (WHITE, white_backdrops(), white_bg.py): grey
  studio walls and sweeps go white, the two black gallery panels become ink on white
"""
import hashlib, html, json, os, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apf_copy, balm_copy, brush_copy, ccf_copy, company, relabel_bottles, serum_copy, support_copy, twin, white_bg
SECOND_PRODUCTS = (brush_copy, balm_copy, serum_copy)

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

def section_image(src, name, size=(1000, 1250), white=False, shadow=False):
    """A 4:5 crop of a brand image for the problem / solution sections, under a content-hashed name. white: on pure
    white like every product image (white_bg.matte; shadow: a contact shadow under a bottle that stands on the
    floor); not for a close-up the product fills (the label detail), which has no backdrop."""
    from PIL import Image, ImageOps
    im = Image.open(src).convert('RGB')
    if white: im = white_bg.matte(im, shadow=shadow)
    im = ImageOps.fit(im, size, Image.LANCZOS, centering=(0.5, 0.42))
    tmp = DST / 'assets' / 'img' / f'{name}.jpg'
    im.save(tmp, quality=85, optimize=True, progressive=True)
    final = tmp.with_name(f"{name}-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.jpg")
    tmp.rename(final)
    return '../assets/img/' + final.name, size[0], size[1]

def problem_solution():
    return apf_copy.problem_solution_html(
        section_image(BRAND / 'persona' / 'age-73.jpg', 'skinofab-problem-skin-after-45', white=True),
        section_image(BRAND / 'adaptive-peptide-foundation' / '03-three-quarter-right.png', 'skinofab-solution-bottle', white=True, shadow=True))

def crop_to(src_path, name, size, centering, white=False):
    """A crop of an export image at `size`, under a content-hashed name (NEXT's CDN caches by file name); white: its
    pale backdrop made pure white first (white_bg.light, a no-op on a scene)."""
    from PIL import Image, ImageOps
    import numpy as np
    im = Image.open(src_path).convert('RGB')
    im = white_bg.light(im) if white else im
    # a drawing on white whose sides the crop would cut (the brush's how-to diagrams: their labels run to the edges):
    # the whole width, the height cropped or padded with white instead
    W, H = im.size
    dx = int(round((W - H * size[0] / size[1]) / 2))
    a = np.asarray(im.convert('L'))
    if dx > 0 and np.median(a[:, :4]) > 248 and np.median(a[:, -4:]) > 248 and (a[:, :dx].min() < 200 or a[:, W - dx:].min() < 200):
        k = size[0] / W
        fitted = im.resize((size[0], round(H * k)), Image.LANCZOS)
        canvas = Image.new('RGB', size, (255, 255, 255))
        canvas.paste(fitted, (0, int((size[1] - fitted.height) * centering[1])))
        im = canvas
    else:
        im = ImageOps.fit(im, size, Image.LANCZOS, centering=centering)
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

# The homepage's expert section quoted a dermatologist, a real doctor, with the product's and the brand's names put into
# her words by the rebrand: an endorsement she never gave SKINOFAB. In its place, in the same layout, a verified buyer
# of the foundation in her own words (the imported reviews, tools/reviews/import_reviews.py), her photo in the tab
# and three verified buyers' photos (photos-approved.txt) where the doctor's portrait was.
CUSTOMER_VOICE = {
    'heading': 'In our customers’ words',
    'name': 'Maria R.', 'role': 'Verified buyer, 56',
    'paragraphs': ['I love how the texture and feel is not greasy or heavy. At 56, I also am happy it doesn’t cake or '
                   'settle in fine lines.',
                   'I do love the product, it’s my skin but better, more coverage than a tinted moisturizer but not '
                   'oily or too dewy feeling like many of them.'],
    'avatar': 'OOv6J0c2A-0', 'photos': ['OOv6J0c2A-0', '2E8YCdyRL-0', 'OGPUmf6ae-0'],   # Maria R., Kelly G., Linda M.
}

def customer_voice(home):
    """CUSTOMER_VOICE in the homepage's expert section. Returns the page."""
    from PIL import Image, ImageOps
    m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+__experts"', home)
    if not m: return home
    end = home.find('</section>', m.start())
    sec = home[m.start():end]
    cv, photos = CUSTOMER_VOICE, REVIEWS / 'photos'
    av = ImageOps.fit(Image.open(photos / f"{cv['avatar']}.jpg").convert('RGB'), (190, 190), Image.LANCZOS, centering=(0.5, 0.3))
    tmp = WORK / 'customer-avatar.jpg'; av.save(tmp, quality=88)
    avatar = hashed_copy(tmp, 'img', 'skinofab-customer-avatar-190w')[3:]
    tiles = [ImageOps.fit(Image.open(photos / f'{p}.jpg').convert('RGB'), (295, 500), Image.LANCZOS, centering=(0.5, 0.35))
             for p in cv['photos']]
    strip = Image.new('RGB', (295 * 3 + 16, 500), (255, 255, 255))
    for i, t in enumerate(tiles): strip.paste(t, (i * 303, 0))
    tmp = WORK / 'customer-strip.jpg'; strip.save(tmp, quality=88, optimize=True, progressive=True)
    photo = hashed_copy(tmp, 'img', 'skinofab-customer-photos-901w')[3:]
    sec = re.sub(r'<h2>.*?</h2>', f"<h2>{cv['heading']}</h2>", sec, count=1, flags=re.S)
    sec = re.sub(r'(<div aria-label=")[^"]*(" class="fh-expert-tabs")', lambda mm: mm.group(1) + cv['heading'] + mm.group(2), sec, count=1)
    sec = re.sub(r'(role="tab"[^>]*>\s*<picture[^>]*>)<img[^>]*>',
                 lambda mm: mm.group(1) + f'<img alt="{cv["name"]}" class="fh-original" height="190" loading="lazy" sizes="47px" '
                                          f'src="{avatar}" width="190"/>', sec, count=1)
    sec = re.sub(r'<span class="fh-expert-secondary">.*?</span>', '', sec, flags=re.S)   # the doctor's two colleagues
    paras = ''.join(f'<p>{html.escape(p)}</p>' for p in cv['paragraphs'])
    sec = re.sub(r'<div class="fh-expert-copy">.*?</div>',
                 f'<div class="fh-expert-copy">{paras}<h3>{cv["name"]}</h3><p class="fh-expert-role">{cv["role"]}</p></div>',
                 sec, count=1, flags=re.S)
    sec = re.sub(r'(<picture class="fh-expert-photo">)<img[^>]*>',
                 lambda mm: mm.group(1) + f'<img alt="Three verified buyers of the Adaptive Peptide Foundation" class="fh-original" '
                                          f'height="500" loading="lazy" sizes="(max-width: 749px) 93vw, 698px" src="{photo}" width="901"/>',
                 sec, count=1)
    # the doctor's portrait filled a tall box (the section's whole height on desktops, 214 px on phones), cover-cropped:
    # the three buyers' photos would be cut through their faces. The strip keeps its own shape, centred beside the words
    X = '[id$="__experts"] .fh-experts'
    sec += (f'<style>{X} .fh-expert-photo{{height:auto;aspect-ratio:901/500}}'
            f'{X} .fh-expert-photo img{{position:absolute;inset:0;left:0;width:100%;height:100%;object-fit:cover}}'
            f'@media(min-width:750px){{{X}{{min-height:440px}}{X} .fh-expert-photo{{top:50%;bottom:auto;transform:translateY(-50%)}}}}</style>')
    return home[:m.start()] + sec + home[end:]

ROOT = Path(__file__).resolve().parents[2]
VIDEO_SWAPS = Path(__file__).resolve().parent / 'queue' / 'video-swaps.json'   # {export media file: Genjutsu re-make}

def demo_override(i):
    """Card i's replacement clip (ccf_copy.VIDEO_DEMO_CLIPS) and its poster, a frame of it at the card's 720 x 1280
    (made once, cached in WORK/clips), or None."""
    if i not in ccf_copy.VIDEO_DEMO_CLIPS: return None
    from PIL import Image, ImageOps
    rel, t = ccf_copy.VIDEO_DEMO_CLIPS[i]
    clip = ROOT / rel
    poster = WORK / 'clips' / f'{hashlib.md5(clip.read_bytes()).hexdigest()[:12]}-poster-{t}.jpg'
    if not poster.exists():
        poster.parent.mkdir(parents=True, exist_ok=True)
        png = poster.with_suffix('.png')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t), '-i', str(clip), '-frames:v', '1', str(png)], check=True)
        ImageOps.fit(Image.open(png).convert('RGB'), (720, 1280), Image.LANCZOS).save(poster, quality=88, optimize=True, progressive=True)
        png.unlink()
    return clip, poster

def video_reviews(home):
    """The homepage's video cards (their clips and posters, ccf_copy.VIDEO_DEMOS' captions) as a product page section:
    illustrative videos of the foundation on skin, labelled as such, the real reviews right after them."""
    sec = home_section(home, 'reviews')
    if not sec: return None
    out = []
    for i, (a, (title, text)) in enumerate(zip(re.findall(r'<article class="fh-review">(.*?)</article>', sec, re.S), ccf_copy.VIDEO_DEMOS)):
        clip = re.search(r'<video[^>]*data-src="(assets/media/[^"]+\.mp4)"', a)
        poster = re.search(r'<img[^>]*class="fh-social-poster"[^>]*src="(assets/img/[^"]+)"|<img[^>]*src="(assets/img/[^"]+)"[^>]*class="fh-social-poster"', a)
        if not clip or not poster: continue
        # the clip as the store shows it: its Genjutsu re-make when it has one (the export's own shows the old brand's
        # bottle; apf_pages.swap_videos points the pages at the re-make only after this script has run), or the card's
        # replacement clip
        src, swaps = DST / clip.group(1), json.loads(VIDEO_SWAPS.read_text()) if VIDEO_SWAPS.exists() else {}
        if src.name in swaps: src = ROOT / swaps[src.name]
        override = demo_override(i)
        if override: src = override[0]
        mp4 = webm = None
        if src.exists():                       # a re-make not made yet: the page keeps the export's file, which
            stem = 'skinofab-demo-' + hashlib.md5(src.read_bytes()).hexdigest()[:6]     # swap_videos then reports
            mp4, webm = card_clip(src, stem, 'mp4'), card_clip(src, stem, 'webm')
        still = hashed_copy(override[1], 'img', 'skinofab-demo-poster') if override else '../' + (poster.group(1) or poster.group(2))
        out.append({'title': html.escape(title), 'text': html.escape(text), 'alt': html.escape(title),
                    'video': (mp4 or '../' + clip.group(1), still) + ((webm,) if webm else ())})
    return apf_copy.pdp_reviews_html('On skin', 'See how it blends', out, plain=True,
                                     note=html.escape(ccf_copy.VIDEO_DEMO_NOTE)) if out else None

def honest_video_cards():
    """The homepage's video cards: VIDEO_DEMOS' captions and label in place of the names, stars and "Verified buyer"
    of people who are not buyers; the section's heading says what the cards are. Returns the cards changed."""
    home = DST / 'index.html'
    t = home.read_text(encoding='utf-8', errors='surrogateescape')
    m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+__reviews"', t)
    if not m: return 0
    end = t.find('</section>', m.start())
    sec = t[m.start():end]
    arts = list(re.finditer(r'<article class="fh-review">.*?</article>', sec, re.S))
    out, last, n = [], 0, 0
    for i, (a, (title, text)) in enumerate(zip(arts, ccf_copy.VIDEO_DEMOS)):
        art = a.group(0)
        override = demo_override(i)
        if override:          # the card's replacement clip, and a frame of it as its poster
            clip = hashed_copy(override[0], 'media', 'skinofab-demo-clip')[3:]
            still = hashed_copy(override[1], 'img', 'skinofab-demo-poster')[3:]
            art, k = re.subn(r'(<video[^>]*data-src=")assets/media/[^"]+\.mp4"', lambda mm: mm.group(1) + clip + '"', art, count=1)
            art, j = re.subn(r'(<img[^>]*class="fh-social-poster"[^>]*?)src="[^"]*" srcset="[^"]*"',
                             lambda mm: mm.group(1) + f'src="{still}" srcset="{still} 720w"', art, count=1)
            if not (k and j): missing.append(('video card clip', title))
        art = re.sub(r'(<div class="fh-review-card">)<img alt="" height="20"[^>]*>', r'\1', art, count=1)      # the stars
        art = re.sub(r'<h3>.*?</h3><p>.*?</p>', f'<h3>{html.escape(title)}</h3><p>{html.escape(text)}</p>', art, count=1, flags=re.S)
        art = re.sub(r'<div class="fh-review-name">.*?</div>', f'<div class="fh-review-name"><span>{html.escape(ccf_copy.VIDEO_DEMO_LABEL)}</span></div>',
                     art, count=1, flags=re.S)
        art = re.sub(r'aria-label="[^"]*"', lambda _: f'aria-label="Illustrative video: {html.escape(title)}"', art)
        art = re.sub(r'(<img alt=")[^"]*(" class="fh-social-poster")', lambda mm: mm.group(1) + html.escape(title) + mm.group(2), art)
        out.append(sec[last:a.start()] + art); last = a.end(); n += 1
    sec = ''.join(out) + sec[last:]
    sec = re.sub(r'<h2>Trusted by 9,800\+ verified buyers who finally found something that works</h2>', '<h2>See how it blends</h2>', sec, count=1)
    # its eyebrow (stars and "Over 7,700 5-star reviews") made the illustrative videos under it read as reviews
    sec = re.sub(r'<div class="fh-eyebrow"><img alt="" height="16" src="[^"]*" width="80"/><span>Over [\d,]+ 5-star reviews</span></div>',
                 '<div class="fh-eyebrow"><span>On skin</span></div>', sec, count=1)
    home.write_text(t[:m.start()] + sec + t[end:], encoding='utf-8', errors='surrogateescape')
    return n

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
    summary = {'count': d['count'], 'average': d['average'], 'distribution': d['distribution']}
    if d.get('note'): summary['note'] = d['note']        # where the imported reviews come from (import_reviews.py --note)
    return {'ship': ship, 'summary': summary,
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

def face_crop(src, focus, aspect=4 / 3, width=640):
    """A review photo cropped to the card's landscape shape with the face (at `focus`, 0 top to 1 bottom of the
    photo) a little above the middle, so a portrait selfie is not cut through the head."""
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    w, h = im.size
    ch = min(h, round(w / aspect))
    top = max(0, min(h - ch, round(focus * h - ch * 0.46)))
    return im.crop((0, top, w, top + ch)).resize((width, round(width / aspect)), Image.LANCZOS)

PLAYFAIR = Path(__file__).resolve().parents[1] / 'theme-build' / 'static' / 'fonts' / 'playfairdisplay_v40_nuFiD-vYSZviVYUb_rj3ij__anPXDTzYgA.woff2'

def drop_sold_badge(im):
    """The foundation's main photo carried a "1m+ Sold" badge (a lavender disc) that no sales record backs: the disc
    is found by its color in the upper right and painted out of the plain backdrop around it."""
    import cv2, numpy as np
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    h, w = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    blue = (b - r > 45) & (b - g > 30) & (b > 150)
    blue[:int(h * 0.2)] = False; blue[int(h * 0.6):] = False; blue[:, :int(w * 0.6)] = False
    ys, xs = np.nonzero(blue)
    if len(ys) < 20: return None
    cy, cx = ys.mean(), xs.mean()
    rad = max(np.percentile(np.hypot(ys - cy, xs - cx), 99) * 1.12, 3)
    yy, xx = np.mgrid[:h, :w]
    mask = (np.hypot(yy - cy, xx - cx) <= rad).astype(np.uint8) * 255
    out = cv2.inpaint(np.asarray(im.convert('RGB')), mask, max(3, int(rad * 0.4)), cv2.INPAINT_TELEA)
    from PIL import Image
    return Image.fromarray(out)

def loved_by_count(count):
    """The gallery's before/after board was headed "Loved by 300.000+": the number becomes the real review total
    (floored to the hundred), set in the same Playfair Display Bold, size and baseline, followed by the original
    lavender "+". Run on the largest copy; honest_images scales the result to the other widths."""
    label = f'{(int(count) // 100) * 100:,}'
    def fix(im):
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        im = im.convert('RGB'); orig = im.copy(); a = np.asarray(im).astype(np.int16)
        h, w = a.shape[:2]
        band = slice(0, int(h * 0.25))
        dark = a[band].mean(2) < 90
        lav = (a[band][..., 2] - a[band][..., 0] > 45) & (a[band][..., 2] > 150)
        rows = np.nonzero(dark.any(1))[0]
        if not len(rows) or not lav.any(): return None
        cols = np.nonzero(dark.any(0))[0]
        # words: dark column runs split by gaps wider than ~1.5% of the width
        words, start, prev = [], cols[0], cols[0]
        for c in cols[1:]:
            if c - prev > max(2, w * 0.015): words.append((start, prev)); start = c
            prev = c
        words.append((start, prev))
        if len(words) < 3: return None
        (l0, l1), (n0, _) = words[0], words[2]                  # "Loved" and the number
        lrows = np.nonzero(dark[:, l0:l1 + 1].any(1))[0]
        base = lrows.max() + 1                                   # "Loved" has no descender: its bottom is the baseline
        ly, lx = np.nonzero(lav)
        gap = lx.min() - words[-1][1]
        ink = tuple(int(v) for v in np.median(a[band][dark], axis=0))
        bg = tuple(int(v) for v in np.median(a[band][~dark & ~lav].reshape(-1, 3), axis=0))
        def font(size):
            f = ImageFont.truetype(str(PLAYFAIR), size); f.set_variation_by_name('Bold'); return f
        f = font(100)
        size = max(6, round(100 * (l1 - l0 + 1) / (f.getbbox('Loved')[2] - f.getbbox('Loved')[0])))
        f = font(size)
        top, bottom = max(0, rows.min() - int(h * 0.01)), min(h, rows.max() + int(h * 0.012))
        d = ImageDraw.Draw(im)
        # the original "+" (heavier than the font's), moved to follow the new number at its old distance
        pad = max(1, int(w * 0.004))
        box = (lx.min() - pad, ly.min() + band.start - pad, lx.max() + 1 + pad, ly.max() + band.start + 1 + pad)
        plus = orig.crop(box)
        d.rectangle((n0 - 1, top, min(w, box[2] + int(w * 0.01)), bottom), fill=bg)
        d.text((n0 - f.getbbox(label, anchor='ls')[0], base), label, font=f, fill=ink, anchor='ls')
        end = n0 + f.getbbox(label, anchor='ls')[2] - f.getbbox(label, anchor='ls')[0]
        im.paste(plus, (end + gap - pad, box[1]))
        return im
    return fix

def honest_images(summary):
    """Numbers drawn into gallery images, fixed in the pixels (apply_persona runs this after the persona swap):
    the main photo's "1m+ Sold" badge goes; "Loved by 300.000+" shows the real review total. Every width of each
    image is fixed, saved under a new content-hashed name, and every reference is rewritten. Returns the count."""
    from PIL import Image
    fixes = [('KoreanColorChangingFoundation-Productimages_1_cee537ea-54c2-', drop_sold_badge)]
    if summary: fixes.append(('ColorChangingFoundation-Productimagesphotos_4_35e0c406-0a8b-', loved_by_count(summary['count'])))
    renames = {}
    for prefix, fixer in fixes:
        files = [f for f in sorted((DST / 'assets' / 'img').glob(prefix + '*')) if not re.search(r'-f[0-9a-f]{6}$', f.stem)]
        # the persona copies (-p<hash>) and the export's originals are different photos: one master for each
        for group in ([f for f in files if re.search(r'-p[0-9a-f]{6}$', f.stem)], [f for f in files if not re.search(r'-p[0-9a-f]{6}$', f.stem)]):
            if not group: continue
            sized = [(f, Image.open(f).size) for f in group]
            master_f, msize = max(sized, key=lambda x: x[1][0] * x[1][1])
            master = fixer(Image.open(master_f))
            if master is None: continue
            for src, size in sized:
                if abs(size[0] / size[1] - msize[0] / msize[1]) > 0.01: continue
                out = master if size == msize else master.resize(size, Image.LANCZOS)
                if src.suffix.lower() == '.png' and Image.open(src).mode in ('RGBA', 'LA', 'P'): out = out.convert('RGBA')
                stem = re.sub(r'-p?[0-9a-f]{6}$', '', src.stem)
                tmp = src.with_name(stem + '-fix' + src.suffix)
                out.save(tmp, **({'quality': 88, 'optimize': True, 'progressive': True} if src.suffix.lower() in ('.jpg', '.jpeg') else {'optimize': True}))
                new = f"{stem}-f{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}{src.suffix}"
                tmp.rename(tmp.with_name(new)); renames[src.name] = new
    if renames:
        rx = re.compile('|'.join(re.escape(k) for k in sorted(renames, key=len, reverse=True)))
        for p in DST.rglob('*'):
            if p.is_file() and p.suffix.lower() in TEXT:
                t = p.read_text(encoding='utf-8', errors='surrogateescape')
                n = rx.sub(lambda m: renames[m.group(0)], t)
                if n != t: p.write_text(n, encoding='utf-8', errors='surrogateescape')
    return len(renames)

# the foundation's photos on one pure white, like the other products' (white_bg.py): by file-name prefix, how
WHITE = [
    ('KoreanColorChangingFoundation-Productimages_1_', 'flood'),     # the packshot on a grey sweep: its floor shadow kept
    ('2_221c6006', 'matte'), ('21_7a5d845a', 'matte'), ('22_ed20463f', 'matte'),   # the 45+ women with the bottle,
    ('24_e2816f7f', 'matte'), ('25_2e1854df', 'matte'), ('HIDDEN_1', 'matte'),      # silver hair on a grey wall
    ('ColorChangingFoundation-Productimagesphotos_4_35e0c406', 'light'),            # "Loved by", on off-white
    ('6_d0973846', 'light'), ('7_ba7831f0', 'light'),                                # What's inside, The Science
    ('ColorChangingFoundation-Productimagesphotos_1_87f31fb4', 'light'), ('new_iamges', 'light'),
    ('2_babe5169', 'matte'),                                            # The skinofab difference
    ('ColorChangingFoundation-Productimagesphotos_412bfd2c', 'ink'),   # "Adapts To Your Skin": white on black
    ('8_87ca3242', 'board'),                                            # "skinofab vs. others": white on black
]
# kept as shot: the daylight before/after (a real room) and the close-ups with no backdrop


def ink_panel(im):
    """A gallery panel of white type on black beside a photo: the type turns to ink on white (the same letters,
    inverted), the photo's grey wall to white (white_bg.matte)."""
    import numpy as np
    from PIL import Image
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    h, w = a.shape[:2]
    col = a[: h // 2].mean((0, 2))                             # the photo starts where 20 columns in a row are light
    x = next((i for i in range(w - 20) if col[i:i + 20].min() > 120), w)   # (the type's columns are mostly black)
    # black -> white, white type -> the gallery's ink; the black's JPEG ringing (up to ~24) goes white, not a halo
    left = 255 - np.clip((a[:, :x] - 24) / 227, 0, 1) * (255 - 21)
    seam = max(2, w // 300)                                     # the photo's first columns are a blend with the black
    right = np.asarray(white_bg.matte(im.convert('RGB').crop((x + seam, 0, w, h)))).astype(np.float32)
    pad = np.full((h, seam, 3), 255, np.float32)
    return Image.fromarray(np.clip(np.concatenate([left, pad, right], 1) + 0.5, 0, 255).astype(np.uint8))


def white_backdrops():
    """Every page's copy of the foundation's photos in WHITE, and every homepage product card's image, made white by
    its own pixels (each width is a separate file), saved under a new content-hashed name, every reference rewritten. The black "vs. others" board
    becomes brand/adaptive-peptide-foundation/vs-others.jpg (product_photos.py foundation). Results are cached by
    the input's hash in <work_dir>/white-cache. Returns the number of files replaced."""
    from PIL import Image
    img_dir, cache = DST / 'assets' / 'img', WORK / 'white-cache'
    cache.mkdir(exist_ok=True)
    texts = {p: p.read_text(encoding='utf-8', errors='surrogateescape') for p in DST.rglob('*')
             if p.is_file() and p.suffix.lower() in TEXT}
    used = set()
    for t in texts.values():
        used.update(re.findall(r'([A-Za-z0-9_.\-]+\.(?:jpg|jpeg|png|webp))', t))
    # the homepage's product cards (shelf, Essentials, Bundle & Save): packshots on a flat pale grey
    home = texts.get(DST / 'index.html', '')
    cards = {n for art in re.findall(r'<article class="fh-product">(.*?)</article>', home, re.S)
             for n in re.findall(r'assets/img/([^" ,]+\.(?:jpg|jpeg|png|webp))', art)}
    board = BRAND / 'adaptive-peptide-foundation' / 'vs-others.jpg'
    make = {'flood': white_bg.flood, 'matte': white_bg.matte, 'light': white_bg.light, 'ink': ink_panel,
            'card': lambda im: white_bg.matte(im, flat=True),
            'board': lambda im: Image.open(board).convert('RGB').resize(im.size, Image.LANCZOS)}
    import inspect
    salt = hashlib.md5(Path(white_bg.__file__).read_bytes() + inspect.getsource(ink_panel).encode()).digest()  # code changes: recompute
    renames = {}
    for name in sorted(used):
        src = img_dir / name
        mode = next((m for prefix, m in WHITE if name.startswith(prefix)), 'card' if name in cards else None)
        if not mode or not src.is_file() or re.search(r'-w[0-9a-f]{6}$', src.stem): continue
        data = src.read_bytes()
        if mode == 'card':
            import numpy as np
            level = white_bg.backdrop_level(np.asarray(Image.open(src).convert('RGB')).astype(np.float32))
            if level is not None and level >= 254: continue          # already white (the second products' cards)
        key = cache / f"{hashlib.md5(salt + data + mode.encode() + (board.read_bytes() if mode == 'board' else b'')).hexdigest()}{src.suffix}"
        if not key.exists():
            im = Image.open(src)
            out = make[mode](im.convert('RGB'))
            if im.mode in ('RGBA', 'LA', 'P') and src.suffix.lower() == '.png':
                out = out.convert('RGBA'); out.putalpha(im.convert('RGBA').getchannel('A'))
            out.save(key, **({'quality': 88, 'optimize': True, 'progressive': True} if src.suffix.lower() in ('.jpg', '.jpeg') else {'optimize': True}))
        stem = re.sub(r'-[pf]?[0-9a-f]{6}$', '', src.stem)
        new = f"{stem}-w{hashlib.md5(key.read_bytes()).hexdigest()[:6]}{src.suffix}"
        shutil.copyfile(key, img_dir / new); renames[name] = new
    if renames:
        rx = re.compile('|'.join(re.escape(k) for k in sorted(renames, key=len, reverse=True)))
        for p, t in texts.items():
            n = rx.sub(lambda m: renames[m.group(0)], t)
            if n != t: p.write_text(n, encoding='utf-8', errors='surrogateescape')
    return len(renames)

def relabel_bottles_on_pages():
    """SKINOFAB's real wordmark on every foundation bottle in the pages' photos (relabel_bottles.SITE: the old,
    stand-in wordmark found, erased and replaced), after white_backdrops: each photo's copies get new content-hashed
    names (-l<hash>) and every reference is rewritten. Cached in <work_dir>/relabel-cache. Returns the files replaced."""
    img_dir = DST / 'assets' / 'img'
    texts = {p: p.read_text(encoding='utf-8', errors='surrogateescape') for p in DST.rglob('*')
             if p.is_file() and p.suffix.lower() in TEXT}
    used = set()
    for t in texts.values():
        used.update(re.findall(r'([A-Za-z0-9_.\-]+\.(?:jpg|jpeg|png|webp))', t))
    renames = relabel_bottles.site(img_dir, used, WORK / 'relabel-cache')
    if renames:
        rx = re.compile('|'.join(re.escape(k) for k in sorted(renames, key=len, reverse=True)))
        for p, t in texts.items():
            n = rx.sub(lambda m: renames[m.group(0)], t)
            if n != t: p.write_text(n, encoding='utf-8', errors='surrogateescape')
    return len(renames)

def even_card(im, size, height=0.70, width=0.80, bottom=0.86):
    """A product card on white with the product at one scale: its outline (everything not white, its soft shadow
    aside) fitted to height of the card (or width, if it is wide), centred, its base at bottom, so every card in the
    shelf shows its product the same size, in the same place, under the badges."""
    import numpy as np
    from PIL import Image
    im = im.convert('RGB')
    a = np.asarray(im).astype(np.int16)
    ys, xs = np.nonzero(a.min(2) < 225)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    k = min(height * size / (y1 - y0), width * size / (x1 - x0))
    dx = np.nonzero(a.min(2) < 160)[1]                    # centred on the product itself, not its shadow beside it
    cx = (dx.min() + dx.max() + 1) / 2 if len(dx) else (x0 + x1) / 2
    big = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    out = Image.new('RGB', (size, size), (255, 255, 255))
    out.paste(big, (round(size / 2 - cx * k), round(bottom * size - y1 * k)))
    return out

SHELF_HANDLES = ['color-changing-foundation'] + [P.HANDLE for P in (brush_copy, balm_copy, serum_copy)]

def even_shelf():
    """The homepage shelf's cards of our four products, each product the same size and in the same place (even_card):
    the foundation's from brand/home/card-foundation.jpg, the others' card.jpg. Every card of theirs in the shelf
    (the list and its tabs) gets the same 720 and 1080 px copies. Returns the cards changed."""
    from PIL import Image
    home = DST / 'index.html'
    t = home.read_text(encoding='utf-8', errors='surrogateescape')
    m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+__bestsellers"', t)
    if not m: return 0
    end = t.find('</section>', m.start())
    sec = t[m.start():end]
    arts = list(re.finditer(r'<article class="fh-product">.*?</article>', sec, re.S))
    def of(a): return next((h for h in SHELF_HANDLES if f'products/{h}.html"' in a.group(0)), None)
    first = next((a for a in arts if of(a) == SHELF_HANDLES[0] and 'fh-upload' in a.group(0)), None)
    # the foundation: one bottle from its front render, PDRN legible, a soft contact shadow (home_images.py)
    src = {SHELF_HANDLES[0]: HOME / 'card-foundation.jpg'} if first else {}
    src.update({P.HANDLE: P.IMG / 'card.jpg' for P in (brush_copy, balm_copy, serum_copy)})
    made = {}
    for h, path in src.items():
        im = Image.open(path)
        for size in (720, 1080):
            tmp = DST / 'assets' / 'img' / f'skinofab-shelf-{h}-{size}w.jpg'
            even_card(im, size).save(tmp, quality=88, optimize=True, progressive=True)
            final = tmp.with_name(f"{tmp.stem}-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.jpg"); tmp.rename(final)
            made[h, size] = 'assets/img/' + final.name
    out, last, n = [], 0, 0
    for a in arts:
        h = of(a)
        if not h or (h, 720) not in made: continue
        art = a.group(0)
        small, big = made[h, 720], made[h, 1080]
        def img(mm):
            tag = mm.group(0)
            rich = 'fh-upload' in tag
            tag = re.sub(r' src="[^"]*"', f' src="{big if rich else small}"', tag)
            tag = re.sub(r' srcset="[^"]*"', f' srcset="{small} 720w, {big} 1080w"' if rich else f' srcset="{small} 720w"', tag)
            tag = re.sub(r' width="\d+"', f' width="{1080 if rich else 720}"', tag)
            return re.sub(r' height="\d+"', f' height="{1080 if rich else 720}"', tag)
        art = re.sub(r'<img [^>]*>', img, art, count=1)
        if h == SHELF_HANDLES[0]:
            # the export's badge said "Save 33%" (its old prices); the card shows $59 -> $37 (with refills): 37%
            pk = apf_copy.PACK1
            save = round(100 * (1 - float(pk['refill']) / float(pk['compare'])))
            art = re.sub(r'(<span class="fh-saving">)Save \d+%(</span>)', lambda mm: f'{mm.group(1)}Save {save}%{mm.group(2)}', art)
        out.append(sec[last:a.start()] + art); last = a.end(); n += 1
    sec = ''.join(out) + sec[last:]
    home.write_text(t[:m.start()] + sec + t[end:], encoding='utf-8', errors='surrogateescape')
    return n

# the store sells four products; every other one the design carried is gone from the pages (and from NEXT:
# prune_catalog.py), and so are the pages that sold only those
OUR_PRODUCTS = {'color-changing-foundation'} | {P.HANDLE for P in SECOND_PRODUCTS}
LEGACY_PAGES = {'aging-brows', 'aging-brows2', 'facemask', 'srm01', 'srm01-2026-10-11-02-01-51-pm', 'page',
                'fuller-lips-without-fillers-copy-copy', 'fullerbutnatural', 'plumper-quiz', 'shadequiz',
                'lip-stain-restock-sign-up', 'top5stains', 'bundle-builder', 'skinofab-how-to-use',
                'complete-your-order'}    # an old checkout funnel: a brow gel add-on and an invented review count
# the design's collections that held only the other products (the store's categories that are empty now), and the
# ones left with one or two of ours (Accessories: the brush; Sale and B2G5: the foundation), which the menus drop too
EMPTY_COLLECTIONS = {'brows', 'bundles', 'canal-products', 'homepage-lips', 'lashes', 'lips', 'lipstain', 'serums',
                     'essentials', 'sale', 'b2g5'}
# FAQ answers about the other products (the contact page's General questions were all about lip plumpers)
LEGACY_WORDS = re.compile(r'lip plumper|plumping gloss|lip stain|lip gloss|lip liner|\bbrows?\b|eyebrow|\blash(?:es)?\b|eyelash|'
                          r'mascara|lifting mask|under-eye (?:patches|reset)|reverse-time|gua sha|face roller', re.I)
# the brand's own words that named the other products
LEGACY_TEXT = [
    ('What started with a single lip gloss formula quickly evolved into a full-range beauty brand, from luscious lip '
     'plumpers to advanced brow serums.',
     'What started with a single formula grew into a focused line for skin after 45: an adaptive peptide foundation, a '
     'PDRN plumping balm, an EGF + NAD+ firming serum and a lymphatic brush.'),
    ('<p>From lip plumpers to brow serums — results you can see and feel.</p>',
     '<p>From an adaptive foundation to a firming serum — results you can see and feel.</p>'),
    ('A movement towards embracing your unique beauty — one lip plumper at a time.',
     'A movement towards embracing your unique beauty — one ritual at a time.'),
    ('From a single lip gloss in a tiny kitchen lab to a full-range beauty house — built on heart, not hype.',
     'From a tiny kitchen lab to a skincare-first line for skin after 45 — built on heart, not hype.'),
    ('high-impact formulas, on-trend shades and products designed to become everyday favourites — from complexion to lips, '
     'brows and beyond.', 'high-impact formulas designed to become everyday favourites, starting with an adaptive peptide '
     'foundation for skin after 45.'),
    ('<p><strong>Beauty Tools &amp; Accessories</strong><br/>The finishing touch to every beauty routine. Smart, easy-to-use '
     'tools and accessories designed', '<p><strong>Beauty Tools</strong><br/>The finishing touch to every beauty routine. '
     'Smart, easy-to-use tools, like our lymphatic brush, designed'),
    ('While our products, including lip plumpers and other cosmetic items, have been used',
     'While our products, including our foundation and skincare, have been used'),
]
# the homepage sections dropped for showing only the other products
HOME_DROP = ()                 # none: home_original() gives those sections our products
STRUCTURAL = {'[document]', 'html', 'body', 'main', 'section', 'header', 'footer', 'nav', 'template', 'form', 'details'}

def resolve(href, page=''):
    """href as an export path (a bare "essentials.html" on collections/face.html is collections/essentials.html)."""
    h = (href or '').split('#')[0].split('?')[0]
    if page and h and not h.startswith(('/', 'http:', 'https:', '#', 'mailto:', 'tel:', 'javascript:', 'data:')):
        import posixpath
        h = posixpath.normpath(posixpath.join(posixpath.dirname(page), h))
    return h

def gone(href, page=''):
    """True when href points at something the store no longer has: another product, a page that sold only those, or
    a collection that held only those. page: the export path of the page the link is on."""
    h = resolve(href, page)
    m = re.search(r'(?:^|/)products/([a-z0-9][a-z0-9-]*?)(?:\.html|\.js)?$', h)
    if m: return m.group(1) not in OUR_PRODUCTS
    m = re.search(r'(?:^|/)pages/([a-z0-9][a-z0-9-]*?)(?:\.html)?$', h)
    if m: return m.group(1) in LEGACY_PAGES
    m = re.search(r'(?:^|/)collections/([a-z0-9][a-z0-9-]*?)(?:\.html)?$', h)
    if m: return m.group(1) in EMPTY_COLLECTIONS
    return False

def keeps(el, page=''):
    """el links to one of our products."""
    return any(re.search(r'(?:^|/)products/(?:%s)(?:\.html)?$' % '|'.join(map(re.escape, OUR_PRODUCTS)), resolve(a['href'], page))
               for a in el.find_all('a', href=True))

def strip_gone(soup, page=''):
    """Every card, menu item, slide or tile that links only to something gone is removed: the largest element around
    the link that holds no link to our products and no prose of its own. A link inside prose is unwrapped (its words
    stay). Returns the number of changes."""
    n = 0
    for a in list(soup.find_all('a', href=lambda h: gone(h, page))):
        if a.parent is None or not gone(a.get('href'), page): continue   # already removed with an earlier card
        node, own = a, len(a.get_text(' ', strip=True))
        while node.parent is not None and node.parent.name not in STRUCTURAL:
            p = node.parent
            if keeps(p, page) or len(p.get_text(' ', strip=True)) > max(500, 4 * own + 300): break
            node = p
        if node is a and a.parent is not None and len(a.parent.get_text(' ', strip=True)) > own + 40:
            a.unwrap()
        else:
            node.decompose()
        n += 1
    return n

# "The SKINOFAB phenomenon": the export's eight cards showed women in their twenties and thirties and products the store
# does not sell (under-eye patches, lip gloss, pink tubes). Each card is now a woman over 45 with one of our four
# products, linked to it: (source, crop centre across the photo, product handle, alt). The cards are 260 x 400.
PHENOMENON = [
    ('persona:2_9c7e1c85-81c7-4ffb-8ccb-a246f8658467_800x800-d920b1.jpg', .42, 'color-changing-foundation',
     'A woman in her fifties taking a selfie with the Adaptive Peptide Foundation'),
    ('serum:mirror.jpg', .5, serum_copy.HANDLE, 'A woman applying the EGF + NAD+ Firming Serum at her bathroom mirror'),
    ('balm:bag.jpg', .5, balm_copy.HANDLE, 'The PDRN Plumping Balm going into a handbag'),
    ('home:phenomenon-4.jpg', .5, 'color-changing-foundation',             # home_images.py: the real bottle on it
     'A woman holding the Adaptive Peptide Foundation'),
    ('serum:hold-cheek.jpg', .3, serum_copy.HANDLE, 'A woman holding the EGF + NAD+ Firming Serum by her cheek'),
    ('balm:apply-lips.jpg', .45, balm_copy.HANDLE, 'A woman pressing the PDRN Plumping Balm on her lips'),
    ('home:phenomenon-7.jpg', .5, 'color-changing-foundation',             # her face and the bottle both in the card
     'A woman with short grey hair holding the Adaptive Peptide Foundation'),
    ('home:source/brush-ai.jpg', .38, brush_copy.HANDLE, 'A woman sweeping The Lymphatic Brush over her cheek'),
]

def home_phenomenon():
    """PHENOMENON in the homepage's carousel, in place of its cards (photos and videos). Returns the cards written."""
    from PIL import Image
    home = DST / 'index.html'
    t = home.read_text(encoding='utf-8', errors='surrogateescape')
    m = re.search(r'<div class="fh-social-track"[^>]*>', t)
    if not m: return 0
    end = balanced_end(t, m.start(), 'div')
    roots = {'persona': IMAGES, 'serum': serum_copy.IMG, 'balm': balm_copy.IMG,
             'home': Path(__file__).resolve().parents[2] / 'brand' / 'home'}
    cards = []
    for i, (src, cx, handle, alt) in enumerate(PHENOMENON, 1):
        root, name = src.split(':', 1)
        im = Image.open(roots[root] / name).convert('RGB')
        cw = round(min(im.height * 13 / 20, im.width))
        x0 = round((im.width - cw) * cx)
        im = im.crop((x0, 0, x0 + cw, im.height))
        if im.height > 1000: im = im.resize((650, 1000), Image.LANCZOS)
        tmp = WORK / f'phenomenon-{i}.jpg'; im.save(tmp, quality=86, optimize=True, progressive=True)
        url = hashed_copy(tmp, 'img', f'skinofab-phenomenon-{i}')[3:]
        cards.append(f'<div class="fh-social-card"><a href="products/{handle}.html"><img alt="{html.escape(alt)}" '
                     f'height="{im.height}" loading="lazy" sizes="260px" src="{url}" width="{im.width}"/></a></div>')
    t = t[:m.end()] + ''.join(cards) + t[end - len('</div>'):]
    home.write_text(t, encoding='utf-8', errors='surrogateescape')
    return len(cards)

def support_pages():
    """support_copy's FAQ answers, contact-page answers, refund policy and shipping policy in place of the export's.
    Returns what changed; a question or a page it expected and did not find is reported as missing."""
    from bs4 import BeautifulSoup
    done, gone = {}, []
    norm = lambda s: re.sub(r'\s+', ' ', s).strip().lower()
    for rel, items, q_sel, a_sel, item_sel in (
            ('pages/faq.html', support_copy.FAQ, '.faq-question span', '.faq-answer-inner', '.faq-item'),
            ('pages/contact.html', support_copy.CONTACT, '.accordion__item__title__text', '.accordion__item__text', '.accordion__item')):
        f = DST / rel
        soup = BeautifulSoup(f.read_text(encoding='utf-8', errors='surrogateescape'), 'html.parser')
        found = soup.select(item_sel)
        n = 0
        for start, q, a in items:
            hits = [it for it in found if it.select_one(q_sel) and norm(it.select_one(q_sel).get_text()).startswith(norm(start))]
            if not hits: gone.append((rel, start)); continue
            for it in hits:
                if a is None: it.decompose(); n += 1; continue
                if q: it.select_one(q_sel).string = q
                box = it.select_one(a_sel)
                box.clear(); box.append(BeautifulSoup(a, 'html.parser')); n += 1
        f.write_text(str(soup), encoding='utf-8', errors='surrogateescape'); done[rel] = n
    for rel, body in (('policies/refund-policy.html', support_copy.REFUND), ('policies/shipping-policy.html', support_copy.SHIPPING)):
        f = DST / rel
        t = f.read_text(encoding='utf-8', errors='surrogateescape')
        m = re.search(r'<div class="shopify-policy__body">\s*<div class="rte">', t)
        if not m: gone.append((rel, 'policy body')); continue
        end = balanced_end(t, m.end() - len('<div class="rte">'), 'div')
        t = t[:m.end()] + body + '</div>' + t[end:]
        f.write_text(t, encoding='utf-8', errors='surrogateescape'); done[rel] = 1
    return done, gone

# image descriptions that still named the old store's products, or were a file name
OLD_PRODUCT_ALT = re.compile(r'eyelash|lash serum|brow serum|lip stain|lip gloss|lip plumper|lip liner|mascara|under-eye patch|'
                             r'lifting mask|reverse.time|stick (?:&|and) stain|blender brush', re.I)

def clean_alts():
    """Every page's alt texts: "Color Changing Foundation" (the product's old name) becomes the Adaptive Peptide
    Foundation, "| Skinofab" suffixes go, an alt that names a product the store does not sell or is a file name is
    emptied (the images left with one are decorative: the persona photos have their own). Returns alts changed."""
    n = 0
    def fix(m):
        nonlocal n
        a = html.unescape(m.group(1))
        b = a.replace('Color Changing Foundation', 'Adaptive Peptide Foundation').replace(' | Skinofab', '')
        if OLD_PRODUCT_ALT.search(b) or re.search(r'\.(?:png|jpe?g|webp|gif)$|_-_|[0-9a-f]{8}-[0-9a-f]{4}', b, re.I): b = ''
        if b == a: return m.group(0)
        n += 1
        return 'alt="' + html.escape(b) + '"'
    for f in DST.rglob('*.html'):
        t = f.read_text(encoding='utf-8', errors='surrogateescape')
        u = re.sub(r'alt="([^"]*)"', fix, t)
        if u != t: f.write_text(u, encoding='utf-8', errors='surrogateescape')
    return n

def drop_dead_social():
    """The footer's Instagram, TikTok and Facebook icons and the contact page's "Follow along" links all pointed to #:
    the store has no social accounts set up yet. They go until it does. Returns pages changed."""
    n = 0
    for f in DST.rglob('*.html'):
        t = f.read_text(encoding='utf-8', errors='surrogateescape')
        u = t
        for rx in (r'<div class="social-sharing-wrapper">', r'<div class="cs-info__item">\s*<div class="cs-info__label">Follow along</div>'):
            while True:
                m = re.search(rx, u)
                if not m: break
                seg = u[m.start():balanced_end(u, m.start(), 'div')]
                if re.search(r'href="(?!#")[^"]+"', seg): break          # a real link: leave the block
                u = u[:m.start()] + u[m.start() + len(seg):]
        if u != t: f.write_text(u, encoding='utf-8', errors='surrogateescape'); n += 1
    return n

def home_features():
    """Two homepage stories the design gave to products the store no longer sells, given to ours: the Reverse-time
    serum's video story becomes the EGF + NAD+ Firming Serum's (a photo of it in use), the lifting mask's "New
    arrivals" banner becomes the PDRN Plumping Balm's. Returns the stories changed."""
    from PIL import Image
    home = DST / 'index.html'
    t = home.read_text(encoding='utf-8', errors='surrogateescape')
    done = 0
    def section(key):
        m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+%s"' % key, t)
        return (m.start(), t.find('</section>', m.start())) if m else (None, None)
    a, b = section('__serum')
    if a is not None:
        sec = t[a:b]
        img = hashed_copy(serum_copy_img('drop'), 'img', 'skinofab-home-serum-1080w', (1080, 1080))[3:]
        sec = re.sub(r'<div class="fh-story-media" data-fh-editorial-video=""( style="[^"]*")?>.*?</div>\s*</div>',
                     lambda m: f'<div class="fh-story-media"{m.group(1) or ""}><img alt="A woman in her sixties applying the EGF + NAD+ Firming Serum" '
                     f'class="fh-social-poster" height="1080" loading="lazy" sizes="(max-width: 749px) calc(100vw - 32px), 760px" '
                     f'src="{img}" style="width:100%;height:100%;object-fit:cover;object-position:50% 30%" width="1080"/></div>', sec, count=1, flags=re.S)
        sec = re.sub(r'<div class="fh-story-copy">.*?</a></div>',
                     '<div class="fh-story-copy"><div class="fh-eyebrow"><span>EGF + NAD+ Firming Serum</span></div>'
                     '<h2>Firmer-looking skin, face and neck</h2><div class="fh-story-body">'
                     '<p>EGF, NAD+ and collagen in a light serum that sinks in within a minute. Two drops for your face, two for '
                     'your neck, morning and night.</p><p>Skin looks smoother, firmer and more radiant with daily use, and it '
                     'layers under your foundation without pilling.</p></div>'
                     f'<a class="fh-button" href="products/{serum_copy.HANDLE}.html">Learn more</a></div>', sec, count=1, flags=re.S)
        t = t[:a] + sec + t[b:]; done += 1
    a, b = section('__arrivals_desktop')
    if a is not None:
        sec = t[a:b]
        # the banner: her photo widened to a landscape (home_images.py, balm-wide.jpg) at the right edge, and on the
        # left, behind the copy, its own studio background carried on row by row, so no edge of the photo shows
        import numpy as np
        W, H = 3360, 1013
        wide = Image.open(HOME / 'balm-wide.jpg').convert('RGB')
        wide = np.asarray(wide.resize((round(wide.width * H / wide.height), H), Image.LANCZOS)).astype(np.float32)
        x0 = W - wide.shape[1]
        edge, y = wide[:, :24].mean(1), np.arange(H)                         # the photo's left edge, each row, as
        edge = np.stack([np.polyval(np.polyfit(y, edge[:, c], 2), y) for c in range(3)], 1)   # a smooth gradient
        field = np.repeat(edge[:, None, :], W, 1)
        ramp = np.clip(np.arange(wide.shape[1]) / 240, 0, 1)[None, :, None]  # 240 px into the photo, its own pixels
        field[:, x0:] = field[:, x0:] * (1 - ramp) + wide * ramp
        field += np.random.default_rng(3).normal(0, 0.8, field.shape)       # a grain, so the gradient never bands
        ban = Image.fromarray(np.clip(field + 0.5, 0, 255).astype(np.uint8))
        tmp = WORK / 'home-balm-banner.jpg'; ban.save(tmp, quality=88, optimize=True, progressive=True)
        big = hashed_copy(tmp, 'img', 'skinofab-home-balm-3360w')[3:]
        small = hashed_copy(tmp, 'img', 'skinofab-home-balm-1680w', (1680, 1680))[3:]
        # under 1200 px the copy and the photo no longer share a wide banner: there it is the photo of her alone
        eye_src = hashed_copy(balm_copy_img('apply-eye'), 'img', 'skinofab-home-balm-eye-1080w')[3:]
        sec = re.sub(r'<img alt="" class="fh-original"[^>]*/>',
                     lambda m: f'<source height="1080" media="(max-width: 1199px)" sizes="(max-width: 1023px) 100vw, 50vw" '
                     f'srcset="{eye_src} 1080w" width="1080">' + m.group(0), sec, count=1)
        sec = re.sub(r'<img alt="" class="fh-original"[^>]*/>',
                     f'<img alt="A woman in her sixties pressing the PDRN Plumping Balm under her eye" class="fh-original" '
                     f'height="1013" loading="lazy" sizes="(max-width: 749px) 269vw, 1680px" src="{big}" '
                     f'srcset="{small} 1680w, {big} 3360w" width="3360"/>', sec, count=1)
        sec = re.sub(r'<div class="fh-story-copy">.*?</a></div>',
                     '<div class="fh-story-copy"><div class="fh-eyebrow"><span>New arrival</span></div>'
                     '<h2>Rested-looking eyes in 10 seconds</h2><div class="fh-story-body">'
                     '<p>The PDRN Plumping Balm puts PDRN, Volufiline™, collagen and hyaluronic acid in a stick you press on '
                     'under your eyes, on smile lines and around your lips.</p><p>No fingers, no mess, over or under makeup: '
                     'skin looks smoother, fuller and more rested.</p></div>'
                     f'<a class="fh-button" href="products/{balm_copy.HANDLE}.html">Shop now</a></div>', sec, count=1, flags=re.S)
        t = t[:a] + sec + t[b:]; done += 1
    home.write_text(t, encoding='utf-8', errors='surrogateescape')
    return done

HOME = BRAND / 'home'          # the homepage's photos in its original design (tools/persona/home_images.py)
# Bundle & Save: each product's best-value bundle, priced as on its page's picker (its copy module's bundles)
HOME_BUNDLES = [
    ('color-changing-foundation', 'Foundation Duo', 'bundle-foundation', 'Two bottles of the Adaptive Peptide Foundation',
     f"Two bottles of your one adaptive shade, with {ccf_copy.REFILL['every']}-day refills (cancel anytime), or "
     f"${float(ccf_copy.PACKS[1]['price']):g} once.", None, None),
    (serum_copy.HANDLE, 'Firming Serum Trio', 'bundle-serum', 'Three bottles of the EGF + NAD+ Firming Serum',
     'Buy 2, get 1 free: about six months, morning and night.', None, None),
    (balm_copy.HANDLE, 'Plumping Balm Trio', 'bundle-balm', 'Three PDRN Plumping Balm sticks',
     'Buy 2, get 1 free: one for home, one for your bag, one to share.', None, None),
    (brush_copy.HANDLE, 'Lymphatic Brush Trio', 'bundle-brush', 'Three Lymphatic Brushes',
     'Buy 2, get 1 free, each with its travel case.', None, None),
]
HOME_TILES = [('color-changing-foundation', 'Foundation', 'tile-foundation', 'A woman in her fifties holding the Adaptive Peptide Foundation'),
              (serum_copy.HANDLE, 'Serum', 'tile-serum', 'A woman in her sixties holding the EGF + NAD+ Firming Serum'),
              (balm_copy.HANDLE, 'Balm', 'tile-balm', 'A woman in her fifties holding the PDRN Plumping Balm to her cheek'),
              (brush_copy.HANDLE, 'Brush', 'tile-brush', 'A woman in her sixties sweeping the Lymphatic Brush along her cheekbone')]
HOME_ESSENTIALS = [('color-changing-foundation', apf_copy.PRODUCT, BRAND / 'adaptive-peptide-foundation' / 'next' / '01-front.jpg'),
                   (serum_copy.HANDLE, serum_copy.TITLE, serum_copy.IMG / 'card.jpg'),
                   (balm_copy.HANDLE, balm_copy.TITLE, balm_copy.IMG / 'card.jpg'),
                   (brush_copy.HANDLE, brush_copy.TITLE, brush_copy.IMG / 'card.jpg')]

def home_original():
    """The homepage in its original design (the export's sections, in their order and look), with our products where it
    showed the old ones: Shop by category shows our four, each in the hands of a woman over 45; Bundle & Save each
    product's best-value bundle; Essentials our four; the banner, "One shade" and "Korean formulas" keep their
    models with the real bottle in hand (brand/home/, home_images.py). No section is dropped. Returns what changed."""
    home = DST / 'index.html'
    t = home.read_text(encoding='utf-8', errors='surrogateescape')
    done = {}
    def style(sec, css):
        return re.subn(r'</style>', css + '</style>', sec, count=1)
    def section(key):
        m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+%s"' % key, t)
        return (m.start(), t.find('</section>', m.start())) if m else (None, None)
    def img(name, widths, sub='img'):
        """Content-hashed copies of brand/home/<name> at each width: (src of the widest, srcset)."""
        path = HOME / name
        from PIL import Image
        W = Image.open(path).size[0]
        out = [(w, hashed_copy(path, sub, f'skinofab-home-{path.stem}-{w}w', (w, 10 ** 5) if w < W else None)[3:]) for w in widths]
        return out[-1][1], ', '.join(f'{u} {w}w' for w, u in out)
    def bundle_offer(handle, price, compare):
        if price: return price, compare
        if handle == 'color-changing-foundation':                          # as its page shows it first: refills ticked
            return ccf_copy.PACKS[1]['refill'], ccf_copy.PACKS[1]['compare']
        P = next(P for P in SECOND_PRODUCTS if P.HANDLE == handle)
        b = P.BUNDLES[-1]
        return b['price'], b['compare']
    usd = lambda v: f"${float(v):.2f}".replace('.00', '') + ' USD'
    # ---- Shop by category
    a, b = section('__categories')
    if a is not None:
        sec = t[a:b]
        tiles = []
        for handle, name, file, alt in HOME_TILES:
            src, srcset = img(f'{file}.jpg', (400, 800))
            tiles.append(f'<a class="fh-category" href="products/{handle}.html"> <picture class=""><img alt="{alt}" class="fh-original" '
                         f'height="1000" loading="lazy" sizes="(max-width: 749px) 93vw, 300px" src="{src}" srcset="{srcset}" width="800"/>'
                         f' </picture> <div><h3>{name}</h3><span class="fh-button fh-button--white">Shop now</span></div></a>')
        m = re.search(r'(<div class="fh-category-grid"[^>]*>)', sec)
        end = balanced_end(sec, m.start(), 'div')
        sec = sec[:m.end()] + ''.join(tiles) + '</div>' + sec[end:]
        # each tile is its photo, whole at 4:5 (the export's fixed heights cut the product out of a narrow tile), with
        # the name and the button under it: the export set them in white on the photo, over a dark gradient across
        # its lower 60%, on the product the woman holds. Two to a row under 1024 px from 750 px
        X = '[id$="__categories"]'
        sec, _ = style(sec, (f'{X} .fh-category{{height:auto;overflow:visible;border-radius:0;display:flex;flex-direction:column;gap:14px;text-decoration:none}}'
                             f'{X} .fh-category:after{{display:none}}'
                             f'{X} .fh-category picture{{position:relative;inset:auto;display:block;aspect-ratio:4/5;border-radius:var(--fh-radius);overflow:hidden}}'
                             f'{X} .fh-category img{{width:100%;height:100%;object-fit:cover;object-position:50% 20%}}'
                             f'{X} .fh-category>div{{position:static;flex-direction:row;align-items:center;justify-content:space-between;gap:12px;padding:0 2px}}'
                             f'{X} .fh-category h3{{color:#151515;font-size:26px}}'
                             f'{X} .fh-category .fh-button--white{{background:#151515;color:#fff !important;border-color:#151515}}'   # the export: #151515 !important
                             f'@media(min-width:750px) and (max-width:1023px){{{X} .fh-category-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}'
                             # four equal columns: the export's 1fr tracks grew to their name-and-button row, so at 1024 the
                             # tiles came out 223 to 291 px wide and the last ran off the screen. Under 1280 px a quarter is
                             # too narrow for the name and the button side by side: the button goes under the name
                             f'@media(min-width:1024px){{{X} .fh-category-grid{{grid-template-columns:repeat(var(--fh-columns),minmax(0,1fr))}}}}'
                             f'@media(min-width:1024px) and (max-width:1279px){{{X} .fh-category>div{{flex-direction:column;align-items:stretch;gap:10px}}'
                             f'{X} .fh-category .fh-button{{width:100%}}}}'))
        t = t[:a] + sec + t[b:]; done['categories'] = len(tiles)
    t = t.replace('alt="Woman applying Skinofab Color Changing Foundation"', 'alt="A woman in her fifties holding the Adaptive Peptide Foundation"')
    # ---- Bundle & Save and Essentials: the shelf's card markup, our products in it
    def cards(key, items):
        nonlocal t
        a, b = section(key)
        if a is None: return 0
        sec = t[a:b]
        m = re.search(r'(<div class="fh-product-list"[^>]*>)', sec)
        end = balanced_end(sec, m.start(), 'div')
        sec = sec[:m.end()] + ''.join(items) + '</div>' + sec[end:]
        t = t[:a] + sec + t[b:]
        return len(items)
    items = []
    for handle, title, file, alt, line, price, compare in HOME_BUNDLES:
        price, compare = bundle_offer(handle, price, compare)
        save = round(100 * (1 - float(price) / float(compare)))
        src, srcset = img(f'{file}.jpg', (500, 1000))
        # data-sf-fixed-price: the bundle's own price (its NEXT variant), as its page's picker shows it, not the product's
        items.append(f'<article class="fh-product"> <a aria-label="{title}" class="fh-product-image" href="products/{handle}.html"> '
                     f'<picture class=""><img alt="{alt}" class="fh-original" height="1000" loading="lazy" sizes="(max-width: 749px) 66vw, 300px" '
                     f'src="{src}" srcset="{srcset}" width="1000"/> </picture> <span class="fh-badges"><span class="fh-saving">Save {save}%</span></span></a> '
                     f'<div class="fh-product-info"><h3><a href="products/{handle}.html">{title}</a></h3><p class="fh-product-description">{line}</p> '
                     f'<div class="fh-price" data-sf-fixed-price=""><s>{usd(compare)}</s><span>{usd(price)}</span></div></div> </article>')
    done['bundles'] = cards('__bundles', items)
    items = []
    for handle, title, path in HOME_ESSENTIALS:
        src = hashed_copy(path, 'img', f'skinofab-home-essential-{handle}-720w', (720, 720))[3:]
        P = next((P for P in SECOND_PRODUCTS if P.HANDLE == handle), None)
        price = P.PRICE if P else apf_copy.PACK1['price']                       # NEXT binds it
        # its was-price as its bestseller card and its page show it (the foundation's: foundation_price below)
        was = f'<s>{usd(P.COMPARE)}</s>' if P and float(P.COMPARE) > float(P.PRICE) else ''
        items.append(f'<article class="fh-product"> <a aria-label="{title}" class="fh-product-image" href="products/{handle}.html"> '
                     f'<picture class=""><img alt="{title}" class="fh-original" height="720" loading="lazy" sizes="(max-width: 749px) 66vw, 300px" '
                     f'src="{src}" width="720"/> </picture> <span class="fh-badges"></span></a> <div class="fh-product-info"><h3>'
                     f'<a href="products/{handle}.html">{title}</a></h3> <div class="fh-price">{was}<span>{usd(price)}</span></div></div> </article>')
    done['essentials'] = cards('__essentials', items)
    # The foundation's cards show its price as its page shows it first (Automatic Refills ticked, the default):
    # 1 bottle $37, was $59. NEXT's own price for it is the one-time $47, which the page shows when refills are off;
    # a card saying $47 above a page saying $37 read as two prices for one bottle.
    # The card says so: "with 28-day refills" under the price (the page's own terms say the rest)
    one = ccf_copy.PACKS[0]
    fixed = (f'<div class="fh-price" data-sf-fixed-price=""><s>{usd(one["compare"])}</s><span>{usd(one["refill"])}</span></div>'
             f'<p class="sf-refill-note" style="margin:2px 0 0;font-size:12px;line-height:16px;color:#5a5a5a">with '
             f'{ccf_copy.REFILL["every"]}-day refills, cancel anytime</p>')
    def foundation_price(m):
        art = m.group(0)
        if 'products/color-changing-foundation.html' not in art: return art
        return re.sub(r'<div class="fh-price"[^>]*>.*?</div>', lambda _: fixed, art, count=1, flags=re.S)
    n_fp = 0
    for key in ('__bestsellers', '__essentials'):
        a, b = section(key)
        if a is None: continue
        sec, k = re.subn(r'<article class="fh-product">.*?</article>', foundation_price, t[a:b], flags=re.S)
        t = t[:a] + sec + t[b:]; n_fp += sec.count('data-sf-fixed-price')
    done['foundation card prices'] = n_fp
    # The three editorial cards below were drawn at fixed heights (One shade 445 px, 818 px on a phone; Celebration
    # 386 / 603 px; Korean formulas 461 / 957 px) with their photos placed at fixed offsets: copy a line longer than
    # the export's, or a screen narrower than its two widths, pushed the button under the photo or out of the card,
    # and a photo shorter than its card showed its cut edge. Each card now grows with its copy at every width: on
    # phones (and on tablets for Korean formulas) the photo sits under the copy in the flow; on wider screens it fills
    # the card's height beside the copy, never under it, its inner edge faded into the card.
    # ---- "One shade": the model (about 57) with the real bottle at her temple; on phones keyed, the card behind her
    a, b = section('__foundation')
    if a is not None:
        sec = t[a:b]
        mob = hashed_copy(HOME / 'oneshade-mobile.webp', 'img', 'skinofab-home-oneshade-mobile-860w')[3:]
        desk = hashed_copy(HOME / 'oneshade-desktop.jpg', 'img', 'skinofab-home-oneshade-desktop-1024w')[3:]
        # under 1200 px the keyed portrait, whole: the wide photo, cropped to a tablet's or a small laptop's box, cut the
        # top of her head (under a fade, 768 px) or her far eye (under the fade into the copy, 1024 px; review 3)
        sec, k1 = re.subn(r'<source height="1182" media="\(max-width: 749px\)" sizes="85vw" srcset="[^"]*" width="660"/?>',
                          f'<source height="1130" media="(max-width: 1199px)" sizes="(max-width: 749px) 100vw, 60vw" srcset="{mob} 860w" '
                          f'type="image/webp" width="860">', sec, count=1)
        sec, k2 = re.subn(r'<img alt="[^"]*" class="fh-original" height="1825"[^>]*>',
                          f'<img alt="A woman in her fifties holding the Adaptive Peptide Foundation to her temple" class="fh-original" height="780" '
                          f'loading="lazy" sizes="880px" src="{desk}" srcset="{desk} 1024w" width="1024"/>', sec, count=1)
        X = '[id$="__foundation"] .fh-editorial--foundation'
        sec, k3 = style(sec, (
            # 1024 px and up: the photo beside the copy; the card is as tall as the copy, or as the photo at its own
            # shape across the width the copy leaves (container units: the card's width)
            f'@media(min-width:1024px){{{X}{{container-type:inline-size;height:auto;min-height:var(--fh-story-height)}}'
            f'{X} .fh-story-copy{{height:auto;padding:40px 0;min-height:max(var(--fh-story-height),calc((100cqw - min(var(--fh-story-width),42cqw) - 64px) / 1.31))}}'
            f'{X} .fh-story-media{{right:calc(min(var(--fh-story-width),42%) + 64px);width:auto}}'
            f'{X} .fh-story-media picture{{position:absolute;inset:0;width:100%;height:100%}}'
            f'{X} .fh-story-media .fh-original{{position:absolute;inset:0;width:100%;height:100%;transform:none;object-fit:cover;object-position:0 35%;'
            f'-webkit-mask-image:linear-gradient(to right,#000 94%,transparent);mask-image:linear-gradient(to right,#000 94%,transparent)}}}}'
            # under 1024 px: the copy, then the photo under it across the card
            f'@media(max-width:1023px){{{X}{{height:auto;min-height:0;display:flex;flex-direction:column}}'
            f'{X} .fh-story-copy{{order:1;height:auto;min-height:0;width:100%;margin:0;padding:32px 32px 8px}}'
            f'{X} .fh-story-media{{position:relative;order:2;inset:auto;top:auto;left:auto;right:auto;bottom:auto;width:100%;aspect-ratio:1024/780}}'
            f'{X} .fh-story-media picture{{position:absolute;inset:0;top:0;left:0;width:100%;height:100%}}'
            f'{X} .fh-story-media .fh-original{{position:absolute;inset:0;top:0;left:0;width:100%;height:100%;transform:none;object-fit:cover;'
            f'-webkit-mask-image:linear-gradient(to bottom,transparent,#000 12%);mask-image:linear-gradient(to bottom,transparent,#000 12%)}}}}'
            f'@media(max-width:749px){{{X} .fh-story-copy{{padding:32px 16px 8px}}{X} .fh-story-media{{aspect-ratio:860/1130}}'
            f'{X} .fh-story-media .fh-original{{object-fit:contain;-webkit-mask-image:none;mask-image:none}}}}'
            # tablets and small laptops: the keyed portrait whole, standing on the card's lower edge (no fade, no crop)
            f'@media(min-width:750px) and (max-width:1023px){{{X} .fh-story-media{{aspect-ratio:4/3}}}}'
            f'@media(min-width:750px) and (max-width:1199px){{{X} .fh-story-media .fh-original{{object-fit:contain;object-position:50% 100%;'
            f'-webkit-mask-image:none;mask-image:none}}}}'))
        t = t[:a] + sec + t[b:]; done['one shade'] = k1 + k2 + k3
    # ---- Korean formulas: one complete photo (her neck and shoulder whole, so no cut edge), the real bottle in hand
    a, b = section('__formulas')
    if a is not None:
        sec = t[a:b]
        src, srcset = img('formulas.jpg', (1200, 1600, 2400, 3344))
        sec, k1 = re.subn(r'<source height="1662" media="\(max-width: 749px\)" sizes="110vw" srcset="[^"]*" width="940"/?>',
                          f'<source height="1882" media="(max-width: 749px)" sizes="150vw" srcset="{srcset}" width="3344">', sec, count=1)
        sec, k2 = re.subn(r'<img alt="[^"]*" class="fh-original" height="939"[^>]*>',
                          f'<img alt="A woman pressing the Adaptive Peptide Foundation to her forehead, a stripe of it on her cheek" class="fh-original" '
                          f'height="1882" loading="lazy" sizes="(max-width: 1023px) 100vw, (max-width: 1439px) 90vw, 1300px" src="{src}" '
                          f'srcset="{srcset}" width="3344"/>', sec, count=1)   # from 1024 px it covers a box ~0.9 screens wide
        X = '[id$="__formulas"]'
        sec, k3 = style(sec, (
            f'@media(min-width:1024px){{{X} .fh-formula-photo{{left:0;top:0;bottom:0;width:58%;height:auto;'
            f'-webkit-mask-image:linear-gradient(to right,#000 72%,transparent 97%);mask-image:linear-gradient(to right,#000 72%,transparent 97%)}}'
            f'{X} .fh-formula-photo .fh-original{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:0 40%}}}}'
            f'@media(max-width:1023px){{{X} .fh-formula{{flex-direction:column;justify-content:flex-start;min-height:0;padding:32px 24px 0;gap:24px;margin:0}}'
            f'{X} .fh-formula-copy{{width:100%}}'
            f'{X} .fh-formula-photo{{position:relative;left:auto;top:auto;bottom:auto;width:auto;height:auto;margin:0 -24px;aspect-ratio:16/9;overflow:hidden;'
            f'-webkit-mask-image:linear-gradient(to bottom,transparent,#000 14%);mask-image:linear-gradient(to bottom,transparent,#000 14%)}}'
            f'{X} .fh-formula-photo .fh-original{{position:absolute;inset:0;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:20% 40%}}}}'
            f'@media(max-width:749px){{{X} .fh-formula{{padding:32px 16px 0}}{X} .fh-formula-photo{{margin:0 -16px;aspect-ratio:6/5}}}}'))
        t = t[:a] + sec + t[b:]; done['formulas'] = k1 + k2 + k3
    # ---- Beauty is a celebration: the two models as women in their fifties; the card the photo's own grey
    a, b = section('__celebration_desktop')
    if a is not None:
        sec = t[a:b]
        src, srcset = img('celebration.jpg', (800, 1536))
        sec, k1 = re.subn(r'<source height="701" media="\(max-width: 749px\)"[^>]*>', '', sec, count=1)
        sec, k2 = re.subn(r'<img alt="[^"]*" class="fh-original" height="941"[^>]*>',
                          f'<img alt="Two women in their fifties, cheek to cheek" class="fh-original" height="1024" loading="lazy" '
                          f'sizes="(max-width: 1023px) 100vw, 900px" src="{src}" srcset="{srcset}" width="1536"/>', sec, count=1)
        X = '[id$="__celebration_desktop"] .fh-editorial--celebration'
        sec, k3 = style(sec, (
            f'{X}{{background:#f6f6f6;height:auto;min-height:var(--fh-story-height)}}'
            f'@media(min-width:1024px){{{X} .fh-story-copy{{height:auto;min-height:var(--fh-story-height);padding:40px 0}}'
            f'{X} .fh-story-media{{right:calc(min(var(--fh-story-width),42%) + 64px)}}'
            f'{X} .fh-story-media .fh-original{{position:absolute;inset:0;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:40% 30%;'
            f'-webkit-mask-image:linear-gradient(to right,#000 80%,transparent);mask-image:linear-gradient(to right,#000 80%,transparent)}}}}'
            f'@media(max-width:1023px){{{X}{{min-height:0;display:flex;flex-direction:column}}'
            f'{X} .fh-story-copy{{order:1;height:auto;min-height:0;width:100%;margin:0;padding:32px 32px 24px}}'
            f'{X} .fh-story-media{{position:relative;order:2;inset:auto;top:auto;left:auto;right:auto;bottom:auto;width:100%;aspect-ratio:3/2}}'
            f'{X} .fh-story-media picture{{position:absolute;inset:0;width:100%;height:100%}}'
            f'{X} .fh-story-media .fh-original{{position:absolute;inset:0;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:50% 30%}}}}'
            f'@media(max-width:749px){{{X} .fh-story-copy{{padding:32px 16px 24px}}}}'))
        t = t[:a] + sec + t[b:]; done['celebration'] = k1 + k2 + k3
    # ---- the product shelves on tablets: the export laid 4 cards across 704 px (164 px each), so badges were cut and
    # the rating and guarantee lines ran into the next card; 2.6 cards across, the rest a swipe or an arrow away
    a, b = section('__bestsellers')
    if a is not None:
        sec, k = style(t[a:b], (
            '@media(min-width:750px) and (max-width:1023px){.fh-shelf .fh-product{flex-basis:calc((100% - 2*var(--fh-gap,16px))/2.6)}}'
            '.fh-badges{flex-wrap:wrap;justify-content:flex-end;left:12px;right:12px;top:12px;gap:6px}.fh-badges>span{white-space:nowrap}'
            '.fh-product-rating{min-width:0;overflow:hidden}.fh-product-rating>span:last-child{overflow:hidden;text-overflow:ellipsis}'))
        t = t[:a] + sec + t[b:]; done['shelf tablets'] = k
    # ---- "Firmer-looking skin" (the serum's story): two columns from 750 px, the card fixed at 519 px; at tablet
    # widths its copy wraps taller than that and the button was cut off at the card's foot: the card grows with it
    a, b = section('__serum')
    if a is not None:
        X = '[id$="__serum"] .fh-editorial--serum'
        sec, k = style(t[a:b], (
            f'@media(min-width:750px) and (max-width:1199px){{{X}{{height:auto;min-height:var(--fh-story-height)}}'
            f'{X} .fh-story-copy{{height:auto;padding-top:48px;padding-bottom:48px}}'
            f'{X} .fh-story-media{{height:auto;min-height:420px}}}}'))
        t = t[:a] + sec + t[b:]; done['serum tablets'] = k
    # ---- "Rested-looking eyes" (the balm's story): on desktops a fixed 369 px card, its banner (white for the copy,
    # her, then the stick) behind the copy. Under 1200 px the photo is her alone (its own source): phones and tablets
    # the copy, then the photo (square on phones, 4:3 on tablets); small laptops the copy and the photo side by side.
    # Its white studio backdrop is multiplied into the card's grey, so photo and card are one surface
    a, b = section('__arrivals_desktop')
    if a is not None:
        X = '[id$="__arrivals_desktop"] .fh-editorial--arrivals'
        img = (f'{X} .fh-story-media .fh-original{{position:absolute;inset:0;left:0;top:0;width:100%;height:100%;transform:none;'
               f'object-fit:cover;object-position:50% 30%;mix-blend-mode:multiply;-webkit-mask-image:none;mask-image:none}}')
        sec, k = style(t[a:b], (
            f'@media(max-width:1023px){{{X}{{height:auto;min-height:0;display:flex;flex-direction:column}}'
            f'{X} .fh-story-copy{{position:relative;order:1;height:auto;width:100%;margin:0;padding:40px 32px 24px}}'
            f'{X} .fh-story-media{{position:relative;order:2;inset:auto;top:auto;left:auto;right:auto;bottom:auto;width:100%;aspect-ratio:4/3;background:#e9e9e9}}'
            f'{X} .fh-story-media picture{{position:absolute;inset:0;width:100%;height:100%}}{img}'
            f'{X} .fh-story-media:after{{display:none}}}}'
            f'@media(max-width:749px){{{X} .fh-story-copy{{padding:32px 16px 16px}}{X} .fh-story-media{{aspect-ratio:1/1}}}}'
            f'@media(min-width:1024px) and (max-width:1199px){{{X}{{height:auto;min-height:var(--fh-story-height);display:grid;'
            f'grid-template-columns:1fr 1fr;align-items:stretch}}'
            f'{X} .fh-story-copy{{position:relative;order:1;height:auto;width:auto;margin:0;padding:48px 40px;justify-content:center}}'
            f'{X} .fh-story-media{{position:relative;order:2;inset:auto;top:auto;left:auto;right:auto;bottom:auto;width:auto;min-height:440px;background:#e9e9e9}}'
            f'{X} .fh-story-media picture{{position:absolute;inset:0;width:100%;height:100%}}{img}'
            f'{X} .fh-story-media:after{{display:none}}}}'))
        t = t[:a] + sec + t[b:]; done['arrivals tablets'] = k
    home.write_text(t, encoding='utf-8', errors='surrogateescape')
    return done

LAYOUT_FIXES = (
    # "The skinofab difference" (product pages): its 1fr 1fr grid grew to the square photo's height-sized width
    # (723 + 286 px in a 728 px box at 768), hiding the copy; equal columns that can shrink, one column under 1024 px
    '.skinofab-why-inner>*{min-width:0}'
    '@media(min-width:768px){.skinofab-why-inner{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}'
    '@media(min-width:768px) and (max-width:1023px){.skinofab-why-inner{grid-template-columns:minmax(0,1fr)}'
    '.skinofab-why-inner--square-image .skinofab-why__image{aspect-ratio:16/10}}'
    # the results cards: three equal columns whatever the width of their numbers (they pushed the page sideways at 768)
    '.skinofab-results__grid{grid-template-columns:repeat(3,minmax(0,1fr))}'
    '@media(min-width:768px) and (max-width:1023px){.skinofab-results__percentage{font-size:56px}.skinofab-results__card{padding:28px 16px}}'
    # product pages on tablets: the gallery above the buy box (side by side the buy box was 261 px wide), not sticky
    '@media(min-width:768px) and (max-width:1023px){.product-single__wrapper{display:block!important}'
    '.product-single__gallery{position:static!important;height:auto!important}}'
    # a circled word: room on both sides so the drawn ellipse never crosses the word before it
    '.text-highlight-wrapper--circle .text-highlight{margin-left:.22em;margin-right:.14em}'
    # policy tables: the export's fixed column widths and row heights (inline) squeezed "Express Shipping" onto 3 lines
    '.rte__table-wrapper table{height:auto!important}.rte__table-wrapper td{width:auto!important;height:auto!important}'
)

def layout_fixes():
    """Every page gets LAYOUT_FIXES at the end of its body, after the sections' own styles, so it wins over them
    without !important (where the export used !important, so does it). Returns how many pages."""
    n = 0
    for page in DST.rglob('*.html'):
        t = page.read_text(encoding='utf-8', errors='surrogateescape')
        if 'data-sf-layout-fixes' in t or '</body>' not in t: continue
        t = t.replace('</body>', f'<style data-sf-layout-fixes>{LAYOUT_FIXES}</style></body>', 1)
        page.write_text(t, encoding='utf-8', errors='surrogateescape'); n += 1
    return n

def local_location():
    """The product pages' "Free shipping to <country>" line asked Shopify's /browsing_context_suggestions.json, which
    NEXT does not have (a 404 and a console error on every product page): it now guesses no country and says the same
    to everyone, "Ships in 1 business day, tracked" (the flag, when a country is ever set, is the emoji flag, not a
    Shopify CDN image). Returns how many pages changed."""
    fetch = re.compile(r"async function fetchLocationInfo\(\) \{\s*try \{\s*const response = await fetch\('/browsing_context_suggestions\.json'\);"
                       r".*?console\.error\('Error fetching location info:', error\);\s*\}\s*\}", re.S)
    # no guess at all: the browser's language is not where the shopper lives (an en-US browser in the UK read "Ships to
    # US" and US delivery dates; one without a region read "Ships to your country", review 3)
    local = "function fetchLocationInfo() {\n    setLocationInfo('', '');\n  }"
    flag = re.compile(r'<img class="shipping-country-flag" src="https://cdn\.shopify\.com/static/images/flags/\$\{normalizedCountryCode\.toLowerCase\(\)\}\.svg\?width=32"[^`]*?>')
    emoji = ('<span class="shipping-country-flag" aria-hidden="true">${String.fromCodePoint.apply(null, normalizedCountryCode.split(\'\')'
             '.map(function (c) { return 127397 + c.charCodeAt(0); }))}</span>')
    n = 0
    for page in DST.rglob('*.html'):
        t = page.read_text(encoding='utf-8', errors='surrogateescape')
        if 'browsing_context_suggestions' not in t: continue
        u = fetch.sub(lambda m: local, t)
        u = flag.sub(lambda m: emoji, u)
        # the line beside it already says "Free shipping on every order": this half says how it ships, the same for everyone
        u = re.sub(r'const shippingMessage = `\$\{flagMarkup\}\$\{separator\}<span class="shipping_usp">Free shipping to <span[^`]*`;',
                   lambda m: "const shippingMessage = `${flagMarkup}${separator}<span class=\"shipping_usp\">Ships in 1 business day, tracked</span>`;", u)
        if u != t:
            page.write_text(u, encoding='utf-8', errors='surrogateescape'); n += 1
    return n

TRACK_FORM = (
    '<div class="sf-track"><form action="https://www.17track.net/en/track" method="get" target="_blank">'
    '<label for="sf-track-code">Tracking code</label><div class="sf-track-row">'
    '<input id="sf-track-code" name="nums" required autocomplete="off" spellcheck="false" maxlength="40" placeholder="e.g. YT2412345678901234">'
    '<button type="submit" class="btn btn--primary btn--solid">Track</button></div>'
    '<p class="sf-track-note">Your tracking code is in your shipping confirmation email. It opens on 17TRACK, which follows every '
    'carrier we ship with.</p></form>'
    f'<p class="sf-track-help">Only have your order number? Email <a href="mailto:{company.EMAIL}?subject=Where%20is%20my%20order%3F">'
    f'{company.EMAIL}</a> with it and we will send you your tracking link.</p></div>'
    '<style>.sf-track{max-width:560px;margin:0 auto 48px;text-align:left}.sf-track label{display:block;font-weight:600;margin-bottom:8px}'
    '.sf-track-row{display:flex;gap:8px;flex-wrap:wrap}.sf-track-row input{flex:1 1 220px;min-width:0;height:52px;padding:0 16px;'
    'border:1px solid #cfcfcf;border-radius:8px;font-size:16px}.sf-track-row button{flex:0 0 auto;height:52px;padding:0 32px}'
    '.sf-track-note,.sf-track-help{font-size:14px;line-height:1.5;color:#555;margin-top:12px}.sf-track-help a{text-decoration:underline}</style>'
)

MAILTO_JS = ("<script>document.addEventListener('submit', function (e) {"
             "var f = e.target, kind = f.getAttribute && f.getAttribute('data-sf-mailto'); if (!kind) return;"
             "e.preventDefault(); if (f.reportValidity && !f.reportValidity()) return;"
             "var v = function (n) { var el = f.querySelector('[name=\"' + n + '\"]'); return el ? el.value.trim() : ''; };"
             "var email = v('contact[email]'), name = v('contact[name]'), subject, body;"
             "if (kind === 'newsletter') { subject = 'Newsletter sign-up'; body = 'Please add ' + email + ' to the SKINOFAB newsletter.'; }"
             "else { subject = 'Message from ' + (name || email); body = v('contact[body]') + '\\n\\n' + [name, email, v('contact[phone]')].filter(Boolean).join('\\n'); }"
             "location.href = 'mailto:' + f.getAttribute('data-sf-to') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);"
             "});</script>")

def working_forms():
    """The forms the old Shopify store left: the footer's newsletter and the contact page's form posted to "#" with
    no token (NEXT answered 403 Forbidden), and NEXT has no newsletter or contact endpoint; the footer's country
    picker was Shopify's 108 markets (NEXT sells in one currency; the checkout asks the country) and posted the same
    way; the menu's "Log in" was a link to "#". Now the two forms open the shopper's email app with the message
    written, to the store's address (data-sf-to: a mailto: action draws Chrome's "Mixed Content" warning on every page;
    the line under the button says so and gives the address for shoppers without an email app), the
    country picker goes, and "Log in" opens the account (NEXT asks for the email code there). Returns the pages changed."""
    mail = company.EMAIL
    n = 0
    for page in sorted(DST.rglob('*.html')):
        t = page.read_text(encoding='utf-8', errors='surrogateescape')
        o = t
        t = re.sub(r'<form accept-charset="UTF-8" action="#" class="newsletter-form"([^>]*) method="post">\s*'
                   r'<input name="form_type" type="hidden" value="customer"/>\s*<input name="utf8" type="hidden" value="✓"/>\s*'
                   r'<input name="contact\[accepts_marketing\]" type="hidden" value="true"/>',
                   lambda m: f'<form accept-charset="UTF-8" class="newsletter-form"{m.group(1)} '
                             f'data-sf-mailto="newsletter" data-sf-to="{mail}" method="get">', t)
        # an empty field opened a mail asking to add "" to the list: the address is required (and checked as one)
        t = t.replace('name="contact[email]" placeholder="Your email" type="email" value=""/>',
                      'name="contact[email]" placeholder="Your email" required type="email" value=""/>')
        t = t.replace('<div class="errors">Email is invalid or already taken.</div>',
                      '<p class="sf-mailto-note" style="margin:10px 0 0;font-size:13px;opacity:.75">Opens your email app '
                      f'with the sign-up written: press Send there. No email app? Write to {mail} with “Newsletter”.</p>')
        t = re.sub(r'<form accept-charset="UTF-8" action="#" class="contact-form" id="([^"]+)" method="post">\s*'
                   r'<input name="form_type" type="hidden" value="contact"/>\s*<input name="utf8" type="hidden" value="✓"/>',
                   lambda m: f'<form accept-charset="UTF-8" class="contact-form" data-sf-mailto="contact" data-sf-to="{mail}" '
                             f'id="{m.group(1)}" method="get">', t)
        t = t.replace('<button class="cs-btn" type="submit">Send message</button>',
                      '<button class="cs-btn" type="submit">Send message</button>'
                      f'<p class="sf-mailto-note" style="margin:12px 0 0;font-size:14px;color:#5a5a5a">Opens your email app '
                      f'with your message to {mail}: press Send there. No email app? Write to us at {mail}.</p>')
        m = re.search(r'<form accept-charset="UTF-8" action="#" class="localization-form"', t)
        if m:
            e = t.find('</form>', m.start())
            if e > 0: t = t[:m.start()] + t[e + len('</form>'):]
        t = t.replace('href="#" id="customer_login_link"', 'href="/accounts/" id="customer_login_link"')   # NEXT's account page
        # "Log in" and "Create account" both opened the same page (NEXT signs in and signs up with one email code): one
        # link, named for both
        t = re.sub(r'(<a class="mobile-navlink mobile-navlink--small" href="/accounts/" id="customer_login_link">)Log in(</a></li>)\s*'
                   r'<li class="mobile-menu__item"><a class="mobile-navlink mobile-navlink--small" href="[^"]*" id="customer_register_link">Create account</a></li>',
                   r'\1Log in or create an account\2', t)
        if 'data-sf-mailto=' in t and MAILTO_JS not in t:
            t = t.replace('</body>', MAILTO_JS + '</body>', 1)
        if t != o:
            page.write_text(t, encoding='utf-8', errors='surrogateescape'); n += 1
    return n

# the listing pages' banner (Shop, Skin, The hits): a 650 px box the collage was drawn wider than (cut at the right on a
# laptop, slicing a face), darkened by an overlay, the title in white on a model's chin. The title now on the page above,
# the collage under it at its own shape (wide from 768 px, two by two on phones), whole, no overlay
LISTING_BANNER_CSS = ('<style>.banner-image__inner.sf-listing-banner{display:flex;flex-direction:column;min-height:0;height:auto}'
                      '.sf-listing-banner .banner-image__text-container{order:-1;min-height:0;padding:40px 0 22px}'
                      '.sf-listing-banner .banner-image__heading{color:#151515}'
                      '.sf-listing-banner .banner-image__image-container{position:relative;min-height:0;padding-top:0;aspect-ratio:3456/1080}'
                      '.sf-listing-banner .banner-image__image-inner{transform:none;animation:none}'
                      '@media (max-width:767px){.sf-listing-banner .banner-image__image-container{aspect-ratio:2000/2500}'
                      '.sf-listing-banner .banner-image__text-container{padding:28px 0 16px}}</style>')

def listing_banners():
    """LISTING_BANNER_CSS on the listing pages' banner. Returns the pages changed."""
    n = 0
    for page in sorted((DST / 'collections').glob('*.html')):
        t = page.read_text(encoding='utf-8', errors='surrogateescape')
        b = re.search(r'<div class="shopify-section supports-transparent-header" id="shopify-section-template--[0-9]+__section_banner_image_[A-Za-z0-9]+">', t)
        if not b or 'sf-listing-banner' in t: continue
        e = t.find('<div class="shopify-section', b.end())
        sec = t[b.start():e]
        sec, k = re.subn(r'class="banner-image__inner six-fifty-height original-height-mobile (item--[a-z-]+) text-light"',
                         r'class="banner-image__inner sf-listing-banner \1 text-dark"', sec, count=1)
        if not k: continue
        sec = sec.replace('<div class="overlay"></div>', '', 1).replace('sizes="(max-width: 1199px) 150vw, 105vw"', 'sizes="100vw"')
        page.write_text(t[:b.start()] + sec + LISTING_BANNER_CSS + t[e:], encoding='utf-8', errors='surrogateescape'); n += 1
    return n

def zoom_links():
    """The product galleries' lightbox said "The image could not be loaded." on every slide: each slide's zoom link
    (the image the lightbox opens) pointed to "#" (the export's went to the old store's CDN). Each now points to its
    slide's own largest image. Returns the links set."""
    n = 0
    for page in sorted((DST / 'products').glob('*.html')):
        t = page.read_text(encoding='utf-8', errors='surrogateescape')
        out, last = [], 0
        for m in re.finditer(r'<a class="product-single__media-link"([^>]*?) href="#"', t):
            imgs = list(re.finditer(r'<img [^>]*>', t[last:m.start()]))
            if not imgs: continue
            tag = imgs[-1].group(0)                 # the slide's image comes just before its zoom link
            ss = re.search(r'srcset="([^"]*)"', tag)
            cands = [(int(w), u) for u, w in re.findall(r'(\S+)\s+(\d+)w', ss.group(1))] if ss else []
            src = max(cands)[1] if cands else (re.search(r' src="([^"]+)"', tag) or [None, None])[1]
            if not src: continue
            out.append(t[last:m.start()] + f'<a class="product-single__media-link"{m.group(1)} href="{src}"'); last = m.end(); n += 1
        if out: page.write_text(''.join(out) + t[last:], encoding='utf-8', errors='surrogateescape')
    return n

def track_form():
    """The track-your-order page promised a form ("Fill in your tracking code...") but had none: its tracking app was
    the old Shopify store's. Now a tracking-code form that opens the parcel on 17TRACK (every carrier), and an email
    line for shoppers who only have their order number. Returns 1 when the page got it."""
    page = DST / 'pages' / 'postflows-track-your-order.html'
    if not page.exists(): return 0
    t = page.read_text(encoding='utf-8', errors='surrogateescape')
    if 'sf-track' in t: return 0
    m = re.search(r'(id="Page--template--[0-9]+__main">\s*<div class="wrapper">.*?<div class="rte">)', t, re.S)
    if not m: return 0
    t = t[:m.end()] + TRACK_FORM + t[m.end():]
    # its banner: a model's face behind white text (the heading ran across her eye at every width, and on phones she
    # held a lash serum the store does not sell): the heading and line on the page's own light grey, no photo
    b = re.search(r'<div class="shopify-section supports-transparent-header" id="shopify-section-template--[0-9]+__section_banner_image_[A-Za-z0-9]+">', t)
    if b:
        e = t.find('<div class="shopify-section', b.end())
        # (an empty [data-banner-image] stays: the theme's banner script looks for it and threw on the page without it)
        sec = re.sub(r'<div class="overlay"></div><div class="banner-image__image-container">.*?</figure></div>\s*</div>',
                     '<div data-banner-image="" hidden></div>', t[b.start():e], count=1, flags=re.S)
        sec = sec.replace('text-light', 'text-dark', 1)
        sec += ('<style>.banner-image .banner-image__inner.text-dark{min-height:0;height:auto;padding:64px 0 16px;background:#f6f5f3;color:#151515}'
                '.banner-image__inner.text-dark .banner-image__text-container{position:relative;inset:auto}'
                '.banner-image__inner.text-dark .banner-image__heading,.banner-image__inner.text-dark .banner-image__content{color:#151515}</style>')
        t = t[:b.start()] + sec + t[e:]
    # "You might like these too": the export's featured collection kept one card (the others were products the store
    # no longer sells); our four, as the homepage shows them
    f = re.search(r'<div class="shopify-section" id="shopify-section-template--[0-9]+__section_collection_[A-Za-z0-9]+">', t)
    if f:
        e = t.find('<div class="shopify-section', f.end())
        t = t[:f.start()] + more_products_html('../') + t[e:]
    page.write_text(t, encoding='utf-8', errors='surrogateescape')
    return 1

def more_products_html(up):
    """Our four products as a simple grid of cards (photo, name, price), for pages outside the homepage. Prices are
    bound to NEXT by the theme build (each card links to its product); the foundation's is the one its page shows
    first, as on the homepage."""
    one = ccf_copy.PACKS[0]
    usd = lambda v: f"${float(v):.2f}".replace('.00', '') + ' USD'
    cards = []
    for handle, title, path in HOME_ESSENTIALS:
        src = up + hashed_copy(path, 'img', f'skinofab-home-essential-{handle}-720w', (720, 720))[3:]
        if handle == 'color-changing-foundation':
            price = (f'<span class="sf-more__price" data-sf-fixed-price=""><s>{usd(one["compare"])}</s><b>{usd(one["refill"])}</b></span>'
                     f'<span class="sf-refill-note" style="font-size:12px;line-height:16px;color:#5a5a5a">with '
                     f'{ccf_copy.REFILL["every"]}-day refills, cancel anytime</span>')
        else:
            price = f'<span class="sf-more__price"><b>{usd(next(P.PRICE for P in SECOND_PRODUCTS if P.HANDLE == handle))}</b></span>'
        cards.append(f'<a class="sf-more__card" href="{up}products/{handle}.html"><img alt="{html.escape(title)}" height="720" loading="lazy" '
                     f'src="{src}" width="720"/><span class="sf-more__title">{html.escape(title)}</span>{price}</a>')
    return ('<div class="shopify-section" id="shopify-section-sf-more"><section class="sf-more"><div class="sf-more__head">'
            f'<h2>You might like these too</h2><a href="{up}collections/all-products.html">Shop all</a></div>'
            f'<div class="sf-more__grid">{"".join(cards)}</div></section>'
            '<style>.sf-more{width:calc(100% - 40px);max-width:1320px;margin:0 auto;padding:24px 0 64px}'
            '.sf-more__head{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-bottom:24px}'
            '.sf-more__head h2{margin:0;font-size:clamp(26px,3vw,36px)}.sf-more__head a{font-weight:600;text-transform:uppercase;text-decoration:underline;white-space:nowrap}'
            '.sf-more__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}'
            '@media(min-width:1024px){.sf-more__grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:24px}}'
            '.sf-more__card{display:flex;flex-direction:column;gap:8px;color:inherit;text-decoration:none}'
            '.sf-more__card img{width:100%;height:auto;aspect-ratio:1;object-fit:contain;background:#f7f7f7;border-radius:10px}'
            '.sf-more__title{font-weight:600;line-height:1.25}.sf-more__price{display:flex;gap:8px;flex-wrap:wrap}'
            '.sf-more__price s{color:#c8102e}.sf-more__price b{font-weight:400}</style></div>')

# Photos on the other pages that still showed products the store no longer sells, or a young model where the
# store's buyer is over 45: each file is replaced, at its own size (cover crop), by one of ours. A replaced file gets a
# new name (NEXT's CDN keeps serving an old name's first upload) and every reference to it is rewritten.
PAGE_IMAGES = [
    # the track page's banner: the persona model held the old pink lash serum to her brow; the same photo without it
    (r'^9_78eacf36-[^/]*\.(?:jpg|png)$', HOME / 'source' / 'track-face.jpg', 0.4),
    # the about page's first photo: the same, another model
    (r'^9_8d6072a5-[^/]*\.(?:jpg|png)$', HOME / 'source' / 'about-face.jpg', 0.4),
    # the about page's "born in a tiny kitchen lab": a young model with lip liner; a woman in her fifties with the balm
    (r'^rk_2-\d+w-[0-9a-f]{6}\.(?:jpg|png)$', BRAND / 'pdrn-balm' / 'apply-lips.jpg', 0.4),
    # the listing pages' banner (four young models with masks and patches): our four women 45+ with our products,
    # each file at the collage's own shape (keep: the page shows it whole, listing_banners), the screen's width
    (r'^skin-\d+w-[0-9a-f]{6}\.jpg$', HOME / 'collage-wide.jpg', 0.3, 1, '100vw', True),
    (r'^SM_-_Sales_Banner_-_Mobile_2_[^/]*\.jpg$', HOME / 'collage-square.jpg', 0.3, 1, None, True),
]

def page_images():
    """PAGE_IMAGES on every page. Returns how many files were replaced."""
    from PIL import Image
    imgdir = DST / 'assets' / 'img'
    renames = {}
    sizes = {}
    for pattern, src, fy, *more in PAGE_IMAGES:
        scale, size_attr, keep = (more + [1, None, False])[:3]
        source = Image.open(src).convert('RGB')
        for target in sorted(imgdir.iterdir()):
            if not re.match(pattern, target.name): continue
            w, h = Image.open(target).size
            if keep: h = round(w * source.height / source.width)        # its width, the source's shape
            if scale > 1 and source.width >= w * scale and source.height >= h * scale: w, h = w * scale, h * scale
            k = max(w / source.width, h / source.height)
            im = source.resize((max(w, round(source.width * k)), max(h, round(source.height * k))), Image.LANCZOS)
            x, y = (im.width - w) // 2, int((im.height - h) * fy)
            im = im.crop((x, y, x + w, y + h))
            stem, ext = os.path.splitext(target.name)
            tmp = imgdir / f'.page-image{ext}'
            im.save(tmp, **({'quality': 86, 'optimize': True, 'progressive': True} if ext.lower() in ('.jpg', '.jpeg') else {'optimize': True}))
            new = re.sub(r'-[a-z]?[0-9a-f]{6}$', '', stem) + f'-h{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}{ext}'
            tmp.rename(imgdir / new); renames[target.name] = new
            if size_attr: sizes[new] = size_attr
    if renames:
        rx = re.compile('|'.join(re.escape(k) for k in sorted(renames, key=len, reverse=True)))
        for p in DST.rglob('*'):
            if p.is_file() and p.suffix.lower() in TEXT:
                t = p.read_text(encoding='utf-8', errors='surrogateescape')
                n = rx.sub(lambda m: renames[m.group(0)], t)
                for name, attr in sizes.items():
                    n = re.sub(r'<(?:img|source)\b[^>]*%s[^>]*>' % re.escape(name),
                               lambda m: re.sub(r'\ssizes="[^"]*"', f' sizes="{attr}"', m.group(0)), n)
                if n != t: p.write_text(n, encoding='utf-8', errors='surrogateescape')
    return len(renames)

MENU = [('Adaptive Peptide Foundation', 'products/color-changing-foundation.html'),
        ('EGF + NAD+ Firming Serum', f'products/{serum_copy.HANDLE}.html'),
        ('PDRN Plumping Balm', f'products/{balm_copy.HANDLE}.html'),
        ('The Lymphatic Brush', f'products/{brush_copy.HANDLE}.html'),
        ('Shop all', 'collections/all-products.html'),
        ('Track your order', 'pages/postflows-track-your-order.html'),
        ('About', 'pages/about-skinofab.html'),
        ('Contact', 'pages/contact.html')]

def clean_menu():
    """The menu kept the export's tree with only our products left in it: "Shop all > Face > Foundation" three taps
    deep while the other three products sat at the top. Now one level: our four products, Shop all, Track your order,
    About, Contact (the account entries stay). Returns how many pages."""
    n = 0
    for page in DST.rglob('*.html'):
        t = page.read_text(encoding='utf-8', errors='surrogateescape')
        m = re.search(r'<ul class="mobile-nav[^"]*">', t)
        if not m: continue
        prefix = '../' * (len(page.relative_to(DST).parts) - 1)
        end = balanced_end(t, m.start(), 'ul'); inner = t[m.end():end - 5]
        keep, pos = [], 0
        for li in re.finditer(r'<li\b', inner):
            if li.start() < pos: continue
            e = balanced_end(inner, li.start(), 'li'); seg = inner[li.start():e]; pos = e
            if re.search(r'(?i)account|log in|sign in', re.sub(r'<[^>]+>', ' ', seg)): keep.append(seg)
        items = ''.join(f'<li class="mobile-menu__item mobile-menu__item--level-1"> <a class="mobile-navlink mobile-navlink--level-1" '
                        f'data-nav-link-mobile="" href="{prefix}{h}">{html.escape(name)}</a></li>' for name, h in MENU)
        t = t[:m.end()] + items + ''.join(keep) + '</ul>' + t[end:]
        # the header's own list (the design keeps it hidden: the menu opens from the button at every width) had the
        # old tree ("Face", "NEW Skinofab Skin"): the same flat list
        d = re.search(r'<div class="menu__items" data-takes-space="">', t)
        if d:
            flat = ''.join(f'<div class="menu__item" data-nav-item=""> <a class="navlink navlink--toplevel caps" data-top-link="" '
                           f'href="{prefix}{h}"> <span class="navtext">{html.escape(name)}</span> </a></div>' for name, h in MENU)
            t = t[:d.end()] + flat + '</div>' + t[balanced_end(t, d.start(), 'div'):]
        page.write_text(t, encoding='utf-8', errors='surrogateescape'); n += 1
    return n

def serum_copy_img(name): return serum_copy.IMG / f'{name}.jpg'
def balm_copy_img(name): return balm_copy.IMG / f'{name}.jpg'

def only_our_products():
    """The pages keep only our four products: the other products' pages and data, the pages that sold only them and
    the empty collections are deleted from the export, every link to them is removed (strip_gone), the homepage
    sections that showed only them are dropped, and the shelf's tabs that are left empty go. Returns a summary."""
    from bs4 import BeautifulSoup
    out = {'files': 0, 'links': 0, 'sections': 0, 'tabs': 0}
    for f in list((DST / 'products').glob('*')):
        if f.stem not in OUR_PRODUCTS: f.unlink(); out['files'] += 1
    for slug in LEGACY_PAGES:
        f = DST / 'pages' / f'{slug}.html'
        if f.exists(): f.unlink(); out['files'] += 1
    for c in EMPTY_COLLECTIONS:
        f = DST / 'collections' / f'{c}.html'
        if f.exists(): f.unlink(); out['files'] += 1
    # the design's product quick-view fragments for the other products (the lifting mask, the under-eye patches)
    for f in list((DST / 'recommendations').glob('*.html')) if (DST / 'recommendations').exists() else []:
        names = re.findall(r'data-product-image="" height|<img alt="([^"]+)" class="is-loading img-object-cover"', f.read_text(encoding='utf-8', errors='surrogateescape'))
        names = [n for n in names if n]
        if names and not any(n in {apf_copy.PRODUCT, 'Adaptive Peptide Foundation', 'Color Changing Foundation'} | {P.TITLE for P in SECOND_PRODUCTS} for n in names):
            f.unlink(); out['files'] += 1
    for p in sorted(DST.rglob('*.html')):
        t0 = p.read_text(encoding='utf-8', errors='surrogateescape')
        t = t0
        for old, new in LEGACY_TEXT: t = t.replace(old, new)
        # the footer's Shop column names the brush, balm and serum: the foundation goes first
        t = re.sub(r'(<li><a href="((?:\.\./)*)collections/all-products\.html">Shop all</a></li>)(?!<li><a href="(?:\.\./)*products/color-changing-foundation)',
                   r'\1<li><a href="\2products/color-changing-foundation.html">Adaptive Peptide Foundation</a></li>', t)
        if not re.search(r'(?:products|pages|collections)/', t) and 'accordion__item' not in t:
            if t != t0: p.write_text(t, encoding='utf-8', errors='surrogateescape')
            continue
        soup = BeautifulSoup(t, 'html.parser')
        k = strip_gone(soup, p.relative_to(DST).as_posix()) + (t != t0)
        for li in soup.select('li.accordion__item'):
            if LEGACY_WORDS.search(li.get_text(' ')):                    # a question or answer about another product
                li.decompose(); k += 1
        for lst in soup.select('ul.accordion__list'):
            if not lst.select('li'):
                sec = lst.find_parent('section') or lst.find_parent(class_=re.compile('shopify-section'))
                (sec or lst).decompose()
        if p == DST / 'index.html':
            for sec in soup.find_all('section', id=True):
                if sec['id'].endswith(HOME_DROP):
                    sec.decompose(); out['sections'] += 1
            # the shelf's tabs whose products are all gone: the panel (if strip_gone left it) and its tab button
            for panel in soup.select('[data-fh-panel]'):
                if not panel.select('article'): panel.decompose()
            panels = {pn['data-fh-panel'] for pn in soup.select('[data-fh-panel]')}
            for b in soup.select('[data-fh-tab]'):
                if b['data-fh-tab'] not in panels: b.decompose(); out['tabs'] += 1
        if k or p == DST / 'index.html':
            p.write_text(str(soup), encoding='utf-8', errors='surrogateescape')
            out['links'] += k
    return out

def real_testimonials(t, reviews=REVIEWS):
    """The product page's testimonial slider showed the design's persona stories ("Margaret, 61") with AI portraits
    under a "Verified purchase" badge. Each card now carries a real verified review (apf_copy.TESTIMONIALS) word for
    word: the reviewer's name as the review app shows it, her own photo, her rating. Returns (html, cards replaced)."""
    data = reviews / 'reviews.json'
    if not data.exists(): return t, 0
    by_id = {r['id']: r for r in json.loads(data.read_text())['reviews']}
    picks = [(by_id[i], f) for i, f in apf_copy.TESTIMONIALS
             if i in by_id and by_id[i].get('photos') and by_id[i]['rating'] == 5 and by_id[i].get('verified')]
    m = re.search(r'<section class="skinofab-testimonials"', t)
    if not m or not picks: return t, 0
    end = t.find('</section>', m.start())
    sec = t[m.start():end]
    slides = list(re.finditer(r'<div class="swiper-slide">\s*<div class="skinofab-testimonials__card">', sec))
    out, last, done = [], 0, 0
    for k, s in enumerate(slides):
        stop = slides[k + 1].start() if k + 1 < len(slides) else len(sec)
        card = sec[s.start():stop]
        if k < len(picks):
            r, focus = picks[k]
            im = face_crop(reviews / 'photos' / r['photos'][0], focus)
            tmp = DST / 'assets' / 'img' / f"review-card-{re.sub(r'[^A-Za-z0-9]', '', r['id'])}.jpg"
            im.save(tmp, quality=84, optimize=True, progressive=True)
            final = tmp.with_name(f"{tmp.stem}-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.jpg"); tmp.rename(final)
            name = html.escape(r['name'])
            body = html.escape(' '.join(r['body'].split()))
            card = re.sub(r'<img alt="[^"]*" loading="lazy" src="[^"]*"/>',
                          f'<img alt="{name}, verified buyer" loading="lazy" src="../assets/img/{final.name}" width="640" height="480"/>', card, count=1)
            card = re.sub(r'(<span class="skinofab-testimonials__name">)[^<]*(</span>)', rf'\g<1>{name}\g<2>', card, count=1)
            card = re.sub(r'(<div class="skinofab-testimonials__text">\s*<p>).*?(</p>)', lambda mm: f'{mm.group(1)}&ldquo;{body}&rdquo;{mm.group(2)}', card, count=1, flags=re.S)
            card = card.replace('Verified purchase', 'Verified buyer', 1)
            done += 1
        else:
            card = ''                                     # no fewer real reviews than cards: an extra story card goes
        out.append(sec[last:s.start()] + card); last = stop
    sec = ''.join(out) + sec[last:] if slides else sec
    return t[:m.start()] + sec + t[end:], done

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
    balm = json.loads((WORK / balm_copy.OFFERS_FILE).read_text())['variants']
    c1, c2 = balm_copy.BUNDLES[0], balm_copy.BUNDLES[1]
    c_text = f"Just {money(round(float(c2['price']) - float(c1['price']), 2))} more for a second stick: one for home, one for your bag."
    serum = json.loads((WORK / serum_copy.OFFERS_FILE).read_text())['variants']
    d1, d2 = serum_copy.BUNDLES[0], serum_copy.BUNDLES[1]
    d_text = f"Just {money(round(float(d2['price']) - float(d1['price']), 2))} more for a second bottle: about two more months."

    return {'product': cart['product'], 'addons': cart['addons'],
            'upgrades': [{'from': variants[one['key']], 'to': variants[two['key']], 'title': cart['upgrade_title'],
                          'text': text, 'button': cart['upgrade_button']},
                         {'from': brush[b1['key']], 'to': brush[b2['key']], 'title': brush_copy.CART_UPGRADE['title'],
                          'text': b_text, 'button': brush_copy.CART_UPGRADE['button']},
                         {'from': balm[c1['key']], 'to': balm[c2['key']], 'title': balm_copy.CART_UPGRADE['title'],
                          'text': c_text, 'button': balm_copy.CART_UPGRADE['button']},
                         {'from': serum[d1['key']], 'to': serum[d2['key']], 'title': serum_copy.CART_UPGRADE['title'],
                          'text': d_text, 'button': serum_copy.CART_UPGRADE['button']}],
            'review': {'text': cart['review_text'], 'name': cart['review_name']}, 'guarantee_text': cart['guarantee_text'],
            # refills on by default: every add of the foundation that names no purchase type is the refill plan
            'refill': {'default': bool(ccf_copy.REFILL.get('default')), 'interval': ccf_copy.REFILL['interval'],
                       'every': ccf_copy.REFILL['every'],
                       # cards and listings show the price its page shows first (refills ticked), and its was-price
                       'price_text': f"${float(ccf_copy.PACKS[0]['refill']):g} USD", 'compare_text': f"${float(ccf_copy.PACKS[0]['compare']):g} USD"},
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

CLIP_ARGS = {'mp4': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '26', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'],
             'webm': ['-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '37', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '4', '-pix_fmt', 'yuv420p']}

def card_clip(src, name, kind, width=540):
    """A silent `width` px copy of a clip for a card that plays it muted (the export's clips are 1080p with sound):
    'mp4' (H.264) or 'webm' (VP9, for browsers without H.264). Made once with ffmpeg, cached in WORK/clips by the
    source's bytes, then copied into the export like hashed_copy. None if ffmpeg can't make it."""
    key = hashlib.md5(src.read_bytes()).hexdigest()[:12]
    cache = WORK / 'clips' / f'{key}-{width}.{kind}'
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        part = cache.with_name('part-' + cache.name)
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src), '-vf', f'scale={width}:-2', '-an',
                            *CLIP_ARGS[kind], str(part)])
        if r.returncode or not part.exists(): return None
        part.rename(cache)
    return hashed_copy(cache, 'media', name)

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

def avatar():
    """The brand's round avatar for its own note (the expert block's signature): a black disc with the S of the
    wordmark in Playfair Display, under a content-hashed name."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGB', (190, 190), (21, 21, 21))
    f = ImageFont.truetype(str(Path(__file__).resolve().parent / 'assets' / 'fonts' / 'PlayfairDisplay-VF.ttf'), 118)
    f.set_variation_by_name('Medium')
    ImageDraw.Draw(im).text((95, 99), 'S', font=f, fill=(255, 255, 255), anchor='mm')
    tmp = DST / 'assets' / 'img' / 'skinofab-avatar.png'
    im.save(tmp, optimize=True)
    final = tmp.with_name(f"skinofab-avatar-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.png"); tmp.rename(final)
    return '../assets/img/' + final.name


def twin_context(P, found, stats, amazon):
    """What twin.sections needs for P: its images (brand/<product>/<name>.jpg, else its labelled/ or source/ photo,
    cropped to the slot), clips, review strips, wall and "no reviews yet" box."""
    def img(name, size, centering=(0.5, 0.5)):
        path = P.IMG / f'{name}.jpg'                   # product_photos.py made these white already
        raw = not path.exists()
        if raw:                                        # the real wordmark on it, if it shows the product (product_photos)
            path = next(p for p in (P.IMG / 'labelled' / f'{name}.jpg', P.IMG / 'source' / f'{name}.jpg') if p.exists())
        return crop_to(path, f'{P.IMG_PREFIX}-{name}-{size[0]}x{size[1]}', size, centering, white=raw)
    media = WORK / 'brush' / 'media'
    def clip(k):
        return (hashed_copy(media / f'{k}.mp4', 'media', f'skinofab-{k}'),
                hashed_copy(media / f'{k}.jpg', 'img', f'skinofab-{k}-poster'))
    reviews = WORK / P.REVIEWS_DIR
    # until the product has its own reviews, its page shows none: the foundation's, even labelled, read as this product's
    brand = None
    wall = (f'<div class="shopify-section" id="shopify-section-sf-{P.KEY}-amazon">{P.amazon_html(amazon)}</div>' if amazon else '') + review_wall(reviews)
    return {'img': img, 'clip': clip, 'avatar': avatar(), 'strip_own': review_strip(reviews), 'strip_brand': brand,
            'wall': wall, 'no_reviews': None if stats else f'<style>{brush_copy.SECTIONS_CSS}</style>{P.no_reviews_html(amazon=amazon)}'}


def product_page(base, P, final, found=None):
    """products/<P.HANDLE>.html for a second product (P: its copy module, the brush's or the balm's): the foundation
    page's chrome and buy box markup with the product's buy box in it, and below it every section of the finished
    foundation page (`final`), in its order and markup, filled with P's copy (twin.py, P.TWIN). Prices, the bundle
    picker's variants and the cart come from NEXT (<work_dir>/<P.OFFERS_FILE>, written by setup_brush_offers.py).
    found: the foundation's imported reviews (review_data()), shown as its own until P has reviews."""
    import copy
    from bs4 import BeautifulSoup, NavigableString
    offers = json.loads((WORK / P.OFFERS_FILE).read_text())
    soup = BeautifulSoup(base, 'html.parser')
    frag = lambda h: BeautifulSoup(h, 'html.parser')
    main = soup.find('main')
    prod = main.select_one('[id$="__main"].shopify-section--product')
    for sec in [c for c in main.find_all(recursive=False) if c is not prod and 'section_custom_html' not in (c.get('id') or '')]:
        sec.decompose()
    img = lambda k, w: hashed_copy(P.IMG / f'{P.GALLERY[k - 1]}.jpg', 'img', f'{P.IMG_PREFIX}-{k}-{w}w', (w, w))
    # gallery: P.GALLERY, the first one eager
    slider = prod.select_one('[data-product-single-media-slider]')
    slides = slider.select('[data-product-single-media-wrapper]')
    thumbs = prod.select_one('[data-product-single-media-thumbs]')
    t_slides = [copy.copy(slides[0]), copy.copy(slides[1])]
    t_thumb = copy.copy(thumbs.select('[data-thumbnail-id]')[0])
    for s_ in slides: s_.decompose()
    for t_ in thumbs.select('[data-thumbnail-id]'): t_.decompose()
    for k in range(1, len(P.GALLERY) + 1):
        mid = str(P.MEDIA_BASE + k)
        big, mid_src, small = img(k, 1080), img(k, 753), img(k, 178)
        sl = copy.copy(t_slides[0 if k == 1 else 1])
        sl['data-id'], sl['data-media-id'] = mid, f'{P.KEY}-{mid}'
        sl['id'] = f'FeaturedMedia-{P.KEY}-{mid}'
        im = sl.find('img')
        im['src'], im['srcset'] = big, f'{mid_src} 753w, {big} 1080w'
        im['alt'], im['data-image-id'] = P.TITLE, mid
        if k > 1: im['fetchpriority'] = 'low'
        slider.append(sl)
        th = copy.copy(t_thumb)
        th['data-id'], th['data-thumbnail-id'] = mid, f'{P.KEY}-{mid}'
        th.find('a')['aria-label'] = P.TITLE
        ti = th.find('img')
        ti['src'], ti['srcset'], ti['alt'] = small, f'{big} 1080w', P.TITLE
        ti['loading'] = 'eager' if k <= 5 else 'lazy'
        thumbs.append(th)
    # the buy box, top to bottom
    blocks = prod.select('.product__block')
    def text_of(b): return ' '.join(b.get_text(' ', strip=True).split())
    for b in blocks:
        cls = b.get('class') or []
        t = text_of(b)
        if ('Formulated in Korea' in t and not getattr(P, 'KOREAN', False)) or 'product__subheading' in str(b)[:200] or 'countdown-timer-wrapper' in cls \
           or b.get('data-default-usp') is not None or b.select_one('[data-serum-subscription-usps]') or b.select_one('hr') \
           or {'product__features', 'product-suitability', 'customer-survey-results'} & set(cls):
            b.decompose()
    # no "Nicole and 5,000+ others purchased": the product is new here; its stars appear with its first real review
    social = prod.select_one('.social-proof-container')
    if social: (social.find_parent(class_='product__block') or social).decompose()
    brush_reviews = WORK / P.REVIEWS_DIR        # tools/reviews/import_reviews.py ... --product <handle> --out <P.REVIEWS_DIR>
    stats = json.loads((brush_reviews / 'reviews.json').read_text()) if (brush_reviews / 'reviews.json').exists() else None
    app = prod.select_one('.product__block.standard__app')
    app.clear(); app.append(frag(brush_rating(stats)))
    price = prod.select_one('.product__price-and-badge [data-price-wrapper]')
    was = price.select_one('.product__price--compare')
    if float(P.COMPARE) > float(P.PRICE): was.string = P.money(P.COMPARE)
    else: was.decompose()                                  # no saving on one: no "was" price
    reg = price.select_one('.product__price--regular')
    reg.string = P.money(P.PRICE)
    off = price.select_one('.product__price--off')
    if off: off.decompose()
    reg.insert_after(frag(f'<span class="sfb-ship">{P.esc(P.SHIPPING_BADGE)}</span>'))
    usp = prod.select_one('.skinofab-usp-grid')
    # no icon grid, as on the foundation's page (it hides its own): the block keeps the buy box styles only
    usp.replace_with(frag(f'<style>{P.BUYBOX_CSS}</style>'))
    # the promise, under the price (the foundation's page has its own description there)
    head = prod.select_one('.product__price-and-badge')
    amazon_f = WORK / P.AMAZON_FILE if P.AMAZON_FILE else None   # tools/reviews/amazon_rating.mjs: the owner's own listing, or nothing
    amazon = json.loads(amazon_f.read_text()) if amazon_f and amazon_f.exists() else None
    if head: head.insert_after(frag(f'<p class="sfb-lead">{P.esc(P.LEAD)}</p>'
                                    + (P.amazon_line(amazon) if amazon else '')))
    title_el = prod.select_one('.product__title')
    if getattr(P, 'EYEBROW', None) and title_el:
        title_el.insert_before(frag(f'<span class="sfp-eyebrow">{P.esc(P.EYEBROW)}</span>'))
    form = prod.select_one('form[data-product-form]')
    form.select_one('input[name=id]')['value'] = str(P.SHOPIFY_VARIANT)
    for el in form.select('.shop-pay-terms'): el.decompose()
    for el in prod.select('skinofab-installments'): el.decompose()   # the foundation's pay-in-4 line
    for el in soup.select('script.kaching-bundles-product, script.kaching-bundles-deal-block-settings'): el.decompose()
    btn = form.select_one('[data-add-to-cart]')
    label = btn.select_one('[data-add-to-cart-text]') if btn else None
    if label: label.insert_after(frag('<span class="sfb-btn-price" data-sfb-btn-price></span>'))
    if btn and btn.get('data-notification-popup'):
        btn['data-notification-popup'] = btn['data-notification-popup'].replace('Adaptive Peptide Foundation', P.TITLE).replace('Color Changing Foundation', P.TITLE)
    gift_imgs = {k: hashed_copy(P.IMG / f'gift-{f}.jpg', 'img', f'{P.GIFT_PREFIX}-{f}') for k, f in P.GIFT_FILES.items()}
    form.select_one('[data-subscription-watch-price]').insert_before(
        frag(P.picker_html(offers['variants'], gift_imgs, apf_copy.OFFER_PICKER_CSS)))
    cta = form.select_one('#CTA_kopstorm')
    # "Love it or your money back" and the bought-once facts, as under the foundation's button
    cta.insert_after(frag(f'<div class="product__block sfp-trust"><style>{apf_copy.TRUST_CSS}</style>'
                          f'{apf_copy.trust_html(terms=False, refills=False)}</div>'))
    # the tabs, in the design's accordion markup
    accs = prod.select('.product__block.product__accordions')
    tpl, anchor = copy.copy(accs[0]), accs[-1]
    for k, (title, body) in reversed(list(enumerate(P.tabs()))):
        a = copy.copy(tpl)
        a['id'] = f'Block--sfb_tab_{k}'
        a.select_one('[data-collapsible-trigger]')['aria-controls'] = f'ProductAccordion--sfb-tab-{k}'
        a.select_one('[data-collapsible-container]')['id'] = f'ProductAccordion--sfb-tab-{k}'
        span = a.select_one('#accordionbefore'); span.clear(); span.append(frag(title))
        inner = a.select_one('[data-collapsible-content]'); inner.clear(); inner.append(frag(body))
        anchor.insert_after(a)
    for a in accs: a.decompose()
    # the foundation's FrontrowMD sticker styles do not belong here
    for st in prod.find_all('style'):
        if '#frontrow-sticker' in (st.string or ''): st.decompose()
    for node in prod.find_all(string=True):
        if 'Color Changing Foundation' in node or 'Adaptive Peptide Foundation' in node:
            node.replace_with(node.replace('Color Changing Foundation', P.TITLE).replace('Adaptive Peptide Foundation', P.TITLE))
    for el in prod.find_all(alt=True):
        el['alt'] = el['alt'].replace('Color Changing Foundation', P.TITLE).replace('Adaptive Peptide Foundation', P.TITLE)
    # the sections below: the finished foundation page's, in its order, with P's copy (twin.py)
    found_main = BeautifulSoup(final, 'html.parser').find('main').find_all(recursive=False)
    out = twin.sections(found_main, P, twin_context(P, found, stats, amazon))
    prod.insert_after(frag(''.join(out)))
    # the design's product JSON (the theme's product script reads prices and variants from it)
    gallery = [s_.find('img')['src'] for s_ in slider.select('[data-product-single-media-wrapper]')]
    pj = soup.select_one('script[data-product-json]')
    if pj: pj.string = json.dumps(product_snapshot(P, ['/' + g.lstrip('./') for g in gallery]), ensure_ascii=True)
    # head and body: the product's own title, description and page id
    text = str(soup)
    text = re.sub(r'<title>.*?</title>', f'<title>{html.escape(P.META_TITLE)}</title>', text, count=1, flags=re.S)
    text = re.sub(r'<meta content="[^"]*" name="description"/>', f'<meta content="{html.escape(P.META_DESCRIPTION)}" name="description"/>', text, count=1)
    text = text.replace('id="color-adapting-foundation-for-flawless-skin-skinofab"', f'id="{P.HANDLE}-skinofab"', 1)
    text, _ = sticky_bar(text, sticky_thumb(P.IMG / 'card.jpg', f'{P.IMG_PREFIX}-sticky'), P.TITLE,
                         f'From {P.money(P.PRICE)} · Free shipping', P.STICKY_BUTTON)
    return text

SHIELD = ('<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#151515" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 4.6-3 8.4-7 10-4-1.6-7-5.4-7-10V6z"/>'
          '<path d="M8.5 12l2.5 2.5 4.5-5"/></svg>')

def shelf_rating(P, home):
    """The rating row every shelf card has, in the same place as the foundation's: P's stars and count once it has
    real reviews (<work_dir>/<P.REVIEWS_DIR>/reviews.json, imported from its review app), else what is true today:
    it is new, and it carries the 30-day money-back guarantee. Never another product's rating."""
    data = WORK / P.REVIEWS_DIR / 'reviews.json'
    summary = json.loads(data.read_text()).get('summary') if data.exists() else None
    if summary and int(summary.get('count') or 0):
        stars = re.search(r'<div class="fh-product-rating"><img alt="" height="16" src="([^"]+)"', home)
        img = f'<img alt="" height="16" src="{stars.group(1)}" width="80"/>' if stars else ''
        return (f'<div class="fh-product-rating">{img}<span>{float(summary["average"]):.1f} '
                f'({int(summary["count"]):,} review{"s" if int(summary["count"]) != 1 else ""})</span></div>')
    # short enough for a quarter of a 1024 px row (the longer "30-day money-back guarantee" ended in an ellipsis)
    return f'<div class="fh-product-rating">{SHIELD}<span>New · 30-day guarantee</span></div>'

def product_shelf(home, P):
    """The homepage product shelf: the product's card (P: its copy module) in the default list (the Bestsellers view)
    and in the Bestsellers, New and Face tabs, after the product P.SHELF names (first when None), in each place's own
    card markup."""
    m = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+__bestsellers"', home)
    if not m: return home, False
    end = home.find('</section>', m.start())
    sec = home[m.start():end]
    sh, title, href = P.SHELF, html.escape(P.TITLE), f'products/{P.HANDLE}.html'
    big = hashed_copy(P.IMG / 'card.jpg', 'img', f'{P.IMG_PREFIX}-card-1080w', (1080, 1080))[3:]
    small = hashed_copy(P.IMG / 'card.jpg', 'img', f'{P.IMG_PREFIX}-card-720w', (720, 720))[3:]
    was = f'<s>{P.money(P.COMPARE)} USD</s>' if float(P.COMPARE) > float(P.PRICE) else ''
    price = f'<div class="fh-price">{was}<span>{P.money(P.PRICE)} USD</span></div>'
    rich = (f'<article class="fh-product">\n<a aria-label="{title}" class="fh-product-image" href="{href}">\n'
            f'<picture class=""><img alt="{title}" class="fh-upload" height="1080" loading="lazy" sizes="100vw" src="{big}" '
            f'srcset="{small} 720w, {big} 1080w" width="1080"/>\n</picture>\n'
            f'<span class="fh-badges"><span>{html.escape(sh["badge"])}</span><span class="fh-saving">{html.escape(sh["saving"])}</span></span></a>\n'
            f'<div class="fh-product-info">{shelf_rating(P, home)}<h3><a href="{href}">{title}</a></h3>\n{price}'
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

def product_snapshot(P, gallery):
    """products/<P.HANDLE>.js: the Shopify product JSON shape the theme build reads (handle, ids, prices)."""
    cents = lambda v: int(round(float(v) * 100))
    v = {'id': P.SHOPIFY_VARIANT, 'title': 'Default Title', 'option1': 'Default Title', 'option2': None, 'option3': None,
         'sku': P.BUNDLES[0]['sku'], 'requires_shipping': True, 'taxable': True, 'featured_image': None, 'available': True,
         'name': P.TITLE, 'public_title': None, 'options': ['Default Title'], 'price': cents(P.PRICE),
         'compare_at_price': cents(P.COMPARE), 'requires_selling_plan': False, 'selling_plan_allocations': []}
    return {'id': P.SHOPIFY_ID, 'title': P.TITLE, 'handle': P.HANDLE, 'description': P.DESCRIPTION,
            'vendor': 'Skinofab', 'type': '', 'tags': [], 'price': v['price'], 'price_min': v['price'], 'price_max': v['price'],
            'available': True, 'price_varies': False, 'compare_at_price': v['compare_at_price'],
            'compare_at_price_min': v['compare_at_price'], 'compare_at_price_max': v['compare_at_price'], 'compare_at_price_varies': False,
            'variants': [v], 'images': gallery, 'featured_image': gallery[0],
            'options': [{'name': 'Title', 'position': 1, 'values': ['Default Title']}], 'url': f'/products/{P.HANDLE}',
            'media': [], 'requires_selling_plan': False, 'selling_plan_groups': []}

def honest_counts(texts, summary):
    """The design's review and customer counts were far above what its review app records (the foundation showed
    351,837 reviews; Loox counts 10,512; the serum 61,583 for 22). Every count becomes a real one: the imported
    reviews' total for the foundation and the store-wide lines, each other product's own Loox count. Returns hits."""
    n, five, avg = int(summary['count']), int(summary['distribution'].get('5', summary['distribution'].get(5, 0))), float(summary['average'])
    floor = lambda v: f'{(v // 100) * 100:,}' if v >= 1000 else str(v)   # 9,996 -> "9,900+": true, and close
    def loved(m):   # any "Loved by N+" above the real total (the design had 40,000+ to 300,000+) becomes the total
        return m.group(1) + (floor(n) if int(m.group(2).replace(',', '')) > n else m.group(2)) + '+'
    def crowd(m):   # "300,000+ women have already switched", "10.000+ customers": above the total -> the total
        v = int(re.sub(r'[,.]', '', m.group(1)))
        if v <= n: return m.group(0)
        noun = 'verified buyers' if m.group(2) == 'women' else m.group(2)
        return f'{floor(n)}+ {noun}'
    reps = [
        (r'(Loved by (?:<span class="text-highlight"[^>]*>)?)(\d[\d,]*)\+', loved),
        (r'(\d{1,3}(?:[,.]\d{3})+)\+ (women|customers|buyers|happy customers|Verified Customers|verified customers)', crowd),
        # the same with the number highlighted ("<span ...>300,000+</span> women have already switched")
        (r'(<span[^>]*>)(\d{1,3}(?:[,.]\d{3})+)\+(</span>\s*)women', lambda m: (
            m.group(0) if int(re.sub(r'[,.]', '', m.group(2))) <= n else f'{m.group(1)}{floor(n)}+{m.group(3)}verified buyers')),
        (r'Why skinofab works for 10\.000\+ brows', 'Why skinofab works for your brows'),
        (r'50,000\+ customers', f'{floor(n)}+ customers'),
        (r'Over 50,000 5-star reviews', f'Over {floor(five)} 5-star reviews'),
        (r'Trusted by 1,000,000\+ women who finally found something that works', 'From verified buyers who finally found something that works'),
        (r'Backed by over 1,000,000 customers, 50,000 five-star reviews and data from independent panels run with real customers',
         # where they come from, as the product page's review wall says it (review 3: only that page said so)
         f'Backed by over {floor(n)} verified reviews of the same formula from our earlier store, {avg:.1f} out of 5 on average'),
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
    """Homepage speed (measured on a throttled phone: LCP 7.2 s, then 12.4 s from the rotating slide). The second hero
    slide loaded its 1,680-px image at once, competed with the first and later became the largest paint; the shelf cards asked for 1,920-px images (sizes 100vw) for a ~260-px card;
    the phone hero downloaded the whole 1,800-px banner although only a quarter of it shows. Returns (html, changes)."""
    from PIL import Image, ImageFilter
    import numpy as np
    n = {}
    # one hero, the foundation: the serum slide rotated in ~6 s after the slider started, so on a throttled phone it
    # became the page's largest paint at 12 s (LCP); a single focused message also sells better than a carousel, and
    # the serum keeps its own section further down. The slider script leaves a one-slide hero alone (no dots, no timer)
    for cls in ('fh-hero-slide fh-hero-slide--serum', 'fh-hero-controls'):
        m = re.search(rf'<div[^>]*class="{cls}"', home)
        if m:
            home = home[:m.start()] + home[balanced_end(home, m.start(), 'div'):]; n[cls.split()[-1]] = 1
    # slides start at opacity 0 until the script marks one active, and it skips a one-slide hero: the slide is active
    # in the HTML, so it shows (and counts as the largest paint) the moment its image arrives, before any script runs
    home, n['hero active'] = re.subn(r'class="fh-hero-slide fh-hero-slide--foundation"', 'class="fh-hero-slide fh-hero-slide--foundation is-active"', home)
    home, n['lazy hero slides'] = re.subn(r'(<img[^>]*fetchpriority="low"[^>]*?)loading="eager"', r'\1loading="lazy"', home)
    home, n['card sizes'] = re.subn(r'(<img[^>]*class="fh-upload"[^>]*?)sizes="100vw"', r'\1sizes="(min-width: 990px) 300px, 270px"', home)
    # The hero photo, one file per layout, from the 4096-px master (docs/persona-image-shots.md, "Home hero").
    # The layout draws it wider than the screen and shows a fixed part of it at every width (measured 360-2560 px):
    # phones 349vw wide showing 64% to 92% of its width, desktops 150vw wide showing the right two thirds. Each file
    # keeps that part sharp and flattens the rest (never on screen) into the backdrop, so it compresses to a fraction.
    # The export said sizes="2885px" for desktops (true only at 1920 px): 150vw lets a 1440-px screen take 2160.
    m = re.search(r'(<picture class="fh-hero-image">\s*)(<img[^>]*class="fh-original"[^>]*fetchpriority="high"[^>]*src="assets/img/([^"]+)"[^>]*>)', home)
    if m:
        # the persona photo when one replaces this banner: the swap below renames files after this runs, so the
        # export's file here is still the old photo (young model, old bottle)
        src = IMAGES / m.group(3) if IMAGES and (IMAGES / m.group(3)).exists() else DST / 'assets' / 'img' / m.group(3)
        master = Image.open(src).convert('RGB')
        def only(width, lo, hi, name):
            im = master if master.width <= width else master.resize((width, round(master.height * width / master.width)), Image.LANCZOS)
            a = np.asarray(im).astype(np.float32)
            x = np.arange(im.width) / im.width
            small = im.resize((im.width // 8, im.height // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(8))
            flat = np.asarray(small.resize(im.size, Image.BILINEAR)).astype(np.float32)
            keep = np.clip(np.minimum((x - lo) / 0.03, (hi - x) / 0.03), 0, 1)[None, :, None]
            out = Image.fromarray(np.clip(a * keep + flat * (1 - keep) + 0.5, 0, 255).astype(np.uint8))
            # WebP: 45% under a JPEG of the same quality (every browser the store supports reads it; the CDN resizes it)
            tmp = DST / 'assets' / 'img' / f'{name}.webp'
            out.save(tmp, 'WEBP', quality=80, method=6)
            final = tmp.with_name(f"{name}-{im.width}w-{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}.webp"); tmp.rename(final)
            return final, out.size
        # phones top out at 2880 px (a 3x phone gets 2.1 image pixels per point: sharp, and half the bytes of 4096,
        # which on a slow phone network is the difference between a 3.5 s and a 7 s first paint); desktops up to 4096
        # phones: an 11:12 window on her, from the hand holding the bottle to her hair's right (the CSS below), 59% to 99%
        (phone, psz), (desk, dsz) = only(2880, 0.585, 1.04, 'skinofab-hero-phone'), only(4096, 0.30, 1.04, 'skinofab-hero-desktop')
        phone_vw = '256vw'                       # the 11:12 window shows 0.39 of the photo's width: it is drawn 1/0.39 screens wide
        source = (f'<source media="(max-width: 749px)" sizes="{phone_vw}" '
                  f'srcset="assets/img/{phone.name} {psz[0]}w" width="{psz[0]}" height="{psz[1]}">')
        img = m.group(2)
        img = re.sub(r'\ssrc="[^"]*"', f' src="assets/img/{desk.name}"', img, 1)
        img = re.sub(r'\ssrcset="[^"]*"', f' srcset="assets/img/{desk.name} {dsz[0]}w"', img, 1)
        img = re.sub(r'\ssizes="[^"]*"', f' sizes="(max-width: 749px) {phone_vw}, 150vw"', img, 1)
        img = re.sub(r'\swidth="\d+"', f' width="{dsz[0]}"', img, 1)
        img = re.sub(r'\sheight="\d+"', f' height="{dsz[1]}"', img, 1)
        home = home[:m.start(2)] + source + img + home[m.end(2):]
        # On phones the export laid the photo 349% wide at fixed offsets under copy of a fixed height (797 px): what
        # showed of her depended on the copy's length and the screen, and it cut her face at its right edge. The slide
        # now stacks: the copy, then an 11:12 window on the photo that always holds the hand with the bottle and her
        # whole face (a taller 4:5 one showed less of the photo's width and cut her hand at the left edge), its top
        # faded into the hero's grey under the button.
        X = '[id$="__hero"]'
        css = (f'@media(max-width:749px){{{X} .fh-hero{{height:auto}}'
               f'{X} .fh-hero-slide--foundation,{X} .fh-hero-slide--foundation .fh-hero-slide-inner{{position:relative;inset:auto;height:auto;'
               f'display:flex;flex-direction:column}}'
               f'{X} .fh-hero-slide--foundation .fh-hero-content{{order:1;height:auto;padding:32px 0 0;justify-content:flex-start}}'
               f'{X} .fh-hero-slide--foundation .fh-hero-image{{position:relative;order:2;inset:auto;display:block;width:100%;aspect-ratio:11/12;margin-top:-24px}}'
               f'{X} .fh-hero-slide--foundation .fh-hero-image .fh-original{{left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:98.2% 0}}'
               f'{X} .fh-hero-slide--foundation .fh-hero-image:after{{background:linear-gradient(to bottom,#ededef 0,rgba(237,237,239,0) 14%)}}}}'
               # tablets: the copy, then a 16:10 window on the photo (bottle and face, cropped from its left)
               f'@media(min-width:750px) and (max-width:1023px){{{X} .fh-hero{{height:auto}}'
               f'{X} .fh-hero-slide--foundation,{X} .fh-hero-slide--foundation .fh-hero-slide-inner{{position:relative;inset:auto;height:auto;'
               f'display:flex;flex-direction:column}}'
               f'{X} .fh-hero-slide--foundation .fh-hero-content{{order:1;height:auto;padding:48px 0 24px;justify-content:flex-start}}'
               f'{X} .fh-hero-slide--foundation .fh-hero-image{{position:relative;order:2;inset:auto;display:block;width:100%;aspect-ratio:16/10}}'
               # her hair reaches the photo's top edge: its top fades into the grey only across the empty wall on the
               # left (two mask layers, added: the right part, her head, is never faded). A fade across the whole
               # width washed out her hair, a hard edge drew a line across the hero (review 3)
               f'{X} .fh-hero-slide--foundation .fh-hero-image .fh-original{{left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:100% 0;'
               f'-webkit-mask-image:linear-gradient(to bottom,transparent,#000 16%),linear-gradient(to right,transparent 34%,#000 52%);'
               f'mask-image:linear-gradient(to bottom,transparent,#000 16%),linear-gradient(to right,transparent 34%,#000 52%)}}'
               f'{X} .fh-hero-slide--foundation .fh-hero-image:after{{display:none}}}}'
               # small laptops: the export's 150%-wide photo cut her face at the right edge; the photo now fills the
               # right 62% of the banner, cropped from its right, its left edge faded into the grey
               f'@media(min-width:1024px) and (max-width:1199px){{{X} .fh-hero-slide--foundation .fh-hero-image .fh-original{{left:auto;right:0;top:0;'
               f'width:62%;height:100%;object-fit:cover;object-position:97% 20%;-webkit-mask-image:linear-gradient(to right,transparent,#000 18%);'
               f'mask-image:linear-gradient(to right,transparent,#000 18%)}}}}')
        hs = re.search(r'<section [^>]*id="shopify-section-template--[0-9]+__hero"', home)
        if hs:
            e = home.find('</style>', hs.start())
            home = home[:e] + css + home[e:]; n['phone hero stacks'] = 1
        n['hero master px'] = master.width
        n['phone hero KB'] = round(phone.stat().st_size / 1024)
        n['desktop hero KB'] = round(desk.stat().st_size / 1024)
    return home, n

def drop_fake_buyers(t):
    """"Lisa (verified tick) and 1M+ others purchased" above the title: no buyer named Lisa, no million sales. The
    rating line right under it carries the real proof. Returns (html, blocks removed)."""
    n = 0
    while True:
        m = re.search(r'<div class="product__block product__images">\s*<div class="social-proof-container">', t)
        if not m: return t, n
        t = t[:m.start()] + t[balanced_end(t, m.start(), 'div'):]; n += 1

STICKY_CSS = """
.sf-sticky{position:fixed;left:0;right:0;bottom:0;z-index:40;background:#fff;box-shadow:0 -6px 24px rgba(0,0,0,.10);
 transform:translateY(110%);transition:transform .3s ease;padding:10px 0 calc(10px + env(safe-area-inset-bottom))}
.sf-sticky.is-on{transform:none}
.sf-sticky__in{width:min(1180px,calc(100% - 32px));margin:0 auto;display:flex;align-items:center;gap:14px}
.sf-sticky img{width:52px;height:52px;border-radius:10px;object-fit:cover;background:#f4f4f2;flex:none}
.sf-sticky__txt{flex:1;min-width:0;line-height:1.3;color:#151515}
.sf-sticky__txt b{display:block;font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sf-sticky__txt span{font-size:13.5px;color:#3b3b3b}
.sf-sticky__txt i{font-style:normal;color:#00b67a;letter-spacing:1px}
.sf-sticky__btn{flex:none;display:inline-flex;align-items:center;justify-content:center;padding:14px 26px;border-radius:999px;background:#151515;
 color:#fff!important;text-decoration:none!important;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
@media (max-width:599px){.sf-sticky__txt b{font-size:14px}.sf-sticky__btn{padding:13px 18px;font-size:12px}}
"""

def sticky_bar(t, img, title, price_line, button, rating=None):
    """The product page's sticky bar, rebuilt: the export's #sticky_atcs was never shown (the app script that showed
    it did not come with the export) and its prices were bound to the wrong product. This one slides up once the buy
    box's add-to-cart button has scrolled out of view, and its button goes back to the pack picker (#apf-buy).
    price_line is plain text ("From $37 · Free shipping"), so the theme build leaves it as written."""
    m = re.search(r'<div id="sticky_atcs"', t)
    if not m: return t, False
    stars = (f' <i aria-hidden="true">&#9733;</i> {rating[0]:.1f} ({int(rating[1]):,})') if rating else ''
    bar = (f'<style>{STICKY_CSS}</style><div class="sf-sticky" id="sf-sticky" aria-hidden="true">'
           f'<div class="sf-sticky__in"><img src="{img}" alt="" width="52" height="52" loading="lazy" decoding="async">'
           f'<div class="sf-sticky__txt"><b>{html.escape(title)}</b><span>{html.escape(price_line)}{stars}</span></div>'
           f'<a class="sf-sticky__btn" href="#apf-buy" tabindex="-1">{html.escape(button)}</a></div>'
           '<script>(function () {'
           'var bar = document.currentScript.parentNode;'
           'function start() {'
           'var btn = document.querySelector("form[data-product-form] [data-add-to-cart]") || document.querySelector("#apf-buy");'
           'if (!btn || !("IntersectionObserver" in window)) return;'
           'new IntersectionObserver(function (es) { var e = es[0], on = !e.isIntersecting && e.boundingClientRect.top < 0;'
           'bar.classList.toggle("is-on", on); bar.setAttribute("aria-hidden", on ? "false" : "true");'
           'bar.querySelector("a").tabIndex = on ? 0 : -1;'
           # while it shows, the page ends that much lower: the footer's last line and the payment icons stay above it
           'document.body.style.paddingBottom = on ? bar.offsetHeight + "px" : ""; }).observe(btn); }'
           'if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();'
           '})();</script></div>')
    return t[:m.start()] + bar + t[balanced_end(t, m.start(), 'div'):], True

def sticky_thumb(src, name):
    """A 104 px square thumbnail on white (a transparent packshot would turn black as a JPEG)."""
    from PIL import Image
    im = Image.open(src).convert('RGBA')
    s = max(im.size); sq = Image.new('RGBA', (s, s), (255, 255, 255, 255))
    sq.alpha_composite(im, ((s - im.width) // 2, (s - im.height) // 2))
    out = DST / 'assets' / 'img' / f'{name}.jpg'
    sq.convert('RGB').resize((104, 104), Image.LANCZOS).save(out, quality=86, optimize=True)
    final = out.with_name(f"{name}-{hashlib.md5(out.read_bytes()).hexdigest()[:6]}.jpg"); out.rename(final)
    return f'../assets/img/{final.name}'

def honest_pdp(t, summary):
    """The foundation page's buy box and results, without claims nothing backs:
    - the "89% sold / ends in" countdown and "Selling out fast" (they reset on every visit) go;
    - "Shipped today" becomes "Free shipping on every order" (every order ships free; the dispatch day is not promised);
    - the "Real results" cards cited "an eight-week independent customer panel" (97% / 98% / 95%) that no document
      backs: they show the verified reviews' own numbers instead (average, share of 5 stars, share of 4 and 5 stars);
    - the gallery slide with the same panel numbers goes."""
    n = {}
    for rx in (r'<div class="product__block countdown-timer-wrapper">', r'<div class="product__block"[^>]*><div class="product__subheading">\s*<p><strong>Selling out fast'):
        m = re.search(rx, t)
        if m:
            t = t[:m.start()] + t[balanced_end(t, m.start(), 'div'):]; n[rx[:40]] = 1
    t, n['shipped today'] = re.subn(r'data-default-usp="Shipped today"', 'data-default-usp="Free shipping on every order"', t)
    t, k = re.subn(r'(<span id="shippingUspText"[^>]*>)Shipped today(</span>)', r'\1Free shipping on every order\2', t); n['shipped today'] += k
    if summary:
        c, d, avg = int(summary['count']), summary['distribution'], float(summary['average'])
        five, four = int(d.get('5', d.get(5, 0))), int(d.get('4', d.get(4, 0)))
        pct = lambda v: f'{int(v * 1000 / c) / 10:g}%'          # floored to a tenth: never rounds up
        cards = [('97%', 'Said it instantly matched their skin tone', f'{avg:.1f}/5', f'Average rating from {c:,} verified reviews'),
                 ('98%', 'Said their blemishes became invisible', pct(five), 'Gave it the full five stars'),
                 ('95%', 'Loved that it didn’t feel heavy or mask-like', pct(five + four), 'Rated it four or five stars')]
        m = re.search(r'<div class="shopify-section" id="shopify-section-template--[0-9]+__kopstorm_results_[^"]*">', t)
        if m:
            end = balanced_end(t, m.start(), 'div')
            sec = t[m.start():end]
            for old_v, old_l, new_v, new_l in cards:
                sec = sec.replace(f'>{old_v}<', f'>{new_v}<').replace(old_l, new_l)
            sec = sec.replace('Based on an eight-week independent customer panel', 'From verified buyers of the same formula')
            n['results'] = int(sec != t[m.start():end])
            t = t[:m.start()] + sec + t[end:]
    # the gallery slides (and their thumbnails) that repeat the panel numbers, and "Even better together": the
    # foundation with a pink blending brush the store does not sell (its free gift is a sponge)
    for cls in ('product-single__media-slide', 'product-single__thumbnail'):
        for m in reversed(list(re.finditer(r'<div class="%s[^"]*"[^>]*>' % cls, t))):
            end = balanced_end(t, m.start(), 'div')
            if any(k in t[m.start():end] for k in ('ColorChangingFoundation-Productimagesphotos_2_1791540a',
                                                   'ColorChangingFoundation-Productimagesphotos_1_87f31fb4')):
                t = t[:m.start()] + t[end:]; n['gone slides'] = n.get('gone slides', 0) + 1
    return t, n

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
    rules = [(f, o, n) for f, rs in ccf_copy.PAGE.items() for o, n in rs] + [(None, o, n) for o, n in ccf_copy.GLOBAL + brush_copy.GLOBAL + balm_copy.GLOBAL + serum_copy.GLOBAL]
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
    gone = ('ColorChangingFoundation-Productimagesphotos_2_1791540a', 'ColorChangingFoundation-Productimagesphotos_1_87f31fb4')
    data['images'] = [u for u in ordered + [u for u in imgs if u not in ordered] if not any(g in u for g in gone)]
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
    # the homepage's "Recommended by a dermatologist" is a verified buyer's words now (customer_voice); the product
    # page goes from the solution to the K-beauty science (apf_copy.KBEAUTY: the actives on the label, no person),
    # its customer reviews before the FAQ, more FAQ answers
    texts[DST / 'index.html'] = customer_voice(texts.get(DST / 'index.html', ''))
    home = texts[DST / 'index.html']
    ps_at = texts[pdp].find('id="shopify-section-sf-problem-solution"')
    if ps_at < 0: missing.append(('k-beauty', 'problem/solution anchor'))
    else:
        kb = section_image(BRAND / 'adaptive-peptide-foundation' / 'composites' / 'label-detail-2x.jpg', 'skinofab-kbeauty-label', (930, 1162))   # the whole label, sharp at 2x
        # its picture is the "how it works" loop (tools/persona/howto_video.py), the label close-up its fallback
        howto = BRAND / 'adaptive-peptide-foundation' / 'howto'
        video = ((hashed_copy(howto / 'howto.mp4', 'media', 'skinofab-howto-foundation'), hashed_copy(howto / 'howto-poster.jpg', 'img', 'skinofab-howto-poster'),
                  864, 1080, 'Illustration: the foundation goes on white and blends into her skin tone')
                 + ((hashed_copy(howto / 'howto.webm', 'media', 'skinofab-howto-foundation'),) if (howto / 'howto.webm').exists() else ())
                 if (howto / 'howto.mp4').exists() else None)
        ps_end = balanced_end(texts[pdp], texts[pdp].rfind('<div', 0, ps_at), 'div')
        texts[pdp] = texts[pdp][:ps_end] + '<div class="shopify-section" id="shopify-section-sf-kbeauty">' + apf_copy.kbeauty_html(kb, video=video) + '</div>' + texts[pdp][ps_end:]
    revs = video_reviews(home)
    faq = re.search(r'<div class="shopify-section" id="shopify-section-template--[0-9]+__section_accordions_', texts[pdp])
    if not revs or not faq: missing.append(('reviews', 'homepage section or FAQ anchor'))
    else:
        # before the FAQ: "Formulated in Korea" (a model in a lab coat with the bottle), the clips, then the review wall
        doctor = BRAND / 'adaptive-peptide-foundation' / 'doctor.jpg'
        korea = ('<div class="shopify-section" id="shopify-section-sf-korea">'
                 + apf_copy.korea_html(crop_to(doctor, 'skinofab-korea-lab', (1000, 1250), (0.5, 0.3))) + '</div>') if doctor.exists() else ''
        if not korea: missing.append(('korea', 'doctor.jpg'))
        texts[pdp] = (texts[pdp][:faq.start()] + korea + '<div class="shopify-section" id="shopify-section-sf-reviews">' + revs + '</div>'
                      + '<div class="shopify-section" id="shopify-section-sf-review-wall">' + review_wall() + '</div>' + texts[pdp][faq.start():])
    texts[pdp], ok = faq_more(texts[pdp])
    if not ok: missing.append(('faq', 'accordion columns'))
    found = review_data()
    texts[pdp], ok = rating_block(texts[pdp], found and found['summary'])
    if not ok: missing.append(('rating', 'loox badge'))
    cta = texts[pdp].find('<div id="CTA_kopstorm">')
    if cta < 0: missing.append(('trust block', 'CTA_kopstorm'))
    else:
        end = balanced_end(texts[pdp], cta, 'div')
        texts[pdp] = texts[pdp][:end] + trust_block() + texts[pdp][end:]
    # the testimonial slider: real verified reviews with their own photos instead of the design's persona stories
    texts[pdp], n_t = real_testimonials(texts[pdp])
    if n_t < 6: missing.append(('testimonials', f'{n_t} of 6 real reviews'))
    print('testimonials', n_t)
    # the foundation page without claims nothing backs (countdown, panel numbers, "Shipped today")
    texts[pdp], hp = honest_pdp(texts[pdp], found and found['summary'])
    print('honest pdp', hp)
    pack = ccf_copy.PACKS[0]
    texts[pdp], ok = sticky_bar(texts[pdp], sticky_thumb(BRAND / 'adaptive-peptide-foundation' / 'next' / '01-front.jpg', 'skinofab-apf-sticky'),
                                'Adaptive Peptide Foundation',
                                f"From {brush_copy.money(pack['refill'] if ccf_copy.REFILL.get('default') else pack['price'])} · Free shipping",
                                'Choose your pack', found and (float(found['summary']['average']), int(found['summary']['count'])))
    if not ok: missing.append(('sticky bar', 'foundation #sticky_atcs'))
    buyers = 0
    for p in [p for p in texts if p.parent.name == 'products']:
        texts[p], k = drop_fake_buyers(texts[p]); buyers += k
    print('fake buyer lines removed', buyers)
    # real review and customer counts everywhere (the foundation's imported reviews are the store's real total)
    if found:
        print('honest counts', honest_counts(texts, found['summary']))
    # homepage speed: lazy hidden hero slides, right-sized shelf cards, a phone hero that only carries what shows
    if DST / 'index.html' in texts:
        texts[DST / 'index.html'], sp = faster_home(texts[DST / 'index.html'])
        print('home speed', sp)
    # the second products (the Lymphatic Brush, the PDRN Plumping Balm, the EGF + NAD+ Firming Serum): a card in the
    # homepage's product shelf, like the other products, their pages (brush_copy, balm_copy, serum_copy) and snapshots
    for P in SECOND_PRODUCTS:
        if DST / 'index.html' in texts:
            texts[DST / 'index.html'], ok = product_shelf(texts[DST / 'index.html'], P)
            if not ok: missing.append((P.KEY, 'homepage shelf list or tab'))
        page = DST / 'products' / f'{P.HANDLE}.html'
        texts[page], _ = drop_fake_buyers(product_page(base_pdp, P, texts[pdp], found))
        shots = dict(re.findall(rf'\.\./assets/img/({re.escape(P.IMG_PREFIX)}-(\d+)-1080w-[0-9a-f]{{6}}\.jpg)', texts[page]))
        gallery = sorted(set(shots), key=lambda g: int(shots[g]))
        (DST / 'products' / f'{P.HANDLE}.js').write_text(json.dumps(product_snapshot(P, ['/assets/img/' + g for g in gallery])))
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
    print('page images', page_images())
    # the real company (company.py) on every page and data file: footer, contact and legal pages, FAQs, product data
    co, co_files = 0, 0
    for p in sorted(DST.rglob('*')):
        if p.is_file() and p.suffix.lower() in ('.html', '.js', '.json'):
            t0 = p.read_text(encoding='utf-8', errors='surrogateescape')
            t1, k = company.rewrite(p.relative_to(DST).as_posix(), t0)
            if k: p.write_text(t1, encoding='utf-8', errors='surrogateescape'); co += k; co_files += 1
    print('company details', co, 'changes in', co_files, 'files')
    stale = re.compile(r'Skinofab LLC|8605 Santa Monica|West Hollywood|(?:hey|info|contact)@skinofab\.com|Xevio|John M\. Schneider|12345678|HRB 123456|Anna Becker|Musterstra')
    left = [p.relative_to(DST).as_posix() for p in DST.rglob('*') if p.is_file() and p.suffix.lower() in ('.html', '.js', '.json')
            and stale.search(p.read_text(encoding='utf-8', errors='surrogateescape'))]
    if left: missing.append(('company details', 'old details left in ' + ', '.join(left[:8])))
    fixed = honest_images(found and found['summary'])
    if not fixed: missing.append(('honest images', 'gallery photos to fix'))
    print('honest images', fixed)
    whitened = white_backdrops()
    if not whitened: missing.append(('white backdrops', 'foundation photos to whiten'))
    print('white backdrops', whitened)
    relabelled = relabel_bottles_on_pages()
    if not relabelled: missing.append(('real wordmark', 'foundation bottles to relabel'))
    print('real wordmark', relabelled)
    print('home features', home_features())
    print('home phenomenon', home_phenomenon())
    print('video cards', honest_video_cards())
    sp, sp_gone = support_pages()
    missing.extend(('support pages', f'{r}: {q}') for r, q in sp_gone)
    print('support pages', sp)
    print('home original', home_original())
    print('layout fixes', layout_fixes())
    print('local location', local_location())
    print('track form', track_form())
    forms = working_forms()
    if not forms: missing.append(('forms', 'newsletter / contact / country forms'))
    print('working forms', forms)
    banners = listing_banners()
    if not banners: missing.append(('listing banners', 'collections banner'))
    print('listing banners', banners)
    pruned = only_our_products()
    left = [p.relative_to(DST).as_posix() for p in DST.rglob('*.html')
            if re.search(r'href="[^"]*products/(?!(?:%s)\.html)[a-z0-9-]+\.html' % '|'.join(map(re.escape, OUR_PRODUCTS)),
                         p.read_text(encoding='utf-8', errors='surrogateescape'))]
    if left: missing.append(('other products', 'links left in ' + ', '.join(left[:6])))
    print('only our products', pruned)
    print('menu', clean_menu())
    print('alts', clean_alts())
    print('dead social links', drop_dead_social())
    evened = even_shelf()
    if not evened: missing.append(('even shelf', 'shelf cards to size'))
    print('even shelf cards', evened)
    zoomed = zoom_links()
    if not zoomed: missing.append(('lightbox', 'gallery zoom links'))
    print('gallery zoom links', zoomed)
    print(json.dumps({'rules': len(rules), 'replacements': sum(hits.values()), 'images': replaced, 'missing': missing}, ensure_ascii=False, indent=1))
    if missing: sys.exit(1)

main()
