"""Put the real Adaptive Peptide Foundation bottle into a photo, in place of the bottle a hand holds, without
generative AI: the product-sheet render is the bottle (so its label reads exactly SKINOFAB / ADAPTIVE PEPTIDE
FOUNDATION / PDRN / 30 mL / 1.01 fl oz), and the face, hands, framing and light stay the photo's, pixel for pixel.

usage: python3 -I held_bottle.py <photo> <out> (--roi x0,y0,x1,y1 --pump up|down|left|right | --line bx,by,px,py --w px)
                                 [--render brand/adaptive-peptide-foundation/01-front.png] [--width 1.0]
                                 [--anchor base|pump|centre] [--shift dx,dy] [--fingers left|right] [--tone photo|render]
                                 [--pdrn label|bold|xl]
                                 [--debug <dir>]
- roi: a box around the old bottle (photo px); in it the old bottle is the largest neutral black object (brown hair
  and grey shadows are not), thin attachments trimmed off
- line, w: the old bottle measured by hand instead: the centre of its base end, the centre of its pump end, its width
- pump: which way the old bottle's cap / pump end points in the photo
- the render's bottle (cut out of its plain backdrop, label and nozzle ring kept) is laid on the old bottle's axis at
  its width (x --width); its length comes from the render's own proportions, measured from the --anchor end (base: the
  end in the hand stays put, so a slimmer, taller bottle grows past the old cap); --shift moves it (photo px)
- in front of it stays what was in front of the old bottle and is skin: the fingers and thumb holding it
- fingers: the side the hand holds it from (in the photo); skin there that the new bottle covers and that runs on from
  the hand outside it (a fingertip at the old bottle's edge, under a wider new one) stays in front too
- what is left of the old bottle outside the new one is filled from around it (inpainting the whole old bottle from
  outside it, so the fill is the background and skin beside it, never the old bottle's own black)
- the new bottle gets the photo's tones (the old bottle's dark and highlight levels) and its softness; --tone render
  keeps the render's own (for a photo whose old bottle was lit flatter than the real one: its label would turn grey)
- the render's small PDRN line is set again at the label's other lines' size first, so it never reads PORN
  (label_fix.legible_pdrn); --pdrn bold sets it larger and heavier, for a bottle shown only ~100 px wide; --pdrn xl
  larger still, for one shown ~40-80 px wide
"""
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).resolve().parent))
import label_fix
from label_fix import legible_pdrn

args = sys.argv[1:]
SRC, OUT = Path(args[0]), Path(args[1])
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
LINE = [float(v) for v in opt('--line').split(',')] if opt('--line') else None
ROI = [int(v) for v in opt('--roi').split(',')] if opt('--roi') else None
PUMP = opt('--pump', 'up')
RENDER = Path(opt('--render', Path(__file__).resolve().parents[2] / 'brand' / 'adaptive-peptide-foundation' / '01-front.png'))
WIDTH, ANCHOR = float(opt('--width', 1.0)), opt('--anchor', 'base')
SHIFT = np.array([float(v) for v in opt('--shift', '0,0').split(',')])
FINGERS = opt('--fingers')
TONE = opt('--tone', 'photo')
PDRN = opt('--pdrn', 'label')
DEBUG = Path(opt('--debug')) if opt('--debug') else None
lum = lambda a: a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114

# ---------------------------------------------------------------- 1. the old bottle: axis, width, ends
photo = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = photo.shape[:2]
pl = lum(photo)
black = (pl < 70) & (photo.max(2) - photo.min(2) < 22)                       # the bottle: neutral and near black
if LINE:
    base_pt, pump_pt = np.array(LINE[:2]), np.array(LINE[2:])
    u = (pump_pt - base_pt) / np.linalg.norm(pump_pt - base_pt); v = np.array([-u[1], u[0]])
    w_old = float(opt('--w'))
    yy, xx = np.mgrid[0:H, 0:W]
    rel = np.stack([xx - base_pt[0], yy - base_pt[1]], -1)
    along, across = rel @ u, rel @ v
    near = (along > -12) & (along < np.linalg.norm(pump_pt - base_pt) + 12) & (np.abs(across) < w_old * 0.58)
    old = ndimage.binary_fill_holes(ndimage.binary_closing(black & near, iterations=4))
    x0, y0 = int(max(0, min(base_pt[0], pump_pt[0]) - w_old)), int(max(0, min(base_pt[1], pump_pt[1]) - w_old))
    x1, y1 = int(min(W, max(base_pt[0], pump_pt[0]) + w_old)), int(min(H, max(base_pt[1], pump_pt[1]) + w_old))
