"""The Adaptive Peptide Foundation funnel's five offer pages, as Campaign Page Kit pages, from one place.

usage: python3 -I tools/funnel/apf/offer_pages.py

Writes campaigns/skinofab/src/apf-funnel/{foundation-offer-1,foundation-offer-2,foundation-offer-2b,lymphatic-brush-offer,
lymphatic-brush-offer-b}.html (generated: edit this file, then run it). The packages, vouchers and routes come from
funnels/apf.py and the CampaignSpec (campaign_spec.py's live read, campaign-spec.apf.json); every price a page states is
the campaign's (check_apf.py holds them to it). Every package is bought once: each page says, by its button, that the
price is charged once to the payment she just used and nothing renews.

v2 (the owner's brief): every offer is "just for you, now": the hero (_includes/sf-upsell-hero.html) is the page's H1,
one line on the offer, "Reserved for you, <her first name>" and an honest countdown (js/sf-offer-timer.js: the deadline
is set once per order and page, survives a reload, and at 0:00 the page declines the offer itself and moves on, which
the hero says under the clock). The foundation offers are short (she knows the product): the offer, three reasons, the
closing card. Only the brush gets a product page, and its loop plays above the fold.

- offer 1 (foundation-offer-1): the supply cards (_includes/sf-supply-cards.html): two bottles for the price of one
  ("Add 1, get 1 FREE": $39 for two, one bottle being $39) and six bottles at $16.50 each with the Lymphatic Brush;
  each card is its own package at its own price, no voucher, and each card's Buy now is the offer's own add action
  (js/sf-supply.js selects the card first; the closing card's picture follows the selected card). Accept goes to the
  brush offer, decline to offer 2.
- offer 2 / its downsell: one more bottle with APF40 (40% off, $23) or APF50 (50% off, $19): Apollo's single-offer
  upsell with the voucher on a hidden selector (as the stick funnel's), three photos, the bullets, the terms, three
  reasons, the closing card.
- offer 3 / its downsell: the Lymphatic Brush with BRUSH40 ($14) or BRUSH60 ($9): the offer with the brush's loop (its
  four sweeps and the case) playing in the media column, then the brush's short product page
  (_includes/sf-brush-pdp.html: the problem with an illustration of the look it is for, the solution, how to use it,
  versus stones and rollers, the box, the questions; the brush's own store copy: a light, dry massage for the look of
  morning puffiness), the closing card. An order that already has a brush in it (the 3-bottle pack, the 6-bottle pack)
  skips both to the thank-you page (js/sf-offer-gate.js, data-sf-skip-skus).
The percentages shown are the SDK's ({discount}), once per page: the campaign rounds a voucher's price down to the
dollar, so 40% off $39 is $23 (41%) and 40% off $24.95 is $14 (44%); the page shows what she pays, never a rounder
number, and no fixed percentage beside the SDK's.
"""
import json, os, sys
from pathlib import Path

os.environ['FUNNEL'] = 'apf'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import funnel as F

ROOT = HERE.parents[2]
SRC = ROOT / 'campaigns' / 'skinofab' / 'src' / F.SLUG
SPEC = ROOT / 'campaigns' / 'skinofab' / F.SPEC_FILE
EMAIL = F.EMAIL
ALLERGY = 'Contains salmon-derived PDRN: not for anyone with a fish allergy.'
ONCE = 'charged once to the payment you just used. Nothing renews, and it ships in the same box.'
GUARANTEE = 'Backed by our 30-day money-back guarantee.'
# the honest countdown: 10 minutes on an offer, 5 on a last chance; at 0:00 the page declines the offer itself
TIMER, TIMER_LAST = 600, 300
EXPIRES = 'When the clock reaches 0:00 this page moves on and this price is gone: you won’t find it in our store or in an email.'


def q(s):
    return json.dumps(s, ensure_ascii=False)


def money(v):
    return f'${v:,.2f}'


def steps(*rows):
    return [{'title': t, 'text': x} for t, x in rows]


