// Run next-theme-dev's assert-geometry gate against the locally rendered theme.
// usage: node geometry.mjs <rendered_dir> <handoff_dir> <assert-geometry.mjs> <out_dir>
// The theme keeps the design markup, so each geometry entry's build hook is its source selector.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process';

const [ROOT, PKG, ASSERT, OUT] = process.argv.slice(2).map(p => path.resolve(p));
const URLS = { home: '/', pdp: '/products/color-changing-foundation/', collection: '/catalogue/', 'page-faq': '/faq/',
  'policy-terms': '/terms-of-service/', article: '/blog/post/', lander: '/bestfoundation/' };
const WIDTHS = { desktop: [1440, 900], tablet: [768, 1024], mobile: [390, 844] };
fs.mkdirSync(OUT, { recursive: true });

// hooks: build selector = source selector
const geoFile = path.join(PKG, 'geometry.json');
const geo = JSON.parse(fs.readFileSync(geoFile, 'utf8'));
for (const r of geo.routes) for (const v of Object.values(r.viewports)) for (const s of v.sections) {
  s.selector = s.source_selector || s.selector;
  for (const e of s.elements || []) e.selector = e.source_selector || e.selector;
}
fs.writeFileSync(geoFile, JSON.stringify(geo, null, 2) + '\n');

const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.woff2': 'font/woff2', '.mp4': 'video/mp4' };
const PORT = 8798, ORIGIN = `http://localhost:${PORT}`;
const srv = http.createServer((q, r) => {
  const url = decodeURIComponent(q.url.split('?')[0]);
  if (url.startsWith('/api/') || url === '/csrf/') { r.writeHead(200, { 'content-type': 'application/json' }); return r.end('{"data":{}}'); }
  let f = path.join(ROOT, url); if (!path.extname(f)) f = path.join(f, 'index.html');
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': TYPES[path.extname(f)] || '' }); r.end(d); });
}).listen(PORT);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const summary = [];
for (const r of geo.routes) {
  for (const vp of Object.keys(r.viewports)) {
    const [w, h] = WIDTHS[vp];
    const probe = path.join(OUT, `probe-${r.route_id}-${vp}.js`);
    execFileSync('node', [ASSERT, 'probe', '--manifest', geoFile, '--route', r.route_id, '--viewport', vp, '--out', probe]);
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await ctx.route('**/*', rt => rt.request().url().startsWith(ORIGIN) ? rt.continue() : rt.abort());
    const page = await ctx.newPage();
    await page.goto(ORIGIN + URLS[r.route_id], { waitUntil: 'load', timeout: 90000 });
    await page.waitForTimeout(1500);
    for (let y = 0; y < 30; y++) { await page.mouse.wheel(0, 900); await page.waitForTimeout(80); }
    await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(800);
    const boxes = await page.evaluate(fs.readFileSync(probe, 'utf8'));
    const boxFile = path.join(OUT, `boxes-${r.route_id}-${vp}.json`);
    fs.writeFileSync(boxFile, typeof boxes === 'string' ? boxes : JSON.stringify(boxes));
    await ctx.close();
    const rep = path.join(OUT, `report-${r.route_id}-${vp}.json`);
    let out = '';
    try { out = execFileSync('node', [ASSERT, 'compare', '--manifest', geoFile, '--route', r.route_id, '--viewport', vp, '--boxes', boxFile, '--report', rep], { encoding: 'utf8' }); }
    catch (e) { out = (e.stdout || '') + (e.stderr || ''); }
    const last = out.trim().split('\n').filter(Boolean).pop() || '';
    summary.push(`${r.route_id}/${vp}: ${last}`);
    console.log(`${r.route_id}/${vp}: ${last}`);
  }
}
fs.writeFileSync(path.join(OUT, 'summary.txt'), summary.join('\n') + '\n');
await browser.close(); srv.close();
