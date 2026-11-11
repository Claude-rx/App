"""Put the new Berberine label (Weight Management*, METABOLISM / CRAVINGS / GLUCOSE) on lifestyle photos that show the
old bottle (Healthy Blood Sugar*), without regenerating the photo.

The bottle region is cropped square, upscaled to 1024 px and relabelled with an image-edit model (Nano Banana 2 via
Kie.ai, reference = the new-label pack shot); only that crop comes back, and this script blends it into the untouched
original with a feathered edge. Everything outside the crop keeps its original pixels.

usage:
  python3 -I tools/mediclab/relabel.py crop  <image> <x0> <y0> <size> <out-crop.jpg>
  python3 -I tools/mediclab/relabel.py paste <image> <x0> <y0> <size> <edited-crop> <out-image> [feather_px]
The boxes used for the MedicLab photos are recorded in tools/mediclab/relabel-boxes.json.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter


def crop(src, x0, y0, size, out):
    im = Image.open(src).convert('RGB')
    im.crop((x0, y0, x0 + size, y0 + size)).resize((1024, 1024), Image.LANCZOS).save(out, quality=92)


def paste(src, x0, y0, size, edited, out, feather=None):
    im = Image.open(src).convert('RGB')
    patch = Image.open(edited).convert('RGB').resize((size, size), Image.LANCZOS)
    feather = feather or max(6, size // 14)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rectangle((feather, feather, size - feather, size - feather), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather / 2))
    im.paste(patch, (x0, y0), mask)
    im.save(out, quality=90, optimize=True, progressive=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('crop', 'paste'):
        sys.exit(__doc__)
    if a[0] == 'crop':
        crop(a[1], int(a[2]), int(a[3]), int(a[4]), a[5])
    else:
        paste(a[1], int(a[2]), int(a[3]), int(a[4]), a[5], a[6], int(a[7]) if len(a) > 7 else None)
