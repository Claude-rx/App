"""Speed pass over the generated SKINOFAB theme. Run after build_theme.py, on its output; deterministic.

usage: python3 -I optimize_theme.py <theme_dir>

Every step keeps what a visitor sees the same and only changes what the browser has to fetch, parse and run:

1. Unused CSS. Design stylesheets (assets/sf/css) and the design's inline <style> blocks lose every selector that
   names a class or id found nowhere in the theme: templates, partials, layouts, every script, the product JSON.
   Classes a script builds from a prefix ("is-" + state) are protected by the prefixes found in script strings;
   selectors inside :not()/:is()/:where()/:has() never count against a rule. Unused @keyframes go too.
2. Fonts. Font faces whose family no remaining rule uses are dropped, and of identical faces only the last (the
   one CSS uses) is kept. Text faces swap instead of blocking. Google Fonts CSS that the landing pages @import from
   fonts.gstatic.com is replaced by self-hosted Latin faces (tools/theme-build/static/fonts).
3. One stylesheet. The design stylesheets every page links become one content-hashed bundle, linked where the
   last of them was. Stylesheets that move past inline <style> blocks to get there are checked to share no
   selector with them (otherwise they stay where they are), so the cascade is unchanged.
4. Swiper off the critical path. The 40 KB Swiper library loads with `defer`; inline scripts that build sliders
   while the page parses are rewritten to build them on DOMContentLoaded (defer_inline.mjs, same global names).
5. Responsive images. A srcset of local theme images becomes CDN-resized candidates of its largest source
   (cdn.29next.store resizes on `&width=`; without it the full image is served), sized for the `sizes` the
   design declares, so a 89 px thumbnail stops downloading a 1080 px photo.
6. Heavy backgrounds. An inline background-image over 60 KB (the browser never lazy-loads those) moves to
   data-sf-bg, at most 1080 px wide through the CDN, and the base layout sets it when its element nears the screen.

Writes theme-optimize-report.json next to the theme dir. Fails (exit 1) when an output does not compile with
the platform's Sass compiler or a step's safety check trips.
"""
import hashlib, json, re, shutil, subprocess, sys
from pathlib import Path

THEME = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
REPORT = {'css': {}, 'fonts': {}, 'bundles': {}, 'swiper': {}, 'images': {}, 'errors': []}
DESIGN_HTML = sorted(set(THEME.glob('templates/**/*.html')) | set(THEME.glob('partials/**/*.html')) | {THEME / 'layouts/base.html'})
SCRIPTS = sorted(THEME.glob('assets/**/*.js')) + sorted(THEME.glob('assets/sf/data/*.json')) + sorted(THEME.glob('assets/sf/js/*.json'))

def read(p): return p.read_text('utf-8', errors='surrogateescape')
def write(p, t): p.write_text(t, 'utf-8', errors='surrogateescape')
def kb(n): return round(n / 1024, 1)

# ---------------------------------------------------------------- DTL protection
# Theme files are Django templates. Real tags/variables are swapped for inert placeholders while CSS/HTML is
# rewritten; `{% templatetag ... %}` (an escaped literal "{%", "{{" or "{#" in the CSS) becomes the literal again so
# the CSS parser sees the braces, and is escaped back on the way out.
TT = {'openblock': '{%', 'openvariable': '{{', 'opencomment': '{#', 'closeblock': '%}', 'closevariable': '}}', 'closecomment': '#}'}
DTL_RE = re.compile(r'\{%(?!\s*templatetag\b).*?%\}|\{\{.*?\}\}|\{#.*?#\}', re.S)
TT_RE = re.compile(r'\{%\s*templatetag\s+(\w+)\s*%\}')
OPENERS = {'{%': '{% templatetag openblock %}', '{{': '{% templatetag openvariable %}', '{#': '{% templatetag opencomment %}'}

def protect(text):
    keep = []
    def put(m): keep.append(m.group(0)); return f'\x00{len(keep) - 1}\x00'
    text = DTL_RE.sub(put, text)
    text = TT_RE.sub(lambda m: TT.get(m.group(1), m.group(0)), text)
    return text, keep

