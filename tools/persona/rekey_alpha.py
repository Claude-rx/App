"""Give an edited cut-out its transparency back, following the edited subject's own silhouette.

usage: python3 -I rekey_alpha.py <original_with_alpha> <edited.png> <out.png>
The source of a cut-out edit was flattened on a plain light backdrop; the model returns it on that backdrop. The
backdrop colour is read from the edited image's border, everything far enough from it becomes the subject (holes
filled, so white cream or highlights inside the subject stay opaque), edges are softened, and the result is limited
to a band around the original mask so stray backdrop noise never becomes visible. Re-using the original mask
directly would cut a re-aged or re-posed subject wrongly; this follows the new silhouette.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

orig, edited, out = sys.argv[1:4]
e = Image.open(edited).convert('RGB')
a0 = Image.open(orig).convert('RGBA').getchannel('A').resize(e.size, Image.LANCZOS)
E = np.asarray(e, np.float32)
border = np.concatenate([E[:8].reshape(-1, 3), E[-8:].reshape(-1, 3), E[:, :8].reshape(-1, 3), E[:, -8:].reshape(-1, 3)])
bg = np.median(border, 0)
dist = np.sqrt(((E - bg) ** 2).sum(-1))
subject = dist > 14
subject = ndimage.binary_opening(subject, iterations=2)
lab, n = ndimage.label(subject)
if n:
    sizes = ndimage.sum(subject, lab, range(1, n + 1))
    subject = np.isin(lab, 1 + np.nonzero(sizes > 0.002 * subject.size)[0])   # drop specks
subject = ndimage.binary_fill_holes(ndimage.binary_closing(subject, iterations=3))
guard = ndimage.binary_dilation(np.asarray(a0) > 20, iterations=max(6, e.width // 80))
subject &= guard
soft = np.clip((dist - 8) / 14, 0, 1)                                            # anti-aliased edge from colour distance
alpha = np.where(ndimage.binary_erosion(subject, iterations=2), 1.0, np.where(subject, np.maximum(soft, 0.5), 0.0))
alpha = ndimage.gaussian_filter(alpha, 0.8)
rgba = np.dstack([E, alpha * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save(out)
print(f'{out}: backdrop {bg.round().tolist()}, subject {subject.mean():.0%} of frame')
