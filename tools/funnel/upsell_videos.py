"""The special offers' "how it works" loops: the product pages' own photos of each product in use, one step a scene,
each under a slow push-in, the step's line in the same white pill as the foundation's loop (tools/persona/howto_video.py),
cross-faded, and back to the first scene so it loops without a jump.

usage: python3 -I tools/funnel/upsell_videos.py
Writes brand/stick-funnel/videos/up<n>-how.mp4 (H.264, 720 x 900, 24 fps, silent, faststart), up<n>-how.webm (the same
in VP9, the page's second source) and up<n>-how-poster.jpg (its first frame) for special offers 2-4; funnel_images.py
copies them into the funnel. Offer 1 (a second stick) plays the stick's own explainer (stick_science_video.py).

Nothing in them moves that the photo doesn't show: no generated motion, so no label is redrawn (the brush has no photo
of it on a face, so its loop is the brush, its how-to card and its case). The photos are AI images, as on the product
pages, and every frame says "Illustration". The steps are the product pages' own (brush_copy, balm_copy, serum_copy:
"How do I use it?").
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BRAND = ROOT / 'brand'
OUT = BRAND / 'stick-funnel' / 'videos'
FONT = ROOT / 'tools' / 'persona' / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
FPS, SIZE, FADE = 24, (720, 900), 0.5
INK = (21, 21, 21)
# the brush's how-to card (1080 px): its four steps' pills, in order (neck, jaw and cheeks, under the eyes, neck again)
TOUR = {'how-to-use': [(30, 280, 560, 410), (30, 465, 560, 595), (30, 650, 560, 780), (25, 835, 555, 965)]}

# each offer's scenes: (product folder, photo, seconds, step number or '', the step's line, fit)
#   fit 'cover' crops the square photo to 4:5 around its middle; 'contain' shows all of it on white (the brush's cards
#   are drawn on white, so the band above and below them doesn't show); 'tour' is 'contain' that walks through the
#   card's steps, one at a time (TOUR: each step's box on the photo, the others dimmed while it is shown)
VIDEOS = {
    2: [('lymphatic-brush', 'source/in-hand', 3.0, '', 'Hundreds of soft tips that bend', 'cover'),
        ('lymphatic-brush', 'how-to-use', 5.2, '', '', 'tour'),
        ('lymphatic-brush', 'card', 3.0, '', '3 minutes, before your foundation', 'contain')],
    3: [('pdrn-balm', 'apply-eye', 2.8, '1', 'Under the eyes', 'cover'),
        ('pdrn-balm', 'apply-smile', 2.8, '2', 'Along smile lines', 'cover'),
        ('pdrn-balm', 'apply-lips', 2.8, '3', 'Around the lips', 'cover'),
        ('pdrn-balm', 'hold-cheek', 2.8, '', 'Press it in, no rubbing', 'cover')],
    4: [('egf-nad-serum', 'drop', 2.8, '1', 'Two drops for your face', 'cover'),
        ('egf-nad-serum', 'apply-cheeks', 2.8, '2', 'Press them in', 'cover'),
        ('egf-nad-serum', 'apply-neck', 2.8, '3', 'Two more, down your neck', 'cover'),
        ('foundation-stick', 'hold-cheek', 2.8, '4', 'Then your stick', 'cover')],
}


def photo(folder, name):
    """The photo the product pages use: brand/<product>/<name>.jpg, else its labelled/ or source/ copy."""
    d = BRAND / folder
    for p in (d / f'{name}.jpg', d / 'labelled' / f'{name}.jpg', d / 'source' / f'{name}.jpg'):
        if p.is_file(): return Image.open(p).convert('RGB')
    raise FileNotFoundError(f'{folder}/{name}')


def toured(im, boxes, local, secs):
    """The card with every step but the one being shown dimmed: all of them first, then each in turn."""
    lead = 0.5
    step = (secs - lead - FADE) / len(boxes)
    if local < lead: return im
    veil = Image.new('L', im.size, 0); d = ImageDraw.Draw(veil)
    for i, box in enumerate(boxes):
        # how much this step is dimmed now: in for the others' turns, out (smoothly) for its own
        t = (local - lead) / step - i
        on = ease((t + 0.25) / 0.25) * (1 - ease((t - 1) / 0.25))
        dim = min(ease((local - lead) / 0.25), 1) * (1 - on)
        if local > secs - FADE: dim *= 1 - ease((local - (secs - FADE)) / (FADE * 0.6))
        d.rounded_rectangle(box, 60, fill=int(170 * dim))
    return Image.composite(Image.new('RGB', im.size, (255, 255, 255)), im, veil)


def frame_of(im, fit, zoom, name='', local=0.0, secs=1.0):
    """The scene at one moment: 4:5, pushed in by zoom (1 = as framed) around its middle."""
    W, H = SIZE
    if fit == 'tour':
        im, fit = toured(im, TOUR[name], local, secs), 'contain'
    if fit == 'cover':
        w, h = im.size
        cw, ch = (int(h * W / H), h) if w / h > W / H else (w, int(w * H / W))
        base = im.crop(((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch))
    else:
        base = Image.new('RGB', (im.width, int(im.width * H / W)), (255, 255, 255))
        base.paste(im, (0, (base.height - im.height) // 2))
    bw, bh = base.size
    vw, vh = bw / zoom, bh / zoom
    box = ((bw - vw) / 2, (bh - vh) / 2, (bw + vw) / 2, (bh + vh) / 2)
    return base.resize(SIZE, Image.LANCZOS, box=box)


def font(size, weight=600):
    f = ImageFont.truetype(str(FONT), size); f.set_variation_by_axes([weight]); return f


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def chip(layer, num, text, alpha, x=28, y=30):
    """A white pill, top left on the overlay: the step's number in a black disc (when it has one) and its line."""
    d = ImageDraw.Draw(layer)
    f, fn = font(25), font(22, 700)
    pad = 56 if num else 22
    w = int(d.textlength(text, font=f)) + pad + 24
    a = int(255 * alpha)
    # a soft shadow and a hairline, so the pill shows on the white cards as on the photos
    sh = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x, y + 3, x + w, y + 57), 27, fill=(0, 0, 0, int(46 * alpha)))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d.rounded_rectangle((x, y, x + w, y + 54), 27, fill=(255, 255, 255, int(240 * alpha)), outline=(0, 0, 0, int(28 * alpha)))
    if num:
        d.ellipse((x + 10, y + 10, x + 44, y + 44), fill=(*INK, a))
        d.text((x + 27, y + 28), num, font=fn, fill=(255, 255, 255, a), anchor='mm')
    d.text((x + pad, y + 28), text, font=f, fill=(*INK, a), anchor='lm')


