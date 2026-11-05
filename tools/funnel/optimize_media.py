"""Phones get small WebP copies of the funnel's large photos, and the ad landing pages their stylesheets inline (speed
pass, 5 Nov 2026: AppLovin counted far more outbound clicks than visitors; the pages were too slow on a phone).

usage: python3 -I tools/funnel/optimize_media.py <built Page Kit site dir> [...]      e.g. campaigns/skinofab/_site/apf-funnel

Runs on the Page Kit build (_site/<slug>/), before deploy_theme.py turns it into theme templates. For every lazy-loaded
<img> whose src is one of the funnel's own JPEG or PNG photos, at least MIN_WIDTH wide and without a srcset of its own, it
writes WebP copies beside the file (<name>-w480.webp, -w800.webp and one at the photo's own width, never wider than
1080) and gives the <img> a srcset of them with sizes: the browser picks the smallest copy that fills the slot on that
screen, and the original file stays the src (a browser without WebP keeps it). An image above the fold (no
loading="lazy") is left as it is: the hero has its own phone copy and preload. The copies are made only when missing or
older than their source (encoded once per source file, cached in .work/media-cache by its hash), so a rebuild writes
the same bytes and the theme push sends nothing new.

The ad landing pages (base-sf.html: <body class="sf ...">, the sales page and the listicle) get their own stylesheets
inline: on the store their CSS comes from the store's CDN, another host, and the first paint waited for that connection
(about 0.45 s on slow 4G). Each <link rel="stylesheet"> to the funnel's own css/ becomes a <style> with the same rules,
its url()s made absolute (/<slug>/fonts/..., which deploy_theme.py then points at the theme's assets).
"""
import hashlib, re, shutil, sys
from pathlib import Path
from PIL import Image

CACHE = Path(__file__).resolve().parents[2] / '.work' / 'media-cache'   # encoded copies by source hash (not committed)

MIN_WIDTH = 300          # smaller pictures (icons, gift thumbnails, avatars) stay as they are
WIDTHS = (480, 800)      # plus the photo's own width, at most 1080
QUALITY = 78
SIZES = '(max-width: 599px) 92vw, 540px'
IMG = re.compile(r'<img\b[^>]*>')


def copies(site, rel):
    """The WebP copies of one photo, made if missing: [(published path, width)]."""
    src = site / rel
    with Image.open(src) as im:
        w0 = im.width
        out = []
        key = hashlib.sha1(src.read_bytes()).hexdigest()[:16]
        for w in sorted({*(w for w in WIDTHS if w < w0), min(w0, 1080)}):
            dst = src.with_name(f'{src.stem}-w{w}.webp')
            cached = CACHE / f'{key}-q{QUALITY}-w{w}.webp'
            if not cached.is_file():
                CACHE.mkdir(parents=True, exist_ok=True)
                img = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
                if w != w0: img = img.resize((w, round(im.height * w / w0)), Image.LANCZOS)
                img.save(cached, 'WEBP', quality=QUALITY, method=6)
            if not dst.is_file(): shutil.copyfile(cached, dst)
            out.append((dst.relative_to(site).as_posix(), w))
        return out


LINK = re.compile(r'<link rel="stylesheet" href="/([\w-]+)/(css/[\w.-]+\.css)">')
CSS_URL = re.compile(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)')


def inline_css(site, html_text):
    """A landing page's own stylesheets as <style> blocks (only on base-sf.html pages)."""
    if '<body class="sf ' not in html_text: return html_text, 0
    n = 0
    def sub(m):
        nonlocal n
        slug, rel = m.group(1), m.group(2)
        if slug != site.name or not (site / rel).is_file(): return m.group(0)
        css = (site / rel).read_text(encoding='utf-8')
        def absolute(u):
            q, url = u.group(1), u.group(2)
            if url.startswith(('data:', 'http:', 'https:', '//', '#', '/')): return u.group(0)
            path = ((site / rel).parent / url).resolve().relative_to(site.resolve()).as_posix()
            return f'url({q}/{slug}/{path}{q})'
        css = CSS_URL.sub(absolute, css)
        if '</style' in css: return m.group(0)
        n += 1
        return f'<style data-sf-inline="{rel}">{css}</style>'
    return LINK.sub(sub, html_text), n


def run(site):
    site = Path(site).resolve()
    slug = site.name
    pages = changed = made = inlined = 0
    for html in site.rglob('index.html'):
        text = html.read_text(encoding='utf-8')
        def sub(m):
            nonlocal changed, made
            tag = m.group(0)
            if 'srcset=' in tag or 'loading="lazy"' not in tag: return tag
            s = re.search(r'\bsrc="/' + re.escape(slug) + r'/([^"]+\.(?:jpe?g|png))"', tag, re.I)
            w = re.search(r'\bwidth="(\d+)"', tag)
            if not s or not (site / s.group(1)).is_file() or (w and int(w.group(1)) < MIN_WIDTH): return tag
            with Image.open(site / s.group(1)) as im:
                if im.width < MIN_WIDTH: return tag
            cs = copies(site, s.group(1)); made += len(cs); changed += 1
            srcset = ', '.join(f'/{slug}/{p} {w}w' for p, w in cs)
            return tag[:-1].rstrip('/').rstrip() + f' srcset="{srcset}" sizes="{SIZES}">'
        new = IMG.sub(sub, text)
        new, k = inline_css(site, new); inlined += k
        if new != text:
            html.write_text(new, encoding='utf-8'); pages += 1
    print(f'optimize_media: {slug}: {changed} photos on {pages} pages get WebP copies ({made} files); {inlined} stylesheets inlined')


if __name__ == '__main__':
    for d in sys.argv[1:]: run(d)
