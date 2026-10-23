"""The Lymphatic Brush: product page copy, offer and sections, built from the owner's Solena page
(https://thesolena.com/products/the-lymphatic-brush), under the SKINOFAB name and in the SKINOFAB look.

Solena's structure and offer, with the claims nothing backs taken out: no "drains fluid", no "less puffy from the first
use" as a promise, no "10 years younger" or "sculpted face" clips, no buyer counts, no Solena reviews. The brush is a
light, dry massage for the look of morning puffiness, and the page says so, including what it will not do. Order:
gallery and buy box (rating once real reviews exist, bundle picker, guarantee, five tabs), the 3-minute routine, the
creator clips, why faces are puffy in the morning, what to expect, the copy comparison, the foundation for after, the
FAQ, the guarantee and the reviews (an honest first-review box until there are some).

Read by apply_persona.py (it builds products/the-lymphatic-brush.html from the foundation page's markup) and by
setup_brush_offers.py (the NEXT product, its three bundles and their prices).
"""
import html, json

HANDLE = 'the-lymphatic-brush'
TITLE = 'The Lymphatic Brush'
SHOPIFY_ID, SHOPIFY_VARIANT = 15517563191626, 61233683038538       # Solena's ids (the design markup carries them)
PRICE, COMPARE = '24.95', '49.90'
EMAIL = 'hello@skinofab.com'
DESCRIPTION = ('<p>A 3-minute depuffing massage for your morning face. Thousands of ultra-soft bristles sweep from under '
               'your eyes, along your cheeks and jaw and down your neck with a light touch, on dry skin, no oil. '
               'Includes a SKINOFAB travel case.</p>')
META_TITLE = 'The Lymphatic Brush | A 3-minute depuffing massage | SKINOFAB'
META_DESCRIPTION = ('A soft-bristle face brush for the look of morning puffiness around the eyes, cheeks and jaw. Dry skin, '
                    'no oils, 3 minutes. 30-day money-back guarantee. Free shipping.')

# the gallery (brush_assets.py writes brand/lymphatic-brush/<name>.jpg), first one eager
GALLERY = ['hero', 'case', 'how-to-use', 'features', 'vs-tools']
HERO = {'title': ['DEPUFF YOUR', 'MORNING FACE'], 'in': 'IN', 'accent': '3 MINUTES',
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
_LINE = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" '
         'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">')
CHIPS = [
    ('100% dry use, no oils', '<path d="M12 3C8.5 7.5 6.5 10.5 6.5 14a5.5 5.5 0 0 0 11 0C17.5 10.5 15.5 7.5 12 3z"/><path d="M4 4l16 16"/>'),
    ('Takes only 3 minutes', '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5"/><path d="M9 2h6"/>'),
    ('Gentle on delicate skin', '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19c3-3 7-6 10-7"/>'),
    ('Easy to clean', '<path d="M12 3C8.5 7.5 6.5 10.5 6.5 14a5.5 5.5 0 0 0 11 0C17.5 10.5 15.5 7.5 12 3z"/><path d="M9.5 14.5c.4 1.2 1.3 2 2.5 2.2"/>'),
]
# the offer: Solena's three bundles (each a NEXT variant); the free cases and the body brush ship with the order
GIFTS = {'case': ('Premium Case', 'Premium Cases', '9.95'), 'body': ('Body Dry Brush', 'Body Dry Brushes', '24.95')}
BUNDLES = [
    {'key': '1', 'name': 'Buy 1 Brush', 'note': '', 'variant': '1 brush + free case', 'sku': 'SKF-LYB-1',
     'price': '24.95', 'compare': '49.90', 'gifts': [('case', 1)]},
    {'key': '2', 'name': 'Buy 2 Brushes', 'note': '2-Pack', 'variant': '2 brushes + 2 free cases', 'sku': 'SKF-LYB-2',
     'price': '39.95', 'compare': '99.80', 'badge': 'Most popular', 'default': True, 'gifts': [('case', 2)]},
    {'key': '3', 'name': 'Buy 2 Brushes + 1 FREE', 'note': '3-Pack', 'variant': '3 brushes + 3 free cases + free body brush',
     'sku': 'SKF-LYB-3', 'price': '49.90', 'compare': '149.70', 'badge': 'Best offer', 'gifts': [('case', 3), ('body', 1)]},
]
GUARANTEE = '30-Day Money-Back Guarantee'