else:
    x0, y0, x1, y1 = ROI
    dark = np.zeros((H, W), bool)
    dark[y0:y1, x0:x1] = black[y0:y1, x0:x1]
    lab, n = ndimage.label(dark)
    old = lab == (np.argmax(ndimage.sum(dark, lab, range(1, n + 1))) + 1)
    old = ndimage.binary_fill_holes(ndimage.binary_closing(old, iterations=4))    # its print is inside it
    trimmed = ndimage.binary_opening(old, iterations=6)                            # shadows and hair joined to it
    lab, n = ndimage.label(trimmed)
    if n: old = lab == (np.argmax(ndimage.sum(trimmed, lab, range(1, n + 1))) + 1)
    ys, xs = np.nonzero(old)
    pts = np.stack([xs, ys], 1).astype(np.float64)
    c = pts.mean(0)
    u = np.linalg.eigh(np.cov((pts - c).T))[1][:, -1]                            # the long axis
    want = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}[PUMP]
    if u @ want < 0: u = -u                                                       # u points at the pump end
    v = np.array([-u[1], u[0]])                                                   # across, as the render's x
    a, b = (pts - c) @ u, (pts - c) @ v
    # its width: the fingers hide some of it, so the widest slices along the axis (80th percentile) are its width
    edges = np.linspace(a.min(), a.max(), 40)
    widths = [np.ptp(b[(a >= e0) & (a < e1)]) for e0, e1 in zip(edges[:-1], edges[1:]) if ((a >= e0) & (a < e1)).sum() > 10]
    w_old = float(np.percentile(widths, 80))
    mid_b = float(np.median(b))
    base_pt, pump_pt = c + a.min() * u + mid_b * v, c + a.max() * u + mid_b * v

# ---------------------------------------------------------------- 2. the real bottle, cut out of the render
r = np.asarray(Image.open(RENDER).convert('RGB')).astype(np.float32)
# label_fix.py; --pdrn bold: larger and heavier, for a bottle a card shows only ~100 px wide (as the home hero's); xl
# for one shown ~40-80 px wide
if RENDER.name == '01-front.png' and r.shape[:2] == (1254, 1254):
    r = legible_pdrn(r, **{'bold': label_fix.BOLD, 'xl': label_fix.XL}.get(PDRN, {}))
rl = lum(r)
bg = np.median(np.concatenate([rl[:20].ravel(), rl[:, :20].ravel(), rl[:, -20:].ravel()]))
rd = rl < bg * 0.62
rlab, rn = ndimage.label(rd)
body = rlab == (np.argmax(ndimage.sum(rd, rlab, range(1, rn + 1))) + 1)
body = ndimage.binary_erosion(ndimage.binary_fill_holes(ndimage.binary_closing(body, iterations=3)), iterations=1)
ry, rx = np.nonzero(body)
rb = (rx.min(), ry.min(), rx.max() + 1, ry.max() + 1)
crop = r[rb[1]:rb[3], rb[0]:rb[2]]
calpha = cv2.GaussianBlur(body[rb[1]:rb[3], rb[0]:rb[2]].astype(np.float32), (0, 0), 0.8)
rh, rw = crop.shape[:2]

# ---------------------------------------------------------------- 3. where it goes
w_new = w_old * WIDTH
l_new = w_new * rh / rw
if ANCHOR == 'base': top = base_pt + l_new * u
elif ANCHOR == 'pump': top = pump_pt
else: top = (base_pt + pump_pt) / 2 + l_new / 2 * u
top = top + SHIFT
s = w_new / rw
# render (x right, y down from the pump end) -> photo: P = top + (x - rw/2) s v - y s u
M = np.array([[s * v[0], -s * u[0], top[0] - rw / 2 * s * v[0]],
              [s * v[1], -s * u[1], top[1] - rw / 2 * s * v[1]]], np.float32)
