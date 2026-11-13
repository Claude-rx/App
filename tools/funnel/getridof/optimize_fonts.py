#!/usr/bin/env python3
"""Convert the sales page's desktop fonts (TTF/OTF, up to 630 KB each) to WOFF2 and point every @font-face at them.

    python3 tools/funnel/getridof/optimize_fonts.py      # run by build_pdp.mjs after swap_images.py; idempotent

WOFF2 is the same glyphs, Brotli-compressed (about 40-60% smaller); every browser that runs the Campaign Cart SDK reads
it. Needs fonttools + brotli (pip install fonttools brotli). References are rewritten in index.html and pdp/*.css.
"""
import re
from pathlib import Path
from fontTools.ttLib import TTFont

CAMP = Path(__file__).resolve().parents[3] / 'campaigns/getridof/src/mouse-pouches'
PDP = CAMP / 'assets/pdp'


def main():
    saved, names = 0, {}
    for src in sorted(list(PDP.glob('*.ttf')) + list(PDP.glob('*.otf'))):
        dst = src.with_suffix('.woff2')
        if not dst.exists():
            f = TTFont(src); f.flavor = 'woff2'; f.save(dst)
        saved += src.stat().st_size - dst.stat().st_size
        names[src.name] = dst.name
    if not names:
        print('fonts: nothing to convert'); local_first(); return
    pat = re.compile(r'url\((["\']?)([^"\')]*?)(' + '|'.join(map(re.escape, names)) + r')\1\)\s*format\((["\'])(?:truetype|opentype)\4\)')
    for f in [CAMP / 'index.html', *PDP.glob('*.css')]:
        s = f.read_text(encoding='utf-8')
        t = pat.sub(lambda m: f'url({m.group(1)}{m.group(2)}{names[m.group(3)]}{m.group(1)}) format({m.group(4)}woff2{m.group(4)})', s)
        t = re.sub('|'.join(map(re.escape, names)), lambda m: names[m.group(0)], t)   # any reference without format()
        if t != s: f.write_text(t, encoding='utf-8')
    for src in names: (PDP / src).unlink()
    local_first()
    print(f'fonts: {len(names)} TTF/OTF -> WOFF2, {saved // 1024} KB smaller')


# Apple devices ship Helvetica / Helvetica Neue: use the installed face first so iOS + macOS download nothing.
LOCAL = {('helvetica neue', '400'): ["Helvetica Neue", "HelveticaNeue"], ('helvetica neue', '500'): ["HelveticaNeue-Medium"],
         ('helvetica neue', '700'): ["HelveticaNeue-Bold"], ('helvetica', '400'): ["Helvetica"]}
FACE = re.compile(r'@font-face\s*\{[^}]*\}', re.I)


def local_first():
    for f in [CAMP / 'index.html', *PDP.glob('*.css')]:
        s = f.read_text(encoding='utf-8')
        def fix(m):
            b = m.group(0)
            fam = re.search(r"font-family:\s*['\"]?([^;'\"]+)", b, re.I); wt = re.search(r'font-weight:\s*(\d+)', b, re.I)
            key = (fam.group(1).strip().lower() if fam else '', wt.group(1) if wt else '400')
            if key not in LOCAL or 'local(' in b: return b
            loc = ', '.join(f'local("{n}")' for n in LOCAL[key])
            return re.sub(r'src:\s*', 'src: ' + loc + ', ', b, count=1)
        t = FACE.sub(fix, s)
        if t != s: f.write_text(t, encoding='utf-8')


if __name__ == '__main__':
    main()
