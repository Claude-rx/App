"""Label transplant, for photos where the image-edit model redrew the bottle at another size (a plain relabel.py paste
then leaves a ghost of the old bottle): scale/rotate the edited crop so its label lands on the original bottle's label
(matched by the heart logo centre and size), match the light (gain from the paper at the patch top, plus the bottle's
per-column cylinder shading with `cols`), and paste only the label rectangle. Parameters per photo are recorded in
tools/mediclab/relabel-boxes.json under "_transplant" (all in the 1024 px crop space).

usage: python3 -I tools/mediclab/relabel_transplant.py <src> <x0> <y0> <size> <edited> <out> <scale> <orig_cx> <orig_cy>
       <edit_cx> <edit_cy> <mx0> <my0> <mx1> <my1> [rot_deg] [cols]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
# src x0 y0 sz edited out  s  ocx ocy  ecx ecy  mx0 my0 mx1 my1 [rot]
a = sys.argv[1:]
src, (x0,y0,sz), ed, out = a[0], map(int,a[1:4]), a[4], a[5]
s, ocx, ocy, ecx, ecy = map(float, a[6:11]); box = tuple(map(float, a[11:15])); rot = float(a[15]) if len(a) > 15 else 0
orig = Image.open(src).convert('RGB')
oc = orig.crop((x0,y0,x0+sz,y0+sz)).resize((1024,1024), Image.LANCZOS)
e = Image.open(ed).convert('RGB').resize((1024,1024), Image.LANCZOS)
th = np.deg2rad(rot); c, sn = np.cos(th)/s, np.sin(th)/s
# output p -> edited: e = ec + R(-rot)/s (p - oc)
inv = (c, sn, ecx - c*ocx - sn*ocy, -sn, c, ecy + sn*ocx - c*ocy)
w = e.transform((1024,1024), Image.AFFINE, inv, Image.BICUBIC)
mask = Image.new('L', (1024,1024), 0); ImageDraw.Draw(mask).rectangle(box, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(3))
# match the light: per-channel gain on bright label paper inside the box
A, B = np.asarray(oc).astype(float), np.asarray(w).astype(float)
x0b,y0b,x1b,y1b = map(int, box)
ra, rb = A[y0b:y0b+30, x0b+40:x1b-40].reshape(-1,3), B[y0b:y0b+30, x0b+40:x1b-40].reshape(-1,3)
ga = ra[ra.mean(1) > np.percentile(ra.mean(1), 60)].mean(0); gb = rb[rb.mean(1) > np.percentile(rb.mean(1), 60)].mean(0)
B = B * (ga/gb)
if len(a) > 16 and a[16] == 'cols':
    from scipy.ndimage import uniform_filter1d
    la, lb = A.mean(2), B.mean(2)
    prof = np.ones(1024)
    for x in range(x0b, x1b):
        ca, cb = la[y0b:y1b, x], lb[y0b:y1b, x]
        prof[x] = np.percentile(ca, 75) / max(np.percentile(cb, 75), 1)
    prof[x0b:x1b] = uniform_filter1d(prof[x0b:x1b], 25)
    B = B * prof[None, :, None]
B = np.clip(B, 0, 255)
# keep the photo's horizontal shading across the label (cylinder light): ratio of smoothed paper brightness
w = Image.fromarray(B.astype('uint8'))
comp = Image.composite(w, oc, mask).resize((sz,sz), Image.LANCZOS)
orig.paste(comp, (x0,y0), mask.resize((sz,sz), Image.LANCZOS))
orig.save(out, quality=90, optimize=True, progressive=True)
print('gain', np.round(ga/gb,3))
