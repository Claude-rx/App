"""The second products' page images, laid out like the Adaptive Peptide Foundation's gallery, on white.

usage: python3 -I product_photos.py     # brand/pdrn-balm/source/*.jpg -> brand/pdrn-balm/*.jpg,
                                        # brand/lymphatic-brush/source/ba-puffy.jpg -> brand/lymphatic-brush/ba-puffy.jpg

Sources (brand/<product>/source/) are photoreal images made with GPT Image 2.5 (Figma's image generator); their
prompts are in image_prompts.json. This script only crops and lays them out: the headline type is Playfair Display (the
foundation gallery's serif), the small type Montserrat, the Korean badge the one cut from the foundation's hero photo
(assets/korea-badge.png). The before/after photos are illustrations, and say so on the image, as the foundation's
"What's inside" and "The Science" images do.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / 'brand' / 'pdrn-balm' / 'source'
OUT = SRC.parent
BRUSH = HERE.parents[1] / 'brand' / 'lymphatic-brush'
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


def src(name, size=W, folder=SRC):
    """A source image fitted to a size x size square."""
    return ImageOps.fit(Image.open(folder / f'{name}.jpg').convert('RGB'), (size, size), Image.LANCZOS)


def save(im, name, folder=OUT):
    im.convert('RGB').save(folder / f'{name}.jpg', quality=90, optimize=True, progressive=True)
    print(folder.name, name, im.size)


def note(d, xy, text=ILLUSTRATIVE, fill=SOFT, anchor='ms', size=17):
    d.text(xy, text, font=sans(size, 'Regular'), fill=fill, anchor=anchor)


def labels(im, pairs, size=34):
    """'Before' / 'After' in white at the bottom left of each half of a split photo (as on the foundation's)."""
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
    """Thin line icons for the 'Look less tired' panel."""
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


def korea_badge(im, cx=948, cy=148):
    """The foundation hero's badge: the flag circle and "Based on Korean / Beauty Innovation" under it."""
    flag = Image.open(HERE / 'assets' / 'korea-badge.png').convert('RGBA')
    shadow = Image.new('L', im.size, 0)
    ImageDraw.Draw(shadow).ellipse((cx - 72, cy - 68, cx + 72, cy + 78), fill=55)
    im.paste((0, 0, 0), mask=shadow.filter(ImageFilter.GaussianBlur(9)))
    im.paste(flag, (cx - flag.width // 2, cy - flag.height // 2), flag)
    d = ImageDraw.Draw(im)
    for k, line in enumerate(('Based on Korean', 'Beauty Innovation')):
        d.text((cx, cy + 108 + k * 29), line, font=sans(23, 'Regular'), fill=INK, anchor='ms')


# ------------------------------------------------------------------------------------------------ gallery
def hero():
    im = src('pack')
    korea_badge(im)
    save(im, 'hero')


def before_after(name, out, note_text=ILLUSTRATIVE, src_dir=SRC, out_dir=OUT):
    im = src(name, folder=src_dir)
    labels(im, [(34, W - 40, 'Before'), (W // 2 + 34, W - 40, 'After')])
    labels(im, [(W // 2 + 34, W - 82, note_text)], size=17)
    save(im, out, out_dir)


def look_less_tired():
    im = src('panel')
    d = ImageDraw.Draw(im)
    d.text((70, 150), 'Look Less', font=serif(84, 'Bold'), fill=INK, anchor='ls')
    d.text((70, 250), 'Tired', font=serif(84, 'Bold', italic=True), fill=INK, anchor='ls')
    rows = [('sparkle', 'Smoother-looking', 'in seconds'), ('drop', 'Hydrates and', 'cushions'), ('stick', 'Press on,', 'no fingers')]
    for k, (kind, a, b) in enumerate(rows):
        y = 380 + k * 130
        icon(d, kind, 104, y + 4)
        d.text((160, y - 4), a, font=sans(32, 'Medium'), fill=INK, anchor='ls')
        d.text((160, y + 36), b, font=sans(32, 'Medium'), fill=INK, anchor='ls')
    save(im, 'look-less-tired')


def results_grid():
    im = Image.new('RGB', (W, W), (247, 247, 246))
    d = ImageDraw.Draw(im)
    d.text((64, 118), 'Swipe, press,', font=serif(66, 'Bold'), fill=INK, anchor='ls')
    d.text((64, 196), 'rested.', font=serif(66, 'Bold', italic=True), fill=INK, anchor='ls')
    pairs = ['ba-eye', 'ba-smile', 'ba-crows', 'ba-lips']
    tw, th, gap, x0, y0 = 452, 312, 48, 64, 252
    for k, name in enumerate(pairs):
        x, y = x0 + (k % 2) * (tw + gap), y0 + (k // 2) * (th + 90)
        im.paste(ImageOps.fit(Image.open(SRC / f'{name}.jpg').convert('RGB'), (tw, th), Image.LANCZOS), (x, y))
        d.text((x + 6, y + th + 32), 'Before', font=sans(21, 'Regular'), fill=SOFT, anchor='ls')
        d.text((x + tw // 2 + 6, y + th + 32), 'After', font=sans(21, 'Regular'), fill=SOFT, anchor='ls')
    note(d, (W // 2, W - 22), ILLUSTRATIVE + '. Results vary.')
    save(im, 'results-grid')


def whats_inside():
    im = Image.new('RGB', (W, W), PAPER)
    im.paste(src('swatch', 700), (W - 700, W - 700))
    d = ImageDraw.Draw(im)
    d.text((64, 150), 'What’s', font=serif(80, 'Bold'), fill=INK, anchor='ls')
    d.text((64, 240), 'inside', font=serif(80, 'Bold'), fill=INK, anchor='ls')
    rows = [('PDRN', 'Salmon DNA, the K-beauty skin booster'),
            ('Volufiline™', 'For areas that look hollow'),
            ('Collagen + hyaluronic acid', 'Cushions the look of lines')]
    for k, (a, b) in enumerate(rows):
        y = 380 + k * 126
        d.text((64, y), a, font=sans(31, 'Medium'), fill=INK, anchor='ls')
        end = 64 + d.textlength(a, font=sans(31, 'Medium')) + 16
        if end < 400: d.line([(end, y - 10), (460, y - 10)], fill=INK, width=2)
        d.text((64, y + 34), b, font=sans(19, 'Regular'), fill=SOFT, anchor='ls')
    note(d, (W - 60, W - 28), anchor='rs')
    save(im, 'whats-inside')


def science():
    im = src('science')
    fade = Image.linear_gradient('L').resize((W, 330)).point(lambda v: 255 - v)       # opaque at the top
    im.paste(PAPER, (0, 0, W, 330), fade.point(lambda v: min(255, int(v * 1.35))))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 120), 'The Science', font=serif(76, 'Bold'), fill=INK, anchor='ms')
    for k, line in enumerate(('PDRN and Volufiline™ in a balm that melts on contact.',
                              'Press it on: it cushions the look of hollows and lines',
                              'while it hydrates, right where you need it.')):
        d.text((W // 2, 190 + k * 40), line, font=sans(27, 'Regular'), fill=INK, anchor='ms')
    note(d, (W // 2, W - 26))
    save(im, 'science')


def cutout(name, thresh=244):
    """The product on a white photo, as RGBA (everything near-white goes transparent, edges feathered)."""
    im = Image.open(SRC / f'{name}.jpg').convert('RGB')
    g = ImageOps.grayscale(im).point(lambda v: 255 if v < thresh else 0).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert('RGBA'); out.putalpha(g)
    return out.crop(g.getbbox())


def vs_others():
    im = Image.new('RGB', (W, W), PAPER)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 112), 'skinofab', font=serif(70, 'Bold', italic=True), fill=INK, anchor='rs')
    d.text((W // 2 + 14, 112), 'vs. others', font=serif(70, 'Bold', italic=True), fill=INK, anchor='ls')
    col1, col2, top = 640, 880, 170
    d.rounded_rectangle((col1 - 110, top, col1 + 110, W - 110), radius=26, fill=(240, 240, 239))
    stick = cutout('tall'); stick.thumbnail((150, 300), Image.LANCZOS)
    im.paste(stick, (col1 - stick.width // 2, top + 24), stick)
    jar = cutout('jar', 240); jar.thumbnail((200, 200), Image.LANCZOS)
    im.paste(jar, (col2 - jar.width // 2, top + 24 + 300 - jar.height), jar)
    d.text((64, top + 150), 'Why a press-on', font=serif(44, 'Bold'), fill=INK, anchor='ls')
    d.text((64, top + 206), 'stick works where', font=serif(44, 'Bold'), fill=INK, anchor='ls')
    d.text((64, top + 262), 'a jar doesn\u2019t', font=serif(44, 'Bold', italic=True), fill=INK, anchor='ls')
    d.text((col1, top + 368), 'SKINOFAB', font=sans(22, 'SemiBold'), fill=INK, anchor='ms')
    d.text((col2, top + 368), 'A jar of cream', font=sans(22, 'Regular'), fill=SOFT, anchor='ms')
    rows = ['Goes exactly where\nyou need it', 'No fingers, no mess', 'Fits in your bag', 'Works over makeup']
    for k, text in enumerate(rows):
        y = top + 440 + k * 112
        d.line([(64, y - 52), (W - 64, y - 52)], fill=LINE, width=1)
        d.multiline_text((64, y - 8 - (16 if '\n' in text else 0)), text, font=sans(30, 'Medium'), fill=INK, anchor='ls', spacing=8)
        check(d, col1, y - 14, 22, True)
        check(d, col2, y - 14, 22, False, (200, 200, 200))
    save(im, 'vs-others')


def plain(name, out):
    save(src(name), out)


# ------------------------------------------------------------------------------------------------ sections
def card():
    """The shop card, cart and sticky-bar image: the packshot alone."""
    save(src('pack'), 'card')


def main():
    hero()
    plain('hold-cheek', 'hold-cheek')
    before_after('ba-eye', 'before-after')
    look_less_tired()
    results_grid()
    whats_inside()
    science()
    vs_others()
    for n in ('apply-eye', 'hold-chin', 'friends', 'apply-lips', 'bag'):
        plain(n, n)
    before_after('ba-smile', 'ba-smile')
    card()
    # the brush page's before/after block
    before_after('ba-puffy', 'ba-puffy', src_dir=BRUSH / 'source', out_dir=BRUSH)


if __name__ == '__main__':
    main()
