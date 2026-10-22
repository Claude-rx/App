"""Homepage and product page for the Adaptive Peptide Foundation, written for the 45+ buyer persona.

Sources
- Skinofab_Color_Adapting_Foundation_Market_and_Persona_Report.md: "Linda, 56" (dry-to-normal skin, fine lines,
  sun spots, redness, a tone that shifted; tried 5-10 foundations; fears the wrong shade, looking cakey or
  "done", wasted money and hidden subscriptions; values honesty, women her age, easy returns), the review
  complaints (shade match 52-58% negative, coverage 40-51%, "dries mature skin" 62%, value 47-74%, trust), the
  product answer (one adaptive shade, serum base, PDRN + peptides + Pro-Xylane, fragrance-free, 30-day money-back
  guarantee, Automatic Refills) and the compliance rules (no SPF claim, never "matches every skin tone",
  cosmetic claims only).
- The offer: ccf_copy.PACKS / REFILL (1 bottle or 2 bottles + free gifts, one-time or with Automatic Refills).

The live store builds with apf_pages.py --classic, which uses only the trust row (trust_html, TRUST_CSS) from here;
home_sections() and pdp_sections() are the long-form layout.
- SKINOFAB product sheet: Adaptive Peptide Foundation, PDRN, 30 mL / 1.01 fl oz, matte black airless bottle
  103 mm x 32.5 mm.
- The 20-part long sales page structure (above the fold 1-5, then 6-20); PDP_SECTIONS follows it in order.

Images are slot names ({img:slot}); apf_pages.py maps them to files (real product photography from the product
sheet, persona photos without any product in them) and fills them in.
"""

import json
import ccf_copy

PRODUCT = 'Adaptive Peptide Foundation'
PACKS, REFILL = ccf_copy.PACKS, ccf_copy.REFILL
PACK1 = PACKS[0]

def usd(v):
    f = float(v)
    return '$%d' % f if f == int(f) else '$%.2f' % f

# prices the long-form sections quote: one bottle bought once, and with Automatic Refills
ONCE, REFILLED = usd(PACK1['price']), usd(PACK1['refill'])
# the product page shows the refills box (buy once or refills) or hides it ticked (refills only)
CHOICE = REFILL.get('show_box', True)

