"""The foundation page's "how it works" loop: the product page's photo of a woman with five dots of the foundation on
her face (goes on white), the dots blending out one by one while their colour shifts into her skin tone, then her
face with nothing left to see (one shade, your tone), and back. It replaces the K-beauty section's label close-up.

usage: python3 -I tools/persona/howto_video.py
Sources (brand/adaptive-peptide-foundation/source/): howto-dots.jpg, the page's photo as the store shows it (1350 px);
howto-clean-ai.png, the same photo with the dots removed (gpt-image-2 edit). Only the dots' areas are taken from the
edit, aligned to the photo (ECC): every other pixel is the photo's own, so nothing else moves.
Writes brand/adaptive-peptide-foundation/howto/howto.mp4 (H.264, 864 x 1080, 24 fps, 9 s, silent, faststart),
howto.webm (the same in VP9, the page's second source) and howto-poster.jpg (its first frame). It is an illustration
and says so in its corner.
"""
import subprocess, shutil, tempfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'brand' / 'adaptive-peptide-foundation' / 'source'
OUT = ROOT / 'brand' / 'adaptive-peptide-foundation' / 'howto'
FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
FPS, SECONDS, SIZE = 24, 9.0, (864, 1080)
CROP = (110, 0, 1190, 1350)                          # 4:5 of the square photo: the bottle and her whole face
# the dots (centre x, y, radii x, y) in the 1350 px photo, in the order they blend
DOTS = [(1022, 159, 48, 52), (1014, 532, 40, 44), (1146, 647, 26, 48), (871, 917, 50, 44)]
STEPS = [(0.0, 1.6, '1', 'Goes on white'), (1.6, 5.2, '2', 'Blend: it shifts to your tone'), (5.2, 7.6, '3', 'One shade. Yours.')]


def font(size, weight=600):
    f = ImageFont.truetype(str(FONT), size); f.set_variation_by_axes([weight]); return f


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def chip(draw, num, text, alpha, x=36, y=40):
    """A white pill, top left: the step's number in a black disc and its line."""
    f, fn = font(30), font(26, 700)
    w = int(draw.textlength(text, font=f)) + 104
    a = int(255 * alpha)
    draw.rounded_rectangle((x, y, x + w, y + 64), 32, fill=(255, 255, 255, int(235 * alpha)))
    draw.ellipse((x + 12, y + 12, x + 52, y + 52), fill=(21, 21, 21, a))
    draw.text((x + 32, y + 33), num, font=fn, fill=(255, 255, 255, a), anchor='mm')
    draw.text((x + 68, y + 33), text, font=f, fill=(21, 21, 21, a), anchor='lm')


def main():
    dots = np.asarray(Image.open(SRC / 'howto-dots.jpg').convert('RGB')).astype(np.float32)
    H, W = dots.shape[:2]
    edit = np.asarray(Image.open(SRC / 'howto-clean-ai.png').convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
    g1, g2 = (cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) for x in (dots, edit))
    warp = np.eye(2, 3, dtype=np.float32)
    _, warp = cv2.findTransformECC(g1, g2, warp, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
    edit = cv2.warpAffine(edit, warp, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    yy, xx = np.mgrid[0:H, 0:W]
    lum = dots.mean(2)
    masks, films = [], []
    for cx, cy, rx, ry in DOTS:
        e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
        m = ndimage.binary_dilation(ndimage.binary_fill_holes(e & (lum > 135)), iterations=12) & ndimage.binary_dilation(e, iterations=16)
        masks.append(np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 5) * 1.4, 0, 1)[..., None])
        # the cream as it spreads: a soft blob around the dot, wider as it is worked in
        films.append(((xx - cx) / (rx * 2.2)) ** 2 + ((yy - cy) / (ry * 2.2)) ** 2)
    clean = dots.copy()
    for m in masks: clean = clean * (1 - m) + edit * m
    skin = [edit[int(cy), int(cx)] for cx, cy, _, _ in DOTS]
    tmp = Path(tempfile.mkdtemp())
    n = int(FPS * SECONDS)
    for i in range(n):
        t = i / FPS
        frame = dots.copy()
        for k, (m, film) in enumerate(zip(masks, films)):
            p = ease((t - (1.6 + 0.75 * k)) / 1.6)                       # each dot blends over 1.6 s, one after another
            if t >= 7.6: p = 1 - ease((t - 7.6) / 1.2)                   # and all come back for the loop
            frame = frame * (1 - m * p) + clean * (m * p)
            # while it is worked in, a thin film of it spreads around the dot, its colour going from cream to her skin
            spread = np.exp(-film / (0.35 + 0.9 * p)) * (0.38 * np.sin(np.pi * p))
            col = np.array([246, 240, 234], np.float32) * (1 - p) + skin[k] * p
            frame = frame * (1 - spread[..., None]) + col * spread[..., None]
        im = Image.fromarray(np.clip(frame + 0.5, 0, 255).astype(np.uint8)).crop(CROP).resize(SIZE, Image.LANCZOS).convert('RGBA')
        layer = Image.new('RGBA', SIZE, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        for s0, s1, num, text in STEPS:
            a = min(ease((t - s0) / 0.35), 1 - ease((t - (s1 - 0.35)) / 0.35)) if s0 <= t < s1 else 0
            if a > 0: chip(d, num, text, a)
        d.rounded_rectangle((SIZE[0] - 168, SIZE[1] - 58, SIZE[0] - 24, SIZE[1] - 24), 17, fill=(255, 255, 255, 200))
        d.text((SIZE[0] - 96, SIZE[1] - 41), 'Illustration', font=font(19, 500), fill=(60, 60, 60, 255), anchor='mm')
        Image.alpha_composite(im, layer).convert('RGB').save(tmp / f'f{i:04d}.jpg', quality=93)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(tmp / 'f0000.jpg', OUT / 'howto-poster.jpg')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(tmp / 'f%04d.jpg'),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '-an', str(OUT / 'howto.mp4')], check=True)
    # the same frames as VP9, for browsers that ship without H.264 (Chromium builds, some Linux Firefox)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(tmp / 'f%04d.jpg'),
                    '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2',
                    '-pix_fmt', 'yuv420p', '-an', str(OUT / 'howto.webm')], check=True)
    shutil.rmtree(tmp)
    for f in ('howto.mp4', 'howto.webm'): print(OUT / f, (OUT / f).stat().st_size // 1024, 'KB')


main()
