"""The funnel the tools work on: one module per funnel under funnels/ (stick: the Adaptive Foundation Stick, the default;
apf: the Adaptive Peptide Foundation), chosen by the FUNNEL environment variable. Every tool does `import funnel as F`
and reads the chosen funnel's SLUG, CAMPAIGN_REF, PAGES, routes and meta tags from here.

    FUNNEL=apf python3 -I tools/funnel/deploy_theme.py campaigns/skinofab/_site/apf-funnel skinofab-theme

A funnel module defines: SLUG, CAMPAIGN_REF, LOCAL_SPEC_ID, FUNNEL_NAME, STORE, FUNNEL_HOST, STORE_ROUTE, TEMPLATE_PREFIX,
ASSET_DIR, SPEC_FILE, FUNNEL_ID, FUNNEL_LABEL, TITLES, EXIT_NOTE and PAGES (in funnel order; each page: id, file, type (the
CampaignSpec page type), sdk (the SDK page type), and its routing: next / success / accept / decline, plus packages,
default_package, exit_offer on a checkout and package(s) / offer(s) on an offer page).
"""
import importlib, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FUNNEL = os.environ.get('FUNNEL', 'stick')
_module = importlib.import_module(f'funnels.{FUNNEL}')
globals().update({k: v for k, v in vars(_module).items() if not k.startswith('_')})
BY_ID = {p['id']: p for p in PAGES}


def route(page_id, served=False):
    """A page's public route: /<slug>/<file>/ as Page Kit builds it, /<file>/ as the store serves it."""
    return (STORE_ROUTE if served else f'/{SLUG}/') + BY_ID[page_id]['file'] + '/'


def meta_tags(page):
    """The SDK meta tags a page carries (CampaignSpec sdk_hints.meta_tags; Page Kit frontmatter meta_tags)."""
    tags = {'next-funnel': FUNNEL_NAME, 'next-page-type': page['sdk']}
    if page.get('success'): tags['next-success-url'] = route(page['success'])
    if page.get('accept'): tags['next-upsell-accept-url'] = route(page['accept'])
    if page.get('decline'): tags['next-upsell-decline-url'] = route(page['decline'])
    return tags


def page_packages(page):
    """The package refs an offer page sells (one, or several tiers) and its vouchers' offer refs, in order."""
    packages = page.get('packages') or ([page['package']] if page.get('package') else [])
    offers = page.get('offers') or ([page['offer']] if page.get('offer') else [])
    return packages, offers
