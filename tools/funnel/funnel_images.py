"""The funnel's images: brand/stick-funnel/source/*.png (photoreal, GPT Image 2, prompts in
tools/persona/image_prompts.json "stick-funnel") and the store's own product photos, laid out for the pages and
written to the Page Kit campaign's images folder (campaigns/skinofab/src/stick-funnel/assets/images/sf/).

usage: python3 -I tools/funnel/funnel_images.py [<work_dir>]
  <work_dir>: the store build's inputs (tools/build_store.sh); its reviews/photos/ has the customers' photos. Their
  crops are kept in brand/stick-funnel/ so a build without the work dir still has them.

The listicle mirrors the image kinds of the owner's other brand's listicle (Facelove, "10 reasons why foundating
stick 2026 new"), one by one: a three-women collage up top, a before/after for the shade match, a woman holding the
stick, a before/after for dry skin, a macro of the brush buffing, a before/after for spots, an ingredient plate, the
women the stick is made for, the how-to, the guarantee seal and the offer card. What Facelove's could not back is
not drawn: no "WEEK 1 / WEEK 8" (nothing measured it), no doctors holding the stick (no expert endorses it), no
"America's #1" or "98%" or award seal. Every before/after says on the image that it is an AI illustration. The
testimonial photos are the customers' own (their reviews of the Adaptive Peptide Foundation, imported from the
store's earlier review app; photos approved by eye in reviews/photos-approved.txt) and the page says whose they are.
"""
import shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'persona'))
import product_photos as P       # the gallery's fonts, words-with-shadow and AI line
import stick_copy as SC

BRAND = ROOT / 'brand'
SRC = BRAND / 'stick-funnel' / 'source'
STICK, BRUSH, BALM, SERUM = BRAND / 'foundation-stick', BRAND / 'lymphatic-brush', BRAND / 'pdrn-balm', BRAND / 'egf-nad-serum'
OUT = ROOT / 'campaigns' / 'skinofab' / 'src' / 'stick-funnel' / 'assets' / 'images' / 'sf'
INK, PAPER, SOFT, CREAM = (21, 21, 21), (255, 255, 255), (96, 96, 96), (246, 242, 236)
# the three testimonials' own photos (review id -> crop box as fractions of the photo: left, top, right, bottom)
# (review id, where her face is across and down the photo: the square crop keeps her whole head)
TESTIMONIAL_PHOTOS = {'lora': ('zjPC7IPmY-0', (0.5, 0.2)), 'hope': ('DCqk83pSC-0', (0.62, 0.2)),
                      'diane': ('Eu0eKzf2sd-0', (0.5, 0.2))}


def save(im, name, size=None, q=82):
    im = im.convert('RGB')
    if size and max(im.size) > size: im.thumbnail((size, size), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f'{name}.jpg', quality=q, optimize=True, progressive=True)
    print(name, im.size)


def src(name): return Image.open(SRC / f'{name}.png').convert('RGB')


