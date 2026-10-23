"""The Lymphatic Brush's page images and videos, from the owner's Solena store, under the SKINOFAB name.

usage: python3 -I brush_assets.py <work_dir>
- downloads the sources listed in brush_copy.SOURCES into <work_dir>/brush/src/ (kept; a re-run reuses them)
- images -> brand/lymphatic-brush/ (committed): the gallery in brush_copy.GALLERY order (hero, case, how-to-use,
  features, vs-tools), the "how it works" drawings, the comparison photos, the bundle gift photos and the homepage
  shelf card (card.jpg). Claims nothing backs are taken out of the pixels: the hero is new (the real brush and its
  SKINOFAB case, an honest headline, no model); "water retention" and "move fluid" (features) and "supports drainage"
  (vs-tools) are re-set in the same Montserrat; the case's printed logo becomes the SKINOFAB wordmark and "THE SOLENA"
  on the chart becomes "THE SKINOFAB". Solena's before/after photos (wrinkles that vanish) and its "Loved by 5,000+"
  board are not used.
- videos -> <work_dir>/brush/media/ (not committed, like the theme's other media): the six silent review clips at
  540 x 960, and the how-to video at 720 x 1280 with the "from Solena" words cut (sound and burned-in caption,
  6.42 s to 7.27 s), each with a poster frame
"""
import shutil, subprocess, sys, urllib.request
from pathlib import Path

import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brush_copy import SOURCES, GALLERY, HERO

WORK = Path(sys.argv[1]).resolve()
SRC, MEDIA = WORK / 'brush' / 'src', WORK / 'brush' / 'media'
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'brand' / 'lymphatic-brush'
LOGO = ROOT / 'brand' / 'checkout' / 'skinofab-logo-1200.png'
FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
PLAYFAIR = ROOT / 'tools' / 'theme-build' / 'static' / 'fonts' / 'playfairdisplay_v40_nuFiD-vYSZviVYUb_rj3ij__anPXDTzYgA.woff2'
BG = (245, 244, 240)                                   # the gallery's cream backdrop
INK, MAUVE = (45, 34, 30), (156, 92, 101)              # its heading and accent colors
TUTORIAL_CUT = (6.42, 7.27)     # "from Solena", spoken and captioned


def fetch():
    SRC.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        dst = SRC / name
        if dst.exists() and dst.stat().st_size: continue
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=120) as r: dst.write_bytes(r.read())
        print('fetched', name)


def rgb(name):
    return np.asarray(Image.open(SRC / name).convert('RGB')).astype(np.float32)


def case_logo(img, box, logo_w):
    """Replace the light logo printed on the dark case inside `box` (x0, y0, x1, y1) with the SKINOFAB wordmark:
    the old letters are inpainted from the case around them, the wordmark takes their center and color."""
    x0, y0, x1, y1 = box
    lum = img.mean(2)
    mask = np.zeros(lum.shape, np.uint8)
    mask[y0:y1, x0:x1] = (lum[y0:y1, x0:x1] > 120).astype(np.uint8) * 255
    ys, xs = np.where(mask > 0)
    cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
    ink = np.median(img[ys, xs], axis=0)                          # the printed logo's color
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
    out = cv2.inpaint(np.clip(img, 0, 255).astype(np.uint8), mask, 9, cv2.INPAINT_TELEA).astype(np.float32)
    mark = Image.open(LOGO).convert('RGBA')
    mark = mark.resize((logo_w, round(mark.height * logo_w / mark.width)), Image.LANCZOS)
    a = np.asarray(mark)[..., 3].astype(np.float32) / 255 * 0.96
    h, w = a.shape
    top, left = int(round(cy - h / 2)), int(round(cx - w / 2))
    region = out[top:top + h, left:left + w]
    out[top:top + h, left:left + w] = region * (1 - a[..., None]) + ink[None, None, :] * a[..., None]
    return out


