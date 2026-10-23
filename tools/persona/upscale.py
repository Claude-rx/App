"""AI super-resolution on the CPU, for photos the store has no larger original of.

usage: python upscale.py <model.pth> <in> <out.png> [--tile 320] [--crop x0,y0,x1,y1]
       python upscale.py --blend <a.png> <b.png> <weight of b> <out.png>

Runs any model spandrel loads (ESRGAN, Real-ESRGAN, SwinIR, HAT, DAT...), in tiles with a padded border so seams never
show; 15 GB of RAM and 4 cores take a 2000 x 853 photo to 8000 x 3412 in about 6 minutes. Needs torch (CPU build) and
spandrel in a virtualenv:
    python3 -m venv sr && sr/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    sr/bin/pip install spandrel pillow numpy
Model files load with torch's weights-only unpickler (no code in them runs). The home hero (docs/persona-image-shots.md)
uses 4x_NMKD-Siax_200k (skin texture, hair) blended with RealESRGAN_x4plus (calmer skin):
    huggingface.co/gemasai/4x_NMKD-Siax_200k   github.com/xinntao/Real-ESRGAN/releases (v0.1.0)
"""
import sys, time
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
args = sys.argv[1:]
if args and args[0] == '--blend':
    a, b, w, out = args[1], args[2], float(args[3]), args[4]
    A = np.asarray(Image.open(a).convert('RGB')).astype(np.float32)
    B = np.asarray(Image.open(b).convert('RGB')).astype(np.float32)
    Image.fromarray(np.clip(A * (1 - w) + B * w + 0.5, 0, 255).astype(np.uint8)).save(out)
    print(f'{out}: {1 - w:.2f} x {a} + {w:.2f} x {b}')
    sys.exit()

import torch
from spandrel import ModelLoader

def opt(name, default):
    return args[args.index(name) + 1] if name in args else default
mp, src, dst = args[:3]
tile = int(opt('--tile', 320))
im = Image.open(src).convert('RGB')
crop = opt('--crop', None)
if crop: im = im.crop(tuple(int(v) for v in crop.split(',')))
torch.set_grad_enabled(False)
model = ModelLoader().load_from_file(mp).eval()
sc = model.scale
a = torch.from_numpy(np.asarray(im).astype(np.float32) / 255).permute(2, 0, 1)[None]
_, _, H, W = a.shape
pad = 16
out = torch.zeros(1, 3, H * sc, W * sc)
t0 = time.time()
for y in range(0, H, tile):
    for x in range(0, W, tile):
        y0, x0 = max(0, y - pad), max(0, x - pad)
        y1, x1 = min(H, y + tile + pad), min(W, x + tile + pad)
        r = model(a[:, :, y0:y1, x0:x1]).clamp(0, 1)
        cy0, cx0 = (y - y0) * sc, (x - x0) * sc                       # keep the tile's core, drop the padding
        cy1, cx1 = cy0 + (min(H, y + tile) - y) * sc, cx0 + (min(W, x + tile) - x) * sc
        out[:, :, y * sc:min(H, y + tile) * sc, x * sc:min(W, x + tile) * sc] = r[:, :, cy0:cy1, cx0:cx1]
Image.fromarray((out[0].permute(1, 2, 0).numpy() * 255 + .5).astype(np.uint8)).save(dst)
print(f'{mp.split("/")[-1]} x{sc} {W}x{H} -> {W * sc}x{H * sc} in {time.time() - t0:.0f} s')
