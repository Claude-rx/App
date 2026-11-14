#!/usr/bin/env python3
"""Builds the Get Rid Of Mouse Pouches checkout (Shopify-style layout from the shop-single-step starter, shop_checkout.py).

    python3 tools/funnel/getridof/build_checkout.py

Writes, under campaigns/getridof/src/mouse-pouches/:
  checkout.html          one-time packs   (package 1)
  (subscription-only funnel: checkout.html is the Automatic Refills checkout, package 2)
  _includes/gro-refill-terms.html, assets/pdp/gro-check.svg
and brands the shared header, receipt, campaigns.json entry and config.js.

Campaign 2362 (Campaigns App, getridof.29next.store): packages 1 One-Time, 2 Auto-Refill, 3 Package Protection;
shipping method 1 (free); offers count 1/3/5 -> $29.99 / $55.98 / $74.95; no exit-intent popup.
The bundle ids buy1/buy3/buy5 are the ones the PDP sends with ?forceBundleId=main:<id>.
Every claim below is the PDP's own copy (90-day guarantee since 14 Nov 2026, the owner's call, 35,129+ properties, the reviews, the benefits).
"""
import json, re, sys
FUNNEL_JS = r'''/* Get Rid Of — funnel step events for the checkout, offer and thank-you pages (build_checkout.py writes this file).
 * Pushes gro_* events to window.dataLayer and, when their tags are on (campaigns.json clarity_id / ga4_id), to Microsoft
 * Clarity and GA4. The sales page sends its own (lp/lp.js). No personal data: field names only, never values. */
(function () {
  'use strict';
  var meta = document.querySelector('meta[name="next-page-type"]');
  var type = (meta && meta.content) || 'page';
  var sent = {};
  window.dataLayer = window.dataLayer || [];
  function track(name, props, once) {
    if (once) { if (sent[name]) return; sent[name] = 1; }
    try {
      var e = { event: 'gro_' + name, gro_page: type, gro_bundle: window.groBundle || '' };
      for (var k in props || {}) e['gro_' + k] = props[k];
      window.dataLayer.push(e);
      if (typeof window.clarity === 'function') window.clarity('event', 'gro_' + name);
      if (typeof window.gtag === 'function') window.gtag('event', 'gro_' + name, props || {});
    } catch (err) { /* never block the page */ }
  }
  window.groTrack = track;
  track(type + '_view', null, true);
  // prices: reveal once the SDK has replaced the placeholder numbers (see gro-checkout.css)
  (function () {
    var root = document.documentElement, els = document.querySelectorAll('[data-next-display^="bundle."][data-next-display$=".price"]');
    if (!els.length) { root.classList.add('gro-prices'); return; }
    var first = []; for (var i = 0; i < els.length; i++) first.push(els[i].textContent);
    var n = 0, iv = setInterval(function () {
      var real = false; for (var j = 0; j < els.length; j++) if (els[j].textContent !== first[j] && /[1-9]/.test(els[j].textContent)) real = true;
      if (real || ++n > 100) { clearInterval(iv); root.classList.add('gro-prices'); if (!real) track('prices_timeout'); }
    }, 100);
  })();
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-next-upsell-action], .submit-button') : null;
    if (!t) return;
    if (t.hasAttribute('data-next-upsell-action')) { track('offer_' + (t.getAttribute('data-next-upsell-action') === 'add' ? 'accept' : 'decline')); return; }
    track('submit_click');
    setTimeout(function () {
      var bad = document.querySelector('.next-error-field');
      if (bad) track('submit_blocked', { field: bad.getAttribute('data-next-checkout-field') || bad.name || bad.id || 'field' });
    }, 700);
  }, true);
  if (type !== 'checkout') return;
  document.addEventListener('focusin', function (e) { if (e.target.matches && e.target.matches('input, select')) track('form_start', null, true); });
  document.addEventListener('change', function (e) {
    var t = e.target; if (!t || !t.matches || !t.matches('input, select')) return;
    if (t.name === 'payment_method') { track('payment_method', { method: t.value }); return; }
    var id = t.getAttribute('data-next-checkout-field') || t.name || t.id;
    if (id && t.value) track('field_' + id.replace(/[^a-z0-9]+/gi, '_').toLowerCase(), null, true);
  }, true);
  // card fields live in iframes: a tap on their wrapper is the signal
  document.addEventListener('pointerdown', function (e) { if (e.target.closest && e.target.closest('[data-next-checkout-field="cc-number"], [data-next-checkout-field="cvv"]')) track('card_field_tap', null, true); }, true);
  // payment errors shown by the SDK
  var errs = document.querySelectorAll('[data-next-component$="-error"]');
  if (errs.length && 'MutationObserver' in window) {
    var mo = new MutationObserver(function () { for (var i = 0; i < errs.length; i++) if (errs[i].offsetParent !== null) { track('payment_error'); break; } });
    for (var i = 0; i < errs.length; i++) mo.observe(errs[i], { attributes: true, childList: true, subtree: true });
  }
})();
'''
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shop_checkout  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
CAMP = ROOT / 'campaigns/getridof/src/mouse-pouches'
STORE = 'https://getridof.shop'   # every visible link goes to the main domain
EMAIL = 'support@getridof.shop'

