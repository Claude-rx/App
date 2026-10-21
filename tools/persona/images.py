"""Turn generated persona images into drop-in replacements for every width variant of their slot.

usage: python3 -I images.py <persona-jobs.json> <groups.json> <gen_dir> <export_dir> <out_dir>
For each job with a slot (n): <gen_dir>/<key>.png is (optionally) rotated, centre-cropped to the slot's aspect
and resized to each variant's exact size, then saved in the variant's format under its (rebranded) file name in
<out_dir>. apply_persona.py copies <out_dir> over the export. Jobs without a slot (bundle packshots) are skipped.

fit: "pad-left" keeps the whole render and extends its background leftwards (the homepage hero).
rotate: the homepage "two bases" panel shows its image turned 90 degrees clockwise with CSS, so the file stores
the scene turned 90 degrees counter-clockwise.
"""
import json, re, sys
from pathlib import Path
from PIL import Image

JOBS, GROUPS = json.load(open(sys.argv[1])), {g['n']: g for g in json.load(open(sys.argv[2]))}
GEN, EXPORT, OUT = Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
OUT.mkdir(parents=True, exist_ok=True)
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)
brand = lambda m: 'SKINOFAB' if m.group(0).isupper() else ('Skinofab' if m.group(0)[0].isupper() else 'skinofab')

def pad_left(im, w, h):
    """Scale to the slot's height and extend the plain studio background to the left (headline space), so a
    narrower render keeps the whole subject instead of losing the top of the face to a crop."""
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    if im.width >= w: return fit(im, w, h)
    canvas = Image.new(im.mode, (w, h))
    edge = im.crop((0, 0, max(4, im.width // 40), h)).resize((1, h), Image.LANCZOS)   # per-row background colour
    canvas.paste(edge.resize((w - im.width + 2, h)), (0, 0))
    canvas.paste(im, (w - im.width, 0))
    return canvas

def fit(im, w, h):
    r, R = im.width / im.height, w / h
    if r > R: nw = round(im.height * R); im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    elif r < R: nh = round(im.width / R); im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)

written = 0
for job in JOBS:
    if job.get('n') is None: continue
    src = GEN / f"{job['key']}.png"
    if not src.exists(): print('missing', src.name); continue
    im = Image.open(src)
    im = im.convert('RGBA') if 'A' in im.getbands() else im.convert('RGB')   # cut-outs keep their transparency
    if job.get('rotate'): im = im.rotate(90, expand=True)
    for v in GROUPS[job['n']]['variants']:
        name = BRAND.sub(brand, v)
        target = EXPORT / 'assets' / 'img' / name
        if not target.exists(): continue
        with Image.open(target) as old: fmt, size = old.format, old.size
        out = (pad_left if job.get('fit') == 'pad-left' else fit)(im, *size); dst = OUT / name
        if fmt == 'JPEG': out.convert('RGB').save(dst, 'JPEG', quality=88, optimize=True, progressive=True)
        elif fmt == 'PNG': out.save(dst, 'PNG', optimize=True)
        elif fmt == 'WEBP': out.save(dst, 'WEBP', quality=88, method=5)
        elif fmt == 'AVIF': out.save(dst, 'AVIF', quality=80)
        else: continue
        written += 1
print(f'{written} variant files written to {OUT}')
