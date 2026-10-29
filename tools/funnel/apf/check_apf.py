"""Offline checks of the Adaptive Peptide Foundation funnel, run by tools/build_store.sh after the funnel is deployed into
the theme: they fail the build when a page drifts from the campaign, from its refill or one-time terms or from the claims
the brand may make.

usage: python3 -I tools/funnel/apf/check_apf.py [<theme dir>]      (default: skinofab-theme)

Reads the CampaignSpec (campaigns/skinofab/campaign-spec.apf.json, the live campaign as campaign_spec.py read it with
FUNNEL=apf), the built pages (campaigns/skinofab/_site/apf-funnel/) and the theme templates deploy_theme.py wrote. Checks:
  routes      every page is built, carries the SDK meta tags funnels/apf.py gives it, and links only to funnel routes
  checkout    one card per checkout package, one selected, each card says what it refills at (its price, every 28 days a
              bottle: funnels/apf.py PACKS, and the campaign's own interval once the package recurs) and names its gifts, and
              shows its name and price before the SDK answers; the pay line by the buttons gives every card's renewal,
              "until you cancel", and the order button asks her to agree to the refills; no coupon
              box; no post-purchase voucher code anywhere on the page; the exit pop applies the exit offer; the
              guarantee right above the order button, the three featured reviews after it (never between the address
              and the payment), 8+ review cards each with the buyer's photo, the reviews' rating and where they are from
  sales page  each pack's price is its package's, its renewal the same price every 28 days a bottle, no crossed-out price
              and no saving on a pack (the store's own refills are lower, live review 8), every checkout link names a
              checkout card, no disclaimer or illustration line anywhere
  offer 1     the supply cards: each card's package is the page's, its price the package's, its crossed-out price the
              store's one-time price for the same bottles (funnels/apf.py store_once), named, its per-bottle and per-day
              prices arithmetic; the cards sit in an upsell-context selector inside
              the one offer, each card's Buy now the offer's add action (no hidden one), with a skip action; charged once
  offers 2-3  each offer's package and voucher are the campaign's; the fallback price is the voucher's price rounded
              down to dollars, the crossed-out price the package's; charged once, it doesn't renew; the brush offers skip an order that
              already has a brush (the SKUs of the campaign's packages that include one), the foundation offers never
  thank you   each checkout package's line (by its SKU) gives its renewal, each offer package's says it was bought once;
              a package with the brush says so
  campaign    the checkout's packages recur at their own price, every 28 days a bottle, and no offer's package recurs
              (APF_RECURRING_PENDING=1 lets a build through while the campaign is not switched yet: the pages may then
              promise refills the campaign does not charge, never the other way round)
  host        each page sends other hosts to the funnel's; its policy links are on it
  theme       a template per page, marked GENERATED for this funnel, no Page Kit route left, every asset it names on disk
  claims      none of the claims the brand may not make; no renewal wording on an offer page; no countdown but the offers' own honest one
              (js/sf-offer-timer.js: it declines the offer at 0:00 and says so); no disclaimer or illustration line (the owner's instruction); the
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
GIFT_SKUS = {'SKF-APF-2-GIFTS', 'SKF-APF-3-GIFTS'}       # the packages with the Blender sponge and the mystery gift
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
    # the owner's instruction (28 Oct 2026): no disclaimer or illustration line on any page or image
    (r'\billustrations?\b', 'an illustration line'),
    (r'\bresults\s+(?:may\s+)?vary\b', 'a results-vary disclaimer'),
    (r'\badvertisement\b', 'an advertisement disclosure'),
    (r'\bnot\s+(?:a\s+)?(?:customer\s+)?photos?\b', 'a not-a-photo line'),
    (r'\bnot\s+an?\s+(?:endorsement|measurement)\b', 'a not-an-endorsement/measurement line'),
    (r'\bnot\s+to\s+scale\b', 'a not-to-scale line'),
    (r'\bfirst charge\b', '"first charge" (the offers are charged once, the packs refill at the same price)'),
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
    # live review 7, B1 (the owner, 29 Oct 2026, before the ads): the 3-bottle pack is "3 bottles for $75, $25 a bottle";
    # "buy 2, get 1 free" beside the $57 2-bottle pack made the free bottle cost $18
    (r'\bbuy\s+(?:2|two),?\s+get\s+(?:1|one)\b', '"buy 2, get 1 free" (the 2-bottle pack costs $57)'),
    (r'\b(?:3rd|third)\s+(?:bottle\s+)?(?:is\s+)?free\b', '"the 3rd bottle free" (the 2-bottle pack costs $57)'),
    (r'\bpay\s+for\s+(?:2|two)\b', '"pay for 2" (the 2-bottle pack costs $57)'),
    (r'\+\s?1\s+free\b', '"+1 free" (the 2-bottle pack costs $57)'),
]
# SPF may only be mentioned as what the foundation does not have, or as her own sunscreen under it
SPF_OK = re.compile(r"(?:no|not an?|has no|without|doesn[’']t have|does it have|left)\s+SPF|SPF\s+out\b|SPF\?|"
                    r"your (?:daily |usual )?(?:SPF|sunscreen)|over your SPF|no[- ]SPF", re.I)
# the offer pages sell one-time add-ons: no renewal wording there (the checkout's packs are the ones that refill)
ONE_TIME_ONLY = [
    (r'\bevery\s+\d+\s+days\b', 'a renewal interval on a one-time offer'),
    (r'\bThen\s+\$\d', 'a "Then $X" renewal line on a one-time offer'),
    (r'\buntil you cancel\b', '"until you cancel" on a one-time offer'),
]
OFFER_IDS = set(F.OFFER_PAGES)
PACK_BY_REF = {p['package']: p for p in F.PACKS}
PENDING = os.environ.get('APF_RECURRING_PENDING') == '1'


def renew(p): return f"Then ${p['price']:.0f} every {p['every']} days"          # "Then $57 every 56 days"


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
    if sku in GIFT_SKUS and ('blender sponge' not in t or 'mystery gift' not in t): fail(where, f'{sku}: the Blender sponge and mystery gift are not named')
    if sku not in GIFT_SKUS | BRUSH_SKUS and re.search(r'\bfree [a-z]+ (?:brush|gift)', t): fail(where, f'{sku}: a gift named on a package without one')


for bid, items, attrs, body in cards:
    ref = json.loads(items)[0]['packageId']
    if ref not in pkgs: fail('checkout', f'card {bid} sells package {ref}, not a checkout package'); continue
    t = text(body)
    if ref in PACK_BY_REF and renew(PACK_BY_REF[ref]) not in t: fail('checkout', f'card {bid}: does not say "{renew(PACK_BY_REF[ref])}"')
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
# (the owner, 29 Oct 2026: the order button straight after the payment options, the guarantee line under it)
pay = co.find('Step 4: Payment')
if btn < 0 or pay < 0 or btn < pay: fail('checkout', 'no order button after the payment step')
elif any(m in co[pay:btn] for m in ('data-sf-summary-box', 'data-sf-guarantee-inline', 'id="refill-terms"')):
    fail('checkout', 'something stands between the payment options and the order button')
if g < 0 or g < btn: fail('checkout', 'no guarantee line under the order button')
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
        ref = json.loads(items)[0]['packageId']
        gifts_said(f'checkout pay line {bid}', pkgs[ref]['product_sku'], terms.get(bid, ''))
        if ref in PACK_BY_REF:
            p = PACK_BY_REF[ref]; want = f"${p['price']:.2f} every {p['every']} days for {p['bottles']} bottle"
            if not terms.get(bid, '').startswith(want): fail('checkout', f'pay line {bid}: "{terms.get(bid)}", not "{want}…"')
    if co.count('data-sf-pay-terms=') < 2: fail('checkout', 'the pay line is not both above the express buttons and by the order button')
if 'until you cancel' not in text(co): fail('checkout', '"until you cancel" missing from the pay line')
if 'you agree to Automatic Refills' not in text(co[co.find('Step 4: Payment'):]): fail('checkout', 'the order button does not ask her to agree to the refills')
if 'id="refill-terms"' not in co or 'To skip or cancel' not in text(co): fail('checkout', 'no refill terms (how to skip or cancel) by the order button')
# the summary's renewal line is the SDK's ({item.frequency}); an inline display:none on it kept it hidden (29 Oct 2026)
_freq = re.search(r'<span data-next-show="item.isRecurring"([^>]*)>([^<]*)</span>', co)
if not _freq or 'display:none' in _freq.group(1) or '{item.frequency}' not in _freq.group(2): fail('checkout', 'the order summary does not show the SDK\'s refill frequency')

# the FrontrowMD "Clinicians' Choice" badge (the owner, 29 Oct 2026, as a badge with no link) on the sales page and the
# checkout: its count is a floor of FrontrowMD's live count for the foundation's listing (product 4694, the store's
# ccf_copy.FRONTROW_PRODUCT_ID), read here on every build; a build that cannot reach FrontrowMD says so and goes on
FRONTROW_ID = 4694
_said = {}
for pid in ('offer', 'checkout'):
    m = re.search(r'<strong>(\d+)\+? clinicians</strong> share this on <em>FrontrowMD</em> without compensation\.', html(pid))
    if not m: fail(pid, 'no FrontrowMD "Clinicians\' Choice" badge with its count')
    else: _said[pid] = int(m.group(1))
if _said:
    import urllib.request
    try:
        with urllib.request.urlopen(f'https://app.thefrontrowhealth.com/api/widgets?presentation_type=sticker&product_id={FRONTROW_ID}', timeout=15) as r:
            _live = re.search(r'(\d[\d,]*)\s*(?:<[^>]*>\s*)*clinicians', r.read().decode('utf-8', 'replace'))
        _n = int(_live.group(1).replace(',', '')) if _live else None
        if _n is None: print('check_apf: FrontrowMD answered without a clinician count; the badge count was not checked')
        else:
            for pid, n in _said.items():
                if n > _n: fail(pid, f'the badge says {n}+ clinicians, FrontrowMD counts {_n} now')
    except Exception as e:
        print(f'check_apf: FrontrowMD not reachable ({type(e).__name__}); the badge count was not checked')

# sales page --------------------------------------------------------------------------------------------------------
pp = html('offer')
card_ids = {c[0] for c in cards}
by_pkg = {int(json.loads(c[1])[0]['packageId']): c[0] for c in cards}
seen = set()
for m in re.finditer(r'<label class="sf-pack[^"]*" data-pack="([^"]+)" data-price="\$([\d.]+)" data-every="([^"]+)" '
                     r'data-renew="([^"]+)" data-label="[^"]*" data-short="(\d+) bottles?[^"]*" data-package="(\d+)">', pp):
    pack, price, every, renewal, bottles, package = m.groups()
    seen.add(pack)
    if by_pkg.get(int(package)) != pack: fail('offer', f'pack {pack} names package {package}; the checkout card for it is {by_pkg.get(int(package))}'); continue
    p = pkgs[int(package)]
    if float(price) != float(p['price']): fail('offer', f'pack {pack}: {price}, campaign {money(p["price"])}')
    want = PACK_BY_REF.get(int(package))
    if not want or renewal != renew(want) or every != f"{want['every']} days": fail('offer', f'pack {pack}: renews "{renewal}" every "{every}", not "{renew(want) if want else "?"}"')
    card = pp[m.end():pp.find('</label>', m.end())]
    if renewal not in text(card): fail('offer', f'pack {pack}: its renewal is not on its card')
    if re.search(r'<s>\$|SAVE \$', card.split('sf-gifts')[0]): fail('offer', f'pack {pack}: a crossed-out price or a saving (the store\'s own refills are lower)')
    gifts_said(f'offer pack {pack}', p['product_sku'], text(card))      # the pack's own card
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
    if not mc or float(mc.group(1).replace(',', '')) != F.store_once(bottles): fail('offer-1', f'card {bid}: crossed-out price is not the store\'s one-time {money(F.store_once(bottles))} for {bottles} bottles')
    if 'Our store, bought once' not in t: fail('offer-1', f'card {bid}: the crossed-out price does not say whose it is')
    ms = re.search(r'SAVE (\d+)%', t)
    if not ms or int(ms.group(1)) != round((F.store_once(bottles) - price) / F.store_once(bottles) * 100): fail('offer-1', f'card {bid}: its saving is not against the store\'s one-time price')
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
    if 'doesn’t renew' not in t: fail(pid, '"doesn’t renew" missing (her pack refills; this add-on does not)')
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
        want = (f"Then ${PACK_BY_REF[ref]['price']:.2f} every {PACK_BY_REF[ref]['every']} days, until you cancel" if ref in PACK_BY_REF else 'One-time purchase')
        if not got.startswith(want): fail('thank-you', f'package {ref} ({p["product_sku"]}) says "{got}", not "{want}…"')
        if p['product_sku'] in BRUSH_SKUS and 'Lymphatic Brush' not in got: fail('thank-you', f'{p["product_sku"]}: the brush is not named')

# campaign: the checkout's packages recur at their own price and interval, and no offer's package recurs ----------------
for ref, want in PACK_BY_REF.items():
    live = pkgs.get(ref)
    if not live: fail('campaign', f'package {ref} ({want["key"]}) is not on the checkout'); continue
    if not live.get('is_recurring'):
        if PENDING: print(f'check_apf: package {ref} does not recur in the campaign yet (APF_RECURRING_PENDING=1)'); continue
        fail('campaign', f'package {ref} ({want["key"]}) is one-time in the campaign; the pages sell it with refills'); continue
    if (live.get('interval'), live.get('interval_count')) != ('day', want['every']) or float(live.get('price_recurring') or 0) != want['price']:
        fail('campaign', f'package {ref} renews ${live.get("price_recurring")} every {live.get("interval_count")} {live.get("interval")}, the pages say ${want["price"]:.2f} every {want["every"]} days')
for pid in OFFER_IDS:
    for p in PAGES[pid].get('packages', []):
        if p.get('is_recurring'): fail(pid, f'package {p["ref_id"]} recurs: the offers are one-time')

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
    # (every policy and contact link carries ?from=offer, which keeps the store's chrome off the page; live review 7)
    for link, query in re.findall(r'href="(https://[^/"]+)/(?:terms-of-service|privacy-policy|refund-policy|shipping-policy|contact)/([^"]*)"', h):
        if link != F.FUNNEL_HOST: fail(p['id'], f'policy link on {link}, not {F.FUNNEL_HOST}')
        if query != '?from=offer': fail(p['id'], f'policy link with {query or "no query"}, not ?from=offer')

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
        for rx, what in FORBIDDEN + (ONE_TIME_ONLY if p['id'] in OFFER_IDS else []):
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
    if 'images/sf/review-' in h and 'earlier store' not in text(h): fail(p['id'], 'buyers\' reviews without where they are from')


# live review 9 ---------------------------------------------------------------------------------------------------------
# no clinician in the pictures: a generated white-coat "clinic" portrait read as an invented medical endorsement (F2;
# the FrontrowMD "Clinicians’ Choice" badge is a real listing, the owner's)
for p in F.PAGES:
    h = html(p['id'])
    for a in re.findall(r'<img[^>]*\balt="([^"]*)"', h):
        if re.search(r'white[- ]coat|lab coat|\bclinic\b|\bdoctor|dermatologist|physician|\bnurse\b', a, re.I): fail(p['id'], f'an image of a clinician: alt "{a[:80]}"')
    for src in re.findall(r'<(?:img|source|video)[^>]*\b(?:src|srcset|poster)="([^"]+)"', h):
        if re.search(r'doctor|derm', src, re.I): fail(p['id'], f'a clinician image: {src}')
# a countdown that ends on the same item cheaper is a pressure trick: at 0:00 an offer whose decline is its downsell
# goes past the downsell (data-sf-timer-to), and the page says the last-chance price goes too (F1)
for p in F.PAGES:
    if p['sdk'] != 'upsell' or 'data-sf-timer=' not in html(p['id']): continue
    h, nxt = html(p['id']), F.BY_ID[F.BY_ID[p['id']]['decline']]
    want = F.route(nxt['decline']) if nxt.get('type') == 'downsell' else ''
    m = re.search(r'data-sf-timer-to="([^"]*)"', h)
    if (m.group(1) if m else '') != want: fail(p['id'], f'at 0:00 the page goes to {m.group(1) if m else "where a decline goes"}, not {want or "where a decline goes"}')
    if want and 'last-chance price' not in text(h): fail(p['id'], 'the countdown does not say the last-chance price goes with it')
    if re.search(r'\breserved\b', text(h), re.I): fail(p['id'], '"reserved": nothing is held for her')
# declines say what happens, nothing about her (confirmshaming, F17)
for p in F.PAGES:
    if p['sdk'] != 'upsell': continue
    for m in re.finditer(r'data-(?:next-upsell-action|upsell-proxy)="skip"[^>]*>(.*?)</a>', html(p['id']), re.S):
        label = text(m.group(1)).strip()
        if label not in ('No thanks, continue', 'No thanks, show my order'): fail(p['id'], f'decline "{label}" is not a plain "No thanks, continue"')
# the store's $37 refill is not a reason to buy here, and nothing is a "launch" price (F4)
for p in F.PAGES:
    t = text(html(p['id']))
    if p['id'] in OFFER_IDS and '$37' in t: fail(p['id'], 'quotes the store\'s $37 refill price')
    if re.search(r'launch (?:offer|price)', t, re.I): fail(p['id'], '"launch offer": the funnel\'s prices are not an introductory price')
# the checkout shows the packs in the sales page's order and opens on the sales page's pack, with or without
# forceBundleId (F18)
_sales_order = re.findall(r'class="sf-pack[^"]*" data-pack="([^"]+)"', html('offer'))
if [c[0] for c in cards] != _sales_order: fail('checkout', f'packs in the order {[c[0] for c in cards]}, the sales page has {_sales_order}')
_sel = [c[0] for c in cards if 'data-next-selected="true"' in c[2]]
_on_pack = re.search(r'<label class="sf-pack is-on"[^>]*data-pack="([^"]+)"', html('offer'))
if _on_pack and _sel != [_on_pack.group(1)]: fail('checkout', f'opens on {_sel}, the sales page on {_on_pack.group(1)}')
# the ingredients before she pays: the key list on the sales page and the checkout, and the full list on request (F16)
for pid in ('offer', 'checkout'):
    t = text(html(pid))
    if 'Key ingredients: Sodium Hyaluronate' not in t or 'subject=Full%20ingredient%20list' not in html(pid): fail(pid, 'no ingredient list (or no way to ask for the full one) before she orders')
# a policy page opened from the funnel keeps ?from=offer on every legal or contact link, its link to itself included,
# and switches off the rest of the store (F5)
_base = (THEME / 'layouts' / 'base.html').read_text(encoding='utf-8')
if "u.searchParams.set('from', 'offer')" not in _base or 'sf-off-link' not in _base: fail('theme', 'policy pages opened from the funnel do not keep ?from=offer on their links')
if 'u.pathname === location.pathname' in _base: fail('theme', 'a policy page\'s link to itself drops ?from=offer (the full store comes back)')
# the offers' words, pictures and landed prices show at the first paint, not behind the loading skeleton until the order
# loads (F11: ~9 s to the largest paint on throttled 4G); only their buttons wait for the SDK
_oc = (SITE / 'css' / 'sf-offers.css').read_text(encoding='utf-8')
if not re.search(r'\.upsell-wrapper\[data-next-await\] \* \{ opacity: 1; \}', _oc) or 'upsell-wrapper[data-next-await]::before' not in _oc:
    fail('offers', 'the offer waits behind the loading skeleton for the SDK (it has its landed prices already)')
# the gate's order lines are not read aloud, and their empty state is not the SDK's "No items found in order" (F12)
for p in F.PAGES:
    h = html(p['id'])
    for m in re.finditer(r'<div[^>]*data-next-order-items[^>]*>', h):
        if 'data-sf-sku' in h[m.end():m.end() + 200] and ('aria-hidden="true"' not in m.group(0) or 'data-empty-template=' not in m.group(0)):
            fail(p['id'], 'the gate\'s order-items list is read aloud or prints "No items found in order"')

# reviews: every quote the pages put a buyer's name to is her own words from the imported reviews (SF_REVIEWS, the store
# build's reviews/reviews.json), and a shortened one says so with "…" (live review 9: Sharon E.'s review was cut where it
# says the shade did not suit her daughter's very pale skin, under "none is edited")
_rev = os.environ.get('SF_REVIEWS', '')
if _rev and Path(_rev).is_file():
    import yaml
    _n = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s).replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('—', '-')).strip()
    _by = {}
    for r in json.loads(Path(_rev).read_text())['reviews']: _by.setdefault(r.get('name', '').split(',')[0].strip(), []).append(_n(re.sub(r'\.\.\.$', '', r.get('body', ''))))
    def _walk(o, at=''):
        if isinstance(o, dict):
            t, who = o.get('text') or o.get('body') or o.get('quote'), o.get('by') or o.get('author') or o.get('name') or o.get('quote_by')
            if isinstance(t, str) and isinstance(who, str): yield at, who, t
            if isinstance(o.get('quote'), str) and isinstance(o.get('quote_by'), str): yield at, o['quote_by'], o['quote']
            for k, v in o.items(): yield from _walk(v, f'{at}.{k}')
        elif isinstance(o, list):
            for i, v in enumerate(o): yield from _walk(v, f'{at}[{i}]')
    _quoted = 0
    for _f in sorted((PROJECT / 'src' / F.SLUG).glob('*.html')):
        _m = re.match(r'---\n(.*?)\n---\n', _f.read_text(encoding='utf-8'), re.S)
        for at, who, t in (_walk(yaml.safe_load(_m.group(1))) if _m else []):
            name = re.split(r'[,(]', who)[0].strip()
            if name not in _by: continue
            _quoted += 1
            q = _n(t).strip('"')
            parts = [x.strip() for x in q.split('…') if x.strip()]
            if not all(any(x in b for b in _by[name]) for x in parts): fail(_f.stem, f'{at}: {name}\'s quote is not her imported words: "{q[:80]}…"')
            elif q not in _by[name] and '…' not in q: fail(_f.stem, f'{at}: {name}\'s review is shortened with no "…"')
    if not _quoted: fail('reviews', 'no quote matched a reviewer in SF_REVIEWS (the names changed?)')
else:
    print('check_apf: SF_REVIEWS not set: the quotes were not checked against the imported reviews')

# the sales page reports its pack to the ad pixels (AppLovin Axon) without touching the cart: view_item from its
# next-analytics-view-item tag, add_to_cart from next.trackAddToCart on the checkout button. A cart add there
# (next.addItem) doubles the order, because the checkout's pack selector keeps every line it did not add itself and
# then adds the pack its forceBundleId names (live 29 Oct: a $75 pack reached the checkout as $150).
_js = (SITE / 'js' / 'sf-apf.js').read_text(encoding='utf-8')
if re.search(r'\.(?:addItem|clearCart|swapPackage)\(', _js): fail('offer', 'sf-apf.js changes the cart (next.addItem/clearCart): the checkout would sell the pack twice')
if 'trackAddToCart(' not in _js: fail('offer', 'sf-apf.js does not report the checkout button as an add_to_cart')
if not re.search(r'<meta name="next-analytics-view-item" content="\d+">', html('offer')): fail('offer', 'no next-analytics-view-item tag (no view_item for the ad pixels)')
_vi = re.search(r'<meta name="next-analytics-view-item" content="(\d+)">', html('offer'))
_on = re.search(r'<label class="sf-pack is-on"[^>]*data-package="(\d+)"', html('offer'))
if _vi and _on and _vi.group(1) != _on.group(1): fail('offer', f'view_item reports package {_vi.group(1)}, the page opens on package {_on.group(1)} (live 29 Oct: $57 reported for the $75 pack)')

# a reason's photo or loop sticks beside its text only where the two stand side by side: a one-column (wide) reason's
# media must scroll with the page, or the text under it slides beneath the stuck video (the owner, 29 Oct 2026)
_css = (SITE / 'css' / 'sf-funnel.css').read_text(encoding='utf-8')
if not re.search(r'\.sf-reason--wide \.sf-reason__media \{[^}]*position:\s*static', _css): fail('listicle', 'a wide reason\'s media is sticky: it slides over the text under it')

# the Axon adapter sends item_category_id only when it is a number: the SDK's item_category is the campaign's name,
# and Axon rejects the whole event with HTTP 400 for a text id (live review 6, 29 Oct 2026)
_ax = (SITE / 'js' / 'axon.adapter.js').read_text(encoding='utf-8')
if 'out.item_category_id = it.item_category' in _ax or 'Number(it.item_category)' not in _ax:
    fail('all pages', 'axon.adapter.js sends the text item_category as item_category_id (Axon answers 400 to view_item, begin_checkout and purchase)')

if problems:
    print('\n'.join(problems)); print(f'check_apf: {len(problems)} problems'); sys.exit(1)
print(f'check_apf: {len(F.PAGES)} pages ok')
