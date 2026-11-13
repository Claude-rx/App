"""Deploy-time asset optimisation for the Get Rid Of funnel (used by deploy_store.py; sources stay untouched).

Images (PNG / JPEG / WebP): longest side capped at MAX_SIDE (2x the widest slot any of these images fills on the page,
so they stay sharp on retina screens), re-encoded as WebP at QUALITY (visually lossless for photos; alpha kept).
The optimised file is used only when it is at least MIN_SAVING smaller; otherwise the original ships.
Long sprites (aspect > 4, e.g. flag strips) are never resized.

Fonts (WOFF2 over 40 KB): subset to the Latin, punctuation and symbol ranges the pages use (layout features kept),
which cuts each Helvetica / Inter face from ~200 KB to ~20-40 KB. Glyphs outside the ranges fall back to the next
font in the stack.

Results are cached by input hash in CACHE, so a deploy only re-encodes what changed.
"""
import hashlib, io
from pathlib import Path

from PIL import Image

CACHE = Path(__file__).resolve().parents[3] / '.cache/getridof-assets'
MAX_SIDE = 1400
QUALITY = 82
MIN_SAVING = 0.10
RASTER = {'.png', '.jpg', '.jpeg', '.webp'}
UNICODES = ('U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,'
            'U+2190-2199,U+2212,U+2215,U+2605-2606,U+2713-2714,U+2716,U+FEFF,U+FFFD')


def _cached(kind, data, fn):
    key = hashlib.sha1(kind.encode() + data).hexdigest()
    f = CACHE / key
    if f.exists():
        out = f.read_bytes()
        return None if out == b'' else out
    out = fn(data)
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_bytes(out or b'')
    return out


def _image(data):
    im = Image.open(io.BytesIO(data))
    if getattr(im, 'is_animated', False): return None
    w, h = im.size
    if max(w, h) > MAX_SIDE and max(w, h) / min(w, h) <= 4:
        s = MAX_SIDE / max(w, h)
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    im = im.convert('RGBA' if alpha else 'RGB')
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=QUALITY, method=6, alpha_quality=90)
    out = buf.getvalue()
    return out if len(out) <= len(data) * (1 - MIN_SAVING) else None


def _font(data):
    if len(data) < 40_000: return None
    from fontTools import subset
    from fontTools.ttLib import TTFont
    f = TTFont(io.BytesIO(data))
    opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['*']; opts.name_IDs = ['*']
    opts.notdef_outline = True; opts.glyph_names = False
    s = subset.Subsetter(opts); s.populate(unicodes=subset.parse_unicodes(UNICODES)); s.subset(f)
    buf = io.BytesIO(); f.flavor = 'woff2'; f.save(buf)
    out = buf.getvalue()
    return out if len(out) <= len(data) * (1 - MIN_SAVING) else None


def optimize(suffix, data):
    """-> (bytes, suffix) to ship: the optimised version when it is worth it, else the original."""
    s = suffix.lower()
    if s in RASTER:
        out = _cached('img2', data, _image)
        return (out, '.webp') if out else (data, s)
    if s == '.woff2':
        out = _cached('font1', data, _font)
        return (out, s) if out else (data, s)
    return data, s
