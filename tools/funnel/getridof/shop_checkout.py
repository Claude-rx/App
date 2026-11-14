"""One-page checkout body for the Get Rid Of funnel (used by build_checkout.py).

Starts from the NEXT starter family shop-single-step (tools/funnel/getridof/shop-checkout.template.html, copied from
campaign-cart-starter-templates src/shop-single-step/checkout.html) and lays it out as the owner's reference
(14 Nov 2026): logo + "secure checkout" header, order-summary bar, Early Black Friday box, then four numbered steps
(bundle offer, contact, shipping address, payment method), the order button, and trust / review blocks.

Funnel specifics:
- Step 1 shows three bundle cards. The sales page sends the choice as ?forceBundleId=main:<id>; subscription ids
  buy1/buy3/buy5 (packages 2 / 5 / 6) or one-time ids ot1/ot3/ot5 (package 1). Only the three cards of that mode show.
- phone required (AppLovin Axon user_data); no express buttons above the form (they skip validation); PayPal and
  Apple Pay stay as payment options, which do require the phone
- Package Protection bump just before the payment step
- under the payment step: order button -> consent line -> payment badges -> Automatic Refills terms (owner's order)
- the Early Black Friday countdown runs to the real end date (the same one the sales page shows)
- reviews are the page's existing customer stories; nothing here is invented, and there are no like counts
"""
import json
import re
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / 'shop-checkout.template.html'
LOGO = "{{ 'pdp/gro-logo.svg' | campaign_asset }}"
DEADLINE = '2026-12-01T23:59:00-05:00'   # Black Friday + Cyber Monday pricing ends (owner: "BFCM ends Dec 1, 2026")
PHONE_ROW = ('<div class="form-group gro-phone"><div class="form-input"><label for="phone" class="label-checkout">Phone</label>'
             '<input autocomplete="tel-full" required data-next-required="true" name="phone" data-name="Phone" type="tel" id="phone" '
             'placeholder="Phone*" data-next-checkout-field="phone" class="input-flds"></div></div>')
HEADER = ('<section class="gro-ch"><div class="gro-ch__in">'
          f'<img src="{LOGO}" loading="eager" alt="{{{{ campaign.store_name }}}}" width="150" height="24">'
          '<div class="gro-ch__r"><span class="gro-ch__sec">🔒 Secure checkout</span><span class="gro-ch__ship">🇺🇸 Free US shipping</span></div>'
          '</div></section>')
EBF = ('<div class="gro-ebf"><span class="gro-ebf__i" aria-hidden="true">%</span><div><b>EARLY BLACK FRIDAY IS LIVE!</b>'
       '<span>Items in your cart are in high demand. Up to 74% off. Ends in <strong data-gro-ebf>soon</strong></span></div></div>\n'
       "<script>(function(){var el=document.querySelector('[data-gro-ebf]');if(!el)return;var end=new Date('" + DEADLINE + "').getTime();"
       "function p(n){return(n<10?'0':'')+n}(function t(){var s=Math.floor((end-Date.now())/1e3);if(s<=0){el.parentNode.parentNode.parentNode.style.display='none';return}"
       "var d=Math.floor(s/86400);el.textContent=(d?d+'d ':'')+p(Math.floor(s%86400/3600))+':'+p(Math.floor(s%3600/60))+':'+p(s%60);setTimeout(t,1e3)})()})();</script>")

# id, packs, package, title, first-order price, per pack, % off (campaign 2362; e2e / polish checks fail if these drift)
BUNDLES = [
    ('buy1', 1, 2, 'Buy 1', '22.49', '22.49', 55), ('buy3', 3, 5, 'Buy 2, Get 1 FREE', '47.97', '15.99', 68), ('buy5', 5, 6, 'Buy 3, Get 2 FREE', '64.95', '12.99', 74),
    ('ot1', 1, 1, 'Buy 1', '24.99', '24.99', 50), ('ot3', 3, 1, 'Buy 2, Get 1 FREE', '49.98', '16.66', 67), ('ot5', 5, 1, 'Buy 3, Get 2 FREE', '69.95', '13.99', 72),
]


