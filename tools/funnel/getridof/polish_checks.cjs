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
    // Shopify-style checkout: no visible bundle picker; the tier comes from the sales page as ?forceBundleId=main:<id>
    // and a hidden selector applies it. Default (no parameter) = buy3.
    const tierCards = await p.evaluate(() => [...document.querySelectorAll('[data-next-bundle-card]')].filter(c => c.offsetParent).length);
    ok(`[${vp.n}] Step 1 shows the three bundle cards of the chosen mode`, tierCards === 3, `visible cards: ${tierCards}`);
    const sumText = async () => (await p.locator('[data-next-cart-summary]').first().innerText()).replace(/\s+/g, ' ');
    ok(`[${vp.n}] default tier = 3 packs, $47.97`, /47\.97/.test(await sumText()));
    for (const [id, price, packs] of [['buy1', '22.49', 1], ['buy5', '64.95', 5]]) {
      await p.goto(base + `/mouse-pouches/checkout/?forceBundleId=main:${id}`, { waitUntil: 'load' });
      await p.waitForFunction(() => document.querySelector('[data-next-bundle-card].next-selected'), null, { timeout: 30000 }); await p.waitForTimeout(2500);
      const t = await sumText();
      ok(`[${vp.n}] ${id} from the sales page -> ${packs} pack(s), $${price}`, t.includes(price), t.slice(0, 90));
    }
    // bump
    const bump = p.locator('[data-next-toggle-card]').first();
    const before = await bump.getAttribute('class');
    await bump.click(); await p.waitForTimeout(1800);
    const after = await bump.getAttribute('class'); const t2 = await p.locator('[data-next-cart-summary]').first().innerText();
    ok(`[${vp.n}] bump toggles on and adds $3.97`, !/next-(active|selected|in-cart)/.test(before || '') && /next-(active|selected|in-cart)/.test(after || '') && /68\.92/.test(t2), `${before} -> ${after}`);
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
  // the exit popup was removed at the owner's request: nothing may pop up (no SDK exit-intent overlay, no placeholder image)
  const overlay = await p.evaluate(() => [...document.querySelectorAll('body *')].some(e => {
    const st = getComputedStyle(e); if (st.position !== 'fixed' || st.display === 'none' || st.visibility === 'hidden') return false;
    const r = e.getBoundingClientRect(); return r.width > innerWidth * 0.5 && r.height > innerHeight * 0.5 && +st.zIndex > 100; }));
  const placeholder = await p.evaluate(() => !!document.querySelector('img[src*="placehold"]'));
  ok('[desktop] no exit-intent popup on leaving the page', !overlay && !placeholder);
  await p.screenshot({ path: `${out}/exit-intent.png` });
  await b.close();
  require('fs').writeFileSync(`${out}/polish-checks.json`, JSON.stringify({ base, ran_at: new Date().toISOString(), results: res }, null, 2));
  const f = res.filter(r => !r.pass).length; console.log(`\n${res.length - f}/${res.length} passed`); process.exit(f ? 1 : 0);
})();