def _list(items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def tabs():
    """The four tabs under the buy box (the tutorial video has its own section, the 3-minute routine)."""
    return [
        ('How to clean it',
         '<p><strong>Quick clean, before each use (10 seconds)</strong></p>'
         + _list(['Spray a brush cleaner or 70% isopropyl alcohol onto a clean cloth', 'Sweep the bristles across it a few times',
                  'Let it air dry for a minute before using it'])
         + '<p><strong>Deeper clean, once a month</strong></p>'
         + _list(['Swirl only the bristle tips on a damp, soapy cloth', 'Rinse them the same way on a clean, wet cloth',
                  'Dry overnight with the bristles facing down', 'Store it in its case only once fully dry'])
         + '<p><strong>Avoid</strong></p>'
         + _list(['Soaking the brush or holding it under running water', 'Wetting the handle', 'Hot water or a hair dryer'])),
        ('Shipping &amp; Delivery',
         '<p><strong>Processing</strong><br>Orders are carefully packed and shipped within 2–4 business days after you place your order.</p>'
         '<p><strong>Shipping</strong><br>We offer <strong>free shipping</strong> on all orders.</p>'
         '<p><strong>Delivery estimates</strong><br>Worldwide: 5–8 business days once your order has been shipped.</p>'),
        ('Product specifications',
         '<p><strong>Bristles:</strong> Ultra-soft, vegan fibers.</p>'
         '<p><strong>Handle:</strong> Ergonomic premium grip designed for precise control.</p>'
         '<p><strong>Dimensions:</strong> Travel-friendly size. Brush: 3.35" x 2.36" (8 x 6 cm) | Case: 3.54" x 2.56" (9 x 6.5 cm).</p>'
         '<p><strong>Usage:</strong> 100% dry-brushing compatible (No oils required).</p>'
         '<p><strong>Bonus:</strong> Includes a durable, clear travel case for on-the-go convenience.</p>'),
        ('Try it 100% risk-free (Easy Returns)',
         '<p>Take your time to try it at home. If you’re not completely in love with your purchase within <strong>30 days</strong>, '
         'simply send it back for a <strong>full refund</strong> – no hassle, no questions asked.</p>'
         f'<p>Please email us at <a href="mailto:{EMAIL}">{EMAIL}</a> to receive return instructions.</p>'),
    ]


# the sections below ------------------------------------------------------------------------------------------------
# creator clips from the owner's Solena page (silent). Clips 1 ("shaving 10 years off") and 6 ("a sculpted face") make
# promises the brush cannot keep and are left out; the woman in her 50s (clip 3) opens. They are creators, not
# verified buyers, so the heading shows the routine, not "real results".
VIDEOS = {'eyebrow': 'See it in action', 'lead': 'Three minutes,', 'mark': 'every morning', 'clips': [3, 5, 4, 2]}
HOW = {'eyebrow': 'How it works', 'lead': 'Why your face is', 'mark': 'puffy in the morning', 'cards': [
    ('The cause', 'Fluid builds up while you sleep.',
     'When you lie still all night, fluid collects under your eyes, in your cheeks and along your jaw. Salty food, short '
     'nights and age make it leave even slower. <strong>That’s why you wake up with a puffy face.</strong>'),
    ('What helps', 'A light, slow massage.',
     'Facial massage for puffiness uses <strong>light, slow strokes toward the neck</strong>, the way an aesthetician '
     'does it by hand. Pressing hard doesn’t help.'),
    ('Why the brush', 'Soft bristles keep it light.',
     '<strong>Thousands of soft bristles</strong> sweep the skin with every stroke. They bend instead of pressing, so the '
     'touch stays light even if you push. No oil, nothing to learn, just 3 minutes.'),
], 'end_lead': 'A fresher-looking face,', 'end_mark': 'before your coffee.', 'button': 'Choose your bundle'}

# the routine, as on the how-to-use card and the tutorial video
ROUTINE = {'eyebrow': 'How to use it', 'lead': 'Your', 'mark': '3-minute routine',
           'note': 'On clean, dry skin, with a light touch. Repeat each sweep about 10 times, then do the other side.',
           'steps': [('Neck', 'Sweep down from under the ear to the collarbone.'),
                     ('Jaw & cheeks', 'Sweep from your chin along the jaw toward the ear.'),
                     ('Under the eyes', 'Sweep out from the nose to the temples, very lightly.'),
                     ('Neck again', 'Finish with a few sweeps down the neck.')]}

# what to expect, said plainly (women past 45 have heard every promise)
EXPECT = {'eyebrow': 'What to expect', 'lead': 'Honest results,', 'mark': 'no hype',
          'cards': [('After your first 3 minutes', 'Your face feels awake and the morning puffiness around your eyes and jaw can look softer.'),
                    ('Every morning', 'The effect is temporary: puffiness comes back after a night’s sleep, a salty dinner or a short night. That’s why it works best as a daily habit.'),
                    ('What it won’t do', 'It won’t erase wrinkles or reshape your face. It’s a gentle massage, not a treatment. If it isn’t for you, the 30-day guarantee has you covered.')]}

# the foundation, for after (its real rating comes from the imported reviews)
CROSS = {'eyebrow': 'Then, your foundation', 'lead': 'Finish your morning with', 'mark': 'one adaptive shade',
         'text': 'The Adaptive Peptide Foundation goes on white and turns into your skin tone as you blend, with peptides and PDRN, '
                 'made for skin after 45. Brush first, then one pump: done in five minutes.',
         'button': 'See the foundation'}

# the reviews before there are any: say so, and make the guarantee the proof
NO_REVIEWS = {'title': 'Customer reviews', 'lead': 'No reviews yet', 'lead_amazon': 'No SKINOFAB reviews yet',
              'text': 'The Lymphatic Brush is new at SKINOFAB, and we only show reviews from real buyers. Try it for 30 days: '
                      'if you don’t love it, we’ll refund you.',
              'button': 'Try it risk-free', 'write': 'Bought it? Write the first review'}
COPIES = {'eyebrow': 'Watch out for copies', 'title': 'Not all brushes are made the same',
           'ours': 'Our Lymphatic Brush', 'copy': 'Cheap Copy'}
FAQ = {'eyebrow': 'Everything you need to know', 'title': 'Still have questions?', 'items': [
    ('When will I see a difference?',
     'You may see a fresher, less puffy look right after your first 3 minutes. It’s temporary, so it works best every morning. Results vary from person to person.'),
    ('Does it work on mature skin?',
     'Yes. The bristles bend instead of pulling, so they don’t drag thinner skin or fine lines. Keep the touch light, especially under the eyes.'),
    ('Will it scratch or leave red marks?',
     'No. The bristles are ultra-soft and you only need a light touch. If your skin is very reactive, start with a few sweeps and build up.'),
    ('How long does the effect last?',
     'It helps clear the fluid that builds up overnight. Puffiness can come back after another night of sleep, a salty meal or a short night. '
     'That’s why a quick 3-minute routine every morning works best.'),
    ('Do I need oil or serum?', 'No. Use it on clean, dry skin. You can apply your skincare right after.'),
    ('Can I use it before my foundation?',
     'Yes, that’s the best time: brush first on dry skin, then your skincare and foundation.'),
    ('What if it doesn’t work for me?',
     'Send it back within 30 days for a full refund. Just email hello@skinofab.com.'),
    ('Is it safe for sensitive skin?',
     'The bristles are soft and the pressure stays light, so it’s gentle on most skin types. Avoid using it on irritated or broken skin, '
     'sunburn or active breakouts. If your swelling doesn’t go away during the day, or if you have a medical condition, check with your doctor first.'),
    ('How often should I use it?', 'Once a day, in the morning, for about 3 minutes. Twice a day is the maximum.'),
    ('How do I keep it clean?',
     'Give the bristles a quick clean on a cloth with a brush cleaner or alcohol before each use, and a gentle wash of the tips once a month. '
     'Full steps are in the “How to clean it” tab above.'),
]}
# Solena's card adds "★★★★★ +10,000 Happy Customers", which nothing backs: left out until there is a real number (set
# 'proof' to show a line there)
RISK_FREE = {'eyebrow': 'Try it 100% Risk-Free', 'lead': '30-day money-back', 'mark': 'guarantee',
             'proof': None,
             'text': 'Take your time to try it at home. If you’re not completely in love with your purchase within 30 days, simply '
                     'send it back for a full refund, no hassle, no questions asked.',
             'button': 'Choose your bundle'}
STICKY_BUTTON = 'Choose your bundle'

# the cart drawer: 1 brush -> 2 brushes for the price difference
CART_UPGRADE = {'title': 'Upgrade to 2 brushes + 2 free cases', 'button': 'Upgrade'}


def money(v):
    f = float(v)
    return '$%d' % f if f == int(f) else '$%.2f' % f


def esc(s): return html.escape(s, quote=False)


_STAR = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path fill="currentColor" '
         'd="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>')