def chart_title(img):
    """Gallery 6: "THE SOLENA" above "LYMPHATIC BRUSH" becomes "THE SKINOFAB" in the same Montserrat setting."""
    lum = img.mean(2)
    band = lum[70:122, 60:520] < 120                               # the first title line only
    ys, xs = np.where(band)
    y0, y1, x0 = ys.min() + 70, ys.max() + 70, xs.min() + 60
    bg = np.median(img[60:66, 60:520].reshape(-1, 3), axis=0)
    out = img.copy()
    out[y0 - 4:y1 + 5, x0 - 4:xs.max() + 60 + 6] = bg
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    cap = y1 - y0 + 1                                              # cap height of the old line
    font = ImageFont.truetype(str(FONT), 10)
    font.set_variation_by_name('Medium')
    size = 10
    while True:                                                    # match the cap height
        f = ImageFont.truetype(str(FONT), size + 1); f.set_variation_by_name('Medium')
        if f.getbbox('THE')[3] - f.getbbox('THE')[1] > cap: break
        font, size = f, size + 1
    bx = font.getbbox('THE SKINOFAB')
    d.text((x0 - bx[0], y0 - bx[1]), 'THE SKINOFAB', font=font, fill=(17, 17, 17))
    return np.asarray(im).astype(np.float32)


def vf(path, size, weight):
    f = ImageFont.truetype(str(path), size); f.set_variation_by_name(weight); return f


def retext(img, region, old_lines, new_lines, weight, align='left', fit=None):
    """The text lines inside region (x0, y0, x1, y1), on a flat backdrop, re-set as new_lines in Montserrat at the
    original's size (from the measured width of each old line), on the original baselines and in the original ink."""
    im = img if isinstance(img, Image.Image) else Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    x0, y0, x1, y1 = region
    a = np.asarray(im.convert('RGB')).astype(np.int16)
    sub = a[y0:y1, x0:x1]
    bg = np.median(np.concatenate([sub[0], sub[-1], sub[:, 0], sub[:, -1]]), axis=0)
    ink = np.abs(sub - bg).sum(2) > 90
    bands, start = [], None
    for y, r in enumerate(list(ink.any(1)) + [False]):
        if r and start is None: start = y
        if not r and start is not None:
            if bands and start - bands[-1][1] < 4: bands[-1] = (bands[-1][0], y)
            elif y - start > 3: bands.append((start, y))
            start = None
    if len(bands) != len(old_lines): raise SystemExit(f'retext: {len(bands)} lines in {region}, expected {len(old_lines)}')
    lines = []
    for b0, b1 in bands:
        cols = np.nonzero(ink[b0:b1].any(0))[0]
        lines.append((x0 + cols.min(), y0 + b0, x0 + cols.max() + 1, y0 + b1))
    ref = vf(FONT, 100, weight)
    w = lambda f, s: f.getbbox(s, anchor='ls')[2] - f.getbbox(s, anchor='ls')[0]
    size = round(np.mean([100 * (l[2] - l[0]) / w(ref, s) for l, s in zip(lines, old_lines)]))
    f = vf(FONT, size, weight)
    px = sub[ink]; lum = px.mean(1)
    color = tuple(int(v) for v in np.median(px[lum <= np.percentile(lum, 35)], axis=0))   # the core of the strokes
    out = im.convert('RGB').copy(); d = ImageDraw.Draw(out)
    d.rectangle(region, fill=tuple(int(v) for v in bg))
    for (lx0, _, _, ly1), old, new in zip(lines, old_lines, new_lines):
        base = ly1 - f.getbbox(old, anchor='ls')[3]
        g = f
        while fit and w(g, new) > fit and g.size > 6: g = vf(FONT, g.size - 1, weight)
        bb = g.getbbox(new, anchor='ls')
        x = (x0 + x1) / 2 - (bb[2] - bb[0]) / 2 - bb[0] if align == 'center' else lx0 - bb[0]
        d.text((x, base), new, font=g, fill=color, anchor='ls')
    return np.asarray(out).astype(np.float32)


