"""Erase the small print under the SKINOFAB wordmark on a bottle in a video clip, frame by frame.

usage: python3 clean_video_label.py <src.mp4> <out.mp4> <t0> <t1> <ref_t> <wx,wy,ww,wh> <dx0,dy0,dx1,dy1>

The bottle in brand/videos/gj-41b77ec4-cut.mp4 (the third "See how it blends" card) carries the old store's small
print under the SKINOFAB wordmark: "COLOR CHANGING FOUNDATION", "15 SPF" and its size (store audit 8). Between t0 and
t1 seconds each frame's wordmark is found by template matching (the wordmark box wx,wy,ww,wh of the frame at ref_t,
tried at small rotations and scales, searched around its last place), and the small print's box, given relative to
the wordmark's bottom-left corner (dx0,dy0 .. dx1,dy1, rotated with it), is cleared: its light text pixels are
painted over from the bottle around them (OpenCV inpainting), so the wordmark stays and the label below it is plain.
Frames where the wordmark is not found (the bottle out of the frame) are left as they are. The audio is copied.
"""
import subprocess, sys, tempfile
from pathlib import Path

import cv2
import numpy as np

MIN_SCORE = 0.5        # below it, the wordmark is taken as not in the frame


def rotated(img, angle, scale):
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, scale)
    return cv2.warpAffine(img, m, (w, h), borderMode=cv2.BORDER_REPLICATE)


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    t0, t1, ref_t = (float(x) for x in sys.argv[3:6])
    wx, wy, ww, wh = (int(x) for x in sys.argv[6].split(','))
    dx0, dy0, dx1, dy1 = (int(x) for x in sys.argv[7].split(','))
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(f)
    cap.release()
    ref = cv2.cvtColor(frames[round(ref_t * fps)], cv2.COLOR_BGR2GRAY)
    pad = 14                                    # the template with some bottle around the wordmark
    tpl0 = ref[wy - pad:wy + wh + pad, wx - pad:wx + ww + pad]
    variants = [(a, s, rotated(tpl0, a, s)) for a in range(-24, 25, 4) for s in (0.86, 0.93, 1.0, 1.07)]
    last = (wx - pad, wy - pad)
    cleaned, skipped = 0, []
    for i in range(round(t0 * fps), min(len(frames), round(t1 * fps) + 1)):
        g = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        x0, y0 = max(0, last[0] - 60), max(0, last[1] - 60)
        win = g[y0:min(H, last[1] + tpl0.shape[0] + 60), x0:min(W, last[0] + tpl0.shape[1] + 60)]
        best = None
        for a, s, t in variants:
            if win.shape[0] < t.shape[0] or win.shape[1] < t.shape[1]: continue
            r = cv2.matchTemplate(win, t, cv2.TM_CCOEFF_NORMED)
            _, v, _, loc = cv2.minMaxLoc(r)
            if not best or v > best[0]: best = (v, a, s, (x0 + loc[0], y0 + loc[1]))
        if not best or best[0] < MIN_SCORE:
            skipped.append((round(i / fps, 2), round(best[0], 2) if best else None)); continue
        v, a, s, (mx, my) = best
        last = (mx, my)
        # the wordmark's bottom-left corner in this frame, and the small print's box around it, turned by its angle
        cx, cy = mx + tpl0.shape[1] / 2, my + tpl0.shape[0] / 2
        rad = np.deg2rad(-a)
        def place(px, py):                       # a point given in the reference frame's wordmark coordinates
            ox, oy = (px - (wx + ww / 2)) * s, (py - (wy + wh / 2)) * s
            return (cx + ox * np.cos(rad) - oy * np.sin(rad), cy + ox * np.sin(rad) + oy * np.cos(rad))
        bl = (wx, wy + wh)
        quad = np.array([place(bl[0] + dx0, bl[1] + dy0), place(bl[0] + dx1, bl[1] + dy0),
                         place(bl[0] + dx1, bl[1] + dy1), place(bl[0] + dx0, bl[1] + dy1)], np.int32)
        box = np.zeros((H, W), np.uint8)
        cv2.fillConvexPoly(box, quad, 255)
        # the light print inside the box: brighter than the bottle around it
        level = np.median(g[box > 0])
        text = ((g.astype(np.int16) > level + 14) & (box > 0)).astype(np.uint8) * 255
        text = cv2.dilate(text, np.ones((3, 3), np.uint8), iterations=1)
        frames[i] = cv2.inpaint(frames[i], text, 4, cv2.INPAINT_TELEA)
        cleaned += 1
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / 'v.avi'
        vw = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*'FFV1'), fps, (W, H))
        for f in frames: vw.write(f)
        vw.release()
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-i', str(src), '-map', '0:v', '-map', '1:a?',
                        '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
                        '-movflags', '+faststart', str(out)], check=True)
    print(f'{out}: {cleaned} frames cleaned of {len(frames)}; left (seconds, best match): {skipped}')


if __name__ == '__main__':
    main()
