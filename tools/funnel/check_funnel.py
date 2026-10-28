"""Offline checks of the funnel, run by tools/build_store.sh after the funnel is deployed into the theme: they fail
the build when a page drifts from the campaign or from the claims the brand may make.

usage: python3 -I tools/funnel/check_funnel.py [<theme dir>]      (default: skinofab-theme)

Reads the CampaignSpec (campaigns/skinofab/campaign-spec.json, the live campaign as campaign_spec.py read it), the
built pages (campaigns/skinofab/_site/stick-funnel/) and the theme templates deploy_theme.py wrote. Checks:
  routes      every page is built, carries the SDK meta tags funnel.py gives it, and links only to funnel routes
  checkout    one card per checkout package, one selected, each card's "Then $X every N days" = the package's
              recurring price and interval; no coupon box; no post-purchase voucher code anywhere on the page; the
              guarantee right above the order button, 8+ review cards each with the buyer's photo, the liquid's rating
  offers      each offer's package and voucher are the campaign's; the renewal sentence states the package's
              recurring price and interval; the fallback price is the voucher's price rounded down to dollars
  product     each pack card's price and interval are its package's; every checkout link names a checkout card
  thank you   each package's renewal line (by its SKU) is its recurring price and interval
  host        each page sends other hosts to funnel.FUNNEL_HOST; its policy links are on it
  theme       a template per page, marked GENERATED, no Page Kit route left, every asset it names on disk
  claims      none of the claims the brand may not make (stick_copy.py, the SKF-ADFS-001 section 8 rules)
"""
import json, re, sys
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funnel as F

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'campaigns' / 'skinofab'
SITE = PROJECT / '_site' / F.SLUG
THEME = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'skinofab-theme')
SPEC = json.loads((PROJECT / 'campaign-spec.json').read_text())
PAGES = {p['id']: p for p in SPEC['funnels'][0]['pages']}
OFFERS = {o['ref_id']: o for o in SPEC['offers']}
# what the pages may never say (the stick's claims rules; "made not to" / "designed not to" keep "settle" hedged)
FORBIDDEN = [
    (r'\b(?:reverses?|reversing)\s+(?:aging|ageing|the clock|time)', 'reverses aging'),
    (r'\bage[- ]reversing\b', 'age-reversing'),
    (r'\blook(?:s)?\s+(?:10|15|20)\s+years\s+younger', 'look N years younger'),
    (r'\bproduces?\s+collagen', 'produces collagen'),
    (r'\b(?:all|every)\s+skin\s+tones?\b', 'every skin tone'),
    (r'\bdermatologists?[- ](?:recommended|approved|tested|developed)', 'dermatologist endorsement'),
    (r'\b\d{1,3}\s?%\s+of\s+(?:women|users|customers|testers)', 'study percentage'),
    (r"\b(?:won['’]t|will not|never)\s+settle", 'unhedged "won\'t settle"'),
    (r'\bonly\s+\d+\s+(?:left|pieces|in stock)', 'scarcity count'),
    # every package recurs: an offer is only on its page, never "one-time" (funnel review 1); the order is placed
    (r'\bone-time offer\b', '"one-time offer" on a recurring item'),
    (r"order isn[’']t complete", '"your order isn\'t complete" after the order is placed'),
    (r"\bdon[’']t close this page\b", 'pressure: "don\'t close this page"'),
    (r'\bfrom 10 ?AM\b.{0,20}\b10 ?PM\b', '12-hour wear'),
    # funnel review 2: the reviews are the liquid's published ones from the earlier store, not "every review"; no
    # "further" discount where there was none; the balm is no filler
    (r'\bevery review\b', '"every review" (the imported reviews are the published ones)'),
    (r'\bsave a further\b', '"a further" discount with no first one'),
    (r'\bfuller\b.{0,30}\bin seconds\b', 'instant plumping'),
    (r"\blines foundation can[’']t fill\b", 'filling lines'),
    (r'\bno cakey lines\b', 'unhedged "no cakey lines"'),
]
SPF_OK = re.compile(r'(?:no|not a|has no|without|doesn[’\']t have|does it have)\s+(?:an?\s+)?SPF|SPF\?|your (?:daily )?(?:SPF|sunscreen)|over your SPF', re.I)
problems = []


