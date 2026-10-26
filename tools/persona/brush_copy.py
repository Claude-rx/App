"""The Lymphatic Brush: product page copy, offer and sections, built from the owner's Solena page
(https://thesolena.com/products/the-lymphatic-brush), under the SKINOFAB name and in the SKINOFAB look.

Solena's offer, with the claims nothing backs taken out: no "drains fluid", no "less puffy from the first use" as a
promise, no "10 years younger" or "sculpted face" clips, no buyer counts, no Solena reviews. The brush is a light, dry
massage for the look of morning puffiness, and the page says so, including what it will not do. The page has the
Adaptive Peptide Foundation page's structure, section by section (twin.py, TWIN below); until the brush has reviews of
its own, the reviews near the top are the foundation's, labelled as theirs, and the review wall says "no reviews yet".

Read by apply_persona.py (it builds products/the-lymphatic-brush.html from the foundation page's markup) and by
setup_brush_offers.py (the NEXT product, its three bundles and their prices).
"""
import re
import html, json
from pathlib import Path
import support_copy

KEY, MEDIA_BASE = 'brush', 9300000000000          # section ids, gallery media ids
HANDLE = 'the-lymphatic-brush'
TITLE = 'The Lymphatic Brush'
SHOPIFY_ID, SHOPIFY_VARIANT = 15517563191626, 61233683038538       # Solena's ids (the design markup carries them)
PRICE, COMPARE = '24.95', '24.95'                                # one brush; no "was" price (a new product)
EMAIL = 'hello@skinofab.com'
DESCRIPTION = ('<p>A 3-minute depuffing massage for your morning face. Hundreds of ultra-soft tips sweep from under '
               'your eyes, along your cheeks and jaw and down your neck with a light touch, on dry skin, no oil. '
               'Includes a SKINOFAB travel case.</p>')
META_TITLE = 'The Lymphatic Brush | A 3-minute depuffing massage | SKINOFAB'
META_DESCRIPTION = ('A soft-bristle face brush for the look of morning puffiness around the eyes, cheeks and jaw. Dry skin, '
                    'no oils, 3 minutes. 30-day money-back guarantee.')

IMG = Path(__file__).resolve().parents[2] / 'brand' / 'lymphatic-brush'   # brush_assets.py
IMG_PREFIX, GIFT_PREFIX = 'skinofab-lymphatic-brush', 'skinofab-brush-gift'
OFFERS_FILE, REVIEWS_DIR, AMAZON_FILE = 'brush-offers.json', 'reviews-brush', 'amazon-brush.json'
EYEBROW = None
# the gallery (brush_assets.py writes brand/lymphatic-brush/<name>.jpg), first one eager
GALLERY = ['hero', 'case', 'how-to-use', 'features', 'vs-tools']
# (the look, not a result: "depuff your face" claimed more than the page's own careful copy, review 7)
HERO = {'title': ['A FRESHER', 'MORNING LOOK'], 'in': 'IN', 'accent': '3 MINUTES',
        'facts': ['Soft bristles, light touch', 'On dry skin, no oils', 'Eyes, cheeks & jaw']}

# Solena's page media (the owner's files), fetched and rebranded by brush_assets.py
_CDN = 'https://cdn.shopify.com/s/files/1/0986/6890/4778/files/'
SOURCES = {
    'gallery-1.png': _CDN + '1-1.png',
    'gallery-2.png': _CDN + '2_647a77d8-ecc9-4c68-9cf8-ebafc5ddef18.png',
    'gallery-3.png': _CDN + '3_e4dbf29c-79a0-47c4-b257-f898340eb298.png',
    'gallery-4.png': _CDN + '4_921c104b-41ed-46ee-8663-3593d54b21ac.png',
    'gallery-5.png': _CDN + '5_4e581ffa-3a9a-45ec-928f-52eca5371c08.png',
    'gallery-6.png': _CDN + '6_64ee026e-4654-40ee-9c07-c2fb2deebe43.png',
    'gallery-7.png': _CDN + '7_d665b398-5393-4a97-b8b6-d4ab8fa1ad85.png',
    'mech-1.webp': _CDN + 'solena-mecanisme-1_png.webp',
    'mech-2.webp': _CDN + '12.webp',
    'mech-3.webp': _CDN + '13_066019c7-5052-453a-85ef-c88ff83fd9c1.webp',
    'compare-ours.png': 'https://thesolena.com/cdn/shop/files/v1.png',
    'compare-copy.png': 'https://thesolena.com/cdn/shop/files/v2.png',
    'avatar-1.webp': _CDN + '20.webp',
    'avatar-2.webp': _CDN + '22.webp',
    'avatar-3.webp': _CDN + '21.webp',
    'mini-1.avif': _CDN + '1770226598__0__DDD4Tqw9__Testi-1__original.avif',
    'mini-2.webp': _CDN + '15.webp',
    'mini-3.webp': _CDN + '14.webp',
    'gift-case.png': _CDN + '04_7.png',
    'gift-body-brush.png': _CDN + '05_6.png',
    'tutorial.mp4': 'https://cdn.shopify.com/videos/c/o/v/2e24d81750d946a495b7b884ec2e5cb9.mp4',
    **{f'video-{k}.mp4': f'https://thesolena.com/cdn/shop/videos/c/vp/{v}/{v}.HD-1080p-7.2Mbps-{n}.mp4' for k, (v, n) in enumerate([
        ('1966d65729cc4b3cba7e1197532454fc', 76975461), ('3213af3ee2434768b31b341042c7e776', 76975463),
        ('4941a5c981c34fdca9fedca48e4fb5c7', 76975462), ('a9b2bac392234c30b4518342bcd63c28', 76975464),
        ('b8b4b963beed4325a115c95383f7a9c1', 76975460), ('cf20c9b98e3742e0800dc913fc385a9b', 76975465)], 1)},
}

