"""Label fixes for the Adaptive Peptide Foundation renders (brand/adaptive-peptide-foundation/01-front.png).

legible_pdrn(r): r, the 1254-px front render as a float32 RGB array, with its PDRN line set again at a readable size
(in place; also returned). Used by held_bottle.py and home_images.py before the render is scaled down.
"""
from pathlib import Path
import numpy as np
from PIL import Image

FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
# legible_pdrn's sizes by how small the bottle is shown: BOLD for ~100-150 px wide on screen (a card, the home hero),
# XL for ~40-80 px (the phenomenon cards, the shelf and bundle cards, the catalogue thumbnail; review 4)
BOLD = {'cap': 22, 'weight': 720, 'track': 0.18}
XL = {'cap': 40, 'weight': 800, 'track': 0.12}


def legible_pdrn(r, cap=15, weight=620, track=0.1):
    """The render prints PDRN at an 11 px cap height, the label's other lines at 16: scaled into a hand, its D closes
    into an O and the line reads PORN. It is set again here at 15 px (Montserrat SemiBold, a little tracking: at a
    third of the size the D keeps its straight back), in the label's own place and white, its old print first filled
    from the bottle above and below it. A photo that shows the bottle smaller still (the home hero on a phone: the
    line a few device pixels tall) passes a larger cap, weight and tracking; the line stays centred where it was."""
    from PIL import ImageDraw, ImageFont
    x0, x1, y0, y1 = 592, 664, 1049, 1072                                   # the old PDRN line, in 01-front.png
    up, dn = r[y0 - 4:y0].mean(0), r[y1:y1 + 4].mean(0)
    for i, y in enumerate(range(y0, y1)):
        k = (i + .5) / (y1 - y0)
        r[y, x0:x1] = up[x0:x1] * (1 - k) + dn[x0:x1] * k
    SS, size = 4, 10.0
    while True:
        f = ImageFont.truetype(str(FONT), int(size * SS)); f.set_variation_by_axes([weight])
        b = f.getbbox('H')
        if b[3] - b[1] >= cap * SS: break
        size += .5
    track, ws = track * size * SS, [f.getlength(c) for c in 'PDRN']
    layer = Image.new('L', (int(sum(ws) + track * 3) + 8 * SS, cap * SS * 2), 0)
    d, x = ImageDraw.Draw(layer), 4 * SS
    for c, w in zip('PDRN', ws):
        d.text((x, -b[1] + 2 * SS), c, font=f, fill=255); x += w + track
    layer = layer.resize((layer.width // SS, layer.height // SS), Image.LANCZOS)
    a = np.asarray(layer).astype(np.float32)[..., None] / 255
    px, py = int(627 - layer.width / 2), round((y0 + y1) / 2 - cap / 2 - 2)     # 1051 at cap 15
    reg = r[py:py + layer.height, px:px + layer.width]
    r[py:py + layer.height, px:px + layer.width] = reg * (1 - a) + 238 * a
    return r


def retype_line(r, box, text, ink=None, weight=620, track=0.08, SS=4):
    """r (float32 RGB array) with the printed line inside box (x0, y0, x1, y1: the old letters, a few px of margin)
    set again in Montserrat at weight, at the old line's cap height and width, along its curve (a label around a
    cylinder seen from a little above smiles: the old letters' bottoms give it), in its ink (default: the old print's).
    The old print is filled first, each column from the bottle just above and below it. In place; also returned.
    The balm's AI-drawn "PDRN · VOLUFILINE" is a light weight whose D closes into an O at a thumbnail's size."""
    from PIL import ImageDraw, ImageFont
    x0, y0, x1, y1 = box
    lum = r[y0:y1, x0:x1].mean(2)
    lit = lum > 120
    if ink is None: ink = float(np.percentile(lum[lit], 90)) * 0.95
    cols = np.nonzero(lit.any(0))[0]
    groups = np.split(cols, np.nonzero(np.diff(cols) > 1)[0] + 1)
    pts = []
    for g in groups:
        if len(g) < 3: continue                                     # the dot
        rows = np.nonzero(lit[:, g[0]:g[-1] + 1].any(1))[0]
        pts.append(((g[0] + g[-1]) / 2 + x0, rows.max() + y0, rows.min() + y0))
    pts = np.array(pts)
    curve = np.polyfit(pts[:, 0], pts[:, 1], 2)                    # the baseline, y(x)
    cap = float(np.median(pts[:, 1] - pts[:, 2]) + 1)
    lx0, lx1 = x0 + cols.min(), x0 + cols.max() + 1
    up, dn = r[y0 - 4:y0].mean(0), r[y1:y1 + 4].mean(0)
    for i, y in enumerate(range(y0, y1)):
        k = (i + .5) / (y1 - y0)
        r[y, x0:x1] = up[x0:x1] * (1 - k) + dn[x0:x1] * k
    size = cap
    while True:
        f = ImageFont.truetype(str(FONT), int(size * SS)); f.set_variation_by_axes([weight])
        b = f.getbbox('H')
        if b[3] - b[1] >= cap * SS: break
        size += .25
    ws = [f.getlength(c) for c in text]
    tr = track * size * SS
    while sum(ws) + tr * (len(text) - 1) > (lx1 - lx0) * SS * 1.04 and tr > 0: tr -= 0.25 * SS
    width = sum(ws) + tr * (len(text) - 1)
    # each letter whole on the curve, at its own centre's baseline (drawn 4x over the box, then scaled down)
    lo, hi = pts[:, 0].min(), pts[:, 0].max()
    canvas = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0)
    d = ImageDraw.Draw(canvas)
    x = ((lx0 + lx1) / 2 - x0) * SS - width / 2
    for c, w in zip(text, ws):
        cx = x0 + (x + w / 2) / SS
        base = np.polyval(curve, np.clip(cx, lo, hi)) + 1 - y0
        d.text((x, base * SS), c, font=f, fill=255, anchor='ls'); x += w + tr
    a = np.asarray(canvas.resize((x1 - x0, y1 - y0), Image.LANCZOS)).astype(np.float32)[..., None] / 255
    r[y0:y1, x0:x1] = r[y0:y1, x0:x1] * (1 - a) + ink * a
    return r


def bold_line(r, box, text, cap, weight=780, track=0.22, ink=None, SS=4):
    """r (float32 RGB array) with the printed line inside box (x0, y0, x1, y1) replaced by text, straight, centred
    on the box, at cap px cap height (larger than the old print: the box's height at most) in a heavy weight with wide
    tracking. For a photo shown so small that the label's own line, retyped at its size, is a few pixels tall: the
    balm's "PDRN · VOLUFILINE" on the comparison card read PORN; there it becomes a bold "PDRN" across the line.
    The old print is filled first, each column from the bottle just above and below it. In place; also returned."""
    from PIL import ImageDraw, ImageFont
    x0, y0, x1, y1 = box
    lum = r[y0:y1, x0:x1].mean(2)
    if ink is None: ink = float(np.percentile(lum[lum > 120], 90)) * 0.95 if (lum > 120).any() else 235.0
    up, dn = r[y0 - 4:y0].mean(0), r[y1:y1 + 4].mean(0)
    for i, y in enumerate(range(y0, y1)):
        k = (i + .5) / (y1 - y0)
        r[y, x0:x1] = up[x0:x1] * (1 - k) + dn[x0:x1] * k
    size = cap
    while True:
        f = ImageFont.truetype(str(FONT), int(size * SS)); f.set_variation_by_axes([weight])
        b = f.getbbox('H')
        if b[3] - b[1] >= cap * SS: break
        size += .25
    ws = [f.getlength(c) for c in text]
    tr = track * size * SS
    while sum(ws) + tr * (len(text) - 1) > (x1 - x0) * SS * 0.96 and tr > 0: tr -= 0.25 * SS
    width = sum(ws) + tr * (len(text) - 1)
    canvas = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0)
    d = ImageDraw.Draw(canvas)
    x, base = ((x1 - x0) * SS - width) / 2, ((y1 - y0) / 2 + cap / 2) * SS
    for c, w in zip(text, ws):
        d.text((x, base), c, font=f, fill=255, anchor='ls'); x += w + tr
    a = np.asarray(canvas.resize((x1 - x0, y1 - y0), Image.LANCZOS)).astype(np.float32)[..., None] / 255
    r[y0:y1, x0:x1] = r[y0:y1, x0:x1] * (1 - a) + ink * a
    return r


