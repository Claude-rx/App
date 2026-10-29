"""The funnel's four special offers (post-purchase upsells), as Campaign Page Kit pages, from one layout.

usage: python3 -I tools/funnel/upsell_pages.py

Writes campaigns/skinofab/src/stick-funnel/stick-special-<n>.html (generated: edit this file, then run it). Each is
Apollo's single-offer upsell (upsell_offer.type: single + voucher: a hidden, pre-selected bundle selector with
data-next-upsell-context adds the line with its voucher on accept, so loading the page writes nothing to a cart).
The package, voucher and routes come from funnel.py and the CampaignSpec (campaign_spec.py's live read), the claims
from each product's store copy (tools/persona/*_copy.py). Every package recurs, so each offer says, by the button,
what is charged today and what after: the voucher takes its discount off this first charge only.
No countdown (nothing expires when it ends) and no rating row (the starter's "4.8/5 - 19,569+ Reviews" is demo copy).
Under the offer, "how it works" (_includes/sf-upsell-how.html): its loop (upsell_videos.py; offer 1 plays the stick's
explainer) beside the product page's own steps; then "reserved for you" (_includes/sf-upsell-reserved.html): the
store's price for it beside today's, why the price is only here (not sold at it anywhere else, it rides in the box she
just ordered, it goes on the payment she just made) and the button again; then what is in it.
The percentages are the SDK's ({discount}): the campaign rounds offer prices down to whole dollars, so 50% off $37 is
$18 (51%) and 20% off $24.95 is $19 (24%); the page shows what she pays, never a rounder number.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'persona'))
import funnel as F
import stick_copy as SC, balm_copy as BC, serum_copy as SEC

ROOT = HERE.parents[1]
SRC = ROOT / 'campaigns' / 'skinofab' / 'src' / F.SLUG
SPEC = ROOT / 'campaigns' / 'skinofab' / 'campaign-spec.json'
EMAIL = 'info@skinofab.com'


def video(name, label, size=(720, 900)):
    """A loop in the funnel's images (funnel_images.py copies them there): its two sources, poster, size and label (which
    says it is an illustration, as its frames do)."""
    return {'mp4': f'images/sf/{name}.mp4', 'webm': f'images/sf/{name}.webm', 'poster': f'images/sf/{name}-poster.jpg',
            'width': size[0], 'height': size[1], 'label': label if label.startswith('Illustration') else f'Illustration: {label}'}


def reserved(title, store_price, store_note, price_title, price_text):
    """Why today's price is hers: the store's own price for one beside today's (with what renews), and three reasons.
    The price reason says what is true of the store (funnel review 3): one costs more there, and where its multi-packs
    cost less each, it says so; a store-wide "only here" would not be true of a 3-pack. Then: the offer goes on the
    payment she just made (an order that can't take one never sees it, sf-offer-gate.js), and the guarantee (the store
    ships free, so "no extra shipping" saved her nothing)."""
    return {'title': title, 'store_price': store_price, 'store_note': store_note, 'items': [
        {'title': price_title, 'text': price_text},
        {'title': 'One tap, nothing to type', 'text': 'It’s added to the order you just placed, in the same box, and charged to the same payment method.'},
        {'title': '30 days to love it', 'text': 'Or email us within 30 days of delivery for a full refund, even opened.'}]}


# the stick and the balm carry the PDRN warning by every button (in the terms under it), as their product pages do
ALLERGY = 'Contains salmon-derived PDRN: not for anyone with a fish allergy.'
# the funnel's multi-pack line: the store's 2- and 3-packs of the brush, balm and serum cost less each than one
PACKS = 'Our 2- and 3-packs cost less each; this is the price for adding just one to your order.'


def steps(*rows):
    return [{'title': t, 'text': x} for t, x in rows]


_SCI = SC.TWIN['science']

OFFERS = {
    'special-1': {
        'hero_title': 'Your order is placed!',
        'hero_offer': 'Add one more stick for {price} ({discount} off)',
        'hero_sub': 'One more Adaptive Foundation Stick for your bag, so the one at home stays at home. This price is only on this page.',
        'pretitle': 'Only on this page · {discount} off your first charge',
        'title': 'One more Adaptive Foundation Stick',
        'bullets': ['Keep one at home and one in your bag for touch-ups',
                    'The same stick: goes on white, meets your tone as you blend, brush built in',
                    'Its own refills, every 28 days: skip, delay or cancel them by email, any time',
                    'Ships with your order, in the same box'],
        'images': [('up1-hold', 'A woman in her fifties holding the Adaptive Foundation Stick by her cheek'),
                   ('g-duo-ends', 'The stick open at both ends: the white cream and the kabuki brush'),
                   ('bag', 'The black SKINOFAB stick going into a handbag')],
        'accept': 'Yes, add one more stick for',
        'decline': 'No thanks, I don’t want another stick',
        'features_title': 'Why women keep a spare stick',
        'features_text': 'The one you keep at home stays at home. The one in your bag saves the afternoon.',
        'features': [('For touch-ups on the go', 'Buff the brush end over your nose and chin and it looks fresh again.'),
                     ('One at home, one with you', 'The stick on your vanity stays there; the spare lives in your bag.'),
                     ('Refills you control', 'It refills on its own every 28 days. Skip or cancel it by email whenever you like.')],
        'closing': 'Add one more stick for {price}?',
        # (its steps are the explainer's four captions, in their order and words: stick_copy's science rows)
        'how': {'eyebrow': 'How it works', 'title': 'One shade that meets your skin', 'text': _SCI['lede'],
                'steps': steps(*_SCI['rows']), 'note': _SCI['note'], 'video': video('science', _SCI['video_alt'], (864, 1080))},
        'reserved': reserved('One more stick, for less than any stick in our store', '$37.00', '1 stick, with Automatic Refills',
                             'Less than any stick in our store', 'One is $37.00 there, and the 2-pack works out at $23.50 a stick.'),
        'allergy': ALLERGY,
    },
    'special-2': {
        'hero_title': 'Add a 3-minute morning ritual',
        'hero_offer': 'Add the Lymphatic Brush for {price} ({discount} off)',
        'hero_sub': 'The 3-minute morning massage for puffy-looking eyes, cheeks and jaw. Getting one free with 2 sticks? Add a second for your travel bag.',
        'pretitle': 'Only on this page · {discount} off your first charge',
        'title': 'The Lymphatic Brush',
        'bullets': ['Hundreds of ultra-soft tips that bend instead of pressing',
                    'On dry skin, no oils: under the eyes, along the cheeks and jaw, down the neck',
                    'A 3-minute ritual before your foundation',
                    'Comes with a SKINOFAB travel case',
                    'A fresh brush every 90 days, as with a toothbrush: skip or cancel by email'],
        'images': [('up2-brush', 'The Lymphatic Brush and its SKINOFAB travel case'),
                   ('up2-how', 'How to use the Lymphatic Brush: neck, jaw and cheeks, under the eyes')],
        'accept': 'Yes, add the brush for',
        'decline': 'No thanks, I don’t want the brush',
        'features_title': 'Why it’s worth three minutes',
        'features_text': 'A light touch, no oils, nothing to wash off.',
        'features': [('Soft tips, light touch', 'Hundreds of ultra-soft tips bend instead of pressing: no red marks.'),
                     ('On dry skin', 'No oils, so your foundation goes straight on after.'),
                     ('A fresh brush every 90 days', 'Like a toothbrush: skip or cancel the refill by email.')],
        'closing': 'Add the Lymphatic Brush for {price}?',
        'how': {'eyebrow': 'How to use it', 'title': 'Three minutes, every morning',
                'text': 'On clean, dry skin, before your foundation. No oils and no pressing: the soft tips do the work.',
                'steps': steps(('Neck', 'Sweep down from under the ear to the collarbone.'),
                               ('Jaw and cheeks', 'Sweep from your chin along the jaw toward the ear.'),
                               ('Under the eyes', 'Sweep out from the nose to the temples, very lightly.'),
                               ('Neck again', 'Finish with a few sweeps down the neck.')),
                'note': 'Repeat each sweep about 10 times, then do the other side. The video is an illustration.',
                'video': video('up2-how', 'The Lymphatic Brush’s soft tips, its four sweeps (neck, jaw and cheeks, under the eyes, neck again) and its travel case')},
        'reserved': reserved('The brush, for less than one in our store', '$24.95', '1 brush with its case',
                             'Less than one brush in our store', f'One is $24.95 there. {PACKS}'),
    },
    'special-3': {
        'hero_title': 'For the look of tired under-eyes',
        'hero_offer': 'Add the PDRN Plumping Balm for {price} ({discount} off)',
        'hero_sub': 'A melting balm you press on where your face looks tired: under the eyes, along smile lines, around the lips.',
        'pretitle': 'Only on this page · {discount} off your first charge',
        'title': 'PDRN Plumping Balm',
        'bullets': ['PDRN, Volufiline™, collagen and hyaluronic acid in a melting balm',
                    'Swipe it on, press it in: a soft, smooth, rested look over or under your foundation',
                    'A black stick like your foundation, made for your bag',
                    '10 g, about a month of daily use'],
        'images': [('up3-balm', 'The PDRN Plumping Balm stick'),
                   ('up3-hold', 'A woman in her fifties holding the PDRN Plumping Balm'),
                   ('up3-inside', 'What is inside the balm: PDRN, Volufiline and collagen with hyaluronic acid')],
        'accept': 'Yes, add the balm for',
        'decline': 'No thanks, I don’t want the balm',
        'features_title': 'What’s in the balm',
        'features_text': 'In a balm that melts on contact, in a black stick like your foundation.',
        'features': [(n, text) for n, _, text in BC.INGREDIENTS[:3]],
        'how': {'eyebrow': 'How to use it', 'title': 'Swipe it on, press it in',
                'text': 'Over or under your foundation, wherever your face looks tired. About 10 seconds.',
                'steps': steps(('Under the eyes', 'Twist up a little and swipe a thin layer out toward the temple.'),
                               ('Along smile lines', 'Swipe it along the fold.'),
                               ('Around the lips', 'On the fine lines lipstick catches in.'),
                               ('Press it in', 'With the stick or a fingertip, no rubbing.')),
                'note': 'Morning and night; at night you can go a little thicker. Less is more: a thin layer looks smooth, too '
                        'much looks shiny. The video is an illustration.',
                'video': video('up3-how', 'A woman pressing the PDRN Plumping Balm on under her eyes, along a smile line and around her lips')},
        'reserved': reserved('The balm, for less than one in our store', '$19.95', 'with Automatic Refills, $24.95 one at a time',
                             'Less than one balm in our store', f'One is $19.95 there with refills, $24.95 one at a time. {PACKS}'),
        'allergy': ALLERGY,
        'note': ALLERGY,
        'closing': 'Add the PDRN Plumping Balm for {price}?',
    },
    'special-4': {
        'hero_title': 'Last one, we promise',
        'hero_offer': 'Add the EGF + NAD+ Firming Serum for {price} ({discount} off)',
        'hero_sub': 'Two drops for your face, two for your neck: the light step before your stick.',
        'pretitle': 'Only on this page · {discount} off your first charge',
        'title': 'EGF + NAD+ Firming Serum',
        'bullets': ['EGF (sh-Oligopeptide-1), NAD+ and collagen in a light, water-based serum',
                    'Sinks in within a minute, so your foundation goes straight on',
                    'Skin looks hydrated and smoother from the first use',
                    '30 mL, about two months of daily use'],
        'images': [('up4-serum', 'The EGF + NAD+ Firming Serum bottle'),
                   ('up4-hold', 'A woman in her fifties holding the EGF + NAD+ Firming Serum'),
                   ('up4-inside', 'What is inside the serum: EGF, NAD+ and collagen')],
        'accept': 'Yes, add the serum for',
        'decline': 'No thanks, I don’t want the serum',
        'features_title': 'What’s in the serum',
        # (the serum page's texture line without its SPF: the funnel names SPF only to say the stick has none, check_funnel)
        'features_text': 'Water-based and light: it sinks in within a minute and sits well under moisturiser and makeup.',
        'features': [(n, text) for n, _, text in SEC.INGREDIENTS[:3]],
        'how': {'eyebrow': 'How to use it', 'title': 'Two drops for your face, two for your neck',
                'text': 'Morning and night, on clean skin. It sinks in within a minute.',
                'steps': steps(('Two drops for your face', 'After cleansing your face and neck.'),
                               ('Press them in', 'With your fingertips, no rubbing.'),
                               ('Two more, down your neck', 'Swept down from under the jaw.'),
                               ('Moisturiser, then your stick', 'They go straight on once it has sunk in.')),
                'note': 'Less is more: two drops cover the whole face. The video is an illustration.',
                'video': video('up4-how', 'A woman putting two drops of the EGF + NAD+ Firming Serum on her face, pressing them in and sweeping more down her neck, then her foundation stick')},
        'reserved': reserved('The serum, for less than one in our store', '$27.95', 'with Automatic Refills, $34.95 one at a time',
                             'Less than one bottle in our store', f'One is $27.95 there with refills, $34.95 one at a time. {PACKS}'),
        'closing': 'Add the EGF + NAD+ Firming Serum for {price}?',
        'skip_europe': True,
    },
}


def q(s):
    return json.dumps(s, ensure_ascii=False)


def page(pid, spec):
    pg, o = F.BY_ID[pid], OFFERS[pid]
    offer = next(x for x in spec['offers'] if x['ref_id'] == pg['offer'])
    pkg = next(p for p in next(f for f in spec['funnels'])['pages'] if p['id'] == pid)['packages'][0]
    every = pkg['interval_count']
    n = pid.split('-')[1]
    nxt = F.BY_ID[pg['accept']]['file'] + '.html'
    # what she pays: the voucher's price today (the campaign rounds offer prices down to whole dollars, so 50% off
    # $37 is $18), then the package's recurring price. The renewal is its own sentence with its amount written out,
    # so it reads as the rebill it is (QA's commercial parity reads "$37.00 every 28 days"; an amount right after
    # "off" reads as a saving), and the SDK's live prices replace the fallbacks as the page loads.
    recurring = float(pkg['price_recurring'])
    today = int(float(pkg['price']) * (100 - float(offer['benefit']['value'])) / 100)
    fallback, compare = f'${today:.2f}', f'${float(pkg["price"]):.2f}'
    discount = f'{round((float(pkg["price"]) - today) / float(pkg["price"]) * 100)}%'
    terms = (f'{{price}} today ({{discount}} off this first charge). After that, ${recurring:.2f} every {every} days for '
             f'this one until you cancel. We email you before every refill; to skip or cancel, just email {EMAIL}. '
             'Backed by our 30-day money-back guarantee.' + (f' {o["allergy"]}' if o.get('allergy') else ''))
    o['reserved']['renews'] = f'then ${recurring:.2f} every {every} days'
    fm = [
        f'title: {q(o["title"] + " | Special offer | SKINOFAB")}',
        'page_type: upsell',
        f'next_url: {nxt}', f'decline_url: {F.BY_ID[pg["decline"]]["file"]}.html',
        'meta_tags:', *[f'  {k}: {q(v)}' for k, v in F.meta_tags(pg).items()],
        '# GENERATED by tools/funnel/upsell_pages.py: edit it there, then run it.',
        'styles:', '  - https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css', '  - css/checkout-brand.css',
        'scripts:', '  - https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js', '  - js/upsells.js', '  - js/payment-logos.js', '  - js/sf-failsafe.js', '  - js/sf-offer-gate.js', '  - js/sf-funnel.js',
        f'announcement_text: {q(f"Offer {n} of 4 · Your order is placed")}',
        'announcement_variant: dark',
        f'thank_you_url: {q(F.route("thank-you"))}',
        *(['skip_europe: true'] if o.get('skip_europe') else []),
        'upsell_hero:', '  variant: band', f'  title: {q(o["hero_title"])}', f'  offer: {q(o["hero_offer"])}', f'  suboffer: {q(o["hero_sub"])}',
        'upsell_layout:', '  style: card', '  boxed: true', '  media: carousel', '  media_position: right', '  media_align: center',
        '  show_bullets: true', '  show_ships_info: true', '  show_payment_logos: true', '  decline_position: below',
        'upsell_offer:', '  type: single', '  pricing_mode: discounted', f'  package_id: {pg["package"]}',
        f'  voucher: {q(offer["code"])}', f'  selector_id: {q("special-" + n)}', '  show_rating: false',
        f'  pretitle: {q(o["pretitle"])}', f'  title: {q(o["title"])}', '  retail_label: "Regular price"',
        '  price_label: "Today, on this page"', '  retail_shipping: ""', '  offer_shipping: "FREE SHIPPING"', f'  accept_text: {q(o["accept"])}', '  accept_show_price: true',
        f'  cta_note: {q(terms)}', f'  decline_text: {q(o["decline"])}', f'  closing_title: {q(o["closing"])}',
        f'  image: {q("images/sf/" + o["images"][0][0] + ".jpg")}',
        f'  fallback_price: {q(fallback)}', f'  fallback_compare: {q(compare)}', f'  fallback_discount: {q(discount)}',
        'offer_bullets:', *[f'  - {q(b)}' for b in o['bullets']],
        'ships_info:', '  icon: "images/icon-shipping.svg"', '  flag: ""', '  text: "Ships with your order, in the same box, with tracking."',
        'swiper_slides:', *[f'  - {{ src: {q("images/sf/" + i + ".jpg")}, alt: {q(a)} }}' for i, a in o['images']],
        'swiper_thumbs:', *[f'  - {{ src: {q("images/sf/" + i + ".jpg")}, alt: "" }}' for i, a in o['images']],
        'upsell_guarantees:', '  - variant: row', '    icon: shield', '    title: "30-day money-back guarantee"',
        '    text: "Love it, or email us within 30 days of delivery for a full refund, even opened."',
        'upsell_body:', '  - type: features', f'    title: {q(o["features_title"])}', f'    text: {q(o["features_text"])}', '    items:',
        *[f'      - {{ title: {q(t)}, text: {q(x)} }}' for t, x in o['features']],
        f'how: {q(o["how"])}', f'reserved: {q(o["reserved"])}',
        'closing_cta:', '  variant: card', f'  title: {q(o["closing"])}',
        f'  note: {q((o.get("note", "") + " " if o.get("note") else "") + "Backed by our 30-day money-back guarantee.")}',
        f'  image: {q("images/sf/" + o["images"][0][0] + ".jpg")}',
    ]
    body = """{% comment %} Apollo's single-offer upsell: announcement, header, hero band, the offer (the one SDK offer), body, closing card
     (its accept / skip proxy the offer's own). {% endcomment %}
{% comment %} the order's facts js/sf-offer-gate.js reads (in the page, not shown: the SDK fills them) {% endcomment %}
<div class="sf-sr" data-sf-offer-gate data-sf-thank-you="{{ thank_you_url }}"><span data-sf-upsell-ok data-next-display="order.supportsUpsells"></span><span data-sf-first-name data-next-display="order.customer.firstName"></span>{% if skip_europe %}<span data-sf-ship-country data-next-display="order.shippingAddress.country"></span>{% endif %}</div>
<p class="sf-failsafe" role="alert" hidden data-sf-failsafe>This offer didn’t load, but your order is placed and confirmed by email. Refresh the page to see the offer, or email <a href="mailto:info@skinofab.com">info@skinofab.com</a>.</p>
<div class="page-wrapper">
  <div class="main-wrapper">
    {% campaign_include 'upsell/announcement.html' announcement_text=announcement_text %}
    {% campaign_include 'upsell/header-bar.html' logo='images/sf/skinofab-wordmark.svg' %}
    {% campaign_include 'upsell/hero.html' upsell_hero=upsell_hero %}
    {% campaign_include 'upsell/offer.html' %}
    {% campaign_include 'sf-upsell-how.html' how=how %}
    {% campaign_include 'sf-upsell-reserved.html' reserved=reserved %}
    {% campaign_include 'upsell/body.html' upsell_body=upsell_body %}
    {% campaign_include 'upsell/closing-cta.html' %}
    {% campaign_include 'footer.html' %}
  </div>
</div>
"""
    return '---\n' + '\n'.join(fm) + '\n---\n' + body


if __name__ == '__main__':
    spec = json.loads(SPEC.read_text())
    for pid in ('special-1', 'special-2', 'special-3', 'special-4'):
        out = SRC / (F.BY_ID[pid]['file'] + '.html')
        out.write_text(page(pid, spec))
        print(out.relative_to(ROOT))