# line icons (24px grid, drawn as strokes in the text colour); the seal is the brand's filled black badge
_SVG = '<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
ICONS = {
    'seal': ('<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 1.6l2.3 1.7 2.8-.3 1.1 2.6 2.6 1.1-.3 2.8 1.7 2.5-1.7 2.3.3 2.8-2.6 1.1-1.1 2.6-2.8-.3L12 22.4l-2.3-1.7-2.8.3-1.1-2.6-2.6-1.1.3-2.8L1.6 12l1.7-2.3-.3-2.8 2.6-1.1 1.1-2.6 2.8.3z"/>'
             '<path d="M7.9 12.3l2.7 2.7 5.5-5.7" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
    'bell': _SVG + '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>',
    # a circular arrow around a parcel: the refill can be stopped
    'cancel': _SVG + '<path d="M3 12a9 9 0 1 0 9-9 9.7 9.7 0 0 0-6.7 2.7L3 8"/><path d="M3 3v5h5"/><path d="M12 8.3l3.3 1.9v3.7L12 15.8l-3.3-1.9v-3.7z"/><path d="M8.7 10.2 12 12l3.3-1.8M12 12v3.8"/></svg>',
    'renew': _SVG + '<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>',
    'truck': _SVG + '<path d="M1 4h14v12H1z"/><path d="M15 9h4l3 3v4h-7"/><circle cx="6" cy="18.5" r="1.8"/><circle cx="18" cy="18.5" r="1.8"/></svg>',
    'shield': _SVG + '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    'lock': _SVG + '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
}
# Refill terms, shown next to the button whenever refills are ticked ({amount} = the chosen pack's refill price)
TERMS = ("You pay {amount} today, then {amount} every %d days until you cancel. We email you before every refill. "
         "To skip or cancel, just email hey@skinofab.com. No minimum, no fees." % REFILL['every'])
TRUST_CSS = r"""
.apf-trust{text-align:center;margin:16px 0 0;color:#151515}
.apf-trust__head{display:flex;align-items:center;justify-content:center;gap:8px;margin:0 0 14px !important;font-size:17px;font-weight:600;letter-spacing:-.01em;color:#151515 !important}
.apf-trust__head svg{flex:none;color:#151515}
.apf-trust__row{list-style:none !important;margin:0 !important;padding:0 !important;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.apf-trust__row li{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;align-items:center;gap:6px;font-size:14px;line-height:1.3;color:#2b2b2b}
.apf-trust__row li:before{content:none !important}
.apf-trust__row[hidden]{display:none !important}
.apf-trust__row b{font-weight:600}
.apf-trust__row svg{width:26px;height:26px;color:#151515}
.apf-trust__terms{margin:14px auto 0 !important;max-width:470px;font-size:13px !important;line-height:1.45;color:#4a4a4a !important}
"""

def trust_html(terms=True):
    """'Love it or your money back', then a row of three facts and the refill terms. While refills are on: refill
    reminder / cancel any time / renews at the pack's refill price; bought once: free shipping / 30-day guarantee /
    secure checkout. The page starts in ccf_copy.REFILL['default']; the offer picker keeps rows, price and terms in
    step with the chosen pack and the refills box."""
    on = bool(REFILL.get('default'))
    def row(kind, items, shown):
        cells = ''.join(f'<li>{ICONS[k]}<span>{label}</span></li>' for k, label in items)
        return f'<ul class="apf-trust__row" data-sf-trust-row="{kind}"{"" if shown else " hidden"}>{cells}</ul>'
    renew = f'Renews at <b data-sf-renew>{usd(PACK1["refill"])}</b> every {REFILL["every"]} days'
    rows = (row('refill', (('bell', 'Refill reminder'), ('cancel', 'Cancel any time'), ('renew', renew)), on) +
            row('once', (('truck', 'Free shipping'), ('shield', '30-day guarantee'), ('lock', 'Secure checkout')), not on))
    return (f'<div class="apf-trust"><p class="apf-trust__head">{ICONS["seal"]}<span>Love it or your money back</span></p>'
            f'{rows}' +
            (f'<p class="apf-trust__terms" data-sf-refill-terms="{html_attr(TERMS)}"'
             + (f'>{html_attr(TERMS.replace("{amount}", usd(PACK1["refill"])))}</p>' if REFILL.get('default') else ' hidden></p>')
             if terms else '') + '</div>')

def html_attr(text):
    return text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')

CSS = r"""
.apf{font-family:futura-pt,'Futura Book',Jost,'Helvetica Neue',Arial,sans-serif;color:#151515;font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
.apf *{box-sizing:border-box}
.apf h1,.apf h2,.apf h3,.apf h4,.apf p,.apf ul,.apf ol,.apf figure{margin:0;padding:0}
.apf h1,.apf h2,.apf h3,.apf h4{font-family:inherit;font-weight:600;letter-spacing:-.03em;color:inherit}
.apf h1{font-size:52px;line-height:1.08}
.apf h2{font-size:38px;line-height:1.15}
.apf h3{font-size:22px;line-height:1.25;letter-spacing:-.02em}
.apf h4{font-size:17px;line-height:1.3;letter-spacing:-.01em}
.apf p{color:#3b3b3b}
.apf strong{color:#151515;font-weight:600}
.apf img{max-width:100%;display:block}
.apf a{color:inherit}
.apf-sec{padding:72px 0}
.apf-sec--tight{padding:44px 0}
.apf-sec--grey{background:#f6f6f6}
.apf-sec--black{background:#151515;color:#fff}
.apf-sec--black p{color:#cfcfcf}
.apf-sec--black strong{color:#fff}
.apf-wrap{width:100%;max-width:1248px;margin:0 auto;padding:0 32px}
.apf-narrow{max-width:820px}
.apf-center{text-align:center}
.apf-center .apf-eyebrow{margin-left:auto;margin-right:auto}
.apf-head{max-width:760px;margin:0 0 40px}
.apf-center .apf-head,.apf-head.apf-center{margin-left:auto;margin-right:auto}
.apf-head p{margin-top:14px;font-size:18px}
.apf-eyebrow{display:inline-flex;align-items:center;gap:8px;padding:6px 14px;border-radius:5px;background:#fff;font-size:13px;line-height:1;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:#585858;margin-bottom:16px}
.apf-sec--grey .apf-eyebrow{background:#fff}
.apf-sec:not(.apf-sec--grey):not(.apf-sec--black) .apf-eyebrow{background:#f1f1f1}
.apf-sec--black .apf-eyebrow{background:#2a2a2a;color:#d6d6d6}
.apf-eyebrow:before{content:'';width:6px;height:6px;border-radius:50%;background:#151515}
.apf-sec--black .apf-eyebrow:before{background:#fff}
.apf-btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:16px 34px;border-radius:5px;background:#151515;color:#fff !important;font-size:15px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;text-decoration:none;border:1px solid #151515;transition:opacity .2s}
.apf-btn:hover{opacity:.86}
.apf-btn--white{background:#fff;color:#151515 !important;border-color:#fff}
.apf-btn--line{background:transparent;color:#151515 !important}
.apf-micro{margin-top:14px;font-size:13px;color:#6a6a6a;display:flex;flex-wrap:wrap;gap:6px 16px}
.apf-micro span:before{content:'\2713';margin-right:6px;color:#151515;font-weight:700}
.apf-sec--black .apf-micro{color:#bdbdbd}.apf-sec--black .apf-micro span:before{color:#fff}
.apf-grid2{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.apf-grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.apf-grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.apf-card{background:#fff;border:1px solid #e7e7e7;border-radius:14px;padding:26px}
.apf-sec--grey .apf-card{border-color:#ececec}
.apf-sec--black .apf-card{background:#1f1f1f;border-color:#2d2d2d}
.apf-card h3,.apf-card h4{margin-bottom:8px}
.apf-card p{font-size:15px}
.apf-num{display:inline-flex;width:34px;height:34px;border-radius:50%;background:#151515;color:#fff;align-items:center;justify-content:center;font-weight:600;font-size:15px;margin-bottom:16px}
.apf-sec--black .apf-num{background:#fff;color:#151515}
.apf-photo{width:100%;border-radius:16px;overflow:hidden;background:#ececec}
.apf-photo img{width:100%;height:100%;object-fit:cover}
.apf-photo--tall{aspect-ratio:4/5}
.apf-photo--sq{aspect-ratio:1/1}
.apf-photo--wide{aspect-ratio:4/3}
.apf-checks{list-style:none;display:grid;gap:12px;margin-top:22px}
.apf-checks li{position:relative;padding-left:32px;font-size:16px;color:#2b2b2b}
.apf-checks li:before{content:'\2713';position:absolute;left:0;top:1px;width:21px;height:21px;border-radius:50%;background:#151515;color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center}
.apf-sec--black .apf-checks li{color:#e9e9e9}.apf-sec--black .apf-checks li:before{background:#fff;color:#151515}
.apf-pains{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}
.apf-pains span{padding:9px 14px;border-radius:30px;background:#fff;border:1px solid #e2e2e2;font-size:14px;font-weight:500}
.apf-pains span:before{content:'\2715';margin-right:8px;font-size:11px;color:#8a8a8a}
/* hero */
.apf-hero{padding:56px 0 64px;background:linear-gradient(#f3f3f3,#fafafa)}
.apf-hero .apf-grid2{grid-template-columns:1.05fr .95fr}
.apf-hero p.apf-lede{font-size:19px;margin-top:18px;max-width:560px}
.apf-hero .apf-btn{margin-top:28px}
.apf-hero-visual{position:relative}
.apf-hero-visual .apf-photo{aspect-ratio:1/1}
.apf-quote-float{position:absolute;left:-28px;bottom:28px;max-width:300px;background:#fff;border-radius:14px;padding:16px 18px;box-shadow:0 14px 40px rgba(0,0,0,.12);display:flex;gap:12px;align-items:center}
.apf-quote-float img{width:54px;height:54px;border-radius:50%;object-fit:cover;flex:none}
.apf-quote-float p{font-size:14px;line-height:1.4;color:#2b2b2b}
.apf-quote-float small{display:block;margin-top:4px;color:#7a7a7a;font-size:12px}
.apf-stars{letter-spacing:2px;font-size:14px;color:#151515}
/* trust strip */
.apf-strip{background:#151515;color:#fff;padding:18px 0}
.apf-strip ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;gap:10px 34px;font-size:14px;font-weight:500;letter-spacing:.02em;text-transform:uppercase}
.apf-strip li:before{content:'\2713';margin-right:8px}
/* colour demo */
.apf-demo{position:relative;border-radius:16px;overflow:hidden;aspect-ratio:4/3;background:radial-gradient(circle at 30% 30%,#e9c6ad,#d4a88b 60%,#c79a7c)}
.apf-demo--deep{background:radial-gradient(circle at 30% 30%,#b88566,#9c6a4c 60%,#8a5b40)}
.apf-demo:before{content:'';position:absolute;left:24%;top:30%;width:52%;height:38%;border-radius:48% 52% 44% 56%/55% 45% 55% 45%;background:#f7f5f1;box-shadow:inset 0 0 18px rgba(255,255,255,.7);animation:apfBlend 6s ease-in-out infinite}
.apf-demo--deep:before{animation-name:apfBlendDeep}
.apf-demo--static:before{animation:none}
.apf-demo--blended:before{background:rgba(0,0,0,0);box-shadow:none}
.apf-demo span{position:absolute;left:16px;bottom:14px;background:rgba(255,255,255,.92);color:#151515;padding:7px 12px;border-radius:30px;font-size:13px;font-weight:600}
@keyframes apfBlend{0%,18%{background:#f7f5f1;transform:scale(1)}55%,85%{background:#dcb398;box-shadow:none;transform:scale(1.18);opacity:.55}100%{background:#f7f5f1;transform:scale(1)}}
@keyframes apfBlendDeep{0%,18%{background:#f7f5f1;transform:scale(1)}55%,85%{background:#a57153;box-shadow:none;transform:scale(1.18);opacity:.55}100%{background:#f7f5f1;transform:scale(1)}}
@media (prefers-reduced-motion:reduce){.apf-demo:before{animation:none}}
.apf-split{display:grid;grid-template-columns:1fr 1fr;gap:14px}
/* compare */
.apf-table{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e6e6e6;font-size:15px}
.apf-table th,.apf-table td{padding:16px 18px;text-align:left;border-bottom:1px solid #eee;vertical-align:top}
.apf-table thead th{font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:#6a6a6a;font-weight:600;background:#fafafa}
.apf-table thead th.apf-us{background:#151515;color:#fff}
.apf-table td.apf-us{background:#f4f4f4;font-weight:600;color:#151515}
.apf-table tr:last-child td{border-bottom:0}
.apf-table td:first-child{font-weight:600;color:#151515;width:22%}
.apf-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
/* fixes */
.apf-fix{display:grid;grid-template-columns:1fr 26px 1fr;gap:14px;align-items:center;padding:18px 0;border-bottom:1px solid #e6e6e6}
.apf-fix:last-child{border-bottom:0}
.apf-fix q{quotes:none;font-style:italic;color:#555;font-size:15px}
.apf-fix b{font-size:20px;text-align:center;color:#151515}
.apf-fix div{font-size:15px;color:#151515;font-weight:500}
/* reviews */
.apf-review{display:flex;flex-direction:column;gap:14px}
.apf-review-top{display:flex;gap:14px;align-items:center}
.apf-review-top img{width:64px;height:64px;border-radius:50%;object-fit:cover;flex:none}
.apf-review-top strong{display:block;font-size:16px}
.apf-review-top small{color:#7a7a7a;font-size:13px}
.apf-review p{font-size:15px}
.apf-review h4{font-size:16px}
/* offer */
.apf-offers{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;align-items:stretch}
.apf-offers--2{grid-template-columns:repeat(2,1fr);max-width:860px;margin:0 auto}
.apf-offer{position:relative;background:#fff;color:#151515;border-radius:16px;padding:28px 24px;display:flex;flex-direction:column;gap:10px;border:1px solid #e6e6e6}
.apf-offer--pick{border:2px solid #151515;box-shadow:0 18px 40px rgba(0,0,0,.10)}
.apf-sec--black .apf-offer p{color:#4a4a4a}
.apf-offer .apf-price{font-size:34px;font-weight:600;letter-spacing:-.03em}
.apf-offer .apf-price small{font-size:15px;font-weight:500;color:#7a7a7a;margin-left:6px}
.apf-offer .apf-btn{margin-top:auto}
.apf-badge{position:absolute;top:-12px;left:24px;background:#151515;color:#fff;font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:5px 12px;border-radius:30px}
.apf-sec--black .apf-badge{background:#fff;color:#151515;box-shadow:0 0 0 1px #151515}
.apf-plan-wrap{max-width:560px;margin:0 auto}
.apf-plan{padding:34px 30px 26px;text-align:left}
.apf-plan .apf-checks{margin:8px 0 6px}
.apf-plan .apf-btn{margin-top:14px;width:100%}
.apf-sec--black .apf-plan .apf-checks li{color:#2b2b2b}.apf-sec--black .apf-plan .apf-checks li:before{background:#151515;color:#fff}
.apf-sec--black .apf-plan .apf-btn{background:#151515;color:#fff !important}
.apf-plan-wrap + .apf-note{max-width:560px;margin-left:auto;margin-right:auto}
.apf-note{margin-top:26px;padding:16px 20px;border-radius:12px;border:1px dashed #5a5a5a;font-size:15px}
.apf-sec:not(.apf-sec--black) .apf-note{border-color:#cfcfcf}
/* guarantee */
.apf-seal{width:150px;height:150px;border-radius:50%;border:2px solid #151515;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-weight:600;letter-spacing:.04em;text-transform:uppercase;font-size:12px;line-height:1.2;margin:0 auto 22px}
.apf-seal b{font-size:44px;letter-spacing:-.03em;line-height:1}
.apf-sec--black .apf-seal{border-color:#fff}
/* faq */
.apf-faq{border-top:1px solid #e2e2e2}
.apf-faq details{border-bottom:1px solid #e2e2e2;padding:20px 0}
.apf-faq summary{cursor:pointer;list-style:none;font-weight:600;font-size:17px;display:flex;justify-content:space-between;gap:20px}
.apf-faq summary::-webkit-details-marker{display:none}
.apf-faq summary:after{content:'+';font-size:22px;line-height:1;font-weight:400}
.apf-faq details[open] summary:after{content:'\2013'}
.apf-faq details p{margin-top:12px;font-size:15.5px}
/* promise */
.apf-promise{font-size:23px;line-height:1.5;color:#eaeaea;font-weight:400;letter-spacing:-.01em}
.apf-promise strong{color:#fff}
.apf-label{background:#151515;border-radius:16px;overflow:hidden}
.apf-legal{font-size:12px;color:#8a8a8a;margin-top:16px}
"""+TRUST_CSS+r"""@media (max-width:989px){
 .apf h1{font-size:40px}.apf h2{font-size:31px}
 .apf-grid2,.apf-hero .apf-grid2{grid-template-columns:1fr;gap:36px}
 .apf-grid4{grid-template-columns:1fr 1fr}
 .apf-grid3,.apf-offers{grid-template-columns:1fr}
 .apf-quote-float{left:12px;bottom:12px;max-width:260px}
 .apf-sec{padding:56px 0}
}
@media (max-width:599px){
 .apf-wrap{padding:0 18px}
 .apf h1{font-size:34px}.apf h2{font-size:27px}
 .apf-grid4{grid-template-columns:1fr}
 .apf-fix{grid-template-columns:1fr;gap:6px}.apf-fix b{text-align:left;transform:rotate(90deg);width:20px}
 .apf-hero .apf-btn,.apf-cta-block .apf-btn{width:100%}
 .apf-strip ul{justify-content:flex-start;gap:8px 18px;font-size:12px}
}
"""

# reviews: the six persona stories from the design, kept with the people's first names and ages
REVIEWS = [
    ('rev-margaret', 'Margaret', 61, 'I thought my foundation days were over',
     'At 61, everything I tried settled into my smile lines within an hour and turned orange by lunch. I had given up and gone back to tinted moisturizer. This one looked like MY skin, just smoother and more even. No lines, no orange, no mask.'),
    ('rev-jennifer', 'Jennifer', 58, "The first one that doesn't cling to dry patches",
     'High-end, drugstore, custom-mixed: I have tried it all. They settled into my pores, clung to dry patches and oxidized. This glides over texture instead of sitting in it, and it stays comfortable all day.'),
    ('rev-deborah', 'Deborah', 53, 'I recommend it to my clients over 50',
     "I'm a makeup artist and 53 myself. What sold me is how it glides over texture instead of settling into it. It's now the base I use on every client with mature skin, and on my own."),
    ('rev-mia', 'Mia', 56, 'The guarantee got me to try one more time',
     'I had spent over $300 in a year returning foundations: wrong shade, oxidized, settled into lines. The shade-match guarantee convinced me to try once more. Three months in, I have not looked back.'),
    ('rev-patricia', 'Patricia', 58, 'I watched it change on my skin',
     "I'm a retired chemist and very skeptical of beauty marketing. I watched the white cream shift on my skin within a minute, including the pink undertone I can never find in stores. Eight hours later, still even. No oxidation."),
    ('rev-susan', 'Susan', 62, 'My daughter was right',
     'My daughter sent it to me. I was sure what works on her skin would never work on my 62-year-old face. No settling, no oxidation, and my skin looks rested. Listen to your daughters, ladies.'),
]

FAQ = [
    ('Which shade do I choose?',
     'There\'s no shade to choose. It goes on white and adapts to your skin tone as you blend. If you don\'t love how it looks on you, we\'ll refund you within 30 days.'),
    ('How do Automatic Refills work?',
     (f"Tick Automatic Refills on the product page and your pack costs less: {REFILLED} instead of {ONCE} for one bottle. " if CHOICE else
      f"Every pack comes with Automatic Refills at the lower price: {REFILLED} for one bottle. ") +
     f"It ships again every {REFILL['every']} days, and we email you before every refill. To skip or cancel, email hey@skinofab.com: no minimum, no fees." +
     (" Prefer to buy once? Leave the box unticked." if CHOICE else "")),
    ('Will it settle into my fine lines?',
     'It\'s designed not to. The base is a satin serum, not a matte formula, and soft-focus powders blur the look of lines instead of filling them with pigment. For the smoothest finish, use one thin layer and skip powder on dry areas.'),
    ('My skin is very dry. Will it look patchy?',
     'Dry, mature skin is who we made it for. Two forms of hyaluronic acid, ceramide NP, squalane and panthenol keep the finish comfortable, so it doesn\'t crack or cling to dry patches. Apply it over your usual moisturizer.'),
    ('Will it cover sun spots and redness?',
     'One pump gives an even, natural, medium coverage that softens sun spots and redness. For a darker spot, tap a second thin layer just there. It builds without looking heavy.'),
    ('I have sensitive skin. Will it sting?',
     'It\'s fragrance-free and made without propylene glycol, drying alcohol or parabens, the usual reasons thinner skin stings. As with anything new, try it on your jawline first.'),
    ('Does it have SPF?',
     'No. We left SPF out on purpose so the formula can stay a light, hydrating serum. Apply your daily sunscreen first; the foundation layers on top without pilling.'),
    ('How long does it last?',
     'It\'s made to stay even and comfortable through a full day, without turning orange or drying into your lines. If you\'re out from morning to dinner, a light touch-up on the nose and chin is usually all it needs.'),
    ('Can I buy just one bottle?',
     f"Yes. One bottle is {ONCE}, or {REFILLED} with Automatic Refills. Two bottles come with a free Skinofab Blender, a free Mystery Gift and free shipping."),
    ('How does the guarantee work?',
     'Wear it in your own daylight for 30 days. If you don\'t love it, email us and we\'ll refund you.'),
    ('When will my order arrive?',
     'Orders ship within 24–48 hours with tracking. Delivery usually takes 5–7 business days depending on where you live.'),
]

def _checks(items): return '<ul class="apf-checks">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def _micro(items): return '<div class="apf-micro">' + ''.join(f'<span>{i}</span>' for i in items) + '</div>'

def reviews_html(title='What women over 45 tell us', sub='Real routines, real skin. No filters, no 25-year-old models.'):
    cards = ''.join(f'''<article class="apf-card apf-review">
  <div class="apf-review-top"><img src="{{img:{k}}}" alt="{n}, {a}" loading="lazy" width="128" height="128"><div><strong>{n}, {a}</strong><small class="apf-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</small></div></div>
  <h4>{t}</h4><p>&ldquo;{q}&rdquo;</p></article>''' for k, n, a, t, q in REVIEWS)
    return f'''<section class="apf-sec apf-sec--grey" id="apf-reviews"><div class="apf-wrap">
  <div class="apf-head apf-center"><span class="apf-eyebrow">Reviews</span><h2>{title}</h2><p>{sub}</p></div>
  <div class="apf-grid3">{cards}</div></div></section>'''

def faq_html(items=FAQ, title='Questions women ask us before they order'):
    qa = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items)
    return f'''<section class="apf-sec" id="apf-faq"><div class="apf-wrap apf-narrow">
  <div class="apf-head apf-center"><span class="apf-eyebrow">FAQ</span><h2>{title}</h2></div>
  <div class="apf-faq">{qa}</div></div></section>'''

