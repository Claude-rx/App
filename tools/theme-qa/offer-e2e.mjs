// Adaptive Peptide Foundation offer, end to end on the NEXT preview (no order is placed).
// usage: node offer-e2e.mjs <store_url> <theme_id> <pdp_path> <shots_dir>
// The offer (tools/persona/ccf_copy.py PACKS/REFILL): 1 bottle or 2 bottles + free gifts, one-time by default, or
// with Automatic Refills (a cheaper price, refilled every 28 days). The picker's data-packs table is the expectation.
//   1-4. every pack x purchase type: the picker's prices and the price under the title follow the choice, the refill
//        terms show only with refills; the button adds that pack's variant at that price, as a 28-day refill or
//        one-time (read from the storefront GraphQL responses); the drawer shows no plan talk, the guarantee, a
//        review, the add-ons, and the upgrade only while the bag holds the 1-bottle pack.
//   5-6. the drawer upgrade from 1 bottle (one-time and refill): one line, the 2-bottle pack, same purchase type.
//   7.   a drawer add-on: added as a second line, then no longer offered.
//   checkout (1 bottle with refills, and 2 bottles one-time): the line, its price and the refill wording.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path';

const [STORE, THEME, PDP, SHOTS] = process.argv.slice(2);
fs.mkdirSync(SHOTS, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const picker = '[data-sf-offer-picker]';
const drawer = 'spark-cart-drawer';
const money = v => '$' + (v % 1 ? v.toFixed(2) : String(v));

async function session(w = 1440, h = 900) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const page = await ctx.newPage();
  const s = { ctx, page, errors: [], cart: null };
  page.on('pageerror', e => s.errors.push(e.message.slice(0, 160)));
  page.on('response', async r => {
    if (!r.url().includes('/api/graphql')) return;
    try {
      const j = await r.json();
      if (JSON.stringify(j.data || {}).includes('"lines"')) s.cart = j.data;
      if (j.errors) s.errors.push('graphql ' + JSON.stringify(j.errors).slice(0, 200));
    } catch (e) {}
  });
  await page.goto(`${STORE}/?preview_theme=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  await page.goto(STORE + PDP, { waitUntil: 'networkidle', timeout: 90000 });
  return s;
}

// the cart's lines wherever the mutation put them
function lines(data) {
  const out = [];
  (function walk(o) {
    if (!o || typeof o !== 'object') return;
    if (Array.isArray(o.lines)) o.lines.forEach(l => out.push(l));
    else Object.values(o).forEach(walk);
  })(data);
  return out.map(l => ({ product: Number(l.product && l.product.pk), title: l.product && l.product.title, quantity: l.quantity,
                         price: parseFloat(l.unitPriceExclTax ?? l.unitPriceInclTax ?? l.unitPrice), interval: l.interval || null,
                         intervalCount: l.intervalCount ? Number(l.intervalCount) : null }));
}

function checkLine(line, want) {
  const p = [];
  if (!line) return ['no cart line'];
  if (line.product !== want.pk) p.push(`variant ${line.product} != ${want.pk}`);
  if (Math.abs(line.price - want.price) > 0.005) p.push(`price ${line.price} != ${want.price}`);
  if (want.refill && !(String(line.interval).toLowerCase().startsWith('day') && line.intervalCount === 28)) p.push(`not a 28-day refill: ${line.interval} ${line.intervalCount}`);
  if (!want.refill && line.interval) p.push(`one-time line has interval ${line.interval} ${line.intervalCount}`);
  return p;
}

async function choose(s, key, refill) {
  const box = s.page.locator(picker);
  await box.scrollIntoViewIfNeeded();
  await box.locator(`input[name=sf_pack][value="${key}"]`).check({ force: true });
  const cb = box.locator('input[name=sf_purchase]');
  if ((await cb.isChecked()) !== refill) await cb.click({ force: true });
  return s.page.evaluate(sel => {
    const root = document.querySelector(sel), form = root.closest('form');
    const head = document.querySelector('.product__price-and-badge');
    const terms = document.querySelector('[data-sf-refill-terms]');
    return { id: form.querySelector('input[name=id]').value,
             now: head.querySelector('.product__price--regular').textContent.trim(), was: head.querySelector('.product__price--compare').textContent.trim(),
             cards: [...root.querySelectorAll('.sfo-card')].map(c => c.querySelector('[data-sfo-now]').textContent + ' ' + c.querySelector('[data-sfo-save]').textContent),
             pct: root.querySelector('[data-sfo-pct]').textContent, termsShown: !!terms && !terms.hidden, terms: terms ? terms.textContent : '' };
  }, picker);
}

async function drawerState(s) {
  return s.page.evaluate(sel => {
    const r = document.querySelector(sel).shadowRoot, text = r.querySelector('.spark-drawer-panel').innerText.replace(/\s+/g, ' ');
    return { open: getComputedStyle(r.querySelector('.spark-drawer-panel')).visibility !== 'hidden', text: text.slice(0, 900),
             upgrade: !!r.querySelector('[data-sf-upgrade]'), addons: [...r.querySelectorAll('.sf-upsell-name')].map(a => a.textContent),
             review: !!r.querySelector('.sf-review'), guarantee: !!r.querySelector('.sf-trust-row'), pay: r.querySelectorAll('.sf-pay img').length,
             planTalk: /refill reminder|cancel any time|due today|switch base/i.test(text) };
  }, drawer);
}

async function addToCart(s) {
  await s.page.click('form[data-sf-product-form] [data-add-to-cart]', { force: true });
  await s.page.waitForTimeout(6000);
}

async function checkout(s, name) {
  const resp = await s.page.goto(`${STORE}/checkout/`, { waitUntil: 'load', timeout: 90000 });
  await s.page.waitForFunction(() => /Adaptive Peptide Foundation/i.test(document.body.innerText), null, { timeout: 25000 }).catch(() => {});
  const text = await s.page.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  await s.page.screenshot({ path: path.join(SHOTS, `checkout-${name}.png`), fullPage: true });
  return { status: resp && resp.status(), hasLine: /Adaptive Peptide Foundation/i.test(text), pack: (text.match(/(1 bottle|2 bottles \+ free gifts)/i) || [])[0] || null,
           refillWords: (text.match(/[^.$]{0,40}(every\s+28\s+days?|subscri|recurring|renew)[^.$]{0,40}/gi) || []).slice(0, 3),
           prices: (text.match(/\$\d+\.\d\d/g) || []).slice(0, 6) };
}

const out = [];
const packs = await (async () => { const s = await session(); const t = JSON.parse(await s.page.getAttribute(picker, 'data-packs')); await s.ctx.close(); return t; })();

for (const [key, pack] of Object.entries(packs)) {
  for (const refill of [false, true]) {
    const name = `${key}-${refill ? 'refill' : 'once'}`;
    const s = await session();
    const ui = await choose(s, key, refill);
    const want = { pk: pack.pk, price: refill ? pack.refill : pack.price, refill };
    const problems = [];
    if (ui.id !== String(pack.pk)) problems.push(`form id ${ui.id} != ${pack.pk}`);
    if (!ui.now.startsWith(money(want.price))) problems.push(`title price ${ui.now} != ${money(want.price)}`);
    if (!ui.was.startsWith(money(pack.compare))) problems.push(`title compare ${ui.was} != ${money(pack.compare)}`);
    if (ui.termsShown !== refill) problems.push(`refill terms shown=${ui.termsShown}`);
    if (refill && !ui.terms.includes(`You pay ${money(pack.refill)} today, then ${money(pack.refill)} every 28 days`)) problems.push('terms amount: ' + ui.terms.slice(0, 80));
    const bb = await s.page.locator('.product__price-and-badge').boundingBox();
    const tb = await s.page.locator('.sfp-trust').boundingBox();
    await s.page.screenshot({ path: path.join(SHOTS, `buybox-${name}.png`), clip: { x: bb.x - 20, y: bb.y - 20, width: Math.max(bb.width, tb ? tb.width : 0) + 40, height: (tb ? tb.y + tb.height : bb.y + 900) - bb.y + 40 } });
    await addToCart(s);
    const ls = lines(s.cart);
    problems.push(...checkLine(ls[0], want));
    await s.page.waitForTimeout(1500);   // add-ons arrive from the storefront API after the drawer opens
    const d = await drawerState(s);
    await s.page.screenshot({ path: path.join(SHOTS, `drawer-${name}.png`) });
    if (!d.open) problems.push('drawer did not open');
    if (d.planTalk) problems.push('drawer has plan talk');
    if (d.upgrade !== (key === '1')) problems.push(`upgrade shown=${d.upgrade}`);
    if (!d.guarantee || !d.review) problems.push('trust card incomplete');
    if (d.addons.length < 1) problems.push('no add-ons');
    let co;
    if ((key === '1' && refill) || (key === '2' && !refill)) {
      co = await checkout(s, name);
      if (!co.hasLine) problems.push('checkout has no line');
      if (!co.prices.includes('$' + want.price.toFixed(2))) problems.push(`checkout prices ${co.prices} lack $${want.price.toFixed(2)}`);
      if (refill && !co.refillWords.length) problems.push('checkout does not say the refill cadence');
    }
    out.push({ case: `buy ${name}`, ui, line: ls[0], lines: ls.length, drawer: { upgrade: d.upgrade, addons: d.addons, pay: d.pay }, checkout: co,
               errors: s.errors, ok: problems.length === 0, problems });
    await s.ctx.close();
  }
}

// 5-6. the upgrade, from both purchase types
for (const refill of [false, true]) {
  const s = await session();
  await choose(s, '1', refill);
  await addToCart(s);
  await s.page.locator(`${drawer} [data-sf-upgrade]`).click();
  await s.page.waitForTimeout(6000);
  const ls = lines(s.cart);
  const want = { pk: packs['2'].pk, price: refill ? packs['2'].refill : packs['2'].price, refill };
  const problems = checkLine(ls[0], want);
  if (ls.length !== 1) problems.push(`${ls.length} lines after the upgrade`);
  const d = await drawerState(s);
  if (d.upgrade) problems.push('upgrade still offered');
  await s.page.screenshot({ path: path.join(SHOTS, `drawer-upgraded-${refill ? 'refill' : 'once'}.png`) });
  out.push({ case: `upgrade from 1 bottle ${refill ? 'refill' : 'one-time'}`, lines: ls, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// 7. a drawer add-on
{
  const s = await session();
  await choose(s, '2', false);
  await addToCart(s);
  await s.page.waitForTimeout(1500);
  const before = await drawerState(s);
  const add = s.page.locator(`${drawer} [data-sf-add]`).first();
  const problems = [];
  if (!(await add.count())) problems.push('no add-on button');
  else {
    await add.click();
    await s.page.waitForTimeout(6000);
  }
  const ls = lines(s.cart);
  const after = await drawerState(s);
  if (ls.length !== 2) problems.push(`${ls.length} lines after adding an add-on`);
  if (after.addons.includes(before.addons[0])) problems.push('the added add-on is still offered');
  await s.page.screenshot({ path: path.join(SHOTS, 'drawer-addon.png') });
  out.push({ case: 'drawer add-on', before: before.addons, after: after.addons, lines: ls, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// mobile buy box and drawer, for the eye
{
  const s = await session(390, 844);
  await choose(s, '2', true);
  const bb = await s.page.locator(picker).boundingBox();
  await s.page.screenshot({ path: path.join(SHOTS, 'mobile-buybox.png'), clip: { x: 0, y: Math.max(0, bb.y - 120), width: 390, height: Math.min(1400, bb.height + 520) } });
  await addToCart(s);
  await s.page.waitForTimeout(1500);
  await s.page.screenshot({ path: path.join(SHOTS, 'mobile-drawer.png') });
  await s.ctx.close();
}

console.log(JSON.stringify(out, null, 1));
await browser.close();
process.exit(out.every(o => o.ok) ? 0 : 1);