def restore(text, keep):
    text = re.sub(r'\{[%{#]', lambda m: OPENERS[m.group(0)], text)
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], text)

# ---------------------------------------------------------------- CSS parsing (slices of the original text)
def skip_string(s, i):
    q, i = s[i], i + 1
    while i < len(s) and s[i] != q:
        i += 2 if s[i] == '\\' else 1
    return i + 1

def css_nodes(css):
    """Top-level nodes as (prelude, body); body None for statement at-rules (@import ...;). Comments are dropped."""
    out, i, n = [], 0, len(css)
    while i < n:
        while i < n and css[i] in ' \t\r\n\f': i += 1
        if i >= n: break
        if css.startswith('/*', i):
            j = css.find('*/', i + 2); i = n if j < 0 else j + 2; continue
        start, paren = i, 0
        while i < n:
            c = css[i]
            if c in '"\'': i = skip_string(css, i); continue
            if css.startswith('/*', i):
                j = css.find('*/', i + 2); i = n if j < 0 else j + 2; continue
            if c == '(': paren += 1
            elif c == ')': paren = max(0, paren - 1)
            elif paren == 0 and c in '{;}': break
            i += 1
        prelude = re.sub(r'/\*.*?\*/', '', css[start:i], flags=re.S).strip()
        if i >= n:
            if prelude.startswith('@'): out.append((prelude, None))     # "@import url(...)" closing a block, no ';'
            break
        if css[i] == '}':                                   # stray closer
            i += 1; continue
        if css[i] == ';':
            if prelude: out.append((prelude, None))
            i += 1; continue
        depth, j = 1, i + 1
        while j < n and depth:
            c = css[j]
            if c in '"\'': j = skip_string(css, j); continue
            if css.startswith('/*', j):
                k = css.find('*/', j + 2); j = n if k < 0 else k + 2; continue
            if c == '{': depth += 1
            elif c == '}': depth -= 1
            j += 1
        out.append((prelude, css[i + 1:j - 1]))
        i = j
    return out

def split_top(text, sep=','):
    parts, cur, depth, i = [], '', 0, 0
    while i < len(text):
        c = text[i]
        if c in '"\'':
            j = skip_string(text, i); cur += text[i:j]; i = j; continue
        if c in '([': depth += 1
        elif c in ')]': depth -= 1
        if c == sep and depth == 0: parts.append(cur); cur = ''
        else: cur += c
        i += 1
    return parts + [cur]

GROUPING = re.compile(r'@(?:-[a-z]+-)?(?:media|supports|document|layer|container|scope)\b', re.I)
KEYFRAMES = re.compile(r'@(?:-[a-z]+-)?keyframes\s+([^\s{]+)', re.I)

def unescape_ident(tok):
    tok = re.sub(r'\\([0-9a-fA-F]{1,6})\s?', lambda m: chr(int(m.group(1), 16)), tok)
    return re.sub(r'\\(.)', r'\1', tok)

def strip_functional_pseudos(sel):
    """Blank the arguments of :not()/:is()/:where()/:has()/:nth-*() etc.: they never make a rule unusable."""
    out, i = [], 0
    while i < len(sel):
        m = re.match(r':{1,2}[a-zA-Z-]+\(', sel[i:])
        if m:
            out.append(m.group(0)[:-1]); depth, j = 1, i + m.end()
            while j < len(sel) and depth:
                if sel[j] == '(': depth += 1
                elif sel[j] == ')': depth -= 1
                j += 1
            i = j; continue
        out.append(sel[i]); i += 1
    return ''.join(out)

def selector_needs(sel):
    s = strip_functional_pseudos(sel)
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = re.sub(r'"[^"]*"|\'[^\']*\'', '', s)
    s = re.sub(r'\x00\d+\x00', '', s)
    classes = [unescape_ident(t) for t in re.findall(r'\.((?:\\.|[\w-])+)', s)]
    ids = [unescape_ident(t) for t in re.findall(r'#((?:\\.|[\w-])+)', s)]
    return classes + ids