def offers_html(href, black=True, title='Choose your pack', sub=None, scarcity=True):
    sub = sub or ('Buy once, or save more with Automatic Refills.' if CHOICE else f'Automatic Refills every {REFILL["every"]} days, cancel any time.') + ' Love it or your money back.'
    def card(p):
        n = 'One 30 mL bottle' if p['key'] == '1' else 'Two 30 mL bottles'
        gifts = [label.replace('FREE ', 'Free ') for k, label, v in p['gifts']] or ['Free shipping']
        badge = f'<span class="apf-badge">{p["badge"]}</span>' if p.get('badge') else ''
        return (f'<div class="apf-offer apf-offer--pick apf-plan">{badge}<h3>{p["name"].capitalize()}</h3>'
                f'<div class="apf-price">{usd(p["price" if CHOICE else "refill"])} <s>{usd(p["compare"])}</s></div>'
                + (f'<p>or {usd(p["refill"])} with Automatic Refills, every {REFILL["every"]} days</p>' if CHOICE else
                   f'<p>Refills every {REFILL["every"]} days, cancel any time</p>') + f'{_checks([n] + gifts)}'
                f'<a class="apf-btn" href="{href}#apf-buy">Choose {p["name"]}</a></div>')
    note = ('<div class="apf-note"><strong>Launch batch.</strong> We make the foundation in small production runs so every bottle '
            'is fresh. When this first run sells out, new orders wait for the next batch.</div>') if scarcity else ''
    return f'''<section class="apf-sec{' apf-sec--black' if black else ' apf-sec--grey'}" id="apf-offer"><div class="apf-wrap">
  <div class="apf-head apf-center"><span class="apf-eyebrow">Launch offer</span><h2>{title}</h2><p>{sub}</p></div>
  <div class="apf-offers apf-offers--2">{''.join(card(p) for p in PACKS)}</div>{trust_html(terms=False)}{note}</div></section>'''

def guarantee_html(href, black=False):
    return f'''<section class="apf-sec{' apf-sec--black' if black else ''}" id="apf-guarantee"><div class="apf-wrap apf-narrow apf-center">
  <div class="apf-seal"><b>30</b>day love it<br>guarantee</div>
  <h2>Love it, or your money back.</h2>
  <p style="margin-top:16px;font-size:18px">Wear it for 30 days in your own bathroom light, in daylight, on a video call. If you don't love it,
  email us and we'll refund you. No forms to argue with.</p>
  <div style="margin-top:28px"><a class="apf-btn{' apf-btn--white' if black else ''}" href="{href}">Try it risk-free</a></div>
  {_micro(['30-day money-back guarantee', 'Free shipping', 'Real people at hey@skinofab.com'])}</div></section>'''


