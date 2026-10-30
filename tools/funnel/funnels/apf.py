"""The Adaptive Peptide Foundation funnel (FUNNEL=apf): its pages, routes, packages and offers.

    listicle  ->  sales page  ->  checkout  ->  offer 1 (stock up)  ->  offer 2 (one more bottle) / its downsell
              ->  offer 3 (the Lymphatic Brush) / its downsell  ->  thank you

The commerce lives in its own campaign, 2221 "SKINOFAB Adaptive Peptide Foundation Funnel" (one campaign per product
funnel; the stick funnel keeps 2211), created on 28 Oct 2026 with the next-campaigns-create skill from a hand-authored
plan (next-campaigns-create-runs/skinofab-apf/, gitignored: its manifest holds the campaign key) and changed with its
update path on 29 Oct 2026, when the owner asked "make sure all is subscription": the checkout's three packs refill at
the same price (1 bottle every 28 days, 2 every 56, 3 every 84; the gifts come with the first order only), and the
offers stay one-time (offers 2 and 2b sell package 7, a one-time bottle of its own, so an add-on never starts a
subscription). On 30 Oct 2026 the owner made the offer "more aggressive, start at 33.97 only, with buy 2 get 1 free and
buy 3 get 2 free", the Blender with the 3 bottles and the Lymphatic Brush with the 5, no mystery gift: 1 bottle $33.97
every 28 days, 3 bottles $66.97 every 84 (under 2 x $33.97), 5 bottles $99.97 every 140 (under 3 x $33.97, $19.99 a bottle:
the owner's .97 prices, the same day), packages 1, 8 and 9 (2 and 3,
the packs before, stay in the campaign for the orders that name them, on no page); the add-on bottle $33.97 too, offer 2
at $19 and its downsell at $15. Nine packages and five vouchers, every price proven by the skill's verify against the Cart API. Package refs (data-next-package-id) and offer refs are the
campaign's own, read live by campaign_spec.py; this file says which page sells which and at what price (check_apf.py
holds every page to it; commerce.py --verify prices each through the Cart API). The campaign's Allowed Domains
(try.skinofab.com) are a dashboard setting the API cannot write. Prices: the store sells one bottle at $47 once or $37 with refills, two at $57 once or $47
with refills. The checkout's crossed-out prices are its own 1-bottle price times the bottles (the free bottles, nothing else);
offer 1's are the store's one-time price for the same bottles.

The pages are Campaign Page Kit pages in campaigns/skinofab/src/apf-funnel/ (file = the page's name there), served by
the store at /<file>/ (deploy_theme.py, store_pages.py) on FUNNEL_HOST, the store domain the campaign allows.
"""

SLUG = 'apf-funnel'
CAMPAIGN_REF = 2221
LOCAL_SPEC_ID = '7c1f4a0e-5b2d-4e8f-9a63-2d9f0c8b1e47'     # the CampaignSpec's stable identity (never a Map ID)
FUNNEL_NAME = 'SKINOFAB Adaptive Peptide Foundation'       # next-funnel on every page (campaigns.json "name")
STORE = 'https://skinofab.29next.store'
FUNNEL_HOST = 'https://try.skinofab.com'
STORE_ROUTE = '/'
TEMPLATE_PREFIX = 'sfa-'
ASSET_DIR = 'sfa'
SPEC_FILE = 'campaign-spec.apf.json'
FUNNEL_ID, FUNNEL_LABEL = 'apf', 'Adaptive Peptide Foundation: listicle to thank you'
EXIT_NOTE = 'Once per visit, on leaving the checkout: 10% off the foundation packs.'
EMAIL = 'info@skinofab.com'
LIST_PRICE = 47.00                 # what the store charges for one bottle, bought once
STORE_ONCE = {1: 47.00, 2: 57.00}  # the store's one-time packs (bottles: price), skinofab.com 29 Oct 2026


