"""Paste-ready store policies for NEXT's checkout, from the store's own (company-updated) legal pages.

usage: python3 -I policy_texts.py <persona_export_dir> <out_dir>
Run after apply_persona.py. The hosted checkout's "Terms & Conditions" and "Privacy Policy" links open the policies
saved in the NEXT dashboard (the Admin API cannot set them); the defaults name "demo.29next.store". This writes
terms.html, privacy.html, refund.html and shipping.html: the same text as the store's pages, as plain HTML (headings,
paragraphs, lists, links), ready to paste into the dashboard's policy editor; and subscription-terms.html, the
Automatic Refills terms the product page already states (prices and interval from ccf_copy.PACKS and REFILL).
Fails when a page is missing, still names an old company, or does not name company.LEGAL_NAME.
"""
import re, sys
from pathlib import Path
from bs4 import BeautifulSoup, Comment

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ccf_copy, company

EXP, OUT = Path(sys.argv[1]), Path(sys.argv[2])
SOURCES = {'terms': ('pages/terms-of-service.html', 'main .rte'),
           'privacy': ('pages/privacy-policy.html', 'main .rte'),
           'refund': ('policies/refund-policy.html', '.shopify-policy__body .rte'),
           'shipping': ('policies/shipping-policy.html', '.shopify-policy__body .rte')}
KEEP = {'h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'a', 'br', 'table', 'tr', 'td', 'th'}
STALE = re.compile(r'Skinofab LLC|8605 Santa Monica|West Hollywood|(?:hey|info|contact)@skinofab\.com|demo\.29next', re.I)


def clean(el):
    for c in el.find_all(string=lambda s: isinstance(s, Comment)): c.extract()
    for t in el.find_all(['script', 'style', 'noscript', 'svg', 'img', 'button', 'form', 'input']): t.decompose()
    for t in el.find_all(True):
        if t.name not in KEEP: t.unwrap(); continue
        href = t.get('href') if t.name == 'a' else None
        t.attrs = {'href': href} if href and not href.startswith('#') else {}
    for p in el.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4']):
        if not p.get_text(strip=True): p.decompose()
    html = el.decode_contents()
    return re.sub(r'\n\s*\n+', '\n', re.sub(r'[ \t]+', ' ', html)).strip()


OUT.mkdir(parents=True, exist_ok=True)
bad = []
for name, (rel, sel) in SOURCES.items():
    f = EXP / rel
    if not f.exists(): bad.append(f'{name}: {rel} missing'); continue
    soup = BeautifulSoup(f.read_text(encoding='utf-8', errors='surrogateescape'), 'html.parser')
    el = soup.select_one(sel)
    if not el: bad.append(f'{name}: {sel} not found in {rel}'); continue
    html = clean(el)
    if STALE.search(html): bad.append(f'{name}: still names an old company')
    if name in ('terms', 'privacy') and company.LEGAL_NAME not in html: bad.append(f'{name}: does not name {company.LEGAL_NAME}')
    (OUT / f'{name}.html').write_text(html + '\n', encoding='utf-8')
    print(name, len(html), 'chars ->', OUT / f'{name}.html')
# the Automatic Refills terms, as the product page states them (nothing more is promised)
usd = lambda v: '$%d' % float(v) if float(v) == int(float(v)) else '$%.2f' % float(v)
one, two, every = ccf_copy.PACKS[0], ccf_copy.PACKS[1], ccf_copy.REFILL['every']
sub = f"""<h2>Automatic Refills: subscription terms</h2>
<p>{company.BRAND} is a brand of {company.LEGAL_NAME}, a {company.STATE} corporation, {company.ADDRESS_LINE}.</p>
<h3>What you agree to</h3>
<p>When you choose Automatic Refills for the Adaptive Peptide Foundation, you authorize {company.LEGAL_NAME} to charge your
payment method today and then every {every} days at the refill price of your pack: {usd(one['refill'])} for 1 bottle or
{usd(two['refill'])} for 2 bottles, plus any applicable taxes. Shipping is free. Each refill ships after it is charged.</p>
<h3>Reminders</h3>
<p>We email you before every refill.</p>
<h3>Skip or cancel anytime</h3>
<p>To skip a refill or cancel, email <a href="mailto:{company.EMAIL}">{company.EMAIL}</a> before your next refill date.
There is no minimum number of refills and no cancellation fee.</p>
<h3>Buying once instead</h3>
<p>You can buy without refills: choose One Time in your cart before checkout ({usd(one['price'])} for 1 bottle,
{usd(two['price'])} for 2 bottles).</p>
<h3>Refunds</h3>
<p>Refunds follow our refund policy and the 30-day money-back guarantee shown on the product page.</p>
<h3>Contact</h3>
<p>{company.LEGAL_NAME}, {company.ADDRESS_LINE}. Email: <a href="mailto:{company.EMAIL}">{company.EMAIL}</a></p>
"""
(OUT / 'subscription-terms.html').write_text(sub, encoding='utf-8')
print('subscription-terms', len(sub), 'chars ->', OUT / 'subscription-terms.html')
if bad: sys.exit('policy_texts: ' + '; '.join(bad))
