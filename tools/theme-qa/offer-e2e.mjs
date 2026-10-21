// Adaptive Peptide Foundation subscription offer, end to end on the NEXT preview (no order is placed).
// usage: node offer-e2e.mjs <store_url> <theme_id> <pdp_path> <shots_dir> [<price> <interval> <interval_count>]
// The product is sold as a month-to-month refill only. For each base it picks the base in the buy box, clicks the
// button and reads the NEXT cart through the storefront GraphQL responses: the line must be that base's variant,
// at the plan price, as a subscription with the plan's interval. A third case adds the foundation with no plan at
// all (window.SFCommerce.addItems, the path every other button on the site uses) and asserts it still becomes the
// plan. It also records the cart page's frequency choices and the checkout's subscription wording.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path';

const [STORE, THEME, PDP, SHOTS, PRICE = '33', INTERVAL = 'month', COUNT = '1'] = process.argv.slice(2);
fs.mkdirSync(SHOTS, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const picker = '[data-sf-offer-picker]';

async function session(w = 1440, h = 900) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const page = await ctx.newPage();
  const s = { ctx, page, errors: [], cart: null };
  page.on('pageerror', e => s.errors.push(e.message.slice(0, 160)));
  page.on('response', async r => {
    if (!r.url().includes('/api/graphql')) return;
    try {
      const j = await r.json();
      const found = JSON.stringify(j.data || {}).includes('"lines"');
      if (found) s.cart = j.data;
      if (j.errors) s.errors.push('graphql ' + JSON.stringify(j.errors).slice(0, 200));
    } catch (e) {}
  });
  await page.goto(`${STORE}/?preview_theme=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  return s;
}

// the cart's lines wherever the mutation put them, flattened to what we assert on
function lines(data) {
  const out = [];
  (function walk(o) {
    if (!o || typeof o !== 'object') return;
    if (Array.isArray(o.lines)) o.lines.forEach(l => out.push(l));
    else Object.values(o).forEach(walk);
  })(data);
  return out.map(l => {
    const flat = JSON.stringify(l);
    const num = k => { const m = flat.match(new RegExp(`"${k}":"?([0-9.]+)`)); return m ? parseFloat(m[1]) : NaN; };
    const str = k => { const m = flat.match(new RegExp(`"${k}":"([^"]*)"`)); return m ? m[1] : null; };
    return { raw: flat.slice(0, 600), pk: num('pk') || num('id'), title: str('title') || str('name'),
             price: [num('unitPriceInclTax'), num('unitPriceExclTax'), num('unitPrice'), num('price')].find(n => !isNaN(n)),
             interval: str('interval'), intervalCount: num('intervalCount'), subscription: /subscri|interval/i.test(flat) };
  });
}

function check(line, wantPk) {
  const problems = [];
  if (!line) return ['no cart line'];
  if (wantPk && line.pk !== wantPk && !line.raw.includes(`"${wantPk}"`) && !line.raw.includes(`:${wantPk},`)) problems.push(`variant ${line.pk} != ${wantPk}`);
  if (!(Math.abs(line.price - parseFloat(PRICE)) < 0.01)) problems.push(`price ${line.price} != ${PRICE}`);
  if (!line.subscription || (line.interval && line.interval.toLowerCase() !== INTERVAL) || (!isNaN(line.intervalCount) && String(line.intervalCount) !== COUNT))
    problems.push(`not a ${COUNT}-${INTERVAL} subscription: ${line.interval} ${line.intervalCount}`);
  return problems;
}

const out = [];
const pks = await (async () => { const s = await session(); await s.page.goto(STORE + PDP, { waitUntil: 'networkidle', timeout: 90000 });
  const t = JSON.parse(await s.page.getAttribute(picker, 'data-pks')); await s.ctx.close(); return t; })();