# the brush's short product page under its offer (its store copy, tools/persona/brush_copy.py, in the page's own words)
BRUSH_PDP = {
    'problem': {'image': 'images/sf/brush-ba-puffy.jpg', 'alt': 'Illustration: the same woman in her fifties, puffy-looking under the eyes and along the jaw on the left, a fresher-looking morning face on the right',
                'caption': 'Illustration of the look it is for, not a customer photo. Results vary.',
                'eyebrow': 'The problem', 'title': 'You wake up looking more tired than you are',
                'lede': 'You slept. And still the mirror shows a puffy face: swollen-looking under the eyes, softer along the jaw. It fades by lunch, but by then you’ve already seen it.',
                'pains': ['Puffy, swollen-looking under-eyes first thing in the morning', 'A jawline and cheekbones that look softer than they used to',
                          'Concealer that only makes puffy eyes look bigger', 'Gua sha stones that need oil and a tutorial, rollers that cover one narrow line at a time'],
                'close': 'The result: a face that looks tired before your day has even started.'},
    'solution': {'image': 'images/sf/brush-in-hand.jpg', 'alt': 'The Lymphatic Brush in a hand: hundreds of ultra-soft tips on a curved head',
                 'eyebrow': 'The solution', 'title': 'Three minutes, on dry skin, before your foundation',
                 'lede': 'The Lymphatic Brush gives your face the light, slow massage an aesthetician would, in 3 minutes, on dry skin.',
                 'fixes': [{'title': 'No oils or serums to glide.', 'text': 'Works on dry skin: nothing to wash off, and your foundation goes straight on after.'},
                           {'title': 'No pressing.', 'text': 'Hundreds of soft tips bend instead of pressing: no red marks, no drag on thinner skin.'},
                           {'title': 'No tutorial.', 'text': 'Four sweeps: neck, jaw, under the eyes, neck again.'},
                           {'title': 'No tool rolling around the counter.', 'text': 'A protective travel case comes with every brush.'}]},
    'use': {'image': 'images/sf/brush-how-to-use.jpg', 'alt': 'How to use the Lymphatic Brush: the four sweeps on a face, neck, jaw and cheeks, under the eyes, neck again',
            'eyebrow': 'How to use it', 'title': 'Four sweeps, about 3 minutes', 'lede': 'On clean, dry skin, in the morning, before your skincare and foundation.',
            'steps': steps(('Neck', 'Sweep down from under the ear to the collarbone.'), ('Jaw and cheeks', 'Sweep from your chin along the jaw toward the ear.'),
                           ('Under the eyes', 'Sweep out from the nose to the temples, very lightly.'), ('Neck again', 'Finish with a few sweeps down the neck.')),
            'note': 'Repeat each sweep about 10 times, then do the other side. Keep it clean: a quick sweep on a cloth with a brush cleaner or 70% alcohol before each use, and a gentle wash of the tips once a month.'},
    'compare': {'title': 'Why this brush, not a stone or a roller?', 'lede': 'Gua sha needs oil and pressure; a roller covers one narrow line at a time. The brush gives the light, wide sweeps facial massage for puffiness uses.',
                'others': 'Gua sha stones and rollers',
                'rows': ['Hundreds of soft contact points', 'Works with just a light touch', 'Flexible bristles adapt to your face', 'Four sweeps, no tutorial', 'A protective case included']},
    'box': {'title': 'What’s in the box', 'lede': 'The Lymphatic Brush is made for one thing: a light, quick massage for the look of morning puffiness.',
            'cards': [{'image': 'images/sf/brush-compare-ours.jpg', 'alt': 'The brush’s raised, soft tufts', 'title': 'Ultra-soft bristles', 'text': 'Vegan fibers that bend instead of pressing.'},
                      {'image': 'images/sf/brush-features.jpg', 'alt': 'The brush’s curved head and raised tufts', 'title': 'A curved head', 'text': 'Follows the cheek, the jaw and the neck in one sweep.'},
                      {'image': 'images/sf/brush-how-1.jpg', 'alt': 'Where morning puffiness shows: under the eyes and along the jaw', 'title': 'Eyes, cheeks and jaw', 'text': 'Where morning puffiness shows first.'},
                      {'image': 'images/sf/brush-case.jpg', 'alt': 'The brush’s protective travel case', 'title': 'A protective case', 'text': 'Keeps the bristles clean between uses, and travels.'}]},
    'faq': {'title': 'Questions', 'items': [
        {'q': 'When will I see a difference?', 'a': 'You may see a fresher, less puffy look right after your first 3 minutes. It’s temporary, so it works best every morning. Results vary from person to person.'},
        {'q': 'Does it work on mature skin?', 'a': 'Yes. The bristles bend instead of pulling, so they don’t drag thinner skin or fine lines. Keep the touch light, especially under the eyes.'},
        {'q': 'Do I need oil or serum?', 'a': 'No. Use it on clean, dry skin. You can apply your skincare and your foundation right after.'},
        {'q': 'Is it safe for sensitive skin?', 'a': 'The bristles are soft and the pressure stays light, so it’s gentle on most skin types. Avoid using it on irritated or broken skin, sunburn or active breakouts. If swelling doesn’t go away during the day, or you have a medical condition, check with your doctor first.'},
        {'q': 'What if it doesn’t work for me?', 'a': f'Email {EMAIL} within 30 days of delivery and we’ll refund it in full, even opened. No questions asked.'}]},
}
BRUSH_IMAGES = [('brush-in-hand', 'The Lymphatic Brush in a hand'),
                ('brush-case', 'The Lymphatic Brush and its SKINOFAB travel case'),
                ('brush-features', 'The brush’s soft bristles, raised tufts and curved shape')]
