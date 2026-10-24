"""The PDRN Plumping Balm's images, from the Blender renders (balm_render.py) in SKINOFAB's black-on-grey look.

usage: python3 -I balm_assets.py <renders_dir>
writes brand/pdrn-balm/: hero, ingredients, stick-vs-cream, where, how-to-use, texture, duo (the gallery, balm_copy.GALLERY)
and card (shelf, cart, sticky bar), 1080 x 1080 JPEG.

Type: Montserrat (the label's face), black #151515 and the renders' own grey. Every word on an image is a cosmetic,
checkable statement (balm_copy): no ratings, counts or results numbers; the guarantee seal states the store's 30-day
money-back guarantee.
"""
import math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import balm_copy as C

R = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'brand' / 'pdrn-balm'; OUT.mkdir(parents=True, exist_ok=True)
FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
INK, SOFT, WHITE = (21, 21, 21), (88, 90, 96), (255, 255, 255)
W = 1080


def vf(size, weight):
    f = ImageFont.truetype(str(FONT), size); f.set_variation_by_name(weight); return f


def render(name):
    return Image.open(R / f'{name}.png').convert('RGB')


def placed(src, scale, dx=0, dy=0):
    """The render scaled to W*scale, shifted by (dx, dy) on a W x W canvas whose empty edges continue the render's
    own backdrop (edge pixels stretched), so there is never a seam."""
    s = round(W * scale)
    im = src.resize((s, s), Image.LANCZOS)
    a = np.asarray(im)
    x0, y0 = (W - s) // 2 + dx, (W - s) // 2 + dy
    pad = ((max(0, y0), max(0, W - (y0 + s))), (max(0, x0), max(0, W - (x0 + s))), (0, 0))
    a = np.pad(a, pad, mode='edge')
    ys, xs = max(0, -y0), max(0, -x0)
    return Image.fromarray(a[ys:ys + W, xs:xs + W])


def crop(name, box):
    """A render cropped to box, given as fractions of its size (renders come at any resolution)."""
    im = render(name); w, h = im.size
    return im.crop((round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)))


def cover(im, w, h):
    """im scaled to cover w x h, centered, cropped."""
    k = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * k), math.ceil(im.height * k)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def text(d, xy, s, size, weight='Bold', fill=INK, anchor='la', track=0.0):
    f = vf(size, weight)
    if not track: d.text(xy, s, font=f, fill=fill, anchor=anchor); return d.textlength(s, font=f)
    x, y = xy
    total = sum(d.textlength(ch, font=f) for ch in s) + track * size * (len(s) - 1)
    if anchor[0] == 'm': x -= total / 2
    elif anchor[0] == 'r': x -= total
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill, anchor='l' + anchor[1]); x += d.textlength(ch, font=f) + track * size
    return total


def fit(d, s, size, weight, width):
    while d.textlength(s, font=vf(size, weight)) > width and size > 12: size -= 1
    return size


def check(d, cx, cy, r, ring=INK, tick=WHITE):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ring)
    d.line([(cx - r * .45, cy + r * .02), (cx - r * .1, cy + r * .36), (cx + r * .48, cy - r * .32)], fill=tick, width=max(3, round(r * .22)), joint='curve')


def cross(d, cx, cy, r, col=(150, 150, 156)):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=max(2, round(r * .14)))
    k = r * .38
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=col, width=max(3, round(r * .18)))
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=col, width=max(3, round(r * .18)))


