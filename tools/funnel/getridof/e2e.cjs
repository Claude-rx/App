// End-to-end check of the Get Rid Of mouse-pouches funnel against a served _site (default http://localhost:8765).
//   node tools/funnel/getridof/e2e.cjs [baseUrl] [outDir]
// Sales page (build_lp.py): first screen, buy box (3 bundles x subscribe / one-time), every price against the live
// Campaign Cart total on the checkout, ADD TO CART -> checkout URL, sticky bar, FAQ, page weight.
// Checkout: the right package is in the cart; Automatic Refills terms only on a subscription. Places no order.
const { chromium } = require('playwright');
const fs = require('fs');
const base = process.argv[2] || 'http://localhost:8765';
const out = process.argv[3] || '.';
const CHECKOUT = /mouse-pouches(\/|-)checkout\//;
const results = []; const ok = (name, pass, detail = '') => { results.push({ name, pass, detail }); console.log((pass ? 'PASS ' : 'FAIL ') + name + (detail ? '  ' + detail : '')); };
(async () => {
  const b = await chromium.launch();
  for (const vp of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 390, height: 664, isMobile: true, hasTouch: true }]) {
    const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, hasTouch: !!vp.hasTouch });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const external = []; p.on('request', r => { const u = r.url(); if (/^https?:\/\/[^/]*(sofyre\.com|shopify|gemcommerce|kaching)/.test(u)) external.push(u); });
    const resp = await p.goto(base + '/mouse-pouches/?utm_source=test', { waitUntil: 'load' });
    const html = await resp.text();
    await p.waitForTimeout(600);
    ok(`[${vp.name}] page title`, (await p.title()).includes('Get Rid Of'));
    // what the phone downloads is the compressed document (repeated markup costs almost nothing), so that is what is budgeted
    const gz = require('zlib').gzipSync(Buffer.from(html)).length;
    ok(`[${vp.name}] page is lean (HTML under 85 KB compressed, incl. the store's ~28 KB monitoring script)`, gz < 85 * 1024, Math.round(gz / 1024) + ' KB compressed, ' + Math.round(html.length / 1024) + ' KB raw');
    ok(`[${vp.name}] no SoFyre text`, !/sofyre/i.test(html));
    // boxed stars sit in one row everywhere (a stacked column means a display rule broke them)
    const tall = await p.evaluate(() => [...document.querySelectorAll('.sbx')].filter(e => e.offsetParent && e.getBoundingClientRect().height > 44).map(e => (e.parentElement.className || e.parentElement.tagName) + ' ' + Math.round(e.getBoundingClientRect().height)));
    ok(`[${vp.name}] star rows are one line high`, tall.length === 0, tall.join(' | '));
    ok(`[${vp.name}] part of the campaign (next-funnel, page type product)`, /name="next-funnel" content="[^"]+"/.test(html) && /name="next-page-type" content="product"/.test(html) && /campaign-cart@v[\d.]+\/dist\/loader\.js/.test(html));
    const first = await p.evaluate(() => { const vis = s => [...document.querySelectorAll(s)].some(e => { if (e.offsetParent === null && getComputedStyle(e).position !== 'fixed') return false; const r = e.getBoundingClientRect(); return r.height > 0 && r.top >= 0 && r.bottom <= innerHeight + 1; });
      return { h1: vis('h1'), rating: vis('.rate'), atc: vis('[data-gro-atc], a.sn'), img: vis('.gal__t img') || document.querySelector('.gal__t img').getBoundingClientRect().top < innerHeight, overflow: document.documentElement.scrollWidth > innerWidth + 1 }; });
    ok(`[${vp.name}] first screen: headline, rating, product and a buy button`, first.h1 && first.rating && first.atc && first.img, JSON.stringify(first));
    ok(`[${vp.name}] no sideways scroll`, !first.overflow);
    await p.screenshot({ path: `${out}/pdp-${vp.name}.png`, fullPage: false });
    // no prices and no buy box on the sales page: the offer is chosen in the checkout
    const priced = await p.evaluate(() => ({ box: !!document.querySelector('[data-gro-bundle], [data-gro-sub], [data-p], [data-total]'),
      amounts: (document.body.innerText.match(/\$(22\.49|34\.99|47\.97|69\.99|64\.95|104\.95|49\.99|149\.97|15\.99|23\.33)/g) || []).length,
      card: !!document.querySelector('#gro-buy.ofr [data-gro-atc]'), cta: document.querySelectorAll('[data-gro-atc]').length, scroll: document.querySelectorAll('main [data-gro-scroll]').length }));
    ok(`[${vp.name}] no prices and no buy box; the offer card and every button go to the checkout`, !priced.box && priced.amounts === 0 && priced.card && priced.cta >= 8 && priced.scroll === 0, JSON.stringify(priced));
    // tabs: reviews by customer type, week-by-week timeline
    await p.locator('[data-gro-tabs="rev"] button').nth(2).scrollIntoViewIfNeeded(); await p.locator('[data-gro-tabs="rev"] button').nth(2).click();
    await p.locator('[data-gro-tabs="tl"] button').nth(3).click();
    ok(`[${vp.name}] tabs switch (Farmers reviews, Week 3 timeline)`, await p.evaluate(() => /Farmer/.test(document.querySelector('.revs:not([hidden])').innerText) && /KNOW NOT TO RETURN/i.test(document.querySelector('.tlp:not([hidden])').innerText)));
    await p.locator('[data-gro-tabs="rev"] button').first().click();
    // FAQ opens
    const faq = p.locator('.faq details').first(); await faq.locator('summary').scrollIntoViewIfNeeded(); await faq.locator('summary').click();
    ok(`[${vp.name}] FAQ opens`, await faq.evaluate(d => d.open));
    // images: scroll the page, nothing broken
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 50)); } });
    await p.waitForTimeout(700);
    await p.evaluate(async () => { const g = document.querySelector('[data-gro-gallery]'); g.scrollIntoView(); for (let i = 1; i < 7; i++) { g.scrollTo(i * g.clientWidth, 0); await new Promise(r => setTimeout(r, 120)); } g.scrollTo(0, 0); });
    await p.evaluate(async () => { const g = document.querySelector('.revs'); g.scrollIntoView(); for (let x = 0; x < g.scrollWidth; x += 300) { g.scrollTo(x, 0); await new Promise(r => setTimeout(r, 80)); } });
    await p.evaluate(async () => { const g = document.querySelector('[data-gro-gallery]'); g.scrollIntoView(); for (let i = 1; i < 7; i++) { g.scrollTo(i * g.clientWidth, 0); await new Promise(r => setTimeout(r, 350)); } g.scrollTo(0, 0); });
    await p.waitForFunction(() => [...document.querySelectorAll('[data-gro-gallery] img, .revs img, .ugc img')].every(i => i.complete), null, { timeout: 15000 }).catch(() => {});
    const imgs = await p.evaluate(() => [...document.images].filter(i => i.offsetParent !== null && (!i.complete || i.naturalWidth === 0)).map(i => (i.getAttribute('src') || '').slice(-40)));
    ok(`[${vp.name}] all images load`, imgs.length === 0, imgs.slice(0, 4).join(' '));
    if (vp.isMobile) ok(`[mobile] sticky buy bar shows while the buy box is off screen`, await p.evaluate(() => { const s = document.querySelector('[data-gro-sticky]'); return getComputedStyle(s).display !== 'none' && !s.classList.contains('off'); }));
    // hero button -> checkout, tracking parameters kept
    await p.evaluate(() => scrollTo(0, 0));
    await Promise.all([p.waitForURL(CHECKOUT), p.locator('.hero [data-gro-atc]').first().click()]);
    let u = new URL(p.url());
    ok(`[${vp.name}] "Buy now" -> checkout on Buy 2, Get 1 FREE + utm kept`, u.searchParams.get('forceBundleId') === 'main:buy3' && u.searchParams.get('utm_source') === 'test', u.pathname + u.search);
    // the offer is chosen in the checkout: Subscribe & Save / One-time switch, 1x and Buy 2 Get 1 FREE, gifts box
    const summary = async (re) => { await p.waitForFunction(r => new RegExp(r).test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), re, { timeout: 30000 }).catch(() => {}); return (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' '); };
    const st = () => p.evaluate(() => ({ cards: [...document.querySelectorAll('[data-next-bundle-card]')].filter(c => c.offsetParent).map(c => c.getAttribute('data-next-bundle-id') + (c.classList.contains('next-selected') ? '*' : '')).join(','),
      locked: [...document.querySelectorAll('.gro-gift__t i em')].filter(e => getComputedStyle(e).display !== 'none').length, terms: (() => { const e = document.querySelector('.gro-refill-terms'); return e && e.offsetParent !== null ? e.innerText.replace(/\s+/g, ' ') : ''; })() }));
    let t = await summary('47\\.97'); let s = await st();
    ok(`[${vp.name}] checkout: Buy 2, Get 1 FREE subscribed by default, $47.97, gifts unlocked, 3-pack refill terms`, /47\.97/.test(t) && s.cards === 'buy1,buy3*' && s.locked === 0 && /3 packs every 90 days for \$104\.97/.test(s.terms), s.cards + ' | locked ' + s.locked + ' | ' + t.slice(-40));
    await p.locator('[data-next-bundle-id="buy1"]').click(); t = await summary('22\\.49'); s = await st();
    ok(`[${vp.name}] checkout: 1x subscribed $22.49, the two bonus gifts lock, 1-pack refill terms`, /22\.49/.test(t) && s.cards === 'buy1*,buy3' && s.locked === 2 && /1 pack every 30 days for \$34\.99/.test(s.terms), s.cards + ' | locked ' + s.locked);
    await p.locator('.gro-mode [data-gro-mode="ot"]').click(); t = await summary('34\\.99'); s = await st();
    ok(`[${vp.name}] checkout: switch to one-time -> 1x $34.99, no refill terms`, /34\.99/.test(t) && s.cards === 'ot1*,ot3' && s.terms === '' && await p.evaluate(() => { const d = document.querySelector('.submit-section__disclaimer'); return !!d && !/Automatic Refills/.test(d.innerText); }), s.cards + ' | ' + t.slice(-40));
    await p.locator('[data-next-bundle-id="ot3"]').click(); t = await summary('69\\.99'); s = await st();
    ok(`[${vp.name}] checkout: one-time Buy 2, Get 1 FREE $69.99, gifts unlocked`, /69\.99/.test(t) && s.cards === 'ot1,ot3*' && s.locked === 0, s.cards + ' | locked ' + s.locked);
    await p.locator('.gro-sw__o [data-gro-mode="buy"]').click(); t = await summary('47\\.97'); s = await st();
    ok(`[${vp.name}] checkout: "Switch to Subscribe & Save" -> $47.97 with refill terms`, /47\.97/.test(t) && s.cards === 'buy1,buy3*' && /3 packs every 90 days/.test(s.terms), s.cards);
    await p.screenshot({ path: `${out}/checkout-${vp.name}.png`, fullPage: true });
    // an old link to the retired 5-pack lands on Buy 2, Get 1 FREE
    await p.goto(base + (CHECKOUT.test('/mouse-pouches-checkout/') && /getridof/.test(base) ? '/mouse-pouches-checkout/' : '/mouse-pouches/checkout/') + '?forceBundleId=main:buy5', { waitUntil: 'load' });
    t = await summary('47\\.97'); s = await st();
    ok(`[${vp.name}] old 5-pack link -> Buy 2, Get 1 FREE $47.97`, /47\.97/.test(t) && s.cards === 'buy1,buy3*', s.cards + ' | ' + t.slice(-40));
    // default checkout (no parameter) = 3 subscribed packs
    await p.goto(base + (CHECKOUT.test('/mouse-pouches-checkout/') && /getridof/.test(base) ? '/mouse-pouches-checkout/' : '/mouse-pouches/checkout/'), { waitUntil: 'load' });
    t = await summary('47\\.97');
    ok(`[${vp.name}] checkout default: 3 subscribed packs $47.97 with their terms`, /47\.97/.test(t) && await p.evaluate(() => /3 packs every 90 days for \$104\.97/.test((document.querySelector('.gro-refill-terms') || {}).innerText || '')), t.slice(0, 120));
    ok(`[${vp.name}] no requests to the source store`, external.length === 0, external.slice(0, 3).join(' '));
    ok(`[${vp.name}] no page JS errors`, errs.length === 0, errs.slice(0, 3).join(' | '));
    await ctx.close();
  }
  await b.close();
  const failed = results.filter(r => !r.pass).length; console.log(`\n${results.length - failed}/${results.length} passed`);
  try { fs.writeFileSync(`${out}/e2e-results.json`, JSON.stringify(results, null, 1)); } catch (e) { /* out dir optional */ }
  process.exit(failed ? 1 : 0);
})();
