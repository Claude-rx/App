"""The stick page's "Adaptive color science" loop: how the stick works on the skin, in four steps and an end card, an
illustration that says so in its corner. It plays in the science block's picture slot (twin.py, apf_copy.kbeauty_html).

  1-2  the capsules: the white cream with its pigment capsules, the brush buffing it in, the capsules breaking and the
       cream turning into a skin tone
  3    the soft-focus spheres (silica in the formula, SKF-ADFS-001 line 13) scattering light over a fine line
  4    the skincare in the cream: hyaluronic acid spheres taking up water, PDRN, peptides, ceramides (lines 9-27)
  5    the stick, both ends open: one stick, your tone

Each scene is its Kling clip, <name>-kling.mp4 (image to video from <name>-a.jpg), when it is there, played at its
own speed and then dissolved into <name>-b.jpg; else a slow push-in dissolving from <name>-a.jpg to <name>-b.jpg.
On 27 Oct 2026 the capsules have a Kling 3.0 clip; the blur and ha scenes wait for credits (Higgsfield, Kie.ai and
4SToken's video balance were spent): drop their clips in and run this again.

What each step says is what the manufacturing spec states the stick does (section 1, "How it works", and the
functions in section 2) and section 8 allows: no result over time, no "all skin tones" (Shade 1 is fair to medium).

usage: python3 -I tools/persona/stick_science_video.py
Sources: brand/foundation-stick/science/<capsules|blur|ha>-<a|b>.jpg (gpt-image-2 renders, b an edit of a),
<name>-kling.mp4 (optional) and brand/foundation-stick/duo-ends.jpg; science.gif (the same loop, 432 px, for
emails and ads) is made from science.mp4 by ffmpeg.
Writes brand/foundation-stick/science/science.mp4 (H.264, 864 x 1080, 24 fps, silent, faststart), science.webm (VP9)
and science-poster.jpg (its first frame).
"""
import subprocess, shutil, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'brand' / 'foundation-stick' / 'science'
STICK = ROOT / 'brand' / 'foundation-stick'
FONTS = Path(__file__).resolve().parent / 'assets' / 'fonts'
FPS, W, H, PIC = 24, 864, 1080, 864              # 4:5; the picture square on top, the caption band under it
INK, SOFT, LINE = (21, 21, 21), (95, 95, 95), (226, 226, 222)
FADE = 0.5                                        # the dissolve between scenes, seconds
# (seconds, source, captions [(from, to, number, title, line)]); the captions' times are within the scene
SCENES = [
    (6.4, 'capsules', [(0.0, 2.0, '1', 'It goes on white', 'The color waits in tiny capsules'),
                       (2.0, 6.4, '2', 'Buff, and the capsules break', 'The color comes out and meets your tone')]),
    (4.2, 'blur', [(0.0, 4.2, '3', 'Soft-focus spheres', 'They scatter the light, so lines look softer')]),
    (4.2, 'ha', [(0.0, 4.2, '4', 'Skincare in every swipe', 'Hyaluronic acid, PDRN, peptides, ceramides')]),
    (3.4, 'end', [(0.0, 3.4, '', 'One stick. Your tone.', 'For fair to medium skin, the brush built in')]),
]
STEPS = 4


def font(size, weight, serif=False):
    f = ImageFont.truetype(str(FONTS / ('PlayfairDisplay-VF.ttf' if serif else 'Montserrat-VF.ttf')), size)
    f.set_variation_by_name(weight)
    return f


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def square(im, zoom=1.0):
    """im (any square) as the PIC x PIC picture, zoomed in about its centre."""
    s = im.width / zoom
    o = (im.width - s) / 2
    return im.resize((PIC, PIC), Image.LANCZOS, box=(o, o, o + s, o + s))


def kling_frames(path, end, n):
    """The clip at its own speed, then a dissolve into the scene's end still (the capsules' clip stops short of the
    cream fully blended in: it ends on beige streaks), n frames in all, as PIL images."""
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(path), '-vf', f'scale={PIC}:{PIC}:flags=lanczos',
                    str(tmp / 'k%04d.png')], check=True)
    got = sorted(tmp.glob('k*.png'))
    out = [Image.open(g).convert('RGB') for g in got[:n]]
    shutil.rmtree(tmp)
    end, last, m = square(Image.open(end).convert('RGB')), out[-1], n - len(out)
    return out + [Image.blend(last, end, ease((j + 1) / (m * 0.7))) for j in range(m)]


