"""Get Rid Of brand kit: logo, mark, app / favicon icons and a line-icon pack, as SVG + PNG, zipped.

    python3 -I tools/brand/getridof_brand_kit.py <out-dir>

Writes <out-dir>/GetRidOf-Brand-Kit/ and <out-dir>/GetRidOf-Brand-Kit.zip. Sources: the logo files used on the store
(campaigns/getridof/src/mouse-pouches/assets/pdp/gro-logo*.svg) and the icons drawn below (24 px grid, 1.75 px round
strokes, currentColor). PNGs are rendered by Chromium (tools/brand/render_svgs.cjs), the .ico by Pillow.
Icon labels only use claims the funnel already makes (no "safe", no results promised)."""
import json, re, shutil, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
LOGO_DARK = ROOT / 'campaigns/getridof/src/mouse-pouches/assets/pdp/gro-logo.svg'
LOGO_WHITE = ROOT / 'campaigns/getridof/src/mouse-pouches/assets/pdp/gro-logo-white.svg'
RENDER = Path(__file__).resolve().parent / 'render_svgs.cjs'

COLORS = {   # from the store's CSS (lp.css :root) and the logo
    'Ink': '#141414', 'Forest': '#23372B', 'Night': '#16261C', 'Leaf': '#7EA254', 'Action green': '#2F7D1E',
    'Lime': '#CCF46F', 'Signal red': '#D62839', 'Mist': '#F3F6EE', 'White': '#FFFFFF'}
FOREST, LIME, RED, NIGHT = COLORS['Forest'], COLORS['Lime'], COLORS['Signal red'], COLORS['Night']

# ---- the mark: the logo's red "no entry" O on its own (same proportions as in the wordmark) ----
def mark_svg(color=RED, bg=None, pad=0.0, size=64):
    s = size
    r_out = s / 2 * (1 - pad)
    k = r_out / 32.752          # logo: r 26.542 + half stroke 6.21
    c = s / 2
    r, sw, lw, d = 26.542 * k, 12.42 * k, 10.12 * k, 17.894 * k
    bgr = f'<rect width="{s}" height="{s}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}">{bgr}'
            f'<circle cx="{c:.3f}" cy="{c:.3f}" r="{r:.3f}" fill="none" stroke="{color}" stroke-width="{sw:.3f}"/>'
            f'<line x1="{c - d:.3f}" y1="{c - d:.3f}" x2="{c + d:.3f}" y2="{c + d:.3f}" stroke="{color}" stroke-width="{lw:.3f}"/></svg>')

