// Adaptive Peptide Foundation offer, end to end on the NEXT preview (no order is placed).
// usage: node offer-e2e.mjs <store_url> <theme_id> <pdp_path> <shots_dir>
// The offer (tools/persona/ccf_copy.py PACKS/REFILL): 1 bottle or 2 bottles + free gifts, one-time or with Automatic
// Refills (a cheaper price, refilled every 28 days). REFILL decides whether refills start ticked and whether the box
// is shown; the test reads both from the page. The picker's data-packs table is the expectation.
//   buy:  every pack in its default purchase type (and the other type too when the box is shown): the picker's prices
//         and the price under the title follow the choice, the refill terms show exactly while refills are on; the
//         button adds that pack's variant at that price, as a 28-day refill or one-time (read from the storefront
//         GraphQL responses); the drawer shows no plan talk, the guarantee, a review, the add-ons, and the upgrade
//         only while the bag holds the 1-bottle pack.
//   upgrade: from 1 bottle with refills and bought once (from the box, or with the box hidden through
//         SFCommerce.addItems, the path other buttons use): one line, the 2-bottle pack, same purchase type.
//   add-on: added as a second line, then no longer offered.
//   checkout (1 bottle and 2 bottles, first case of each): the line, its price and the refill wording.
// The Lymphatic Brush (tools/persona/brush_copy.py BUNDLES; optional 5th argument, its product page path):
//   buy: each bundle adds its variant at its price, one-time; the drawer offers the 1 -> 2 brushes upgrade only for
//        one brush, and never the brush as an add-on while it is in the bag; checkout shows the 2-brush bundle.
//   upgrade: 1 brush -> 2 brushes in the drawer: one line, one-time.
//   page: Solena's sections in order, no "Solena" anywhere, five tabs with the how-to video, seven FAQ answers, the
//        title price with cents, the button price, no stars or review wall without reviews; its card is in the
//        homepage shelf (default list, Bestsellers, New and Face tabs) at $24.95, and the menu link leads to it.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path';

