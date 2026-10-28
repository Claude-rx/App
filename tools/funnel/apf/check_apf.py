"""Offline checks of the Adaptive Peptide Foundation funnel, run by tools/build_store.sh after the funnel is deployed into
the theme: they fail the build when a page drifts from the campaign, from its one-time terms or from the claims the brand
may make.

usage: python3 -I tools/funnel/apf/check_apf.py [<theme dir>]      (default: skinofab-theme)

Reads the CampaignSpec (campaigns/skinofab/campaign-spec.apf.json, the live campaign as campaign_spec.py read it with
FUNNEL=apf), the built pages (campaigns/skinofab/_site/apf-funnel/) and the theme templates deploy_theme.py wrote. Checks:
  routes      every page is built, carries the SDK meta tags funnels/apf.py gives it, and links only to funnel routes
  checkout    one card per checkout package, one selected, each card says it is bought once and names its gifts, and
              shows its name and price before the SDK answers; the pay line by the buttons names every card; no coupon
              box; no post-purchase voucher code anywhere on the page; the exit pop applies the exit offer; the
              guarantee right above the order button, the three featured reviews after it (never between the address
              and the payment), 8+ review cards each with the buyer's photo, the reviews' rating and where they are from
  sales page  each pack's price is its package's, its crossed-out price the list price times its bottles, its saving
              the difference, every checkout link names a checkout card, the before/afters carry the AI label
  offer 1     the supply cards: each card's package is the page's, its price the package's, its crossed-out, per-bottle
              and per-day prices arithmetic from the one-bottle price; the cards sit in an upsell-context selector inside
              the one offer, each card's Buy now the offer's add action (no hidden one), with a skip action; charged once
  offers 2-3  each offer's package and voucher are the campaign's; the fallback price is the voucher's price rounded
              down to dollars, the crossed-out price the package's; charged once; the brush offers skip an order that
              already has a brush (the SKUs of the campaign's packages that include one), the foundation offers never
  thank you   each package's line (by its SKU) says it was bought once; a package with the brush says so
  host        each page sends other hosts to the funnel's; its policy links are on it
  theme       a template per page, marked GENERATED for this funnel, no Page Kit route left, every asset it names on disk
  claims      none of the claims the brand may not make; nothing recurs; no countdown but the offers' own honest one
              (js/sf-offer-timer.js: it declines the offer at 0:00 and says so); the AI before/afters are labelled; the
              reviews say where they are from; SPF is only ever mentioned as absent
"""
import json, os, re, sys
from html import unescape
from pathlib import Path

os.environ['FUNNEL'] = 'apf'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import funnel as F

