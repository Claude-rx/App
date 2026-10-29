"""The sales page's copy deck (docs/apf-funnel/copy-deck.md): the 20 sections of the long sales page in the
long-sales-page skill's deck format, generated from the page's own frontmatter (campaigns/skinofab/src/apf-funnel/
adaptive-foundation-offer.html), so the deck and the page can never disagree.

usage: python3 -I tools/funnel/apf/copy_deck.py [--validator <path to the skill's validate_copy.py>]

The page is the source: edit its frontmatter, run this, and the deck is validated with the skill's validator when one is
found (the default path below, or --validator); its report is printed and a deck with errors fails the run. The images
the page shows are named as briefs ([IMAGE: …], [VIDEO: …]) with the file the funnel serves, since the deck is a document
and not the page; the reviews are the page's, with the buyers' photos.
"""
import os, re, subprocess, sys
from html import unescape
from pathlib import Path
import yaml

os.environ['FUNNEL'] = 'apf'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import funnel as F

ROOT = HERE.parents[2]
PAGE = ROOT / 'campaigns' / 'skinofab' / 'src' / F.SLUG / (F.BY_ID['offer']['file'] + '.html')
OUT = ROOT / 'docs' / 'apf-funnel' / 'copy-deck.md'
HOST = F.FUNNEL_HOST
CHECKOUT = HOST + F.route('checkout', served=True)
SALES = HOST + F.route('offer', served=True)
VALIDATOR = Path('/root/.claude/skills/synced/ed788572-c450-4483-91f6-5cfc39c30887_bfd58911-f832-4256-b134-0fe0d46ca616/long-sales-page/scripts/validate_copy.py')
ORIGIN = 'Verified buyer, from our earlier store'


def frontmatter(path):
    m = re.match(r'---\n(.*?)\n---\n', path.read_text(encoding='utf-8'), re.S)
    return yaml.safe_load(m.group(1))


def md(s):
    """The page's inline HTML as markdown."""
    s = str(s)
    s = re.sub(r'<strong>(.*?)</strong>', r'**\1**', s)
    s = re.sub(r'<em>(.*?)</em>', r'*\1*', s)
    s = re.sub(r'<a href="([^"]+)">(.*?)</a>', r'[\2](\1)', s)
    return unescape(re.sub(r'<[^>]+>', '', s)).strip()


def cta(label, pack='apf-2'):
    return f'[CTA: {md(label).replace("→", "").strip()} | {CHECKOUT}?forceBundleId={pack}]'


def offer_token(p):
    note = p['supply'] + ' · free shipping' + (' · ' + ' + '.join(g['name'] for g in p['gifts']) if p.get('gifts') else '')
    return f"[OFFER: {p['name']} | {p['price']} | {p['compare']} | {note} | {p.get('tab', '')}]"


