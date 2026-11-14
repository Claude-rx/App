#!/usr/bin/env python3
"""Get Rid Of — lean sales page for /mouse-pouches/ (campaign 2362). Replaces the page-builder clone that
build_pdp.mjs produced (2.3 MB of HTML, ~5 s to first paint on a 4G phone); that builder is kept for rollback.

    python3 tools/funnel/getridof/build_lp.py        # writes campaigns/getridof/src/mouse-pouches/index.html + assets/lp/

Hand-written template (lp/page.html), styles (lp/lp.css) and script (lp/lp.js) are inlined into one document:
no framework, no web fonts, no render-blocking request. The first gallery image is embedded, so the first screen
paints from the HTML alone; every other image is right-sized here and lazy-loaded.
Tracking tags (Microsoft Clarity, GA4) come from clarity_id / ga4_id in campaigns/getridof/_data/campaigns.json (the same
keys the checkout and offer pages use) and stay off while the ids are empty.
"""
import base64
import io
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'tools/funnel/getridof/lp'
CAMP = ROOT / 'campaigns/getridof/src/mouse-pouches'
SRC = CAMP / 'assets/pdp'            # new-packaging images (swap_images.py output, committed)
OUT = CAMP / 'assets/lp'

# name -> (source in assets/pdp, width, WebP quality)
IMAGES = {
    'hero-1': ('t12-rodent-57d2b1.png', 1024, 80),
    'hero-2': ('image2-829fe1.webp', 800, 76), 'hero-3': ('image3-597645.webp', 800, 76), 'hero-4': ('image4-ef9455.webp', 800, 76),
    'hero-5': ('image5-4e7092.webp', 800, 76), 'hero-6': ('image6-7a8fe2.webp', 800, 76), 'hero-7': ('image7-6cb854.webp', 800, 76),
    'problem': ('gro-problem-pantry.webp', 720, 74), 'scent-trail': ('gro-scent-trail.webp', 720, 74), 'dream': ('gro-dream-kitchen.webp', 720, 74),
    'before': ('gro-before-sink.webp', 640, 72), 'after': ('gro-after-sink.webp', 640, 72),
    'safe-home': ('Frame_1484584678-e0d344.webp', 720, 74), 'guarantee': ('Gemini_Generated_Image_3vtc0h3vtc0h3vtc_2_1-16ab3c.webp', 720, 74),
    'oil-peppermint': ('Frame_1484584545-e824f3.webp', 480, 70), 'oil-cinnamon': ('Frame_1484584546-e77b4c.webp', 480, 70),
    'oil-cedar': ('Frame_1484584547-503ae3.webp', 480, 70), 'oil-castor': ('Frame_1484584548-3ec508.webp', 480, 70),
    'pack-1': ('Gemini_Generated_Image_ma08i2ma08i2ma08_1_1991c301-7c7eb2.webp', 160, 78),
    'pack-3': ('Group_1484581866-04f2c7.webp', 200, 78), 'pack-5': ('Group_1484581864-71aab5.webp', 200, 78),
    'av-robert': ('Frame_1484584519_2-8927b5.webp', 88, 80), 'av-tom': ('Frame_1484584519_1-2daa3e.webp', 88, 80),
    'av-amelia': ('Frame_1484584519_3-c5c0cd.webp', 88, 80), 'av-dave': ('Frame_1484584520-9e9157.png', 88, 80),
    'av-gary': ('Frame_1484584520_66c4055f-d094-4e29-b545-8ddee8d7e-07a331.png', 88, 80),
    'av-russel': ('Frame_1484584519_ea551e31-7ec5-4687-8149-17d3c8965-97a552.webp', 88, 80),
    'av-dale': ('Frame_1484584519_1_ff003d52-42a0-49c8-89d3-f0a91aa-a2c534.webp', 88, 80),
    'av-thomas': ('Frame_1484584687-298c6b.png', 88, 80), 'av-earl': ('Frame_1484584520_47133397-48d5-4b69-bd33-cf40c8238-44c647.png', 88, 80),
}
HERO_INLINE = (560, 62)   # width, quality of the embedded first image (sharper hero-1 swaps in after load on big screens)