# the buy box --------------------------------------------------------------------------------------------------------
SHIPPING_BADGE = '\U0001F381 FREE SHIPPING'
LEAD = ('A 3-minute morning massage for puffy-looking eyes, cheeks and jaw. Ultra-soft bristles that bend instead of '
        'pressing, on dry skin, no oils.')
# the offer: Solena's three bundles (each a NEXT variant); the free cases and the body brush ship with the order
# the case comes with every brush (no price of its own: "included", not a free gift worth $9.95); the body brush is the
# 3-pack's gift, the price it sells for
GIFTS = {'case': ('Protective case', 'Protective cases', None), 'body': ('Body Dry Brush', 'Body Dry Brushes', '24.95')}
BUNDLES = [
    {'key': '1', 'name': 'Buy 1 Brush', 'note': '', 'variant': '1 brush + free case', 'sku': 'SKF-LYB-1',
     'price': '24.95', 'compare': '24.95', 'gifts': [('case', 1)]},
    {'key': '2', 'name': 'Buy 2 Brushes', 'note': '2-Pack', 'variant': '2 brushes + 2 free cases', 'sku': 'SKF-LYB-2',
     'price': '39.95', 'compare': '49.90', 'badge': 'Recommended', 'default': True, 'gifts': [('case', 2)]},
    {'key': '3', 'name': 'Buy 2 Brushes + 1 FREE', 'note': '3-Pack', 'variant': '3 brushes + 3 free cases + free body brush',
     'sku': 'SKF-LYB-3', 'price': '49.90', 'compare': '74.85', 'badge': 'Best offer', 'gifts': [('case', 3), ('body', 1)]},
]
GIFT_FILES = {'case': 'case', 'body': 'body-brush'}     # brand/lymphatic-brush/gift-<file>.jpg