BRUSH_BULLETS = ['Hundreds of ultra-soft tips that bend instead of pressing', 'On dry skin, no oils: under the eyes, along the cheeks and jaw, down the neck',
                 'A 3-minute ritual before your foundation', 'Comes with a SKINOFAB travel case', 'Bought once: nothing renews']
BRUSH_VIDEO = {'src': 'images/sf/brush-how.mp4', 'webm': 'images/sf/brush-how.webm', 'poster': 'images/sf/brush-how-poster.jpg', 'autoplay': True, 'loop': True, 'controls': False,
               'id': 'sf-brush-loop'}
FOUNDATION_IMAGES = [('g-hold', 'A woman in her sixties, silver-haired, holding the Adaptive Peptide Foundation by her cheek'),
                     ('bottle', 'The Adaptive Peptide Foundation bottle'),
                     ('g-dots', 'A woman in her fifties with the foundation dotted on white, eyes closed')]


def head(pid, title, n_text, extra_scripts=(), extra_styles=()):
    pg = F.BY_ID[pid]
    return [
        f'title: {q(title + " | Special offer | SKINOFAB")}',
        'page_type: upsell',
        f'next_url: {F.BY_ID[pg["accept"]]["file"]}.html', f'decline_url: {F.BY_ID[pg["decline"]]["file"]}.html',
        'meta_tags:', *[f'  {k}: {q(v)}' for k, v in F.meta_tags(pg).items()],
        '# GENERATED by tools/funnel/apf/offer_pages.py: edit it there, then run it.',
        'styles:', '  - https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css', '  - css/checkout-brand.css', '  - css/sf-offers.css', *[f'  - {s}' for s in extra_styles],
        'scripts:', '  - https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js', '  - js/upsells.js', '  - js/payment-logos.js', '  - js/sf-failsafe.js', '  - js/sf-offer-gate.js', '  - js/sf-offer-timer.js', '  - js/sf-apf.js', *[f'  - {s}' for s in extra_scripts],
        f'announcement_text: {q(n_text)}',
        'announcement_variant: dark',
        'payment_flags:', '  show_affirm: false', '  show_afterpay: false',      # the campaign offers neither (the logos row reads the campaign; this keeps the fallback honest)
        f'thank_you_url: {q(F.route("thank-you"))}',
    ]