def bundle_card(i, packs, package, title, price, each, off):
    mode = 'ot' if i.startswith('ot') else 'sub'
    items = json.dumps([{'packageId': package, 'quantity': packs}], separators=(',', ':'))
    head = {3: '<div class="gro-bc__hd"><span>Early Black Friday deal</span><b>★ Most Popular</b></div>',
            5: '<div class="gro-bc__hd gro-bc__hd--v"><span>Whole-home pack</span><b>Best Value</b></div>'}.get(packs, '')
    sel = ' data-next-selected="true"' if i == 'buy3' else ''
    sub = f'{packs} pack{"s" if packs > 1 else ""} · {packs * 12} pouches'
    return (f'<div data-next-bundle-card data-next-bundle-id="{i}" data-next-shipping-id="{{{{ shipping_methods.standard }}}}" '
            f"data-next-bundle-items='{items}'{sel} role=\"button\" class=\"gro-bc gro-bc--{mode} gro-bc--{packs}\">{head}"
            f'<div class="gro-bc__in"><span class="gro-bc__r"></span>'
            f'<img src="{{{{ \'lp/thumb.webp\' | campaign_asset }}}}" alt="" width="56" height="60" loading="eager">'
            f'<div class="gro-bc__t"><b>{title}</b><small>{sub}</small><em>+ FREE US shipping</em></div>'
            f'<div class="gro-bc__p"><span class="gro-bc__off">{off}% OFF</span><s data-next-bundle-display="originalPrice">${packs * 49.99:.2f}</s>'
            f'<b data-next-bundle-display="price">${price}</b><small>${each} per pack</small></div></div></div>')


def step1():
    cards = [bundle_card(*b) for b in BUNDLES]
    up = '<div class="gro-up gro-bc--{m}"><span>Upgrade your order</span></div>'
    body = cards[0] + up.format(m='sub') + cards[1] + cards[2] + cards[3] + up.format(m='ot') + cards[4] + cards[5]
    return ('<div class="form-section gro-s1"><h2 class="form-section__title">Step 1: Choose bundle offer</h2>'
            '<div data-next-catalog-component="bundle-selector" data-next-bundle-selector data-next-selector-id="main" data-next-selection-mode="swap" '
            f'data-next-include-shipping="true" class="gro-bs">{body}</div>'
            '<div class="gro-inc"><p>🎁 <b>EARLY BLACK FRIDAY SPECIAL</b><span>Included with every order today</span></p>'
            '<div class="gro-inc__g"><span><i>FREE</i><u>🚚</u>US shipping</span><span><i>FREE</i><u>↩</u>30-day money-back guarantee</span>'
            '<span><i>FAST</i><u>📦</u>Ships in 1 business day</span></div></div></div>')


# The page's existing customer stories (short forms of the sales page's reviews; avatars are the same files).
COMMENTS = [('robert', 'Robert L.', 'Finally something that keeps them gone - for good. Eleven days later, not a single mouse. Six weeks on, still nothing.'),
            ('tom', 'Tom W.', 'I wasted $200+ on traps. Week two with the pouches: completely silent. Was ready to call an exterminator. Glad I didn\'t.'),
            ('amelia', 'Amelia R.', 'First October in six years I haven\'t had to deal with them. This just works.'),
            ('dave', 'Dave B.', 'We live in our RV full time. Three months in a field in Texas. Not one mouse the entire time.')]
CARDS = [('Gary M.', 'RV owner · Austin, Texas', 'Opened it in spring and not a single mouse. First time in three years.'),
         ('Russel O.', 'RV owner · Duluth, Minnesota', 'This season: completely clean. Not a dropping, not a chew mark. Nothing.'),
         ('Dale T.', 'Farmer · Lancaster, Pennsylvania', 'Six weeks in, the feed room is clean. Dogs are fine. Haven\'t touched a trap since.'),
         ('Thomas E.', 'Farmer · Des Moines, Iowa', 'Set them out in September this year. October came and went. Nothing.'),
         ('Earl H.', 'Farmer · Abilene, Kansas', 'Bins have been clean for four months. Not a single dropping.')]