ROOT = HERE.parents[2]
PROJECT = ROOT / 'campaigns' / 'skinofab'
SITE = PROJECT / '_site' / F.SLUG
THEME = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'skinofab-theme')
SPEC = json.loads((PROJECT / F.SPEC_FILE).read_text())
PAGES = {p['id']: p for p in SPEC['funnels'][0]['pages']}
OFFERS = {o['ref_id']: o for o in SPEC['offers']}
ALL_PKGS = {p['ref_id']: p for pg in PAGES.values() for p in pg.get('packages', [])}
SKUS = {p['product_sku'] for p in ALL_PKGS.values()}
BRUSH_SKUS = {'SKF-APF-3-GIFTS', 'SKF-APF-6-BRUSH'}      # the packages that include the Lymphatic Brush
GIFT_SKUS = {'SKF-APF-2-GIFTS', 'SKF-APF-3-GIFTS'}       # the packages with the Blender brush and the mystery gift
ONE_SKU = 'SKF-APF-1'                                    # one bottle: the price the supply cards' arithmetic starts from
# what the pages may never say (the foundation's claims rules, docs/apf-funnel/persona.md; "made not to" / "designed not
# to" keep "settle" hedged)
FORBIDDEN = [
    (r'\b(?:reverses?|reversing)\s+(?:aging|ageing|the clock|time)', 'reverses aging'),
    (r'\bage[- ]reversing\b', 'age-reversing'),
    (r'\blook(?:s)?\s+(?:10|15|20)\s+years\s+younger', 'look N years younger'),
    (r'\bproduces?\s+collagen', 'produces collagen'),
    (r'\b(?:all|every)\s+skin\s+tones?\b', 'every skin tone'),
    (r'\bmatches\s+\d{2,3}\s?%', 'matches N%'),
    (r'\bdermatologists?[- ](?:recommended|approved|tested|developed)', 'dermatologist endorsement'),
    (r'\bclinically\s+(?:proven|tested|shown)', 'a clinical claim'),
    (r'\b\d{1,3}\s?%\s+of\s+(?:women|users|customers|testers)', 'study percentage'),
    (r"\b(?:won['’]t|will not|never)\s+settle", 'unhedged "won\'t settle"'),
    (r'\bonly\s+\d+\s+(?:left|pieces|in stock)', 'scarcity count'),
    (r"order isn[’']t complete", '"your order isn\'t complete" after the order is placed'),
    (r"\bdon[’']t close this page\b", 'pressure: "don\'t close this page"'),
    (r'\btrustpilot\b', 'Trustpilot'),
    # nothing in this funnel recurs: no renewal wording anywhere (the stick funnel's terms must not be copied in)
    (r'\bevery\s+\d+\s+days\b', 'a renewal interval'),
    (r'\bThen\s+\$\d', 'a "Then $X" renewal line'),
    (r'\buntil you cancel\b', '"until you cancel"'),
    (r'\bfirst charge\b', '"first charge" (nothing is charged again)'),
    (r'\bevery review\b', '"every review" (the imported reviews are the published ones)'),
    (r'\bsave a further\b', '"a further" discount with no first one'),
    (r'\bfuller\b.{0,30}\bin seconds\b', 'instant plumping'),
    # live review 1 (28 Oct 2026)
    (r'\bthis price is gone\b', '"this price is gone" (a decline leads to a last chance that costs less)'),
    (r'\bwomen rated it\b', '"women rated it" (reviews, not women: nobody counted them)'),
    (r'\bprinted on the bottle\b', '"printed on the bottle" (the renders differ)'),
    (r'\bsurprise charges\b', 'an unsourced complaint about competitors'),
    (r'\bwhere adaptive serum foundations were born\b', 'an origin claim with nothing behind it'),
    (r'\bprice you see (?:when you order )?is the price you pay\b', '"the price you see is the price you pay" (the exit pop lowers it)'),
    (r'\{discount\}|\{price\}|\{first_name\}', 'a raw copy token'),
    (r'\bno cakey lines\b', 'unhedged "no cakey lines"'),
    (r'\bnothing sitting in your lines\b', 'unhedged "nothing sitting in your lines"'),
    (r'\blowest price we will ever\b', 'a "lowest ever" price (the downsells go lower)'),
    (r'\blowest single-bottle price anywhere\b', 'a "lowest anywhere" price on offer 2 (its downsell goes lower)'),
    (r'\bsix for the price of three\b', '"six for the price of three" (no shown price backs it)'),
]
# SPF may only be mentioned as what the foundation does not have, or as her own sunscreen under it
SPF_OK = re.compile(r"(?:no|not an?|has no|without|doesn[’']t have|does it have|left)\s+SPF|SPF\s+out\b|SPF\?|"
                    r"your (?:daily |usual )?(?:SPF|sunscreen)|over your SPF|no[- ]SPF", re.I)
problems = []


def fail(where, what): problems.append(f'{where}: {what}')


def html(page_id): return (SITE / F.BY_ID[page_id]['file'] / 'index.html').read_text(encoding='utf-8')


def text(h):
    h = re.sub(r'<(script|style|template)\b.*?</\1>', ' ', h, flags=re.S | re.I)
    return unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)))


def money(v): return f'${float(v):.2f}'


def landed(pkg, offer):
    """A voucher's price: the campaign rounds a percentage voucher's result down to the dollar (price_rounding "0.00")."""
    return int(float(pkg['price']) * (100 - float(offer['benefit']['value'])) / 100)


