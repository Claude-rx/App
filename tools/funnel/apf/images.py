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
PDP_PHOTOS = {'g-hold': 'hold-cheek', 'g-dots': 'dots-eyes-closed', 'g-grey': 'hold-grey-hair', 'g-duo': 'duo-women',
              'g-inside': 'whats-inside', 'g-brush': 'buffing-brush',
              'g-bottle': 'bottle-korea', 'problem': 'problem', 'solution': 'solution-bottle',
              'gift-blender': 'gift-blender', 'gift-mystery': 'gift-mystery', 'gift-shipping': 'gift-shipping'}
# the demo clips (brand/videos/gj-<key>*.mp4): women 45+ with the real bottle; poster from the live page or a frame
CLIPS = {'demo-navy': ('gj-43e0f648-cut', 'poster-navy', 'A woman in her fifties, blonde, in a navy top, dots the foundation on white and blends it in while she talks (60 s, with sound)'),
         'demo-black': ('gj-41b77ec4-clean', 'sharp', 'A woman in her fifties in black pumps the bottle and buffs the foundation in with a brush'),
         'demo-silver': ('gj-88d49199', None, 'A silver-haired woman in her sixties blends the foundation in with her fingers'),
         'demo-robe': ('gj-b705ce67', 'sharp', 'A blonde woman in a grey robe dots the foundation on her cheeks and forehead and buffs it in')}
CLIP_WIDTH = 540


def save(im, name, size=None, q=84):
    im = im.convert('RGB')
    if size and max(im.size) > size: im.thumbnail((size, size), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f'{name}.jpg', quality=q, optimize=True, progressive=True)
    print(name, im.size)


def bottle(size):
    """The bottle on white: the live page's own render (the product sheet's, its grey backdrop already lifted), with
    the label's PDRN line, which that copy lacks: the line is taken from the product sheet's own front render
    (01-front.png, relabelled by tools/persona/relabel_bottles.py), whose label sits 127 px right of and 3 px below this
    one at the same scale, as its light print over the bottle's black (live review 5: the pack shots read without the
    PDRN line every held bottle and the store's photos print)."""
    im = Image.open(PDP / 'solution-bottle.jpg').convert('RGB')
    front = np.asarray(Image.open(APF / '01-front.png').convert('L'), dtype=np.float32)
    fx0, fy0, fx1, fy1, dx, dy = 586, 1046, 668, 1074, -127, -3               # the PDRN line on the front render
    patch = front[fy0:fy1, fx0:fx1]
    bg = np.median(np.concatenate([front[1030:1042, fx0:fx1], front[1080:1100, fx0:fx1]]), axis=0)   # its black, per column
    alpha = np.clip((patch - bg[None]) / (238.0 - bg[None]), 0, 1)[..., None]
    a = np.asarray(im).astype(np.float32)
    region = a[fy0 + dy:fy1 + dy, fx0 + dx:fx1 + dx]
    assert float(region.mean()) < 60, 'solution-bottle.jpg changed: the PDRN line would not land on the black label'
    a[fy0 + dy:fy1 + dy, fx0 + dx:fx1 + dx] = region * (1 - alpha) + 238.0 * alpha
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    # the faint grey smear to the lower right of the base goes (a detached shadow, live reviews 1 and 2); the darker
    # contact shadow under the base stays
    a = np.asarray(im).copy(); y0 = int(a.shape[0] * 0.84)
    band = a[y0:]; band[band.min(axis=2) > 196] = 255; a[y0:] = band
    im = Image.fromarray(a)
    return ImageOps.pad(im, (size, size), Image.LANCZOS, color=PAPER)


