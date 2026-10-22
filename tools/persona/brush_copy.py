"""The Lymphatic Brush: product page copy, offer and sections, from the owner's Solena page
(https://thesolena.com/products/the-lymphatic-brush), under the SKINOFAB name and in the SKINOFAB look.

The words are Solena's own, kept as written; only the brand name and the contact address change. The page follows
Solena's order: gallery and buy box (buyers, rating, bundle picker, guarantee, three short reviews, five tabs), the
review videos, how it works, the copy comparison, the FAQ, the guarantee and the customer reviews.

Read by apply_persona.py (it builds products/the-lymphatic-brush.html from the foundation page's markup) and by
setup_brush_offers.py (the NEXT product, its three bundles and their prices).
"""
import html, json

HANDLE = 'the-lymphatic-brush'
TITLE = 'The Lymphatic Brush'
SHOPIFY_ID, SHOPIFY_VARIANT = 15517563191626, 61233683038538       # Solena's ids (the design markup carries them)
PRICE, COMPARE = '24.95', '49.90'
EMAIL = 'hey@skinofab.com'
DESCRIPTION = ('<p>Depuff your face in 3 minutes. Thousands of ultra-soft bristles sweep the fluid that builds up overnight '
               'from under your eyes, your cheeks and your jaw toward your neck, with a light touch and no oil. Use it on '
               'clean, dry skin every morning. Includes a clear travel case.</p>')
META_TITLE = 'The Lymphatic Brush | Depuff your face in 3 minutes | SKINOFAB'
META_DESCRIPTION = ('Soft bristles drain fluid out of your face: less puffy eyes, cheeks and jaw from the first use. '
                    '100% dry use, no oils, 3 minutes. 30-day money-back guarantee. Free shipping.')

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
BUYERS = {'name': 'Nicole', 'text': 'and 5,000+ others purchased'}
SHIPPING_BADGE = '\U0001F381 FREE SHIPPING'
_LINE = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" '
         'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">')
CHIPS = [
    ('100% dry use, no oils', '<path d="M12 3C8.5 7.5 6.5 10.5 6.5 14a5.5 5.5 0 0 0 11 0C17.5 10.5 15.5 7.5 12 3z"/><path d="M4 4l16 16"/>'),
    ('Takes only 3 minutes', '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5"/><path d="M9 2h6"/>'),
    ('Gentle on delicate skin', '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19c3-3 7-6 10-7"/>'),
    ('Easy to clean', '<path d="M12 3C8.5 7.5 6.5 10.5 6.5 14a5.5 5.5 0 0 0 11 0C17.5 10.5 15.5 7.5 12 3z"/><path d="M9.5 14.5c.4 1.2 1.3 2 2.5 2.2"/>'),
]
# the offer: Solena's three bundles (each a NEXT variant); the free cases and the body brush ship with the order
GIFTS = {'case': ('Premium Case', 'Premium Cases', '9.95'), 'body': ('Anti-Cellulite Dry Brush', 'Anti-Cellulite Dry Brushes', '24.95')}
BUNDLES = [
    {'key': '1', 'name': 'Buy 1 Brush', 'note': '', 'variant': '1 brush + free case', 'sku': 'SKF-LYB-1',
     'price': '24.95', 'compare': '49.90', 'gifts': [('case', 1)]},
    {'key': '2', 'name': 'Buy 2 Brushes', 'note': '2-Pack', 'variant': '2 brushes + 2 free cases', 'sku': 'SKF-LYB-2',
     'price': '39.95', 'compare': '99.80', 'badge': 'Most popular', 'default': True, 'gifts': [('case', 2)]},
    {'key': '3', 'name': 'Buy 2 Brushes + 1 FREE', 'note': '3-Pack', 'variant': '3 brushes + 3 free cases + free body brush',
     'sku': 'SKF-LYB-3', 'price': '49.90', 'compare': '149.70', 'badge': 'Best offer', 'gifts': [('case', 3), ('body', 1)]},
]
GUARANTEE = '30-Day Money-Back Guarantee'
MINI_REVIEWS = [
    ('Jessica H.', 'I was embarrassed to go to work with a puffy face. Now the puffiness is down before I leave the house.'),
    ('Emily C.', 'I could actually see the difference right away, my face looked less swollen and more awake.'),
    ('Erika N.', 'So soft, so easy and actually relaxing. I use it every morning now because it takes almost no effort.'),
]


