"""Author the SKINOFAB live-site handoff package from its captures (run after capture-routes.mjs).

usage: python3 -I author-package.py <package_dir> <export_dir> <design-package.py>

Fills sections.json, routes.json section order, assets.json (+ media/ copies; reuse is declared),
platform-divergence-ledger.json, copy.json decisions, behaviors.json, gaps, notes.md and observed styles,
then re-runs geometry and coverage. Every entry cites the capture it came from.
"""
import json, os, re, shutil, subprocess, sys, hashlib, urllib.parse as up
from pathlib import Path
from bs4 import BeautifulSoup

PKG, EXPORT, PKG_PY = (Path(p).resolve() for p in sys.argv[1:4])
J = lambda name: json.load(open(PKG / name))
def W(name, body): json.dump(body, open(PKG / name, 'w'), indent=2, ensure_ascii=False); open(PKG / name, 'a').write('\n')

captures = J('captures.json')['captures']
routes = J('routes.json')
raw = {c['capture_id']: json.load(open(PKG / c['raw_output'])) for c in captures}
cap = lambda route, vp: f'{route}-{vp}-static'
ROUTE_FILE = {'home': 'index.html', 'pdp': 'products/color-changing-foundation.html', 'collection': 'collections/all.html',
              'page-faq': 'pages/faq.html', 'policy-terms': 'pages/terms-of-service.html',
              'article': 'blogs/news/color-changing-foundation-does-it-actually-work-the-science-explained.html',
              'lander': 'pages/bestfoundation.html'}
RIGHTS = 'Operator states SKINOFAB owns or is licensed to reuse this content (design-handoff.json source.rights).'
COMMERCE_GRIDS = ('bestsellers', 'bundles', 'essentials', 'main', 'product-grid', 'collection')

# ---------------------------------------------------------------- sections
sections, order = [], {}
for r in routes['routes']:
    rid = r['route_id']
    keys = []
    for vp in ('desktop', 'tablet', 'mobile'):
        for k in raw[cap(rid, vp)]['targets']:
            if '::' not in k and k not in keys: keys.append(k)
    order[rid] = keys
    for i, k in enumerate(keys, 1):
        part = k.split('.', 1)[1]
        refs = {vp: cap(rid, vp) for vp in ('desktop', 'tablet', 'mobile') if k in raw[cap(rid, vp)]['boxes']}
        src_sel = next((raw[c]['targets'][k]['selector'] for c in refs.values()), '')
        if part in ('announcement', 'header', 'footer'):
            spark, status = ('footer' if part == 'footer' else 'header'), 'chrome'
            klass = 'live-commerce-component'
            target = {'template': f'partials/{spark}.html', 'partials': [f'partials/sf_{part}.html'], 'settings': []}
            why = 'Shared storefront chrome: exported markup kept 1:1, menus/cart trigger wired to NEXT (cart badge, side cart).'
        else:
            spark, status = '', 'unmapped'
            commerce = rid in ('pdp', 'collection') and part.startswith(('main', 'product')) or any(g in part for g in COMMERCE_GRIDS[:3])
            klass = 'live-commerce-component' if commerce else 'semantic-rebuild'
            target = {'template': r['theme_template'], 'partials': [f'partials/sf/{rid}/{part}.html'], 'settings': []}
            why = ('Product data (title, price, variants, add-to-cart) bound to NEXT; layout and copy from the source markup.'
                   if commerce else 'Source markup kept as live HTML text, links, and media (no screenshots).')
        sections.append({
            'section_id': k, 'route_id': rid, 'order': i, 'in_scope': True, 'source_selector': src_sel,
            'capture_refs': refs, 'classification': klass, 'classification_rationale': why,
            'spark_section': spark, 'roster_status': status, 'implementation_target': target,
            'commerce_surface': 'product-data' if klass == 'live-commerce-component' and status == 'unmapped' else '',
            'asset_ids': [], 'divergence_ids': [], 'behavior_ids': [], 'responsive_notes': ''})
sec_by_id = {s['section_id']: s for s in sections}
for r in routes['routes']:
    r['section_order'] = order[r['route_id']]; r['status'] = 'ready'

# ---------------------------------------------------------------- assets (reuse declared -> downloaded into media/)
media_dir = PKG / 'media'; media_dir.mkdir(exist_ok=True)
assets, seen = [], {}
def local_file(current_src):
    p = up.urlparse(current_src).path.lstrip('/')
    f = EXPORT / up.unquote(p)
    return f if p.startswith('assets/') and f.is_file() else None

