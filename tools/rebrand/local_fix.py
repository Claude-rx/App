"""Deterministic fixes for simple graphics where an image model would redraw too much.

usage: python3 -I local_fix.py <groups.json> <export_dir_before> <gen_dir>
- pink_to_black(n, region): brand-pink pixels (inside region, if given) become neutral greys darkening to black at
  full brand-pink strength, keeping anti-aliasing and alpha
- wordmark(n): "SMOOCHE SKIN" lockup -> SKINOFAB wordmark (white) above the original "SKIN" line
Writes <gen_dir>/<n>.png at the master's size.
"""
import colorsys, json, sys
from pathlib import Path
from PIL import Image

G = {g['n']: g for g in json.load(open(sys.argv[1]))}
IMG, GEN = Path(sys.argv[2]) / 'assets' / 'img', Path(sys.argv[3])
LOGO_WHITE = Path(__file__).resolve().parents[2] / 'tools' / 'rebrand' / 'skinofab-logo-white.png'

def pink_to_black(n, region=None):
    im = Image.open(IMG / G[n]['master']).convert('RGBA')
    px = im.load(); x0, y0, x1, y1 = region or (0, 0, im.width, im.height)
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if s > 0.18 and (h > 0.80 or h < 0.03) and r > g:
                strength = min(1.0, (r - g) / 70)            # brand pinks (r-g >= 70) -> full black
                v = max(0, min(255, round((1 - strength) * 255 * l)))
                px[x, y] = (v, v, v, a)
    im.save(GEN / f'{n}.png')

def wordmark(n, split_y):
    src = Image.open(IMG / G[n]['master']).convert('RGBA')
    out = Image.new('RGBA', src.size, (0, 0, 0, 0))
    out.alpha_composite(src.crop((0, split_y, src.width, src.height)), (0, split_y))
    logo = Image.open(LOGO_WHITE).convert('RGBA'); logo = logo.crop(logo.getbbox())
    # original lockup: text block occupies the band above split_y; match its bounding box
    top = src.crop((0, 0, src.width, split_y)); bb = top.getbbox()
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    k = min(bw / logo.width, bh / logo.height)
    logo = logo.resize((round(logo.width * k), round(logo.height * k)), Image.LANCZOS)
    out.alpha_composite(logo, ((src.width - logo.width) // 2, bb[1] + (bh - logo.height) // 2))
    out.save(GEN / f'{n}.png')

if __name__ == '__main__':
    for n in (112, 345, 691): pink_to_black(n)
    g = G[718]; pink_to_black(718, (0, int(g['h'] * 0.86), g['w'], g['h']))
    wordmark(696, int(G[696]['h'] * 0.66))
    print('done')
