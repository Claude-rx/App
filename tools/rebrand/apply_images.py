"""Write regenerated images back into an export, replacing every width variant of each source image.

usage: python3 -I apply_images.py <groups.json> <gen_dir> <export_dir>
For each <gen_dir>/<n>.png: crop to the original master's aspect ratio (centre), then for every variant file of
group n resize to that variant's exact size and save in its format under its (rebranded) name, so no reference in
the HTML/CSS changes. Files are written to a temp name and renamed over the old one (hard links stay untouched).
"""
import json, os, re, sys
from pathlib import Path
from PIL import Image

GROUPS, GEN, EXPORT = json.load(open(sys.argv[1])), Path(sys.argv[2]), Path(sys.argv[3])
IMG = EXPORT / 'assets' / 'img'
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)
brand = lambda m: 'SKINOFAB' if m.group(0).isupper() else ('Skinofab' if m.group(0)[0].isupper() else 'skinofab')

def fit(im, w, h):
    r, R = im.width / im.height, w / h
    if abs(r - R) > 0.005:
        if r > R: nw = round(im.height * R); im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
        else: nh = round(im.width / R); im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)

done = files = 0
for g in GROUPS:
    src = GEN / f"{g['n']}.png"
    if not src.exists() or src.stat().st_size < 1000: continue
    new = Image.open(src).convert('RGBA')
    for v in g['variants']:
        f = IMG / BRAND.sub(brand, v)
        if not f.exists(): continue
        with Image.open(f) as old: fmt, size, mode = old.format, old.size, old.mode
        out = fit(new, *size)
        tmp = f.with_name(f.name + '.tmp')
        if fmt == 'JPEG': out.convert('RGB').save(tmp, 'JPEG', quality=88, optimize=True, progressive=True)
        elif fmt == 'WEBP': out.save(tmp, 'WEBP', quality=88, method=5)
        elif fmt == 'PNG': (out if 'A' in mode or mode == 'P' else out.convert('RGB')).save(tmp, 'PNG', optimize=True)
        elif fmt == 'AVIF': out.save(tmp, 'AVIF', quality=80)
        else: continue
        os.replace(tmp, f); files += 1
    done += 1
print(f'applied {done} generated images to {files} files')
