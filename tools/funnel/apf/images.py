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
  even, luminous tone on the right; gen/README.md has the model and prompts) for the before/afters, every one saying
  on the image that it is an AI illustration, not a customer photo; the pairs no image credit could make yet (the
  listicle's lines, dry-skin and ages reasons, the shade panel's three women) show a persona photo (brand/persona/
  age-*.jpg, women 45+ made for the store) on its own, or the shade panel's evened-tone after, until they are made;
- the buyers' own photos (reviews/photos-approved.txt), square on the face;
- the seven demo clips the homepage plays (brand/videos/gj-*, the old bottle replaced by the real one): the four
  with women 45+, at 540 px with a WebM copy, posters from the live page or a frame;
- the store's how-it-works loop (brand/adaptive-peptide-foundation/howto/) and the stick funnel's brush loop
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
    """The bottle on white: the live page's own render (the product sheet's, its grey backdrop already lifted)."""
    im = Image.open(PDP / 'solution-bottle.jpg').convert('RGB')
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
    """The shade objection answered in one picture (the owner's ask, 28 Oct 2026, after a competitor's "16 skin
    tones" panel): a white drop of the foundation blending into a fair, a medium and a deep skin tone under a
    fair-to-deep tone bar. No faces (the persona photos' filtered "afters" showed no difference, live review 2; the
    real pairs wait for image credit), no count of tones (the claims rules), the illustration line in full."""
    W, H = 1080, 1000
    im = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 150), 'One shade, no number to guess', font=P.serif(58, 'Bold'), fill=INK, anchor='ms')
    d.text((W // 2, 202), 'It goes on white and blends into your own tone', font=P.sans(32, 'Regular'), fill=SOFT, anchor='ms')
    x0b, x1b, bh, cy = 60, W - 60, 34, 262
    tones = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in P.SKIN_TONES[:9]]   # fair to deep, as the words say
    xs = np.linspace(0, len(tones) - 1, x1b - x0b)
    lo = np.floor(xs).astype(int).clip(0, len(tones) - 2); f = (xs - lo)[:, None]
    row = (np.array(tones)[lo] * (1 - f) + np.array(tones)[lo + 1] * f).astype(np.uint8)
    bar = Image.fromarray(np.repeat(row[None], bh, 0), 'RGB')
    mask = Image.new('L', bar.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, bar.width - 1, bh - 1), bh // 2, fill=255)
    im.paste(bar, (x0b, cy - bh // 2), mask)
    cw, g, ph = 316, 26, 316
    x0, y0 = (W - 3 * cw - 2 * g) // 2, cy + 90
    yy, xx = np.mgrid[0:ph, 0:cw].astype(np.float32)
    for k, (tone, word) in enumerate(((tones[1], 'Fair'), (tones[4], 'Medium'), (tones[8], 'Deep'))):
        # the tone as a swatch; a white drop at the top left fading into it, as the foundation does as it is blended
        dist = np.sqrt((xx - cw * 0.34) ** 2 + (yy - ph * 0.34) ** 2)
        t = np.clip((dist - 52) / 120, 0, 1)[..., None]
        px = (np.array([255, 255, 255], dtype=np.float32) * (1 - t) + np.array(tone, dtype=np.float32) * t).astype(np.uint8)
        swatch = Image.fromarray(px, 'RGB')
        m = Image.new('L', (cw, ph), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ph - 1), 28, fill=255)
        x = x0 + k * (cw + g)
        im.paste(swatch, (x, y0), m)
        d.text((x + cw // 2, y0 + ph + 52), word, font=P.sans(34, 'SemiBold'), fill=INK, anchor='ms')
    d.text((W // 2, y0 + ph + 150), 'The same white drop, your tone as you blend', font=P.sans(30, 'Medium'), fill=INK, anchor='ms')
    d.text((W // 2, y0 + ph + 198), 'Made for fair to deep skin. Very fair or very deep? Email us first, or let the 30-day guarantee decide.', font=P.sans(22, 'Regular'), fill=SOFT, anchor='ms')
    P.note(d, (W // 2, H - 50), 'Illustration of how the colour blends, not a photo. Results vary.', size=30)
    save(im, 'one-shade', size=1080)


GEN = APF / 'gen'                    # the v2 sources (GPT Image 2 through 4SToken, 28 Oct 2026; gen/README.md has the prompts)


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
    save(src, 'science-poster', size=w)
    if not encode: return
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
    # the falling drop in the still: cut out (its box, as fractions of the still), its place filled white
    bx0, by0, bx1, by1 = int(W * 0.60), int(H * 0.25), int(W * 0.66), int(H * 0.355)
    box = a[by0:by1, bx0:bx1]
    dmask = FI._blur(((255 - box.min(-1)) > 20).astype(np.float32), 1.0)[..., None]
    drop = box.copy()
    for base in (a, dry): base[by0:by1, bx0:bx1] = base[by0:by1, bx0:bx1] * (1 - dmask) + 255 * dmask
    y_nozzle, y_land = int(H * 0.19), int(H * 0.40) - (by1 - by0)
    frames = _frames_dir('science')
    n = int(fps * seconds)
    ys, xs = np.mgrid[0:H, 0:W]
    y_top, y_bot = int(H * 0.40), int(H * 0.92)
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
            frame = dry * (1 - r * bm) + a * (r * bm)
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
    big, small, tiny = P.sans(44, 'SemiBold'), P.sans(26, 'Regular'), P.sans(22, 'Regular')
    for i in range(n):
        p = min(1.0, max(0.0, (i / fps - 0.5) / (seconds - 1.5)))
        im = Image.new('RGB', (W, H), PAPER)
        d = ImageDraw.Draw(im)
        hour = 8 + p * 10
        hh = int(hour); label = f'{hh if hh <= 12 else hh - 12} {"AM" if hh < 12 else "PM"}'
        d.text((W // 2, 92), label, font=P.serif(64, 'Bold'), fill=INK, anchor='ms')
        d.rounded_rectangle((120, 150, W - 120, 164), 7, fill=(232, 228, 222))
        d.rounded_rectangle((120, 150, 120 + int((W - 240) * p), 164), 7, fill=INK)
        for k, (col, title, sub) in enumerate(((ours, 'This foundation', 'the same tone all day'),
                                               (tuple(int(theirs0[c] + (theirs1[c] - theirs0[c]) * p) for c in range(3)), 'One that oxidises', 'orange by the afternoon'))):
            cx = W // 4 + k * (W // 2)
            d.ellipse((cx - 150, 220, cx + 150, 520), fill=col)
            f, fs = big, 44
            while d.textlength(title, font=f) > W // 2 - 60 and fs > 28: fs -= 2; f = P.sans(fs, 'SemiBold')
            d.text((cx, 580), title, font=f, fill=INK, anchor='ms')
            d.text((cx, 622), sub, font=small, fill=SOFT, anchor='ms')
        P.note(d, (W // 2, H - 28), 'Illustration of the pigments, not a photo. Results vary.', size=tiny.size)
        im.save(frames / f'f{i + 1:04d}.png')
    save(Image.open(frames / f'f{n:04d}.png'), 'allday-poster', size=W)
    if encode: _encode(frames, 'allday', fps)
    shutil.rmtree(frames)
    print('allday clip', n, 'frames')


def split_pair(key, out, size=1080, height=900, band=150):
    """A generated split portrait (gen/ba-split-<key>.png: the same woman twice in one frame, her bare skin with its
    lines, spots and redness on the left, the foundation on with an even, luminous tone on the right, a white line
    between) laid out as the pages' before/after: each half fitted to its column (no upscaling at 1376 px wide),
    Before / After and the AI line in ink on a white band at the foot, a white line between the halves."""
    im = Image.open(GEN / f'ba-split-{key}.png').convert('RGB')
    w, h = im.size
    g = np.asarray(im.convert('L'), dtype=np.float32).mean(axis=0)       # the divider: the brightest column near the middle
    lo, hi = int(w * 0.45), int(w * 0.55)
    mid = lo + int(np.argmax(g[lo:hi]))
    halves = (im.crop((0, 0, mid - 6, h)), im.crop((mid + 6, 0, w, h)))
    col_w, col_h = size // 2, height - band
    out_im = Image.new('RGB', (size, height), PAPER)
    for j, half in enumerate(halves):
        out_im.paste(ImageOps.fit(half, (col_w, col_h), Image.LANCZOS, centering=(0.5, 0.35)), (j * col_w, 0))
    d = ImageDraw.Draw(out_im)
    d.rectangle((size // 2 - 3, 0, size // 2 + 3, col_h), fill=PAPER)
    d.text((34, height - 88), 'Before', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    d.text((size // 2 + 34, height - 88), 'After', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    P.note(d, (34, height - 30), P.AI_NOTE, anchor='ls', size=38)
    save(out_im, out, size=size)


def portrait(src, out, size=1080, crop=None, centering=(0.5, 0.3)):
    """A persona photo on its own, square: the stand-in for a reason whose before/after is not made yet. crop: (left,
    top, right, bottom) as fractions, the part of the photo to show."""
    im = Image.open(PERSONA / f'{src}.jpg').convert('RGB')
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    save(ImageOps.fit(im, (size, size), Image.LANCZOS, centering=centering), out, size=size)


def hero_collage():
    """Three women past 45 with the bottle, side by side (the listicle's top image), 2:3 each."""
    w, h = 560, 840
    panels = [ImageOps.fit(Image.open(PDP / f'{n}.jpg').convert('RGB'), (w, h), Image.LANCZOS, centering=c)
              for n, c in (('hold-cheek', (0.5, 0.4)), ('dots-eyes-closed', (0.35, 0.45)), ('hold-grey-hair', (0.5, 0.4)))]
    im = Image.new('RGB', (w * 3 + 8, h), PAPER)
    for i, p in enumerate(panels): im.paste(p, (i * (w + 4), 0))
    save(im, 'hero', size=1688)


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
    for n in ('hero', 'how-to-use', 'vs-tools', 'card', 'how-1', 'how-2', 'how-3', 'compare-ours'):
        save(Image.open(BRUSH / f'{n}.jpg'), f'brush-{n}', size=1080)
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
    for f in ('up2-how.mp4', 'up2-how.webm', 'up2-how-poster.jpg'): shutil.copyfile(BRAND / 'stick-funnel' / 'videos' / f, OUT / f.replace('up2-how', 'brush-how'))
    # the store's how-it-works loop (white dots, blended, the ingredients) and its poster
    for f in ('howto.mp4', 'howto.webm'): shutil.copyfile(APF / 'howto' / f, OUT / f)
    save(Image.open(APF / 'howto' / 'howto-poster.jpg'), 'howto-poster', size=864)
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
    wow = ImageOps.fit(Image.open(GEN / 'wow-split.png').convert('RGB'), (1080, 1350), Image.LANCZOS, centering=(0.5, 0.35))
    d = ImageDraw.Draw(wow); d.rectangle((0, 1350 - 72, 1080, 1350), fill=PAPER)   # the AI line on a white band (grey on skin was unreadable, live review 1)
    P.note(d, (540, 1350 - 26), P.AI_NOTE, fill=INK, size=34)
    save(wow, 'wow', size=1350)
    for n in ('problem-mirror', 'problem-orange'):
        save(ImageOps.fit(Image.open(GEN / f'{n}.png').convert('RGB'), (1080, 1350), Image.LANCZOS, centering=(0.5, 0.3)), n, size=1350)
    save(ImageOps.fit(Image.open(APF / 'doctor.jpg').convert('RGB'), (1080, 1350), Image.LANCZOS, centering=(0.5, 0.3)), 'doctor', size=1350)
    stick = ROOT / 'campaigns' / 'skinofab' / 'src' / 'stick-funnel' / 'assets' / 'images' / 'sf'
    for n in ('pdrn', 'peptides', 'ha', 'ceramides', 'squalane', 'niacinamide'): shutil.copyfile(stick / f'ing-{n}.jpg', OUT / f'ing-{n}.jpg')


if __name__ == '__main__':
    work = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    for old in OUT.glob('*.jpg'): old.unlink()
    pack_cards()
    hero_collage()
    offer_card()
    # the before/afters (28 Oct 2026, the owner's brief: a before with lines, sun spots and uneven tone, an after with
    # even, glowing skin, the same woman of 45+): the sales page's close-up and the listicle's first reason from the
    # generated split portraits; the listicle's lines, dry-skin and ages reasons show a persona photo on its own until
    # their pairs are made (no image credit was left after the first two; gen/README.md)
    split_pair('closeup', 'ba-closeup')
    split_pair('glow', 'ba-glow')
    portrait('age-109', 'reason-lines', centering=(0.5, 0.4))
    portrait('age-255', 'reason-dry', crop=(0.2, 0.0, 0.8, 0.75))
    portrait('age-223', 'reason-ages', crop=(0.25, 0.0, 0.75, 0.5))
    one_shade()
    science_clip(encode='--no-video' not in sys.argv)
    allday_clip(encode='--no-video' not in sys.argv)
    reviews(work)
    copies(video='--no-video' not in sys.argv)
    # (every before/after says on the image that it is an AI illustration; the buyers' photos are their own, uncut on
    # the face; no "after" changes a face: the same woman, the same age, her lines softened, not erased)
