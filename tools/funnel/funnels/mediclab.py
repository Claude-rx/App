"""The MedicLab Berberine funnels (FUNNEL=mediclab), one product and one campaign (2475), two entry pages: the healthy
glucose metabolism sales page /berberine/ and the weight-management angle /weight-support/; then the shared sales page -> checkout -> one upsell -> thank you, on the Mediclab
store (mediclab.29next.store), served at https://try.mediclab.us, the store's primary domain.

Campaign only, no storefront: every page is a standalone theme template with no base layout (deploy_theme.py), so the
Campaign Cart SDK owns the page and the storefront's cart, checkout and scripts never load. The theme's other routes
(home, catalogue, cart, search, 404) send the visitor to the sales page (mediclab-theme/, tools/mediclab/theme.py).

The pages are Campaign Page Kit pages in campaigns/mediclab/src/berberine/ (file = the page's name there). The
campaign is created by the next-campaigns-create engine from tools/mediclab/campaign_plan.py (run kept outside git in
next-campaigns-create-runs/mediclab/); its package ids reach the pages through tools/mediclab/wire_funnel.py.
"""

SLUG = 'berberine'
CAMPAIGN_REF = None                      # set once the campaign exists (campaigns/mediclab/funnel-ids.json)
LOCAL_SPEC_ID = None
FUNNEL_NAME = 'MedicLab Berberine'
BRAND = 'MedicLab'                       # store page meta titles (store_pages.py)
PROJECT = 'campaigns/mediclab'           # the Page Kit project (deploy_theme.py's GENERATED marker)
STORE = 'https://mediclab.29next.store'
FUNNEL_HOST = 'https://try.mediclab.us'
STORE_ROUTE = '/'
PAGE_TEMPLATES = False                   # store pages keep an empty template: pages/page.html renders them by slug
                                         # (tools/mediclab/theme.py; this store fails {% include %} and ignores the choice in preview)
TEMPLATE_PREFIX = 'mlb-'
PAGES = [
    {'id': 'sales', 'file': 'berberine', 'type': 'presell', 'sdk': 'product', 'entry': True, 'next': 'checkout',
     'label': 'Sales page: the Open-Door Meal Routine, healthy glucose metabolism (mediclab.us product page copy)'},
    {'id': 'listicle', 'file': 'berberine-natural-glp1', 'type': 'presell', 'sdk': 'product', 'next': 'checkout',
     'label': 'Presell listicle for cold traffic: 8 reasons, root problem/solution, GLP-1 injection comparison'},
    {'id': 'weight', 'file': 'weight-support', 'type': 'presell', 'sdk': 'product', 'next': 'checkout',
     'label': 'Sales page, weight-management angle (the delivered copy deck), same product and checkout'},
    {'id': 'checkout', 'file': 'berberine-checkout', 'type': 'checkout', 'sdk': 'checkout', 'success': 'offer',
     'label': 'Checkout: monthly plan ($20.97, then $42.97 every 30 days) or one bottle ($52.97)'},
    {'id': 'offer', 'file': 'berberine-offer', 'type': 'upsell', 'sdk': 'upsell', 'accept': 'thank-you',
     'decline': 'thank-you', 'label': 'Upsell: one more bottle, one-time, $29.97'},
    {'id': 'thank-you', 'file': 'berberine-thank-you', 'type': 'thankyou', 'sdk': 'receipt', 'label': 'Thank you'},
]
ASSET_DIR = 'mlb'
SPEC_FILE = None
FUNNEL_ID, FUNNEL_LABEL = 'mediclab-berberine', 'MedicLab Berberine: sales page to thank you'
TITLES = {
    'sales': ('MedicLab Berberine: a routine for the hours after you eat',
              'Two capsules with meals and a few minutes of walking after you eat, a daily routine that supports healthy '
              'glucose metabolism.* 60-day empty-bottle guarantee.'),
    'listicle': ('8 Reasons Everyone Over 40 Is Using Berberine, the "Natural GLP-1", in Their Weight-Loss Plan',
                 "After 40, your body's own fullness signal gets quieter. Why adults are adding berberine to their "
                 'weight-loss plan instead of a needle, and how it compares with a GLP-1 injection.'),
    'weight': ('Natural GLP-1 Support for Adults 40+ Done Fighting Stubborn Weight',
               'MedicLab Berberine: two capsules with meals, protein first, a 10-minute walk after dinner. '
               '60-day empty-bottle guarantee.'),
    'checkout': ('Secure checkout', 'Checkout for MedicLab Berberine.'),
    'offer': ('One more bottle', 'A one-time offer for your order.'),
    'thank-you': ('Thank you', 'Your order is confirmed.'),
}
EXIT_NOTE = ''