_CHECK = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="11" fill="currentColor"/>'
          '<path d="m7.5 12.3 3 3 6-6.3" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')
_ARROW = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
          'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>')
_CHEV = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></svg>')

# buy box pieces ----------------------------------------------------------------------------------------------------
BUYBOX_CSS = r"""
.sfb-lead{margin:12px 0 0;font-size:16px;line-height:1.55;color:#3b3b3b}
.sfb-chips{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0}
.sfb-chips span{display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:999px;background:#f6f6f6;font-size:14px;line-height:1.25;color:#151515}
.sfb-chips svg{flex:none}
.sfb-ship{display:inline-block;margin-left:10px;padding:4px 10px;border-radius:999px;background:#151515;color:#fff;font-size:12px;font-weight:600;letter-spacing:.06em;vertical-align:middle;white-space:nowrap}
.sfb-guar{display:flex;align-items:center;justify-content:center;gap:8px;margin:2px 0 0;font-size:15px;font-weight:600;color:#151515}
.sfb-guar svg{color:#151515}
.sfb-tutorial{margin:12px 0 4px;max-width:320px;border-radius:14px;overflow:hidden;background:#000}
.sfb-tutorial video{display:block;width:100%;height:auto;aspect-ratio:9/16}
.sfo--bundle .sfo-main small:empty{display:none}
.sfo--bundle .sfo-gifts{margin-top:12px!important;padding-top:10px!important}
"""