GALLERY = ['t12-rodent-57d2b1.png', 'image2-829fe1.webp', 'image3-597645.webp', 'image4-ef9455.webp',
           'image5-4e7092.webp', 'image6-7a8fe2.webp', 'image7-6cb854.webp']
REVIEWS = [
    ('“Finally something that keeps them gone - for good.”',
     'Placed pouches under the kitchen sink and along the basement wall. Eleven days later, not a single mouse. '
     'Six weeks on — still nothing. My wife actually feels comfortable in her own kitchen again.',
     'Robert L.', 'Homeowner · Columbus, Ohio'),
    ('“I wasted $200+ on traps, then I found this.”',
     'Pouches behind the fridge, along the garage wall, inside the crawl space. Week two - completely silent. '
     'Was ready to call an exterminator and spend $400. Glad I didn’t.',
     'Tom W.', 'Homeowner · Nashville, Tennessee'),
]
BENEFITS = ['Kid &amp; pet safe', 'No poison, no corpses', 'Works in 3 days', '90 days of protection per pouch']

def yq(s):  # YAML double-quoted scalar
    return json.dumps(s, ensure_ascii=False)

def front(refill):
    pkg = 2 if refill else 1
    name = 'Rodent Repellent Pouches' + (' with Automatic Refills' if refill else '')
    slides = '\n'.join(f'  - src: "pdp/{g}"\n    alt: {yq(name)}' for g in GALLERY)
    thumbs = '\n'.join(f'  - src: "pdp/{g}"\n    alt: ""' for g in GALLERY)
    # each pack lasts a month: the subscription renews by pack count (1 -> 30 days, 3 -> 90, 5 -> 150), $34.99 a pack.
    # One campaign package per schedule: 2 (variant 8), 5 (variant 37), 6 (variant 38).
    SUB_PKG = {1: 2, 3: 5, 5: 6}
    def sub(q):
        if not refill: return ''
        return ' · then $34.99 every 30 days' if q == 1 else f' · then {q} packs (${q * 34.99:.2f}) every {q * 30} days'
    def card(i, q, title, label, selected=False, badge=None):
        s = (f'  - id: "{i}"\n    quantity: {q}\n    shipping_method: "standard"\n'
             + (f'    package_id: {SUB_PKG[q]}\n' if refill else '') +
             f'    title_prefix: {yq(title)}\n    subtitle_text: {yq(label + sub(q))}\n    shipping_label: "+ Free Shipping"\n')
        if badge: s += f'    badge_text: {yq(badge)}\n    badge_pill_class: "os-card__label--pill-primary"\n'
        if selected: s += '    selected: true\n'
        return s
    def once(i, q, title, label):   # one-time purchase: campaign package 1 (offers 1 / 2 / 3 price it by count)
        return (f'  - id: "{i}"\n    quantity: {q}\n    shipping_method: "standard"\n    package_id: 1\n'
                f'    title_prefix: {yq(title)}\n    subtitle_text: {yq(label + " · one-time purchase")}\n    shipping_label: "+ Free Shipping"\n')
    return f'''---
# Generated by tools/funnel/getridof/build_checkout.py from the olympus starter — edit the generator, not this file.
title: {yq("Secure Checkout | Get Rid Of")}
page_type: checkout
promo_banner:
  variant: classic
  text: "BLACK FRIDAY + CYBER MONDAY - UP TO 72% OFF!"
  code_label: ""
  code: ""
  suffix: ""
next_url: receipt.html
cart_summary_variant: "{'02' if refill else '01'}"
order_bump_variant: "check01"
styles:
  - css/gro-checkout.css
scripts:
  - js/checkout.js
  - js/payment-logos.js
swiper_slides:
{slides}
swiper_thumbs:
{thumbs}
packages:
  main_package: {pkg}
  prepurchase_1: 3
order_bump:
  check01:
    package_id: 3
    sync_quantity: false
    is_upsell: false
    title: "Add Package Protection"
    image_src: "pdp/Shipping-Protection-Copy-8b8589.png"
    features:
      - "Covers your order if it is lost, stolen or damaged in transit"
      - "We reship it at no cost"
shipping_methods:
  standard: 1
submit_disclaimer: "By completing your purchase you agree to our Terms of Use and Privacy Policy<span class='gro-sub-only'> and the Automatic Refills terms below</span>."
payment_methods:
  show_klarna: false
  show_google_pay: false
  show_twint: false
  show_affirm: false
  show_bancontact: false
  show_ideal: false
  show_sepa_debit: false
  show_link: false
  show_shop_pay: false
payment_flags:
  secure_text: "100% Encrypted &amp; Secure Checkout"
  show_visa: true
  show_mastercard: true
  show_american_express: true
  show_discover: true
  show_paypal: true
  show_apple_pay: true
bundles:
{card("buy1", 1, "Buy 1", "1x Pack | 12 Pouches")}{card("buy3", 3, "Buy 2, Get 1 Free", "3x Pack | 36 Pouches", True, "Best Seller")}{card("buy5", 5, "Buy 3, Get 2 Free", "5x Pack | 60 Pouches", False, "Best Value")}{once("ot1", 1, "Buy 1", "1x Pack | 12 Pouches")}{once("ot3", 3, "Buy 2, Get 1 Free", "3x Pack | 36 Pouches")}{once("ot5", 5, "Buy 3, Get 2 Free", "5x Pack | 60 Pouches")}refill_terms: {"true" if refill else "false"}
address_form:
  label_style: inset
  gated: false
---
'''