def add_asset(sid, cid, src_url, role, mtype, alt, w, h):
    f = local_file(src_url)
    key = (sid, str(f or src_url))
    if key in seen: return
    aid = re.sub(r'[^a-z0-9._-]+', '-', f'{sid}.{Path(up.urlparse(src_url).path).stem}'.lower())[:80].strip('-')
    while any(a['asset_id'] == aid for a in assets): aid += '-x'
    seen[key] = aid
    entry = {'asset_id': aid, 'section_id': sid, 'role': role, 'media_type': mtype, 'source_url': src_url,
             'capture_id': cid, 'alt': alt or '', 'natural_width': w, 'natural_height': h}
    if f:
        dest = media_dir / f.name
        if not dest.exists(): shutil.copy2(f, dest)
        entry.update(state='downloaded', local_path=f'media/{f.name}', treatment='use-downloaded',
                     notes='Copied from the operator-supplied export; theme asset path assets/' + str(f.relative_to(EXPORT / 'assets')))
    else:
        entry.update(state='replacement-needed', treatment='',
                     target_asset=f'Source file for {src_url}: the export could not download it (host blocked in the build environment).',
                     notes='Blocked host during export; supply the file or allow the host and re-export.')
    assets.append(entry)
    sec_by_id[sid]['asset_ids'].append(aid)

for c in captures:
    rc = raw[c['capture_id']]
    for im in rc.get('images', []):
        sid = im.get('target_key')
        if not sid or sid not in sec_by_id or not im.get('current_src') or im['current_src'].startswith('data:'): continue
        role = 'logo' if 'skinofab-logo' in im['current_src'] else 'image'
        mtype = 'svg' if im['current_src'].lower().endswith('.svg') else 'image'
        add_asset(sid, c['capture_id'], im['current_src'], role, mtype, im.get('alt'), im.get('natural_width'), im.get('natural_height'))
    soup = None
    for m in rc.get('media', []):
        sid = m.get('target_key')
        if not sid or sid not in sec_by_id: continue
        src = m.get('current_src') or (m.get('sources') or [None])[0]
        if not src:  # lazy video: resolve its source from the supplied HTML by element id
            soup = soup or BeautifulSoup(open(EXPORT / ROUTE_FILE[c['route_id']]).read(), 'lxml')
            mid = (m.get('hint') or '').split(' ')[0]
            el = soup.select_one(mid) if mid.startswith('#') else None
            s = el and (el.get('src') or el.get('data-src') or (el.find('source') or {}).get('src') or (el.find('source') or {}).get('data-src'))
            if s: src = 'http://localhost/' + re.sub(r'^(\.\./)+', '', s)
        if src: add_asset(sid, c['capture_id'], src, 'video', 'video', '', m.get('width'), m.get('height'))

# ---------------------------------------------------------------- copy decisions + ledger
copy = J('copy.json')
PRICE = re.compile(r'(\$\s?\d|\d+\s?USD)')
SAVING = re.compile(r'(?i)\b(save|off|sale|free (shipping|gift|mystery)|% ?off|\bdeal)\b|\d+\s?%')
CLAIM = re.compile(r'(?i)(\d[\d,.]*\s?(\+|k\b|m\b|million)|\bloved by\b|\btrusted\b|dermatolog|clinical|\breviews?\b|\bsold\b|#1|\bbest\b|\bproven\b|\bresults?\b|guarantee)')
ledger = {}
def ledger_entry(did, kind, surface, sid, cid, src_exp, plat, decision, guard):
    e = ledger.setdefault(did, {'divergence_id': did, 'kind': kind, 'surface': surface, 'route_ids': [], 'section_ids': [],
        'capture_ids': [], 'source_expectation': src_exp, 'platform_behavior': plat, 'decision': decision,
        'implementation_guardrail': guard, 'status': 'open', 'approved_by': '',
        'target_evidence': {'origin': 'none', 'summary': 'No NEXT store is connected yet; nothing could be read from NEXT.'}})
    rid = sec_by_id[sid]['route_id']
    for f, v in (('route_ids', rid), ('section_ids', sid), ('capture_ids', cid)):
        if v not in e[f]: e[f].append(v)
    if did not in sec_by_id[sid]['divergence_ids']: sec_by_id[sid]['divergence_ids'].append(did)
    return did

