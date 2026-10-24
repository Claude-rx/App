"""The PDRN Plumping Balm: product page copy, offer and sections. Inspired by FEM+'s "Collagen Plump & Repair Volufiline
Balm" page (https://www.femplus.com/products/fempdrnbalm, teardown in docs/pdrn-balm.md), written new for SKINOFAB and
women past 45, in the foundation's black packaging.

FEM+'s structure that sells honestly stays (the tired-look problem, the stick-vs-cream comparison, the ingredient
cards, where and how to use it, a what-to-expect timeline, the objection FAQ, bundles, the guarantee, a sticky bar).
What nothing backs is left out: "96% sold", "1M+ units sold", "300+ bought today", "77% said...", the countdown,
"dermatologist tested", "supports collagen production" (a drug claim), and their customers' testimonials. The balm is
new at SKINOFAB: no reviews until real buyers write them. Bundle savings are real (the single-stick price times the
sticks), there is no invented "was" price.

Before launch: the key ingredients (INGREDIENTS) and the net weight must match the supplier's specification sheet.

Read by apply_persona.py (it builds products/pdrn-plumping-balm.html from the foundation page's markup, product_page())
and by setup_brush_offers.py (the NEXT product, its three bundles and their prices).
"""
import html
from pathlib import Path
import brush_copy as _b
from brush_copy import money, esc, _CHECK, _ARROW, _head

KEY, MEDIA_BASE = 'balm', 9400000000000           # section ids, gallery media ids
HANDLE = 'pdrn-plumping-balm'
TITLE = 'PDRN Plumping Balm'
NAV_LABEL = 'PDRN Balm'
SHOPIFY_ID, SHOPIFY_VARIANT = 15517563191700, 61233683038600    # ids for the design markup's product JSON (not Shopify's)
PRICE, COMPARE = '24.95', '24.95'                                # one stick; no "was" price
EMAIL = 'hello@skinofab.com'
NET = '10 g / 0.35 oz'
IMG = Path(__file__).resolve().parents[2] / 'brand' / 'pdrn-balm'     # balm_assets.py writes the images here
IMG_PREFIX, GIFT_PREFIX = 'skinofab-pdrn-balm', 'skinofab-balm-gift'
OFFERS_FILE, REVIEWS_DIR, AMAZON_FILE = 'balm-offers.json', 'reviews-balm', None
DESCRIPTION = ('<p>A press-on PDRN balm stick for under-eyes, smile lines and lip lines. PDRN, Volufiline™, collagen and '
               'hyaluronic acid in a melting balm: skin looks smoother, plumper and rested in seconds, and softer with daily use. '
               f'{NET}, about a month of daily use.</p>')
META_TITLE = 'PDRN Plumping Balm | Press-on stick for tired-looking under-eyes | SKINOFAB'
META_DESCRIPTION = ('A PDRN, Volufiline and collagen balm stick for tired-looking under-eyes, smile lines and lip lines. '
                    'Swipe, press, done in 10 seconds. 30-day money-back guarantee. Free shipping.')

# the gallery (balm_assets.py), first one eager; the card is the shelf, cart and sticky-bar image
GALLERY = ['hero', 'ingredients', 'stick-vs-cream', 'where', 'how-to-use', 'texture', 'duo']
HERO = {'title': ['LOOK LESS TIRED'], 'accent': 'IN 10 SECONDS',
        'facts': ['PDRN + Volufiline™', 'Under-eyes, smile & lip lines', 'Press on, no fingers']}

# the buy box --------------------------------------------------------------------------------------------------------
EYEBROW = 'PDRN K-beauty · Press-on stick'
SHIPPING_BADGE = '\U0001F381 FREE SHIPPING'
LEAD = ('The 10-second pick-me-up for the spots that make you look tired: hollow-looking under-eyes, smile lines and the lines '
        'around your lips. Swipe it on, press it in, and skin looks smoother, fuller and rested.')
