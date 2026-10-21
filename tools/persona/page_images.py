"""Images shown on given export pages, resolved to their image group and the file to edit.

usage: python3 -I page_images.py <rel4_export> <rel3_export> <groups.json> <persona_img_dir> <alpha_renames.json> <out.json> <page> [<page> ...]
For every image a page references (src, srcset, data-src, inline style url()), finds:
- rel4: the file name in the persona export (what the page shows; on the theme CDN under the same name)
- rel3: its name before the persona layer (the name images.py / apply_persona.py write replacements under)
- n: its group in groups.json (all width variants of one picture)
One entry per group, with the largest shown file as the edit source.
"""
import hashlib, json, os, re, sys
from pathlib import Path
from PIL import Image

REL4, REL3, GROUPS, PIMG, ALPHA, OUT = (Path(p) for p in sys.argv[1:7])
PAGES = sys.argv[7:]
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)
brand = lambda m: 'SKINOFAB' if m.group(0).isupper() else ('Skinofab' if m.group(0)[0].isupper() else 'skinofab')

# rel4 name -> rel3 name: persona replacements (-p<md5>) and fresh alpha names (-a<hash>)
to_rel3 = {}
for f in PIMG.iterdir():
    stem, ext = os.path.splitext(f.name)
    to_rel3[re.sub(r'-[0-9a-f]{6}$', '', stem) + '-p' + hashlib.md5(f.read_bytes()).hexdigest()[:6] + ext] = f.name
alpha = json.loads(ALPHA.read_text())
inv_alpha = {v: k for k, v in alpha.items()}
by_variant = {}
for g in json.loads(GROUPS.read_text()):
    for v in g['variants']: by_variant[BRAND.sub(brand, v)] = g['n']

out, seen = [], {}
for page in PAGES:
    t = (REL4 / page).read_text(errors='replace')
    names = set(re.findall(r'assets/img/([^"\'\s,)?&\\]+\.(?:jpe?g|png|webp|avif|gif))', t, re.I))
    for name in sorted(names):
        rel3 = to_rel3.get(name) or inv_alpha.get(name) or name
        rel3 = to_rel3.get(rel3, rel3)
        n = by_variant.get(rel3)
        if n is None or not (REL4 / 'assets/img' / name).exists(): continue
        with Image.open(REL4 / 'assets/img' / name) as im: w, h = im.size
        cur = seen.get(n)
        if cur is None:
            seen[n] = {'n': n, 'rel4': name, 'rel3': rel3, 'w': w, 'h': h, 'pages': [page]}
            out.append(seen[n])
        else:
            if page not in cur['pages']: cur['pages'].append(page)
            if w * h > cur['w'] * cur['h']: cur.update(rel4=name, rel3=rel3, w=w, h=h)
json.dump(out, open(OUT, 'w'), indent=1)
print(len(out), 'image groups on', PAGES)