ICONS = ('<div class="gro-ti"><span><u>🌿</u>Four plant oils, no poison</span><span><u>📦</u>Ships within 1 business day</span><span><u>🛡</u>Up to 90 days per pouch</span></div>')


def social(extra=''):
    com = ''.join(f'<div class="gro-cm"><img src="{{{{ \'lp/av-{s}.webp\' | campaign_asset }}}}" alt="" width="40" height="40" loading="lazy">'
                  f'<div><b>{n}</b><span>{t}</span><small>✓ Verified buyer</small></div></div>' for s, n, t in COMMENTS)
    cards = ''.join(f'<div class="gro-rc"><div class="gro-rc__h"><i>{"".join(w[0] for w in n.replace(".", "").split())}</i><div><b>{n}</b><small>{w}</small></div></div>'
                    f'<div class="gro-rc__s" aria-label="5 out of 5 stars">★★★★★</div><p>{t}</p></div>' for n, w, t in CARDS)
    return (f'<div class="gro-soc{extra}"><h3 class="gro-div"><span>Trusted customer reviews</span></h3>{com}'
            '<h3 class="gro-div"><span>Why choose us</span></h3>'
            '<div class="gro-why"><div><u>🛡</u><p><b>30-Day Money-Back Guarantee</b>If mice haven\'t left in 30 days, we refund your purchase in full.</p></div>'
            '<div><u>🏠</u><p><b>35,129+ Properties Protected</b>Homes, RVs, barns and sheds.</p></div>'
            '<div><u>🔒</u><p><b>Shop With Confidence</b>Your details are encrypted and sent securely over SSL.</p></div></div>'
            '<h3 class="gro-more">More Trusted Customer Reviews</h3>'
            f'<p class="gro-rate"><span>★★★★★</span> 4.8 • Based on 1,668 verified reviews</p>{cards}</div>')


# Which bundle is selected, as classes on <html>: gro-b-<id>, plus gro-onetime for a one-time purchase (no Automatic
# Refills terms, one-time cards shown). Set from the URL before paint, then kept in step with clicks on the cards.
BUNDLE_CLASS = ("<script>(function(){var m=/[?&]forceBundleId=main(?::|%3A)([a-z0-9]+)/i.exec(location.search),b=m?m[1].toLowerCase():'buy3';"
                "if(!/^(buy|ot)[135]$/.test(b))b='buy3';var c=document.documentElement.classList;"
                "function set(b){for(var i=c.length-1;i>=0;i--)if(/^gro-b-/.test(c[i]))c.remove(c[i]);c.add('gro-b-'+b);c.toggle('gro-onetime',b.indexOf('ot')===0);window.groBundle=b}"
                "set(b);document.addEventListener('click',function(e){var k=e.target.closest&&e.target.closest('[data-next-bundle-card]');"
                "if(k&&/^(buy|ot)[135]$/.test(k.getAttribute('data-next-bundle-id')))set(k.getAttribute('data-next-bundle-id'))});})();</script>\n")


def _once(s, old, new, what):
    assert s.count(old) == 1, f'{what}: found {s.count(old)}'
    return s.replace(old, new, 1)


