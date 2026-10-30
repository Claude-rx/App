"""The Adaptive Foundation Stick funnel (FUNNEL=stick, the default): its pages, routes, packages and offers.
The Adaptive Foundation Stick funnel: one source for its pages, routes, packages and offers.

    listicle  ->  product page  ->  checkout  ->  special offers 1-4 (post-purchase)  ->  thank you

The commerce lives in the Campaigns App campaign 2211 "SKINOFAB Foundation Stick Funnel" (made with the
next-campaigns-create engine, run kept outside git in next-campaigns-create-runs/skinofab/). Every package is a
subscription, as the owner asked ("all subscription"): the stick ships every 28 days (1 stick) or 56 days (2 sticks
+ the free Lymphatic Brush), the balm every 28, the serum every 56 and the brush every 90. An upsell's voucher takes
its discount off the first charge only; the renewals are at the package's recurring price, and each page says so.

Package refs (data-next-package-id) and offer refs are the campaign's own, read live by campaign_spec.py; this file
only says which page sells which. The pages are Campaign Page Kit pages in campaigns/skinofab/src/stick-funnel/
(file = the page's name there), served by the store itself at /<file>/ (deploy_theme.py turns the built pages
into theme templates, store_pages.py creates the store pages that render them), on FUNNEL_HOST: the store domain the
campaign allows. The SDK's calls are refused from any other host, so the pages send a visit on another host there.

The helpers (route, meta_tags, BY_ID) are funnel.py's, shared with every funnel.
"""

SLUG = 'stick-funnel'                    # the Page Kit campaign slug (campaigns/skinofab/src/<SLUG>/)
CAMPAIGN_REF = 2211                      # the Campaigns App campaign id
LOCAL_SPEC_ID = '1b7c62ea-589f-49eb-83f9-31869ed0c283'   # the CampaignSpec's stable identity (never a Map ID)
FUNNEL_NAME = 'SKINOFAB Foundation Stick'                # next-funnel on every page (campaigns.json "name")
STORE = 'https://skinofab.29next.store'  # the store's own host: its Admin API (store_pages.py)
FUNNEL_HOST = 'https://try.skinofab.com'  # where the funnel is served: a store domain the Campaigns App allows (CORS)
STORE_ROUTE = '/'                        # the store serves each page at /<file>/ (as its /faq/ and /contact/)
TEMPLATE_PREFIX = 'sfc-'                 # theme template page.<file>.html; assets sfc-<name>-<hash>.<ext>

# the pages in funnel order. type: the CampaignSpec page type; sdk: the SDK page type (Page Kit page_type).
PAGES = [
    {'id': 'listicle', 'file': '10-reasons-foundation-stick', 'type': 'presell', 'sdk': 'product', 'entry': True,
     'next': 'offer', 'label': 'Listicle: 10 reasons women past 45 switch to the stick'},
    {'id': 'offer', 'file': 'foundation-stick-offer', 'type': 'landing', 'sdk': 'product', 'next': 'checkout',
     'label': 'Product page: choose 1 stick or 2 sticks + a free Lymphatic Brush'},
    {'id': 'checkout', 'file': 'stick-checkout', 'type': 'checkout', 'sdk': 'checkout', 'packages': [1, 2],
     'default_package': 2, 'success': 'special-1', 'exit_offer': 5, 'label': 'Checkout'},
    {'id': 'special-1', 'file': 'stick-special-1', 'type': 'upsell', 'sdk': 'upsell', 'package': 1, 'offer': 1,
     'accept': 'special-2', 'decline': 'special-2', 'label': 'Special offer 1: one more stick, 50% off'},
    {'id': 'special-2', 'file': 'stick-special-2', 'type': 'upsell', 'sdk': 'upsell', 'package': 3, 'offer': 2,
     'accept': 'special-3', 'decline': 'special-3', 'label': 'Special offer 2: the Lymphatic Brush, 20% off'},
    {'id': 'special-3', 'file': 'stick-special-3', 'type': 'upsell', 'sdk': 'upsell', 'package': 4, 'offer': 3,
     'accept': 'special-4', 'decline': 'special-4', 'label': 'Special offer 3: the PDRN Plumping Balm, 20% off'},
    {'id': 'special-4', 'file': 'stick-special-4', 'type': 'upsell', 'sdk': 'upsell', 'package': 5, 'offer': 4,
     'accept': 'thank-you', 'decline': 'thank-you', 'label': 'Special offer 4: the EGF + NAD+ Firming Serum, 20% off'},
    {'id': 'thank-you', 'file': 'stick-thank-you', 'type': 'thankyou', 'sdk': 'receipt', 'label': 'Thank you'},
]
ASSET_DIR = 'sfc'                        # the theme's asset folder for this funnel's assets (deploy_theme.py)
SPEC_FILE = 'campaign-spec.json'         # the CampaignSpec campaign_spec.py writes (campaigns/skinofab/)
FUNNEL_ID, FUNNEL_LABEL = 'stick', 'Foundation Stick: listicle to thank you'
# the store pages' titles and descriptions (store_pages.py)
TITLES = {
    'listicle': ('10 Reasons Women Over 45 Look Fresher With This Shade-Adapting Foundation Stick',
                 'The foundation stick that goes on white and meets your own skin tone as you blend, with the brush built in.'),
    'offer': ('Adaptive Foundation Stick: choose your pack', 'One shade that adapts to fair to medium skin, brush built in. 30-day guarantee.'),
    'checkout': ('Secure checkout', 'Checkout for the Adaptive Foundation Stick.'),
    'special-1': ('Special offer 1', 'A one-time offer for your order.'),
    'special-2': ('Special offer 2', 'A one-time offer for your order.'),
    'special-3': ('Special offer 3', 'A one-time offer for your order.'),
    'special-4': ('Special offer 4', 'A one-time offer for your order.'),
    'thank-you': ('Thank you', 'Your order is confirmed.'),
}
# the checkout's exit offer and what the offer pages' packages and vouchers are, as campaign_spec.py reads them
EXIT_NOTE = 'Once per visit, on leaving the checkout: 10% off the stick packs.'

# the design source Campaigns OS reads (tools/funnel/design_source.py): where it is, which pages were designed from a
# capture (the rest are Apollo template stock), and when each capture was made
DESIGN_SOURCE = {'dir': 'design-source', 'designed': {'listicle': 'facelove-listicle.html', 'offer': 'stick-pdp.html'},
                 'captured': {'listicle': '2026-10-27T09:41:00Z', 'offer': '2026-10-27T09:41:00Z'}}
