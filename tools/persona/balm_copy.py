"""The PDRN Plumping Balm: product page copy, offer and sections. Inspired by FEM+'s "Collagen Plump & Repair Volufiline
Balm" page (https://www.femplus.com/products/fempdrnbalm, teardown in docs/pdrn-balm.md), written new for SKINOFAB and
women past 45, in the foundation's black packaging.

The page has the Adaptive Peptide Foundation page's structure, section by section (twin.py, TWIN below), with its
photos: women past 45 holding and using the stick on white, before/after illustrations (labelled as such) and the
ingredient textures (product_photos.py, image_prompts.json). FEM+'s devices that sell honestly are in it (the tired-look
problem, the stick-vs-cream comparison, the ingredient cards, where to use it, what to expect, the objection FAQ,
bundles, the guarantee); what nothing backs stays out: "96% sold", "1M+ units sold", "300+ bought today", "77%
said...", the countdown, "dermatologist tested", "supports collagen production" (a drug claim) and their customers'
testimonials. The balm is new at SKINOFAB: the reviews near the top are the foundation's, labelled as theirs, and the
review wall says "no reviews yet" until real buyers write some. Bundle savings are real (the single-stick price times
the sticks); there is no invented "was" price.

Before launch: the key ingredients (INGREDIENTS) and the net weight must match the supplier's specification sheet.

Read by apply_persona.py (it builds products/pdrn-plumping-balm.html from the foundation page's markup, product_page())
and by setup_brush_offers.py (the NEXT product, its three bundles and their prices).
"""
import html
from pathlib import Path
import brush_copy as _b
from brush_copy import money, esc

KEY, MEDIA_BASE = 'balm', 9400000000000           # section ids, gallery media ids
HANDLE = 'pdrn-plumping-balm'
TITLE = 'PDRN Plumping Balm'
NAV_LABEL = 'PDRN Balm'
SHOPIFY_ID, SHOPIFY_VARIANT = 15517563191700, 61233683038600    # ids for the design markup's product JSON (not Shopify's)
PRICE, COMPARE = '24.95', '24.95'                                # one stick; no "was" price
EMAIL = 'hello@skinofab.com'
NET = '10 g / 0.35 oz'
IMG = Path(__file__).resolve().parents[2] / 'brand' / 'pdrn-balm'     # product_photos.py writes the images here
IMG_PREFIX, GIFT_PREFIX = 'skinofab-pdrn-balm', 'skinofab-balm-gift'
OFFERS_FILE, REVIEWS_DIR, AMAZON_FILE = 'balm-offers.json', 'reviews-balm', None
DESCRIPTION = ('<p>A press-on PDRN balm stick for under-eyes, smile lines and lip lines. PDRN, Volufiline™, collagen and '
               'hyaluronic acid in a melting balm: skin looks smoother, plumper and rested in seconds, and softer with daily use. '
               f'{NET}, about a month of daily use.</p>')
META_TITLE = 'PDRN Plumping Balm | Press-on stick for tired-looking under-eyes | SKINOFAB'
META_DESCRIPTION = ('A PDRN, Volufiline and collagen balm stick for tired-looking under-eyes, smile lines and lip lines. '
                    'Swipe, press, done in 10 seconds. 30-day money-back guarantee. Free shipping.')

# the gallery (product_photos.py writes brand/pdrn-balm/<name>.jpg): the foundation gallery's order and kinds of image,
# first one eager; the card is the shelf, cart and sticky-bar image
GALLERY = ['hero', 'hold-cheek', 'before-after', 'look-less-tired', 'results-grid', 'whats-inside', 'science', 'vs-others',
           'apply-eye', 'hold-chin', 'friends', 'apply-lips', 'bag']
KOREAN = True          # the foundation's "Formulated in Korea" line stays in the buy box

# the buy box --------------------------------------------------------------------------------------------------------
EYEBROW = None
SHIPPING_BADGE = '\U0001F381 FREE SHIPPING'
LEAD = ('The 10-second pick-me-up for the spots that make you look tired: hollow-looking under-eyes, smile lines and the lines '
        'around your lips. Swipe it on, press it in, and skin looks smoother, fuller and rested.')
