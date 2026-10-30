"""Replace a burned-in white caption in a video with new text, frame by frame (e.g. "SMOOCHE" -> "SKINOFAB").

usage: python3 -I caption_swap.py <in.mp4> <out.mp4> <x0,y0,x1,y1> <new text> [--weight ExtraBold]
- box: where the caption sits (px of the video); in each frame the caption is its near-white, colourless pixels
  inside the box (skin and nails are warmer, so they are left alone)
- the caption's shape comes from the frame where it shows most (it may fade in; it does not move); in every frame it
  shows in, at any opacity, its letters and soft shadow are inpainted away from the picture around them, and the new
  text is drawn in Montserrat at its centre and letter height, white with a soft dark shadow like the original, at the
  same opacity as the old caption in that frame
- frames without the caption, and the soundtrack, are left exactly as they are
"""
import subprocess, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, DST = sys.argv[1], sys.argv[2]
X0, Y0, X1, Y1 = (int(v) for v in sys.argv[3].split(','))
TEXT = sys.argv[4]
WEIGHT = sys.argv[sys.argv.index('--weight') + 1] if '--weight' in sys.argv else 'ExtraBold'
FONT = Path(__file__).resolve().parents[2] / 'tools' / 'persona' / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
if not FONT.exists(): FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'


def probe(key):
    return subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', f'stream={key}', '-of', 'csv=p=0', SRC],
                          check=True, capture_output=True, text=True).stdout.strip()


W, H = (int(v) for v in probe('width,height').split(','))
FPS = probe('r_frame_rate')


def font(px):
    f = ImageFont.truetype(str(FONT), px); f.set_variation_by_name(WEIGHT); return f


def caption_mask(frame):
    box = frame[Y0:Y1, X0:X1].astype(np.int16)
    lo, hi = box.min(axis=2), box.max(axis=2)
    m = (lo > 222) & (hi - lo < 26)                       # near white and colourless
    full = np.zeros((H, W), np.uint8); full[Y0:Y1, X0:X1] = m.astype(np.uint8) * 255
    return full


def draw_text(frame, cx, cy, cap_h):
    """The new caption, white, at the old one's centre and letter height (a 4x render, scaled down)."""
    S = 4
    size = 10
    while True:                                          # the font size whose capital height matches the caption's
        bb = font(size * S).getbbox('H')
        if bb[3] - bb[1] >= cap_h * S or size > 400: break
        size += 1
    f = font(size * S)
    l, t, r, b = f.getbbox(TEXT)
    tw, th = r - l, b - t
    pad = 12 * S
    layer = Image.new('L', (tw + 2 * pad, th + 2 * pad), 0)
    ImageDraw.Draw(layer).text((pad - l, pad - t), TEXT, font=f, fill=255)
    small = layer.resize((layer.width // S, layer.height // S), Image.LANCZOS)
    shadow = small.filter(ImageFilter.GaussianBlur(1.6))
    img = Image.fromarray(frame)
    ox, oy = int(round(cx - small.width / 2)), int(round(cy - small.height / 2))
    dark = Image.new('RGB', small.size, (40, 30, 30))
    img.paste(dark, (ox + 1, oy + 2), shadow.point(lambda v: int(v * 0.45)))
    img.paste(Image.new('RGB', small.size, (255, 255, 255)), (ox, oy), small)
    return np.asarray(img)


def frames():
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
    dec.wait()


# pass 1: the caption's own shape, from the frame where it shows most (it fades in, it does not move)
best, best_n = None, 0
for frame in frames():
    m = caption_mask(frame); k = int(m.sum() // 255)
    if k > best_n: best, best_n = m, k
if best_n < 150: sys.exit('no caption found in the box')
ys, xs = np.nonzero(best)
rows = np.bincount(ys - ys.min()); keep = np.nonzero(rows > rows.max() * 0.15)[0]
CAP_H = keep.max() - keep.min() + 1
CX, CY = (xs.min() + xs.max()) / 2, ys.min() + keep.min() + CAP_H / 2
GLYPH = best > 0
CORE = cv2.erode(best, np.ones((3, 3), np.uint8)) > 0          # inside the letters, away from their soft edges
ERASE = cv2.dilate(best, np.ones((9, 9), np.uint8))            # the letters, their anti-aliasing and shadow


def opacity(frame, clean):
    """How much of the white caption is in this frame: 0 (none) to 1 (full), from its letters against what is behind."""
    lum = lambda a: a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    li, bi = lum(frame.astype(float))[CORE].mean(), lum(clean.astype(float))[CORE].mean()
    return float(np.clip((li - bi) / max(1.0, 255 - bi), 0, 1))


# pass 2: every frame the caption shows in (fading in too): erased from the picture around it, the new text drawn at
# the same opacity
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', FPS, '-i', '-',
                        '-i', SRC, '-map', '0:v:0', '-map', '1:a:0?', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                        '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', DST], stdin=subprocess.PIPE)
n = done = 0
for frame in frames():
    clean = cv2.inpaint(frame, ERASE, 6, cv2.INPAINT_TELEA)
    a = opacity(frame, clean)
    if a > 0.04:
        drawn = draw_text(clean.copy(), CX, CY, CAP_H)
        frame = (clean * (1 - a) + drawn * a).astype(np.uint8) if a < 0.97 else drawn
        done += 1
    enc.stdin.write(np.ascontiguousarray(frame).tobytes()); n += 1
enc.stdin.close(); enc.wait()
print(f'{DST}: the caption ({CAP_H} px letters at {CX:.0f},{CY:.0f}) was in {done} of {n} frames, replaced with "{TEXT}"')
