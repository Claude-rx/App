// One real test order through the live funnel: the checkout with NEXT's test card (no charge, no transaction; the
// order is flagged as a test and lands in the store, to be cancelled), then each special offer accepted or declined as
// the funnel routes them, then the thank-you page's lines, their terms and the total.
//
// usage: [FUNNEL=stick|apf] node tools/funnel/live_order.mjs <host> <out-dir> [--path accept,decline,...] [--pack <card>]
//        [--tier <bundle id>] [--resume <ref_id> [--start <page file>]]
//   FUNNEL   which funnel's pages (tools/funnel/funnels/<name>.py): stick (default) or apf
//   <host>   https://try.skinofab.com (the funnel's host: the domain the campaign allows), or a local build under its
//            Page Kit slug, http://127.0.0.1:8090/apf-funnel (localhost is always allowed by the campaign)
//   --path   what to do on the offer pages, in the order they come. Accept and decline route differently (apf: offer 1
//            accepted skips offer 2; a decline goes to the downsell), so the walk reads where to arrive from each page's
//            own accept / decline meta tags, and stops on the thank-you page; pages after the list are declined.
//            Default: decline everything, the shortest path.
//   --pack   the checkout card to buy (default: the funnel's featured card)
//   --tier   on a supply-card offer (apf's offer 1), the card whose Buy now is pressed on accept (default: the selected one)
//   --resume <ref_id> [--start <page file>]  skip the checkout: walk the offers of an order already placed, from that page
// Writes a screenshot per step and order.json (order number, lines, terms, total) to <out-dir>; exits 1 when a step
// does not arrive where the page routes it.
//
// Campaigns OS's own `qa run` places these orders on a local build; it cannot yet on the store's host, where the funnel
// is served at the site root (/<page>/) rather than under its Page Kit slug.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'node:fs';

const [host, out] = process.argv.slice(2);
const opt = (name, dflt) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : dflt; };
const FUNNELS = {
  stick: { checkout: 'stick-checkout', pack: 'stick-2', first: 'stick-special-1', thankYou: 'stick-thank-you' },
  apf: { checkout: 'foundation-checkout', pack: 'apf-2', first: 'foundation-offer-1', thankYou: 'foundation-thank-you' },
};
const FN = FUNNELS[process.env.FUNNEL || 'stick'];
const path = opt('--path', 'decline').split(',');
const pack = opt('--pack', FN.pack);
const tier = opt('--tier', null);
const resume = opt('--resume', null);                  // an order's ref_id: start on an offer page with it
const start = opt('--start', FN.first);                // with --resume: the page to start on
const CARD = '6011111111111117', CVV = '123';          // NEXT's test card (as Campaigns OS's QA uses)
const ADDRESS = { fname: 'Quinn', lname: 'Tester', email: 'qa-live@skinofab.test', address1: '1600 Amphitheatre Pkwy',
  city: 'Mountain View', province: 'CA', postal: '94043' };
fs.mkdirSync(out, { recursive: true });

// the agent proxy only for a remote host: it answers 405 to a local address (a run on Page Kit's _site, http://127.0.0.1:<port>/<slug>)
const browser = await chromium.launch({ proxy: process.env.HTTPS_PROXY && !/127\.0\.0\.1|localhost/.test(host) ? { server: process.env.HTTPS_PROXY } : undefined, args: ['--disable-dev-shm-usage'] });
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
// a filled text field the SDK still flags (its state missed the typing): type it again, as a shopper would
const retypeErrored = async () => {
  await page.waitForTimeout(600);
  for (const [name, value] of Object.entries(ADDRESS)) {
    if (name === 'province') continue;
    const f = field(name);
    if (await f.count() && /has-error|next-error-field/.test(await f.getAttribute('class') || '')) await fill(name, value);
  }
};
const arrive = async (file) => page.waitForURL(new RegExp(`/${file}/`), { timeout: 90000 });
const fileOf = (u) => new URL(u, host).pathname.split('/').filter(Boolean).pop();