(CAMP / 'checkout-refill.html').unlink(missing_ok=True)   # subscription-only funnel: one checkout
for refill, fn in [(True, 'checkout.html')]:
    (CAMP / fn).write_text(front(refill) + shop_checkout.body(REVIEWS))   # Shopify-style layout (shop_checkout.py)

(CAMP / '_includes/gro-refill-terms.html').write_text(f'''{{% comment %}} Automatic Refills disclosure, under the order button + payment badges on checkout.html (build_checkout.py). {{% endcomment %}}
<div class="gro-refill-terms" role="note">
  <strong>Automatic Refills:</strong> today you pay the price shown above. Each pack lasts about a month, so your refill ships when it runs out:
  <span class="gro-rt gro-rt--buy1"><strong>1 pack every 30 days for $34.99</strong>.</span>
  <span class="gro-rt gro-rt--buy3"><strong>3 packs every 90 days for $104.97</strong> ($34.99 a pack).</span>
  <span class="gro-rt gro-rt--buy5"><strong>5 packs every 150 days for $174.95</strong> ($34.99 a pack).</span>
  Free shipping. Charged to this payment method until you cancel.
  No commitment: cancel anytime from <a href="{STORE}/accounts/subscriptions/" target="_blank">your account</a>
  or by emailing <a href="mailto:{EMAIL}">{EMAIL}</a>. <a href="{STORE}/auto-refill-terms/" target="_blank">Auto-Refill Terms</a>.
</div>
''')
(CAMP / 'assets/pdp').mkdir(parents=True, exist_ok=True)
(CAMP / 'assets/pdp/gro-check.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#CCF46F"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#23372B" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>\n')
(CAMP / 'assets/js/gro-checkout.js').unlink(missing_ok=True)   # held the exit-intent popup, now removed
core = CAMP / 'assets/css/next-core.css'
core.write_text(core.read_text().split('\n/* gro: refill terms */')[0])   # earlier builds appended here
(CAMP / 'assets/css/gro-checkout.css').write_text("""/* Get Rid Of checkout additions (build_checkout.py) */
.gro-refill-terms{margin:12px 0;padding:12px 14px;border:1px solid #7EA254;background:#EEF4E6;border-radius:8px;font-size:13px;line-height:1.45;color:#23372B}
.gro-refill-terms a{color:#23372B;text-decoration:underline}
/* the bundle comes from the sales page (?forceBundleId=main:<id>); shop_checkout.py's head script puts it on <html> */
.gro-rt{display:none}
.gro-b-buy1 .gro-rt--buy1,.gro-b-buy3 .gro-rt--buy3,.gro-b-buy5 .gro-rt--buy5{display:inline}
.gro-onetime .gro-refill-terms,.gro-onetime .gro-sub-only{display:none}
/* no layout jumps while the SDK fills the page: room is held for the address fields and the mobile summary bar */
.gro-addr{min-height:496px}
.order-summary-mobile{min-height:61px}
@media (min-width:992px){.gro-addr{min-height:304px}.order-summary-mobile{min-height:0}}
/* offer pages: product, copy and layout paint at once; only the numbers the SDK fills wait for it */
html:not(.next-display-ready) .upsell-container[data-next-await]::before,
html:not(.next-display-ready) .upsell-container[data-next-await]::after{display:none}
.upsell-container[data-next-await] *{opacity:1}
/* the pages ship placeholder numbers ($0.00, $9.99): nothing the SDK fills is shown until it holds the real value
   (gro-funnel.js adds .gro-prices when the price changes from its placeholder, or after 10 s as a fallback) */
html:not(.gro-prices) [data-next-display^="bundle."]{visibility:hidden}
html:not(.gro-prices) .upsell-container[data-next-await] :is(.badge,button,a):has([data-next-display]){opacity:0}
""" + shop_checkout.CSS + """/* header review under the product line */
.gro-hrev{margin:14px auto 4px;max-width:520px;background:#F1F2EE;border-radius:12px;padding:14px 18px;text-align:left}
.gro-hrev__q{margin:0 0 6px;font-style:italic;font-weight:700;font-size:17px;line-height:1.35;color:#23372B}
.gro-hrev__by{margin:0;font-size:15px;color:#4a4f4a}
.gro-hrev__stars{color:#F2B636;letter-spacing:2px;margin-right:6px}
@media (min-width:992px){.gro-hrev{margin-left:0}}
/* payment step order: button -> consent line -> badges -> refill terms */
.submit-section{display:flex;flex-direction:column}
.submit-section__button{order:1}
.submit-section__disclaimer{order:2;margin-top:8px;font-size:12px;text-align:center}
.gro-pay-badges{margin:14px 0 4px;text-align:center}
.gro-pay-badges .payment-logos{display:flex;flex-wrap:wrap;justify-content:center;gap:6px}
.gro-pay-badges .payment-logos__item{height:26px;width:auto}
/* bundle cards: the deal is the title (package name hidden); the % off is stated on the PDP, not the SDK's 62.67% badge */
[data-next-bundle-card] .os-card__title [data-next-display="package.name"],
[data-next-bundle-card] [data-next-discounts="offer"].os-card__title-badge{display:none!important}
/* brand palette = the packaging: green #7EA254 on deep green #23372B (replaces the starter's blue/navy/teal) */
.promo-banner__bar{background:#23372B!important;color:#fff!important}
.submit-button{background:#2f7d1e!important;border-color:#2f7d1e!important;color:#fff!important;box-shadow:0 4px 0 #1d5211}
.submit-button:hover{background:#256617!important;border-color:#256617!important}
[data-next-bundle-card].next-selected{border-color:#23372B!important}
.os-card__label-2{background:#EEF4E6!important;color:#4F7A2E!important;border-color:#7EA254!important}
.card-icons,.card-icons svg,.card-icons path{color:#4F7A2E!important;border-color:#4F7A2E!important}
.footer_section,.icon-img{color:#23372B;border-color:#23372B}
""")


