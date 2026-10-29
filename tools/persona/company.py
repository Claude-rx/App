"""The company behind SKINOFAB, the one source for every page that names it: footer, contact pages, legal pages,
FAQs, product data and the copy in tools/persona.

From the Colorado Secretary of State record (owner's brief, 23 Oct 2026): SYNDERRA INC, a domestic profit corporation
in good standing, company number 20258305259, registered agent Global Accounting service inc at 2525 Arapahoe Ave
Ste E4 Unit 1280, Boulder, CO 80302. The store's mailing address is the registered agent's (the company gives no other).

The export carried the old store's company in every footer and legal page (Smooche's "LLC" and its West Hollywood
mailbox, renamed by the rebrand), a placeholder German Impressum ("John M. Schneider", "+49 (0)30 12345678",
"HRB 123456 B") and another company's Impressum (Xevio GmbH, Cologne). apply_persona.py rewrites all of it with
rewrite(): block rewrites for the pages that list company details, then plain replacements on every text file.
"""
import re

BRAND = 'SKINOFAB'
LEGAL_NAME = 'Synderra Inc'
STATE = 'Colorado'
COMPANY_NUMBER = '20258305259'                     # Colorado Secretary of State
REGISTRY = 'Colorado Secretary of State'
STREET, SUITE = '2525 Arapahoe Ave', 'Ste E4 Unit 1280'
CITY, REGION, POSTCODE, COUNTRY = 'Boulder', 'CO', '80302', 'United States'
AGENT = 'Global Accounting service inc'
EMAIL = 'info@skinofab.com'                       # the owner, 29 Oct 2026: every customer-support contact
PHONE = '+1 (563) 239-5520'
PHONE_TEL = '+15632395520'                         # for tel: links
WEBSITE = 'www.skinofab.com'
UPDATED = 'October 23, 2026'                       # the legal pages' "last updated" after the change

ADDRESS_LINE = f'{STREET}, {SUITE}, {CITY}, {REGION} {POSTCODE}, {COUNTRY}'
AGENT_LINE = f'{AGENT}, {STREET} {SUITE}, {CITY}, {REGION} {POSTCODE}, {COUNTRY}'