def hero(case_img):
    """Gallery 1: the real brush and its SKINOFAB case (from the case photo) on the gallery's backdrop, with an honest
    promise (brush_copy.HERO), three plain facts and the 30-day guarantee seal. No model: a persona photo takes this
    place once one is generated (docs/persona-image-shots.md, B1)."""
    W = 1080
    im = Image.new('RGB', (W, W), BG); d = ImageDraw.Draw(im)
    src = np.asarray(case_img).astype(np.int16)
    mask = np.abs(src - np.array(BG)).sum(2) > 30
    mask[:320] = False                                   # the case photo's own heading
    ys, xs = np.nonzero(mask)
    prod = case_img.crop((xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7))
    scale = 640 / prod.height
    prod = prod.resize((round(prod.width * scale), 640), Image.LANCZOS)
    im.paste(prod, (W - prod.width - 40, W - prod.height - 70))
    y = 70
    for line in HERO['title']:
        f = vf(FONT, 78, 'Black')
        while d.textlength(line, font=f) > W - 120: f = vf(FONT, f.size - 2, 'Black')
        d.text((60, y), line, font=f, fill=INK, anchor='lt'); y += 88
    small, big = vf(FONT, 40, 'Bold'), vf(PLAYFAIR, 92, 'Bold')
    d.text((62, y + 66), HERO['in'], font=small, fill=INK, anchor='ls')
    d.text((62 + d.textlength(HERO['in'] + ' ', font=small), y + 70), HERO['accent'], font=big, fill=MAUVE, anchor='ls')
    y += 120
    chip_f = vf(FONT, 27, 'SemiBold')
    for fact in HERO['facts']:
        tw = d.textlength(fact, font=chip_f)
        d.rounded_rectangle((52, y, 52 + 94 + tw + 30, y + 78), radius=39, fill=(233, 228, 220))
        d.ellipse((66, y + 15, 114, y + 63), fill=(255, 255, 255))
        d.line([(79, y + 40), (87, y + 48), (102, y + 31)], fill=MAUVE, width=5, joint='curve')
        d.text((136, y + 40), fact, font=chip_f, fill=(75, 60, 55), anchor='lm'); y += 96
    seal = guarantee_seal(220)
    im.paste(seal, (44, W - seal.height - 44), seal)
    return np.asarray(im).astype(np.float32)


def guarantee_seal(size):
    """The 30-day money-back seal of Solena's first image, redrawn (its photo overlaps the model): a mauve
    starburst, the text slightly tilted. RGBA, size x size."""
    import math
    k = 4                                                # drawn large, scaled down for smooth edges
    S = size * k
    seal = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(seal)
    c, R, r, n = S / 2, S / 2 - 2, S / 2 * 0.86, 24
    pts = [(c + (R if i % 2 == 0 else r) * math.cos(math.pi * i / n), c + (R if i % 2 == 0 else r) * math.sin(math.pi * i / n)) for i in range(2 * n)]
    d.polygon(pts, fill=MAUVE + (255,))
    text = Image.new('RGBA', (S, S), (0, 0, 0, 0)); td = ImageDraw.Draw(text)
    td.text((c, c - S * 0.11), '30-Day', font=vf(FONT, int(S * 0.17), 'Bold'), fill=(255, 255, 255, 255), anchor='mm')
    td.text((c, c + S * 0.07), 'Money-Back', font=vf(FONT, int(S * 0.095), 'Medium'), fill=(255, 255, 255, 255), anchor='mm')
    td.text((c, c + S * 0.19), 'Guarantee', font=vf(FONT, int(S * 0.095), 'Medium'), fill=(255, 255, 255, 255), anchor='mm')
    seal.alpha_composite(text.rotate(8, resample=Image.BICUBIC, center=(c, c)))
    return seal.resize((size, size), Image.LANCZOS)


def save(arr_or_img, name, size=None, quality=86):
    im = arr_or_img if isinstance(arr_or_img, Image.Image) else Image.fromarray(np.clip(arr_or_img, 0, 255).astype(np.uint8))
    im = im.convert('RGB')
    if size: im.thumbnail(size, Image.LANCZOS)
    im.save(OUT / name, quality=quality, optimize=True, progressive=True)
    return OUT / name


def square(name, px):
    im = Image.open(SRC / name).convert('RGB')
    s = min(im.size); l, t = (im.width - s) // 2, (im.height - s) // 2
    return im.crop((l, t, l + s, t + s)).resize((px, px), Image.LANCZOS)