def pack_cards():
    """The checkout cards' and the offers' pack images on white, no words (they show at 64 px): 1, 2, 3 and 6 bottles,
    the 3 and the 6 with the free brush."""
    one = bottle(1254)
    bbox = ImageOps.invert(one.convert('L')).point(lambda v: 255 if v > 40 else 0).getbbox()      # the bottle itself
    cut = one.crop(bbox)
    brush = ImageOps.fit(Image.open(BRUSH / 'card.jpg').convert('RGB'), (420, 420), Image.LANCZOS)

    def card(n, with_brush=False, name=''):
        """v2 (28 Oct 2026): with the brush, the bottles stand clear of it (no bottle half hidden behind the brush's
        box: the owner's "the offer image is not good"): a shorter row shifted left, the brush and its case at the
        bottom right on their own."""
        size = 900
        im = Image.new('RGB', (size, size), PAPER)
        if with_brush: h = 560 if n <= 3 else 360
        else: h = 640 if n <= 3 else 400
        b = cut.resize((int(cut.width * h / cut.height), h), Image.LANCZOS)
        gap = 18
        cols = n if n <= 3 else 3
        rows = 1 if n <= 3 else 2
        total_w = cols * b.width + (cols - 1) * gap
        x0 = (size - total_w) // 2 - (130 if with_brush else 0)
        y0 = ((size - rows * h - (rows - 1) * gap) // 2) - (60 if with_brush else 0)
        for i in range(n):
            im.paste(b, (x0 + (i % cols) * (b.width + gap), y0 + (i // cols) * (h + gap)))
        if with_brush:
            br = brush.resize((300, 300) if n > 3 else (340, 340), Image.LANCZOS)
            # pasted by its own mask (what is not its white backdrop), so it never blanks out a bottle behind it
            m = Image.fromarray(((255 - np.asarray(br.convert('L'))) > 10).astype(np.uint8) * 255, 'L').filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
            im.paste(br, (size - br.width - 24, size - br.height - 40), m)
        save(ground(im), name, size=700)
    card(1, name='pack-1'); card(2, name='pack-2'); card(3, True, 'pack-3'); card(6, True, 'pack-6')
    save(ground(bottle(1080)), 'bottle', size=1080)


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
    W, H = 1080, 1196
    im = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 104), 'One shade, no number to guess', font=P.serif(58, 'Bold'), fill=INK, anchor='ms')
    d.text((W // 2, 154), 'It goes on white and blends into your own tone', font=P.sans(30, 'Regular'), fill=SOFT, anchor='ms')
    # nine swatches, fair to deep, each a soft dome with a white rim and a contact shadow
    tones = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in P.SKIN_TONES], dtype=np.float32)
    n, r, gap = 9, 44, 21
    xs = np.linspace(0, len(tones) - 1, n)
    x0, cy, K = (W - (n * 2 * r + (n - 1) * gap)) // 2, 236, 4
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
    cols = (('car', 'Fair skin', (0.5, 0.22), 1.0), ('kitchen', 'Olive skin', (0.5, 0.2), 1.0), ('garden', 'Medium-deep skin', (0.5, 0.22), 1.45))
    cw, g2 = 316, 26
    cx0, top = (W - 3 * cw - 2 * g2) // 2, 330
    def spaced(x, y, text, font, fill):
        w = sum(font.getlength(ch) for ch in text) + 3 * (len(text) - 1)
        x -= w / 2
        for ch in text: d.text((x, y), ch, font=font, fill=fill, anchor='ls'); x += font.getlength(ch) + 3
    lab = P.sans(22, 'Bold')
    for k, (key, word, centering, zoom) in enumerate(cols):
        before, after = pair_halves(Image.open(OWNER / f'ba-{key}.webp'))
        x = cx0 + k * (cw + g2)
        d.text((x + cw // 2, top), word, font=P.sans(30, 'SemiBold'), fill=INK, anchor='ms')
        if zoom > 1:
            aw, ah = after.size; zw, zh = int(aw / zoom), int(ah / zoom)
            after = after.crop(((aw - zw) // 2, int((ah - zh) * 0.12), (aw - zw) // 2 + zw, int((ah - zh) * 0.12) + zh))
        for row, (half, name) in enumerate(((before, 'BEFORE'), (after, 'AFTER'))):
            y = top + 42 + row * (cw + 58)
            spaced(x + cw // 2, y, name, lab, SOFT if row == 0 else INK)
            ph = ImageOps.fit(half, (cw, cw), Image.LANCZOS, centering=centering)
            m = Image.new('L', (cw, cw), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, cw - 1), 18, fill=255)
            im.paste(ph, (x, y + 14), m)
    d.text((W // 2, H - 44), 'One bottle. Three skin tones.', font=P.sans(36, 'Medium'), fill=INK, anchor='ms')
    save(im, 'one-shade', size=1196)


def _encode(frames, key, fps=25):
    """frames (a folder of f0001.png…) as <key>.mp4 (H.264) and <key>.webm (VP9), silent, and the last frame as
    the poster."""
    for ext, args in (('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']),
                      ('webm', ['-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0', '-row-mt', '1', '-pix_fmt', 'yuv420p'])):   # yuv420p: an RGB VP9 painted blank in some captures (live review 2)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', str(frames / 'f%04d.png'), '-an', *args, str(OUT / f'{key}.{ext}')], check=True)


def _frames_dir(key):
    import tempfile
    return Path(tempfile.mkdtemp(prefix=f'{key}-'))


def science_clip(encode=True, w=1080, fps=25, seconds=6.0):
    """The serum-absorption loop drawn from the generated cross-section still: the drop leaves the pump, lands, and
    the serum's blue sinks down through the right block while the cream on the left stays on top; then it loops.
    No words (the page's words carry what it shows). science-poster.jpg is the still with the serum in."""
    src = Image.open(GEN / 'science-cross-section.png').convert('RGB')
    src = src.resize((w, round(src.height * w / src.width)), Image.LANCZOS)
    a = np.asarray(src).astype(np.float32)
    H, W = a.shape[:2]
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
    y_cut = int(H * 0.54)
    # below the cut the right block borrows the left block's dermis (the same render, one block-width to the left), so no
    # pale channel marks where the blue was; the seam is feathered
    dx = W * 457 // 1080
    deep = FI._blur(blue.astype(np.float32), 6.0)[..., None]; deep[: y_cut] = 0
    clone = a.copy(); clone[:, dx:] = a[:, : W - dx]
    held = a * (1 - deep) + clone * deep
    save(Image.fromarray(np.clip(held, 0, 255).astype(np.uint8)), 'science-poster', size=w)
    if not encode: return
    # the falling drop in the still: cut out (its box, as fractions of the still), its place filled white
    bx0, by0, bx1, by1 = int(W * 0.60), int(H * 0.25), int(W * 0.66), int(H * 0.355)
    box = a[by0:by1, bx0:bx1]
    dmask = FI._blur(((255 - box.min(-1)) > 20).astype(np.float32), 1.0)[..., None]
    drop = box.copy()
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
                                               (tuple(int(theirs0[c] + (theirs1[c] - theirs0[c]) * p) for c in range(3)), 'One that oxidises', 'can turn orange by noon'))):
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


def split_pair(key, out, size=1080, height=900, band=100, src=None, centering=(0.5, 0.35)):
    """A generated split portrait (gen/ba-split-<key>.png: the same woman twice in one frame, her bare skin with its
    lines, spots and redness on the left, the foundation on with an even, luminous tone on the right, a white line
    between) laid out as the pages' before/after: each half fitted to its column (no upscaling at 1376 px wide),
    Before / After in ink on a white band at the foot, a white line between the halves (no disclaimer line: the owner's
    instruction, 28 Oct 2026)."""
    halves = pair_halves(Image.open(src or GEN / f'ba-split-{key}.png'))
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
               'step-3': ('gj-41b77ec4-clean', 7.5, 0.24), 'step-4': ('gj-b705ce67', 8.6, 0.22)}


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
    """The store's how-it-works loop (white dots, blended, one shade; brand/adaptive-peptide-foundation/howto/, 864x1080)
    and its poster, for the listicle. Its baked "Illustration" pill (bottom right, over her neck, 697..842 x 1022..1056)
    is cut away: the frame is cropped to 812x1015 (8 px off the left, 44 off the right, 65 off the bottom, still 4:5) and
    scaled back to 864x1080 (the owner's instruction, 28 Oct 2026: no disclaimer or illustration line on any image).
    The bottle stands still in every frame, so its label gets the PDRN line the real label carries (as on the doctor's
    and the solution bottle), set once in the label's tilt (7.6 deg), sizes and grey, between FOUNDATION and 30 mL."""
    src = APF / 'howto'
    poster = Image.open(src / 'howto-poster.jpg').convert('RGB')
    assert poster.size == (864, 1080), 'howto-poster.jpg changed: measure the label and the pill again'
    mask = label_mask('PDRN', 28, 6.4, angle=7.6, weight='SemiBold')   # a touch above the label's 0.77 cap, SemiBold: thinner, the encoded D read as an O
    lay = Image.new('RGBA', poster.size, (0, 0, 0, 0))
    lay.paste(Image.new('RGBA', mask.size, (205, 205, 207, 255)), (int(round(138.4 - mask.width / 2)), int(round(933.9 - mask.height / 2))), mask)
    crop, size = (8, 0, 820, 1015), (864, 1080)
    save(Image.alpha_composite(poster.convert('RGBA'), lay).convert('RGB').crop(crop).resize(size, Image.LANCZOS), 'howto-poster', size=864)
    if not encode: return
    tmp = _frames_dir('howto') / 'pdrn.png'
    lay.save(tmp)
    vf = f'[0:v][1:v]overlay=0:0,crop={crop[2] - crop[0]}:{crop[3] - crop[1]}:{crop[0]}:{crop[1]},scale={size[0]}:{size[1]}:flags=lanczos,format=yuv420p'
    for ext, args in (('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-movflags', '+faststart']),    # about the source's own size
                      ('webm', ['-c:v', 'libvpx-vp9', '-crf', '35', '-b:v', '0', '-row-mt', '1'])):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src / f'howto.{ext}'), '-i', str(tmp), '-filter_complex', vf, '-an', *args,
                        str(OUT / f'howto.{ext}')], check=True)


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
    save(ImageOps.fit(Image.open(PDP / 'hold-cheek.jpg').convert('RGB'), (1080, 1080), Image.LANCZOS, centering=(0.5, 0.5)), 'hero-m', size=1080)


