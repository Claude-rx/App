"""The EGF + NAD+ Firming Serum: product page copy, offer and sections. Inspired by Meimei's "NAD+ Firming Serum" page
(https://officialmeimei.com/products/egf-nad-firming-serum, teardown in docs/egf-nad-serum.md), written new for SKINOFAB
and women past 45, in the brand's packaging system: the foundation's matte black cylinder, here with a dropper, and its vertical label
with SKINOFAB's real wordmark (label_composite.py prints it on every photo).

The page has the Adaptive Peptide Foundation page's structure, section by section (twin.py, TWIN below), with its
photos on white: women past 45 holding and using the serum, before/after illustrations (labelled as such) and the
ingredient textures (product_photos.py, image_prompts.json). Meimei's devices that sell honestly are in it (the
firmness problem, how to use it, the ingredient cards, what to expect, the objection FAQ, the guarantee); what nothing
backs stays out: "#1 Firming Serum", "4.9 based on 137,135 reviews", "Join over 10,000+ happy customers", the
"clinically proven" percentages (from a self-perception study), "clinically recommended", "works at the source",
"repair" and "stimulate collagen" (drug claims), and its testimonials (they name another product, a cream). The
serum is new at SKINOFAB: the reviews near the top are the foundation's, labelled as theirs, and the review wall says
"no reviews yet" until real buyers write some. Bundle savings are real (the single-bottle price times the bottles);
there is no invented "was" price.

Before launch: the ingredients (INGREDIENTS) and the size must match the supplier's specification sheet. Meimei's own
ingredient list names NAD+ and collagen but no EGF: if the supplier's formula has no sh-Oligopeptide-1, the name and
the EGF lines change. sh-Oligopeptide-1 is not allowed in cosmetics sold in the EU: check before selling there.

Read by apply_persona.py (it builds products/egf-nad-firming-serum.html from the foundation page's markup,
product_page()) and by setup_brush_offers.py (the NEXT product, its three bundles and their prices).
"""
from pathlib import Path
import brush_copy as _b
from brush_copy import money, esc

KEY, MEDIA_BASE = 'serum', 9500000000000          # section ids, gallery media ids
HANDLE = 'egf-nad-firming-serum'
TITLE = 'EGF + NAD+ Firming Serum'
NAV_LABEL = 'Firming Serum'
SHOPIFY_ID, SHOPIFY_VARIANT = 15517563191800, 61233683038700    # ids for the design markup's product JSON (not Shopify's)
PRICE, COMPARE = '34.95', '34.95'                                # one bottle; no "was" price
EMAIL = 'hello@skinofab.com'
SIZE = '30 mL / 1.01 fl oz'
IMG = Path(__file__).resolve().parents[2] / 'brand' / 'egf-nad-serum'   # product_photos.py writes the images here
IMG_PREFIX, GIFT_PREFIX = 'skinofab-egf-nad-serum', 'skinofab-serum-gift'
OFFERS_FILE, REVIEWS_DIR, AMAZON_FILE = 'serum-offers.json', 'reviews-serum', None
DESCRIPTION = ('<p>A light firming serum for face and neck. EGF (sh-Oligopeptide-1), NAD+ and collagen in a water-based serum '
               'that sinks in within a minute: skin looks hydrated and smoother from the first use, and firmer and more radiant '
               f'with daily use. {SIZE}, about two months of daily use.</p>')
META_TITLE = 'EGF + NAD+ Firming Serum | Light firming serum for face and neck after 45 | SKINOFAB'
META_DESCRIPTION = ('EGF, NAD+ and collagen in one light serum for skin after 45. Two drops for the face, two for the neck, '
                    'morning and night. 30-day money-back guarantee. Free shipping.')

# the gallery (product_photos.py writes brand/egf-nad-serum/<name>.jpg): the foundation gallery's order and kinds of
# image, first one eager; the card is the shelf, cart and sticky-bar image
GALLERY = ['hero', 'hold-cheek', 'before-after', 'look-firmer', 'results-grid', 'whats-inside', 'science', 'vs-others',
           'drop', 'hold-black', 'friends', 'apply-neck', 'trio']
KOREAN = True          # the foundation's "Formulated in Korea" line stays in the buy box

