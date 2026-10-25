"""Check a Genjutsu product swap against its source video: a before/after frame sheet and the timing drift.

usage: python3 -I video_swap_sheet.py <source.mp4> <result.mp4> <out_dir> [--frames 8]
- <out_dir>/<result stem>-sheet.jpg: the source (top row) and the result (bottom row) at the same moments
- prints the drift: for sampled result frames, the source moment that looks most like it (grey thumbnails, mean
  normalised), and the result's length against the source's. A steady growth means the result runs fast or slow and
  needs stretching back (genjutsu_direct.py does that when it publishes).
"""
import subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

SRC, RES, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
N = int(sys.argv[sys.argv.index('--frames') + 1]) if '--frames' in sys.argv else 8
OUT.mkdir(parents=True, exist_ok=True)


def duration(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                check=True, capture_output=True, text=True).stdout)


def frame(p, t, h=560):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', str(p), '-frames:v', '1', '-vf', f'scale=-2:{h}',
                          '-f', 'image2pipe', '-vcodec', 'png', '-'], check=True, capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert('RGB')


def grey(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-vf', 'fps=10,scale=48:86,format=gray', '-f', 'rawvideo', '-'],
                         check=True, capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 86, 48).astype(float)
    return (a - a.mean(axis=(1, 2), keepdims=True)) / (a.std(axis=(1, 2), keepdims=True) + 1e-6)


ds, dr = duration(SRC), duration(RES)
ts = [dr * (k + 0.5) / N for k in range(N)]
pairs = [(frame(SRC, t * ds / dr), frame(RES, t)) for t in ts]           # the same moment in each
w = max(max(a.width, b.width) for a, b in pairs); h = 560
sheet = Image.new('RGB', (w * N, h * 2 + 24), 'white'); d = ImageDraw.Draw(sheet)
for k, (a, b) in enumerate(pairs):
    sheet.paste(a, (k * w, 0)); sheet.paste(b, (k * w, h + 24)); d.text((k * w + 4, h + 6), f'{ts[k]:.1f} s  before / after', fill='black')
dst = OUT / f'{RES.stem}-sheet.jpg'; sheet.save(dst, quality=85)
a, b = grey(SRC), grey(RES)
offs = [round(int(((a - b[i]) ** 2).mean(axis=(1, 2)).argmin()) / 10 - i / 10, 1) for i in range(0, len(b), 10)]
print(f'{RES.name}: {dr:.2f} s against {ds:.2f} s source ({dr / ds:.3f}); drift each 1 s: {offs}')
print('sheet', dst)
