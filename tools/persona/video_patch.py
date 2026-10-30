"""Put a re-made stretch of a video back into it, on the source video's own timeline.

usage: python3 -I video_patch.py <source.mp4> <base.mp4> <patch.mp4> <out.mp4> --at <s> --len <s> --from <s> --to <s>
                                 [--box x,y,w,h] [--region x0,y0,x1,y1 --feather px]
- source: the original video; its length, frame rate, size and soundtrack are the output's
- base: the whole video as it should look outside the patch (the source itself, or its Genjutsu result); it is
  stretched to the source's length first (Genjutsu returns 24 fps and runs a few % fast)
- patch: a Genjutsu result of the clip cut from the source at --at, --len seconds long (of a crop of it at --box, if
  given; the whole frame otherwise), stretched back to that length
- between --from and --to the patch replaces the base: whole frames, or, with --region (in source px), only that
  area, blended in with a soft edge of --feather px, so the rest of the frame stays the base's pixel for pixel
"""
import subprocess, sys
import numpy as np

SRC, BASE, PATCH, OUT = sys.argv[1:5]
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
AT, T0, T1 = float(arg('--at')), float(arg('--from')), float(arg('--to'))
BOX = [int(v) for v in arg('--box').split(',')] if arg('--box') else None
REGION = [int(v) for v in arg('--region').split(',')] if arg('--region') else None
FEATHER = int(arg('--feather', 24))


def probe(p, entries, stream='v:0'):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', entries, '-of', 'csv=p=0', p]
    if stream: cmd[3:3] = ['-select_streams', stream]
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()


dur = lambda p: float(probe(p, 'format=duration', None))
W, H = (int(v) for v in probe(SRC, 'stream=width,height').split(','))
num, den = (int(v) for v in probe(SRC, 'stream=r_frame_rate').split('/')); FPS = num / den
DS = dur(SRC); N = int(round(DS * FPS))
bx, by, bw, bh = BOX or (0, 0, W, H)


def frames(p, w, h, k):
    """Frames of p, its timing stretched by k, at the source's frame rate and size w x h."""
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'setpts={k:.6f}*PTS,fps={num}/{den},scale={w}:{h}:flags=lanczos',
                             '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        buf = proc.stdout.read(w * h * 3)
        if len(buf) < w * h * 3: break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    proc.wait()


# the patch was made from source[AT : AT + --len] (the length of the clip that was cut and sent)
SEG = float(arg('--len'))
patch = list(frames(PATCH, bw, bh, SEG / dur(PATCH)))
mask = None
if REGION:
    x0, y0, x1, y1 = REGION
    m = np.zeros((H, W), np.float32); m[y0:y1, x0:x1] = 1
    import cv2
    m = cv2.GaussianBlur(m, (0, 0), FEATHER / 2.5)
    mask = m[by:by + bh, bx:bx + bw, None]
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', f'{num}/{den}',
                        '-i', '-', '-i', SRC, '-map', '0:v:0', '-map', '1:a:0?', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-t', f'{DS:.3f}', '-movflags', '+faststart', OUT],
                       stdin=subprocess.PIPE)
used = 0
for i, f in enumerate(frames(BASE, W, H, DS / dur(BASE))):
    if i >= N: break
    t = i / FPS
    if T0 <= t < T1:
        j = int(round((t - AT) * FPS))
        if 0 <= j < len(patch):
            f = f.copy(); p = patch[j].astype(np.float32); cur = f[by:by + bh, bx:bx + bw].astype(np.float32)
            f[by:by + bh, bx:bx + bw] = (p if mask is None else cur * (1 - mask) + p * mask).astype(np.uint8)
            used += 1
    enc.stdin.write(np.ascontiguousarray(f).tobytes())
enc.stdin.close(); enc.wait()
print(f'{OUT}: {used} frames patched between {T0:.2f} s and {T1:.2f} s ({len(patch)} patch frames from {AT:.2f} s)')