def chips_html():
    return ('<div class="sfb-chips">' + ''.join(f'<span>{_LINE}{svg}</svg>{esc(t)}</span>' for t, svg in CHIPS) + '</div>')


def picker_html(variants, gift_imgs, css):
    """The bundle picker: three cards (Solena's bundles), the middle one chosen. It sets the form's variant and the
    button's price; brush lines are one-time purchases (no refill choice)."""
    table = {b['key']: {'pk': variants[b['key']], 'price': float(b['price']), 'compare': float(b['compare'])} for b in BUNDLES}
    default = next((b['key'] for b in BUNDLES if b.get('default')), BUNDLES[0]['key'])
    base, base_compare = float(BUNDLES[0]['price']), float(BUNDLES[0]['compare'])
    cards = []
    for b in BUNDLES:
        gifts = ''.join(
            f'<li><img src="{gift_imgs[k]}" alt="" width="40" height="40" loading="lazy" decoding="async">'
            f'<span>+ {n} FREE {esc(GIFTS[k][0 if n == 1 else 1])}</span><s>{money(float(GIFTS[k][2]) * n)}</s><b>FREE</b></li>'
            for k, n in b['gifts'])
        cards.append(
            '<label class="sfo-card sfo-card--gifts">'
            + (f'<em class="sfo-tab">{esc(b["badge"])}</em>' if b.get('badge') else '')
            + f'<span class="sfo-row"><input type="radio" name="sf_pack" value="{b["key"]}"{" checked" if b["key"] == default else ""}>'
            f'<span class="sfo-main"><span class="sfo-name">{esc(b["name"])}'
            f'<span class="sfo-save">SAVE {money(float(b["compare"]) - float(b["price"]))}</span></span>'
            f'<small>{esc(b["note"])}</small></span>'
            f'<span class="sfo-price"><b>{money(b["price"])}</b><s>{money(b["compare"])}</s></span></span>'
            f'<ul class="sfo-gifts">{gifts}</ul></label>')
    return (f"""<div class="sfo sfo--bundle" id="apf-buy" data-sf-offer-picker data-packs='{json.dumps(table)}'>
<style>{css}</style>
<fieldset><legend>Choose your bundle</legend>{''.join(cards)}</fieldset>
<script>
(function () {{
  var root = document.currentScript.parentNode;
  var form = root.closest('form');
  var packs = JSON.parse(root.getAttribute('data-packs'));
  function money(v) {{ return '$' + (v % 1 ? v.toFixed(2) : String(v)); }}
  // the title price is the single brush, with cents: the design's money format drops them
  var scope = root, head = null;
  while (scope && !head) {{ scope = scope.parentElement; head = scope && scope.querySelector('.product__price-and-badge'); }}
  function titlePrice() {{
    var now = head && head.querySelector('.product__price--regular'), was = head && head.querySelector('.product__price--compare');
    var unit = now && / USD\\s*$/.test(now.textContent) ? ' USD' : '';
    if (now) now.textContent = money({base}) + unit;
    if (was) was.textContent = money({base_compare}) + unit;
  }}
  function sync() {{
    titlePrice();
    var key = (root.querySelector('input[name=sf_pack]:checked') || {{}}).value || '{default}';
    var pick = packs[key];
    var id = form && form.querySelector('input[name=id]');
    if (id) id.value = pick.pk;
    var price = form && form.querySelector('[data-sfb-btn-price]');
    if (price) price.textContent = ' | ' + money(pick.price);
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
  fromHash();
  sync();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', sync);
  window.addEventListener('load', sync);
}})();
</script>
</div>""")


