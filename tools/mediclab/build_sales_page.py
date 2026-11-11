"""Funnel 2, the weight-management angle for MedicLab Berberine (same product and campaign 2475 as the glucose funnel):
turn the delivered sales page (copy-deck render: index.html + img/, kept in docs/mediclab/natural-glp1/) into the Page Kit
page /weight-support/, in the mediclab.us brand.

usage: python3 -I tools/mediclab/build_sales_page.py [<unzipped sales-page dir>]   (default docs/mediclab/natural-glp1)

Writes campaigns/mediclab/src/berberine/weight-support.html, assets/css/sales.css and assets/images/ml/weight/*.
The copy is the deck's, word for word, with its compliance lines (FDA disclaimer, "not a GLP-1 medication" FAQ,
example-review and model-portrayal labels). Changes: mediclab.us brand tokens; CTAs to the shared checkout with
?forceBundleId=plan|one; one radio group per offer block (one shared group left the top block unselected); the FAQ's
"Express is $5.97." dropped (the store has no express method).
"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMP = ROOT / 'campaigns' / 'mediclab' / 'src' / 'berberine'
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'mediclab' / 'natural-glp1'

BRAND = {  # deck token -> mediclab.us
    '--primary:#1F3D2C': '--primary:#1D503A',
    '--accent:#C2410C': '--accent:#1D503A',
    '--primary-tint:#edefee': '--primary-tint:#F5F1E8',
    '--primary-soft:#9aa8a0': '--primary-soft:#9AB5A6',
    '--accent-tint:#f6e4dd': '--accent-tint:#E6EFE9',
    '--accent-shadow:#9b340a': '--accent-shadow:#0B2A1B',
    '--ink:#2b2f36': '--ink:#2B3330',
    '--ink-strong:#111418': '--ink-strong:#1F2421',
    '--muted:#5d6470': '--muted:#545B57',
    '--line:#e6e8ec': '--line:#E3E0D7',
    "--font-heading:'Jost'": "--font-heading:'Fustat'",
    "--font-body:'Jost'": "--font-body:'Fustat'",
    '#1F3D2C': '#1D503A',
    '#F4EEE4': '#F5F1E8',
}
EXTRA_CSS = """
/* ---- mediclab.us brand layer ---- */
.announce{background:#F5F1E8;color:#1F2421;font-weight:500;letter-spacing:0}
.site-head{background:#0B2A1B;border-bottom:0}
.site-head .brand img{height:30px}
.head-cta{background:#E3F6A4;color:#0B2A1B}
.btn{border-radius:999px;font-weight:700}
.badge{background:#C4301C}
.offer{border-radius:18px}
.tone-dark{background:#0B2A1B}
.tone-dark .btn{background:#E3F6A4;color:#0B2A1B;box-shadow:none}
.tone-dark .guarantee-badge{color:var(--ink)}
.sec-guarantee .wrap{border-radius:24px}
thead th:nth-child(2){background:#1D503A}
tbody td:nth-child(2){background:#E6EFE9}
.media{border-radius:20px}
.site-foot{background:#0B2A1B;color:#C9D9CF;border-top:0}
.site-foot a{color:#fff}
.site-foot .foot-logo{height:26px;width:auto;margin:0 auto 18px}
"""
CHECKOUT = "{{ 'berberine-checkout.html' | campaign_link }}"
SYNC_JS = """<script>
(function(){
  // the chosen offer (sections 05 and 16 stay in sync) rides into every CTA as the checkout's bundle card
  var base = document.body.getAttribute('data-checkout');
  function sync(){
    var c = document.querySelector('input[name^=offer]:checked'); if (!c) return;
    document.querySelectorAll('.offer').forEach(function(o){ o.classList.toggle('selected', o.querySelector('input').value === c.value); });
    var q = location.search.replace(/^\\?/, '').split('&').filter(function(p){ return p && p.indexOf('forceBundleId=') !== 0; });
    q.unshift('forceBundleId=' + c.value);
    document.querySelectorAll('a[data-cta]').forEach(function(a){ a.href = base + '?' + q.join('&'); });
  }
  document.addEventListener('change', function(e){ if (/^offer/.test(e.target.name || '')) { document.querySelectorAll('input[name^=offer]').forEach(function(i){ i.checked = i.value === e.target.value; }); sync(); } });
  sync();
  // sticky mobile CTA once the hero offer scrolls away
  var bar = document.querySelector('.sticky-cta'), anchor = document.querySelector('#s05');
  if (bar && anchor && 'IntersectionObserver' in window) {
    new IntersectionObserver(function(es){ es.forEach(function(e){ bar.classList.toggle('show', !e.isIntersecting && e.boundingClientRect.top < 0); }); }).observe(anchor);
  }
})();
</script>"""


def main():
    html = (SRC / ('index.html' if (SRC / 'index.html').exists() else 'sales-page.source.html')).read_text()
    css = '\n'.join(re.findall(r'<style>(.*?)</style>', html, re.S))
    for a, b in BRAND.items():
        css = css.replace(a, b)
    (CAMP / 'assets' / 'css' / 'sales.css').write_text(css.strip() + '\n' + EXTRA_CSS.lstrip())

    title = re.search(r'<title>(.*?)</title>', html, re.S).group(1).strip()
    desc = re.search(r'<meta name="description" content="(.*?)">', html, re.S).group(1)
    body = html[html.index('<body>') + 6: html.rindex('<script>')]

    # images -> campaign assets
    img_dir = CAMP / 'assets' / 'images' / 'ml' / 'weight'
    img_dir.mkdir(parents=True, exist_ok=True)
    for f in (SRC / 'img').iterdir():
        if not f.name.startswith('mediclab-logo'):
            shutil.copy2(f, img_dir / f.name)
    body = re.sub(r'src="img/(mediclab-logo-[^"]+)"', 'src="{{ \'images/ml/mediclab-logo-white.png\' | campaign_asset }}"', body, count=1)
    body = re.sub(r'src="img/([^"]+)"', lambda m: 'src="{{ \'images/ml/weight/%s\' | campaign_asset }}"' % m.group(1), body)
    # CTAs -> funnel checkout (the script adds ?forceBundleId=)
    body = re.sub(r'href="https://mediclab\.us/cart/add\?[^"]*"', f'href="{CHECKOUT}?forceBundleId=plan"', body)
    # offer radios: 0/2 = monthly plan, 1/3 = one bottle
    for old, new in (('0', 'plan'), ('2', 'plan'), ('1', 'one'), ('3', 'one')):
        body = body.replace(f'name="offer" value="{old}"', f'name="offer" value="{new}"')
        body = body.replace(f'data-offer="{old}"', f'data-offer="{new}"')
    body = re.sub(r'(<input type="radio" name="offer" value="plan")(>)', r'\1 checked\2', body)
    # one radio group per offer block (sections 05 and 16), or the browser keeps only the last pre-checked radio
    i = body.index('id="s16"')
    body = body[:i] + body[i:].replace('name="offer"', 'name="offer-2"')
    # no express method on the store yet
    n = body.count(' Express is $5.97.')
    body = body.replace(' Express is $5.97.', '')
    assert n == 1, f'express line found {n} times'
    # footer: the brand logo over the policy links
    body = body.replace('<footer class="site-foot"><div class="wrap">',
                        '<footer class="site-foot"><div class="wrap"><img class="foot-logo" src="{{ \'images/ml/mediclab-logo-white.png\' | campaign_asset }}" alt="MedicLab">', 1)
    assert 'mediclab.us/cart' not in body and 'img/' not in body.replace('images/ml/', '')

    front = ('---\n'
             f'title: "{title}"\n'
             'page_layout: base-sales.html\n'
             'page_type: product\n'
             f'description: "{desc}"\n'
             'next_url: berberine-checkout.html\n'
             'styles:\n  - css/sales.css\n  - css/berberine.css\n'
             '---\n')
    page = front + body.replace('<body>', '') + SYNC_JS + '\n'
    page = page.replace('<main id="top">', '<main id="top">', 1)
    (CAMP / 'weight-support.html').write_text(page)
    print('wrote', CAMP / 'weight-support.html', len(page), 'bytes;', len(list(img_dir.iterdir())), 'images')


if __name__ == '__main__':
    main()
