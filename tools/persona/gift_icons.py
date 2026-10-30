"""The offer picker's free-gift icons in the brand's black: the blender (a pink sponge in the export) becomes a matte
black sponge, the mystery gift (a pink box) a black box with an ivory ribbon. The shading of each photo is kept: only
its colours are mapped. Originals: tools/persona/assets/source/; results: tools/persona/assets/offer-gift-*.jpg
(apply_persona.py copies them into the theme). The shipping box stays as it is.

usage: python3 -I tools/persona/gift_icons.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent / 'assets'


def load(name):
    return np.asarray(Image.open(HERE / 'source' / name).convert('RGB')).astype(np.float32)


def soft(mask, r=0.8):
    return np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)[..., None] / 255


def save(a, name):
    Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)).save(HERE / name, quality=92, optimize=True)
    print('wrote', HERE / name)


def black(a, mask, lo=16, hi=92):
    """mask's pixels as a neutral dark tone: the photo's own light and shade, stretched over lo..hi."""
    lum = a @ np.array([.299, .587, .114], np.float32)
    v = lum[mask > 0.5]
    l0, l1 = np.percentile(v, 2), np.percentile(v, 99.5)
    t = np.clip((lum - l0) / max(l1 - l0, 1), 0, 1) ** 1.25
    return (lo + t * (hi - lo))[..., None].repeat(3, 2)


# ---- the blender: everything that is pink
a = load('offer-gift-blender.jpg')
R, G, B = a[..., 0], a[..., 1], a[..., 2]
pink = ((R - G) > 14) & ((R - B) > 6)
# how pink each pixel is: its edge pixels (half sponge, half backdrop) take half the black, so the outline stays smooth
m = np.clip(((R - G) - 6) / 22, 0, 1)[..., None]
save(a * (1 - m) + black(a, pink) * m, 'offer-gift-blender.jpg')

# ---- the mystery gift: the box (saturated pink-red) black, the ribbon and tag (pale pink) ivory
a = load('offer-gift-mystery.jpg')
R, G, B = a[..., 0], a[..., 1], a[..., 2]
lum = a @ np.array([.299, .587, .114], np.float32)
box = ((R - G) > 60) & (lum < 170)
ribbon = ((R - G) > 6) & ~box & (lum >= 150)
mb, mr = soft(box), soft(ribbon)
ivory = np.clip(lum[..., None] * np.array([1.0, 0.985, 0.95], np.float32) + 18, 0, 252)
out = a * (1 - mb) + black(a, box, 14, 80) * mb
out = out * (1 - mr) + ivory * mr
save(out, 'offer-gift-mystery.jpg')