def bold_line_rot(r, center, angle, size, text, cap, **kw):
    """bold_line for a line printed at an angle (degrees, clockwise: the bottle held tilted): the area around it turned
    level, the line set again there, turned back; only the line's own box (feathered) goes back into r. center: the
    old line's centre; size: its box (w, h) when level. In place; also returned."""
    from PIL import ImageFilter
    w, h = size
    side = int(2 * max(w, h) + 12) | 1
    cx, cy = center
    x0, y0 = int(round(cx - side / 2)), int(round(cy - side / 2))
    patch = Image.fromarray(np.clip(r[y0:y0 + side, x0:x0 + side] + 0.5, 0, 255).astype(np.uint8))
    level = patch.rotate(angle, resample=Image.BICUBIC, center=(cx - x0, cy - y0))
    a = np.asarray(level).astype(np.float32).copy()
    bx0, by0 = int(round(cx - x0 - w / 2)), int(round(cy - y0 - h / 2))
    bold_line(a, (bx0, by0, bx0 + w, by0 + h), text, cap, **kw)
    back = np.asarray(Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)).rotate(-angle, resample=Image.BICUBIC,
                                                                                         center=(cx - x0, cy - y0))).astype(np.float32)
    m = Image.new('L', (side, side), 0)
    m.paste(255, (bx0 - 1, by0 - 1, bx0 + w + 1, by0 + h + 1))
    m = np.asarray(m.rotate(-angle, resample=Image.BICUBIC, center=(cx - x0, cy - y0)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32)[..., None] / 255
    r[y0:y0 + side, x0:x0 + side] = r[y0:y0 + side, x0:x0 + side] * (1 - m) + back * m
    return r
