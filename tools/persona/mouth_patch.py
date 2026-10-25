"""Put a lip-synced mouth (a LatentSync result, 25 fps) back into the source video, on the source's own frames.

usage: <LatentSync venv>/bin/python mouth_patch.py <source.mp4> <synced.mp4> <out.mp4> --at <s> --from <s> --to <s>
                                                   --insightface <dir> [--audio <new.wav>] [--fade 0.08]
- synced: LatentSync's result for the clip cut from the source at --at (it works at 25 fps: frame i is --at + i/25)
- between --from and --to, every source frame gets the lower face of the synced frame nearest in time, moved onto
  this frame's face first (a similarity transform between the two frames' eyes and nose, insightface's key points, so
  the 25 fps head lines up with the 30 fps one), inside a soft mask: under the nose, inside the jawline (the 106-point
  contour, 0-32), a little wider, its edge feathered; it fades in after --from and out before --to over --fade s
- everything else, in every frame, stays the source's pixel for pixel; the soundtrack is --audio (the edited one)
- --insightface: the folder holding models/buffalo_l (LatentSync's checkpoints/auxiliary)
"""
import subprocess, sys
import cv2
import numpy as np
from insightface.app import FaceAnalysis

SRC, SYN, OUT = sys.argv[1:4]
args = sys.argv[4:]
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
AT, T0, T1, FADE = float(opt('--at')), float(opt('--from')), float(opt('--to')), float(opt('--fade', 0.08))
AUDIO = opt('--audio', SRC)


def probe(p, entries, stream='v:0'):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', entries, '-of', 'csv=p=0', p]
    if stream: cmd[3:3] = ['-select_streams', stream]
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()


W, H = (int(v) for v in probe(SRC, 'stream=width,height').split(','))
num, den = (int(v) for v in probe(SRC, 'stream=r_frame_rate').split('/')); FPS = num / den
DUR = float(probe(SRC, 'format=duration', None))


def frames(p):
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    dec.wait()


app = FaceAnalysis(allowed_modules=['detection', 'landmark_2d_106'], root=opt('--insightface'),
                   providers=['CPUExecutionProvider'])
app.prepare(ctx_id=-1, det_size=(512, 512))


def face(img):
    fs = app.get(img)
    return max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])) if fs else None


def lower_face_mask(f):
    """Under the nose and inside the jawline, 6 px wider, feathered: the part of the face that speaks."""
    lm = f.landmark_2d_106
    top = lm[72:87, 1].max()                                        # the underside of the nose
    jaw = lm[:33][lm[:33, 1] > top]
    poly = np.concatenate([jaw[np.argsort(jaw[:, 0])], [[jaw[:, 0].max(), top], [jaw[:, 0].min(), top]]])
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [cv2.convexHull(poly.astype(np.int32))], 255)
    m = cv2.dilate(m, np.ones((13, 13), np.uint8))
    return cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 6)[..., None]


syn = list(frames(SYN))
syn_faces = [face(s) for s in syn]
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', f'{num}/{den}',
                        '-i', '-', '-i', AUDIO, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'medium',
                        '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-t', f'{DUR:.3f}',
                        '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
done = []
for n, fr in enumerate(frames(SRC)):
    t = n / FPS
    if T0 <= t < T1:
        i = int(round((t - AT) * 25))
        fs, ss = face(fr), syn_faces[i] if 0 <= i < len(syn) else None
        if fs is not None and ss is not None:
            M, _ = cv2.estimateAffinePartial2D(ss.kps[:3].astype(np.float32), fs.kps[:3].astype(np.float32))
            moved = cv2.warpAffine(syn[i], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            k = min(1.0, (t - T0) / FADE, (T1 - t) / FADE) if FADE else 1.0
            m = lower_face_mask(fs) * k
            fr = (fr.astype(np.float32) * (1 - m) + moved.astype(np.float32) * m).astype(np.uint8)
            done.append((round(t, 3), float(np.linalg.norm(ss.kps[:3] - fs.kps[:3], axis=1).mean())))
    enc.stdin.write(np.ascontiguousarray(fr).tobytes())
enc.stdin.close(); enc.wait()
print(f'{OUT}: {len(done)} frames got the synced mouth between {T0:.2f} and {T1:.2f} s '
      f'(its eyes and nose were up to {max(d for _, d in done):.1f} px from the synced frame\'s, moved to line up)')
