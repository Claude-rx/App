"""The owner's own clips, made light for a phone and placed in the funnel's image folder (the sales page's video
carousel, 5 Nov 2026: "add the videos carousel ... just use 4 to 5" from the owner's Skinofab-S24 folder).

usage: python3 -I tools/funnel/apf/add_clips.py [--key ugc] [--max 30] [--start 0] clip1.mp4 clip2.mov ...

For each clip, in order, it writes campaigns/skinofab/src/apf-funnel/assets/images/sf/<key>-<n>.mp4 (H.264, sound kept
when the clip has some, +faststart so a phone starts it before it has all of it), <key>-<n>.webm (VP9 + Opus, smaller,
first choice for the browsers that play it) and <key>-<n>-poster.jpg (the card's still before a tap). Each is 540 x
960 (9:16, the card's shape: a wider clip is cut to its centre), at most --max seconds from --start, and prints what it
wrote. The sales page lists them in usage.carousel (adaptive-foundation-offer.html) with a chip and a caption each;
the build's video brand gate then reads every frame for the old brand's pink label.

Nothing is uploaded here: the theme push (tools/funnel/push_theme.py) sends the new files with the next deploy.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'campaigns/skinofab/src/apf-funnel/assets/images/sf'
W, H = 540, 960


def probe(src):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(src)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    rot = int((v.get('tags') or {}).get('rotate', 0) or 0)
    for sd in v.get('side_data_list') or []:
        if 'rotation' in sd: rot = int(sd['rotation'])
    w, h = int(v['width']), int(v['height'])
    if abs(rot) in (90, 270): w, h = h, w
    audio = any(s['codec_type'] == 'audio' for s in d['streams'])
    return w, h, float(d['format'].get('duration') or v.get('duration') or 0), audio


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(f'add_clips: ffmpeg failed:\n{r.stderr[-1500:]}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('clips', nargs='+')
    ap.add_argument('--key', default='ugc')
    ap.add_argument('--max', type=float, default=30.0, help='longest a clip may run, in seconds')
    ap.add_argument('--start', type=float, default=0.0, help='where to start each clip, in seconds')
    a = ap.parse_args()
    # cover the 9:16 card: scale up to fill it, then cut the centre
    vf = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30'
    for n, src in enumerate(a.clips, 1):
        src = Path(src)
        w, h, dur, audio = probe(src)
        t = max(0.0, min(a.max, dur - a.start))
        base = OUT / f'{a.key}-{n}'
        head = ['ffmpeg', '-y', '-v', 'error', '-ss', f'{a.start}', '-i', str(src), '-t', f'{t:.2f}', '-vf', vf]
        run(head + ['-c:v', 'libx264', '-preset', 'slow', '-crf', '27', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart'] + (['-c:a', 'aac', '-b:a', '96k', '-ac', '2'] if audio else ['-an'])
            + [str(base) + '.mp4'])
        run(head + ['-c:v', 'libvpx-vp9', '-crf', '36', '-b:v', '0', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2']
            + (['-c:a', 'libopus', '-b:a', '64k'] if audio else ['-an']) + [str(base) + '.webm'])
        run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{a.start + min(1.0, t / 3):.2f}', '-i', str(src), '-frames:v', '1',
             '-vf', vf, '-q:v', '4', str(base) + '-poster.jpg'])
        kb = {x: round((Path(str(base) + x)).stat().st_size / 1024) for x in ('.mp4', '.webm', '-poster.jpg')}
        print(f'{base.name}: {src.name} {w}x{h} {dur:.1f}s -> {t:.1f}s, sound {"yes" if audio else "no"}; '
              f'mp4 {kb[".mp4"]} KB, webm {kb[".webm"]} KB, poster {kb["-poster.jpg"]} KB')


if __name__ == '__main__':
    main()