# plain replacements on every text page and data file, most specific first; (pattern, replacement, regex?)
RULES = [
    (r'"vendor":\s*"Skinofab LLC"', '"vendor":"SKINOFAB"', True),
    (r'Skinofab is headquartered at 8605 Santa Monica Boulevard, PMB 44698, West Hollywood, CA 90069, USA\. '
     r'We ship worldwide to 65\+ countries\.',
     f'SKINOFAB is a brand of {LEGAL_NAME}, {STREET}, {SUITE}, {CITY}, {REGION} {POSTCODE}, USA. '
     'We ship to every country offered at checkout.', True),
    (r'8605 Santa Monica Boulevard, PMB 44698(,?)', f'{STREET}, {SUITE}\\1', True),
    (r'West Hollywood,? CA 90069', f'{CITY}, {REGION} {POSTCODE}', True),
    (r'Skinofab LLC', LEGAL_NAME, False),
    (r'<span>© (\d{4}) Skinofab\.</span>', f'<span>© \\1 {LEGAL_NAME}. {BRAND} is a brand of {LEGAL_NAME}.</span>', True),
    (r'(?:hey|hello|contact)@skinofab\.com', EMAIL, True),   # (hello@ until 29 Oct 2026)
    # the support phone beside the support email (the owner, 29 Oct 2026): the footer on every page, the contact page's
    # "Email us" card, the FAQ's how-to-reach-us answer (each once: the lookaheads keep a rebuild from adding it twice)
    (r'(<a class="sf__email" href="mailto:[^"]+">[^<]+</a>)(?!<br/><a class="sf__email sf__phone")',
     f'\\1<br/><a class="sf__email sf__phone" href="tel:{PHONE_TEL}">{PHONE}</a>', True),
    (r'(<div class="cs-info__item">\s*<div class="cs-info__label">Email us</div>\s*<div class="cs-info__value"><a href="mailto:[^"]+">[^<]+</a></div>\s*</div>)(?!<div class="cs-info__item"><div class="cs-info__label">Call us)',
     f'\\1<div class="cs-info__item"><div class="cs-info__label">Call us</div><div class="cs-info__value"><a href="tel:{PHONE_TEL}">{PHONE}</a></div></div>', True),
    (r'(<a href="mailto:[^"]+">[^<]+</a>), or use the form on our', f'\\1, call <a href="tel:{PHONE_TEL}">{PHONE}</a>, or use the form on our', True),
    # one reply time everywhere: the funnels and the policies say a person replies within one business day (live review 10)
    (r'We reply within 24 hours, Monday to Friday\.', 'A person replies within one business day, Monday to Friday.', True),
    # the privacy policy names AppLovin (Axon), the ad pixel on the funnels and the store (live review 10): an entry after
    # TikTok's in the advertising section, in the same form, and AppLovin among the third parties of that purpose
    (r'(?s)(<h4>TikTok conversion tracking \(TikTok Pixel\)</h4>(?:(?!<details).)*?</details>\n)(?!<details class="legalDoc__accordion" data-sf-applovin>)', '\\1' + '<details class="legalDoc__accordion" data-sf-applovin>\n<summary>\n<figure>\n\n</figure>\n<div>\n<h4>AppLovin conversion tracking (Axon pixel)</h4>\n<div class="accordion__meta">\n<p class="meta__company"><span class="sr-only">Company: </span>AppLovin Corporation</p>\n<p class="meta__location"><span class="sr-only">Place of processing: </span>United States</p>\n<p class="meta__keys"><span class="sr-only">Personal Data processed: </span> Trackers +1</p>\n</div>\n</div>\n</summary>\n<div class="accordion__body">\n<p>AppLovin conversion tracking (Axon pixel) is an analytics and behavioral targeting service provided by AppLovin Corporation that connects data from the AppLovin advertising network with actions performed on this Application. The Axon pixel tracks page views, products viewed, items added to the cart, checkouts started and purchases, so that ads in the AppLovin network can be measured and shown to groups of Users on the base of their past use of this Application.</p>\n<div class="body__details-box">\n<h5>Personal Data processed:</h5>\n<ul>\n<li>Trackers</li>\n<li>Usage Data</li>\n</ul>\n<h5>Service provided by:</h5>\n<ul>\n<li>AppLovin Corporation (United States) – <a href="https://www.applovin.com/privacy/" rel="noopener noreferrer" target="_blank">Privacy Policy</a></li>\n</ul>\n<h5>Category of Personal Information collected according to the CCPA</h5>\n<ul>\n<li>internet or other electronic network activity information</li>\n</ul>\n<h5>This processing constitutes:</h5>\n<ul>\n<li>a Sale in the United States</li>\n</ul>\n</div>\n</div>\n</details>\n', True),
    (r'TikTok Inc\.,(?! AppLovin Corporation,)', 'TikTok Inc., AppLovin Corporation,', True),
    # "Your privacy choices" (live review 11: the privacy policy promises a privacy choices link, and no page had one): the
    # store footer links the opt-out page, and that page's opt-out works. The export's form was a Shopify privacy app's
    # empty container (it needs the app's script, which NEXT has not got): in its place one button opts this browser out
    # (a cookie for every skinofab.com host and this browser's storage, which the funnels' pixel gate reads like GPC), and
    # a ready-made email opts out the customer account
    (r'(<a href="/cookie-policy/">Cookie policy</a>)(</nav>)', '\\1<a href="/data-sharing-opt-out/">Your privacy choices</a>\\2', True),
    (r'<div data-description=\'[^\']*\'[^>]*id="pc--optOutFormContainer"></div>',
     '<div class="sf-optout" data-sf-optout>'
     '<h2>Opt out on this browser</h2>'
     '<p>One tap and our offer pages stop loading the AppLovin advertising pixel in this browser, as they do for a browser that sends the Global Privacy Control signal.</p>'
     '<p><button type="button" class="btn btn--primary btn--solid" data-sf-optout-btn>Opt out on this browser</button></p>'
     '<p data-sf-optout-done hidden><strong>This browser is opted out.</strong> If you clear your cookies, or use another browser or device, opt out there too.</p>'
     '<h2>Opt out for your customer account</h2>'
     f'<p>Send our ready-made email from the address you order with: <a href="mailto:{EMAIL}?subject=Do%20not%20sell%20or%20share%20my%20personal%20information'
     '&amp;body=Please%20opt%20me%20out%20of%20the%20sale%20or%20sharing%20of%20my%20personal%20information%20and%20of%20targeted%20advertising.%20I%20order%20with%20this%20email%20address.">'
     f'Opt out my account</a>. Or write to {EMAIL} or call {PHONE}. A person replies within one business day.</p>'
     '</div>'
     '<script>(function () { var box = document.querySelector("[data-sf-optout]"); if (!box) return;'
     ' var btn = box.querySelector("[data-sf-optout-btn]"), done = box.querySelector("[data-sf-optout-done]");'
     ' var on = function () { var c = /(?:^|;\\\\s*)sf_optout=1/.test(document.cookie); try { c = c || localStorage.getItem("sf_optout") === "1"; } catch (e) {} return c; };'
     ' var show = function () { if (on()) { done.hidden = false; btn.disabled = true; btn.textContent = "Opted out"; } };'
     ' btn.addEventListener("click", function () { var d = /(^|\\\\.)skinofab\\\\.com$/.test(location.hostname) ? "; domain=.skinofab.com" : "";'
     ' document.cookie = "sf_optout=1; max-age=63072000; path=/; SameSite=Lax" + d; try { localStorage.setItem("sf_optout", "1"); } catch (e) {} show(); done.focus && done.setAttribute("tabindex", "-1"); done.focus(); });'
     ' show(); })();</script>', True),
    # the collaboration agreement: the company's own state and courts
    (r'laws of the State of Delaware', f'laws of the State of {STATE}', False),
    (r'courts located in Wilmington, Delaware', f'courts located in Boulder County, {STATE}', False),
    (r'Last Updated: August 4, 2024', f'Last Updated: {UPDATED}', False),
]

