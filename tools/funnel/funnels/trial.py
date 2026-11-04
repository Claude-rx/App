"""The Adaptive Peptide Foundation flash trial funnel (FUNNEL=trial): its pages, routes, packages and offers.

    product page (the store's foundation page, copied, with the flash trial box)  ->  checkout (the trial)
    ->  offer 1 (stock up)  ->  offer 2 (one more bottle) / its downsell  ->  offer 3 (the Lymphatic Brush) / its downsell
    ->  thank you

The owner, 4 Nov 2026: "create a new campaign in next commerce for the adaptive peptide foundation but use our store
front pdp ... then a custom checkout after the upsells like the other campaign ... we will do a subscription with 39 usd
with 50% for the first month so 19.97 first month after will be 39.97 ... with a title like Trial offer limited time
today only", "like a flash trial offer", and the trial's clock "ends at her midnight": a countdown to midnight, her
time, from her first visit; after it the page shows the regular $39.97 a month and the checkout applies no code.

The commerce is campaign 2251 "SKINOFAB Adaptive Peptide Foundation Flash Trial", created on 4 Nov 2026 with the
next-campaigns-create skill (next-campaigns-create-runs/skinofab-apf-trial/, gitignored: its manifest holds the
campaign key). Package 1 is one bottle at $39.97 refilling every month at $39.97; FLASH50 (offer 1, 50% off, the
campaign's .97 rounding) makes the first order $19.97, and a code never reaches a refill. Packages 6 and 7 are the
packs beside it (4 Nov 2026): 3 bottles + a free Blender at $66.97 every 3 months (buy 2, get 1 free) and 5 bottles
+ a free Lymphatic Brush at $99.97 every 5 months (buy 3, get 2 free), the APF funnel's prices. The offers are bought once and
are APF's at the same prices (packages 2 to 5, codes APFT40, APFT50, BRUSHT40, BRUSHT60). The campaign's Allowed Domains
(try.skinofab.com) are a dashboard setting the API cannot write.

The product page is not a Page Kit page: tools/funnel/trial/pdp_copy.py writes it into the theme
(templates/pages/page.<file>.html) from the store's own foundation page, so it keeps the store's layout, photos,
reviews and the AppLovin app's pixel; 'native': True keeps deploy_theme.py from looking for it in the Page Kit build.
The other pages are Campaign Page Kit pages in campaigns/skinofab/src/trial-funnel/, served at /<file>/ on FUNNEL_HOST.
"""

SLUG = 'trial-funnel'
CAMPAIGN_REF = 2251
LOCAL_SPEC_ID = '4b8e2d61-9c3a-4f17-b0d5-7e1a6c2f9d38'     # the CampaignSpec's stable identity (never a Map ID)
FUNNEL_NAME = 'SKINOFAB Adaptive Peptide Foundation Flash Trial'
STORE = 'https://skinofab.29next.store'
FUNNEL_HOST = 'https://try.skinofab.com'
STORE_ROUTE = '/'
TEMPLATE_PREFIX = 'sft-'
ASSET_DIR = 'sft'
SPEC_FILE = 'campaign-spec.trial.json'
FUNNEL_ID, FUNNEL_LABEL = 'trial', 'Adaptive Peptide Foundation flash trial: product page to thank you'
EXIT_NOTE = ''
EMAIL = 'info@skinofab.com'
LIST_PRICE = 47.00                 # what the store charges for one bottle, bought once
STORE_ONCE = {1: 47.00, 2: 57.00}  # the store's one-time packs (bottles: price)


