"""SKINOFAB's real wordmark on every foundation bottle in the store's photos.

The foundation's renders, packshots and the photos of women holding it were made with a stand-in wordmark (a
Trajan-like serif; on two AI photos a misspelt "SKINOFAS"). label_composite.py finds that print on each bottle, erases
it and sets the brand's own wordmark (brand/logo/skinofab-wordmark.svg) where it was, at its size and angle; this
file says where the bottles are in each photo:

- ('auto', roi, angle, kw): the bottle is in roi (shares of the width and height; None: the whole photo), turned
  angle degrees; label_composite.composite(relabel=True) finds the old print on it and wraps ours around the cylinder
- ('box', box, first): a print on a stick or a small bottle: its letters are found in box (x0, y0, x1, y1, px), first
  is a point at its first letter (which way it reads); label_composite.measure_print + swap_flat
- ('flat', p0, p1, h): a print too small, turned or cut out for that (a photo on pure black, a bottle seen end-on):
  the old wordmark runs from p0 to p1 (its first and last letters' outer ends), h px tall, in the reference size's px;
  label_composite.swap_flat sets ours flat on the same line

renders()  the product-sheet renders and composites in brand/adaptive-peptide-foundation/, in place: the originals are
           kept in brand/adaptive-peptide-foundation/source/renders/ and every run starts from them
site()     every page's copy of the foundation photos (apply_persona.relabel_bottles): per photo, its largest copy at
           the reference size is relabelled and every other width of it is that result resized, so the srcset agrees

usage: python3 -I tools/persona/relabel_bottles.py renders
       python3 -I tools/persona/relabel_bottles.py sheet <export_dir> <out_dir>   (before/after crops of every photo)
"""
import hashlib, re, shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import label_composite as L

FOUNDATION = HERE.parents[1] / 'brand' / 'adaptive-peptide-foundation'
ORIGINALS = FOUNDATION / 'source' / 'renders'

RENDERS = {
    '01-front.png': [('auto', None, 0, {})],
    '02-three-quarter-left.png': [('auto', None, 0, {})],
    '03-three-quarter-right.png': [('auto', None, 0, {})],
    'composites/two-bottles.jpg': [('auto', (0.12, 0.04, 0.45, 0.96), 0, {}), ('auto', (0.56, 0.04, 0.88, 0.96), 0, {})],
    'composites/duo-square.jpg': [('auto', (0.0, 0.0, 0.5, 1.0), 0, {}), ('auto', (0.5, 0.0, 1.0, 1.0), 0, {})],
    'composites/label-detail.jpg': [('auto', None, 0, {'lit_max': 175})],   # a close-up: its highlight band is lighter
}
# not relabelled (no wordmark in view, or not on the site): 04-08 (profile, rear, top, base), 09-pump-detail (the
# pump only), composites/set-tiles.jpg (the old pink set)

# the PDRN balm's photos (brand/pdrn-balm/source/<name>.jpg, 1024 px): an AI-drawn wordmark on each stick
BALM = {
    'pack': [('box', (420, 330, 490, 680), (452, 340))],
    'tall': [('box', (455, 520, 565, 1170), (510, 540))],
    'hold-cheek': [('box', (290, 400, 360, 565), (310, 550))],
    'panel': [('box', (850, 440, 935, 585), (872, 450))],
    'swatch': [('box', (660, 50, 980, 320), (690, 290))],
    'apply-eye': [('box', (600, 470, 690, 660), (625, 485))],
    'hold-chin': [('box', (185, 505, 245, 705), (205, 525))],
    'friends': [('box', (835, 450, 895, 605), (862, 465))],
    'apply-lips': [('box', (280, 560, 420, 680), (300, 655))],
    'bag': [('box', (480, 395, 565, 600), (499, 410))],
    'apply-brows': [('box', (190, 330, 420, 450), (215, 425))],     # these four the page takes straight from source/
    'apply-smile': [('box', (270, 590, 420, 810), (290, 790))],     # (apply_persona.twin_context)
    'mirror': [('box', (415, 395, 485, 530), (430, 515))],
    'temple': [('box', (150, 330, 285, 485), (170, 470))],
}

