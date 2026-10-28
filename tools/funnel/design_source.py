"""The funnel's design source for Campaigns OS (campaigns/skinofab/design-source/): what each page was designed from,
with desktop and mobile screenshots as proof, and the source-html manifest that names them.

usage: [FUNNEL=stick|apf] python3 -I tools/funnel/design_source.py

Each funnel names its sources (funnels/<name>.py DESIGN_SOURCE: the folder, the pages designed from a capture, when each
was captured); the other pages are Apollo template stock (no bespoke design: the family's Template Reference covers
them), declared with a skip_reason.
  stick (design-source/): listicle facelove-listicle.html, the owner's other brand's listicle, captured from
        https://facelove-cosmetics.com/pages/10-reasons-why-foundating-stick-2026-new (27 Oct 2026, 1440 x 900 and
        390 x 844 full-page Chromium captures); offer stick-pdp.html, the store's own Adaptive Foundation Stick page
  apf (design-source-apf/): listicle the same Facelove capture; offer apf-pdp.html, the store's own Adaptive Peptide
        Foundation page (28 Oct 2026), captured in 4000 px parts and stitched where Chromium refused one capture

The screenshots are kept as JPEG (quality 80) under .campaigns-os/screenshots/; this writes their hashes and sizes
into .campaigns-os/source-html-manifest.json. Re-run after replacing a capture.
"""
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funnel as F

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'campaigns' / 'skinofab' / F.DESIGN_SOURCE['dir']
SHOTS = SRC / '.campaigns-os' / 'screenshots'
CAPTURED = F.DESIGN_SOURCE['captured']                      # by page id
BROWSER = 'playwright-chromium/1194'
DESIGNED = F.DESIGN_SOURCE['designed']
VIEWPORTS = {'desktop': (1440, 'desktop-1440x900'), 'mobile': (390, 'mobile-390x844')}


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def shot(page_id, viewport):
    png, jpg = SHOTS / f'{page_id}-{viewport}.png', SHOTS / f'{page_id}-{viewport}.jpg'
    if png.exists():                                  # keep the repository light: the PNG capture as a JPEG
        Image.open(png).convert('RGB').save(jpg, quality=80, optimize=True, progressive=True)
        png.unlink()
    w, h = Image.open(jpg).size
    return {'id': f'source-{page_id}-{viewport}', 'kind': 'source_screenshot', 'viewport': viewport, 'availability': 'available',
            'path': jpg.relative_to(SRC).as_posix(), 'sha256': sha(jpg), 'width': w, 'height': h,
            'device_profile': VIEWPORTS[viewport][1], 'browser': BROWSER, 'captured_at': CAPTURED[page_id]}


pages = []
for pg in F.PAGES:
    if pg['id'] in DESIGNED:
        html = SRC / DESIGNED[pg['id']]
        pages.append({'page_id': pg['id'], 'path': html.name, 'source_hash': sha(html),
                      'screenshots': [shot(pg['id'], v) for v in VIEWPORTS]})
    else:
        pages.append({'page_id': pg['id'], 'skip_reason': f'template stock: Apollo {pg["sdk"]} page, no bespoke design'})
manifest = {'schema_version': 'source-html-manifest/v0', 'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'generator': 'tools/funnel/design_source.py@1', 'campaign_slug': F.SLUG,
            'wrapper_policy': 'preserve_document_wrappers', 'pages': pages}
(SRC / '.campaigns-os' / 'source-html-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'{len(pages)} pages, {sum(len(p.get("screenshots", [])) for p in pages)} screenshots')
