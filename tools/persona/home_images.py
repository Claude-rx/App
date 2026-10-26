"""The homepage's photos for its original design, with the store's real products: built from brand/home/source/ (and
the product folders) into brand/home/, which apply_persona.home_original puts on the page. (The banner is the persona
photo of the build's image set, a woman of about 55 holding the real bottle: apply_persona.faster_home.)

usage: python3 -I tools/persona/home_images.py

- oneshade-mobile.webp, oneshade-desktop.webp: the "One shade" model (source/oneshade-ai.jpg: the original photo, its
  model made a woman of about 57 by gpt-image-2, her bottle's small print garbled), the real bottle laid on it. The
  phone file (also tablets and small laptops, under 1200 px) is its backdrop keyed out, the gaps between her fingers
  and between her arm and neck too (the card's grey gradient behind her, as behind the original cut-out); the desktop
  file is the same keyed photo, hair to chest, on a wider transparent canvas (1.31:1), so a computer shows her whole
  head on the card (a landscape crop of the photo cut it); both from source/oneshade-ai-2x.jpg (Real-ESRGAN 2x)
- formulas.jpg: the "Korean formulas" photo (source/formulas-ai-2x.jpg: the original model with her neck and shoulder
  completed, so no cut edge shows at any width; Real-ESRGAN 2x), the real bottle laid on it, a little wider than the
  image model's bottle so it covers it whole
- phenomenon-1.jpg: "The SKINOFAB phenomenon" card 1 at 2x (source/phenomenon-1-sr.jpg); phenomenon-4.jpg,
  phenomenon-7.jpg: two of its cards (source/phenomenon-*-ai.jpg), the real
  bottle laid on them
- balm-wide.jpg: the balm banner's photo from 1200 px (pdrn-balm/source/apply-eye-wide-ai.png)
- celebration.jpg: "Beauty is a celebration", the export's two models as women in their fifties (gpt-image-2)
- tile-*.jpg (4:5): Shop by category, a woman over 45 holding each product
- adaptive-peptide-foundation/doctor.jpg: the foundation page's "Formulated in Korea" photo, a model in a lab coat
  (a portrayal, said so on the page) with the real bottle
- collage-wide.jpg, collage-square.jpg: the listing pages' banners, the four tiles side by side and two by two
- bundle-*.jpg (1:1): Bundle & Save, each bundle's units on white with soft contact shadows (the foundation from
  its front render, the brush with its case); card-foundation.jpg, the shelf's foundation card, one bottle the same way;
  tools/theme-build/static/skinofab-cart-bottle.png, the empty cart drawer's bottle
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
import label_fix
from label_fix import legible_pdrn
import relabel_bottles
TMP = OUT / '.work'


def held(src, out, *geometry):
    """held_bottle.py on a photo; its PDRN line bold (--pdrn bold) unless geometry says otherwise: every one of these
    photos shows the bottle a few hundred px tall at most, where the label's own line reads PORN (review 4)."""
    pdrn = () if '--pdrn' in geometry else ('--pdrn', 'bold')
    subprocess.run([sys.executable, '-I', str(HELD), str(src), str(out), *geometry, *pdrn], check=True)


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
    """The Adaptive Peptide Foundation bottle cut out of its front render (its grey sweep dropped), its PDRN line at
    label_fix.XL: the shelf card and the bundle card show it ~60 px wide on a 1440 px screen."""
    r = legible_pdrn(np.asarray(Image.open(BRAND / 'adaptive-peptide-foundation' / '01-front.png').convert('RGB')).astype(np.float32),
                     **label_fix.XL)
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
    """Three (or two, or one) of a product on white, side by side on one floor line, the middle one in front, soft
    contact shadows."""
    canvas = Image.new('RGB', (size, size), (255, 255, 255))
    floor = int(size * 0.84)
    shadow = Image.new('L', (size, size), 0)
    placed = []
    spots = {3: ((-spread, side), (spread, side), (0.0, 1.0)), 2: ((-spread, 1.0), (spread, 1.0)), 1: ((0.0, 1.0),)}[count]
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
    # ---- One shade: the bottle at her temple, measured by hand (its base, its pump end, its width; at 2x: the photo is
    # source/oneshade-ai-2x.jpg, Real-ESRGAN 2x of oneshade-ai.jpg, so a 2x screen's 880 px box gets real detail); ours is
    # a little wider than the image model's, so it covers it whole
    held(SRC / 'oneshade-ai-2x.jpg', TMP / 'oneshade.jpg', '--line', '366,1874,502,824', '--w', '304', '--width', '1.11', '--anchor', 'centre',
         '--fingers', 'left', '--pdrn', 'xl')                       # her fingertip at its edge stays in front; the PDRN
                                                                    # line bold read PORN at 1024 (review 5): extra large
    one = Image.open(TMP / 'oneshade.jpg').convert('RGB')                               # 2048 x 3072
    a = np.asarray(one).astype(np.float32)
    white = (a.min(2) > 238) & (a.max(2) - a.min(2) < 10)
    lab, n = ndimage.label(white)
    edge = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    # the backdrop: white, touching the edges, and the white it shows through the gaps (between her fingers under the
    # bottle, between her arm and her neck: 11,000-13,000 px each), which showed as a white box on the card's grey
    # (review 3); the bottle's printed letters are far smaller
    size = ndimage.sum(white, lab, range(n + 1))
    bg = np.isin(lab, [i for i in range(1, n + 1) if i in edge or size[i] > 16000])     # 4,000 px at 1x
    alpha = 1 - ndimage.gaussian_filter(bg.astype(np.float32), 2.4)
    rgba = Image.fromarray(np.dstack([a.astype(np.uint8), (np.clip(alpha, 0, 1) * 255).astype(np.uint8)]), 'RGBA')
    # phones: her head and shoulders from the hair down, keyed (the card's grey gradient shows behind her)
    # (1290 px wide: a tablet shows it across the card, ~700 px, at 2x)
    save(rgba.crop((0, 380, 2048, 3072)).resize((1290, 1695), Image.LANCZOS), 'oneshade-mobile.webp', quality=84, method=6)
    # wide screens: the keyed photo from above her hair to her chest, on a transparent canvas 1.31 times as wide as it
    # is tall (her at its left, the card's grey to her right), 2048 px wide for the 880 px box at 2x: a landscape crop
    # of the photo cut the top of her head (review 5)
    body = rgba.crop((0, 90, 2048, 2290))
    wide = Image.new('RGBA', (round(body.height * 1.31), body.height), (0, 0, 0, 0)); wide.paste(body, (0, 0))
    save(wide.resize((2048, round(2048 / 1.31)), Image.LANCZOS), 'oneshade-desktop.webp', quality=84, method=6)
    # ---- Korean formulas: the bottle at her forehead, measured by hand at 2x
    # (its old bottle is slimmer than ours, 178 px to our 226 at the same length: ours covers it whole, the fingers that
    # crossed the old one stay in front); first a white wedge the image model left on her nose is filled from the skin
    src = np.asarray(Image.open(SRC / 'formulas-ai-2x.jpg').convert('RGB'))
    box = np.zeros(src.shape[:2], np.uint8)
    box[700:760, 1138:1186] = src[700:760, 1138:1186].mean(2) > 225
    box = cv2.dilate(box, np.ones((5, 5), np.uint8))
    Image.fromarray(cv2.inpaint(src, box * 255, 5, cv2.INPAINT_TELEA)).save(TMP / 'formulas-src.jpg', quality=95)
    held(TMP / 'formulas-src.jpg', OUT / 'formulas.jpg', '--line', '1607,1105,1235,475', '--w', '178', '--width', '1.27', '--anchor', 'centre',
         '--pdrn', 'xl')                                     # a laptop shows the bottle ~80 px wide (review 5)
    # ---- the foundation page's "Formulated in Korea": a model in a lab coat (gpt-image-2, source/doctor-ai.png), the
    # real bottle laid in her hand, its own tones kept (the image model's bottle was lit flatter)
    held(BRAND / 'adaptive-peptide-foundation' / 'source' / 'doctor-ai.png', BRAND / 'adaptive-peptide-foundation' / 'doctor.jpg',
         '--line', '269,925,269,566', '--w', '97', '--width', '1.15', '--anchor', 'centre', '--fingers', 'left', '--tone', 'render')
    # ---- "The SKINOFAB phenomenon" card 1: the persona selfie's card crop was 442 x 680 px for a 260 x 400 card (a 3x
    # phone stretched it 1.76x, review 5). source/phenomenon-1-sr.jpg is it at 2x: Real-ESRGAN x4 (tools/persona/
    # upscale.py, RealESRGAN_x4plus) resized to 2x and blended 60/40 with a plain resize, so the skin keeps its
    # texture, and the bottle (the left column) the plain resize alone (the upscaler garbled its small print); its
    # PDRN line set again bold, as on the other cards
    r = np.asarray(Image.open(SRC / 'phenomenon-1-sr.jpg').convert('RGB')).astype(np.float32)
    label_fix.bold_line_rot(r, (86, 931), 0, (44, 16), 'PDRN', 11, weight=760, track=0.2)
    save(Image.fromarray(np.clip(r + 0.5, 0, 255).astype(np.uint8)), 'phenomenon-1.jpg')
    # ---- "The SKINOFAB phenomenon" cards 4 and 7: persona photos whose bottles printed the old "COLOR CHANGING
    # FOUNDATION / 15 SPF" (4) or a PDRN that read PORN at the card's size; the real bottle laid on them, its PDRN line
    # set large enough for a bottle the card shows ~45 px wide on a 1440 px screen, --pdrn xl (review 4; card 7: the
    # photo frames her whole face and the bottle in the card's 13:20, which the old card 7's selfie could not)
    held(SRC / 'phenomenon-4-ai.jpg', OUT / 'phenomenon-4.jpg', '--roi', '420,540,600,945', '--pump', 'up', '--anchor', 'centre',
         '--tone', 'render', '--pdrn', 'xl')
    held(SRC / 'phenomenon-7-ai.jpg', OUT / 'phenomenon-7.jpg', '--line', '411,1053,401,544', '--w', '127', '--width', '1.23',
         '--anchor', 'base', '--fingers', 'left', '--tone', 'render', '--pdrn', 'xl')
    # ---- the balm banner (from 1200 px): the balm eye photo widened to a landscape by gpt-image-2
    # (pdrn-balm/source/apply-eye-wide-ai.png: her whole head in frame, studio background to her left; the square
    # original was framed so tight that her temple and hair ran into its edges, which showed as a pasted rectangle),
    # the brand's wordmark set on the stick
    wide = Image.open(BRAND / 'pdrn-balm' / 'source' / 'apply-eye-wide-ai.png').convert('RGB')
    save(relabel_bottles.relabel(wide, [('box', (1198, 536, 1264, 664), (1230, 552))]), 'balm-wide.jpg')
    # ---- Beauty is a celebration: the export's two models as women in their fifties (gpt-image-2, source/celebration-ai.jpg)
    save(Image.open(SRC / 'celebration-ai.jpg').convert('RGB'), 'celebration.jpg')
    # ---- Shop by category: 4:5 crops, face and product in the upper two thirds (the name and button sit low left)
    save(crop45(SRC / 'tile-foundation.jpg', (0, 0, 1397, 1747)), 'tile-foundation.jpg')
    save(crop45(BRAND / 'egf-nad-serum' / 'hold-cheek.jpg', (108, 0, 972, 1080)), 'tile-serum.jpg')
    save(crop45(BRAND / 'pdrn-balm' / 'hold-cheek.jpg', (150, 0, 1014, 1080)), 'tile-balm.jpg')
    # her whole head and the brush in her hand (1254 px source: the old box, measured on a 1024 px one, cut her hair
    # and ear at the tile's right edge, review 5)
    save(crop45(SRC / 'brush-ai.jpg', (150, 0, 1153, 1254)), 'tile-brush.jpg')
    # ---- Bundle & Save
    save(trio(foundation_unit(), height=0.7, spread=0.2, count=2), 'bundle-foundation.jpg')
    # the shelf's foundation card: the bottle alone, as the bundle's (the export's card photo cast a long grey shadow
    # off to one side)
    save(trio(foundation_unit(), height=0.7, count=1), 'card-foundation.jpg')
    # the empty cart drawer's bottle (76 x 213 on screen): the same cut-out at 3x, its PDRN line at label_fix.XL (the
    # old hand-made file printed the render's own line, which read PORN; review 5)
    unit = foundation_unit(); unit.thumbnail((228, 640), Image.LANCZOS)
    bottle = Image.new('RGBA', (228, 640), (0, 0, 0, 0)); bottle.alpha_composite(unit, ((228 - unit.width) // 2, 640 - unit.height))
    path = ROOT / 'tools' / 'theme-build' / 'static' / 'skinofab-cart-bottle.png'
    bottle.save(path, optimize=True); print(f'{path.relative_to(ROOT)}  {bottle.size[0]}x{bottle.size[1]}  {path.stat().st_size // 1024} KB')
    save(Image.open(BRAND / 'egf-nad-serum' / 'trio.jpg').convert('RGB').resize((1000, 1000), Image.LANCZOS), 'bundle-serum.jpg')
    save(trio(cutout(BRAND / 'pdrn-balm' / 'card.jpg', keep='tallest'), height=0.62), 'bundle-balm.jpg')
    save(trio(cutout(BRAND / 'lymphatic-brush' / 'card.jpg', keep='all'), height=0.5, spread=0.3, side=0.9), 'bundle-brush.jpg')
    # ---- banners of the listing pages (the export's showed four young models with products the store no longer
    # sells): our four women 45+ with their products, side by side (wide) and two by two (phones)
    tiles = [Image.open(OUT / f'tile-{k}.jpg').convert('RGB') for k in ('foundation', 'serum', 'balm', 'brush')]
    def cover(im, w, h, fy=0.3):
        k = max(w / im.width, h / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        x, y = (im.width - w) // 2, int((im.height - h) * fy)
        return im.crop((x, y, x + w, y + h))
    # each tile whole, at its own 4:5 (narrower panels cut the brush model's face at the right; the page shows the
    # collage at its own shape, the title above it: apply_persona.listing_banners)
    wide = Image.new('RGB', (3456, 1080), 'white')
    for i, tile in enumerate(tiles): wide.paste(cover(tile, 864, 1080), (i * 864, 0))
    save(wide, 'collage-wide.jpg')
    square = Image.new('RGB', (2000, 2500), 'white')
    for i, tile in enumerate([tiles[0], tiles[1], tiles[3], tiles[2]]):
        square.paste(cover(tile, 1000, 1250), ((i % 2) * 1000, (i // 2) * 1250))
    save(square, 'collage-square.jpg')
    for f in TMP.iterdir(): f.unlink()
    TMP.rmdir()


if __name__ == '__main__':
    main()
