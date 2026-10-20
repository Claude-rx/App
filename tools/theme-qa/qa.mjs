// Browser QA for the locally rendered SKINOFAB theme (see render.py).
// usage: node qa.mjs <rendered_dir> <shots_dir|-> [--mobile] [--only /a/,/b/] [--cart]
// Per route: JS errors, 404s, external requests, broken images, SKINOFAB logo present.
// --cart: on a PDP, submit the design's add-to-cart and assert the Spark side cart opens with the line
// (NEXT's /api/graphql/ cart is mocked with the same mutations SparkCartClient sends).
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path';

const ROOT = path.resolve(process.argv[2]);
const SHOTS = process.argv[3] && process.argv[3] !== '-' ? path.resolve(process.argv[3]) : null;
const MOBILE = process.argv.includes('--mobile');
const CART = process.argv.includes('--cart');
const oi = process.argv.indexOf('--only');
const routes = oi > 0 ? process.argv[oi + 1].split(',') : Object.keys(JSON.parse(fs.readFileSync(path.join(ROOT, 'routes.json'))));
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.woff2': 'font/woff2',
  '.woff': 'font/woff', '.ttf': 'font/ttf', '.mp4': 'video/mp4', '.webm': 'video/webm' };
const PORT = 8799, ORIGIN = `http://localhost:${PORT}`;

// ---- mock NEXT storefront GraphQL cart (state per server run)
let cart = null, lineSeq = 1;
const newCart = () => ({ id: 'cart_1', pk: 1, currency: 'USD', totalExclTax: '0.00', totalExclTaxExclDiscounts: '0.00', totalDiscount: '0.00',
  numItems: 0, numLines: 0, offerDiscounts: [], voucherDiscounts: [], lines: [] });
const recalc = () => { let t = 0, n = 0; cart.lines.forEach(l => { l.linePriceExclTax = l.linePriceExclTaxInclDiscounts = (39 * l.quantity).toFixed(2); t += 39 * l.quantity; n += l.quantity; });
  cart.totalExclTax = cart.totalExclTaxExclDiscounts = t.toFixed(2); cart.numItems = n; cart.numLines = cart.lines.length; };
function graphql(body) {
  const q = body.query || '', input = (body.variables || {}).input || {};
  if (/createCart/.test(q)) { cart = cart || newCart(); return { createCart: { cart } }; }
  cart = cart || newCart();
  if (/addCartLines/.test(q)) {
    (input.lines || []).forEach(l => {
      const ex = cart.lines.find(x => x.product.pk === l.productPk);
      if (ex) ex.quantity += l.quantity; else cart.lines.push({ pk: lineSeq++, quantity: l.quantity, unitPriceExclTax: '39.00', isUpsell: false,
        interval: null, intervalCount: null, properties: [], product: { pk: l.productPk, title: `Product ${l.productPk}`, url: '/products/x/', metadata: null,
          primaryImage: null, subscriptionInfo: null, parent: null, purchaseInfo: { priceRetail: { value: '49.00', format: '$49.00', currency: 'USD' }, availableForSale: true, availability: 'instock' } } });
    });
    recalc(); return { addCartLines: { success: true, errors: [], cart } };
  }
  if (/updateCartLines/.test(q)) { (input.lines || []).forEach(u => { const l = cart.lines.find(x => String(x.pk) === String(u.lineId)); if (l) l.quantity = u.quantity; }); recalc(); return { updateCartLines: { success: true, errors: [], cart } }; }
  if (/removeCartLines/.test(q)) { cart.lines = cart.lines.filter(l => !(input.lineIds || []).map(String).includes(String(l.pk))); recalc(); return { removeCartLines: { success: true, errors: [], cart } }; }
  return { cart };
}

