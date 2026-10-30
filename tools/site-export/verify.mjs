// Offline QA for the static export: every page is loaded with ALL external network blocked.
// usage: node verify.mjs <export_dir> [shots_dir] [--mobile] [--only page.html,page.html]
// Reports per page: external requests attempted, JS errors, 404s, broken images, logo count. Exit 1 on any failure.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path';

const ROOT = path.resolve(process.argv[2]);
const SHOTS = process.argv[3] && !process.argv[3].startsWith('--') ? path.resolve(process.argv[3]) : null;
const MOBILE = process.argv.includes('--mobile');
const onlyIdx = process.argv.indexOf('--only');
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'export-manifest.json'), 'utf8'));
const pages = onlyIdx > 0 ? process.argv[onlyIdx + 1].split(',') : manifest.pages;
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.gif': 'image/gif', '.avif': 'image/avif', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf',
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime' };
const PORT = 8765, ORIGIN = `http://localhost:${PORT}`;
const srv = http.createServer((q, r) => {
  const rel = decodeURIComponent(q.url.split('?')[0].split('#')[0]);
  const f = path.join(ROOT, rel === '/' ? 'index.html' : rel);
  fs.readFile(f, (e, d) => {
    if (e) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'content-type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' }); r.end(d);
  });
}).listen(PORT);

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await browser.newContext({ viewport: MOBILE ? { width: 390, height: 844 } : { width: 1440, height: 900 } });
await ctx.route('**/*', rt => rt.request().url().startsWith(ORIGIN) ? rt.continue() : rt.abort());
if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });
const report = {}; let bad = 0;
for (const pg of pages) {
  const p = await ctx.newPage();
  const r = { external: new Set(), errors: [], missing: [] };
  p.on('request', q => { if (!q.url().startsWith(ORIGIN) && !q.url().startsWith('data:') && !q.url().startsWith('blob:')) r.external.add(q.url().slice(0, 120)); });
  p.on('pageerror', e => r.errors.push(e.message.slice(0, 160)));
  p.on('response', s => { if (s.status() === 404) r.missing.push(s.url().replace(ORIGIN, '')); });
  try {
    await p.goto(`${ORIGIN}/${pg}`, { waitUntil: 'networkidle', timeout: 60000 });
    for (let y = 0; y < 25; y++) { await p.mouse.wheel(0, 800); await p.waitForTimeout(120); }
    await p.waitForTimeout(800);
    r.broken = await p.evaluate(() => [...document.images]
      .filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src') && getComputedStyle(i).display !== 'none')
      .map(i => i.getAttribute('src').slice(0, 100)));
    r.logos = await p.evaluate(() => [...document.images].filter(i => /skinofab-logo/.test(i.currentSrc || i.src)).length);
    r.oldLogos = await p.evaluate(() => [...document.images].filter(i => /Smooche_LOGO/i.test(i.currentSrc || i.src)).length);
    if (SHOTS) { await p.evaluate(() => window.scrollTo(0, 0)); await p.screenshot({ path: path.join(SHOTS, pg.replace(/\//g, '__') + '.png'), fullPage: true }); }
  } catch (e) { r.errors.push('LOAD: ' + e.message.slice(0, 120)); }
  await p.close();
  const out = { ...r, external: [...r.external] };
  const fail = out.external.length || out.errors.length || out.missing.length || (out.broken || []).length || out.oldLogos;
  if (fail) bad++;
  report[pg] = out;
  console.log(`${fail ? 'FAIL' : ' ok '} ${pg}${fail ? ' ' + JSON.stringify(out) : ''}`);
}
fs.writeFileSync(path.join(ROOT, `qa-report${MOBILE ? '-mobile' : ''}.json`), JSON.stringify(report, null, 1));
console.log(`\n${pages.length - bad}/${pages.length} pages clean (${MOBILE ? 'mobile 390px' : 'desktop 1440px'})`);
await browser.close(); srv.close();
process.exit(bad ? 1 : 0);
