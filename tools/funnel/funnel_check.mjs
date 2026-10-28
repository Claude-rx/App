// Load every funnel page in Chromium at phone and desktop width: console errors, failed requests, the SDK's state,
// the checkout's two pack cards and their prices, and full-page screenshots.
//
// usage: [FUNNEL=stick|apf] [ORDER_REF=<ref_id>] node tools/funnel/funnel_check.mjs <base-url> <out-dir> [--served]
//   <base-url>  http://127.0.0.1:8090 (Page Kit's _site, routes /<slug>/<page>/) or https://try.skinofab.com (live)
//   --served    the store's routes (/<page>/) instead of Page Kit's
//   FUNNEL      which funnel's pages (tools/funnel/funnels/<name>.py): stick (default) or apf
//   ORDER_REF   an order's ref_id to open the offer and thank-you pages with (their order.* displays and the offer gate
//               then run as they do for a buyer); without it those pages show their fallbacks
// Exits 1 when a page has a console error, a failed same-site request or a checkout without its priced packs.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs';

const [base, out] = process.argv.slice(2);
const served = process.argv.includes('--served');
const FUNNELS = {
  stick: { slug: 'stick-funnel', checkout: 'stick-checkout', bundle: 'stick-2', cards: 2,
    files: ['10-reasons-foundation-stick', 'foundation-stick-offer', 'stick-checkout', 'stick-special-1', 'stick-special-2',
      'stick-special-3', 'stick-special-4', 'stick-thank-you'] },
  apf: { slug: 'apf-funnel', checkout: 'foundation-checkout', bundle: 'apf-2', cards: 3,
    files: ['10-reasons-adaptive-foundation', 'adaptive-foundation-offer', 'foundation-checkout', 'foundation-offer-1',
      'foundation-offer-2', 'foundation-offer-2b', 'lymphatic-brush-offer', 'lymphatic-brush-offer-b', 'foundation-thank-you'] },
};
const FN = FUNNELS[process.env.FUNNEL || 'stick'];
const FILES = FN.files;
const ref = process.env.ORDER_REF || '';
// the pages after the checkout (offers, thank you) take the order's reference
const query = (f) => f === FN.checkout ? `?forceBundleId=${FN.bundle}` : (ref && FILES.indexOf(f) > FILES.indexOf(FN.checkout) ? `?ref_id=${ref}` : '');
const route = (f) => `${base}${served ? '/' : '/' + FN.slug + '/'}${f}/`;
fs.mkdirSync(out, { recursive: true });