BUNDLES = [
    {'key': '1', 'name': '1 Stick', 'note': 'About 1 month', 'variant': '1 stick', 'sku': 'SKF-PDB-1',
     'price': '24.95', 'compare': '24.95', 'gifts': []},
    {'key': '2', 'name': '2 Sticks', 'note': 'About 2 months · one for your bag', 'variant': '2 sticks', 'sku': 'SKF-PDB-2',
     'price': '39.95', 'compare': '49.90', 'badge': 'Most popular', 'default': True, 'gifts': []},
    {'key': '3', 'name': 'Buy 2, Get 1 Free', 'note': 'About 3 months · best value', 'variant': '3 sticks (buy 2, get 1 free)',
     'sku': 'SKF-PDB-3', 'price': '49.90', 'compare': '74.85', 'badge': 'Best value', 'gifts': []},
]
GIFTS = {}
GIFT_FILES = {}
STICKY_BUTTON = 'Choose your pack'
CART_UPGRADE = {'title': 'Upgrade to 2 sticks', 'button': 'Upgrade'}

# what is in it (match to the supplier's INCI before launch)
INGREDIENTS = [
    ('PDRN', 'Salmon DNA, the K-beauty favorite',
     'Polydeoxyribonucleotide, the ingredient behind Korea’s “skin booster” trend. In a balm it helps tired, dry skin '
     'look healthier, smoother and more even.'),
    ('Volufiline™', 'For areas that look hollow',
     'A plant-derived active (Anemarrhena root) made for volume. It helps hollow-looking under-eyes, smile lines and '
     'lips look fuller and more cushioned.'),
    ('Collagen', 'Low-weight, for a smoother look',
     'Hydrolyzed collagen films the surface so fine lines and crepey texture look less noticeable.'),
    ('Hyaluronic acid', 'Pulls water into skin',
     'Draws in moisture so skin looks bouncy and fresh instead of dry and creased, and makeup has less to settle into.'),
]
ADENOSINE = 'With adenosine, a K-beauty staple for the look of fine lines, and nourishing oils that lock moisture in.'


