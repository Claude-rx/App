"""The second products' page images, laid out like the Adaptive Peptide Foundation's gallery, on pure white.

usage: python3 -I product_photos.py [balm] [serum] [brush] [foundation] [stick]     # all when none is named
  balm   brand/pdrn-balm/source/*.jpg -> brand/pdrn-balm/*.jpg (the AI-drawn wordmark on each stick replaced first:
         relabel_bottles.BALM -> brand/pdrn-balm/labelled/)
  serum  brand/egf-nad-serum/source/*.jpg -> brand/egf-nad-serum/*.jpg (the real label printed on first, see below)
  brush  brand/lymphatic-brush/source/ba-puffy.jpg -> brand/lymphatic-brush/ba-puffy.jpg
  stick  brand/foundation-stick/source/*.jpg -> brand/foundation-stick/*.jpg (the real wordmark on every tube first:
         relabel_bottles.STICK -> brand/foundation-stick/labelled/)
  foundation  its bottle render + source/others.jpg -> brand/adaptive-peptide-foundation/vs-others.jpg (the gallery's
         "skinofab vs. others" on white; apply_persona.py puts it in place of the black one), and the NEXT product's
         gallery on white -> brand/adaptive-peptide-foundation/next/*.jpg (FOUNDATION_NEXT)

Sources (brand/<product>/source/) are photoreal images made with GPT Image 2.5 (Figma's image generator); their
prompts are in image_prompts.json. The serum's were made with its packaging blank: label_composite.py prints
SKINOFAB's real wordmark and label on each bottle (SERUM_LABELS: where it is in each photo), so the logo
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
import label_composite, label_fix, relabel_bottles, white_bg
import numpy as np
BRAND = HERE.parents[1] / 'brand'
BALM, SERUM, BRUSH = BRAND / 'pdrn-balm', BRAND / 'egf-nad-serum', BRAND / 'lymphatic-brush'
STICK = BRAND / 'foundation-stick'
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
    if product == STICK and (product / 'labelled' / f'{name}.jpg').exists(): return product / 'labelled' / f'{name}.jpg'
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


def cutout(product, name, thresh=244, im=None):
    """The product on a white photo, as RGBA (everything near-white goes transparent, edges feathered). im: the
    photo already loaded (and changed), else photo(product, name)."""
    im = photo(product, name) if im is None else im
    g = ImageOps.grayscale(im).point(lambda v: 255 if v < thresh else 0).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert('RGBA'); out.putalpha(g)
    return out.crop(g.getbbox())


# ------------------------------------------------------------------------------------------------ layouts
def hero(product, name, badge=(948, 148)):
    im = src(product, name)
    korea_badge(im, *badge)
    save(im, product, 'hero')


# the line on every AI before/after picture: big enough to read in the gallery on a phone (a 1080 px image shows
# about 350 px wide there: 30 px is about 10 px on the screen; the old 17 px line read as a smudge, review 6)
AI_NOTE = 'AI illustration, not a customer photo'


def match_color(im, ref):
    """im with ref's color balance: each channel scaled so the face area (the middle of the frame) has ref's mean,
    so the brightness may differ but not the cast. The evening half of the 10 AM / 10 PM photo came out warmer, the
    orange the page says the stick does not turn (stick review 3)."""
    import numpy as np
    a, r = np.asarray(im, dtype=np.float32), np.asarray(ref, dtype=np.float32)
    def face(x): h, w = x.shape[:2]; return x[int(h * .2):int(h * .7), int(w * .2):int(w * .8)].reshape(-1, 3)
    fa, fr = face(a), face(r)
    gain = (fr.mean(0) / fr.mean()) / (fa.mean(0) / fa.mean())     # the cast only: overall brightness stays im's
    return Image.fromarray(np.clip(a * gain, 0, 255).astype(np.uint8))


def before_after(product, name, out, note_text=AI_NOTE, dark=False, words=('Before', 'After')):
    """The two halves with their words (words: 'Before' / 'After', or e.g. '10 AM · Morning' / '10 PM · Evening') and
    the AI line. dark: the words in ink on a white band at the foot (for photos whose lower edge is white: white words
    were lost on a white t-shirt), and a white line between the halves."""
    im = src(product, name)
    if not dark:
        labels(im, [(34, W - 84, words[0]), (W // 2 + 34, W - 84, words[1])])
        labels(im, [(34, W - 34, note_text)], size=40)        # 40: legible where a phone shows it (stick review 2)
        return save(im, product, out)
    d = ImageDraw.Draw(im)
    d.rectangle((W // 2 - 3, 0, W // 2 + 3, W), fill=PAPER)
    d.rectangle((0, W - 132, W, W), fill=PAPER)
    d.text((34, W - 78), words[0], font=sans(34, 'SemiBold'), fill=INK, anchor='ls')
    d.text((W // 2 + 34, W - 78), words[1], font=sans(34, 'SemiBold'), fill=INK, anchor='ls')
    note(d, (34, W - 28), note_text, anchor='ls', size=40)
    save(im, product, out)


# the stick's shade range panel: swatches from fair to deep, then three women (fair, medium, deep) before and after
SKIN_TONES = ['#f3dac8', '#ecc9b2', '#e2b898', '#d6a683', '#cb9572', '#bd8462', '#ad7454', '#9b6447', '#87553b',
              '#734731', '#5e3a27', '#4a2e1f']


def tones_panel(product, cols, title, out, tall=False):
    """A white panel (1080 square, or 1080 x 1350 for a 4:5 slot): a serif title, a row of skin-tone swatches and
    cols [(before, after)] side by side, each woman's photo before and after the same edit, with the AI line."""
    H = round(W * 1.25) if tall else W
    im = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # tall: everything inside the middle 1170 px, since phones show this panel in a 4:4.4 box, center-cropped (the
    # title and the AI line were cut there, stick review 2)
    top = 96 if not tall else 160
    d.text((W // 2, top), title[0], font=serif(54 if not tall else 60, 'Bold'), fill=INK, anchor='ms')
    d.text((W // 2, top + 46), title[1], font=sans(26, 'Regular'), fill=SOFT, anchor='ms')
    # the tones as one smooth bar, fair to deep: a row of dots read as so many shades (stick review 2)
    r = 26
    cy = top + (106 if not tall else 100)
    x0b, x1b, bh = 60, W - 60, 34
    stops = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in SKIN_TONES]
    xs = np.linspace(0, len(stops) - 1, x1b - x0b)
    lo = np.floor(xs).astype(int).clip(0, len(stops) - 2); f = (xs - lo)[:, None]
    row = (np.array(stops)[lo] * (1 - f) + np.array(stops)[lo + 1] * f).astype(np.uint8)
    bar = Image.fromarray(np.repeat(row[None], bh, 0), 'RGB')
    mask = Image.new('L', bar.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, bar.width - 1, bh - 1), bh // 2, fill=255)
    im.paste(bar, (x0b, cy - bh // 2), mask)
    cw, g = 316, 26
    x0 = (W - 3 * cw - 2 * g) // 2
    y0 = cy + r + (40 if not tall else 34)
    ph = cw if not tall else round(cw * 1.26)        # the 4:5 panel's height: taller photos, no empty foot
    for k, (b, a) in enumerate(cols):
        x = x0 + k * (cw + g)
        for j, (name, word) in enumerate(((b, 'Before'), (a, 'After'))):
            y = y0 + j * (ph + 54)
            im.paste(ImageOps.fit(photo(product, name), (cw, ph), Image.LANCZOS, centering=(0.5, 0.35)), (x, y))
            d.text((x + 4, y + ph + 34), word, font=sans(26, 'SemiBold'), fill=INK, anchor='ls')
    note(d, (W // 2, H - 26 if not tall else y0 + 2 * ph + 54 + 80), AI_NOTE + '. Results vary.', size=38)
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
    # the rows at 40 px: the photo is 350 px wide on a phone, where 32 px read as 10 px (stick review 5)
    for k, (kind, a, b) in enumerate(rows):
        y = 384 + k * 148
        icon(d, kind, 100, y + 6)
        d.text((150, y - 2), a, font=sans(40, 'Medium'), fill=INK, anchor='ls')
        d.text((150, y + 46), b, font=sans(40, 'Medium'), fill=INK, anchor='ls')
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
    note(d, (W // 2, W - 24), AI_NOTE + '. Results vary.', size=36)
    save(im, product, 'results-grid')


def whats_inside(product, name, rows, size=700, note_left=False, shadow=False):
    """shadow: a soft contact shadow under a product standing on the white (the stick's floated, stick review 5)."""
    import cv2
    im = Image.new('RGB', (W, W), PAPER)
    im.paste(src(product, name, size), (W - size, W - size))
    # the product itself: the largest dark shape (not a dropper or a swatch beside it), for the lines and the shadow
    dark = (np.asarray(im.convert('L')) < 90).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(dark)
    main = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    ys, xs = np.where(lab == main)
    sx0, sx1, sy0, sy1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    def edge(y):                     # the product's left edge at height y (its nearest row that has it)
        rows_ = np.unique(ys)
        r = int(rows_[np.argmin(np.abs(rows_ - y))])
        return int(xs[ys == r].min()), r
    if shadow:
        sh = Image.new('L', (W, W), 0)
        ImageDraw.Draw(sh).ellipse((sx0 - (sx1 - sx0) * .45, sy1 - 7, sx1 + (sx1 - sx0) * .45, sy1 + 15), fill=150)
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(9))).astype(np.float32)[..., None] / 255
        im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32) * (1 - .42 * sh), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((64, 150), 'What’s', font=serif(80, 'Bold'), fill=INK, anchor='ls')
    d.text((64, 240), 'inside', font=serif(80, 'Bold'), fill=INK, anchor='ls')
    for k, (a, b) in enumerate(rows):
        y = 380 + k * 126
        d.text((64, y), a, font=sans(31, 'Medium'), fill=INK, anchor='ls')
        # each line runs on to the product itself, a dot where it meets it (they stopped 200 px short and pointed at
        # nothing, stick review 5)
        end = 64 + d.textlength(a, font=sans(31, 'Medium')) + 16
        tx, ty = edge(sy0 + (sy1 - sy0) * (.16 + .2 * k))
        tx -= 8
        if end < tx - 40:
            d.line([(end, y - 10), (tx - 70, y - 10), (tx, ty)], fill=INK, width=2, joint='curve')
            d.ellipse((tx - 5, ty - 5, tx + 5, ty + 5), fill=INK)
        d.text((64, y + 34), b, font=sans(19, 'Regular'), fill=SOFT, anchor='ls')
    # note_left: on the white side (a photo that runs to the bottom-right corner hid it)
    if note_left: note(d, (64, W - 28), anchor='ls')
    else: note(d, (W - 60, W - 28), anchor='rs')
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


def vs_others(product, ours, others, others_label, why, rows, others_thresh=240, others_h=200, small_print=None):
    """'skinofab vs. others': the product in a light highlight column, a generic one beside it, tick rows.
    small_print: (box, text, cap) in the photo of ours: its small print set again, larger and bold (label_fix.bold_line),
    before the product is scaled down to the column (a third of its size: the old line would be a few px tall)."""
    im = Image.new('RGB', (W, W), PAPER)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 112), 'skinofab', font=serif(70, 'Bold', italic=True), fill=INK, anchor='rs')
    d.text((W // 2 + 14, 112), 'vs. others', font=serif(70, 'Bold', italic=True), fill=INK, anchor='ls')
    col1, col2, top = 640, 880, 170
    d.rounded_rectangle((col1 - 110, top, col1 + 110, W - 110), radius=26, fill=(240, 240, 239))
    ours_photo = photo(product, ours)
    if small_print:
        box, text, cap = small_print
        a = label_fix.bold_line(np.asarray(ours_photo).astype(np.float32), box, text, cap)
        ours_photo = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))
    ours_im = cutout(product, ours, im=ours_photo); ours_im.thumbnail((150, 300), Image.LANCZOS)
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


def paint_over(path, box, level):
    """Paint over what is lighter than `level` (0-255) inside box (x0, y0, x1, y1) of the photo at path, from what is
    round it (OpenCV inpainting), in place: an AI artefact on a dark ground."""
    import cv2
    im = cv2.imread(str(path))
    x0, y0, x1, y1 = box
    mask = np.zeros(im.shape[:2], np.uint8)
    region = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    mask[y0:y1, x0:x1] = (region > level).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((9, 9), np.uint8))
    mask[:y0], mask[y1:], mask[:, :x0], mask[:, x1:] = 0, 0, 0, 0
    cv2.imwrite(str(path), cv2.inpaint(im, mask, 6, cv2.INPAINT_TELEA), [cv2.IMWRITE_JPEG_QUALITY, 95])


def plain(product, name, out=None, small_print=None):
    """The photo as it is, on white; small_print: (box, text, cap) set again bold first (label_fix.bold_line), for a
    photo shown only a few hundred px wide."""
    if not small_print: return save(src(product, name), product, out or name)
    box, text, cap = small_print
    a = label_fix.bold_line(np.asarray(photo(product, name)).astype(np.float32), box, text, cap)
    im = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))
    save(ImageOps.fit(im, (W, W), Image.LANCZOS), product, out or name)


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
              ['Goes exactly where\nyou need it', 'No fingers, no mess', 'Fits in your bag', 'Works over makeup'],
              small_print=((402, 1300, 622, 1331), 'PDRN', 22))   # the line relabel_bottles retypes, as one bold word
    for n in ('apply-eye', 'hold-chin', 'friends', 'apply-lips', 'bag'):
        plain(P, n)
    before_after(P, 'ba-smile', 'ba-smile')
    # the card (the shelf, the essentials row and the bundle card show the stick ~60 px wide on a laptop): its
    # "PDRN · VOLUFILINE" as one bold PDRN, which reads at that size (review 5)
    plain(P, 'pack', 'card', small_print=((372, 789, 540, 821), 'PDRN', 18))


