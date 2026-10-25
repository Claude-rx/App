"""Label fixes for the Adaptive Peptide Foundation renders (brand/adaptive-peptide-foundation/01-front.png).

legible_pdrn(r): r, the 1254-px front render as a float32 RGB array, with its PDRN line set again at a readable size
(in place; also returned). Used by held_bottle.py and home_images.py before the render is scaled down.
"""
from pathlib import Path
import numpy as np
from PIL import Image

FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'


def legible_pdrn(r):
    """The render prints PDRN at an 11 px cap height, the label's other lines at 16: scaled into a hand, its D closes
    into an O and the line reads PORN. It is set again here at 15 px (Montserrat SemiBold, a little tracking: at a
    third of the size the D keeps its straight back), in the label's own place and white, its old print first filled
    from the bottle above and below it."""
    from PIL import ImageDraw, ImageFont
    x0, x1, y0, y1 = 592, 664, 1049, 1072                                   # the old PDRN line, in 01-front.png
    up, dn = r[y0 - 4:y0].mean(0), r[y1:y1 + 4].mean(0)
    for i, y in enumerate(range(y0, y1)):
        k = (i + .5) / (y1 - y0)
        r[y, x0:x1] = up[x0:x1] * (1 - k) + dn[x0:x1] * k
    SS, cap, size = 4, 15, 10.0
    while True:
        f = ImageFont.truetype(str(FONT), int(size * SS)); f.set_variation_by_axes([620])
        b = f.getbbox('H')
        if b[3] - b[1] >= cap * SS: break
        size += .5
    track, ws = 0.1 * size * SS, [f.getlength(c) for c in 'PDRN']
    layer = Image.new('L', (int(sum(ws) + track * 3) + 8 * SS, cap * SS * 2), 0)
    d, x = ImageDraw.Draw(layer), 4 * SS
    for c, w in zip('PDRN', ws):
        d.text((x, -b[1] + 2 * SS), c, font=f, fill=255); x += w + track
    layer = layer.resize((layer.width // SS, layer.height // SS), Image.LANCZOS)
    a = np.asarray(layer).astype(np.float32)[..., None] / 255
    px, py = int(627 - layer.width / 2), 1051
    reg = r[py:py + layer.height, px:px + layer.width]
    r[py:py + layer.height, px:px + layer.width] = reg * (1 - a) + 238 * a
    return r