def store_once(bottles):
    """The least the store charges for this many bottles bought once (its 2-packs, then a single)."""
    return (bottles // 2) * STORE_ONCE[2] + (bottles % 2) * STORE_ONCE[1]


# the campaign's packages (the plan's keys): key -> ref
PACKAGE = {'trial': 1, 'apf-1-add': 2, 'apf-2': 3, 'apf-6-brush': 4, 'brush-1': 5, 'apf-3-blender': 6, 'apf-5-brush': 7}
# the vouchers: code -> offer ref
VOUCHER = {'FLASH50': 1, 'APFT40': 2, 'APFT50': 3, 'BRUSHT40': 4, 'BRUSHT60': 5}

# the trial: one bottle every month; today's price with the code, the price without it (the regular price, and every
# refill's), what the code takes off
TRIAL = {'package': 1, 'voucher': 'FLASH50', 'today': 19.97, 'regular': 39.97, 'off': 50, 'every': 'month',
         'name': 'Adaptive Peptide Foundation - 1 bottle', 'sku': 'SKF-APF-1'}
UNIT = TRIAL['regular']

# the packs beside the trial (the owner, 4 Nov 2026: "put the offer also of buy 2 get 1 free and buy 3 get 2 free", at
# the APF funnel's prices; packages 6 and 7, added that day through the create skill's update path): the checkout card
# id, the package, the bottles, what she pays today and at every refill, how many months apart, the crossed-out price
# (the bottles at the trial's $39.97 a bottle: the free bottles) and the gift in the first box
PACKS = [
    {'bundle': 'trial-3', 'package': 6, 'bottles': 3, 'paid': 2, 'price': 66.97, 'months': 3, 'compare': 119.91,
     'tab': 'Buy 2, get 1 FREE', 'gift': 'FREE Blender sponge', 'sku': 'SKF-APF-3-BLENDER'},
    {'bundle': 'trial-5', 'package': 7, 'bottles': 5, 'paid': 3, 'price': 99.97, 'months': 5, 'compare': 199.85,
     'tab': 'Buy 3, get 2 FREE', 'gift': 'FREE Lymphatic Brush', 'sku': 'SKF-APF-5-BRUSH'},
]

# the offer pages: as APF's, on this campaign's packages and codes
OFFER_PAGES = {
    'offer-1': {'id': 'offer-1', 'tiers': [
        {'key': 'b1g1', 'package': 'apf-2', 'ref': 3, 'bottles': 2, 'price': 39.00, 'compare': 57.00, 'badge': '8 weeks’ supply'},
        {'key': 'b3g3', 'package': 'apf-6-brush', 'ref': 4, 'bottles': 6, 'price': 99.00, 'compare': 171.00, 'badge': 'Best value', 'gift': 'brush'}]},
    'offer-2': {'id': 'offer-2', 'tiers': [{'key': 'one', 'package': 'apf-1-add', 'ref': 2, 'bottles': 1, 'voucher': 'APFT40', 'price': 19.00, 'compare': 33.97}]},
    'offer-2b': {'id': 'offer-2b', 'tiers': [{'key': 'one', 'package': 'apf-1-add', 'ref': 2, 'bottles': 1, 'voucher': 'APFT50', 'price': 15.00, 'compare': 33.97}]},
    'brush-offer': {'id': 'brush-offer', 'tiers': [{'key': 'brush', 'package': 'brush-1', 'ref': 5, 'voucher': 'BRUSHT40', 'price': 14.00, 'compare': 24.95}]},
    'brush-offer-b': {'id': 'brush-offer-b', 'tiers': [{'key': 'brush', 'package': 'brush-1', 'ref': 5, 'voucher': 'BRUSHT60', 'price': 9.00, 'compare': 24.95}]},
}

PAGES = [
    {'id': 'offer', 'file': 'adaptive-foundation-trial', 'type': 'landing', 'sdk': 'product', 'entry': True, 'native': True,
     'next': 'checkout', 'label': 'Product page: the store’s foundation page with the flash trial ($19.97 the first month, then $39.97 a month)'},
    {'id': 'checkout', 'file': 'trial-checkout', 'type': 'checkout', 'sdk': 'checkout', 'packages': [1, 6, 7],
     'default_package': 1, 'voucher_offer': 1, 'success': 'offer-1', 'label': 'Checkout: the flash trial'},
    {'id': 'offer-1', 'file': 'trial-offer-1', 'type': 'upsell', 'sdk': 'upsell', 'packages': [3, 4], 'offers': [],
     'accept': 'brush-offer', 'decline': 'offer-2', 'label': 'Offer 1: stock up (2 bottles at $19.50 each; 6 at $16.50 each + the brush)'},
    {'id': 'offer-2', 'file': 'trial-offer-2', 'type': 'upsell', 'sdk': 'upsell', 'packages': [2], 'offers': [2],
     'accept': 'brush-offer', 'decline': 'offer-2b', 'label': 'Offer 2: one more bottle, $19'},
    {'id': 'offer-2b', 'file': 'trial-offer-2b', 'type': 'downsell', 'sdk': 'upsell', 'packages': [2], 'offers': [3],
     'accept': 'brush-offer', 'decline': 'brush-offer', 'label': 'Offer 2 downsell: one more bottle, $15'},
    {'id': 'brush-offer', 'file': 'trial-brush-offer', 'type': 'upsell', 'sdk': 'upsell', 'packages': [5], 'offers': [4],
     'accept': 'thank-you', 'decline': 'brush-offer-b', 'label': 'Offer 3: the Lymphatic Brush, $14'},
    {'id': 'brush-offer-b', 'file': 'trial-brush-offer-b', 'type': 'downsell', 'sdk': 'upsell', 'packages': [5], 'offers': [5],
     'accept': 'thank-you', 'decline': 'thank-you', 'label': 'Offer 3 downsell: the Lymphatic Brush, $9'},
    {'id': 'thank-you', 'file': 'trial-thank-you', 'type': 'thankyou', 'sdk': 'receipt', 'label': 'Thank you'},
]

TITLES = {
    'offer': ('Adaptive Peptide Foundation: flash trial offer',
              'The Adaptive Peptide Foundation flash trial: $19.97 today, then $39.97 a month. Cancel any time.'),
    'checkout': ('Secure checkout', 'Checkout for the Adaptive Peptide Foundation flash trial.'),
    'offer-1': ('Special offer', 'A one-time offer for your order.'),
    'offer-2': ('Special offer', 'A one-time offer for your order.'),
    'offer-2b': ('Special offer', 'A one-time offer for your order.'),
    'brush-offer': ('Special offer: the Lymphatic Brush', 'A one-time offer for your order.'),
    'brush-offer-b': ('Special offer: the Lymphatic Brush', 'A one-time offer for your order.'),
    'thank-you': ('Thank you', 'Your order is confirmed.'),
}