def offer_card():
    """The listicle's offer image, v2 (28 Oct 2026, the owner: the lettered composite was not good): a flat lay with
    no words, the three bottles standing on the left, the three gifts (the Lymphatic Brush with its case, the Blender
    brush, the mystery gift) stacked on the right, grounded shadows. The words are the page's (sf-cta)."""
    size = 1080
    im = Image.new('RGB', (size, size), PAPER)
    one = bottle(1254)
    bbox = ImageOps.invert(one.convert('L')).point(lambda v: 255 if v > 40 else 0).getbbox()
    cut = one.crop(bbox)
    h = 700
    b = cut.resize((int(cut.width * h / cut.height), h), Image.LANCZOS)
    gap = 22
    x0, y0 = 70, (size - h) // 2 - 20
    for i in range(3): im.paste(b, (x0 + i * (b.width + gap), y0))
    tiles = [(BRUSH / 'card.jpg', 0.0), (PDP / 'gift-blender.jpg', 0.0), (PDP / 'gift-mystery.jpg', 0.0)]
    t, tg = 292, 18
    tx = size - t - 60
    ty0 = (size - 3 * t - 2 * tg) // 2
    for k, (path, _) in enumerate(tiles):
        tile = ImageOps.fit(Image.open(path).convert('RGB'), (t, t), Image.LANCZOS)
        mask = Image.new('L', (t, t), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, t - 1, t - 1), 26, fill=255)
        im.paste(tile, (tx, ty0 + k * (t + tg)), mask)
        ImageDraw.Draw(im).rounded_rectangle((tx, ty0 + k * (t + tg), tx + t - 1, ty0 + k * (t + tg) + t - 1), 26, outline=(226, 222, 216), width=2)
    save(ground(im), 'offer')


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
        save(Image.open(kept), f'review-{key}', size=600)


