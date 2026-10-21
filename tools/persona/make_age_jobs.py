"""Build "make her 45+" edit jobs for every image that still shows a young woman.

usage: python3 -I make_age_jobs.py <groups.json> <young.json> <export_dir> <ref_dir> <out_jobs.json>
- young.json: [{"n", "young", "kind"}] from the visual review
- copies each slot's current master (rebranded export) to <ref_dir>/skf-src-<n>.<ext> so it can be pushed to the
  theme under a never-used name (NEXT's CDN caches by file name) and used as the edit's source image
- the prompt keeps everything but the woman's age; ages and looks rotate so the site shows a range of 45+ women
"""
import json, re, shutil, sys
from PIL import Image
from pathlib import Path

G = {g['n']: g for g in json.load(open(sys.argv[1]))}
YOUNG = [y for y in json.load(open(sys.argv[2])) if y.get('young')]
EXPORT, REF, OUT = Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5]
REF.mkdir(parents=True, exist_ok=True)
CDN = 'https://cdn.29next.store/media/skinofab/themes/34/assets/'
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)
brand = lambda m: 'SKINOFAB' if m.group(0).isupper() else ('Skinofab' if m.group(0)[0].isupper() else 'skinofab')
LOOKS = [
    'about 56, light skin, chin-length silver-blonde hair',
    'about 61, medium olive skin, shoulder-length grey hair',
    'about 52, medium-deep brown skin, short natural hair with grey',
    'about 58, fair skin with a few sun spots, soft grey bob',
    'about 54, light-medium skin, honey-blonde hair with grey roots blended in',
    'about 63, East Asian, light skin, short silver hair',
    'about 50, golden-tan skin, dark hair with silver streaks',
    'about 59, deep brown skin, cropped silver hair',
]
KIND = {
    'closeup': 'This is a close-up crop. Keep exactly the same crop and part of the face; make the visible skin, lips, eyes or brows those of a woman {look}: natural fine lines, slightly thinner lips with soft lip lines, softer jawline, mature but well-cared-for, fresh skin.',
    'ugc': 'This is a casual customer photo or video thumbnail. Replace the young woman with a real-looking woman {look}, same pose, same clothes, same room, same phone/selfie look and quality. Keep any play button, overlay text or captions exactly as they are.',
    'beforeafter': 'This is a before/after image. Replace the young woman in both halves with the same woman {look}, keeping the left/right difference (the before side less even, the after side more even and fresh). Keep labels and layout.',
    'graphic': 'This is a designed graphic. Replace only the young woman in it with a woman {look}, same pose and crop. Keep every word of text, the layout, fonts, colors, icons and product exactly.',
    'model': 'Replace the young woman with a woman {look}, same pose, gesture, crop, clothing and expression. Keep the product, background, lighting and any text exactly.',
}
COMMON = (' Make her look her age honestly: natural fine lines and crow\'s feet, mature skin texture, no airbrushing, '
          'but fresh, even and radiant. If there are several young women, make all of them 45 to 65 with different looks. '
          'Keep the image\'s framing, aspect ratio, crop and composition exactly; no new objects, no new text. Photorealistic.')

jobs = []
for i, y in enumerate(sorted(YOUNG, key=lambda y: y['n'])):
    g = G[y['n']]
    src = EXPORT / 'assets' / 'img' / BRAND.sub(brand, g['master'])
    if not src.exists(): print('missing', src.name); continue
    ref = f"skf-src-{g['n']}{src.suffix.lower()}"
    im = Image.open(src)
    if im.mode in ('RGBA', 'LA', 'P') and im.convert('RGBA').getchannel('A').getextrema()[0] < 250:
        # transparent cut-out: flatten on the site's light grey so the model doesn't invent a black background
        # (restore_alpha.py puts the original transparency back afterwards)
        flat = Image.new('RGBA', im.size, (242, 242, 242, 255)); flat.alpha_composite(im.convert('RGBA'))
        flat.convert('RGB').save(REF / ref)
    else:
        shutil.copy2(src, REF / ref)
    look = LOOKS[i % len(LOOKS)]
    prompt = 'Edit the first image. ' + KIND.get(y.get('kind'), KIND['model']).format(look=look) + COMMON
    jobs.append({'n': g['n'], 'key': f"age-{g['n']}", 'kind': y.get('kind'), 'aspect': 'auto', 'w': g['w'], 'h': g['h'],
                 'refs': [CDN + ref], 'prompt': prompt})
json.dump(jobs, open(OUT, 'w'), indent=1)
print(len(jobs), 'jobs', {k: sum(j['kind'] == k for j in jobs) for k in KIND})
