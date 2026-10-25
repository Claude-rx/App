"""Put the real SKINOFAB label on the bottle in the home hero photo.

usage: python3 -I hero_label.py <upscaled.png> <label_render> <out.png> [ox oy scale]
       label_render: brand/adaptive-peptide-foundation/01-front.png (the real wordmark and label, PDRN legible)

The hero photo's bottle came from an AI product swap: its wordmark is right, but the small print is garbled ("PEPTIOE",
and "PDRN" reads like another word). Blurry it passed; a 4K upscale sharpens it. This erases the bottle's printed text
and draws the label of the real product render (SKINOFAB, ADAPTIVE PEPTIDE FOUNDATION, PDRN, 30 mL / 1.01 fl oz) in its
place, fitted to the bottle: same tilt, same wordmark size, same span as the old print. The render's small PDRN line
is set again first (label_fix.legible_pdrn), larger and bolder: drawn as printed, its D closed into an O (PORN).

Geometry is measured on the 2000 x 853 hero master (skinofab-color-changing-foundation-hero-4096w, persona set) and
the 1254 x 1254 front render (skf-apf-01-front.jpg). <upscaled.png> is that master upscaled by <scale> (default 4),
optionally a crop of it whose top-left is (ox, oy) in master pixels.
"""
import sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_fix import legible_pdrn

src, label_path, dst = sys.argv[1:4]
ox, oy, k = (float(v) for v in sys.argv[4:7]) if len(sys.argv) > 6 else (0.0, 0.0, 4.0)

# --- geometry (master pixels) --------------------------------------------------------------------------------
TILT = np.deg2rad(4.25)                       # the bottle leans right: its axis is x = 1396 - 0.0743 (y - 437)
SX = SY = 0.27                                # render -> master: the bottle's width; one scale both ways, so the
                                              # wordmark keeps its proportions (0.30 along the axis made it squat)
LABEL_C_RENDER = (627.5, 843.5)               # render: label block centre (SKINOFAB top 556 .. "30 mL" bottom 1131)
LABEL_C_HERO = (1393.5, 470.0)                # master: on the bottle axis, old print 383 .. 557.5
# the bottle body where the old print sits (master), left of x 1358 the fingers hold it
BODY = np.array([[1358, 372], [1440, 366], [1430, 566], [1358, 566]], np.float32)
TEXT_RENDER = (505, 545, 760, 1140)           # render: the label's text (x0, y0, x1, y1), bottle black around it

img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]
to_px = lambda p: ((np.asarray(p, np.float32) - [ox, oy]) * k)

# --- 1. erase the old print: bright, neutral pixels on the bottle body, inpainted from the black around them ----
body = np.zeros((H, W), np.uint8)
cv2.fillPoly(body, [to_px(BODY).astype(np.int32)], 1)
lum = img.mean(2)
neutral = (img[..., 0] - img[..., 2]) < 28   # skin is warm (red well above blue); the print is grey-white
# the print's strokes only (white ~200-255 on a bottle of 30-60 with a soft highlight up to ~95), grown over their
# anti-aliased edges; the bottle's own shading and highlight stay as photographed
old = ((body > 0) & neutral & (lum > 118)).astype(np.uint8)
old = cv2.dilate(old, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(1.5 * k) * 2 + 1,) * 2))
old &= body
bgr = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
clean = cv2.inpaint(bgr, old * 255, int(3 * k), cv2.INPAINT_TELEA)
clean = cv2.cvtColor(clean, cv2.COLOR_BGR2RGB).astype(np.float32)
# inpainting leaves faint streaks where wide letters were: smooth inside the erased area only, feathered
feather = cv2.GaussianBlur(old.astype(np.float32), (0, 0), k)[..., None]
clean = clean * (1 - feather) + cv2.GaussianBlur(clean, (0, 0), 1.5 * k) * feather

# --- 2. the real label as an alpha mask, warped onto the bottle ----------------------------------------------
# the render's PDRN line is set again first, so at a hand's size it never reads PORN (label_fix.py): here larger and
# bolder than the label's own size, because a phone draws this bottle at a quarter of the master's pixels and the line
# lands 5-7 device pixels tall (at the render's 15 px, its D blurs into an O there)
lab = np.asarray(Image.open(label_path).convert('RGB')).astype(np.float32)
if lab.shape[:2] == (1254, 1254): lab = legible_pdrn(lab, cap=22, weight=720, track=0.18)
lab = lab.mean(2)
x0, y0, x1, y1 = TEXT_RENDER
alpha_r = np.zeros_like(lab)
# the print against the bottle behind it: the render's bottle is lit by a vertical highlight stripe (up to ~160) that
# must not come along, so each column keys against its own background (a cylinder's shading is constant down it)
box = lab[y0:y1, x0:x1]
bg = np.percentile(box, 20, axis=0)[None, :]
alpha_r[y0:y1, x0:x1] = np.clip((box - bg - 30) / np.maximum(235 - bg - 30, 40), 0, 1)
c, s = np.cos(TILT), np.sin(TILT)
A = k * np.array([[c, -s], [s, c]]) @ np.diag([SX, SY])                         # render -> output pixels
t = to_px(LABEL_C_HERO) - A @ np.asarray(LABEL_C_RENDER)
M = np.hstack([A, t[:, None]]).astype(np.float32)
alpha = cv2.warpAffine(alpha_r, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=0)
alpha = np.clip(alpha * 1.12, 0, 1) * (body > 0)
# match the photo: a touch of softness and the bottle's light (brighter on the lit left, as the old print was)
alpha = cv2.GaussianBlur(alpha, (0, 0), 0.35 * k / 2)
xs = np.arange(W, dtype=np.float32)[None, :] / k + ox
ys = np.arange(H, dtype=np.float32)[:, None] / k + oy
axis = 1396 - 0.0743 * (ys - 437)
light = np.clip(1.0 - 0.10 * (xs - axis) / 40, 0.86, 1.04)                       # +-40 px from the axis
ink = (np.array([246, 246, 243], np.float32)[None, None, :] * light[..., None])
noise = np.random.default_rng(7).normal(0, 2.0, (H, W, 1)).astype(np.float32)
out = clean * (1 - alpha[..., None]) + (ink + noise) * alpha[..., None]
Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(dst)
print(f'{dst}: old print {int(old.sum())} px erased, label drawn ({int((alpha > .5).sum())} px)')
