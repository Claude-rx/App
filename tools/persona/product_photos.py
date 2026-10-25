"""The second products' page images, laid out like the Adaptive Peptide Foundation's gallery, on pure white.

usage: python3 -I product_photos.py [balm] [serum] [brush] [foundation]      # all four when none is named
  balm   brand/pdrn-balm/source/*.jpg -> brand/pdrn-balm/*.jpg (the AI-drawn wordmark on each stick replaced first:
         relabel_bottles.BALM -> brand/pdrn-balm/labelled/)
  serum  brand/egf-nad-serum/source/*.jpg -> brand/egf-nad-serum/*.jpg (the real label printed on first, see below)
  brush  brand/lymphatic-brush/source/ba-puffy.jpg -> brand/lymphatic-brush/ba-puffy.jpg
  foundation  its bottle render + source/others.jpg -> brand/adaptive-peptide-foundation/vs-others.jpg (the gallery's
         "skinofab vs. others" on white; apply_persona.py puts it in place of the black one), and the NEXT product's
         gallery on white -> brand/adaptive-peptide-foundation/next/*.jpg (FOUNDATION_NEXT)

Sources (brand/<product>/source/) are photoreal images made with GPT Image 2.5 (Figma's image generator); their
prompts are in image_prompts.json. The serum's were made with its packaging blank: label_composite.py prints
SKINOFAB's real wordmark and label on each bottle and carton (SERUM_LABELS: where they are in each photo), so the logo
is ours to the pixel. This script then crops and lays them out: the headline type is Playfair Display (the foundation
gallery's serif), the small type Montserrat, the Korean badge the one cut from the foundation's hero photo
(assets/korea-badge.png). The before/after photos are illustrations, and say so on the image, as the foundation's
"What's inside" and "The Science" images do. Every photo's backdrop is made pure white first (white_bg.light), so all
the products' pages share one white.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import label_composite, relabel_bottles, white_bg
BRAND = HERE.parents[1] / 'brand'
BALM, SERUM, BRUSH = BRAND / 'pdrn-balm', BRAND / 'egf-nad-serum', BRAND / 'lymphatic-brush'
FOUNDATION = BRAND / 'adaptive-peptide-foundation'
FONTS = HERE / 'assets' / 'fonts'
W = 1080
INK, SOFT, LINE, PAPER = (21, 21, 21), (96, 96, 96), (214, 214, 214), (255, 255, 255)
ILLUSTRATIVE = 'Image only for illustrative purposes'


def serif(size, weight='Bold', italic=False):
    f = ImageFont.truetype(str(FONTS / ('PlayfairDisplay-Italic-VF.ttf' if italic else 'PlayfairDisplay-VF.ttf')), size)
    f.set_variation_by_name(f'{weight} Italic' if italic else weight)
    return f


def sans(size, weight='Medium'):
    f = ImageFont.truetype(str(FONTS / 'Montserrat-VF.ttf'), size)
    f.set_variation_by_name(weight)
    return f


def path_of(product, name):
    """A product photo: the serum's with its label printed on (brand/egf-nad-serum/<name>.jpg), the balm's with the
    real wordmark in place of the AI-drawn one (brand/pdrn-balm/labelled/<name>.jpg), the foundation's
    bottle renders (brand/adaptive-peptide-foundation/<name>.png), else the source."""
    if product == SERUM and name in SERUM_LABELS: return product / f'{name}.jpg'
    if product == BALM and name in relabel_bottles.BALM: return product / 'labelled' / f'{name}.jpg'
    if product == FOUNDATION and (product / f'{name}.png').exists(): return product / f'{name}.png'
    return product / 'source' / f'{name}.jpg'


def photo(product, name):
    """A product photo with its backdrop made pure white (white_bg.light): every product's images share one white.
    The serum's labelled photos were made white when they were labelled (once: the ramp is not idempotent)."""
    path = path_of(product, name)
    im = Image.open(path).convert('RGB')
    if product == SERUM and name in SERUM_LABELS: return im
    return white_bg.matte(im) if path.suffix == '.png' else white_bg.light(im)    # the renders' backdrop is a grey sweep


def src(product, name, size=W):
    """A product photo fitted to a size x size square."""
    return ImageOps.fit(photo(product, name), (size, size), Image.LANCZOS)


def save(im, product, name):
    im.convert('RGB').save(product / f'{name}.jpg', quality=90, optimize=True, progressive=True)
    print(product.name, name, im.size)


