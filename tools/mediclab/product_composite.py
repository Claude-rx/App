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
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

D = __file__.rsplit('/', 1)[0]
CUT = Image.open(str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'docs' / 'mediclab' / 'product' / 'berberine-front-cutout.png')).convert('RGBA')
CREAM_REF = np.array([238., 232., 220.])     # the label paper of the product photo (studio light)

def magenta(A, tol=70):
    r, g, b = A[..., 0], A[..., 1], A[..., 2]
    return (r > 150) & (b > 120) & (g < 120) & (r - g > tol) & (b - g > tol - 20)

def key(scene, out, light=None, scale_adj=1.0, dy=0, grain=1.8, blur=0.5, blob='largest', source=None, anchor='bottom'):
    scale_adj = float(scale_adj); dy = int(dy)
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
    cut = CUT.resize((int(w), int(h)), Image.LANCZOS)
    if anchor == 'center':      # hand-held: keep the bottle centred in the grip
        oy = int((y0 + y1) / 2 - h / 2) + dy
    else:                       # standing: the base stays where it touches the surface
        oy = int(y1 - h) + dy
    ox = int(cx - w / 2)
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
    # leftover matte (larger than the real bottle) and its edge spill: harmonic fill (smooth, no streaks) from the
    # photo around it, then grain; the real bottle covers most of it
    left = ndimage.binary_dilation(M, iterations=4) & ~occ
    out_im = sc.copy()
    if left.any():
        from scipy.sparse import lil_matrix
        from scipy.sparse.linalg import spsolve
        ys_, xs_ = np.nonzero(left); idx = -np.ones(left.shape, int); idx[ys_, xs_] = np.arange(len(ys_))
        n = len(ys_); Lm = lil_matrix((n, n)); bvec = np.zeros((n, 3))
        for k, (y, x) in enumerate(zip(ys_, xs_)):
            Lm[k, k] = 4
            for yy, xx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                yy = min(max(yy, 0), left.shape[0]-1); xx = min(max(xx, 0), left.shape[1]-1)
                if left[yy, xx]: Lm[k, idx[yy, xx]] -= 1
                else: bvec[k] += A[yy, xx]
        Lc = Lm.tocsc(); F = A.copy()
        for ch in range(3): F[ys_, xs_, ch] = spsolve(Lc, bvec[:, ch])
        F[ys_, xs_] += np.random.normal(0, grain * 1.5, (n, 3))
        out_im = Image.fromarray(np.clip(F, 0, 255).astype('uint8'))
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


def place(plate, out, base_cx, base_y, height, grain=1.8, blur=0.5, shadow=0.38):
    """Standing bottle on a clean plate (scene with the bottle removed): the real cutout at an exact pixel height,
    base centred at (base_cx, base_y), light matched to the surroundings, soft contact shadow drawn underneath."""
    sc = Image.open(plate).convert('RGB'); A = np.asarray(sc).astype(float)
    h = int(height); w = int(h * CUT.width / CUT.height); ox, oy = int(base_cx - w / 2), int(base_y - h)
    cut = CUT.resize((w, h), Image.LANCZOS); C = np.asarray(cut).astype(float)
    pad = int(w * 0.8)
    ring = A[max(oy - pad // 2, 0):min(base_y, A.shape[0]), max(ox - pad, 0):min(ox + w + pad, A.shape[1])].reshape(-1, 3)
    sat = ring.max(1) - ring.min(1); neutral = ring[sat < np.percentile(sat, 35)]
    nb = neutral[neutral.mean(1) > np.percentile(neutral.mean(1), 50)].mean(0)
    k = float(np.clip((nb[0] - nb[2]) / nb.mean() / 2, -0.03, 0.05)); tint = np.array([1 + k, 1.0, 1 - k])
    bright = ring[ring.mean(1) > np.percentile(ring.mean(1), 70)].mean()
    expo = float(np.clip(bright / 205.0, 0.8, 1.08))
    Ls = A[oy:base_y, max(ox - pad, 0):ox].mean(); Rs = A[oy:base_y, ox + w:ox + w + pad].mean()
    gr = np.linspace(1 + 0.07 * np.sign(Ls - Rs), 1 - 0.07 * np.sign(Ls - Rs), w) if abs(Ls - Rs) > 12 else np.ones(w)
    rgb = np.clip(C[..., :3] * (tint * expo)[None, None, :] * gr[None, :, None] + np.random.normal(0, grain, (h, w, 3)), 0, 255)
    patch = Image.fromarray(rgb.astype('uint8')).filter(ImageFilter.GaussianBlur(blur))
    alpha = Image.fromarray(C[..., 3].astype('uint8')).filter(ImageFilter.GaussianBlur(0.7))
    # contact shadow: a tight dark core at the base plus a soft wider falloff, offset away from the light
    sh = Image.new('L', sc.size, 0); d = ImageDraw.Draw(sh)
    off = int(0.06 * w * np.sign(Ls - Rs)) if abs(Ls - Rs) > 12 else 0
    d.ellipse((ox - int(0.06 * w) + off, base_y - int(0.05 * w), ox + w + int(0.06 * w) + off, base_y + int(0.07 * w)), fill=int(255 * shadow))
    d.ellipse((ox + int(0.04 * w), base_y - int(0.025 * w), ox + w - int(0.04 * w), base_y + int(0.025 * w)), fill=int(255 * min(shadow * 1.6, 0.75)))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, w * 0.05)))
    S = np.asarray(sh).astype(float)[..., None] / 255
    out_im = Image.fromarray((A * (1 - S)).astype('uint8'))
    out_im.paste(patch, (ox, oy), alpha)
    out_im.save(out)
    return dict(bottle=(ox, oy, ox + w, base_y), tint=tint.round(3).tolist(), expo=round(expo, 3))


