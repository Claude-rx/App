"""Apply the 45+ persona layer to a (rebranded) export: copy rules, the offer picker and persona images.

usage: python3 -I apply_persona.py <src_export> <dst_export> <ccf-offers.json> [<images_dir>]

- copies src -> dst (binary files hard-linked, text files rewritten)
- applies tools/persona/ccf_copy.py: PAGE rules on their file, then GLOBAL rules on every HTML page; a rule that
  matches nothing fails the run (rules prefixed RE: are raw regexes)
- inserts the offer picker (1 bottle / 2 bottles + free gifts, and the Automatic Refills box) into the foundation's
  product form, and the "love it or your money back" trust row under its button; packs map to the NEXT variant
  pks in ccf-offers.json (written by setup_ccf_offers.py)
- writes sf-offer.json for the theme build's Cart Drawer settings: the 1 -> 2 bottle upgrade, add-ons and review
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

def money(v):
    f = float(v)
    return '$%d' % f if f == int(f) else '$%.2f' % f

GIFT_ICONS = Path(__file__).resolve().parent / 'assets'

def gift_icons():
    """Gift thumbnails, copied into the export under content-hashed names (NEXT's CDN caches by file name)."""
    out = {}
    for key in ('blender', 'mystery', 'shipping'):
        src = GIFT_ICONS / f'offer-gift-{key}.jpg'
        name = f"offer-gift-{key}-{hashlib.md5(src.read_bytes()).hexdigest()[:6]}.jpg"
        shutil.copy2(src, DST / 'assets' / 'img' / name)
        out[key] = '../assets/img/' + name
    return out

def picker():
    """The offer, as on the old store: 1 bottle or 2 bottles + free gifts, each a "temporary deal" off the compare-at
    price, and an Automatic Refills box (unticked by default) that drops both to their refill price.

    Prices come from ccf_copy.PACKS, the same table setup_ccf_offers.py writes to NEXT. The box is
    data-sf-offer-picker, so the theme build keeps these prices as written instead of binding them to the product."""
    packs, refill, icons = ccf_copy.PACKS, ccf_copy.REFILL, gift_icons()
    variants = OFFERS['foundation']['variants']
    table = {p['key']: {'pk': variants[p['key']], 'price': float(p['price']), 'refill': float(p['refill']),
                        'compare': float(p['compare'])} for p in packs}
    first = packs[0]
    pct = round((float(first['compare']) - float(first['refill'])) / float(first['compare']) * 100)
    cards = []
    for i, p in enumerate(packs):
        gifts = ''.join(
            f'<li><img src="{icons[k]}" alt="" width="40" height="40" loading="lazy" decoding="async">'
            f'<span>+ {html.escape(label)}</span>' + (f'<s>{money(value)}</s>' if value else '') + '<b>FREE</b></li>'
            for k, label, value in p['gifts'])
        cards.append(
            f'<label class="sfo-card{" sfo-card--gifts" if gifts else ""}">'
            + (f'<em class="sfo-tab">{html.escape(p["badge"])}</em>' if p.get('badge') else '')
            + f'<span class="sfo-row"><input type="radio" name="sf_pack" value="{p["key"]}"{" checked" if i == 0 else ""}>'
            f'<span class="sfo-main"><span class="sfo-name">{html.escape(p["name"])}'
            f'<span class="sfo-save" data-sfo-save>SAVE {money(float(p["compare"]) - float(p["price"]))}</span></span>'
            f'<small>{html.escape(p["note"])}</small></span>'
            f'<span class="sfo-price"><b data-sfo-now>{money(p["price"])}</b><s>{money(p["compare"])}</s></span></span>'
            + (f'<ul class="sfo-gifts">{gifts}</ul>' if gifts else '') + '</label>')
    perks = ' <i>|</i> '.join(html.escape(x) for x in refill['perks'])
    return f"""<div class="sfo" id="apf-buy" data-sf-offer-picker data-packs='{json.dumps(table)}'>
<style>
.sfo{{margin:6px 0 16px;display:grid;gap:12px;font-family:inherit;color:#151515}}
.sfo fieldset{{border:0;margin:0;padding:0;display:grid;gap:12px;min-width:0}}
.sfo legend{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}
.sfo-card{{position:relative;display:block;cursor:pointer;border:1px solid #e1e1e1;border-radius:12px;background:#f6f6f6;padding:16px 18px;transition:border-color .15s,background .15s}}
.sfo-card:has(input:checked){{border:2px solid #151515;background:#fff;padding:15px 17px}}
.sfo-row{{display:flex;align-items:center;gap:14px}}
.sfo-card input{{appearance:none;-webkit-appearance:none;flex:none;width:22px;height:22px;margin:0;border:1.5px solid #9a9a9a;border-radius:50%;background:#fff;display:grid;place-content:center}}
.sfo-card input:checked{{border-color:#151515}}
.sfo-card input:checked:before{{content:"";width:12px;height:12px;border-radius:50%;background:#151515}}
.sfo-card input:focus-visible,.sfo-refill input:focus-visible{{outline:2px solid #151515;outline-offset:2px}}
.sfo-main{{flex:1;min-width:0}}
.sfo-name{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;font-size:19px;font-weight:600;line-height:1.2}}
.sfo-save{{font-size:12px;font-weight:500;letter-spacing:.04em;background:#151515;color:#fff;border-radius:999px;padding:3px 10px;white-space:nowrap}}
.sfo-main small{{display:block;font-size:14px;color:#6a6a6a;margin-top:3px}}
.sfo-price{{text-align:right;line-height:1.15;white-space:nowrap}}
.sfo-price b{{display:block;font-size:21px;font-weight:600}}
.sfo-price s,.sfo-gifts s{{font-size:14px;color:#7a7a7a}}
.sfo-tab{{position:absolute;top:-13px;right:16px;background:#151515;color:#fff;font-style:normal;font-size:13px;font-weight:600;padding:4px 12px;border-radius:6px;line-height:1.3}}
.sfo-gifts{{list-style:none!important;margin:14px 0 0!important;padding:12px 0 0!important;border-top:1px solid #e6e6e6;display:grid;gap:8px}}
.sfo-gifts li{{list-style:none;margin:0;padding:0;display:flex;align-items:center;gap:12px;font-size:14px;font-weight:600}}
.sfo-gifts li:before{{content:none!important}}
.sfo-gifts img{{width:40px;height:40px;border-radius:8px;object-fit:cover;flex:none;background:#fff}}
.sfo-gifts span{{flex:1}}
.sfo-gifts s{{font-weight:400}}
.sfo-gifts b{{font-size:12px;letter-spacing:.06em;color:#1f7a3f;min-width:36px;text-align:right}}
.sfo-refill{{display:flex;align-items:center;gap:16px;cursor:pointer;border:2px dashed #151515;border-radius:12px;padding:14px 18px;background:#fff}}
.sfo-refill input{{appearance:none;-webkit-appearance:none;flex:none;width:26px;height:26px;margin:0;border:1.5px solid #151515;border-radius:5px;background:#fff;display:grid;place-content:center}}
.sfo-refill input:checked{{background:#151515}}
.sfo-refill input:checked:before{{content:"";width:12px;height:7px;border:solid #fff;border-width:0 0 2.5px 2.5px;transform:translateY(-2px) rotate(-45deg)}}
.sfo-refill strong{{display:block;font-size:16px;line-height:1.3}}
.sfo-refill small{{display:block;font-size:13px;color:#5a5a5a;margin-top:3px;line-height:1.35}}
.sfo-refill i{{font-style:normal;color:#b5b5b5;margin:0 4px}}
@media (max-width:420px){{.sfo-card{{padding:14px}}.sfo-card:has(input:checked){{padding:13px}}.sfo-name{{font-size:17px}}.sfo-price b{{font-size:19px}}.sfo-refill{{padding:12px 14px}}}}
</style>
<fieldset><legend>Choose your pack</legend>{''.join(cards)}</fieldset>
<label class="sfo-refill"><input type="checkbox" name="sf_purchase" value="subscribe" data-interval="{refill['interval']}" data-interval-count="{refill['every']}">
<span><strong>Save <span data-sfo-pct>{pct}%</span> with {html.escape(refill['name'])}</strong><small>{perks}</small></span></label>
<script>
(function () {{
  var root = document.currentScript.parentNode;
  var form = root.closest('form');
  var packs = JSON.parse(root.getAttribute('data-packs'));
  var box = root.querySelector('input[name=sf_purchase]');
  function money(v) {{ return '$' + (v % 1 ? v.toFixed(2) : String(v)); }}
  // the price under the product title (the nearest one above the picker)
  var scope = root, head = null;
  while (scope && !head) {{ scope = scope.parentElement; head = scope && scope.querySelector('.product__price-and-badge'); }}
  var now = head && head.querySelector('.product__price--regular');
  var was = head && head.querySelector('.product__price--compare');
  var unit = now && / USD\\s*$/.test(now.textContent) ? ' USD' : '';
  function sync() {{
    var key = (root.querySelector('input[name=sf_pack]:checked') || {{}}).value || '1';
    var sub = box.checked, pick = packs[key];
    var id = form && form.querySelector('input[name=id]');
    if (id) id.value = pick.pk;
    Array.prototype.forEach.call(root.querySelectorAll('input[name=sf_pack]'), function (r) {{
      var p = packs[r.value], card = r.closest('.sfo-card'), v = sub ? p.refill : p.price;
      card.querySelector('[data-sfo-now]').textContent = money(v);
      card.querySelector('[data-sfo-save]').textContent = 'SAVE ' + money(p.compare - v);
    }});
    root.querySelector('[data-sfo-pct]').textContent = Math.round((pick.compare - pick.refill) / pick.compare * 100) + '%';
    if (now) now.textContent = money(sub ? pick.refill : pick.price) + unit;
    if (was) was.textContent = money(pick.compare) + unit;
    var terms = document.querySelector('[data-sf-refill-terms]');   // under the button: parsed after this script
    if (terms) {{
      terms.hidden = !sub;
      terms.textContent = terms.getAttribute('data-sf-refill-terms').replace(/\\{{amount\\}}/g, money(pick.refill));
    }}
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
  // the trust block (with the refill terms) comes after the button: sync again once it is parsed
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', sync);
}})();
</script>
</div>"""

def cart_offer():
    """The cart drawer's settings for this offer (read by the theme build into Theme settings > Cart Drawer): the
    1 -> 2 bottle upgrade with its price difference, the add-ons and the review."""
    one, two = ccf_copy.PACKS[0], ccf_copy.PACKS[1]
    variants = OFFERS['foundation']['variants']
    diffs = {float(two['price']) - float(one['price']), float(two['refill']) - float(one['refill'])}
    extras = ['a second bottle'] + ['a free ' + label.replace('FREE ', '') for k, label, value in two['gifts'] if value]
    what = ', '.join(extras[:-1]) + ' and ' + extras[-1]
    text = (f'Just {money(diffs.pop())} more for {what}.' if len(diffs) == 1 else f'Get {what}.')
    cart = ccf_copy.CART
    return {'product': cart['product'], 'addons': cart['addons'],
            'upgrade': {'from': variants[one['key']], 'to': variants[two['key']], 'title': cart['upgrade_title'],
                        'text': text, 'button': cart['upgrade_button']},
            'review': {'text': cart['review_text'], 'name': cart['review_name']}}

def trust_block():
    """Under the add-to-cart button: love it or your money back, free shipping / 30-day guarantee / secure checkout,
    and the refill terms (shown by the picker only while Automatic Refills is ticked)."""
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
    for p, t in texts.items(): p.write_text(t, encoding='utf-8', errors='surrogateescape')
    # the theme build turns this into the Cart Drawer theme settings (upgrade, add-ons, review)
    (DST / 'sf-offer.json').write_text(json.dumps(cart_offer(), indent=1, ensure_ascii=False))
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
