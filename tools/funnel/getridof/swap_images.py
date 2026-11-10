#!/usr/bin/env python3
"""Put the new-packaging product images (brand/getridof/generated/, made with Kie Nano Banana 2 from
brand/getridof/new-pack.png) in place of the reference page's packaging shots.

    python3 tools/funnel/getridof/swap_images.py      # run after build_pdp.mjs, before campaign-build

Each target keeps its file name, pixel size and format, so every reference (PDP gallery and thumbnails, info tiles,
directions sachets, checkout gallery, exit popup) picks up the new image with no markup change. The new image is
center-cropped to the target's aspect ratio. Customer (UGC) photos are deliberately not edited.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
GEN = ROOT / 'brand/getridof/generated'
PDP = ROOT / 'campaigns/getridof/src/mouse-pouches/assets/pdp'

SWAP = {
    'hero-no-more-mice': ['t12-rodent-57d2b1.png', 't12-rodent-6095bb.png', 'P_1_1-bd629d.png'],
    'protect-your-home': ['image2-829fe1.webp', 'image2-85b991.webp'],
    'safe-kids-pets': ['image3-597645.webp', 'image3-305c8c.webp'],
    'all-natural': ['image5-4e7092.webp', 'image5-de1be6.webp'],
    'designed-with-you': ['image6-7a8fe2.webp', 'image6-d075fa.webp'],
    'why-choose-us': ['image7-6cb854.webp', 'image7-5bb25c.webp'],
    'buy2-get1-banner': ['Buy_3-707070.png'],
    'hand-drop-sachet': ['Frame_1484584678-e0d344.webp'],
    'still-life-table': ['Frame_1484584678_1-2ed920.webp'],
    'guarantee-scene': ['Gemini_Generated_Image_3vtc0h3vtc0h3vtc_2_1-16ab3c.webp'],
    'sachet-1': ['Gemini_Generated_Image_ma08i2ma08i2ma08_1_1991c301-7c7eb2.webp'],
    'sachet-5': ['Group_1484581864-71aab5.webp'],
    'sachet-8': ['Group_1484581865-9960fc.webp'],
    'sachet-3': ['Group_1484581866-04f2c7.webp'],
}


def cover(im, w, h):
    sw, sh = im.size
    scale = max(w / sw, h / sh)
    im = im.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def main():
    n = 0
    for src, targets in SWAP.items():
        new = Image.open(GEN / f'{src}.webp').convert('RGB')
        for t in targets:
            path = PDP / t
            if not path.exists(): raise SystemExit(f'missing target {t} (run build_pdp.mjs first)')
            old = Image.open(path)
            w, h = old.size
            # draw at 2x the old size (sharper on retina) unless the old one was already large
            k = 2 if max(w, h) <= 700 else 1
            out = cover(new, w * k, h * k)
            if path.suffix == '.webp': out.save(path, 'WEBP', quality=88, method=6)
            else: out.save(path, 'PNG', optimize=True)
            n += 1
    print(f'swapped {n} images from {len(SWAP)} new-packaging renders')


if __name__ == '__main__':
    main()