def note(d, xy, text=ILLUSTRATIVE, fill=SOFT, anchor='ms', size=17):
    d.text(xy, text, font=sans(size, 'Regular'), fill=fill, anchor=anchor)


def labels(im, pairs, size=34):
    """White words with a soft shadow ('Before' / 'After' at the bottom left of each half, as on the foundation's)."""
    d = ImageDraw.Draw(im)
    for x, y, text in pairs:
        f = sans(size, 'SemiBold')
        shadow = Image.new('L', im.size, 0)
        ImageDraw.Draw(shadow).text((x, y), text, font=f, fill=150, anchor='ls')
        im.paste((0, 0, 0), mask=shadow.filter(ImageFilter.GaussianBlur(6)).point(lambda v: v // 2))
        d.text((x, y), text, font=f, fill=PAPER, anchor='ls')
    return im


def check(d, cx, cy, r, ok=True, fill=INK, mark=PAPER):
    """A filled round tick (or cross) of radius r."""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    w = max(2, round(r * 0.22))
    if ok:
        d.line([(cx - r * .45, cy + r * .02), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)], fill=mark, width=w, joint='curve')
    else:
        for s in (1, -1):
            d.line([(cx - r * .38, cy - r * .38 * s), (cx + r * .38, cy + r * .38 * s)], fill=mark, width=w)


def icon(d, kind, cx, cy, r=24):
    """Thin line icons for the panel images."""
    w = 3
    if kind == 'sparkle':
        for (x, y, s) in ((cx, cy, r), (cx + r * .95, cy - r * .9, r * .42)):
            d.polygon([(x, y - s), (x + s * .22, y - s * .22), (x + s, y), (x + s * .22, y + s * .22),
                       (x, y + s), (x - s * .22, y + s * .22), (x - s, y), (x - s * .22, y - s * .22)], outline=INK, width=w)
    elif kind == 'drop':
        d.arc((cx - r * .72, cy - r * .2, cx + r * .72, cy + r * 1.05), 200, 340 + 360, fill=INK, width=w)
        d.line([(cx - r * .66, cy + r * .2), (cx, cy - r * 1.05), (cx + r * .66, cy + r * .2)], fill=INK, width=w, joint='curve')
    elif kind == 'stick':
        d.rounded_rectangle((cx - r * .34, cy - r * .35, cx + r * .34, cy + r * 1.05), radius=4, outline=INK, width=w)
        d.chord((cx - r * .3, cy - r * 1.05, cx + r * .3, cy - r * .1), 180, 360, outline=INK, width=w)
        d.line([(cx - r * .3, cy - r * .55), (cx - r * .3, cy - r * .35)], fill=INK, width=w)
        d.line([(cx + r * .3, cy - r * .55), (cx + r * .3, cy - r * .35)], fill=INK, width=w)
    elif kind == 'dropper':
        d.rounded_rectangle((cx - r * .45, cy - r * .1, cx + r * .45, cy + r * 1.05), radius=6, outline=INK, width=w)
        d.rectangle((cx - r * .22, cy - r * .45, cx + r * .22, cy - r * .1), outline=INK, width=w)
        d.ellipse((cx - r * .16, cy - r * 1.05, cx + r * .16, cy - r * .45), outline=INK, width=w)


BADGE_LINES = label_composite.ORIGIN_LINES


def korea_badge(im, cx=948, cy=148):
    """The gallery's origin badge: the flag circle (cut from the foundation's hero photo) and "Formulated in Korea /
    Advanced formula" under it."""
    flag = Image.open(HERE / 'assets' / 'korea-badge.png').convert('RGBA')
    shadow = Image.new('L', im.size, 0)
    ImageDraw.Draw(shadow).ellipse((cx - 72, cy - 68, cx + 72, cy + 78), fill=55)
    im.paste((0, 0, 0), mask=shadow.filter(ImageFilter.GaussianBlur(9)))
    im.paste(flag, (cx - flag.width // 2, cy - flag.height // 2), flag)
    d = ImageDraw.Draw(im)
    for k, line in enumerate(BADGE_LINES):
        d.text((cx, cy + 108 + k * 29), line, font=sans(23, 'Regular'), fill=INK, anchor='ms')


def cutout(product, name, thresh=244):
    """The product on a white photo, as RGBA (everything near-white goes transparent, edges feathered)."""
    im = photo(product, name)
    g = ImageOps.grayscale(im).point(lambda v: 255 if v < thresh else 0).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert('RGBA'); out.putalpha(g)
    return out.crop(g.getbbox())


# ------------------------------------------------------------------------------------------------ layouts
def hero(product, name, badge=(948, 148)):
    im = src(product, name)
    korea_badge(im, *badge)
    save(im, product, 'hero')


def before_after(product, name, out, note_text=ILLUSTRATIVE):
    im = src(product, name)
    labels(im, [(34, W - 40, 'Before'), (W // 2 + 34, W - 40, 'After')])
    labels(im, [(W // 2 + 34, W - 82, note_text)], size=17)
    save(im, product, out)


def panel(product, name, title, rows, out):
    """A photo with the person on the right and the left half white: a two-line serif title and three icon rows."""
    im = src(product, name)
    d = ImageDraw.Draw(im)
    size = 84                                           # the title fits the white half
    while size > 48 and max(d.textlength(title[0], font=serif(size)), d.textlength(title[1], font=serif(size, italic=True))) > 470:
        size -= 2
    d.text((70, 150), title[0], font=serif(size, 'Bold'), fill=INK, anchor='ls')
    d.text((70, 150 + round(size * 100 / 84)), title[1], font=serif(size, 'Bold', italic=True), fill=INK, anchor='ls')
    for k, (kind, a, b) in enumerate(rows):
        y = 380 + k * 130
        icon(d, kind, 104, y + 4)
        d.text((160, y - 4), a, font=sans(32, 'Medium'), fill=INK, anchor='ls')
        d.text((160, y + 36), b, font=sans(32, 'Medium'), fill=INK, anchor='ls')
    save(im, product, out)


def results_grid(product, pairs, title):
    im = Image.new('RGB', (W, W), PAPER)
    d = ImageDraw.Draw(im)
    d.text((64, 118), title[0], font=serif(66, 'Bold'), fill=INK, anchor='ls')
    d.text((64, 196), title[1], font=serif(66, 'Bold', italic=True), fill=INK, anchor='ls')
    tw, th, gap, x0, y0 = 452, 312, 48, 64, 252
    for k, name in enumerate(pairs):
        x, y = x0 + (k % 2) * (tw + gap), y0 + (k // 2) * (th + 90)
        im.paste(ImageOps.fit(photo(product, name), (tw, th), Image.LANCZOS), (x, y))
        d.text((x + 6, y + th + 32), 'Before', font=sans(21, 'Regular'), fill=SOFT, anchor='ls')
        d.text((x + tw // 2 + 6, y + th + 32), 'After', font=sans(21, 'Regular'), fill=SOFT, anchor='ls')
    note(d, (W // 2, W - 22), ILLUSTRATIVE + '. Results vary.')
    save(im, product, 'results-grid')


def whats_inside(product, name, rows, size=700):
    im = Image.new('RGB', (W, W), PAPER)
    im.paste(src(product, name, size), (W - size, W - size))
    d = ImageDraw.Draw(im)
    d.text((64, 150), 'What’s', font=serif(80, 'Bold'), fill=INK, anchor='ls')
    d.text((64, 240), 'inside', font=serif(80, 'Bold'), fill=INK, anchor='ls')
    for k, (a, b) in enumerate(rows):
        y = 380 + k * 126
        d.text((64, y), a, font=sans(31, 'Medium'), fill=INK, anchor='ls')
        end = 64 + d.textlength(a, font=sans(31, 'Medium')) + 16
        if end < 400: d.line([(end, y - 10), (460, y - 10)], fill=INK, width=2)
        d.text((64, y + 34), b, font=sans(19, 'Regular'), fill=SOFT, anchor='ls')
    note(d, (W - 60, W - 28), anchor='rs')
    save(im, product, 'whats-inside')


def science(product, name, lines):
    im = src(product, name)
    fade = Image.linear_gradient('L').resize((W, 330)).point(lambda v: 255 - v)       # opaque at the top
    im.paste(PAPER, (0, 0, W, 330), fade.point(lambda v: min(255, int(v * 1.35))))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 120), 'The Science', font=serif(76, 'Bold'), fill=INK, anchor='ms')
    for k, line in enumerate(lines):
        d.text((W // 2, 190 + k * 40), line, font=sans(27, 'Regular'), fill=INK, anchor='ms')
    note(d, (W // 2, W - 26))
    save(im, product, 'science')


def vs_others(product, ours, others, others_label, why, rows, others_thresh=240, others_h=200):
    """'skinofab vs. others': the product in a light highlight column, a generic one beside it, tick rows."""
    im = Image.new('RGB', (W, W), PAPER)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 112), 'skinofab', font=serif(70, 'Bold', italic=True), fill=INK, anchor='rs')
    d.text((W // 2 + 14, 112), 'vs. others', font=serif(70, 'Bold', italic=True), fill=INK, anchor='ls')
    col1, col2, top = 640, 880, 170
    d.rounded_rectangle((col1 - 110, top, col1 + 110, W - 110), radius=26, fill=(240, 240, 239))
    ours_im = cutout(product, ours); ours_im.thumbnail((150, 300), Image.LANCZOS)
    im.paste(ours_im, (col1 - ours_im.width // 2, top + 24), ours_im)
    oth = cutout(product, others, others_thresh); oth.thumbnail((200, others_h), Image.LANCZOS)
    im.paste(oth, (col2 - oth.width // 2, top + 24 + 300 - oth.height), oth)
    for k, (text, italic) in enumerate(why):
        d.text((64, top + 150 + k * 56), text, font=serif(44, 'Bold', italic=italic), fill=INK, anchor='ls')
    d.text((col1, top + 368), 'SKINOFAB', font=sans(22, 'SemiBold'), fill=INK, anchor='ms')
    d.text((col2, top + 368), others_label, font=sans(22, 'Regular'), fill=SOFT, anchor='ms')
    for k, text in enumerate(rows):
        y = top + 440 + k * 112
        d.line([(64, y - 52), (W - 64, y - 52)], fill=LINE, width=1)
        d.multiline_text((64, y - 8 - (16 if '\n' in text else 0)), text, font=sans(30, 'Medium'), fill=INK, anchor='ls', spacing=8)
        check(d, col1, y - 14, 22, True)
        check(d, col2, y - 14, 22, False, (200, 200, 200))
    save(im, product, 'vs-others')


def plain(product, name, out=None):
    save(src(product, name), product, out or name)


# ------------------------------------------------------------------------------------------------ products



def balm():
    P = BALM
    (P / 'labelled').mkdir(exist_ok=True)
    for name, ops in relabel_bottles.BALM.items():      # the real wordmark first, on every stick (relabel_bottles.BALM)
        relabel_bottles.relabel(Image.open(P / 'source' / f'{name}.jpg'), ops).save(P / 'labelled' / f'{name}.jpg', quality=95)
        print('relabelled', name)
    hero(P, 'pack')
    plain(P, 'hold-cheek')
    before_after(P, 'ba-eye', 'before-after')
    panel(P, 'panel', ('Look Less', 'Tired'), [('sparkle', 'Smoother-looking', 'in seconds'), ('drop', 'Hydrates and', 'cushions'),
                                              ('stick', 'Press on,', 'no fingers')], 'look-less-tired')
    results_grid(P, ['ba-eye', 'ba-smile', 'ba-crows', 'ba-lips'], ('Swipe, press,', 'rested.'))
    whats_inside(P, 'swatch', [('PDRN', 'Salmon DNA, the K-beauty skin booster'), ('Volufiline™', 'For areas that look hollow'),
                               ('Collagen + hyaluronic acid', 'Cushions the look of lines')])
    science(P, 'science', ('PDRN and Volufiline™ in a balm that melts on contact.',
                           'Press it on: it cushions the look of hollows and lines',
                           'while it hydrates, right where you need it.'))
    vs_others(P, 'tall', 'jar', 'A jar of cream', [('Why a press-on', False), ('stick works where', False), ('a jar doesn’t', True)],
              ['Goes exactly where\nyou need it', 'No fingers, no mess', 'Fits in your bag', 'Works over makeup'])
    for n in ('apply-eye', 'hold-chin', 'friends', 'apply-lips', 'bag'):
        plain(P, n)
    before_after(P, 'ba-smile', 'ba-smile')
    plain(P, 'pack', 'card')


# where the serum's blank bottle (roi) and carton front (box) are in each photo; blur: out-of-focus bottles
SERUM_LABELS = {
    'pack': [dict(roi=(225, 160, 478, 905), box=(492, 150, 738, 848))],
    'tall': [dict()],
    'hold-cheek': [dict(roi=(200, 300, 360, 690))],
    'hold-black': [dict(roi=(140, 320, 310, 740))],
    'drop': [dict(roi=(190, 640, 400, 1024), blur=0.8)],
    'friends': [dict(roi=(770, 320, 860, 600))],
    'panel': [dict(roi=(550, 410, 670, 730))],
    'mirror': [dict(roi=(520, 600, 620, 890), blur=0.4)],
    'temple': [dict(roi=(140, 180, 300, 600))],
    'swatch': [dict(roi=(540, 0, 850, 630), blur=0.5)],
    'trio': [dict(roi=(100, 120, 355, 870)), dict(roi=(365, 120, 620, 870)), dict(roi=(628, 120, 885, 870))],
}


def serum():
    P = SERUM
    for name, bottles in SERUM_LABELS.items():         # the real label first, on every bottle and carton
        im = Image.open(P / 'source' / f'{name}.jpg')
        for b in bottles:
            im = label_composite.composite(im, 'serum', b.get('roi'), b.get('box'), blur=b.get('blur', 0.0))
        im = white_bg.light(im)
        im.save(P / f'{name}.jpg', quality=92, optimize=True, progressive=True)
        print('labelled', name)
    hero(P, 'pack', badge=(140, 132))                 # the carton fills the top right
    plain(P, 'hold-cheek')
    before_after(P, 'ba-jaw', 'before-after')
    panel(P, 'panel', ('Firmer-Looking', 'Skin'), [('sparkle', 'Smoother-looking', 'with daily use'), ('drop', 'Deep, light', 'hydration'),
                                                  ('dropper', 'Two drops,', 'morning and night')], 'look-firmer')
    results_grid(P, ['ba-jaw', 'ba-cheeks', 'ba-neck', 'ba-glow'], ('Firmer, smoother,', 'brighter-looking.'))
    whats_inside(P, 'swatch', [('EGF', 'sh-Oligopeptide-1, for renewed-looking skin'), ('NAD+', 'For skin that looks tired and dull'),
                               ('Collagen', 'For firmer-feeling, plumper-looking skin')], size=610)
    science(P, 'science', ('EGF, NAD+ and collagen in a light serum that sinks in.',
                           'Two drops, face and neck: skin looks smoother, firmer',
                           'and more radiant with daily use.'))
    vs_others(P, 'tall', 'others', 'A basic serum', [('Why one serum', False), ('does the work', False), ('of three', True)],
              ['EGF + NAD+ + collagen\nin one bottle', 'Made for skin after 45', 'Light, sinks in\nin a minute', 'Face and neck'],
              others_thresh=246, others_h=230)
    for n in ('drop', 'hold-black', 'friends', 'apply-neck', 'trio'):
        plain(P, n)
    before_after(P, 'ba-cheeks', 'ba-cheeks')
    plain(P, 'pack', 'card')


def brush():
    before_after(BRUSH, 'ba-puffy', 'ba-puffy')


# the foundation's NEXT gallery: the bottle renders (on the floor: a contact shadow each), the pump close-up, two women
FOUNDATION_NEXT = [(FOUNDATION / '01-front.png', True), (FOUNDATION / '03-three-quarter-right.png', True),
                   (FOUNDATION / 'composites' / 'two-bottles.jpg', True), (FOUNDATION / '09-pump-detail.png', False),
                   (FOUNDATION / '02-three-quarter-left.png', True), (BRAND / 'persona' / 'age-109.jpg', False),
                   (BRAND / 'persona' / 'pdp-duo-women.jpg', False)]


def foundation():
    """The foundation gallery's "skinofab vs. others" was white on black: the same board on white, as the other
    products' (its three rows, with the other gallery panel's "won't settle into lines"). The other bottle is a blank,
    generic one (source/others.jpg): the old board's showed another brand's name."""
    vs_others(FOUNDATION, '01-front', 'others', 'A basic foundation', [('One shade that', False), ('adapts to', False), ('your skin', True)],
              ['Adapts to\nskin tone', 'Hydrating\nserum base', 'Won’t settle\ninto lines', 'Fragrance-free'],
              others_thresh=246, others_h=210)
    # the NEXT product's gallery (cart and checkout thumbnails, in this order) on the same white: next/<name>.jpg
    out = FOUNDATION / 'next'; out.mkdir(exist_ok=True)
    for path, shadow in FOUNDATION_NEXT:
        im = white_bg.matte(Image.open(path).convert('RGB'), shadow=shadow)
        im.save(out / f'{path.stem}.jpg', quality=92, optimize=True, progressive=True)
        print('next', path.stem, im.size)


if __name__ == '__main__':
    which = sys.argv[1:] or ['balm', 'serum', 'brush', 'foundation']
    for w in which: {'balm': balm, 'serum': serum, 'brush': brush, 'foundation': foundation}[w]()
