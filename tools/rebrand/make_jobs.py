"""Build the image-regeneration job list from groups.json + class.json.

usage: python3 -I make_jobs.py <groups.json> <class.json> <out_jobs.json>
Each job: n, master file, public source URL (theme 34 CDN, pre-rebrand file name), logo reference URL,
aspect ratio (nearest the endpoint supports) and the edit prompt for its class (foundation / logo / pink graphic).
"""
import json, sys
CDN = 'https://cdn.29next.store/media/skinofab/themes/34/assets/'
RATIOS = {'1:1': 1, '3:2': 1.5, '2:3': 2 / 3, '4:3': 4 / 3, '3:4': .75, '16:9': 16 / 9, '9:16': 9 / 16, '21:9': 21 / 9}
KEEP = ('Edit the first image. Keep everything else exactly the same: people, faces, skin, hands, pose, composition, '
        'framing, camera angle, lighting, shadows, background, props and any marketing text or graphics. ')
CCF = ('Change ONLY the Color Changing Foundation bottle(s): make the whole bottle and its cap full matte black, and replace '
       'the SMOOCHE logo on it with the SKINOFAB wordmark shown in the second image, printed in white, same position, '
       'orientation, size and perspective as the old logo; keep the bottle\'s small print (COLOR CHANGING FOUNDATION, '
       '15 SPF, 30 ml / 1.01 fl oz) in white. If other branded products appear, keep their colors and only replace their '
       'SMOOCHE logo with the SKINOFAB wordmark in the original logo\'s color. ')
LOGO = ('Change ONLY the brand name: everywhere the SMOOCHE / smooche logo or word appears (on products, packaging, sachets, '
        'boxes, tools, screens or signs), replace it with the SKINOFAB wordmark shown in the second image, matching the '
        'original logo\'s color, position, orientation, size, perspective and print quality. Keep all product colors and '
        'shapes unchanged. ')
PINK = ('Make the designed graphic elements black and white: pink background panels, pink headline text, pink icons and '
        'pink design accents become black (text on them white) or white/light grey. Do not recolor products, skin, lips or photos. ')
END = 'Any written word "Smooche" becomes "Skinofab". Photorealistic, same resolution and sharpness, no new objects, no extra text.'

groups = {g['n']: g for g in json.load(open(sys.argv[1]))}
jobs = []
for c in json.load(open(sys.argv[2])):
    if not (c['logo'] or c['ccf'] or c['pink_graphic']): continue
    g = groups[c['n']]
    r = g['w'] / g['h']
    ar = min(RATIOS, key=lambda k: abs(RATIOS[k] - r))
    body = CCF if c['ccf'] else (LOGO if c['logo'] else '')
    prompt = KEEP + body + (PINK if c['pink_graphic'] else '') + END
    jobs.append({'n': c['n'], 'master': g['master'], 'w': g['w'], 'h': g['h'], 'src': CDN + g['master'],
                 'logo_ref': CDN + ('skf-ref-logo-on-black.png' if c['ccf'] else 'skf-ref-logo-on-white.png'),
                 'aspect_ratio': ar, 'kind': 'ccf' if c['ccf'] else ('logo' if c['logo'] else 'pink'), 'prompt': prompt})
json.dump(jobs, open(sys.argv[3], 'w'), indent=1)
print(len(jobs), {k: sum(j['kind'] == k for j in jobs) for k in ('ccf', 'logo', 'pink')})