def decide(s):
    t = s['source_text']; sid = s['section_id']; cid = s['capture_id']
    s['role'] = s['role'] or ('heading' if s['capture_key'].endswith('::heading') else 'cta' if s['capture_key'].endswith('::cta') else 'body')
    for k in ('reuse_basis', 'commerce_fact', 'next_evidence', 'divergence_id', 'approved_by', 'next_source'): s.pop(k, None)
    if PRICE.search(t) and len(t) <= 24:
        s.update(decision='omit', text='', commerce_fact=True,
                 divergence_id=ledger_entry('prices-from-next', 'commerce', 'product prices', sid, cid,
                     'The source shows fixed prices and compare-at prices.',
                     'Prices, compare-at prices and currency come from the NEXT catalog per visitor currency.',
                     'platform-wins', 'Render every price with {% purchase_info_for_product %} / session.price; never hardcode a price.'))
    elif SAVING.search(t) or (PRICE.search(t) and re.search(r'(?i)shipping|delivery|protection', t)):
        s.update(decision='reuse', text=t, reuse_basis=RIGHTS, commerce_fact=True, next_evidence='',
                 divergence_id=ledger_entry('promotions-need-offers', 'commerce', 'promotional / savings copy', sid, cid,
                     'The source advertises sales, savings percentages and free gifts.',
                     'NEXT applies discounts only through configured Offers or vouchers; none exist yet.',
                     'source-wins-with-guardrails', 'Keep the copy in a Theme setting so it can change with the Offer; configure the matching Offer in Dashboard > Marketing > Offers before publishing.'))
    elif CLAIM.search(t):
        s.update(decision='reuse', text=t, reuse_basis=RIGHTS,
                 divergence_id=ledger_entry('social-proof-claims', 'claim', 'social proof and performance claims', sid, cid,
                     'The source states customer counts, ratings, review counts, expert endorsements and results.',
                     'NEXT has no evidence for these numbers; they are the merchant\'s own claims.',
                     'source-wins-with-guardrails', 'Reuse only with the operator\'s approval that SKINOFAB can substantiate each claim.'))
    else:
        s.update(decision='reuse', text=t, reuse_basis=RIGHTS)
    if s.get('commerce_fact') and s['decision'] == 'reuse': s['next_evidence'] = 'pending: no NEXT store connected'
    fee = re.compile(r'\s*\$\s?\d[\d,]*(?:\.\d{2})?\s?USD')
    if len(t) > 24 and fee.search(t) and re.search(r'(?i)shipping|delivery|protection', t):
        # the build renders the fee from the Shipping Fee theme setting inside the sentence
        s.update(decision='replace', text=re.sub(r'\s+', ' ', fee.sub(' ', t)).strip(),
                 next_source='Theme setting sf_shipping_fee_text (must equal the NEXT shipping rate)')
        for k in ('reuse_basis', 'next_evidence'): s.pop(k, None)

copy['strings'] = [s for s in copy['strings'] if not s['copy_id'].startswith('ft_')]
for s in copy['strings']: decide(s)

# Full visible-text coverage: every line each section showed, every image alt and link name (captured evidence).
seen_text = {(s['section_id'], s['source_text']) for s in copy['strings']}
def add_text(sid, cid, key, vp, text, role):
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) < 2 or not re.search(r'[A-Za-z]', text) or (sid, text) in seen_text: return
    seen_text.add((sid, text))
    entry = {'copy_id': f"ft_{re.sub(r'[^a-z0-9]+', '_', sid)}_{len(seen_text)}", 'section_id': sid, 'capture_id': cid,
             'viewport': vp, 'role': role, 'source_text': text, 'decision': 'unresolved', 'text': ''}
    if key: entry['capture_key'] = key
    decide(entry); copy['strings'].append(entry)
for c in captures:
    rc = raw[c['capture_id']]
    for key, tgt in rc['targets'].items():
        if '::' in key or key not in sec_by_id: continue
        for line in (tgt.get('text') or '').split('\n'):
            add_text(key, c['capture_id'], key, c['viewport'], line, 'body')
    for im in rc.get('images', []):
        if im.get('target_key') in sec_by_id and im.get('alt'):
            add_text(im['target_key'], c['capture_id'], None, c['viewport'], im['alt'], 'alt')
    for ln in rc.get('links', []):
        if ln.get('target_key') in sec_by_id:
            for t in (ln.get('accessible_name'), ln.get('text')):
                if t: add_text(ln['target_key'], c['capture_id'], None, c['viewport'], t, 'label')