GATE = """{% comment %} the order's facts js/sf-offer-gate.js reads (in the page, not shown and not read aloud: the SDK fills them) {% endcomment %}
<div class="sf-sr" aria-hidden="true" data-sf-offer-gate data-sf-thank-you="{{ thank_you_url }}"{% if skip_skus %} data-sf-skip-skus="{{ skip_skus }}"{% endif %}><span data-sf-upsell-ok data-next-display="order.supportsUpsells"></span><span data-sf-first-name data-next-display="order.customer.firstName"></span>{% if skip_skus %}<div data-next-order-items data-item-template-id="sf-gate-items"><template id="sf-gate-items"><span data-sf-sku="{item.sku}"></span></template></div>{% endif %}</div>
<p class="sf-failsafe" role="alert" hidden data-sf-failsafe>This offer didn’t load, but your order is placed and confirmed by email. Refresh the page to see the offer, or email <a href="mailto:hello@skinofab.com">hello@skinofab.com</a>.</p>
"""


def hero(eyebrow, title, text, seconds):
    return ['uh:', f'  eyebrow: {q(eyebrow)}', f'  title: {q(title)}', f'  text: {q(text)}', f'  seconds: {seconds}', f'  expires: {q(EXPIRES)}']


def single_page(pid, spec, o):
    """A single-package offer with a voucher (offers 2, 2b, 3, 3b)."""
    pg = F.BY_ID[pid]
    tier = F.OFFER_PAGES[pid]['tiers'][0]
    offer = next(x for x in spec['offers'] if x['ref_id'] == F.VOUCHER[tier['voucher']])
    pkg = next(p for p in spec['funnels'][0]['pages'] if p['id'] == pid)['packages'][0]
    assert pkg['ref_id'] == tier['ref'], (pid, pkg['ref_id'], tier)
    today = int(float(pkg['price']) * (100 - float(offer['benefit']['value'])) / 100)
    assert today == int(tier['price']), (pid, today, tier)
    fallback, compare = money(today), money(float(pkg['price']))
    discount = f'{round((float(pkg["price"]) - today) / float(pkg["price"]) * 100)}%'
    terms = f'{{price}} today, {ONCE} {GUARANTEE}' + (f' {o["allergy"]}' if o.get('allergy') else '')
    brush = o.get('brush_pdp')
    fm = head(pid, o['title'], o['announcement']) + [
        *([f'skip_skus: {q(o["skip_skus"])}'] if o.get('skip_skus') else []),
        *hero(o['eyebrow'], o['hero_title'], o['hero_text'], o['seconds']),
        'upsell_layout:', '  style: card', '  boxed: true', f'  media: {"video" if brush else "carousel"}', '  media_position: right', '  media_align: center',
        '  show_bullets: true', '  show_ships_info: true', '  show_payment_logos: true', '  decline_position: below',
        *(['media_video:', *[f'  {k}: {q(v) if isinstance(v, str) else str(v).lower()}' for k, v in BRUSH_VIDEO.items()]] if brush else []),
        'upsell_offer:', '  type: single', '  pricing_mode: discounted', f'  package_id: {tier["ref"]}',
        f'  voucher: {q(tier["voucher"])}', f'  selector_id: {q(pid)}', '  show_rating: false',
        f'  pretitle: {q(o["pretitle"])}', f'  title: {q(o["title"])}', '  retail_label: "Regular price"',
        '  price_label: "Today, on this page"', '  retail_shipping: ""', '  offer_shipping: "FREE SHIPPING · CHARGED ONCE"', f'  accept_text: {q(o["accept"])}', '  accept_show_price: true',
        f'  cta_note: {q(terms)}', f'  decline_text: {q(o["decline"])}', f'  closing_title: {q(o["closing"])}',
        f'  image: {q("images/sf/" + o["images"][0][0] + ".jpg")}',
        f'  fallback_price: {q(fallback)}', f'  fallback_compare: {q(compare)}', f'  fallback_discount: {q(discount)}',
        'offer_bullets:', *[f'  - {q(b)}' for b in o['bullets']],
        'ships_info:', '  icon: "images/icon-shipping.svg"', '  flag: ""', '  text: "Ships with your order, in the same box, with tracking."',
        'swiper_slides:', *[f'  - {{ src: {q("images/sf/" + i + ".jpg")}, alt: {q(a)} }}' for i, a in o['images']],
        'swiper_thumbs:', *[f'  - {{ src: {q("images/sf/" + i + ".jpg")}, alt: "" }}' for i, a in o['images']],
        'upsell_guarantees:', '  - variant: row', '    icon: shield', '    title: "30-day money-back guarantee"',
        '    text: "Love it, or email us within 30 days of delivery for a full refund, even opened."',
        *(['upsell_body:', '  - type: features', f'    title: {q(o["features_title"])}', f'    text: {q(o["features_text"])}', '    items:',
           *[f'      - {{ title: {q(t)}, text: {q(x.replace("{price}", fallback).replace("{discount}", discount))} }}' for t, x in o['features']]] if o.get('features') else []),
        *([f'brush: {q(BRUSH_PDP)}'] if brush else []),
        'closing_cta:', '  variant: card', f'  title: {q(o["closing"])}',
        f'  note: {q((o.get("note", "") + " " if o.get("note") else "") + GUARANTEE + " The clock above is the offer’s: at 0:00 this page moves on.")}',
        f'  image: {q("images/sf/" + o["images"][0][0] + ".jpg")}',
    ]
    body = GATE + """<div class="page-wrapper">
  <div class="main-wrapper""" + (' sf-brush-page' if brush else '') + """">
    {% campaign_include 'upsell/announcement.html' announcement_text=announcement_text %}
    {% campaign_include 'upsell/header-bar.html' logo='images/sf/skinofab-wordmark.svg' %}
    {% campaign_include 'sf-upsell-hero.html' uh=uh %}
    {% campaign_include 'upsell/offer.html' %}
""" + ("    {% campaign_include 'sf-brush-pdp.html' brush=brush %}\n" if brush else "    {% campaign_include 'upsell/body.html' upsell_body=upsell_body %}\n") + """    {% campaign_include 'upsell/closing-cta.html' %}
    {% campaign_include 'footer.html' %}
  </div>
</div>
"""
    return '---\n' + '\n'.join(fm) + '\n---\n' + body