# file-name prefix -> (the reference copy's size, the bottles in it); the longest prefix whose aspect matches wins
SITE = {
    'KoreanColorChangingFoundation-Productimages_1_cee537ea-54c2-': ((1080, 1080), [('auto', (0.38, 0.23, 0.62, 0.87), 0, {})]),
    'skinofab-hero-phone': ((2880, 1228), [('auto', (0.655, 0.27, 0.75, 0.70), 7, {})]),
    'skinofab-hero-desktop': ((4096, 1747), [('auto', (0.655, 0.27, 0.75, 0.70), 6, {})]),
    'ColorChangingFoundation-Productimage_31cddf53-0315-41bf-bfe5': ((1080, 1080), [('auto', (0.46, 0.21, 0.68, 0.79), 0, {})]),
    'skinofab-color-changing-foundation-model-mobile': ((660, 1182), [('flat', (153.6, 528.4), (161.4, 611.6), 15)]),
    'skinofab-color-changing-foundation-model': ((1460, 1825), [('flat', (968, 1252), (968, 1153), 19),
                                                                ('flat', (826, 1757), (826, 1661), 20)]),
    'skinofab-foundation-mega-pack-bundle': ((710, 1069), [('flat', (105.3, 604.8), (102.3, 695.0), 14),
                                                           ('flat', (275, 560), (275, 646), 15),
                                                           ('flat', (393, 487), (393, 574), 15),
                                                           ('flat', (598.5, 629), (598.5, 715), 16)]),
    'skinofab-korean-formulas-foundation-application-mobile': ((940, 1662), [('flat', (718.6, 885.2), (778.1, 991.1), 20)]),
    'skinofab-korean-formulas-foundation-application': ((2000, 858), [('flat', (815, 364), (893.8, 505.7), 25)]),
    '2_221c6006-6944-4b6f-a085-220e11ef092d': ((1080, 1080), [('auto', (0.08, 0.33, 0.40, 0.86), -20, {})]),
    'ColorChangingFoundation-Productimagesphotos_412bfd2c-43db-4b': ((1350, 1350), [('box', (822, 520, 900, 730), (870, 540))]),
    'ColorChangingFoundation-Productimagesphotos_1_87f31fb4-5811-': ((1080, 1080), [('box', (720, 330, 950, 425), (745, 405))]),
    '21_7a5d845a-8ab5-4163-b4ff-b8fd4b71f0c7': ((1350, 1350), [('auto', (0.05, 0.12, 0.34, 0.67), 15, {})]),
    '22_ed20463f-1b63-4206-8734-81f1bfc33ec4': ((1350, 1350), [('auto', (0.07, 0.34, 0.32, 0.96), -6, {})]),
    '24_e2816f7f-0236-4d48-8794-a7b92c9b627d': ((1350, 1350), [('auto', (0.225, 0.385, 0.385, 0.83), -5, {})]),
    '2_babe5169': ((1500, 1500), [('flat', (584.3, 203.6), (830.9, 105.3), 42)]),
}


def relabel(im, ops, ref=None):
    """The photo with each bottle in ops relabelled. ref: the size the flat ops' px are in (default: the photo's)."""
    out = im.convert('RGB')
    W, H = out.size
    k = W / ref[0] if ref else 1.0
    for op in ops:
        if op[0] == 'box':
            _, box, first = op
            p0, p1, h = L.measure_print(out, [v * k for v in box], (first[0] * k, first[1] * k))
            out = L.swap_flat(out, p0, p1, h)
            continue
        if op[0] == 'flat':
            _, p0, p1, h = op
            out = L.swap_flat(out, (p0[0] * k, p0[1] * k), (p1[0] * k, p1[1] * k), h * k)
            continue
        _, roi, angle, kw = op
        r = None if roi is None else tuple(int(v) for v in (roi[0] * W, roi[1] * H, roi[2] * W, roi[3] * H))
        out = L.composite(out, 'foundation', r, angle=angle, relabel=True, **kw)
    return out


def salt():
    """The code and the logo the results depend on: a change to either recomputes them."""
    return hashlib.md5(Path(L.__file__).read_bytes() + L.LOGO.read_bytes() + Path(__file__).read_bytes()).digest()


def save(im, path, like=None):
    """Saved in the format its name says; like: a photo whose transparency it keeps (a PNG cut-out)."""
    path = Path(path)
    if like is not None and like.mode in ('RGBA', 'LA', 'P') and path.suffix.lower() == '.png':
        im = im.convert('RGBA'); im.putalpha(like.convert('RGBA').getchannel('A').resize(im.size, Image.LANCZOS))
    ext = path.suffix.lower()
    opts = ({'quality': 90, 'optimize': True, 'progressive': True} if ext in ('.jpg', '.jpeg')
            else {'quality': 88, 'method': 6} if ext == '.webp' else {'optimize': True})
    im.save(path, **opts)


