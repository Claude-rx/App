"""Gates for the built MedicLab Berberine funnel (campaigns/mediclab/_site/berberine-glp1/). Run after the Page Kit
build; exits 1 on any failure. --live additionally requires the pages to be wired to a campaign (a real apiKey).

usage: python3 -I tools/mediclab/check_funnel.py [--live]
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'campaigns' / 'mediclab' / '_site' / 'berberine-glp1'
PAGES = ['glp1-support', 'berberine-checkout', 'berberine-offer', 'berberine-thank-you']
FDA = 'These statements have not been evaluated by the Food and Drug Administration'
DEMO = ['LLbBgtusfE2zopDcjnOY9NbrlN690zSjuedqQ04J', 'demo.29next.com', 'TRUSTED BY 180,000', '19,569', 'Lorem ipsum',
        'Daniel K.', 'XXCODE', 'EXIT10', 'placehold.co', 'next-dark.svg', 'Product Name', 'Extended Warranty']
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def text(p):
    return re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', p, flags=re.S))


html = {}
for name in PAGES:
    f = SITE / name / 'index.html'
    check(f.exists(), f'{name}: not built')
    html[name] = f.read_text() if f.exists() else ''

for name, h in html.items():
    for d in DEMO:
        check(d not in h, f'{name}: starter demo content "{d}"')
    check('mediclab.us/cart' not in h, f'{name}: links to the Shopify cart')
    check('Fustat' in h or 'mediclab-funnel.css' in h, f'{name}: not on the brand font')
    check('{{' not in h and '{%' not in h, f'{name}: unrendered Liquid')

# FDA disclaimer wherever a claim is made (sales page, checkout, upsell)
for name in ('glp1-support', 'berberine-checkout', 'berberine-offer'):
    check(FDA in html[name], f'{name}: FDA disclaimer missing')

s = html['glp1-support']
check(len(re.findall(r'id="s(0[1-9]|1\d|20)"', s)) == 20, 'sales page: not all 20 copy-deck sections present')
check('Express is $5.97' not in s, 'sales page: promises express shipping the store does not sell')
check(s.count('data-cta') >= 3, 'sales page: CTAs missing')
for m in re.findall(r'<a[^>]+data-cta[^>]*>', s):
    check('/berberine-checkout/' in m and 'forceBundleId=plan' in m, f'sales page: CTA not pointing at the checkout plan card: {m[:120]}')
check('value="plan" checked' in s, 'sales page: monthly plan is not the default offer')
for label in ('Example review', 'Model portrayal'):
    check(label in s, f'sales page: compliance label "{label}" missing')
check('not a GLP-1 medication' in s or 'Is this a GLP-1 medication?' in s, 'sales page: GLP-1 medication FAQ missing')

c = html['berberine-checkout']
check('data-next-bundle-id="plan"' in c and 'data-next-bundle-id="one"' in c, 'checkout: plan / one cards missing')
check(re.search(r'data-next-bundle-id="plan"[^>]*data-next-selected="true"', c) is not None, 'checkout: plan card not preselected')
check('$20.97' in c and '$42.97 every 30 days' in c, 'checkout: plan terms (price, renewal) not stated')
check('data-ml-plan-consent' in c and 'ml-plan-consent' in c, 'checkout: plan consent checkbox / script missing')
check('3-month minimum' in c, 'checkout: 3-month minimum not disclosed')
check('BERBERINE45' not in c, 'checkout: upsell voucher code exposed (it would stack at checkout)')
check('data-next-checkout="form"' in c, 'checkout: SDK form missing')

u = html['berberine-offer']
check('data-next-upsell="offer"' in u, 'upsell: SDK offer missing')
check('BERBERINE45' in u, 'upsell: voucher not wired')
check('data-next-upsell-action="add"' in u and 'data-next-upsell-action="skip"' in u, 'upsell: accept / skip missing')
check('data-next-timer' not in u and 'countdown' not in u.lower().replace('countdown-timer.html', ''),
      'upsell: countdown present (no fake urgency)')
check('$29.97' in u, 'upsell: one-time price not stated')

t = html['berberine-thank-you']
check('What happens next' in t, 'thank-you: next-steps block missing')
check('every 30 days' in t, 'thank-you: refill reminder missing')

cfg = (SITE.parent / 'berberine-glp1').glob('**/config.js')
cfg_text = ''.join(p.read_text() for p in cfg)
if '--live' in sys.argv:
    check(re.search(r'apiKey:\s*"[A-Za-z0-9]{20,}"', cfg_text) is not None, 'config.js: not wired to a campaign (apiKey empty)')

if fails:
    print('FAIL'); [print(' -', f) for f in fails]; sys.exit(1)
print(f'OK: {len(PAGES)} pages pass the MedicLab funnel gates' + (' (live)' if '--live' in sys.argv else ''))