const proxy = process.env.HTTPS_PROXY && !base.includes('127.0.0.1') ? { server: process.env.HTTPS_PROXY } : undefined;
// a capture, tried up to three times: Chromium refuses one now and then while a page's videos are being decoded
const shot = async (page, opts, tries = 3) => {
  for (let t = 1; ; t++) {
    try { return await page.screenshot({ animations: 'disabled', ...opts }); }
    catch (e) { if (t >= tries) throw e; await page.waitForTimeout(1000); }
  }
};
const browser = await chromium.launch({ proxy, args: ['--disable-dev-shm-usage'] });
let failed = false;
const report = [];
for (const f of FILES) {
  for (const [w, h] of [[390, 844], [1440, 900]]) {
    // a shopper's locale: the container's own (en-US@posix) is one Intl rejects, which the SDK's price formatter throws on
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, ignoreHTTPSErrors: true, locale: 'en-US', timezoneId: 'America/New_York' });
    const page = await ctx.newPage();
    const errors = [], bad = [];
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text().slice(0, 240)); });
    page.on('pageerror', (e) => errors.push('pageerror: ' + String(e).slice(0, 240)));
    page.on('response', (r) => { if (r.status() >= 400) bad.push(`${r.status()} ${r.url().slice(0, 160)}`); });
    page.on('requestfailed', (r) => r.failure()?.errorText === 'net::ERR_ABORTED' || bad.push(`failed ${r.failure()?.errorText} ${r.url().slice(0, 160)}`));
    const t0 = Date.now();
    try { await page.goto(route(f) + query(f), { waitUntil: 'load', timeout: 60000 }); }
    catch (e) { errors.push('goto: ' + e.message.slice(0, 160)); }
    await page.waitForTimeout(3000);
    // scroll through once so lazy images load before the full-page screenshot
    const H = await page.evaluate(() => document.body.scrollHeight);
    for (let y = 0; y < H; y += 600) { await page.evaluate((y) => window.scrollTo(0, y), y); await page.waitForTimeout(90); }
    await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(1200);
    const state = await page.evaluate(() => {
      const q = (s) => Array.from(document.querySelectorAll(s));
      return {
        sdk: !!window.next, version: window.next && (window.next.version || (window.next.getVersion && window.next.getVersion())),
        wide: Array.from(document.querySelectorAll('body *')).filter((e) => e.getBoundingClientRect().right > window.innerWidth + 1).slice(0, 5).map((e) => e.tagName + '.' + String(e.className).slice(0, 40)),
        title: document.title,
        cards: q('[data-next-bundle-card]').filter((c) => !c.closest('[data-next-upsell-context]') && c.offsetParent).map((c) => ({
          id: c.getAttribute('data-next-bundle-id'), selected: c.classList.contains('next-selected'),
          price: (c.querySelector('[data-next-bundle-display="price"]') || {}).textContent,
          name: (c.querySelector('[data-next-display="package.name"]') || {}).textContent })),
        upsellPrice: (document.querySelector('[data-next-upsell="offer"] .upsell-offer__price, [data-next-upsell="offer"] [data-next-display$=".price"], [data-next-upsell="offer"] [data-next-bundle-display="price"]') || {}).textContent,
        offerCards: q('[data-next-upsell="offer"] [data-next-bundle-card]').filter((c) => c.offsetParent).map((c) => ({
          id: c.getAttribute('data-next-bundle-id'), selected: c.classList.contains('next-selected'),
          price: (c.querySelector('[data-next-bundle-display="price"]') || {}).textContent })),
        orderNumber: (document.querySelector('[data-next-display="order.number"]') || {}).textContent,
        overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
        h: document.body.scrollHeight,
      };
    });
    // the lazy loops are paused for the capture; a capture Chromium refuses (its raster limit, which the long pages
    // reach on a phone) is taken in 6000 px parts instead
    await page.evaluate(() => document.querySelectorAll('video').forEach((v) => { v.pause(); v.removeAttribute('autoplay'); }));
    await page.waitForTimeout(500);
    try { await shot(page, { path: `${out}/${f}-${w}.png`, fullPage: true }); }
    catch (e) {
      const H2 = await page.evaluate(() => document.documentElement.scrollHeight);
      for (let y = 0, n = 1; y < H2; y += 6000, n++) {
        await shot(page, { path: `${out}/${f}-${w}-part${String(n).padStart(2, '0')}.png`, fullPage: true, clip: { x: 0, y, width: w, height: Math.min(6000, H2 - y) } });
      }
    }
    // the same site's own requests only: third parties (fonts, analytics) are not this page's to fix
    const own = bad.filter((b) => b.includes(new URL(base).host) || b.includes('campaigns.apps.29next.com'));
    const row = { page: f, width: w, ms: Date.now() - t0, errors, bad: own, ...state };
    if (errors.length || own.length || state.overflowX || (f === FN.checkout && (state.cards.length !== FN.cards || state.cards.some((c) => !/\$\d/.test(c.price || ''))))) {
      failed = true; row.fail = true;
    }
    report.push(row);
    console.log(JSON.stringify(row));
    await ctx.close();
  }
}
await browser.close();
fs.writeFileSync(`${out}/report.json`, JSON.stringify(report, null, 2));
process.exit(failed ? 1 : 0);
