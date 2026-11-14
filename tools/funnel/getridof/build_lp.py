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
SECTIONS = ROOT / 'brand/getridof/sections'   # generated section images (Kie), looked up first
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
    'reveal': ('gro-solution-reveal.webp', 720, 74),
    'timeline': ('gro-timeline.webp', 720, 76),
    'pantry-before': ('gro-pantry-before.webp', 640, 72), 'pantry-after': ('gro-pantry-after.webp', 640, 72),
    'garage-before': ('gro-garage-before.webp', 640, 72), 'garage-after': ('gro-garage-after.webp', 640, 72),
    'fam-baby': ('gro-fam-baby.webp', 640, 74), 'fam-kids': ('image3-597645.webp', 640, 74), 'fam-pets': ('gro-fam-pets.webp', 640, 74),
    'ugc-1': ('gro-ugc-1.webp', 520, 74), 'ugc-2': ('gro-ugc-2.webp', 520, 74), 'ugc-3': ('gro-ugc-3.webp', 520, 74), 'ugc-4': ('gro-ugc-4.webp', 520, 74),
    'av-thomas': ('Frame_1484584687-298c6b.png', 88, 80), 'av-earl': ('Frame_1484584520_47133397-48d5-4b69-bd33-cf40c8238-44c647.png', 88, 80),
}
HERO_INLINE = (560, 62)   # width, quality of the embedded first image (sharper hero-1 swaps in after load on big screens)

