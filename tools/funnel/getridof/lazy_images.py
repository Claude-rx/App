#!/usr/bin/env python3
"""Lazy-load every sales-page image below the buy box (run by build_pdp.mjs; idempotent).

Everything up to the end of the bundle selector (<kaching-bundles-block>: header, hero gallery, buy box) stays eager,
so the first screen and the LCP image are untouched. Every <img> after it gets loading="lazy" decoding="async", so
a phone downloads the 75 below-the-fold images only as the shopper scrolls to them.
"""
import re
from pathlib import Path

# GemPages entrance-animated blocks never report as intersecting, so native lazy-load never fires there: keep eager.
EAGER = ('Gemini_Generated_Image_ma08i2ma08i2ma08', 'Group_1484581864', 'Group_1484581865', 'Group_1484581866')
MARK = 'gro-lazy-fallback'
# Carousels (transformed tracks) can keep a lazy <img> from ever counting as visible: as its ROW nears the viewport,
# switch it to eager. Vertical position only, so horizontally parked slides load with their row.
FALLBACK = """<script id="gro-lazy-fallback">(function(){var t=0;function go(){t=0;var h=innerHeight,l=document.querySelectorAll('img[loading="lazy"]');for(var i=0;i<l.length;i++){var r=l[i].getBoundingClientRect();if(r.top<h*1.25&&r.bottom>-h)l[i].loading='eager';}}function q(){if(!t)t=requestAnimationFrame(go);}addEventListener('scroll',q,{passive:true});addEventListener('resize',q);addEventListener('load',q);})();</script>
"""
PAGE = Path(__file__).resolve().parents[3] / 'campaigns/getridof/src/mouse-pouches/index.html'


def main():
    s = PAGE.read_text(encoding='utf-8')
    cut = s.find('</kaching-bundles-block>')
    assert cut > 0, 'buy box not found'
    head, tail = s[:cut], s[cut:]
    n = [0]
    def lazy(m):
        t = m.group(0)
        if any(e in t for e in EAGER):
            return re.sub(r' loading="lazy" decoding="async"', '', t)
        if re.search(r'\sloading=', t) or 'fetchpriority="high"' in t: return t
        n[0] += 1
        return t[:4] + ' loading="lazy" decoding="async"' + t[4:]
    tail = re.sub(r'<img\b[^>]*>', lazy, tail)
    # hero gallery: slides 2-7 (and their thumbnails' full-size twins) are hidden until swiped
    # (the page builder marks every slide fetchpriority="high"; only slide 1 is on screen)
    head = re.sub(r'<img\b(?![^>]*\sloading=)(?=[^>]*pdp/image[2-9]-)[^>]*>',
                  lambda m: lazy(re.match(r'.*', m.group(0).replace('fetchpriority="high"', 'fetchpriority="low"'))), head)
    out = head + tail
    if MARK not in out:
        assert out.count('</body>') == 1
        out = out.replace('</body>', FALLBACK + '</body>')
    PAGE.write_text(out, encoding='utf-8')
    print(f'images: {n[0]} below the buy box now lazy-load')


if __name__ == '__main__':
    main()