def render(n, scenes, tmp):
    ims = [(photo(folder, name), secs, num, text, fit, name) for folder, name, secs, num, text, fit in scenes]
    starts, t = [], 0.0
    for _, secs, *_ in ims:
        starts.append(t); t += secs
    total = t
    i = 0
    for k in range(int(round(total * FPS))):
        t = k / FPS
        s = max(j for j, s0 in enumerate(starts) if s0 <= t)
        im, secs, num, text, fit, name = ims[s]
        local = t - starts[s]
        cur = frame_of(im, fit, 1 + 0.07 * (local + FADE) / (secs + FADE), name, local, secs)
        # the last half second fades into the next scene (the last one into the first: the loop has no seam)
        if local > secs - FADE:
            nxt = ims[(s + 1) % len(ims)]
            p = ease((local - (secs - FADE)) / FADE)
            cur = Image.blend(cur, frame_of(nxt[0], nxt[4], 1 + 0.07 * (local - secs + FADE) / (nxt[1] + FADE), nxt[5]), p)
        layer = Image.new('RGBA', SIZE, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        a = min(ease((local - 0.15) / 0.35), 1 - ease((local - (secs - FADE - 0.1)) / 0.35))
        if a > 0 and text: chip(layer, num, text, a)
        d.rounded_rectangle((SIZE[0] - 148, SIZE[1] - 52, SIZE[0] - 20, SIZE[1] - 20), 16, fill=(255, 255, 255, 200))
        d.text((SIZE[0] - 84, SIZE[1] - 36), 'Illustration', font=font(17, 500), fill=(60, 60, 60, 255), anchor='mm')
        Image.alpha_composite(cur.convert('RGBA'), layer).convert('RGB').save(tmp / f'f{i:04d}.jpg', quality=93)
        i += 1


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for n, scenes in VIDEOS.items():
        tmp = Path(tempfile.mkdtemp())
        render(n, scenes, tmp)
        base = OUT / f'up{n}-how'
        shutil.copy(tmp / 'f0000.jpg', f'{base}-poster.jpg')
        frames = ['-framerate', str(FPS), '-i', str(tmp / 'f%04d.jpg')]
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *frames, '-c:v', 'libx264', '-preset', 'slow', '-crf', '25',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', f'{base}.mp4'], check=True)
        # the same frames as VP9, for browsers that ship without H.264 (Chromium builds, some Linux Firefox)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *frames, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38',
                        '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', '-pix_fmt', 'yuv420p', '-an', f'{base}.webm'],
                       check=True)
        shutil.rmtree(tmp)
        for ext in ('mp4', 'webm'):
            p = Path(f'{base}.{ext}'); print(p.relative_to(ROOT), p.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
