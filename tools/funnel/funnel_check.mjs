// Load every funnel page in Chromium at phone and desktop width: console errors, failed requests, the SDK's state,
// the checkout's two pack cards and their prices, and full-page screenshots.
//
// usage: node tools/funnel/funnel_check.mjs <base-url> <out-dir> [--served]
//   <base-url>  http://127.0.0.1:8090 (Page Kit's _site, routes /stick-funnel/<page>/) or https://try.skinofab.com (live)
//   --served    the store's routes (/<page>/) instead of Page Kit's
// Exits 1 when a page has a console error, a failed same-site request or a checkout without its two priced packs.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs';

const [base, out] = process.argv.slice(2);
const served = process.argv.includes('--served');
const FILES = ['10-reasons-foundation-stick', 'foundation-stick-offer', 'stick-checkout', 'stick-special-1', 'stick-special-2',
  'stick-special-3', 'stick-special-4', 'stick-thank-you'];
const route = (f) => `${base}${served ? '/' : '/stick-funnel/'}${f}/`;
fs.mkdirSync(out, { recursive: true });

const proxy = process.env.HTTPS_PROXY && !base.includes('127.0.0.1') ? { server: process.env.HTTPS_PROXY } : undefined;
const browser = await chromium.launch({ proxy });
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
    try { await page.goto(route(f) + (f === 'stick-checkout' ? '?forceBundleId=stick-2' : ''), { waitUntil: 'load', timeout: 60000 }); }
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
        upsellPrice: (document.querySelector('[data-next-upsell="offer"] .upsell-offer__price, [data-next-upsell="offer"] [data-next-display$=".price"]') || {}).textContent,
        overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
        h: document.body.scrollHeight,
      };
    });
    await page.screenshot({ path: `${out}/${f}-${w}.png`, fullPage: true });
    // the same site's own requests only: third parties (fonts, analytics) are not this page's to fix
    const own = bad.filter((b) => b.includes(new URL(base).host) || b.includes('campaigns.apps.29next.com'));
    const row = { page: f, width: w, ms: Date.now() - t0, errors, bad: own, ...state };
    if (errors.length || own.length || state.overflowX || (f === 'stick-checkout' && (state.cards.length !== 2 || state.cards.some((c) => !/\$\d/.test(c.price || ''))))) {
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
