// Polish interaction checks + evidence screenshots for the Get Rid Of mouse-pouches checkout.
//   node tools/funnel/getridof/polish_checks.cjs [baseUrl] [outDir]   (places no order)
const { chromium } = require('playwright');
const base = process.argv[2] || 'http://localhost:8765';
const out = process.argv[3] || 'campaigns/getridof/runs/polish';
const res = []; const ok = (n, p, d = '') => { res.push({ check: n, pass: !!p, detail: d }); console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };
(async () => {
  const b = await chromium.launch();
  for (const vp of [{ n: 'desktop', w: 1440, h: 900 }, { n: 'mobile', w: 390, h: 844, m: true }]) {
    const ctx = await b.newContext({ viewport: { width: vp.w, height: vp.h }, isMobile: !!vp.m, hasTouch: !!vp.m, deviceScaleFactor: 2 });
    const p = await ctx.newPage();
    await p.goto(base + '/mouse-pouches/checkout/', { waitUntil: 'load' });
    await p.waitForFunction(() => document.querySelector('[data-next-bundle-card].next-selected'), null, { timeout: 30000 });
    await p.waitForTimeout(2500);
    const state = () => p.evaluate(() => [...document.querySelectorAll('[data-next-bundle-card]')].map(c => ({ id: c.dataset.nextBundleId, sdk: c.classList.contains('next-selected'), radio: (c.querySelector('.radio-style-1') || {}).getAttribute ? c.querySelector('.radio-style-1').getAttribute('data-selected') : null })));
    const s0 = await state();
    ok(`[${vp.n}] default card buy3 selected (SDK class)`, s0.find(c => c.id === 'buy3').sdk && s0.filter(c => c.sdk).length === 1, JSON.stringify(s0));
    await p.locator('[data-next-bundle-card][data-next-bundle-id="buy1"]').click(); await p.waitForTimeout(1500);
    const s1 = await state();
    ok(`[${vp.n}] picking buy1 deselects buy3`, s1.find(c => c.id === 'buy1').sdk && !s1.find(c => c.id === 'buy3').sdk, JSON.stringify(s1));
    ok(`[${vp.n}] no stale static data-selected on an unselected card`, !s1.some(c => !c.sdk && c.radio === 'true'), JSON.stringify(s1));
    const radioVis = await p.evaluate(() => [...document.querySelectorAll('[data-next-bundle-card]')].map(c => getComputedStyle(c.querySelector('.radio-inner') || c, '::before').content + '|' + getComputedStyle(c.querySelector('.radio-inner') || c).opacity + '|' + getComputedStyle(c.querySelector('.radio-inner') || c).backgroundColor));
    ok(`[${vp.n}] radio visuals follow selection`, radioVis[0] !== radioVis[1], radioVis.join(' / '));
    const total1 = await p.locator('[data-next-cart-summary]').first().innerText();
    ok(`[${vp.n}] buy1 total $24.99 (subscription first order)`, /24\.99/.test(total1));
    await p.locator('[data-next-bundle-card]').first().screenshot({ path: `${out}/bundle-cards-${vp.n}.png` }).catch(() => {});
    await p.locator('[data-next-bundle-selector]').first().screenshot({ path: `${out}/bundle-selector-${vp.n}.png` });
    // bump
    const bump = p.locator('[data-next-toggle-card]').first();
    const before = await bump.getAttribute('class');
    await bump.click(); await p.waitForTimeout(1800);
    const after = await bump.getAttribute('class'); const t2 = await p.locator('[data-next-cart-summary]').first().innerText();
    ok(`[${vp.n}] bump toggles on and adds $3.97`, !/next-(active|selected|in-cart)/.test(before || '') && /next-(active|selected|in-cart)/.test(after || '') && /28\.96/.test(t2), `${before} -> ${after}`);
    await bump.screenshot({ path: `${out}/bump-${vp.n}.png` });
    await bump.click(); await p.waitForTimeout(1500);
    ok(`[${vp.n}] bump toggles off`, !/next-(active|selected|in-cart)/.test(await bump.getAttribute('class') || ''));
    // card fields
    await p.waitForFunction(() => document.querySelector('[data-next-checkout-field="cc-number"] iframe'), null, { timeout: 30000 }).catch(() => {});
    await p.waitForTimeout(2000);
    const cc = await p.evaluate(() => ['cc-number', 'cvv'].map(f => { const h = document.querySelector(`[data-next-checkout-field="${f}"]`); if (!h) return null; const i = h.querySelector('iframe'); const hr = h.getBoundingClientRect(); const ir = i ? i.getBoundingClientRect() : null; return { f, host: Math.round(hr.height), iframe: ir ? Math.round(ir.height) : null, offTop: ir ? Math.round(ir.top - hr.top) : null, offBottom: ir ? Math.round(hr.bottom - ir.bottom) : null }; }));
    ok(`[${vp.n}] card + CVV hosted fields mounted, centered, not full-height`, cc.every(c => c && c.iframe && c.iframe < 80 && Math.abs(c.offTop - c.offBottom) <= 4), JSON.stringify(cc));
    const pay = p.locator('[data-next-checkout-field="cc-number"]').first();
    await pay.scrollIntoViewIfNeeded(); const box = await pay.evaluate(e => { const r = e.closest('.payment-method, [data-next-payment-form], form').getBoundingClientRect(); return { x: r.x, y: r.y + scrollY, w: r.width, h: Math.min(r.height, 420) }; });
    await p.screenshot({ path: `${out}/card-fields-${vp.n}.png`, clip: { x: Math.max(0, box.x), y: box.y, width: box.w, height: box.h }, fullPage: true });
    // express wallets: the campaign enables bankcard only
    const ex = await p.evaluate(() => { const c = document.querySelector('[data-next-express-checkout="container"]'); if (!c) return 'no container'; const sec = c; return { buttons: c.querySelectorAll('button, .payment-btn, iframe').length, visibleHeight: Math.round(sec.getBoundingClientRect().height), display: getComputedStyle(sec).display }; });
    ok(`[${vp.n}] express area not an empty visible box (campaign is card-only)`, ex === 'no container' || ex.buttons > 0 || ex.visibleHeight < 10, JSON.stringify(ex));
    await p.screenshot({ path: `${out}/checkout-${vp.n}.png`, fullPage: true });
    await ctx.close();
  }
  // exit intent (desktop): mouse leaves the top of the viewport
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
  await p.goto(base + '/mouse-pouches/checkout/'); await p.waitForFunction(() => document.querySelector('[data-next-bundle-card].next-selected'), null, { timeout: 30000 }); await p.waitForTimeout(4000);
  await p.mouse.move(700, 300); await p.mouse.move(700, 5, { steps: 10 }); await p.mouse.move(700, -50);
  await p.evaluate(() => document.dispatchEvent(new MouseEvent('mouseout', { relatedTarget: null, clientY: -5, bubbles: true })));
  await p.waitForTimeout(1500);
  const popup = p.locator('.exit-intent-popup').first();
  const shown = await popup.isVisible().catch(() => false);
  ok('[desktop] exit-intent popup shows', shown);
  if (shown) {
    await p.screenshot({ path: `${out}/exit-intent.png` });
    await p.locator('[data-exit-intent-action="apply-coupon"]').first().click(); await p.waitForTimeout(3000);
    const t = await p.locator('[data-next-cart-summary]').first().innerText();
    ok('[desktop] exit coupon GROMOUSE10 applies (3-pack $47.97 -> $43.17)', /43\.17/.test(t), t.replace(/\s+/g, ' ').slice(0, 220));
  }
  await b.close();
  require('fs').writeFileSync(`${out}/polish-checks.json`, JSON.stringify({ base, ran_at: new Date().toISOString(), results: res }, null, 2));
  const f = res.filter(r => !r.pass).length; console.log(`\n${res.length - f}/${res.length} passed`); process.exit(f ? 1 : 0);
})();
