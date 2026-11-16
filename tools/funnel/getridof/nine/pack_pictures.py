#!/usr/bin/env python3
"""Get Rid Of — product pictures for the 9-reason funnel, made from the REAL pack photo (brand/getridof/new-pack.png).

    python3 -I tools/funnel/getridof/nine/pack_pictures.py      # writes brand/getridof/sections/gro-n9-{ingredients,pack,guarantee}.webp

Image generators cannot spell the small print on a label, so no picture that shows the bag's label is generated:
the real pack is cut out of its photo and placed on a generated still life with no packaging in it
(gro-n9-still-bg.webp) or on a plain studio background. The 90-day seal is drawn here.

The cutout: the bag is dark on a light background, but its white label panel touches that background, so the outline
is measured on the dark rows and carried straight across the panel rows (the bag's sides are straight).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[4]
B = ROOT / 'brand/getridof/sections'


def cutout():
    im = Image.open(ROOT / 'brand/getridof/new-pack.png').convert('RGB')
    a = np.asarray(im).astype(int); h, w, _ = a.shape
    dark = a.mean(axis=2) < 110
    rows = {}
    for y in range(4, h - 2):
        xs = np.where(dark[y, 20:440])[0]          # ignore the photo's dark frame at the far right
        if len(xs) > 200: rows[y] = (xs[0] + 20, xs[-1] + 20)
    ys = sorted(rows)
    top, bottom = ys[0], ys[-1]
    body = [y for y in ys if 60 < y < 400]
    left = int(np.median([rows[y][0] for y in body])); right = int(np.median([rows[y][1] for y in body]))
    s, k = 4, 3
    m = Image.new('L', (w * s, h * s), 0)
    ImageDraw.Draw(m).rounded_rectangle((left * s, top * s, (right + 1) * s, (bottom + 1) * s), radius=14 * s, fill=255)
    mask = m.resize((w * k, h * k), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
    big = im.resize((w * k, h * k), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.2, percent=85, threshold=2))
    out = big.convert('RGBA'); out.putalpha(mask)
    return out.crop((left * k - 6, top * k - 6, (right + 1) * k + 6, (bottom + 1) * k + 6))


pack = cutout()


def place(bg, height, cx, base_y, shadow=True):
    p = pack.resize((round(pack.width * height / pack.height), height), Image.LANCZOS)
    x, y = round(cx - p.width / 2), base_y - height
    if shadow:   # soft contact shadow under and behind the bag
        sh = Image.new('RGBA', bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        d.ellipse((x - p.width * .08, base_y - height * .035, x + p.width * 1.12, base_y + height * .045), fill=(0, 0, 0, 120))
        sh = sh.filter(ImageFilter.GaussianBlur(height * .03))
        bg.alpha_composite(sh)
        sh2 = Image.new('RGBA', bg.size, (0, 0, 0, 0)); sh2.paste((0, 0, 0, 70), (x + round(p.width * .05), y + round(height * .03)), p.split()[3])
        bg.alpha_composite(sh2.filter(ImageFilter.GaussianBlur(height * .035)))
    bg.alpha_composite(p, (x, y))
    return bg


# 1. reason 2: the pack among its ingredients
st = Image.open(B / 'gro-n9-still-bg.webp').convert('RGBA')
W, H = st.size
st = place(st, round(H * .66), round(W * .56), round(H * .80))
st.convert('RGB').save(B / 'gro-n9-ingredients.webp', 'WEBP', quality=90, method=6)

# 2. offer pages: the pack on a soft studio background
def studio(size, top, bot):
    g = Image.new('RGB', size, top); d = ImageDraw.Draw(g)
    for y in range(size[1]):
        t = y / size[1]; d.line((0, y, size[0], y), fill=tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g.convert('RGBA')
o = studio((1000, 1000), (246, 248, 242), (224, 231, 214))
o = place(o, 820, 500, 930)
o.convert('RGB').save(B / 'gro-n9-pack.webp', 'WEBP', quality=90, method=6)

# 3. guarantee section: the pack with a 90-day seal drawn here (no generated lettering)
g = studio((1000, 1100), (240, 245, 233), (214, 226, 200))
g = place(g, 860, 470, 1020)
seal = Image.new('RGBA', (360, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(seal)
d.ellipse((6, 6, 354, 354), fill=(35, 55, 43, 255), outline=(207, 229, 154, 255), width=10)
d.ellipse((30, 30, 330, 330), outline=(207, 229, 154, 255), width=3)
fb = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ctext(y, text, size, fill):
    f = ImageFont.truetype(fb, size); w = d.textlength(text, font=f); d.text(((360 - w) / 2, y), text, font=f, fill=fill)
ctext(54, '90', 112, (255, 255, 255, 255)); ctext(170, 'DAY', 42, (207, 229, 154, 255)); ctext(222, 'MONEY BACK', 29, (255, 255, 255, 255)); ctext(258, 'GUARANTEE', 25, (207, 229, 154, 255))
g.alpha_composite(seal.rotate(-8, resample=Image.BICUBIC, expand=False), (610, 690))
g.convert('RGB').save(B / 'gro-n9-guarantee.webp', 'WEBP', quality=90, method=6)
print('wrote gro-n9-ingredients.webp, gro-n9-pack.webp, gro-n9-guarantee.webp')
