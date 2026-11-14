#!/usr/bin/env python3
"""Get Rid Of post-purchase offers (campaign 2362). Run by build_checkout.py (after the checkout is written).

    checkout -> upsell     (1 pack, 70% off  = $14.98)  --yes--> upsell-2
                                                       --no---> upsell-2
    (downsell, 1 pack 50% off = $24.97, is no longer routed: since the owner set upsell 1 to 70% off on 14 Nov 2026 it
    would offer a higher price after a no)
             -> upsell-2   (5 packs, $48.95)            --yes--> receipt
                                                       --no---> downsell-2 (5 packs, $38.95) -> receipt

All four sell package 1 (one-time pouch pack, SKU GRO-MOUSE-OT) with a voucher scoped to it:
GROU1PK30Q (offer 10), GROD1PK50Q (11), GROU2FIVE48Q (12, needs 5 units), GROD2FIVE38Q (13, needs 5 units).
Prices end in .97 where one unit is sold. Five identical units can't total .97 (per-unit cents x 5 ends in 0 or 5),
so the 5-packs are $48.95 / $38.95, the owner's choice. Every page carries the limited-time / exclusive badges and the
house map (house_map.py). There is no countdown: nothing would actually expire when it reached zero.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAMP = ROOT / 'campaigns/getridof/src/mouse-pouches'
HERE = ROOT / 'tools/funnel/getridof'

PACK1 = 'Rodent Repellent Pouches · 1 Pack (12 Pouches)'
PACK5 = 'Whole-Home Pack · 5 Packs (60 Pouches)'
FEATS = [('Garage & shed', 'Door edges, corners and anywhere you store bird seed, grass seed or pet food.'),
         ('Basement & attic', 'The quiet spots where mice nest first and where you check last.'),
         ('Kitchen & pantry', 'Under the sink, behind the fridge and stove, and inside the cabinets.'),
         ('No gaps for 90 days', 'Each pouch lasts up to 90 days. Fresh pouches in every zone leave mice nowhere quiet to move to.')]
MAP1 = ('Why one pack isn’t enough for your whole house',
        'Your first order protects one zone. Mice simply move to the next quiet room. Here’s where pouches go in a typical home.')
MAP5 = ('Protect every room, every floor, for the whole family',
        'A typical 2-story home with a garage and basement needs about 60 pouches. That’s exactly 5 packs.')
B1 = ['12 more pouches, the same 4-oil formula', '{pct} off: {price} instead of {compare_price}',
      'Added with one click, no need to re-enter your card', 'Same 30-day money-back guarantee']
B5 = ['60 pouches: enough for a typical 2-story home, garage and basement', '{discount} off: {price} instead of {compare_price}',
      '{per_pack}, our lowest price ever', 'One click, same 30-day money-back guarantee']

OFFERS = {
    'upsell': dict(
        title='One More Pack, 70% Off', next='upsell-2.html', decline='upsell-2.html',
        announce='EXCLUSIVE OFFER JUST FOR YOU · LIMITED TIME ONLY',
        badge_note='Your order is confirmed. This 70%-off price is only available on this page.',
        hero_title='Exclusive: Add Another Pack for 70% Off',
        hero_text='One pack covers about one zone of your home. Protect the next one too: 12 more pouches for just <strong>{price}</strong>, added to the order you just placed.',
        qty=1, voucher='GROU1PK30Q', selector='upsell-pouch', offer_title=PACK1, image='pdp/t12-rodent-57d2b1.png',
        accept='Yes, add 1 pack for', decline_text='No thanks, one pack is enough',
        bullets=[b.replace('{pct}', '70%') for b in B1],
        features_title='Where a second pack goes', features_text='Mice don’t stop at the kitchen. Put the second pack where they nest first.',
        closing='Add one more pack for 70% off?', map=MAP1),
    'downsell': dict(
        title='Last Chance: 50% Off One More Pack', next='upsell-2.html', decline='upsell-2.html',
        announce='WAIT! ONE-TIME EXCLUSIVE OFFER · LIMITED TIME',
        badge_note='We cut the price in half, just for you. This 50%-off price disappears when you leave this page.',
        hero_title='Wait! Take an Extra Pack at 50% Off',
        hero_text='Here’s our best price on one more pack: 12 pouches for just <strong>{price}</strong>. That’s half off, added to your order with one click.',
        qty=1, voucher='GROD1PK50Q', selector='downsell-pouch', offer_title=PACK1, image='pdp/t12-rodent-57d2b1.png',
        accept='Yes, add 1 pack at 50% off for', decline_text='No thanks, I’ll pass on 50% off',
        bullets=[b.replace('{pct}', '50%') for b in B1],
        features_title='Where your extra pack goes', features_text='Cover the zone mice will move to next.',
        closing='Add one more pack for 50% off?', map=MAP1),
    'upsell-2': dict(
        title='Whole-Home Pack: 5 Packs', next='receipt.html', decline='downsell-2.html',
        announce='EXCLUSIVE WHOLE-HOME OFFER JUST FOR YOU · LIMITED TIME',
        badge_note='Only for customers who just ordered. This whole-home price is only available on this page.',
        hero_title='Protect the Entire House &amp; Family: 5 Packs for Only {price}',
        hero_text='Every room, every floor, the garage, attic and basement: 5 packs (60 pouches) for just <strong>{price}</strong>. That’s under $10 a pack.',
        qty=5, voucher='GROU2FIVE48Q', selector='upsell-home5', offer_title=PACK5, image='pdp/gro-whole-home-5-pack.webp',
        accept='Yes, protect my whole house for', decline_text='No thanks, I’ll protect just part of my home',
        bullets=[b.replace('{per_pack}', 'Under $10 per pack') for b in B5],
        features_title='What 60 pouches cover', features_text='Every zone at once, so mice have nowhere quiet left to move to.',
        closing='Protect your whole house for just {price}?', map=MAP5),
    'downsell-2': dict(
        title='Final Offer: 5 Packs', next='receipt.html', decline='receipt.html',
        announce='FINAL EXCLUSIVE OFFER · LIMITED TIME · THIS PAGE ONLY',
        badge_note='Our lowest price ever, only for you. It’s gone the moment you leave this page.',
        hero_title='Final Offer: The Whole-Home 5 Packs for Only {price}',
        hero_text='Our lowest price ever: 5 packs (60 pouches) to cover the entire house for just <strong>{price}</strong>. Less than $8 a pack.',
        qty=5, voucher='GROD2FIVE38Q', selector='downsell-home5', offer_title=PACK5, image='pdp/gro-whole-home-5-pack.webp',
        accept='Yes, protect my whole house for', decline_text='No thanks, complete my order',
        bullets=[b.replace('{per_pack}', 'Less than $8 per pack') for b in B5],
        features_title='What 60 pouches cover', features_text='Every zone at once, so mice have nowhere quiet left to move to.',
        closing='Protect your whole house for just {price}?', map=MAP5),
}

PALETTE = '''/* upsell palette: packaging green #7EA254, deep green #23372B */
.announcement__block{background:#23372B!important;color:#fff!important}
.upsell-container--box{border-color:#7EA254!important}
.bullet_features-icon-svg,.bullet_features-icon-svg svg,.bullet_features-icon-svg path{color:#4F7A2E!important;border-color:#4F7A2E!important}
.icon-wrapper.cc-circle{background:#7EA254!important}
a.button.cc-xl,.button.cc-xl{background:#7EA254!important;border-color:#7EA254!important;color:#fff!important}
a.button.cc-xl:hover{background:#6B8D45!important}
'''

BADGES = '''{%- comment -%} GENERATED by tools/funnel/getridof/build_offers.py: limited-time + exclusive badges on every post-purchase offer. {%- endcomment -%}
<div class="gro-badges" role="note">
  <span class="gro-badge gro-badge--time">&#9200; Limited-time offer</span>
  <span class="gro-badge gro-badge--you">&#9733; Exclusive offer just for you</span>
  <p class="gro-badges__note">{{ badge_note | default: "This price is only available on this page. Once you leave, it’s gone." }}</p>
</div>
'''


def q(v):
    """YAML double-quoted scalar."""
    return '"' + str(v).replace('\\', '\\\\').replace('"', '\\"') + '"'


def page(o):
    lines = ['---',
             '# Generated by tools/funnel/getridof/build_offers.py from the olympus upsell-single starter — edit the generator.',
             f'title: {q(o["title"] + " | Get Rid Of")}', 'page_type: upsell',
             f'next_url: {o["next"]}', f'decline_url: {o["decline"]}',
             'scripts:', '  - js/upsells.js', '  - js/payment-logos.js', 'styles:', '  - css/gro-checkout.css',
             f'announcement_text: {q(o["announce"])}', f'badge_note: {q(o["badge_note"])}',
             f'map_title: {q(o["map"][0])}', f'map_intro: {q(o["map"][1])}',
             'payment_flags:', '  show_visa: true', '  show_mastercard: true', '  show_american_express: true',
             '  show_discover: true', '  show_paypal: true', '  show_apple_pay: true',
             'upsell_hero:', '  variant: plain', f'  title: {q(o["hero_title"])}', f'  text: {q(o["hero_text"])}',
             'upsell_layout:', '  style: box', '  media: image', '  media_width: medium', '  show_bullets: true',
             '  show_decline: false', '  show_payment_logos: true',
             'upsell_offer:', '  type: single', '  pricing_mode: discounted', '  show_rating: false', '  package_id: 1',
             f'  quantity: {o["qty"]}', f'  voucher: {q(o["voucher"])}', f'  selector_id: {q(o["selector"])}',
             f'  title: {q(o["offer_title"])}', f'  image: {q(o["image"])}',
             f'  urgency_text: {q("&#9200; Limited-time offer · exclusive to you · only on this page")}',
             '  price_label: "Yours today"', f'  accept_text: {q(o["accept"])}',
             '  details_hint: "Where the extra pouches go ↓"', f'  decline_text: {q(o["decline_text"])}',
             'offer_bullets:'] + [f'  - {q(b)}' for b in o['bullets']] + [
             'upsell_body:', '  - type: features', f'    title: {q(o["features_title"])}', f'    text: {q(o["features_text"])}',
             '    items:'] + [x for t, d in FEATS for x in (f'      - title: {q(t)}', f'        text: {q(d)}')] + [
             'closing_cta:', '  variant: card', f'  title: {q(o["closing"])}',
             '  note: "Limited-time, exclusive offer. One click, no need to re-enter your card. Same 30-day money-back guarantee."',
             '---', '']
    return '\n'.join(lines)


def main():
    subprocess.run([sys.executable, str(HERE / 'house_map.py')], check=True)
    sys.path.insert(0, str(HERE))
    from house_map import CSS as MAP_CSS
    (CAMP / '_includes/gro-offer-badges.html').write_text(BADGES, encoding='utf-8')

    tpl = (HERE / 'olympus-upsell-single.template.html').read_text().split('---', 2)[2]
    tpl = tpl.replace("    {% campaign_include 'countdown-timer.html' countdown_timer=countdown_timer %}\n", '')
    hero = "    {% campaign_include 'upsell/hero.html' upsell_hero=upsell_hero %}\n"
    body = "    {% campaign_include 'upsell/body.html' upsell_body=upsell_body %}\n"
    assert hero in tpl and body in tpl
    tpl = tpl.replace(hero, "    {% campaign_include 'gro-offer-badges.html' badge_note=badge_note %}\n" + hero)
    tpl = tpl.replace(body, "    {% campaign_include 'gro-house-map.html' map_title=map_title map_intro=map_intro %}\n" + body)
    for name, o in OFFERS.items():
        (CAMP / f'{name}.html').write_text(page(o) + tpl, encoding='utf-8')

    gc = CAMP / 'assets/css/gro-checkout.css'
    base = gc.read_text().split('/* upsell palette')[0].split('/* gro: house map')[0]
    gc.write_text(base + PALETTE + MAP_CSS)
    f = CAMP / 'checkout.html'
    f.write_text(f.read_text().replace('next_url: receipt.html', 'next_url: upsell.html', 1))
    hb = CAMP / '_includes/upsell/header-bar.html'
    hb.write_text(hb.read_text().replace('images/next-dark.svg', 'pdp/gro-logo.svg'))
    print('wrote upsell, downsell, upsell-2, downsell-2 (checkout -> up1 -no-> up2 -no-> down2 -> receipt)')


if __name__ == '__main__':
    main()
