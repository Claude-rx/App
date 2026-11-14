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
const PRICES = { buy1: ['22.49', '24.99'], buy3: ['47.97', '49.98'], buy5: ['64.95', '69.95'] };   // [subscribe, one-time] = campaign 2362
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
    ok(`[${vp.name}] page is lean (HTML under 200 KB incl. the store's ~81 KB monitoring script)`, html.length < 200 * 1024, Math.round(html.length / 1024) + ' KB');
    ok(`[${vp.name}] no SoFyre text`, !/sofyre/i.test(html));
    ok(`[${vp.name}] part of the campaign (next-funnel, page type product)`, /name="next-funnel" content="[^"]+"/.test(html) && /name="next-page-type" content="product"/.test(html) && /campaign-cart@v[\d.]+\/dist\/loader\.js/.test(html));
    const first = await p.evaluate(() => { const vis = s => [...document.querySelectorAll(s)].some(e => { if (e.offsetParent === null && getComputedStyle(e).position !== 'fixed') return false; const r = e.getBoundingClientRect(); return r.height > 0 && r.top >= 0 && r.bottom <= innerHeight + 1; });
      return { h1: vis('h1'), rating: vis('.rate'), atc: vis('[data-gro-atc], a.sn'), price: vis('[data-total], [data-p]'), img: vis('.gal__t img') || document.querySelector('.gal__t img').getBoundingClientRect().top < innerHeight, overflow: document.documentElement.scrollWidth > innerWidth + 1 }; });
    ok(`[${vp.name}] first screen: headline, rating, product, price and a buy button`, first.h1 && first.rating && first.atc && first.price && first.img, JSON.stringify(first));
    ok(`[${vp.name}] no sideways scroll`, !first.overflow);
    await p.screenshot({ path: `${out}/pdp-${vp.name}.png`, fullPage: false });
    ok(`[${vp.name}] default = Buy 2 Get 1 Free, subscribed`, await p.evaluate(() => document.querySelector('[data-gro-bundle="buy3"]').classList.contains('on') && document.querySelector('[data-gro-sub]').checked));
    // every price on the buy box, both modes
    let priceOk = true; const seen = [];
    for (const mode of [0, 1]) {
      if (mode === 1) await p.locator('[data-gro-sub]').uncheck();
      for (const id of ['buy1', 'buy3', 'buy5']) {
        const t = await p.locator(`[data-gro-bundle="${id}"] [data-p]`).innerText(); seen.push(t);
        if (!t.includes(PRICES[id][mode])) priceOk = false;
      }
    }
    ok(`[${vp.name}] buy box prices: subscribe 22.49 / 47.97 / 64.95, one-time 24.99 / 49.98 / 69.95`, priceOk, seen.join(' '));
    ok(`[${vp.name}] one-time copy when unticked`, /One-time purchase: \$49\.98, no refills/.test(await p.locator('[data-sub-terms]').innerText()));
    await p.locator('[data-gro-sub]').check();
    ok(`[${vp.name}] renewal terms shown when subscribed`, /3 packs \(\$104\.97\) every 90 days/.test(await p.locator('[data-sub-terms]').innerText()));
    // FAQ opens
    const faq = p.locator('.faq details').first(); await faq.locator('summary').scrollIntoViewIfNeeded(); await faq.locator('summary').click();
    ok(`[${vp.name}] FAQ opens`, await faq.evaluate(d => d.open));
    // images: scroll the page, nothing broken
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 50)); } });
    await p.waitForTimeout(700);
    await p.evaluate(async () => { const g = document.querySelector('[data-gro-gallery]'); g.scrollIntoView(); for (let i = 1; i < 7; i++) { g.scrollTo(i * g.clientWidth, 0); await new Promise(r => setTimeout(r, 120)); } g.scrollTo(0, 0); });
    await p.evaluate(async () => { const g = document.querySelector('.revs'); g.scrollIntoView(); for (let x = 0; x < g.scrollWidth; x += 300) { g.scrollTo(x, 0); await new Promise(r => setTimeout(r, 80)); } });
    await p.waitForTimeout(1200);
    const imgs = await p.evaluate(() => [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => (i.getAttribute('src') || '').slice(-40)));
    ok(`[${vp.name}] all images load`, imgs.length === 0, imgs.slice(0, 4).join(' '));
    if (vp.isMobile) ok(`[mobile] sticky buy bar shows while the buy box is off screen`, await p.evaluate(() => { const s = document.querySelector('[data-gro-sticky]'); return getComputedStyle(s).display !== 'none' && !s.classList.contains('off'); }));
    // subscribed 5-pack -> checkout
    await p.evaluate(() => scrollTo(0, 0));
    await p.locator('[data-gro-bundle="buy5"]').scrollIntoViewIfNeeded(); await p.locator('[data-gro-bundle="buy5"]').click();
    await Promise.all([p.waitForURL(CHECKOUT), p.locator('#gro-buy [data-gro-atc]').click()]);
    let u = new URL(p.url());
    ok(`[${vp.name}] ADD TO CART -> checkout with buy5 + utm kept`, u.searchParams.get('forceBundleId') === 'main:buy5' && u.searchParams.get('utm_source') === 'test', u.pathname + u.search);
    const summary = async (re) => { await p.waitForFunction(r => new RegExp(r).test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), re, { timeout: 30000 }).catch(() => {}); return (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' '); };
    let t = await summary('64\\.95');
    ok(`[${vp.name}] checkout: 5 subscribed packs, first order $64.95`, /64\.95/.test(t), t.slice(0, 140));
    ok(`[${vp.name}] checkout: Automatic Refills terms for 5 packs`, await p.evaluate(() => { const e = document.querySelector('.gro-refill-terms'); return !!e && e.offsetParent !== null && /5 packs every 150 days for \$174\.95/.test(e.innerText) && !/3 packs every 90/.test(e.innerText); }));
    await p.screenshot({ path: `${out}/checkout-${vp.name}.png`, fullPage: true });
    // one-time single pack -> checkout
    await p.goto(base + '/mouse-pouches/', { waitUntil: 'load' }); await p.waitForTimeout(400);
    await p.locator('[data-gro-bundle="buy1"]').scrollIntoViewIfNeeded(); await p.locator('[data-gro-bundle="buy1"]').click();
    await p.locator('[data-gro-sub]').uncheck();
    await Promise.all([p.waitForURL(CHECKOUT), p.locator('#gro-buy [data-gro-atc]').click()]);
    u = new URL(p.url());
    t = await summary('24\\.99');
    ok(`[${vp.name}] one-time 1 pack -> main:ot1, total $24.99`, u.searchParams.get('forceBundleId') === 'main:ot1' && /24\.99/.test(t), u.search + ' | ' + t.slice(0, 120));
    ok(`[${vp.name}] one-time checkout: no Automatic Refills terms, no "Every 30 days"`, await p.evaluate(() => { const e = document.querySelector('.gro-refill-terms'); const d = document.querySelector('.submit-section__disclaimer'); return (!e || e.offsetParent === null) && !!d && !/Automatic Refills/.test(d.innerText) && !/Every \d+ days/i.test(document.querySelector('[data-next-cart-summary]').innerText); }));
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
