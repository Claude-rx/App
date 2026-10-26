"""The Adaptive Foundation Stick: product page copy, offer and sections. Inspired by the owner's other brand's page
(Facelove's "Changing Foundation Stick", https://facelove-cosmetics.com/products/changing-foundation-stick-main, teardown
in docs/foundation-stick.md), written new for SKINOFAB and women past 45, in the brand's black packaging with its real
wordmark.

The product: a dual-ended stick. One end is a twist-up cream foundation that goes on white and shifts toward the
wearer's skin tone as it is blended; the other end is a dense kabuki brush to buff it in. The page has the Adaptive
Peptide Foundation page's structure, section by section (twin.py, TWIN below), with its photos on white: women past
45 holding and using the stick, a before/after illustration (labelled as such) and the ingredient textures
(product_photos.py stick, image_prompts.json). What sells honestly on Facelove's page is in it (no shade to choose,
the brush in the stick, made for mature and dry skin, the ingredient cards, the comparison with a liquid foundation,
the guarantee); what nothing backs stays out: "97% of women agree..." and the other percentages, "more than 50,000
women", "only 7 pieces remain", "Promotion runs until 11:59 PM tonight", the $59 "was" price, "16 skin tones" (its
own image says "fair to medium"), "anti-aging" and "reduces redness" as skincare effects, and its testimonials (no
review app behind them, several from women under 45). The stick is new at SKINOFAB: the reviews near the top are the
foundation's, labelled as theirs, and the review wall says "no reviews yet" until real buyers write some. Bundle
savings are real (the single-stick price times the sticks).

Before launch (owner): the ingredients (INGREDIENTS), the shade range it adapts to (SHADE_FAQ, and the photos of
women with deep skin), the net weight (NET) and where it is formulated (KOREAN) must match the supplier's sheet.

Read by apply_persona.py (it builds products/adaptive-foundation-stick.html from the foundation page's markup,
product_page()) and by setup_brush_offers.py (the NEXT product, its three bundles and their prices).
"""
from pathlib import Path
import brush_copy as _b
from brush_copy import money, esc

KEY, MEDIA_BASE = 'stick', 9600000000000          # section ids, gallery media ids
HANDLE = 'adaptive-foundation-stick'
TITLE = 'Adaptive Foundation Stick'
NAV_LABEL = 'Foundation Stick'
SHOPIFY_ID, SHOPIFY_VARIANT = 15517563191900, 61233683038800    # ids for the design markup's product JSON (not Shopify's)
PRICE, COMPARE = '39.00', '39.00'                                # one stick; no "was" price
EMAIL = 'hello@skinofab.com'
NET = None                       # the net weight, from the supplier's sheet (shown in the Ingredients tab once set)
IMG = Path(__file__).resolve().parents[2] / 'brand' / 'foundation-stick'   # product_photos.py stick writes the images here
IMG_PREFIX, GIFT_PREFIX = 'skinofab-foundation-stick', 'skinofab-stick-gift'
OFFERS_FILE, REVIEWS_DIR, AMAZON_FILE = 'stick-offers.json', 'reviews-stick', None
DESCRIPTION = ('<p>A dual-ended foundation stick for skin after 45. The cream goes on white and shifts toward your skin tone '
               'as you blend; the kabuki brush on the other end buffs it into an even, natural finish. Hyaluronic acid, '
               'niacinamide, squalane, vitamin E and centella in a creamy base made for dry, mature skin.</p>')
META_TITLE = 'Adaptive Foundation Stick | One shade that adapts, brush built in | SKINOFAB'
META_DESCRIPTION = ('A foundation stick that goes on white and blends into your skin tone, kabuki brush built in. Made '
                    'for dry, mature skin. 30-day money-back guarantee.')

