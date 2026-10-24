"""Print SKINOFAB's real label on a black bottle, stick or box in a photo, with the brand's own wordmark (the owner's
vector file, brand/logo/skinofab-wordmark.svg, rasterized to brand/logo/skinofab-wordmark-black.png), so the logo is
ours to the pixel, not an AI's or a font's guess at it.

usage: python3 -I label_composite.py <in.jpg> <out.jpg> <product> [--roi x0,y0,x1,y1] [--box x0,y0,x1,y1] [--blur px]
                                     [--angle deg] [--relabel] [--debug <dir>]
  product   serum, foundation or balm; the label's lines are in LABELS
  --roi     where to look for the bottle (default: the whole image); the bottle is the largest near-black area in it
  --box     the carton's front face, if the photo shows one: the logo goes on it, centred, with the product name
  --blur    extra softening for a bottle that is out of focus (px)
  --angle   the photo is turned by this many degrees (counter-clockwise) first, so the bottle stands upright with its
            top up, and turned back after; for a tilted or lying bottle
  --relabel the bottle already has a printed label with another wordmark: that wordmark is found and erased, and
            ours goes where it was, at its size and angle around the cylinder; the small printed lines stay

The bottle's body is found from the near-black pixels: the rows where it is widest are the body, their centre line
(with its tilt) the label's axis. The label is the foundation bottle's layout: the wordmark set vertically, reading
top to bottom, then the product lines in Montserrat. It is wrapped around the cylinder, shaded by the bottle's own
light (brighter on the highlight side, fading at the edges), softened to the photo's sharpness and clipped to the
bottle's pixels, so fingers in front of it stay in front.

An old print is found as small bright strokes on the black (a white top-hat of the luminance: narrower than the
bottle's highlight band), grouped into the label's column (the wordmark and the small lines under it; a pump's
bright nozzle above it is a separate group and stays), and inpainted from the black around it.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
LOGO = HERE.parents[1] / 'brand' / 'logo' / 'skinofab-wordmark-black.png'
FONT = HERE / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
DEBUG = False
# logo: the wordmark's letter height as a share of the bottle's width; start: where the label starts, as a share of
# the body's height (a blank bottle; a relabelled one keeps its old label's place)
LABELS = {
    'serum': {'lines': [('EGF + NAD+', 'Medium'), ('FIRMING SERUM', 'Medium')], 'sub': 'COLLAGEN', 'size': '30 mL / 1.01 fl oz',
              'logo': 0.27, 'start': 0.14},
    'foundation': {'lines': [('ADAPTIVE PEPTIDE', 'Medium'), ('FOUNDATION', 'Medium')], 'sub': 'PDRN', 'size': '30 mL / 1.01 fl oz',
                   'logo': 0.22, 'start': 0.41},
    'balm': {'lines': [('PLUMPING', 'Medium'), ('BALM', 'Medium')], 'sub': 'PDRN · VOLUFILINE', 'size': '10 g / 0.35 oz',
             'logo': 0.30, 'start': 0.12},
}


def sans(size, weight='Medium'):
    f = ImageFont.truetype(str(FONT), size); f.set_variation_by_name(weight); return f


def logo_alpha():
    """The wordmark as an alpha mask (the rasterized vector: black letters on transparent)."""
    m = Image.open(LOGO).getchannel('A')
    return m.crop(m.getbbox())


def label_art(product, w, logo_px=None, logo_only=False, theta=0.0):
    """The bottle label as a white-on-transparent mask for a body w px wide (sizes as seen at the bottle's centre);
    drawn 4x and returned at 4x (the caller scales it to the photo). logo_px: the wordmark's letter height in photo
    px (an old label's), else LABELS' share of the width; logo_only: the wordmark alone (it replaces an old one, the
    printed lines under it stay); theta: where around the cylinder the wordmark's middle sits (radians, 0 = facing)."""
    spec = LABELS[product]
    S = 4
    logo = logo_alpha().rotate(-90, expand=True)                 # reads top to bottom, S at the top
    lw = int((logo_px if logo_px else w * spec['logo']) * S)
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    A = int(w * S * np.pi / 2)                                   # the art spans the visible half of the cylinder
    if logo_only:
        m = Image.new('L', (A, logo.height), 0)
        u = (theta / (np.pi / 2) * 0.5 + 0.5) * A                 # the art's columns are angles across the cylinder
        m.paste(logo, (int(u - lw / 2), 0))
        return m, logo.height
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


def body_of(img, roi, floor=0, lit_max=125):
    """The bottle's body in roi: (mask of the bottle's dark pixels, centre x per row fit, top, bottom, width, angle)."""
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    x0, y0, x1, y1 = roi
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    sat = a.max(2) - a.min(2)
    dark = (lum < 70) & (lum >= floor) & (sat < 40)             # floor: a pure black backdrop is not the bottle
    dark[:y0] = False; dark[y1:] = False; dark[:, :x0] = False; dark[:, x1:] = False
    lab, n = ndimage.label(ndimage.binary_opening(dark, iterations=2))
    if not n: raise SystemExit('no dark bottle in the roi')
    core = lab == (np.argmax(ndimage.sum(dark, lab, range(1, n + 1))) + 1)
    # the lit side of a turned bottle is lighter than its core, still a smooth grey (grey hair beside it is a grey
    # too, but textured): grown into from the core
    # (on a lightly blurred copy, so the printed letters on it average into the bottle's grey)
    sg = max(1.5, 0.005 * max(x1 - x0, y1 - y0))
    bl, bs = ndimage.gaussian_filter(lum, sg), ndimage.gaussian_filter(sat, sg)
    m1 = ndimage.uniform_filter(bl, 7); m2 = ndimage.uniform_filter(bl * bl, 7)
    smooth = np.sqrt(np.maximum(m2 - m1 * m1, 0)) < 7
    lit = (bl < lit_max) & (bl >= floor) & (bs < 40) & smooth
    lit[:y0] = False; lit[y1:] = False; lit[:, :x0] = False; lit[:, x1:] = False
    lab2, _ = ndimage.label(lit)
    ids = np.unique(lab2[core & (lab2 > 0)])
    if len(ids): core = core | np.isin(lab2, ids)
    core = ndimage.binary_fill_holes(ndimage.binary_closing(core, iterations=3))
    # the bottle is everything between its dark edges on each row (its highlight band is lighter than the core),
    # except skin: fingers in front of it stay in front
    rows = np.nonzero(core.any(1))[0]
    big = np.zeros_like(core)
    for r in rows:
        xs = np.nonzero(core[r])[0]; big[r, xs.min():xs.max() + 1] = True
    inside = big.copy()                                          # the bottle's rows, its print included
    skin = (sat > 34) | ((lum > 140) & (sat > 14))           # skin is warm; a bottle's lit side is a neutral grey
    big &= ~ndimage.binary_dilation(skin, iterations=1)
    widths = np.array([np.ptp(np.nonzero(core[r])[0]) + 1 for r in rows])
    wmax = np.percentile(widths, 90)
    body_rows = rows[widths > wmax * 0.86]
    top, bottom = body_rows.min(), body_rows.max()
    cs = np.array([(np.nonzero(core[r])[0].min() + np.nonzero(core[r])[0].max()) / 2 for r in body_rows])
    k, c = np.polyfit(body_rows, cs, 1)                         # centre line x = k*y + c (the bottle's tilt)
    body_of.inside = inside
    return big, (k, c), top, bottom, wmax


def old_print(a, roi, bw, centre, inside):
    """The old wordmark printed on the bottle in roi: (mask of its letters, its first row, its letter height, how far
    its middle sits from the cylinder's centre line in px), or None. Letters are small neutral-white strokes on the
    bottle (inside: its rows, filled between its dark edges), in the label's band (the rims' highlights are not
    letters), grouped into columns; the wordmark is the tallest dense column (the small lines under it are wider than
    tall, a pump's nozzle is small, hair strands are sparse). centre: the bottle's centre line (k, c), x = k*y + c."""
    x0, y0, x1, y1 = roi
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    sat = a.max(2) - a.min(2)
    region = np.zeros(lum.shape, bool); region[y0:y1, x0:x1] = True
    yy, xx = np.mgrid[0:lum.shape[0], 0:lum.shape[1]]
    cx = centre[0] * yy + centre[1]
    band = np.abs(xx - cx) < bw * 0.49
    se = max(5, int(bw * 0.10)) | 1
    top = ndimage.white_tophat(ndimage.gaussian_filter(lum, 0.6), size=se)
    raw = inside & region & (top > 30) & (sat < 55) & (lum > 60)
    # printed letters are near-white and neutral (the dark gaps between their strokes are not; skin is warm); a
    # highlight streak down the cylinder can be as bright, but it is one long thin line: what stays after a vertical
    # opening longer than any letter, and thin, is a streak
    text = raw & band & (lum > 140) & (sat < 22)
    op = ndimage.binary_opening(text, structure=np.ones((max(9, int(bw * 0.45)), 1), bool))
    lab, n = ndimage.label(op)
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        if (sl[1].stop - sl[1].start) <= max(3, bw * 0.06):
            text &= ~ndimage.binary_dilation(lab == k, structure=np.ones((3, 5), bool))
    # the seam between cap and body runs across the whole bottle: its rows (and a few px around) hold no letters
    seam = ndimage.binary_opening(raw, structure=np.ones((1, max(9, int(bw * 0.5))), bool))
    lab, n = ndimage.label(seam)
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        if (sl[0].stop - sl[0].start) <= max(3, bw * 0.03):
            pad = max(2, int(bw * 0.03)); text[max(0, sl[0].start - pad):sl[0].stop + pad] = False
    # and a thin fragment of the seam (a line or, on a turned bottle, an arc: a few px thick, much wider than that)
    # or a speck is not a letter either
    lab, n = ndimage.label(text)
    areas = ndimage.sum(text, lab, range(1, n + 1))
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        thick = areas[k - 1] / max(ww, 1)
        if (hh <= max(3, bw * 0.025) and ww >= 5 * hh) or (ww >= bw * 0.2 and thick <= max(3, bw * 0.012)) \
                or areas[k - 1] < max(6, bw * bw * 0.0003):
            text &= lab != k
    if text.sum() < 20: return None
    col = ndimage.binary_dilation(text, structure=np.ones((max(3, int(bw * 0.08)), max(3, int(bw * 0.05))), bool))
    lab, n = ndimage.label(col)
    best, main = 0.0, None
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        px = (text[sl] & (lab[sl] == k)).sum()
        dense = px / max(1, hh * ww)
        if DEBUG: print('  column', hh, ww, round(dense, 2), 'bw', bw, file=sys.stderr)
        if hh >= 2.2 * ww and hh >= bw * 0.35 and dense >= 0.12 and hh > best: best, main = hh, k
    if main is None: return None
    text &= lab == main
    rows = np.nonzero(text.any(1))[0]
    spans = [np.ptp(np.nonzero(text[r])[0]) + 1 for r in rows if text[r].sum() > 1]
    height = float(np.percentile(spans, 70)) if spans else bw * 0.22
    ys, xs = np.nonzero(text)
    dx = float(np.mean(xs - cx[ys, xs]))
    return text, int(rows.min()), height, dx


def erase(a, text, bw):
    """The old letters inpainted from the black around them."""
    import cv2
    m = ndimage.binary_dilation(text, iterations=max(1, int(round(bw / 140)) + 1)).astype(np.uint8) * 255
    bgr = np.clip(a[..., ::-1], 0, 255).astype(np.uint8)
    out = cv2.inpaint(bgr, m, max(3, int(bw * 0.03)), cv2.INPAINT_TELEA)
    return out[..., ::-1].astype(np.float32)


def composite(img, product, roi=None, box=None, debug=None, blur=0.0, angle=0.0, relabel=False, floor=0, lit_max=125):
    """floor: a pure black backdrop's level (a photo cut out on black: the backdrop is not the bottle); lit_max: how
    light the bottle's lit side gets (a close-up's highlight band is lighter)."""
    img = img.convert('RGB')
    if angle:
        return turned(img, angle, roi, lambda im, r: composite(im, product, r, box, debug, blur, 0.0, relabel, floor, lit_max))
    W, H = img.size
    roi = roi or (0, 0, W, H)
    mask, (slope, c), top, bottom, bw = body_of(img, roi, floor, lit_max)
    a = np.asarray(img).astype(np.float32)
    spec = LABELS[product]
    anchor = None
    if relabel:
        found = old_print(a, roi, bw, (slope, c), body_of.inside)
        if found:
            text, first, height, dx = found
            a = erase(a, text, bw)
            img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
            mask, (slope, c), top, bottom, bw = body_of(img, roi, floor, lit_max)
            theta = float(np.arcsin(np.clip(dx / (bw / 2), -0.95, 0.95)))
            anchor = (first, height / max(0.35, np.cos(theta)), theta)   # its size at the facing side
        else:
            print('relabel: no old wordmark found in', roi, '- left as it is', file=sys.stderr)
            return img
            if debug:
                Path(debug).mkdir(parents=True, exist_ok=True)
                Image.fromarray((text * 255).astype(np.uint8)).save(Path(debug) / 'old-print.png')
    body_h = bottom - top
    cut = bottom >= min(roi[3], H) - 3                           # the frame cuts the bottle: its body is longer
    if cut: body_h = max(body_h, bw * 1.65); bottom = top + body_h
    art, ah = (label_art(product, bw, anchor[1], logo_only=True, theta=anchor[2]) if anchor
               else label_art(product, bw))                      # at 4x
    lab_h = ah / 4
    y_start = anchor[0] if anchor else top + body_h * spec['start']
    if not anchor and y_start + lab_h > bottom - body_h * 0.05:   # a short body: shrink the label to fit
        f = max(0.3, (bottom - body_h * 0.05 - y_start) / lab_h)
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
    ink_col = 230 + 22 * lift
    for ch in range(3):
        out[..., ch] = out[..., ch] * (1 - ink) + ink_col * ink
    if box:
        out = carton(out, product, box)
    res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    if debug:
        Path(debug).mkdir(parents=True, exist_ok=True)
        Image.fromarray((mask * 255).astype(np.uint8)).save(Path(debug) / 'mask.png')
    return res


def turned(img, angle, roi, fn):
    """fn(image, roi) on the photo turned by angle degrees (counter-clockwise) around the roi's centre, turned back;
    only a square around the roi is turned, and only the pixels fn changed are taken back, so the rest of the photo
    is not resampled."""
    W, H = img.size
    x0, y0, x1, y1 = roi or (0, 0, W, H)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = int(np.hypot(x1 - x0, y1 - y0) / 2) + 8
    bx, by = int(cx) - half, int(cy) - half
    sub = Image.new('RGB', (2 * half, 2 * half), (255, 255, 255)); sub.paste(img, (-bx, -by))
    c = (half, half)
    rs = sub.rotate(angle, resample=Image.BICUBIC, center=c)
    box = Image.new('L', sub.size, 0); ImageDraw.Draw(box).rectangle((x0 - bx, y0 - by, x1 - bx, y1 - by), fill=255)
    rroi = box.rotate(angle, center=c).getbbox()
    done = fn(rs, rroi)
    diff = (np.abs(np.asarray(done).astype(np.int16) - np.asarray(rs).astype(np.int16)).max(2) > 1)
    diff = ndimage.binary_dilation(diff, iterations=2)
    alpha = Image.fromarray((diff * 255).astype(np.uint8)).rotate(-angle, resample=Image.BILINEAR, center=c)
    back = done.rotate(-angle, resample=Image.BICUBIC, center=c)
    sub.paste(back, (0, 0), alpha.filter(ImageFilter.GaussianBlur(0.6)))
    out = img.copy()
    out.paste(sub.crop((max(0, -bx), max(0, -by), min(2 * half, W - bx), min(2 * half, H - by))), (max(0, bx), max(0, by)))
    return out


def measure_print(img, box, first):
    """Where an old wordmark is: its letters are the bright, grey pixels in box (x0, y0, x1, y1) with black around
    them (the backdrop's white is not), their main axis (PCA) its line. Returns (p0, p1, height) for swap_flat: p0 the
    end nearer first (a point on or near its first letter, which says which way it reads)."""
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    a = np.asarray(img.convert('RGB').crop((x0, y0, x1, y1))).astype(np.float32)
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    sat = a.max(2) - a.min(2)
    black = lum < 70
    if black.sum() < 50: raise SystemExit(f'measure_print: no black in {box}')
    warm = a[..., 0] - a[..., 2]                                 # skin (a fingertip at the edge) is warm, ink is not
    lift = lum - ndimage.grey_opening(lum, size=(21, 21))     # brighter than the bottle around it, lit side or not
    up_ = lum[lift > 45]
    top = float(np.percentile(up_, 95)) if up_.size else 255.0  # the ink's own level: a lit edge is dimmer than it
    bright = (lift > 45) & (lum > max(90.0, 0.7 * top)) & (sat < 30) & (warm < 15)
    lab, n = ndimage.label(bright, structure=np.ones((3, 3)))
    # a letter sits on the black all round (the ring of px just outside it is much darker) and inside the box; the
    # white backdrop, a white sleeve or grey hair beside the stick does not
    on_black = np.zeros(n + 1, bool)
    H, W = lum.shape
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl[0].start == 0 or sl[1].start == 0 or sl[0].stop == H or sl[1].stop == W: continue
        y0_, y1_ = max(0, sl[0].start - 3), min(H, sl[0].stop + 3)
        x0_, x1_ = max(0, sl[1].start - 3), min(W, sl[1].stop + 3)
        comp = lab[y0_:y1_, x0_:x1_] == i
        ring = ndimage.binary_dilation(comp, iterations=3) & ~ndimage.binary_dilation(comp, iterations=1)
        patch = lum[y0_:y1_, x0_:x1_]
        on_black[i] = ring.any() and patch[ring].mean() < patch[comp].mean() - 40
    letters = on_black[lab]
    ys, xs = np.nonzero(letters)
    if len(xs) < 30: raise SystemExit(f'measure_print: no print in {box}')
    P = np.stack([xs + x0, ys + y0], 1).astype(float)
    c = P.mean(0)
    d = np.linalg.svd(P - c, full_matrices=False)[2][0]
    # a second pass without what lies off the letters' line (an eye's catchlight under the stick, a speck)
    ids = lab[ys, xs]
    keep = np.zeros(n + 1, bool)
    upv = np.array([d[1], -d[0]])
    ext = []
    for i in np.unique(ids):
        q = (P[ids == i] - c) @ upv
        ext.append((i, q.mean(), q.max() - q.min()))
    hh = float(np.median([e[2] for e in ext]))
    for i, off, _ in ext: keep[i] = abs(off) <= max(0.75 * hh, 2.0)
    P = P[keep[ids]]
    if len(P) < 30: raise SystemExit(f'measure_print: no print in {box}')
    c = P.mean(0)
    d = np.linalg.svd(P - c, full_matrices=False)[2][0]
    up = np.array([d[1], -d[0]])
    al, ac = (P - c) @ d, (P - c) @ up
    a0, a1 = np.percentile(al, [0.3, 99.7]); c0, c1 = np.percentile(ac, [1, 99])
    mid = c + d * (a0 + a1) / 2 + up * (c0 + c1) / 2
    p0, p1 = mid - d * (a1 - a0) / 2, mid + d * (a1 - a0) / 2
    if np.hypot(*(p1 - np.asarray(first, float))) < np.hypot(*(p0 - np.asarray(first, float))): p0, p1 = p1, p0
    return tuple(p0), tuple(p1), float(c1 - c0)


def swap_flat(img, p0, p1, height, blur=0.5):
    """The old wordmark printed from p0 (the outer end of its first letter) to p1 (the outer end of its last), its
    letters height px tall, is erased and the brand's wordmark set in its place, flat (a small or turned print, where
    the cylinder's curve does not show): the same middle, length and angle, in the old print's own ink colour, with
    fingers in front of it kept in front. p0, p1 in the photo's px."""
    import cv2
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    H, W = a.shape[:2]
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0; L = float(np.hypot(*d)); d /= L
    up = np.array([d[1], -d[0]])                                 # the letters' up (screen y points down)
    mid = (p0 + p1) / 2
    yy, xx = np.mgrid[0:H, 0:W]
    rx, ry = xx - mid[0], yy - mid[1]
    along, across = rx * d[0] + ry * d[1], rx * up[0] + ry * up[1]
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    sat = a.max(2) - a.min(2)
    strip = (np.abs(along) <= L / 2 + height * 0.65) & (np.abs(across) <= height * 0.72)   # a little past both ends
    base = float(np.percentile(lum[strip], 35))
    text = strip & (lum > base + 40) & (sat < 45) & (a[..., 0] - a[..., 2] < 20)   # not a fingertip's warm highlight
    ink = (np.median(a[text & (lum >= np.percentile(lum[text], 60))], axis=0) if text.sum() > 10
           else np.array([235, 235, 235], np.float32))
    m = ndimage.binary_dilation(text, iterations=max(1, int(round(height / 14)))) & ndimage.binary_dilation(strip, iterations=2)
    bgr = np.clip(a[..., ::-1], 0, 255).astype(np.uint8)
    a = cv2.inpaint(bgr, m.astype(np.uint8) * 255, max(3, int(height * 0.25)), cv2.INPAINT_TELEA)[..., ::-1].astype(np.float32)
    # the new wordmark: the logo at the old print's length, turned to its angle, centred on its middle
    S = 4
    logo = logo_alpha()
    lw = max(8, int(L * S)); lh = max(2, int(logo.height * lw / logo.width))
    logo = logo.resize((lw, lh), Image.LANCZOS).rotate(float(np.degrees(np.arctan2(-d[1], d[0]))), resample=Image.BICUBIC, expand=True)
    logo = logo.resize((max(1, logo.width // S), max(1, logo.height // S)), Image.LANCZOS)
    alpha = np.zeros((H, W), np.float32)
    ox, oy = int(round(mid[0] - logo.width / 2)), int(round(mid[1] - logo.height / 2))
    la = np.asarray(logo).astype(np.float32) / 255
    sx0, sy0 = max(0, -ox), max(0, -oy)
    tx0, ty0 = max(0, ox), max(0, oy)
    tx1, ty1 = min(W, ox + logo.width), min(H, oy + logo.height)
    alpha[ty0:ty1, tx0:tx1] = la[sy0:sy0 + ty1 - ty0, sx0:sx0 + tx1 - tx0]
    alpha = ndimage.gaussian_filter(alpha, blur)
    lum2 = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    sat2 = a.max(2) - a.min(2)
    skin = (sat2 > 34) | ((lum2 > 140) & (sat2 > 14))
    alpha *= ~ndimage.binary_dilation(skin, iterations=1)
    out = a * (1 - alpha[..., None]) + ink[None, None, :] * alpha[..., None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


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
    num = lambda k, d=0.0: float(args[args.index(k) + 1]) if k in args else d
    out = composite(Image.open(src), product, opt('--roi'), opt('--box'), args[args.index('--debug') + 1] if '--debug' in args else None,
                    num('--blur'), num('--angle'), '--relabel' in args)
    out.save(dst, quality=93)
    print(dst, out.size)