def fail(where, what): problems.append(f'{where}: {what}')


def html(page_id): return (SITE / F.BY_ID[page_id]['file'] / 'index.html').read_text(encoding='utf-8')


def text(h):
    h = re.sub(r'<(script|style|template)\b.*?</\1>', ' ', h, flags=re.S | re.I)
    return unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)))


def money(v): return f'${float(v):.2f}'


# routes ------------------------------------------------------------------------------------------------------------
routes = {F.route(p['id']) for p in F.PAGES}
for p in F.PAGES:
    path = SITE / p['file'] / 'index.html'
    if not path.is_file(): fail(p['id'], f'not built ({path})'); continue
    h = path.read_text(encoding='utf-8')
    for name, value in F.meta_tags(p).items():
        if f'<meta name="{name}" content="{value}">' not in h: fail(p['id'], f'meta {name}={value} missing')
    for link in re.findall(r'href="(/' + F.SLUG + r'/[a-z0-9-]+/)(?=["?#])', h):      # pages, not asset folders
        if link not in routes: fail(p['id'], f'link to a page outside the funnel: {link}')
    if PAGES[p['id']].get('sdk_hints', {}).get('meta_tags') != F.meta_tags(p): fail(p['id'], 'CampaignSpec meta tags differ from funnel.py')

# checkout ----------------------------------------------------------------------------------------------------------
co = html('checkout')
cards = re.findall(r"<div data-next-bundle-card data-next-bundle-id=\"([^\"]+)\"[^>]*?data-next-bundle-items='([^']+)'([^>]*)>(.*?)</div>\s*</div>\s*</div>", co, re.S)
pkgs = {p['ref_id']: p for p in PAGES['checkout']['packages']}
if len(cards) != len(pkgs): fail('checkout', f'{len(cards)} pack cards for {len(pkgs)} packages')
if sum('data-next-selected="true"' in c[2] for c in cards) != 1: fail('checkout', 'not exactly one selected card')
for bid, items, attrs, body in cards:
    ref = json.loads(items)[0]['packageId']
    if ref not in pkgs: fail('checkout', f'card {bid} sells package {ref}, not a checkout package'); continue
    want = f'Then {money(pkgs[ref]["price_recurring"])} every {pkgs[ref]["interval_count"]} days'
    if want not in text(body): fail('checkout', f'card {bid}: "{want}" missing')
if re.search(r'data-next-coupon=', co): fail('checkout', 'a coupon box (post-purchase vouchers could be typed in)')
for o in OFFERS.values():
    if o['code'] != OFFERS[PAGES['checkout']['exit_intent']['offer_ref_id']]['code'] and o['code'] in co:
        fail('checkout', f'post-purchase voucher {o["code"]} appears on the checkout')
if f'data-coupon-code="{PAGES["checkout"]["exit_intent"]["offer_code"]}"' not in co: fail('checkout', 'exit pop does not apply the exit offer')
# the checkout sells on trust: the guarantee right above the order button, the review wall with each buyer's own photo,
# and the liquid's ratings as the listicle and product page give them
g, btn = co.find('data-sf-guarantee-inline'), co.find('COMPLETE MY ORDER')
if g < 0 or btn < 0 or g > btn: fail('checkout', 'no guarantee line right above the order button')
cards_r = re.findall(r'<article class="sf-co-review">(.*?)</article>', co, re.S)
if len(cards_r) < 8: fail('checkout', f'{len(cards_r)} review cards, not at least 8')
if any('<img ' not in c for c in cards_r): fail('checkout', 'a review card without its buyer\'s photo')
if '4.8 out of 5' not in co or '9,855 reviews' not in co: fail('checkout', 'the rating is not the liquid\'s 4.8 from 9,855 reviews')
# the buyers wrote no titles: none is put on their reviews (checkout review: an invented title read as theirs); and on a
# phone, where the proof column follows the button, three reviews come before the payment step
if 'sf-co-review__title' in co: fail('checkout', 'a title on a review (the buyers wrote none)')
f, pay = co.find('id="sf-co-featured"'), co.find('Step 4: Payment')
if f < 0 or f > pay: fail('checkout', 'no reviews before the payment step on a phone')

