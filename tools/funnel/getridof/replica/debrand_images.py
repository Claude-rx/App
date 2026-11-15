#!/usr/bin/env python3
"""One-off brand pass over campaigns/getridof/src/mouse-pouches/assets/pdp (the images every Get Rid Of funnel copies).

    python3 -I tools/funnel/getridof/replica/debrand_images.py

The replica product page shows images the lean sales page never used, and a review of all of them found the old brand
name on eight. This script fixes those files in place (same names and proportions, so no markup changes):

  - customer photos (4): replaced by the de-branded versions in brand/getridof/sections/gro-ugc-*.webp
  - phone version of the "Safe home" photo and the third "All natural" tile: the Get Rid Of packaging renders in
    brand/getridof/generated/ that their desktop versions already use
  - small "No more mice" thumbnails (2): redrawn from the corrected first gallery photo (90-day guarantee)
  - "Works everywhere" tile: the brand word painted out on the bag and on the pouch; its thumbnail redrawn from it

Safe to run again.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
PDP = ROOT / 'campaigns/getridof/src/mouse-pouches/assets/pdp'
GEN = ROOT / 'brand/getridof/generated'
SEC = ROOT / 'brand/getridof/sections'

REPLACE = {   # target in assets/pdp -> source image
    'Screenshot_2026-03-07_at_183516_1-0fbef3.webp': SEC / 'gro-ugc-1.webp',
    'Screenshot_2026-03-07_at_183534_1-b34a99.webp': SEC / 'gro-ugc-2.webp',
    'Screenshot_2026-03-07_at_185304_1-7740d8.webp': SEC / 'gro-ugc-3.webp',
    'Frame_1484584680-0137e2.webp': SEC / 'gro-ugc-4.webp',
    'Frame_1484584549-5421fa.webp': GEN / 'hand-drop-sachet.webp',
    'image5-4979c3.webp': GEN / 'all-natural.webp',
    'P_1_1-bd629d.png': PDP / 't12-rodent-57d2b1.png',
    # the header menu's product picture in the 15 Nov capture (not in the first one: its size comes from the capture)
    'Screenshot2026-06-23at40710PM_5a7d1618-cb1a-4023-b-40542d.png': PDP / 't12-rodent-57d2b1.png',
}
CAPTURE = ROOT / 'exports/sofyre/live-desktop/assets'
# "Works everywhere": where the brand word sits, as fractions of the image (x0, y0, x1, y1)
WORD_ON_BAG = (0.474, 0.414, 0.524, 0.436)
WORD_ON_POUCH = (0.548, 0.574, 0.616, 0.601)


def cover(im, w, h):
    sw, sh = im.size
    k = max(w / sw, h / sh)
    im = im.resize((round(sw * k), round(sh * k)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def save(im, path):
    if path.suffix == '.webp': im.save(path, 'WEBP', quality=86, method=6)
    else: im.save(path, 'PNG', optimize=True)


def paint_out(im, box):
    """Fill a box by blending, column by column, the row just above it into the row just below it."""
    w, h = im.size
    x0, y0, x1, y1 = (round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h))
    px = im.load()
    for x in range(x0, x1 + 1):
        top, bot = px[x, y0 - 2], px[x, y1 + 2]
        for y in range(y0, y1 + 1):
            k = (y - y0) / max(1, y1 - y0)
            px[x, y] = tuple(round(top[c] * (1 - k) + bot[c] * k) for c in range(3))


def main():
    for name, src in REPLACE.items():
        dst = PDP / name
        w, h = Image.open(dst if dst.exists() else CAPTURE / name).size
        new = Image.open(src).convert('RGB')
        k = 2 if max(w, h) <= 400 else 1
        save(cover(new, w * k, h * k) if (w * k, h * k) != new.size else new, dst)
        print(f'{name}: from {src.relative_to(ROOT)}')
    big, small = PDP / 'image4-ef9455.webp', PDP / 'image4-aa03a3.webp'
    im = Image.open(big).convert('RGB')
    paint_out(im, WORD_ON_BAG); paint_out(im, WORD_ON_POUCH)
    save(im, big)
    save(im.resize((512, 512), Image.LANCZOS), small)   # the thumbnail is the same picture: redrawn from the fixed one
    print('image4 (2 sizes): brand word painted out')
    # keep the render the swap script uses in step with the corrected first gallery photo
    Image.open(PDP / 't12-rodent-57d2b1.png').convert('RGB').save(GEN / 'hero-no-more-mice.webp', 'WEBP', quality=90, method=6)


if __name__ == '__main__':
    main()