# The page's existing customer stories (carried over from the previous page, not written here).
REVIEWS = [
    ('robert', 'Robert L.', '🏠 Homeowner · Columbus, Ohio', '“Finally something that keeps them gone - for good.”',
     'Tried every trap and poison for 3 years straight. Placed pouches under the kitchen sink and along the basement wall. Eleven days later, not a single mouse. Six weeks on, still nothing.'),
    ('tom', 'Tom W.', '🏠 Homeowner · Nashville, Tennessee', '“I wasted $200+ on traps, then I found this.”',
     'Pouches behind the fridge, along the garage wall, inside the crawl space. Week two: completely silent. Was ready to call an exterminator and spend $400. Glad I didn\'t.'),
    ('amelia', 'Amelia R.', '🏠 Homeowner · Rochester, New York', '“First October in six years I haven\'t had to deal with them.”',
     'Old house, lots of entry points. Lined every basement corner and both garage door edges before the cold hit. Usually by mid-October I\'m setting traps every other day. Not this year.'),
    ('dave', 'Dave B.', '🚐 Full-time RV · Bozeman, Montana', '“Three months in a field in Texas. Not one mouse.”',
     'We live in our RV full time. Put pouches under every seat, in both storage bays and the slide-out compartments. Haven\'t touched a trap since.'),
    ('gary', 'Gary M.', '🚐 RV owner · Austin, Texas', '“Opened it in spring and not a single mouse.”',
     'Mice had chewed wiring and shredded insulation two winters in a row. Tucked pouches into the engine bay, wheel wells and every storage compartment. Four months later: untouched.'),
    ('russel', 'Russel O.', '🚐 RV owner · Duluth, Minnesota', '“This season: completely clean.”',
     'Placed pouches in all four storage compartments and two under the dinette before closing her up. Six months later I opened it up spotless.'),
    ('dale', 'Dale T.', '🌾 Farmer · Lancaster, Pennsylvania', '“Six weeks in, the feed room is clean. Dogs are fine.”',
     'Put pouches around the entire feed storage perimeter, every 8 feet. Within two weeks the droppings stopped. Nothing to clean up: no dead mice, no poison, no mess.'),
    ('thomas', 'Thomas E.', '🌾 Farmer · Des Moines, Iowa', '“First clean winter in eight years.”',
     'Covered the feed room perimeter and tucked pouches inside three pieces of equipment that always got hit. Didn\'t have to pull a single trap all season.'),
    ('earl', 'Earl H.', '🌾 Farmer · Abilene, Kansas', '“Bins have been clean for four months.”',
     'Mice got into my grain bins two years running. Placed pouches around every bin entry and along the floor perimeter. Two weeks later the activity stopped.'),
]

AXON = ('<script>!function(e,r){var t=["https://s.axon.ai/pixel.js","https://c.albss.com/p/l/loader.iife.js"];if(!e.axon){var a=e.axon=function(){'
        'a.performOperation?a.performOperation.apply(a,arguments):a.operationQueue.push(arguments)};a.operationQueue=[],a.ts=Date.now(),a.eventKey="%KEY%";'
        'for(var n=r.getElementsByTagName("script")[0],o=0;o<t.length;o++){var i=r.createElement("script");i.async=!0,i.src=t[o],n.parentNode.insertBefore(i,n)}}}'
        '(window,document);axon("init");window.__axonEventKey="%KEY%";window.__axonImageUrl=%IMG%;</script>')
# Campaign Cart SDK on the sales page: campaign page view + attribution capture. Loaded after the page is interactive.
SDK = ("<script>window.addEventListener('load',function(){setTimeout(function(){var c=document.createElement('script');c.src='/mouse-pouches/config.js';"
       "c.onload=function(){var s=document.createElement('script');s.type='module';s.src='https://cdn.jsdelivr.net/gh/NextCommerceCo/campaign-cart@v%VER%/dist/loader.js';"
       "document.head.appendChild(s)};document.head.appendChild(c)},800)});</script>")
CLARITY = ('<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;'
           't.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y)})(window,document,"clarity","script","%ID%");</script>')
