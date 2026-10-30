"""The Adaptive Peptide Foundation funnel's images and clips, written to the Page Kit campaign's images folder
(campaigns/skinofab/src/apf-funnel/assets/images/sf/).

usage: python3 -I tools/funnel/apf/images.py [<work_dir>] [--no-video]      (--no-video: no clip is encoded; their posters are still written)
  <work_dir>: the store build's inputs (tools/build_store.sh); its reviews/photos/ has the buyers' own photos. Their
  crops are kept in brand/adaptive-peptide-foundation/reviews/ so a build without the work dir still has them.

Sources, none generated here (no image model has credit on 27 Oct 2026, and the live page's photos are the owner's,
approved):
- the live product page's photos (brand/adaptive-peptide-foundation/pdp/, with their origin in manifest.json): the
  women past 45 with the real bottle, the "goes on white" dots, the two infographics, the problem and solution photos;
- the product sheet's renders (brand/adaptive-peptide-foundation/*.png) for the packshots and the packs' cards;
- the generated split portraits (brand/adaptive-peptide-foundation/gen/ba-split-*.png, 28 Oct 2026: one woman of
  45+ twice in one frame, bare skin with its lines, sun spots and redness on the left, the foundation on with an
  even, luminous tone on the right; gen/README.md has the model and prompts): retired on 29 Oct 2026 for the owner's
  own pairs (no disclaimer line on any image, the owner's instruction of 28 Oct 2026); the listicle's lines, dry-skin
  and ages reasons, which have no pair yet, show a persona photo (brand/persona/age-*.jpg, women 45+ made for the store);
- the owner's own images (brand/adaptive-peptide-foundation/owner/, 29 Oct 2026): three before/after pairs of
  women past 45 (bare skin with lines, spots and uneven tone, then the foundation on, glowing and even) and the
  SKINOFAB doctor in her clinic holding the bottle, its small print reset by doctor_photo();
- the buyers' own photos (reviews/photos-approved.txt), square on the face;
- the seven demo clips the homepage plays (brand/videos/gj-*, the old bottle replaced by the real one): the four
  with women 45+, at 540 px with a WebM copy, posters from the live page or a frame;
- the store's how-it-works loop (brand/adaptive-peptide-foundation/howto/, its pill cropped away and its label's PDRN
  line set, howto_loop()) and the stick funnel's brush loop
  (brand/stick-funnel/videos/up2-how.*);
- the brush's own images (brand/lymphatic-brush/) and the stick funnel's guarantee seal.
"""
import json, shutil, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'funnel'))
sys.path.insert(0, str(ROOT / 'tools' / 'persona'))
import funnel_images as FI          # even_tone, face_square (the stick funnel's)
import product_photos as P          # fonts, the AI line

BRAND = ROOT / 'brand'
APF, PDP, PERSONA, BRUSH = BRAND / 'adaptive-peptide-foundation', BRAND / 'adaptive-peptide-foundation' / 'pdp', BRAND / 'persona', BRAND / 'lymphatic-brush'
KEPT = APF / 'reviews'              # the buyers' photo crops, kept in git
OWNER = APF / 'owner'               # the owner's own images (29 Oct 2026): three before/after pairs, the doctor in her clinic
GEN = APF / 'gen'                   # the generated sources (GPT Image 2 through 4SToken; gen/README.md has the prompts)
OUT = ROOT / 'campaigns' / 'skinofab' / 'src' / 'apf-funnel' / 'assets' / 'images' / 'sf'
INK, PAPER, SOFT, CREAM = (21, 21, 21), (255, 255, 255), (96, 96, 96), (246, 242, 236)

# the buyers whose photos the pages show (review id -> where her face sits: (x, y) for the largest square there, or
# (x, y, side) for a square of side x the photo's height padded with a blur of itself when it runs past the photo)
REVIEW_PHOTOS = {
    'lora': ('zjPC7IPmY', (0.5, 0.2)), 'hope': ('DCqk83pSC', (0.5, 0.22)), 'tina': ('9y5hcA803', (0.5, 0.22)),
    'gillian': ('Nr7dIjYVa', (0.5, 0.22)), 'darla': ('UMV04vLbx', (0.5, 0.22)), 'rachel': ('xrPwzXagm', (0.5, 0.22)),
    'sharon': ('9F13vuZCr', (0.5, 0.22)), 'michele': ('P7Xzlz5Oi', (0.5, 0.26, 0.6)), 'maria': ('OOv6J0c2A', (0.5, 0.22)),
    'virginia': ('5FRfi6xsO', (0.55, 0.36, 0.78)), 'susan': ('yguFL8u9n', (0.5, 0.38, 0.66)), 'vicki': ('DOovCyNzE', (0.5, 0.22)),
    'diane': ('Eu0eKzf2sd', (0.5, 0.22)), 'sherron': ('3WiAfEawf', (0.5, 0.45, 0.72)), 'mary': ('ZTOdiyg6x', (0.5, 0.4)),
    'judith': ('AsJHczI5X', (0.5, 0.22)), 'barbara': ('SPVvNkR4Q', (0.5, 0.22)), 'kathryn': ('BJ6W4ha63', (0.5, 0.35)),
    'katie': ('5-xR3f8FU', (0.5, 0.22)), 'tracy': ('bGoecpWaG', (0.5, 0.42, 0.62)), 'grace': ('0z7LbNoAb', (0.5, 0.48, 0.5)),
    'donna': ('do7iDXXm-', (0.5, 0.4)), 'maryh': ('4tu6r96fi', (0.5, 0.22)), 'emily': ('Yrqqzl0Uo', (0.5, 0.22)),
    'sharyl': ('-mKd4TTBE', (0.5, 0.22)), 'dotty': ('cJ7rJAid8', (0.5, 0.22)), 'melissa': ('rilMz9W7y', (0.5, 0.22)),
    'vanna': ('crntCbrIc_', (0.5, 0.22)), 'patricia': ('4MhLZP2jw', (0.5, 0.4, 0.7)), 'ginger': ('YBJPvZ7CE', (0.5, 0.22)),
    'june': ('K2BFPc2-r', (0.5, 0.22)), 'michelle': ('qeP59lM3X', (0.5, 0.22)), 'liz': ('SMuH-0VGM', (0.5, 0.22)),
    'susans': ('u7mcI49kr', (0.5, 0.22)), 'caroline': ('66CwHKYLP', (0.5, 0.26, 0.58)), 'mrss': ('EwyYcrBRX', (0.5, 0.22)),
}
# the live page's photos, by the name the pages use
# (the store's "The Science" and "vs. others" graphics stay out: each carries a line the claims rules forbid)
# the kept crops padded with a blurred band of themselves (live review 6): the photo's own columns, as a square
# (x0, x1[, y0]): the square of the kept photo that is her own picture, from y0 down (susan: brows to chin, live review 7:
# from the top it cut her face below the nose)
REVIEW_TRIM = {'susan': (0.15, 0.85, 0.30), 'virginia': (0.02, 0.92)}
PDP_PHOTOS = {'g-hold': 'hold-cheek', 'g-dots': 'dots-eyes-closed', 'g-grey': 'hold-grey-hair',
              'g-inside': 'whats-inside', 'g-brush': 'buffing-brush',      # g-brush: offers 2 and 2b's gallery
              'g-bottle': 'bottle-korea', 'problem': 'problem', 'solution': 'solution-bottle',
              'gift-blender': 'gift-blender', 'gift-mystery': 'gift-mystery', 'gift-shipping': 'gift-shipping'}
# the demo clips (brand/videos/gj-<key>*.mp4): women 45+ with the real bottle; poster from the live page or a frame
# (no demo-navy any more: its speaker is an AI model talking as a buyer, "I'll be buying this on repeat", which the
# funnel showed as "women like you": an invented testimonial, live review 10, F1. The silent clips show how it goes on.)
CLIPS = {'demo-black': ('gj-41b77ec4-clean', 'sharp', 'A woman in her fifties in black pumps the bottle and buffs the foundation in with a brush'),
         'demo-silver': ('gj-88d49199', None, 'A silver-haired woman in her sixties blends the foundation in with her fingers'),
         'demo-robe': ('gj-b705ce67', 'sharp', 'A blonde woman in a grey robe dots the foundation on her cheeks and forehead and buffs it in')}
CLIP_WIDTH = 540


def save(im, name, size=None, q=84):
    im = im.convert('RGB')
    if size and max(im.size) > size: im.thumbnail((size, size), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f'{name}.jpg', quality=q, optimize=True, progressive=True)
    print(name, im.size)


