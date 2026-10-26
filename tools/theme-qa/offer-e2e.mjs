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
// The Lymphatic Brush, the PDRN Plumping Balm, the EGF + NAD+ Firming Serum and the Adaptive Foundation Stick
// (brush_copy.py / balm_copy.py / serum_copy.py / stick_copy.py BUNDLES; optional 5th to 8th arguments, their page paths):
//   buy: each bundle adds its variant at its price, one-time; the drawer offers the 1 -> 2 upgrade only for one, and
//        never the product as an add-on while it is in the bag; checkout shows the 2-pack with its thumbnail.
//   upgrade: 1 -> 2 in the drawer: one line, one-time.
//   page: the foundation page's sections in the foundation's order (tools/persona/twin.py), its six tabs, the
//        product's FAQ; no other product's reviews while it has none of its own, photo cards without stars or "verified", the
//        expert block signed by the brand, before/after photos marked as illustrations; no competitor name or dropped
//        claim, no broken image after scrolling the whole page, the title price (no "was" on one stick), no stars
//        without reviews; its card in the homepage shelf (default list, Bestsellers, New and Face tabs) at its
//        single price ($24.95; the serum $34.95; the stick $39), and the menu links lead to it.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path';

const [STORE, THEME, PDP, SHOTS, BRUSH = '/catalogue/the-lymphatic-brush_169/', BALM = '/catalogue/pdrn-plumping-balm_202/',
       SERUM = '/catalogue/egf-nad-firming-serum_206/', STICK = '/catalogue/adaptive-foundation-stick_235/'] = process.argv.slice(2);
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
  const every = want.every || 28;
  if (want.refill && !(String(line.interval).toLowerCase().startsWith('day') && line.intervalCount === every)) p.push(`not a ${every}-day refill: ${line.interval} ${line.intervalCount}`);
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
             now: head.querySelector('.product__price--regular').textContent.trim(),
             // the crossed-out price as shown: empty when hidden (the theme's own price script hid it, build 39)
             was: (w => w && w.getClientRects().length ? w.textContent.trim() : '')(head.querySelector('.product__price--compare')),
             cards: [...root.querySelectorAll('.sfo-card')].map(c => c.querySelector('[data-sfo-now]').textContent + ' ' + c.querySelector('[data-sfo-save]').textContent),
             pct: pct ? pct.textContent : null, termsShown: !!terms && !terms.hidden, terms: terms ? terms.textContent : '' };
  }, picker);
}