# sections below the buy box ----------------------------------------------------------------------------------------
SECTIONS_CSS = r"""
.sfb{color:#151515;font-family:inherit}
.sfb *{box-sizing:border-box}
.sfb-sec{padding:72px 0}
.sfb-sec--grey{background:#f6f6f6}
.sfb-wrap{width:min(1180px,calc(100% - 40px));margin:0 auto}
.sfb-head{text-align:center;max-width:760px;margin:0 auto 36px}
.sfb-eyebrow{display:block;font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#6a6a6a;margin:0 0 12px}
.sfb h2{font-size:clamp(28px,3.4vw,42px);line-height:1.15;font-weight:600;letter-spacing:-.01em;margin:0}
.sfb-mark{background:#151515;color:#fff;border-radius:8px;padding:0 .22em;white-space:nowrap;display:inline-block;line-height:1.2;margin-top:.12em}
.sfb-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:16px 34px;border-radius:999px;background:#151515;color:#fff !important;text-decoration:none !important;font-size:14px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;border:0;cursor:pointer}
.sfb-btn:hover{background:#000}
.sfb-btn--light{background:#fff;color:#151515 !important}
.sfb-btn--light:hover{background:#ececec}
.sfb-videos{display:grid;grid-template-columns:repeat(4,minmax(0,260px));justify-content:center;gap:16px;width:min(1180px,calc(100% - 40px));margin:0 auto}
.sfb-video{border-radius:18px;overflow:hidden;background:#e9e9e9;aspect-ratio:9/16;position:relative}
.sfb-video video{width:100%;height:100%;object-fit:cover;display:block}
.sfb-how{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.sfb-how__card{background:#fff;border-radius:20px;overflow:hidden;display:flex;flex-direction:column}
.sfb-how__card img{width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;display:block;background:#f1efec}
.sfb-how__body{padding:22px 24px 26px}
.sfb-how__step{display:flex;align-items:center;gap:10px;font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#6a6a6a;margin:0 0 10px}
.sfb-how__step b{display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:#151515;color:#fff;font-size:13px;letter-spacing:0}
.sfb-how h3{font-size:20px;line-height:1.3;font-weight:600;margin:0 0 10px}
.sfb-how p{font-size:15.5px;line-height:1.55;color:#3b3b3b;margin:0}
.sfb-end{text-align:center;margin:40px 0 0}
.sfb-end p{font-size:clamp(22px,2.4vw,28px);font-weight:600;margin:0 0 18px}
.sfb-end em{font-style:italic}
.sfb-cmp{position:relative;max-width:560px;margin:0 auto;border-radius:20px;overflow:hidden;aspect-ratio:1/1;background:#e9e9e9;touch-action:pan-y;--pos:50%}
.sfb-cmp img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;pointer-events:none;user-select:none}
.sfb-cmp__ours{clip-path:inset(0 calc(100% - var(--pos)) 0 0)}
.sfb-cmp__line{position:absolute;top:0;bottom:0;left:var(--pos);width:2px;margin-left:-1px;background:#fff;pointer-events:none}
.sfb-cmp__line i{position:absolute;top:50%;left:50%;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;background:#fff;color:#151515;display:grid;place-items:center;box-shadow:0 2px 10px rgba(0,0,0,.18)}
.sfb-cmp__tag{position:absolute;top:14px;padding:5px 12px;border-radius:999px;background:#151515;color:#fff;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;pointer-events:none}
.sfb-cmp__tag--ours{left:14px}
.sfb-cmp__tag--copy{right:14px;background:#fff;color:#151515}
.sfb-cmp input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:ew-resize;-webkit-appearance:none;appearance:none}
.sfb-cmp input:focus-visible + .sfb-cmp__line i{outline:2px solid #151515;outline-offset:2px}
.sfb-risk{background:#151515;color:#fff;border-radius:24px;padding:48px 32px;max-width:760px;margin:0 auto;text-align:center}
.sfb-risk .sfb-eyebrow{color:#bdbdbd}
.sfb-risk h2{color:#fff}
.sfb-risk .sfb-mark{background:#fff;color:#151515}
.sfb-risk__proof{display:flex;align-items:center;justify-content:center;gap:8px;margin:18px 0 0;font-size:15px;font-weight:600}
.sfb-risk__proof span{display:inline-flex;gap:2px;color:#fff}
.sfb-risk p{max-width:560px;margin:16px auto 26px;font-size:16px;line-height:1.6;color:#e2e2e2}
.sfb-routine{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:40px;align-items:center;max-width:960px;margin:0 auto}
.sfb-steps{list-style:none;margin:0;padding:0;display:grid;gap:14px}
.sfb-steps li{display:flex;gap:16px;align-items:flex-start;background:#fff;border-radius:16px;padding:18px 20px}
.sfb-steps b{flex:none;display:grid;place-items:center;width:32px;height:32px;border-radius:50%;background:#151515;color:#fff;font-size:15px}
.sfb-steps h3{font-size:17px;font-weight:600;margin:2px 0 4px}
.sfb-steps p{font-size:15px;line-height:1.5;color:#3b3b3b;margin:0}
.sfb-routine__note{font-size:14.5px;color:#6a6a6a;margin:16px 0 0}
.sfb-routine__video{border-radius:18px;overflow:hidden;background:#000;aspect-ratio:9/16}
.sfb-routine__video video{display:block;width:100%;height:100%;object-fit:cover}
.sfb-expect{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.sfb-expect article{background:#fff;border:1px solid #e7e7e7;border-radius:20px;padding:26px 24px}
.sfb-expect h3{font-size:18px;font-weight:600;margin:0 0 10px}
.sfb-expect p{font-size:15.5px;line-height:1.55;color:#3b3b3b;margin:0}
.sfb-expect article:last-child{background:#151515;border-color:#151515}
.sfb-expect article:last-child h3,.sfb-expect article:last-child p{color:#fff}
.sfb-cross{display:grid;grid-template-columns:420px minmax(0,1fr);gap:44px;align-items:center;max-width:1000px;margin:0 auto}
.sfb-cross img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:20px;display:block;background:#f1efec}
.sfb-cross .sfb-eyebrow{text-align:left}
.sfb-cross h2{text-align:left}
.sfb-cross__rating{display:flex;align-items:center;gap:10px;margin:16px 0 0;font-size:15px;font-weight:600}
.sfb-cross__rating span{display:inline-flex;gap:2px}
.sfb-cross__rating i{display:grid;place-items:center;width:22px;height:22px;background:#00b67a;color:#fff;font-style:normal}
.sfb-cross p{font-size:16px;line-height:1.6;color:#3b3b3b;margin:14px 0 22px}
.sfb-cross__price{font-size:18px;font-weight:600;margin:0 0 18px}
.sfb-cross__price s{color:#8a8a8a;font-weight:400;margin-left:8px}
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
@media (max-width:989px){
 .sfb-sec{padding:52px 0}
 .sfb-how{grid-template-columns:1fr}
 .sfb-videos{grid-template-columns:repeat(2,minmax(0,1fr));max-width:560px;gap:12px}
 .sfb-routine{grid-template-columns:1fr;gap:24px}
 .sfb-routine__video{max-width:300px;margin:0 auto;width:100%}
 .sfb-expect{grid-template-columns:1fr}
 .sfb-cross{grid-template-columns:1fr;gap:24px}
 .sfb-cross .sfb-eyebrow,.sfb-cross h2{text-align:center}
 .sfb-cross__rating{justify-content:center}
 .sfb-cross p,.sfb-cross__price{text-align:center}
}
@media (max-width:599px){
 .sfb-wrap{width:calc(100% - 32px)}
 .sfb-videos{width:calc(100% - 32px)}
 .sfb-head{padding:0 16px;margin-bottom:28px}
 .sfb h2{font-size:27px}
 .sfb-cross__rating{flex-wrap:wrap;gap:6px 10px}
 .sfb-risk{padding:36px 20px}
 .sfb-btn{width:100%}
}
"""


