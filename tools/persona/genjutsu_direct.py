"""Genjutsu object swap on the site's videos through the Higgsfield API directly (no studio in between).

usage: HF_API_KEY_ID=... HF_API_KEY_SECRET=... NEXT_API_TOKEN=... \
       python3 -I genjutsu_direct.py <jobs.json> <theme_dir> <work_dir> [--go]
- jobs.json: tools/persona/queue/genjutsu-queue.json ({"refs": [...], "prompt": "...", "resolution": "720p",
  "jobs": [{"key", "video": <file name under assets/sf/media>}]})
- dry run by default (prints parts and the list-price estimate); --go submits
- videos over 28 s are cut into equal parts of at most 28 s (the endpoint trims at 30 s); parts are pushed to the
  theme so Higgsfield can fetch them from the public CDN
- each part: POST https://api.higgsfield.ai/higgsfield/genjutsu/object-swap/v1.0, poll its status_url, download
- parts are joined back and the ORIGINAL soundtrack is laid over the result: <work_dir>/<key>.mp4, kept in
  brand/videos/<key>.mp4 and mapped in queue/video-swaps.json, which apf_pages.py uses on the next build
- state (request ids, results) is kept in <work_dir>/state.json, so a re-run never resubmits finished parts
Key: Authorization: Key <id>:<secret> (docs.higgsfield.ai). The key is read from the environment only.
"""
import json, math, os, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

JOBS, THEME, WORK = json.load(open(sys.argv[1])), Path(sys.argv[2]), Path(sys.argv[3])
GO = '--go' in sys.argv
WORK.mkdir(parents=True, exist_ok=True)
STATE_P = WORK / 'state.json'
STATE = json.loads(STATE_P.read_text()) if STATE_P.exists() else {}
API = 'https://api.higgsfield.ai'
ENDPOINT = 'higgsfield/genjutsu/object-swap/v1.0'
CDN = 'https://cdn.29next.store/media/skinofab/themes/34/assets/'
RATE = {'480p': 0.318, '720p': 0.681, '1080p': 1.632}       # $ per input second (list price, docs)
MAX_PART = 28.0

def save(): STATE_P.write_text(json.dumps(STATE, indent=1))

def sh(*cmd): return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()