CONTACT_INFO = (f'<p><strong>Trade name:</strong> {BRAND}</p>'
                f'<p><strong>Company:</strong> {LEGAL_NAME}, a {STATE} corporation ({REGISTRY}, company number {COMPANY_NUMBER})</p>'
                f'<p><strong>Email:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>'
                f'<p><strong>Phone:</strong> <a href="tel:{PHONE_TEL}">{PHONE}</a></p>'
                f'<p><strong>Address:</strong> {LEGAL_NAME}, {ADDRESS_LINE}</p>'
                f'<p><strong>Registered agent:</strong> {AGENT_LINE}</p>')

# German legal notice (§ 5 DDG, which replaced § 5 TMG in May 2024). The person authorised to represent the company
# is not in the record: add OFFICER once the owner names them.
OFFICER = None
IMPRESSUM = ('<p><b>Angaben gemäß § 5 DDG</b></p>'
             f'<p>{LEGAL_NAME}<br>{STREET}, {SUITE}<br>{CITY}, {REGION} {POSTCODE}<br>USA</p>'
             f'<p><b>Rechtsform:</b> Corporation nach dem Recht des US-Bundesstaats {STATE}</p>'
             + (f'<p><b>Vertreten durch:</b> {OFFICER}</p>' if OFFICER else '') +
             f'<p><b>Registereintrag:</b> {REGISTRY}, Company Number {COMPANY_NUMBER}</p>'
             f'<p><b>Registered Agent:</b> {AGENT_LINE.replace(COUNTRY, "USA")}</p>'
             f'<p><b>Kontakt:</b><br>E-Mail: <a href="mailto:{EMAIL}">{EMAIL}</a><br>Telefon: <a href="tel:{PHONE_TEL}">{PHONE}</a><br>Webseite: {WEBSITE}</p>'
             '<p><b>Verbraucherstreitbeilegung:</b> Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren '
             'vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>')


def _rte_after(t, heading_rx):
    """(start, end) of the first <div class="rte"> after the heading matching heading_rx, or None."""
    h = re.search(heading_rx, t)
    if not h: return None
    m = re.search(r'<div class="rte">', t[h.end():])
    if not m: return None
    start = h.end() + m.end()
    depth, i = 1, start
    for tag in re.finditer(r'<(/?)div\b[^>]*>', t[start:]):
        depth += -1 if tag.group(1) else 1
        if depth == 0: return start, start + tag.start()
    return None


def rewrite(rel, t):
    """The page at export-relative path rel, with the real company everywhere. Returns (text, changes)."""
    n = 0
    if rel in ('policies/contact-information.html',):
        span = _rte_after(t, r'<h1>Contact information</h1>')
        if span: t, n = t[:span[0]] + CONTACT_INFO + t[span[1]:], n + 1
    if rel in ('pages/impressum.html', 'pages/impressum-1.html'):
        span = _rte_after(t, r'<h1 class="page-title text-center">Impressum</h1>')
        if span:
            body = t[span[0]:span[1]]
            keep = re.search(r'<(?:p|h[1-6])[^>]*>\s*<b>Haftungsausschluss', body)   # the generic liability disclaimer stays
            t, n = t[:span[0]] + IMPRESSUM + (body[keep.start():] if keep else '') + t[span[1]:], n + 1
        # the page descriptions (search, social) quoted the old notices
        t = re.sub(r'(<meta content=")[^"]*("\s+(?:name="(?:description|twitter:description)"|property="og:description")\s*/?>)',
                   lambda m: m.group(1) + f'Impressum: {LEGAL_NAME}, {ADDRESS_LINE}. {EMAIL}' + m.group(2), t)
    for rx, new, is_rx in RULES:
        t, k = (re.subn(rx, new, t) if is_rx else (t.replace(rx, new), t.count(rx)))
        n += k
    return t, n