for sku in BRUSH_SKUS | GIFT_SKUS | {ONE_SKU}:
    if sku not in SKUS: fail('campaign', f'package SKU {sku} is not in the funnel\'s packages ({sorted(SKUS)})')

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
    if PAGES[p['id']].get('sdk_hints', {}).get('meta_tags') != F.meta_tags(p): fail(p['id'], 'CampaignSpec meta tags differ from funnels/apf.py')

# checkout ----------------------------------------------------------------------------------------------------------
co = html('checkout')
cards = re.findall(r"<div data-next-bundle-card data-next-bundle-id=\"([^\"]+)\"[^>]*?data-next-bundle-items='([^']+)'([^>]*)>(.*?)</div>\s*</div>\s*</div>", co, re.S)
pkgs = {p['ref_id']: p for p in PAGES['checkout']['packages']}
if len(cards) != len(pkgs): fail('checkout', f'{len(cards)} pack cards for {len(pkgs)} packages')
if sum('data-next-selected="true"' in c[2] for c in cards) != 1: fail('checkout', 'not exactly one selected card')


def gifts_said(where, sku, t):
    """A package with gifts names them; one without names none."""
    t = t.lower()
    if sku in BRUSH_SKUS and 'lymphatic brush' not in t: fail(where, f'{sku}: the free Lymphatic Brush is not named')
    if sku in GIFT_SKUS and ('blender brush' not in t or 'mystery gift' not in t): fail(where, f'{sku}: the Blender brush and mystery gift are not named')
    if sku not in GIFT_SKUS | BRUSH_SKUS and re.search(r'\bfree [a-z]+ (?:brush|gift)', t): fail(where, f'{sku}: a gift named on a package without one')


for bid, items, attrs, body in cards:
    ref = json.loads(items)[0]['packageId']
    if ref not in pkgs: fail('checkout', f'card {bid} sells package {ref}, not a checkout package'); continue
    t = text(body)
    if 'One-time' not in t: fail('checkout', f'card {bid}: not said to be bought once')
    gifts_said(f'checkout card {bid}', pkgs[ref]['product_sku'], t)
if re.search(r'data-next-coupon=', co): fail('checkout', 'a coupon box (post-purchase vouchers could be typed in)')
exit_code = PAGES['checkout']['exit_intent']['offer_code']
for o in OFFERS.values():
    if o['code'] != exit_code and re.search(r'\b' + re.escape(o['code']) + r'\b', co):
        fail('checkout', f'post-purchase voucher {o["code"]} appears on the checkout')
if f'data-coupon-code="{exit_code}"' not in co: fail('checkout', 'exit pop does not apply the exit offer')
if exit_code != OFFERS[PAGES['checkout']['exit_intent']['offer_ref_id']]['code']: fail('checkout', 'exit offer code is not the campaign\'s')
# the checkout sells on trust: the guarantee right above the order button, the review wall with each buyer's own photo,
# and the ratings as the listicle and sales page give them, with where they are from
g, btn = co.find('data-sf-guarantee-inline'), co.find('COMPLETE MY ORDER')
if g < 0 or btn < 0 or g > btn: fail('checkout', 'no guarantee line right above the order button')
cards_r = re.findall(r'<article class="sf-co-review">(.*?)</article>', co, re.S)
if len(cards_r) < 8: fail('checkout', f'{len(cards_r)} review cards, not at least 8')
if any('<img ' not in c for c in cards_r): fail('checkout', 'a review card without its buyer\'s photo')
if '4.8 out of 5' not in co or '9,855 reviews' not in co: fail('checkout', 'the rating is not the foundation\'s 4.8 from 9,855 reviews')
if 'sf-co-review__title' in co: fail('checkout', 'a title on a review (the buyers wrote none)')
f = co.find('id="sf-co-featured"')
if f < 0 or f < btn: fail('checkout', 'the featured reviews are not after the order button (v2: the form comes first)')
s3, s4 = co.find('Step 3: Shipping address'), co.find('Step 4: Payment')
if 'sf-co-review' in co[s3:s4]: fail('checkout', 'a review between the address and the payment step')
for bid, items, attrs, body in cards:
    if '>Package<' in body or 'bundle-card__price-total">--<' in body: fail('checkout', f'card {bid} has no name or price before the SDK answers')