let result = { funnel: process.env.FUNNEL || 'stick', host, pack, path };
try {
  if (!resume) {
  await step('checkout', async () => {
    await page.goto(`${host}/${FN.checkout}/?forceBundleId=${pack}`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction(() => [...document.querySelectorAll('[data-next-bundle-card] .bundle-card__price-total')]
      .some((e) => /\$\d/.test(e.textContent)), null, { timeout: 30000 });
    // the SDK binds the form after it has priced the cards: the country select gets its options last. A field typed
    // before that keeps its value but not the SDK's state ("Enter a first name" on a filled field)
    await page.waitForFunction(() => document.querySelectorAll('[data-next-checkout-field="country"] option').length > 1, null, { timeout: 30000 });
    await page.waitForTimeout(1500);
  });
  await step('details', async () => {
    await fill('fname', ADDRESS.fname); await fill('lname', ADDRESS.lname); await fill('email', ADDRESS.email);
    await select('country', 'US');
    await fill('address1', ADDRESS.address1);
    await page.keyboard.press('Escape');                 // close the address suggestions
    await page.waitForTimeout(800);
    await fill('city', ADDRESS.city); await select('province', ADDRESS.province); await fill('postal', ADDRESS.postal);
    await retypeErrored();
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
    try { await arrive(FN.first); }
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
    await step('resume', async () => { await page.goto(`${host}/${start}/?ref_id=${resume}`, { waitUntil: 'load', timeout: 60000 }); });
  }
  result.ref_id = new URL(page.url()).searchParams.get('ref_id');
  result.offers = [];
  // the offer pages, as the funnel routes them, until the thank-you page
  for (let i = 0, guard = 0; guard < 10; guard++) {
    const file = fileOf(page.url());
    if (file === FN.thankYou) break;
    const action = path[i] || 'decline';
    await step(`${file}-${action}`, async () => {
      // the SDK has the order (sf-offer-gate's field is filled) before its offer actions answer a click; a page with a
      // skip rule (the brush offers) has read the order's lines by then, and may be sending the order on
      // a page with a skip rule may send the order on (the brush offers, for an order with a brush) while this waits
      const left = page.waitForURL((u) => !u.pathname.includes(`/${file}/`), { timeout: 45000 }).then(() => 'left').catch(() => 'stayed');
      await Promise.race([left, (async () => {
        await page.waitForFunction(() => (document.querySelector('[data-sf-upsell-ok]')?.textContent || '').trim(), null, { timeout: 45000 });
        await page.waitForFunction(() => !document.querySelector('[data-sf-skip-skus]') || document.querySelector('[data-sf-sku]'), null, { timeout: 30000 }).catch(() => {});
        await page.waitForTimeout(1500);
      })()]).catch(() => {});
      const now = fileOf(page.url());
      if (now !== file) { result.offers.push({ page: file, gate: `sent on to ${now} without an offer` }); return; }
      i++;
      const meta = async (n) => page.locator(`meta[name="${n}"]`).first().getAttribute('content');
      const next = fileOf(await meta(action === 'accept' ? 'next-upsell-accept-url' : 'next-upsell-decline-url'));
      const supply = await page.locator('[data-sf-supply-buy]').count();
      if (action === 'accept' && supply) {
        // a supply-card offer: the card's own Buy now (it selects the card, then fires the offer's add)
        const card = tier ? page.locator(`[data-next-bundle-card][data-next-bundle-id="${tier}"]`).first() : page.locator('[data-next-bundle-card].next-selected').first();
        const price = (await card.locator('[data-next-bundle-display="price"]').first().textContent().catch(() => ''))?.trim();
        result.offers.push({ page: file, action, tier: await card.getAttribute('data-next-bundle-id'), shown_price: price, next });
        // a real (trusted) click, as hers: sf-supply.js only steps in for those (it selects the card, then clicks the
        // button again for the SDK); a synthetic click would add the card selected before
        const buy = card.locator('[data-sf-supply-buy]').first();
        await buy.scrollIntoViewIfNeeded();
        await buy.click({ force: true, timeout: 15000 });
      } else {
        const price = (await page.locator('[data-next-upsell="offer"] .upsell-offer__price:not(.diagonal-strike), [data-next-upsell="offer"] [data-next-bundle-card].next-selected [data-next-bundle-display="price"]').first().textContent().catch(() => ''))?.trim();
        result.offers.push({ page: file, action, shown_price: price, next });
        // (the accept button pulses, so it is never "stable" to Playwright: the element's own click)
        await page.locator(`[data-next-upsell="offer"] [data-next-upsell-action="${action === 'accept' ? 'add' : 'skip'}"]`).first().evaluate((el) => el.click());
      }
      await arrive(next);
    });
  }
  await step('thank-you', async () => {
    await page.waitForSelector('[data-order-line-id]', { timeout: 30000 });
    await page.waitForTimeout(2000);
    Object.assign(result, await page.evaluate(() => ({
      order_number: document.querySelector('[data-next-display="order.number"]')?.textContent.trim(),
      lines: [...document.querySelectorAll('.summary-desktop [data-order-line-id]')]       // (the desktop summary; the phone one repeats it)
        .slice(0, 8).map((l) => ({ name: l.querySelector('.cart-item__title')?.textContent.trim(),
          terms: l.querySelector('.sf-line-renew')?.textContent.trim(), total: l.querySelector('.checkout__line-item__final-price')?.textContent.trim() })),
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
