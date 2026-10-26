"""Cut shots out of the Genjutsu re-makes (brand/videos/gj-*.mp4) that show what the store must not: another brand's
product. Each cut drops picture and sound together, at the pauses around the words spoken over that shot.

usage: python3 -I clip_cuts.py          # writes brand/videos/<name>-cut.mp4 for every clip in CUTS

tools/persona/queue/video-swaps.json then points the export's clip at the cut file, so every page that plays it
(the homepage card, the product page's demo row, any legacy page) shows the cut.

gj-43e0f648 ("Goes on white", 60 s): at 53.4-54.9 s a hand drops a Giorgio Armani foundation and a Dolce concealer
into a bin while she says "I won't be needing these anymore." (review 3, 26 Oct 2026). The cut runs from the pause
after "bronzer." (53.18-53.46 s) to the pause before "I'll be buying this on repeat." (54.86-55.08 s); the orchid shot
with the SKINOFAB bottle follows straight on.

gj-41b77ec4 ("all white", 21.5 s): its last 2.2 s, from 19.3 s, show her holding two bottles whose small PDRN line
the video model drew as "PORN", while she says "Click the link below to check it out for yourself." (a TikTok
caption's call, review 4). The clip now ends at the pause after "I'll never have to look for the right shade again."
(19.02-19.16 s), on the brushing shot.

gj-f8efa52f (the social carousel's "application" clip, 11.6 s): its opening shot, 0-0.54 s (13 frames at 24 fps),
holds the bottle to camera with its PDRN line drawn as "PORN" (review 4's video scan). The clip now starts at the
hard cut into the next shot; the carousel plays it muted.
"""
import subprocess
from pathlib import Path

VIDEOS = Path(__file__).resolve().parents[2] / 'brand' / 'videos'
CUTS = {'gj-43e0f648.mp4': [(53.32, 54.97)], 'gj-41b77ec4.mp4': [(19.09, 99.0)], 'gj-f8efa52f.mp4': [(0.0, 0.535)]}


def keep(spans):
    """The ffmpeg select expression that drops every (start, end) span."""
    return '*'.join(f'not(between(t,{a},{b}))' for a, b in spans)


def cut(name, spans):
    src, out = VIDEOS / name, VIDEOS / name.replace('.mp4', '-cut.mp4')
    expr = keep(spans)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src),
                    '-vf', f"select='{expr}',setpts=N/FRAME_RATE/TB", '-af', f"aselect='{expr}',asetpts=N/SR/TB",
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart', str(out)], check=True)
    dur = lambda p: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                         capture_output=True, text=True, check=True).stdout)
    print(f'{out.name}: {dur(src):.2f} s -> {dur(out):.2f} s')


if __name__ == '__main__':
    for name, spans in CUTS.items(): cut(name, spans)