# special offers ----------------------------------------------------------------------------------------------------
for pid in ('special-1', 'special-2', 'special-3', 'special-4'):
    h, spec_pg = html(pid), PAGES[pid]
    pkg, offer = spec_pg['packages'][0], OFFERS[spec_pg['offers'][0]['ref_id']]
    if f'data-next-upsell="offer" data-next-await="" data-next-package-id="{pkg["ref_id"]}"' not in h:
        fail(pid, f'offer wrapper is not package {pkg["ref_id"]}')
    sel = re.search(r'<div data-next-bundle-selector data-next-upsell-context[^>]*>.*?</div>\s*</div>', h, re.S)
    if not sel or f'["{offer["code"]}"]' not in sel.group(0) or f'"packageId":{pkg["ref_id"]}' not in sel.group(0):
        fail(pid, f'no upsell-context selector adding package {pkg["ref_id"]} with {offer["code"]}')
    want = f'After that, {money(pkg["price_recurring"])} every {pkg["interval_count"]} days'
    if want not in text(h): fail(pid, f'"{want}" missing')
    landed = int(float(pkg['price']) * (100 - float(offer['benefit']['value'])) / 100)
    if f'>${landed:.2f}<' not in h: fail(pid, f'fallback price ${landed:.2f} missing')

# product page ------------------------------------------------------------------------------------------------------
pp = html('offer')
card_ids = {c[0] for c in cards}
by_pkg = {int(json.loads(c[1])[0]['packageId']): c[0] for c in cards}
for m in re.finditer(r'class="sf-pack[^"]*" data-pack="([^"]+)" data-price="([^"]+)" data-compare="[^"]*" data-every="(\d+)"', pp):
    pack, price, every = m.groups()
    ref = next((r for r, b in by_pkg.items() if b == pack), None)
    if ref is None: fail('offer', f'pack {pack} is no checkout card'); continue
    p = pkgs[ref]
    if float(price.strip('$')) != float(p['price_recurring']) or int(every) != int(p['interval_count']):
        fail('offer', f'pack {pack}: {price} every {every} days, campaign {money(p["price_recurring"])} every {p["interval_count"]}')
for b in re.findall(r'forceBundleId=([a-z0-9-]+)', pp):
    if b not in card_ids: fail('offer', f'checkout link to a card that does not exist: {b}')

# checkout pay line: what renews, per card (by the express buttons and the order button)
m = re.search(r"data-sf-pay-terms='([^']+)'", co)
if not m: fail('checkout', 'no pay line by the express buttons')
else:
    terms = json.loads(unescape(m.group(1)))
    for bid, items, attrs, body in cards:
        ref = json.loads(items)[0]['packageId']
        want = f'{money(pkgs[ref]["price_recurring"])} every {pkgs[ref]["interval_count"]} days'
        if not terms.get(bid, '').startswith(want): fail('checkout', f'pay line for {bid}: "{terms.get(bid)}", not "{want}"')
    if co.count('data-sf-pay-terms=') < 2: fail('checkout', 'the pay line is not both above the express buttons and by the order button')

# thank you: each package's renewal under its line
ty = html('thank-you')
m = re.search(r"data-sf-renewals='([^']+)'", ty)
all_pkgs = {p['ref_id']: p for pg in PAGES.values() for p in pg.get('packages', [])}
if not m: fail('thank-you', 'no renewals map')
else:
    ren = json.loads(unescape(m.group(1)))
    for ref, p in all_pkgs.items():
        want = f'Then {money(p["price_recurring"])} every {p["interval_count"]} days'
        got = ren.get(p['product_sku'], '')
        if not got.startswith(want): fail('thank-you', f'package {ref} ({p["product_sku"]}) renews "{got}", not "{want}"')

