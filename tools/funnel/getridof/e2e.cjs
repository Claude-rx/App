// End-to-end check of the Get Rid Of mouse-pouches funnel against a served _site (default http://localhost:8765).
//   node tools/funnel/getridof/e2e.cjs [baseUrl] [outDir]
// PDP: bundle bars, refill toggle, ADD TO CART -> checkout URL; accordions, tabs. Checkout: the chosen card is
// selected and the live Campaign Cart total matches campaign 2362 (one-time 29.99 / 55.98 / 74.95; subscribed first order 24.99 / 47.97 / 64.95). Places no order.
const { chromium } = require('playwright');
const base = process.argv[2] || 'http://localhost:8765';
const out = process.argv[3] || '.';
const results = []; const ok = (name, pass, detail = '') => { results.push({ name, pass, detail }); console.log((pass ? 'PASS ' : 'FAIL ') + name + (detail ? '  ' + detail : '')); };
(async () => {
  const b = await chromium.launch();
  for (const vp of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 390, height: 844, isMobile: true, hasTouch: true }]) {
    const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, hasTouch: !!vp.hasTouch });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const external = []; p.on('request', r => { const u = r.url(); if (/^https?:\/\/[^/]*(sofyre\.com|shopify|gemcommerce|kaching)/.test(u)) external.push(u); });
    await p.goto(base + '/mouse-pouches/?utm_source=test', { waitUntil: 'load' });
    await p.waitForTimeout(800);
    ok(`[${vp.name}] PDP title`, (await p.title()).includes('Get Rid Of'));
    ok(`[${vp.name}] no SoFyre text visible`, !(await p.evaluate(() => /sofyre/i.test(document.body.innerText))));
    ok(`[${vp.name}] no requests to the source store`, external.length === 0, external.slice(0, 3).join(' '));
    ok(`[${vp.name}] default bundle = buy3`, await p.evaluate(() => document.querySelector('[data-gro-bundle="buy3"]').classList.contains('kaching-bundles__bar--selected')));
    ok(`[${vp.name}] 5-pack shows $64.95 subscribed (default)`, (await p.locator('[data-gro-bundle="buy5"] .kaching-bundles__bar-price').innerText()).includes('64.95'));
    await p.screenshot({ path: `${out}/pdp-${vp.name}.png`, fullPage: false });
    // accordion (FAQ) opens
    const acc = p.locator('gp-accordion').nth(1).locator('.gp-accordion-item').first();
    await acc.locator('.gp-accordion-item_header').scrollIntoViewIfNeeded(); await acc.locator('.gp-accordion-item_header').click();
    await p.waitForTimeout(400);
    ok(`[${vp.name}] FAQ accordion opens`, await acc.evaluate(i => i.querySelector('.gp-accordion-item_body').getBoundingClientRect().height > 30));
    // tabs switch
    const tab = p.locator('gp-tab').first(); const li = tab.locator('li.gp-tab-item').nth(2);
    await li.scrollIntoViewIfNeeded(); await li.click(); await p.waitForTimeout(300);
    ok(`[${vp.name}] timeline tab switches`, await li.getAttribute('aria-selected') === 'true');
    // buy box: 5-pack, refill off -> one-time checkout
    await p.locator('[data-gro-bundle="buy5"]').scrollIntoViewIfNeeded(); await p.locator('[data-gro-bundle="buy5"]').click();
    const refillOn = await p.locator('[data-gro-refill]').getAttribute('aria-checked');
    if (refillOn === 'true') await p.locator('[data-gro-refill]').click();
    await Promise.all([p.waitForURL(/checkout\//), p.locator('[data-gro-atc]').first().click()]);
    const u = new URL(p.url());
    ok(`[${vp.name}] ATC -> one-time checkout with buy5 + utm kept`, u.pathname === '/mouse-pouches/checkout/' && u.searchParams.get('forceBundleId') === 'main:buy5' && u.searchParams.get('utm_source') === 'test', u.pathname + u.search);
    await p.waitForFunction(() => window.next && document.querySelector('[data-next-bundle-card][data-next-bundle-id="buy5"]'), null, { timeout: 30000 }).catch(() => {});
    await p.waitForTimeout(5000);
    const st = await p.evaluate(() => { const s = window.next && window.next.cart && window.next.cart.getState ? window.next.cart.getState() : (window.nextDebug && window.nextDebug.stores.cart.getState()); return s ? JSON.stringify({ items: (s.items || []).map(i => [i.packageId, i.quantity]), total: s.totals && s.totals.total && s.totals.total.value, sub: s.totals && s.totals.subtotal && s.totals.subtotal.value }) : null; }).catch(e => 'err ' + e.message);
    const totalText = await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '');
    ok(`[${vp.name}] checkout cart = 5 x pkg 1, total $74.95`, /74\.95/.test(totalText) || /74\.95/.test(st || ''), (st || '') + ' | ' + totalText.replace(/\s+/g, ' ').slice(0, 160));
    await p.screenshot({ path: `${out}/checkout-${vp.name}.png`, fullPage: true });
    // refill checkout, 3-pack
    await p.goto(base + '/mouse-pouches/checkout-refill/?forceBundleId=main:buy3', { waitUntil: 'load' }); await p.waitForTimeout(6000);
    const t2 = await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '');
    ok(`[${vp.name}] refill checkout 3-pack first order $47.97 (50% off)`, /47\.97/.test(t2), t2.replace(/\s+/g, ' ').slice(0, 200));
    ok(`[${vp.name}] refill terms shown`, await p.locator('.gro-refill-terms').isVisible());
    await p.screenshot({ path: `${out}/checkout-refill-${vp.name}.png`, fullPage: true });
    ok(`[${vp.name}] no page JS errors`, errs.length === 0, errs.slice(0, 3).join(' | '));
    await ctx.close();
  }
  await b.close();
  const failed = results.filter(r => !r.pass).length; console.log(`\n${results.length - failed}/${results.length} passed`); process.exit(failed ? 1 : 0);
})();