def _head(eyebrow, lead, mark=None):
    title = esc(lead) + (f' <span class="sfb-mark">{esc(mark)}</span>' if mark else '')
    return f'<div class="sfb-head"><span class="sfb-eyebrow">{esc(eyebrow)}</span><h2>{title}</h2></div>'


def videos_html(clips):
    """The creator clips (silent), all in view and centered: one row of four on a computer, two by two on a phone.
    Each plays while it is on screen."""
    items = ''.join(f'<div class="sfb-video"><video muted loop playsinline preload="none" poster="{poster}" width="540" height="960" '
                    f'aria-label="Creator video {k}"><source src="{mp4}" type="video/mp4"></video></div>'
                    for k, (mp4, poster) in enumerate(clips, 1))
    return (f'<section class="sfb sfb-sec" aria-label="Creator videos">{_head(VIDEOS["eyebrow"], VIDEOS["lead"], VIDEOS["mark"])}'
            f'<div class="sfb-videos" data-sfb-videos>{items}'
            '<script>(function () {'
            'var root = document.currentScript.parentNode, vids = root.querySelectorAll("video");'
            'if (!("IntersectionObserver" in window)) return;'
            'var io = new IntersectionObserver(function (es) { es.forEach(function (e) {'
            'var v = e.target; if (e.isIntersecting && e.intersectionRatio > 0.5) { if (v.preload !== "auto") v.preload = "auto"; var p = v.play(); if (p && p.catch) p.catch(function () {}); }'
            'else v.pause(); }); }, { threshold: [0, 0.5, 1] });'
            'Array.prototype.forEach.call(vids, function (v) { io.observe(v); });'
            '})();</script></div></section>')


