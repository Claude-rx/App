"""Gates for the built MedicLab Berberine funnel (campaigns/mediclab/_site/berberine/). Run after the Page Kit
build; exits 1 on any failure. --live additionally requires the pages to be wired to a campaign (a real apiKey).

usage: python3 -I tools/mediclab/check_funnel.py [--live]
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'campaigns' / 'mediclab' / '_site' / 'berberine'
PAGES = ['berberine', 'berberine-natural-glp1', 'weight-support', 'berberine-checkout', 'berberine-offer', 'berberine-thank-you']
WEIGHT = 'weight-support'   # the weight-management angle: GLP-1 / weight wording allowed, its compliance lines required
LISTICLE = 'berberine-natural-glp1'   # presell listicle, same angle: wording allowed, its own compliance lines required
FDA = 'These statements have not been evaluated by the Food and Drug Administration'
DEMO = ['LLbBgtusfE2zopDcjnOY9NbrlN690zSjuedqQ04J', 'demo.29next.com', 'TRUSTED BY 180,000', '19,569', 'Lorem ipsum',
        'Daniel K.', 'XXCODE', 'EXIT10', 'placehold.co', 'next-dark.svg', 'Product Name', 'Extended Warranty',
        'Package Title', 'Your headline', 'data-selected="true"', 'images/favicon.png', '#FF9425', 'Plus Jakarta']
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
for name in ('berberine', LISTICLE, WEIGHT, 'berberine-checkout', 'berberine-offer'):
    check(FDA in html[name], f'{name}: FDA disclaimer missing')

# The glucose sales page and the shared checkout, upsell and thank-you carry no GLP-1 or weight-loss claims; only the
# weight-management entry page (/weight-support/) uses that angle, with its own compliance lines below
# (the store's own FAQ answer, "Will it help me lose weight? We do not make that claim.", is the one allowed mention)
CLAIMS = re.compile(r'glp-?1|semaglutide|tirzepatide|ozempic|wegovy|weight[- ]loss plan|stubborn weight|lose weight|'
                    r'fat burn|appetite|cravings|natural ozempic', re.I)
ALLOWED = ('Will it help me lose weight?', 'we will not sell it as a weight-loss product')
for name, h in html.items():
    if name in (WEIGHT, LISTICLE):
        continue
    t = text(h)
    for a in ALLOWED:
        t = t.replace(a, '')
    t = re.sub(r'We do not make that claim\..{0,200}?weight-loss product\.', '', t, flags=re.S)
    found = sorted({m.group(0).lower() for m in CLAIMS.finditer(t)})
    check(not found, f'{name}: GLP-1 / weight-loss wording on the Berberine funnel: {found}')

s = html['berberine']
check(len(re.findall(r'<section id="s\d{2}"', s)) >= 20, 'sales page: sections missing (expected 20+)')
check('Supports healthy glucose metabolism*' in s, 'sales page: the glucose metabolism claim (with its asterisk) is missing')
check('Express is $5.97' not in s, 'sales page: promises express shipping the store does not sell')
check(s.count('data-cta') >= 6, 'sales page: CTAs missing')
for m in re.findall(r'<a[^>]+data-cta[^>]*>', s):
    check('/berberine-checkout/' in m and 'forceBundleId=plan' in m, f'sales page: CTA not pointing at the checkout plan card: {m[:120]}')
check('value="plan" checked' in s, 'sales page: monthly plan is not the default offer')
from collections import Counter
dup = [n for n, k in Counter(re.findall(r'<input[^>]*name="([^"]+)"[^>]*checked', s)).items() if k > 1]
check(not dup, f'sales page: radio group(s) {dup} pre-check more than one input (the browser keeps only the last)')
for label in ('Staged with models', 'No reviews here yet', 'not a medical endorsement'.capitalize(), '3-month minimum',
              'Is it safe with my medication?', 'About 73 mg'):
    check(label.lower() in s.lower(), f'sales page: compliance / honesty line "{label}" missing')

w = html[WEIGHT]
check(len(re.findall(r'id="s(0[1-9]|1\d|20)"', w)) == 20, 'weight page: not all 20 copy-deck sections present')
check('Express is $5.97' not in w, 'weight page: promises express shipping the store does not sell')
for m in re.findall(r'<a[^>]+data-cta[^>]*>', w):
    check('/berberine-checkout/' in m and 'forceBundleId=plan' in m, f'weight page: CTA not pointing at the checkout plan card: {m[:120]}')
check(w.count('data-cta') >= 3, 'weight page: CTAs missing')
for label in ('Example review', 'Model portrayal', 'Is this a GLP-1 medication?', 'contains no GLP-1, semaglutide or tirzepatide',
              'not a substitute for any prescription', "we don't promise pounds"):
    check(label.lower() in w.lower(), f'weight page: compliance line "{label}" missing')
check(w.count('class="wp-study"') >= 6, 'weight page: research cards missing (expected 6+)')
for blk in ('wp-pathway', 'wp-clinic', 'wp-timeline'):
    check(blk in w, f'weight page: {blk} block missing')
check('Yin J., Xing H., Ye J.' in w and 'Asbaghi' in w and 'Yu Y.' in w, 'weight page: study citations missing')
dupw = [n for n, k in Counter(re.findall(r'<input[^>]*name="([^"]+)"[^>]*checked', w)).items() if k > 1]
check(not dupw, f'weight page: radio group(s) {dupw} pre-check more than one input')

L = html[LISTICLE]
Lt = text(L)
check(len(re.findall(r'<section class="lc-item" id="r[1-8]"', L)) == 8, 'listicle: not exactly 8 numbered reasons')
for sec in ('id="root-problem"', 'id="root-solution"', 'id="compare"', 'id="faq"', 'id="offer"'):
    check(sec in L, f'listicle: section {sec} missing')
for sec in ('id="research"', 'id="timeline"', 'class="lc-pathway"', 'class="lc-checklist"'):
    check(sec in L, f'listicle: {sec} missing')
check(L.count('<tr>') >= 8, 'listicle: injection vs berberine comparison table incomplete')
check(L.count('data-cta') >= 4, 'listicle: CTAs missing')
for m in re.findall(r'<a[^>]+data-cta[^>]*>', L):
    check('/berberine-checkout/' in m and 'forceBundleId=' in m, f'listicle: CTA not pointing at a checkout card: {m[:120]}')
for label in ('Advertorial', 'is not a GLP-1 medication', 'contains no GLP-1, semaglutide or tirzepatide',
              'not a substitute for any prescription', "don't promise pounds", 'follow your doctor',
              'People shown are models', 'not affiliated with Novo Nordisk', 'Individual results vary'):
    check(label.lower() in Lt.lower(), f'listicle: compliance line "{label}" missing')
# no invented results, proof or urgency on a page aimed at cold traffic
for bad in (r'\blost \d+\s*(lbs?|pounds|kg)', r'\d+\s*(lbs?|pounds)\s+in\s+\d+', r'clinically proven', r'guaranteed (weight|results)',
            r'\b\d{2,3},\d{3}\+? (customers|women|people)', r'only \d+ (left|bottles)', r'(sale|offer) ends', r'works like ozempic'):
    check(re.search(bad, Lt, re.I) is None, f'listicle: banned claim pattern "{bad}"')
check('data-next-timer' not in L and 'countdown' not in L.lower(), 'listicle: countdown present (no fake urgency)')
for img in re.findall(r"images/ml/listicle/([\w-]+\.(?:jpg|mp4))", L):
    check((SITE / 'images' / 'ml' / 'listicle' / img).exists(), f'listicle: asset {img} missing from the build')

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
# any "N% off" stated on the upsell must be the real discount of $29.97 against $52.97 (43%), not the voucher's 45%
real = round((1 - 29.97 / 52.97) * 100)
for n in set(re.findall(r'(\d+)% off', u, re.I)):
    check(int(n) == real, f'upsell: says {n}% off, the real discount is {real}%')

t = html['berberine-thank-you']
check('What happens next' in t, 'thank-you: next-steps block missing')
check('every 30 days' in t, 'thank-you: refill reminder missing')

cfg = SITE.glob('**/config.js')
cfg_text = ''.join(p.read_text() for p in cfg)
if '--live' in sys.argv:
    check(re.search(r'apiKey:\s*"[A-Za-z0-9]{20,}"', cfg_text) is not None, 'config.js: not wired to a campaign (apiKey empty)')

if fails:
    print('FAIL'); [print(' -', f) for f in fails]; sys.exit(1)
print(f'OK: {len(PAGES)} pages pass the MedicLab funnel gates' + (' (live)' if '--live' in sys.argv else ''))