prog = CAMP / '_includes/checkout-progress.html'
prog.write_text(prog.read_text().replace('<div class="step-label">Bonus Deals</div>', '<div class="step-label">Order Confirmed</div>'))
pr = prog.read_text()
pr = re.sub(r'\s*<div class="line line-inactive arrow-inactive"></div>\s*<div class="step">\s*<div class="step-label">Summary</div>\s*</div>', '', pr)
prog.write_text(pr)

# bundle cards: the starter fallback text "Package Title" (the SDK replaces it with the package name)
bs = CAMP / '_includes/bundle-selector.html'
bs.write_text(bs.read_text().replace('>Package Title</span>', '>Rodent Repellent Pouches</span>'))
# the radio's static data-selected="true" stayed on the first card after the shopper picked another; selection is the SDK's next-selected class
bs.write_text(bs.read_text().replace('<div{% if b.selected %} data-selected="true"{% endif %} class="radio-style-1">', '<div class="radio-style-1">'))

# shared header and receipt branding
hdr = CAMP / '_includes/checkout-header.html'
h = hdr.read_text()
h = h.replace("{{ 'images/next-dark.svg' | campaign_asset }}", "{{ 'pdp/gro-logo.svg' | campaign_asset }}")
h = re.sub(r'<img loading="lazy" src="\{\{ \'images/90d.webp\' \| campaign_asset \}\}" alt="" class="mg-image">\s*', '', h)
h = h.replace('90 - Day 100%<br>Money Back Guarantee', '90-Day 100%<br>Money Back Guarantee').replace('30-Day 100%<br>Money Back Guarantee', '90-Day 100%<br>Money Back Guarantee')
h = re.sub(r'Questions\?<br>Call: <a href="\{\{ campaign\.store_phone_tel \}\}" class="link-tel">\{\{ campaign\.store_phone \}\}</a>',
           'Questions?<br>Email: <a href="mailto:{{ campaign.store_email }}" class="link-tel">{{ campaign.store_email }}</a>', h)
