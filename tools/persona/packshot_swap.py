"""Swap the product in a studio packshot for the real bottle from the product sheet, without generative AI.

usage: python3 -I packshot_swap.py <product.png> <in_image> <out_image> [--height <x>] [--debug <dir>]
- product.png: a product-sheet view of the bottle on its plain grey backdrop (brand/adaptive-peptide-foundation/01-front.png)
- in_image: an old packshot on a plain light backdrop (bottle + cap, optional badges in the corners)
The old bottle and cap (the large dark objects in the lower part of the frame) and their floor shadows are removed and the
backdrop is rebuilt from a smooth fit of the surrounding background; the real bottle is cut out (its white label text and
nozzle ring kept inside the mask), scaled to the old bottle's height x <height> (default 1.12), stood on the same floor
line where the old pair stood, and given a soft contact + cast shadow in the same direction as the original's.
Everything else in the frame (badges, text) is untouched.
"""
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter
from scipy import ndimage

args = sys.argv[1:]
PRODUCT, SRC, OUT = (Path(a) for a in args[:3])
HEIGHT = float(args[args.index('--height') + 1]) if '--height' in args else 1.12
DEBUG = Path(args[args.index('--debug') + 1]) if '--debug' in args else None

def lum(a): return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114

# ---------------------------------------------------------------- 1. the real bottle, cut out
p = np.asarray(Image.open(PRODUCT).convert('RGB')).astype(np.float32)
pl = lum(p)
bg_level = np.median(np.concatenate([pl[:20].ravel(), pl[:, :20].ravel(), pl[:, -20:].ravel()]))
dark = pl < bg_level * 0.62
lab, n = ndimage.label(dark)
body = lab == (np.argmax(ndimage.sum(dark, lab, range(1, n + 1))) + 1)       # the largest dark object: the bottle
body = ndimage.binary_closing(body, iterations=3)
body = ndimage.binary_fill_holes(body)                                         # label text + nozzle ring stay in
body = ndimage.binary_erosion(body, iterations=1)                              # drop the grey fringe
ys, xs = np.nonzero(body)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
alpha = Image.fromarray((body[y0:y1, x0:x1] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
bottle = Image.fromarray(p[y0:y1, x0:x1].astype(np.uint8))

# ---------------------------------------------------------------- 2. the old objects and their shadows
s = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = s.shape[:2]
sl = lum(s)
bgv = np.percentile(sl, 75)
objs = sl < bgv * 0.55
lab, n = ndimage.label(objs)
keep = np.zeros_like(objs)
boxes = []
for i, sl_ in enumerate(ndimage.find_objects(lab), 1):
    hh, ww = sl_[0].stop - sl_[0].start, sl_[1].stop - sl_[1].start
    if hh * ww > 0.008 * H * W and sl_[0].stop > 0.5 * H:                      # bottle and cap, not badges up top
        keep |= lab == i; boxes.append(sl_)
if not boxes: sys.exit(f'{SRC.name}: no packshot objects found')
oy0 = min(b[0].start for b in boxes); oy1 = max(b[0].stop for b in boxes)
ox0 = min(b[1].start for b in boxes); ox1 = max(b[1].stop for b in boxes)
tallest = max(boxes, key=lambda b: b[0].stop - b[0].start)
old_h = tallest[0].stop - tallest[0].start
keep = ndimage.binary_fill_holes(ndimage.binary_closing(keep, iterations=4))
# floor shadows: anything darker than the backdrop in a band around the objects' base, out to the right
band = np.zeros_like(keep)
band[max(0, oy1 - int(.10 * H)):min(H, oy1 + int(.03 * H)), max(0, ox0 - int(.03 * W)):min(W, ox1 + int(.30 * W))] = True
local_bg = ndimage.median_filter(sl, size=41)
shadow = band & (sl < np.percentile(sl[band & ~keep], 90) - 3)
remove = ndimage.binary_dilation(keep | shadow, iterations=7)

# ---------------------------------------------------------------- 3. rebuild the backdrop from its own surroundings
# inpainted at a quarter size (the backdrop is smooth), so the fill continues the real neighbouring pixels
import cv2
q = 4
big = ndimage.binary_dilation(remove, iterations=max(8, W // 60))           # fill well past the old silhouettes
small = cv2.resize(s.astype(np.uint8), (W // q, H // q), interpolation=cv2.INTER_AREA)
msk = cv2.resize((big * 255).astype(np.uint8), (W // q, H // q), interpolation=cv2.INTER_NEAREST)
fill = cv2.resize(cv2.inpaint(small, msk, 8, cv2.INPAINT_TELEA), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
fill = cv2.GaussianBlur(fill, (0, 0), 6)
# exposure match: the fill must sit at the level of the backdrop right around it
ring = ndimage.binary_dilation(big, iterations=max(6, W // 120)) & ~ndimage.binary_dilation(big, iterations=2)
for c in range(3): fill[..., c] += np.median(s[..., c][ring] - fill[..., c][ring])
fill = fill + np.random.default_rng(7).normal(0, 0.8, (H, W, 1))            # the backdrop's fine noise, not flat paint
feather = ndimage.gaussian_filter(big.astype(np.float32), max(6, W // 90))[..., None]
feather = np.clip(feather * 1.6, 0, 1) * (1 - remove[..., None]) + remove[..., None]   # fully filled where the objects were
clean = s * (1 - feather) + fill * feather

# ---------------------------------------------------------------- 4. the real bottle on the same floor line
th = int(round(old_h * HEIGHT)); tw = int(round(bottle.width * th / bottle.height))
b_img = bottle.resize((tw, th), Image.LANCZOS); b_a = alpha.resize((tw, th), Image.LANCZOS)
cx = (ox0 + ox1) // 2; floor = oy1
px, py = cx - tw // 2, floor - th
canvas = Image.fromarray(np.clip(clean, 0, 255).astype(np.uint8))
# shadow: a flattened, right-leaning copy of the silhouette on the floor + a tight contact line under the base
sh = Image.new('L', (W, H), 0)
flat = b_a.resize((tw, max(3, int(th * 0.07))), Image.LANCZOS)
cast = Image.new('L', (W, H), 0); cast.paste(flat, (px + int(tw * 0.55), floor - flat.height + 2))
cast = cast.transform((W, H), Image.AFFINE, (1, 0.9, -0.9 * floor, 0, 1, 0), Image.BILINEAR).filter(ImageFilter.GaussianBlur(max(2, tw // 14)))
contact = Image.new('L', (W, H), 0); contact.paste(Image.new('L', (int(tw * 1.04), max(2, th // 70)), 255), (px - int(tw * .02), floor - max(2, th // 70) // 2))
contact = contact.filter(ImageFilter.GaussianBlur(max(1.5, tw / 40)))
shade = np.maximum(np.asarray(cast, np.float32) * 0.40, np.asarray(contact, np.float32) * 0.55) / 255
arr = np.asarray(canvas, np.float32) * (1 - shade[..., None] * 0.55)
canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
canvas.paste(b_img, (px, py), b_a)
canvas.save(OUT, quality=92) if OUT.suffix.lower() in ('.jpg', '.jpeg') else canvas.save(OUT)
if DEBUG:
    DEBUG.mkdir(parents=True, exist_ok=True)
    Image.fromarray((remove * 255).astype(np.uint8)).save(DEBUG / f'{SRC.stem}-remove.png')
print(f'{SRC.name}: old bottle {old_h}px -> real bottle {th}px at x={px}, floor y={floor}')