# ------------------------------------------------------------------------------------------------ homepage
def home_sections(pdp):
    """pdp: the design-relative link to the product page (rewritten to the NEXT URL by the theme build)."""
    return f'''<div class="apf" id="apf-home"><style>{CSS}</style>

<section class="apf-hero"><div class="apf-wrap"><div class="apf-grid2">
  <div>
    <span class="apf-eyebrow">Made for skin after 45</span>
    <h1>Stop guessing your shade after 45.</h1>
    <p class="apf-lede">The {PRODUCT} goes on white and turns into your skin as you blend. A hydrating serum foundation with
    PDRN and peptides that evens out sun spots and redness, without settling into your lines.</p>
    {_checks(['One adaptive shade: it does the matching for you', 'Satin serum finish that won\'t crease or cake', 'Fragrance-free, made for thinner, drier skin'])}
    <a class="apf-btn" href="{pdp}">Get yours &middot; {ONCE}</a>
    {_micro(['Love it or your money back', 'Free shipping', 'Fingertips, one minute'])}
  </div>
  <div class="apf-hero-visual">
    <div class="apf-photo"><img src="{{img:hero}}" alt="SKINOFAB {PRODUCT}, 30 mL" width="1254" height="1254"></div>
    <div class="apf-quote-float"><img src="{{img:rev-jennifer}}" alt="Jennifer, 58" width="108" height="108"><p>&ldquo;The first foundation that doesn't cling to my dry patches.&rdquo;<small>Jennifer, 58</small></p></div>
  </div>
</div></div></section>

<div class="apf-strip"><div class="apf-wrap"><ul><li>Made for skin after 45</li><li>One adaptive shade</li><li>PDRN + peptides</li><li>Fragrance-free</li><li>Love it or your money back</li></ul></div></div>

<section class="apf-sec"><div class="apf-wrap"><div class="apf-grid2">
  <div class="apf-photo apf-photo--tall"><img src="{{img:problem}}" alt="A woman in her late 50s looking at her skin" loading="lazy" width="1080" height="1350"></div>
  <div>
    <span class="apf-eyebrow">Sound familiar?</span>
    <h2>Your skin changed. Your foundation didn't.</h2>
    <p style="margin-top:16px;font-size:18px">After 45 the color of your skin shifts: a few sun spots, some redness, a tone that's more sallow, olive or grey than it used to be.
    Your skin gets thinner and drier too. So the shade you wore for years looks wrong, it settles into the lines around your eyes and mouth
    by lunch, and in daylight or on a video call you can see the mask.</p>
    <div class="apf-pains"><span>Wrong shade online</span><span>Settles into lines</span><span>Cakey on dry skin</span><span>Too sheer for spots</span><span>Looks &ldquo;made-up&rdquo;</span></div>
    <p style="margin-top:22px"><strong>It isn't you. Most foundations are made for young, even, oily skin.</strong> We made one for the skin you have now.</p>
  </div>
</div></div></section>

<section class="apf-sec apf-sec--grey" id="apf-how"><div class="apf-wrap">
  <div class="apf-head apf-center"><span class="apf-eyebrow">How it works</span><h2>One pump. One minute. Your skin, just fresher.</h2>
  <p>No shade to guess, no primer, no magnifying mirror. Your fingertips do the work.</p></div>
  <div class="apf-grid3">
    <div class="apf-card"><span class="apf-num">1</span><div class="apf-photo apf-photo--wide" style="margin-bottom:18px"><img src="{{img:pump}}" alt="Airless pump of the {PRODUCT}" loading="lazy" width="1254" height="940"></div>
      <h3>One pump, five dots</h3><p>Over your moisturizer and sunscreen, dot one pump on your forehead, cheeks, nose and chin. It looks white. That's the point.</p></div>
    <div class="apf-card"><span class="apf-num">2</span><div class="apf-demo" style="margin-bottom:18px"><span>Goes on white &rarr; turns into your tone</span></div>
      <h3>Blend and watch it change</h3><p>As you blend, color-adapting pigments shift to your skin tone, so there's no white cast and no orange edge.</p></div>
    <div class="apf-card"><span class="apf-num">3</span><div class="apf-photo apf-photo--wide" style="margin-bottom:18px"><img src="{{img:done}}" alt="A woman in her 50s with even, fresh skin" loading="lazy" width="1080" height="810"></div>
      <h3>Even, fresh, nothing in your lines</h3><p>A satin, skin-like finish that softens sun spots and redness and blurs the look of fine lines. Tap a second layer only where you want it.</p></div>
  </div>
</div></section>

<section class="apf-sec" id="apf-bases"><div class="apf-wrap"><div class="apf-grid2">
  <div class="apf-photo apf-photo--sq"><img src="{{img:bases}}" alt="The {PRODUCT}" loading="lazy" width="1254" height="1254"></div>
  <div>
    <span class="apf-eyebrow">One adaptive shade</span>
    <h2>One shade. No more guessing.</h2>
    <p style="margin-top:16px;font-size:18px">Dozens of shades to guess online is why buying foundation goes wrong after 45.
    This one goes on white and adapts to your skin tone as you blend, so there's nothing to choose.</p>
    <p style="margin-top:22px">Not happy with how it looks on you? <strong>We'll refund you within 30 days.</strong></p>
  </div>
</div></div></section>

<section class="apf-sec apf-sec--grey"><div class="apf-wrap"><div class="apf-grid2">
  <div>
    <span class="apf-eyebrow">What's inside</span>
    <h2>Skincare under your makeup, not just color on top.</h2>
    <p style="margin-top:16px;font-size:18px">Most color-changing foundations are a basic, drying base with fragrance and nothing in it for your skin.
    Ours is a serum, with the actives named on the bottle.</p>
    <div class="apf-grid2" style="gap:16px;margin-top:26px;align-items:stretch">
      <div class="apf-card"><h4>PDRN + Pro-Xylane</h4><p>Skincare actives for thinner, drier skin after 45.</p></div>
      <div class="apf-card"><h4>Peptides</h4><p>Matrixyl 3000 to smooth the look of fine lines while you wear it.</p></div>
      <div class="apf-card"><h4>Hyaluronic acid + ceramide</h4><p>With squalane and panthenol, so the finish never cracks.</p></div>
      <div class="apf-card"><h4>Fragrance-free</h4><p>No fragrance, propylene glycol, drying alcohol or parabens.</p></div>
    </div>
  </div>
  <div class="apf-label"><img src="{{img:label}}" alt="Label: Adaptive Peptide Foundation, PDRN, 30 mL / 1.01 fl oz" loading="lazy" width="930" height="1306" style="width:100%"></div>
</div></div></section>

<section class="apf-sec"><div class="apf-wrap apf-narrow">
  <div class="apf-head apf-center"><span class="apf-eyebrow">Built from your complaints</span><h2>We read what women 45+ said about the foundations they tried. Then we fixed it.</h2></div>
  <div>
    <div class="apf-fix"><q>&ldquo;Doesn't match my skin tone.&rdquo;</q><b>&rarr;</b><div>One adaptive shade that turns into your tone as you blend, and a 30-day money-back guarantee.</div></div>
    <div class="apf-fix"><q>&ldquo;It dried out my skin.&rdquo;</q><b>&rarr;</b><div>A serum base with hyaluronic acid, ceramide NP and squalane.</div></div>
    <div class="apf-fix"><q>&ldquo;Settles into my wrinkles.&rdquo;</q><b>&rarr;</b><div>Satin, never matte, with soft-focus powders that blur instead of fill.</div></div>
    <div class="apf-fix"><q>&ldquo;No coverage for my spots.&rdquo;</q><b>&rarr;</b><div>Buildable medium coverage: a second thin layer only where you want it.</div></div>
    <div class="apf-fix"><q>&ldquo;Not worth the price.&rdquo;</q><b>&rarr;</b><div>PDRN, peptides and Pro-Xylane from {REFILLED} a bottle, shipped free.</div></div>
    <div class="apf-fix"><q>&ldquo;I couldn't cancel my subscription.&rdquo;</q><b>&rarr;</b><div>{'Buy once, no strings. Refills are optional: a' if CHOICE else 'No traps: a'} reminder before each refill, and one email cancels them.</div></div>
  </div>
</div></section>

{reviews_html()}
{offers_html(pdp)}
{guarantee_html(pdp)}
{faq_html(FAQ[:7])}

<section class="apf-sec apf-sec--black apf-cta-block"><div class="apf-wrap apf-narrow apf-center">
  <h2>Look like yourself again. Just fresher.</h2>
  <p style="margin-top:14px;font-size:18px">One minute a day, no shade guessing. Love it or your money back.</p>
  <div style="margin-top:28px"><a class="apf-btn apf-btn--white" href="{pdp}">Get yours</a></div>
</div></section>
</div>'''