# the buy box --------------------------------------------------------------------------------------------------------
EYEBROW = None
SHIPPING_BADGE = '\U0001F381 FREE SHIPPING'
LEAD = ('One light step for skin that looks less firm, drier and duller: EGF, NAD+ and collagen in a serum that sinks in '
        'within a minute. Two drops for your face, two for your neck.')
BUNDLES = [
    {'key': '1', 'name': '1 Bottle', 'note': 'About 2 months', 'variant': '1 bottle', 'sku': 'SKF-ENS-1',
     'price': '34.95', 'compare': '34.95', 'gifts': []},
    {'key': '2', 'name': '2 Bottles', 'note': 'About 4 months · or share one', 'variant': '2 bottles', 'sku': 'SKF-ENS-2',
     'price': '59.95', 'compare': '69.90', 'badge': 'Most popular', 'default': True, 'gifts': []},
    {'key': '3', 'name': 'Buy 2, Get 1 Free', 'note': 'About 6 months · best value', 'variant': '3 bottles (buy 2, get 1 free)',
     'sku': 'SKF-ENS-3', 'price': '69.90', 'compare': '104.85', 'badge': 'Best value', 'gifts': []},
]
GIFTS = {}
GIFT_FILES = {}
STICKY_BUTTON = 'Choose your pack'
CART_UPGRADE = {'title': 'Upgrade to 2 bottles', 'button': 'Upgrade'}

# what is in it (match to the supplier's INCI before launch)
INGREDIENTS = [
    ('EGF', 'sh-Oligopeptide-1, a lab-made peptide',
     'A bioengineered peptide modelled on a growth factor found in skin. In a serum it helps skin look smoother, firmer '
     'and more even.'),
    ('NAD+', 'The “longevity” coenzyme',
     'Nicotinamide adenine dinucleotide, the ingredient behind the longevity skincare trend. It’s there for skin that '
     'looks tired and dull, to help it look fresher and more radiant.'),
    ('Collagen', 'For a firmer feel',
     'Collagen holds water on the skin’s surface, so skin feels firmer and smoother and looks plumper.'),
    ('Glycerin', 'Pulls water into skin',
     'Draws in moisture so skin stays soft and hydrated, and fine lines look less obvious.'),
]
TEXTURE = 'Water-based and light: it sinks in within a minute and sits well under moisturiser, SPF and makeup.'