const [STORE, THEME, PDP, SHOTS, BRUSH = '/catalogue/the-lymphatic-brush_169/'] = process.argv.slice(2);
fs.mkdirSync(SHOTS, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const picker = '[data-sf-offer-picker]';
const drawer = 'spark-cart-drawer';
const money = v => '$' + (v % 1 ? v.toFixed(2) : String(v));

async function session(w = 1440, h = 900, pdp = PDP) {
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
  await page.goto(STORE + pdp, { waitUntil: 'networkidle', timeout: 90000 });
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

// refill: true/false to set the box (it must be shown), null to keep the page's default
async function choose(s, key, refill = null) {
  const box = s.page.locator(picker);
  await box.scrollIntoViewIfNeeded();
  await box.locator(`input[name=sf_pack][value="${key}"]`).check({ force: true });
  const cb = box.locator('input[name=sf_purchase]');
  if (refill !== null && (await cb.isChecked()) !== refill) await cb.click({ force: true });
  return s.page.evaluate(sel => {
    const root = document.querySelector(sel), form = root.closest('form');
    const head = document.querySelector('.product__price-and-badge');
    const terms = document.querySelector('[data-sf-refill-terms]');
    const cb = root.querySelector('input[name=sf_purchase]'), pct = root.querySelector('[data-sfo-pct]');
    return { id: form.querySelector('input[name=id]').value, refill: cb.checked, boxShown: !!cb.offsetParent,
             now: head.querySelector('.product__price--regular').textContent.trim(), was: head.querySelector('.product__price--compare').textContent.trim(),
             cards: [...root.querySelectorAll('.sfo-card')].map(c => c.querySelector('[data-sfo-now]').textContent + ' ' + c.querySelector('[data-sfo-save]').textContent),
             pct: pct ? pct.textContent : null, termsShown: !!terms && !terms.hidden, terms: terms ? terms.textContent : '' };
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

async function checkout(s, name, product = 'Adaptive Peptide Foundation') {
  const resp = await s.page.goto(`${STORE}/checkout/`, { waitUntil: 'load', timeout: 90000 });
  await s.page.waitForFunction(p => document.body.innerText.toLowerCase().includes(p.toLowerCase()), product, { timeout: 25000 }).catch(() => {});
  const text = await s.page.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  await s.page.screenshot({ path: path.join(SHOTS, `checkout-${name}.png`), fullPage: true });
  return { status: resp && resp.status(), hasLine: text.toLowerCase().includes(product.toLowerCase()),
           pack: (text.match(/(1 bottle|2 bottles \+ free gifts|1 brush \+ free case|2 brushes \+ 2 free cases|3 brushes \+ 3 free cases \+ free body brush)/i) || [])[0] || null,
           refillWords: (text.match(/[^.$]{0,40}(every\s+28\s+days?|subscri|recurring|renew)[^.$]{0,40}/gi) || []).slice(0, 3),
           prices: (text.match(/\$\d+\.\d\d/g) || []).slice(0, 6) };
}

const out = [];
const { packs, start } = await (async () => {
  const s = await session();
  const t = JSON.parse(await s.page.getAttribute(picker, 'data-packs'));
  const ui = await choose(s, '1');
  await s.ctx.close();
  return { packs: t, start: ui };
})();
console.error(`refills ${start.refill ? 'on' : 'off'} by default, box ${start.boxShown ? 'shown' : 'hidden'}`);
if (!start.boxShown && !start.refill) console.error('note: the box is hidden and unticked, so refills cannot be bought from the product page');
const states = start.boxShown ? [start.refill, !start.refill] : [start.refill];

for (const [key, pack] of Object.entries(packs)) {
  for (const refill of states) {
    const name = `${key}-${refill ? 'refill' : 'once'}`;
    const s = await session();
    const ui = await choose(s, key, start.boxShown ? refill : null);
    const want = { pk: pack.pk, price: refill ? pack.refill : pack.price, refill };
    const problems = [];
    if (ui.id !== String(pack.pk)) problems.push(`form id ${ui.id} != ${pack.pk}`);
    if (ui.refill !== refill) problems.push(`refills ${ui.refill} != ${refill}`);
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
    if (refill === states[0]) {
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

// the upgrade, from both purchase types
for (const refill of [false, true]) {
  const s = await session();
  if (start.boxShown || refill === start.refill) {
    await choose(s, '1', start.boxShown ? refill : null);
    await addToCart(s);
  } else {   // the box is hidden: this purchase type comes from the site's other buttons
    await s.page.evaluate(pk => window.SFCommerce.addItems([{ id: String(pk), quantity: 1,
      subscription: null }]), packs['1'].pk);
    await s.page.waitForTimeout(6000);
  }
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

// any other button (landing pages, permalinks) names no purchase type: refills by default when the theme says so
{
  const s = await session();
  const dflt = await s.page.evaluate(() => window.SFDefaultPlan);
  await s.page.evaluate(pk => window.SFCommerce.addItems([{ id: String(pk), quantity: 1 }]), packs['1'].pk);
  await s.page.waitForTimeout(6000);
  const ls = lines(s.cart);
  const problems = checkLine(ls[0], { pk: packs['1'].pk, price: dflt ? packs['1'].refill : packs['1'].price, refill: !!dflt });
  out.push({ case: `other buttons: ${dflt ? 'refill by default' : 'one-time'}`, defaultPlan: dflt, line: ls[0], errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// the badges under the title: FrontrowMD Clinicians' Choice (when a listing is set) and the black star rating
{
  const s = await session(1280, 900);
  await s.page.waitForTimeout(5000);
  const b = await s.page.evaluate(() => {
    const f = document.getElementById('frontrow-sticker'), r = document.querySelector('.sf-rating');
    const t = document.querySelector('.product__title');
    return { frontrowId: window.SFFrontrowId, sticker: f ? { w: f.offsetWidth, h: f.offsetHeight, onGallery: !!f.closest('[data-product-single-media-group]'),
                                                             shown: getComputedStyle(f).display !== 'none' } : null,
             rating: r ? r.textContent.trim() : null, starColor: r ? getComputedStyle(r.querySelector('.sf-star svg + svg')).color : null,
             pill: (document.querySelector('.product__icon__text') || {}).textContent || '',
             hScroll: document.documentElement.scrollWidth > window.innerWidth };
  });
  const problems = [];
  if (b.frontrowId && !(b.sticker && b.sticker.h > 40 && b.sticker.onGallery && b.sticker.shown)) problems.push('frontrow badge missing or not on the gallery');
  if (b.sticker) {   // on the first slide only (as on the original store)
    // the gallery's own controls, as a shopper uses them (its Flickity is bundled, not on window)
    const shown = () => s.page.evaluate(() => getComputedStyle(document.getElementById('frontrow-sticker')).display !== 'none');
    const thumbs = s.page.locator('[data-product-thumbnail], .product-single__thumbnail, [data-thumbnail-id]');
    await thumbs.nth(1).click({ force: true });
    await s.page.waitForTimeout(1000); b.sticker.onSlide2 = await shown();
    await thumbs.nth(0).click({ force: true });
    await s.page.waitForTimeout(1000); b.sticker.backOnSlide1 = await shown();
    if (b.sticker.onSlide2 || !b.sticker.backOnSlide1) problems.push(`first-slide-only broken: slide2=${b.sticker.onSlide2} slide1=${b.sticker.backOnSlide1}`);
  }
  if (!b.rating) problems.push('no star rating');
  if (b.hScroll) problems.push('page scrolls sideways');
  await s.page.evaluate(() => window.scrollTo(0, 0));
  await s.page.waitForTimeout(500);
  await s.page.screenshot({ path: path.join(SHOTS, 'badges.png') });
  if (b.sticker) {   // the badge opens FrontrowMD's clinicians and FAQ
    await s.page.frameLocator('#frontrow-sticker').locator('text=/learn more/i').first().click({ timeout: 10000 }).catch(e => problems.push('badge click: ' + e.message.slice(0, 80)));
    await s.page.waitForTimeout(3000);
    b.modalOpen = await s.page.evaluate(() => [...document.querySelectorAll('iframe.iframe.frontrow')].some(f => getComputedStyle(f).display !== 'none'));
    if (!b.modalOpen) problems.push('badge click opened nothing');
    await s.page.screenshot({ path: path.join(SHOTS, 'badges-modal.png') });
  }
  out.push({ case: 'badges', ...b, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// the product page story: problem -> solution, the dermatologist, customer reviews before the FAQ, the refill FAQ
{
  const s = await session();
  const st = await s.page.evaluate(() => {
    const ids = [...document.querySelectorAll('[id^="shopify-section-"]')].map(e => e.id);
    const at = k => ids.findIndex(i => i.includes(k));
    const faq = [...document.querySelectorAll('.accordion__item__title__text')].map(e => e.textContent.trim());
    return { reviews1: at('kopstorm_testomonials'), problem: at('sf-problem-solution'), derm: at('sf-dermatologist'),
             reviews2: at('sf-reviews'), faq: at('section_accordions'), faqItems: faq.length,
             refillsFaq: faq.includes('How do Automatic Refills work?') && faq.includes('Can I buy just once?'),
             dermName: (document.querySelector('#sf-dermatologist .sfx-sign b') || {}).textContent || '',
             spfInQuote: /has SPF/i.test((document.querySelector('#sf-dermatologist') || {}).textContent || '') };
  });
  const problems = [];
  if (!(st.reviews1 >= 0 && st.reviews1 < st.problem && st.problem < st.derm && st.derm < st.reviews2 && st.reviews2 < st.faq))
    problems.push('sections missing or out of order: ' + JSON.stringify(st));
  if (!st.refillsFaq) problems.push('refill questions missing from the FAQ');
  if (st.spfInQuote) problems.push('SPF claim in the dermatologist quote');
  out.push({ case: 'product page story', ...st, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// the review wall: NEXT's reviews as valid JSON, Write a review linked to NEXT's form, after the FAQ, shown only when
// there are reviews (the imported ones load when the wall scrolls into view)
{
  const s = await session();
  await s.page.locator('#sf-review-wall-sentinel').scrollIntoViewIfNeeded().catch(() => {});
  await s.page.waitForTimeout(2500);
  const w = await s.page.evaluate(() => {
    const root = document.getElementById('sf-review-wall');
    if (!root) return { present: false };
    let native = null;
    try { native = JSON.parse(root.querySelector('[data-sf-native-reviews]').textContent); } catch (e) {}
    const ids = [...document.querySelectorAll('[id^="shopify-section-"]')].map(e => e.id);
    const section = root.closest('[id^="shopify-section-"]');
    return { present: true, native: native && { write: native.write, reviews: native.reviews.length },
             imported: root.dataset.src ? (window.SFReviewsData ? (window.SFReviewsData.summary ? +window.SFReviewsData.summary.count : window.SFReviewsData.reviews.length) : 'not loaded') : 0,
             shown: !root.hidden, cards: root.querySelectorAll('.sfr-card').length,
             summary: ((root.querySelector('[data-sfr-avg]') || {}).innerText || '').replace(/\s+/g, ' '),
             badge: (document.querySelector('.sf-rating__text') || {}).textContent || '',
             strip: ((document.querySelector('#shopify-section-sf-review-strip .sfrs-sum') || {}).innerText || '').replace(/\s+/g, ' '),
             stripCards: document.querySelectorAll('#shopify-section-sf-review-strip .sfrs-card').length,
             names: /smooche|solena/i.test(root.innerText),
             afterFaq: ids.findIndex(i => i.includes('section_accordions')) < ids.indexOf(section && section.id),
             write: (root.querySelector('.sfr-write:not([hidden])') || {}).href || '' };
  });
  const problems = [];
  if (!w.present) problems.push('no review wall');
  else {
    if (!w.native) problems.push('NEXT reviews JSON does not parse');
    else if (!/\/reviews\/add\//.test(w.native.write)) problems.push('no Write a review link: ' + w.native.write);
    if (w.imported === 'not loaded') problems.push('imported reviews did not load');
    const total = (w.native ? w.native.reviews : 0) + (typeof w.imported === 'number' ? w.imported : 0);
    if (w.shown !== total > 0) problems.push(`wall shown=${w.shown} with ${total} reviews`);
    if (total > 0 && (!w.cards || !w.write)) problems.push(`wall shown without cards (${w.cards}) or write link`);
    if (!w.afterFaq) problems.push('wall is not after the FAQ');
    // one total everywhere: the wall's summary, the badge under the title and the strip after the buy box
    if (total > 0) {
      const n = total.toLocaleString('en-US');
      if (!w.summary.includes(n)) problems.push(`wall summary "${w.summary}" lacks ${n}`);
      if (w.badge && !w.badge.includes(n)) problems.push(`badge "${w.badge}" lacks ${n}`);
      if (w.imported && (!w.strip.includes(n) || w.stripCards < 3)) problems.push(`strip "${w.strip}" (${w.stripCards} cards)`);
    }
    if (w.names) problems.push('another brand named in the reviews');
  }
  // NEXT's own review form, styled inside the SKINOFAB chrome
  if (w.native && w.native.write) {
    await s.page.goto(new URL(w.native.write, STORE).href + (w.native.write.includes('?') ? '&' : '?') + `preview_theme=${THEME}`, { waitUntil: 'domcontentloaded' });
    w.form = await s.page.evaluate(() => {
      const f = [...document.querySelectorAll('#main-content form')].find(x => x.querySelector('[name="body"]'));
      if (!f) return null;
      const field = f.querySelector('[name="title"]');
      return { fields: ['name', 'email', 'title', 'score', 'body'].filter(n => f.querySelector(`[name="${n}"]`)),
               border: field ? getComputedStyle(field).borderTopWidth : '' };
    });
    if (!w.form) problems.push('review form not found');
    else if (!w.form.fields.includes('body') || !w.form.fields.includes('score')) problems.push('review form fields: ' + w.form.fields);
    else if (w.form.border === '0px') problems.push('review form fields have no border');
  }
  out.push({ case: 'review wall', ...w, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// a drawer add-on
{
  const s = await session();
  await choose(s, '2');
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
  if (before.addons[0] !== 'The Lymphatic Brush') problems.push('first add-on is not the brush: ' + before.addons[0]);
  const addon = ls.find(l => /lymphatic brush/i.test(l.title || ''));
  if (addon && addon.interval) problems.push(`the brush add-on is a ${addon.interval} plan`);
  await s.page.screenshot({ path: path.join(SHOTS, 'drawer-addon.png') });
  out.push({ case: 'drawer add-on', before: before.addons, after: after.addons, lines: ls, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// ---------------------------------------------------------------- the Lymphatic Brush
const brushPacks = await (async () => {
  const s = await session(1440, 900, BRUSH);
  const t = JSON.parse(await s.page.getAttribute(picker, 'data-packs'));
  await s.ctx.close();
  return t;
})();
async function chooseBundle(s, key) {
  const box = s.page.locator(picker);
  await box.scrollIntoViewIfNeeded();
  await box.locator(`input[name=sf_pack][value="${key}"]`).check({ force: true });
  return s.page.evaluate(sel => {
    const form = document.querySelector(sel).closest('form');
    return { id: form.querySelector('input[name=id]').value, button: form.querySelector('[data-add-to-cart]').textContent.replace(/\s+/g, ' ').trim() };
  }, picker);
}
for (const [key, pack] of Object.entries(brushPacks)) {
  const s = await session(1440, 900, BRUSH);
  const ui = await chooseBundle(s, key);
  const problems = [];
  if (ui.id !== String(pack.pk)) problems.push(`form id ${ui.id} != ${pack.pk}`);
  if (!ui.button.includes(money(pack.price))) problems.push(`button "${ui.button}" lacks ${money(pack.price)}`);
  await addToCart(s);
  const ls = lines(s.cart);
  if (ls.length !== 1) problems.push(`${ls.length} lines`);
  problems.push(...checkLine(ls[0], { pk: pack.pk, price: pack.price, refill: false }));
  const d = await drawerState(s);
  if (!d.open) problems.push('drawer did not open');
  if (d.upgrade !== (key === '1')) problems.push(`upgrade shown=${d.upgrade}`);
  if (d.addons.includes('The Lymphatic Brush')) problems.push('brush offered as an add-on while in the bag');
  if (d.addons.length < 1) problems.push('no add-ons');
  if (d.planTalk) problems.push('drawer has plan talk');
  let co = null;
  if (key === '2') {
    co = await checkout(s, 'brush-2', 'Lymphatic Brush');
    if (!co.hasLine) problems.push('checkout has no brush line');
    if (!co.prices.includes('$' + pack.price.toFixed(2))) problems.push(`checkout prices ${co.prices} lack $${pack.price.toFixed(2)}`);
    if (co.refillWords.length) problems.push('checkout talks about a plan: ' + co.refillWords[0]);
  }
  out.push({ case: `brush ${key}`, ui, line: ls[0], drawer: { upgrade: d.upgrade, addons: d.addons }, checkout: co, errors: s.errors,
             ok: problems.length === 0, problems });
  await s.ctx.close();
}
{
  const s = await session(1440, 900, BRUSH);
  await chooseBundle(s, '1');
  await addToCart(s);
  const problems = [];
  const btn = s.page.locator(`${drawer} [data-sf-upgrade]`);
  if (!(await btn.count())) problems.push('no upgrade button');
  else { await btn.first().click(); await s.page.waitForTimeout(7000); }
  const ls = lines(s.cart);
  if (ls.length !== 1) problems.push(`${ls.length} lines after the upgrade`);
  problems.push(...checkLine(ls[0], { pk: brushPacks['2'].pk, price: brushPacks['2'].price, refill: false }));
  const d = await drawerState(s);
  if (d.upgrade) problems.push('upgrade still offered');
  await s.page.screenshot({ path: path.join(SHOTS, 'drawer-brush-upgrade.png') });
  out.push({ case: 'brush upgrade 1 -> 2', lines: ls, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}
{
  const s = await session(1440, 900, BRUSH);
  await s.page.locator('#sf-review-wall-sentinel').scrollIntoViewIfNeeded().catch(() => {});
  await s.page.waitForTimeout(2000);
  const pg = await s.page.evaluate(() => {
    const ids = [...document.querySelectorAll('main > [id^="shopify-section-"]')].map(e => e.id.replace(/shopify-section-(template--\d+__)?/, ''));
    const tabs = [...document.querySelectorAll('.product__accordions #accordionbefore')].map(e => e.textContent.trim());
    const head = document.querySelector('.product__price-and-badge');
    let native = { reviews: [] };
    try { native = JSON.parse(document.querySelector('[data-sf-native-reviews]').textContent); } catch (e) {}
    const text = document.body.innerText, chips = document.querySelector('.sfb-chips'), cross = document.querySelector('#sfb-cross');
    const empty = document.getElementById('sfb-no-reviews');
    return { ids, tabs, video: !!document.querySelector('.sfb-routine__video video source[src*=".mp4"]'),
             faq: document.querySelectorAll('#shopify-section-sf-brush-faq .accordion__item').length,
             gallery: document.querySelectorAll('[data-product-single-media-slider] [data-product-single-media-wrapper]').length,
             chips: !!chips && chips.getBoundingClientRect().height > 0, lead: !!document.querySelector('.sfb-lead'),
             claims: (text.match(/drain|5,000|Nicole|10 years|Anti-Cellulite|sculpted|water retention/gi) || []),
             cross: cross ? { href: (cross.querySelector('a.sfb-btn') || {}).pathname || '', rating: (cross.querySelector('.sfb-cross__rating') || {}).textContent || '' } : null,
             empty: !!empty && !empty.hidden,
             now: head.querySelector('.product__price--regular').textContent.trim(), was: head.querySelector('.product__price--compare').textContent.trim(),
             solena: /solena/i.test(document.documentElement.outerHTML), afterpay: !!document.querySelector('skinofab-installments'),
             reviews: native.reviews.length, stars: !document.querySelector('[data-sfb-rating]').hidden, wall: !document.getElementById('sf-review-wall').hidden,
             clips: document.querySelectorAll('.sfb-video video').length, hScroll: document.documentElement.scrollWidth > innerWidth + 1 };
  });
  const problems = [];
  const order = ['main', 'sf-brush-routine', 'sf-brush-videos', 'sf-brush-how', 'sf-brush-expect', 'sf-brush-compare', 'sf-brush-cross',
                 'sf-brush-faq', 'sf-brush-risk-free', 'sf-review-wall'];
  if (order.some((k, i) => pg.ids.indexOf(k) < 0 || (i && pg.ids.indexOf(k) < pg.ids.indexOf(order[i - 1])))) problems.push('sections: ' + pg.ids.join(','));
  if (pg.tabs.length !== 4 || pg.tabs[0] !== 'How to clean it') problems.push('tabs: ' + pg.tabs.join(' | '));
  if (!pg.video) problems.push('no how-to video in the routine');
  if (pg.faq !== 10) problems.push(`${pg.faq} FAQ answers`);
  if (pg.gallery !== 5) problems.push(`${pg.gallery} gallery images`);
  if (!pg.chips || !pg.lead) problems.push(`chips ${pg.chips} / lead ${pg.lead}`);
  if (pg.claims.length) problems.push('claims back on the page: ' + pg.claims.join(', '));
  if (!pg.cross || !pg.cross.href.includes('adaptive-peptide-foundation') || !/\d\.\d\/5 from [\d,]+ verified reviews/.test(pg.cross.rating))
    problems.push('foundation cross-sell: ' + JSON.stringify(pg.cross));
  if (pg.empty === (pg.reviews > 0)) problems.push(`"No reviews yet" box ${pg.empty} with ${pg.reviews} reviews`);
  if (!/^\$24\.95/.test(pg.now) || !/^\$49\.90/.test(pg.was)) problems.push(`title price ${pg.now} / ${pg.was}`);
  if (pg.solena) problems.push('"Solena" on the page');
  if (pg.afterpay) problems.push('pay-in-4 line shown');
  if (pg.stars !== (pg.reviews > 0) || pg.wall !== (pg.reviews > 0)) problems.push(`stars ${pg.stars} / wall ${pg.wall} with ${pg.reviews} reviews`);
  if (pg.clips !== 4) problems.push(`${pg.clips} creator clips`);
  if (pg.hScroll) problems.push('page scrolls sideways');
  // the homepage section and the menu link
  await s.page.goto(`${STORE}/`, { waitUntil: 'networkidle', timeout: 90000 });
  const home = await s.page.evaluate(() => {
    const shelf = document.querySelector('[id$="__bestsellers"]');
    const has = el => !!el && [...el.querySelectorAll('article h3 a')].some(a => a.pathname.includes('the-lymphatic-brush'));
    return {
      section: !!document.querySelector('[id$="__brush"]'),
      list: has(shelf && shelf.querySelector('.fh-product-list')),
      tabs: ['bestsellers_0', 'bestsellers_1', 'bestsellers_2'].filter(k => has(shelf && shelf.querySelector(`[data-fh-panel="${k}"]`))),
      price: ((shelf && [...shelf.querySelectorAll('.fh-product-list article')].find(a => /Lymphatic Brush/.test(a.textContent))) || {}).innerText || '',
      menu: [...document.querySelectorAll('a')].filter(a => /^\s*Lymphatic Brush\s*$/i.test(a.textContent)).map(a => a.pathname)
    };
  });
  if (home.section) problems.push('the homepage still has a brush section');
  if (!home.list || home.tabs.length !== 3) problems.push(`homepage shelf: list ${home.list}, tabs ${home.tabs.join(',')}`);
  if (!/\$24\.95/.test(home.price)) problems.push('shelf card price: ' + home.price.replace(/\s+/g, ' ').slice(0, 80));
  if (!home.menu.length || home.menu.some(p => !p.includes('the-lymphatic-brush'))) problems.push('menu links: ' + home.menu.join(','));
  out.push({ case: 'brush page', ...pg, home, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// the sticky bar on both product pages: hidden at the top, shown once the add-to-cart button has scrolled away, and
// its button brings the pack picker back into view
for (const [name, route] of [['foundation', PDP], ['brush', BRUSH]]) for (const [w, h] of [[390, 844], [1440, 900]]) {
  const s = await session(w, h, route);
  const on = () => s.page.evaluate(() => { const b = document.getElementById('sf-sticky'); return b ? b.classList.contains('is-on') : null; });
  const problems = [];
  const atTop = await on();
  await s.page.evaluate(() => window.scrollTo(0, 3000)); await s.page.waitForTimeout(900);
  const scrolled = await on();
  if (atTop !== false) problems.push(`at the top: ${atTop}`);
  if (scrolled !== true) problems.push(`after scrolling: ${scrolled}`);
  if (scrolled) {
    await s.page.click('#sf-sticky a'); await s.page.waitForTimeout(1500);
    const r = await s.page.evaluate(() => { const e = document.getElementById('apf-buy').getBoundingClientRect(); return [e.top, e.bottom, innerHeight]; });
    if (r[0] > r[2] || r[1] < 0) problems.push('picker not in view after the sticky button: ' + r.map(Math.round).join(','));
  }
  out.push({ case: `sticky bar ${name} ${w}`, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// mobile buy box and drawer, for the eye
{
  const s = await session(390, 844);
  await choose(s, '2');
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