def seal(size):
    """The 30-day money-back seal, black starburst, white type, slightly tilted."""
    k = 4; S = size * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c, Ro, Ri, n = S / 2, S / 2 - 2, S / 2 * .87, 24
    d.polygon([(c + (Ro if i % 2 == 0 else Ri) * math.cos(math.pi * i / n), c + (Ro if i % 2 == 0 else Ri) * math.sin(math.pi * i / n))
               for i in range(2 * n)], fill=INK + (255,))
    t = Image.new('RGBA', (S, S), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
    td.text((c, c - S * .11), '30-Day', font=vf(int(S * .17), 'Bold'), fill=WHITE + (255,), anchor='mm')
    td.text((c, c + S * .07), 'Money-Back', font=vf(int(S * .095), 'Medium'), fill=WHITE + (255,), anchor='mm')
    td.text((c, c + S * .19), 'Guarantee', font=vf(int(S * .095), 'Medium'), fill=WHITE + (255,), anchor='mm')
    im.alpha_composite(t.rotate(8, resample=Image.BICUBIC, center=(c, c)))
    return im.resize((size, size), Image.LANCZOS)


def mark(d, x, y, s, size, pad=(20, 10)):
    """White words on a black rounded box (the site's highlighted heading)."""
    f = vf(size, 'Black'); w = d.textlength(s, font=f)
    asc, desc = f.getmetrics()
    d.rounded_rectangle((x, y, x + w + 2 * pad[0], y + asc + desc * .2 + 2 * pad[1]), radius=14, fill=INK)
    d.text((x + pad[0], y + pad[1]), s, font=f, fill=WHITE)
    return y + asc + desc * .2 + 2 * pad[1]


def pill(d, x, y, s, size=26):
    f = vf(size, 'SemiBold'); w = d.textlength(s, font=f); h = 66
    d.rounded_rectangle((x, y, x + 76 + w + 26, y + h), radius=h // 2, fill=WHITE)
    check(d, x + 38, y + h / 2, 19)
    d.text((x + 76, y + h / 2), s, font=f, fill=INK, anchor='lm')
    return y + h


def save(im, name):
    im.convert('RGB').save(OUT / f'{name}.jpg', quality=88, optimize=True, progressive=True)
    print('wrote', OUT / f'{name}.jpg')


# 1. hero: the open stick and its cap, the promise, three facts, the seal -------------------------------------------
def hero():
    im = placed(render('open'), 1.02, dx=210, dy=40); d = ImageDraw.Draw(im)
    y = 78
    for line in C.HERO['title']:
        y += 4; text(d, (62, y), line, fit(d, line, 84, 'Black', 560), 'Black'); y += 96
    y = mark(d, 60, y, C.HERO['accent'], 60) + 34
    for fact in C.HERO['facts']: y = pill(d, 56, y, fact) + 16
    s = seal(210); im.paste(s, (52, W - s.height - 48), s)
    return im


# 2. ingredients: the stick, four actives around it -------------------------------------------------------------------
def ingredients():
    im = placed(render('front'), 1.0, dy=60); d = ImageDraw.Draw(im)
    text(d, (W / 2, 70), 'FOUR K-BEAUTY ACTIVES', 46, 'Black', anchor='mt')
    text(d, (W / 2, 132), 'in one press-on balm', 30, 'Medium', fill=SOFT, anchor='mt')
    spots = [(60, 330, 'l'), (60, 640, 'l'), (W - 60, 330, 'r'), (W - 60, 640, 'r')]
    subs = {'PDRN': ['Salmon DNA, the', 'K-beauty skin booster'], 'Volufiline™': ['For areas that', 'look hollow'],
            'Collagen': ['Smooths the look of', 'fine lines'], 'Hyaluronic acid': ['Pulls water in,', 'skin looks bouncy']}
    for (x, y, side), (name, _, _) in zip(spots, C.INGREDIENTS):
        a = 'l' if side == 'l' else 'r'
        text(d, (x, y), name, 38, 'Black', anchor=a + 'a')
        for k, line in enumerate(subs[name]): text(d, (x, y + 56 + k * 36), line, 26, 'Medium', fill=SOFT, anchor=a + 'a')
        lx = x + (300 if side == 'l' else -300)
        d.line([(x + (0 if side == 'l' else 0), y + 136), (lx, y + 136)], fill=(170, 172, 178), width=2)
    text(d, (W / 2, W - 70), '+ Adenosine and nourishing oils', 28, 'SemiBold', fill=INK, anchor='mb')
    return im


# 3. stick vs jar --------------------------------------------------------------------------------------------------
def stick_vs_cream():
    im = Image.new('RGB', (W, W), (236, 237, 240)); d = ImageDraw.Draw(im)
    text(d, (W / 2, 66), 'STICK VS. JAR', 50, 'Black', anchor='mt')
    text(d, (W / 2, 132), 'why a press-on stick works where creams don’t', 28, 'Medium', fill=SOFT, anchor='mt')
    # the two products, side by side
    for k, (name, box) in enumerate((('card', (.2, .1, .8, .7)), ('jar', (.16, .19, .84, .86)))):
        src = cover(crop(name, box), 470, 470)
        m = Image.new('L', src.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 469, 469), radius=28, fill=255)
        im.paste(src, (60 + k * 490, 190), m)
    d.rounded_rectangle((60, 190 + 400, 530, 190 + 470), radius=0, fill=INK)
    d.rounded_rectangle((550, 190 + 400, 1020, 190 + 470), radius=0, fill=(206, 207, 212))
    text(d, (295, 625), 'PDRN PLUMPING BALM', 25, 'Black', fill=WHITE, anchor='mm', track=.06)
    text(d, (785, 625), 'A JAR OF CREAM', 25, 'Black', fill=(90, 90, 96), anchor='mm', track=.06)
    rows = [('Goes exactly on the line', 'One film over the whole face'), ('Stays where you pressed it', 'Slides off the crease'),
            ('10 seconds, no fingers', 'Scoop, rub, wipe your hands'), ('Touch-ups from your bag', 'Stays on the shelf')]
    y = 700
    for a, b in rows:
        check(d, 92, y + 20, 17); text(d, (122, y + 20), a, 25, 'SemiBold', anchor='lm')
        cross(d, 582, y + 20, 17); text(d, (612, y + 20), b, 25, 'Medium', fill=(110, 110, 116), anchor='lm')
        y += 86
    return im


# 4. where to use it -----------------------------------------------------------------------------------------------
def where():
    im = placed(render('tilt'), 1.0, dx=250, dy=40); d = ImageDraw.Draw(im)
    text(d, (62, 80), 'ONE STICK,', 70, 'Black')
    mark(d, 60, 168, 'FIVE SPOTS', 62)
    y = 330
    for k, (a, b) in enumerate(C.WHERE['spots'], 1):
        d.ellipse((60, y, 112, y + 52), fill=INK); text(d, (86, y + 26), str(k), 26, 'Black', fill=WHITE, anchor='mm')
        text(d, (134, y + 4), a, 34, 'Black'); text(d, (134, y + 46), b, 24, 'Medium', fill=SOFT)
        y += 118
    return im


# 5. how to use: swipe, press, done --------------------------------------------------------------------------------
def how_to_use():
    im = Image.new('RGB', (W, W), (236, 237, 240)); d = ImageDraw.Draw(im)
    text(d, (W / 2, 66), 'SWIPE. PRESS. DONE.', 52, 'Black', anchor='mt')
    text(d, (W / 2, 134), '10 seconds, morning and night', 28, 'Medium', fill=SOFT, anchor='mt')
    panels = [('bullet', (.25, .02, .75, .64), 'Swipe', 'a thin layer on the spot'),
              ('open', (.20, .08, .62, .82), 'Press', 'it in, no rubbing'),
              ('front', (.30, .10, .70, .82), 'Done', 'under or over makeup')]
    for k, (name, box, h, sub) in enumerate(panels):
        x = 50 + k * 336
        src = cover(crop(name, box), 308, 560)
        m = Image.new('L', (308, 560), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 307, 559), radius=26, fill=255)
        im.paste(src, (x, 200), m)
        d.ellipse((x + 20, 220, x + 76, 276), fill=INK); text(d, (x + 48, 248), str(k + 1), 28, 'Black', fill=WHITE, anchor='mm')
        text(d, (x + 154, 800), h, 44, 'Black', anchor='mt')
        text(d, (x + 154, 862), sub, 23, 'Medium', fill=SOFT, anchor='mt')
    text(d, (W / 2, W - 60), 'Less is more: a thin layer looks smooth, too much looks shiny.', 24, 'SemiBold', anchor='mb')
    return im