def supply_page(spec):
    """Offer 1: the supply cards, each its own package at its own price."""
    pid = 'offer-1'
    tiers = F.OFFER_PAGES[pid]['tiers']
    live = {p['ref_id']: p for p in next(p for p in spec['funnels'][0]['pages'] if p['id'] == pid)['packages']}
    for t in tiers: assert float(live[t['ref']]['price']) == t['price'], (t, live[t['ref']]['price'])
    two, six = F.PACKAGE['apf-2'], F.PACKAGE['apf-6-brush']
    cards = [
        {'id': 'supply-b1g1', 'items_json': json.dumps([{'packageId': two, 'quantity': 1}]), 'image': 'images/sf/pack-2.jpg',
         'alt': 'Two bottles of Adaptive Peptide Foundation', 'badge': 'Most popular', 'save': '50%',
         'name': '2 more bottles', 'deal': 'Add 1, get 1 FREE', 'gift': '',
         'per_day': '$0.65 a day', 'per_bottle': '$19.50 a bottle · 2 bottles', 'price': '$39.00', 'compare': '$78', 'selected': True, 'button': 'BUY NOW · $39'},
        {'id': 'supply-b3g3', 'items_json': json.dumps([{'packageId': six, 'quantity': 1}]), 'image': 'images/sf/pack-6.jpg',
         'alt': 'Six bottles of Adaptive Peptide Foundation and the Lymphatic Brush', 'badge': 'Best value', 'save': '58%',
         'name': '6 more bottles', 'deal': '$16.50 a bottle', 'gift': 'FREE Lymphatic Brush + case ($24.95)',
         'per_day': '$0.55 a day', 'per_bottle': '$16.50 a bottle · 6 bottles', 'price': '$99.00', 'compare': '$234', 'selected': False, 'button': 'BUY NOW · $99'},
    ]
    supply = {'title': 'Choose your pack', 'lede': 'Half price a bottle or less, charged once, shipped in the same box as the order you just placed.',
              'tiers': cards, 'guarantee': '30-day money-back guarantee on every bottle, even opened. You don’t send anything back.',
              'charged': 'Charged once to the payment you just used. Nothing renews.', 'decline': 'No thanks, I don’t want to stock up'}
    features = [('A bottle lasts about a month', 'One pump a day. Two more bottles cover the next two months; six cover the year’s photos, calls and lunches.'),
                ('One at home, one in your bag', 'The one on your vanity stays there. The one in your bag saves the afternoon.'),
                ('This price is only here', 'In our store one bottle is $47, bought once. On this page a bottle works out at $19.50 or $16.50, in the same box as your order.')]
    fm = head(pid, 'Stock up on the Adaptive Peptide Foundation', 'Offer 1 of 3 · Your order is placed', extra_scripts=['js/sf-supply.js']) + [
        *hero('A one-time offer', 'Just for you, right now: more bottles at half price or less',
              'Add bottles to the order you just placed: one tap, same box, same payment. These prices exist on this page only.', TIMER),
        f'supply: {q(supply)}',
        # the closing card prices the selected card (bundle.supply.*) and proxies its add / skip
        'upsell_offer:', '  type: tier-cards', f'  package_id: {two}', '  selector_id: "supply"', '  display_selector_id: "supply"', '  display_bundle_id: "supply-b1g1"',
        '  accept_text: "Yes, add it for"', '  accept_show_price: true', '  decline_text: "No thanks, I don’t want to stock up"',
        '  fallback_price: "$39.00"', '  fallback_compare: "$78.00"',
        f'  cta_note: {q("Charged once to the payment you just used. Nothing renews, and it ships in the same box. " + GUARANTEE + " " + ALLERGY)}',
        'upsell_bundle_tiers:',
        f'  - {{ id: "supply-b1g1", items_json: {q(cards[0]["items_json"])}, vouchers_json: "[]", label: "2 bottles", hint: "Add 1, get 1 free", selected: true }}',
        f'  - {{ id: "supply-b3g3", items_json: {q(cards[1]["items_json"])}, vouchers_json: "[]", label: "6 bottles", hint: "$16.50 a bottle" }}',
        'upsell_layout:', '  style: card', '  boxed: true', '  media: image', '  show_payment_logos: false',
        'upsell_body:', '  - type: features', '    title: "Why women stock up"', '    text: "Because the shade that finally works is the one you don’t want to run out of."', '    items:',
        *[f'      - {{ title: {q(t)}, text: {q(x)} }}' for t, x in features],
        'closing_cta:', '  variant: card', '  title: "Add the pack you chose above?"',
        f'  note: {q("The card you picked above is what this adds. " + GUARANTEE + " The clock above is the offer’s: at 0:00 this page moves on.")}', '  image: "images/sf/pack-2.jpg"',
    ]
    body = GATE + """<div class="page-wrapper">
  <div class="main-wrapper">
    {% campaign_include 'upsell/announcement.html' announcement_text=announcement_text %}
    {% campaign_include 'upsell/header-bar.html' logo='images/sf/skinofab-wordmark.svg' %}
    {% campaign_include 'sf-upsell-hero.html' uh=uh %}
    {% campaign_include 'sf-supply-cards.html' supply=supply %}
    {% campaign_include 'upsell/body.html' upsell_body=upsell_body %}
    {% campaign_include 'upsell/closing-cta.html' %}
    {% campaign_include 'footer.html' %}
  </div>
</div>
"""
    return '---\n' + '\n'.join(fm) + '\n---\n' + body