if 'data-sf-gift-line' not in html('thank-you'): fail('thank-you', 'no gift line for js/sf-receipt.js to fill')
# the pay line by the express buttons and the order button: every card, bought once, with its gifts
m = re.search(r"data-sf-pay-terms='([^']+)'", co)
if not m: fail('checkout', 'no pay line by the express buttons')
else:
    terms = json.loads(unescape(m.group(1)))
    if set(terms) != {c[0] for c in cards}: fail('checkout', f'pay line names {sorted(terms)}, the cards are {sorted(c[0] for c in cards)}')
    for bid, items, attrs, body in cards:
        gifts_said(f'checkout pay line {bid}', pkgs[json.loads(items)[0]['packageId']]['product_sku'], terms.get(bid, ''))
    if co.count('data-sf-pay-terms=') < 2: fail('checkout', 'the pay line is not both above the express buttons and by the order button')
if 'Nothing renews' not in co: fail('checkout', '"Nothing renews" missing by the order button')

# sales page --------------------------------------------------------------------------------------------------------
pp = html('offer')
card_ids = {c[0] for c in cards}
by_pkg = {int(json.loads(c[1])[0]['packageId']): c[0] for c in cards}
seen = set()
for m in re.finditer(r'<label class="sf-pack[^"]*" data-pack="([^"]+)" data-price="\$([\d.]+)" data-compare="\$([\d.]+)" '
                     r'data-save="SAVE \$([\d.]+)" data-label="[^"]*" data-short="(\d+) bottles?[^"]*" data-package="(\d+)">', pp):
    pack, price, compare, save, bottles, package = m.groups()
    seen.add(pack)
    if by_pkg.get(int(package)) != pack: fail('offer', f'pack {pack} names package {package}; the checkout card for it is {by_pkg.get(int(package))}'); continue
    p = pkgs[int(package)]
    if float(price) != float(p['price']): fail('offer', f'pack {pack}: {price}, campaign {money(p["price"])}')
    if float(compare) != F.LIST_PRICE * int(bottles): fail('offer', f'pack {pack}: crossed-out ${compare}, not {F.LIST_PRICE} x {bottles} bottles')
    if abs(float(save) - (float(compare) - float(price))) > 0.005: fail('offer', f'pack {pack}: saving ${save} is not ${compare} - ${price}')
    gifts_said(f'offer pack {pack}', p['product_sku'], text(pp[m.end():pp.find('</label>', m.end())]))      # the pack's own card
if seen != card_ids: fail('offer', f'packs {sorted(seen)} are not the checkout cards {sorted(card_ids)}')
for pack in re.findall(r'class="sf-pack[^"]*" data-pack="([^"]+)"', pp):
    if pack not in card_ids: fail('offer', f'pack {pack} is no checkout card')
for b in re.findall(r'forceBundleId=([a-z0-9-]+)', pp):
    if b not in card_ids: fail('offer', f'checkout link to a card that does not exist: {b}')

