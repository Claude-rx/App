"""The homepage's photos for its original design, with the store's real products: built from brand/home/source/ (and
the product folders) into brand/home/, which apply_persona.home_original puts on the page. (The banner is the persona
photo of the build's image set, a woman of about 55 holding the real bottle: apply_persona.faster_home.)

usage: python3 -I tools/persona/home_images.py

- oneshade-mobile.webp, oneshade-desktop.jpg, oneshade-narrow.jpg: the "One shade" model (source/oneshade-ai.jpg: the original photo, its
  model made a woman of about 57 by gpt-image-2, her bottle's small print garbled), the real bottle laid on it. The
  phone file is its backdrop keyed out (the card's grey gradient behind her, as behind the original cut-out); the
  desktop files are a landscape and a squarer crop of it
- formulas.jpg: the "Korean formulas" photo (source/formulas-ai-2x.jpg: the original model with her neck and shoulder
  completed, so no cut edge shows at any width; Real-ESRGAN 2x), the real bottle laid on it, a little wider than the
  image model's bottle so it covers it whole
- celebration.jpg: "Beauty is a celebration", the export's two models as women in their fifties (gpt-image-2)
- tile-*.jpg (4:5): Shop by category, a woman over 45 holding each product
- bundle-*.jpg (1:1): Bundle & Save, each bundle's units on white with soft contact shadows (the foundation from
  its front render, the brush with its case)
"""
import subprocess, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
SRC, OUT, BRAND = ROOT / 'brand' / 'home' / 'source', ROOT / 'brand' / 'home', ROOT / 'brand'
HELD = Path(__file__).resolve().parent / 'held_bottle.py'
sys.path.insert(0, str(HELD.parent))
from label_fix import legible_pdrn
TMP = OUT / '.work'


def held(src, out, *geometry):
    subprocess.run([sys.executable, '-I', str(HELD), str(src), str(out), *geometry], check=True)


def save(im, name, **kw):
    path = OUT / name
    im.save(path, **({'quality': 90, 'optimize': True, 'progressive': True} if name.endswith('.jpg') else {}), **kw)
    print(f'{path.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}  {path.stat().st_size // 1024} KB')


def cutout(path, keep='largest'):
    """A product photographed on white, as RGBA: alpha from how far each pixel is from white, its printed white
    letters kept inside it (holes filled); keep='tallest' drops a second object beside it (a cap lying there),
    keep='all' keeps every sizeable part (a brush above its case)."""
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(2)
    soft = np.clip((247 - lum) / 22, 0, 1)
    solid = ndimage.binary_fill_holes(ndimage.binary_closing(soft > 0.5, iterations=2))
    lab, n = ndimage.label(solid)
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    if keep == 'tallest':
        spans = [np.ptp(np.nonzero(lab == i)[0]) for i in range(1, n + 1)]
        obj = lab == int(np.argmax(spans)) + 1
    elif keep == 'all':                                                    # every part of it (a brush and its case)
        obj = np.isin(lab, np.nonzero(sizes >= 0.05 * sizes.max())[0] + 1)
    else:
        obj = lab == int(np.argmax(sizes)) + 1
    alpha = np.where(obj, np.maximum(soft, ndimage.binary_erosion(obj, iterations=2)), 0)
    alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    ys, xs = np.nonzero(obj)
    rgba = np.dstack([a.astype(np.uint8), alpha])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(rgba, 'RGBA')


