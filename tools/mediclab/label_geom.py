"""Find the MedicLab label on a generated bottle: the dark green heart and the bottom band (pixel boxes)."""
import numpy as np
from PIL import Image
from scipy import ndimage
def greens(rgb):
    a = np.asarray(rgb).astype(int); r,g,b = a[...,0],a[...,1],a[...,2]
    m = (g > r + 8) & (g >= b - 4) & ((r+g+b)/3 < 105)
    m = ndimage.binary_closing(ndimage.binary_opening(m, iterations=1), iterations=4)
    lab, n = ndimage.label(m)
    objs = ndimage.find_objects(lab); sizes = ndimage.sum(m, lab, range(1, n+1))
    comps = [(int(sizes[i]), objs[i][1].start, objs[i][0].start, objs[i][1].stop, objs[i][0].stop) for i in range(n)]
    return sorted(comps, reverse=True)
def label_geom(rgb, min_area=200):
    """heart (top) + band (wide, below): return (heart_box, band_box) in pixel coords, or None"""
    comps = [c for c in greens(rgb)[:12] if c[0] >= min_area]
    best = None
    for h in comps:
        hx0,hy0,hx1,hy1 = h[1:]; hw, hh = hx1-hx0, hy1-hy0
        if not (0.7 < hh/max(hw,1) < 1.5): continue
        for b in comps:
            bx0,by0,bx1,by1 = b[1:]; bw, bh = bx1-bx0, by1-by0
            if b is h or bw < hw*1.2 or bh > bw*0.45 or by0 < hy1: continue
            if not (bx0 < (hx0+hx1)/2 < bx1): continue
            gap = by0 - hy1
            if gap > hh*1.6: continue
            score = h[0] + b[0]
            if best is None or score > best[0]: best = (score, (hx0,hy0,hx1,hy1), (bx0,by0,bx1,by1))
    return None if best is None else best[1:]
if __name__ == '__main__':
    import sys
    cut = Image.open(sys.argv[1]).convert('RGBA'); rgb = Image.new('RGB', cut.size, 'white'); rgb.paste(cut, mask=cut.split()[3])
    print(cut.size, label_geom(rgb))