# host: each deployed page sends a visit on another host to the funnel's (the only one the campaign allows), and its
# policy links stay on it. The redirect is read from the theme template: the layout leaves it out of a development
# build, which is what _site holds after a local Campaigns OS run.
REDIRECT = re.compile(r'location\.replace\(u\.origin \+ location\.pathname \+ location\.search \+ location\.hash\);'
                      r' \} catch \(e\) \{\} \}\)\("([^"]+)"\);</script>')
for p in F.PAGES:
    h = html(p['id'])
    t = THEME / 'templates' / 'pages' / f'page.{p["file"]}.html'
    hosts = REDIRECT.findall(t.read_text(encoding='utf-8')) if t.is_file() else []
    if hosts != [F.FUNNEL_HOST]: fail(p['id'], f'deployed page redirects to {hosts or "nothing"}, not {F.FUNNEL_HOST}')
    for link in re.findall(r'href="(https://[^/"]+)/(?:terms-of-service|privacy-policy|refund-policy|shipping-policy|contact)/"', h):
        if link != F.FUNNEL_HOST: fail(p['id'], f'policy link on {link}, not {F.FUNNEL_HOST}')

# theme -------------------------------------------------------------------------------------------------------------
for p in F.PAGES:
    t = THEME / 'templates' / 'pages' / f'page.{p["file"]}.html'
    if not t.is_file(): fail('theme', f'{t.name} missing'); continue
    s = t.read_text(encoding='utf-8')
    if not s.startswith('{# GENERATED by tools/funnel/deploy_theme.py'): fail('theme', f'{t.name} not generated')
    if f'/{F.SLUG}/' in s: fail('theme', f'{t.name} still names a Page Kit route')
    for a in re.findall(r"\{\{ '(sfc/[^']+)'\|asset_url \}\}", s):
        if not (THEME / 'assets' / a).is_file(): fail('theme', f'{t.name}: asset {a} not on disk')

# claims ------------------------------------------------------------------------------------------------------------
for p in F.PAGES:
    h = html(p['id'])
    # the page's words, and what a screen reader is told (aria-label, alt and title attributes; checkout review 2:
    # "every review" sat in a list's label)
    for t in (text(h), ' '.join(re.findall(r'(?:aria-label|alt|title)="([^"]*)"', h))):
      for rx, what in FORBIDDEN:
        for m in re.finditer(rx, t, re.I):
            if what.startswith('unhedged') and re.search(r'(?:made|designed)\s+not\s+to\s+$', t[max(0, m.start() - 20):m.start()], re.I): continue
            fail(p['id'], f'{what}: "{t[max(0, m.start() - 40):m.end() + 20]}"')
    t = text(h)
    for m in re.finditer(r'\bSPF\b', t):
        ctx = t[max(0, m.start() - 24):m.end() + 2]
        if not SPF_OK.search(ctx): fail(p['id'], f'SPF named outside a "no SPF" line: "{ctx}"')
    if 'AI illustration' not in t and p['id'] in ('listicle', 'offer'): fail(p['id'], 'before/after shown without the AI-illustration label')
    # every review card says whose review it is and where it was written (the liquid's, at the earlier store)
    h = html(p['id'])
    for who in re.findall(r'class="(?:sf-review__who|checkout-review__verified)">([^<]*)<', h):
        if 'liquid foundation' not in who or 'earlier store' not in who: fail(p['id'], f'review card labelled "{who}"')

if problems:
    print(f'check_funnel: {len(problems)} problem(s)'); print('\n'.join('  ' + x for x in problems)); sys.exit(1)
print(f'check_funnel: {len(F.PAGES)} pages, {len(cards)} checkout packs, 4 offers, theme templates and claims OK')
