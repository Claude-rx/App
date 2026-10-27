"""The Adaptive Foundation Stick funnel: one source for its pages, routes, packages and offers.

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
BY_ID = {p['id']: p for p in PAGES}


def route(page_id, served=False):
    """A page's public route: /stick-funnel/<file>/ as Page Kit builds it, /<file>/ as the store serves it."""
    return (STORE_ROUTE if served else f'/{SLUG}/') + BY_ID[page_id]['file'] + '/'


def meta_tags(page):
    """The SDK meta tags a page carries (CampaignSpec sdk_hints.meta_tags; Page Kit frontmatter meta_tags)."""
    tags = {'next-funnel': FUNNEL_NAME, 'next-page-type': page['sdk']}
    if page.get('success'): tags['next-success-url'] = route(page['success'])
    if page.get('accept'): tags['next-upsell-accept-url'] = route(page['accept'])
    if page.get('decline'): tags['next-upsell-decline-url'] = route(page['decline'])
    return tags