for (const base of Object.keys(pks)) {
  const s = await session();
  await s.page.goto(STORE + PDP, { waitUntil: 'networkidle', timeout: 90000 });
  const box = s.page.locator(picker);
  await box.scrollIntoViewIfNeeded();
  await box.locator(`input[name=sf_base][value=${base}]`).check({ force: true });
  const plan = await box.locator('input[name=sf_purchase]:checked').evaluate(el => ({ value: el.value, interval: el.dataset.interval, count: el.dataset.intervalCount }));
  const onetime = await s.page.locator('input[name=sf_purchase][value=once]').count();
  const bb = await box.boundingBox();
  const trust = await s.page.locator('.sfp-trust').boundingBox();
  await s.page.screenshot({ path: path.join(SHOTS, `buybox-${base}.png`), clip: { x: bb.x - 20, y: bb.y - 20, width: bb.width + 40, height: (trust ? trust.y + trust.height : bb.y + bb.height) - bb.y + 40 } });
  await s.page.click('form[data-sf-product-form] [data-add-to-cart]', { force: true });
  await s.page.waitForTimeout(6000);
  const line = lines(s.cart)[0];
  await s.page.screenshot({ path: path.join(SHOTS, `cart-${base}.png`) });
  const problems = check(line, pks[base]);
  if (plan.value !== 'subscribe' || plan.interval !== INTERVAL || plan.count !== COUNT) problems.push('picker plan ' + JSON.stringify(plan));
  if (onetime) problems.push('one-time option present');
  let extra = {};
  if (base === Object.keys(pks)[0]) {
    // the cart page's per-line frequency select, and the checkout's wording for the subscription
    await s.page.goto(`${STORE}/cart/`, { waitUntil: 'networkidle', timeout: 90000 });
    extra.cartPageOptions = await s.page.evaluate(() => [...document.querySelectorAll('select')].filter(sel => /subscri|interval|frequen/i.test(sel.name + sel.id))
      .map(sel => ({ name: sel.name, selected: sel.value, options: [...sel.options].map(o => `${o.value}=${o.text.trim()}`) })));
    extra.cartPagePlan = await s.page.evaluate(() => [...document.querySelectorAll('input[type=hidden][name$="subscription_range"]')].map(i => i.value));
    if (extra.cartPageOptions.some(o => o.options.some(v => /one.?time/i.test(v)))) problems.push('cart page offers one-time');
    // a quantity update on the cart page posts the formset: the line must stay the plan (checked at checkout below)
    const qty = s.page.locator('#cart_formset [name$="-quantity"]').first();
    if (await qty.count()) {
      if (await qty.evaluate(el => el.tagName === 'SELECT')) await qty.selectOption('2'); else await qty.fill('2');
      // the select may submit the form itself (Spark's cart page); either way wait for the reloaded cart page
      await Promise.all([s.page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {}),
                         s.page.evaluate(() => { const f = document.getElementById('cart_formset'); if (f) f.requestSubmit ? f.requestSubmit() : f.submit(); }).catch(() => {})]);
      await s.page.waitForLoadState('networkidle').catch(() => {});
      await s.page.waitForTimeout(2000);
      extra.cartPageAfterUpdate = await s.page.evaluate(() => document.body.innerText.replace(/\s+/g, ' ').match(/Adaptive Peptide Foundation[^$]{0,80}\$[0-9.]+[^$]{0,120}/)?.[0] || '');
    }
    await s.page.screenshot({ path: path.join(SHOTS, 'cart-page.png'), fullPage: true });
    const resp = await s.page.goto(`${STORE}/checkout/`, { waitUntil: 'load', timeout: 90000 });
    await s.page.waitForFunction(() => /Adaptive Peptide Foundation/i.test(document.body.innerText), null, { timeout: 25000 }).catch(() => {});
    const text = await s.page.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    extra.checkout = { status: resp && resp.status(), hasLine: /Adaptive Peptide Foundation/i.test(text),
                       subscriptionWords: (text.match(/[^.]{0,60}(subscri|every\s+\d*\s*month|renew|recurring)[^.]{0,60}/gi) || []).slice(0, 4),
                       prices: (text.match(/\$\d+\.\d\d/g) || []).slice(0, 6) };
    await s.page.screenshot({ path: path.join(SHOTS, 'checkout.png'), fullPage: true });
    if (extra.cartPageAfterUpdate !== undefined && !(/Every 1 Month/i.test(text) && /\$66\.00/.test(text))) problems.push('after the cart page update the checkout is not 2 x monthly $33');
  }
  out.push({ case: `buy box ${base}`, line: line && { pk: line.pk, title: line.title, price: line.price, interval: line.interval, intervalCount: line.intervalCount },
             ...extra, errors: s.errors, ok: problems.length === 0, problems, raw: problems.length ? line && line.raw : undefined });
  await s.ctx.close();
}

// any other button: the foundation added with no plan must still be the plan
{
  const s = await session();
  const first = Object.values(pks)[0];
  await s.page.evaluate(id => window.SFCommerce.addItems([{ id: String(id), quantity: 1 }]), first);
  await s.page.waitForTimeout(5000);
  const line = lines(s.cart)[0];
  const problems = check(line, first);
  out.push({ case: 'add without a plan (cart drawer, landing pages)', line: line && { pk: line.pk, price: line.price, interval: line.interval, intervalCount: line.intervalCount },
             errors: s.errors, ok: problems.length === 0, problems, raw: problems.length ? line && line.raw : undefined });
  await s.ctx.close();
}

console.log(JSON.stringify(out, null, 1));
await browser.close();
process.exit(out.every(o => o.ok) ? 0 : 1);