def body(reviews=None):
    s = TEMPLATE.read_text().split('---', 2)[2]
    s = s.replace("{{ 'images/next-dark.svg' | campaign_asset }}", LOGO)
    s = _once(s, "{% campaign_include 'checkout-header.html' %}", HEADER, 'header')
    bump = re.search(r'[ \t]*\{% assign bump_variant = order_bump_variant.*?\{% endunless %\}\n', s, re.S)
    assert bump, 'bump block'
    s = s.replace(bump.group(0), '', 1)
    s = _once(s, "{% campaign_include 'express-checkout.html' %}", '', 'express')
    s = _once(s, '<div class="form-sections">', '<div class="form-sections">\n                          ' + step1(), 'step 1')
    s = _once(s, '<h2 class="form-section__title">Contact</h2>', '<h2 class="form-section__title">Step 2: Contact information</h2>', 'contact title')
    s = _once(s, '<h1 class="form-section__title">Shipping</h1>', '<h2 class="form-section__title">Step 3: Shipping address</h2>', 'delivery')
    s = _once(s, '<h1 class="form-section__title">Payment</h1>', '<h2 class="form-section__title">Step 4: Payment method</h2>', 'payment title')
    chk = re.search(r'<div class="checkbox-wrapper"><label for="accepts_marketing".*?</label></div>', s, re.S)
    assert chk, 'marketing checkbox'
    s = s.replace(chk.group(0), chk.group(0) + '\n                            <p class="gro-ship">🚚 Free US shipping. Ships within 1 business day.</p>', 1)
    addr = re.search(r'<div data-next-address="shipping"[^>]*></div>', s)
    assert addr, 'address block'
    # the wrapper holds the address block's height: the SDK re-renders the inner element (it collapses for a moment)
    s = s.replace(addr.group(0), '<div class="gro-addr">' + addr.group(0) + '</div>\n                              ' + PHONE_ROW, 1)
    pay = re.search(r'[ \t]*<div class="form-section form-section--last">\s*<div class="form-section__header">\s*<h2 class="form-section__title">Step 4: Payment method</h2>', s)
    assert pay, 'payment section'
    s = s[:pay.start()] + "                          <div class=\"form-section gro-bump\">{% campaign_include 'bump-check01.html' packages=packages %}</div>\n" + s[pay.start():]
    sub = re.search(r'[ \t]*<div class="submit-section">.*?</button></div>\n\s*</div>\n', s, re.S)
    assert sub, 'submit section'
    s = s.replace(sub.group(0), "                          {% campaign_include 'submit-block.html' disclaimer=submit_disclaimer subtext='TRY IT RISK-FREE · 30-DAY MONEY-BACK GUARANTEE' %}\n"
                  "                          {% campaign_include 'payment-logos.html' payment_flags=payment_flags wrapper_class='gro-pay-badges' %}\n"
                  "                          {% if refill_terms %}{% campaign_include 'gro-refill-terms.html' %}{% endif %}\n"
                  '                          ' + ICONS + '\n', 1)
    s = s.replace("Feel safe knowing you're protected. Try it risk-free and return it within 30 days for a full refund or replacement—no questions asked.",
                  "We stand behind our product. 100% refund valid for 30 days. No questions asked.")
    # Early Black Friday box under the mobile summary bar; reviews after the form on phones, under the summary on desktop
    mob = re.search(r'<div class="order-summary-mobile">.*?\{% campaign_include \'cart-summary04.html\' %\}\s*</div>\s*</div>\s*</div>', s, re.S)
    assert mob, 'mobile summary'
    s = s.replace(mob.group(0), mob.group(0) + '\n                  ' + EBF, 1)
    s = _once(s, "{% campaign_include 'checkout-footer-links.html' %}", social(' hide-tablet-up') + "\n                  {% campaign_include 'checkout-footer-links.html' %}", 'footer links')
    desk = re.search(r"<div class=\"summary-holder\">\s*\{% campaign_include 'cart-summary04.html' %\}\s*</div>\s*</div>", s)
    assert desk, 'desktop summary'
    s = s.replace(desk.group(0), desk.group(0) + '\n                    ' + social(), 1)
    assert 'SPEC_' not in s and 'next-dark.svg' not in s
    return BUNDLE_CLASS + s


