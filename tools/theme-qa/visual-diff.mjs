// Pixel comparison of two locally rendered copies of the theme (render.py output): before vs after a change.
// usage: node visual-diff.mjs <before_dir> <after_dir> <out_dir> [--routes /,/products/x/] [--widths 390,1440]
// Each route is captured full-page in both copies at each width, with animations and transitions frozen and
// every lazy image scrolled into view. diff.py (same folder) then scores the pairs and writes highlighted diffs.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path';

const [BEFORE, AFTER, OUT] = process.argv.slice(2).map(p => path.resolve(p));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const ROUTES = arg('--routes', '/,/products/color-changing-foundation/,/catalogue/,/contact/,/faq/,/cart/').split(',');
const WIDTHS = arg('--widths', '390,1440').split(',').map(Number);
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.woff2': 'font/woff2',
  '.woff': 'font/woff', '.ttf': 'font/ttf', '.mp4': 'video/mp4' };
fs.mkdirSync(OUT, { recursive: true });

function serve(root, port) {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      let p = decodeURIComponent(req.url.split('?')[0]);
      if (p.startsWith('/api/')) { rsp.writeHead(200, { 'Content-Type': 'application/json' }); return rsp.end('{"data":{}}'); }
      let f = path.join(root, p);
      if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
      if (!fs.existsSync(f)) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(rsp);
    }).listen(port, () => res(srv));
  });
}

const servers = [await serve(BEFORE, 8811), await serve(AFTER, 8812)];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const FREEZE = '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}';
for (const w of WIDTHS) {
  const ctx = await browser.newContext({ viewport: { width: w, height: w < 800 ? 844 : 900 }, deviceScaleFactor: 1 });
  for (const route of ROUTES) {
    for (const [tag, port] of [['before', 8811], ['after', 8812]]) {
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(String(e.message).slice(0, 160)));
      await page.goto(`http://localhost:${port}${route}`, { waitUntil: 'load', timeout: 90000 }).catch(e => errors.push('goto ' + e.message));
      await page.addStyleTag({ content: FREEZE }).catch(() => {});
      const h = await page.evaluate(() => document.documentElement.scrollHeight).catch(() => 0);
      for (let y = 0; y < Math.min(h, 12000); y += 700) { await page.evaluate(v => window.scrollTo(0, v), y); await page.waitForTimeout(60); }
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(1200);
      const name = `${route.replace(/\//g, '_') || '_'}-${w}-${tag}.png`;
      await page.screenshot({ path: path.join(OUT, name), fullPage: true, clip: undefined, timeout: 60000 }).catch(e => errors.push('shot ' + e.message));
      fs.writeFileSync(path.join(OUT, name.replace('.png', '.errors.json')), JSON.stringify(errors));
      await page.close();
    }
    console.log('captured', route, w);
  }
  await ctx.close();
}
await browser.close();
servers.forEach(s => s.close());
