const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const URL_ = 'https://sofyre.com/products/mouse-repellent-pouches';
const OUT = process.argv[2];
const A = path.join(OUT, 'assets');
fs.mkdirSync(A, { recursive: true });

const cache = new Map(); // url -> {buf, type}
const extFor = (u, t='') => {
  const m = new URL(u).pathname.match(/\.([a-z0-9]{2,5})$/i);
  if (m) return m[1].toLowerCase();
  if (t.includes('css')) return 'css'; if (t.includes('svg')) return 'svg';
  if (t.includes('webp')) return 'webp'; if (t.includes('png')) return 'png';
  if (t.includes('jpeg')) return 'jpg'; if (t.includes('gif')) return 'gif';
  if (t.includes('woff2')) return 'woff2'; if (t.includes('woff')) return 'woff';
  if (t.includes('mp4')) return 'mp4'; return 'bin';
};
const local = new Map(); // url -> relative path
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage();
  p.on('response', async r => {
    const rt = r.request().resourceType();
    if (!['image','font','stylesheet','media'].includes(rt)) return;
    try { const buf = await r.body(); if (buf.length) cache.set(r.url(), { buf, type: r.headers()['content-type'] || '' }); } catch {}
  });
  await p.goto(URL_, { waitUntil: 'networkidle', timeout: 90000 }).catch(()=>{});
  // force lazy assets
  await p.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager'));
  for (let pass = 0; pass < 2; pass++) {
    await p.evaluate(async () => { for (let y=0; y<document.body.scrollHeight; y+=400){ window.scrollTo(0,y); await new Promise(r=>setTimeout(r,120)); } window.scrollTo(0,0); });
    await p.waitForTimeout(2500);
  }
  await p.waitForLoadState('networkidle').catch(()=>{});

  // Copy (text) for copy.md
  const copy = await p.evaluate(() => {
    const out = []; const seen = new Set();
    const walk = el => {
      if (!el || ['SCRIPT','STYLE','NOSCRIPT','SVG','TEMPLATE'].includes(el.tagName)) return;
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
      const tag = el.tagName;
      if (/^H[1-6]$/.test(tag) || ['P','LI','BUTTON','A','SUMMARY','LABEL','SPAN','DIV','TD','TH','BLOCKQUOTE'].includes(tag)) {
        const hasBlockKids = [...el.children].some(c => ['DIV','P','UL','OL','H1','H2','H3','H4','H5','H6','SECTION','LI','TABLE'].includes(c.tagName));
        if (!hasBlockKids || /^H[1-6]$/.test(tag) || tag==='P' || tag==='LI') {
          const t = el.innerText.replace(/\s+/g,' ').trim();
          if (t && !seen.has(t)) { seen.add(t);
            out.push(/^H[1-6]$/.test(tag) ? '\n' + '#'.repeat(+tag[1]) + ' ' + t + '\n' : tag==='LI' ? '- ' + t : t); }
          if (!hasBlockKids) return;
        }
      }
      for (const c of el.children) walk(c);
      if (el.shadowRoot) for (const c of el.shadowRoot.children) walk(c);
    };
    walk(document.body);
    return out.join('\n');
  });
  const imgs = await p.evaluate(() => [...document.images].filter(i=>i.currentSrc).map(i => `- ${i.alt || '(no alt)'} — ${i.currentSrc}`));

  // Snapshot DOM, freeze images to the variant actually shown
  const snap = await p.evaluate(() => {
    document.querySelectorAll('[type="text/disabled-css"]').forEach(e => e.removeAttribute('type'));
    document.querySelectorAll('link[media="print"][onload]').forEach(e => { e.media = 'all'; e.removeAttribute('onload'); });
    document.querySelectorAll('.gps-lazy').forEach(e => e.classList.remove('gps-lazy'));
    [...document.querySelectorAll('body *')].forEach(e => { const c = getComputedStyle(e);
      if (c.position === 'fixed' && c.display !== 'none' && c.visibility !== 'hidden' && +c.opacity > 0) {
        const r = e.getBoundingClientRect(); if (r.width * r.height > innerWidth * innerHeight * 0.25) e.remove(); } });
    document.querySelectorAll('img[id^=batBeacon], [id^=batBeacon], #web-pixels-manager-sandbox-container, #fv-loading-icon').forEach(e => e.remove());
    document.body.style.overflow = ''; document.documentElement.style.overflow = '';
    document.body.classList.remove('overflow-hidden', 'modal-open');
    document.querySelectorAll('img').forEach(i => {
      const s = i.currentSrc || i.src || i.dataset.src; if (s) i.setAttribute('src', s);
      i.removeAttribute('srcset'); i.removeAttribute('data-srcset'); i.removeAttribute('sizes'); i.removeAttribute('loading');
    });
    document.querySelectorAll('picture source').forEach(s => s.remove());
    document.querySelectorAll('video source, video').forEach(v => { if (v.src) v.setAttribute('src', v.src); });
    document.querySelectorAll('script:not([type="application/ld+json"])').forEach(s => s.remove());
    document.querySelectorAll('link[rel=preload],link[rel=prefetch],link[rel=preconnect],link[rel=dns-prefetch],link[rel=modulepreload]').forEach(l => l.remove());
    document.querySelectorAll('iframe').forEach(f => { if (!/youtube|vimeo/.test(f.src)) f.remove(); });
    // absolutize every URL attribute
    const abs = u => { try { return new URL(u, location.href).href; } catch { return u; } };
    document.querySelectorAll('[src]').forEach(e => e.setAttribute('src', abs(e.getAttribute('src'))));
    document.querySelectorAll('link[href]').forEach(e => e.setAttribute('href', abs(e.getAttribute('href'))));
    document.querySelectorAll('[poster]').forEach(e => e.setAttribute('poster', abs(e.getAttribute('poster'))));
    // capture adopted/dynamic stylesheets not in DOM
    const extra = [];
    for (const sh of document.styleSheets) { if (!sh.ownerNode) try { extra.push([...sh.cssRules].map(r=>r.cssText).join('\n')); } catch {} }
    if (extra.length) { const st = document.createElement('style'); st.textContent = extra.join('\n'); document.head.append(st); }
    return '<!doctype html>\n' + document.documentElement.outerHTML;
  });

  const fetchBuf = async u => {
    if (cache.has(u)) return cache.get(u);
    try { const r = await ctx.request.get(u, { timeout: 30000 }); if (r.ok()) { const v = { buf: await r.body(), type: r.headers()['content-type']||'' }; cache.set(u, v); return v; } } catch {}
    return null;
  };
  const failed = [];
  const save = async (u, prefix) => {
    if (local.has(u)) return local.get(u);
    const v = await fetchBuf(u); if (!v) { failed.push(u); return null; }
    const base = path.basename(new URL(u).pathname).replace(/\.[^.]+$/,'').replace(/[^\w-]/g,'').slice(0,50) || 'asset';
    const name = `${base}-${crypto.createHash('md5').update(u).digest('hex').slice(0,6)}.${extFor(u, v.type)}`;
    let buf = v.buf;
    if (extFor(u, v.type) === 'css') buf = Buffer.from(await rewriteCss(buf.toString(), u, ''));
    fs.writeFileSync(path.join(A, name), buf);
    local.set(u, prefix + name); return prefix + name;
  };
  // CSS url() rewriting; prefix = path from the css file's location to assets/
  const rewriteCss = async (css, baseUrl, prefix) => {
    const urls = new Set();
    css.replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, (_, q, u) => { if (!u.startsWith('data:') && !u.startsWith('#')) urls.add(u); });
    css.replace(/@import\s+(['"])([^'"]+)\1/g, (_, q, u) => urls.add(u));
    const map = {};
    for (const u of urls) { let a; try { a = new URL(u.replace(/&amp;/g,'&'), baseUrl).href; } catch { continue; } const l = await save(a, ''); if (l) map[u] = prefix + l; }
    return css.replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, (m, q, u) => map[u] ? `url("${map[u]}")` : m)
              .replace(/@import\s+(['"])([^'"]+)\1/g, (m, q, u) => map[u] ? `@import "${map[u]}"` : m);
  };

  let html = snap;
  const dec = s => s.replace(/&amp;/g, '&');
  // stylesheets
  for (const m of [...html.matchAll(/<link\b[^>]*rel="stylesheet"[^>]*>/g)]) {
    const h = (m[0].match(/href="([^"]+)"/)||[])[1]; if (!h) continue;
    const l = await save(dec(h), 'assets/'); if (l) html = html.split(m[0]).join(m[0].replace(h, l));
  }
  // <style> blocks & style="" attributes
  const styleBlocks = [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/g)];
  for (const m of styleBlocks) html = html.split(m[1]).join(await rewriteCss(m[1], URL_, 'assets/'));
  for (const m of [...new Set([...html.matchAll(/style="([^"]*url\([^"]*)"/g)].map(x=>x[1]))]) {
    const css = m.replace(/&quot;/g, '"');
    html = html.split(`style="${m}"`).join(`style="${(await rewriteCss(css, URL_, 'assets/')).replace(/"/g, "'")}"`);
  }
  // src / poster / icons
  for (const m of [...new Set([...html.matchAll(/\b(?:src|poster)="(https?:[^"]+)"/g)].map(x=>x[1]))]) {
    if (/youtube|vimeo/.test(m)) continue;
    const l = await save(dec(m), 'assets/'); if (l) html = html.split(`"${m}"`).join(`"${l}"`);
  }
  for (const m of [...html.matchAll(/<link\b[^>]*rel="(?:icon|shortcut icon|apple-touch-icon)"[^>]*>/g)]) {
    const h = (m[0].match(/href="([^"]+)"/)||[])[1]; if (!h) continue;
    const l = await save(dec(h), 'assets/'); if (l) html = html.split(m[0]).join(m[0].replace(h, l));
  }
  // in-svg/inline <image href>
  for (const m of [...new Set([...html.matchAll(/<image\b[^>]*href="(https?:[^"]+)"/g)].map(x=>x[1]))]) {
    const l = await save(dec(m), 'assets/'); if (l) html = html.split(`"${m}"`).join(`"${l}"`);
  }
  html = html.replace(/<base\b[^>]*>/g, '');
  html = html.replace('<head>', '<head><meta charset="utf-8"><!-- Offline snapshot of ' + URL_ + ' taken ' + new Date().toISOString() + ' -->');
  fs.writeFileSync(path.join(OUT, 'index.html'), html);
  fs.writeFileSync(path.join(OUT, 'copy.md'), `# Page copy — ${URL_}\n\n${copy}\n\n---\n## Images on page (alt — source)\n\n${imgs.join('\n')}\n`);
  fs.writeFileSync(path.join(OUT, 'failed-assets.txt'), failed.join('\n'));
  console.log('assets', local.size, 'failed', failed.length);
  await b.close();
})();