# where the serum's blank bottle is in each photo (roi, px); blur: out-of-focus bottles. The bottle is the brand's
# matte black cylinder (the foundation's, with a dropper); there is no carton, as for the other products
SERUM_LABELS = {
    'pack': [dict(roi=(380, 40, 650, 960))],
    'tall': [dict()],
    'hold-cheek': [dict(roi=(150, 290, 320, 750))],
    'hold-black': [dict(roi=(150, 270, 300, 710))],
    'drop': [dict(roi=(290, 600, 540, 1024), blur=0.6)],
    'friends': [dict(roi=(820, 320, 960, 670))],
    'panel': [dict(roi=(630, 360, 770, 740))],
    'mirror': [dict(roi=(310, 640, 430, 920), blur=0.3)],
    'temple': [dict(roi=(150, 160, 300, 600))],
    'swatch': [dict(roi=(560, 120, 820, 830))],
    'trio': [dict(roi=(120, 130, 350, 890)), dict(roi=(380, 130, 640, 890)), dict(roi=(670, 130, 900, 890))],
}


def stick():
    """The Adaptive Foundation Stick: brand/foundation-stick/source -> labelled/ (the real wordmark on every tube,
    relabel_bottles.STICK, and the two composites below) -> brand/foundation-stick/*.jpg."""
    P = STICK
    (P / 'labelled').mkdir(exist_ok=True)
    for name, ops in relabel_bottles.STICK.items():
        relabel_bottles.relabel(Image.open(P / 'source' / f'{name}.jpg'), ops).save(P / 'labelled' / f'{name}.jpg', quality=95)
        print('relabelled', name)
    # the handbag's top right corner: the AI ran its zipper into a loose loop of chain links (stick review 5); the
    # links painted over from the dark lining round them, the zipper below and the hand above left as they are
    paint_over(P / 'labelled' / 'bag.jpg', (1140, 410, 1254, 496), 16)
    # the before/after illustration: one woman, the same photo twice (the after is an image edit of the before: her
    # hair, pose, light and lines unchanged, only the foundation added), the middle half of each side by side
    b, a = photo(P, 'before'), photo(P, 'after')
    w, h = b.size
    ba = Image.new('RGB', (w, h), PAPER)
    ba.paste(b.crop((w // 4, 0, w // 4 + w // 2, h)), (0, 0)); ba.paste(a.crop((w // 4, 0, w // 4 + w // 2, h)), (w // 2, 0))
    ba.save(P / 'labelled' / 'ba-even.jpg', quality=95)
    # the panel: the woman (already at the frame's right) scaled to 85 % into the lower right, so the title and the
    # rows on the left never touch her hair
    pn = photo(P, 'panel'); s = pn.resize((round(pn.width * .85), round(pn.height * .85)), Image.LANCZOS)
    wide = Image.new('RGB', pn.size, PAPER); wide.paste(s, (pn.width - s.width, pn.height - s.height))
    wide.save(P / 'labelled' / 'panel-wide.jpg', quality=95)
    # the science block's picture: the cream stroke turning from white to a skin tone (no stick, so no wordmark for a
    # crop to cut), at 4:5 with white round it, so the block's 4:5 and 4:4.4 crops keep the whole stroke
    sc = photo(P, 'science'); k = .93
    s = sc.resize((round(sc.width * k), round(sc.height * k)), Image.LANCZOS)
    tall = Image.new('RGB', (sc.width, round(sc.width * 1.25)), PAPER)
    tall.paste(s, ((tall.width - s.width) // 2, (tall.height - s.height) // 2))
    tall.save(P / 'labelled' / 'science-tall.jpg', quality=95)
    plain(P, 'pack', 'hero')
    plain(P, 'duo-ends')                 # one stick, both ends open: what "foundation + brush in one" means
    plain(P, 'hold-cheek')
    before_after(P, 'ba-even', 'before-after', dark=True)
    # from 10 AM to 10 PM: one portrait in the morning and the same photo edited to the evening's light, the middle
    # half of each side by side (named ba-: the page captions it as an AI illustration)
    m, e = photo(P, 'wear-morning'), photo(P, 'wear-evening')
    w, h = m.size
    wear = Image.new('RGB', (w, h), PAPER)
    mc, ec = m.crop((w // 4, 0, w // 4 + w // 2, h)), e.crop((w // 4, 0, w // 4 + w // 2, h))
    wear.paste(mc, (0, 0)); wear.paste(match_color(ec, mc), (w // 2, 0))
    wear.save(P / 'labelled' / 'ba-wear.jpg', quality=95)
    before_after(P, 'ba-wear', 'wear-day', dark=True, words=('10 AM · Morning', '10 PM · Evening'))
    tones = [('tone-fair-b', 'tone-fair-a'), ('tone-med-b', 'tone-med-a'), ('tone-deep-b', 'tone-deep-a')]
    tones_panel(P, tones, ('One stick, many skin tones', 'It goes on white and blends into your own tone'), 'tones')
    tones_panel(P, tones, ('One stick, many skin tones', 'It goes on white and blends into your own tone'), 'tones-tall', tall=True)
    panel(P, 'panel-wide', ('One Stick,', 'Your Shade'), [('sparkle', 'Goes on white,', 'blends to your tone'),
                                                          ('drop', 'Creamy, made for', 'dry, mature skin'),
                                                          ('stick', 'Swipe, buff,', 'done in a minute')], 'one-stick')
    # on the stick itself (the swatch photo is "How does it work?" further down: the same photo twice, stick review 3)
    whats_inside(P, 'single', [('Hyaluronic acid', 'Keeps dry skin comfortable'), ('Niacinamide', 'For a more even-looking tone'),
                               ('Squalane + vitamin E', 'Soft and supple, never tight')], note_left=True, shadow=True)
    science(P, 'science', ('Color pigments wrapped in tiny capsules break as you blend,',
                           'and the white cream shifts toward your own skin tone:',
                           'one shade that meets your skin where it is.'))
    vs_others(P, 'single', 'liquid', 'Your old foundation', [('Why one stick', False), ('works where a', False), ('bottle doesn’t', True)],
              ['Adapts to your\nskin tone', 'Kabuki brush\nbuilt in', 'No spills, fits\nyour bag', 'Creamy, made for\ndry skin'])
    for n in ('apply-cheek', 'blend', 'temple', 'friends', 'hold-chin', 'bag', 'tips', 'swatch', 'twist', 'dots', 'daylight',
              'buff-jaw'):
        plain(P, n)
    plain(P, 'single', 'card')


def serum():
    P = SERUM
    for name, bottles in SERUM_LABELS.items():         # the real label first, on every bottle
        im = Image.open(P / 'source' / f'{name}.jpg')
        for b in bottles:
            im = label_composite.composite(im, 'serum', b.get('roi'), blur=b.get('blur', 0.0))
        im = white_bg.light(im)
        im.save(P / f'{name}.jpg', quality=92, optimize=True, progressive=True)
        print('labelled', name)
    hero(P, 'pack')
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

# the renders' PDRN line left out: the cart, the bag and the checkout show the first one 80 to 100 px wide, where even a
# bold PDRN blurred to PORN on a 1x screen (store audit 8); the sticky bar's thumbnail is cut from it too
NEXT_BOLD = {'01-front.png': lambda a: label_fix.bold_line(a, (585, 1049, 668, 1072), '', 14),
             '03-three-quarter-right.png': lambda a: label_fix.bold_line(a, (466, 1038, 566, 1072), '', 14)}


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
        im = Image.open(path).convert('RGB')
        if path.name in NEXT_BOLD:
            im = Image.fromarray(np.clip(NEXT_BOLD[path.name](np.asarray(im).astype(np.float32)) + 0.5, 0, 255).astype(np.uint8))
        im = white_bg.matte(im, shadow=shadow)
        im.save(out / f'{path.stem}.jpg', quality=92, optimize=True, progressive=True)
        print('next', path.stem, im.size)


if __name__ == '__main__':
    which = sys.argv[1:] or ['balm', 'serum', 'brush', 'foundation', 'stick']
    for w in which: {'balm': balm, 'serum': serum, 'brush': brush, 'foundation': foundation, 'stick': stick}[w]()