def bottle(size, pdrn=2.0):
    """The bottle on white: the live page's own render (the product sheet's, its grey backdrop already lifted), with
    the label's PDRN line, which that copy lacks: the line is taken from the product sheet's own front render
    (01-front.png, relabelled by tools/persona/relabel_bottles.py), whose label sits 127 px right of and 3 px below this
    one at the same scale, as its light print over the bottle's black (live review 5: the pack shots read without the
    PDRN line every held bottle and the store's photos print).
    pdrn: the line's size against the label's own. Every use of this bottle is a pack shot shown 300-470 px wide,
    where the line at its own size was 3-4 px tall on a 1x screen and "PDRN" read "PORN" (29 Oct 2026); at
    twice its size, centred where it was, it stays inside the black between FOUNDATION and the volume."""
    im = Image.open(PDP / 'solution-bottle.jpg').convert('RGB')
    front = np.asarray(Image.open(APF / '01-front.png').convert('L'), dtype=np.float32)
    fx0, fy0, fx1, fy1, dx, dy = 586, 1046, 668, 1074, -127, -3               # the PDRN line on the front render
    patch = front[fy0:fy1, fx0:fx1]
    bg = np.median(np.concatenate([front[1030:1042, fx0:fx1], front[1080:1100, fx0:fx1]]), axis=0)   # its black, per column
    alpha = np.clip((patch - bg[None]) / (238.0 - bg[None]), 0, 1)
    h, w = alpha.shape
    if pdrn != 1.0:
        big = Image.fromarray((alpha * 255).astype(np.uint8), 'L').resize((round(w * pdrn), round(h * pdrn)), Image.LANCZOS)
        alpha = np.asarray(big, dtype=np.float32) / 255
    H2, W2 = alpha.shape
    cy, cx = fy0 + dy + h / 2, fx0 + dx + w / 2                                 # centred where the line was
    y0, x0 = round(cy - H2 / 2), round(cx - W2 / 2)
    a = np.asarray(im).astype(np.float32)
    region = a[y0:y0 + H2, x0:x0 + W2]
    assert float(region.mean()) < 60, 'solution-bottle.jpg changed: the PDRN line would not land on the black label'
    a[y0:y0 + H2, x0:x0 + W2] = region * (1 - alpha[..., None]) + 238.0 * alpha[..., None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    # the faint grey smear to the lower right of the base goes (a detached shadow, live reviews 1 and 2); the darker
    # contact shadow under the base stays
    a = np.asarray(im).copy(); y0 = int(a.shape[0] * 0.84)
    band = a[y0:]; band[band.min(axis=2) > 196] = 255; a[y0:] = band
    im = Image.fromarray(a)
    return ImageOps.pad(im, (size, size), Image.LANCZOS, color=PAPER)


def cutout(im, dark=110, fill=True):
    """A product cut from its white backdrop as RGBA: what is darker than `dark` (or not white, dark=None), its holes
    filled (the label's white print stays), the edge softened over a pixel."""
    from scipy import ndimage
    im = im.convert('RGB')
    L = np.asarray(im.convert('L'))
    m = (L < dark) if dark else (np.asarray(im).min(-1) < 236)
    if fill: m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, iterations=1)
    alpha = Image.fromarray((m * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(0.9))
    out = im.convert('RGBA'); out.putalpha(alpha)
    return out.crop(alpha.getbbox())


def stage(size, items, bg='white'):
    """Products on a table (the owner, 29 Oct 2026: "more natural shadow and better design"): each item (rgba, x
    centre, y of its base, height) is drawn back to front over its own shadow, light from the upper left: a tight dark
    contact under the base and a wide soft pool falling to the right. bg 'white' (the checkout cards) or 'warm' (a
    cream studio sweep)."""
    W = H = size
    if bg == 'warm':
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.hypot((xx - W * 0.5) / W, (yy - H * 0.36) / H)
        top, edge = np.array([252, 250, 246], np.float32), np.array([236, 228, 218], np.float32)
        t = np.clip(r / 0.75, 0, 1)[..., None] ** 1.4
        canvas = Image.fromarray((top * (1 - t) + edge * t).astype(np.uint8), 'RGB')
    else:
        canvas = Image.new('RGB', (W, H), PAPER)
    for rgba, xc, base, h in items:
        obj = rgba.resize((max(1, int(rgba.width * h / rgba.height)), int(h)), Image.LANCZOS)
        w = obj.width
        sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh)
        d.ellipse((xc + 0.12 * w - 0.78 * w, base - 0.07 * w, xc + 0.12 * w + 0.78 * w, base + 0.13 * w), fill=70)
        sh = sh.filter(ImageFilter.GaussianBlur(max(2, 0.08 * w)))
        c = Image.new('L', (W, H), 0)
        ImageDraw.Draw(c).ellipse((xc + 0.03 * w - 0.47 * w, base - 0.03 * w, xc + 0.03 * w + 0.47 * w, base + 0.035 * w), fill=150)
        c = c.filter(ImageFilter.GaussianBlur(max(1.5, 0.022 * w)))
        shade = Image.fromarray(np.maximum(np.asarray(sh), np.asarray(c)), 'L')
        canvas.paste(Image.new('RGB', (W, H), (58, 46, 38)), (0, 0), shade)
        canvas.paste(obj, (int(xc - w / 2), int(base - h)), obj)
    return canvas


def laurel(im, cx, cy, r, color, K=4):
    """Two laurel branches either side of (cx, cy), the wreath of an award badge around words that are true: a thin
    stem curving up each side, pointed leaves along it turned up and alternately out and in, drawn 4x and brought
    down so the edges stay smooth."""
    import math
    W = int(r * 2.9)
    lay = Image.new('L', (W * K, W * K), 0)
    d = ImageDraw.Draw(lay)
    o = W * K / 2
    def leaf(x, y, ang, length, width):
        pts = []
        for t in np.linspace(0, 1, 14):                                          # a pointed leaf: two arcs tip to tip
            pts.append((t * length, math.sin(t * math.pi) * width / 2))
        pts += [(t * length, -math.sin(t * math.pi) * width / 2) for t in np.linspace(1, 0, 14)]
        ca, sa = math.cos(ang), math.sin(ang)
        d.polygon([(o + (x + px * ca - py * sa) * K, o + (y + px * sa + py * ca) * K) for px, py in pts], fill=255)
    for side in (-1, 1):
        stem = []
        for n, th in enumerate(np.radians(np.linspace(108, 238, 40))):
            stem.append((o + (r * math.cos(th) if side < 0 else -r * math.cos(th)) * K, o + r * math.sin(th) * 0.9 * K))
        d.line(stem, fill=255, width=int(2.6 * K))
        for n, th in enumerate(np.radians(np.linspace(116, 228, 7))):
            x = r * math.cos(th) if side < 0 else -r * math.cos(th)
            y = r * math.sin(th) * 0.9
            tang = math.atan2(-math.cos(th) * 0.9, -math.sin(th)) if side < 0 else math.atan2(-math.cos(th) * 0.9, math.sin(th))
            up = tang + (math.pi if side < 0 else 0)                              # along the stem, toward its tip
            for flip in (-1, 1):
                leaf(x, y, up + flip * side * 0.62, 30 - n * 1.6, 12 - n * 0.5)
    lay = lay.resize((W, W), Image.LANCZOS)
    im.paste(Image.new('RGB', lay.size, color), (int(cx - W / 2), int(cy - W / 2)), lay)