# The page's customer stories, carried over from the original page (not written here): (tab, avatar, name, who/where,
# "before" quote, headline, story).
REVIEWS = [
    ('home', 'robert', 'Robert L.', '🏠 Homeowner · Columbus, Ohio', '“Tried every trap and poison for 3 years straight. Nothing lasted more than a week."',
     '“Finally something that keeps them gone - for good.”',
     "Placed pouches under the kitchen sink and along the basement wall. Eleven days later, not a single mouse. Six weeks on — still nothing. My wife actually feels comfortable in her own kitchen again. I genuinely wish I'd found this years ago."),
    ('home', 'tom', 'Tom W.', '🏠 Homeowner · Nashville, Tennessee', '"Spent close to $200 on traps, poison and one of those ultrasonic plug-ins. Nothing worked longer than a few days."',
     'I wasted $200+ on traps, then I found this Get Rid Of solution...',
     "Pouches behind the fridge, along the garage wall, inside the crawl space. Week two - completely silent. Was ready to call an exterminator and spend $400. Glad I didn't."),
    ('home', 'amelia', 'Amelia R.', '🏠 Homeowner · Rochester, New York', '"Old house, lots of entry points. Had mice every single winter for six years." "First October in six years I haven\'t had to deal with them."',
     '“This just works, that’s all I want to say!!!',
     "Lined every basement corner and both garage door edges before the cold hit. Usually by mid-October I'm setting traps every other day. Not this year. Not one."),
    ('rv', 'dave', 'Dave B.', '🚐 Full-Time RV · Bozeman, Montana', '"We live in our RV full time. Tried every spray and trap on the market — mice kept coming back every time we parked anywhere rural."',
     '"Three months in a field in Texas. Not one mouse the entire time."',
     "Put pouches under every seat, in both storage bays and the slide-out compartments. Didn't think something this simple would work. Haven't touched a trap since. For full-timers this is the only thing that's actually worked for us."),
    ('rv', 'gary', 'Gary M.', '🚐 RV Owner · Austin, Texas', '"Mice had completely destroyed my RV two winters in a row. Chewed wiring, shredded insulation — thousands in damage."',
     '"Opened it in spring and not a single mouse. First time in three years."',
     'Tucked pouches into the engine bay, wheel wells and every storage compartment before putting her away for winter. Pulled her out four months later completely untouched. Already ordered a second set for next season.'),
    ('rv', 'russel', 'Russel O.', '🚐 RV Owner · Duluth, Minnesota', '"Pulled my camper out last April and the damage was unreal. Chewed through seat cushions, found droppings everywhere."',
     '"This season — completely clean. Not a dropping, not a chew mark. Nothing."',
     'Placed pouches in all four storage compartments and two under the dinette before closing her up. Six months later opened it up spotless. Saved myself a $600 repair bill minimum.'),
    ('farm', 'dale', 'Dale T.', '🌾 Farmer · Lancaster, Pennsylvania', '"Lost so much feed to mice every single year. Tried poison but worried constantly about my dogs and cattle getting into it."',
     '"Six weeks in — feed room is clean. Dogs are fine. Haven\'t touched a trap since."',
     "Put pouches around the entire feed storage perimeter, every 8 feet like the instructions said. Within two weeks the droppings stopped completely. What got me is there's nothing to clean up — no dead mice, no poison, no mess. Just gone."),
    ('farm', 'thomas', 'Thomas E.', '🌾 Farmer · Des Moines, Iowa', '"Every fall without fail — mice moved into the equipment shed and feed room the second the temperature dropped."',
     '"Set them out in September this year. October came and went. Nothing."',
     "Covered the feed room perimeter and tucked pouches inside three pieces of equipment that always got hit. Didn't have to pull a single trap all season. First clean winter in eight years."),
    ('farm', 'earl', 'Earl H.', '🌾 Farmer · Abilene, Kansas', '"Mice got into my grain bins two years running. Lost hundreds of dollars of feed before I even noticed."',
     '"Bins have been clean for four months. Not a single dropping."',
     'Placed pouches around every bin entry and along the floor perimeter. Two weeks later the activity stopped completely. No poison near my feed, no dead mice to find. Just gone.'),
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


def expert_card():
    """Authority figure: only a real, consenting expert from brand/getridof/expert.json (approved: true). Never generated."""
    e = json.loads((ROOT / 'brand/getridof/expert.json').read_text())
    esc = lambda v: str(v or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    if e.get('approved') is not True or not all(str(e.get(k) or '').strip() for k in ('name', 'credentials', 'bio', 'photo_file', 'quote')):
        return '', None
    photo = SECTIONS / e['photo_file']
    if not photo.is_file(): raise SystemExit(f'expert photo missing: {photo}')
    data, _ = webp(photo, 240, 80)
    (OUT / 'expert.webp').write_bytes(data)
    certs = ''.join(f'<li><b>{esc(c["title"])}</b> · {esc(c["issuer"])}' + (f' · No. {esc(c["number"])}' if c.get('number') else '') + '</li>'
                    for c in e.get('certifications') or [] if c.get('title') and c.get('issuer'))
    who = esc(e['credentials']) + (' · ' + esc(e['organization']) if e.get('organization') else '') + (f' · {esc(e["years_experience"])} years in the field' if e.get('years_experience') else '')
    return (f'  <div class="xp"><div class="xp__h"><img src="/mouse-pouches/lp/expert.webp" alt="{esc(e["name"])}" width="92" height="92" loading="lazy">'
            f'<div><b>{esc(e["name"])}</b><span>{who}</span></div></div><p style="margin:0">{esc(e["bio"])}</p>'
            + (f'<ul aria-label="Certifications">{certs}</ul>' if certs else '') +
            f'<blockquote>“{esc(e["quote"])}”</blockquote>' + (f'<small>{esc(e["disclosure"])}</small>' if e.get('disclosure') else '') + '</div>'), e['name']


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (src, width, q) in IMAGES.items():
        data, _ = webp(SECTIONS / src if (SECTIONS / src).is_file() else SRC / src, width, q)
        (OUT / f'{name}.webp').write_bytes(data); total += len(data)
    hero, _ = webp(SRC / IMAGES['hero-1'][0], *HERO_INLINE)
    camp = json.loads((ROOT / 'campaigns/getridof/_data/campaigns.json').read_text())['mouse-pouches']
    key = camp.get('axon_event_key') or ''
    if key and not re.fullmatch(r'[0-9a-fA-F-]{36}', key): raise SystemExit('axon_event_key is not an event key')
    axon = AXON.replace('%KEY%', key).replace('%IMG%', json.dumps(camp.get('axon_image_url') or '')) if key else ''
    def card(r):
        _, slug, who, where, pre, head, body = r
        return (f'    <article class="rev"><div class="rev__t"><span class="st" aria-label="5 out of 5 stars">★★★★★</span><span class="vb vb--b">✓ Verified Buyer</span></div>'
                f'<p class="rev__q">{pre}</p><h3>{head}</h3><p>{body}</p>'
                f'<footer><img src="/mouse-pouches/lp/av-{slug}.webp" alt="" width="40" height="40" loading="lazy"><span><b>{who}</b>{where}</span></footer></article>')
    reviews = '\n'.join(
        f'  <div class="revs" data-pane="{tab}"{"" if n == 0 else " hidden"}>\n' + '\n'.join(card(r) for r in REVIEWS if r[0] == tab) + '\n  </div>'
        for n, tab in enumerate(('home', 'rv', 'farm')))
    tags, on = tracking_tags(camp)
    expert, expert_name = expert_card()
    css = re.sub(r'/\*.*?\*/', '', (HERE / 'lp.css').read_text(), flags=re.S)
    css = re.sub(r'\s*\n\s*', '', css)
    js = (HERE / 'lp.js').read_text()
    html = (HERE / 'page.html').read_text()
    for token, value in (('@@CSS@@', css), ('@@JS@@', js), ('@@AXON_HEAD@@', axon), ('@@FUNNEL@@', camp['name']),
                         ('@@HERO_DATA@@', 'data:image/webp;base64,' + base64.b64encode(hero).decode()),
                         ('@@REVIEWS@@', reviews), ('@@EXPERT@@', expert), ('@@TRACKING@@', SDK.replace('%VER%', camp['sdk_version']) + ('\n' + tags if tags else ''))):
        assert html.count(token) == 1, token
        html = html.replace(token, value)
    assert '@@' not in html and '{%' not in html and '{{' not in html and '</script' not in js.lower()
    assert not re.search(r'sofyre', html, re.I)
    front = ('---\npage_layout: pdp.html\ntitle: "Rodent Repellent Pouches – Get Rid Of"\npage_type: product\n'
             '# Generated by tools/funnel/getridof/build_lp.py from tools/funnel/getridof/lp/ — edit those, not this file.\n---\n')
    (CAMP / 'index.html').write_text(front + '{% raw %}' + html + '{% endraw %}\n', encoding='utf-8')
    (CAMP / '_layouts/pdp.html').write_text('{{ content }}\n')
    print(f'wrote {CAMP / "index.html"}: {len(html) / 1024:.0f} KB (hero inline {len(hero) / 1024:.0f} KB, css {len(css) / 1024:.0f} KB, js {len(js) / 1024:.0f} KB); '
          f'{len(IMAGES)} images, {total / 1024:.0f} KB lazy; tracking tags on: {on or "none"}; expert card: {expert_name or "off (no approved expert in brand/getridof/expert.json)"}')


if __name__ == '__main__':
    main()