def store_once(bottles):
    """The least the store charges for this many bottles bought once (its 2-packs, then a single)."""
    return (bottles // 2) * STORE_ONCE[2] + (bottles % 2) * STORE_ONCE[1]


# LIST_PRICE: live review 2, a $59 list price above the $47 the pages themselves quote was an unsubstantiated reference;
# the store's own $47 is the honest one

# the campaign's packages (the plan's keys, tools/funnel/apf/commerce.py): key -> ref
PACKAGE = {'apf-1': 1, 'apf-2-gifts': 2, 'apf-3-gifts': 3, 'apf-2': 4, 'apf-6-brush': 5, 'brush-1': 6, 'apf-1-add': 7,
           'apf-3-blender': 8, 'apf-5-brush': 9}
# the vouchers: code -> offer ref
VOUCHER = {'APF10': 1, 'APF40': 2, 'APF50': 3, 'BRUSH40': 4, 'BRUSH60': 5}

# the sales page's and checkout's packs (Automatic Refills at the same price, free shipping): the checkout card id, the
# package, what she pays today and at every refill, how many days apart (every: 28 a bottle), the crossed-out price (the
# 1-bottle price times the bottles: the free bottles; the price is at most the 1-bottle price times the bottles she pays
# for, 'paid') and the gift in the first box (refills are the bottles only)
UNIT = 33.97                       # one bottle with refills, the price every free-bottle claim is counted against
PACKS = [
    {'key': 'apf-1', 'bundle': 'apf-1', 'package': 1, 'bottles': 1, 'paid': 1, 'price': 33.97, 'every': 28, 'gifts': [],
     'name': '1 bottle', 'supply': 'About a month'},
    {'key': 'apf-3-blender', 'bundle': 'apf-3', 'package': 8, 'bottles': 3, 'paid': 2, 'price': 66.97, 'compare': 101.91, 'every': 84,
     'gifts': ['blender'], 'name': '3 bottles', 'supply': 'About three months', 'tab': 'Buy 2, get 1 FREE'},
    {'key': 'apf-5-brush', 'bundle': 'apf-5', 'package': 9, 'bottles': 5, 'paid': 3, 'price': 99.97, 'compare': 169.85, 'every': 140,
     'gifts': ['brush'], 'name': '5 bottles', 'supply': 'About five months', 'selected': True, 'tab': 'Buy 3, get 2 FREE · Best value'},
]
GIFTS = {'blender': ('SKINOFAB Blender sponge', None), 'brush': ('The Lymphatic Brush', 24.95)}

# the offer pages: each tier's package, voucher (none: the package's own price is the price), what she pays (the
# campaign rounds a voucher's price down to the dollar) and the crossed-out price (offer 1: the store's one-time price for
# the same bottles, store_once; offers 2 and 3: the package's own price)
OFFER_PAGES = {
    'offer-1': {'id': 'offer-1', 'tiers': [
        {'key': 'b1g1', 'package': 'apf-2', 'ref': 4, 'bottles': 2, 'price': 39.00, 'compare': 57.00, 'badge': 'Two months’ supply'},
        {'key': 'b3g3', 'package': 'apf-6-brush', 'ref': 5, 'bottles': 6, 'price': 99.00, 'compare': 171.00, 'badge': 'Best value', 'gift': 'brush'}]},
    'offer-2': {'id': 'offer-2', 'tiers': [{'key': 'one', 'package': 'apf-1-add', 'ref': 7, 'bottles': 1, 'voucher': 'APF40', 'price': 19.00, 'compare': 33.97}]},
    'offer-2b': {'id': 'offer-2b', 'tiers': [{'key': 'one', 'package': 'apf-1-add', 'ref': 7, 'bottles': 1, 'voucher': 'APF50', 'price': 15.00, 'compare': 33.97}]},
    'brush-offer': {'id': 'brush-offer', 'tiers': [{'key': 'brush', 'package': 'brush-1', 'ref': 6, 'voucher': 'BRUSH40', 'price': 14.00, 'compare': 24.95}]},
    'brush-offer-b': {'id': 'brush-offer-b', 'tiers': [{'key': 'brush', 'package': 'brush-1', 'ref': 6, 'voucher': 'BRUSH60', 'price': 9.00, 'compare': 24.95}]},
}

# the pages in funnel order. type: the CampaignSpec page type; sdk: the SDK page type (Page Kit page_type).
PAGES = [
    {'id': 'listicle', 'file': '10-reasons-adaptive-foundation', 'type': 'presell', 'sdk': 'product', 'entry': True,
     'next': 'offer', 'label': 'Listicle: 10 reasons women over 45 look fresher with this shade-adapting foundation'},
    {'id': 'offer', 'file': 'adaptive-foundation-offer', 'type': 'landing', 'sdk': 'product', 'next': 'checkout',
     'label': 'Sales page: the 20-section long page, 1 bottle, buy 2 get 1 free, buy 3 get 2 free, refills at the same price'},
    {'id': 'checkout', 'file': 'foundation-checkout', 'type': 'checkout', 'sdk': 'checkout', 'packages': [1, 8, 9],
     'default_package': 9, 'success': 'offer-1', 'exit_offer': 1, 'label': 'Checkout'},
    {'id': 'offer-1', 'file': 'foundation-offer-1', 'type': 'upsell', 'sdk': 'upsell', 'packages': [4, 5], 'offers': [],
     'accept': 'brush-offer', 'decline': 'offer-2', 'label': 'Offer 1: stock up (2 bottles at $19.50 each; 6 at $16.50 each + the brush)'},
    {'id': 'offer-2', 'file': 'foundation-offer-2', 'type': 'upsell', 'sdk': 'upsell', 'packages': [7], 'offers': [2],
     'accept': 'brush-offer', 'decline': 'offer-2b', 'label': 'Offer 2: one more bottle, $19'},
    {'id': 'offer-2b', 'file': 'foundation-offer-2b', 'type': 'downsell', 'sdk': 'upsell', 'packages': [7], 'offers': [3],
     'accept': 'brush-offer', 'decline': 'brush-offer', 'label': 'Offer 2 downsell: one more bottle, $15'},
    {'id': 'brush-offer', 'file': 'lymphatic-brush-offer', 'type': 'upsell', 'sdk': 'upsell', 'packages': [6], 'offers': [4],
     'accept': 'thank-you', 'decline': 'brush-offer-b', 'label': 'Offer 3: the Lymphatic Brush, 40% off'},
    {'id': 'brush-offer-b', 'file': 'lymphatic-brush-offer-b', 'type': 'downsell', 'sdk': 'upsell', 'packages': [6], 'offers': [5],
     'accept': 'thank-you', 'decline': 'thank-you', 'label': 'Offer 3 downsell: the Lymphatic Brush, 60% off'},
    {'id': 'thank-you', 'file': 'foundation-thank-you', 'type': 'thankyou', 'sdk': 'receipt', 'label': 'Thank you'},
]

# the store pages' titles and descriptions (store_pages.py)
TITLES = {
    'listicle': ('10 Reasons Why Women Over 45 Look Fresher With This Shade-Adapting Foundation',
                 'The serum foundation that goes on white and adapts to your skin tone as you blend. Made for skin after 45.'),
    'offer': ('Adaptive Peptide Foundation: your shade, without guessing',
              'One adaptive shade in a hydrating serum base with PDRN and peptides. From $19.99 a bottle: buy 3, get 2 free, or buy 2, get 1 free. 30-day guarantee.'),
    'checkout': ('Secure checkout', 'Checkout for the Adaptive Peptide Foundation.'),
    'offer-1': ('Special offer', 'A one-time offer for your order.'),
    'offer-2': ('Special offer', 'A one-time offer for your order.'),
    'offer-2b': ('Special offer', 'A one-time offer for your order.'),
    'brush-offer': ('Special offer: the Lymphatic Brush', 'A one-time offer for your order.'),
    'brush-offer-b': ('Special offer: the Lymphatic Brush', 'A one-time offer for your order.'),
    'thank-you': ('Thank you', 'Your order is confirmed.'),
}

# the design source Campaigns OS reads (tools/funnel/design_source.py): the Facelove listicle the stick funnel's listicle
# also follows, and the store's own Adaptive Peptide Foundation page the sales page draws its photos and structure from
DESIGN_SOURCE = {'dir': 'design-source-apf', 'designed': {'listicle': 'facelove-listicle.html', 'offer': 'apf-pdp.html'},
                 'captured': {'listicle': '2026-10-27T09:41:00Z', 'offer': '2026-10-28T08:45:00Z'}}