def deck(fm):
    hero, g, o, ba, pr, u, gs, v, rs, sv = (fm[k] for k in ('hero', 'guarantee', 'offer', 'before_after', 'proof', 'usage', 'guarantee_section', 'value', 'reviews_section', 'service'))
    packs = {p['id']: p for p in fm['packs']}
    policy = {'shipping': f'{HOST}/shipping-policy/', 'returns': f'{HOST}/refund-policy/'}
    sections = []

    def sec(title, *lines): sections.append((title, [l for l in lines if l is not None]))

    sec('01 · Hero Image or GIF',
        '[IMAGE: images/sf/hero.jpg — the hero collage: women over 45 with the real bottle, one with the foundation dotted white on her cheek before it blends, the SKINOFAB wordmark]',
        f"[VIDEO: images/sf/howto.mp4 (poster images/sf/howto-poster.jpg) — {hero['video_label']}]")
    sec('02 · Headline', f"### {md(hero['headline'])}", hero['sub'], f"[TRUST: {'; '.join(hero['trust'])}]", cta(hero['button']), f"*{hero['note']}*")
    sec('03 · Summary', fm['summary'])
    sec('04 · Key Benefits with Guarantee', '### Why women over 45 keep this one', *[f'- {md(b)}' for b in fm['benefits']],
        f"[GUARANTEE: {g['title']} — {md(g['short'])}]")
    sec('05 · Call to Action with Offer', f"### {o['title']}", o['lead'], *[offer_token(p) for p in fm['packs']], cta(o['button']),
        f"[TRUST: {'; '.join(o['trust'])}]", o['once'])
    p = fm['problem']
    sec('06 · State the Problem Clearly', f"### {p['title']}", *[f"- **{s['time']}** {s['text']}" for s in p['scenes']], p['close'])
    m = fm['mechanism']
    sec('07 · Explain the Problem Mechanism', f"### {m['title']}", m['lede'], *sum([[f"#### {c['title']}", c['text']] for c in m['causes']], []), m['end'])
    s = fm['solution']
    sec('08 · Detail the Solution Mechanism', f"### {s['title']}", s['lede'], *sum([[f"#### {c['title']}", c['text']] for c in s['parts']], []), s['note'],
        '[IMAGE: images/sf/g-inside.jpg — the “what’s inside” infographic: the actives (PDRN, peptides, Pro-Xylane, niacinamide, adenosine), the hydrators (two hyaluronic acids, ceramide NP, squalane, panthenol), fragrance-free]',
        '[IMAGE: images/sf/g-dots.jpg — a woman in her fifties, eyes closed, the foundation dotted white on her cheeks before it blends]')
    c = fm['compare']
    sec('09 · Clarify Why Other Solutions Fall Short', f"### {c['title']}", c['lede'],
        f"| {c['what']} | SKINOFAB {c['us']} | {c['them']} |", '|---|---|---|', *[f"| {r['label']} | ✓ {r['us']} | {'✕' if r['mark'] == 'no' else '–'} {r['them']} |" for r in c['rows']],
        '[IMAGE: images/sf/old-routine.jpg — the old routine: a woman in her late fifties at a vanity crowded with a primer, four foundations, concealers, powder, a contour palette and brushes, fed up]')
    w = fm['why']
    sec('10 · Explain Why Your Solution is Effective', f"### {w['title']}", w['lede'],
        *sum([[f"> “{x['quote']}”" + (f" — {x['source']}" if x['source'] else ''), x['fix']] for x in w['fixes']], []))
    sec('11 · Include Before and After Scenarios', f"### {ba['title']}", ba['lede'],
        *sum([[f"[IMAGE: {i['image']} — {i['alt']}]", f"*{i['caption']}*"] for i in ba['items']], []),
        f"[BEFORE: {'; '.join(ba['before'])}]", f"[AFTER: {'; '.join(ba['after'])}]", *[f"> “{b['review']['text']}” — {b['review']['name']}, verified buyer, from our earlier store ({b['review']['topic'].lower()})" for b in ba['items'] if b.get('review')], *([f"*{ba['label']}*"] if ba.get('label') else []))   # no label since 28 Oct 2026 (the owner: no illustration line)
    r = fm['ratings']
    sec('12 · Proof Elements', f"### {pr['title']}", f"[RATING: {r['average']} | {r['count']} verified reviews of this foundation, from our earlier store]",
        *sum([[f"#### {x['title']}", x['text']] for x in pr['cards']], []), *[f"> “{q['text']}” — {q['by']}" for q in pr['quotes']])
    pm = fm['promise']
    sec('13 · Big Promise and Dream Outcome', f"### {pm['title']}", md(pm['text']), cta(pm['button']))
    sec('14 · Usage Instructions', f"### {u['title']}", *[f"{i}. **{st['title']}** {st['text']}" for i, st in enumerate(u['steps'], 1)],
        f"#### {u['demos_title']}", u['demos_lede'], *[f"[VIDEO: images/sf/{d['key']}.mp4 — {d['caption']}]" for d in u['demos']],
        *[f"- **{t['when']}** {t['text']}" for t in u['timeline']])
    sec('15 · Feature an Ironclad Guarantee', f"### {gs['title']}", gs['text'], *[f'- {md(t)}' for t in gs['terms']], gs['why'],
        f"[GUARANTEE: {g['title']} — 30 days from delivery, a full refund even opened, nothing to send back]")
    sec('16 · Highlight an Irresistible Offer with Urgency', f"### {v['title']}", '| What you get | Value |', '|---|---|',
        *[f"| {x['item']} | {x['value']} |" for x in v['stack']], f"| **{v['total']['item']}** | **{v['total']['value']}** |",
        f"| **{v['today']['item']}** | **{v['today']['value']}** |", md(v['why_now']), offer_token(packs['apf-3']), cta(o['button'], 'apf-3'))
    sec('17 · Emphasize Scarcity', f"### {fm['scarcity']['title']}", fm['scarcity']['text'])
    sec('18 · Incorporate Customer Reviews with Images', f"### {rs['title']}", f"**{rs['stars']}** — {rs['lede']}",
        *[f"[REVIEW: {x['name']} | {ORIGIN} | {x['stars']} | | {x['text']} | {x['photo']} | yes]" for x in fm['reviews']],
        *[f"> “{q['text']}” — {q['by']}, verified buyer" for q in rs['more']], f"*{rs['note']}*")
    sec('19 · Address FAQs', '### Questions women ask before they order', *sum([[f"**Q: {x['q']}**", x['a']] for x in fm['faq']], []))
    sec('20 · Highlight Customer Service Options', f"### {sv['title']}", sv['text'],
        *[f"- [{x['title']}]({policy.get(x['href'], x['href'])}) — {x['text']}" for x in sv['cards']])
    return sections


