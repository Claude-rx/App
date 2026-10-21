// Live end-to-end check on the NEXT preview (no order is placed).
// usage: node live-e2e.mjs <store_url> <theme_id> <pdp_path> <shots_dir>
// Opens the PDP with ?preview_theme, picks the second colour swatch if any, submits the design's add-to-cart,
// asserts the Spark side cart opens with a line and the badge counts it, then follows the drawer's checkout
// link and asserts the platform checkout loads. Also screenshots home + PDP at 1440 and 390.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path';

const [STORE, THEME, PDP, SHOTS] = process.argv.slice(2);
fs.mkdirSync(SHOTS, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const result = { errors: [], graphql: [] };

for (const [vp, w, h] of [['desktop', 1440, 900], ['mobile', 390, 844]]) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const page = await ctx.newPage();
  page.on('pageerror', e => result.errors.push(`${vp} ${e.message.slice(0, 140)}`));
  await page.goto(`${STORE}/?preview_theme=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  await page.screenshot({ path: path.join(SHOTS, `home-${vp}.png`) });
  await page.goto(STORE + PDP, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(SHOTS, `pdp-${vp}.png`) });
  if (vp === 'desktop') {
    page.on('response', async r => { if (r.url().includes('/api/graphql')) { try { const j = await r.json(); result.graphql.push(Object.keys(j.data || {}).join(',') + (j.errors ? ' ERR ' + JSON.stringify(j.errors).slice(0, 160) : '')); } catch (e) {} } });
    result.title = await page.title();
    result.price = await page.evaluate(() => (document.querySelector('.product__price') || {}).innerText || '');
    const swatches = await page.$$('form[data-sf-product-form] input[type=radio]');
    if (swatches.length > 1) { await swatches[1].evaluate(el => { el.click(); el.dispatchEvent(new Event('change', { bubbles: true })); }); await page.waitForTimeout(800); }
    result.variant_id = await page.evaluate(() => (document.querySelector('form[data-sf-product-form] input[name="id"]') || {}).value);
    const btn = await page.$('form[data-sf-product-form] [type="submit"], form[data-sf-product-form] button[name="add"]');
    await btn.scrollIntoViewIfNeeded(); await btn.click({ force: true });
    await page.waitForTimeout(5000);
    result.cart = await page.evaluate(() => {
      const d = document.querySelector('spark-cart-drawer');
      const root = d && d.shadowRoot;
      const text = root ? root.textContent.replace(/\s+/g, ' ').trim() : '';
      const checkout = root && [...root.querySelectorAll('a,button')].find(a => /checkout/i.test(a.textContent + (a.getAttribute('href') || '')));
      return { open: d && d.getAttribute('data-open'), badge: (document.getElementById('cart-badge') || {}).textContent,
               text: text.slice(0, 300), checkout: checkout ? (checkout.getAttribute('href') || checkout.dataset.href || 'button') : null };
    });
    await page.screenshot({ path: path.join(SHOTS, 'cart-drawer.png') });
    const checkoutUrl = await page.evaluate(() => (document.querySelector('spark-cart-drawer') || {}).dataset?.checkoutUrl || '/checkout/');
    const resp = await page.goto(STORE + checkoutUrl, { waitUntil: 'load', timeout: 90000 });
    await page.waitForFunction(() => /lip liner|liner/i.test(document.body.innerText), null, { timeout: 20000 }).catch(() => {});
    result.checkout = { status: resp && resp.status(), url: page.url(), title: await page.title(),
                        hasLine: await page.evaluate(() => /lip liner|liner/i.test(document.body.innerText)) };
    await page.screenshot({ path: path.join(SHOTS, 'checkout.png') });
  }
  await ctx.close();
}
console.log(JSON.stringify(result, null, 1));
await browser.close();
