"""Gate: no video the theme plays shows the old brand's pink bottle.

usage: python3 -I video_brand_gate.py <theme_dir>
Every .mp4 and .webm that a template, partial or layout references ('sf/<dir>/<file>'|asset_url) is decoded at 4
frames a second, 160 px wide, and each frame's share of saturated pink-to-crimson pixels is measured (green well
below red, blue above green and below red: the SMOOCHE bottles, pink in the creators' clips and crimson in the ad
loop; skin has blue below green). A video fails when two or more frames are over 1% (measured 25 Oct 2026: the
Genjutsu re-makes peak at 0.36%, the old-brand clips reach 5-11% in 10 to 74 frames). Exits 1 on a failure, after
listing every video.

Browsers in QA (Playwright's Chromium) have no H.264, so a clip's picture is never seen there: this checks what
Chrome and Safari show.
"""
import re, subprocess, sys
from pathlib import Path
import numpy as np

THEME = Path(sys.argv[1])
FPS, WIDTH, PINK, FRAMES = 4, 160, 0.01, 2


def pink_frames(path):
    """The share of pink pixels in each sampled frame."""
    W, H = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                    '-of', 'csv=p=0', str(path)], check=True, capture_output=True, text=True).stdout.split(',')[:2])
    h = round(H * WIDTH / W / 2) * 2
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'fps={FPS},scale={WIDTH}:{h}', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], check=True, capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, WIDTH, 3).astype(np.int16)
    R, G, B = fr[..., 0], fr[..., 1], fr[..., 2]
    return ((R > 120) & (R - G > 90) & (B - G > 5) & (B < R)).mean((1, 2))


refs = {}
for f in sorted(p for d in ('templates', 'partials', 'layouts') for p in (THEME / d).rglob('*.html')):
    for m in re.finditer(r"'(sf/[a-z]+/[^']+\.(?:mp4|webm))'\s*\|\s*asset_url", f.read_text(encoding='utf-8', errors='surrogateescape')):
        refs.setdefault(m.group(1), f.relative_to(THEME).as_posix())
failed = []
for ref, page in sorted(refs.items()):
    path = THEME / 'assets' / ref
    if not path.exists(): failed.append(ref); print(f'MISSING {ref} ({page})'); continue
    s = pink_frames(path)
    bad = int((s > PINK).sum())
    print(f'{"FAIL" if bad >= FRAMES else "ok  "} {ref} ({page}): {len(s)} frames, max pink {s.max() * 100:.2f}%, {bad} over {PINK * 100:.1f}%')
    if bad >= FRAMES: failed.append(ref)
print(f'Video brand gate {"failed" if failed else "passed"}: {len(refs)} video(s), {len(failed)} failing.')
sys.exit(1 if failed else 0)