def duration(p): return float(sh('ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)))

def auth():
    kid, sec = os.environ.get('HF_API_KEY_ID'), os.environ.get('HF_API_KEY_SECRET')
    if not (kid and sec) and os.environ.get('HF_KEY') and ':' in os.environ['HF_KEY']:
        kid, sec = os.environ['HF_KEY'].split(':', 1)
    if not (kid and sec): sys.exit('Set HF_API_KEY_ID and HF_API_KEY_SECRET (Higgsfield API key) in the environment.')
    return f'Key {kid}:{sec}'

def call(method, url, body=None):
    for attempt in range(5):
        req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                     headers={'Authorization': auth(), 'Content-Type': 'application/json', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read() or b'{}')
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 4: time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f'{method} {url} -> {e.code}: {e.read()[:500].decode("utf-8", "replace")}')

def parts_of(job):
    """Cut a long video into equal parts of at most 28 s (re-encoded, so every cut lands exactly)."""
    src = THEME / 'assets' / 'sf' / 'media' / job['video']
    if not src.exists():                    # a fresh checkout has no built media: take the live copy from the CDN
        src.parent.mkdir(parents=True, exist_ok=True); urllib.request.urlretrieve(CDN + job['video'], src)
    d = duration(src); n = max(1, math.ceil(d / MAX_PART))
    if n == 1: return src, d, [{'name': job['video'], 'url': CDN + job['video'], 'seconds': d, 'local': str(src)}]
    out, step = [], d / n
    for i in range(n):
        name = f"gj-src-{job['key']}-p{i + 1}.mp4"; p = THEME / 'assets' / 'sf' / 'media' / name
        if not p.exists():
            sh('ffmpeg', '-v', 'error', '-y', '-ss', f'{i * step:.3f}', '-t', f'{step:.3f}', '-i', str(src),
               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(p))
        out.append({'name': name, 'url': CDN + name, 'seconds': duration(p), 'local': str(p)})
    return src, d, out

def push(files):
    cfg = THEME / 'config.yml'                 # git-ignored; recreate it in a fresh checkout (no secrets in it)
    if not cfg.exists():
        cfg.write_text('development:\n  sass:\n    output_style: nested\n  store: https://skinofab.29next.store\n  theme_id: 34\n')
    if files: subprocess.run(['ntk', 'push', '-a', os.environ['NEXT_API_TOKEN'], *files], cwd=THEME, check=True, capture_output=True)

plan, total = [], 0.0
for job in JOBS['jobs']:
    src, d, parts = parts_of(job)
    plan.append((job, src, parts)); total += sum(math.ceil(p['seconds']) for p in parts)
res = JOBS.get('resolution', '720p')
print(json.dumps([{'key': j['key'], 'parts': [(p['name'], round(p['seconds'], 1)) for p in ps]} for j, _, ps in plan], indent=1))
print(f'{total:.0f} s of video at {res}: about ${total * RATE[res]:.2f} at list price')
if not GO: sys.exit()

auth()
push([str(Path(p['local']).relative_to(THEME)) for _, _, ps in plan for p in ps if p['name'].startswith('gj-src-')])
for job, src, parts in plan:                                        # submit everything first, then poll
    for p in parts:
        st = STATE.setdefault(p['name'], {})
        if st.get('request_id') and st.get('status') not in ('failed', 'nsfw', 'canceled'): continue
        r = call('POST', f'{API}/{ENDPOINT}', {'video_url': p['url'], 'image_urls': JOBS['refs'], 'prompt': job.get('prompt') or JOBS['prompt'],
                                               'resolution': res})
        st.update(request_id=r['request_id'], status_url=r['status_url'], status=r.get('status')); save()
        print('submitted', p['name'], r['request_id'])
pending = {p['name'] for _, _, ps in plan for p in ps if STATE[p['name']].get('status') != 'completed'}
delay = 5.0
while pending:
    for name in sorted(pending):
        st = STATE[name]; r = call('GET', st['status_url']); st['status'] = r['status']
        if r['status'] == 'completed':
            st['video_url'] = (r.get('video') or {}).get('url'); urllib.request.urlretrieve(st['video_url'], WORK / f'out-{name}')
            pending.discard(name); print('done', name)
        elif r['status'] in ('failed', 'nsfw', 'canceled'):
            st['error'] = r.get('error'); pending.discard(name); print('FAILED', name, r['status'], r.get('error'))
        save()
    if pending: time.sleep(delay); delay = min(delay * 1.4, 20)

for job, src, parts in plan:                                        # join parts, original soundtrack on top
    outs = [WORK / f"out-{p['name']}" for p in parts]
    if not all(o.exists() for o in outs): print('incomplete', job['key']); continue
    joined = WORK / f"{job['key']}-video.mp4"
    if len(outs) == 1: joined = outs[0]
    else:
        lst = WORK / f"{job['key']}-list.txt"; lst.write_text(''.join(f"file '{o}'\n" for o in outs))
        sh('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-an', '-c:v', 'libx264', '-preset', 'veryfast',
           '-crf', '18', '-pix_fmt', 'yuv420p', str(joined))
    final = WORK / f"{job['key']}.mp4"
    sh('ffmpeg', '-v', 'error', '-y', '-i', str(joined), '-i', str(src), '-map', '0:v:0', '-map', '1:a:0?', '-c:v', 'copy', '-c:a', 'aac',
       '-shortest', '-movflags', '+faststart', str(final))
    STATE.setdefault('finals', {})[job['key']] = {'source': job['video'], 'file': str(final)}; save()
    print('final', final, round(duration(final), 1), 's')

# keep the finished videos with the brand assets and tell apf_pages.py to use them (queue/video-swaps.json)
KEEP = Path('brand/videos'); KEEP.mkdir(parents=True, exist_ok=True)
swaps_p = Path(__file__).resolve().parent / 'queue' / 'video-swaps.json'
swaps = json.loads(swaps_p.read_text()) if swaps_p.exists() else {}
for key, f in STATE.get('finals', {}).items():
    dst = KEEP / f'{key}.mp4'
    dst.write_bytes(Path(f['file']).read_bytes()); swaps[f['source']] = str(dst)
swaps_p.write_text(json.dumps(swaps, indent=1)); print(len(swaps), 'videos mapped in', swaps_p)

# put them live without a rebuild: new content-hashed names in the theme, every template reference rewritten, pushed
import hashlib, re
ren = {}
for old, f in swaps.items():
    data = Path(f).read_bytes()
    new = re.sub(r'-[0-9a-f]{6}$', '', Path(old).stem) + '-g' + hashlib.md5(data).hexdigest()[:6] + '.mp4'
    (THEME / 'assets' / 'sf' / 'media' / new).write_bytes(data); ren[old] = new
changed = []
for p in list(THEME.glob('templates/**/*.html')) + list(THEME.glob('partials/**/*.html')) + list(THEME.glob('layouts/*.html')):
    s = p.read_text(encoding='utf-8', errors='surrogateescape'); n = s
    for old, new in ren.items(): n = n.replace(old, new)
    if n != s: p.write_text(n, encoding='utf-8', errors='surrogateescape'); changed.append(str(p.relative_to(THEME)))
push([f'assets/sf/media/{n}' for n in ren.values()] + changed)
print('live:', len(ren), 'videos,', len(changed), 'templates updated and pushed')
