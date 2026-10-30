"""Paste an edited crop back into its original image (for scenes an image model refuses or reframes).

usage: python3 -I composite.py <groups.json> <export_dir_before> <crop-boxes.json> <n> <edited_crop.png> <out.png>
The edited crop is fitted to the box's aspect and size and pasted with a feathered edge; the output is written at
4x the master size so apply_images can downscale it into every variant.
"""
import json, sys
from PIL import Image, ImageFilter
G = {g['n']: g for g in json.load(open(sys.argv[1]))}
n = int(sys.argv[4]); b = json.load(open(sys.argv[3]))[str(n)]
orig = Image.open(f"{sys.argv[2]}/assets/img/{G[n]['master']}").convert('RGB')
w, h = b[2] - b[0], b[3] - b[1]
new = Image.open(sys.argv[5]).convert('RGB')
r, R = w / h, new.width / new.height
if R > r: nw = round(new.height * r); new = new.crop(((new.width - nw) // 2, 0, (new.width - nw) // 2 + nw, new.height))
else: nh = round(new.width / r); new = new.crop((0, (new.height - nh) // 2, new.width, (new.height - nh) // 2 + nh))
new = new.resize((w, h), Image.LANCZOS)
m = max(2, min(w, h) // 12)
mask = Image.new('L', (w, h), 0); mask.paste(255, (m, m, w - m, h - m)); mask = mask.filter(ImageFilter.GaussianBlur(m / 2))
orig.paste(new, (b[0], b[1]), mask)
orig.resize((orig.width * 4, orig.height * 4), Image.LANCZOS).save(sys.argv[6])