# offer 1: the supply cards -----------------------------------------------------------------------------------------
h1, pg1 = html('offer-1'), PAGES['offer-1']
opk = {p['ref_id']: p for p in pg1['packages']}
one = float(next(p['price'] for p in ALL_PKGS.values() if p['product_sku'] == ONE_SKU))
if 'data-next-upsell="offer" data-next-await=""' not in h1: fail('offer-1', 'no offer wrapper')
if 'data-next-bundle-selector data-next-upsell-context data-next-selector-id="supply"' not in h1: fail('offer-1', 'the supply selector is not an upsell-context selector')
if h1.count('data-next-upsell-action="add"') != len(opk) or 'data-next-upsell-action="skip"' not in h1: fail('offer-1', 'not one add action per card and a skip action')
if 'class="sf-sr" tabindex="-1" aria-hidden="true">Add to my order' in h1: fail('offer-1', 'a hidden add action (a harness or a screen reader must reach the real one)')
cards1 = re.findall(r"<div data-next-bundle-card data-next-bundle-id=\"([^\"]+)\" data-next-bundle-items='([^']+)'([^>]*)>(.*?<p class=\"sf-supply__charged\">[^<]*</p>)", h1, re.S)
if len(cards1) != len(opk): fail('offer-1', f'{len(cards1)} supply cards for {len(opk)} packages')
if sum('data-next-selected="true"' in c[2] for c in cards1) != 1: fail('offer-1', 'not exactly one selected supply card')
for bid, items, attrs, body in cards1:
    it = json.loads(items)[0]
    if it['packageId'] not in opk or it.get('quantity') != 1: fail('offer-1', f'card {bid} adds {items}, not one of the page\'s packages once'); continue
    p, t = opk[it['packageId']], text(body)
    price = float(p['price'])
    mb = re.search(r'(\d+) bottles', t)
    if not mb: fail('offer-1', f'card {bid}: no bottle count'); continue
    bottles = int(mb.group(1))
    if money(price) not in t: fail('offer-1', f'card {bid}: fallback price {money(price)} missing')
    mc = re.search(r'\$([\d,.]+) ' + re.escape(money(price)), t)
    if not mc or float(mc.group(1).replace(',', '')) != one * bottles: fail('offer-1', f'card {bid}: crossed-out price is not {bottles} x {money(one)}')
    mp = re.search(r'\$([\d.]+) a bottle', t)
    if not mp or abs(float(mp.group(1)) - price / bottles) > 0.005: fail('offer-1', f'card {bid}: per-bottle price is not {money(price)} / {bottles}')
    md = re.search(r'\$([\d.]+) a day', t)
    if not md or abs(float(md.group(1)) - price / (bottles * 30)) > 0.006: fail('offer-1', f'card {bid}: per-day price is not {money(price)} over {bottles} months')
    if 'Charged once' not in t: fail('offer-1', f'card {bid}: not said to be charged once')
    gifts_said(f'offer-1 card {bid}', p['product_sku'], t)
    if 'data-sf-supply-card' not in attrs: fail('offer-1', f'card {bid}: not a supply card (js/sf-supply.js)')
    if 'data-next-upsell-action="add" data-sf-supply-buy' not in h1[h1.find(bid):h1.find(bid) + 3000]: fail('offer-1', f'card {bid}: its Buy now is not the offer\'s add action')
if 'data-sf-skip-skus' in h1: fail('offer-1', 'a brush skip rule on a foundation offer')

# offers 2 and 3, with their downsells -------------------------------------------------------------------------------
for pid in ('offer-2', 'offer-2b', 'brush-offer', 'brush-offer-b'):
    h, spec_pg = html(pid), PAGES[pid]
    pkg, offer = spec_pg['packages'][0], OFFERS[spec_pg['offers'][0]['ref_id']]
    if f'data-next-upsell="offer" data-next-await="" data-next-package-id="{pkg["ref_id"]}"' not in h:
        fail(pid, f'offer wrapper is not package {pkg["ref_id"]}')
    sel = re.search(r'<div data-next-bundle-selector data-next-upsell-context[^>]*>.*?</div>\s*</div>', h, re.S)
    if not sel or f'["{offer["code"]}"]' not in sel.group(0) or f'"packageId":{pkg["ref_id"]}' not in sel.group(0):
        fail(pid, f'no upsell-context selector adding package {pkg["ref_id"]} with {offer["code"]}')
    if f'>${landed(pkg, offer):.2f}<' not in h: fail(pid, f'fallback price ${landed(pkg, offer):.2f} missing')
    if f'>{money(pkg["price"])}<' not in h: fail(pid, f'crossed-out price {money(pkg["price"])} missing')
    t = text(h)
    if 'charged once' not in t.lower(): fail(pid, 'not said to be charged once')
    if 'Nothing renews' not in t: fail(pid, '"Nothing renews" missing')
    if pid.startswith('brush'):
        skip = re.search(r'data-sf-skip-skus="([^"]+)"', h)
        if not skip or set(skip.group(1).split(',')) != BRUSH_SKUS: fail(pid, f'brush skip rule is not {sorted(BRUSH_SKUS)}')
        if 'data-sf-sku="{item.sku}"' not in h: fail(pid, 'no order-items list for the skip rule to read')
        if 'Lymphatic Brush' not in t: fail(pid, 'the brush is not named')
    elif 'data-sf-skip-skus' in h: fail(pid, 'a brush skip rule on a foundation offer')
    if pid.endswith('b') and 'last chance' not in t.lower() and 'lowest price' not in t.lower(): fail(pid, 'a downsell that does not say it is the last or lowest')