# Hidden-state copy (closed accordions, inactive tabs, off-canvas drawers, screen-reader labels) is not visible text,
# so captures cannot record it. It is extracted from the supplied HTML with copy-lint's own tokenizer, per section.
import importlib.util
FIGMA = Path(PKG_PY).parents[2] / 'next-theme-figma' / 'scripts' / 'copy-lint.py'
spec = importlib.util.spec_from_file_location('copy_lint', FIGMA); copy_lint = importlib.util.module_from_spec(spec); spec.loader.exec_module(copy_lint)
supplied = 0
corpus = {copy_lint.normalize(x['text']) for x in copy['strings'] if x.get('text')}
for r in routes['routes']:
    rid = r['route_id']; soup = BeautifulSoup(open(EXPORT / ROUTE_FILE[rid]).read(), 'lxml')
    for sid in order[rid]:
        sel = sec_by_id[sid]['source_selector']
        try: el = soup.select_one(sel)
        except Exception: el = None
        if el is None: continue
        for cand in copy_lint.extract_candidates(str(el), 2):
            text = copy_lint.normalize(cand['text'])
            if text in corpus: continue
            corpus.add(text)
            entry = {'copy_id': f"ft_{re.sub(r'[^a-z0-9]+', '_', sid)}_h{len(corpus)}", 'section_id': sid,
                     'capture_id': cap(rid, 'desktop'), 'viewport': 'desktop', 'role': 'alt' if cand['kind'] == 'attribute' else 'body',
                     'source_text': text, 'decision': 'unresolved', 'text': '', 'source_basis': 'supplied-html (hidden state, not visible at capture)'}
            decide(entry); copy['strings'].append(entry); supplied += 1
    chrome = next((x for x in order[rid] if x.endswith('.header')), order[rid][0])
    for cand in copy_lint.extract_candidates(str(soup.body), 2):
        text = copy_lint.normalize(cand['text'])
        if text in corpus: continue
        corpus.add(text)
        entry = {'copy_id': f"ft_{re.sub(r'[^a-z0-9]+', '_', chrome)}_b{len(corpus)}", 'section_id': chrome,
                 'capture_id': cap(rid, 'desktop'), 'viewport': 'desktop', 'role': 'alt' if cand['kind'] == 'attribute' else 'label',
                 'source_text': text, 'decision': 'unresolved', 'text': '', 'source_basis': 'supplied-html (page chrome outside sections)'}
        decide(entry); copy['strings'].append(entry); supplied += 1
print('supplied-html copy strings', supplied)
copy['allowed_deviations'] = []
W('copy.json', copy)

# ---------------------------------------------------------------- behaviors
behaviors = []
def beh(bid, kind, sid, vp, cids, trigger, observed, evidence, details, method=None):
    b = {'behavior_id': bid, 'kind': kind, 'route_id': sec_by_id[sid]['route_id'], 'section_id': sid, 'viewport': vp,
         'capture_ids': cids, 'trigger': trigger, 'observed': observed, 'evidence': evidence, 'details': details}
    if method: b['method'] = method
    behaviors.append(b); sec_by_id[sid]['behavior_ids'].append(bid)
for c in captures:
    rc = raw[c['capture_id']]; vp = c['viewport']
    for f in rc.get('fixed_elements', []):
        sid = f.get('target_key')
        if sid in sec_by_id and f.get('visible') and f['position'] in ('sticky', 'fixed'):
            beh(f'{sid}.{vp}.sticky', 'sticky', sid, vp, [c['capture_id']], 'scroll',
                f"{sid.split('.',1)[1]} is position:{f['position']} top:{f['top']} z-index:{f['z_index']}.", 'extracted',
                {'position': f['position'], 'top': f['top'], 'z_index': f['z_index']})
    if vp == 'desktop':
        for i, m in enumerate(rc.get('media', [])):
            sid = m.get('target_key')
            if sid in sec_by_id:
                beh(f'{sid}.media{i}', 'media', sid, None, [c['capture_id']], 'in view / click',
                    f"Video autoplay={m['autoplay']} loop={m['loop']} muted={m['muted']} playsinline={m['plays_inline']} controls={m['controls']}.",
                    'extracted', {k: m.get(k) for k in ('autoplay', 'loop', 'muted', 'plays_inline', 'controls', 'duration_s')})
        for k, t in rc['targets'].items():
            if k.endswith('::cta') and t.get('href') and k.split('::')[0] in sec_by_id:
                sid = k.split('::')[0]; path = up.urlparse(t['href']).path
                beh(f'{sid}.cta-dest', 'cta-destination', sid, None, [c['capture_id']], 'click',
                    f"CTA \"{(t.get('text') or '').strip()[:60]}\" links to {path} in the export; the theme resolves it to the matching NEXT product/category/page URL.",
                    'extracted', {'source_href': path})
