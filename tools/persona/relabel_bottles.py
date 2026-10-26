"""SKINOFAB's real wordmark on every foundation bottle in the store's photos.

The foundation's renders, packshots and the photos of women holding it were made with a stand-in wordmark (a
Trajan-like serif; on two AI photos a misspelt "SKINOFAS"). label_composite.py finds that print on each bottle, erases
it and sets the brand's own wordmark (brand/logo/skinofab-wordmark.svg) where it was, at its size and angle; this
file says where the bottles are in each photo:

- ('auto', roi, angle, kw): the bottle is in roi (shares of the width and height; None: the whole photo), turned
  angle degrees; label_composite.composite(relabel=True) finds the old print on it and wraps ours around the cylinder
- ('box', box, first): a print on a stick or a small bottle: its letters are found in box (x0, y0, x1, y1, px), first
  is a point at its first letter (which way it reads); label_composite.measure_print + swap_flat
- ('badge', box, cx, base1, base2, size): the origin badge under the Korean flag, cleared (box, on white) and set
  again as label_composite.ORIGIN_LINES, centred on cx, on the two baselines, Montserrat at size px
- ('boldrot', centre, angle, (w, h), text, cap): a small line printed at a slant (degrees clockwise), set again
  bold at cap px (label_fix.bold_line_rot)
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
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import label_composite as L
import label_fix

FOUNDATION = HERE.parents[1] / 'brand' / 'adaptive-peptide-foundation'
ORIGINALS = FOUNDATION / 'source' / 'renders'

RENDERS = {
    # legible / retype: the small PDRN line set again at the label's size (label_fix): printed as rendered, its D
    # closes into an O when the bottle is shown small, and it reads PORN
    '01-front.png': [('auto', None, 0, {}), ('legible',)],
    '02-three-quarter-left.png': [('auto', None, 0, {})],
    '03-three-quarter-right.png': [('auto', None, 0, {})],
    'composites/two-bottles.jpg': [('auto', (0.12, 0.04, 0.45, 0.96), 0, {}), ('auto', (0.56, 0.04, 0.88, 0.96), 0, {}),
                                   ('retype', (332, 1048, 392, 1075), 'PDRN'), ('retype', (893, 1048, 952, 1075), 'PDRN')],
    'composites/duo-square.jpg': [('auto', (0.0, 0.0, 0.5, 1.0), 0, {}), ('auto', (0.5, 0.0, 1.0, 1.0), 0, {}),
                                  ('retype', (332, 1061, 392, 1090), 'PDRN'), ('retype', (893, 1061, 952, 1090), 'PDRN')],
    'composites/label-detail.jpg': [('auto', None, 0, {'lit_max': 175})],   # a close-up: its highlight band is lighter
}
# not relabelled (no wordmark in view, or not on the site): 04-08 (profile, rear, top, base), 09-pump-detail (the
# pump only), composites/set-tiles.jpg (the old pink set). The three-quarter renders keep their PDRN line as
# rendered: it wraps around the turned cylinder (slanted, foreshortened), and they are only shown large

# the PDRN balm's photos (brand/pdrn-balm/source/<name>.jpg, 1024 px): an AI-drawn wordmark on each stick
BALM = {
    # retype: the AI-drawn "PDRN · VOLUFILINE" line set again, legible at a thumbnail's size (label_fix.retype_line)
    # the hero (NEXT's first photo: the listing cards show it 360 px wide): "PDRN" alone, bold and larger, where
    # "PDRN · VOLUFILINE" (14 px caps) read PORN at that size (review 6)
    'pack': [('box', (420, 330, 490, 680), (452, 340)), ('boldrot', (454, 805), 0, (156, 30), 'PDRN', 17)],
    'tall': [('box', (455, 520, 565, 1170), (510, 540)), ('retype', (402, 1303, 622, 1328), 'PDRN · VOLUFILINE')],
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

# the Adaptive Foundation Stick's photos (brand/foundation-stick/source/<name>.jpg, 1254 px, GPT Image 2 with the
# packshot as reference): the AI-drawn SKINOFAB on each tube, a box round it and a point on its first letter
# every stick reads from its brush end to its cream end, as the packshot does (duo-ends): 'first' / p0 at the brush
# end (stick review 6: the S sat at the cream end in six photos, at the brush end in the others)
STICK = {
    'pack': [('box', (420, 520, 500, 870), (460, 550)), ('box', (750, 520, 830, 870), (790, 550))],
    'single': [('box', (585, 480, 670, 840), (626, 510))],
    'tips': [('box', (360, 830, 445, 1215), (402, 860)), ('box', (790, 860, 875, 1230), (832, 890))],
    'hold-cheek': [('box', (240, 670, 360, 890), (283, 700))],
    'apply-cheek': [('box', (220, 630, 370, 780), (240, 760))],
    'blend': [('flat', (426, 694), (341, 797), 21)],              # dim, lit print: measured by hand
    'swatch': [('box', (930, 580, 1080, 890), (965, 865))],
    'temple': [('flat', (303, 540), (279, 691), 22)],
    'friends': [('box', (570, 805, 655, 1000), (612, 832))],
    'bag': [('box', (680, 500, 830, 725), (780, 528))],
    # (aged up with GPT Image 2, store audit 8 / stick review 4: its re-drawn print is letter-spaced, measured by hand)
    'hold-chin': [('flat', (372, 973), (386, 826), 21)],
    'panel': [('box', (700, 725, 800, 895), (742, 870))],
    'twist': [('box', (598, 480, 662, 772), (629, 752))],
    'dots': [('box', (395, 840, 440, 995), (417, 980))],
    'daylight': [('flat', (275, 810), (301, 946), 14)],
    'buff-jaw': [('flat', (510, 910), (405, 982), 16)],
    'duo-ends': [('flat', (545, 660), (755, 447), 34)],   # the band wide enough to clear the AI print's ends (stick review 4)
}

# file-name prefix -> (the reference copy's size, the bottles in it); the longest prefix whose aspect matches wins
SITE = {
    'KoreanColorChangingFoundation-Productimages_1_cee537ea-54c2-': ((1080, 1080), [('auto', (0.38, 0.23, 0.62, 0.87), 0, {}),
        ('badge', (846, 212, 1062, 284), 952, 243, 267, 21),       # its flag badge: "Based on Korean / Beauty Innovation"
        ('boldrot', (540.5, 832), 0, (80, 20), 'PDRN', 12)]),       # its 6 px PDRN line read PORN on a phone (review 4)
    # (the home hero's files are not relabelled here: hero_label.py draws the real label on its master, flat and at
    # the logo's own proportions; wrapping a second wordmark around its cylinder made the letters wobble)
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
    '2_221c6006-6944-4b6f-a085-220e11ef092d': ((1080, 1080), [('auto', (0.08, 0.33, 0.40, 0.86), -20, {}),
        ('boldrot', (316, 831), -18, (56, 20), 'PDRN', 11)]),       # its 6 px PDRN read PORN at the gallery's size (review 5)
    # the gallery photos' PDRN lines, 7-9 px tall in 1350, read PORN at the gallery's size on a computer (about 650 px
    # wide at 1440): set again bold along each label's slant (review 5)
    'ColorChangingFoundation-Productimagesphotos_412bfd2c-43db-4b': ((1350, 1350), [('box', (822, 520, 900, 730), (870, 540)),
        ('boldrot', (826.5, 783), 9, (44, 18), 'PDRN', 9.5)]),
    'ColorChangingFoundation-Productimagesphotos_1_87f31fb4-5811-': ((1080, 1080), [('box', (720, 330, 950, 425), (745, 405))]),
    '21_7a5d845a-8ab5-4163-b4ff-b8fd4b71f0c7': ((1350, 1350), [('auto', (0.05, 0.12, 0.34, 0.67), 15, {}),
        ('boldrot', (192.5, 765), 11, (52, 20), 'PDRN', 11.5)]),
    '22_ed20463f-1b63-4206-8734-81f1bfc33ec4': ((1350, 1350), [('auto', (0.07, 0.34, 0.32, 0.96), -6, {}),
        ('boldrot', (282.5, 1169), -7, (52, 20), 'PDRN', 11.5)]),
    '24_e2816f7f-0236-4d48-8794-a7b92c9b627d': ((1350, 1350), [('auto', (0.225, 0.385, 0.385, 0.83), -5, {}),
        ('boldrot', (426, 988), -4, (44, 18), 'PDRN', 10)]),
    # the comparison card's bottle: its PDRN line 5 px tall in 1080 read PORN even at full size (review 5)
    '8_87ca3242-b11c-40e2-beab-fb1aa34022a6': ((1080, 1080), [('boldrot', (622.5, 458), 0, (36, 16), 'PDRN', 7.5)]),
    '2_babe5169': ((1500, 1500), [('flat', (584.3, 203.6), (830.9, 105.3), 42)]),
    # the "Soft on fine lines" clip's poster (the swapped bottle, tilted in her hand): its small PDRN line, a few px
    # tall, was drawn as PORN; set again bold along the label's slant (review 4)
    'softer-lines-foundation-review-poster-720w-p': ((720, 1280), [('boldrot', (42.5, 1072.5), 31, (24, 9), 'PDRN', 5.5)]),
}


def relabel(im, ops, ref=None):
    """The photo with each bottle in ops relabelled. ref: the size the flat ops' px are in (default: the photo's)."""
    out = im.convert('RGB')
    W, H = out.size
    k = W / ref[0] if ref else 1.0
    for op in ops:
        if op[0] == 'badge':                                   # the origin badge's two lines under the flag, rewritten
            _, (x0, y0, x1, y1), cx, b1, b2, size = op
            out = out.copy(); d = ImageDraw.Draw(out)
            d.rectangle((x0 * k, y0 * k, x1 * k, y1 * k), fill=(255, 255, 255))
            for line, base in zip(L.ORIGIN_LINES, (b1, b2)):
                d.text((cx * k, base * k), line, font=L.sans(max(8, round(size * k)), 'Regular'), fill=(38, 38, 38), anchor='ms')
            continue
        if op[0] == 'legible':
            out = Image.fromarray(np.clip(label_fix.legible_pdrn(np.asarray(out).astype(np.float32)) + 0.5, 0, 255).astype(np.uint8))
            continue
        if op[0] == 'boldrot':                                 # a small line at a slant, set again bold (label_fix)
            _, (cx, cy), angle, (w, h), text, cap = op
            a = label_fix.bold_line_rot(np.asarray(out).astype(np.float32), (cx * k, cy * k), angle,
                                        (round(w * k), round(h * k)), text, cap * k, weight=760, track=0.2)
            out = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))
            continue
        if op[0] == 'retype':
            _, box, text = op
            a = label_fix.retype_line(np.asarray(out).astype(np.float32), [round(v * k) for v in box], text)
            out = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))
            continue
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
    return hashlib.md5(Path(L.__file__).read_bytes() + L.LOGO.read_bytes() + Path(__file__).read_bytes()
                       + Path(label_fix.__file__).read_bytes()).digest()


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