# 6. texture --------------------------------------------------------------------------------------------------------
def texture():
    im = placed(render('bullet'), 1.32, dy=40); d = ImageDraw.Draw(im)
    text(d, (W / 2, 70), 'A BALM THAT', 58, 'Black', anchor='mt')
    mark(d, W / 2 - d.textlength('MELTS IN', font=vf(58, 'Black')) / 2 - 20, 144, 'MELTS IN', 58)
    text(d, (W / 2, 268), 'Cushiony, never sticky. A thin layer gives a soft, natural glow.', 26, 'SemiBold', fill=SOFT, anchor='mt')
    return im


# 7. two sticks -----------------------------------------------------------------------------------------------------
def duo():
    im = placed(render('duo'), 1.0, dy=80); d = ImageDraw.Draw(im)
    text(d, (W / 2, 70), 'ONE FOR HOME.', 56, 'Black', anchor='mt')
    w = vf(56, 'Black')
    mark(d, W / 2 - d.textlength('ONE FOR YOUR BAG.', font=w) / 2 - 20, 142, 'ONE FOR YOUR BAG.', 56)
    text(d, (W / 2, W - 70), 'Touch up your under-eyes anywhere, over makeup too.', 26, 'SemiBold', anchor='mb')
    return im


def card():
    return placed(render('card'), 1.06, dy=20)


for name, fn in [('hero', hero), ('ingredients', ingredients), ('stick-vs-cream', stick_vs_cream), ('where', where),
                 ('how-to-use', how_to_use), ('texture', texture), ('duo', duo), ('card', card)]:
    save(fn(), name)