def _list(items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def tabs():
    """The tabs under the buy box, the foundation's six."""
    return [
        ('What makes it different?',
         '<p>Most serums do one thing, for the face only. This one puts EGF, NAD+ and collagen in one light serum made for '
         'skin after 45, for the face and the neck.</p>'
         + _list(['EGF, NAD+ and collagen in one bottle', 'Light and water-based: sinks in within a minute',
                  'Face and neck, morning and night', 'Under moisturiser, SPF and makeup'])),
        ('Does it work on my skin?',
         '<p>It’s made for skin after 45: skin that looks less firm, drier and duller is exactly where these actives show the most.</p>'
         '<p>It’s gentle on most skin. If your skin reacts easily, try it on a small area first, and don’t use it on broken or '
         'irritated skin. Keep it out of your eyes. Pregnant, breastfeeding or under treatment for a skin condition? Ask your '
         'doctor first.</p>'),
        ('How do I use it?',
         _list(['Cleanse your face and neck', 'Two drops for your face, pressed in with your fingertips',
                'Two more drops, swept down your neck', 'Morning and night: then your moisturiser, and SPF in the morning'])
         + '<p><strong>Less is more:</strong> two drops cover the whole face.</p>'),
        ('How does the money-back guarantee work?',
         '<p>Use it for <strong>30 days</strong>. If you don’t see a difference, send it back for a <strong>full refund</strong>, '
         'no hassle, no questions asked.</p>'
         f'<p>Please email us at <a href="mailto:{EMAIL}">{EMAIL}</a> to receive return instructions.</p>'),
        ('Ingredients',
         ''.join(f'<p><strong>{esc(n)}:</strong> {esc(t)}.</p>' for n, t, _ in INGREDIENTS)
         + f'<p>{esc(TEXTURE)}</p>'
         '<p>The full ingredient list is on the box. If your skin reacts easily, check it before use.</p>'
         f'<p><strong>Size:</strong> {SIZE}.</p>'),
        _b.SHIPPING_TAB,
    ]


# the sections below: the foundation page's, in its order (twin.py), with the serum's copy -----------------------------
NO_REVIEWS = {'title': 'Customer reviews', 'lead': 'No reviews yet', 'lead_amazon': 'No SKINOFAB reviews yet',
              'text': 'The EGF + NAD+ Firming Serum is new at SKINOFAB, and we only show reviews from real buyers. Try it for '
                      '30 days: if you don’t see a difference, we’ll refund you.',
              'button': 'Try it risk-free', 'write': 'Bought it? Write the first review'}
FAQ = {'items': [
    ('How do I use it?',
     'After cleansing, two drops for your face and two for your neck, morning and night. Press it in, wait a minute, then '
     'your moisturiser, and SPF in the morning.'),
    ('Will it feel sticky or heavy?',
     'No. It’s a light, water-based serum that sinks in within a minute and leaves skin soft, not tacky.'),
    ('Can I wear it under makeup?',
     'Yes. Let it sink in for a minute, then your moisturiser and foundation: it gives makeup a smoother surface.'),
    ('Does it work on mature skin?',
     'It’s made for it. Skin after 45 looks less firm, drier and duller, and that’s exactly what EGF, NAD+ and collagen are there for.'),
    ('Can I use it with retinol or vitamin C?',
     'Yes. Use it after cleansing and before heavier creams; at night, apply it first and let it sink in before your retinol. '
     'If your skin is sensitive, start one new product at a time.'),
    ('How long until I see a difference?',
     'Skin looks hydrated and smoother from the first use. A firmer, more radiant look comes with daily use over a few weeks. '
     'Results vary from person to person.'),
    ('How long does one bottle last?',
     'About two months, with two drops for the face and two for the neck, morning and night.'),
    ('Is it safe for sensitive skin?',
     'It’s gentle on most skin, but try it on a small area first if your skin reacts easily, and don’t use it on broken or '
     'irritated skin. Keep it out of your eyes.'),
    ('What is the EGF in it?',
     'sh-Oligopeptide-1: a peptide made in the lab, not taken from human or animal cells. If you are pregnant, breastfeeding '
     'or under treatment for a skin condition, ask your doctor before use.'),
    ('What if it doesn’t work for me?',
     f'Send it back within 30 days for a full refund. Just email {EMAIL}.'),
]}
# section by section, in the foundation page's order (twin.py names each slot); images are brand/egf-nad-serum/<name>.jpg
# or its source/ photo. The before/after photos are illustrations and say so on the image.
TWIN = {
    'loved': {'lead': 'Made for real life', 'mark': 'after 45'},
    'moments': [
        ('hold-cheek', 'Every morning', 'Two drops before your moisturiser.', 'A woman in her late fifties holding the EGF + NAD+ Firming Serum'),
        ('hold-black', 'Before makeup', 'It sinks in within a minute, so foundation goes on smooth.', 'A woman in her sixties holding the serum'),
        ('friends', 'One to keep, one to share', 'The 2-bottle pack: yours and your best friend’s.', 'Two women in their fifties and sixties with the serum'),
        ('mirror', 'At night', 'The last drops of the day, before your night cream.', 'A woman applying the serum at her bathroom mirror'),
        ('trio', 'Months of routine', 'Buy 2, get 1 free: about six months, morning and night.', 'Three bottles of the EGF + NAD+ Firming Serum'),
        ('apply-neck', 'Don’t forget the neck', 'Sweep two drops down your neck, every time.', 'A woman smoothing the serum down her neck'),
    ],
    'problem': {
        'img_problem': 'problem', 'img_solution': 'tall',
        'photo_alt': 'A woman in her fifties touching her jawline',
        'problem': ('The problem', 'Your skin isn’t bouncing', 'back like it used to'),
        'lede': 'Your jawline looks softer in photos. Your neck shows more than your face. And the creams that used to work now '
                'just sit on top.',
        'pains': ['A jawline that looks softer every year',
                  'Crepey-looking skin on the neck',
                  'Dull, tired-looking skin even after a full night',
                  'Fine lines that show more on dry days',
                  'Heavy creams that sit on top and pill under makeup'],
        'close': 'The result: more products, more steps, and skin that still looks tired.',
        'root': ('The root of it', 'Your skin changed.', 'Your routine didn’t.'),
        'causes': [('Less collagen, less bounce',
                    'Skin loses up to 30% of its collagen in the first five years after menopause, so it looks less firm and '
                    'less springy, on the face and the neck.'),
                   ('Drier, duller skin',
                    'Skin holds less water and renews more slowly with age, so it looks dull and fine lines show more.'),
                   ('Too many steps, too heavy',
                    'A drawer of creams that sit on top, pill under makeup and still leave the neck out.')],
        'root_end': 'So the problem was never you. It’s a routine that wasn’t made for skin after 45.',
        'solution': ('The solution', 'So we put three actives', 'in one light serum'),
        'solution_lede': 'The EGF + NAD+ Firming Serum starts from skin after 45: EGF, NAD+ and collagen in a light serum '
                         'that sinks in within a minute, for the face and the neck.',
        'fixes': [('Skin that looks less firm', 'EGF and collagen for skin that looks firmer and smoother.'),
                  ('Dull, tired-looking skin', 'NAD+, the longevity skincare ingredient, for a fresher, more radiant look.'),
                  ('Dry, deeper-looking lines', 'Glycerin and collagen hydrate, so fine lines look softer.'),
                  ('Heavy creams that pill', 'A light, water-based serum: it sinks in and sits well under makeup.'),
                  ('A routine that skips the neck', 'Two drops for the face, two for the neck: one step for both.')],
        'button': 'Get yours', 'note': 'Use it for 30 days, or your money back.',
        'product_alt': 'The EGF + NAD+ Firming Serum',
    },
    # the foundation's expert block: here the brand's own note, signed as the brand (no invented expert)
    'note': {'id': 'sf-note', 'eyebrow': 'Why we made it', 'photo': 'mirror',
             'photo_alt': 'A woman applying the EGF + NAD+ Firming Serum at her mirror',
             'headline_lead': '&hellip;one light step', 'headline_mark': 'for skin after 45.',
             'paragraphs': ['We make SKINOFAB for skin after 45. It changes: it looks less firm, drier and duller, and the neck '
                            'shows it as much as the face.',
                            'So we put EGF, NAD+ and collagen in a light serum that sinks in within a minute: <strong>two drops '
                            'for your face, two for your neck, morning and night.</strong>',
                            'It isn’t a facelift in a bottle, and we won’t pretend it is. It’s the one step that helps your skin '
                            'look firmer, smoother and more rested.'],
             'name': 'The SKINOFAB team', 'role': 'Made for skin after 45'},
    'science': {'img': 'swatch', 'alt': 'The EGF + NAD+ Firming Serum with its dropper and a drop of serum',
                'eyebrow': 'K-beauty skin science', 'lead': 'The Korean skincare actives,', 'mark': 'in one light serum',
                'lede': 'Korean skincare made EGF and NAD+ serums the step for skin that looks tired and less firm. We put them '
                        'with collagen in a light, water-based serum that sinks in within a minute.',
                'rows': [(n, d) for n, _, d in INGREDIENTS],
                'note': 'Water-based and light. The full ingredient list is on the box.',
                'button': 'Choose your pack'},
    'iwt': [
        {'img': 'ba-cheeks', 'alt': 'Cheeks and jawline before and after the serum (illustration)',
         'lead': 'Firmer-looking', 'mark': 'day by day',
         'paras': ['Skin looks hydrated and smoother from the first drops. With daily use, morning and night, it looks firmer, '
                   'more even and more radiant, on the face and the neck. Results vary from person to person.'],
         'usps': ['Hydrated from day one', 'Face and neck']},
        {'img': 'drop', 'alt': 'A woman applying the serum with its dropper',
         'lead': 'How does it work?', 'mark': None,
         'paras': ['Two drops on your face, morning and night, after cleansing.',
                   'Press it in with your fingertips: the light serum sinks in within a minute, and skin looks hydrated and smoother.',
                   'Two more drops down your neck. Then your moisturiser, and SPF in the morning.'],
         'usps': ['Sinks in within a minute', 'Under makeup and SPF']},
    ],
    'results': {'title': 'What to expect',
                'cards': [('2 drops', 'For your face, two more for your neck', 'Morning and night'),
                          ('Day 1', 'Skin looks hydrated and smoother', 'A cosmetic effect you can see right away'),
                          ('8 weeks', 'Of daily use from one bottle', 'Morning and night, face and neck')]},
    'compare': {'title': 'Why skinofab?', 'others': 'Basic serums',
                'rows': ['EGF, NAD+ and collagen in one bottle', 'Made for skin after 45', 'Light, sinks in within a minute',
                         'Face and neck', 'Under moisturiser, SPF and makeup']},
    'inside': {'title': 'What’s inside, and why your skin will love it',
               'intro': 'The EGF + NAD+ Firming Serum is K-beauty skincare in one light step: three actives made for skin after 45.',
               'cards': [('ing-egf', 'EGF', 'A lab-made peptide modelled on a growth factor in skin'),
                         ('ing-nad', 'NAD+', 'The ingredient behind the longevity skincare trend'),
                         ('ing-collagen', 'Collagen', 'Holds water so skin feels firmer and looks plumper'),
                         ('palm', 'A light serum', 'Water-light: it sinks in within a minute'),
                         ('swatch', 'Two drops is enough', 'For your face; two more for your neck')]},
    # the foundation's customer clips: how to use it, in the same cards (not reviews)
    'cards': {'eyebrow': 'How to use it', 'title': 'Two drops, face and neck', 'items': [
        {'img': 'palm', 'title': 'Two drops', 'text': 'Into your fingertips, after cleansing.', 'alt': 'Two drops of serum from the dropper into a palm'},
        {'img': 'apply-cheeks', 'title': 'Press it in', 'text': 'Over your face, no rubbing: it sinks in within a minute.', 'alt': 'A woman pressing the serum into her cheeks'},
        {'img': 'apply-neck', 'title': 'Down the neck', 'text': 'Two more drops, swept down toward the chest.', 'alt': 'A woman smoothing the serum down her neck'},
        {'img': 'mirror', 'title': 'Morning and night', 'text': 'Then your moisturiser, and SPF in the morning.', 'alt': 'A woman applying the serum at her mirror'}]},
    'why': {'title': 'The skinofab difference', 'img': 'temple', 'button': 'Claim offer',
            'features': [('Three actives, one step', 'EGF, NAD+ and collagen in one light serum'),
                         ('Made for skin after 45', 'For skin that looks less firm, drier and duller'),
                         ('30-day money-back guarantee', 'Love it or send it back for a full refund')]},
}


def picker_html(variants, gift_imgs, css):
    return _b.picker_html(variants, gift_imgs, css, bundles=BUNDLES, gifts=GIFTS, legend='Choose your pack')


def no_reviews_html(buy='#apf-buy', amazon=None): return _b.no_reviews_html(buy, amazon, NO_REVIEWS)


BUYBOX_CSS = _b.BUYBOX_CSS


# around the site ---------------------------------------------------------------------------------------------------
SHELF = {'badge': 'New', 'saving': 'Buy 2, get 1 free', 'tags': ['EGF', 'NAD+', 'Face & neck'],
         'after': {'list': 'pdrn-plumping-balm', 'bestsellers_0': 'pdrn-plumping-balm',
                   'bestsellers_1': 'pdrn-plumping-balm', 'bestsellers_2': 'pdrn-plumping-balm'}}
# the NEXT collections (as the foundation and the other face skincare): Face, Skin, Bestsellers
CATEGORIES = ['face', 'skin', 'the-hits']
# menus on every page (after the balm's rules ran): a top-level link before the balm (desktop and mobile) and one after
# it in the footer's Shop column
GLOBAL = [
    (r'RE:(<div class="menu__item child" data-hover-disclosure-toggle="" data-nav-item="">\s*<a class="navlink navlink--toplevel caps" '
     r'data-top-link="" href=")((?:\.\./)*)(products/pdrn-plumping-balm\.html">)',
     r'\1\2products/' + HANDLE + r'.html"> <span class="navtext">' + NAV_LABEL + r'</span> </a></div> \1\2\3'),
    (r'RE:(<li class="mobile-menu__item mobile-menu__item--level-1">\s*<a class="mobile-navlink mobile-navlink--level-1" href=")'
     r'((?:\.\./)*)(products/pdrn-plumping-balm\.html">)',
     r'\1\2products/' + HANDLE + r'.html"> ' + NAV_LABEL + r' </a> </li>\1\2\3'),
    (r'RE:(<li><a href=")((?:\.\./)*)(products/pdrn-plumping-balm\.html">PDRN Balm</a></li>)',
     r'\1\2\3<li><a href="\2products/' + HANDLE + r'.html">' + NAV_LABEL + r'</a></li>'),
]
