"""Shopify-style one-page checkout body for the Get Rid Of funnel (used by build_checkout.py).

Starts from the NEXT starter family shop-single-step (tools/funnel/getridof/shop-checkout.template.html, copied from
campaign-cart-starter-templates src/shop-single-step/checkout.html): logo header, Contact / Delivery / Payment on the
left, order summary on the right (a "Show order summary" accordion on mobile). Same layout as a native Shopify
checkout, no Shopify branding.

Funnel specifics layered on top:
- the tier picked on the sales page arrives as ?forceBundleId=main:<id>; a hidden bundle selector applies it, so the
  cart always holds the right subscription package (2 / 5 / 6) with no visible picker
- phone required (AppLovin Axon user_data); no top express buttons (they skip validation); PayPal / Apple Pay stay as
  payment options, which do require the phone
- Package Protection bump just before Payment
- under Payment: COMPLETE PURCHASE -> consent line -> payment badges -> Automatic Refills terms (owner's order)
- one short review under the summary
"""
import re
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / 'shop-checkout.template.html'
LOGO = "{{ 'pdp/gro-logo.svg' | campaign_asset }}"
PHONE_ROW = ('<div class="form-group gro-phone"><div class="form-input"><label for="phone" class="label-checkout">Phone</label>'
             '<input autocomplete="tel-full" required data-next-required="true" name="phone" data-name="Phone" type="tel" id="phone" '
             'placeholder="Phone*" data-next-checkout-field="phone" class="input-flds"></div></div>')
HEADER = ('<section class="checkout-header checkout-header--lg gro-shop-header"><div class="container">'
          '<div class="checkout-header__inner checkout-header__inner--center"><div class="checkout-header__brand">'
          f'<img src="{LOGO}" loading="eager" alt="{{{{ campaign.store_name }}}}" class="brand-logo"></div></div></div></section>')
TIER = ('<div class="gro-tier" hidden aria-hidden="true">'
        "{% campaign_include 'bundle-selector.html' selector_id='main' packages=packages shipping_methods=shipping_methods bundles=bundles %}"
        '</div>')
BUMP = "<div class=\"form-section gro-bump\">{% campaign_include 'bump-check01.html' packages=packages %}</div>"
PAY_TAIL = ("{% campaign_include 'submit-block.html' disclaimer=submit_disclaimer %}\n"
            "                          {% campaign_include 'payment-logos.html' payment_flags=payment_flags wrapper_class='gro-pay-badges' %}\n"
            "                          {% if refill_terms %}{% campaign_include 'gro-refill-terms.html' %}{% endif %}\n")


# Which bundle the shopper picked on the sales page, as classes on <html>: gro-b-<id>, plus gro-onetime for a
# one-time purchase (no Automatic Refills terms). No parameter = the default bundle, buy3.
BUNDLE_CLASS = ("<script>(function(){var m=/[?&]forceBundleId=main(?::|%3A)([a-z0-9]+)/i.exec(location.search),b=m?m[1].toLowerCase():'buy3';"
                "if(!/^(buy|ot)[135]$/.test(b))b='buy3';var c=document.documentElement.classList;c.add('gro-b-'+b);if(b.indexOf('ot')===0)c.add('gro-onetime');"
                "window.groBundle=b;})();</script>\n")


def review(r, extra=''):
    t, _, a, _ = r
    return (f'<div class="gro-hrev{extra}" role="note"><p class="gro-hrev__q">{t}</p>'
            f'<p class="gro-hrev__by"><span class="gro-hrev__stars" aria-label="5 out of 5 stars">★★★★★</span> {a} · Verified Buyer</p></div>')


def _once(s, old, new, what):
    assert s.count(old) == 1, f'{what}: found {s.count(old)}'
    return s.replace(old, new, 1)


def body(reviews):
    s = TEMPLATE.read_text().split('---', 2)[2]
    s = s.replace("{{ 'images/next-dark.svg' | campaign_asset }}", LOGO)
    s = _once(s, "{% campaign_include 'checkout-header.html' %}", HEADER, 'header')
    bump = re.search(r'[ \t]*\{% assign bump_variant = order_bump_variant.*?\{% endunless %\}\n', s, re.S)
    assert bump, 'bump block'
    s = s.replace(bump.group(0), '', 1)
    s = _once(s, "{% campaign_include 'express-checkout.html' %}", '', 'express')
    form = '<form data-next-checkout="form" id="combo_form" method="post">'
    s = _once(s, form, form + '\n                      ' + TIER, 'form')
    s = _once(s, '<h1 class="form-section__title">Shipping</h1>', '<h2 class="form-section__title">Delivery</h2>', 'delivery')
    s = _once(s, '<h1 class="form-section__title">Payment</h1>', '<h2 class="form-section__title">Payment</h2>', 'payment title')
    addr = re.search(r'<div data-next-address="shipping"[^>]*></div>', s)
    assert addr, 'address block'
    # the wrapper holds the address block's height: the SDK re-renders the inner element (it collapses for a moment)
    s = s.replace(addr.group(0), '<div class="gro-addr">' + addr.group(0) + '</div>\n                              ' + PHONE_ROW, 1)
    pay = re.search(r'[ \t]*<div class="form-section form-section--last">\s*<div class="form-section__header">\s*<h2 class="form-section__title">Payment</h2>', s)
    assert pay, 'payment section'
    s = s[:pay.start()] + '                          ' + BUMP + '\n' + s[pay.start():]
    sub = re.search(r'[ \t]*<div class="submit-section">.*?</button></div>\n\s*</div>\n', s, re.S)
    assert sub, 'submit section'
    s = s.replace(sub.group(0), '                          ' + PAY_TAIL, 1)
    s = s.replace("Feel safe knowing you're protected. Try it risk-free and return it within 30 days for a full refund or replacement—no questions asked.",
                  "We stand behind our product. 100% refund valid for 30 days. No questions asked.")
    # review: under the summary accordion on mobile, under the order summary on desktop
    mob = re.search(r'<div class="order-summary-mobile">.*?\{% campaign_include \'cart-summary04.html\' %\}\s*</div>\s*</div>\s*</div>', s, re.S)
    assert mob, 'mobile summary'
    s = s.replace(mob.group(0), mob.group(0) + '\n                  ' + review(reviews[0], ' hide-tablet-up'), 1)
    desk = re.search(r"<div class=\"summary-holder\">\s*\{% campaign_include 'cart-summary04.html' %\}\s*</div>\s*</div>", s)
    assert desk, 'desktop summary'
    s = s.replace(desk.group(0), desk.group(0) + '\n                    ' + review(reviews[0]), 1)
    assert 'SPEC_' not in s and 'next-dark.svg' not in s
    return BUNDLE_CLASS + s


CSS = """/* Shopify-style checkout (shop_checkout.py) */
.gro-shop-header .brand-logo{height:34px;width:auto}
.checkout--shop .form-section__title{font-size:21px;font-weight:600}
.gro-phone{margin-top:12px}
.gro-bump{margin-bottom:8px}
.checkout--shop .gro-hrev{max-width:none;margin:16px 0 0}
.checkout__column--right .gro-hrev{background:#fff;border:1px solid #E3E3E3}
"""