def blender_sponge(h=900):
    """The SKINOFAB Blender sponge as an object on the table (RGBA, h px tall): the black teardrop of the store's gift icon
    (gift-blender.jpg; there is no photo of it), standing on its round end, lit from the upper left like the bottles, with
    a fine pore grain. Drawn at 4x and brought down, so its edge is smooth."""
    K, R = 4, h * 0.30
    W, H = int(R * 2.2) * K, h * K
    cx, cy = W / 2, H - R * K * 1.02
    pts = []
    for i in range(720):
        t = 2 * np.pi * i / 720
        up = max(0.0, -np.cos(t))                                   # the upper half narrows to a soft point
        pts.append((cx + R * K * np.sin(t) * (1 - 0.30 * up ** 1.4), cy + R * K * np.cos(t) * (1 if np.cos(t) > 0 else 2.05)))
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).polygon(pts, fill=255)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    hx, hy = cx - R * K * 0.38, cy - R * K * 0.55                     # the light, upper left
    light = np.exp(-(((xx - hx) / (R * K * 0.75)) ** 2 + ((yy - hy) / (R * K * 1.25)) ** 2))
    shade = np.clip((xx - cx) / (R * K), -1, 1)                       # darker toward the right
    rng = np.random.default_rng(7)
    grain = Image.fromarray((rng.normal(0, 1, (H // 2, W // 2)) * 40 + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    grain = (np.asarray(grain.filter(ImageFilter.GaussianBlur(1.2)), np.float32) - 128) / 128
    v = 34 + 46 * light - 12 * shade + 5 * grain
    rgb = np.stack([v, v * 0.97, v * 0.99], -1).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(rgb, 'RGB').convert('RGBA'); im.putalpha(mask)
    im = im.resize((W // K, H // K), Image.LANCZOS)
    return im.crop(im.getbbox())


def pack_cards():
    """The packs as products on a table: the checkout cards' and the offers' pack images on white (no words: they
    show at 64 px): 1 bottle; 3 with the free Blender sponge (pack-3b) and 5 with the free Lymphatic Brush and its case
    (pack-5), the owner's offer of 30 Oct 2026; the offers' 2 and 6 (the 6 with the brush); the gifts in front of
    the bottles, never in front of a label. And the sales page's 5-pack (offer-5) on a warm sweep under a "BUY 3, GET 2
    FREE" ribbon (true: 5 bottles for less than 3 x the 1-bottle price) with three true badges: the free brush, formulated in
    Korea (a laurel, no clinical claim: there is no clinical study), the 30-day guarantee seal."""
    bot = cutout(bottle(1254))
    card_im = Image.open(BRUSH / 'card.jpg').convert('RGB')
    brush = cutout(card_im.crop((250, 180, 830, 515)), dark=None, fill=False)    # the brush: its comb's gaps stay open
    case = cutout(card_im.crop((250, 515, 830, 905)), dark=None)                  # its case, the SKINOFAB print kept

    sponge = blender_sponge()

    def scene(n, with_brush, size, bg, with_sponge=False):
        s = size / 900
        items = []
        if n == 1: items = [(bot, 450, 800, 700)]
        elif n == 3 and with_sponge:                                              # three bottles, the sponge in front, left
            items = [(bot, 360, 700, 500), (bot, 690, 700, 500), (bot, 525, 726, 535), (sponge, 170, 872, 205)]
        elif n == 5:                                                              # five: two behind, three in front
            items = [(bot, 355, 618, 420), (bot, 545, 618, 420), (bot, 260, 668, 445), (bot, 450, 684, 460), (bot, 640, 668, 445)]
        elif n == 2: items = [(bot, 360, 790, 640), (bot, 545, 812, 660)]
        elif n == 3:
            items = [(bot, 270, 670, 470), (bot, 630, 670, 470), (bot, 450, 695, 500)] if with_brush else \
                    [(bot, 250, 770, 600), (bot, 650, 770, 600), (bot, 450, 800, 630)]
        else:                                                                     # six: three behind, three in front
            items = [(bot, x, 600, 430) for x in (300, 450, 600)] + [(bot, 225, 655, 450), (bot, 450, 668, 462), (bot, 675, 655, 450)]
        if with_brush:
            items += [(brush, 250, 878, 135), (case, 650, 884, 165)]
        return stage(size, [(o, x * s, y * s, h * s) for o, x, y, h in items], bg)

    for n, wb, name in ((1, False, 'pack-1'), (2, False, 'pack-2'), (5, True, 'pack-5'), (6, True, 'pack-6')):
        save(scene(n, wb, 900, 'white'), name, size=700)
    save(scene(3, False, 900, 'white', with_sponge=True), 'pack-3b', size=700)
    # the sales page's 5-pack: a "BUY 3, GET 2 FREE" ribbon over its three badges, the scene a little smaller under them,
    # and a "$19.99 a bottle" tag beside the back right bottle's cap (never on a label)
    k, A, s3 = 0.86, 1050, 1080 / 900
    items = [(bot, 355, 618, 420), (bot, 545, 618, 420), (bot, 260, 668, 445), (bot, 450, 684, 460), (bot, 640, 668, 445),
             (brush, 250, 878, 135), (case, 650, 884, 165)]
    im = stage(1080, [(o, 540 + (x * s3 - 540) * k, A - (A - y * s3) * k, h * s3 * k) for o, x, y, h in items], 'warm')
    d = ImageDraw.Draw(im)
    GOLD = (222, 190, 128)
    x0, x1, y0, y1, notch = 150, 930, 30, 120, 26                                 # the ribbon, its ends cut in
    d.polygon([(x0 - 34, y0 + 10), (x0 + 6, y0 + 10), (x0 + 6, y1 + 10), (x0 - 34, y1 + 10), (x0 - 34 + notch, (y0 + y1) / 2 + 10)], fill=(150, 124, 74))
    d.polygon([(x1 + 34, y0 + 10), (x1 - 6, y0 + 10), (x1 - 6, y1 + 10), (x1 + 34, y1 + 10), (x1 + 34 - notch, (y0 + y1) / 2 + 10)], fill=(150, 124, 74))
    d.rounded_rectangle((x0, y0, x1, y1), radius=6, fill=INK)
    d.line((x0 + 14, y0 + 9, x1 - 14, y0 + 9), fill=GOLD, width=2); d.line((x0 + 14, y1 - 9, x1 - 14, y1 - 9), fill=GOLD, width=2)
    f = P.sans(58, 'Bold'); a, b = 'BUY 3, GET ', '2 FREE'
    wa, wb = d.textlength(a, font=f), d.textlength(b, font=f)
    tx = (x0 + x1) / 2 - (wa + wb) / 2
    d.text((tx, (y0 + y1) / 2 + 2), a, font=f, fill=PAPER, anchor='lm'); d.text((tx + wa, (y0 + y1) / 2 + 2), b, font=f, fill=GOLD, anchor='lm')
    cx, cy, r = 150, 236, 88                                                      # the free brush, and the gifts
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK)
    d.ellipse((cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8), outline=(200, 170, 110), width=2)
    d.text((cx, cy - 30), 'FREE', font=P.sans(34, 'Bold'), fill=GOLD, anchor='ms')
    d.text((cx, cy + 2), 'Lymphatic', font=P.sans(22, 'SemiBold'), fill=PAPER, anchor='ms')
    d.text((cx, cy + 28), 'Brush', font=P.sans(22, 'SemiBold'), fill=PAPER, anchor='ms')
    laurel(im, 540, 228, 104, INK)                                                # formulated in Korea, in a laurel
    d.text((540, 222), 'Formulated', font=P.serif(29, 'Bold'), fill=INK, anchor='ms')
    d.text((540, 256), 'in Korea', font=P.serif(29, 'Bold'), fill=INK, anchor='ms')
    seal = Image.open(OUT / 'guarantee-seal.png').convert('RGBA'); seal.thumbnail((184, 184), Image.LANCZOS)
    im.paste(seal, (1080 - 58 - seal.width, 236 - seal.height // 2), seal)
    T = 150                                                                       # the $19.99 a bottle tag
    tag = Image.new('L', (4 * T, 4 * T), 0); ImageDraw.Draw(tag).ellipse((0, 0, 4 * T - 1, 4 * T - 1), fill=255)
    tag = tag.resize((T, T), Image.LANCZOS)
    tx, ty = 880, 420
    sh = Image.new('L', im.size, 0); sh.paste(tag, (tx - T // 2 + 4, ty - T // 2 + 6)); sh = sh.filter(ImageFilter.GaussianBlur(6))
    im.paste(Image.new('RGB', im.size, (90, 72, 50)), (0, 0), sh.point(lambda v: v * 0.45))
    im.paste(Image.new('RGB', (T, T), GOLD), (tx - T // 2, ty - T // 2), tag)
    d = ImageDraw.Draw(im)
    d.ellipse((tx - T // 2 + 8, ty - T // 2 + 8, tx + T // 2 - 8, ty + T // 2 - 8), outline=INK, width=2)
    d.text((tx, ty + 2), '$19.99', font=P.sans(36, 'Bold'), fill=INK, anchor='ms')
    d.text((tx, ty + 30), 'A BOTTLE', font=P.sans(17, 'Bold'), fill=INK, anchor='ms')
    save(im, 'offer-5', size=1080)
    save(ground(bottle(1080)), 'bottle', size=1080)


def clinicians_badge():
    """The "Clinicians' Choice" mark of the FrontrowMD badge on the sales page and checkout (the owner, 29 Oct 2026: as a
    badge, no link, "like this one", FrontrowMD's own sticker): the two words in Lora between two short laurel branches
    that hug them, four rounded leaves a side turned up and out, in ink on white, drawn 4x and brought down to twice its
    170 x 84 px display size; the count beside it is page text (_includes/sf-frontrow.html), held to FrontrowMD's live
    count by check_apf.py."""
    import math
    from PIL import ImageFont
    K, W, H = 4, 340, 168
    lay = Image.new('L', (W * K, H * K), 0); d = ImageDraw.Draw(lay)
    font = ImageFont.truetype(str(ROOT / 'tools' / 'persona' / 'assets' / 'fonts' / 'Lora-Regular.ttf'), 40 * K)
    d.text((W / 2 * K, 76 * K), 'Clinicians\u2019', font=font, fill=255, anchor='ms')
    d.text((W / 2 * K, 124 * K), 'Choice', font=font, fill=255, anchor='ms')
    def leaf(x, y, ang, length, width):                     # a rounded leaf: blunt at its base, pointed at its tip
        pts = []
        for t in [i / 24 for i in range(25)]:
            w = width / 2 * math.sin(math.pi * t) * (1 - 0.35 * t)
            pts.append((t * length, w))
        pts += [(t * length, -w) for t, w in reversed([(q, width / 2 * math.sin(math.pi * q) * (1 - 0.35 * q)) for q in [i / 24 for i in range(25)]])]
        ca, sa = math.cos(ang), math.sin(ang)
        d.polygon([((x + px * ca - py * sa) * K, (y + px * sa + py * ca) * K) for px, py in pts], fill=255)
    for side in (-1, 1):                                    # each branch a "(" beside the words: foot, outward bulge, top
        P0, P1, P2 = (80, 152), (14, 96), (60, 26)
        if side > 0: P0, P1, P2 = ((W - x, y) for x, y in (P0, P1, P2))
        bez = lambda t: ((1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0],
                         (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1])
        stem = [bez(k / 40) for k in range(41)]
        d.line([(x * K, y * K) for x, y in stem], fill=255, width=int(2.6 * K), joint='curve')
        for t, ln, wd in ((0.06, 26, 13), (0.34, 29, 15), (0.62, 29, 15), (0.90, 27, 14)):
            (x0, y0), (x1, y1) = bez(t), bez(min(1, t + 0.02))
            tang = math.atan2(y1 - y0, x1 - x0)            # along the stem, from the foot up
            leaf(x0, y0, tang + (math.radians(42) if side > 0 else -math.radians(42)), ln, wd)   # turned out, away from the words
        x0, y0 = bez(1.0); x1, y1 = bez(0.97)              # and one at the tip, along the stem
        leaf(x0, y0, math.atan2(y0 - y1, x0 - x1), 22, 11)
    im = Image.new('RGB', (W * K, H * K), PAPER); im.paste(Image.new('RGB', im.size, INK), (0, 0), lay)
    save(im.resize((W, H), Image.LANCZOS), 'clinicians-choice', size=W)

def ground(im, strength=1.0):
    """A natural shadow under a product on white (the owner, 28 Oct 2026: the packshots' shadows looked pasted on):
    a tight contact shadow along the base of whatever is not white and a wider, fainter pool under it, feathered
    sideways, in a warm grey; nothing is drawn over the product itself."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    H, W = a.shape[:2]
    s = W / 900
    mask = (255 - a.min(-1)) > 16
    cols = mask.any(0)
    if not cols.any(): return im
    yb = np.where(cols, H - 1 - np.argmax(mask[::-1], 0), -10 ** 6).astype(np.float32)
    d = np.arange(H, dtype=np.float32)[:, None] - yb[None, :]            # rows below each column's base
    below = (d > -3 * s)
    contact = np.exp(-(d / (4.5 * s)) ** 2) * below * 0.42
    pool = np.exp(-(d / (16 * s)) ** 2) * below * 0.2
    shade = (contact + pool) * cols[None, :]
    shade = FI._blur(shade, 5 * s) * (1 - FI._blur(mask.astype(np.float32), 1.2 * s))
    shade = np.clip(shade * strength, 0, 0.6)[..., None]
    out = a * (1 - shade) + np.array([38, 34, 32], np.float32) * shade
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))




def one_shade():
    """The shade question in one picture (the owner's reference, 29 Oct 2026: a competitor's swatch row over three
    women's before and after): a fair-to-deep swatch row, then the owner's three pairs (owner/ba-*.webp: fair, olive
    and medium-deep skin, past 45) as Before over After, square on the face, each column named by its skin. No count
    of tones (the claims rules), no disclaimer line (the owner's instruction, 28 Oct 2026)."""
    # every word at least 38 px of the 1080: 12.6 px where the picture is narrowest (358 px at 390; 7 to 10 px before,
    # live review 11)
    W, H = 1080, 1260
    im = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 100), 'One shade, no number to guess', font=P.serif(62, 'Bold'), fill=INK, anchor='ms')
    d.text((W // 2, 160), 'It goes on white, then blends into your tone', font=P.sans(40, 'Regular'), fill=SOFT, anchor='ms')
    # nine swatches, fair to deep, each a soft dome with a white rim and a contact shadow
    tones = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in P.SKIN_TONES], dtype=np.float32)
    n, r, gap = 9, 44, 21
    xs = np.linspace(0, len(tones) - 1, n)
    x0, cy, K = (W - (n * 2 * r + (n - 1) * gap)) // 2, 246, 4
    shadow = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(shadow)
    for k in range(n): cx = x0 + r + k * (2 * r + gap); sd.ellipse((cx - r + 2, cy - r + 6, cx + r + 2, cy + r + 6), fill=70)
    im.paste(Image.new('RGB', (W, H), (110, 96, 84)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(7)))
    yy, xx = np.mgrid[0:2 * r * K, 0:2 * r * K].astype(np.float32) / K - r
    lit = np.clip(1.08 - 0.16 * np.hypot(xx + r * 0.35, yy + r * 0.4) / r, 0.9, 1.08)[..., None]   # light from the top left
    for k, f in enumerate(xs):
        lo_ = min(int(f), len(tones) - 2); c = tones[lo_] * (1 - (f - lo_)) + tones[lo_ + 1] * (f - lo_)
        dome = Image.fromarray(np.clip(c * lit, 0, 255).astype(np.uint8), 'RGB').resize((2 * r, 2 * r), Image.LANCZOS)
        m = Image.new('L', (2 * r * K, 2 * r * K), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r * K - 1, 2 * r * K - 1), fill=255)
        cx = x0 + r + k * (2 * r + gap)
        im.paste(dome, (cx - r, cy - r), m.resize((2 * r, 2 * r), Image.LANCZOS))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=PAPER, width=3)
    # the three women: Before over After, square on the face
    # (key, her skin, where her face sits, how far to zoom the after: the garden after is the wider shot)
    cols = (('car', 'Fair', (0.5, 0.22), 1.0), ('kitchen', 'Olive', (0.5, 0.2), 1.0), ('garden', 'Medium-deep', (0.5, 0.22), 1.45))
    cw, g2 = 316, 26
    cx0, top = (W - 3 * cw - 2 * g2) // 2, 356
    def spaced(x, y, text, font, fill):
        w = sum(font.getlength(ch) for ch in text) + 3 * (len(text) - 1)
        x -= w / 2
        for ch in text: d.text((x, y), ch, font=font, fill=fill, anchor='ls'); x += font.getlength(ch) + 3
    lab = P.sans(38, 'Bold')
    for k, (key, word, centering, zoom) in enumerate(cols):
        before, after = pair_halves(Image.open(OWNER / f'ba-{key}.webp'))
        x = cx0 + k * (cw + g2)
        d.text((x + cw // 2, top), word, font=P.sans(40, 'SemiBold'), fill=INK, anchor='ms')
        after = zoom_in(after, zoom)
        for row, (half, name) in enumerate(((before, 'BEFORE'), (after, 'AFTER'))):
            y = top + 62 + row * (cw + 76)
            spaced(x + cw // 2, y, name, lab, SOFT if row == 0 else INK)
            ph = ImageOps.fit(half, (cw, cw), Image.LANCZOS, centering=centering)
            m = Image.new('L', (cw, cw), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, cw - 1), 18, fill=255)
            im.paste(ph, (x, y + 16), m)
    d.text((W // 2, H - 38), 'The same bottle on every one of them', font=P.sans(40, 'Medium'), fill=INK, anchor='ms')
    save(im, 'one-shade', size=H)


def _encode(frames, key, fps=25):
    """frames (a folder of f0001.png…) as <key>.mp4 (H.264) and <key>.webm (VP9), silent, and the last frame as
    the poster."""
    for ext, args in (('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']),
                      ('webm', ['-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0', '-row-mt', '1', '-pix_fmt', 'yuv420p'])):   # yuv420p: an RGB VP9 painted blank in some captures (live review 2)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', str(frames / 'f%04d.png'), '-an', *args, str(OUT / f'{key}.{ext}')], check=True)


def _frames_dir(key):
    import tempfile
    return Path(tempfile.mkdtemp(prefix=f'{key}-'))


def milky(a, m, k=0.72, base=(248, 245, 240), lo=0.78):
    """The serum's clear blue made the foundation's milky white where m (0..1, H x W x 1) is set: its lightness kept as
    shading (lo..1 of base), its colour pulled k of the way to base, a warm white. A drop in the air needs a creamy base
    below the page's white, or only its outline shows and it reads as water (live review 7)."""
    lum = a.mean(-1, keepdims=True)
    white = np.array(base, np.float32) * (lo + (1 - lo) * lum / 255)
    return a * (1 - m * k) + white * (m * k)


def science_clip(encode=True, w=1080, fps=25, seconds=6.0):
    """The serum-absorption loop drawn from the generated cross-section still: the drop leaves the pump, lands, and
    the serum's blue sinks down through the right block while the cream on the left stays on top; then it loops.
    No words (the page's words carry what it shows). science-poster.jpg is the still with the serum in."""
    src = Image.open(GEN / 'science-cross-section.png').convert('RGB')
    src = src.resize((w, round(src.height * w / src.width)), Image.LANCZOS)
    a = np.asarray(src).astype(np.float32)
    H, W = a.shape[:2]
    # the label's PDRN line, which this render lacks (live review 7: every other bottle on the funnel prints it), between
    # FOUNDATION and the volume, at the label's slant (18 degrees down to the right), in its light print
    s_ = w / 1080
    lm = np.asarray(label_mask('PDRN', 31 * s_, 7.6 * s_, angle=-21, weight='SemiBold'), np.float32)[..., None] / 255
    lx, ly = int(986 * s_ - lm.shape[1] / 2), int(209 * s_ - lm.shape[0] / 2)
    reg = a[ly:ly + lm.shape[0], lx:lx + lm.shape[1]]
    assert float(reg.mean()) < 60, 'science-cross-section.png changed: the PDRN line would not land on the black label'
    a[ly:ly + lm.shape[0], lx:lx + lm.shape[1]] = reg * (1 - lm) + 232.0 * lm
    blue = (a[..., 2] - a[..., 0] > 14) & (a[..., 2] > 110)
    blue[:, : W // 2] = False
    blue[: int(H * 0.36)] = False
    bm = FI._blur(blue.astype(np.float32), 2.0)[..., None]
    hsv = np.asarray(src.convert('HSV')).astype(np.float32)
    pink = bm[..., 0] > 0.2
    hsv[..., 0] = np.where(pink, 8.0, hsv[..., 0])
    hsv[..., 1] = np.where(pink, hsv[..., 1] * 0.55, hsv[..., 1])
    dry = np.asarray(Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')).astype(np.float32)
    dry = a * (1 - bm) + dry * bm
    # the serum stays in the surface layer: below the epidermis (the cobbled band ends at 54% of the still) the block keeps its
    # own pink, in the poster and at the end of the loop (the blue through the dermis read as a penetration claim, live review 3)
    # live review 6: still read as sinking in, and clear blue is not the product: the serum now stays in the top of the
    # surface layer (above 45.5%, the cobbled band begins at 40%) and is the foundation's own milky white
    y_cut = int(H * 0.455)
    # below the cut the right block borrows the left block's dermis (the same render, one block-width to the left), so no
    # pale channel marks where the blue was; the seam is feathered
    dx = W * 457 // 1080
    deep = FI._blur(blue.astype(np.float32), 6.0)[..., None]; deep[: y_cut] = 0
    clone = a.copy(); clone[:, dx:] = a[:, : W - dx]
    held = a * (1 - deep) + clone * deep
    # the right block's whole dermis below the cut is the left block's (the render's faint blue haze in its fibres
    # still read as the serum reaching them), feathered over 12 px at the cut
    yy_, xx_ = np.mgrid[0:H, 0:W]
    under = ((yy_ >= y_cut) & (xx_ >= int(W * 0.48)) & (xx_ <= int(W * 0.875))).astype(np.float32)
    under = FI._blur(under, 6.0)[..., None]
    held = held * (1 - under) + clone * under
    # the drop, its stream and the pool: the foundation's milky white, not a clear blue
    liquid = ((a[..., 2] - a[..., 0] > 10) & (a[..., 2] > 100)).astype(np.float32)
    liquid[:, : int(W * 0.55)] = 0; liquid[y_cut:] = 0
    liquid = FI._blur(liquid, 1.5)[..., None]
    # (k: the drop and the film the foundation's opaque milky white, live review 7: at 0.72 they read as clear water)
    held = milky(held, np.maximum(bm * (1 - deep), liquid) * (1 - under), k=0.96, base=(240, 235, 227), lo=0.86)
    dry = dry * (1 - under) + clone * under                              # the loop's first frames: the same clean dermis
    # the thin stream from the pump to the drop, in every frame: the same creamy white as the drop (live review 7: it stayed
    # clear, so the foundation read as water); its light-blue body and its grey edges, below the bottle's lower edge only
    hsv0 = np.asarray(src.convert('HSV')).astype(np.float32)
    dark = a.max(-1) < 70
    low = np.where(dark.any(0), H - 1 - np.argmax(dark[::-1], 0), -1)
    sy, sx = np.mgrid[0:H, 0:W]
    # (above the falling drop's box, which moves)
    stream = ((sy > H * 0.17) & (sy < H * 0.25) & (sx > W * 0.60) & (sx < W * 0.65) & (sy > low[None, :] + 2) & (a.min(-1) < 247)
              & ((hsv0[..., 1] < 41) | (a[..., 2] - a[..., 0] > 8)) & (a.max(-1) > 90)).astype(np.float32)
    stream = FI._blur(stream, 0.8)[..., None]
    dry, held = (milky(x, stream, k=1.0, base=(234, 228, 218), lo=0.86) for x in (dry, held))
    # the pool on the right block, its glassy rim too: the same milky white (on the review 7 build only its centre had
    # caught the blue mask, so the layer still read as clear water); the ellipse is the pool's in the still, and its
    # orange skin (red well above blue) stays as it is
    pool = ((((sx - W * 0.6565) / (W * 0.112)) ** 2 + ((sy - H * 0.4139) / (H * 0.034)) ** 2 < 1)
            & (a[..., 0] - a[..., 2] < 35) & (a.min(-1) < 250)).astype(np.float32)
    pool = FI._blur(pool, 1.2)[..., None]
    dry, held = (milky(x, pool, k=0.9, base=(240, 235, 227), lo=0.86) for x in (dry, held))
    # the falling drop in the still: cut out (its box, as fractions of the still), its place filled white
    bx0, by0, bx1, by1 = int(W * 0.60), int(H * 0.25), int(W * 0.66), int(H * 0.355)
    box = a[by0:by1, bx0:bx1]
    from scipy import ndimage
    # (its faint rim too: at > 20 a ghost of the drop stayed where it started, live review 7)
    dmask = FI._blur(ndimage.binary_dilation((255 - box.min(-1)) > 6, iterations=2).astype(np.float32), 1.0)[..., None]
    drop = milky(box.copy(), dmask, k=1.0, base=(234, 228, 218), lo=0.86)
    # the poster (the still before the clip plays, and for anyone who asks for less motion) shows that milky drop too
    poster = held.copy(); poster[by0:by1, bx0:bx1] = poster[by0:by1, bx0:bx1] * (1 - dmask) + drop * dmask
    save(Image.fromarray(np.clip(poster, 0, 255).astype(np.uint8)), 'science-poster', size=w)
    if not encode: return
    for base in (a, dry, held): base[by0:by1, bx0:bx1] = base[by0:by1, bx0:bx1] * (1 - dmask) + 255 * dmask
    y_nozzle, y_land = int(H * 0.19), int(H * 0.40) - (by1 - by0)
    frames = _frames_dir('science')
    n = int(fps * seconds)
    ys, xs = np.mgrid[0:H, 0:W]
    y_top, y_bot = int(H * 0.40), y_cut + int(H * 0.04)
    for i in range(n):
        t = i / fps
        if t < 1.3:                                                       # the drop falls (ease in)
            k = min(1.0, max(0.0, (t - 0.2) / 1.1)) ** 1.6
            frame = dry.copy()
            y = int(y_nozzle + (y_land - y_nozzle) * k)
            frame[y:y + (by1 - by0), bx0:bx1] = frame[y:y + (by1 - by0), bx0:bx1] * (1 - dmask) + drop * dmask
        else:                                                              # the serum sinks in, then holds
            p = min(1.0, (t - 1.3) / 3.0)
            edge = y_top + (y_bot - y_top) * p
            r = np.clip((edge - ys) / (H * 0.06), 0, 1)[..., None]       # revealed above the sinking edge
            frame = dry * (1 - r * bm) + held * (r * bm)
            if t > seconds - 0.4:                                          # a short crossfade back to the first frame
                q = (t - (seconds - 0.4)) / 0.4
                frame = frame * (1 - q) + dry * q
        Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8)).save(frames / f'f{i + 1:04d}.png')
    _encode(frames, 'science', fps)
    shutil.rmtree(frames)
    print('science clip', n, 'frames')


def allday_clip(encode=True, fps=25, seconds=6.0):
    """Reason 5's loop (the owner, 28 Oct 2026: its video did not play, it was a still): two swatches through a day,
    8 AM to 6 PM. The left (this foundation) keeps its tone; the right (a foundation that oxidises) drifts orange.
    An illustration, and it says so."""
    W, H = 1080, 720
    ours, theirs0, theirs1 = (214, 166, 131), (214, 166, 131), (221, 136, 70)
    frames = _frames_dir('allday')
    n = int(fps * seconds)
    big, small, tiny = P.sans(48, 'SemiBold'), P.sans(38, 'Regular'), P.sans(22, 'Regular')   # the sub line 12 px on a phone, not 8 (live review 5)
    for i in range(n):
        p = min(1.0, max(0.0, (i / fps - 0.5) / (seconds - 1.5)))
        im = Image.new('RGB', (W, H), PAPER)
        d = ImageDraw.Draw(im)
        hour = 8 + p * 10
        hh = int(hour); label = f'{hh if hh <= 12 else hh - 12} {"AM" if hh < 12 else "PM"}'
        d.text((W // 2, 92), label, font=P.serif(64, 'Bold'), fill=INK, anchor='ms')
        d.rounded_rectangle((120, 150, W - 120, 164), 7, fill=(232, 228, 222))
        d.rounded_rectangle((120, 150, 120 + int((W - 240) * p), 164), 7, fill=INK)
        # the words hedge as the copy does: "made not to turn orange", not "the same tone all day" (live review 5)
        for k, (col, title, sub) in enumerate(((ours, 'This foundation', 'made not to turn orange'),
                                               (tuple(int(theirs0[c] + (theirs1[c] - theirs0[c]) * p) for c in range(3)), 'One that oxidizes', 'can turn orange by noon'))):
            cx = W // 4 + k * (W // 2)
            d.ellipse((cx - 150, 220, cx + 150, 520), fill=col)
            f, fs = big, 44
            while d.textlength(title, font=f) > W // 2 - 60 and fs > 28: fs -= 2; f = P.sans(fs, 'SemiBold')
            d.text((cx, 584), title, font=f, fill=INK, anchor='ms')
            sf_, ss = small, 38
            while d.textlength(sub, font=sf_) > W // 2 - 50 and ss > 28: ss -= 2; sf_ = P.sans(ss, 'Regular')
            d.text((cx, 638), sub, font=sf_, fill=SOFT, anchor='ms')
        # the disclosure is the page's caption under the clip (the baked line repeated it, live review 3)
        im.save(frames / f'f{i + 1:04d}.png')
    save(Image.open(frames / f'f{n:04d}.png'), 'allday-poster', size=W)
    if encode: _encode(frames, 'allday', fps)
    shutil.rmtree(frames)
    print('allday clip', n, 'frames')


def pair_halves(im):
    """A before/after made as one frame (the same woman twice, a white bar between): its two halves, cut either side of
    the whole white bar (the brightest column near the middle and every column around it above 235)."""
    im = im.convert('RGB')
    w, h = im.size
    g = np.asarray(im.convert('L'), dtype=np.float32).mean(axis=0)
    lo, hi = int(w * 0.45), int(w * 0.55)
    mid = lo + int(np.argmax(g[lo:hi]))
    left, right = mid, mid
    while left > lo and g[left - 1] > 235: left -= 1
    while right < hi and g[right + 1] > 235: right += 1
    return im.crop((0, 0, left - 4, h)), im.crop((right + 5, 0, w, h))


def zoom_in(im, zoom, top=0.12):
    """The middle 1/zoom of a photo, from `top` of the spare height down (a wider shot brought to a closer one's scale)."""
    if zoom <= 1: return im
    w, h = im.size; zw, zh = int(w / zoom), int(h / zoom)
    x0, y0 = (w - zw) // 2, int((h - zh) * top)
    return im.crop((x0, y0, x0 + zw, y0 + zh))


def split_pair(key, out, size=1080, height=900, band=100, src=None, centering=(0.5, 0.35), zoom_after=1.0, face=1.0, face_top=0.22):
    """A generated split portrait (gen/ba-split-<key>.png: the same woman twice in one frame, her bare skin with its
    lines, spots and redness on the left, the foundation on with an even, luminous tone on the right, a white line
    between) laid out as the pages' before/after: each half fitted to its column (no upscaling at 1376 px wide),
    Before / After in ink on a white band at the foot, a white line between the halves (no disclaimer line: the owner's
    instruction, 28 Oct 2026)."""
    before, after = pair_halves(Image.open(src or GEN / f'ba-split-{key}.png'))
    halves = (before, zoom_in(after, zoom_after))      # zoom_after: an after shot from further away, at the before's scale
    # face: both halves closer on the face, so the skin carries the comparison and the two shots' clothes and settings
    # mostly leave the frame (live review 7: blue to beige sweater, garden to porch read as two sessions)
    halves = tuple(zoom_in(h, face, top=face_top) for h in halves)
    col_w, col_h = size // 2, height - band
    out_im = Image.new('RGB', (size, height), PAPER)
    for j, half in enumerate(halves):
        out_im.paste(ImageOps.fit(half, (col_w, col_h), Image.LANCZOS, centering=centering), (j * col_w, 0))
    d = ImageDraw.Draw(out_im)
    d.rectangle((size // 2 - 3, 0, size // 2 + 3, col_h), fill=PAPER)
    d.text((34, height - 32), 'Before', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    d.text((size // 2 + 34, height - 32), 'After', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    save(out_im, out, size=size)


def doctor_photo():
    """The owner's portrait of the SKINOFAB doctor in her clinic holding the bottle (owner/doctor-clinic.webp, 29 Oct
    2026). The image model misspelt the small print under the wordmark ("PORN" for PDRN, "PEPTIOE"): that block is
    painted out with the bottle's own black, column by column from the rows above and below it (feathered over 4 px,
    no text within them), and set again in the label's sizes and greys: ADAPTIVE PEPTIDE / FOUNDATION / PDRN /
    30 mL / 1.01 fl oz. The wordmark, her hand and the rest of the photo are untouched."""
    a = np.asarray(Image.open(OWNER / 'doctor-clinic.webp').convert('RGB')).astype(np.float32)
    assert a.shape[:2] == (1402, 1122), 'doctor-clinic.webp changed: measure the label block again'
    paint_out(a, (304, 671, 383, 734), (662, 668), (733, 740))
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    for text, cx, cy, width, cap, tone in (('ADAPTIVE PEPTIDE', 342, 680.5, 62, 6.0, 236), ('FOUNDATION', 343, 688.5, 44, 6.0, 236),
                                           ('PDRN', 345.5, 706, 15, 4.6, 205), ('30 mL / 1.01 fl oz', 345, 725, 42, 5.0, 214)):
        small = label_mask(text, width, cap)
        im.paste(Image.new('RGB', small.size, (tone,) * 3), (int(round(cx - small.width / 2)), int(round(cy - small.height / 2))), small)
    save(ImageOps.fit(im, (1080, 1350), Image.LANCZOS, centering=(0.5, 0.3)), 'doctor', size=1350)


def paint_out(a, box, top_rows, bot_rows, feather=4.0):
    """Paint a block of a photo (a: float array, changed in place) out with its own surface: box (x0, y0, x1, y1) is
    filled column by column from the median of top_rows to the median of bot_rows (row ranges with nothing in them),
    with a little grain, feathered into the photo over feather px."""
    x0, y0, x1, y1 = box
    top, bot = np.median(a[top_rows[0]:top_rows[1], x0:x1], axis=0), np.median(a[bot_rows[0]:bot_rows[1], x0:x1], axis=0)
    t = np.linspace(0, 1, y1 - y0)[:, None, None]
    fill = top[None] * (1 - t) + bot[None] * t + np.random.default_rng(7).normal(0, 1.4, (y1 - y0, x1 - x0, 1))
    yy, xx = np.mgrid[0:y1 - y0, 0:x1 - x0]
    wgt = np.clip(np.minimum.reduce([xx, x1 - x0 - 1 - xx, yy, y1 - y0 - 1 - yy]).astype(np.float32) / feather, 0, 1)[..., None]
    a[y0:y1, x0:x1] = a[y0:y1, x0:x1] * (1 - wgt) + fill * wgt


def old_routine():
    """The sales page's "old routine" card: a woman in her late fifties at a vanity crowded with a primer, four
    foundations in four shades, concealers, spilled powder, a contour palette and a cup of brushes, swatches on the back
    of her hand, fed up (gen/old-routine.png, GPT Image 2 through 4SToken, 29 Oct 2026, the owner's request). The model's
    made-up small print on the white primer tube is painted out with the tube's own white; nothing else is changed."""
    a = np.asarray(Image.open(GEN / 'old-routine.png').convert('RGB')).astype(np.float32)
    assert a.shape[:2] == (1254, 1254), 'old-routine.png changed: measure the tube print again'
    paint_out(a, (84, 948, 142, 984), (940, 946), (986, 992))
    save(Image.fromarray(a.clip(0, 255).astype(np.uint8)), 'old-routine', size=1080)


# the four steps of "How to use it", each a still from the demo clips the page plays (the owner's ask, 29 Oct 2026:
# an image for each step): (source clip, second, where her face sits). No clip shows a moisturiser, so step 1 is
# her bare skin before she starts.
STEP_FRAMES = {'step-1': ('gj-43e0f648-cut', 0.4, 0.18), 'step-2': ('gj-43e0f648-cut', 24.0, 0.2),
               'step-3': ('gj-41b77ec4-clean', 7.5, 0.24), 'step-4': ('gj-b705ce67', 8.6, 0.22),
               # listicle reason 4 ("One pump, your fingertips"): her fingertips working it in (the brush photo was not)
               'reason-fingers': ('gj-88d49199', 14.0, 0.2)}


def step_frames():
    """Each step's still, square on her face, 600 px."""
    for key, (src, t, y) in STEP_FRAMES.items():
        tmp = _frames_dir(key) / 'f.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', str(BRAND / 'videos' / f'{src}.mp4'), '-frames:v', '1', str(tmp)], check=True)
        im = Image.open(tmp).convert('RGB')
        save(ImageOps.fit(im, (im.width, im.width), Image.LANCZOS, centering=(0.5, y)), key, size=600)
        shutil.rmtree(tmp.parent, ignore_errors=True)


def guarantee_seal():
    """The guarantee seal cut out of its cream square (guarantee.jpg) with a soft edge, as a PNG, for the trust card's
    tinted panel (the square showed on it)."""
    im = Image.open(OUT / 'guarantee.jpg').convert('RGB')
    a = np.asarray(im).astype(np.float32)
    bg = np.median(np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3)]), axis=0)
    alpha = np.clip((np.abs(a - bg).max(axis=2) - 10) * 12, 0, 255).astype(np.uint8)
    m = Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(0.8))
    rgba = im.convert('RGBA'); rgba.putalpha(m)
    rgba = rgba.crop(m.getbbox()); rgba.thumbnail((360, 360), Image.LANCZOS)
    rgba.quantize(colors=128, method=Image.Quantize.FASTOCTREE).save(OUT / 'guarantee-seal.png', optimize=True)   # a palette PNG: a third of the size
    print('guarantee-seal', rgba.size)


def compare_heads():
    """The sales page's comparison table heads: our bottle cut tall from its packshot (bottle.jpg), and for regular
    foundation five overlapping swatches from fair to deep (the shade you have to guess), drawn, on white. Both are
    shown multiplied onto the table, so their white drops away."""
    save(Image.open(OUT / 'bottle.jpg').convert('RGB').crop((360, 40, 720, 1040)), 'cmp-ours', size=330)
    K, W, H = 4, 300, 330
    im = Image.new('RGB', (W * K, H * K), PAPER)
    shades = [(243, 214, 190), (229, 189, 158), (205, 156, 118), (166, 112, 78), (112, 72, 48)]
    shadow = Image.new('L', im.size, 0)
    sd = ImageDraw.Draw(shadow)
    spots = [(78, 120), (150, 92), (222, 120), (112, 205), (188, 205)]
    r = 52
    for x, y in spots: sd.ellipse(((x - r + 3) * K, (y - r + 7) * K, (x + r + 3) * K, (y + r + 7) * K), fill=60)
    im.paste(Image.new('RGB', im.size, (120, 110, 100)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(8 * K)))
    d = ImageDraw.Draw(im)
    for (x, y), c in zip(spots, shades):
        d.ellipse(((x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K), fill=c, outline=PAPER, width=3 * K)
    save(im.resize((W, H), Image.LANCZOS), 'cmp-theirs', size=330)


def label_mask(text, width, cap, angle=0.0, weight='Medium', K=8):
    """One line of the bottle label's small print as a mask: Montserrat (Medium) drawn 8x at cap px cap height, condensed
    to width px (the label's own width for that line), turned angle degrees counter-clockwise, brought down to 1x."""
    f = P.sans(int(round(cap / 0.70 * K)), weight)
    l, tp, r, b = f.getbbox(text)
    lay = Image.new('L', (r - l + 4 * K, b - tp + 4 * K), 0)
    ImageDraw.Draw(lay).text((2 * K - l, 2 * K - tp), text, font=f, fill=255)
    lay = lay.resize((int(width * K + 4 * K * width * K / (r - l)), lay.height), Image.LANCZOS)
    if angle: lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
    return lay.resize((max(1, round(lay.width / K)), max(1, round(lay.height / K))), Image.LANCZOS)


def howto_loop(encode=True):
    """The listicle's how-it-works loop, v3 (live review 6: the store's loop faded the dots out under a still hand and
    cut her forehead): eleven seconds of the demo clip the sales page plays with sound (brand/videos/gj-43e0f648-cut,
    21.5 to 32.5 s): the white dots go on, then the brush blends them into her tone. Silent, 4:5 on her whole head,
    at the clip's own 606 px width; the poster is a frame with every dot on."""
    src, t0, dur = BRAND / 'videos' / 'gj-43e0f648-cut.mp4', 21.5, 11.0
    vf = 'crop=606:758:0:40'
    tmp = _frames_dir('howto') / 'p.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0 + 2.8), '-i', str(src), '-frames:v', '1', '-vf', vf, str(tmp)], check=True)
    save(Image.open(tmp), 'howto-poster', size=758)
    if not encode: return
    for ext, args in (('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '29',   # about 400 kB for the 11 s
                      '-pix_fmt', 'yuv420p', '-movflags', '+faststart']),
                      ('webm', ['-c:v', 'libvpx-vp9', '-crf', '40', '-b:v', '0', '-row-mt', '1', '-pix_fmt', 'yuv420p'])):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-t', str(dur), '-i', str(src), '-vf', vf, '-an', *args, str(OUT / f'howto.{ext}')], check=True)

def portrait(src, out, size=1080, crop=None, centering=(0.5, 0.3)):
    """A persona photo on its own, square: the stand-in for a reason whose before/after is not made yet. crop: (left,
    top, right, bottom) as fractions, the part of the photo to show."""
    im = Image.open(PERSONA / f'{src}.jpg').convert('RGB')
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    save(ImageOps.fit(im, (size, size), Image.LANCZOS, centering=centering), out, size=size)


def soften_patch(im, box):
    """Flatten a generated photo's pigment inside an ellipse (box as fractions of the image): the mottling blends 60% into a
    blurred copy and its darkest marks lift halfway toward their surround, with a feathered edge. Sun spots and redness
    stay, the solid blotch that read as a bruise at page size does not (the mirror photo, live review 3)."""
    w, h = im.size
    a = np.asarray(im).astype(np.float32)
    blur = np.asarray(im.filter(ImageFilter.GaussianBlur(14))).astype(np.float32)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).ellipse((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])), fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(28))).astype(np.float32)[..., None] / 255
    soft = a * 0.4 + blur * 0.6
    dark = np.clip((blur.mean(-1, keepdims=True) - a.mean(-1, keepdims=True)) / 40, 0, 1)
    soft = soft + (blur - soft) * dark * 0.5
    return Image.fromarray(np.clip(a * (1 - m) + soft * m, 0, 255).astype(np.uint8))


def soften_seam(im, x=512, band=40, probe=6, smooth=25):
    """A split portrait's vertical seam (the two halves of the generated face meet at column x with a step in colour,
    clearest at the chin, live review 5) spread over band px each side: per row, the step between the probe px either
    side is measured, smoothed down the rows, and half of it fades in on the left and half fades out on the right, so
    the halves meet at one colour. Only colour moves; no detail is blurred."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    step = a[:, x + 1:x + 1 + probe].mean(axis=1) - a[:, x - probe:x].mean(axis=1)          # right minus left, per row
    k = np.exp(-0.5 * (np.arange(-3 * smooth, 3 * smooth + 1) / smooth) ** 2); k /= k.sum()
    step = np.stack([np.convolve(np.pad(step[:, c], 3 * smooth, mode='edge'), k, mode='valid') for c in range(3)], axis=1)
    a[:, x - band + 1:x + 1] += (step[:, None, :] / 2) * np.linspace(1 / band, 1, band)[None, :, None]
    a[:, x + 1:x + 1 + band] -= (step[:, None, :] / 2) * np.linspace(1, 1 / band, band)[None, :, None]
    # the seam's own light hairline (its two columns either side) redrawn from the columns beyond it
    l, r = a[:, x - 2].copy(), a[:, x + 3].copy()
    for j, c in enumerate(range(x - 1, x + 3)):
        t = (j + 1) / 5
        a[:, c] = l * (1 - t) + r * t
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def hero_collage():
    """The listicle's top image: two women past 45 holding the bottle by the face, each photo whole and square, side by
    side (2:1, 1688 x 844). The three 2:3 panels it was cut the face of the right-hand woman at the frame and the middle
    woman's forehead, and showed on a phone as a 140 px strip (live review 5). A phone gets one of them on its own,
    square (hero-m, the page's <picture>)."""
    side = 842
    sq = [ImageOps.fit(Image.open(PDP / f'{n}.jpg').convert('RGB'), (side, side), Image.LANCZOS, centering=c)
          for n, c in (('hold-cheek', (0.5, 0.5)), ('hold-grey-hair', (0.5, 0.5)))]
    im = Image.new('RGB', (side * 2 + 4, side), PAPER)
    for i, p in enumerate(sq): im.paste(p, (i * (side + 4), 0))
    save(im, 'hero', size=1688)
    save(ImageOps.fit(Image.open(PDP / 'hold-cheek.jpg').convert('RGB'), (1080, 1080), Image.LANCZOS, centering=(0.5, 0.5)), 'hero-m', size=760)   # phones only: 760 px is 390 at 2x (live review 9)


def offer_card():
    """The listicle's offer image, v4: the 5-bottle pack (the owner's offer of 30 Oct 2026, buy 3, get 2 free) on a warm
    sweep with the Lymphatic Brush's case and the brush in front, each on its own shadow (stage()), no words (the
    page's sf-cta box lists the pack and its gift)."""
    bot = cutout(bottle(1254))
    card_im = Image.open(BRUSH / 'card.jpg').convert('RGB')
    brush = cutout(card_im.crop((250, 180, 830, 515)), dark=None, fill=False)
    case = cutout(card_im.crop((250, 515, 830, 905)), dark=None)
    s = 1080 / 900
    items = [(bot, 355, 560, 400), (bot, 545, 560, 400), (bot, 260, 610, 425), (bot, 450, 626, 440), (bot, 640, 610, 425),
             (case, 245, 838, 170), (brush, 660, 832, 140)]
    save(stage(1080, [(o, x * s, y * s, h * s) for o, x, y, h in items], 'warm'), 'offer')

def reviews(work):
    """Each buyer's own photo, square on her face (kept in brand/adaptive-peptide-foundation/reviews/<key>.jpg)."""
    KEPT.mkdir(parents=True, exist_ok=True)
    for key, (rid, centering) in REVIEW_PHOTOS.items():
        kept = KEPT / f'{key}.jpg'
        photo = Path(work) / 'reviews' / 'photos' / f'{rid.replace("_", "").replace("-", "") if False else rid}-0.jpg' if work else None
        if photo and not photo.exists():                       # the photo files drop the id's dashes and underscores
            photo = Path(work) / 'reviews' / 'photos' / f'{rid.replace("-", "").replace("_", "")}-0.jpg'
        if photo and photo.exists():
            im = Image.open(photo).convert('RGB')
            if len(centering) == 3: crop = FI.face_square(im, *centering)
            else:
                side = min(im.size)
                crop = ImageOps.fit(im, (side, side), Image.LANCZOS, centering=centering)
            crop.thumbnail((600, 600), Image.LANCZOS)
            crop.save(kept, quality=88)
        if not kept.exists(): raise SystemExit(f'no photo for review {key} ({rid}): run with the work dir once')
        im = Image.open(kept)
        if key in REVIEW_TRIM:                                   # padded with a blur of itself: keep the photo's own part
            x0, x1, *y = REVIEW_TRIM[key]; w = im.width
            side = int(w * (x1 - x0)); top = int(im.height * (y[0] if y else 0))
            im = im.crop((int(w * x0), top, int(w * x0) + side, top + side))
        save(im, f'review-{key}', size=600)


# the seconds of a clip's voice that are silenced, by clip key, as (start, end) seconds. None now: the one clip with a
# voice (demo-navy, silenced in two places at live review 8) left the funnel at live review 10.
MUTE = {}


def clip(key, src, poster, label, encode=True):
    """A demo clip at 540 px (H.264 + WebM) and its poster. Nothing is redrawn: the clips are the re-makes the store plays.
    A clip already written is kept, unless its silenced seconds (MUTE) changed since; with encode=False (--no-video)
    none is written, but the poster always is."""
    src_path = BRAND / 'videos' / f'{src}.mp4'
    mute = MUTE.get(key, [])
    af = ['-af', ','.join(f"volume=enable='between(t,{a},{b})':volume=0" for a, b in mute)] if mute else []
    mark = Path(__file__).resolve().parent / 'clips' / f'{key}.mute'                         # the ranges the written clip was encoded with (kept with the tools, not shipped)
    mark.parent.mkdir(exist_ok=True)
    if encode and (mark.read_text() if mark.exists() else '') != repr(mute):
        for ext in ('mp4', 'webm'): (OUT / f'{key}.{ext}').unlink(missing_ok=True)
    for ext, args in (('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '96k']),
                      ('webm', ['-c:v', 'libvpx-vp9', '-crf', '34', '-b:v', '0', '-row-mt', '1', '-c:a', 'libopus', '-b:a', '64k'])):
        out = OUT / f'{key}.{ext}'
        if out.exists() or not encode: continue
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src_path), '-vf', f'scale={CLIP_WIDTH}:-2', *af, *args, str(out)], check=True)
        mark.write_text(repr(mute))
    if poster and poster != 'sharp': save(Image.open(PDP / f'{poster}.jpg'), f'{key}-poster', size=720)
    else:
        # the sharpest frame of the first two seconds (a mid-motion blur as the poster, live review 2), or the frame at 1 s
        tmp = _frames_dir(f'{key}-poster')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-t', '2.2', '-i', str(src_path), '-vf', 'fps=5', str(tmp / 'f%04d.png')], check=True)
        frames = sorted(tmp.glob('f*.png'))
        def sharp(f):
            g = np.asarray(Image.open(f).convert('L'), dtype=np.float32)
            lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
            return float(lap.var())
        best = max(frames, key=sharp) if poster == 'sharp' and frames else (frames[min(5, len(frames) - 1)] if frames else None)
        save(Image.open(best), f'{key}-poster', size=720)
        shutil.rmtree(tmp, ignore_errors=True)
    print(key, 'clip', label[:40])


def drop_flag_caption(im):
    """The store's Korea pack shot without its caption under the flag ("Formulated in Korea / Advanced formula"): at a
    phone's width it was 6 px text inside the picture (live review 11); the page's pill beside it says the same in
    HTML. The caption's rows are refilled, column by column, with the background just above and below it (a soft
    vertical shade), so the flag and the bottle stay as they are."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    H, W = a.shape[:2]
    x0, x1 = int(W * 0.74), W                          # right of the bottle, under the flag
    y0, y1 = int(H * 0.19), int(H * 0.265)
    ink = (255 - a[y0:y1, x0:x1].min(-1)) > 60          # the caption's letters
    rows = np.where(ink.any(1))[0]
    if not len(rows): return im
    top, bot = y0 + rows[0] - 6, y0 + rows[-1] + 7
    above, below = a[top - 4:top].mean(0), a[bot:bot + 4].mean(0)
    w = np.linspace(0, 1, bot - top, dtype=np.float32)[:, None, None]
    a[top:bot, x0:x1] = above[None, x0:x1] * (1 - w) + below[None, x0:x1] * w
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def copies(video=True):
    for name, src in PDP_PHOTOS.items():
        im = Image.open(PDP / f'{src}.jpg')
        if name == 'g-bottle': im = drop_flag_caption(im)
        save(im, name, size=1080 if not name.startswith('gift') else 240)
    save(Image.open(APF / 'composites' / 'two-bottles.jpg'), 'two-bottles', size=1080)
    # the brush: its page's images, in-hand and problem photos, the before/after it already shows (its own illustration
    # label is on the image) and the stick funnel's loop of it
    # (only the ones the brush page shows: its how-to infographic repeated the page's four steps, live review 5, and the
    # hero, tools and channel diagrams were not shown at all)
    for n in ('card', 'how-1', 'compare-ours'):
        save(Image.open(BRUSH / f'{n}.jpg').convert('RGB'), f'brush-{n}', size=1080)
    # the case photo without its baked headline (illegible at card size, live review 2), and the brush's head alone
    # cut from the clean product shot
    case = Image.open(BRUSH / 'case.jpg').convert('RGB'); cw, ch = case.size
    save(ImageOps.pad(case.crop((0, int(ch * 0.27), cw, ch)), (1080, 1080), Image.LANCZOS, color=PAPER), 'brush-case', size=1080)
    card_im = Image.open(BRUSH / 'card.jpg').convert('RGB'); kw, kh = card_im.size
    save(ImageOps.pad(card_im.crop((int(kw * 0.24), int(kh * 0.12), int(kw * 0.76), int(kh * 0.465))), (1080, 1080), Image.LANCZOS, color=PAPER), 'brush-head', size=1080)
    # the features infographic's own headline hedged ("BUILT TO TARGET MORNING PUFFINESS" made the claim the page's words
    # avoid, live review 1): the top band redrawn with the page's wording; the brush's before/after is no longer used
    feat = Image.open(BRUSH / 'features.jpg').convert('RGB')
    fw, fh = feat.size
    fd = ImageDraw.Draw(feat); fd.rectangle((0, 0, fw, int(fh * 0.25)), fill=PAPER)
    fd.text((fw // 2, int(fh * 0.085)), 'FOR THE LOOK OF', font=P.sans(int(fh * 0.028), 'Medium'), fill=SOFT, anchor='ms')
    fd.text((fw // 2, int(fh * 0.155)), 'MORNING PUFFINESS', font=P.sans(int(fh * 0.058), 'Bold'), fill=INK, anchor='ms')
    fd.text((fw // 2, int(fh * 0.215)), 'with a light touch', font=P.serif(int(fh * 0.042), 'Bold', italic=True), fill=(140, 72, 84), anchor='ms')
    save(feat, 'brush-features', size=1080)
    save(Image.open(BRUSH / 'source' / 'in-hand.jpg'), 'brush-in-hand', size=1080)
    save(Image.open(BRUSH / 'source' / 'problem.jpg'), 'brush-problem', size=1080)
    # the stick funnel's loop of the brush, its baked "Illustration" pill (bottom right, on white) painted out of every frame
    # and of the poster (the owner's instruction, 28 Oct 2026: no disclaimer or illustration line on any image)
    pill = dict(x=510, y=824, w=200, h=66)   # the pill's outline spans 520..700 × 834..880 in the 720×900 frame
    src_dir = BRAND / 'stick-funnel' / 'videos'
    poster = Image.open(src_dir / 'up2-how-poster.jpg').convert('RGB')
    ImageDraw.Draw(poster).rectangle((pill['x'], pill['y'], pill['x'] + pill['w'], pill['y'] + pill['h']), fill=(255, 255, 255))
    save(poster, 'brush-how-poster', size=poster.width)
    if video:
        box = f"drawbox=x={pill['x']}:y={pill['y']}:w={pill['w']}:h={pill['h']}:color=white@1:t=fill"
        for ext, args in (('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']),
                          ('webm', ['-c:v', 'libvpx-vp9', '-crf', '30', '-b:v', '0', '-row-mt', '1', '-pix_fmt', 'yuv420p'])):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src_dir / f'up2-how.{ext}'), '-vf', box, '-an', *args, str(OUT / f'brush-how.{ext}')], check=True)
    # the store's how-it-works loop (white dots, blended, one shade) and its poster: no pill, the label's PDRN line
    howto_loop(encode=video)
    shutil.copyfile(ROOT / 'campaigns' / 'skinofab' / 'src' / 'stick-funnel' / 'assets' / 'images' / 'sf' / 'guarantee.jpg', OUT / 'guarantee.jpg')
    # the thank-you page's range cards: the balm's and the serum's store cards
    save(Image.open(BRAND / 'pdrn-balm' / 'card.jpg'), 'more-balm', size=400)
    save(Image.open(BRAND / 'egf-nad-serum' / 'card.jpg'), 'more-serum', size=400)
    shutil.copyfile(BRAND / 'logo' / 'skinofab-wordmark.svg', OUT / 'skinofab-wordmark.svg')
    static = ROOT / 'tools' / 'theme-build' / 'static'
    shutil.copyfile(static / 'skinofab-favicon-32.png', OUT.parent / 'favicon.png')
    shutil.copyfile(static / 'skinofab-favicon-180.png', OUT.parent / 'webclip.png')
    for key, (src, poster, label) in CLIPS.items(): clip(key, src, poster, label, encode=video)
    # v2 (28 Oct 2026): the generated sources in gen/ (the science cross-section with the real bottle, the split-face
    # "wow" portrait, two problem photos), the store's Korean formulator portrait, the stick funnel's ingredient
    # textures (the same ingredients, the same photos)
    wow = ImageOps.fit(soften_seam(Image.open(GEN / 'wow-split.png')), (1080, 1350), Image.LANCZOS, centering=(0.5, 0.35))
    save(wow, 'wow', size=1350)
    # a phone's copy: the sales page's LCP on a slow line (live review 9). Cut to the 5:4 a phone shows (sf-apf.css,
    # object-position 50% 32%) and WebP, not the whole 4:5 JPEG: 115 KB for a 358 x 286 box was 2.8 to 3.2 s on slow
    # 4G (live review 12). 760 px wide is enough for 390 px at 2x; a browser without WebP takes the desktop JPEG.
    for old in OUT.glob('wow-m.*'): old.unlink()
    ImageOps.fit(wow, (760, 608), Image.LANCZOS, centering=(0.5, 0.32)).save(OUT / 'wow-m.webp', quality=78, method=6)
    print('wow-m', (760, 608), 'webp')
    for n in ('problem-mirror', 'problem-orange'):
        im = Image.open(GEN / f'{n}.png').convert('RGB')
        if n == 'problem-mirror': im = soften_patch(im, (0.19, 0.27, 0.47, 0.49))   # her cheek's pigment read as a bruise at page size (live review 3)
        save(ImageOps.fit(im, (1080, 1350), Image.LANCZOS, centering=(0.5, 0.3)), n, size=1350)
    # (doctor_photo() is no longer called: the sales page shows the pack shot with the flag, live review 9, F2)
    old_routine()
    compare_heads()
    step_frames()
    guarantee_seal()
    stick = ROOT / 'campaigns' / 'skinofab' / 'src' / 'stick-funnel' / 'assets' / 'images' / 'sf'
    for n in ('pdrn', 'peptides', 'ha', 'ceramides', 'squalane', 'niacinamide'): shutil.copyfile(stick / f'ing-{n}.jpg', OUT / f'ing-{n}.jpg')


if __name__ == '__main__':
    work = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    for old in OUT.glob('*.jpg'): old.unlink()
    pack_cards()
    hero_collage()
    offer_card()
    # the before/afters (the owner's brief: a before with lines, sun spots and uneven tone, an after with even,
    # glowing skin, the same woman of 45+): the owner's own pairs below; the listicle's lines, dry-skin and ages
    # reasons show a persona photo on its own until their pairs are made
    portrait('age-109', 'reason-lines', centering=(0.5, 0.4))
    # (the generated glow pair is retired too: the owner asked for one of their own pairs on the listicle's shade
    # reason, 29 Oct 2026; it shows the kitchen pair, also on the sales page)
    # (the generated close-up pair is retired: its "after" erased forehead lines and crow's feet, more than a
    # foundation does, live review 5)
    # the owner's three pairs (29 Oct 2026: one woman each, before and after, a fair, an olive and a medium-deep
    # tone): the sales page's before/after row, and the kitchen pair on the listicle's shade reason (the owner's ask)
    # the garden after is shot from about twice as far: brought to the before's scale (live review 6)
    # every after is shot from further away than its before: brought to the before's scale (garden 1.45, live review 6;
    # car and kitchen 1.3, live review 7), then both a little closer on the face (face=1.12)
    for key, centering, z in (('kitchen', (0.5, 0.3), 1.3), ('car', (0.5, 0.3), 1.3), ('garden', (0.5, 0.3), 1.45)):
        split_pair(key, f'ba-{key}', src=OWNER / f'ba-{key}.webp', centering=centering, zoom_after=z, face=1.12)
    portrait('age-255', 'reason-dry', crop=(0.2, 0.0, 0.8, 0.75))
    portrait('age-200', 'promise', crop=(0.08, 0.0, 0.92, 0.84))     # the sales page's Tomorrow at 8 a.m. (the duo photo cut a face, live review 6)
    portrait('age-223', 'reason-ages', crop=(0.25, 0.0, 0.75, 0.5))
    one_shade()
    clinicians_badge()
    science_clip(encode='--no-video' not in sys.argv)
    allday_clip(encode='--no-video' not in sys.argv)
    reviews(work)
    copies(video='--no-video' not in sys.argv)
    # (no image carries a disclaimer or illustration line, the owner's instruction of 28 Oct 2026; the buyers' photos are their own, uncut on
    # the face; no "after" changes a face: the same woman, the same age, her lines softened, not erased)
