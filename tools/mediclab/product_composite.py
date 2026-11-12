#!/usr/bin/env python3
"""MedicLab product compositor: puts the REAL Berberine bottle (docs/mediclab/product/berberine-front-cutout.png, cut
from the official product photo) into lifestyle photos, so every image shows the same product, design and proportions.

Workflow: an image model (Kie.ai Nano Banana 2 / GPT Image 2.5) replaces the bottle in a scene with a flat magenta
matte of the bottle's outline at real-world size (10 cm tall), fingers in front; this script keys the matte out and fits
the real product to it.

usage: python3 -I tools/mediclab/product_composite.py <matte.png> <out.png> [blob=largest|right] [source=<scene.png>]

Chroma-key compositor: the scene has a flat magenta bottle matte (AI placeholder, fingers in front); the real
product cutout is fitted to the matte (by height, true 1.83 aspect, centred) and shown only where the matte is
(occluders such as fingers stay in front). Light: gain from the scene around the bottle + left/right gradient; the
magenta's edge spill is removed; grain and a touch of blur to sit in the photo."""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

D = __file__.rsplit('/', 1)[0]
CUT = Image.open(str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'docs' / 'mediclab' / 'product' / 'berberine-front-cutout.png')).convert('RGBA')
CREAM_REF = np.array([238., 232., 220.])     # the label paper of the product photo (studio light)

def magenta(A, tol=70):
    r, g, b = A[..., 0], A[..., 1], A[..., 2]
    return (r > 150) & (b > 120) & (g < 120) & (r - g > tol) & (b - g > tol - 20)