# ---------------------------------------------------------------- 1. what the theme uses
# markup and scripts only: a class named by nothing but a stylesheet's own selector is not in use
corpus = '\n'.join(re.sub(r'(<style\b[^>]*>).*?(</style>)', r'\1\2', read(p), flags=re.S | re.I) for p in DESIGN_HTML) \
    + '\n' + '\n'.join(read(p) for p in SCRIPTS)
TOKENS = set(re.findall(r'[A-Za-z_][\w-]*', corpus)) | set(re.findall(r'[A-Za-z_][\w:/.\[\]%-]*[\w\]%]', corpus))
TOKENS |= {t.lower() for t in TOKENS}
# Class/id prefixes scripts complete at runtime: string literals ending in - or _ ("is-" + x, `swiper-${dir}`).
PREFIXES = set()
for p in SCRIPTS + DESIGN_HTML:
    t = read(p)
    PREFIXES |= set(re.findall(r'["\'`]([A-Za-z][\w-]*[-_])["\'`]?\s*\+', t))
    PREFIXES |= set(re.findall(r'([A-Za-z][\w-]*[-_])\$\{', t))
    PREFIXES |= set(re.findall(r'["\']([A-Za-z][\w-]*(?:--|__|-))["\']', t))
PREFIXES = {p for p in PREFIXES if len(p) >= 3}
# State classes libraries toggle with computed names (Swiper, Flickity, PhotoSwipe, the theme's drawers).
# classes/ids that only exist at runtime: slider and animation libraries, state classes, and the FrontrowMD widget's
# iframes (its own script adds them to <body>)
SAFE_PREFIXES = ('swiper-', 'flickity-', 'pswp', 'is-', 'has-', 'js-', 'no-js', 'aos', 'animate', 'fade', 'slide',
                 'frontrow', 'iframe')

def used(token):
    if token in TOKENS or token.startswith(SAFE_PREFIXES): return True
    return any(token.startswith(p) for p in PREFIXES)

def keep_selector(sel):
    return all(used(t) for t in selector_needs(sel))

def purge(css, stats):
    out = []
    for prelude, body in css_nodes(css):
        if body is None:
            out.append(prelude + ';'); continue
        if prelude.startswith('@'):
            if GROUPING.match(prelude):
                inner = purge(body, stats)
                if inner.strip(): out.append(prelude + '{' + inner + '}')
            else:
                out.append(prelude + '{' + body + '}')
            continue
        sels = [s.strip() for s in split_top(prelude) if s.strip()]
        kept = [s for s in sels if keep_selector(s)]
        stats['selectors'] = stats.get('selectors', 0) + len(sels)
        stats['dropped'] = stats.get('dropped', 0) + len(sels) - len(kept)
        if kept: out.append(','.join(kept) + '{' + body.strip() + '}')
    return ''.join(out)

def animation_names(css):
    names = set()
    for m in re.finditer(r'animation(?:-name)?\s*:\s*([^;}]+)', css, re.I):
        names |= set(re.findall(r'[A-Za-z_][\w-]*', m.group(1)))
    return names

def drop_keyframes(css, names):
    out = []
    for prelude, body in css_nodes(css):
        if body is None: out.append(prelude + ';'); continue
        k = KEYFRAMES.match(prelude)
        if k and k.group(1).strip('"\'') not in names and k.group(1) not in TOKENS: continue
        if GROUPING.match(prelude):
            inner = drop_keyframes(body, names)
            if inner.strip(): out.append(prelude + '{' + inner + '}')
            continue
        out.append(prelude + '{' + body + '}')
    return ''.join(out)

# ---------------------------------------------------------------- 1a. design stylesheets
CSS_DIR = THEME / 'assets/sf/css'
PURGED = {}
for f in sorted(CSS_DIR.glob('*.css')):
    src = read(f); st = {}
    PURGED[f.name] = purge(src, st)
    REPORT['css'][f.name] = {'before_kb': kb(len(src)), 'after_kb': kb(len(PURGED[f.name])), **st}

