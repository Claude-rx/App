// One real test order through the live funnel: the checkout with NEXT's test card (no charge, no transaction; the
// order is flagged as a test and lands in the store, to be cancelled), then each special offer accepted or declined,
// then the thank-you page's lines, renewals and total.
//
// usage: node tools/funnel/live_order.mjs <host> <out-dir> [--path accept,decline,accept,decline] [--pack stick-2]
//   <host>   https://try.skinofab.com (the funnel's host: the domain the campaign allows)
//   --path   what to do on special offers 1-4, in order (default accept,decline,accept,decline)
//   --pack   the checkout card to buy (default stick-2)
//   --resume <ref_id> [--start N]  skip the checkout: walk the offers of an order already placed, from offer N
// Writes a screenshot per step and order.json (order number, lines, renewals, total) to <out-dir>; exits 1 when a step
// does not arrive where the funnel routes it.
//
// Campaigns OS's own `qa run` places these orders on a local build; it cannot yet on the store's host, where the funnel
// is served at the site root (/<page>/) rather than under its Page Kit slug.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs';

const [host, out] = process.argv.slice(2);
const opt = (name, dflt) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : dflt; };
const path = opt('--path', 'accept,decline,accept,decline').split(',');
const pack = opt('--pack', 'stick-2');
const resume = opt('--resume', null);                  // an order's ref_id: start on a special offer with it
const start = Number(opt('--start', '1'));             // with --resume: the special offer to start on (1-4)
const CARD = '6011111111111117', CVV = '123';          // NEXT's test card (as Campaigns OS's QA uses)
const ADDRESS = { fname: 'Quinn', lname: 'Tester', email: 'qa-live@skinofab.test', address1: '1600 Amphitheatre Pkwy',
  city: 'Mountain View', province: 'CA', postal: '94043' };
fs.mkdirSync(out, { recursive: true });

const browser = await chromium.launch({ proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'en-US', ignoreHTTPSErrors: true });
const page = await ctx.newPage();
const errors = [];
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text().slice(0, 200)); });
const log = [];
const step = async (name, fn) => {
  const t0 = Date.now();
  try { await fn(); log.push({ step: name, ok: true, ms: Date.now() - t0, url: page.url() }); }
  catch (e) { log.push({ step: name, ok: false, error: String(e.message || e).slice(0, 300), url: page.url() }); throw e; }
  finally { await page.screenshot({ path: `${out}/${String(log.length).padStart(2, '0')}-${name}.png` }).catch(() => {}); }
};
const field = (name) => page.locator(`[data-next-checkout-field="${name}"]:visible`).first();
// typed like a shopper and tabbed out of: the SDK validates on its own input and blur events (an instant fill() leaves
// "Enter a first name" on a filled field)
const fill = async (name, value) => {
  const f = field(name); await f.waitFor({ timeout: 20000 });
  await f.click(); await f.fill(''); await f.pressSequentially(value, { delay: 20 }); await f.press('Tab');
};
const select = async (name, value) => { const f = field(name); await f.waitFor({ timeout: 20000 }); await f.selectOption(value); };
const arrive = async (file) => page.waitForURL(new RegExp(`/${file}/`), { timeout: 90000 });

