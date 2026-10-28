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
- the persona photos (brand/persona/age-*.jpg, women 45+ made for the store) for the before/afters: the "after" is
  the same photo with the skin's colour evened out and nothing else (funnel_images.even_tone, the stick funnel's
  honest after: every line, pore and the face's shape kept), and every one says on the image that it is an AI
  illustration, not a customer photo;
- the buyers' own photos (reviews/photos-approved.txt), square on the face;
- the seven demo clips the homepage plays (brand/videos/gj-*, the old bottle replaced by the real one): the four
  with women 45+, at 540 px with a WebM copy, posters from the live page or a frame;
- the store's how-it-works loop (brand/adaptive-peptide-foundation/howto/) and the stick funnel's brush loop
  (brand/stick-funnel/videos/up2-how.*);
- the brush's own images (brand/lymphatic-brush/) and the stick funnel's guarantee seal.
"""
import json, shutil, subprocess, sys
from pathlib import Path
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
         'demo-black': ('gj-41b77ec4-clean', 'poster-black', 'A woman in her fifties in black pumps the bottle and buffs the foundation in with a brush'),
         'demo-silver': ('gj-88d49199', None, 'A silver-haired woman in her sixties blends the foundation in with her fingers'),
         'demo-robe': ('gj-b705ce67', 'poster-robe', 'A blonde woman in a grey robe dots the foundation on her cheeks and forehead and buffs it in')}
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
    return ImageOps.pad(im, (size, size), Image.LANCZOS, color=PAPER)


def pack_cards():
    """The checkout cards' and the offers' pack images on white, no words (they show at 64 px): 1, 2, 3 and 6 bottles,
    the 3 and the 6 with the free brush."""
    one = bottle(1254)
    bbox = ImageOps.invert(one.convert('L')).point(lambda v: 255 if v > 40 else 0).getbbox()      # the bottle itself
    cut = one.crop(bbox)
    brush = ImageOps.fit(Image.open(BRUSH / 'card.jpg').convert('RGB'), (420, 420), Image.LANCZOS)

    def card(n, with_brush=False, name=''):
        size = 900
        im = Image.new('RGB', (size, size), PAPER)
        h = 640 if n <= 3 else 400
        b = cut.resize((int(cut.width * h / cut.height), h), Image.LANCZOS)
        gap = 18
        cols = n if n <= 3 else 3
        rows = 1 if n <= 3 else 2
        total_w = cols * b.width + (cols - 1) * gap
        x0 = (size - total_w) // 2 - (120 if with_brush and n <= 3 else 0)
        y0 = (size - rows * h - (rows - 1) * gap) // 2
        for i in range(n):
            im.paste(b, (x0 + (i % cols) * (b.width + gap), y0 + (i // cols) * (h + gap)))
        if with_brush: im.paste(brush, (size - brush.width - 30, size - brush.height - 60))
        save(im, name, size=700)
    card(1, name='pack-1'); card(2, name='pack-2'); card(3, True, 'pack-3'); card(6, True, 'pack-6')
    save(bottle(1080), 'bottle', size=1080)


def before_after(name, src, out, size=1080, crop=None):
    """A split-screen before/after: the persona photo and the same photo with its skin tone evened out, Before / After and
    the AI line in ink on a white band at the foot, a white line between the halves. crop: (left, top, right, bottom) as
    fractions, the part of the photo to show."""
    im = Image.open(src).convert('RGB')
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    half = ImageOps.fit(im, (size // 2, size - 150), Image.LANCZOS, centering=(0.5, 0.22))
    after = FI.even_tone(half)
    out_im = Image.new('RGB', (size, size), PAPER)
    out_im.paste(half, (0, 0)); out_im.paste(after, (size // 2, 0))
    d = ImageDraw.Draw(out_im)
    d.rectangle((size // 2 - 3, 0, size // 2 + 3, size - 150), fill=PAPER)
    d.text((34, size - 88), 'Before', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    d.text((size // 2 + 34, size - 88), 'After', font=P.sans(42, 'SemiBold'), fill=INK, anchor='ls')
    P.note(d, (34, size - 30), P.AI_NOTE, anchor='ls', size=38)
    save(out_im, out, size=size)


def hero_collage():
    """Three women past 45 with the bottle, side by side (the listicle's top image), 2:3 each."""
    w, h = 560, 840
    panels = [ImageOps.fit(Image.open(PDP / f'{n}.jpg').convert('RGB'), (w, h), Image.LANCZOS, centering=c)
              for n, c in (('hold-cheek', (0.5, 0.4)), ('dots-eyes-closed', (0.35, 0.45)), ('hold-grey-hair', (0.5, 0.4)))]
    im = Image.new('RGB', (w * 3 + 8, h), PAPER)
    for i, p in enumerate(panels): im.paste(p, (i * (w + 4), 0))
    save(im, 'hero', size=1688)


def offer_card():
    """The listicle's offer box image: three bottles and the brush with the gifts named."""
    size = 1080
    im = Image.new('RGB', (size, size), PAPER)
    three = Image.open(OUT / 'pack-3.jpg').convert('RGB').resize((760, 760), Image.LANCZOS)
    im.paste(three, (160, 250))
    d = ImageDraw.Draw(im)
    d.text((60, 110), 'Adaptive Peptide', font=P.serif(84, 'Bold'), fill=INK, anchor='ls')
    d.text((60, 200), 'Foundation', font=P.serif(84, 'Bold', italic=True), fill=INK, anchor='ls')
    d.text((62, 256), 'One adaptive shade · made for skin after 45', font=P.sans(32, 'Medium'), fill=SOFT, anchor='ls')
    f = P.sans(30, 'SemiBold'); word = '3 bottles + FREE Lymphatic Brush + 2 free gifts'
    tw = d.textlength(word, font=f); cx = size / 2
    d.rounded_rectangle((cx - tw / 2 - 30, 930, cx + tw / 2 + 30, 1000), radius=35, fill=INK)
    d.text((cx, 965), word, font=f, fill=PAPER, anchor='mm')
    d.text((size / 2, size - 28), 'Free shipping · 30-day money-back guarantee', font=P.sans(28, 'Medium'), fill=INK, anchor='ms')
    save(im, 'offer')


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
    if poster: save(Image.open(PDP / f'{poster}.jpg'), f'{key}-poster', size=720)
    else:
        frame = OUT / f'{key}-frame.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.0', '-i', str(src_path), '-frames:v', '1', str(frame)], check=True)
        save(Image.open(frame), f'{key}-poster', size=720); frame.unlink()
    print(key, 'clip', label[:40])