# ---------------------------------------------------------------- 1b. inline <style> blocks in design markup
STYLE_RE = re.compile(r'(<style\b[^>]*>)(.*?)(</style>)', re.S | re.I)
INLINE = {'blocks': 0, 'before_kb': 0, 'after_kb': 0, 'skipped': 0}
# files generated from the design (Spark's own templates and partials are left as Spark ships them)
DESIGN_FILES = [p for p in DESIGN_HTML if 'sf_pages' in p.parts or p.name in ('header.html', 'footer.html')
                or ((THEME / 'templates') in p.parents and "{{ 'sf/css/" in read(p))]
def purge_inline(m):
    head, body, tail = m.groups()
    prot, keep = protect(body)
    if restore(prot, keep) != body:                     # DTL round trip not lossless: leave the block alone
        INLINE['skipped'] += 1; return m.group(0)
    new = restore(purge(prot, {}), keep)
    INLINE['blocks'] += 1; INLINE['before_kb'] += len(body); INLINE['after_kb'] += len(new)
    return head + new + tail
for p in DESIGN_FILES:
    t = read(p)
    if '<style' not in t: continue
    n = STYLE_RE.sub(purge_inline, t)
    if n != t: write(p, n)
INLINE['before_kb'], INLINE['after_kb'] = kb(INLINE['before_kb']), kb(INLINE['after_kb'])
REPORT['css']['inline'] = INLINE

# keyframes: keep the ones some remaining rule (file, inline block, style attribute) or script names
ALL_CSS = '\n'.join(PURGED.values()) + '\n'.join(read(p) for p in DESIGN_HTML)
ANIM = animation_names(ALL_CSS)
for name in PURGED: PURGED[name] = drop_keyframes(PURGED[name], ANIM)

# ---------------------------------------------------------------- 2. fonts
FACE_RE = re.compile(r'@font-face\s*\{[^}]*\}', re.I)
def face_key(face):
    g = lambda k: (re.search(k + r'\s*:\s*([^;}]+)', face, re.I) or [None, ''])[1].strip().strip('"\'').lower()
    return (g('font-family'), g('font-weight') or '400', g('font-style') or 'normal', g('font-stretch'), g('unicode-range'))

def families_in_use(text):
    fams = set()
    for m in re.finditer(r'(?:font-family|font|--[\w-]*font[\w-]*)\s*:\s*([^;}]+)', text, re.I):
        for part in split_top(m.group(1)):
            fams.add(part.strip().strip('"\'').lower())
        for q in re.findall(r'["\']([^"\']+)["\']', m.group(1)): fams.add(q.lower())
    return fams

USED_FAMILIES = families_in_use(FACE_RE.sub('', '\n'.join(PURGED.values()) + '\n'.join(read(p) for p in DESIGN_HTML)
                                             + read(THEME / 'assets/main.css') + '\n'.join(read(p) for p in THEME.glob('assets/**/*.js'))))
ICON_FAMILIES = re.compile(r'awesome|icon', re.I)

def prune_faces(text, stats):
    faces = FACE_RE.findall(text)
    last = {}
    for i, f in enumerate(faces): last[face_key(f)] = i
    out, idx = [], [0]
    def rep(m):
        i = idx[0]; idx[0] += 1
        f = m.group(0); fam = face_key(f)[0]
        if fam not in USED_FAMILIES: stats['unused'] = stats.get('unused', 0) + 1; return ''
        if last[face_key(f)] != i: stats['duplicate'] = stats.get('duplicate', 0) + 1; return ''
        if not ICON_FAMILIES.search(fam): f = re.sub(r'font-display\s*:\s*block', 'font-display:swap', f)
        stats['kept'] = stats.get('kept', 0) + 1
        return f
    return FACE_RE.sub(rep, text)

st = {}
asset_styles = THEME / 'partials/sf_asset_styles.html'
t = read(asset_styles)
t = prune_faces(t, st)
# --sfu-* url() variables nothing reads any more
for var in set(re.findall(r'(--sfu-[\w-]+):', t)):
    if not re.search(r'var\(\s*' + re.escape(var) + r'\s*[,)]', ALL_CSS.replace(t, '')):
        t = re.sub(re.escape(var) + r':url\("[^"]*"\);', '', t); st['url_vars_dropped'] = st.get('url_vars_dropped', 0) + 1