# the gallery (product_photos.py stick writes brand/foundation-stick/<name>.jpg): the foundation gallery's order and
# kinds of image, first one eager; the card is the shelf, cart and sticky-bar image
# (6: no photo the sections below show again, and none of the two-tube packshots, which read as two products:
# the stick is one stick, foundation at one end, brush at the other; stick reviews 1 and 2)
# first a woman past 50 with the stick and what it does (stick review 3: the first phone screen did not sell), then the
# stick open at both ends; no slide repeats a photo used further down the page (the packshot was the Solution's, the
# swatch hand "How does it work?", stick review 3)
GALLERY = ['one-stick', 'duo-ends', 'before-after', 'whats-inside', 'science', 'hold-chin']
GALLERY_ALT = {'one-stick': 'A woman in her fifties holding the Adaptive Foundation Stick: goes on white, blends to your tone',
               'duo-ends': 'The Adaptive Foundation Stick open at both ends: the white cream and the kabuki brush',
               'before-after': 'Before and after the stick on dry, mature skin (AI illustration)',
               'whats-inside': 'What is inside: hyaluronic acid, niacinamide, squalane and vitamin E',
               'science': 'How it works: color capsules break as you blend',
               'hold-chin': 'A woman in her fifties holding the Adaptive Foundation Stick by her chin'}
KOREAN = False         # no "Formulated in Korea" line until the supplier confirms where it is formulated

# the buy box --------------------------------------------------------------------------------------------------------
EYEBROW = None
SHIPPING_BADGE = '\U0001F381 FREE SHIPPING'
# the header's line on this page (the store's "Up to 60% OFF + FREE Gifts" names gifts and savings the stick has
# not got, stick review 3): what every stick order does get
ANNOUNCEMENT = 'Buy 2, get 1 free · Free shipping · 30-day money-back guarantee'
# three lines under the lead, what she checks first (stick review 4: the first phone screen named no benefit); the
# lead says what she gets, the lines how (stick review 5: the lead and the lines said the same three things)
BULLETS = ['No shade to choose: it goes on white and adapts as you blend', 'Kabuki brush built into the other end',
           'No pump, no spills: it fits in your bag']
LEAD = 'Even, natural coverage in about a minute, in a creamy stick made for dry, mature skin.'
BUNDLES = [
    {'key': '1', 'name': '1 Stick', 'note': 'Foundation + brush in one', 'variant': '1 stick', 'sku': 'SKF-AFS-1',
     'price': '39.00', 'refill': '31.00', 'every': 28, 'compare': '39.00', 'gifts': []},
    {'key': '2', 'name': '2 Sticks', 'note': 'One at home, one in your bag', 'variant': '2 sticks', 'sku': 'SKF-AFS-2',
     'price': '59.00', 'refill': '47.00', 'every': 56, 'compare': '78.00', 'badge': 'Recommended', 'default': True, 'gifts': []},
    {'key': '3', 'name': '3 Sticks: buy 2, get 1 free', 'note': 'Home, bag and one to share', 'variant': '3 sticks (buy 2, get 1 free)',
     'sku': 'SKF-AFS-3', 'price': '78.00', 'refill': '62.00', 'every': 84, 'compare': '117.00', 'badge': 'Best value', 'gifts': []},
]
# Automatic Refills (the owner's brief of 26 Oct 2026: every product but the brush is sold with refills, as the
# foundation is): on by default, so the cards and the title show the refill price (20% under the one-time price);
# one-time stays a choice on the cart page. A pack ships again when it runs out: 'every' days per pack, 28 for one
# stick (the owner to confirm how long a stick lasts). setup_brush_offers.py writes the refill prices to NEXT.
REFILL = {'interval': 'day', 'every': 28, 'name': 'Automatic Refills', 'default': True, 'unit': 'stick'}
GIFTS = {}
GIFT_FILES = {}
# the boxed guarantee under the button (as the foundation's)
GUARANTEE = 'Wear it in your own daylight for 30 days. If it isn’t right for you, we’ll refund you, even opened.'
STICKY_BUTTON = 'Choose your pack'
CART_UPGRADE = {'title': 'Upgrade to 2 sticks', 'button': 'Upgrade'}
CART_UPGRADE_3 = {'title': 'Make it 3 sticks: buy 2, get 1 free', 'button': 'Upgrade'}   # from the 2-stick pack

