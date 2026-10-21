"""Apply the 45+ persona layer to a (rebranded) export: copy rules, the offer picker and persona images.

usage: python3 -I apply_persona.py <src_export> <dst_export> <ccf-offers.json> [<images_dir>]

- copies src -> dst (binary files hard-linked, text files rewritten)
- applies tools/persona/ccf_copy.py: PAGE rules on their file, then GLOBAL rules on every HTML page; a rule that
  matches nothing fails the run (rules prefixed RE: are raw regexes)
- inserts the base picker and the one plan (month-to-month refill, subscription only) into the foundation's
  product form, and the "love it or your money back" trust row under its button; base radios map to the NEXT
  variant pks in ccf-offers.json (written by setup_ccf_offers.py)
- writes sf-subscription.json (ccf_copy.SUBSCRIPTION) for the theme build's Subscription Offer settings
- <images_dir>/<target file name> replaces that export image (persona images made by tools/persona/images.py)
  under a new content-hashed name, with every reference rewritten (NEXT's CDN caches by file name)
"""
import hashlib, html, json, os, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apf_copy, ccf_copy

SRC, DST, OFFERS = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), json.load(open(sys.argv[3]))
IMAGES = Path(sys.argv[4]).resolve() if len(sys.argv) > 4 else None
TEXT = {'.html', '.css', '.js', '.json', '.md', '.txt', '.xml', '.svg'}

def loose(text):
    out = []
    for ch in text:
        if ch.isspace(): out.append(r'\s+')
        elif ch in "'’": out.append(r"(?:'|’|&#39;|&#x27;|&rsquo;)")
        elif ch == '—': out.append(r'(?:—|&mdash;|&#8212;)')
        elif ch == '–': out.append(r'(?:–|&ndash;|&#8211;)')
        elif ch == '&': out.append(r'(?:&|&amp;)')
        else: out.append(re.escape(ch))
    return re.sub(r'(?:\\s\+)+', r'\\s+', ''.join(out))

def compile_rule(old, new):
    if old.startswith('RE:'):                     # raw regex rule: pattern and replacement used as written
        return re.compile(old[3:]), new
    if old.startswith('>') and old.endswith('<'):
        return re.compile(r'>\s*' + loose(old[1:-1]) + r'\s*<'), '>' + html.escape(new[1:-1], quote=False) + '<'
    return re.compile(loose(old)), html.escape(new, quote=False)

def picker():
    """Base choice + the one plan (a month-to-month refill, pre-selected: the product is sold by subscription only)."""
    b, sub = ccf_copy.BASES, ccf_copy.SUBSCRIPTION
    variants = OFFERS['foundation']['variants']
    table = {code: variants.get(name) for code, name, _ in b}
    bases = ''.join(
        f'<label class="sfp-base"><input type="radio" name="sf_base" value="{code}"{" checked" if i == 0 else ""}>'
        f'<span><strong>{html.escape(name)}</strong><small>{html.escape(desc)}</small></span></label>'
        for i, (code, name, desc) in enumerate(b))
    return f'''<div class="sfp" id="apf-buy" data-sf-offer-picker data-pks='{json.dumps(table)}'>
<style>
.sfp{{margin:4px 0 14px;display:grid;gap:14px;font-family:inherit}}
.sfp-h{{font-size:13px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin:0 0 6px;display:flex;justify-content:space-between;align-items:baseline}}
.sfp-h a{{font-size:12px;font-weight:500;text-transform:none;letter-spacing:0;color:#000;text-decoration:underline}}
.sfp-bases{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.sfp label{{cursor:pointer;display:flex;gap:10px;align-items:flex-start;border:1px solid #d9d9d9;border-radius:10px;padding:10px 12px;background:#fff;position:relative}}
.sfp input[type=radio]{{accent-color:#000;margin-top:3px;flex:none}}
.sfp label:has(input:checked){{border-color:#000;box-shadow:0 0 0 1px #000}}
.sfp strong{{display:block;font-size:14px}}
.sfp small{{display:block;font-size:12px;color:#555;line-height:1.35;margin-top:2px}}
.sfp-plan{{padding:14px 14px 12px !important}}
.sfp-offer__main{{flex:1}}
.sfp-offer__price{{font-weight:600;font-size:18px;white-space:nowrap;line-height:1.2}}
.sfp-offer__price small{{display:inline;font-size:12px;font-weight:500;color:#555;margin:0}}
.sfp-badge{{position:absolute;top:-9px;right:12px;background:#000;color:#fff;font-style:normal;font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:20px}}
</style>
<div><p class="sfp-h">1. Choose your base <a href="/ccf-quiz/">Not sure? 30-second quiz</a></p><div class="sfp-bases">{bases}</div></div>
<div><p class="sfp-h">2. Your plan</p>
<label class="sfp-plan"><input type="radio" name="sf_purchase" value="subscribe" data-interval="{sub['interval']}" data-interval-count="{sub['every']}" checked><span class="sfp-offer__main"><strong>Monthly refill</strong><small>1 bottle (30 mL) in your base, every month. Switch base, skip a month or cancel any time.</small></span><span class="sfp-offer__price">{sub['amount']}<small>/mo</small></span><em class="sfp-badge">Month to month</em></label>
</div>
<script>
(function () {{
  var root = document.currentScript.parentNode;
  var form = root.closest('form');
  var table = JSON.parse(root.getAttribute('data-pks'));
  function sync() {{
    var base = (root.querySelector('input[name=sf_base]:checked') || {{}}).value || 'lm';
    var id = form && form.querySelector('input[name=id]');
    if (id && table[base]) id.value = table[base];
  }}
  root.addEventListener('change', sync);
  // deep links from the page sections (#apf-buy) scroll here
  function fromHash() {{
    if (!/^#apf-buy(?:-[a-z]+)?$/.test(window.location.hash || '')) return;
    root.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}
  window.addEventListener('hashchange', fromHash);
  document.addEventListener('click', function (e) {{
    var a = e.target.closest && e.target.closest('a[href*="#apf-buy"]');
    if (!a || a.pathname.replace(/\\/$/, '') !== window.location.pathname.replace(/\\/$/, '')) return;
    e.preventDefault(); history.replaceState(null, '', a.hash); fromHash();
  }});
  fromHash();
  sync();
}})();
</script>
</div>'''