t = re.sub(r'\n{2,}', '\n', t)
write(asset_styles, t)
REPORT['fonts']['sf_asset_styles'] = st

# self-hosted Google Fonts for the landing pages' @import url(".../sf/img/css2-*.css")
FONT_STATIC = HERE / 'static' / 'fonts'
def localize_google_css(name):
    css = read(THEME / 'assets/sf/img' / name)
    faces = []
    for m in re.finditer(r'/\*\s*latin\s*\*/\s*(@font-face\s*\{[^}]*\})', css):
        face = m.group(1)
        url = re.search(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', face).group(1)
        local = FONT_STATIC / re.sub(r'[^A-Za-z0-9._-]', '_', url.split('fonts.gstatic.com/s/')[1])
        if not local.exists():
            FONT_STATIC.mkdir(parents=True, exist_ok=True)
            subprocess.run(['curl', '-sSfL', '-o', str(local), url], check=True)
        data = local.read_bytes()
        dest = f"sf/fonts/g-{local.stem[:40]}-{hashlib.md5(data).hexdigest()[:6]}.woff2"
        (THEME / 'assets' / dest).write_bytes(data)
        faces.append(re.sub(r'url\(https://fonts\.gstatic\.com/[^)]+\)', "url(\"{{ '%s'|asset_url }}\")" % dest, face))
    return '\n'.join(faces)
gf = {}
for p in DESIGN_FILES:
    t = read(p)
    n = re.sub(r"""@import url\("\{\{ 'sf/img/(css2-[0-9a-f]+\.css)'\|asset_url \}\}"\);?""",
               lambda m: gf.setdefault(m.group(1), localize_google_css(m.group(1))), t)
    if n != t: write(p, n)
REPORT['fonts']['google_fonts_self_hosted'] = {k: v.count('@font-face') for k, v in gf.items()}

# ---------------------------------------------------------------- 3. one stylesheet per page head
LINK_RE = re.compile(r"""<link\b[^>]*href="\{\{ 'sf/css/([\w.-]+\.css)'\|asset_url \}\}"[^>]*>""")
def head_regions():
    for p in DESIGN_HTML:
        t = read(p)
        if 'sf_pages' in p.parts and p.name == 'head.html':
            yield p, t, 0, len(t)
        else:
            m = re.search(r'\{% block sf_head %\}(.*?)\{% endblock sf_head %\}', t, re.S)
            if m and LINK_RE.search(m.group(1)): yield p, t, m.start(1), m.end(1)

heads = list(head_regions())
from collections import Counter
seen = Counter(tuple(LINK_RE.findall(t[a:b])) for _, t, a, b in heads)
common = Counter(f for seq, n in seen.items() for f in seq for _ in range(n))
SHARED = []
for f in (seen.most_common(1)[0][0] if seen else ()):
    if common[f] < 0.6 * len(heads): continue
    ok = True
    for seq in seen:
        if f in seq and SHARED and SHARED[-1] in seq:
            a, b = seq.index(SHARED[-1]), seq.index(f)
            if b < a or any(x not in SHARED for x in seq[a + 1:b]): ok = False; break
    if ok: SHARED.append(f)

def rule_subjects(css):
    """(subject, property) pairs of a stylesheet for the cascade-safety check. The subject is each class, id or tag
    of a selector's last compound; media and specificity are ignored, so the check errs on the side of 'clash'."""
    pairs = set()
    def walk(c):
        for prelude, body in css_nodes(c):
            if body is None: continue
            if prelude.startswith('@'):
                if GROUPING.match(prelude): walk(body)
                continue
            props = {d.split(':', 1)[0].strip().lower() for d in split_top(body, ';') if ':' in d}
            for s in split_top(prelude):
                last = re.split(r'[\s>+~]+', strip_functional_pseudos(s).strip())[-1]
                subj = set(re.findall(r'[.#]?-?[A-Za-z_][\w-]*', re.sub(r'::?[\w-]+|\[[^\]]*\]', '', last))) or {'*'}
                for prop in props:
                    for x in subj: pairs.add((x, prop))
    walk(css)
    return pairs

bundles = {}
for p, t, a, b in heads:
    region = t[a:b]
    links = list(LINK_RE.finditer(region))
    names = [m.group(1) for m in links]
    members = [n for n in SHARED if n in names]
    if len(members) < 2: continue
    anchor = max(names.index(n) for n in members)
    if any(n not in members for n in names[:anchor + 1]):
        # a page-specific stylesheet sits inside the shared run: bundle only what comes after it
        members = [n for n in members if names.index(n) > max(i for i, n in enumerate(names[:anchor + 1]) if n not in SHARED)]
    # cascade check: a member that moves forward to the anchor must not share a (selector, property) with any
    # inline <style> it jumps over
    anchor_pos = links[names.index(members[-1])].start()
    safe = []
    for n in members:
        pos = links[names.index(n)].end()
        between = ''.join(protect(m.group(2))[0] for m in STYLE_RE.finditer(region[pos:anchor_pos]))
        between += ''.join(PURGED[x.group(1)] for x in LINK_RE.finditer(region[pos:anchor_pos]) if x.group(1) not in members)
        clash = rule_subjects(PURGED[n]) & rule_subjects(between) if between.strip() else set()
        if clash:
            REPORT['errors'].append(f'{p.relative_to(THEME)}: {n} kept separate, shares {sorted(clash)[:3]} with inline styles')
        else: safe.append(n)
    if len(safe) < 2: continue
    text = '\n'.join(f'/* {n} */\n' + PURGED[n] for n in safe) + '\n'
    if re.search(r'@import\b', text): REPORT['errors'].append(f'{p.relative_to(THEME)}: @import in bundle members, skipped'); continue
    name = f"sfb-{hashlib.md5(text.encode()).hexdigest()[:8]}.css"
    bundles.setdefault(name, (text, safe))
    keep_link = links[names.index(safe[-1])]
    new_region = region[:keep_link.start()] + '<link href="{{ \'sf/css/%s\'|asset_url }}" rel="stylesheet">' % name + region[keep_link.end():]
    for n in safe[:-1]:
        new_region = LINK_RE.sub(lambda m: '' if m.group(1) == n else m.group(0), new_region, count=0)
    write(p, t[:a] + new_region + t[b:])
for name, (text, members) in bundles.items():
    write(CSS_DIR / name, text)
    REPORT['bundles'][name] = {'kb': kb(len(text)), 'members': members}
for name, text in PURGED.items():                       # purged copies for what pages still link one by one
    write(CSS_DIR / name, text if text.strip() else '/* no rules in use */\n')

# ---------------------------------------------------------------- 4. Swiper with defer
SWIPER_TAG = re.compile(r"""<script(?![^>]*\bdefer)([^>]*src="\{\{ 'sf/js/swiper-bundle-min-[0-9a-f]+\.js'\|asset_url \}\}"[^>]*)>""")
INLINE_JS = re.compile(r'(<script(?![^>]*\bsrc=)(?![^>]*type="(?:application/(?:ld\+)?json|text/template|module)")[^>]*>)(.*?)(</script>)', re.S)
jobs = []
for p in DESIGN_HTML:
    t = read(p)
    for m in INLINE_JS.finditer(t):
        if re.search(r'\bSwiper\b', m.group(2)) and not DTL_RE.search(m.group(2)): jobs.append((p, m.group(2)))
node_ok = False
if jobs:
    try:
        res = subprocess.run(['node', str(HERE / 'defer_inline.mjs')], input=json.dumps([j[1] for j in jobs]),
                             capture_output=True, text=True, check=True)
        results = json.loads(res.stdout); node_ok = True
    except Exception as e:
        REPORT['errors'].append(f'swiper: defer_inline.mjs unavailable ({e}); Swiper stays render-blocking')
if node_ok:
    # where a global can be read at parse time: other inline scripts and inline event handlers
    others = '\n'.join(m.group(2) for p in DESIGN_HTML for m in INLINE_JS.finditer(read(p))) + '\n'.join(
        h for p in DESIGN_HTML for h in re.findall(r'\son\w+="([^"]*)"', read(p)))
    late = {g for r in results for g in r['globals']}
    # a late-assigned global must not be read anywhere but its own declaration
    clash = sorted(g for g in late if len(re.findall(r'(?<![\w$.])' + re.escape(g) + r'(?![\w$])', others)) > sum(
        len(re.findall(r'(?<![\w$.])' + re.escape(g) + r'(?![\w$])', b)) for _, b in jobs))
    unparsed = sum(1 for r in results if r['code'] is None)
    if clash or unparsed:
        REPORT['errors'].append(f'swiper: left render-blocking (globals read elsewhere: {clash[:5]}, unparsed scripts: {unparsed})')
    else:
        rewrite = {}
        for (p, body), r in zip(jobs, results): rewrite.setdefault(p, []).append((body, r['code']))
        for p, pairs in rewrite.items():
            t = read(p)
            for body, code in pairs: t = t.replace('>' + body + '</script>', '>' + code + '</script>', 1)
            write(p, t)
        tags = 0
        for p in DESIGN_HTML:
            t = read(p); n, k = SWIPER_TAG.subn(r'<script defer\1>', t)
            if k: write(p, n); tags += k
        REPORT['swiper'] = {'inline_scripts_deferred': len(jobs), 'script_tags_deferred': tags}

# ---------------------------------------------------------------- 5. responsive images through the CDN
try:
    from PIL import Image
except ImportError:
    Image = None
IMG_TAG = re.compile(r'<(img|source)\b[^>]*\ssrcset="([^"]*)"[^>]*>')
CAND = re.compile(r"\{\{ '(sf/img/[^']+\.(?:jpe?g|png|webp))'\|asset_url \}\}\s+(\d+)w")
# up to 4K: the home hero is drawn 150vw (desktop) and 349vw (phone) wide, so a retina screen asks for 2-4K
STEPS = [360, 540, 720, 1080, 1440, 2160, 2880, 3600]
widths = {}
def intrinsic(rel):
    if rel not in widths:
        try:
            with Image.open(THEME / 'assets' / rel) as im: widths[rel] = im.size[0]
        except Exception: widths[rel] = 0
    return widths[rel]
img_stats = {'elements': 0, 'skipped': 0}
def responsive(m):
    tag, srcset = m.group(0), m.group(2)
    if '{%' in tag: img_stats['skipped'] += 1; return tag
    cands = CAND.findall(srcset)
    if not cands or len(cands) != len([c for c in srcset.split(',') if c.strip()]):
        img_stats['skipped'] += 1; return tag
    src, top = max(cands, key=lambda c: int(c[1]))
    top = min(int(top), intrinsic(src))          # a replaced photo can be smaller than the width its descriptor claims
    if top < 100: img_stats['skipped'] += 1; return tag
    sizes = re.search(r'\ssizes="([^"]*)"', tag)
    px = re.fullmatch(r'\s*(\d+)px\s*', sizes.group(1)) if sizes else None
    want = sorted({min(top, int(px.group(1)) * k) for k in (1, 2, 3)} if px else {w for w in STEPS if w < top})
    want = [w for w in want if w < top * 0.9] + [top]
    new = ', '.join(("{{ sf_img }}&amp;width=%d %dw" % (w, w)) if w != top else ("{{ sf_img }} %dw" % w) for w in want)
    img_stats['elements'] += 1
    return "{%% with sf_img='%s'|asset_url %%}" % src + tag.replace(srcset, new, 1) + '{% endwith %}'
if Image:
    for p in DESIGN_FILES:
        t = read(p)
        n = IMG_TAG.sub(responsive, t)
        if n != t: write(p, n)
REPORT['images'] = img_stats

# ---------------------------------------------------------------- 6. heavy background images wait for their section
# An inline background-image downloads with the page wherever it sits (the browser does not lazy-load CSS images):
# the 1,500-px "why" photo at the bottom of every product page cost 183 KB before anything below the buy box was
# seen. A background whose file is over BG_LAZY_KB moves to data-sf-bg, at most BG_MAX_W wide through the CDN, and
# a small script in the base layout sets it when the element comes within ~two screens of the viewport.
BG = re.compile(r"""background-image:\s*url\((["']?)(\{\{ '(sf/img/[^']+\.(?:jpe?g|png|webp))'\|asset_url \}\})\1\);?\s*""")
BG_LAZY_KB, BG_MAX_W = 60, 1080
BG_SCRIPT = ('<script>/* sf lazy backgrounds */(function(){var els=[].slice.call(document.querySelectorAll("[data-sf-bg]"));'
             'if(!els.length)return;function show(e){e.style.backgroundImage=\'url("\'+e.getAttribute("data-sf-bg")+\'")\';'
             'e.removeAttribute("data-sf-bg")}if(!("IntersectionObserver"in window)){els.forEach(show);return}'
             'var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){io.unobserve(x.target);'
             'show(x.target)}})},{rootMargin:"1600px 2400px"});els.forEach(function(e){io.observe(e)})})();</script>\n')
bg_stats = {'lazy': 0, 'kb_deferred': 0}
def lazy_backgrounds(t):
    out, last = [], 0
    for m in BG.finditer(t):
        f = THEME / 'assets' / m.group(3)
        if not f.exists() or f.stat().st_size < BG_LAZY_KB * 1024 or m.start() < last: continue
        start = t.rfind('<', 0, m.start())
        tag = re.match(r'<([a-zA-Z][\w-]*)', t[start:])
        if not tag or 'data-sf-bg' in t[start:m.start()]: continue
        url = m.group(2) + (f'&amp;width={BG_MAX_W}' if intrinsic(m.group(3)) > BG_MAX_W else '')
        at = start + tag.end()
        out += [t[last:at], f' data-sf-bg="{url}"', t[at:m.start()]]; last = m.end()
        bg_stats['lazy'] += 1; bg_stats['kb_deferred'] += round(f.stat().st_size / 1024)
    return ''.join(out) + t[last:] if out else t
if Image:
    for p in DESIGN_FILES:
        t = read(p)
        n = lazy_backgrounds(t)
        if n != t: write(p, n)
    base = THEME / 'layouts' / 'base.html'
    b = read(base)
    if bg_stats['lazy'] and '/* sf lazy backgrounds */' not in b:
        if '\n</body>' not in b: REPORT['errors'].append('lazy backgrounds: no </body> in layouts/base.html')
        else: write(base, b.replace('\n</body>', '\n' + BG_SCRIPT + '</body>', 1))
REPORT['backgrounds'] = bg_stats

# ---------------------------------------------------------------- gates + report
try:
    import sass
    for f in [CSS_DIR / n for n in list(bundles) + list(PURGED)]:
        try: sass.compile(string=read(f))
        except Exception as e: REPORT['errors'].append(f'sass: {f.name}: {str(e).splitlines()[0][:160]}')
except ImportError:
    REPORT['errors'].append('libsass not installed: CSS gate skipped')
for p in DESIGN_HTML:
    for n, line in enumerate(read(p).splitlines(), 1):
        if re.search(r'\{#(?![^\n]*#\})', line): REPORT['errors'].append(f'{p.relative_to(THEME)}:{n}: multi-line {{# #}} comment')
(THEME.parent / 'theme-optimize-report.json').write_text(json.dumps(REPORT, indent=1))
tot_b = sum(v['before_kb'] for k, v in REPORT['css'].items() if k != 'inline')
tot_a = sum(v['after_kb'] for k, v in REPORT['css'].items() if k != 'inline')
print(f"css files {tot_b:.0f} KB -> {tot_a:.0f} KB; inline styles {INLINE['before_kb']:.0f} KB -> {INLINE['after_kb']:.0f} KB in {INLINE['blocks']} blocks; "
      f"bundles {len(bundles)}; fonts {REPORT['fonts']['sf_asset_styles']}; swiper {REPORT['swiper'] or 'unchanged'}; images {img_stats}; backgrounds {bg_stats}")
for e in REPORT['errors']: print('  !', e)
sys.exit(1 if any(e.startswith('sass:') or 'comment' in e for e in REPORT['errors']) else 0)