GA4 = ('<script async src="https://www.googletagmanager.com/gtag/js?id=%ID%"></script><script>window.dataLayer=window.dataLayer||[];'
       'function gtag(){dataLayer.push(arguments)}gtag("js",new Date());gtag("config","%ID%");</script>')


def webp(src, width, quality):
    im = Image.open(src)
    im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    if im.mode == 'RGBA' and im.getextrema()[3][0] == 255: im = im.convert('RGB')
    if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=quality, method=6)
    return buf.getvalue(), im.size


def tracking_tags(t):
    out = []
    if re.fullmatch(r'[a-z0-9]{8,14}', t.get('clarity_id') or ''): out.append(CLARITY.replace('%ID%', t['clarity_id']))
    if re.fullmatch(r'G-[A-Z0-9]{6,14}', t.get('ga4_id') or ''): out.append(GA4.replace('%ID%', t['ga4_id']))
    return '\n'.join(out), [k for k in ('clarity_id', 'ga4_id') if t.get(k)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (src, width, q) in IMAGES.items():
        data, _ = webp(SRC / src, width, q)
        (OUT / f'{name}.webp').write_bytes(data); total += len(data)
    hero, _ = webp(SRC / IMAGES['hero-1'][0], *HERO_INLINE)
    camp = json.loads((ROOT / 'campaigns/getridof/_data/campaigns.json').read_text())['mouse-pouches']
    key = camp.get('axon_event_key') or ''
    if key and not re.fullmatch(r'[0-9a-fA-F-]{36}', key): raise SystemExit('axon_event_key is not an event key')
    axon = AXON.replace('%KEY%', key).replace('%IMG%', json.dumps(camp.get('axon_image_url') or '')) if key else ''
    reviews = '\n'.join(
        f'    <article class="rev"><span class="st" aria-label="5 out of 5 stars">★★★★★</span><h3>{h}</h3><p>{body}</p>'
        f'<footer><img src="/mouse-pouches/lp/av-{slug}.webp" alt="" width="40" height="40" loading="lazy"><span><b>{who}</b>{where} · <span class="vb">✓ Verified buyer</span></span></footer></article>'
        for slug, who, where, h, body in REVIEWS)
    tags, on = tracking_tags(camp)
    css = re.sub(r'/\*.*?\*/', '', (HERE / 'lp.css').read_text(), flags=re.S)
    css = re.sub(r'\s*\n\s*', '', css)
    js = (HERE / 'lp.js').read_text()
    html = (HERE / 'page.html').read_text()
    for token, value in (('@@CSS@@', css), ('@@JS@@', js), ('@@AXON_HEAD@@', axon), ('@@FUNNEL@@', camp['name']),
                         ('@@HERO_DATA@@', 'data:image/webp;base64,' + base64.b64encode(hero).decode()),
                         ('@@REVIEWS@@', reviews), ('@@TRACKING@@', SDK.replace('%VER%', camp['sdk_version']) + ('\n' + tags if tags else ''))):
        assert html.count(token) == 1, token
        html = html.replace(token, value)
    assert '@@' not in html and '{%' not in html and '{{' not in html and '</script' not in js.lower()
    assert not re.search(r'sofyre', html, re.I)
    front = ('---\npage_layout: pdp.html\ntitle: "Rodent Repellent Pouches – Get Rid Of"\npage_type: product\n'
             '# Generated by tools/funnel/getridof/build_lp.py from tools/funnel/getridof/lp/ — edit those, not this file.\n---\n')
    (CAMP / 'index.html').write_text(front + '{% raw %}' + html + '{% endraw %}\n', encoding='utf-8')
    (CAMP / '_layouts/pdp.html').write_text('{{ content }}\n')
    print(f'wrote {CAMP / "index.html"}: {len(html) / 1024:.0f} KB (hero inline {len(hero) / 1024:.0f} KB, css {len(css) / 1024:.0f} KB, js {len(js) / 1024:.0f} KB); '
          f'{len(IMAGES)} images, {total / 1024:.0f} KB lazy; tracking tags on: {on or "none"}')


if __name__ == '__main__':
    main()
