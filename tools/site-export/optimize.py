"""Shrink oversized images in an export in place (same file name and format, so no references change).

usage: python3 -I optimize.py <export_dir> [max_width=2000]
- anything wider than max_width is downscaled (Lanczos)
- JPEG re-encoded at q=85 progressive, PNG re-saved optimized, WebP at q=85
- opaque PNG photos over 500 KB become .jpg (references in every .html/.css/.js/.json are rewritten)
- a file is only replaced when the result is smaller
"""
import os, sys
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

ROOT = sys.argv[1]
MAXW = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
MIN_BYTES = 300_000

def opaque(im):
    if im.mode in ('RGB', 'L'): return True
    if im.mode in ('RGBA', 'LA') or 'transparency' in im.info:
        return im.convert('RGBA').getchannel('A').getextrema()[0] == 255
    return im.mode == 'P' and 'transparency' not in im.info

def shrink(path):
    """returns (bytes saved, renamed-from basename, renamed-to basename)"""
    before = os.path.getsize(path)
    try:
        im = Image.open(path)
        fmt = im.format
        if fmt == 'PNG' and before > 500_000 and opaque(im) and path.lower().endswith('.png'):
            if im.width > MAXW: im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
            new = path[:-4] + '.jpg'
            im.convert('RGB').save(new, 'JPEG', quality=86, optimize=True, progressive=True)
            os.remove(path)
            return before - os.path.getsize(new), os.path.basename(path), os.path.basename(new)
        if fmt not in ('JPEG', 'PNG', 'WEBP') or getattr(im, 'is_animated', False): return 0, None, None
        if im.width > MAXW:
            im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
        tmp = path + '.opt'
        if fmt == 'JPEG':
            im.convert('RGB').save(tmp, 'JPEG', quality=85, optimize=True, progressive=True)
        elif fmt == 'PNG':
            im.save(tmp, 'PNG', optimize=True)
        else:
            im.save(tmp, 'WEBP', quality=85, method=5)
        after = os.path.getsize(tmp)
        if after < before:
            os.replace(tmp, path); return before - after, None, None
        os.remove(tmp)
    except Exception as e:
        print('skip', path, e)
    return 0, None, None

SIGS = ((b'\xff\xd8\xff', '.jpg'), (b'\x89PNG', '.png'), (b'GIF8', '.gif'))

def true_ext(path):
    head = open(path, 'rb').read(12)
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP': return '.webp'
    return next((e for sig, e in SIGS if head.startswith(sig)), None)

# 1) files whose content doesn't match their extension (CDNs negotiate formats): rename to the real one
mislabeled = {}
for d, _, fs in os.walk(os.path.join(ROOT, 'assets', 'img')):
    for f in fs:
        p = os.path.join(d, f); stem, ext = os.path.splitext(f)
        real = true_ext(p)
        if real and ext.lower() not in (real, '.jpeg' if real == '.jpg' else real):
            new = stem + real
            os.replace(p, os.path.join(d, new)); mislabeled[f] = new

files = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(ROOT, 'assets', 'img')) for f in fs
         if os.path.getsize(os.path.join(d, f)) > MIN_BYTES]
with ProcessPoolExecutor() as ex:
    results = list(ex.map(shrink, files, chunksize=4))
saved = sum(r[0] for r in results)
renames = {a: b for _, a, b in results if a}
for a, b in mislabeled.items():  # chain: a mislabeled file may also have been converted
    renames[a] = renames.get(b, b)
if renames:
    import re
    pat = re.compile('|'.join(re.escape(a) for a in sorted(renames, key=len, reverse=True)))
    for d, _, fs in os.walk(ROOT):
        for f in fs:
            if f.endswith(('.html', '.css', '.js', '.json')):
                p = os.path.join(d, f)
                txt = open(p, encoding='utf-8', errors='surrogateescape').read()
                new = pat.sub(lambda m: renames[m.group(0)], txt)
                if new != txt: open(p, 'w', encoding='utf-8', errors='surrogateescape').write(new)
print(f'optimized {len(files)} images ({len(renames) - len(mislabeled)} PNG->JPEG, {len(mislabeled)} mislabeled fixed), saved {saved / 1e6:.0f} MB')