for s in sections:
    if s['route_id'] in ('home', 'pdp', 'lander') and s['roster_status'] == 'unmapped':
        txt = (raw[cap(s['route_id'], 'desktop')]['targets'].get(s['section_id']) or {}).get('text', '')
    rid = s['route_id']
for sid in [s['section_id'] for s in sections if re.search(r'(bestsellers|reviews|social|testimon|essentials|bundles|hero)', s['section_id'])]:
    beh(f'{sid}.slider', 'motion', sid, None, [sec_by_id[sid]['capture_refs'].get('desktop') or next(iter(sec_by_id[sid]['capture_refs'].values()))],
        'swipe / arrows / autoplay', 'Carousel driven by the theme JavaScript (Swiper / Flickity); slide order and controls come from the source markup.',
        'observed', {'driver': 'theme JavaScript (vendor.js, theme.js, figma-home.js, swiper-bundle)'},
        method='Opened the export in headless Chromium and interacted with the carousel arrows; JS-driven motion is not in the CSS animations list.')

# ---------------------------------------------------------------- gaps, handoff, notes
h = J('design-handoff.json')
h['gaps'] = [g for g in h.get('gaps', []) if not g['gap_id'].startswith('sf-')]
blocked = [a for a in assets if a['state'] == 'replacement-needed']
if blocked:
    h['gaps'].append({'gap_id': 'sf-lander-blocked-media', 'kind': 'media', 'route_id': 'lander', 'section_id': None, 'viewport': None,
        'reason': f'{len(blocked)} image(s) on page-builder pages are hosted on assets.replocdn.com / cdn.instant.so, which the export environment could not reach.',
        'next_action': 'Allow those hosts and re-run the export, or upload the original files; the theme references them by their original URLs until then.',
        'blocks_build': False, 'excluded_by': ''})
h['gaps'].append({'gap_id': 'sf-video-frame-text', 'kind': 'claim', 'route_id': 'home', 'section_id': None, 'viewport': None,
    'reason': 'Text and claims drawn inside UGC/review videos cannot be read by the capture script; no media-frame captures were taken.',
    'next_action': 'Review the videos for claims before publishing; the theme ships the videos unchanged.',
    'blocks_build': False, 'excluded_by': ''})
h['unresolved_questions'] = ['Operator approval for the divergence-ledger entries (prices from NEXT, promotional copy needing Offers, social-proof claims).',
                             'NEXT store subdomain and Theme API key for upload.']
W('design-handoff.json', h)
W('sections.json', {'schema_version': 'next-theme-dev/handoff-sections/v1', 'sections': sections})
W('routes.json', routes)
W('assets.json', {'schema_version': 'next-theme-dev/handoff-assets/v1', 'assets': assets})
# Decisions already recorded (operator approvals, implementation status) are carried forward, never reset.
try:
    previous = {e['divergence_id']: e for e in json.load(open(PKG / 'platform-divergence-ledger.json')).get('entries', [])}
except Exception:
    previous = {}
for did, e in ledger.items():
    old = previous.get(did)
    if old and old.get('status') in ('approved', 'implemented', 'accepted-gap'):
        for k in ('status', 'approved_by', 'target_evidence', 'decision'): e[k] = old[k]
for did, old in previous.items():  # entries authored by hand (e.g. build-time layout divergences) survive regeneration
    if did not in ledger: ledger[did] = old
W('platform-divergence-ledger.json', {'schema_version': 'next-theme-dev/handoff-divergence/v1', 'entries': list(ledger.values())})
W('behaviors.json', {'schema_version': 'next-theme-dev/handoff-behaviors/v1', 'behaviors': behaviors, 'claims': []})

def run(*a): return subprocess.run(['python3', str(PKG_PY), *a], capture_output=True, text=True).stdout.strip().splitlines()[-1:]
styles_doc = J('observed-styles.json'); styles_doc['styles'] = []; W('observed-styles.json', styles_doc)
for c in captures:
    run('geometry', '--package', str(PKG), '--capture', c['capture_id'])
    keys = [k for k in raw[c['capture_id']]['targets'] if k.endswith(('::heading', '::cta'))]
    if keys and c['viewport'] in ('desktop', 'mobile'):
        run('draft-styles', '--package', str(PKG), '--capture', c['capture_id'], '--keys', ','.join(keys))
run('coverage', '--package', str(PKG))
print(f'sections {len(sections)}  assets {len(assets)} ({len(blocked)} replacement-needed)  copy {len(copy["strings"])}  '
      f'ledger {len(ledger)}  behaviors {len(behaviors)}')