def _list(items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


# the store's shipping terms (the balm's page has the same tab)
SHIPPING_TAB = ('Shipping and returns', support_copy.SHIPPING_TAB_HTML)      # the shipping policy's terms (support_copy.py)


def tabs():
    """The tabs under the buy box, the foundation's six."""
    return [
        ('What makes it different?',
         '<p>Gua sha needs oil, and rollers and stones need pressure. The Lymphatic Brush gives your face the light, '
         'slow sweeps that facial massage for puffiness uses, with hundreds of ultra-soft tips that bend instead of pressing.</p>'
         + _list(['On dry skin, no oils', '3 minutes, every morning', 'Eyes, cheeks, jaw and neck', 'A protective case with every brush'])),
        ('Does it work on my skin?',
         '<p>Yes, it’s made for mature skin: the bristles bend instead of pulling, so they don’t drag thinner skin or fine lines. '
         'Keep the touch light, especially under the eyes.</p>'
         '<p>Avoid irritated or broken skin, sunburn or active breakouts. If swelling doesn’t go away during the day, or you have a '
         'medical condition, check with your doctor first.</p>'),
        ('How do I use it?',
         '<p><strong>Your 3-minute routine, on clean, dry skin</strong></p>'
         + _list(['Neck: sweep down from under the ear to the collarbone', 'Jaw and cheeks: sweep from your chin along the jaw toward the ear',
                  'Under the eyes: sweep out from the nose to the temples, very lightly', 'Neck again: finish with a few sweeps down the neck'])
         + '<p>Repeat each sweep about 10 times, then do the other side.</p>'
         '<p><strong>Keep it clean:</strong> before each use, sweep the bristles on a cloth with a brush cleaner or 70% alcohol; '
         'once a month, wash only the tips on a damp, soapy cloth, rinse the same way and dry overnight, bristles down. Never '
         'soak it, wet the back or use hot water.</p>'),
        ('How does the money-back guarantee work?',
         f'<p>Try it for <strong>30 days</strong>. If you don’t love it, email us at <a href="mailto:{EMAIL}">{EMAIL}</a> and we’ll refund it in <strong>full</strong>, even opened, no questions asked.</p>'),
        ('Product specifications',
         '<p><strong>Bristles:</strong> Ultra-soft, vegan fibers.</p>'
         '<p><strong>Shape:</strong> A curved, half-moon head that sits between your fingers, no handle to grip.</p>'
         '<p><strong>Dimensions:</strong> Travel-friendly size. Brush: 3.35" x 2.36" (8 x 6 cm) | Case: 3.54" x 2.56" (9 x 6.5 cm).</p>'
         '<p><strong>Usage:</strong> 100% dry-brushing compatible (No oils required).</p>'
         '<p><strong>Bonus:</strong> Includes a protective SKINOFAB travel case that keeps the bristles clean.</p>'),
        SHIPPING_TAB,
    ]


# the sections below: the foundation page's, in its order (twin.py), with the brush's copy ------------------------------
NO_REVIEWS = {'title': 'Customer reviews', 'lead': 'No reviews of the brush yet', 'lead_amazon': 'No SKINOFAB reviews yet',
              'text': 'The Lymphatic Brush is new at SKINOFAB, and we only show reviews from real buyers. Try it for 30 days: '
                      'if you don’t love it, we’ll refund you.',
              'button': 'Try it risk-free', 'write': 'Bought it? Write the first review'}
FAQ = {'items': [
    ('When will I see a difference?',
     'You may see a fresher, less puffy look right after your first 3 minutes. It’s temporary, so it works best every morning. Results vary from person to person.'),
    ('Does it work on mature skin?',
     'Yes. The bristles bend instead of pulling, so they don’t drag thinner skin or fine lines. Keep the touch light, especially under the eyes.'),
    ('Will it scratch or leave red marks?',
     'No. The bristles are ultra-soft and you only need a light touch. If your skin is very reactive, start with a few sweeps and build up.'),
    ('How long does the effect last?',
     'The fresher look lasts through the morning. Puffiness can come back after another night of sleep, a salty meal or a short night. '
     'That’s why a quick 3-minute routine every morning works best.'),
    ('Do I need oil or serum?', 'No. Use it on clean, dry skin. You can apply your skincare right after.'),
    ('Can I use it before my foundation?',
     'Yes, that’s the best time: brush first on dry skin, then your skincare and foundation.'),
    ('What if it doesn’t work for me?',
     'Email hello@skinofab.com within 30 days and we’ll refund it in full, even opened. No questions asked.'),
    ('Is it safe for sensitive skin?',
     'The bristles are soft and the pressure stays light, so it’s gentle on most skin types. Avoid using it on irritated or broken skin, '
     'sunburn or active breakouts. If your swelling doesn’t go away during the day, or if you have a medical condition, check with your doctor first.'),
    ('How often should I use it?', 'Once a day, in the morning, for about 3 minutes. Twice a day is the maximum.'),
    ('How do I keep it clean?',
     'Give the bristles a quick clean on a cloth with a brush cleaner or alcohol before each use, and a gentle wash of the tips once a month. '
     'Full steps are in the “How do I use it?” tab above.'),
]}
STICKY_BUTTON = 'Choose your bundle'

# the cart drawer: 1 brush -> 2 brushes for the price difference
CART_UPGRADE = {'title': 'Upgrade to 2 brushes + 2 free cases', 'button': 'Upgrade'}

# section by section, in the foundation page's order (twin.py names each slot); images are brand/lymphatic-brush/<name>.jpg
# or its source/ photo, clips are <work_dir>/brush/media/<name>.mp4 (brush_assets.py). Creator clips 1 ("shaving 10 years
# off") and 6 ("a sculpted face") make promises the brush can't keep and stay out; they are creators, not verified buyers.
TWIN = {
    'loved': {'lead': 'A fresher face in', 'mark': '3 minutes'},
    'moments': [
        ('how-1', 'Where it shows', 'Morning puffiness shows under the eyes and along the jaw.', 'Where morning puffiness shows'),
        ('how-2', 'What helps', 'Light, slow strokes toward the neck, the way an aesthetician does it by hand.', 'A light massage just under the skin'),
        ('how-3', 'Why the brush', 'Hundreds of soft tips bend instead of pressing.', 'Soft bristles sweeping toward the neck'),
        ('compare-ours', 'Raised, soft tufts', 'They follow your jaw and cheekbones in one stroke.', 'The Lymphatic Brush in hand'),
        ('card', 'Clean between uses', 'Every brush comes with its own protective case.', 'The Lymphatic Brush and its case'),
    ],
    'problem': {
        'img_problem': 'problem', 'img_solution': 'card',
        'photo_alt': 'A woman in her fifties with a puffy morning face',
        'problem': ('The problem', 'You wake up looking', 'more tired than you are'),
        'lede': 'You slept. And still the mirror shows a puffy face: swollen-looking under the eyes, softer along the jaw. It '
                'fades by lunch, but by then you’ve already seen it.',
        'pains': ['Puffy, swollen-looking under-eyes first thing in the morning',
                  'A jawline and cheekbones that look softer than they used to',
                  'Concealer that only makes puffy eyes look bigger',
                  'Gua sha stones that need oil and a tutorial, rollers that cover one narrow line at a time',
                  'Cold spoons and ice cubes that help for five minutes'],
        'close': 'The result: a face that looks tired before your day has even started.',
        'root': ('The root of it', 'It’s not your face.', 'It’s the night.'),
        'causes': [('Puffiness shows up while you sleep',
                    'Lying still all night, your face can wake up looking puffy under the eyes, in the cheeks and along the jaw. '
                    'Salty food and short nights make it worse, and with age it takes longer to fade.'),
                   ('Pressing hard doesn’t help',
                    'Facial massage for puffiness uses light, slow strokes toward the neck, the way an aesthetician does it by hand. '
                    'A gua sha stone needs oil to glide and pressure to work; a roller presses one hard line at a time.'),
                   ('It comes back every morning',
                    'Puffiness returns after a night’s sleep, a salty dinner or a short night. That’s why a quick daily habit works '
                    'better than a one-off treatment.')],
        'root_end': 'So the problem was never you. It’s morning puffiness, and it calls for a light touch every morning.',
        'solution': ('The solution', 'So we made it', 'light and quick'),
        'solution_lede': 'The Lymphatic Brush gives your face the light, slow massage an aesthetician would, in 3 minutes, on dry skin.',
        'fixes': [('Oils and serums to glide', 'Works on dry skin: nothing to wash off.'),
                  ('Pressing too hard', 'Hundreds of soft tips bend instead of pressing.'),
                  ('A tutorial to follow', 'Four sweeps: neck, jaw, under the eyes, neck again.'),
                  ('Twenty minutes in the mirror', '3 minutes, before your coffee.'),
                  ('A tool rolling around the counter', 'A protective case comes with every brush.')],
        'button': 'Get yours', 'note': 'Try it for 30 days, or your money back.',
        'product_alt': 'The Lymphatic Brush and its case',
    },
    # the foundation's expert block: here the brand's own note, signed as the brand (no invented expert)
    'note': {'id': 'sf-note', 'eyebrow': 'Why we made it', 'photo': 'compare-ours', 'photo_alt': 'The Lymphatic Brush in hand',
             'headline_lead': '&hellip;a fresher-looking face,', 'headline_mark': 'before your coffee.',
             'paragraphs': ['We make SKINOFAB for skin after 45. Morning puffiness is one of the first things that changes, and '
                            'the tools for it, gua sha, rollers, ice, ask for oil, pressure or time.',
                            'So we made a brush instead: hundreds of ultra-soft tips that bend instead of pressing, for the '
                            'light, slow sweeps toward the neck that facial massage uses. <strong>On dry skin, in 3 minutes.</strong>',
                            'It’s a gentle massage, not a treatment, and we won’t pretend otherwise. If it isn’t for you, the 30-day '
                            'guarantee has you covered.'],
             'name': 'The SKINOFAB team', 'role': 'Made for skin after 45'},
    'science': {'img': 'how-3', 'alt': 'Soft bristles sweeping just under the skin toward the neck',
                'eyebrow': 'How it works', 'lead': 'A light lymphatic massage,', 'mark': 'in 3 minutes',
                'lede': 'Facial massage for puffiness uses light, slow strokes toward the neck. The brush makes that light touch '
                        'automatic: the bristles bend before they can press.',
                'rows': [('Soft bristles', 'Hundreds of soft tips sweep over the skin; no pressing needed.'),
                         ('Raised tufts', 'They follow your jawline and cheekbones in a single stroke.'),
                         ('Curved shape', 'It fits the curves under your eyes and along your jaw.'),
                         ('Dry use', 'No oil or serum: use it on clean, dry skin, then your skincare.')],
                'note': 'Ultra-soft vegan bristles. A protective travel case comes with every brush.',
                'button': 'Choose your bundle'},
    'iwt': [
        {'img': 'ba-puffy', 'alt': 'A face before and after a 3-minute brush routine (illustration)',
         'lead': 'Fresher-looking', 'mark': 'in 3 minutes',
         'paras': ['Three minutes of light sweeps toward the neck, and the morning puffiness around your eyes and jaw can look '
                   'softer while your face feels awake. The effect is temporary: puffiness comes back after a night’s sleep, a '
                   'salty dinner or a short night, which is why it works best as a daily habit.'],
         'usps': ['3 minutes, every morning', 'On dry skin, no oils']},
        {'img': 'how-to-use', 'alt': 'How to use the Lymphatic Brush',
         'lead': 'How does it work?', 'mark': None,
         'paras': ['Neck: sweep down from under the ear to the collarbone.',
                   'Jaw and cheeks: sweep from your chin along the jaw toward the ear. Under the eyes: sweep out from the nose '
                   'to the temples, very lightly.',
                   'Neck again: finish with a few sweeps down the neck. Repeat each sweep about 10 times, then do the other side.'],
         'usps': ['Light touch, no pressing', 'Easy to clean']},
    ],
    'results': {'title': 'What to expect',
                'cards': [('3 min', 'Every morning, on dry skin', 'Neck, jaw, under the eyes, neck again'),
                          ('Day 1', 'Your face feels awake', 'Morning puffiness can look softer after the first 3 minutes'),
                          ('Daily', 'Works best as a habit', 'Puffiness comes back overnight, so does the routine')]},
    'compare': {'title': 'Why SKINOFAB?', 'others': 'Other tools',
                # rows other tools (gua sha, rollers: the gallery's chart) really lack; the chart ticks rollers for dry
                # skin and no red marks, so the table no longer says otherwise (review 6)
                'rows': ['Hundreds of soft contact points', 'Works with just a light touch', 'Flexible bristles adapt to your face',
                         'Four sweeps, no tutorial', 'A protective case included']},
    'inside': {'title': 'What’s in the box, and why it works',
               'intro': 'The Lymphatic Brush is made for one thing: a light, quick massage for the look of morning puffiness.',
               'cards': [('compare-ours', 'Ultra-soft bristles', 'Vegan fibers that bend instead of pressing'),
                         ('how-2', 'A light touch', 'Just under the skin, where morning puffiness sits'),
                         ('how-1', 'Eyes, cheeks and jaw', 'Where morning puffiness shows first'),
                         ('card', 'A protective case', 'Keeps the bristles clean between uses')]},
    # the foundation's customer clips: none. The creator clips of the routine showed women in their twenties and
    # thirties, with TikTok captions burned in ("the difference is insane"); the brush has no buyers' clips yet
    'cards': None,
    'why': {'title': 'The SKINOFAB difference', 'img': 'card', 'button': 'Choose your pack',
            'features': [('Fresher-looking in 3 minutes', 'A light morning massage for eyes, cheeks and jaw'),
                         ('No oils, no mess', 'Use it on dry skin, then your skincare'),
                         ('30-day money-back guarantee', 'Love it, or email us for a full refund')]},
}


def money(v):
    f = float(v)
    return '$%d' % f if f == int(f) else '$%.2f' % f


def esc(s): return html.escape(s, quote=False)



# buy box pieces ----------------------------------------------------------------------------------------------------
# the free-shipping badge on its own line under the price, at every width: inline, it fitted beside the prices in
# the fallback font and wrapped once Jost loaded (a 0.1 layout shift at 1024, stick review 5)
BUYBOX_CSS = r"""
.sfb-lead{margin:12px 0 0;font-size:16px;line-height:1.55;color:#3b3b3b}
.product__price[data-sf-fixed-price]:before{content:'';flex-basis:100%;order:1;height:0}.product__price[data-sf-fixed-price] .sfb-ship{order:2}.sfb-ship{display:inline-block;margin-left:0;padding:4px 10px;border-radius:999px;background:#151515;color:#fff;font-size:12px;font-weight:600;letter-spacing:.06em;vertical-align:middle;white-space:nowrap}
.sfo--bundle .sfo-main small:empty{display:none}
.sfo--bundle .sfo-gifts{margin-top:12px!important;padding-top:10px!important}
"""




REFILL_TERMS = ('You pay {amount} today, then {amount} every {every} days until you cancel. We email you before every '
                'refill. To skip or cancel, just email hello@skinofab.com. No minimum, no fees.')


def refill_faq(bundles, refill, email='hello@skinofab.com'):
    """The two refill questions the foundation's FAQ answers, for a product sold with Automatic Refills (P.REFILL):
    how they work (each pack's refill price and how often it ships) and how to buy once."""
    unit = refill.get('unit', 'item')
    n = lambda b: b['variant'].split(' (')[0]
    every = ', '.join(f"{money(b['refill'])} every {b['every']} days for {n(b)}" for b in bundles)
    once = ', '.join(f"{money(b['price'])} for {n(b)}" for b in bundles)
    return [('How do Automatic Refills work?',
             f'Your pack ships again on a set schedule, at the refill price: {every}. We email you '
             f'before every refill. '
             f'To skip, delay or cancel, just email {email}: no minimum, no fees.'),
            ('Can I buy just once?',
             f'Yes. In your bag, tap Change under the {unit}, then on the cart page set it to One-time purchase before '
             f'checkout: {once}, with no refills.')]


def pack_label(name):
    """A pack's name without its offer: '3 sticks (buy 2, get 1 free)' or '3 Sticks: buy 2, get 1 free' -> '3 sticks'."""
    return re.split(r':| \(', name)[0]


def picker_html(variants, gift_imgs, css, bundles=None, gifts=None, legend='Choose your bundle', refill=None):
    """The bundle picker: three cards (Solena's bundles, or another product's `bundles` and `gifts`), the default one
    chosen. It sets the form's variant and the button's price. A bundle shows a saving only when its compare-at price
    is above its price.

    refill (the product's REFILL, its bundles carrying 'refill' prices and 'every' days): sold with Automatic Refills
    as the foundation is. A hidden, ticked refill box (the form adds the pack as a refill, every 'every' days of the
    chosen pack), the cards and the title at the refill price against the one-time price, and the refill row and
    terms under the button ([data-sf-renew], [data-sf-refill-terms]) kept in step with the chosen pack. Without it the
    lines are one-time purchases (no refill choice)."""
    bundles, gifts = bundles or BUNDLES, GIFTS if gifts is None else gifts
    on = bool(refill)
    units = lambda b: int(b.get('units') or (b['key'] if b['key'].isdigit() else 1))
    table = {b['key']: {'pk': variants[b['key']], 'price': float(b['price']), 'compare': float(b['compare']),
                        'label': pack_label(b['name']), 'units': units(b),
                        **({'refill': float(b['refill']), 'every': int(b['every'])} if on else {})} for b in bundles}
    default = next((b['key'] for b in bundles if b.get('default')), bundles[0]['key'])
    base, base_compare = float(bundles[0]['price']), float(bundles[0]['compare'])
    now_of = lambda b: float(b['refill' if on else 'price'])
    cards = []
    for b in bundles:
        saves = float(b['compare']) > now_of(b)
        gifts_li = ''.join(
            f'<li><img src="{gift_imgs[k]}" alt="" width="40" height="40" loading="lazy" decoding="async">'
            + (f'<span>+ {n} FREE {esc(gifts[k][0 if n == 1 else 1])}</span><s>{money(float(gifts[k][2]) * n)}</s><b>FREE</b></li>'
               if gifts[k][2] else f'<span>+ {n} {esc(gifts[k][0 if n == 1 else 1])}</span><b>Included</b></li>')
            for k, n in b['gifts'])
        cards.append(
            '<label class="sfo-card sfo-card--gifts">'
            + (f'<em class="sfo-tab">{esc(b["badge"])}</em>' if b.get('badge') else '')
            + f'<span class="sfo-row"><input type="radio" name="sf_pack" value="{b["key"]}"{" checked" if b["key"] == default else ""}>'
            f'<span class="sfo-main"><span class="sfo-name">{esc(b["name"])}'
            + (f'<span class="sfo-save">SAVE {money(round(float(b["compare"]) - now_of(b), 2))}</span>' if saves else '') + '</span>'
            f'<small>{esc(b["note"])}</small></span>'
            f'<span class="sfo-price"><b>{money(now_of(b))}</b>' + (f'<s>{money(b["compare"])}</s>' if saves else '')
            # a pack of several: its price per stick or bottle (stick review 3: two reference prices, no unit price)
            + (f'<small class="sfo-per">{money(round(now_of(b) / units(b), 2))} / {esc(refill["unit"])}</small>'
               if on and refill.get('unit') and units(b) > 1 else '') + '</span></span>'
            + (f'<ul class="sfo-gifts">{gifts_li}</ul>' if gifts_li else '') + '</label>')
    first = next(b for b in bundles if b['key'] == default)
    # inline !important: the design's stylesheets give inputs display:block, which beats the hidden attribute
    box = (f'<input type="checkbox" name="sf_purchase" value="subscribe" data-interval="{refill["interval"]}" '
           f'data-interval-count="{first["every"]}" checked hidden style="display:none !important" aria-hidden="true" tabindex="-1">'
           if on else '')
    # under the cards, while refills are on: what the prices are, and the one-time prices (stick review 2: the cards
    # and their savings did not say they were refill prices)
    # what the crossed-out prices are (every pack's compare-at price is its count bought one at a time), and where
    # one-time is chosen: the cart page, from the drawer's "Change" link (stick review 3: "in your bag" was not it)
    off = min(round(100 * (1 - float(b['refill']) / float(b['price']))) for b in bundles) if on else 0
    one_each = on and refill.get('unit') and all(abs(float(b['compare']) - units(b) * base) < 0.01 for b in bundles)
    note = (f'<p class="sfo-refill-note">Prices with Automatic Refills, {off}% off.'
            + (f' Crossed out: {money(base)} a {esc(refill["unit"])}, bought one at a time.' if one_each else '')
            + ' One-time packs: '
            + ' · '.join(f"{esc(pack_label(b['name']))} {money(b['price'])}" for b in bundles)
            + ' (choose one-time on the cart page).</p>') if on else ''
    return (f"""<div class="sfo sfo--bundle" id="apf-buy" data-sf-offer-picker data-packs='{json.dumps(table)}'>
<style>{css}</style>
<fieldset><legend>{esc(legend)}</legend>{''.join(cards)}</fieldset>
{note}{box}
<script>
(function () {{
  var root = document.currentScript.parentNode;
  var form = root.closest('form');
  var packs = JSON.parse(root.getAttribute('data-packs'));
  var box = root.querySelector('input[name=sf_purchase]');
  function money(v) {{ return '$' + (v % 1 ? v.toFixed(2) : String(v)); }}
  // the title price follows the chosen pack (as the button does), against its compare-at price, with cents: the
  // design's money format drops them (stick review 2: it stayed at the single pack's while the button showed $47)
  var scope = root, head = null;
  while (scope && !head) {{ scope = scope.parentElement; head = scope && scope.querySelector('.product__price-and-badge'); }}
  function titlePrice(now, compare) {{
    var a = head && head.querySelector('.product__price--regular'), was = head && head.querySelector('.product__price--compare');
    var unit = a && / USD\\s*$/.test(a.textContent) ? ' USD' : '';
    if (a) a.textContent = money(now) + unit;
    // the theme's own price script hides it by class when the NEXT variant has no compare-at price
    if (was) {{ was.hidden = !(compare > now); was.classList.remove('hidden'); if (compare > now) was.textContent = money(compare) + unit; }}
  }}
  function sync() {{
    var key = (root.querySelector('input[name=sf_pack]:checked') || {{}}).value || '{default}';
    var pick = packs[key];
    var id = form && form.querySelector('input[name=id]');
    if (id) id.value = pick.pk;
    var sub = !!(box && box.checked), now = sub ? pick.refill : pick.price;
    titlePrice(now, pick.compare);
    // what the title's price is: the chosen pack, with refills (stick review 4: "$47 USD" said neither)
    Array.prototype.forEach.call(document.querySelectorAll('[data-sf-title-note]'), function (e) {{
      e.textContent = pick.label + (sub ? ' with Automatic Refills' + (pick.units > 1 ? ', ' + money(Math.round(now / pick.units * 100) / 100) + ' a ' + e.getAttribute('data-unit') : '') : '');
    }});
    var price = form && form.querySelector('[data-sfb-btn-price]');
    if (price) price.textContent = ' | ' + money(now);
    // the sticky bar names the chosen pack and its price (stick review 7: "From $31" under a title price of $47)
    Array.prototype.forEach.call(document.querySelectorAll('[data-sf-sticky-pack]'), function (e) {{ e.textContent = pick.label; }});
    Array.prototype.forEach.call(document.querySelectorAll('[data-sf-sticky-now]'), function (e) {{ e.textContent = money(now); }});
    if (!sub) return;
    // the refill: how often the chosen pack ships, and the row and terms under the button
    box.setAttribute('data-interval-count', String(pick.every));
    Array.prototype.forEach.call(document.querySelectorAll('[data-sf-renew]'), function (e) {{ e.textContent = money(pick.refill); }});
    Array.prototype.forEach.call(document.querySelectorAll('[data-sf-renew-every]'), function (e) {{ e.textContent = String(pick.every); }});
    var terms = document.querySelector('[data-sf-refill-terms]');
    if (terms) terms.textContent = terms.getAttribute('data-sf-refill-terms').replace(/\\{{amount\\}}/g, money(pick.refill)).replace(/\\{{every\\}}/g, String(pick.every));
  }}
  root.addEventListener('change', sync);
  function fromHash() {{
    if (!/^#apf-buy(?:-[a-z]+)?$/.test(window.location.hash || '')) return;
    root.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}
  window.addEventListener('hashchange', fromHash);
  document.addEventListener('click', function (e) {{
    var a = e.target.closest && e.target.closest('a[href*="#apf-buy"]');
    if (!a || a.pathname.replace(/\\/$/, '') !== window.location.pathname.replace(/\\/$/, '')) return;
    e.preventDefault(); history.replaceState(null, '', a.hash); fromHash();
  }});
  // a link to one pack (the cart's line links carry its variant, ?variant-id=238): that pack chosen (it opened on
  // the default pack whichever was in the bag, stick review 6)
  (function () {{
    var q = new URLSearchParams(window.location.search), v = q.get('variant-id') || q.get('variant');
    if (!v) return;
    Object.keys(packs).forEach(function (k) {{
      var r = root.querySelector('input[name=sf_pack][value="' + k + '"]');
      if (r && String(packs[k].pk) === v) r.checked = true;
    }});
  }})();
  fromHash();
  sync();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', sync);
  window.addEventListener('load', sync);
}})();
</script>
</div>""")


# sections below the buy box ----------------------------------------------------------------------------------------
# the Amazon rating box and the "no reviews yet" box (the rest of the page uses the foundation's styles)
SECTIONS_CSS = r"""
.sfb{color:#151515;font-family:inherit}
.sfb *{box-sizing:border-box}
.sfb-sec{padding:72px 0}
.sfb-wrap{width:min(1180px,calc(100% - 40px));margin:0 auto}
.sfb-head{text-align:center;max-width:760px;margin:0 auto 36px}
.sfb-eyebrow{display:block;font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#6a6a6a;margin:0 0 12px}
.sfb h2{font-size:clamp(28px,3.4vw,42px);line-height:1.15;font-weight:600;letter-spacing:-.01em;margin:0}
.sfb-mark{background:#151515;color:#fff;border-radius:8px;padding:0 .22em;white-space:nowrap;display:inline-block;line-height:1.2;margin-top:.12em}
.sfb-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:16px 34px;border-radius:999px;background:#151515;color:#fff !important;text-decoration:none !important;font-size:14px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;border:0;cursor:pointer}
.sfb-btn:hover{background:#000}
.sfb-amz{max-width:760px;margin:0 auto;text-align:center;border:1px solid #e7e7e7;border-radius:20px;padding:36px 28px}
.sfb-tp{display:inline-flex;gap:3px;vertical-align:middle}
.sfb-tp i{display:grid;place-items:center;width:30px;height:30px;color:#fff;font-style:normal;font-size:18px;line-height:1}
.sfb-amz .sfb-tp{margin:0 0 14px}
.sfb-amz b{display:block;font-size:24px;font-weight:700;margin:0 0 6px}
.sfb-amz p{font-size:15.5px;line-height:1.55;color:#3b3b3b;margin:0 auto 16px;max-width:520px}
.sfb-amz a{color:#151515;font-weight:600;text-decoration:underline}
.sfb-amz small{display:block;margin-top:12px;font-size:12.5px;color:#6a6a6a}
.sfb-amzline{display:inline-flex;align-items:center;gap:8px;margin:10px 0 0;font-size:14.5px;color:#151515;text-decoration:none!important}
.sfb-amzline .sfb-tp i{width:18px;height:18px;font-size:11px}
.sfb-amzline span{text-decoration:underline}
.sfb-noreviews{max-width:760px;margin:0 auto;text-align:center;border:1px solid #e7e7e7;border-radius:20px;padding:40px 28px}
.sfb-noreviews__stars{display:inline-flex;gap:3px;margin:0 0 14px}
.sfb-noreviews__stars i{display:grid;place-items:center;width:30px;height:30px;background:#dcdce6;color:#fff;font-style:normal;font-size:18px}
.sfb-noreviews h3{font-size:22px;font-weight:600;margin:0 0 10px}
.sfb-noreviews p{font-size:16px;line-height:1.6;color:#3b3b3b;margin:0 auto 22px;max-width:560px}
.sfb-noreviews .sfb-noreviews__write{margin:16px 0 0;font-size:14.5px}
.sfb-noreviews__write a{color:#151515;text-decoration:underline}
#sfb-no-reviews[hidden],.sfb-noreviews__write[hidden]{display:none}
@media (max-width:989px){.sfb-sec{padding:52px 0}}
@media (max-width:599px){.sfb-wrap{width:calc(100% - 32px)}.sfb-head{padding:0 16px;margin-bottom:28px}.sfb h2{font-size:27px}.sfb-btn{width:100%}}
"""


def _head(eyebrow, lead, mark=None):
    title = esc(lead) + (f' <span class="sfb-mark">{esc(mark)}</span>' if mark else '')
    return f'<div class="sfb-head"><span class="sfb-eyebrow">{esc(eyebrow)}</span><h2>{title}</h2></div>'
















def tp_stars(rating):
    """Five Trustpilot-style boxes, the last one filled in part (4.6 fills 60% of the fifth)."""
    boxes = []
    for i in range(5):
        f = max(0.0, min(1.0, rating - i)) * 100
        boxes.append(f'<i aria-hidden="true" style="background:linear-gradient(90deg,#151515 {f:g}%,#dcdce6 {f:g}%)">&#9733;</i>')
    return f'<span class="sfb-tp" role="img" aria-label="Rated {rating:.1f} out of 5">{"".join(boxes)}</span>'


def amazon_html(a):
    """The owner's own Amazon listing of this brush: its rating and number of ratings (tools/reviews/amazon_rating.mjs,
    which writes them only when the listing's brand is the owner's), linked to the listing. No review text is copied."""
    return (f'<section class="sfb sfb-sec" id="sfb-amazon"><div class="sfb-wrap">{_head("Rated on Amazon", "What Amazon buyers say")}'
            f'<div class="sfb-amz">{tp_stars(float(a["rating"]))}<b>{float(a["rating"]):.1f} out of 5</b>'
            f'<p>From {int(a["count"]):,} Amazon ratings of this brush, sold there by {esc(a["brand"])}.</p>'
            f'<a href="{esc(a["url"])}" target="_blank" rel="noopener nofollow">See the ratings on Amazon</a>'
            f'<small>Checked on {esc(a["checked"])}</small></div></div></section>')


def amazon_line(a):
    """The same rating in the buy box, pointing to the box above."""
    return (f'<a class="sfb-amzline" href="#sfb-amazon">{tp_stars(float(a["rating"]))}'
            f'<span>{float(a["rating"]):.1f}/5 on Amazon ({int(a["count"]):,} ratings)</span></a>')


def no_reviews_html(buy='#apf-buy', amazon=None, n=None):
    """Until the brush has real reviews: an empty Trustpilot-style box that says so, with the guarantee as the proof.
    It hides itself once the store's own reviews of the brush appear (the review wall above then shows them), and
    shows a "Write a review" link when NEXT lets the shopper review the brush."""
    n = n or NO_REVIEWS
    stars = ''.join('<i aria-hidden="true">&#9733;</i>' for _ in range(5))
    return (f'<section class="sfb sfb-sec" id="sfb-no-reviews"><div class="sfb-wrap">'
            f'{_head(n["title"], n["lead_amazon"] if amazon else n["lead"])}<div class="sfb-noreviews"><span class="sfb-noreviews__stars">{stars}</span>'
            f'<p>{esc(n["text"])}</p><a class="sfb-btn" href="{buy}">{esc(n["button"])}</a>'
            f'<p class="sfb-noreviews__write" hidden><a href="#">{esc(n["write"])}</a></p></div></div>'
            '<script>(function () {'
            'var box = document.currentScript.parentNode;'
            'function check() {'
            'var el = document.querySelector("[data-sf-native-reviews]"), d = null;'
            'try { d = JSON.parse(el ? el.textContent : "{}"); } catch (e) { return; }'
            'if (d && (d.reviews || []).length) { box.hidden = true; return; }'
            'if (d && d.write) { var w = box.querySelector(".sfb-noreviews__write"); w.querySelector("a").href = d.write; w.hidden = false; }'
            '}'
            'if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", check); else check();'
            '})();</script></section>')




# around the site ---------------------------------------------------------------------------------------------------
# the homepage product shelf (the Bestsellers list and its tabs): a card like the other products', next to the gua sha
# and the face roller, in the default list and the Bestsellers, New and Face tabs (the shelf's tab keys)
SHELF = {'badge': 'New', 'saving': 'Buy 2, get 1 free', 'tags': ['No oils', '3 minutes', 'Less puffy'],
         'after': {'list': 'color-changing-foundation', 'bestsellers_0': 'color-changing-foundation',
                   'bestsellers_1': None, 'bestsellers_2': 'under-eye-reset'}}
# the NEXT collections it is in, as the other face tools (gua sha, face roller): Accessories, Face, Skin, Bestsellers
CATEGORIES = ['essentials', 'face', 'skin', 'the-hits']
# menus on every page: a top-level link before Bestsellers (desktop and mobile) and one in the footer's Shop column;
# raw-regex rules (apply_persona.py), the relative prefix of each page is kept
NAV_LABEL = 'Lymphatic Brush'
GLOBAL = [
    (r'RE:(<div class="menu__item child" data-hover-disclosure-toggle="" data-nav-item="">\s*<a class="navlink navlink--toplevel caps" '
     r'data-top-link="" href=")((?:\.\./)*)(collections/the-hits\.html">)',
     r'\1\2products/' + HANDLE + r'.html"> <span class="navtext">' + NAV_LABEL + r'</span> </a></div> \1\2\3'),
    (r'RE:(<li class="mobile-menu__item mobile-menu__item--level-1">\s*<a class="mobile-navlink mobile-navlink--level-1" href=")'
     r'((?:\.\./)*)(collections/the-hits\.html">)',
     r'\1\2products/' + HANDLE + r'.html"> ' + NAV_LABEL + r' </a> </li>\1\2\3'),
    (r'RE:(<summary class="sf__menu-title">Shop</summary><ul>\s*<li><a href=")((?:\.\./)*)(collections/all-products\.html">Shop all</a></li>)',
     r'\1\2\3<li><a href="\2products/' + HANDLE + r'.html">' + NAV_LABEL + r'</a></li>'),
]