def _list(items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def tabs(video):
    """The five tabs under the buy box. video: (mp4 path, poster path)."""
    mp4, poster = video
    return [
        ('Video Tutorial',
         '<p><em>Use on clean, dry skin. Give the bristles a quick clean before each use and let them dry for a minute.</em></p>'
         '<p>First time using a Lymphatic Brush from SKINOFAB? This quick video shows the exact steps:</p>'
         f'<div class="sfb-tutorial"><video controls playsinline preload="none" poster="{poster}" width="720" height="1280">'
         f'<source src="{mp4}" type="video/mp4"></video></div>'),
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
VIDEOS = {'eyebrow': 'They love our lymphatic brush', 'lead': 'Real people,', 'mark': 'real results'}
HOW = {'eyebrow': 'How it works', 'lead': 'Why your face is', 'mark': 'puffy in the morning', 'cards': [
    ('The cause', 'Fluid builds up while you sleep.',
     'When you lie still all night, fluid collects under your eyes, in your cheeks and along your jaw. Salty food, short '
     'nights and age make it leave even slower. <strong>That’s why you wake up with a puffy face.</strong>'),
    ('What clears it', 'It needs a light touch.',
     'The tiny channels that clear this fluid sit <strong>just under your skin</strong>. They work best with slow, gentle '
     'strokes toward your neck. Pressing hard doesn’t help.'),
    ('Why the brush', 'Soft bristles do it for you.',
     '<strong>Thousands of soft bristles</strong> move the fluid with every stroke. They bend instead of pressing, so the '
     'touch stays light even if you push. No oil, nothing to learn, just 3 minutes.'),
], 'end_lead': 'Less puffy from the', 'end_mark': 'first use.', 'button': 'Choose your bundle'}
COPIES = {'eyebrow': 'Watch out for copies', 'title': 'Not all brushes are made the same',
           'ours': 'Our Lymphatic Brush', 'copy': 'Cheap Copy'}
FAQ = {'eyebrow': 'Everything you need to know', 'title': 'Still have questions?', 'items': [
    ('When will I see a difference?',
     'Most people notice their face looks less puffy right after the first use. For the best results, use it every morning as part of your routine.'),
    ('How long does the effect last?',
     'It helps clear the fluid that builds up overnight. Puffiness can come back after another night of sleep, a salty meal or a short night. '
     'That’s why a quick 3-minute routine every morning works best.'),
    ('Where does the fluid go?',
     'Gentle strokes guide fluid toward the lymph nodes in your neck, and your body takes care of the rest naturally.'),
    ('Do I need oil or serum?', 'No. Use it on clean, dry skin. You can apply your skincare right after.'),
    ('Is it safe for sensitive skin?',
     'The bristles are soft and the pressure stays light, so it’s gentle on most skin types. Avoid using it on irritated or broken skin, '
     'sunburn or active breakouts. If your swelling doesn’t go away during the day, or if you have a medical condition, check with your doctor first.'),
    ('How often should I use it?', 'Once a day, in the morning, for about 3 minutes. Twice a day is the maximum.'),
    ('How do I keep it clean?',
     'Give the bristles a quick clean on a cloth with a brush cleaner or alcohol before each use, and a gentle wash of the tips once a month. '
     'Full steps are in the “How to clean it” tab above.'),
]}
# Solena's card adds "★★★★★ +10,000 Happy Customers", which the same page contradicts ("5,000+ others purchased")
# and no review backs: left out until the owner gives the real number (set 'proof' to show a line there)
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
_HEART = ('<svg viewBox="1.6 4 20.2 18" width="12" height="12" aria-hidden="true" focusable="false"><path fill="currentColor" '
          'd="M12 21s-7.5-4.6-9.6-9.2C1 8.6 3 5 6.6 5c2.1 0 3.6 1.2 4.4 2.5C11.8 6.2 13.3 5 15.4 5 19 5 21 8.6 19.6 11.8 17.5 16.4 12 21 12 21z"/></svg>')
_ARROW = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
          'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>')
_CHEV = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></svg>')

# buy box pieces ----------------------------------------------------------------------------------------------------
BUYBOX_CSS = r"""
.sfb-chips{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0}
.sfb-chips span{display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:999px;background:#f6f6f6;font-size:14px;line-height:1.25;color:#151515}
.sfb-chips svg{flex:none}
.sfb-ship{display:inline-block;margin-left:10px;padding:4px 10px;border-radius:999px;background:#151515;color:#fff;font-size:12px;font-weight:600;letter-spacing:.06em;vertical-align:middle;white-space:nowrap}
.sfb-guar{display:flex;align-items:center;justify-content:center;gap:8px;margin:2px 0 0;font-size:15px;font-weight:600;color:#151515}
.sfb-guar svg{color:#151515}
.sfb-minis{position:relative;margin:4px 0 0}
.sfb-minis__track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;gap:12px}
.sfb-minis__track::-webkit-scrollbar{display:none}
.sfb-mini{flex:0 0 100%;scroll-snap-align:start;display:flex;gap:14px;align-items:center;padding:14px 16px;border-radius:14px;background:#f6f6f6}
.sfb-mini__av{position:relative;flex:none;width:52px;height:52px}
.sfb-mini__av img{width:52px;height:52px;border-radius:50%;object-fit:cover;display:block}
.sfb-mini__av i{position:absolute;right:-2px;bottom:-2px;width:20px;height:20px;border-radius:50%;background:#151515;color:#fff;display:grid;place-items:center;border:2px solid #f6f6f6}
.sfb-mini__top{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:600}
.sfb-mini__top span{color:#151515;letter-spacing:1px;font-size:13px}
.sfb-mini p{margin:4px 0 0;font-size:14px;line-height:1.45;color:#3b3b3b}
.sfb-minis__dots{display:flex;justify-content:center;gap:6px;margin-top:10px}
.sfb-minis__dots button{width:6px;height:6px;padding:0;border:0;border-radius:99px;background:#d4d4d4;cursor:pointer;transition:width .2s,background .2s}
.sfb-minis__dots button[aria-current=true]{width:18px;background:#151515}
.sfb-tutorial{margin:12px 0 4px;max-width:320px;border-radius:14px;overflow:hidden;background:#000}
.sfb-tutorial video{display:block;width:100%;height:auto;aspect-ratio:9/16}
.sfo--bundle .sfo-main small:empty{display:none}
.sfo--bundle .sfo-gifts{margin-top:12px!important;padding-top:10px!important}
"""


def chips_html():
    return ('<div class="sfb-chips">' + ''.join(f'<span>{_LINE}{svg}</svg>{esc(t)}</span>' for t, svg in CHIPS) + '</div>')


def minis_html(avatars):
    slides = ''.join(
        f'<div class="sfb-mini"><span class="sfb-mini__av"><img src="{a}" alt="{esc(n)}" width="52" height="52" loading="lazy" decoding="async">'
        f'<i>{_HEART}</i></span><div><div class="sfb-mini__top">{esc(n)}<span aria-label="5 out of 5 stars">★★★★★</span></div>'
        f'<p>{esc(t)}</p></div></div>' for (n, t), a in zip(MINI_REVIEWS, avatars))
    dots = ''.join(f'<button type="button" aria-label="Review {k + 1}"{" aria-current=true" if k == 0 else ""}></button>'
                   for k in range(len(MINI_REVIEWS)))
    return (f'<div class="sfb-minis" data-sfb-minis><div class="sfb-minis__track">{slides}</div>'
            f'<div class="sfb-minis__dots">{dots}</div>'
            '<script>(function () {'
            'var root = document.currentScript.parentNode, track = root.querySelector(".sfb-minis__track");'
            'var dots = root.querySelectorAll(".sfb-minis__dots button"), n = dots.length, at = 0, timer = null;'
            'function go(i) { at = (i + n) % n; track.scrollTo({ left: track.clientWidth * at, behavior: "smooth" }); }'
            'track.addEventListener("scroll", function () {'
            'var i = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));'
            'Array.prototype.forEach.call(dots, function (d, k) { d.setAttribute("aria-current", k === i ? "true" : "false"); }); at = i; }, { passive: true });'
            'Array.prototype.forEach.call(dots, function (d, k) { d.addEventListener("click", function () { go(k); restart(); }); });'
            'function restart() { if (timer) clearInterval(timer); timer = setInterval(function () { go(at + 1); }, 5000); }'
            'root.addEventListener("pointerenter", function () { if (timer) clearInterval(timer); });'
            'root.addEventListener("pointerleave", restart);'
            'restart();'
            '})();</script></div>')


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
.sfb-videos{position:relative}
.sfb-videos__track{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:4px calc(50% - 150px) 8px}
.sfb-videos__track::-webkit-scrollbar{display:none}
.sfb-video{flex:0 0 300px;scroll-snap-align:center;border-radius:18px;overflow:hidden;background:#e9e9e9;aspect-ratio:9/16;position:relative}
.sfb-video video{width:100%;height:100%;object-fit:cover;display:block}
.sfb-videos__nav{position:absolute;top:50%;transform:translateY(-50%);width:44px;height:44px;border-radius:50%;border:0;background:#151515;color:#fff;display:grid;place-items:center;cursor:pointer;z-index:2}
.sfb-videos__nav--prev{left:max(8px,calc(50% - 560px))}
.sfb-videos__nav--next{right:max(8px,calc(50% - 560px))}
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
@media (max-width:989px){
 .sfb-sec{padding:52px 0}
 .sfb-how{grid-template-columns:1fr}
 .sfb-videos__nav{display:none}
}
@media (max-width:599px){
 .sfb-wrap{width:calc(100% - 32px)}
 .sfb-video{flex-basis:240px}
 .sfb-videos__track{padding:4px calc(50% - 120px) 8px}
 .sfb-risk{padding:36px 20px}
 .sfb-btn{width:100%}
}
"""


def _head(eyebrow, lead, mark=None):
    title = esc(lead) + (f' <span class="sfb-mark">{esc(mark)}</span>' if mark else '')
    return f'<div class="sfb-head"><span class="sfb-eyebrow">{esc(eyebrow)}</span><h2>{title}</h2></div>'


def videos_html(clips):
    """The review clips (silent): a centered strip, each clip plays while it is on screen."""
    items = ''.join(f'<div class="sfb-video"><video muted loop playsinline preload="none" poster="{poster}" width="540" height="960" '
                    f'aria-label="Customer video {k}"><source src="{mp4}" type="video/mp4"></video></div>'
                    for k, (mp4, poster) in enumerate(clips, 1))
    prev, nxt = _CHEV.format(d='m15 18-6-6 6-6'), _CHEV.format(d='m9 18 6-6-6-6')
    return (f'<section class="sfb sfb-sec" aria-label="Customer videos">{_head(VIDEOS["eyebrow"], VIDEOS["lead"], VIDEOS["mark"])}'
            f'<div class="sfb-videos" data-sfb-videos><button type="button" class="sfb-videos__nav sfb-videos__nav--prev" aria-label="Previous video">{prev}</button>'
            f'<div class="sfb-videos__track">{items}</div>'
            f'<button type="button" class="sfb-videos__nav sfb-videos__nav--next" aria-label="Next video">{nxt}</button>'
            '<script>(function () {'
            'var root = document.currentScript.parentNode, track = root.querySelector(".sfb-videos__track");'
            'var vids = root.querySelectorAll("video");'
            'function step(d) { var w = vids[0] ? vids[0].parentNode.getBoundingClientRect().width + 16 : 300; track.scrollBy({ left: d * w, behavior: "smooth" }); }'
            'root.querySelector(".sfb-videos__nav--prev").addEventListener("click", function () { step(-1); });'
            'root.querySelector(".sfb-videos__nav--next").addEventListener("click", function () { step(1); });'
            'if (!("IntersectionObserver" in window)) return;'
            'var io = new IntersectionObserver(function (es) { es.forEach(function (e) {'
            'var v = e.target; if (e.isIntersecting && e.intersectionRatio > 0.6) { if (v.preload !== "auto") v.preload = "auto"; var p = v.play(); if (p && p.catch) p.catch(function () {}); }'
            'else v.pause(); }); }, { threshold: [0, 0.6, 1] });'
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
