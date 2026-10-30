"""Score the before/after screenshot pairs visual-diff.mjs captured.

usage: python3 diff.py <shots_dir>
For each pair: share of pixels that differ (any channel > 24), the page heights, and a side-by-side image
(before | after | differences in red) for every pair over 0.5 %. Prints one line per pair, worst first.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

D = Path(sys.argv[1])
rows = []
for before in sorted(D.glob('*-before.png')):
    after = before.with_name(before.name.replace('-before.png', '-after.png'))
    if not after.exists(): continue
    a, b = Image.open(before).convert('RGB'), Image.open(after).convert('RGB')
    w, h = min(a.width, b.width), min(a.height, b.height)
    A, B = np.asarray(a.crop((0, 0, w, h)), np.int16), np.asarray(b.crop((0, 0, w, h)), np.int16)
    mask = (np.abs(A - B).max(-1) > 24)
    share = mask.mean() * 100
    rows.append((share, before.name.replace('-before.png', ''), a.height, b.height))
    if share > 0.5:
        red = B.copy().astype(np.uint8); red[mask] = [255, 0, 0]
        scale = min(1.0, 4000 / h)
        side = Image.new('RGB', (w * 3, h), 'white')
        for i, im in enumerate((a.crop((0, 0, w, h)), b.crop((0, 0, w, h)), Image.fromarray(red))): side.paste(im, (i * w, 0))
        side.resize((int(w * 3 * scale), int(h * scale))).save(D / (before.name.replace('-before.png', '-diff.jpg')), quality=70)
for share, name, ha, hb in sorted(rows, reverse=True):
    print(f'{share:6.2f}%  {name:60s} height {ha} -> {hb}')
