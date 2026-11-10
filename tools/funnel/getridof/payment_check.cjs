// Live payment-readiness check for the Get Rid Of funnel. Fills the checkout but NEVER submits it (no order, no charge).
//   node tools/funnel/getridof/payment_check.cjs [base]
const { chromium } = require('playwright');
const base = process.argv[2] || 'https://getridof.shop';
const ok = (n, p, d = '') => console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : ''));
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  // routing meta tags
  for (const pg of ['mouse-pouches-checkout', 'mouse-pouches-checkout-refill']) {
    const html = await (await p.request.get(`${base}/${pg}/`)).text();
    const m = html.match(/next-success-url" content="([^"]*)"/);
    ok(`${pg}: completed order goes to the upsell`, m && m[1] === '/mouse-pouches-special-offer/', m && m[1]);
  }
  const up = await (await p.request.get(`${base}/mouse-pouches-special-offer/`)).text();
  const acc = (up.match(/next-upsell-accept-url" content="([^"]*)"/) || [])[1], dec = (up.match(/next-upsell-decline-url" content="([^"]*)"/) || [])[1];
  ok('upsell: accept and decline go to the thank-you page', acc === '/mouse-pouches-thank-you/' && dec === '/mouse-pouches-thank-you/', `accept=${acc} decline=${dec}`);
  // upsell price
  await p.goto(`${base}/mouse-pouches-special-offer/`, { waitUntil: 'load' }); await p.waitForTimeout(8000);
  const ut = (await p.locator('body').innerText()).replace(/\s+/g, ' ');
  ok('upsell page shows $29.99 (40% off $49.99)', /\$29\.99/.test(ut) && /\$49\.99/.test(ut), (ut.match(/\$\d+\.\d\d/g) || []).slice(0, 4).join(' '));
  await p.screenshot({ path: (process.argv[3] || '.') + '/live-upsell.png', fullPage: true });
  // checkout payment surfaces
  await p.goto(`${base}/mouse-pouches-checkout/?forceBundleId=main:buy3`, { waitUntil: 'load' });
  await p.waitForFunction(() => document.querySelector('[data-next-checkout-field="cc-number"] iframe'), null, { timeout: 45000 }).catch(() => {});
  await p.waitForTimeout(4000);
  const pay = await p.evaluate(() => {
    const ex = document.querySelector('[data-next-express-checkout="container"]');
    const btns = ex ? [...ex.querySelectorAll('button, .payment-btn, [class*="paypal"], [class*="apple"], iframe')].map(e => (e.className.baseVal === undefined ? String(e.className) : '') + '|' + (e.getAttribute('aria-label') || e.title || e.tagName)).slice(0, 6) : [];
    const radios = [...document.querySelectorAll('[data-next-payment-method]')].filter(r => r.offsetParent).map(r => r.getAttribute('data-next-payment-method') || r.value);
    return { card: !!document.querySelector('[data-next-checkout-field="cc-number"] iframe'), cvv: !!document.querySelector('[data-next-checkout-field="cvv"] iframe'), express: btns, expressShown: ex ? getComputedStyle(ex).display !== 'none' : false, radios };
  });
  ok('card number + CVV fields loaded (29next payments / Adyen)', pay.card && pay.cvv);
  ok('express checkout shown (PayPal / Apple Pay as the browser allows)', pay.expressShown, JSON.stringify(pay.express));
  ok('payment method radios', pay.radios.length > 0, pay.radios.join(', '));
  // fill the form (no submit)
  const fill = async (sel, v) => { const el = p.locator(sel).first(); if (await el.count()) { await el.fill(v); await el.blur().catch(() => {}); } };
  await fill('[data-next-checkout-field="fname"]', 'Test'); await fill('[data-next-checkout-field="lname"]', 'Buyer');
  await fill('[data-next-checkout-field="email"]', 'qa-test@getridof.shop');
  await fill('[data-next-checkout-field="address1"]', '350 5th Ave'); await p.waitForTimeout(800);
  await fill('[data-next-checkout-field="city"]', 'New York');
  const prov = p.locator('[data-next-checkout-field="province"]').first(); if (await prov.count()) await prov.selectOption('NY').catch(() => {});
  await fill('[data-next-checkout-field="postal"]', '10118');
  await p.waitForTimeout(1500);
  const sum = (await p.locator('[data-next-cart-summary]').first().innerText()).replace(/\s+/g, ' ');
  ok('checkout total for 3 packs = $55.98, free shipping', /55\.98/.test(sum) && /Free/i.test(sum), sum.slice(0, 120));
  const submit = await p.evaluate(() => { const s = document.querySelector('[data-next-checkout="form"] button[type="submit"], .submit-button'); return s ? { text: s.innerText.trim(), disabled: s.disabled } : null; });
  ok('order button present and enabled (not clicked)', submit && !submit.disabled, submit && submit.text);
  await p.screenshot({ path: (process.argv[3] || '.') + '/live-checkout-filled.png', fullPage: true });
  ok('no JavaScript errors', errs.length === 0, errs.slice(0, 2).join(' | '));
  await b.close();
})();
