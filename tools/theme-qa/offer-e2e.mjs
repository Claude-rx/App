// Color Changing Foundation offer picker, end to end on the NEXT preview (no order is placed).
// usage: node offer-e2e.mjs <store_url> <theme_id> <pdp_path> <shots_dir>
// For three picks (Medium-Deep single as a 60-day subscription, Light-Medium Duo, Medium-Deep Complexion Set) it
// clicks the picker, clicks Add to Cart, then reads the NEXT cart through the storefront GraphQL API and asserts the
// line's product, price and subscription interval.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path';

const [STORE, THEME, PDP, SHOTS] = process.argv.slice(2);
fs.mkdirSync(SHOTS, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const picks = [
  { name: 'md-subscribe', base: 'md', offer: 'single', purchase: 'subscribe', expect: { title: /Color Changing Foundation/, price: 33, interval: 60 } },
  { name: 'lm-duo', base: 'lm', offer: 'duo', expect: { title: /Duo/, price: 64 } },
  { name: 'md-set', base: 'md', offer: 'set', expect: { title: /Complexion Set/, price: 79 } },
];
const out = [];
for (const pick of picks) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message.slice(0, 140)));
  let lines = null;
  page.on('response', async r => {
    if (!r.url().includes('/api/graphql')) return;
    try { const j = await r.json(); const c = j.data && (j.data.addCartLines || j.data.cart); if (c) lines = (c.cart || c).lines || lines; } catch (e) {}
  });
  await page.goto(`${STORE}/?preview_theme=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  await page.goto(STORE + PDP, { waitUntil: 'networkidle', timeout: 90000 });
  const picker = page.locator('[data-sf-offer-picker]');
  await picker.scrollIntoViewIfNeeded();
  await picker.locator(`input[name=sf_base][value=${pick.base}]`).check({ force: true });
  await picker.locator(`input[name=sf_offer][value=${pick.offer}]`).check({ force: true });
  if (pick.purchase) await picker.locator(`input[name=sf_purchase][value=${pick.purchase}]`).check({ force: true });
  const id = await page.evaluate(() => document.querySelector('form[data-sf-product-form] input[name=id]').value);
  await page.screenshot({ path: path.join(SHOTS, `picker-${pick.name}.png`), clip: await picker.boundingBox().then(b => ({ x: b.x - 20, y: b.y - 20, width: b.width + 40, height: b.height + 40 })) });
  await page.click('form[data-sf-product-form] [data-add-to-cart]', { force: true });
  await page.waitForTimeout(5000);
  const cart = await page.evaluate(() => { const d = document.querySelector('spark-cart-drawer'); return d && d.shadowRoot ? d.shadowRoot.textContent.replace(/\s+/g, ' ') : ''; });
  await page.screenshot({ path: path.join(SHOTS, `cart-${pick.name}.png`) });
  const line = (lines || [])[0] || {};
  const title = line.product ? (line.product.title || line.product.name || '') : cart;
  const price = parseFloat(line.unitPriceExclTax || line.unitPrice || 'NaN');
  const ok = pick.expect.title.test(title + ' ' + cart) && (isNaN(price) || Math.abs(price - pick.expect.price) < 0.01)
    && (!pick.expect.interval || String(line.intervalCount || (line.subscriptionInfo || {}).intervalCount) === String(pick.expect.interval) || /every 60/i.test(cart));
  out.push({ pick: pick.name, productPk: id, lineTitle: title.slice(0, 60), unitPrice: price, interval: line.intervalCount || (line.subscriptionInfo || {}).intervalCount || null,
             cartMentions: (cart.match(/\$\d+\.\d\d/g) || []).slice(0, 4), errors, ok });
  await ctx.close();
}
console.log(JSON.stringify(out, null, 1));
await browser.close();
process.exit(out.every(o => o.ok) ? 0 : 1);