sharp = cv2.warpAffine(crop, M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC, borderValue=(0, 0, 0))
alpha = cv2.warpAffine(calpha, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
new = alpha > 0.5

# ---------------------------------------------------------------- 4. its tones and softness from the old bottle
def levels(img, mask):
    l = lum(img)[mask]
    return np.percentile(l, 35), np.percentile(l, 97)
old_body = old & black
p_lo, p_hi = levels(photo, old_body)
r_lo, r_hi = levels(sharp, new & (lum(sharp) < 85))
gain = float(np.clip((p_hi - p_lo) / max(r_hi - r_lo, 1), 0.6, 1.4)) if TONE == 'photo' else 1.0
toned = np.clip((sharp - r_lo) * gain + p_lo, 0, 255) if TONE == 'photo' else sharp
toned = cv2.GaussianBlur(toned, (0, 0), 0.6)                                 # the photo is a touch soft too

# ---------------------------------------------------------------- 5. in front: the fingers; behind: the rest
R, G, B = photo[..., 0], photo[..., 1], photo[..., 2]
skin = (R > G) & (G > B * 0.9) & (R - B > 12) & (pl > 70) & (pl < 248)
# in front are only the fingers that crossed the old bottle (skin inside its outline); skin outside it that the new
# bottle covers (a wider or longer bottle) is behind the new one
hull = np.zeros((H, W), np.uint8)                                   # the old bottle's outline: its black, convex
ys, xs = np.nonzero(old)
cv2.fillConvexPoly(hull, cv2.convexHull(np.stack([xs, ys], 1).astype(np.int32)), 1)
reach = cv2.erode(hull, np.ones((5, 5), np.uint8)) > 0             # well inside it: skin at its edge is beside it
front = ndimage.binary_opening(skin & reach & new, iterations=1)
if FINGERS:
    # the hand's side of the new bottle: skin there that runs on from skin outside the bottle (its finger)
    yy, xx = np.mgrid[0:H, 0:W]
    across_new = (np.stack([xx - top[0], yy - top[1]], -1) @ v)
    side = (across_new < 0) if (FINGERS == 'left') == (v[0] > 0) else (across_new > 0)
    lab, n = ndimage.label(ndimage.binary_opening(skin, iterations=1))
    outside = np.unique(lab[(lab > 0) & ~(cv2.dilate(new.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)])
    tips = new & side & np.isin(lab, outside) & ~front
    front = front | tips
lab, n = ndimage.label(front)                                         # fingers, not specks of warm print on the old one
if n:
    keep = np.nonzero(ndimage.sum(front, lab, range(1, n + 1)) >= 0.03 * w_old ** 2)[0] + 1
    front = np.isin(lab, keep)
front = cv2.GaussianBlur(front.astype(np.float32), (0, 0), 1.0)
front = np.clip(front * 1.6, 0, 1)
out = photo.copy()
# the whole old bottle is filled from what is around it (not from itself), then the new one goes on top: where the
# old one was wider or longer, the fill shows
gone = (cv2.dilate(old.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0) & ~skin
left_over = gone & ~new
if left_over.any():
    out = cv2.inpaint(out.astype(np.uint8), gone.astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA).astype(np.float32)
k = (alpha * (1 - front))[..., None]
out = out * (1 - k) + toned * k
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(OUT, quality=95)
print(f'{OUT}: old bottle {w_old:.1f} px wide, axis {np.degrees(np.arctan2(u[1], u[0])):.1f} deg; new bottle '
      f'{w_new:.1f} x {l_new:.1f} px from its {ANCHOR}; tone gain {gain:.2f}; filled {int(left_over.sum())} px of the old one')
if DEBUG:
    DEBUG.mkdir(parents=True, exist_ok=True)
    pad = 40
    bx0, by0 = max(0, x0 - pad), max(0, y0 - pad)
    bx1, by1 = min(W, x1 + pad), min(H, y1 + pad)
    dbg = np.concatenate([photo[by0:by1, bx0:bx1], out[by0:by1, bx0:bx1]], 1).astype(np.uint8)
    Image.fromarray(dbg).save(DEBUG / f'{OUT.stem}-before-after.jpg', quality=90)