def before_after(name, out, size=1080):
    """A split-screen photo with Before / After and the AI line in ink on a white band at its foot (the gallery's
    style, P.before_after dark: white words were lost on the white t-shirts), a white line between the halves."""
    im = ImageOps.fit(src(name), (size, size), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle((size // 2 - 3, 0, size // 2 + 3, size), fill=PAPER)
    d.rectangle((0, size - 150, size, size), fill=PAPER)
    d.text((34, size - 88), 'Before', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    d.text((size // 2 + 34, size - 88), 'After', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    P.note(d, (34, size - 30), P.AI_NOTE, anchor='ls', size=38)
    save(im, out)


def hero():
    """Three women past 45 with the stick, side by side (Facelove's top collage), 2:3 each."""
    w, h = 560, 840
    panels = [ImageOps.fit(src(n), (w, h), Image.LANCZOS, centering=(0.5, 0.35)) for n in ('hero-a', 'hero-b', 'hero-c')]
    im = Image.new('RGB', (w * 3 + 8, h), PAPER)
    for i, p in enumerate(panels): im.paste(p, (i * (w + 4), 0))
    save(im, 'hero', size=1688)


def labelled_plate():
    """The ingredient plate with each one named (Facelove's labelled flat lay), names in the gallery's sans."""
    size = 1080
    im = ImageOps.fit(src('flatlay'), (size, size), Image.LANCZOS)
    k = size / 1254
    # (label, the item's centre, where the label sits) in the 1254 px source
    tags = [('Vitamin E', (290, 370), (120, 150)), ('Ceramides', (571, 160), (560, 52)),
            ('Hyaluronic acid', (960, 470), (900, 300)), ('Centella', (204, 650), (60, 560)),
            ('Squalane', (911, 728), (1010, 860)), ('Silica spheres', (802, 960), (930, 1110))]
    d = ImageDraw.Draw(im)
    f = P.sans(30, 'SemiBold')
    for text, (ix, iy), (lx, ly) in tags:
        ix, iy, lx, ly = ix * k, iy * k, lx * k, ly * k
        tw = d.textlength(text, font=f)
        x0 = min(max(lx - tw / 2 - 16, 8), size - tw - 40)
        box = (x0, ly - 24, x0 + tw + 32, ly + 24)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        d.line([(cx, cy), (ix, iy)], fill=PAPER, width=3)
        d.ellipse((ix - 7, iy - 7, ix + 7, iy + 7), fill=PAPER, outline=INK, width=2)
        d.rounded_rectangle(box, radius=24, fill=PAPER)
        d.text((cx, cy), text, font=f, fill=INK, anchor='mm')
    d.rounded_rectangle((24, size - 92, size - 24, size - 24), radius=18, fill=(255, 255, 255))
    d.text((size / 2, size - 58), 'Plus PDRN, peptides and Volufiline™ · For illustration only', font=P.sans(26, 'Medium'),
           fill=INK, anchor='mm')
    save(im, 'plate')


def made_without():
    """The stick on a bathroom shelf with what it is made without beside it (stick_copy.FREE_FROM)."""
    size = 1080
    im = ImageOps.fit(src('vanity'), (size, size), Image.LANCZOS)
    d = ImageDraw.Draw(im, 'RGBA')
    x0, y0, x1 = 600, 150, 1040
    rows = SC.FREE_FROM
    d.rounded_rectangle((x0, y0, x1, y0 + 120 + 64 * len(rows)), radius=28, fill=(255, 255, 255, 236))
    d.text((x0 + 36, y0 + 64), 'Made without', font=P.serif(46, 'Bold'), fill=INK, anchor='ls')
    for i, r in enumerate(rows):
        y = y0 + 128 + i * 64
        d.ellipse((x0 + 36, y - 16, x0 + 68, y + 16), fill=INK)
        d.line([(x0 + 45, y - 7), (x0 + 59, y + 7)], fill=PAPER, width=4)
        d.line([(x0 + 59, y - 7), (x0 + 45, y + 7)], fill=PAPER, width=4)
        d.text((x0 + 88, y), r[0].upper() + r[1:], font=P.sans(32, 'Medium'), fill=INK, anchor='lm')
    save(im, 'made-without')


def how_to():
    """Twist, dot, buff: the stick page's three how-to photos side by side with their step."""
    s = 720
    steps = [('twist', '1  Twist up'), ('dots', '2  Dot it on'), ('blend', '3  Buff it in')]
    im = Image.new('RGB', (s * 3 + 16, s), PAPER)
    for i, (n, word) in enumerate(steps):
        p = ImageOps.fit(Image.open(STICK / 'labelled' / f'{n}.jpg').convert('RGB'), (s, s), Image.LANCZOS)
        d = ImageDraw.Draw(p)
        f = P.sans(46, 'SemiBold')
        tw = d.textlength(word, font=f)
        d.rounded_rectangle((28, s - 104, 28 + tw + 48, s - 32), radius=36, fill=INK)
        d.text((52, s - 68), word, font=f, fill=PAPER, anchor='lm')
        im.paste(p, (i * (s + 8), 0))
    save(im, 'how-to', size=1620)


def seal():
    """The 30-day guarantee seal (Facelove's "FREE TRIAL" seal, in the brand's black)."""
    import math
    size = 1080
    im = Image.new('RGB', (size, size), CREAM)
    d = ImageDraw.Draw(im)
    cx = cy = size / 2
    pts = []
    for i in range(96):
        a = 2 * math.pi * i / 96
        r = 430 if i % 2 == 0 else 404
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=INK)
    d.ellipse((cx - 370, cy - 370, cx + 370, cy + 370), outline=(201, 169, 110), width=6)
    d.text((cx, cy - 150), '30-DAY', font=P.sans(84, 'Bold'), fill=PAPER, anchor='mm')
    d.text((cx, cy - 10), 'Money-back', font=P.serif(108, 'Bold', italic=True), fill=PAPER, anchor='mm')
    d.text((cx, cy + 110), 'GUARANTEE', font=P.sans(70, 'SemiBold'), fill=(201, 169, 110), anchor='mm')
    d.text((cx, cy + 210), 'Full refund · even opened', font=P.sans(34, 'Medium'), fill=PAPER, anchor='mm')
    for k in range(5):
        x = cx - 120 + k * 60
        star = [(x + 18 * math.cos(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45),
                 cy - 250 - 18 * math.sin(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45)) for j in range(10)]
        d.polygon(star, fill=(201, 169, 110))
    save(im, 'guarantee')


def offer_card():
    """The offer (Facelove's product card): the two sticks and the free brush, on white."""
    size = 1080
    im = Image.new('RGB', (size, size), PAPER)
    sticks = ImageOps.fit(P.white_bg.light(Image.open(STICK / 'hero.jpg').convert('RGB')), (700, 700), Image.LANCZOS)
    brush = ImageOps.fit(P.white_bg.light(Image.open(BRUSH / 'card.jpg').convert('RGB')), (520, 520), Image.LANCZOS)
    im.paste(sticks, (-70, 290)); im.paste(brush, (540, 420))
    d = ImageDraw.Draw(im)
    d.text((72, 120), 'Adaptive', font=P.serif(92, 'Bold'), fill=INK, anchor='ls')
    d.text((72, 220), 'Foundation Stick', font=P.serif(92, 'Bold', italic=True), fill=INK, anchor='ls')
    d.text((74, 280), 'For skin after 45 · fair to medium tones', font=P.sans(34, 'Medium'), fill=SOFT, anchor='ls')
    f = P.sans(32, 'SemiBold'); word = '+ FREE Lymphatic Brush'
    tw = d.textlength(word, font=f); cx = 800
    d.rounded_rectangle((cx - tw / 2 - 30, 400, cx + tw / 2 + 30, 470), radius=35, fill=INK)
    d.text((cx, 435), word, font=f, fill=PAPER, anchor='mm')
    d.text((size / 2, size - 48), 'With 2 sticks · Free shipping · 30-day money-back guarantee', font=P.sans(32, 'Medium'),
           fill=INK, anchor='ms')
    save(im, 'offer')


def testimonials(work):
    """Each testimonial's own photo, square on her face (kept in brand/stick-funnel/review-<key>.jpg)."""
    for key, (rid, centering) in TESTIMONIAL_PHOTOS.items():
        kept = BRAND / 'stick-funnel' / f'review-{key}.jpg'
        photo = Path(work) / 'reviews' / 'photos' / f'{rid}.jpg' if work else None
        if photo and photo.exists():
            im = Image.open(photo).convert('RGB')
            side = min(im.size)
            crop = ImageOps.fit(im, (side, side), Image.LANCZOS, centering=centering)
            crop.thumbnail((600, 600), Image.LANCZOS)
            crop.save(kept, quality=88)
        save(Image.open(kept), f'review-{key}', size=600)


def copies():
    """The store's own photos, as the product page and the special offers use them."""
    plain = {
        # product page gallery (the stick page's, in its order) and its sections
        'g-one-stick': STICK / 'one-stick.jpg', 'g-tones': STICK / 'tones.jpg', 'g-duo-ends': STICK / 'duo-ends.jpg',
        'g-before-after': STICK / 'before-after.jpg', 'g-whats-inside': STICK / 'whats-inside.jpg', 'g-hold-chin': STICK / 'hold-chin.jpg',
        'wear-day': STICK / 'wear-day.jpg', 'vs-others': STICK / 'vs-others.jpg', 'science-poster': STICK / 'science' / 'science-poster.jpg',
        'gift-brush': STICK / 'gift-brush.jpg', 'gift-shipping': STICK / 'gift-shipping.jpg', 'stick-card': STICK / 'card.jpg',
        'temple': STICK / 'temple.jpg', 'friends': STICK / 'friends.jpg', 'swatch': STICK / 'swatch.jpg',
        **{f'ing-{n}': STICK / f'ing-{n}.jpg' for n in ('pdrn', 'peptides', 'ha', 'ceramides', 'squalane', 'niacinamide', 'centella')},
        # the special offers
        'up1-hold': STICK / 'hold-cheek.jpg', 'up1-pack': STICK / 'hero.jpg',
        'up2-brush': BRUSH / 'hero.jpg', 'up2-card': BRUSH / 'card.jpg', 'up2-how': BRUSH / 'how-to-use.jpg', 'up2-ba': BRUSH / 'ba-puffy.jpg',
        'up3-balm': BALM / 'card.jpg', 'up3-hold': BALM / 'hold-cheek.jpg', 'up3-ba': BALM / 'before-after.jpg', 'up3-inside': BALM / 'whats-inside.jpg',
        'up4-serum': SERUM / 'card.jpg', 'up4-hold': SERUM / 'hold-cheek.jpg', 'up4-ba': SERUM / 'before-after.jpg', 'up4-inside': SERUM / 'whats-inside.jpg',
    }
    for name, path in plain.items():
        save(Image.open(path), name, size=1080)
    for n in ('cheek-brush', 'macro-buff'):
        save(src(n), n, size=1080)
    # the explainer loop (stick_science_video.py): video for the pages, the poster above
    for ext in ('mp4', 'webm'):
        shutil.copyfile(STICK / 'science' / f'science.{ext}', OUT / f'science.{ext}')
    # the brand's wordmark (header) and the store's favicons (the starter's are replaced)
    shutil.copyfile(BRAND / 'logo' / 'skinofab-wordmark.svg', OUT / 'skinofab-wordmark.svg')
    static = ROOT / 'tools' / 'theme-build' / 'static'
    shutil.copyfile(static / 'skinofab-favicon-32.png', OUT.parent / 'favicon.png')
    shutil.copyfile(static / 'skinofab-favicon-180.png', OUT.parent / 'webclip.png')


if __name__ == '__main__':
    hero()
    before_after('ba-redness', 'ba-redness')
    before_after('ba-dry', 'ba-dry')
    before_after('ba-spots', 'ba-spots')
    labelled_plate()
    made_without()
    how_to()
    seal()
    offer_card()
    testimonials(sys.argv[1] if len(sys.argv) > 1 else None)
    copies()