def trust_block():
    """Under the add-to-cart button: love it or your money back, the three plan facts and the renewal terms."""
    return f'<div class="product__block sfp-trust"><style>{apf_copy.TRUST_CSS}</style>{apf_copy.trust_html()}</div>'

def balanced_end(t, start, tag):
    depth = 0
    for m in re.finditer(r'<(/?)%s\b[^>]*>' % tag, t[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0: return start + m.end()
    raise ValueError('unbalanced ' + tag)

def main():
    if DST.exists(): shutil.rmtree(DST)
    for d, dirs, files in os.walk(SRC):
        out = DST / Path(d).relative_to(SRC); out.mkdir(parents=True, exist_ok=True)
        for f in files:
            s, t = Path(d) / f, out / f
            if s.suffix.lower() in TEXT: shutil.copy2(s, t)
            else: os.link(s, t)
    hits, missing = {}, []
    # page rules first: they rewrite whole blocks that the global rules would otherwise half-change
    rules = [(f, o, n) for f, rs in ccf_copy.PAGE.items() for o, n in rs] + [(None, o, n) for o, n in ccf_copy.GLOBAL]
    pages = sorted(DST.rglob('*.html'))
    texts = {p: p.read_text(encoding='utf-8', errors='surrogateescape') for p in pages}
    for scope, old, new in rules:
        rx, rep = compile_rule(old, new)
        n = 0
        for p in ([DST / scope] if scope else pages):
            texts[p], k = (rx.subn(rep, texts[p]) if old.startswith('RE:') else rx.subn(lambda m: rep, texts[p])); n += k
        hits[old[:60]] = n
        if not n: missing.append((scope or '*', old[:90]))
    snap = DST / 'products' / 'color-changing-foundation.js'
    data = json.loads(snap.read_text())
    imgs = data.get('images', [])
    ordered = []
    for prefix in getattr(ccf_copy, 'GALLERY', []):
        hit = next((u for u in imgs if Path(u.split('?')[0]).name.startswith(prefix) and u not in ordered), None)
        if hit: ordered.append(hit)
        else: missing.append(('gallery', prefix))
    data['images'] = ordered + [u for u in imgs if u not in ordered]
    snap.write_text(json.dumps(data))
    pdp = DST / 'products' / 'color-changing-foundation.html'
    anchor = '<span data-subscription-watch-price=""></span>'
    if texts[pdp].count(anchor) < 1: missing.append(('picker', anchor))
    texts[pdp] = texts[pdp].replace(anchor, picker() + anchor, 1)
    cta = texts[pdp].find('<div id="CTA_kopstorm">')
    if cta < 0: missing.append(('trust block', 'CTA_kopstorm'))
    else:
        end = balanced_end(texts[pdp], cta, 'div')
        texts[pdp] = texts[pdp][:end] + trust_block() + texts[pdp][end:]
    # the theme build turns this into the "Subscription Offer" theme settings (price text, cadence, product)
    (DST / 'sf-subscription.json').write_text(json.dumps({'handle': 'color-changing-foundation', **ccf_copy.SUBSCRIPTION}, indent=1))
    for p, t in texts.items(): p.write_text(t, encoding='utf-8', errors='surrogateescape')
    # Replaced images get a new, content-hashed file name and every reference is rewritten: NEXT's CDN keeps
    # serving a cached copy for a re-uploaded file name, so a changed image must never reuse its old name.
    replaced, renames = 0, {}
    if IMAGES and IMAGES.exists():
        for img in sorted(IMAGES.iterdir()):
            target = DST / 'assets' / 'img' / img.name
            if not target.exists(): missing.append(('image target', img.name)); continue
            digest = hashlib.md5(img.read_bytes()).hexdigest()[:6]
            stem, ext = os.path.splitext(img.name)
            new = (re.sub(r'-[0-9a-f]{6}$', '', stem) + f'-p{digest}{ext}')
            shutil.copy2(img, target.with_name(new)); renames[img.name] = new; replaced += 1
    if renames:
        rx = re.compile('|'.join(re.escape(k) for k in sorted(renames, key=len, reverse=True)))
        for p in DST.rglob('*'):
            if p.is_file() and p.suffix.lower() in TEXT:
                t = p.read_text(encoding='utf-8', errors='surrogateescape')
                n = rx.sub(lambda m: renames[m.group(0)], t)
                if n != t: p.write_text(n, encoding='utf-8', errors='surrogateescape')
    print(json.dumps({'rules': len(rules), 'replacements': sum(hits.values()), 'images': replaced, 'missing': missing}, ensure_ascii=False, indent=1))
    if missing: sys.exit(1)

main()
