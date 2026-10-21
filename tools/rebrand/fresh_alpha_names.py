"""Give alpha-restored images a fresh, content-hashed file name and rewrite every reference to it.

NEXT's CDN caches theme assets by file name, so a re-uploaded image under its old name keeps serving the old copy.
Run after restore_alpha.py and apply_persona.py, on the export the theme is built from.

usage: python3 -I fresh_alpha_names.py <groups.json> <original_export> <export_dir> <out_renames.json>
"""
import hashlib, json, os, re, sys
from pathlib import Path
from PIL import Image

G = json.load(open(sys.argv[1]))
ORIG, EXP = Path(sys.argv[2]) / 'assets' / 'img', Path(sys.argv[3])
IMG = EXP / 'assets' / 'img'
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)
brand = lambda m: 'SKINOFAB' if m.group(0).isupper() else ('Skinofab' if m.group(0)[0].isupper() else 'skinofab')
ren = {}
for g in G:
    for v in g['variants']:
        try:
            o = Image.open(ORIG / v)
            if not (o.mode in ('RGBA', 'LA', 'P') and o.convert('RGBA').getchannel('A').getextrema()[0] < 250): continue
        except Exception: continue
        t = IMG / BRAND.sub(brand, v)
        if not t.exists() or t.read_bytes() == (ORIG / v).read_bytes(): continue
        stem, ext = os.path.splitext(t.name)
        new = re.sub(r'-[0-9a-f]{6}$', '', stem) + '-a' + hashlib.md5(t.read_bytes()).hexdigest()[:6] + ext
        if not (IMG / new).exists(): os.link(t, IMG / new)
        ren[t.name] = new
if ren:
    rx = re.compile('|'.join(re.escape(k) for k in sorted(ren, key=len, reverse=True)))
    for p in EXP.rglob('*'):
        if p.is_file() and p.suffix in ('.html', '.css', '.js', '.json'):
            t = p.read_text(encoding='utf-8', errors='surrogateescape'); n = rx.sub(lambda m: ren[m.group(0)], t)
            if n != t: p.write_text(n, encoding='utf-8', errors='surrogateescape')
json.dump(ren, open(sys.argv[4], 'w'), indent=1)
print(len(ren), 'alpha files renamed')
