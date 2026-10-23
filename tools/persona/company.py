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
EMAIL = 'hello@skinofab.com'
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
    (r'(?:hey|info|contact)@skinofab\.com', EMAIL, True),
    # the collaboration agreement: the company's own state and courts
    (r'laws of the State of Delaware', f'laws of the State of {STATE}', False),
    (r'courts located in Wilmington, Delaware', f'courts located in Boulder County, {STATE}', False),
    (r'Last Updated: August 4, 2024', f'Last Updated: {UPDATED}', False),
]

CONTACT_INFO = (f'<p><strong>Trade name:</strong> {BRAND}</p>'
                f'<p><strong>Company:</strong> {LEGAL_NAME}, a {STATE} corporation ({REGISTRY}, company number {COMPANY_NUMBER})</p>'
                f'<p><strong>Email:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>'
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
             f'<p><b>Kontakt:</b><br>E-Mail: <a href="mailto:{EMAIL}">{EMAIL}</a><br>Webseite: {WEBSITE}</p>'
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