def write(fm):
    front = {
        'brand': 'SKINOFAB', 'product': 'Adaptive Peptide Foundation', 'language': 'en', 'direction': 'ltr', 'currency': 'USD',
        'primary_color': '"#151515"', 'accent_color': '"#e8a33d"', 'cta_url': f'{CHECKOUT}?forceBundleId=apf-3', 'cta_label': 'GET MY FOUNDATION',
        'font_heading': 'Playfair Display', 'font_body': 'Montserrat', 'support_email': F.EMAIL, 'company': 'SKINOFAB',
        'shipping_url': f'{HOST}/shipping-policy/', 'refund_url': f'{HOST}/refund-policy/', 'privacy_url': f'{HOST}/privacy-policy/',
        'terms_url': f'{HOST}/terms-of-service/', 'contact_url': f'{HOST}/contact/', 'announcement': fm['offer_bar'],
        'disclaimer': 'Cosmetic claims only: the foundation evens the look of skin tone and keeps dry skin comfortable; it treats nothing and has no SPF. Individual results vary. Contains salmon-derived PDRN: not for anyone with a fish allergy. The before/after images are AI illustrations of what a thin layer of foundation does to the look of skin tone, not customer photos.',
    }
    out = ['---', *[f'{k}: {v}' for k, v in front.items()], '---', '',
           '# Strategy', '',
           f'Generated by tools/funnel/apf/copy_deck.py from the sales page\'s frontmatter ({PAGE.relative_to(ROOT)}); the page at {SALES} is the deliverable, this deck its copy in the 20-section format. Persona: docs/apf-funnel/persona.md (Linda, 56).', '',
           '- **Big idea:** the shade that matched at 45 looks wrong at 56 because her tone moved and her skin got drier; a foundation that adapts to her tone, in a serum made for skin after 45, ends the shade guessing.',
           '- **Problem mechanism (07):** the fixed-shade trap: several tones in one face, thinner and drier skin, formulas built for 25-year-old skin.',
           '- **Solution mechanism (08):** encapsulated pigments that go on white and open toward her tone, in a hydrating serum base with soft-focus powders and the actives named on the label.',
           '- **Offer architecture:** 1 bottle $39 ($47 in our store), 2 bottles $57 with the Blender sponge and a mystery gift (two months), 3 bottles $75 with the Lymphatic Brush and both gifts (\"Buy 2, get 1 FREE\": less than two single bottles at $78; the sales page opens on it); one-time, free shipping, 30-day money-back guarantee even opened, nothing to send back. Post-purchase: offer 1 supply cards (2 bottles $39, 6 bottles $99 with the brush), offer 2 one bottle $23 (downsell $19), offer 3 the brush $14 (downsell $9).',
           '- **Proof inventory:** 9,855 imported reviews of this foundation (4.8), the buyers\' own photos, the actives printed on the label and box, formulated in Korea, the guarantee, the owner’s before/after photos; no clinical study, no medical claim, no fabricated review.',
           '- **Urgency:** honest only: the launch gift (the brush) while launch stock lasts, the price only on this page; no countdown.', '']
    for title, lines in deck(fm):
        out += [f'## {title}', '', *sum([[l, ''] for l in lines], [])]
    OUT.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')
    return OUT


if __name__ == '__main__':
    path = write(frontmatter(PAGE))
    print(path.relative_to(ROOT))
    validator = Path(sys.argv[sys.argv.index('--validator') + 1]) if '--validator' in sys.argv else VALIDATOR
    if validator.is_file():
        r = subprocess.run([sys.executable, '-I', str(validator), str(path)], capture_output=True, text=True)
        print(r.stdout.strip()); sys.exit(r.returncode)
    print(f'(no validator at {validator}: the deck was not validated)')
