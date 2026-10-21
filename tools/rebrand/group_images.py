"""Group an export's raster images by source (width variants share a stem) and pick the largest of each.

usage: python3 -I group_images.py <export_dir> <out.json> [contact_sheet_prefix]
Writes [{"key", "master", "variants": [...], "w", "h"}] and optional numbered contact sheets (6x6) for review.
"""
import json, os, re, sys
from pathlib import Path
from PIL import Image, ImageDraw

EXPORT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
SHEET = sys.argv[3] if len(sys.argv) > 3 else None
IMG = EXPORT / 'assets' / 'img'

def key(name):
    s = re.sub(r'\.[a-z0-9]+$', '', name, flags=re.I)
    s = re.sub(r'-[0-9a-f]{6}$', '', s)
    s = re.sub(r'-[0-9]+w$', '', s)
    return re.sub(r'_[0-9]+x[0-9]*$', '', s)

groups = {}
for f in sorted(IMG.iterdir()):
    if f.suffix.lower() in ('.svg', '.gif') or not f.is_file(): continue
    try:
        with Image.open(f) as im: w, h = im.size
    except Exception: continue
    g = groups.setdefault(key(f.name), {'key': key(f.name), 'variants': []})
    g['variants'].append({'file': f.name, 'w': w, 'h': h})
out = []
for g in groups.values():
    m = max(g['variants'], key=lambda v: v['w'] * v['h'])
    out.append({'key': g['key'], 'master': m['file'], 'w': m['w'], 'h': m['h'], 'variants': [v['file'] for v in g['variants']]})
out.sort(key=lambda g: g['key'])
for i, g in enumerate(out): g['n'] = i
OUT.write_text(json.dumps(out, indent=1))
print(len(out), 'groups')
if SHEET:
    T, C = 200, 6
    for s in range(0, len(out), C * C):
        sheet = Image.new('RGB', (C * T, C * (T + 18)), 'white'); d = ImageDraw.Draw(sheet)
        for j, g in enumerate(out[s:s + C * C]):
            try:
                im = Image.open(IMG / g['master']).convert('RGB'); im.thumbnail((T, T))
            except Exception: continue
            x, y = (j % C) * T, (j // C) * (T + 18)
            sheet.paste(im, (x + (T - im.width) // 2, y))
            d.rectangle([x, y + T, x + T, y + T + 18], fill='black'); d.text((x + 4, y + T + 3), f"#{g['n']} {g['w']}x{g['h']}", fill='white')
        sheet.save(f'{SHEET}-{s // (C * C):02d}.jpg', quality=80)