async function drawerState(s) {
  return s.page.evaluate(sel => {
    const r = document.querySelector(sel).shadowRoot, text = r.querySelector('.spark-drawer-panel').innerText.replace(/\s+/g, ' ');
    return { open: getComputedStyle(r.querySelector('.spark-drawer-panel')).visibility !== 'hidden', text: text.slice(0, 900),
             upgrade: !!r.querySelector('.sf-upgrade-btn[data-sf-upgrade]'), plus: !!r.querySelector('.spark-drawer-qty-btn[data-sf-upgrade]'), addons: [...r.querySelectorAll('.sf-upsell-name')].map(a => a.textContent),
             review: !!r.querySelector('.sf-review'), guarantee: !!r.querySelector('.spark-drawer-footer .sf-guarantee, .sf-guarantee'), pay: r.querySelectorAll('.sf-pay img').length,
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
  // a new product's line thumbnail is resized on first view: wait for it before the screenshot
  await s.page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0), null, { timeout: 20000 }).catch(() => {});
  const text = await s.page.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  const thumbs = await s.page.evaluate(() => [...document.images].filter(i => !/\.svg/.test(i.currentSrc || i.src)).map(i => i.naturalWidth));
  await s.page.screenshot({ path: path.join(SHOTS, `checkout-${name}.png`), fullPage: true });
  return { status: resp && resp.status(), hasLine: text.toLowerCase().includes(product.toLowerCase()),
           pack: (text.match(/(1 bottle|2 bottles \+ free gifts|1 brush \+ free case|2 brushes \+ 2 free cases|3 brushes \+ 3 free cases \+ free body brush|1 stick|2 sticks|3 sticks \(buy 2, get 1 free\))/i) || [])[0] || null,
           refillWords: (text.match(/[^.$]{0,40}(every\s+\d+\s+days?|subscri|recurring|renew)[^.$]{0,40}/gi) || []).slice(0, 3),
           thumbs, prices: (text.match(/\$\d+\.\d\d/g) || []).slice(0, 6) };
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
    const wantWas = pack.compare > want.price ? money(pack.compare) : '';
    if (wantWas ? !ui.was.startsWith(wantWas) : ui.was) problems.push(`title compare shown "${ui.was}" != "${wantWas}"`);
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
  await s.page.locator(`${drawer} .sf-upgrade-btn[data-sf-upgrade]`).click();
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

// the product page story: problem -> solution, the Korean doctor photo (a model, no endorsement; no dermatologist
// block), customer reviews before the FAQ (the owner's request of 25 Oct), the refill FAQ
{
  const s = await session();
  const st = await s.page.evaluate(() => {
    const ids = [...document.querySelectorAll('[id^="shopify-section-"]')].map(e => e.id);
    const at = k => ids.findIndex(i => i.includes(k));
    const faq = [...document.querySelectorAll('.accordion__item__title__text')].map(e => e.textContent.trim());
    return { reviews1: at('kopstorm_testomonials'), problem: at('sf-problem-solution'), derm: at('sf-dermatologist'), korea: at('sf-korea'),
             reviews2: at('sf-reviews'), faq: at('section_accordions'), faqItems: faq.length,
             refillsFaq: faq.includes('How do Automatic Refills work?') && faq.includes('Can I buy just once?'),
             dermName: (document.querySelector('#sf-dermatologist .sfx-sign b') || {}).textContent || '',
             spfInQuote: /has SPF/i.test((document.querySelector('#sf-dermatologist') || {}).textContent || '') };
  });
  const problems = [];
  if (!(st.reviews1 >= 0 && st.reviews1 < st.problem && st.problem < st.korea && st.korea < st.reviews2 && st.reviews2 < st.faq && st.derm === -1))
    problems.push('sections missing or out of order: ' + JSON.stringify(st));
  if (!st.refillsFaq) problems.push('refill questions missing from the FAQ');
  if (st.spfInQuote) problems.push('SPF claim in the dermatologist quote');
  out.push({ case: 'product page story', ...st, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// the review wall: NEXT's reviews as valid JSON, Write a review linked to NEXT's form, before the FAQ, shown only when
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
             beforeFaq: ids.indexOf(section && section.id) < ids.findIndex(i => i.includes('section_accordions')),
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
    if (!w.beforeFaq) problems.push('wall is not before the FAQ');
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

// ---------------------------------------------------------------- the second products' bundles (brush, balm, serum, stick)
async function packsOf(route) {
  const s = await session(1440, 900, route);
  const t = JSON.parse(await s.page.getAttribute(picker, 'data-packs'));
  await s.ctx.close();
  return t;
}
async function chooseBundle(s, key) {
  const box = s.page.locator(picker);
  await box.scrollIntoViewIfNeeded();
  await box.locator(`input[name=sf_pack][value="${key}"]`).check({ force: true });
  return s.page.evaluate(sel => {
    const form = document.querySelector(sel).closest('form');
    return { id: form.querySelector('input[name=id]').value, button: form.querySelector('[data-add-to-cart]').textContent.replace(/\s+/g, ' ').trim() };
  }, picker);
}
// each bundle: its variant and price, one-time, the drawer (its 1 -> 2 upgrade only for one, never itself as an
// add-on), checkout for the 2-pack; then the drawer upgrade 1 -> 2. to3: the 2-pack is offered 2 -> 3 as well (the
// stick, stick review 5), and the upgraded bag then takes it
async function bundleCases(name, route, title, label, refills = false, to3 = false) {
  const packs = await packsOf(route);
  const want = pack => (refills ? { price: pack.refill, refill: true, every: pack.every } : { price: pack.price, refill: false });
  for (const [key, pack] of Object.entries(packs)) {
    const s = await session(1440, 900, route);
    const ui = await chooseBundle(s, key);
    const problems = [];
    if (ui.id !== String(pack.pk)) problems.push(`form id ${ui.id} != ${pack.pk}`);
    if (!ui.button.includes(money(want(pack).price))) problems.push(`button "${ui.button}" lacks ${money(want(pack).price)}`);
    await addToCart(s);
    const ls = lines(s.cart);
    if (ls.length !== 1) problems.push(`${ls.length} lines`);
    problems.push(...checkLine(ls[0], { pk: pack.pk, ...want(pack) }));
    const d = await drawerState(s);
    if (!d.open) problems.push('drawer did not open');
    if (d.upgrade !== (key === '1' || (to3 && key === '2'))) problems.push(`upgrade shown=${d.upgrade}`);
    // a line of one pack that has a bigger pack above it: its "+" moves it up a pack instead of adding a second line
    if (d.plus !== d.upgrade) problems.push(`"+" upgrades=${d.plus}, banner=${d.upgrade}`);
    if (d.addons.includes(title)) problems.push(`${title} offered as an add-on while in the bag`);
    if (d.addons.length < 1) problems.push('no add-ons');
    if (d.planTalk) problems.push('drawer has plan talk');
    let co = null;
    if (key === '2') {
      co = await checkout(s, `${name}-2`, label);
      if (!co.hasLine) problems.push(`checkout has no ${name} line`);
      if (!co.prices.includes('$' + want(pack).price.toFixed(2))) problems.push(`checkout prices ${co.prices} lack $${want(pack).price.toFixed(2)}`);
      if (!refills && co.refillWords.length) problems.push('checkout talks about a plan: ' + co.refillWords[0]);
      if (refills && !co.refillWords.length) problems.push('checkout does not say the refill cadence');
      if (!co.thumbs.length || co.thumbs.some(w => !w)) problems.push(`checkout line thumbnail missing (${co.thumbs})`);
    }
    out.push({ case: `${name} ${key}`, ui, line: ls[0], drawer: { upgrade: d.upgrade, addons: d.addons }, checkout: co, errors: s.errors,
               ok: problems.length === 0, problems });
    await s.ctx.close();
  }
  const s = await session(1440, 900, route);
  await chooseBundle(s, '1');
  await addToCart(s);
  const problems = [];
  const btn = s.page.locator(`${drawer} .sf-upgrade-btn[data-sf-upgrade]`);
  if (!(await btn.count())) problems.push('no upgrade button');
  else { await btn.first().click(); await s.page.waitForTimeout(7000); }
  const ls = lines(s.cart);
  if (ls.length !== 1) problems.push(`${ls.length} lines after the upgrade`);
  problems.push(...checkLine(ls[0], { pk: packs['2'].pk, ...want(packs['2']) }));
  const d = await drawerState(s);
  if (d.upgrade !== to3) problems.push(`upgrade offered after 1 -> 2: ${d.upgrade}`);
  await s.page.screenshot({ path: path.join(SHOTS, `drawer-${name}-upgrade.png`) });
  out.push({ case: `${name} upgrade 1 -> 2`, lines: ls, errors: s.errors, ok: problems.length === 0, problems });
  if (to3 && d.upgrade) {
    const p3 = [];
    await s.page.locator(`${drawer} .sf-upgrade-btn[data-sf-upgrade]`).first().click(); await s.page.waitForTimeout(7000);
    const l3 = lines(s.cart);
    if (l3.length !== 1) p3.push(`${l3.length} lines after the upgrade`);
    p3.push(...checkLine(l3[0], { pk: packs['3'].pk, ...want(packs['3']) }));
    if ((await drawerState(s)).upgrade) p3.push('an upgrade still offered with the 3-pack in the bag');
    await s.page.screenshot({ path: path.join(SHOTS, `drawer-${name}-upgrade-3.png`) });
    out.push({ case: `${name} upgrade 2 -> 3`, lines: l3, errors: s.errors, ok: p3.length === 0, problems: p3 });
  }
  await s.ctx.close();
  // the "+" on a single pack: one line of the next pack up at its price, not two lines of one
  const q = await session(390, 844, route), pq = [];
  await chooseBundle(q, '1');
  await addToCart(q);
  const plus = q.page.locator(`${drawer} .spark-drawer-qty-btn[data-sf-upgrade]`);
  if (!(await plus.count())) pq.push('no "+" upgrade on the single pack');
  else { await plus.first().click(); await q.page.waitForTimeout(7000); }
  const lq = lines(q.cart);
  if (lq.length !== 1) pq.push(`${lq.length} lines after "+"`);
  pq.push(...checkLine(lq[0], { pk: packs['2'].pk, ...want(packs['2']) }));
  await q.page.screenshot({ path: path.join(SHOTS, `drawer-${name}-plus.png`) });
  out.push({ case: `${name} "+" 1 -> 2`, lines: lq, errors: q.errors, ok: pq.length === 0, problems: pq });
  await q.ctx.close();
}
await bundleCases('brush', BRUSH, 'The Lymphatic Brush', 'Lymphatic Brush');
// the balm, serum and stick sell with Automatic Refills on by default (26 Oct 2026): every pack adds as a refill at
// its refill price, every its own days; the brush is one-time only
await bundleCases('balm', BALM, 'PDRN Plumping Balm', 'PDRN Plumping Balm', true);
await bundleCases('serum', SERUM, 'EGF + NAD+ Firming Serum', 'EGF + NAD+ Firming Serum', true);
await bundleCases('stick', STICK, 'Adaptive Foundation Stick', 'Adaptive Foundation Stick', true, true);

// ---------------------------------------------------------------- the brush's, the balm's, the serum's and the stick's pages
// All are built on the foundation page's structure (tools/persona/twin.py): the same sections in the same order (the
// expert block is the brand's own note; the review wall adds an honest "no reviews yet" box while there are none),
// the foundation's six tabs, the product's FAQ. Borrowed reviews must say they are the foundation's; the photo cards
// are not reviews (no stars, no "verified"); before/after photos are marked as illustrations.
const sectionKeys = () => [...document.querySelectorAll('main > [id^="shopify-section-"]')]
  .map(e => e.id.replace(/^shopify-section-(template--\d+__)?/, '').replace(/_[A-Za-z0-9]{4,}$/, '').replace(/^sf-(brush|balm|serum|stick)-(no-reviews|amazon)$/, '$2'))
  .filter(k => !/^(section_custom_html|\d+[0-9a-f]+)$/.test(k));
async function scrollThrough(page) {
  const h = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < h; y += 700) { await page.evaluate(v => window.scrollTo(0, v), y); await page.waitForTimeout(120); }
  await page.waitForTimeout(2500);
}
const foundationKeys = await (async () => {
  const s = await session(1440, 900, PDP);
  const keys = await s.page.evaluate(sectionKeys);
  await s.ctx.close();
  return keys.map(k => (k === 'sf-dermatologist' ? 'sf-note' : k));
})();
async function twinPage(name, route, cfg) {
  const s = await session(1440, 900, route);
  await scrollThrough(s.page);
  const pg = await s.page.evaluate(([keysSrc, claimsSrc]) => {
    const keys = new Function('return (' + keysSrc + ')')()();
    const tabs = [...document.querySelectorAll('.product__accordions .sf-acctitle')].map(e => e.textContent.trim());
    const head = document.querySelector('.product__price-and-badge');
    let native = { reviews: [] };
    try { native = JSON.parse(document.querySelector('[data-sf-native-reviews]').textContent); } catch (e) {}
    const text = document.body.innerText, empty = document.getElementById('sfb-no-reviews');
    const strip = document.querySelector('#shopify-section-sf-review-strip');
    const moments = document.querySelector('[id*="__kopstorm_testomonials_"]');
    const faqSec = document.querySelector('[id*="__section_accordions_"]');
    return { keys, tabs, faq: faqSec ? faqSec.querySelectorAll('.accordion__item').length : 0,
             gallery: document.querySelectorAll('[data-product-single-media-slider] [data-product-single-media-wrapper]').length,
             chips: !!document.querySelector('.sfb-chips'), lead: !!document.querySelector('.sfb-lead'),
             title: (document.querySelector('.product__title') || {}).textContent || '',
             // the page's own words (a review wall of another product's buyers is theirs, not a claim of the page)
             claims: text.replace((document.getElementById('sf-review-wall') || {}).innerText || '', '').match(new RegExp(claimsSrc, 'gi')) || [],
             strip: strip ? strip.innerText.replace(/\s+/g, ' ') : '',
             momentsReviewish: moments ? moments.querySelectorAll('.skinofab-testimonials__stars, .skinofab-testimonials__verified').length : -1,
             moments: moments ? moments.querySelectorAll('.swiper-slide').length : 0,
             note: (document.querySelector('#sf-note .sfx-sign b') || {}).textContent || '', derm: !!document.getElementById('sf-dermatologist'),
             beforeAfter: [...document.querySelectorAll('main img')].filter(i => /before and after/i.test(i.alt)).map(i => i.alt),
             clips: document.querySelectorAll('#sf-video-reviews video source[src*=".mp4"]').length,
             cards: document.querySelectorAll('#sf-video-reviews .sfx-review').length,
             empty: !!empty && !empty.hidden, now: head.querySelector('.product__price--regular').textContent.trim(),
             was: (w => w && w.getClientRects().length ? w.textContent.trim() : '')(head.querySelector('.product__price--compare')),
             competitor: /solena|fem\+|femplus|meimei|facelove/i.test(document.documentElement.outerHTML), reviews: native.reviews.length,
             announce: ((document.querySelector('.announcement .text-highlight__break') || {}).textContent || '').trim(),
             stars: !document.querySelector('[data-sfb-rating]').hidden, hScroll: document.documentElement.scrollWidth > innerWidth + 1,
             // under the trust row, as on the foundation: free shipping and the boxed 30-day guarantee (stick review 5)
             assure: (() => { const a = document.querySelector('.sfb-assure'), t = document.querySelector('.sfp-trust');
               return !!a && !!a.querySelector('.sfb-guarantee') && /Free shipping/.test(a.textContent) && !!t
                 && !!(t.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING); })(),
             // another product's FrontrowMD listing: in a box under the add-to-cart button, the line naming whose first
             frontrow: (() => { const b = document.querySelector('.sfb-frontrow'), a = document.querySelector('form[data-product-form] [data-add-to-cart]');
               if (!b || !a) return null; const note = b.querySelector('.sfb-frontrow-note'), badge = b.querySelector('.sfb-frontrow__badge');
               return { belowAtc: b.getBoundingClientRect().top >= a.getBoundingClientRect().bottom - 1,
                        noteFirst: !!(note && badge && note.compareDocumentPosition(badge) & Node.DOCUMENT_POSITION_FOLLOWING) }; })(),
             // images that asked for a file and got none (the review lightbox's empty <img> asks for nothing)
             imgs: [...document.querySelectorAll('main img')].filter(i => i.complete && i.naturalWidth === 0 && (i.getAttribute('src') || i.getAttribute('srcset'))
                                                                     && !/^data:/.test(i.getAttribute('src') || '')).map(i => i.currentSrc || i.src) };
  }, [sectionKeys.toString(), cfg.claims]);
  const problems = [];
  // the foundation's sections, less its own: the Korean doctor photo (its bottle), its review strip while the product
  // has no reviews of its own (borrowed reviews read as this product's), the use cards when the product has none; the
  // brand's own note after the problem/solution, and the honest "no reviews yet" box after the wall
  const own = pg.reviews || cfg.borrowed;       // a page with reviews: its own, or the foundation's labelled (the stick)
  const want = foundationKeys.filter(k => k !== 'sf-korea' && (own || k !== 'sf-review-strip') && (cfg.cards !== 0 || k !== 'sf-reviews'))
    .flatMap(k => (k === 'sf-review-wall' && !own ? [k, 'no-reviews'] : k === 'sf-problem-solution' ? [k, 'sf-note'] : [k]));
  const got = pg.keys.filter(k => k !== 'amazon');
  if (got.join() !== want.join()) problems.push(`sections differ from the foundation's:\n  ${got.join(',')}\n  ${want.join(',')}`);
  if (pg.tabs.length !== 6 || pg.tabs[0] !== 'What makes it different?' || pg.tabs[5] !== 'Shipping and returns') problems.push('tabs: ' + pg.tabs.join(' | '));
  if (pg.faq !== cfg.faq) problems.push(`${pg.faq} FAQ answers`);
  if (pg.gallery !== cfg.gallery) problems.push(`${pg.gallery} gallery images`);
  if (pg.chips || !pg.lead) problems.push(`chips ${pg.chips} / lead ${pg.lead} (the foundation's buy box has a lead, no chips)`);
  if (!pg.title.includes(cfg.title)) problems.push(`title "${pg.title}"`);
  if (pg.claims.length) problems.push('claims or competitor on the page: ' + pg.claims.join(', '));
  if (pg.competitor) problems.push('a competitor name in the markup');
  if (!pg.reviews && !cfg.borrowed && pg.strip) problems.push('another product\'s reviews on the page: ' + pg.strip.slice(0, 120));
  if (cfg.borrowed && !/of our Adaptive Peptide Foundation/.test(pg.strip)) problems.push('borrowed review strip does not say whose: ' + pg.strip.slice(0, 120));
  if (cfg.borrowed && /Verified buyer(?! of the foundation)/.test(pg.strip)) problems.push('a borrowed review card says "Verified buyer" without "of the foundation"');
  if (pg.momentsReviewish !== 0 || pg.moments < 4) problems.push(`photo cards: ${pg.moments}, with ${pg.momentsReviewish} stars/verified marks`);
  if (pg.derm || pg.note !== 'The SKINOFAB team') problems.push(`expert block: dermatologist ${pg.derm}, signed "${pg.note}"`);
  if (!pg.beforeAfter.length || pg.beforeAfter.some(a => !/illustration/i.test(a))) problems.push('before/after not marked as an illustration: ' + pg.beforeAfter.join(' | '));
  if (pg.cards !== (cfg.cards ?? 4) || pg.clips !== cfg.clips) problems.push(`use cards ${pg.cards}, clips ${pg.clips}`);
  if (pg.empty === (pg.reviews > 0 || !!cfg.borrowed)) problems.push(`"No reviews yet" box ${pg.empty} with ${pg.reviews} reviews`);
  const price = cfg.price || '$24.95';
  if (!pg.now.startsWith(price) || (cfg.was ? !pg.was.startsWith(cfg.was) : !!pg.was.trim())) problems.push(`title price ${pg.now} / was "${pg.was}"`);
  if (pg.stars !== (pg.reviews > 0 || !!cfg.borrowed)) problems.push(`stars ${pg.stars} with ${pg.reviews} reviews`);
  if (pg.hScroll) problems.push('page scrolls sideways');
  if (cfg.announce && pg.announce !== cfg.announce) problems.push('announcement: ' + pg.announce);
  if (!cfg.announce && !/Fall Sale/.test(pg.announce)) problems.push('announcement (the store\'s line): ' + pg.announce);
  if (!!cfg.frontrow !== !!pg.frontrow || (pg.frontrow && !(pg.frontrow.belowAtc && pg.frontrow.noteFirst))) problems.push('FrontrowMD box: ' + JSON.stringify(pg.frontrow));
  if (pg.imgs.length) problems.push(`${pg.imgs.length} broken images: ${pg.imgs.slice(0, 3).join(' ')}`);
  if (!pg.assure) problems.push('no free-shipping row and boxed guarantee under the trust row');
  // the homepage shelf card and the menu links
  await s.page.goto(`${STORE}/`, { waitUntil: 'networkidle', timeout: 90000 });
  const home = await s.page.evaluate(([handle, title, nav]) => {
    const shelf = document.querySelector('[id$="__bestsellers"]');
    const has = el => !!el && [...el.querySelectorAll('article h3 a')].some(a => a.pathname.includes(handle));
    return { list: has(shelf && shelf.querySelector('.fh-product-list')),
             tabs: ['bestsellers_0', 'bestsellers_1', 'bestsellers_2'].filter(k => has(shelf && shelf.querySelector(`[data-fh-panel="${k}"]`))),
             price: ((shelf && [...shelf.querySelectorAll('.fh-product-list article')].find(a => a.textContent.includes(title))) || {}).innerText || '',
             menu: [...document.querySelectorAll('a')].filter(a => a.textContent.trim().toLowerCase() === nav.toLowerCase()).map(a => a.pathname) };
  }, [cfg.handle, cfg.title, cfg.nav]);
  if (!home.list || home.tabs.length !== 3) problems.push(`homepage shelf: list ${home.list}, tabs ${home.tabs.join(',')}`);
  // the shelf card shows one pack's price (cfg.shelf), the page's title the default pack's
  if (!home.price.includes(cfg.shelf || price)) problems.push('shelf card price: ' + home.price.replace(/\s+/g, ' ').slice(0, 120));
  if (home.menu.length < 2 || home.menu.some(p => !p.includes(cfg.handle))) problems.push('menu links: ' + home.menu.join(','));
  out.push({ case: `${name} page`, ...pg, home, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}
await twinPage('brush', BRUSH, { title: 'The Lymphatic Brush', handle: 'the-lymphatic-brush', nav: 'The Lymphatic Brush', gallery: 5, faq: 10,
                                 clips: 0, cards: 0, price: '$39.95', was: '$49.90', shelf: '$24.95', claims: 'drain|fluid|5,000|Nicole|10 years|Anti-Cellulite|sculpted|water retention' });
await twinPage('balm', BALM, { title: 'PDRN Plumping Balm', handle: 'pdrn-plumping-balm', nav: 'PDRN Plumping Balm', gallery: 13, faq: 12, clips: 0,
                               price: '$31.95', was: '$49.90', shelf: '$19.95', claims: '96%|1M\\+|bought today|77%|dermatologist|collagen production|clinically' });
await twinPage('serum', SERUM, { title: 'EGF + NAD+ Firming Serum', handle: 'egf-nad-firming-serum', nav: 'EGF + NAD+ Firming Serum', gallery: 13, faq: 12,
                                 clips: 0, was: '$69.90', price: '$47.95', shelf: '$27.95',
                                 claims: '#1 Firming|137,135|10,000\\+|clinically|stimulate collagen|at the source|dermatologist|Madeca|Time Reverse' });
await twinPage('stick', STICK, { title: 'Adaptive Foundation Stick', handle: 'adaptive-foundation-stick', nav: 'Adaptive Foundation Stick',
                                 gallery: 6, faq: 18, clips: 0, was: '$78', price: '$47', shelf: '$31', borrowed: true, frontrow: true,
                                 announce: 'Buy 2, get 1 free · Free shipping · 30-day money-back guarantee',
                                 claims: '97%|93%|50,000|pieces remain|11:59|16 skin tones|anti-aging|reduces redness|clinically|dermatologist|Changing Foundation' });

// the sticky bar on every product page: shown while the add-to-cart button is out of view on a phone or a tablet
// (at the top on a phone the button is below the fold: the bar shows), on a laptop only once the button has scrolled
// up off the screen (shown while it was below, it covered the pack cards, stick review 6); its button brings the
// pack picker back into view
for (const [name, route] of [['foundation', PDP], ['brush', BRUSH], ['balm', BALM], ['serum', SERUM], ['stick', STICK]]) for (const [w, h] of [[390, 844], [1024, 900], [1440, 900]]) {
  const s = await session(w, h, route);
  const on = () => s.page.evaluate(() => { const b = document.getElementById('sf-sticky'); return b ? b.classList.contains('is-on') : null; });
  const problems = [];
  await s.page.waitForTimeout(400);
  const atTop = await on();
  const atcOut = await s.page.evaluate(() => { const b = document.querySelector('form[data-product-form] [data-add-to-cart]') || document.querySelector('#apf-buy');
    const r = b.getBoundingClientRect(); return r.top >= innerHeight || r.bottom <= 0; });
  await s.page.evaluate(() => window.scrollTo(0, 3000)); await s.page.waitForTimeout(900);
  const scrolled = await on();
  if (atTop !== (atcOut && w < 1024)) problems.push(`at the top: bar ${atTop}, add-to-cart out of view ${atcOut} at ${w}`);
  // on the first screen the bar covers neither the title nor the price (stick review 3)
  if (atTop) {
    const cover = await s.page.evaluate(() => { const bar = document.getElementById('sf-sticky'), top = innerHeight - bar.offsetHeight;
      return ['.product__title', '.product__price-and-badge'].map(q => document.querySelector(q)).filter(e => e && e.getBoundingClientRect().bottom > top)
        .map(e => e.className + ' ' + Math.round(e.getBoundingClientRect().bottom) + '>' + Math.round(top)); });
    if (cover.length) problems.push('the sticky bar covers ' + cover.join(', '));
  }
  if (scrolled !== true) problems.push(`after scrolling: ${scrolled}`);
  if (scrolled) {
    await s.page.click('#sf-sticky a'); await s.page.waitForTimeout(1500);
    const r = await s.page.evaluate(() => { const e = document.getElementById('apf-buy').getBoundingClientRect(); return [e.top, e.bottom, innerHeight]; });
    if (r[0] > r[2] || r[1] < 0) problems.push('picker not in view after the sticky button: ' + r.map(Math.round).join(','));
  }
  out.push({ case: `sticky bar ${name} ${w}`, errors: s.errors, ok: problems.length === 0, problems });
  await s.ctx.close();
}

// a failed add says so by the button (store audit 8: the button reset, no bag opened, no word): the cart request
// blocked, the stick page at 390
{
  const s = await session(390, 844, STICK);
  await s.page.route('**/api/graphql/**', r => (/cart/i.test(r.request().postData() || '') ? r.abort('failed') : r.continue()));
  await s.page.click('form[data-sf-product-form] [data-add-to-cart]', { force: true });
  await s.page.waitForTimeout(4000);
  const msg = await s.page.evaluate(() => { const e = document.querySelector('.sf-atc-error'); return e && !e.hidden && e.offsetHeight > 0 ? e.textContent : null; });
  const problems = msg && /try again/.test(msg) ? [] : ['no message after a failed add: ' + msg];
  out.push({ case: 'add to cart failure message', errors: [], ok: problems.length === 0, problems });
  await s.ctx.close();
}

// the cart page's header line: what every order gets, not one product's sale (stick review 4)
{
  const s = await session(390, 844, '/cart/');
  const line = await s.page.evaluate(() => ((document.querySelector('.announcement .text-highlight__break') || {}).textContent || '').trim());
  const want = 'Free shipping on every order · 30-day money-back guarantee';
  out.push({ case: 'cart page announcement', errors: [], ok: line === want, problems: line === want ? [] : ['announcement: ' + line] });
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