def how_html(images, buy='#apf-buy'):
    cards = ''.join(
        f'<article class="sfb-how__card"><img src="{img}" alt="" width="1264" height="848" loading="lazy" decoding="async">'
        f'<div class="sfb-how__body"><p class="sfb-how__step"><b>{k}</b>{esc(label)}</p><h3>{esc(h)}</h3><p>{p}</p></div></article>'
        for k, ((label, h, p), img) in enumerate(zip(HOW['cards'], images), 1))
    return (f'<section class="sfb sfb-sec sfb-sec--grey" id="sfb-how">{_head(HOW["eyebrow"], HOW["lead"], HOW["mark"])}'
            f'<div class="sfb-wrap"><div class="sfb-how">{cards}</div>'
            f'<div class="sfb-end"><p>{esc(HOW["end_lead"])} <em>{esc(HOW["end_mark"])}</em></p>'
            f'<a class="sfb-btn" href="{buy}">{esc(HOW["button"])} {_ARROW}</a></div></div></section>')


def compare_html(ours, copy):
    grip = _CHEV.format(d='m9 18-6-6 6-6M15 6l6 6-6 6')
    return (f'<section class="sfb sfb-sec">{_head(COPIES["eyebrow"], COPIES["title"])}<div class="sfb-wrap">'
            '<div class="sfb-cmp" data-sfb-cmp>'
            f'<img src="{copy}" alt="{esc(COPIES["copy"])}" width="1000" height="1000" loading="lazy" decoding="async">'
            f'<img class="sfb-cmp__ours" src="{ours}" alt="{esc(COPIES["ours"])}" width="1000" height="1000" loading="lazy" decoding="async">'
            f'<span class="sfb-cmp__tag sfb-cmp__tag--ours">{esc(COPIES["ours"])}</span>'
            f'<span class="sfb-cmp__tag sfb-cmp__tag--copy">{esc(COPIES["copy"])}</span>'
            f'<input type="range" min="0" max="100" value="50" aria-label="Compare {esc(COPIES["ours"])} with a {esc(COPIES["copy"].lower())}">'
            f'<span class="sfb-cmp__line"><i>{grip}</i></span>'
            '<script>(function () {'
            'var root = document.currentScript.parentNode, input = root.querySelector("input");'
            'function set() { root.style.setProperty("--pos", input.value + "%"); }'
            'input.addEventListener("input", set); set();'
            '})();</script></div></div></section>')