# thank you: each package bought once, its gifts named ---------------------------------------------------------------
ty = html('thank-you')
m = re.search(r"data-sf-renewals='([^']+)'", ty)
if not m: fail('thank-you', 'no terms map')
else:
    ren = json.loads(unescape(m.group(1)))
    for ref, p in ALL_PKGS.items():
        got = ren.get(p['product_sku'], '')
        if not got.startswith('One-time purchase'): fail('thank-you', f'package {ref} ({p["product_sku"]}) says "{got}", not "One-time purchase…"')
        if p['product_sku'] in BRUSH_SKUS and 'Lymphatic Brush' not in got: fail('thank-you', f'{p["product_sku"]}: the brush is not named')

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
    if not s.startswith('{# GENERATED by tools/funnel/deploy_theme.py') or f'Campaign Page Kit, {F.SLUG})' not in s[:200]: fail('theme', f'{t.name} not generated for {F.SLUG}')
    if f'/{F.SLUG}/' in s: fail('theme', f'{t.name} still names a Page Kit route')
    for a in re.findall(r"\{\{ '(" + F.ASSET_DIR + r"/[^']+)'\|asset_url \}\}", s):
        if not (THEME / 'assets' / a).is_file(): fail('theme', f'{t.name}: asset {a} not on disk')
# the social share image (campaigns.json og_image) is one of this funnel's deployed assets: its name carries the
# image's hash, so a changed hero collage changes the name and must be followed here
og = json.loads((PROJECT / '_data' / 'campaigns.json').read_text())[F.SLUG].get('og_image', '')
if not og or not (THEME / 'assets' / F.ASSET_DIR / og.rsplit('/', 1)[-1]).is_file(): fail('theme', f'og_image {og!r} is not a deployed asset of this funnel')
for p in F.PAGES:
    if f'<meta property="og:image" content="{og}">' not in html(p['id']): fail(p['id'], 'og:image meta is not the campaign\'s og_image')

# claims ------------------------------------------------------------------------------------------------------------
for p in F.PAGES:
    h = html(p['id'])
    # the page's words, and what a screen reader is told (aria-label, alt and title attributes)
    for t in (text(h), ' '.join(re.findall(r'(?:aria-label|alt|title)="([^"]*)"', h))):
        for rx, what in FORBIDDEN:
            for m in re.finditer(rx, t, re.I):
                if what.startswith('unhedged') and re.search(r'(?:made|designed)\s+not\s+to\s+$', t[max(0, m.start() - 20):m.start()], re.I): continue
                fail(p['id'], f'{what}: "…{t[max(0, m.start() - 40):m.end() + 40]}…"')
        for m in re.finditer(r'\bSPF\b', t):
            if not SPF_OK.search(t[max(0, m.start() - 30):m.end() + 12]): fail(p['id'], f'SPF mentioned as present: "…{t[max(0, m.start() - 40):m.end() + 40]}…"')
    if 'data-next-timer' in h or 'data-next-element="timer"' in h: fail(p['id'], 'a countdown timer the page does not keep (the kit\'s)')
    if 'data-sf-timer' in h:
        if 'data-sf-timer-expires="skip"' not in h or 'js/sf-offer-timer' not in h or 'this page moves on' not in text(h):
            fail(p['id'], 'a countdown without its consequence (the offer must decline itself at 0:00 and say so)')
        if p['sdk'] != 'upsell': fail(p['id'], 'a countdown on a page that is not an offer')
    if 'images/sf/ba-' in h and 'AI illustration' not in h: fail(p['id'], 'before/after images without the AI illustration label')
    if 'images/sf/review-' in h and 'earlier store' not in text(h): fail(p['id'], 'buyers\' reviews without where they are from')

if problems:
    print('\n'.join(problems)); print(f'check_apf: {len(problems)} problems'); sys.exit(1)
print(f'check_apf: {len(F.PAGES)} pages ok')