hdr.write_text(h)
rc = CAMP / 'receipt.html'
r = rc.read_text().replace('title: "Olympus — Receipt"', 'title: "Thank You | Get Rid Of"').replace("{{ 'images/next-dark.svg' | campaign_asset }}", "{{ 'pdp/gro-logo.svg' | campaign_asset }}")
rc.write_text(r)
# the thank-you page's loading skeleton showed the starter's logo until the order loaded
sk = CAMP / '_includes/receipt-skeleton.html'
sk.write_text(sk.read_text().replace("{{ 'images/next-dark.svg' | campaign_asset }}", "{{ 'pdp/gro-logo.svg' | campaign_asset }}"))

# campaigns.json and config.js
data_f = ROOT / 'campaigns/getridof/_data/campaigns.json'
data = json.loads(data_f.read_text())
data['mouse-pouches'].update({
    'name': 'Get Rid Of Mouse Repellent Pouches', 'description': 'Get Rid Of Rodent Repellent Pouches: natural 4-oil formula, mice gone in 72 hours, 90 days per pouch.',
    'entry_url': '', 'store_name': 'Get Rid Of', 'store_url': STORE, 'store_terms': f'{STORE}/terms/', 'store_privacy': f'{STORE}/privacy/',
    'store_contact': f'{STORE}/contact/', 'store_returns': f'{STORE}/refund-policy/', 'store_shipping': f'{STORE}/shipping-policy/',
    'store_email': EMAIL, 'store_phone': '', 'store_phone_tel': '', 'gtm_id': '', 'fb_pixel_id': '', 'og_image': '',
    # AppLovin Axon (Route C): every page. 7137 = Home & Garden > Household Supplies > Pest Control > Repellents >
    # Animal & Pet Repellents (pouches, variants 7/8); 728 = Pest Control (Copper Seal Kit, variant 17). Keys are the
    # SDK's item_id (SKU) or item_variant_id. user_data on: email/phone/
    # user_id/phone_last10_hashed (AppLovin's pixel hashes email/phone in the browser).
    'axon_event_key': 'b4bc9878-3e1d-43fc-94de-d53f78913b7c', 'axon_item_category_id': '7137',
    'axon_category_by_package': 'cdkh:7137,7:7137,8:7137,37:7137,38:7137,GRO-COPPER:728,17:728', 'axon_send_user_data': 'true', 'axon_allowed_events': 'all',
    'axon_image_url': 'https://cdn.cachebucket.com/media/getridof/themes/11/assets/gro-new-pack.png'})
