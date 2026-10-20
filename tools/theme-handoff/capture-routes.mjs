// Capture representative routes of the static export for the next-theme-design handoff package.
// usage: node capture-routes.mjs <export_dir> <package_dir> <capture-page.js> <design-package.py>
// For each route x width (1440x900, 768x1024, 390x844): derive section targets (one unique selector per
// section, plus its first visible heading and CTA), run capture-page.js in `static` state with preload_scroll,
// save the raw JSON and an unscaled full-page PNG, then file both with `design-package.py record`.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process';

const [ROOT, PKG, CAPTURE_JS, PKG_PY] = process.argv.slice(2).map(p => path.resolve(p));
export const ROUTES = [
  { route_id: 'home', file: 'index.html' },
  { route_id: 'pdp', file: 'products/color-changing-foundation.html' },
  { route_id: 'collection', file: 'collections/all.html' },
  { route_id: 'page-faq', file: 'pages/faq.html' },
  { route_id: 'policy-terms', file: 'pages/terms-of-service.html' },
  { route_id: 'article', file: 'blogs/news/color-changing-foundation-does-it-actually-work-the-science-explained.html' },
  { route_id: 'lander', file: 'pages/bestfoundation.html' },
];
const WIDTHS = [['desktop', 1440, 900], ['tablet', 768, 1024], ['mobile', 390, 844]];
const ONLY = process.env.ONLY ? process.env.ONLY.split(',') : null;
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.gif': 'image/gif', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.mp4': 'video/mp4' };
const PORT = 8790, ORIGIN = `http://localhost:${PORT}`;
const srv = http.createServer((q, r) => {
  const rel = decodeURIComponent(q.url.split('?')[0].split('#')[0]);
  const f = path.join(ROOT, rel === '/' ? 'index.html' : rel);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'content-type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' }); r.end(d); });
}).listen(PORT);

// Runs in the page: one target per section (chrome + main sections), each with heading/cta children.
function deriveTargets(routeId) {
  const uniq = el => {
    if (el.id && document.querySelectorAll('#' + CSS.escape(el.id)).length === 1) return '#' + CSS.escape(el.id);
    const parts = [];
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      if (n.id && document.querySelectorAll('#' + CSS.escape(n.id)).length === 1) { parts.unshift('#' + CSS.escape(n.id)); break; }
      const i = Array.prototype.indexOf.call(n.parentElement.children, n) + 1;
      parts.unshift(`${n.tagName.toLowerCase()}:nth-child(${i})`);
    }
    return parts.join(' > ');
  };
  const visible = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const key = (el, i) => {
    const raw = (el.id || '').split('__').pop() || `s${i}`;
    return `${routeId}.${raw.toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '') || 's' + i}`;
  };
  const sections = [];
  const ann = document.querySelector('[id$="__announcement-bar"]'); if (ann) sections.push(['announcement', ann]);
  const hdr = document.getElementById('SiteHeader'); if (hdr) sections.push(['header', hdr]);
  const main = document.getElementById('MainContent');
  let kids = main ? [...main.children] : [];
  // Page-builder landers wrap everything in one element: descend to the first level that has real siblings.
  for (let d = 0; d < 8 && kids.length > 0; d++) {
    const real = kids.filter(k => !['SCRIPT', 'STYLE', 'LINK'].includes(k.tagName) && visible(k));
    if (real.length !== 1) { kids = real.length ? real : kids; break; }
    kids = [...real[0].children];
  }
  kids.forEach((el, i) => { if (!['SCRIPT', 'STYLE', 'LINK'].includes(el.tagName)) sections.push([null, el, i]); });
  const ftr = document.querySelector('[id$="__footer"]'); if (ftr) sections.push(['footer', ftr]);
  const targets = [], seen = new Set();
  for (const [fixed, el, i] of sections) {
    if (!visible(el)) continue;
    let k = fixed ? `${routeId}.${fixed}` : key(el, i ?? 0);
    while (seen.has(k)) k += '-x'; seen.add(k);
    targets.push({ key: k, selector: uniq(el) });
    const h = [...el.querySelectorAll('h1,h2,h3')].find(visible);
    if (h && h.textContent.trim()) targets.push({ key: `${k}::heading`, selector: uniq(h) });
    const c = [...el.querySelectorAll('a.btn,button.btn,.btn,a.button,button[type=submit],[class*="button"]')].find(n => visible(n) && n.textContent.trim());
    if (c) targets.push({ key: `${k}::cta`, selector: uniq(c) });
  }
  return targets;
}

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--autoplay-policy=no-user-gesture-required'] });
const script = fs.readFileSync(CAPTURE_JS, 'utf8');
const RAW = path.join(PKG, 'captures', 'raw'); fs.mkdirSync(RAW, { recursive: true });
const TMP = path.join(PKG, '..', '.capture-tmp'); fs.mkdirSync(TMP, { recursive: true });
const allTargets = {};
for (const r of ROUTES) {
  if (ONLY && !ONLY.includes(r.route_id)) continue;
  for (const [vp, w, h] of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await ctx.route('**/*', rt => rt.request().url().startsWith(ORIGIN) ? rt.continue() : rt.abort());
    const page = await ctx.newPage();
    await page.goto(`${ORIGIN}/${r.file}`, { waitUntil: 'load', timeout: 90000 });
    await page.waitForTimeout(1500);
    const targets = await page.evaluate(deriveTargets, r.route_id);
    const id = `${r.route_id}-${vp}-static`;
    allTargets[id] = targets;
    await page.evaluate(o => { globalThis.NEXT_THEME_DESIGN_CAPTURE = o; },
      { capture_id: id, route_id: r.route_id, viewport: vp, state: 'static', preload_scroll: true, targets, wait_ms: 8000 });
    const raw = await page.evaluate(script);
    const rawFile = path.join(TMP, `${id}.json`), shot = path.join(TMP, `${id}.png`);
    fs.writeFileSync(rawFile, raw);
    await page.screenshot({ path: shot, fullPage: true, scale: 'device' });
    await ctx.close();
    const out = execFileSync('python3', [PKG_PY, 'record', '--package', PKG, '--raw', rawFile, '--screenshot', shot,
      '--screenshot-kind', 'full-page', '--tool', 'playwright-chromium-headless'], { encoding: 'utf8' });
    console.log(id, targets.length, 'targets |', out.trim().split('\n').pop());
  }
}
fs.writeFileSync(path.join(PKG, '..', '.capture-tmp', 'targets.json'), JSON.stringify(allTargets, null, 1));
await browser.close(); srv.close();