def copies(video=True):
    for name, src in PDP_PHOTOS.items(): save(Image.open(PDP / f'{src}.jpg'), name, size=1080 if not name.startswith('gift') else 240)
    save(Image.open(APF / 'composites' / 'two-bottles.jpg'), 'two-bottles', size=1080)
    for n in ('age-109', 'age-223', 'age-255', 'age-200'): save(Image.open(PERSONA / f'{n}.jpg'), n, size=1080)
    # the brush: its page's images, in-hand and problem photos, the before/after it already shows (its own illustration
    # label is on the image) and the stick funnel's loop of it
    for n in ('hero', 'case', 'how-to-use', 'features', 'vs-tools', 'ba-puffy', 'card', 'how-1', 'how-2', 'how-3', 'compare-ours'):
        save(Image.open(BRUSH / f'{n}.jpg'), f'brush-{n}', size=1080)
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


if __name__ == '__main__':
    work = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    for old in OUT.glob('*.jpg'): old.unlink()
    pack_cards()
    hero_collage()
    offer_card()
    # the honest before/afters: four persona photos (women 45+), the after the same photo with the skin's colour evened
    before_after('close-up', PERSONA / 'age-73.jpg', 'ba-closeup')
    before_after('redness', PERSONA / 'age-264.jpg', 'ba-tone', crop=(0.08, 0.0, 0.92, 0.84))
    before_after('spots', PERSONA / 'age-238.jpg', 'ba-spots', crop=(0.1, 0.0, 0.9, 0.8))
    before_after('dry', PERSONA / 'age-107.jpg', 'ba-dry', crop=(0.05, 0.05, 0.95, 0.95))
    reviews(work)
    copies(video='--no-video' not in sys.argv)
    # (every before/after says on the image that it is an AI illustration; the buyers' photos are their own, uncut on
    # the face; no "after" smooths a line, lifts a jaw or changes a face)
