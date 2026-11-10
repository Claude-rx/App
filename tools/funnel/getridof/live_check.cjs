// Live check of the store-hosted funnel (default https://getridof.shop). Places no order.
const { chromium } = require('playwright');
const base = process.argv[2] || 'https://getridof.shop';
(async () => {
  const b = await chromium.launch(); const res = [];
  const ok = (n, p, d = '') => { res.push(p); console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };
  for (const vp of [{ n: 'desktop', w: 1440, h: 900 }, { n: 'mobile', w: 390, h: 844, m: true }]) {
    const ctx = await b.newContext({ viewport: { width: vp.w, height: vp.h }, isMobile: !!vp.m, hasTouch: !!vp.m });
    const p = await ctx.newPage(); const bad = [], errs = [];
    p.on('response', r => { if (r.status() >= 400 && !/analytics|pixel|collect/.test(r.url())) bad.push(r.status() + ' ' + r.url().slice(0, 120)); });
    p.on('pageerror', e => errs.push(e.message));
    const r = await p.goto(base + '/mouse-pouches/', { waitUntil: 'load', timeout: 90000 });
    ok(`[${vp.n}] sales page ${r.status()}`, r.status() === 200);
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
    await p.waitForTimeout(1500);
    const imgs = await p.evaluate(() => [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src')).map(i => i.getAttribute('src').slice(0, 90)));
    ok(`[${vp.n}] no broken images`, imgs.length === 0, imgs.slice(0, 3).join(' '));
    ok(`[${vp.n}] styles applied (bundle bar laid out)`, await p.evaluate(() => { const e = document.querySelector('[data-gro-bundle="buy3"]'); return !!e && e.getBoundingClientRect().height > 40 && getComputedStyle(e).borderTopStyle !== 'none'; }));
    await p.screenshot({ path: `${process.argv[3] || '.'}/live-pdp-${vp.n}.png` });
    await p.locator('[data-gro-bundle="buy5"]').scrollIntoViewIfNeeded(); await p.locator('[data-gro-bundle="buy5"]').click();
    if (await p.locator('[data-gro-refill]').getAttribute('aria-checked') === 'true') await p.locator('[data-gro-refill]').click();
    await Promise.all([p.waitForURL(/mouse-pouches-checkout\//, { timeout: 60000 }), p.locator('[data-gro-atc]').first().click()]);
    ok(`[${vp.n}] ADD TO CART -> ${new URL(p.url()).pathname}${new URL(p.url()).search}`, /forceBundleId=main%3Abuy5/.test(p.url()));
    await p.waitForTimeout(9000);
    const sum = (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' ');
    ok(`[${vp.n}] checkout loads prices, 5 packs = $74.95`, /74\.95/.test(sum), sum.slice(0, 160));
    await p.screenshot({ path: `${process.argv[3] || '.'}/live-checkout-${vp.n}.png`, fullPage: false });
    const r2 = await p.goto(base + '/mouse-pouches-checkout-refill/?forceBundleId=main:buy3', { waitUntil: 'load' }); await p.waitForTimeout(9000);
    const s2 = (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' ');
    ok(`[${vp.n}] refill checkout ${r2.status()}, 3 packs = $55.98`, /55\.98/.test(s2), s2.slice(0, 120));
    const r3 = await p.goto(base + '/mouse-pouches-thank-you/', { waitUntil: 'load' });
    ok(`[${vp.n}] thank-you page ${r3.status()}`, r3.status() === 200);
    ok(`[${vp.n}] no failed asset requests`, bad.filter(x => /cdn|getridof/.test(x)).length === 0, bad.slice(0, 4).join(' | '));
    ok(`[${vp.n}] no JS errors`, errs.length === 0, errs.slice(0, 2).join(' | '));
    await ctx.close();
  }
  await b.close(); const f = res.filter(x => !x).length; console.log(`\n${res.length - f}/${res.length} passed`); process.exit(f ? 1 : 0);
})();