# what is in it (match to the supplier's INCI before launch)
INGREDIENTS = [
    ('Hyaluronic acid', 'Holds water in the skin',
     'Draws in moisture, so dry skin stays comfortable under the foundation and the finish looks fresh instead of tight.'),
    ('Niacinamide', 'Vitamin B3, for a more even look',
     'A skincare classic for skin that looks uneven, dull or a little red: it helps the complexion look more even over time.'),
    ('Squalane', 'A light oil skin already knows',
     'Softens and seals in moisture, so the cream glides over texture and dry patches instead of catching on them.'),
    ('Vitamin E', 'Antioxidant care',
     'Nourishes and helps protect the skin’s surface, for skin that feels soft and supple through the day.'),
    ('Centella asiatica', 'A calming plant extract',
     'Also called cica or gotu kola: a soothing botanical for sensitive-feeling skin.'),
]
# (with the foundation's word for very fair and very deep skin: ask first, review 7)
SHADE_FAQ = ('It’s made to adapt to a wide range of skin tones without picking a shade: the cream goes on white and its '
             'pigments shift toward your tone as you blend. Try it along your jaw in daylight. Not your match? Email us '
             f'within 30 days for a full refund, even opened. If your skin is very fair or very deep, you can also email {EMAIL} '
             'before you order and we’ll tell you honestly how it suits you.')