let result = { host, pack, path };
try {
  if (!resume) {
  await step('checkout', async () => {
    await page.goto(`${host}/stick-checkout/?forceBundleId=${pack}`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction(() => [...document.querySelectorAll('[data-next-bundle-card] .bundle-card__price-total')]
      .some((e) => /\$\d/.test(e.textContent)), null, { timeout: 30000 });
  });
  await step('details', async () => {
    await fill('fname', ADDRESS.fname); await fill('lname', ADDRESS.lname); await fill('email', ADDRESS.email);
    await select('country', 'US');
    await fill('address1', ADDRESS.address1);
    await page.keyboard.press('Escape');                 // close the address suggestions
    await page.waitForTimeout(800);
    await fill('city', ADDRESS.city); await select('province', ADDRESS.province); await fill('postal', ADDRESS.postal);
  });
  await step('card', async () => {
    await page.locator('[data-next-payment-method="credit"], #combo_mode_credit').first().click({ force: true }).catch(() => {});
    await select('exp-month', '12');
    const years = await field('exp-year').locator('option').evaluateAll((o) => o.map((x) => x.value).filter(Boolean));
    await select('exp-year', years.includes('2030') ? '2030' : years[years.length - 1]);
    await page.waitForFunction(() => !document.querySelector('.next-loading-spreedly'), null, { timeout: 45000 });
    const num = page.frameLocator('iframe[id^="spreedly-number-frame"], iframe[id^="spreedly-hosted-number"]').locator('input').first();
    const cvv = page.frameLocator('iframe[id^="spreedly-cvv-frame"], iframe[id^="spreedly-hosted-cvv"]').locator('input').first();
    await num.click(); await num.pressSequentially(CARD, { delay: 25 });
    await cvv.click(); await cvv.pressSequentially(CVV, { delay: 25 });
    await page.locator('body').click({ position: { x: 10, y: 10 } });
    result.checkout_total = (await page.locator('[data-next-display="cart.total"]').first().textContent())?.trim();
  });
  await step('place-order', async () => {
    await page.locator('#combo_form button[type="submit"]').first().click();
    try { await arrive('stick-special-1'); }
    catch (e) {
      // what stopped it: the form's visible messages, by field
      result.name_fields = await page.evaluate(() => [...document.querySelectorAll('[data-next-checkout-field="fname"], [data-next-checkout-field="lname"], input[name="first_name"], input[name="fname"]')]
        .map((e) => ({ field: e.getAttribute('data-next-checkout-field'), name: e.name, id: e.id, visible: !!e.offsetParent, value: e.value, cls: e.className.slice(0, 80) })));
      result.form_errors = await page.evaluate(() => [...document.querySelectorAll('#combo_form *')]
        .filter((el) => el.children.length === 0 && el.offsetParent && /error|invalid/i.test(el.className + ' ' + (el.getAttribute('role') || '')) && el.textContent.trim())
        .map((el) => el.textContent.trim().slice(0, 120)).slice(0, 12));
      await page.screenshot({ path: `${out}/place-order-full.png`, fullPage: true });
      throw e;
    }
  });
  } else {
    await step('resume', async () => { await page.goto(`${host}/stick-special-${start}/?ref_id=${resume}`, { waitUntil: 'load', timeout: 60000 }); });
  }
  result.ref_id = new URL(page.url()).searchParams.get('ref_id');
  const files = ['stick-special-1', 'stick-special-2', 'stick-special-3', 'stick-special-4', 'stick-thank-you'];
  result.offers = [];
  for (let i = resume ? start - 1 : 0; i < 4; i++) {
    const action = path[i] === 'accept' ? 'add' : 'skip';
    await step(`offer-${i + 1}-${path[i]}`, async () => {
      // the SDK has the order (sf-offer-gate's field is filled) before its offer actions answer a click
      await page.waitForFunction(() => (document.querySelector('[data-sf-upsell-ok]')?.textContent || '').trim(), null, { timeout: 45000 });
      await page.waitForTimeout(1500);
      const price = (await page.locator('[data-next-upsell="offer"] .upsell-offer__price:not(.diagonal-strike)').first().textContent().catch(() => ''))?.trim();
      result.offers.push({ offer: i + 1, action: path[i], shown_price: price });
      // (the accept button pulses, so it is never "stable" to Playwright: the element's own click)
      await page.locator(`[data-next-upsell="offer"] [data-next-upsell-action="${action}"]:visible`).first().evaluate((el) => el.click());
      await arrive(files[i + 1]);
    });
  }
  await step('thank-you', async () => {
    await page.waitForSelector('[data-order-line-id]', { timeout: 30000 });
    await page.waitForTimeout(2000);
    Object.assign(result, await page.evaluate(() => ({
      order_number: document.querySelector('[data-next-display="order.number"]')?.textContent.trim(),
      lines: [...document.querySelectorAll('.summary-desktop [data-order-line-id]')]       // (the desktop summary; the phone one repeats it)
       
        .slice(0, 8).map((l) => ({ name: l.querySelector('.cart-item__title')?.textContent.trim(),
          renew: l.querySelector('.sf-line-renew')?.textContent.trim(), total: l.querySelector('.checkout__line-item__final-price')?.textContent.trim() })),
      order_total: document.querySelector('.order-totals__value--total')?.textContent.trim(),
    })));
  });
  result.ok = true;
} catch (e) {
  result.ok = false;
}
result.steps = log;
result.console_errors = errors.slice(0, 10);
fs.writeFileSync(`${out}/order.json`, JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
await browser.close();
process.exit(result.ok ? 0 : 1);