# ---- line icons (24 x 24, stroke currentColor) ----
ICONS = [
    ('no-poison', 'No poison', 'No poison, no rodenticide',
     '<path d="M9.5 3h5M10.5 3v5.2L6.3 16a3 3 0 0 0 2.6 4.5h6.2a3 3 0 0 0 2.6-4.5l-4.2-7.8V3"/><path d="M8.3 14h7.4"/><path d="M3.5 3.5l17 17"/>'),
    ('plant-oils', '4 plant oils', 'Peppermint, cinnamon, cedarwood and castor oil',
     '<path d="M5 19.5C5 11 10.5 5.5 19.5 4.5 19.5 13 14 18.5 5 19.5z"/><path d="M5 19.5l8.5-8.5"/><path d="M9.5 15.2V12M12.5 12.3V9.7"/>'),
    ('peppermint', 'Peppermint', 'Job 1: the strong mint scent',
     '<path d="M12 21v-9.5"/><path d="M12 13.5C8 13.5 5.5 11 5.5 7.5c3.6 0 6.5 2.4 6.5 6z"/><path d="M12 11.5c0-3.8 2.6-6.5 6.5-6.5 0 3.8-2.7 6.5-6.5 6.5z"/><path d="M12 17.5c-1.8 0-3.2-1-3.7-2.6M12 16c1.6 0 2.9-.9 3.4-2.3"/>'),
    ('cinnamon', 'Cinnamon', 'Job 2: covers the scent trail',
     '<g transform="rotate(-30 12 12)"><rect x="2.5" y="6.6" width="19" height="4.4" rx="2.2"/><rect x="2.5" y="13" width="19" height="4.4" rx="2.2"/><path d="M19.3 8.8a.9.9 0 1 0-.9.9M19.3 15.2a.9.9 0 1 0-.9.9"/></g>'),
    ('cedarwood', 'Cedarwood', 'Job 3: spoils the nesting spots',
     '<path d="M12 3l-5 6.2h3L6 14.5h4L6.5 19.5h11L14 14.5h4l-4-5.3h3z"/><path d="M12 19.5V22"/>'),
    ('castor-oil', 'Castor oil', 'Job 4: slows the scent down',
     '<path d="M12 3c3.2 4.3 6 7.8 6 11.2a6 6 0 0 1-12 0C6 10.8 8.8 7.3 12 3z"/><path d="M9.2 14.6a2.8 2.8 0 0 0 2.8 2.8"/>'),
    ('pouch', '12 pouches', '12 pouches in every pack',
     '<path d="M6 8l1.5-1.5L9 8l1.5-1.5L12 8l1.5-1.5L15 8l1.5-1.5L18 8"/><path d="M6 8v11a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8"/><path d="M10 17c0-2.6 1.6-4.2 4.2-4.2 0 2.6-1.6 4.2-4.2 4.2z"/>'),
    ('way-in', 'At the way in', 'Goes where mice come in',
     '<path d="M6 21V4.2A1.2 1.2 0 0 1 7.2 3h9.6A1.2 1.2 0 0 1 18 4.2V21"/><path d="M3 21h18"/><circle cx="14.8" cy="12" r=".9" fill="currentColor" stroke="none"/><rect x="8.2" y="16.8" width="4.2" height="4.2" rx=".9"/>'),
    ('lasts-90-days', 'Up to 90 days', 'Each pouch is made to last up to 90 days',
     '<path d="M7 3h10M7 21h10"/><path d="M8 3c0 4.5 4 6.2 4 9s-4 4.5-4 9M16 3c0 4.5-4 6.2-4 9s4 4.5 4 9"/><path d="M9.6 18.5h4.8"/>'),
    ('guarantee', '90-day guarantee', 'Full refund if mice haven\'t left within 90 days',
     '<path d="M12 3l7.5 3v5.2c0 4.8-3.1 8.4-7.5 9.8-4.4-1.4-7.5-5-7.5-9.8V6z"/><path d="M8.8 12.2l2.2 2.2 4.3-4.4"/>'),
    ('free-shipping', 'Free US shipping', 'Free shipping on every US order',
     '<path d="M2.5 6.5h11v9h-11z"/><path d="M13.5 9.5h4l3.5 3.8v2.2h-7.5"/><circle cx="6.5" cy="17" r="1.9"/><circle cx="17" cy="17" r="1.9"/>'),
    ('refills', 'Skip or cancel anytime', 'Subscribe & Save refills',
     '<path d="M19.5 12a7.5 7.5 0 0 1-12.9 5.2M4.5 12a7.5 7.5 0 0 1 12.9-5.2"/><path d="M17.8 3.2v3.9h-3.9M6.2 20.8v-3.9h3.9"/>'),
    ('secure-checkout', 'Secure checkout', 'Encrypted payment',
     '<rect x="5" y="10.5" width="14" height="10.5" rx="2"/><path d="M8.2 10.5V7.8a3.8 3.8 0 0 1 7.6 0v2.7"/><path d="M12 14.5v2.5"/>'),
    ('whole-home', 'Whole home', 'One pack per zone',
     '<path d="M3 11.2L12 4l9 7.2"/><path d="M5.2 9.6V20h13.6V9.6"/><path d="M10 20v-5.2h4V20"/>'),
    ('garage-rv', 'Garage, RV & shed', 'Vehicles and storage too',
     '<path d="M3 17V7.2A1.2 1.2 0 0 1 4.2 6H15a5 5 0 0 1 5 5v6z"/><path d="M14.5 6v5.5H20"/><rect x="5.5" y="8.5" width="5.5" height="3" rx=".6"/><circle cx="7.5" cy="17.6" r="1.9"/><circle cx="16.3" cy="17.6" r="1.9"/>'),
    ('no-traps', 'No traps to empty', 'Nothing to set, check or clean up',
     '<rect x="3" y="13.5" width="18" height="6" rx="1.2"/><path d="M7 13.5V9h10v4.5"/><circle cx="12" cy="16.5" r="1"/><path d="M3.5 3.5l17 17"/>'),
    ('pets', 'No poison for pets', 'Nothing poisonous for the dog to find',
     '<circle cx="6.6" cy="10.4" r="1.7"/><circle cx="10" cy="6.8" r="1.7"/><circle cx="14" cy="6.8" r="1.7"/><circle cx="17.4" cy="10.4" r="1.7"/><path d="M12 12.2c-2.5 0-5 3-5 5.3 0 1.5 1.1 2.3 2.4 2.3 1.1 0 1.6-.6 2.6-.6s1.5.6 2.6.6c1.3 0 2.4-.8 2.4-2.3 0-2.3-2.5-5.3-5-5.3z"/>'),
    ('mouse-free', 'Mouse repellent', 'Keeps mice from settling in',
     '<path d="M3.5 17.5c.4-4.4 3.8-7.5 8.2-7.5 4.2 0 7.3 2.7 8.3 6.6l.9.9H3.5z"/><circle cx="15.8" cy="9.2" r="2.1"/><path d="M3.5 17.5c-.9.4-1.3 1.3-1 2.2"/><path d="M3 3l18 18"/>'),
]