def key(scene, out, light=None, scale_adj=1.0, dy=0, grain=1.8, blur=0.5, blob='largest', source=None):
    sc = Image.open(scene).convert('RGB'); A = np.asarray(sc).astype(float)
    M = magenta(A)
    M = ndimage.binary_opening(M, iterations=1)
    lab, n = ndimage.label(M); sizes = ndimage.sum(M, lab, range(1, n + 1))
    big = [i + 1 for i in range(n) if sizes[i] > 0.15 * sizes.max()]
    if blob == 'right':
        pick = max(big, key=lambda i: ndimage.center_of_mass(M, lab, i)[1])
    else:
        pick = int(np.argmax(sizes)) + 1
    others = np.isin(lab, [i for i in big if i != pick])
    M = lab == pick
    if others.any() and source:
        src = Image.open(source).convert('RGB').resize(sc.size, Image.LANCZOS)
        om = Image.fromarray((ndimage.binary_dilation(others, iterations=6) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(3))
        sc.paste(src, (0, 0), om); A = np.asarray(sc).astype(float)
    ys, xs = np.nonzero(M); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    # bottle height from the matte: top of the cap to the base; width follows the real aspect
    h = (y1 - y0) * scale_adj; w = h * CUT.width / CUT.height
    cx = (x0 + x1) / 2 if (x1 - x0) > 0.75 * w else xs[ys < y0 + (y1 - y0) * 0.2].mean()   # cap centre if the sides are hidden
    cut = CUT.resize((int(w), int(h)), Image.LANCZOS); ox, oy = int(cx - w / 2), int(y1 - h) + dy
    C = np.asarray(cut).astype(float)
    # light: scene brightness and tint around the bottle, gradient left to right
    pad = int(w * 0.6)
    ring = A[max(y0 - pad // 2, 0):min(y1, A.shape[0]), max(x0 - pad, 0):min(x1 + pad, A.shape[1])]
    ringM = M[max(y0 - pad // 2, 0):min(y1, A.shape[0]), max(x0 - pad, 0):min(x1 + pad, A.shape[1])]
    env = ring[~ringM].reshape(-1, 3)
    sat = env.max(1) - env.min(1); neutral = env[(sat < np.percentile(sat, 35))]           # near-grey surfaces show the light's colour
    bright = env[env.mean(1) > np.percentile(env.mean(1), 70)].mean(0)
    nb = neutral[neutral.mean(1) > np.percentile(neutral.mean(1), 50)].mean(0) if len(neutral) > 50 else bright
    k = float(np.clip((nb[0] - nb[2]) / nb.mean() / 2, -0.03, 0.05))
    tint = np.array([1 + k, 1.0, 1 - k])                            # warm/cool only, never a green or magenta cast
    expo = light if light is not None else np.clip(bright.mean() / 205.0, 0.8, 1.08)
    Lside = A[y0:y1, max(x0 - pad, 0):x0].reshape(-1, 3).mean(); Rside = A[y0:y1, x1:x1 + pad].reshape(-1, 3).mean()
    gr = np.clip(np.linspace(1 + 0.08 * np.sign(Lside - Rside), 1 - 0.08 * np.sign(Lside - Rside), int(w)), 0.85, 1.15) if abs(Lside - Rside) > 12 else np.ones(int(w))
    rgb = C[..., :3] * (tint * expo)[None, None, :] * gr[None, :, None]
    rgb = np.clip(rgb + np.random.normal(0, grain, rgb.shape), 0, 255).astype('uint8')
    patch = Image.fromarray(rgb).filter(ImageFilter.GaussianBlur(blur))
    # visibility: cutout alpha, minus occluders (non-magenta pixels inside the matte's filled outline)
    fill = ndimage.binary_fill_holes(ndimage.binary_closing(M, iterations=6))
    occ = fill & ~ndimage.binary_dilation(M, iterations=2)
    occ = ndimage.binary_opening(occ, iterations=2)
    a = C[..., 3] / 255.0
    sub = np.zeros_like(a); H, W = M.shape
    yy0, xx0 = max(oy, 0), max(ox, 0); yy1, xx1 = min(oy + int(h), H), min(ox + int(w), W)
    occ_crop = occ[yy0:yy1, xx0:xx1].astype(float)
    occ_soft = np.asarray(Image.fromarray((occ_crop * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))) / 255.0
    a_crop = a[yy0 - oy:yy1 - oy, xx0 - ox:xx1 - ox] * (1 - occ_soft)
    alpha = Image.fromarray((np.clip(a_crop, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.7))
    out_im = sc.copy()
    # kill leftover magenta (matte bigger than the bottle, edge spill): fill from the scene around it
    left = ndimage.binary_dilation(M, iterations=3)
    if left.any():
        blurred = np.asarray(sc.filter(ImageFilter.GaussianBlur(9))).astype(float)
        R = A.copy(); mask3 = left[..., None]
        # replace magenta with nearby non-magenta colour (dilate-erode trick via repeated blur of unmasked pixels)
        valid = (~left).astype(float); num = np.asarray(Image.fromarray(np.uint8(A * valid[..., None])).filter(ImageFilter.GaussianBlur(14))).astype(float)
        den = np.asarray(Image.fromarray(np.uint8(valid * 255)).filter(ImageFilter.GaussianBlur(14))).astype(float)[..., None] / 255.0
        fillc = np.clip(num / np.maximum(den, 1e-3), 0, 255)
        R = np.where(mask3, fillc, A); out_im = Image.fromarray(R.astype('uint8'))
        # restore true occluders (fingers) over the fill
        out_im.paste(sc, (0, 0), Image.fromarray((occ & ~left).astype('uint8') * 255))
    O = np.asarray(out_im).astype(float)
    ry0, ry1 = max(oy - int(h * 0.1), 0), min(oy + int(h * 1.7), H); rx0, rx1 = max(ox - int(w * 0.5), 0), min(ox + int(w * 1.5), W)
    R = O[ry0:ry1, rx0:rx1]; r, g, b = R[..., 0], R[..., 1], R[..., 2]
    pink = (r - g > 6) & (b - g > 3) & (np.abs(r - b) < 70)
    pink = ndimage.binary_dilation(ndimage.binary_opening(pink, iterations=1), iterations=2)
    v = R.mean(2, keepdims=True); neutral = np.clip(v * tint[None, None, :], 0, 255)
    soft = np.asarray(Image.fromarray((pink * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(2))).astype(float)[..., None] / 255
    O[ry0:ry1, rx0:rx1] = R * (1 - soft) + neutral * soft
    out_im = Image.fromarray(O.astype('uint8'))
    out_im.paste(patch.crop((xx0 - ox, yy0 - oy, xx1 - ox, yy1 - oy)), (xx0, yy0), alpha)
    out_im.save(out)
    return dict(matte=(int(x0), int(y0), int(x1), int(y1)), bottle=(ox, oy, ox + int(w), oy + int(h)), tint=np.round(tint, 3).tolist(), expo=round(float(expo), 3))

if __name__ == '__main__':
    kw = dict(a.split('=', 1) for a in sys.argv[3:])
    print(key(sys.argv[1], sys.argv[2], **kw))