OFFERS = {
    'offer-2': {
        'announcement': 'Offer 2 of 3 · Your order is placed', 'seconds': TIMER, 'eyebrow': 'A one-time offer',
        'hero_title': 'One more bottle, {discount} off, just for you',
        'hero_text': 'One for your vanity, one for your bag: {price} instead of $39, charged once, in the same box as your order.',
        'pretitle': 'Only on this page',
        'title': 'One more Adaptive Peptide Foundation',
        'bullets': ['The same foundation: goes on white, adapts to your tone as you blend', 'Keep one at home and one in your bag', 'A bottle lasts about a month', 'Bought once: nothing renews', 'Ships with your order, in the same box'],
        'images': FOUNDATION_IMAGES,
        'accept': 'Yes, add one more bottle for', 'decline': 'No thanks, I don’t want another bottle',
        'features_title': 'Why women keep a second bottle',
        'features_text': 'The one you keep at home stays at home. The one in your bag saves the afternoon.',
        'features': [('For touch-ups on the go', 'One pump in your bag: a thin layer over the nose and chin and it looks fresh again.'),
                     ('Less than any bottle in our store', 'One is $47 there, bought once, and $39 on the page you came from. Here, {price}, charged once.'),
                     ('30 days to love it', 'Or email us within 30 days of delivery for a full refund, even opened.')],
        'closing': 'Add one more bottle for {price} today?',
        'allergy': ALLERGY, 'note': ALLERGY,
    },
    'offer-2b': {
        'announcement': 'Offer 2 of 3 · One more chance', 'seconds': TIMER_LAST, 'eyebrow': 'One more chance',
        'hero_title': 'Last chance: one more bottle, {discount} off',
        'hero_text': '{price} instead of $39 for one more bottle, charged once, in the same box as your order. After this page the price is gone.',
        'pretitle': 'Last chance',
        'title': 'One more Adaptive Peptide Foundation',
        'bullets': ['The same foundation: goes on white, adapts to your tone as you blend', 'Charged once, nothing renews', 'A bottle lasts about a month', 'Ships with your order, in the same box'],
        'images': FOUNDATION_IMAGES,
        'accept': 'Yes, add one more bottle for', 'decline': 'No thanks, not even at this price',
        'features_title': 'Why we make this offer',
        'features_text': 'A second bottle in the same box costs us little to ship, and it keeps you from running out of the shade that finally works.',
        'features': [('{discount} off, same bottle', 'The same 30 mL airless pump, the same serum, {price} instead of $39.'),
                     ('Charged once', 'To the payment you just used. Nothing renews, nothing else is charged.'),
                     ('The same guarantee', '30 days from delivery, a full refund even opened, on this bottle too.')],
        'closing': 'Add one more bottle for {price} today?',
        'allergy': ALLERGY, 'note': ALLERGY,
    },
    'brush-offer': {
        'announcement': 'Offer 3 of 3 · Your order is placed', 'seconds': TIMER, 'eyebrow': 'A one-time offer',
        'hero_title': 'Add the Lymphatic Brush, {discount} off, just for you',
        'hero_text': 'A 3-minute morning massage for the look of puffy eyes, cheeks and jaw, on dry skin, before your foundation. {price} with its travel case, charged once.',
        'pretitle': 'Only on this page',
        'title': 'The Lymphatic Brush',
        'bullets': BRUSH_BULLETS,
        'images': BRUSH_IMAGES,
        'accept': 'Yes, add the brush for', 'decline': 'No thanks, I don’t want the brush',
        'closing': 'Add the Lymphatic Brush for {price} today?',
        'brush_pdp': True, 'skip_skus': 'SKF-APF-3-GIFTS,SKF-APF-6-BRUSH',
    },
    'brush-offer-b': {
        'announcement': 'Offer 3 of 3 · Last chance', 'seconds': TIMER_LAST, 'eyebrow': 'Last chance',
        'hero_title': 'Last chance: the brush at {discount} off',
        'hero_text': '{price} instead of $24.95 for the brush with its travel case, charged once, in the same box as your foundation. After this page the price is gone.',
        'pretitle': 'Last chance',
        'title': 'The Lymphatic Brush',
        'bullets': BRUSH_BULLETS,
        'images': BRUSH_IMAGES,
        'accept': 'Yes, add the brush for', 'decline': 'No thanks, I’ll pass on the brush',
        'closing': 'Add the Lymphatic Brush for {price} today?',
        'brush_pdp': True, 'skip_skus': 'SKF-APF-3-GIFTS,SKF-APF-6-BRUSH',
    },
}


if __name__ == '__main__':
    spec = json.loads(SPEC.read_text())
    out = SRC / (F.BY_ID['offer-1']['file'] + '.html')
    out.write_text(supply_page(spec)); print(out.relative_to(ROOT))
    for pid, o in OFFERS.items():
        out = SRC / (F.BY_ID[pid]['file'] + '.html')
        out.write_text(single_page(pid, spec, o)); print(out.relative_to(ROOT))