_LINE = _b._LINE
CHIPS = [
    ('Looks smoother in seconds', '<path d="M3 12h4l3-8 4 16 3-8h4"/>'),
    ('Under-eyes, smile & lip lines', '<circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>'),
    ('No fingers, no mess', '<path d="M8 3h8v6H8z"/><path d="M9 9h6v12H9z"/>'),
    ('Fits in your pocket', '<rect x="6" y="3" width="12" height="18" rx="3"/><path d="M10 7h4"/>'),
]
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
GUARANTEE = '30-Day Money-Back Guarantee'
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
    """The four tabs under the buy box."""
    ship = _b.tabs()[1]                        # the store's shipping terms, as on the brush
    return [
        ('What it does',
         '<p>A melting balm in a press-on stick for the spots that make you look tired.</p>'
         + _list(['Under-eyes look smoother, fuller and less hollow', 'Smile lines and lip lines look softer',
                  'Dry, crepey patches look hydrated', 'Makeup sits better and creases less'])
         + '<p>Use it under or over makeup, or on bare skin.</p>'),
        ('Key ingredients',
         ''.join(f'<p><strong>{esc(n)}:</strong> {esc(t)}.</p>' for n, t, _ in INGREDIENTS)
         + f'<p>{esc(ADENOSINE)}</p>'
         '<p><strong>Contains salmon-derived DNA (PDRN).</strong> If you have a fish allergy, check the full ingredient list '
         'on the box and ask your doctor before use.</p>'
         f'<p><strong>Net weight:</strong> {NET}.</p>'),
        ('How to use',
         _list(['Twist up a little balm', 'Swipe a thin layer on the spot: under the eyes, smile lines, around the lips',
                'Press it in with the stick or tap with a fingertip, no rubbing', 'Morning and night; at night you can go a little thicker'])
         + '<p><strong>Less is more:</strong> a thin layer looks smooth; too much looks shiny.</p>'),
        ship,
        ('Try it 100% risk-free (Easy Returns)',
         '<p>Use it for <strong>30 days</strong>. If you don’t see a difference, send it back for a <strong>full refund</strong>, '
         'no hassle, no questions asked.</p>'
         f'<p>Please email us at <a href="mailto:{EMAIL}">{EMAIL}</a> to receive return instructions.</p>'),
    ]


# the sections below ------------------------------------------------------------------------------------------------
PROBLEM = {'eyebrow': 'It’s not you, it’s your skin after 45', 'lead': 'Why you look tired', 'mark': 'even when you’re not',
           'cards': [
               ('Thinner skin under the eyes',
                'Skin loses up to 30% of its collagen in the first five years after menopause. The thin skin under the eyes '
                'shows it first: it looks hollow and shadowed even after a full night.'),
               ('Drier skin, deeper-looking lines',
                'Skin holds less water with age. Smile lines and the lines around your lips look deeper when skin is dry, '
                'and they look softer when it is hydrated.'),
               ('Concealer that settles in',
                'You cover the shadows, and an hour later the concealer has slid into every crease. More product only makes it worse.'),
               ('Fine in the morning, tired by noon',
                'You look rested at home, then catch yourself in a shop window or a photo and look exhausted. That gap is what gets to you.'),
           ], 'end_lead': 'You don’t want to look different.', 'end_mark': 'Just rested.', 'button': 'Choose your pack'}
SCIENCE = {'eyebrow': 'What’s inside', 'lead': 'Four K-beauty actives,', 'mark': 'one balm'}
STICK = {'eyebrow': 'Why a stick', 'lead': 'Why a press-on stick works', 'mark': 'where creams don’t',
         'ours': 'PDRN Plumping Balm', 'theirs': 'A jar of cream',
         'rows': [('Goes exactly where you look tired', 'Spreads one thin film over your whole face'),
                  ('Stays on the line you pressed it into', 'Slides off the crease you aimed at'),
                  ('10 seconds, nothing on your fingers', 'A pump, both hands, then a towel'),
                  ('Lives in your bag, touch-ups anywhere', 'Stays on the bathroom shelf'),
                  ('The same thin layer every time', 'However much your finger scooped up'),
                  ('One stick for eyes, smile and lips', 'A different jar for each area')]}
WHERE = {'eyebrow': 'Where to use it', 'lead': 'One stick,', 'mark': 'five spots',
         'spots': [('Under the eyes', 'hollow-looking, shadowed'), ('Smile lines', 'nose to mouth'),
                   ('Around the lips', 'lip lines and dry lips'), ('Between the brows', 'and forehead lines'),
                   ('Neck', 'dry, crepey-looking skin')]}
HOWTO = {'eyebrow': 'How to use it', 'lead': 'Swipe, press,', 'mark': 'done',
         'steps': [('Swipe', 'Twist up a little and swipe a thin layer onto the spot.'),
                   ('Press', 'Press it in with the stick or tap with a fingertip. Don’t rub or drag the skin.'),
                   ('Repeat', 'Morning and night. Touch up during the day, over makeup too.')],
         'note': 'Less is more: a thin layer looks smooth and natural, too much looks shiny.'}
EXPECT = {'eyebrow': 'What to expect', 'lead': 'Honest results,', 'mark': 'no filters',
          'cards': [('Right away', 'Skin looks hydrated and smoother, under-eyes look less dry and crepey, and concealer creases less. That’s the balm at work, on day one.'),
                    ('With daily use', 'Over the first weeks, skin stays more hydrated and feels softer, and fine lines around the eyes and mouth look less obvious. Results vary from person to person.'),
                    ('What it won’t do', 'It’s not a filler: it won’t erase deep wrinkles or change the color of dark circles. If it isn’t for you, the 30-day guarantee has you covered.')]}