# ------------------------------------------------------------------------------------------------ product page
def pdp_sections():
    """Steps 6-20 of the long sales page structure; steps 1-5 live in the buy box above."""
    buy = '#apf-buy'
    return f'''<div class="apf" id="apf-pdp"><style>{CSS}</style>

<!-- 6. the problem -->
<section class="apf-sec apf-sec--grey" id="apf-problem"><div class="apf-wrap"><div class="apf-grid2">
  <div class="apf-photo apf-photo--tall"><img src="{{img:problem}}" alt="A woman in her late 50s looking at her skin" loading="lazy" width="1080" height="1350"></div>
  <div>
    <span class="apf-eyebrow">The problem</span>
    <h2>Your skin changed after 45. Your foundation didn't.</h2>
    <p style="margin-top:16px;font-size:18px">The shade you wore for years suddenly looks wrong. By lunch it has settled into the lines around your eyes and mouth.
    It clings to dry patches, it's too sheer for your sun spots, and in daylight or on a video call you can see it sitting on top of your skin.</p>
    <p style="margin-top:14px">You've probably bought five, maybe ten foundations trying to fix it. Drugstore, department store, a "color match" at the counter,
    a viral color-changing one. Most of them are in a drawer.</p>
    <div class="apf-pains"><span>Wrong shade online</span><span>Settles into lines</span><span>Cakey on dry skin</span><span>Too sheer for spots</span><span>Looks &ldquo;made-up&rdquo;</span></div>
  </div>
</div></div></section>

<!-- 7. the problem mechanism -->
<section class="apf-sec"><div class="apf-wrap">
  <div class="apf-head apf-center"><span class="apf-eyebrow">Why it happens</span><h2>Why foundation stops working on skin after 45</h2>
  <p>It isn't your technique. Three things changed, and most foundations ignore all three.</p></div>
  <div class="apf-grid3">
    <div class="apf-card"><span class="apf-num">1</span><h3>Your tone isn't one color anymore</h3><p>Sun spots, redness and a sallow, olive or grey cast mean your face now has several tones. One fixed pigment can only match one of them, so you see patches, a white cast or an orange edge.</p></div>
    <div class="apf-card"><span class="apf-num">2</span><h3>Your skin got thinner and drier</h3><p>After menopause skin makes less oil and holds less water. Matte and long-wear formulas pull moisture out of it, then crack and collect in every line.</p></div>
    <div class="apf-card"><span class="apf-num">3</span><h3>Formulas are made for 25-year-olds</h3><p>Heavy, high-pigment foundations are built to sit on top of young, even, oily skin. On mature skin they cover, but they emphasize every line and dry patch.</p></div>
  </div>
</div></section>

<!-- 8. the solution mechanism -->
<section class="apf-sec apf-sec--grey" id="apf-how"><div class="apf-wrap"><div class="apf-grid2">
  <div>
    <span class="apf-eyebrow">The solution</span>
    <h2>How the {PRODUCT} works</h2>
    <p style="margin-top:16px;font-size:18px">A color-adapting foundation built on a serum, so it adjusts to your tone and treats the skin underneath.</p>
    <div style="display:grid;gap:14px;margin-top:24px">
      <div class="apf-card"><h4>1. Color-adapting pigments</h4><p>Encapsulated pigments go on white. As you blend, they release and mix into your skin tone. No shade to guess.</p></div>
      <div class="apf-card"><h4>2. A hydrating serum base</h4><p>Two forms of hyaluronic acid, ceramide NP, squalane and panthenol keep dry, mature skin comfortable, so the finish stays satin instead of tight or flaky.</p></div>
      <div class="apf-card"><h4>3. PDRN, peptides and Pro-Xylane</h4><p>Skincare actives for thinner skin after 45, with Matrixyl 3000 peptides, niacinamide and adenosine. Named on the bottle, not hidden in a "complex".</p></div>
      <div class="apf-card"><h4>4. Soft-focus powders</h4><p>Silica and boron nitride scatter light to blur the look of lines and pores, without the dry, matte finish that settles into them.</p></div>
    </div>
  </div>
  <div style="display:grid;gap:14px">
    <div class="apf-demo"><span>Goes on white &rarr; turns into your tone</span></div>
    <div class="apf-split"><div class="apf-photo apf-photo--sq"><img src="{{img:threequarter}}" alt="{PRODUCT}, three-quarter view" loading="lazy" width="1254" height="1254"></div>
    <div class="apf-label"><img src="{{img:label}}" alt="Label: Adaptive Peptide Foundation, PDRN" loading="lazy" width="930" height="1306" style="width:100%;height:100%;object-fit:cover"></div></div>
  </div>
</div></div></section>

<!-- 9. why other solutions fall short -->
<section class="apf-sec"><div class="apf-wrap">
  <div class="apf-head apf-center"><span class="apf-eyebrow">Compare</span><h2>Why the foundations you tried fell short</h2></div>
  <div class="apf-scroll"><table class="apf-table">
    <thead><tr><th></th><th class="apf-us">{PRODUCT}</th><th>Regular liquid foundation</th><th>Other color-changing foundations</th></tr></thead>
    <tbody>
      <tr><td>Choosing a shade</td><td class="apf-us">Nothing to choose: one adaptive shade + 30-day money-back guarantee</td><td>Dozens of shades to guess online</td><td>Often turns ashy or orange, with no guarantee</td></tr>
      <tr><td>On dry, mature skin</td><td class="apf-us">Satin serum base, hydrating</td><td>Matte and long-wear formulas dry out and crack</td><td>Often a basic, drying base</td></tr>
      <tr><td>Fine lines</td><td class="apf-us">Blurs the look of lines, made not to settle</td><td>Pigment collects in lines</td><td>Often settles by midday</td></tr>
      <tr><td>Skincare actives</td><td class="apf-us">PDRN, peptides, Pro-Xylane, hyaluronic acid</td><td>Rarely</td><td>Usually none</td></tr>
      <tr><td>Fragrance</td><td class="apf-us">Fragrance-free</td><td>Often fragranced</td><td>Often contains parfum</td></tr>
      <tr><td>Buying</td><td class="apf-us">{'Buy once, or optional refills' if CHOICE else 'Refills every %d days' % REFILL['every']}: a reminder before each, cancel with one email</td><td>&mdash;</td><td>Complaints about surprise charges and hard cancellations</td></tr>
    </tbody></table></div>
</div></section>

<!-- 10. why this solution is effective -->
<section class="apf-sec apf-sec--grey"><div class="apf-wrap apf-narrow">
  <div class="apf-head apf-center"><span class="apf-eyebrow">Why it works</span><h2>Built from the complaints of women 45+</h2>
  <p>We studied what women over 45 wrote about the color-changing foundations they bought, and answered each complaint in the formula.</p></div>
  <div>
    <div class="apf-fix"><q>&ldquo;Doesn't match my skin tone.&rdquo;</q><b>&rarr;</b><div>One adaptive shade and a 30-day money-back guarantee.</div></div>
    <div class="apf-fix"><q>&ldquo;It dried out my skin.&rdquo;</q><b>&rarr;</b><div>A serum base with hyaluronic acid, ceramide NP and squalane.</div></div>
    <div class="apf-fix"><q>&ldquo;Settles into my wrinkles.&rdquo;</q><b>&rarr;</b><div>Satin finish and soft-focus powders that blur instead of fill.</div></div>
    <div class="apf-fix"><q>&ldquo;Doesn't cover my spots.&rdquo;</q><b>&rarr;</b><div>Buildable medium coverage, a second layer just where you need it.</div></div>
    <div class="apf-fix"><q>&ldquo;Stings my sensitive skin.&rdquo;</q><b>&rarr;</b><div>Fragrance-free, without propylene glycol, drying alcohol or parabens.</div></div>
    <div class="apf-fix"><q>&ldquo;Not worth the price.&rdquo;</q><b>&rarr;</b><div>Real skincare actives from {REFILLED} a bottle, shipped free.</div></div>
  </div>
</div></section>

<!-- 11. before and after -->
<section class="apf-sec"><div class="apf-wrap"><div class="apf-grid2">
  <div>
    <span class="apf-eyebrow">Before &amp; after</span>
    <h2>From white dots to your skin, in about a minute</h2>
    <p style="margin-top:16px;font-size:18px">Before you blend, the dots look white. That's the formula waiting for your skin. As you blend, it shifts to your tone
    and settles into a satin finish: sun spots and redness softened, nothing sitting in your lines.</p>
    <p style="margin-top:16px">&ldquo;I honestly thought my foundation days were over. At 61 everything settled into my smile lines and turned orange by lunch. This looked like my skin, just smoother and more even.&rdquo; <strong>Margaret, 61</strong></p>
  </div>
  <div>
    <div class="apf-split">
      <div class="apf-demo apf-demo--static"><span>Before blending</span></div>
      <div class="apf-demo apf-demo--static apf-demo--blended"><span>After blending</span></div>
    </div>
    <p class="apf-legal">Illustration of how the formula changes as you blend. Everyone's skin is different.</p>
  </div>
</div></div></section>

<!-- 12. proof elements -->
<section class="apf-sec apf-sec--grey"><div class="apf-wrap">
  <div class="apf-head apf-center"><span class="apf-eyebrow">Why you can trust it</span><h2>No hype. Just what's in the bottle and what we promise.</h2></div>
  <div class="apf-grid4">
    <div class="apf-card"><h4>Actives on the label</h4><p>PDRN is printed on the bottle. Peptides, Pro-Xylane and hyaluronic acid are listed in the ingredients.</p></div>
    <div class="apf-card"><h4>Fragrance-free</h4><p>No fragrance, propylene glycol, drying alcohol or parabens, for thinner, reactive skin.</p></div>
    <div class="apf-card"><h4>Honest shade promise</h4><p>It adapts to your tone as you blend. If you don't love how it looks on you, we'll refund you within 30 days.</p></div>
    <div class="apf-card"><h4>Refills without traps</h4><p>{'Buy once, or tick Automatic Refills to save. ' if CHOICE else ''}We email you before every refill, and one email cancels it.</p></div>
  </div>
</div></section>

<!-- 13. big promise and dream outcome -->
<section class="apf-sec apf-sec--black"><div class="apf-wrap"><div class="apf-grid2">
  <div class="apf-photo apf-photo--wide"><img src="{{img:promise}}" alt="Two women in their 50s and 60s with fresh, even skin" loading="lazy" width="1080" height="810"></div>
  <div>
    <span class="apf-eyebrow">Picture this</span>
    <h2>Tomorrow at 8 a.m.</h2>
    <p class="apf-promise" style="margin-top:18px">One pump, one minute, fingertips. You look in the mirror and <strong>your skin looks like yours again</strong>: even, fresh,
    nothing sitting in your lines. At lunch it's still there. On the video call, nobody sees makeup. <strong>They just see you, rested.</strong></p>
    <div style="margin-top:28px"><a class="apf-btn apf-btn--white" href="{buy}">Choose your pack</a></div>
  </div>
</div></div></section>

<!-- 14. usage instructions -->
<section class="apf-sec" id="apf-use"><div class="apf-wrap">
  <div class="apf-head apf-center"><span class="apf-eyebrow">How to use</span><h2>Four steps. About a minute.</h2></div>
  <div class="apf-grid4">
    <div class="apf-card"><span class="apf-num">1</span><h4>Moisturizer and sunscreen</h4><p>Apply your usual moisturizer and daily sunscreen. No primer needed.</p></div>
    <div class="apf-card"><span class="apf-num">2</span><h4>One pump, five dots</h4><p>Dot it on your forehead, cheeks, nose and chin. It looks white. That's the point.</p></div>
    <div class="apf-card"><span class="apf-num">3</span><h4>Blend and watch</h4><p>Blend outward with your fingertips or a brush. The white turns into your tone in about a minute.</p></div>
    <div class="apf-card"><span class="apf-num">4</span><h4>Layer where you want</h4><p>Tap a little more over sun spots or redness. Skip powder on dry areas so lines stay soft.</p></div>
  </div>
</div></section>

<!-- 15. ironclad guarantee -->
{guarantee_html(buy, black=False).replace('<section class="apf-sec"', '<section class="apf-sec apf-sec--grey"', 1)}

<!-- 16 + 17. offer with urgency, scarcity -->
{offers_html('', black=True, title='Your launch offer', sub='Pick your pack at the top of the page' + (': buy once, or save with Automatic Refills.' if CHOICE else '.') + ' Love it or your money back.')}

<!-- 18. customer reviews with images -->
{reviews_html()}

<!-- 19. FAQ -->
{faq_html()}

<!-- 20. customer service -->
<section class="apf-sec apf-sec--grey" id="apf-help"><div class="apf-wrap"><div class="apf-grid2">
  <div>
    <span class="apf-eyebrow">We're here</span>
    <h2>Real people, real answers</h2>
    <p style="margin-top:16px;font-size:18px">Questions about your order or your skin? Write to us. A real person on our team replies within one business day,
    Monday to Friday.</p>
    <div style="margin-top:26px;display:flex;flex-wrap:wrap;gap:12px"><a class="apf-btn" href="mailto:hey@skinofab.com">Email hey@skinofab.com</a><a class="apf-btn apf-btn--line" href="../pages/contact.html">Contact page</a></div>
  </div>
  <div class="apf-grid2" style="gap:14px;align-items:stretch">
    <a class="apf-card" style="text-decoration:none" href="../pages/postflows-track-your-order.html"><h4>Track your order</h4><p>Ships in 24–48 hours with tracking.</p></a>
    <a class="apf-card" style="text-decoration:none" href="../pages/contact.html"><h4>Ask about your skin</h4><p>Dry, sensitive, very fair or deep? Ask us first.</p></a>
    <a class="apf-card" style="text-decoration:none" href="../policies/shipping-policy.html"><h4>Shipping</h4><p>Delivery in about 5–7 business days.</p></a>
    <a class="apf-card" style="text-decoration:none" href="../policies/refund-policy.html"><h4>Returns &amp; refunds</h4><p>Love it or your money back, 30 days.</p></a>
  </div>
</div></div></section>
</div>'''


