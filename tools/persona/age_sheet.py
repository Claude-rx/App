"""Before/after review sheets for the 45+ edits: current site image (left) next to the edit (right), 4 pairs per row.

usage: python3 -I age_sheet.py <age-jobs.json> <ref_dir> <gen_dir> <out_prefix> [key,key,...]
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
jobs = {j['key']: j for j in json.load(open(sys.argv[1]))}
REF, GEN, OUT = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
keys = sys.argv[5].split(',') if len(sys.argv) > 5 else sorted((p.stem for p in GEN.glob('age-*.png')), key=lambda k: int(k[4:]))
T, C, PER = 260, 4, 16
for s in range(0, len(keys), PER):
    chunk = keys[s:s + PER]; rows = (len(chunk) + C - 1) // C
    sheet = Image.new('RGB', (C * 2 * T, rows * (T + 18)), 'white'); d = ImageDraw.Draw(sheet)
    for j, k in enumerate(chunk):
        x, y = (j % C) * 2 * T, (j // C) * (T + 18)
        src = REF / jobs[k]['refs'][0].rsplit('/', 1)[1]
        for i, p in enumerate((src, GEN / f'{k}.png')):
            try: im = Image.open(p).convert('RGB'); im.thumbnail((T, T)); sheet.paste(im, (x + i * T + (T - im.width) // 2, y))
            except Exception: pass
        d.rectangle([x, y + T, x + 2 * T, y + T + 18], fill='black'); d.text((x + 4, y + T + 3), f"#{k[4:]} {jobs[k]['kind']}", fill='white')
    sheet.save(f'{OUT}-{s // PER:02d}.jpg', quality=78)
print((len(keys) + PER - 1) // PER, 'sheets')