def icon_svg(body, color='currentColor', size=24):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{body.replace("currentColor", color)}</svg>')


def badge_svg(body, fg, bg, size=96):
    """The icon in a filled circle (for social / marketplace badges)."""
    inner = re.sub(r'<svg[^>]*>|</svg>', '', icon_svg(body, fg))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}">'
            f'<circle cx="12" cy="12" r="12" fill="{bg}"/><g transform="translate(4.8 4.8) scale(.6)" fill="none" stroke="{fg}" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{inner}</g></svg>')


def main(out):
    out = Path(out)
    kit = out / 'GetRidOf-Brand-Kit'
    if kit.exists(): shutil.rmtree(kit)
    jobs = []   # (svg text, png path, width, height or None, transparent)
    def svg_file(rel, text):
        p = kit / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text); return p
    def png(svg_text, rel, w, h=None, transparent=True):
        p = kit / rel; p.parent.mkdir(parents=True, exist_ok=True); jobs.append({'svg': svg_text, 'out': str(p), 'w': w, 'h': h, 'transparent': transparent})

    # 1. logo
    dark, white = LOGO_DARK.read_text(), LOGO_WHITE.read_text()
    svg_file('01-logo/svg/getridof-logo-dark.svg', dark)
    svg_file('01-logo/svg/getridof-logo-white.svg', white)
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', dark).group(1).split()]
    ratio = vb[3] / vb[2]
    for w in (600, 1200, 2400):
        png(dark, f'01-logo/png/getridof-logo-dark-{w}w.png', w, round(w * ratio))
        png(white, f'01-logo/png/getridof-logo-white-{w}w.png', w, round(w * ratio))
    # padded versions on solid backgrounds (email headers, marketplaces, documents)
    for name, src, bg in (('on-white', dark, '#FFFFFF'), ('on-forest', white, NIGHT)):
        inner = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', src.strip())
        W, H = vb[2] * 1.3, vb[3] * 2.2
        boxed = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}"><rect width="100%" height="100%" fill="{bg}"/>'
                 f'<g transform="translate({vb[2] * .15:.1f} {vb[3] * .6:.1f})">{inner}</g></svg>')
        svg_file(f'01-logo/svg/getridof-logo-{name}.svg', boxed)
        png(boxed, f'01-logo/png/getridof-logo-{name}-1600w.png', 1600, round(1600 * H / W), False)

    # 2. mark (the red no-entry O)
    svg_file('02-mark/svg/getridof-mark-red.svg', mark_svg(RED))
    svg_file('02-mark/svg/getridof-mark-white.svg', mark_svg('#FFFFFF'))
    svg_file('02-mark/svg/getridof-mark-forest.svg', mark_svg(FOREST))
    for s in (64, 256, 512, 1024):
        png(mark_svg(RED), f'02-mark/png/getridof-mark-red-{s}.png', s, s)
        png(mark_svg('#FFFFFF'), f'02-mark/png/getridof-mark-white-{s}.png', s, s)

    # 3. app icons, favicons, social profile picture
    on_white = mark_svg(RED, '#FFFFFF', pad=0.22)
    maskable = mark_svg(RED, '#FFFFFF', pad=0.38)          # inside the 80 % safe zone
    svg_file('03-app-icons/favicon.svg', mark_svg(RED))
    for s in (16, 32, 48):
        png(mark_svg(RED), f'03-app-icons/favicon-{s}x{s}.png', s, s)
    png(on_white, '03-app-icons/apple-touch-icon.png', 180, 180, False)
    png(on_white, '03-app-icons/android-chrome-192x192.png', 192, 192, False)
    png(on_white, '03-app-icons/android-chrome-512x512.png', 512, 512, False)
    png(maskable, '03-app-icons/maskable-512x512.png', 512, 512, False)
    profile = mark_svg(RED, '#FFFFFF', pad=0.34)           # survives round crops (TikTok, Facebook, Instagram)
    png(profile, '03-app-icons/social-profile-1024.png', 1024, 1024, False)
    (kit / '03-app-icons/site.webmanifest').write_text(json.dumps({
        'name': 'Get Rid Of', 'short_name': 'Get Rid Of', 'theme_color': FOREST, 'background_color': '#FFFFFF', 'display': 'standalone',
        'icons': [{'src': '/android-chrome-192x192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': '/android-chrome-512x512.png', 'sizes': '512x512', 'type': 'image/png'},
                  {'src': '/maskable-512x512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]}, indent=2) + '\n')
    (kit / '03-app-icons/head-tags.html').write_text(
        '<link rel="icon" href="/favicon.ico" sizes="any">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n'
        f'<meta name="theme-color" content="{FOREST}">\n')

    # 4. icon pack
    meta = []
    for slug, label, note, body in ICONS:
        svg_file(f'04-icons/svg/{slug}.svg', icon_svg(body))
        svg_file(f'04-icons/svg-badge/{slug}-badge.svg', badge_svg(body, FOREST, LIME))
        png(icon_svg(body, FOREST), f'04-icons/png-forest/{slug}.png', 256, 256)
        png(icon_svg(body, '#FFFFFF'), f'04-icons/png-white/{slug}.png', 256, 256)
        png(badge_svg(body, FOREST, LIME), f'04-icons/png-badge/{slug}-badge.png', 256, 256)
        meta.append({'file': slug, 'label': label, 'use_for': note})
    (kit / '04-icons/icons.json').write_text(json.dumps(meta, indent=2) + '\n')

    # 5. preview sheet
    cells = ''.join(f'<div class="c"><div class="i">{icon_svg(b, FOREST, 44)}</div><b>{l}</b><small>{s}.svg</small></div>' for s, l, n, b in ICONS)
    sw = ''.join(f'<div class="sw"><span style="background:{v}"></span><b>{k}</b><small>{v}</small></div>' for k, v in COLORS.items())
    sheet = f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;font:15px/1.4 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1b241d;background:#fff;width:1400px}}
.hd{{display:flex;gap:28px;align-items:center;padding:36px 48px;border-bottom:1px solid #dfe6d6}} .hd svg{{height:56px;width:auto}}
.dk{{background:{NIGHT};padding:18px 26px;border-radius:12px}} .mk svg{{width:64px;height:64px}}
h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#5b665d;margin:28px 48px 12px}}
.g{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;padding:0 48px}} .c{{border:1px solid #dfe6d6;border-radius:12px;padding:16px 10px;text-align:center}}
.c b{{display:block;font-size:14px;margin-top:8px}} .c small{{color:#8a948c;font-size:11.5px}}
.s{{display:flex;flex-wrap:wrap;gap:12px;padding:0 48px 40px}} .sw{{width:140px}} .sw span{{display:block;height:56px;border-radius:10px;border:1px solid #dfe6d6}}
.sw b{{display:block;font-size:13px;margin-top:6px}} .sw small{{color:#5b665d}}
</style></head><body><div class="hd">{dark}<div class="dk">{white}</div><div class="mk">{mark_svg(RED)}</div></div>
<h2>Icon pack · 24 px line icons</h2><div class="g">{cells}</div><h2>Colours</h2><div class="s">{sw}</div></body></html>'''
    (out / 'preview.html').write_text(sheet)
    jobs.append({'html': str(out / 'preview.html'), 'out': str(kit / 'preview.png'), 'w': 1400})

    (out / 'jobs.json').write_text(json.dumps(jobs))
    subprocess.run(['node', str(RENDER), str(out / 'jobs.json')], check=True, cwd='/tmp')
    (out / 'jobs.json').unlink(); (out / 'preview.html').unlink()

    ico = Image.open(kit / '03-app-icons/favicon-48x48.png')
    ico.save(kit / '03-app-icons/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])

    (kit / 'README.md').write_text(readme(meta))
    z = out / 'GetRidOf-Brand-Kit.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(kit.rglob('*')):
            if p.is_file(): zf.write(p, p.relative_to(out))
    n = sum(1 for p in kit.rglob('*') if p.is_file())
    print(f'wrote {z} ({z.stat().st_size // 1024} KB, {n} files)')


def readme(meta):
    rows = '\n'.join(f'| `{m["file"]}` | {m["label"]} | {m["use_for"]} |' for m in meta)
    cols = '\n'.join(f'| {k} | `{v}` |' for k, v in COLORS.items())
    return f'''# Get Rid Of — brand kit

## 01-logo
- `svg/getridof-logo-dark.svg` — on white or light backgrounds. `svg/getridof-logo-white.svg` — on dark backgrounds or photos.
- `png/` — transparent PNGs 600 / 1200 / 2400 px wide, and `getridof-logo-on-white` / `-on-forest` with their background.
- Keep clear space of at least the height of the red "O" on every side. Don't recolour the red, stretch or outline it.

## 02-mark
The red no-entry "O" from the logo, on its own: for small spaces where the full name won't fit. Red, white and forest
versions; PNG 64–1024 px.

## 03-app-icons
Favicons (`favicon.ico`, `favicon.svg`, 16 / 32 / 48 px), `apple-touch-icon.png` (180), Android 192 / 512, a maskable
512, `site.webmanifest` and `head-tags.html` (the lines to paste in a page's `<head>`). `social-profile-1024.png` is
padded so it survives the round crop on TikTok, Facebook and Instagram.

## 04-icons
18 line icons on a 24 px grid, 1.75 px round strokes.
- `svg/` — `currentColor`: they take the text colour of where you put them. Best at 20–48 px.
- `png-forest/`, `png-white/` — 256 px transparent PNGs. `svg-badge/`, `png-badge/` — forest icon on a lime circle.
- `icons.json` — the label and use of each.

| File | Label | Use for |
|---|---|---|
{rows}

The labels match claims the store already makes. Keep it that way in ads: no "safe", no promised results ("gone in
3 days"), and the guarantee as "full refund if mice haven't left within 90 days".

## Colours
| Name | Hex |
|---|---|
{cols}

Forest / Night for text and dark backgrounds, Lime for highlights and badges, Action green for buttons, Signal red only
for the mark.
'''


if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(sys.argv[1])
