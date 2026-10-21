"""Put the original transparency back on regenerated images.

The image model returns opaque pictures, so a transparent PNG/WebP cut-out (e.g. a model on a see-through
background laid over a section's grey panel) came back with a solid, usually black, background. For every variant
whose ORIGINAL has real transparency, this keeps the regenerated colours and re-applies the original alpha mask.

usage: python3 -I restore_alpha.py <groups.json> <original_export> <export_to_fix> [<extra_dir> ...]
<extra_dir>: folders of drop-in replacements (persona-img) named like the export's files; fixed the same way.
"""
import json, re, sys
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter

G = json.load(open(sys.argv[1]))
ORIG, FIX = Path(sys.argv[2]) / 'assets' / 'img', Path(sys.argv[3]) / 'assets' / 'img'
EXTRA = [Path(p) for p in sys.argv[4:]]
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)
brand = lambda m: 'SKINOFAB' if m.group(0).isupper() else ('Skinofab' if m.group(0)[0].isupper() else 'skinofab')

def alpha_of(p):
    try:
        im = Image.open(p)
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            a = im.convert('RGBA').getchannel('A')
            if a.getextrema()[0] < 250: return a
    except Exception: pass
    return None

fixed = 0
for g in G:
    for v in g['variants']:
        a = alpha_of(ORIG / v)
        if a is None: continue
        for target in [FIX / BRAND.sub(brand, v)] + [d / BRAND.sub(brand, v) for d in EXTRA]:
            if not target.exists() or target.is_symlink(): continue
            if target.samefile(ORIG / v) or target.read_bytes() == (ORIG / v).read_bytes(): continue   # untouched original
            with Image.open(target) as cur:
                rgba = cur.convert('RGB').convert('RGBA')
            # the regenerated subject sits a few pixels off the old cut-out edge and the model filled the background
            # dark, so shrink the mask slightly and soften it to drop the dark fringe
            k = max(3, (rgba.width // 300) | 1)
            base = a.resize(rgba.size, Image.LANCZOS)
            mask = base.filter(ImageFilter.MinFilter(k)).filter(ImageFilter.GaussianBlur(k / 3))
            # in a band along the cut-out edge, near-black pixels are the model's background, not the subject
            band_w = max(5, (rgba.width // 70) | 1)
            outer = base.filter(ImageFilter.MaxFilter(band_w)); inner = base.filter(ImageFilter.MinFilter(band_w))
            band = ImageChops.subtract(outer, inner).point(lambda v: 255 if v > 8 else 0)
            luma = rgba.convert('L')
            keep = luma.point(lambda v: 0 if v < 28 else (255 if v > 70 else int((v - 28) * 255 / 42)))
            keyed = ImageChops.multiply(mask, keep)
            mask = Image.composite(keyed, mask, band).filter(ImageFilter.GaussianBlur(1))
            rgba.putalpha(mask)
            fmt = 'WEBP' if target.suffix.lower() == '.webp' else 'PNG'
            tmp = target.with_name(target.name + '.tmp')
            rgba.save(tmp, fmt, **({'quality': 88, 'method': 5} if fmt == 'WEBP' else {'optimize': True}))
            tmp.replace(target); fixed += 1
print(f'{fixed} files got their transparency back')
