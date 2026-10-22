"""Product page gallery slide 1: the studio render of the bottle, centered on a light studio sweep with grounded
shadows (contact, ambient occlusion, a soft cast shadow toward the back right), and the badges of the current
slide (Korean flag, "1m+ Sold") composited back unchanged.

usage: python3 -I packshot_slide.py <render.png> <current_slide.jpg> <out.jpg> [<variants_dir>]
- render.png: brand/adaptive-peptide-foundation/01-front.png (bottle on a grey studio gradient)
- current_slide.jpg: the slide being replaced, 1080 x 1080 on a flat #f5f5f5 backdrop (badges in its top right)
- variants_dir: also rewrite every size variant of the slide found there (same names and pixel sizes), e.g. the
  persona images folder apply_persona.py reads (NEXT's CDN caches by file name: apply_persona renames them)
"""
import os, re, sys
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi

RENDER, CURRENT, OUT = sys.argv[1:4]
VARIANTS = sys.argv[4] if len(sys.argv) > 4 else None
SIZE = 1080


def matte(img):
    """Soft alpha of the dark bottle on its smooth grey backdrop, and the foreground with the backdrop unmixed."""
    lum = img.mean(2)
    core = lum < 95
    lab, n = ndi.label(core)
    core = lab == (1 + int(np.argmax(ndi.sum(core, lab, range(1, n + 1)))))
    core = ndi.binary_fill_holes(ndi.binary_closing(core, iterations=3))
    core = ndi.binary_erosion(core, iterations=2)
    band = ndi.binary_dilation(core, iterations=6) & ~core
    # backdrop behind the edge: normalized blur of the pixels outside the bottle
    outside = (~ndi.binary_dilation(core, iterations=6)).astype(np.float32)
    k = (0, 0)
    bg = cv2.GaussianBlur(img * outside[..., None], k, 18) / np.maximum(cv2.GaussianBlur(outside, k, 18), 1e-3)[..., None]
    fg_edge = 22.0
    a = core.astype(np.float32)
    bl = bg.mean(2)
    a[band] = np.clip((bl[band] - lum[band]) / np.maximum(bl[band] - fg_edge, 1), 0, 1)
    a = np.maximum(a, core)
    fg = np.where(a[..., None] > 0.03, (img - (1 - a[..., None]) * bg) / np.maximum(a[..., None], 0.03), 0)
    return np.clip(fg, 0, 255), a


def sweep():
    """Light warm-grey studio sweep: a wall that turns into the floor, the floor brightening toward the camera."""
    gy = np.linspace(0, 1, SIZE)[:, None]
    gx = np.linspace(-1, 1, SIZE)[None, :]
    horizon = 0.70
    wall = 243 - 7 * gy / horizon
    floor = 236 + 10 * np.clip((gy - horizon) / (1 - horizon), 0, 1)
    t = np.clip((gy - (horizon - 0.08)) / 0.16, 0, 1)
    t = t * t * (3 - 2 * t)
    base = (wall * (1 - t) + floor * t) * (1 - 0.035 * gx ** 2 - 0.02 * ((gy - 0.5) * 2) ** 2)
    return np.stack([base + 1.5, base + 0.5, base - 0.8], -1)


def compose(render, current):
    fg, a = matte(render)
    ys, xs = np.where(a > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    fg, a = fg[y0:y1 + 1, x0:x1 + 1], a[y0:y1 + 1, x0:x1 + 1]
    target_h = 640                                    # the bottle at ~59% of the frame, like the other slides
    s = target_h / a.shape[0]
    nh, nw = target_h, int(round(a.shape[1] * s))
    fg = cv2.resize(fg, (nw, nh), interpolation=cv2.INTER_AREA)
    a = np.clip(cv2.resize(a, (nw, nh), interpolation=cv2.INTER_AREA), 0, 1)
    canvas = sweep()
    bx, base_y = (SIZE - nw) // 2, 905
    by = base_y - nh
    yy = np.mgrid[0:SIZE, 0:SIZE][0]

    def darken(layer, k):
        nonlocal canvas
        canvas = canvas * (1 - k * layer[..., None])

    ao = np.zeros((SIZE, SIZE), np.float32)            # ambient occlusion pool
    cv2.ellipse(ao, (SIZE // 2 + 10, base_y + 2), (int(nw * 0.85), 30), 0, 0, 360, 1, -1)
    darken(cv2.GaussianBlur(ao, (0, 0), 22), 0.34)
    sil = np.zeros((SIZE, SIZE), np.float32)           # cast shadow on the floor, back right, fading with distance
    sil[by:base_y, bx:bx + nw] = a
    M = cv2.getAffineTransform(np.float32([[bx, by], [bx + nw, by], [bx, base_y]]),
                               np.float32([[bx + nw * 0.95, base_y - nh * 0.22], [bx + nw * 1.95, base_y - nh * 0.22], [bx, base_y]]))
    cast = cv2.warpAffine(sil, M, (SIZE, SIZE)) * np.clip(1 - (base_y - yy) / (nh * 0.24), 0, 1) ** 1.4
    darken(cv2.GaussianBlur(cast, (0, 0), 9) * 0.6 + cv2.GaussianBlur(cast, (0, 0), 28) * 0.4, 0.30)
    cs = np.zeros((SIZE, SIZE), np.float32)            # contact shadow along the curved base
    cv2.ellipse(cs, (SIZE // 2 + 1, base_y - 9), (int(nw * 0.47), 11), 0, 0, 360, 1, -1)
    darken(cv2.GaussianBlur(cs, (0, 0), 3.2), 0.58)
    region = canvas[by:base_y, bx:bx + nw]
    canvas[by:base_y, bx:bx + nw] = region * (1 - a[..., None]) + fg * a[..., None]
    rh = int(nh * 0.08)                                # soft floor sheen under the base
    refl = cv2.GaussianBlur(fg[nh - rh:][::-1], (0, 0), 6)
    ra = (np.linspace(0.12, 0, rh)[:, None] * cv2.GaussianBlur(a[nh - rh:][::-1], (0, 0), 3))[..., None]
    canvas[base_y:base_y + rh, bx:bx + nw] = canvas[base_y:base_y + rh, bx:bx + nw] * (1 - ra) + refl * ra
    bdg = current[60:460, 850:1060]                    # the current slide's badges, unchanged
    ba = cv2.GaussianBlur(np.clip((np.abs(bdg - 245.0).max(2) - 3) / 10, 0, 1), (0, 0), 0.6)[..., None]
    canvas[60:460, 850:1060] = canvas[60:460, 850:1060] * (1 - ba) + bdg * ba
    canvas += np.random.default_rng(7).normal(0, 1.1, canvas.shape)   # fine grain, as in a photograph
    return Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))


render = np.asarray(Image.open(RENDER).convert('RGB')).astype(np.float32)
current = np.asarray(Image.open(CURRENT).convert('RGB').resize((SIZE, SIZE))).astype(np.float32)
slide = compose(render, current)
slide.save(OUT, quality=94)
print('slide ->', OUT)
if VARIANTS:
    stem = re.sub(r'(-\d+w)?-[0-9a-f]{6}\.jpg$', '', os.path.basename(CURRENT))
    for name in sorted(os.listdir(VARIANTS)):
        if not name.startswith(stem): continue
        path = os.path.join(VARIANTS, name)
        size = Image.open(path).size
        (slide if size == slide.size else slide.resize(size, Image.LANCZOS)).save(path, quality=90, optimize=True, progressive=True)
        print('  ', name, size)