def renders():
    """The renders and composites relabelled in place, from their originals in source/renders/ (moved there on the
    first run)."""
    for name, ops in RENDERS.items():
        dst, src = FOUNDATION / name, ORIGINALS / name
        if not src.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(dst, src)
        im = Image.open(src)
        save(relabel(im, ops), dst, like=im)
        print('relabelled', name, im.size)


def match(name, size):
    """The SITE entry for a file name and size: the longest prefix whose reference aspect is the file's."""
    hits = [p for p in SITE if name.startswith(p) and abs(SITE[p][0][0] / SITE[p][0][1] - size[0] / size[1]) < 0.015]
    return max(hits, key=len) if hits else None


def site(img_dir, names, cache):
    """Relabel every copy in names (file names in img_dir) of a SITE photo. Returns {old name: new name}; the new
    files are written next to the old ones as <stem>-l<hash><ext>. Results are cached by input in cache."""
    img_dir, cache = Path(img_dir), Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    groups = {}
    for n in sorted(names):
        p = img_dir / n
        if not p.is_file() or re.search(r'-l[0-9a-f]{6}$', p.stem): continue
        try: size = Image.open(p).size
        except Exception: continue
        key = match(n, size)
        if key: groups.setdefault(key, []).append((n, size))
    s, renames = salt(), {}
    for key, files in groups.items():
        ref, ops = SITE[key]
        # the reference copy: the one at the reference size, else the largest
        master = next((f for f in files if f[1] == ref), max(files, key=lambda f: f[1][0]))
        mdata = (img_dir / master[0]).read_bytes()
        mkey = cache / f'{hashlib.md5(s + mdata + repr(ops).encode()).hexdigest()}.png'
        if not mkey.exists():
            relabel(Image.open(img_dir / master[0]), ops, ref).save(mkey)
        done = Image.open(mkey).convert('RGB')
        morig = Image.open(img_dir / master[0]).convert('RGB')
        for n, size in files:
            src = img_dir / n
            im = Image.open(src)
            if src.read_bytes() == mdata:
                out = done
            else:
                # another width of the same photo: the relabelled reference resized, if it is the same picture (a
                # thumbnail always: too small to find a print on, and its processing differs a little at that size)
                same = size[0] < 300 or np.abs(np.asarray(morig.resize(size, Image.LANCZOS)).astype(np.float32)
                                               - np.asarray(im.convert('RGB')).astype(np.float32)).mean() < 6
                if same:
                    out = done.resize(size, Image.LANCZOS)
                else:
                    print('relabel: a different crop, relabelled on its own:', n, file=sys.stderr)
                    out = relabel(im, ops, ref)
            stem = re.sub(r'-[a-z]?[0-9a-f]{6}$', '', src.stem)
            tmp = img_dir / f'{stem}-relabel{src.suffix}'
            save(out, tmp, like=im)
            new = f"{stem}-l{hashlib.md5(tmp.read_bytes()).hexdigest()[:6]}{src.suffix}"
            tmp.replace(img_dir / new)
            renames[n] = new
    return renames


def sheet(export, out):
    """Before/after crops of every SITE photo's reference copy in an export (out/<prefix>.jpg), for review."""
    img_dir, out = Path(export) / 'assets' / 'img', Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for key, (ref, ops) in SITE.items():
        files = [p for p in img_dir.glob(key + '*') if match(p.name, Image.open(p).size) == key]
        if not files: print('no copy of', key); continue
        p = next((f for f in files if Image.open(f).size == ref), max(files, key=lambda f: Image.open(f).size[0]))
        a = Image.open(p).convert('RGB'); b = relabel(a, ops, ref)
        c = Image.new('RGB', (a.width * 2 + 8, a.height), (255, 0, 255)); c.paste(a, (0, 0)); c.paste(b, (a.width + 8, 0))
        c.thumbnail((1800, 1800)); c.save(out / f'{key[:40]}.jpg', quality=86)
        print(key[:50], p.name)


if __name__ == '__main__':
    if sys.argv[1:2] == ['renders']: renders()
    elif sys.argv[1:2] == ['sheet']: sheet(sys.argv[2], sys.argv[3])
    else: sys.exit(__doc__)