def _list(items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def tabs():
    """The tabs under the buy box, the foundation's six."""
    return [
        ('What makes it different?',
         '<p>Most eye creams spread one thin film over your whole face and slide off the spot you aimed at. This is a melting '
         'balm in a press-on stick: it goes exactly where you look tired, and stays there.</p>'
         + _list(['PDRN, Volufiline™, collagen and hyaluronic acid in one balm', 'Under-eyes, smile lines, lip lines and brows',
                  '10 seconds, nothing on your fingers', 'Under or over makeup, at home or in your bag'])),
        ('Does it work on my skin?',
         '<p>It’s made for skin after 45: drier, thinner skin is exactly where a cushioning, hydrating balm shows the most.</p>'
         '<p>It’s gentle on most skin. If your skin reacts easily, try it on a small area first, and don’t use it on broken or '
         'irritated skin. <strong>It contains salmon-derived DNA (PDRN):</strong> if you have a fish allergy, ask your doctor first.</p>'),
        ('How do I use it?',
         _list(['Twist up a little balm', 'Swipe a thin layer on the spot: under the eyes, smile lines, around the lips',
                'Press it in with the stick or tap with a fingertip, no rubbing', 'Morning and night; at night you can go a little thicker'])
         + '<p><strong>Less is more:</strong> a thin layer looks smooth; too much looks shiny.</p>'),
        ('How does the money-back guarantee work?',
         '<p>Use it for <strong>30 days</strong>. If you don’t see a difference, send it back for a <strong>full refund</strong>, '
         'no hassle, no questions asked.</p>'
         f'<p>Please email us at <a href="mailto:{EMAIL}">{EMAIL}</a> to receive return instructions.</p>'),
        ('Ingredients',
         ''.join(f'<p><strong>{esc(n)}:</strong> {esc(t)}.</p>' for n, t, _ in INGREDIENTS)
         + f'<p>{esc(ADENOSINE)}</p>'
         '<p><strong>Contains salmon-derived DNA (PDRN).</strong> If you have a fish allergy, check the full ingredient list '
         'on the box and ask your doctor before use.</p>'
         f'<p><strong>Net weight:</strong> {NET}.</p>'),
        _b.SHIPPING_TAB,
    ]


# the sections below: the foundation page's, in its order (twin.py), with the balm's copy ------------------------------
NO_REVIEWS = {'title': 'Customer reviews', 'lead': 'No reviews yet', 'lead_amazon': 'No SKINOFAB reviews yet',
              'text': 'The PDRN Plumping Balm is new at SKINOFAB, and we only show reviews from real buyers. Try it for 30 days: '
                      'if you don’t see a difference, we’ll refund you.',
              'button': 'Try it risk-free', 'write': 'Bought it? Write the first review'}
FAQ = {'items': [
    ('Will it feel greasy?',
     'Not if you use a thin layer. It melts into skin and leaves a soft, natural glow. Too much looks shiny: one swipe per spot is enough.'),
    ('Can I wear it under makeup?',
     'Yes. Press a thin layer in, wait a minute, then apply your foundation or concealer: it gives makeup a smoother surface so it creases less. '
     'You can also tap it over makeup to refresh the under-eyes during the day.'),
    ('Is it gentle enough for the under-eye area?',
     'Yes, that’s what it’s made for. Swipe lightly or tap it in; don’t drag the thin skin around the eyes. Keep it out of the eyes themselves.'),
    ('Does it work on mature skin?',
     'It’s made for it. Skin after 45 is drier and thinner, which is exactly when a hydrating, cushioning balm makes the most visible difference.'),
    ('Morning or night?',
     'Both. In the morning use a thin layer before makeup; at night you can apply a little more and let it work while you sleep.'),
    ('Can I use it with retinol or other skincare?',
     'Yes. Apply it last, after your serum or retinol: it helps keep dry, sensitive spots comfortable.'),
    ('How long until I see a difference?',
     'Hydration and a smoother look show right away. Softer-looking lines come with daily use over a few weeks. Results vary from person to person.'),
    ('How long does one stick last?',
     'About a month, used morning and night on the under-eyes, smile lines and lips.'),
    ('Is it safe for sensitive skin?',
     'It’s gentle on most skin, but try it on a small area first if your skin reacts easily. Don’t use it on broken or irritated skin. '
     'It contains salmon-derived DNA (PDRN): if you have a fish allergy, ask your doctor first.'),
    ('What if it doesn’t work for me?',
     f'Send it back within 30 days for a full refund. Just email {EMAIL}.'),
]}
# section by section, in the foundation page's order (twin.py names each slot); images are brand/pdrn-balm/<name>.jpg or
# its source/ photo. The before/after photos are illustrations and say so on the image.
TWIN = {
    'loved': {'lead': 'Made for real life', 'mark': 'after 45'},
    'moments': [
        ('hold-cheek', 'Before makeup', 'A swipe under the eyes, then your foundation.', 'A woman in her late fifties holding the PDRN Plumping Balm'),
        ('hold-chin', 'Before a long day', 'Rested-looking eyes in 10 seconds.', 'A woman in her fifties holding the PDRN Plumping Balm'),
        ('friends', 'One to keep, one to share', 'The 2-stick pack: one at home, one in your bag.', 'Two women in their fifties and sixties with the balm'),
        ('mirror', 'At night', 'A slightly thicker layer before bed.', 'A woman touching up under her eye at the bathroom mirror'),
        ('bag', 'Over makeup, anywhere', 'Tap it on to refresh your under-eyes during the day.', 'The balm taken out of a handbag'),
        ('apply-brows', 'Between the brows', 'Press it on frown and forehead lines too.', 'A woman pressing the balm between her eyebrows'),
    ],
    'problem': {
        'img_problem': 'problem', 'img_solution': 'pack',
        'photo_alt': 'A woman in her fifties looking tired',
        'problem': ('The problem', 'You look more tired', 'than you feel'),
        'lede': 'You slept. You drank your water. And still the mirror, the shop window and every photo show hollow-looking '
                'under-eyes and lines that weren’t there five years ago.',
        'pains': ['Concealer that slides into every crease by lunch',
                  'Eye creams that spread a thin film everywhere except the spot you aimed at',
                  'Under-eyes that look hollow and shadowed even after a full night',
                  'Smile lines and lip lines that look deeper on dry days',
                  'Fillers and in-office treatments you don’t want to start'],
        'close': 'The result: you cover it up, it shows through, and “you look tired” starts to sting.',
        'root': ('The root of it', 'Your skin changed.', 'Your eye cream didn’t.'),
        'causes': [('Less collagen, thinner skin',
                    'Skin loses up to 30% of its collagen in the first five years after menopause. The thin skin under the eyes '
                    'shows it first: it looks hollow and shadowed.'),
                   ('Drier skin, deeper-looking lines',
                    'Skin holds less water with age. Smile lines and lip lines look deeper when skin is dry, and softer when it '
                    'is cushioned and hydrated.'),
                   ('Creams that don’t stay put',
                    'A cream spreads one thin film over your whole face and slides off the crease you aimed at. The spots that '
                    'need it most get the least.')],
        'root_end': 'So the problem was never you. It’s a formula that can’t stay where you need it.',
        'solution': ('The solution', 'So we put it in', 'a press-on stick'),
        'solution_lede': 'The PDRN Plumping Balm starts from skin after 45: four K-beauty actives in a melting balm you press '
                         'exactly where you look tired.',
        'fixes': [('Concealer creasing', 'A cushioning balm that gives makeup a smoother surface, so it creases less.'),
                  ('Hollow-looking under-eyes', 'PDRN and Volufiline™ for under-eyes that look fuller and more rested.'),
                  ('Dry, deeper-looking lines', 'Collagen and hyaluronic acid cushion and hydrate smile and lip lines.'),
                  ('Messy fingers and jars', 'Swipe, press, done: 10 seconds, nothing on your fingers.'),
                  ('A different cream for every spot', 'One stick for under-eyes, smile lines, lips and brows. It fits in your bag.')],
        'button': 'Get yours', 'note': 'Use it for 30 days, or your money back.',
        'product_alt': 'The PDRN Plumping Balm',
    },
    # the foundation's expert block: here the brand's own note, signed as the brand (no invented expert)
    'note': {'id': 'sf-note', 'eyebrow': 'Why we made it', 'photo': 'mirror',
             'photo_alt': 'A woman touching up under her eye with the PDRN Plumping Balm',
             'headline_lead': '&hellip;for the days you look', 'headline_mark': 'more tired than you feel.',
             'paragraphs': ['We make SKINOFAB for skin after 45. The spots that make you look tired, hollow-looking under-eyes, '
                            'smile lines and the lines around your lips, are exactly where a cream slides off and concealer settles in.',
                            'So we put PDRN, Volufiline™, collagen and hyaluronic acid in a balm that melts on contact, in a stick '
                            'you press exactly where you need it: <strong>morning, night or over makeup.</strong>',
                            'It isn’t a filler, and we won’t pretend it is. It’s the 10-second step that helps you look as rested as you feel.'],
             'name': 'The SKINOFAB team', 'role': 'Made for skin after 45'},
    'science': {'img': 'tall', 'alt': 'The PDRN Plumping Balm with PDRN, Volufiline, collagen and hyaluronic acid',
                'eyebrow': 'K-beauty skin science', 'lead': 'The Korean skincare actives,', 'mark': 'in a press-on balm',
                'lede': 'Korean skincare made PDRN “skin boosters” famous. We put PDRN with Volufiline™, collagen and hyaluronic '
                        'acid in a balm you press on in seconds, right where skin looks tired.',
                'rows': [(n, d) for n, _, d in INGREDIENTS],
                'note': 'With adenosine and nourishing oils. Contains salmon-derived DNA: check the ingredient list if you have a fish allergy.',
                'button': 'Choose your pack'},
    'iwt': [
        {'img': 'ba-smile', 'alt': 'Smile lines and lip lines before and after the balm (illustration)',
         'lead': 'Plumper-looking', 'mark': 'in seconds',
         'paras': ['Press it on and dry, crepey skin looks cushioned and hydrated right away: under-eyes look smoother and less '
                   'hollow, smile lines and lip lines look softer. With daily use, skin stays more hydrated and fine lines look '
                   'less obvious. Results vary from person to person.'],
         'usps': ['Smoother-looking in seconds', 'Cushions lines and hollows']},
        {'img': 'apply-smile', 'alt': 'A woman gliding the balm along her smile line',
         'lead': 'How does it work?', 'mark': None,
         'paras': ['Swipe a thin layer on the spot: under the eyes, along your smile lines, around the lips.',
                   'Press it in with the stick or tap with a fingertip. The balm melts on contact and cushions the skin, so the '
                   'area looks smoother and fuller.',
                   'Morning, night or over makeup. Less is more: one swipe per spot is enough.'],
         'usps': ['10 seconds, no fingers', 'Under or over makeup']},
    ],
    'results': {'title': 'What to expect',
                'cards': [('10 sec', 'To swipe and press it on', 'Morning, night or over makeup'),
                          ('Day 1', 'Under-eyes look smoother and more hydrated', 'A cosmetic effect you can see right away'),
                          ('1 month', 'Of daily use from one stick', 'Morning and night, a thin layer')]},
    'compare': {'title': 'Why skinofab?', 'others': 'Eye creams',
                'rows': ['Goes exactly where you need it', 'No fingers, no mess', 'Touch-ups over makeup', 'Fits in your bag',
                         'One stick for eyes, smile and lips']},
    'inside': {'title': 'What’s inside, and why your skin will love it',
               'intro': 'The PDRN Plumping Balm is K-beauty skincare in a stick: four actives in a melting balm, made for skin after 45.',
               'cards': [('ing-pdrn', 'PDRN', 'Salmon DNA, the active behind Korea’s “skin booster” trend'),
                         ('ing-volu', 'Volufiline™', 'From Anemarrhena root, for areas that look hollow'),
                         ('ing-collagen', 'Collagen', 'Films the surface so fine lines look less noticeable'),
                         ('ing-ha', 'Hyaluronic acid', 'Draws in moisture so skin looks bouncy, not creased'),
                         ('swatch', 'A balm that melts', 'Cushiony, never sticky: a thin layer gives a soft glow')]},
    # the foundation's customer clips: where to use it, in the same cards (not reviews)
    'cards': {'eyebrow': 'Where to use it', 'title': 'One stick, every spot that looks tired', 'items': [
        {'img': 'apply-eye', 'title': 'Under the eyes', 'text': 'For under-eyes that look hollow and shadowed.', 'alt': 'Pressing the balm under the eye'},
        {'img': 'apply-smile', 'title': 'Smile lines', 'text': 'From the nose to the corners of the mouth.', 'alt': 'Gliding the balm along a smile line'},
        {'img': 'apply-lips', 'title': 'Around the lips', 'text': 'Lip lines and dry lips.', 'alt': 'Tracing the balm above the upper lip'},
        {'img': 'apply-brows', 'title': 'Between the brows', 'text': 'Frown lines and the forehead.', 'alt': 'Pressing the balm between the eyebrows'}]},
    'why': {'title': 'The skinofab difference', 'img': 'temple', 'button': 'Claim offer',
            'features': [('Visible in seconds', 'Smoother, more rested-looking under-eyes the moment you press it on'),
                         ('Four K-beauty actives', 'PDRN, Volufiline™, collagen and hyaluronic acid'),
                         ('30-day money-back guarantee', 'Love it or send it back for a full refund')]},
}


def picker_html(variants, gift_imgs, css):
    return _b.picker_html(variants, gift_imgs, css, bundles=BUNDLES, gifts=GIFTS, legend='Choose your pack')


def no_reviews_html(buy='#apf-buy', amazon=None): return _b.no_reviews_html(buy, amazon, NO_REVIEWS)


BUYBOX_CSS = _b.BUYBOX_CSS


# around the site ---------------------------------------------------------------------------------------------------
SHELF = {'badge': 'New', 'saving': 'Buy 2, get 1 free', 'tags': ['PDRN', 'Under-eyes', 'Press-on'],
         'after': {'list': 'the-lymphatic-brush', 'bestsellers_0': 'the-lymphatic-brush',
                   'bestsellers_1': None, 'bestsellers_2': 'the-lymphatic-brush'}}
# the NEXT collections (as the foundation and the other face skincare): Face, Skin, Bestsellers
CATEGORIES = ['face', 'skin', 'the-hits']
# menus on every page: a top-level link before the brush (desktop and mobile) and one in the footer's Shop column
GLOBAL = [
    (r'RE:(<div class="menu__item child" data-hover-disclosure-toggle="" data-nav-item="">\s*<a class="navlink navlink--toplevel caps" '
     r'data-top-link="" href=")((?:\.\./)*)(products/the-lymphatic-brush\.html">)',
     r'\1\2products/' + HANDLE + r'.html"> <span class="navtext">' + NAV_LABEL + r'</span> </a></div> \1\2\3'),
    (r'RE:(<li class="mobile-menu__item mobile-menu__item--level-1">\s*<a class="mobile-navlink mobile-navlink--level-1" href=")'
     r'((?:\.\./)*)(products/the-lymphatic-brush\.html">)',
     r'\1\2products/' + HANDLE + r'.html"> ' + NAV_LABEL + r' </a> </li>\1\2\3'),
    (r'RE:(<li><a href=")((?:\.\./)*)(products/the-lymphatic-brush\.html">Lymphatic Brush</a></li>)',
     r'\1\2\3<li><a href="\2products/' + HANDLE + r'.html">' + NAV_LABEL + r'</a></li>'),
]
