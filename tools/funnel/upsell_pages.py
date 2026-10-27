"""The funnel's four special offers (post-purchase upsells), as Campaign Page Kit pages, from one layout.

usage: python3 -I tools/funnel/upsell_pages.py

Writes campaigns/skinofab/src/stick-funnel/stick-special-<n>.html (generated: edit this file, then run it). Each is
Apollo's single-offer upsell (upsell_offer.type: single + voucher: a hidden, pre-selected bundle selector with
data-next-upsell-context adds the line with its voucher on accept, so loading the page writes nothing to a cart).
The package, voucher and routes come from funnel.py and the CampaignSpec (campaign_spec.py's live read), the claims
from each product's store copy (tools/persona/*_copy.py). Every package recurs, so each offer says, by the button,
what is charged today and what after: the voucher takes its discount off this first charge only.
No countdown (nothing expires when it ends) and no rating row (the starter's "4.8/5 - 19,569+ Reviews" is demo copy).
The percentages are the SDK's ({discount}): the campaign rounds offer prices down to whole dollars, so 50% off $37 is
$18 (51%) and 20% off $24.95 is $19 (24%); the page shows what she pays, never a rounder number.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import funnel as F

ROOT = HERE.parents[1]
SRC = ROOT / 'campaigns' / 'skinofab' / 'src' / F.SLUG
SPEC = ROOT / 'campaigns' / 'skinofab' / 'campaign-spec.json'
EMAIL = 'hello@skinofab.com'

OFFERS = {
    'special-1': {
        'hero_title': 'Your order is placed!',
        'hero_offer': 'Add one more stick for {price} ({discount} off)',
        'hero_sub': 'A second Adaptive Foundation Stick for your bag, so the one at home stays at home. This price is only on this page.',
        'pretitle': 'Only on this page · {discount} off your first charge',
        'title': 'One more Adaptive Foundation Stick',
        'bullets': ['Keep one at home and one in your bag for touch-ups',
                    'The same stick: goes on white, meets your tone as you blend, brush built in',
                    'Its own refills, every 28 days: skip, delay or cancel them by email, any time',
                    'Ships with your order, no extra shipping'],
        'images': [('up1-hold', 'A woman in her fifties holding the Adaptive Foundation Stick by her cheek'),
                   ('g-duo-ends', 'The stick open at both ends: the white cream and the kabuki brush'),
                   ('bag', 'The black SKINOFAB stick going into a handbag')],
        'accept': 'Yes, add one more stick for',
        'decline': 'No thanks, I don’t want a second stick',
        'features_title': 'Why women add a second stick',
        'features_text': 'The one you keep at home stays at home. The one in your bag saves the afternoon.',
        'features': [('For touch-ups on the go', 'Buff the brush end over your nose and chin and it looks fresh again.'),
                     ('One at home, one with you', 'The stick on your vanity stays there; the spare lives in your bag.'),
                     ('Refills you control', 'It refills on its own every 28 days. Skip or cancel it by email whenever you like.')],
        'closing': 'Add one more stick for {price}?',
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
                   ('up2-how', 'How to use the Lymphatic Brush: neck, jaw and cheeks, under the eyes'),
                   ('up2-ba', 'A puffy morning face, and the same face after a gentle massage (AI illustration)')],
        'accept': 'Yes, add the brush for',
        'decline': 'No thanks, I don’t want the brush',
        'features_title': 'Three minutes, every morning',
        'features_text': 'A light touch with soft bristles, before your foundation goes on.',
        'features': [('Neck first', 'Sweep down toward the collarbone, ten times.'),
                     ('Jaw and cheeks', 'Sweep out toward the ear, ten times each side.'),
                     ('Under the eyes', 'Sweep out to the temples with the lightest touch.')],
        'closing': 'Add the Lymphatic Brush for {price}?',
    },
    'special-3': {
        'hero_title': 'For the lines foundation can’t fill',
        'hero_offer': 'Add the PDRN Plumping Balm for {price} ({discount} off)',
        'hero_sub': 'The 10-second pick-me-up for hollow-looking under-eyes, smile lines and the lines around your lips.',
        'pretitle': 'Only on this page · {discount} off your first charge',
        'title': 'PDRN Plumping Balm',
        'bullets': ['PDRN, Volufiline™, collagen and hyaluronic acid in a melting balm',
                    'Swipe it on, press it in: skin looks smoother, fuller and rested in seconds',
                    'A black stick like your foundation, made for your bag',
                    '10 g, about a month of daily use'],
        'images': [('up3-balm', 'The PDRN Plumping Balm stick'),
                   ('up3-hold', 'A woman in her fifties holding the PDRN Plumping Balm'),
                   ('up3-ba', 'Under-eyes before and after the balm (AI illustration)'),
                   ('up3-inside', 'What is inside the balm: PDRN, Volufiline and collagen with hyaluronic acid')],
        'accept': 'Yes, add the balm for',
        'decline': 'No thanks, I don’t want the balm',
        'features_title': 'Made for the spots foundation can’t fix',
        'features_text': 'Press it on where your face looks tired, over or under your foundation.',
        'features': [('Under the eyes', 'Where skin looks hollow and shadowed by the afternoon.'),
                     ('Smile lines', 'Swipe along the fold, then press it in with a fingertip.'),
                     ('Around the lips', 'The fine lines lipstick catches in.')],
        'note': 'Contains salmon-derived PDRN: not for anyone with a fish allergy.',
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
        'features_title': 'One light step, face and neck',
        'features_text': 'For skin that looks less firm, drier and duller after 45.',
        'features': [('Two drops for your face', 'Press them in after cleansing, morning and night.'),
                     ('Two for your neck', 'Sweep upward from the collarbone.'),
                     ('Then your stick', 'It sinks in within a minute, so your foundation goes straight on.')],
        'closing': 'Add the EGF + NAD+ Firming Serum for {price}?',
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
             'Backed by our 30-day money-back guarantee.')
    fm = [
        f'title: {q(o["title"] + " | Special offer | SKINOFAB")}',
        'page_type: upsell',
        f'next_url: {nxt}', f'decline_url: {F.BY_ID[pg["decline"]]["file"]}.html',
        'meta_tags:', *[f'  {k}: {q(v)}' for k, v in F.meta_tags(pg).items()],
        '# GENERATED by tools/funnel/upsell_pages.py: edit it there, then run it.',
        'styles:', '  - https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css', '  - css/checkout-brand.css',
        'scripts:', '  - https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js', '  - js/upsells.js', '  - js/payment-logos.js',
        f'announcement_text: {q(f"Offer {n} of 4 · Your order is placed")}',
        'announcement_variant: dark',
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
        'closing_cta:', '  variant: card', f'  title: {q(o["closing"])}',
        f'  note: {q((o.get("note", "") + " " if o.get("note") else "") + "Backed by our 30-day money-back guarantee.")}',
        f'  image: {q("images/sf/" + o["images"][0][0] + ".jpg")}',
    ]
    body = """{% comment %} Apollo's single-offer upsell: announcement, header, hero band, the offer (the one SDK offer), body, closing card
     (its accept / skip proxy the offer's own). {% endcomment %}
<div class="page-wrapper">
  <div class="main-wrapper">
    {% campaign_include 'upsell/announcement.html' announcement_text=announcement_text %}
    {% campaign_include 'upsell/header-bar.html' logo='images/sf/skinofab-wordmark.svg' %}
    {% campaign_include 'upsell/hero.html' upsell_hero=upsell_hero %}
    {% campaign_include 'upsell/offer.html' %}
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