# Session recordings / heatmaps (Microsoft Clarity) and GA4: off while the id is empty. Set them here in campaigns.json.
data['mouse-pouches'].setdefault('clarity_id', '')
data['mouse-pouches'].setdefault('ga4_id', '')
data_f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
cfg = CAMP / 'assets/config.js'
c = cfg.read_text()
if 'storeName' in c:
    c = re.sub(r"storeName:\s*(['\"])[^'\"]*\1", "storeName: 'getridof'", c)
c = c.replace("requiredFields: ['email', 'fname', 'lname']", "requiredFields: ['email', 'fname', 'lname', 'phone']")   # GRO: phone before PayPal / Apple Pay too
cfg.write_text(c)
# funnel step events on every checkout / offer / thank-you page, and the Clarity tag when campaigns.json has a clarity_id
(CAMP / 'assets/js/gro-funnel.js').write_text(FUNNEL_JS)
CLARITY = ('    {% if campaign.clarity_id and campaign.clarity_id != "" %}<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};'
           't=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y)})'
           '(window,document,"clarity","script","{{ campaign.clarity_id }}");</script>{% endif %}\n')
base = CAMP / '_layouts/base.html'
bl = base.read_text()
if 'clarity.ms/tag' not in bl:
    anchor = "    {% campaign_include 'analytics-head.html' %}\n"
    assert bl.count(anchor) == 1
    bl = bl.replace(anchor, anchor + CLARITY)
if 'gro: offer photo first' not in bl:
    anchor = '    <link rel="dns-prefetch" href="//i18n-rules.nextcommerce.com">\n'
    assert bl.count(anchor) == 1
    bl = bl.replace(anchor, anchor + '    {% comment %} gro: offer photo first {% endcomment %}{% if upsell_offer.image %}<link rel="preload" as="image" href="{{ upsell_offer.image | campaign_asset }}" fetchpriority="high">{% endif %}\n')
if 'js/gro-funnel.js' not in bl:
    anchor = "    {% for script in scripts %}\n"
    assert bl.count(anchor) == 1
    bl = bl.replace(anchor, "    <script defer src=\"{{ 'js/gro-funnel.js' | campaign_asset }}\"></script>\n" + anchor)
base.write_text(bl)
print('wrote checkout.html (subscription), refill terms, header, receipt, campaigns.json')

# ---- post-purchase offers: upsell -> downsell -> upsell-2 -> downsell-2 (see build_offers.py) ----
import subprocess, sys
subprocess.run([sys.executable, str(ROOT / 'tools/funnel/getridof/build_offers.py')], check=True)