# ------------------------------------------------------------------------------------------------ buy box (steps 1-5)
# Copy rules for the product page buy box, applied by apf_pages.py (old text -> new text, exact visible text).
BUYBOX = [
    ('The color-adapting serum foundation made for skin after 45',
     'Even, fresh skin in one minute: no shade guessing, nothing settling into your lines'),
    ('and 1M+ others purchased', 'and women 45+ who stopped guessing their shade'),
    ('>Lisa<', '>Made for skin after 45<'),
    ('>Bestseller<', '>New<'),
    ('>Sale<', '>Launch offer<'),
    ('Stop guessing your shade after 45. It goes on white and turns into your skin as you blend, evening out spots and redness and softening the look of fine lines in about a minute. A hydrating serum base with peptides and PDRN means it doesn\'t dry you out or settle into your lines.',
     'Your skin changed after 45, so your old shade looks wrong and settles into your lines. This one goes on white and turns into your skin tone as you blend. A hydrating serum base with PDRN and peptides evens out sun spots and redness and blurs the look of fine lines, without drying you out.'),
    ('>30-day money-back guarantee<', '>Love it or your money back<'),
    ('Find your flawless shade with zero risk. Our Color Changing Foundation comes with a complete satisfaction promise: if your shade isn\'t spot-on, we\'ll make it right with a full refund—no questions asked.',
     'Wear it in your own daylight for 30 days. If you don\'t love it, email us and we\'ll refund you.'),
    ('We know finding the perfect foundation match online can feel like a gamble. That\'s why we\'ve eliminated the risk entirely. Try it on your skin, in your lighting, with your routine. If it\'s not your perfect match, simply let us know within 30 days and we\'ll process your full refund immediately.',
     'We know buying foundation online after 45 feels like a gamble. Try it on your skin, in your lighting, with your routine. Write to hey@skinofab.com within 30 days and a real person will sort it out.'),
    ('All returns must be postmarked within thirty (30) days of delivery. All returned items must be new, unused, and in their original packaging. See our',
     'Refunds are handled by email within 30 days of delivery. See our'),
]


# ------------------------------------------------------------------------------------------------ problem -> solution
# Product page, right after the first customer reviews (apply_persona.py): what goes wrong with ordinary foundation
# after 45, the root cause, then how this one is built the other way around. Cosmetic claims only; every ingredient
# named is one the "What's inside" section lists.
_X = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="11" fill="#151515"/>'
      '<path d="m8.5 8.5 7 7m0-7-7 7" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>')
_V = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="11" fill="#151515"/>'
      '<path d="m7.5 12.3 3 3 6-6.3" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')

PROBLEM_PAINS = [
    'Dozens of shades to guess online, for a skin tone that has shifted since you last bought one',
    'Matte, long-wear formulas that cling to dry patches and crack by lunch',
    'Pigment and powder that settle into fine lines and make them look deeper',
    'A color that oxidizes orange or turns ashy as the day goes on',
    'Primer, foundation, concealer, setting powder: four steps just to look like yourself',
]
ROOT_CAUSES = [
    ('Less collagen, less moisture',
     'In the years around menopause, skin makes less collagen and holds less water. It gets thinner, drier and more '
     'textured, so a formula built to control oil grips every dry patch and line.'),
    ('A tone that keeps moving',
     'Sun spots, redness and an undertone that shifts with age and seasons mean the shade that matched at 35 rarely '
     'matches now. A fixed shade can\'t follow you.'),
    ('Formulas made for 25-year-old skin',
     'Many foundations chase oil control and long wear with mattifying powders, drying alcohol and fragrance: the '
     'opposite of what drier, more sensitive skin needs.'),
]
SOLUTION_FIXES = [
    ('Guessing your shade', 'One adaptive shade. It goes on white and turns into your skin tone as you blend.'),
    ('Dry patches and cracking', 'A hydrating serum base with two forms of hyaluronic acid, ceramide NP and squalane.'),
    ('Settling into lines', 'Soft-focus powders blur the look of lines and pores instead of filling them with pigment.'),
    ('Makeup that does nothing for your skin', 'Skincare in every layer: Matrixyl 3000 peptides, PDRN and Pro-Xylane.'),
    ('Four steps every morning', 'One step with your fingertips, in about a minute. Fragrance-free.'),
]

PROBLEM_SOLUTION_CSS = r"""
.sfps{color:#151515;font-family:inherit}
.sfps *{box-sizing:border-box}
.sfps-sec{padding:72px 0}
.sfps-sec--grey{background:#f6f6f6}
.sfps-wrap{width:min(1180px,calc(100% - 40px));margin:0 auto}
.sfps-grid{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.sfps-photo{border-radius:20px;overflow:hidden;background:#eee;aspect-ratio:4/5}
.sfps-photo img{width:100%;height:100%;object-fit:cover;display:block}
.sfps-eyebrow{display:block;font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#6a6a6a;margin:0 0 12px}
.sfps h2{font-size:clamp(28px,3.4vw,42px);line-height:1.15;font-weight:600;letter-spacing:-.01em;margin:0}
.sfps-mark{background:#151515;color:#fff;border-radius:8px;padding:0 .22em;white-space:nowrap;display:inline-block;line-height:1.2;margin-top:.12em}
.sfps-lede{font-size:18px;line-height:1.55;color:#3b3b3b;margin:18px 0 0}
.sfps-list{list-style:none !important;margin:26px 0 0 !important;padding:0 !important;display:grid;gap:14px}
.sfps-list li{list-style:none;margin:0;padding:0;display:flex;gap:12px;align-items:flex-start;font-size:16px;line-height:1.45}
.sfps-list li:before{content:none !important}
.sfps-list svg{flex:none;margin-top:1px}
.sfps-close{margin:24px 0 0;font-size:16px;line-height:1.5;color:#3b3b3b;font-style:italic}
.sfps-head{text-align:center;max-width:760px;margin:0 auto 40px}
.sfps-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.sfps-card{background:#fff;border-radius:18px;padding:28px 26px}
.sfps-card b{display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;background:#151515;color:#fff;font-size:15px;margin:0 0 16px}
.sfps-card h3{font-size:20px;line-height:1.3;font-weight:600;margin:0 0 10px}
.sfps-card p{font-size:15.5px;line-height:1.55;color:#3b3b3b;margin:0}
.sfps-root{max-width:760px;margin:36px auto 0;text-align:center;font-size:19px;line-height:1.5;font-weight:500}
.sfps-fixes{margin:26px 0 0;display:grid;gap:12px}
.sfps-fix{display:grid;grid-template-columns:22px 1fr;gap:12px;align-items:start;padding:14px 16px;border:1px solid #e6e6e6;border-radius:14px;background:#fff}
.sfps-fix s{display:block;font-size:13px;color:#8a8a8a;text-decoration-thickness:1px;margin:0 0 3px}
.sfps-fix span{display:block;font-size:16px;line-height:1.45}
.sfps-cta{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin:28px 0 0}
.sfps-btn{display:inline-flex;align-items:center;justify-content:center;padding:16px 34px;border-radius:999px;background:#151515;color:#fff !important;text-decoration:none !important;font-size:14px;font-weight:600;letter-spacing:.1em;text-transform:uppercase}
.sfps-btn:hover{background:#000}
.sfps-note{font-size:14px;color:#3b3b3b}
@media (max-width:989px){
 .sfps-sec{padding:52px 0}
 .sfps-grid{grid-template-columns:1fr;gap:30px}
 .sfps-grid--rev .sfps-photo{order:-1}
 .sfps-cards{grid-template-columns:1fr}
 .sfps-photo{aspect-ratio:4/4.4}
}
@media (max-width:599px){
 .sfps-wrap{width:calc(100% - 32px)}
 .sfps-lede{font-size:16.5px}
 .sfps-card{padding:22px 20px}
 .sfps-root{font-size:17px}
 .sfps-btn{width:100%}
}
"""

def problem_solution_html(img_problem, img_solution, buy_href='#apf-buy'):
    """Three blocks: the problem (photo + what goes wrong), the root cause (three cards), the solution (problem ->
    fix rows, the product, a button to the offer). img_*: (src, width, height)."""
    pains = ''.join(f'<li>{_X}<span>{p}</span></li>' for p in PROBLEM_PAINS)
    cards = ''.join(f'<div class="sfps-card"><b>{i}</b><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(ROOT_CAUSES, 1))
    fixes = ''.join(f'<div class="sfps-fix">{_V}<div><s>{was}</s><span>{now}</span></div></div>' for was, now in SOLUTION_FIXES)
    ip, isol = img_problem, img_solution
    return f'''<div class="sfps" id="sf-problem-solution"><style>{PROBLEM_SOLUTION_CSS}</style>
<section class="sfps-sec"><div class="sfps-wrap sfps-grid">
  <div class="sfps-photo"><img src="{ip[0]}" alt="A woman in her late fifties looking at her skin" width="{ip[1]}" height="{ip[2]}" loading="lazy" decoding="async"></div>
  <div>
    <span class="sfps-eyebrow">The problem</span>
    <h2>Foundation wasn&rsquo;t made for <span class="sfps-mark">skin after 45</span></h2>
    <p class="sfps-lede">You&rsquo;re not doing it wrong. Most foundations are designed around younger, oilier skin. Then your skin changed, and they stopped working.</p>
    <ul class="sfps-list">{pains}</ul>
    <p class="sfps-close">The result: a drawer full of bottles that didn&rsquo;t work, and the feeling that makeup isn&rsquo;t for you anymore.</p>
  </div>
</div></section>
<section class="sfps-sec sfps-sec--grey"><div class="sfps-wrap">
  <div class="sfps-head"><span class="sfps-eyebrow">The root of it</span><h2>Your skin changed. <span class="sfps-mark">Your foundation didn&rsquo;t.</span></h2></div>
  <div class="sfps-cards">{cards}</div>
  <p class="sfps-root">So the problem was never your skin or your technique. It&rsquo;s a formula built for someone else.</p>
</div></section>
<section class="sfps-sec"><div class="sfps-wrap sfps-grid sfps-grid--rev">
  <div>
    <span class="sfps-eyebrow">The solution</span>
    <h2>So we built it <span class="sfps-mark">the other way around</span></h2>
    <p class="sfps-lede">The {PRODUCT} starts from skin after 45, not from a shade chart: Korean color-adapting technology in a skincare serum base.</p>
    <div class="sfps-fixes">{fixes}</div>
    <div class="sfps-cta"><a class="sfps-btn" href="{buy_href}">Get yours</a><span class="sfps-note">Love it in your own daylight for 30 days, or your money back.</span></div>
  </div>
  <div class="sfps-photo"><img src="{isol[0]}" alt="The {PRODUCT} bottle" width="{isol[1]}" height="{isol[2]}" loading="lazy" decoding="async"></div>
</div></section>
</div>'''


# ------------------------------------------------------------------------------------------------ dermatologist + reviews
# Product page versions of two homepage sections (apply_persona.py fills them from the homepage, after its copy rules),
# in the product page's style: same type, black highlight, rounded photos as the problem / solution block.
PDP_EXTRA_CSS = r"""
.sfx{color:#151515;font-family:inherit}
.sfx *{box-sizing:border-box}
.sfx-sec{padding:72px 0}
.sfx-sec--grey{background:#f6f6f6}
.sfx-wrap{width:min(1180px,calc(100% - 40px));margin:0 auto}
.sfx-grid{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:56px;align-items:center}
.sfx-photo{border-radius:20px;overflow:hidden;background:#eee;aspect-ratio:4/5}
.sfx-photo img{width:100%;height:100%;object-fit:cover;display:block}
.sfx-eyebrow{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#6a6a6a;margin:0 0 12px}
.sfx h2{font-size:clamp(28px,3.2vw,40px);line-height:1.18;font-weight:600;letter-spacing:-.01em;margin:0}
.sfx-mark{background:#151515;color:#fff;border-radius:8px;padding:0 .22em;white-space:nowrap;display:inline-block;line-height:1.2;margin-top:.12em}
.sfx-quote{margin:22px 0 0;padding:0;border:0}
.sfx-quote p{font-size:17.5px;line-height:1.6;color:#3b3b3b;margin:0 0 14px}
.sfx-quote strong{color:#151515}
.sfx-sign{display:flex;align-items:center;gap:14px;margin:24px 0 0;padding:18px 0 0;border-top:1px solid #e6e6e6}
.sfx-sign img{width:52px;height:52px;border-radius:50%;object-fit:cover;flex:none;border:2px solid #151515}
.sfx-sign b{display:block;font-size:17px;font-weight:600}
.sfx-sign span{display:block;font-size:14px;color:#6a6a6a;margin-top:2px}
.sfx-head{text-align:center;max-width:760px;margin:0 auto 36px}
.sfx-head .sfx-eyebrow{justify-content:center}
.sfx-stars{display:inline-flex;gap:2px;color:#151515}
.sfx-reviews{display:grid;grid-template-columns:repeat(var(--n,2),minmax(0,1fr));gap:22px;max-width:calc(var(--n,2) * 400px);margin:0 auto}
.sfx-review{background:#fff;border-radius:18px;overflow:hidden;display:flex;flex-direction:column}
.sfx-review .sfx-photo{border-radius:0;aspect-ratio:4/5}
.sfx-review-body{padding:22px 22px 24px;display:flex;flex-direction:column;gap:10px;flex:1}
.sfx-review h3{font-size:18px;line-height:1.3;font-weight:600;margin:0}
.sfx-review p{font-size:15.5px;line-height:1.55;color:#3b3b3b;margin:0}
.sfx-review-name{margin-top:auto;padding-top:8px;display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:14px}
.sfx-review-name b{font-weight:600}
.sfx-verified{display:inline-flex;align-items:center;gap:5px;color:#1f7a3f;font-size:13px;font-weight:500}
@media (max-width:989px){
 .sfx-sec{padding:52px 0}
 .sfx-grid{grid-template-columns:1fr;gap:28px}
 .sfx-photo{aspect-ratio:4/4.4}
 .sfx-review .sfx-photo{aspect-ratio:4/5}
}
@media (max-width:599px){
 .sfx-wrap{width:calc(100% - 32px)}
 .sfx-quote p{font-size:16.5px}
 .sfx-reviews{grid-template-columns:1fr}
}
"""
_STAR = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path fill="currentColor" '
         'd="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>')