CROSS = {'eyebrow': 'Then, your foundation', 'lead': 'No more creasing with', 'mark': 'one adaptive shade',
         'text': 'Press the balm in first, then one pump of the Adaptive Peptide Foundation: it goes on white and turns into your skin '
                 'tone as you blend, and glides over the smoothed lines instead of settling into them.',
         'button': 'See the foundation'}
NO_REVIEWS = {'title': 'Customer reviews', 'lead': 'No reviews yet', 'lead_amazon': 'No SKINOFAB reviews yet',
              'text': 'The PDRN Plumping Balm is new at SKINOFAB, and we only show reviews from real buyers. Try it for 30 days: '
                      'if you don’t see a difference, we’ll refund you.',
              'button': 'Try it risk-free', 'write': 'Bought it? Write the first review'}
FAQ = {'eyebrow': 'Before you try it', 'title': 'Your questions, answered', 'items': [
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
RISK_FREE = {'eyebrow': 'Try it 100% Risk-Free', 'lead': '30-day money-back', 'mark': 'guarantee', 'proof': None,
             'text': 'Use it for 30 days. If your under-eyes don’t look more rested and your lines don’t look softer, send it back for a '
                     'full refund, no hassle, no questions asked.',
             'button': 'Choose your pack'}

SECTIONS_CSS = r"""
.sfp-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.sfp-cards article{background:#fff;border-radius:20px;padding:24px 22px}
.sfp-cards b{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#151515;color:#fff;font-size:14px;margin:0 0 14px}
.sfp-cards h3{font-size:18px;line-height:1.3;font-weight:600;margin:0 0 8px}
.sfp-cards p{font-size:15px;line-height:1.55;color:#3b3b3b;margin:0}
.sfp-sci{display:grid;grid-template-columns:minmax(0,440px) minmax(0,1fr);gap:44px;align-items:center;max-width:1080px;margin:0 auto}
.sfp-sci img,.sfp-how img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:22px;display:block;background:#e9eaee}
.sfp-ing{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.sfp-ing article{border:1px solid #e7e7e7;border-radius:18px;padding:20px}
.sfp-ing h3{font-size:19px;font-weight:700;margin:0}
.sfp-ing small{display:block;font-size:12.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#6a6a6a;margin:4px 0 10px}
.sfp-ing p{font-size:15px;line-height:1.55;color:#3b3b3b;margin:0}
.sfp-ing-note{font-size:14.5px;color:#6a6a6a;margin:16px 0 0}
.sfp-vs{max-width:860px;margin:0 auto;border-radius:22px;overflow:hidden;border:1px solid #e3e3e3;background:#fff}
.sfp-vs table{width:100%;border-collapse:collapse}
.sfp-vs th{padding:18px 16px;font-size:14px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;text-align:left;width:50%}
.sfp-vs th:first-child{background:#151515;color:#fff}
.sfp-vs th:last-child{background:#f3f3f3;color:#6a6a6a}
.sfp-vs td{padding:15px 16px;font-size:15.5px;line-height:1.45;vertical-align:top;border-top:1px solid #ececec}
.sfp-vs td:first-child{font-weight:600;color:#151515;background:#fafafa}
.sfp-vs td:last-child{color:#7a7a7a}
.sfp-vs td span{display:inline-flex;align-items:flex-start;gap:8px}
.sfp-vs td svg{flex:none;margin-top:2px}
.sfp-how{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,440px);gap:44px;align-items:center;max-width:1080px;margin:0 auto}
.sfp-spots{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 26px;padding:0;list-style:none}
.sfp-spots li{padding:9px 14px;border-radius:999px;background:#fff;border:1px solid #e3e3e3;font-size:14.5px}
.sfp-spots b{font-weight:600}
.sfp-spots span{color:#6a6a6a}
@media (max-width:989px){
 .sfp-cards{grid-template-columns:1fr 1fr}
 .sfp-sci,.sfp-how{grid-template-columns:1fr;gap:26px}
 .sfp-how > :last-child{order:-1}
}
@media (max-width:599px){
 .sfp-cards{grid-template-columns:1fr}
 .sfp-ing{grid-template-columns:1fr}
 .sfp-vs th,.sfp-vs td{padding:12px 12px;font-size:14px}
}
"""
_X = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
      'stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>')


def problem_html(buy='#apf-buy'):
    p = PROBLEM
    cards = ''.join(f'<article><b>{k}</b><h3>{esc(h)}</h3><p>{esc(t)}</p></article>' for k, (h, t) in enumerate(p['cards'], 1))
    return (f'<section class="sfb sfb-sec sfb-sec--grey" id="sfp-problem">{_head(p["eyebrow"], p["lead"], p["mark"])}'
            f'<div class="sfb-wrap"><div class="sfp-cards">{cards}</div>'
            f'<div class="sfb-end"><p>{esc(p["end_lead"])} <em>{esc(p["end_mark"])}</em></p>'
            f'<a class="sfb-btn" href="{buy}">{esc(p["button"])} {_ARROW}</a></div></div></section>')


def science_html(img):
    s = SCIENCE
    cards = ''.join(f'<article><h3>{esc(n)}</h3><small>{esc(t)}</small><p>{esc(d)}</p></article>' for n, t, d in INGREDIENTS)
    return (f'<section class="sfb sfb-sec" id="sfp-science">{_head(s["eyebrow"], s["lead"], s["mark"])}'
            f'<div class="sfb-wrap"><div class="sfp-sci"><img src="{img}" alt="The PDRN Plumping Balm and its key ingredients" '
            f'width="1080" height="1080" loading="lazy" decoding="async">'
            f'<div><div class="sfp-ing">{cards}</div><p class="sfp-ing-note">{esc(ADENOSINE)}</p></div></div></div></section>')


def stick_html():
    s = STICK
    rows = ''.join(f'<tr><td><span>{_CHECK}{esc(a)}</span></td><td><span>{_X}{esc(b)}</span></td></tr>' for a, b in s['rows'])
    return (f'<section class="sfb sfb-sec sfb-sec--grey" id="sfp-stick">{_head(s["eyebrow"], s["lead"], s["mark"])}'
            f'<div class="sfb-wrap"><div class="sfp-vs"><table><thead><tr><th scope="col">{esc(s["ours"])}</th>'
            f'<th scope="col">{esc(s["theirs"])}</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>')


def how_html(img, buy='#apf-buy'):
    w, h = WHERE, HOWTO
    spots = ''.join(f'<li><b>{esc(a)}</b> <span>· {esc(b)}</span></li>' for a, b in w['spots'])
    steps = ''.join(f'<li><b>{k}</b><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>' for k, (t, d) in enumerate(h['steps'], 1))
    return (f'<section class="sfb sfb-sec" id="sfp-how">{_head(w["eyebrow"], w["lead"], w["mark"])}'
            f'<div class="sfb-wrap"><div class="sfp-how"><div><ul class="sfp-spots">{spots}</ul>'
            f'<span class="sfb-eyebrow">{esc(h["eyebrow"])}</span><ol class="sfb-steps">{steps}</ol>'
            f'<p class="sfb-routine__note">{esc(h["note"])}</p></div>'
            f'<img src="{img}" alt="How to use the PDRN Plumping Balm" width="1080" height="1080" loading="lazy" decoding="async"></div>'
            f'<div class="sfb-end"><a class="sfb-btn" href="{buy}">{esc(PROBLEM["button"])} {_ARROW}</a></div></div></section>')


def picker_html(variants, gift_imgs, css):
    return _b.picker_html(variants, gift_imgs, css, bundles=BUNDLES, gifts=GIFTS, legend='Choose your pack')


def risk_free_html(buy='#apf-buy'): return _b.risk_free_html(buy, RISK_FREE)


def no_reviews_html(buy='#apf-buy', amazon=None): return _b.no_reviews_html(buy, amazon, NO_REVIEWS)


def chips_html():
    return ('<div class="sfb-chips">' + ''.join(f'<span>{_LINE}{svg}</svg>{esc(t)}</span>' for t, svg in CHIPS) + '</div>')


BUYBOX_CSS = _b.BUYBOX_CSS + r"""
.sfp-eyebrow{display:block;margin:0 0 8px;font-size:12.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#6a6a6a}
"""


def sections(ctx):
    """The sections under the buy box, in order. ctx: copy(path, sub, name, size) -> url, strip (review strip html or
    ''), cross (img, href, price, compare, rating)."""
    img = lambda name, w=1080: ctx['copy'](IMG / f'{name}.jpg', 'img', f'{IMG_PREFIX}-{name}-{w}w', (w, w))
    out = ([f'<div class="shopify-section" id="shopify-section-sf-review-strip">{ctx["strip"]}</div>'] if ctx['strip'] else [])
    out += [f'<div class="shopify-section" id="shopify-section-sf-balm-problem"><style>{_b.SECTIONS_CSS}{SECTIONS_CSS}</style>{problem_html()}</div>',
            f'<div class="shopify-section" id="shopify-section-sf-balm-science">{science_html(img("ingredients"))}</div>',
            f'<div class="shopify-section" id="shopify-section-sf-balm-stick">{stick_html()}</div>',
            f'<div class="shopify-section" id="shopify-section-sf-balm-how">{how_html(img("how-to-use"))}</div>',
            f'<div class="shopify-section" id="shopify-section-sf-balm-expect">{_b.expect_html(EXPECT)}</div>',
            f'<div class="shopify-section" id="shopify-section-sf-balm-cross">{_b.cross_html(*ctx["cross"], c=CROSS)}</div>']
    return out


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
