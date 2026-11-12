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

# ---- upgrades on top of the copy deck (12 Nov 2026): research + clinician authority, the "same pathway" explainer,
# the week-by-week timeline. Facts only from published studies; no named doctor or endorsement (the doctor photo stays
# a disclosed model until a real clinician consents to be named).
PATHWAY = """<div class="wp-pathway"><h3>“Natural GLP-1”: the same pathway, your own hormone</h3>
<div class="wp-pathway-grid"><div class="wp-col"><b>GLP-1 injections</b><p>A prescription drug that imitates the GLP-1 hormone at drug strength, by needle, usually weekly.</p></div>
<div class="wp-col wp-us"><b>MedicLab Berberine + the routine</b><p>Works on the same GLP-1 “I'm full” pathway, the natural way: berberine is studied for your body's <em>own</em> GLP-1 release, and protein first plus a short walk add to it at every meal.*</p></div></div>
<p class="wp-fine">Not a GLP-1 medication and not a substitute for one: no drug-strength effect is promised. If your doctor prescribes a GLP-1 medication, follow your doctor.</p></div>"""
RESEARCH = """<h2 class="section-title">What the studies say, and what a careful clinician checks</h2>
<p>Berberine is one of the most studied botanicals for metabolism. Here is the research the routine is built on, stated the way a scientist would state it: what was studied, in whom, and what it does not prove.</p>
<div class="wp-studies">
<div class="wp-study"><span class="wp-tag">Mechanism · GLP-1</span><b>Berberine increased GLP-1 release</b><p>Yu Y. et al., <em>Biochemical Pharmacology</em>, 2010. Laboratory and animal research on the body's own GLP-1 secretion.</p></div>
<div class="wp-study"><span class="wp-tag">12 randomized trials</span><b>Lower body weight, BMI and waist circumference</b><p>Asbaghi O. et al., <em>Clinical Nutrition ESPEN</em>, 2020, a meta-analysis of human trials. Mostly at higher daily amounts than one serving of ours, and on the ingredient, not this product.</p></div>
<div class="wp-study"><span class="wp-tag">Human trial · glucose</span><b>Healthier glucose metabolism markers</b><p>Yin J., Xing H., Ye J., <em>Metabolism</em>, 2008. A 3-month human trial of berberine and glucose metabolism.</p></div>
<div class="wp-study"><span class="wp-tag">The root problem</span><b>A smaller after-meal GLP-1 response with extra weight</b><p>Færch K. et al., <em>Diabetes</em>, 2015. Why the “I'm full” signal gets quieter.</p></div>
<div class="wp-study"><span class="wp-tag">The plate</span><b>Protein raised GLP-1 and fullness</b><p>Lejeune M. et al., <em>American Journal of Clinical Nutrition</em>, 2006.</p></div>
<div class="wp-study"><span class="wp-tag">The walk</span><b>Light walking lowered after-meal sugar</b><p>Buffey A. et al., <em>Sports Medicine</em>, 2022, seven crossover trials.</p></div>
</div>
<div class="wp-clinic"><div class="wp-clinic-copy"><h3>The clinician's checklist for any “natural GLP-1” bottle</h3>
<ul class="wp-checks"><li><b>Every amount printed.</b> No proprietary blend. Ours: 800 mg extract, both strengths, about 73 mg berberine HCl.</li>
<li><b>Taken with meals.</b> Berberine's #1 side effect is the stomach; never on an empty stomach.</li>
<li><b>No stimulants.</b> No caffeine, no “fat burner” blend.</li>
<li><b>Medicine cautions up front.</b> Blood sugar medicine, GLP-1 medication, blood thinners, cyclosporine: ask first.</li>
<li><b>Never sold as a GLP-1 drug.</b> A bottle that calls itself one is not telling you the truth.</li>
<li><b>Made in an FDA-registered, GMP facility</b>, in the USA.</li></ul></div>"""
TIMELINE = """<div class="wp-timeline"><h3>What to expect, and when</h3>
<ol><li><b>Week 1: gentle start.</b> One capsule with your largest meal. Protein first. Let your body settle in.</li>
<li><b>Week 2: the full routine.</b> One capsule with lunch, one with dinner, a 10-minute walk after dinner.</li>
<li><b>Weeks 3 and 4: it becomes automatic.</b> The point where people say the evenings stop being about food.*</li>
<li><b>Weeks 8 to 12: judge it honestly.</b> Your afternoons, your evenings, how your clothes fit. No promise in pounds; your 60-day guarantee covers the first order the whole way.</li></ol>
<p class="wp-fine">Individual experiences vary. A supplement is not a substitute for a varied, balanced diet and an active lifestyle.</p></div>"""
UPGRADE_CSS = """
/* ---- upgrades: pathway, research, clinician checklist, timeline ---- */
.wp-pathway{margin:22px 0;padding:18px;border-radius:18px;background:#E6EFE9}
.wp-pathway h3,.wp-timeline h3,.wp-clinic h3{margin:0 0 10px;font-size:22px;line-height:1.25;color:#1F2421}
.wp-pathway-grid{display:grid;gap:10px}
.wp-col{background:#fff;border-radius:14px;padding:14px;border:1px solid #E3E0D7}.wp-col p{margin:6px 0 0}
.wp-us{border:2px solid #1D503A}.wp-us b{color:#1D503A}
.wp-fine{font-size:14px;color:#545B57;margin:10px 0 0}
.wp-studies{display:grid;gap:10px;margin:16px 0}
.wp-study{background:#fff;border:1px solid #E3E0D7;border-radius:14px;padding:14px 16px}.wp-study b{display:block;color:#1F2421;font-size:18px;margin:6px 0 4px}.wp-study p{margin:0;font-size:15px;color:#545B57}
.wp-tag{display:inline-block;background:#1D503A;color:#fff;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;border-radius:999px;padding:3px 10px}
.wp-clinic{display:grid;gap:16px;align-items:center;background:#F5F1E8;border-radius:20px;padding:18px;margin:18px 0}
.wp-checks{list-style:none;padding:0;margin:0;display:grid;gap:8px}.wp-checks li{position:relative;padding-left:28px}.wp-checks li::before{content:'✓';position:absolute;left:0;color:#1D503A;font-weight:800}
.wp-timeline{margin:18px 0 0;padding:18px;background:#fff;border-radius:18px;border:1px solid #E3E0D7}
.wp-timeline ol{margin:0;padding-left:20px;display:grid;gap:8px}
@media(min-width:760px){.wp-pathway-grid{grid-template-columns:1fr 1fr}.wp-studies{grid-template-columns:1fr 1fr 1fr}.wp-clinic{grid-template-columns:1.3fr 1fr;padding:26px}}
"""


