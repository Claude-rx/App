"""The Lymphatic Brush's page images and videos, from the owner's Solena store, under the SKINOFAB name.

usage: python3 -I brush_assets.py <work_dir>
- downloads the sources listed in brush_copy.SOURCES into <work_dir>/brush/src/ (kept; a re-run reuses them)
- images -> brand/lymphatic-brush/ (committed): the 7 gallery images, the "how it works" drawings, the comparison
  photos, the buyer avatars and the bundle gift photos. Two carried the Solena name and are rebranded here:
  the case's printed logo (gallery 5 and the case gift photo) becomes the SKINOFAB wordmark, and "THE SOLENA" on
  the comparison chart (gallery 6) becomes "THE SKINOFAB"
- videos -> <work_dir>/brush/media/ (not committed, like the theme's other media): the six silent review clips at
  540 x 960, and the how-to video at 720 x 1280 with the "from Solena" words cut (sound and burned-in caption,
  6.42 s to 7.27 s), each with a poster frame
"""
import shutil, subprocess, sys, urllib.request
from pathlib import Path

import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brush_copy import SOURCES

WORK = Path(sys.argv[1]).resolve()
SRC, MEDIA = WORK / 'brush' / 'src', WORK / 'brush' / 'media'
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'brand' / 'lymphatic-brush'
LOGO = ROOT / 'brand' / 'checkout' / 'skinofab-logo-1200.png'
FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
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
    for k in range(1, 8):
        img = rgb(f'gallery-{k}.png')
        if k == 5: img = case_logo(img, (400, 750, 690, 836), 252)
        if k == 6: img = chart_title(img)
        save(img, f'gallery-{k}.jpg', quality=88)
    for k in range(1, 4): save(Image.open(SRC / f'mech-{k}.webp'), f'how-{k}.jpg', (1264, 848))
    save(Image.open(SRC / 'compare-ours.png'), 'compare-ours.jpg', (1000, 1000))
    save(Image.open(SRC / 'compare-copy.png'), 'compare-copy.jpg', (1000, 1000))
    for k in range(1, 4):
        save(square(f'avatar-{k}.webp', 96), f'buyer-{k}.jpg')
        save(square(f'mini-{k}.' + ('avif' if k == 1 else 'webp'), 112), f'review-{k}.jpg')
    case = case_logo(rgb('gift-case.png'), (285, 340, 520, 420), 196)
    save(Image.fromarray(np.clip(case, 0, 255).astype(np.uint8)).crop((210, 200, 590, 580)), 'gift-case.jpg', (160, 160))
    save(Image.open(SRC / 'gift-body-brush.png').convert('RGB').crop((120, 120, 680, 680)), 'gift-body-brush.jpg', (160, 160))
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