def _list(items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def tabs():
    """The tabs under the buy box, the foundation's six."""
    return [
        ('What makes it different?',
         '<p>Most foundations make you choose a shade under shop lights, then need a sponge or brush, then settle into lines by '
         'lunch. This one goes on white and shifts toward your own skin tone as you blend, with the brush built into the other end.</p>'
         + _list(['No shade to choose: it adapts as you blend', 'A dense kabuki brush on the other end',
                  'Creamy, made for dry, mature skin', 'No pump, no spills: it fits in your bag'])),
        ('Does it work on my skin?',
         '<p>It’s made for skin after 45: drier, with redness, sun spots and fine lines. The cream base keeps dry skin '
         'comfortable, and the brush buffs it into a thin, even layer that doesn’t sit on top of texture.</p>'
         f'<p>{esc(SHADE_FAQ)}</p>'
         '<p>If your skin reacts easily, try it on a small area first.</p>'),
        ('How do I use it?',
         _list(['Twist up a little foundation', 'Dot a little on your cheeks, forehead and chin: it looks white at first',
                'Turn the stick and buff it in with the brush, in small circles, until it shifts to your tone',
                'Add a second thin layer where you want more coverage: spots, redness, under the eyes'])
         + '<p><strong>Less is more:</strong> two thin layers look more natural than one thick one.</p>'),
        ('How does the money-back guarantee work?',
         f'<p>Try it for <strong>30 days</strong>. If you don’t love it, email us at <a href="mailto:{EMAIL}">{EMAIL}</a> and we’ll '
         'refund it in <strong>full</strong>, even opened, no questions asked.</p>'),
        ('Ingredients',
         ''.join(f'<p><strong>{esc(n)}:</strong> {esc(t)}.</p>' for n, t, _ in INGREDIENTS)
         + '<p>The full ingredient list is printed on the box.</p>'
         + (f'<p><strong>Net weight:</strong> {NET}.</p>' if NET else '')),
        _b.SHIPPING_TAB,
    ]


# the sections below: the foundation page's, in its order (twin.py), with the stick's copy -----------------------------
# the reviews on this page (the owner, 26 Oct 2026: the stick is the same product as the Adaptive Peptide
# Foundation): the foundation's imported reviews, labelled as the foundation's wherever they show (the strip after
# the buy box, the stars under the title, the wall), and the foundation's FrontrowMD listing, named as its listing
# (the foundation goes on white and adapts the same way; its skincare base is its own: peptides and PDRN in a serum,
# the stick's a cream with hyaluronic acid and squalane. Stick review 5: "the same adaptive formula" said six times,
# against two different ingredient lists)
BORROW_REVIEWS = {'of': 'our Adaptive Peptide Foundation, which adapts to your tone the same way', 'buyer': 'Verified buyer of the foundation',
                  'title': 'Reviews of our Adaptive Peptide Foundation',
                  'note': 'Our liquid foundation: it goes on white and adapts to your tone the same way, in a serum base of '
                          'its own. The stick is new at SKINOFAB: its own reviews join these as buyers write them.',
                  'badge': 'of the foundation',          # one line under the stars on a phone (stick review 4)
                  'wall_note': 'of our Adaptive Peptide Foundation from our earlier store'}   # the wall's count line
# the reviews' stars, bars and checks in the review-site look the owner asked for (26 Oct 2026): green boxed stars,
# with no review site's name or logo (the reviews are the store's own imports, and the page says so)
REVIEW_STARS = '#00b67a'
FRONTROW_NOTE = ('This FrontrowMD Clinicians’ Choice listing is for our Adaptive Peptide Foundation, the liquid that adapts to '
                 'your tone the same way this stick does.')
NO_REVIEWS = {'title': 'Customer reviews', 'lead': 'No reviews of the stick yet', 'lead_amazon': 'No SKINOFAB reviews yet',
              'text': 'The Adaptive Foundation Stick is new at SKINOFAB, and we only show reviews from real buyers. Try it for 30 days: '
                      'if it isn’t the easiest foundation you’ve worn, we’ll refund you.',
              'button': 'Try it risk-free', 'write': 'Bought it? Write the first review'}
FAQ = {'items': [
    ('Will it match my skin tone?', SHADE_FAQ),
    ('Will it settle into my fine lines?',
     'Use it in thin layers and buff it in with the brush: a thin, creamy layer moves with your skin instead of collecting in '
     'lines. Starting with moisturized skin helps too.'),
    ('Will it look cakey or heavy?',
     'Not in thin layers. It’s a cream, not a powder, so it doesn’t crack on dry skin. Build only where you need it.'),
    ('Is it good for dry skin?',
     'That’s who it’s made for: hyaluronic acid, squalane and vitamin E in a creamy base that keeps dry, mature skin comfortable.'),
    ('Can it cover spots and redness?',
     'It evens out the look of redness and sun spots in a thin layer; for a darker spot, tap a second layer on just that spot '
     'and buff the edges. It’s a natural finish, not a mask.'),
    ('How long does it last on my skin?',
     'It’s made to wear from morning to evening as a thin, flexible layer that doesn’t settle into lines. On a long day, '
     'buff the brush end over your nose and chin to refresh it; there’s no need to add more.'),
    ('Stick or bottle: which one is for me?',
     'Both go on white and shift toward your tone as you blend. The Adaptive Peptide Foundation is a liquid in a serum base '
     'with peptides and PDRN, blended with your fingertips. The stick is a cream with hyaluronic acid, niacinamide and '
     'squalane, with the brush built in, made for quick mornings and touch-ups on the go.'),
    ('Does it have SPF?',
     'No. Wear your daily sunscreen first and let it settle for a minute; the stick goes on top.'),
    ('How do I clean the brush?',
     'Once a week, wash the bristles with lukewarm water and a little gentle soap, rinse, squeeze out the water and let it dry '
     'bristles down, cap off. Keep water away from the foundation end.'),
    ('Is it gentle on sensitive skin?',
     'It has soothing centella in the formula. If your skin reacts easily, try it on a small area first, '
     'and don’t use it on broken or irritated skin.'),
    ('Can I wear it over skincare and under powder?',
     'Yes. Apply it after your moisturizer and sunscreen. If you like powder, a light dusting on top is fine.'),
    # her last two questions before buying a cream foundation (stick review 3); no transfer-proof claim: nothing
    # tested says so
    ('Will it rub off on my collar?',
     'Give it a minute to set after you buff it in. It’s a cream, so where a collar or a scarf rubs, a light dusting of '
     'powder on the jaw and neck keeps it in place.'),
    ('How much coverage does it give?',
     'Light to medium in one thin layer, buildable: tap a second layer where you want more and buff the edges. It’s a '
     'natural finish that still looks like skin.'),
    ('Where do you ship, and are there import duties?',
     'Free shipping, with tracking, to every country offered at checkout: 2–4 business days in the US, 6–9 to Europe, '
     'the UK, Canada, Australia and New Zealand, 8–12 elsewhere. Outside the US, your country may charge import duties '
     f'or taxes at delivery; email {EMAIL} before you order and we’ll tell you what to expect.'),
    ('How do I take it off at night?',
     'With your usual cleanser. On a day you built up a second layer, a cleansing balm or micellar water first, then '
     'your cleanser.'),
    ('What if it doesn’t work for me?',
     f'Email {EMAIL} within 30 days and we’ll refund it in full, even opened. No questions asked.'),
]}
FAQ['items'][-1:-1] = _b.refill_faq(BUNDLES, REFILL)     # how refills work, how to buy once
# section by section, in the foundation page's order (twin.py names each slot); images are brand/foundation-stick/
# <name>.jpg, its labelled/ photo or its source/ photo. The before/after photo is an illustration and says so.
TWIN = {
    'loved': {'lead': 'Made for real life', 'mark': 'after 45'},
    # (the handbag second: on a phone the second card peeks in by a third, and the bag's left third has no face to
    # cut, stick review 5)
    'moments': [
        ('daylight', 'Check it in daylight', 'Blended in, it shifts toward your own tone.', 'A woman in her sixties touching her jawline, the stick in her other hand'),
        ('bag', 'Touch-ups anywhere', 'No pump, no spills, no sponge to carry.', 'The stick going into a handbag'),
        ('buff-jaw', 'The brush is built in', 'Buff it in with the other end of the stick.', 'A woman in her sixties buffing foundation along her jaw with the brush end'),
        ('friends', 'Home, bag and one to share', 'The 3-stick pack: one at home, one in your bag, one for a friend.', 'Two women in their fifties and sixties with the stick'),
    ],
    'problem': {
        'img_problem': 'problem', 'img_solution': 'card',
        'photo_alt': 'A woman in her fifties frowning at her foundation in a hand mirror',
        'problem': ('The problem', 'Your foundation used to work.', 'Your skin changed.'),
        'lede': 'You found your shade years ago. Now the same bottle looks orange in daylight, gray by the window, and by lunch '
                'it has found every line around your eyes.',
        'pains': ['A shade that looked right in the shop and wrong at home',
                  'Foundation that settles into fine lines and looks heavier by the hour',
                  'Dry patches that catch it and make it look cakey',
                  'Redness and sun spots that show through, or a mask that hides your skin',
                  'A drawer of half-used bottles, sponges and brushes'],
        'close': 'So you wear less and less, and you still don’t like what you see in photos.',
        'root': ('The root of it', 'Your skin tone moves.', 'Your old shade doesn’t.'),
        'causes': [('Your tone shifted',
                    'After 45, skin loses evenness: more redness, more sun spots, a slightly different undertone. The shade '
                    'you knew is no longer quite yours, and it changes with the light.'),
                   ('Your skin got drier',
                    'Drier, thinner skin has more texture for a liquid or a powder to cling to. That’s why the same foundation '
                    'looks cakey now and settles into lines.'),
                   ('Too many tools',
                    'A bottle, a sponge and a brush, each to buy, carry and wash: when it takes three things, most '
                    'mornings you skip it.')],
        'root_end': 'The problem was never you. It’s a foundation that can’t keep up with your skin.',
        'solution': ('The solution', 'So we made a foundation', 'that adapts to you'),
        'solution_lede': 'The Adaptive Foundation Stick starts from skin after 45: one creamy shade that adapts to your tone as '
                         'you blend, and the brush on the other end.',
        'fixes': [('The wrong shade', 'It goes on white and shifts toward your skin tone as you blend.'),
                  ('Cakey on dry skin', 'A creamy base with hyaluronic acid, squalane and vitamin E.'),
                  ('Settling into lines', 'Buffed in thin with the brush, it moves with your skin.'),
                  ('Redness and spots', 'A thin layer evens their look; a second one covers more.'),
                  ('Three tools', 'Foundation and kabuki brush in one stick that fits in your bag.')],
        'button': 'Get yours', 'note': 'Try it for 30 days: love it, or your money back.',
        'product_alt': 'The Adaptive Foundation Stick',
    },
    # the foundation's expert block: here the brand's own note, signed as the brand (no invented expert)
    'note': {'id': 'sf-note', 'eyebrow': 'Why we made it', 'photo': 'temple',
             'photo_alt': 'A woman in her sixties holding the Adaptive Foundation Stick by her temple',
             'headline_lead': 'Made for the mornings you want to look like', 'headline_mark': 'yourself, just fresher.',
             'paragraphs': ['We make SKINOFAB for skin after 45. The women we talk to don’t want more makeup: they want the '
                            'foundation they already wear to stop turning orange, stop settling into lines and stop needing three tools.',
                            'That’s why we put a foundation that adapts to your tone and a kabuki brush into one stick: '
                            '<strong>swipe it on, buff it in, done.</strong>',
                            'It won’t make you look 30, and we won’t pretend it will. It evens out the look of your skin and lets the rest of you show.'],
             'name': 'The SKINOFAB team', 'role': 'Made for skin after 45'},
    'science': {'img': 'tones-tall', 'alt': 'Three women, fair, medium and deep skin, before and after the same light foundation (AI illustration)',
                'eyebrow': 'Adaptive color science', 'lead': 'One shade', 'mark': 'that meets your skin',
                'lede': 'The color pigments are wrapped in tiny capsules in a white cream. As you blend, the capsules break and '
                        'the color shifts toward your own tone, so there is no shade to pick.',
                'rows': [(n, d) for n, _, d in INGREDIENTS[:4]],
                'note': 'With soothing centella. The full ingredient list is on the box.',
                'button': 'Choose your pack'},
    'iwt': [
        {'img': 'wear-day', 'alt': 'The same woman at 10 AM and at 10 PM wearing the stick (AI illustration)',
         'lead': 'From 10 AM', 'mark': 'to 10 PM',
         'paras': ['A thin, creamy layer moves with your skin instead of drying on top of it, so it is made to look the same at '
                   'dinner as it did at breakfast: no orange by the window, no lines it found by lunch. Out late? Buff the brush '
                   'end over your nose and chin and you are done. Results vary from person to person.'],
         'usps': [('Made to wear all day', 'clock'), ('Touch up with the brush', 'brush')]},
        {'img': 'swatch', 'alt': 'A stripe of the stick’s white cream and the same stripe blended into the skin (AI illustration)',
         'lead': 'How does it work?', 'mark': None,
         'paras': ['Dot a little on your cheeks, forehead and chin. It looks white: that’s the capsules, still closed.',
                   'Turn the stick and buff with the brush in small circles. The capsules break and the color shifts toward your '
                   'own tone in about a minute.',
                   'Add a second thin layer where you want more coverage. That’s it: no sponge, no shade, no mess.'],
         'usps': [('Goes on white, blends to you', 'tones'), ('Brush in the stick', 'stick')]},
    ],
    'results': {'title': 'What to expect',
                'cards': [('1 min', 'From white to your tone', 'Swipe on, then buff with the brush'),
                          ('0', 'Shades to choose', 'One stick adapts as you blend'),
                          ('30 days', 'To try it risk-free', 'Love it, or your money back')]},
    'compare': {'title': 'Why SKINOFAB?', 'others': 'Your old foundation',
                'rows': ['No shade to choose', 'Brush built in', 'No pump, no spills', 'Fits in your bag',
                         'Creamy on dry skin']},
    'inside': {'title': 'What’s inside, and why your skin will love it',
               'intro': 'The Adaptive Foundation Stick is makeup with skincare in it: an adaptive cream in a base made for dry, mature skin.',
               'cards': [('ing-ha', 'Hyaluronic acid', 'Holds water in the skin, for a fresh, comfortable finish'),
                         ('ing-niacinamide', 'Niacinamide', 'Vitamin B3, for a more even-looking complexion'),
                         ('ing-squalane', 'Squalane', 'Softens, so the cream glides over dry patches'),
                         ('ing-vite', 'Vitamin E', 'Antioxidant care for soft, supple skin'),
                         ('ing-centella', 'Centella asiatica', 'A calming plant extract, for skin that feels sensitive')]},
    # the foundation's customer clips: how to use it, in the same cards (not reviews)
    'cards': {'eyebrow': 'How to use it', 'title': 'Twist, dot, buff, done', 'items': [
        {'img': 'twist', 'title': 'Twist up a little', 'text': 'A few millimeters is all you need.', 'alt': 'Hands twisting up the white foundation end of the stick'},
        {'img': 'dots', 'title': 'Dot it on', 'text': 'A few dots on your cheeks and forehead. It looks white at first.', 'alt': 'A woman with three white dots of the foundation on her face, the stick in her hand'},
        {'img': 'blend', 'title': 'Buff it in', 'text': 'Small circles with the brush end until it shifts to your tone.', 'alt': 'Buffing the foundation in with the brush end'},
        {'img': 'apply-cheek', 'title': 'Build where you need it', 'text': 'A second thin swipe on spots and redness, then buff the edges.', 'alt': 'Swiping the white foundation along a cheekbone'}]},
    'why': {'title': 'The SKINOFAB difference', 'img': 'hold-cheek', 'button': 'Choose your pack',
            'features': [('Your shade, without guessing', 'It goes on white and adapts to your tone as you blend', 'tones'),
                         ('The brush is built in', 'A dense kabuki brush on the other end of the stick', 'brush'),
                         ('30-day money-back guarantee', 'Love it, or email us for a full refund', 'shield')]},
}


def picker_html(variants, gift_imgs, css):
    return _b.picker_html(variants, gift_imgs, css, bundles=BUNDLES, gifts=GIFTS, legend='Choose your pack', refill=REFILL)


def no_reviews_html(buy='#apf-buy', amazon=None): return _b.no_reviews_html(buy, amazon, NO_REVIEWS)


BUYBOX_CSS = _b.BUYBOX_CSS


# around the site ---------------------------------------------------------------------------------------------------
# the shelf: after the foundation in the default list and the Bestsellers and Face tabs, first in the New tab (it is
# the newest, and that tab has no foundation card)
# (not in the NEXT Bestsellers collection: a new product has no sales to rank it by; the homepage shelf is
# "Shop the range", review 7)
SHELF = {'badge': 'New', 'saving': 'Buy 2, get 1 free', 'tags': ['Adapts to you', 'Brush built in', 'Cream stick'],
         'after': {'list': 'color-changing-foundation', 'bestsellers_0': 'color-changing-foundation',
                   'bestsellers_1': None, 'bestsellers_2': 'color-changing-foundation'}}
# the NEXT collections (as the foundation): Face, Skin, Bestsellers
CATEGORIES = ['face', 'skin']
# menus: apply_persona.py's MENU puts the stick after the foundation (desktop and mobile), and its footer's Shop column
# after the foundation; no page-wide copy rules of its own
GLOBAL = []