def images():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in list(OUT.glob('gallery-*.jpg')) + list(OUT.glob('buyer-*.jpg')) + list(OUT.glob('review-*.jpg')): old.unlink()
    case = case_logo(rgb('gallery-5.png'), (400, 750, 690, 836), 252)
    case_img = Image.fromarray(np.clip(case, 0, 255).astype(np.uint8))
    made = {
        'hero': hero(case_img),
        'case': case,
        'how-to-use': rgb('gallery-4.png'),
        'features': retext(retext(rgb('gallery-3.png'), (60, 112, 1020, 186), ['WATER RETENTION'], ['MORNING PUFFINESS'],
                                  'ExtraBold', 'center', fit=960),
                           (220, 425, 515, 515), ['Hundreds of tips move', 'fluid just under the skin,', 'no pressing needed'],
                           ['Hundreds of soft tips', 'sweep over the skin,', 'no pressing needed'], 'Regular'),
        'vs-tools': retext(chart_title(rgb('gallery-6.png')), (85, 690, 470, 760), ['Supports drainage with', 'light pressure'],
                           ['Works with just a', 'light touch'], 'SemiBold'),
    }
    for name in GALLERY: save(made[name], f'{name}.jpg', quality=88)
    for k in range(1, 4): save(Image.open(SRC / f'mech-{k}.webp'), f'how-{k}.jpg', (1264, 848))
    save(Image.open(SRC / 'compare-ours.png'), 'compare-ours.jpg', (1000, 1000))
    save(Image.open(SRC / 'compare-copy.png'), 'compare-copy.jpg', (1000, 1000))
    gift = case_logo(rgb('gift-case.png'), (285, 340, 520, 420), 196)
    save(Image.fromarray(np.clip(gift, 0, 255).astype(np.uint8)).crop((210, 200, 590, 580)), 'gift-case.jpg', (160, 160))
    save(Image.open(SRC / 'gift-body-brush.png').convert('RGB').crop((120, 120, 680, 680)), 'gift-body-brush.jpg', (160, 160))
    # the product card (homepage shelf): the brush and its SKINOFAB case, without the photo's heading, on the same
    # backdrop with room around it (the card crops to its own aspect)
    card = Image.new('RGB', (1080, 1080), BG)
    card.paste(case_img.crop((200, 330, 880, 1010)).resize((820, 820), Image.LANCZOS), (130, 140))
    save(card, 'card.jpg', quality=88)
    for p in sorted(OUT.glob('*.jpg')): print(p.relative_to(ROOT), Image.open(p).size, p.stat().st_size // 1024, 'KB')


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def videos():
    MEDIA.mkdir(parents=True, exist_ok=True)
    for k in range(1, 7):
        src, dst = SRC / f'video-{k}.mp4', MEDIA / f'brush-review-{k}.mp4'
        # the clips are silent: no audio track, 540 x 960, start fast
        ffmpeg('-i', str(src), '-an', '-vf', 'scale=540:-2', '-c:v', 'libx264', '-preset', 'slow', '-crf', '27',
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dst))
        ffmpeg('-ss', '0.6', '-i', str(dst), '-frames:v', '1', '-q:v', '4', str(dst.with_suffix('.jpg')))
    a, b = TUTORIAL_CUT
    src, dst = SRC / 'tutorial.mp4', MEDIA / 'brush-how-to.mp4'
    graph = (f'[0:v]trim=0:{a},setpts=PTS-STARTPTS[v0];[0:v]trim=start={b},setpts=PTS-STARTPTS[v1];'
             f'[0:a]atrim=0:{a},asetpts=PTS-STARTPTS,afade=t=out:st={a - 0.04}:d=0.04[a0];'
             f'[0:a]atrim=start={b},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.04[a1];'
             '[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a];[v]scale=720:-2[vs]')
    ffmpeg('-i', str(src), '-filter_complex', graph, '-map', '[vs]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'slow',
           '-crf', '26', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(dst))
    ffmpeg('-ss', '1.0', '-i', str(dst), '-frames:v', '1', '-q:v', '4', str(dst.with_suffix('.jpg')))
    for p in sorted(MEDIA.iterdir()): print(p.relative_to(WORK), p.stat().st_size // 1024, 'KB')


fetch()
images()
if '--no-video' not in sys.argv: videos()