CSS = """/* Checkout layout after the owner's reference (shop_checkout.py) */
.gro-ch{background:#fff;border-bottom:1px solid #e6e8e2}
.gro-ch__in{max-width:1100px;margin:0 auto;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;gap:10px}
.gro-ch__in img{height:24px;width:auto}
.gro-ch__r{display:flex;flex-direction:column;align-items:flex-end;gap:5px}
.gro-ch__sec{font-weight:800;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#1b241d}
.gro-ch__ship{font-size:12px;font-weight:700;border:1.5px solid #1b241d;border-radius:99px;padding:2px 10px;color:#1b241d}
.gro-ebf{display:grid;grid-template-columns:40px 1fr;gap:12px;align-items:center;margin:14px 0 4px;padding:13px 14px;border:1px solid #f1c9cf;background:#fdf1f2;border-radius:10px}
.gro-ebf__i{width:38px;height:38px;border-radius:50%;background:#a3122a;color:#fff;font-weight:800;font-size:18px;display:grid;place-items:center}
.gro-ebf b{display:block;color:#a3122a;font-size:16px;letter-spacing:.01em}
.gro-ebf span{font-size:14px;line-height:1.4;color:#33402f}
.gro-ebf strong{color:#a3122a;font-variant-numeric:tabular-nums}
.checkout--shop .form-section__title{font-size:19px;font-weight:800;text-transform:uppercase;letter-spacing:.03em;color:#1b241d}
.gro-s1{margin-bottom:6px}
.gro-bs{display:grid;gap:12px;margin-top:12px}
.gro-bc{border:1.5px solid #d6dbd0;border-radius:12px;background:#fff;cursor:pointer;overflow:hidden}
.gro-bc__in{display:grid;grid-template-columns:22px 52px 1fr auto;gap:10px;align-items:center;padding:12px 12px}
.gro-bc__r{width:20px;height:20px;border-radius:50%;border:2px solid #9aa596;display:grid;place-items:center}
.gro-bc img{width:52px;height:56px;object-fit:contain}
.gro-bc__t b{display:block;font-size:15.5px;line-height:1.2;color:#1b241d}
.gro-bc__t small{display:block;font-size:12.5px;color:#5b665d}
.gro-bc__t em{display:inline-block;font-style:normal;font-size:11.5px;font-weight:800;background:#fdeeb4;color:#5c4300;border-radius:5px;padding:2px 7px;margin-top:4px}
.gro-bc__p{text-align:right;line-height:1.2}
.gro-bc__off{display:inline-block;background:#c8102e;color:#fff;font-size:11px;font-weight:800;border-radius:99px;padding:2px 8px;margin-bottom:3px}
.gro-bc__p s{display:block;font-size:12.5px;color:#a3122a}
.gro-bc__p b{display:block;font-size:18px;color:#1b241d}
.gro-bc__p small{font-size:11.5px;color:#5b665d}
.gro-bc__hd{display:flex;justify-content:space-between;align-items:center;background:#23372B;color:#fff;font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:7px 12px}
.gro-bc__hd b{color:#ffd24a;text-transform:none;letter-spacing:0;font-size:12.5px}
.gro-bc__hd--v{background:#4F7A2E}
.gro-bc.next-selected{border-color:#23372B;box-shadow:0 0 0 1.5px #23372B;background:#f6faf1}
.gro-bc.next-selected .gro-bc__r{border-color:#23372B}
.gro-bc.next-selected .gro-bc__r::after{content:"";width:10px;height:10px;border-radius:50%;background:#23372B}
.gro-up{display:flex;align-items:center;gap:10px;font-size:12.5px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#1b241d;margin:2px 0}
.gro-up::before,.gro-up::after{content:"";flex:1;height:1px;background:#cfd6c8}
.gro-onetime .gro-bc--sub,html:not(.gro-onetime) .gro-bc--ot{display:none}
.gro-inc{background:#fbf3e4;border-radius:12px;padding:12px 12px 14px;margin-top:12px}
.gro-inc p{margin:0 0 10px;font-size:13.5px;line-height:1.4;color:#1b241d}
.gro-inc p span{display:block;font-weight:700}
.gro-inc__g{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center}
.gro-inc__g span{position:relative;font-size:11.5px;font-weight:700;line-height:1.25;color:#1b241d}
.gro-inc__g u{display:grid;place-items:center;text-decoration:none;height:54px;margin-bottom:5px;border:1px dashed #c9a56a;border-radius:8px;background:#fff;font-size:24px}
.gro-inc__g i{position:absolute;top:-7px;left:50%;transform:translateX(-50%);font-style:normal;background:#c8102e;color:#fff;font-size:9.5px;font-weight:800;border-radius:5px;padding:1px 7px}
.gro-ship{margin:10px 0 0;padding:9px 12px;background:#eaf6e4;border:1px solid #bfe0b0;border-radius:6px;font-size:13.5px;color:#2c5a1c}
.gro-phone{margin-top:12px}
.gro-bump{margin-bottom:8px}
.gro-ti{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:18px 0 6px;text-align:center}
.gro-ti span{font-size:12px;line-height:1.3;color:#1b241d}
.gro-ti u{display:grid;place-items:center;text-decoration:none;width:54px;height:54px;border-radius:50%;background:#1b241d;margin:0 auto 6px;font-size:24px}
.gro-soc{margin-top:22px}
.gro-div{display:flex;align-items:center;gap:12px;margin:22px 0 14px;font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#1b241d}
.gro-div::before,.gro-div::after{content:"";flex:1;height:1px;background:#1b241d}
.gro-cm{display:grid;grid-template-columns:40px 1fr;gap:10px;margin-bottom:14px;align-items:start}
.gro-cm img{width:40px;height:40px;border-radius:50%;object-fit:cover}
.gro-cm div{background:#eef0f3;border-radius:16px;padding:9px 13px;justify-self:start}
.gro-cm b{display:block;font-size:14px;color:#1b241d}
.gro-cm span{display:block;font-size:14.5px;line-height:1.4;color:#1b241d}
.gro-cm small{display:block;margin-top:3px;font-size:11.5px;font-weight:700;color:#2f7d1e}
.gro-why div{display:grid;grid-template-columns:34px 1fr;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid #e1e4dc}
.gro-why div:last-child{border-bottom:0}
.gro-why u{text-decoration:none;font-size:24px;text-align:center}
.gro-why p{margin:0;font-size:13.5px;line-height:1.4;color:#5b665d}
.gro-why b{display:block;font-size:15.5px;color:#1b241d}
.gro-more{margin:18px 0 10px;padding:16px 10px;text-align:center;background:#f6f0e6;border-radius:10px;font-size:18px;font-weight:800;color:#1b241d}
.gro-rate{text-align:center;font-size:14.5px;margin:0 0 12px;color:#1b241d}
.gro-rate span,.gro-rc__s{color:#f5a623;letter-spacing:2px}
.gro-rc{border:1px solid #e1e4dc;border-radius:12px;padding:14px;margin-bottom:10px;background:#fff}
.gro-rc__h{display:grid;grid-template-columns:40px 1fr;gap:10px;align-items:center;margin-bottom:8px}
.gro-rc__h i{width:40px;height:40px;border-radius:50%;background:#fdf1c4;display:grid;place-items:center;font-style:normal;font-weight:800;font-size:14px;color:#1b241d}
.gro-rc__h b{display:block;font-size:15px;color:#1b241d}
.gro-rc__h small{font-size:12px;color:#5b665d}
.gro-rc p{margin:8px 0 0;font-size:14.5px;line-height:1.45;color:#1b241d}
.checkout__column--right .gro-soc{margin-top:8px}
@media (min-width:992px){.gro-ch__in{padding:16px 24px}.gro-ch__in img{height:30px}.gro-ch__r{flex-direction:row;align-items:center;gap:12px}.gro-bc__in{grid-template-columns:22px 56px 1fr auto;padding:14px 16px}.gro-bc__t b{font-size:17px}}
"""