def upgrade(body):
    # s08: the "same pathway" explainer at the end of the solution mechanism
    i = body.index('id="s08"'); j = body.index('</div></section>', i)
    body = body[:j] + PATHWAY + body[j:]
    # s12: research cards + clinician checklist; the doctor photo (a disclosed model) sits beside the checklist
    i = body.index('id="s12"'); a = body.index('<h2', i); j = body.index('</div></section>', i)
    s12 = body[a:j]
    fig = s12[s12.index('<figure'): s12.index('</figure>') + 9]
    note = s12[s12.index('<p><em>Model portrayal'):]
    body = body[:a] + RESEARCH + fig + '</div></div>' + note + body[j:]
    # s14: the one-line "What to expect" becomes the timeline
    i = body.index('id="s14"'); a = body.index('<p><strong>What to expect:</strong>', i); b = body.index('</p>', a) + 4
    body = body[:a] + TIMELINE + body[b:]
    return body


def main():
    html = (SRC / ('index.html' if (SRC / 'index.html').exists() else 'sales-page.source.html')).read_text()
    css = '\n'.join(re.findall(r'<style>(.*?)</style>', html, re.S))
    for a, b in BRAND.items():
        css = css.replace(a, b)
    (CAMP / 'assets' / 'css' / 'sales.css').write_text(css.strip() + '\n' + EXTRA_CSS.lstrip() + UPGRADE_CSS.lstrip())

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
    body = upgrade(body)
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