_CHECK = ('<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="11" fill="currentColor"/>'
          '<path d="m7.5 12.3 3 3 6-6.3" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def dermatologist_html(d):
    """d: name, role, paragraphs (HTML, her words as the homepage shows them), photo (src, w, h), avatar src,
    headline (a verbatim fragment of her quote)."""
    paras = ''.join(f'<p>{p}</p>' for p in d['paragraphs'])
    ph = d['photo']
    return f'''<div class="sfx" id="sf-dermatologist"><style>{PDP_EXTRA_CSS}</style>
<section class="sfx-sec sfx-sec--grey"><div class="sfx-wrap sfx-grid">
  <div class="sfx-photo"><img src="{ph[0]}" alt="{d['name']}" width="{ph[1]}" height="{ph[2]}" loading="lazy" decoding="async"></div>
  <div>
    <span class="sfx-eyebrow">Dermatologist recommended</span>
    <h2>&ldquo;{d['headline_lead']} <span class="sfx-mark">{d['headline_mark']}</span>&rdquo;</h2>
    <blockquote class="sfx-quote">{paras}</blockquote>
    <div class="sfx-sign"><img src="{d['avatar']}" alt="" width="52" height="52" loading="lazy" decoding="async"><div><b>{d['name']}</b><span>{d['role']}</span></div></div>
  </div>
</div></section></div>'''

def pdp_reviews_html(eyebrow, title, reviews):
    """reviews: dicts with title, text, name, photo (src, w, h)."""
    stars = '<span class="sfx-stars" aria-label="5 out of 5 stars">' + _STAR * 5 + '</span>'
    cards = ''.join(f'''<article class="sfx-review">
  <div class="sfx-photo"><img src="{r['photo'][0]}" alt="{r['name']} with the {PRODUCT}" width="{r['photo'][1]}" height="{r['photo'][2]}" loading="lazy" decoding="async"></div>
  <div class="sfx-review-body">{stars}<h3>{r['title']}</h3><p>&ldquo;{r['text']}&rdquo;</p>
  <div class="sfx-review-name"><b>{r['name']}</b><span class="sfx-verified">{_CHECK}Verified buyer</span></div></div>
</article>''' for r in reviews)
    return f'''<div class="sfx" id="sf-video-reviews"><style>{PDP_EXTRA_CSS}</style>
<section class="sfx-sec sfx-sec--grey"><div class="sfx-wrap">
  <div class="sfx-head"><span class="sfx-eyebrow">{stars}{eyebrow}</span><h2>{title}</h2></div>
  <div class="sfx-reviews" style="--n:{len(reviews)}">{cards}</div>
</div></section></div>'''


# ------------------------------------------------------------------------------------------------ review wall
# Real reviews only: NEXT's own approved reviews of the product (rendered by the theme) plus the owner's imported
# reviews of the same formula (tools/reviews/import_reviews.py -> a data script loaded when the wall comes near).
# Hidden while there are none. Summary (average, 5..1 distribution) is computed from what is shown.
REVIEW_WALL_CSS = r"""
.sfr{color:#151515;font-family:inherit;padding:64px 0;background:#fff}
.sfr[hidden]{display:none !important}
.sfr *{box-sizing:border-box}
.sfr-wrap{width:min(1180px,calc(100% - 40px));margin:0 auto}
.sfr-top{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:48px;align-items:start}
.sfr h2{font-size:clamp(26px,3vw,36px);line-height:1.2;font-weight:600;margin:0 0 18px}
.sfr-avg{display:flex;align-items:center;gap:14px}
.sfr-avg b{font-size:48px;line-height:1;font-weight:600}
.sfr-avg small{display:block;font-size:14px;color:#6a6a6a;margin-top:4px}
.sfr-stars{display:inline-flex;gap:2px;color:#151515;vertical-align:middle}
.sfr-stars svg{width:18px;height:18px}
.sfr-stars i{position:relative;display:inline-block;width:18px;height:18px;color:#d6d6d6}
.sfr-stars i svg{position:absolute;inset:0}
.sfr-stars i svg+svg{color:#151515;clip-path:inset(0 calc(100% - var(--f)) 0 0)}
.sfr-dist{list-style:none !important;margin:18px 0 0 !important;padding:0 !important;display:grid;gap:7px}
.sfr-dist li{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:34px 1fr 52px;gap:10px;align-items:center;font-size:14px;cursor:pointer}
.sfr-dist li:before{content:none !important}
.sfr-dist span{height:8px;border-radius:99px;background:#ececec;overflow:hidden}
.sfr-dist span em{display:block;height:100%;background:#151515;border-radius:99px}
.sfr-dist small{color:#6a6a6a;text-align:right}
.sfr-write{display:inline-flex;margin-top:22px;padding:13px 26px;border-radius:999px;border:1.5px solid #151515;color:#151515 !important;text-decoration:none !important;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
.sfr-write:hover{background:#151515;color:#fff !important}
.sfr-bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;margin:0 0 18px}
.sfr-chips{display:flex;flex-wrap:wrap;gap:8px}
.sfr-chip{border:1px solid #d9d9d9;background:#fff;border-radius:999px;padding:8px 14px;font:inherit;font-size:13px;color:#151515;cursor:pointer}
.sfr-chip[aria-pressed="true"]{background:#151515;border-color:#151515;color:#fff}
.sfr-sort{border:1px solid #d9d9d9;border-radius:10px;padding:8px 10px;font:inherit;font-size:13px;background:#fff;color:#151515}
.sfr-list{display:grid;gap:14px}
.sfr-card{background:#f6f6f6;border-radius:16px;padding:20px 22px}
.sfr-head{display:flex;align-items:center;gap:12px;margin:0 0 10px}
.sfr-ava{width:38px;height:38px;border-radius:50%;background:#151515;color:#fff;display:grid;place-content:center;font-size:14px;font-weight:600;flex:none}
.sfr-who{flex:1;min-width:0;font-size:14px;line-height:1.35}
.sfr-who b{font-weight:600}
.sfr-who small{display:block;color:#6a6a6a;font-size:12.5px}
.sfr-ver{display:inline-flex;align-items:center;gap:4px;color:#1f7a3f;font-size:12.5px;font-weight:500;margin-left:8px}
.sfr-card h3{font-size:16px;font-weight:600;margin:8px 0 4px;line-height:1.35}
.sfr-body{font-size:15px;line-height:1.55;color:#2b2b2b;margin:0;white-space:pre-line}
.sfr-body.is-clamped{display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden}
.sfr-more-text{background:none;border:0;padding:4px 0 0;font:inherit;font-size:13px;font-weight:600;text-decoration:underline;cursor:pointer;color:#151515}
.sfr-photos{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.sfr-photos button{padding:0;border:0;background:none;cursor:zoom-in;border-radius:10px;overflow:hidden;width:84px;height:84px}
.sfr-photos img{width:84px;height:84px;object-fit:cover;display:block}
.sfr-more{display:flex;justify-content:center;margin-top:22px}
.sfr-more button{padding:14px 30px;border-radius:999px;background:#151515;color:#fff;border:0;font:inherit;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;cursor:pointer}
.sfr-empty{padding:30px;text-align:center;color:#6a6a6a;background:#f6f6f6;border-radius:16px}
.sfr-box{position:fixed;inset:0;z-index:2147483002;background:rgba(21,21,21,.85);display:flex;align-items:center;justify-content:center;padding:24px}
.sfr-box[hidden]{display:none}
.sfr-box img{max-width:min(92vw,900px);max-height:86vh;border-radius:12px}
.sfr-box button{position:absolute;top:16px;right:16px;width:44px;height:44px;border-radius:50%;border:0;background:#fff;font-size:22px;cursor:pointer}
@media (min-width:990px){.sfr-top>div:first-child{position:sticky;top:120px}}
@media (max-width:989px){.sfr{padding:48px 0}.sfr-top{grid-template-columns:1fr;gap:26px}}
@media (max-width:599px){.sfr-wrap{width:calc(100% - 32px)}.sfr-card{padding:18px}.sfr-bar{flex-direction:column;align-items:stretch}.sfr-sort{width:100%}}
"""

REVIEW_WALL_JS = r"""
(function () {
  var root = document.getElementById('sf-review-wall');
  var sentinel = document.getElementById('sf-review-wall-sentinel');
  if (!root || !sentinel) return;
  var STAR = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>';
  var CHECK = '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="currentColor"/><path d="m7.5 12.3 3 3 6-6.3" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var PAGE = 8, all = [], shown = 0, filter = 'all', sort = 'recent', photoBase = {};
  try { photoBase = JSON.parse((root.querySelector('[data-sf-review-photos]') || {}).textContent || '{}'); } catch (e) {}
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function stars(v) {
    var h = '<span class="sfr-stars" role="img" aria-label="' + v + ' out of 5 stars">';
    for (var i = 0; i < 5; i++) { var f = Math.max(0, Math.min(1, Math.round((v - i) * 2) / 2)); h += '<i style="--f:' + (f * 100) + '%">' + STAR + STAR + '</i>'; }
    return h + '</span>';
  }
  function month(d) {
    if (!d) return '';
    var t = new Date(d + (d.length === 10 ? 'T12:00:00' : ''));
    return isNaN(t) ? '' : t.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
  }
  function photoSrc(p) { return /^https?:|^\//.test(p) ? p : (photoBase[p] || ''); }
  function list() {
    var l = all.filter(function (r) {
      return filter === 'all' || (filter === 'photos' ? r.photos && r.photos.length : String(r.rating) === filter);
    });
    l.sort(function (a, b) {
      if (sort === 'high') return b.rating - a.rating || (b.date > a.date ? 1 : -1);
      if (sort === 'low') return a.rating - b.rating || (b.date > a.date ? 1 : -1);
      if (sort === 'photos') return ((b.photos || []).length ? 1 : 0) - ((a.photos || []).length ? 1 : 0) || (b.date > a.date ? 1 : -1);
      return b.date > a.date ? 1 : b.date < a.date ? -1 : 0;
    });
    return l;
  }
  function card(r) {
    var initial = esc((r.name || '?').charAt(0).toUpperCase());
    var ph = (r.photos || []).map(function (p) { var s = photoSrc(p); return s ? '<button type="button" data-sfr-zoom="' + esc(s) + '"><img src="' + esc(s) + '" alt="Photo from ' + esc(r.name) + '" loading="lazy" decoding="async"></button>' : ''; }).join('');
    return '<article class="sfr-card"><div class="sfr-head"><span class="sfr-ava" aria-hidden="true">' + initial + '</span>' +
      '<div class="sfr-who"><b>' + esc(r.name) + '</b>' + (r.verified ? '<span class="sfr-ver">' + CHECK + 'Verified buyer</span>' : '') +
      '<small>' + esc(month(r.date)) + '</small></div>' + stars(r.rating) + '</div>' +
      (r.title ? '<h3>' + esc(r.title) + '</h3>' : '') +
      '<p class="sfr-body' + ((r.body || '').length > 360 ? ' is-clamped' : '') + '">' + esc(r.body) + '</p>' +
      ((r.body || '').length > 360 ? '<button type="button" class="sfr-more-text">Read more</button>' : '') +
      (ph ? '<div class="sfr-photos">' + ph + '</div>' : '') + '</article>';
  }
  function paint(reset) {
    var l = list(), box = root.querySelector('.sfr-list');
    if (reset) { shown = 0; box.innerHTML = ''; }
    var next = l.slice(shown, shown + PAGE);
    box.insertAdjacentHTML('beforeend', next.length ? next.map(card).join('') : (shown ? '' : '<p class="sfr-empty">No reviews match this filter yet.</p>'));
    shown += next.length;
    root.querySelector('.sfr-more').hidden = shown >= l.length;
  }
  function summary() {
    var n = all.length, sum = 0, dist = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }, photos = 0;
    all.forEach(function (r) { sum += r.rating; dist[r.rating] = (dist[r.rating] || 0) + 1; if (r.photos && r.photos.length) photos++; });
    var avg = n ? Math.round(sum / n * 10) / 10 : 0;
    root.querySelector('[data-sfr-avg]').innerHTML = '<b>' + avg.toFixed(1) + '</b><div>' + stars(avg) + '<small>Based on ' + n.toLocaleString() + ' review' + (n === 1 ? '' : 's') + '</small></div>';
    root.querySelector('.sfr-dist').innerHTML = [5, 4, 3, 2, 1].map(function (s) {
      var c = dist[s] || 0, pct = n ? Math.round(c / n * 100) : 0;
      return '<li data-sfr-filter="' + s + '" title="Show ' + s + '-star reviews">' + s + ' &#9733;<span><em style="width:' + pct + '%"></em></span><small>' + c.toLocaleString() + '</small></li>';
    }).join('');
    var chips = '<button type="button" class="sfr-chip" data-sfr-filter="all" aria-pressed="true">All (' + n.toLocaleString() + ')</button>';
    if (photos) chips += '<button type="button" class="sfr-chip" data-sfr-filter="photos" aria-pressed="false">With photos (' + photos + ')</button>';
    [5, 4, 3, 2, 1].forEach(function (s) { if (dist[s]) chips += '<button type="button" class="sfr-chip" data-sfr-filter="' + s + '" aria-pressed="false">' + s + ' &#9733; (' + dist[s].toLocaleString() + ')</button>'; });
    root.querySelector('.sfr-chips').innerHTML = chips;
  }
  function setFilter(f) {
    filter = f;
    Array.prototype.forEach.call(root.querySelectorAll('.sfr-chip'), function (c) { c.setAttribute('aria-pressed', String(c.getAttribute('data-sfr-filter') === f)); });
    paint(true);
  }
  function start(imported) {
    var nativeEl = root.querySelector('[data-sf-native-reviews]'), native = { reviews: [] };
    try { native = JSON.parse(nativeEl.textContent || '{}'); } catch (e) {}
    if (native.write) { var w = root.querySelector('.sfr-write'); w.href = native.write; w.hidden = false; }
    all = (native.reviews || []).map(function (r) { return { name: r.name, rating: +r.score || 0, title: r.title, body: r.body, date: (r.date || '').slice(0, 10), verified: false, photos: [] }; })
      .concat(imported && imported.reviews || []).filter(function (r) { return r.rating >= 1 && r.rating <= 5; });
    if (!all.length) return;
    root.hidden = false;
    summary(); paint(true);
  }
  root.addEventListener('click', function (e) {
    var f = e.target.closest('[data-sfr-filter]');
    if (f) { setFilter(f.getAttribute('data-sfr-filter')); return; }
    var z = e.target.closest('[data-sfr-zoom]');
    if (z) { var b = root.querySelector('.sfr-box'); b.querySelector('img').src = z.getAttribute('data-sfr-zoom'); b.hidden = false; return; }
    if (e.target.closest('.sfr-box button') || e.target.classList.contains('sfr-box')) { root.querySelector('.sfr-box').hidden = true; return; }
    if (e.target.closest('.sfr-more button')) { paint(false); return; }
    var m = e.target.closest('.sfr-more-text');
    if (m) { m.previousElementSibling.classList.remove('is-clamped'); m.remove(); }
  });
  root.querySelector('.sfr-sort').addEventListener('change', function (e) { sort = e.target.value; paint(true); });
  // the imported reviews load only when the wall comes near (hundreds of reviews cost nothing on page load)
  var loaded = false;
  function load() {
    if (loaded) return; loaded = true;
    var src = root.getAttribute('data-src');
    if (!src) return start(null);
    var s = document.createElement('script'); s.src = src; s.async = true;
    s.onload = function () { start(window.SFReviewsData || null); };
    s.onerror = function () { start(null); };
    document.head.appendChild(s);
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { if (es.some(function (x) { return x.isIntersecting; })) { io.disconnect(); load(); } }, { rootMargin: '800px 0px' });
    io.observe(sentinel);
  } else { load(); }
  if (/^#sf-reviews-all/.test(location.hash)) load();
})();
"""

def review_wall_html(data_src='', photos=None):
    """The wall's skeleton; the script fills it. data_src: the imported reviews' data script ('' = NEXT reviews only);
    photos: {photo name: page-relative path} (the theme build turns the paths into asset URLs)."""
    return (f'<div id="sf-review-wall-sentinel" aria-hidden="true" style="height:1px"></div>'
            f'<section class="sfr" id="sf-review-wall" data-src="{data_src}" hidden aria-labelledby="sfr-title"><style>{REVIEW_WALL_CSS}</style>'
            '<script type="application/json" data-sf-native-reviews>{"write": "", "reviews": []}</script>'
            f'<script type="application/json" data-sf-review-photos>{json.dumps(photos or {})}</script>'
            '<div class="sfr-wrap"><div class="sfr-top">'
            '<div><h2 id="sfr-title">Customer reviews</h2><div class="sfr-avg" data-sfr-avg></div><ul class="sfr-dist"></ul>'
            '<a class="sfr-write" href="#" hidden>Write a review</a></div>'
            '<div><div class="sfr-bar"><div class="sfr-chips"></div>'
            '<select class="sfr-sort" aria-label="Sort reviews"><option value="recent">Most recent</option><option value="high">Highest rated</option>'
            '<option value="low">Lowest rated</option><option value="photos">With photos first</option></select></div>'
            '<div class="sfr-list"></div><div class="sfr-more" hidden><button type="button">Show more reviews</button></div></div>'
            '</div></div>'
            '<div class="sfr-box" hidden role="dialog" aria-label="Review photo"><img alt=""><button type="button" aria-label="Close">&times;</button></div>'
            f'<script>{REVIEW_WALL_JS}</script></section>')