def fix_label_text(img, out, geom=None, inset=0.0, hand=False):
    """Replace only the label's text strip (between the heart and the bottom band: "Berberine", "Weight Management*",
    the three pills, "DIETARY SUPPLEMENT · 60 CAPSULES") with the real artwork, mapped by the heart and band of the
    generated bottle and relit with its own shading. Image models garble small print; this keeps it exact."""
    import sys as _s
    _s.path.insert(0, __file__.rsplit('/', 1)[0])
    sc = Image.open(img).convert('RGB'); A = np.asarray(sc).astype(float)
    if geom is None:
        from label_geom import label_geom
        geom = label_geom(sc, 100)
    (hx0, hy0, hx1, hy1), (bx0, by0, bx1, by1) = geom
    H0, B0 = (244, 577, 787, 1127), (4, 1503, 956, 1637)
    src = Image.new('RGB', CUT.size, (255, 255, 255)); src.paste(CUT, mask=CUT.split()[3])
    # source strip (cutout coords) -> target strip (scene coords), x by the band, y from heart bottom to band top
    sx0, sx1 = B0[0] + (B0[2] - B0[0]) * inset, B0[2] - (B0[2] - B0[0]) * inset
    tx0, tx1 = bx0 + (bx1 - bx0) * inset, bx1 - (bx1 - bx0) * inset
    sy0, sy1 = H0[3] + 1, B0[3]; ty0, ty1 = hy1 + 1, by1
    tw, th = int(round(tx1 - tx0)), int(round(ty1 - ty0))
    strip = np.asarray(src.crop((int(sx0), int(sy0), int(sx1), int(sy1))).resize((tw, th), Image.LANCZOS)).astype(float)
    tgt = A[int(round(ty0)):int(round(ty0)) + th, int(round(tx0)):int(round(tx0)) + tw]
    # relight: the generated paper's low-frequency light (shading, warmth) over the artwork's paper
    def lowpass(a, r):
        return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(r))).astype(float)
    r = max(4, th // 3)
    paper_t = lowpass(np.where((tgt.mean(2, keepdims=True) > np.percentile(tgt.mean(2), 40)), tgt, tgt.mean((0, 1))), r)
    paper_s = lowpass(np.where((strip.mean(2, keepdims=True) > np.percentile(strip.mean(2), 40)), strip, strip.mean((0, 1))), r)
    rel = np.clip(strip * paper_t / np.maximum(paper_s, 1), 0, 255)
    rel = np.asarray(Image.fromarray(rel.astype('uint8')).filter(ImageFilter.GaussianBlur(0.4))).astype(float)
    m = np.ones((th, tw)); fy = max(2, th // 25); fx = max(2, tw // 60)
    m[:fy] *= np.linspace(0, 1, fy)[:, None]                       # soft only under the heart; the band edge stays crisp
    m[:, :fx] *= np.linspace(0, 1, fx)[None]; m[:, -fx:] *= np.linspace(1, 0, fx)[None]
    # the strip spans exactly the band's width, i.e. the bottle body; fingers over the label stay in front
    skin = np.zeros((th, tw), bool)
    if hand:   # a finger over the label continues past the bottle's edge; label paper never does
        y, x = int(round(ty0)), int(round(tx0)); px = max(4, tw // 6)
        X0, X1 = max(x - px, 0), min(x + tw + px, A.shape[1]); E = A[y:y + th, X0:X1]
        er, eg, eb = E[..., 0], E[..., 1], E[..., 2]
        sk = (er - eg >= 18) & (er - eb >= 42) & (er > 70) & (E.mean(2) < 205)
        sk = ndimage.binary_opening(sk, iterations=2); lab_, n_ = ndimage.label(sk)
        outer = set(np.unique(lab_[:, :max(2, (x - X0) // 2)])) | set(np.unique(lab_[:, -max(2, (X1 - x - tw) // 2):]))
        sk = ndimage.binary_dilation(np.isin(lab_, [i for i in outer if i]), iterations=2)
        skin = sk[:, x - X0:x - X0 + tw]
    m *= 1 - np.asarray(Image.fromarray((skin * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255
    out_arr = A.copy(); y, x = int(round(ty0)), int(round(tx0))
    out_arr[y:y + th, x:x + tw] = tgt * (1 - m[..., None]) + rel * m[..., None]
    Image.fromarray(out_arr.astype('uint8')).save(out)
    return dict(strip=(x, y, x + tw, y + th))