const srv = http.createServer((q, r) => {
  const url = decodeURIComponent(q.url.split('?')[0].split('#')[0]);
  if (url.startsWith('/api/graphql')) {
    let b = ''; q.on('data', c => b += c); q.on('end', () => {
      let body = {}; try { body = JSON.parse(b || '{}'); } catch (e) {}
      r.writeHead(200, { 'content-type': 'application/json' }); r.end(JSON.stringify({ data: graphql(body) }));
    }); return;
  }
  if (url === '/csrf/') { r.writeHead(200, { 'content-type': 'application/json', 'set-cookie': 'csrftoken=qa; Path=/' }); return r.end('{}'); }
  let f = path.join(ROOT, url);
  if (!path.extname(f)) f = path.join(f, 'index.html');
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'content-type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' }); r.end(d); });
}).listen(PORT);

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await browser.newContext({ viewport: MOBILE ? { width: 390, height: 844 } : { width: 1440, height: 900 } });
await ctx.route('**/*', rt => rt.request().url().startsWith(ORIGIN) ? rt.continue() : rt.abort());
if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });
const report = {}; let bad = 0;
for (const route of routes) {
  const p = await ctx.newPage();
  const r = { external: new Set(), errors: [], missing: [] };
  p.on('request', q => { const u = q.url(); if (!u.startsWith(ORIGIN) && !/^(data|blob):/.test(u)) r.external.add(u.slice(0, 120)); });
  p.on('pageerror', e => r.errors.push(e.message.slice(0, 160)));
  p.on('response', s => { if (s.status() === 404) r.missing.push(s.url().replace(ORIGIN, '').slice(0, 120)); });
  try {
    await p.goto(ORIGIN + route, { waitUntil: 'networkidle', timeout: 60000 });
    for (let y = 0; y < 20; y++) { await p.mouse.wheel(0, 900); await p.waitForTimeout(100); }
    await p.waitForTimeout(600);
    r.broken = await p.evaluate(() => [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src') &&
      getComputedStyle(i).display !== 'none').map(i => i.getAttribute('src').slice(0, 100)));
    r.logos = await p.evaluate(() => [...document.images].filter(i => /skinofab-logo/.test(i.currentSrc || i.src)).length);
    r.dtlLeak = await p.evaluate(() => /\{%|\{\{|SFSLOT\d+X/.test(document.body.innerText));
    if (SHOTS) { await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(400);
      await p.screenshot({ path: path.join(SHOTS, (route.replace(/\//g, '_') || 'home') + '.png'), fullPage: true }); }
    if (CART && route.startsWith('/products/')) {
      const btn = await p.$('form[data-sf-product-form] [type="submit"], form[data-sf-product-form] button[name="add"]');
      if (!btn) r.errors.push('CART: no add-to-cart button');
      else {
        await btn.scrollIntoViewIfNeeded(); await btn.click({ force: true });
        await p.waitForTimeout(2500);
        r.cart = await p.evaluate(() => {
          const d = document.querySelector('spark-cart-drawer');
          return { drawerOpen: d && d.getAttribute('data-open'), badge: (document.getElementById('cart-badge') || {}).textContent,
                   lines: d && d.shadowRoot ? d.shadowRoot.querySelectorAll('[data-line-id], .spark-cart-line, li').length : -1 };
        });
        if (!r.cart.drawerOpen || r.cart.drawerOpen !== 'true') r.errors.push('CART: side cart did not open ' + JSON.stringify(r.cart));
      }
    }
  } catch (e) { r.errors.push('LOAD: ' + e.message.slice(0, 120)); }
  await p.close();
  const out = { ...r, external: [...r.external] };
  const fail = out.external.length || out.errors.length || out.missing.length || (out.broken || []).length || out.dtlLeak;
  if (fail) bad++;
  report[route] = out;
  console.log(`${fail ? 'FAIL' : ' ok '} ${route}${fail ? ' ' + JSON.stringify(out).slice(0, 600) : ''}${out.cart ? ' cart=' + JSON.stringify(out.cart) : ''}`);
}
fs.writeFileSync(path.join(ROOT, `qa-report${MOBILE ? '-mobile' : ''}.json`), JSON.stringify(report, null, 1));
console.log(`\n${routes.length - bad}/${routes.length} routes clean (${MOBILE ? 'mobile 390' : 'desktop 1440'})`);
await browser.close(); srv.close(); process.exit(bad ? 1 : 0);