def scene_frames(name, seconds):
    n = round(seconds * FPS)
    if (SRC / f'{name}-kling.mp4').exists():
        return kling_frames(SRC / f'{name}-kling.mp4', SRC / f'{name}-b.jpg', n)
    if name == 'end':
        im = Image.open(STICK / 'duo-ends.jpg').convert('RGB')
        return [square(im, 1.0 + 0.05 * ease(i / n)) for i in range(n)]
    a, b = (Image.open(SRC / f'{name}-{k}.jpg').convert('RGB') for k in 'ab')
    out = []
    for i in range(n):
        t = i / FPS
        p = ease((t - 0.6) / (seconds - 1.6))                    # holds the start, dissolves, holds the end
        z = 1.0 + 0.07 * (i / n)                                 # a slow push-in all the way
        out.append(Image.blend(square(a, z), square(b, z), p))
    return out


def band(d, step, title, line, alpha):
    """The caption band under the picture: the four steps as a progress bar, the step's number, title and line."""
    d.rectangle((0, PIC, W, H), fill=(255, 255, 255, 255))
    gap, x0 = 10, 48
    seg = (W - 2 * x0 - gap * (STEPS - 1)) / STEPS
    for k in range(STEPS):
        x = x0 + k * (seg + gap)
        on = not step or k < int(step)                          # the end card: all four done
        d.rounded_rectangle((x, PIC + 26, x + seg, PIC + 32), 3, fill=INK + (255,) if on else LINE + (255,))
    a = int(255 * alpha)
    if step:
        d.ellipse((x0, PIC + 66, x0 + 52, PIC + 118), fill=INK + (a,))
        d.text((x0 + 26, PIC + 93), step, font=font(28, 'Bold'), fill=(255, 255, 255, a), anchor='mm')
        tx = x0 + 74
    else:
        tx = x0
    d.text((tx, PIC + 100), title, font=font(40, 'Bold', serif=True), fill=INK + (a,), anchor='ls')
    d.text((x0, PIC + 162), line, font=font(27, 'Medium'), fill=SOFT + (a,), anchor='ls')


def main():
    tmp = Path(tempfile.mkdtemp())
    pics, caps = [], []
    for si, (seconds, name, captions) in enumerate(SCENES):
        fr = scene_frames(name, seconds)
        for i, im in enumerate(fr):
            t = i / FPS
            cur = next((c for c in captions if c[0] <= t < c[1]), captions[-1])
            # each caption fades in over 0.3 s; the scene's first fades in only after the dissolve
            lag = FADE if cur is captions[0] and si else 0
            alpha = 1.0 if not si and cur is captions[0] else ease((t - cur[0] - lag) / 0.3)   # the poster shows step 1
            caps.append((cur, alpha)); pics.append(im)
    # the dissolves: the last FADE seconds of each scene laid over the next one's first (and the end card over the
    # first frame, so the loop closes)
    f = round(FADE * FPS)
    starts, at = [], 0
    for seconds, _, _ in SCENES:
        starts.append(at); at += round(seconds * FPS)
    for s in starts[1:]:
        for j in range(f):
            p = ease((j + 1) / (f + 1))
            pics[s + j] = Image.blend(pics[s - f + j], pics[s + j], p)
    for j in range(f):
        p = ease((j + 1) / (f + 1))
        pics[len(pics) - f + j] = Image.blend(pics[len(pics) - f + j], pics[j], p)
    for i, (im, (cap, alpha)) in enumerate(zip(pics, caps)):
        frame = Image.new('RGBA', (W, H), (255, 255, 255, 255))
        frame.paste(im, (0, 0))
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        band(d, cap[2], cap[3], cap[4], alpha)
        d.rounded_rectangle((W - 168, 22, W - 24, 58), 17, fill=(255, 255, 255, 215))
        d.text((W - 96, 40), 'Illustration', font=font(19, 'Medium'), fill=(60, 60, 60, 255), anchor='mm')
        Image.alpha_composite(frame, layer).convert('RGB').save(tmp / f'f{i:04d}.jpg', quality=93)
    shutil.copy(tmp / 'f0000.jpg', SRC / 'science-poster.jpg')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(tmp / 'f%04d.jpg'),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '25', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '-an', str(SRC / 'science.mp4')], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(tmp / 'f%04d.jpg'),
                    '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '38', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2',
                    '-pix_fmt', 'yuv420p', '-an', str(SRC / 'science.webm')], check=True)
    shutil.rmtree(tmp)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(SRC / 'science.mp4'), '-vf',
                    'fps=10,scale=432:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=full[p];'
                    '[b][p]paletteuse=dither=bayer:bayer_scale=4', '-loop', '0', str(SRC / 'science.gif')], check=True)
    for n in ('science.mp4', 'science.webm', 'science-poster.jpg', 'science.gif'): print(SRC / n, (SRC / n).stat().st_size // 1024, 'KB')


main()