def foundation_unit():
    """The Adaptive Peptide Foundation bottle cut out of its front render (its grey sweep dropped), PDRN legible."""
    r = legible_pdrn(np.asarray(Image.open(BRAND / 'adaptive-peptide-foundation' / '01-front.png').convert('RGB')).astype(np.float32))
    l = r.mean(2)
    bg = np.median(np.concatenate([l[:20].ravel(), l[:, :20].ravel(), l[:, -20:].ravel()]))
    lab, n = ndimage.label(l < bg * 0.62)
    body = lab == (np.argmax(ndimage.sum(l < bg * 0.62, lab, range(1, n + 1))) + 1)
    body = ndimage.binary_fill_holes(ndimage.binary_closing(body, iterations=3))
    alpha = np.asarray(Image.fromarray((body * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    ys, xs = np.nonzero(body)
    rgba = np.dstack([np.clip(r, 0, 255).astype(np.uint8), alpha])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(rgba, 'RGBA')


def trio(unit, height=0.66, size=1000, spread=0.27, side=0.9, count=3):
    """Three (or two) of a product on white, side by side on one floor line, the middle one in front, soft contact
    shadows."""
    canvas = Image.new('RGB', (size, size), (255, 255, 255))
    floor = int(size * 0.84)
    shadow = Image.new('L', (size, size), 0)
    placed = []
    spots = ((-spread, side), (spread, side), (0.0, 1.0)) if count == 3 else ((-spread, 1.0), (spread, 1.0))
    for dx, k in spots:                                                   # the middle one drawn last, in front
        h = int(size * height * k); w = int(unit.width * h / unit.height)
        u = unit.resize((w, h), Image.LANCZOS)
        x = int(size / 2 + dx * size - w / 2)
        placed.append((u, x, floor - h))
        sw, sh = int(w * 1.05), max(6, int(w * 0.16))
        e = Image.new('L', (sw, sh), 0)
        ImageDraw.Draw(e).ellipse((0, 0, sw - 1, sh - 1), fill=150)
        shadow.paste(e, (x + (w - sw) // 2, floor - sh // 2), e)
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.012))
    canvas = Image.composite(Image.new('RGB', canvas.size, (175, 172, 170)), canvas, shadow.point(lambda v: v * 0.55))
    for u, x, y in placed:
        canvas.paste(u, (x, y), u)
    return canvas


def crop45(path, box):
    im = Image.open(path).convert('RGB').crop(box)
    return im.resize((800, 1000), Image.LANCZOS)


def main():
    OUT.mkdir(exist_ok=True); TMP.mkdir(exist_ok=True)
    # ---- One shade: the bottle at her temple, measured by hand (its base, its pump end, its width); ours is a little
    # wider than the image model's, so it covers it whole
    held(SRC / 'oneshade-ai.jpg', TMP / 'oneshade.jpg', '--line', '183,937,251,412', '--w', '152', '--width', '1.11', '--anchor', 'centre')
    one = Image.open(TMP / 'oneshade.jpg').convert('RGB')                               # 1024 x 1536
    a = np.asarray(one).astype(np.float32)
    white = (a.min(2) > 238) & (a.max(2) - a.min(2) < 10)
    lab, n = ndimage.label(white)
    edge = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    bg = np.isin(lab, [i for i in edge if i])                                            # the backdrop: white, touching the edges
    alpha = 1 - ndimage.gaussian_filter(bg.astype(np.float32), 1.2)
    rgba = Image.fromarray(np.dstack([a.astype(np.uint8), (np.clip(alpha, 0, 1) * 255).astype(np.uint8)]), 'RGBA')
    # phones: her head and shoulders from the hair down, keyed (the card's grey gradient shows behind her)
    save(rgba.crop((0, 190, 1024, 1536)).resize((860, 1130), Image.LANCZOS), 'oneshade-mobile.webp', quality=86, method=6)
    # wide screens and tablets: bottle and face, chin included (1.31:1); 1024-1199 px, where the card leaves the
    # photo a near-square box: a squarer crop of the same (1.1:1)
    save(one.crop((0, 360, 1024, 1140)), 'oneshade-desktop.jpg')
    save(one.crop((40, 330, 940, 1150)), 'oneshade-narrow.jpg')
    # ---- Korean formulas: the bottle at her forehead, measured by hand at 2x
    # (its old bottle is slimmer than ours, 178 px to our 226 at the same length: ours covers it whole, the fingers that
    # crossed the old one stay in front); first a white wedge the image model left on her nose is filled from the skin
    src = np.asarray(Image.open(SRC / 'formulas-ai-2x.jpg').convert('RGB'))
    box = np.zeros(src.shape[:2], np.uint8)
    box[700:760, 1138:1186] = src[700:760, 1138:1186].mean(2) > 225
    box = cv2.dilate(box, np.ones((5, 5), np.uint8))
    Image.fromarray(cv2.inpaint(src, box * 255, 5, cv2.INPAINT_TELEA)).save(TMP / 'formulas-src.jpg', quality=95)
    held(TMP / 'formulas-src.jpg', OUT / 'formulas.jpg', '--line', '1607,1105,1235,475', '--w', '178', '--width', '1.27', '--anchor', 'centre')
    # ---- Beauty is a celebration: the export's two models as women in their fifties (gpt-image-2, source/celebration-ai.jpg)
    save(Image.open(SRC / 'celebration-ai.jpg').convert('RGB'), 'celebration.jpg')
    # ---- Shop by category: 4:5 crops, face and product in the upper two thirds (the name and button sit low left)
    save(crop45(SRC / 'tile-foundation.jpg', (0, 0, 1397, 1747)), 'tile-foundation.jpg')
    save(crop45(BRAND / 'egf-nad-serum' / 'hold-cheek.jpg', (108, 0, 972, 1080)), 'tile-serum.jpg')
    save(crop45(BRAND / 'pdrn-balm' / 'hold-cheek.jpg', (150, 0, 1014, 1080)), 'tile-balm.jpg')
    save(crop45(SRC / 'brush-ai.jpg', (102, 0, 921, 1024)), 'tile-brush.jpg')
    # ---- Bundle & Save
    save(trio(foundation_unit(), height=0.7, spread=0.2, count=2), 'bundle-foundation.jpg')
    save(Image.open(BRAND / 'egf-nad-serum' / 'trio.jpg').convert('RGB').resize((1000, 1000), Image.LANCZOS), 'bundle-serum.jpg')
    save(trio(cutout(BRAND / 'pdrn-balm' / 'card.jpg', keep='tallest'), height=0.62), 'bundle-balm.jpg')
    save(trio(cutout(BRAND / 'lymphatic-brush' / 'card.jpg', keep='all'), height=0.5, spread=0.3, side=0.9), 'bundle-brush.jpg')
    for f in TMP.iterdir(): f.unlink()
    TMP.rmdir()


if __name__ == '__main__':
    main()
