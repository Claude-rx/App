"""The stick page's "Adaptive color science" loop: how the stick works on the skin, in four steps and an end card, an
illustration that says so in its corner. It plays in the science block's picture slot (twin.py, apf_copy.kbeauty_html).

  1-2  the capsules: the white cream with its pigment capsules, the stick's own kabuki end buffing it in small
       circles, the cream turning into a skin tone wherever the brush has been (buff_frames: capsules-a and -b, the
       cheek without a brush, and kabuki.jpg, the stick's brush end on white, moved over them)
  3    the soft-focus spheres (silica in the formula, SKF-ADFS-001 line 13) scattering light over a fine line
  4    the skincare in the cream: hyaluronic acid spheres taking up water, PDRN, peptides, ceramides (lines 9-27)
  5    the stick, both ends open: one stick, your tone

Each scene is its Kling clip, <name>-kling.mp4 (image to video from <name>-a.jpg), when it is there, played at its
own speed and then dissolved into <name>-b.jpg; else the capsules' brush animation (buff_frames) or a slow push-in
dissolving from <name>-a.jpg to <name>-b.jpg. The first Kling clip (27 Oct 2026) buffed with a separate long-handled
flat brush, not the stick's kabuki end (stick review 12: against "no separate brush"), so it is not used; a new one
must start from a frame with the stick's own brush. The blur and ha scenes wait for credits (Higgsfield, Kie.ai and
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
from scipy import ndimage

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
                       (2.0, 6.4, '2', 'Buff: the capsules break', 'The color comes out to meet your tone')]),
    (4.2, 'blur', [(0.0, 4.2, '3', 'Soft-focus spheres', 'They scatter light: lines look softer')]),
    (4.2, 'ha', [(0.0, 4.2, '4', 'Skincare in every swipe', 'PDRN, peptides, ceramides, HA')]),
    (3.4, 'end', [(0.0, 3.4, '', 'One stick. Your tone.', 'Fair to medium skin, brush built in')]),
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


def brush_cutout():
    """kabuki.jpg (the stick's brush end on white, its tube running off the top-right corner) as (RGB image,
    alpha, the head's centre): the alpha from how dark it is (its contact shadow left out), the white
    fringe taken out of its edge, and the tube carried on 1000 px past where the photo cuts it, so no cut end shows
    in the frame: turned so the tube points right, its last whole cross-section repeated, turned back."""
    kb = Image.open(SRC / 'kabuki.jpg').convert('RGB')
    rgb = np.asarray(kb).astype(np.float32)
    # only the dark product: its grey contact shadow beside the tube (lum 150-215) came along as a light band
    alpha = np.clip((150 - rgb.mean(2)) / 50, 0, 1)
    alpha = ndimage.grey_erosion(alpha, size=(3, 3))
    # the edge's colour without the white behind it (un-mixed), so no light halo on the cheek
    a3 = np.maximum(alpha[..., None], 1e-3)
    rgb = np.clip((rgb - 255 * (1 - a3)) / a3, 0, 255)
    ky, kx = np.nonzero(alpha > 0.5)
    tip = np.argmin(kx - ky)
    head = np.array([kx[tip], ky[tip]]) + 250 / np.sqrt(2) * np.array([1, -1])
    ang = np.degrees(np.arctan2(-(0 - head[1]), kb.width - head[0]))      # the tube's direction, to the top right
    rgba = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), 'RGBA')
    big = Image.new('RGBA', (kb.width * 3, kb.height * 3), (0, 0, 0, 0)); big.paste(rgba, (kb.width, kb.height))
    cx, cy = head[0] + kb.width, head[1] + kb.height
    rot = np.asarray(big.rotate(-ang, resample=Image.BICUBIC, center=(cx, cy))).copy()   # the tube now points right
    # the tube's height in each column past the head: from just past the ringed collar (where the body reaches its
    # full width) one clean cross-section is repeated, so the body is plain matte black (the render drew faint
    # letter-like marks there, and the photo's corner cuts it at a slant further on)
    heights = (rot[:, :, 3] > 128).sum(0)
    cols = np.arange(rot.shape[1])
    tube = (cols > cx + 300) & (heights > 0)
    full = np.percentile(heights[tube], 90)
    cut = int(cols[tube & (heights >= 0.97 * full)].min()) + 30
    rot[:, cut:cut + 1000] = np.repeat(rot[:, cut:cut + 1], 1000, axis=1)
    back = Image.fromarray(rot, 'RGBA').rotate(ang, resample=Image.BICUBIC, center=(cx, cy))
    bb = back.getbbox()
    back = back.crop(bb)
    out = np.asarray(back).astype(np.float32)
    return Image.fromarray(out[..., :3].astype(np.uint8)), out[..., 3] / 255, np.array([cx - bb[0], cy - bb[1]])


def buff_frames(n):
    """The capsules scene, n frames: the white stroke on the cheek (capsules-a), then the stick's kabuki end
    (kabuki.jpg, its brush end on white, cut out by its whiteness) coming in from the top right, buffing in small
    circles from one end of the stroke to the other and leaving the same way; wherever its head has passed, the
    cheek shows capsules-b (the cream blended in), a little more on each pass; a soft shadow under the brush."""
    import cv2
    load = lambda f: np.asarray(Image.open(SRC / f).convert('RGB').resize((PIC, PIC), Image.LANCZOS)).astype(np.float32)
    a, b = load('capsules-a.jpg'), load('capsules-b.jpg')
    # b is an edit of a: aligned to it (ECC), so only the cream changes
    ga, gb = (cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) for x in (a, b))
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        _, warp = cv2.findTransformECC(ga, gb, warp, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
        b = cv2.warpAffine(b, warp, (PIC, PIC), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    except cv2.error:
        pass
    # the stroke: the largest white, unsaturated patch; its long axis is the brush's path
    # (light, unsaturated, its beige capsules closed over and its holes filled: the capsules split a stricter mask
    # into pieces, and the brush then buffed only one of them)
    white = (a.mean(2) > 200) & (a.max(2) - a.min(2) < 50)
    whole = ndimage.binary_fill_holes(ndimage.binary_closing(white, iterations=8))
    lab, k = ndimage.label(whole)
    stroke = lab == (np.argmax(ndimage.sum(whole, lab, range(1, k + 1))) + 1)
    ys, xs = np.nonzero(stroke)
    c = np.array([xs.mean(), ys.mean()])
    u = np.linalg.eigh(np.cov(np.stack([xs - c[0], ys - c[1]])))[1][:, -1]
    if u[0] < 0: u = -u                                        # pointing right (the stroke's top-right end)
    t = (xs - c[0]) * u[0] + (ys - c[1]) * u[1]
    p0, p1 = c + u * np.percentile(t, 92), c + u * np.percentile(t, 8)    # its two ends, top right first
    # the brush: its alpha from how dark it is (its contact shadow, light grey, left out), scaled so the head is
    # about the stroke's width; the head's centre in kabuki.jpg is 250 px up-right of its lower-left tip
    kb, alpha, head = brush_cutout()
    width = np.percentile(np.abs((xs - c[0]) * -u[1] + (ys - c[1]) * u[0]), 90) * 2
    sc = 0.95 * width / 500                                    # the head is about 500 px across in kabuki.jpg
    kw, kh = round(kb.width * sc), round(kb.height * sc)
    rgb = np.asarray(kb.resize((kw, kh), Image.LANCZOS)).astype(np.float32)
    al = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((kw, kh), Image.LANCZOS)).astype(np.float32) / 255
    hc, r = head * sc, 0.55 * width                          # the head's reach: the stroke's whole width on its way
    yy, xx = np.mgrid[0:PIC, 0:PIC]
    off = np.array([PIC * 0.8, -PIC * 0.8])                    # off the frame, top right
    T = lambda sec: round(sec * FPS)
    t_in, t_on, t_off, t_out = T(1.4), T(2.0), T(5.2), T(5.8)
    acc = np.zeros((PIC, PIC), np.float32)
    out = []
    for i in range(n):
        if i < t_in: pos = None
        elif i < t_on: pos = p0 + off * (1 - ease((i - t_in) / (t_on - t_in)))
        elif i < t_off:
            q = (i - t_on) / (t_off - t_on)
            w = 2 * np.pi * 3.2 * q                             # small circles as it travels down the stroke
            pos = p0 + (p1 - p0) * ease(q) + 0.2 * width * np.array([np.cos(w), np.sin(w)])
        elif i < t_out: pos = p1 + (p0 - p1) * 0.15 + off * ease((i - t_off) / (t_out - t_off))
        else: pos = None
        if pos is not None and t_on <= i < t_off:
            d = np.exp(-(((xx - pos[0]) ** 2 + (yy - pos[1]) ** 2) / (2 * r ** 2)) ** 2)
            acc = np.minimum(1, acc + 0.16 * d)
        m = acc if i < t_off else np.minimum(1, acc + ease((i - t_off) / (t_out - t_off)))   # the edges finish as it leaves
        frame = a * (1 - m[..., None]) + b * m[..., None]
        if pos is not None:
            x0, y0 = round(pos[0] - hc[0]), round(pos[1] - hc[1])
            layer = np.zeros((PIC, PIC, 3), np.float32); A = np.zeros((PIC, PIC), np.float32)
            sx0, sy0, sx1, sy1 = max(0, -x0), max(0, -y0), min(kw, PIC - x0), min(kh, PIC - y0)
            if sx1 > sx0 and sy1 > sy0:
                layer[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1] = rgb[sy0:sy1, sx0:sx1]
                A[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1] = al[sy0:sy1, sx0:sx1]
            sh = ndimage.shift(ndimage.gaussian_filter(A, 22), (22, 16), order=1) * 0.22
            frame = frame * (1 - sh[..., None])
            frame = frame * (1 - A[..., None]) + layer * A[..., None]
        out.append(Image.fromarray(np.clip(frame + 0.5, 0, 255).astype(np.uint8)))
    return out


def scene_frames(name, seconds):
    n = round(seconds * FPS)
    if (SRC / f'{name}-kling.mp4').exists():
        return kling_frames(SRC / f'{name}-kling.mp4', SRC / f'{name}-b.jpg', n)
    if name == 'capsules' and (SRC / 'kabuki.jpg').exists():
        return buff_frames(n)
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
        d.ellipse((x0, PIC + 62, x0 + 58, PIC + 120), fill=INK + (a,))
        d.text((x0 + 29, PIC + 92), step, font=font(32, 'Bold'), fill=(255, 255, 255, a), anchor='mm')
        tx = x0 + 78
    else:
        tx = x0
    # (the page shows the loop about 360 px wide on a phone, 0.41 of its size: 48 and 34 px read as 20 and 14 px;
    # 40 and 27 read as 16 and 11, stick review 12)
    d.text((tx, PIC + 104), title, font=font(48, 'Bold', serif=True), fill=INK + (a,), anchor='ls')
    d.text((x0, PIC + 172), line, font=font(34, 'Medium'), fill=SOFT + (a,), anchor='ls')


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
        if i >= len(pics) - f:
            # the loop's seam: the end card's line gives way to step 1's as the picture dissolves into the first frame
            # (it used to jump back on a still picture, funnel review 3)
            p = ease((i - (len(pics) - f) + 1) / (f + 1))
            first = caps[0][0]
            band(d, cap[2], cap[3], cap[4], alpha * (1 - p))
            band(d, first[2], first[3], first[4], p)
        else:
            band(d, cap[2], cap[3], cap[4], alpha)
        d.rounded_rectangle((W - 236, 20, W - 20, 72), 26, fill=(255, 255, 255, 225))
        d.text((W - 128, 46), 'Illustration', font=font(28, 'Medium'), fill=(50, 50, 50, 255), anchor='mm')
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