def risk_free_html(buy='#apf-buy'):
    stars = ''.join(_STAR for _ in range(5))
    r = RISK_FREE
    return (f'<section class="sfb sfb-sec"><div class="sfb-wrap"><div class="sfb-risk">'
            f'<span class="sfb-eyebrow">{esc(r["eyebrow"])}</span><h2>{esc(r["lead"])} <span class="sfb-mark">{esc(r["mark"])}</span></h2>'
            + (f'<p class="sfb-risk__proof"><span aria-label="5 out of 5 stars">{stars}</span>{esc(r["proof"])}</p>' if r.get('proof') else '') +
            f'<p>{esc(r["text"])}</p><a class="sfb-btn sfb-btn--light" href="{buy}">{esc(r["button"])}</a></div></div></section>')


def routine_html(video, buy='#apf-buy'):
    """The 3-minute routine: four steps (as on the how-to-use card) beside the tutorial video. video: (mp4, poster)."""
    mp4, poster = video
    r = ROUTINE
    steps = ''.join(f'<li><b>{k}</b><div><h3>{esc(h)}</h3><p>{esc(p)}</p></div></li>' for k, (h, p) in enumerate(r['steps'], 1))
    return (f'<section class="sfb sfb-sec sfb-sec--grey" id="sfb-routine">{_head(r["eyebrow"], r["lead"], r["mark"])}'
            f'<div class="sfb-wrap"><div class="sfb-routine"><div><ol class="sfb-steps">{steps}</ol>'
            f'<p class="sfb-routine__note">{esc(r["note"])}</p></div>'
            f'<div class="sfb-routine__video"><video controls playsinline preload="none" poster="{poster}" width="720" height="1280" '
            f'aria-label="How to use the Lymphatic Brush"><source src="{mp4}" type="video/mp4"></video></div></div>'
            f'<div class="sfb-end"><a class="sfb-btn" href="{buy}">{esc(HOW["button"])} {_ARROW}</a></div></div></section>')


def expect_html():
    e = EXPECT
    cards = ''.join(f'<article><h3>{esc(h)}</h3><p>{esc(p)}</p></article>' for h, p in e['cards'])
    return (f'<section class="sfb sfb-sec">{_head(e["eyebrow"], e["lead"], e["mark"])}'
            f'<div class="sfb-wrap"><div class="sfb-expect">{cards}</div></div></section>')


def cross_html(img, href, price, compare, rating=None):
    """The foundation after the brush. rating: (average, count) of its verified reviews, shown in the same green
    boxed stars as its own page."""
    c = CROSS
    stars = ''.join('<i aria-hidden="true">&#9733;</i>' for _ in range(5))
    proof = (f'<p class="sfb-cross__rating"><span role="img" aria-label="Rated {rating[0]:.1f} out of 5">{stars}</span>'
             f'{rating[0]:.1f}/5 from {int(rating[1]):,} verified reviews</p>') if rating else ''
    return (f'<section class="sfb sfb-sec sfb-sec--grey" id="sfb-cross"><div class="sfb-wrap"><div class="sfb-cross">'
            f'<a href="{href}"><img src="{img}" alt="Adaptive Peptide Foundation" width="1080" height="1080" loading="lazy" decoding="async"></a>'
            f'<div><span class="sfb-eyebrow">{esc(c["eyebrow"])}</span><h2>{esc(c["lead"])} <span class="sfb-mark">{esc(c["mark"])}</span></h2>'
            f'{proof}<p>{esc(c["text"])}</p><p class="sfb-cross__price">From {money(price)}<s>{money(compare)}</s></p>'
            f'<a class="sfb-btn" href="{href}">{esc(c["button"])}</a></div></div></div></section>')


def tp_stars(rating):
    """Five Trustpilot-style boxes, the last one filled in part (4.6 fills 60% of the fifth)."""
    boxes = []
    for i in range(5):
        f = max(0.0, min(1.0, rating - i)) * 100
        boxes.append(f'<i aria-hidden="true" style="background:linear-gradient(90deg,#00b67a {f:g}%,#dcdce6 {f:g}%)">&#9733;</i>')
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


def no_reviews_html(buy='#apf-buy', amazon=None):
    """Until the brush has real reviews: an empty Trustpilot-style box that says so, with the guarantee as the proof.
    It hides itself once the store's own reviews of the brush appear (the review wall above then shows them), and
    shows a "Write a review" link when NEXT lets the shopper review the brush."""
    n = NO_REVIEWS
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
SHELF = {'badge': 'New', 'saving': 'Save 50%', 'tags': ['No oils', '3 minutes', 'Less puffy'],
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