def clip(key, src, poster, label, encode=True):
    """A demo clip at 540 px (H.264 + WebM) and its poster. Nothing is redrawn: the clips are the re-makes the store plays.
    A clip already written is kept; with encode=False (--no-video) none is written, but the poster always is."""
    src_path = BRAND / 'videos' / f'{src}.mp4'
    for ext, args in (('mp4', ['-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '96k']),
                      ('webm', ['-c:v', 'libvpx-vp9', '-crf', '34', '-b:v', '0', '-row-mt', '1', '-c:a', 'libopus', '-b:a', '64k'])):
        out = OUT / f'{key}.{ext}'
        if out.exists() or not encode: continue
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src_path), '-vf', f'scale={CLIP_WIDTH}:-2', *args, str(out)], check=True)
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


def copies(video=True):
    for name, src in PDP_PHOTOS.items(): save(Image.open(PDP / f'{src}.jpg'), name, size=1080 if not name.startswith('gift') else 240)
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
    save(ImageOps.fit(soften_seam(Image.open(GEN / 'wow-split.png')), (1080, 1350), Image.LANCZOS, centering=(0.5, 0.35)), 'wow', size=1350)
    for n in ('problem-mirror', 'problem-orange'):
        im = Image.open(GEN / f'{n}.png').convert('RGB')
        if n == 'problem-mirror': im = soften_patch(im, (0.19, 0.27, 0.47, 0.49))   # her cheek's pigment read as a bruise at page size (live review 3)
        save(ImageOps.fit(im, (1080, 1350), Image.LANCZOS, centering=(0.5, 0.3)), n, size=1350)
    doctor_photo()
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
    for key, centering in (('kitchen', (0.5, 0.3)), ('car', (0.5, 0.3)), ('garden', (0.5, 0.3))):
        split_pair(key, f'ba-{key}', src=OWNER / f'ba-{key}.webp', centering=centering)
    portrait('age-255', 'reason-dry', crop=(0.2, 0.0, 0.8, 0.75))
    portrait('age-223', 'reason-ages', crop=(0.25, 0.0, 0.75, 0.5))
    one_shade()
    science_clip(encode='--no-video' not in sys.argv)
    allday_clip(encode='--no-video' not in sys.argv)
    reviews(work)
    copies(video='--no-video' not in sys.argv)
    # (no image carries a disclaimer or illustration line, the owner's instruction of 28 Oct 2026; the buyers' photos are their own, uncut on
    # the face; no "after" changes a face: the same woman, the same age, her lines softened, not erased)
