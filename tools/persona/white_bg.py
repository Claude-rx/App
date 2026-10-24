"""Clean white backgrounds for every product's photos, so all the product pages share one look (pure white, as the
page itself).

usage: python3 -I white_bg.py <in> <out> [light|flood|matte] [--debug <dir>]

light  for photos already shot on white or a pale backdrop (the generated photos, the brush's cream cards): the
       backdrop's level is read from the image border (its near-neutral pixels); every near-neutral pixel from just
       under that level up is pushed to pure white along a smooth ramp, so a 245 cream becomes 255 while the product,
       skin (warmer) and silver hair or a white top (darker than the backdrop) keep their shading. A photo whose
       border shows no pale backdrop (a close-up, a bathroom scene) is left as it is. Nothing is segmented: no
       cut-out edges.
flood  for studio photos on a grey backdrop (the foundation's renders and gallery): the backdrop is the smooth,
       low-saturation area connected to the image border; it is lifted to white with a feathered edge, and its soft
       floor shadow is kept, lighter, under the product.
matte  for photos whose backdrop a colour rule can't tell from the subject (silver hair on a grey wall, a render on
       a grey gradient): a segmentation model (ISNet, through rembg; the model file is downloaded once into
       ~/.u2net) gives the subject's alpha, hair strands soft; each near-neutral pixel is lifted by (1 - alpha) x
       (255 - the local backdrop), so the backdrop becomes pure white and a strand of hair only as much as it is
       see-through, with no grey fringe. Warm pixels (skin) are never lifted, even where the model misses them.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

NEUTRAL = 16      # max - min channel spread that still counts as backdrop (the brush's cream is about 9)
RAMP = 18         # light: the ramp to white starts this far under the backdrop's level (darkest channel)
PALE = 232        # light: a border level under this is a scene, not a backdrop: the photo is left as it is


def backdrop_level(a, neutral=NEUTRAL):
    """The backdrop's level (darkest channel) from the image border, or None when the border is not mostly a pale,
    near-neutral backdrop."""
    b = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    mn = b.min(1); flat = (b.max(1) - mn) < neutral
    if flat.mean() < 0.35: return None
    level = float(np.median(mn[flat]))
    return level if level >= PALE else None


def light(im, lo=None, hi=None, neutral=NEUTRAL):
    """Pale near-neutral pixels to pure white; lo and hi (the ramp, darkest channel) default to the backdrop's."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    if hi is None:
        level = backdrop_level(a, neutral)
        if level is None: return im.convert('RGB')
        hi = min(level - 1, 250)
    lo = hi - RAMP if lo is None else lo
    mn, mx = a.min(2), a.max(2)
    t = np.clip((mn - lo) / (hi - lo), 0, 1)
    t = t * t * (3 - 2 * t)                                     # smoothstep: no band where the ramp starts
    t *= np.clip((neutral + 6 - (mx - mn)) / 6, 0, 1)           # warm or coloured pixels (skin, the balm) keep theirs
    out = a + (255 - a) * t[..., None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


def flood(im, tol=14, feather=2.2, shadow=0.45, debug=None):
    """The backdrop (border-connected, smooth, near the border's colour, low saturation) lifted to white."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    h, w = a.shape[:2]
    lum = a @ np.array([.299, .587, .114], np.float32)
    sat = a.max(2) - a.min(2)
    border = np.concatenate([lum[:4].ravel(), lum[-4:].ravel(), lum[:, :4].ravel(), lum[:, -4:].ravel()])
    bg_l = np.median(border)
    # the backdrop's local level (a smooth gradient on studio sweeps): a heavy blur of the image
    smooth = ndimage.gaussian_filter(lum, 3)
    grad = np.hypot(ndimage.sobel(smooth, 0), ndimage.sobel(smooth, 1))
    cand = (sat < 18) & (grad < 18) & (np.abs(lum - bg_l) < 60) & (lum > bg_l - 60)
    lab, n = ndimage.label(cand)
    edge_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge_labels))
    bg = ndimage.binary_opening(bg, iterations=2)
    soft = ndimage.gaussian_filter(bg.astype(np.float32), feather)
    # inside the backdrop: how much darker than the plain backdrop (the floor shadow) -> kept, lighter
    ref = np.percentile(lum[bg], 90) if bg.any() else bg_l
    dark = np.clip((ref - lum - 8) / max(ref, 1), 0, 1) * shadow     # the backdrop's own grain goes white
    white = 255 * (1 - dark)[..., None]
    out = a * (1 - soft[..., None]) + white * soft[..., None]
    if debug:
        Path(debug).mkdir(parents=True, exist_ok=True)
        Image.fromarray((bg * 255).astype(np.uint8)).save(Path(debug) / 'bg.png')
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


_SESSION = {}


def alpha_of(im, model='isnet-general-use'):
    """The subject's alpha (0..1) from the segmentation model."""
    from rembg import new_session, remove
    if model not in _SESSION: _SESSION[model] = new_session(model)
    m = remove(im.convert('RGB'), session=_SESSION[model], only_mask=True)
    a = np.asarray(m.convert('L').resize(im.size, Image.LANCZOS)).astype(np.float32) / 255
    return np.clip((a - 0.03) / 0.94, 0, 1)                         # the model's faint haze over the backdrop goes


def matte(im, debug=None, model='isnet-general-use', shadow=False):
    """shadow: a soft contact shadow under a product that stands on a floor (a render's own floor shadow is part of
    the grey floor, so it goes with it)."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    alpha = alpha_of(im, model)
    # the backdrop's local colour, from the confident backdrop pixels only (normalised convolution); where the subject
    # covers it, the backdrop's median
    w = (1 - alpha) ** 4
    num = np.stack([ndimage.gaussian_filter(a[..., c] * w, 24) for c in range(3)], -1)
    den = ndimage.gaussian_filter(w, 24)[..., None]
    med = np.median(a[w > 0.9], axis=0) if (w > 0.9).any() else np.full(3, 255, np.float32)
    B = np.where(den > 1e-3, num / np.maximum(den, 1e-3), med)
    # only near-neutral pixels are lifted: where the model takes skin for backdrop (a pale neck against a pale wall),
    # the skin's warmth keeps it as it is
    spread = a.max(2) - a.min(2)
    n = np.clip((30 - spread) / 8, 0, 1)
    out = a + ((1 - alpha) * n)[..., None] * (255 - B)
    # what is left of the backdrop's grain (a floor's mottling) goes white too, only where the subject is see-through
    mn = out.min(2)
    t = np.clip((mn - 228) / 22, 0, 1); t = t * t * (3 - 2 * t)
    out += (255 - out) * (t * (1 - alpha) * n)[..., None]
    if shadow:                                                   # one per product standing in the photo
        lab, n = ndimage.label(alpha > 0.5)
        h, wd = alpha.shape
        yy, xx = np.mgrid[0:h, 0:wd]
        sh = np.zeros_like(alpha)
        for k in range(1, n + 1):
            ys, xs = np.nonzero(lab == k)
            if len(ys) < alpha.size * 0.01 or ys.max() >= h - 2: continue   # specks; a product cut by the frame
            bottom = ys.max(); foot = xs[ys > bottom - max(4, (bottom - ys.min()) * 0.03)]
            cx, half = (foot.min() + foot.max()) / 2, max(4, (foot.max() - foot.min()) / 2)
            e = ((xx - cx) / (half * 1.08)) ** 2 + ((yy - bottom + half * 0.02) / (half * 0.09)) ** 2
            sh = np.maximum(sh, ndimage.gaussian_filter((e <= 1).astype(np.float32), half * 0.07) * 0.32)
        out *= (1 - sh * (1 - alpha))[..., None]
    if debug:
        Path(debug).mkdir(parents=True, exist_ok=True)
        Image.fromarray((alpha * 255).astype(np.uint8)).save(Path(debug) / 'alpha.png')
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


if __name__ == '__main__':
    args = sys.argv[1:]
    mode = args[2] if len(args) > 2 and not args[2].startswith('--') else 'light'
    dbg = args[args.index('--debug') + 1] if '--debug' in args else None
    im = Image.open(args[0])
    out = {'light': lambda: light(im), 'flood': lambda: flood(im, debug=dbg), 'matte': lambda: matte(im, dbg)}[mode]()
    out.save(args[1], quality=92)
    print(args[1], mode)
