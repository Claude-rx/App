"""SKINOFAB's logo files, all from the owner's vector wordmark (brand/logo/skinofab-wordmark.svg):

  brand/logo/skinofab-wordmark-black.png    black on transparent, 3902 px wide, cropped to the letters: what
                                            label_composite.py prints on every bottle and stick
  brand/checkout/skinofab-logo-1200.png     the checkout and email logo, 1200 x 198, black on transparent
  brand/checkout/skinofab-icon-512.png      the favicon and checkout tab icon: the wordmark's own S, white on a black
                                            rounded square

usage: python3 -I tools/persona/brand_logo.py      (needs node and Playwright's Chromium, which render the SVG)
"""
import re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BRAND = HERE.parents[1] / 'brand'
SVG = BRAND / 'logo' / 'skinofab-wordmark.svg'


def render(width, first_only=False):
    """The wordmark rendered at width px: its alpha, cropped to the letters. first_only: its first letter alone (the
    S: the SVG's first path)."""
    src = SVG.read_text()
    if first_only:
        paths = re.findall(r'<path\b.*?/>', src, re.S)
        src = src.replace(''.join(src[src.index(paths[1]):src.rindex(paths[-1]) + len(paths[-1])]), '')
    with tempfile.TemporaryDirectory() as d:
        svg, out = Path(d) / 'w.svg', Path(d) / 'w.png'
        svg.write_text(src)
        subprocess.run(['node', str(HERE / 'svg_render.cjs'), str(svg), str(out), str(width)], check=True)
        a = Image.open(out).convert('RGBA').getchannel('A')
    return a.crop(a.getbbox())


def ink(alpha, colour=(0, 0, 0)):
    im = Image.new('RGBA', alpha.size, colour + (0,))
    im.putalpha(alpha)
    return im


def main():
    big = render(4000)
    ink(big).save(BRAND / 'logo' / 'skinofab-wordmark-black.png', optimize=True)
    print('wordmark', big.size)
    # checkout logo: the letters 1193 x 192 inside 1200 x 198
    w = 1193
    logo = big.resize((w, round(big.height * w / big.width)), Image.LANCZOS)
    can = Image.new('RGBA', (1200, 198), (0, 0, 0, 0))
    can.alpha_composite(ink(logo), ((1200 - logo.width) // 2, (198 - logo.height) // 2))
    can.save(BRAND / 'checkout' / 'skinofab-logo-1200.png', optimize=True)
    print('checkout logo', can.size)
    # icon: the wordmark's own S
    s = render(8000, first_only=True)
    S = 4
    icon = Image.new('RGBA', (512 * S, 512 * S), (0, 0, 0, 0))
    ImageDraw.Draw(icon).rounded_rectangle((0, 0, 512 * S - 1, 512 * S - 1), radius=112 * S, fill=(0, 0, 0, 255))
    h = 392 * S
    s = s.resize((round(s.width * h / s.height), h), Image.LANCZOS)
    icon.alpha_composite(ink(s, (255, 255, 255)), ((512 * S - s.width) // 2, (512 * S - s.height) // 2))
    icon.resize((512, 512), Image.LANCZOS).save(BRAND / 'checkout' / 'skinofab-icon-512.png', optimize=True)
    print('icon', (512, 512))


if __name__ == '__main__':
    sys.exit(main())
