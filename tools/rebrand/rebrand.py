"""Rebrand an export from Smooche to SKINOFAB and move its palette to black and white.

usage: python3 -I rebrand.py <src_export> <dst_export>

- every file/dir name containing "smooch" is renamed (case-preserving: smooche->skinofab, Smooche->Skinofab,
  SMOOCHE->SKINOFAB; also Smooch/Smoochie/smooches), and the same replacement runs over every text file, so all
  references stay consistent (emails become hey@skinofab.com etc.)
- brand pinks become black, pink tints become neutral greys of the same lightness (hex, hex+alpha and rgb() forms);
  sale reds and payment-badge colours are left alone
- writes <dst>/rebrand-report.json (counts per replacement)
"""
import colorsys, json, os, re, shutil, sys
from collections import Counter
from pathlib import Path

SRC, DST = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
TEXT = {'.html', '.css', '.js', '.json', '.md', '.txt', '.xml', '.svg', '.webmanifest', '.liquid'}
BRAND = re.compile(r'smooch(?:ie|es|e)?', re.I)

def brand(m):
    s = m.group(0)
    if s.isupper(): return 'SKINOFAB'
    if s[0].isupper(): return 'Skinofab'
    return 'skinofab'

# brand pink family -> black; tints -> grey with the same lightness
TO_BLACK = ['df8096', 'df8195', '8096df', 'a94e63', '632c40', '8b1538', '8a3d50', 'c9295e', 'd91e63', 'b64a51', 'cd6471', 'ce7883', 'fb6c83']
TINTS = ['f8dce4', 'f9e5eb', 'f6ddea', 'fdf0f3', 'f5d7de', 'fbeaf0', 'f3e7ea', 'ffebee', 'f3cbcb', 'd8bdc5', 'ccabb1', 'cc949b', 'cc939b', 'd9939b', 'cb929a', 'f2a7b9', 'b17a88']
def grey(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255 for i in (0, 2, 4))
    _, l, _ = colorsys.rgb_to_hls(r, g, b)
    v = round(l * 255)
    return f'{v:02x}{v:02x}{v:02x}'
PAL = {h: '000000' for h in TO_BLACK} | {h: grey(h) for h in TINTS}
HEX = re.compile(r'#(' + '|'.join(PAL) + r')(?=[0-9a-f]{2}\b|\b)', re.I)
RGB = {(223, 128, 150): (0, 0, 0), (201, 41, 94): (0, 0, 0), (248, 220, 228): tuple(int(grey('f8dce4')[i:i + 2], 16) for i in (0, 2, 4))}
RGBRE = re.compile(r'(rgba?\(\s*)(\d+)(\s*,\s*)(\d+)(\s*,\s*)(\d+)', re.I)

stats = Counter()
def recolor(t):
    def h(m):
        stats['hex:' + m.group(1).lower()] += 1
        new = PAL[m.group(1).lower()]
        return '#' + (new.upper() if m.group(1).isupper() else new)
    t = HEX.sub(h, t)
    def r(m):
        k = (int(m.group(2)), int(m.group(4)), int(m.group(6)))
        if k not in RGB: return m.group(0)
        stats['rgb:%d,%d,%d' % k] += 1
        n = RGB[k]
        return f'{m.group(1)}{n[0]}{m.group(3)}{n[1]}{m.group(5)}{n[2]}'
    return RGBRE.sub(r, t)

if DST.exists(): shutil.rmtree(DST)
for d, dirs, files in os.walk(SRC):
    rel = Path(d).relative_to(SRC)
    out_dir = DST / BRAND.sub(brand, str(rel))
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        src = Path(d) / f
        name = BRAND.sub(brand, f)
        if name != f: stats['renamed files'] += 1
        dst = out_dir / name
        if src.suffix.lower() in TEXT:
            t = src.read_text(encoding='utf-8', errors='surrogateescape')
            n = len(BRAND.findall(t)); stats['brand text'] += n
            t = recolor(BRAND.sub(brand, t))
            dst.write_text(t, encoding='utf-8', errors='surrogateescape')
        else:
            os.link(src, dst) if os.stat(src).st_dev == os.stat(out_dir).st_dev else shutil.copy2(src, dst)
left = sum(len(BRAND.findall(p.read_text(errors='ignore'))) for p in DST.rglob('*') if p.is_file() and p.suffix.lower() in TEXT)
(DST / 'rebrand-report.json').write_text(json.dumps({'stats': dict(stats), 'brand_mentions_left': left}, indent=1))
print(json.dumps({'renamed': stats['renamed files'], 'brand_text': stats['brand text'], 'left': left,
                  'colours': sum(v for k, v in stats.items() if k.startswith(('hex', 'rgb')))}))
