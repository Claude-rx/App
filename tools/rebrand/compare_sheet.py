"""Before/after review sheets: original master (left) next to its regenerated image (right), 4 pairs per row.

usage: python3 -I compare_sheet.py <groups.json> <export_dir_before> <gen_dir> <out_prefix> [n,n,...]
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
G = {g['n']: g for g in json.load(open(sys.argv[1]))}
IMG, GEN, OUT = Path(sys.argv[2]) / 'assets' / 'img', Path(sys.argv[3]), sys.argv[4]
ns = [int(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 else sorted(int(p.stem) for p in GEN.glob('*.png') if p.stem.isdigit())
T, C, PER = 260, 4, 16
for s in range(0, len(ns), PER):
    chunk = ns[s:s + PER]
    rows = (len(chunk) + C - 1) // C
    sheet = Image.new('RGB', (C * 2 * T, rows * (T + 18)), 'white'); d = ImageDraw.Draw(sheet)
    for j, n in enumerate(chunk):
        x, y = (j % C) * 2 * T, (j // C) * (T + 18)
        for k, p in enumerate((IMG / G[n]['master'], GEN / f'{n}.png')):
            try: im = Image.open(p).convert('RGB'); im.thumbnail((T, T)); sheet.paste(im, (x + k * T + (T - im.width) // 2, y))
            except Exception: pass
        d.rectangle([x, y + T, x + 2 * T, y + T + 18], fill='black'); d.text((x + 4, y + T + 3), f'#{n}', fill='white')
    sheet.save(f'{OUT}-{s // PER:02d}.jpg', quality=78)
print((len(ns) + PER - 1) // PER, 'sheets')
