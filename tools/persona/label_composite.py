"""Print SKINOFAB's real label on a blank black bottle or box in a photo (the photos are generated with the packaging
blank, so the logo is ours to the pixel, not an AI's guess at it).

usage: python3 -I label_composite.py <in.jpg> <out.jpg> <product> [--roi x0,y0,x1,y1] [--box x0,y0,x1,y1] [--blur px] [--debug <dir>]
  product   serum (EGF + NAD+ Firming Serum); the label's lines are in LABELS
  --roi     where to look for the bottle (default: the whole image); the bottle is the largest near-black area in it
  --box     the carton's front face, if the photo shows one: the logo goes on it, centred, with the product name
  --blur    extra softening for a bottle that is out of focus (px)

The bottle's body is found from the near-black pixels: the rows where it is widest are the body, their centre line
(with its tilt) the label's axis. The label is the foundation bottle's layout: the wordmark (brand/adaptive-peptide-
foundation/00-logo.png) set vertically, reading top to bottom, then the product lines in Montserrat. It is wrapped
around the cylinder, shaded by the bottle's own light (brighter on the highlight side, fading at the edges), softened
to the photo's sharpness and clipped to the bottle's pixels, so fingers in front of it stay in front.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
LOGO = HERE.parents[1] / 'brand' / 'adaptive-peptide-foundation' / '00-logo.png'
FONT = HERE / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
LABELS = {
    'serum': {'lines': [('EGF + NAD+', 'Medium'), ('FIRMING SERUM', 'Medium')], 'sub': 'COLLAGEN', 'size': '30 mL / 1.01 fl oz'},
}


def sans(size, weight='Medium'):
    f = ImageFont.truetype(str(FONT), size); f.set_variation_by_name(weight); return f


def logo_alpha():
    """The wordmark as an alpha mask (black letters on the file's flat grey)."""
    a = np.asarray(Image.open(LOGO).convert('L')).astype(np.float32)
    bg = np.median(a[:10]); alpha = np.clip((bg - a) / max(bg - a.min(), 1) * 1.15, 0, 1)
    m = Image.fromarray((alpha * 255).astype(np.uint8))
    return m.crop(m.point(lambda v: 255 if v > 40 else 0).getbbox())


def label_art(product, w):
    """The bottle label as a white-on-transparent mask for a body w px wide (sizes as seen at the bottle's centre);
    drawn 4x and returned at 4x (the caller scales it to the photo)."""
    spec = LABELS[product]
    S = 4
    logo = logo_alpha().rotate(-90, expand=True)                 # reads top to bottom, S at the top
    lw = int(w * S * 0.27)
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    A = int(w * S * np.pi / 2)                                   # the art spans the visible half of the cylinder
    gap, line = int(w * S * 0.09), int(w * S * 0.058)
    H = logo.height + gap + int(line * 1.4) * len(spec['lines']) + int(line * 2.1) * 2 + line
    m = Image.new('L', (A, H), 0)
    m.paste(logo, ((A - lw) // 2, 0))
    d = ImageDraw.Draw(m)
    y = logo.height + gap
    def spaced(text, size, weight, y, track=0.16):
        f = sans(size, weight)
        widths = [d.textlength(ch, font=f) for ch in text]
        total = sum(widths) + track * size * (len(text) - 1)
        x = (A - total) / 2
        for ch, cw in zip(text, widths):
            d.text((x, y), ch, font=f, fill=255, anchor='ls'); x += cw + track * size
    for text, weight in spec['lines']:
        y += int(line * 1.4); spaced(text, line, weight, y)
    y += int(line * 2.1); spaced(spec['sub'], int(line * 0.8), 'Medium', y)
    y += int(line * 2.1); spaced(spec['size'], int(line * 0.8), 'Medium', y, 0.08)
    return m, H


def body_of(img, roi):
    """The bottle's body in roi: (mask of the bottle's dark pixels, centre x per row fit, top, bottom, width, angle)."""
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    x0, y0, x1, y1 = roi
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    sat = a.max(2) - a.min(2)
    dark = (lum < 70) & (sat < 40)
    dark[:y0] = False; dark[y1:] = False; dark[:, :x0] = False; dark[:, x1:] = False
    lab, n = ndimage.label(ndimage.binary_opening(dark, iterations=2))
    if not n: raise SystemExit('no dark bottle in the roi')
    core = lab == (np.argmax(ndimage.sum(dark, lab, range(1, n + 1))) + 1)
    core = ndimage.binary_fill_holes(ndimage.binary_closing(core, iterations=3))
    # the bottle is everything between its dark edges on each row (its highlight band is lighter than the core),
    # except skin: fingers in front of it stay in front
    rows = np.nonzero(core.any(1))[0]
    big = np.zeros_like(core)
    for r in rows:
        xs = np.nonzero(core[r])[0]; big[r, xs.min():xs.max() + 1] = True
    skin = (sat > 38) | (lum > 125)
    big &= ~ndimage.binary_dilation(skin, iterations=1)
    widths = np.array([np.ptp(np.nonzero(core[r])[0]) + 1 for r in rows])
    wmax = np.percentile(widths, 90)
    body_rows = rows[widths > wmax * 0.86]
    top, bottom = body_rows.min(), body_rows.max()
    cs = np.array([(np.nonzero(core[r])[0].min() + np.nonzero(core[r])[0].max()) / 2 for r in body_rows])
    k, c = np.polyfit(body_rows, cs, 1)                         # centre line x = k*y + c (the bottle's tilt)
    return big, (k, c), top, bottom, wmax


def composite(img, product, roi=None, box=None, debug=None, blur=0.0):
    img = img.convert('RGB')
    W, H = img.size
    roi = roi or (0, 0, W, H)
    mask, (slope, c), top, bottom, bw = body_of(img, roi)
    a = np.asarray(img).astype(np.float32)
    body_h = bottom - top
    cut = bottom >= min(roi[3], H) - 3                           # the frame cuts the bottle: its body is longer
    if cut: body_h = max(body_h, bw * 1.65); bottom = top + body_h
    art, ah = label_art(product, bw)                             # at 4x
    lab_h = ah / 4
    y_start = top + body_h * 0.14
    if y_start + lab_h > bottom - body_h * 0.05:                 # a short body: shrink the label to fit
        f = (bottom - body_h * 0.05 - y_start) / lab_h
        art = art.resize((int(art.width * f), int(art.height * f)), Image.LANCZOS); lab_h *= f
    n_rows = max(1, int(round(lab_h)))
    art = art.resize((max(2, art.width // 4), n_rows), Image.LANCZOS)   # 1 art px = 1 photo px at the centre
    art_a = np.asarray(art).astype(np.float32) / 255
    out = a.copy()
    r = bw / 2
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    ink = np.zeros((H, W), np.float32)
    # each photo row of the label: its art row, wrapped across the cylinder (x = centre + r sin theta)
    for k in range(n_rows):
        y = int(y_start) + k
        if y < 0 or y >= H: continue
        row = art_a[k]
        cx = slope * y + c
        xs = np.arange(int(cx - r), int(cx + r) + 1)
        xs = xs[(xs >= 0) & (xs < W)]
        s_ = np.clip((xs - cx) / r, -1, 1)
        theta = np.arcsin(s_)                                    # where on the cylinder this pixel looks
        u = (theta / (np.pi / 2) * 0.5 + 0.5) * (art.width - 1)
        u0 = np.floor(u).astype(int); f = u - u0; u1 = np.minimum(u0 + 1, art.width - 1)
        val = row[u0] * (1 - f) + row[u1] * f
        ink[y, xs] = val * np.cos(theta) ** 0.6                  # print fades toward the edges
    ink = ndimage.gaussian_filter(ink, 0.45 * max(1, W / 1024) + blur)    # blur: an out-of-focus bottle
    ink *= mask                                                  # only on the bottle (fingers stay in front)
    # the ink catches the bottle's own light: brighter where the black is lighter (the highlight side)
    local = ndimage.uniform_filter(lum, int(max(5, bw * 0.15)))
    lift = np.clip((local - 10) / 50, 0, 1)
    ink_col = 222 + 26 * lift
    for ch in range(3):
        out[..., ch] = out[..., ch] * (1 - ink) + ink_col * ink
    if box:
        out = carton(out, product, box)
    res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    if debug:
        Path(debug).mkdir(parents=True, exist_ok=True)
        Image.fromarray((mask * 255).astype(np.uint8)).save(Path(debug) / 'mask.png')
    return res


def carton(a, product, box):
    """The logo and product name on the carton's front face (box = x0, y0, x1, y1), as printed white ink."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    spec = LABELS[product]
    S = 4
    m = Image.new('L', (w * S, h * S), 0)
    logo = logo_alpha().rotate(-90, expand=True)
    lw = int(w * S * 0.30)
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    m.paste(logo, ((w * S - lw) // 2, int(h * S * 0.12)))
    d = ImageDraw.Draw(m)
    y = int(h * S * 0.12) + logo.height + int(w * S * 0.13)
    size = int(w * S * 0.068)
    for text, weight in spec['lines']:
        f = sans(size, weight)
        d.text((w * S / 2, y), ' '.join(text) if len(text) < 14 else text, font=f, fill=255, anchor='ms'); y += int(size * 1.45)
    m = m.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.5))
    ink = np.asarray(m).astype(np.float32) / 255 * 0.92
    reg = a[y0:y1, x0:x1]
    for ch in range(3):
        reg[..., ch] = reg[..., ch] * (1 - ink) + 228 * ink
    a[y0:y1, x0:x1] = reg
    return a


if __name__ == '__main__':
    args = sys.argv[1:]
    src, dst, product = args[0], args[1], args[2]
    opt = lambda k: tuple(int(v) for v in args[args.index(k) + 1].split(',')) if k in args else None
    out = composite(Image.open(src), product, opt('--roi'), opt('--box'), args[args.index('--debug') + 1] if '--debug' in args else None,
                    float(args[args.index('--blur') + 1]) if '--blur' in args else 0.0)
    out.save(dst, quality=93)
    print(dst, out.size)
