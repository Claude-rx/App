// Add to cart speed, live: click the product page's Add to Cart (fresh visitor, no cart) and time, from the click
// event, when the side cart shows the product (pending line), starts sliding in, is fully open, and shows the real
// cart line from the server. Desktop, then a throttled phone (4x CPU, 1.6 Mbps, 150 ms latency).
//
// usage: node atc-timing.mjs <store_url> <theme_id> [product paths...]
// Fails (exit 1) when the drawer starts opening later than 300 ms (desktop) / 600 ms (phone) after the click, or the
// cart line never arrives. The server's answer (createCart, ~0.7-1.8 s) is reported, not gated: it is NEXT's.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';

const [STORE, THEME, ...ROUTES] = process.argv.slice(2);
if (!STORE || !THEME) { console.error('usage: node atc-timing.mjs <store_url> <theme_id> [product paths...]'); process.exit(2); }
const routes = ROUTES.length ? ROUTES : ['/catalogue/adaptive-peptide-foundation_14/', '/catalogue/the-lymphatic-brush_169/'];
const Q = '?preview_theme=' + THEME, LIMIT = { desktop: 300, phone: 600 };
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const rows = [], bad = [];
for (const route of routes) for (const device of ['desktop', 'phone']) {
  const phone = device === 'phone';
  const ctx = await b.newContext(phone ? { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } : { viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage();
  await p.goto(STORE + '/' + Q, { waitUntil: 'domcontentloaded' });            // sets the preview theme cookie
  if (phone) {
    const cdp = await ctx.newCDPSession(p);
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6e6 / 8, uploadThroughput: 750e3 / 8 });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  }
  await p.goto(STORE + route + Q, { waitUntil: 'load', timeout: 180000 });
  await p.waitForTimeout(phone ? 6000 : 2500);                                    // a shopper reads before buying
  const warm = await p.evaluate(() => !!window.SparkSideCart);
  const btn = await p.$('form[data-product-form] [data-add-to-cart]');
  if (!btn) { bad.push(`${route} ${device}: no Add to Cart button`); await ctx.close(); continue; }
  await btn.scrollIntoViewIfNeeded();
  await p.evaluate(() => {
    const t = {}; window.__atc = t;
    window.addEventListener('click', () => {
      t.start = performance.now();
      (function tick() {
        const d = document.querySelector('spark-cart-drawer'), r = d && d.shadowRoot, now = Math.round(performance.now() - t.start);
        const panel = r && r.querySelector('.spark-drawer-panel'), box = panel && panel.getBoundingClientRect();
        if (r && t.pending == null && r.querySelector('.sf-pending')) t.pending = now;
        if (box && t.opening == null && box.left < innerWidth - 2) t.opening = now;
        if (box && t.open == null && Math.abs(box.right - innerWidth) < 2 && box.left < innerWidth - 300) t.open = now;
        if (r && t.line == null && r.querySelector('.spark-drawer-item')) t.line = now;
        if ((t.line == null || t.open == null) && now < 20000) requestAnimationFrame(tick);
      })();
    }, { capture: true, once: true });
  });
  await (phone ? btn.tap() : btn.click());
  await p.waitForFunction(() => window.__atc.line != null && window.__atc.open != null, null, { timeout: 25000 }).catch(() => {});
  const t = await p.evaluate(() => window.__atc);
  rows.push({ route, device, warm, pending: t.pending, opening: t.opening, open: t.open, line: t.line });
  if (t.opening == null || t.opening > LIMIT[device]) bad.push(`${route} ${device}: drawer started opening at ${t.opening} ms (limit ${LIMIT[device]})`);
  if (t.line == null) bad.push(`${route} ${device}: the cart line never arrived`);
  await ctx.close();
}
await b.close();
console.log('product'.padEnd(44) + 'device   ready  product shown  opening  fully open  cart line (server)');
for (const r of rows) console.log(r.route.padEnd(44) + r.device.padEnd(9) + String(r.warm).padEnd(7) +
  `${r.pending} ms`.padEnd(15) + `${r.opening} ms`.padEnd(9) + `${r.open} ms`.padEnd(12) + `${r.line} ms`);
if (bad.length) { console.error('FAIL\n- ' + bad.join('\n- ')); process.exit(1); }
console.log('ok');
