// AppLovin (Axon) event data on the four Get Rid Of funnels. Sends NOTHING to AppLovin and places no order:
// window.axon is replaced by a recorder before the page's own code runs, and the pixel hosts are blocked.
//   node tools/funnel/getridof/axon_check.cjs [baseUrl]
// Local build: http://localhost:8765 (/slug/checkout/, /slug/upsell/, /slug/receipt/)
// Store:       https://getridof.shop  (/slug-checkout/, /slug-special-offer/, /slug-thank-you/)
// Checks, per funnel: every event carries user_data with one stable user_id (6+ characters) from the first page view
// on; view_item / add_to_cart items are complete; a purchase carries email, phone (digits with country code) and the
// required order fields; the purchases recorded on the offer pages and the thank-you page view still carry the
// email and phone, although the SDK's own events there arrive without them.
const { chromium } = require('playwright');
const base = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
const STORE = /getridof/.test(base);
const FUNNELS = [['mouse-pouches', '.hero [data-gro-atc]'], ['mice-5-reasons', '.lh [data-gro-atc]'], ['mouse-repellent-pouches', '#gro-buy ~ * [data-gro-atc], [data-gro-atc]'], ['mice-9-reasons', '.lh [data-gro-atc]']];
const OFFER = { 'mice-9-reasons': 'home-plan' };   // store slug of a funnel's first offer page when it is not "special-offer"
const url = (slug, page) => page === '' ? `${base}/${slug}/` : STORE ? `${base}/${slug}-${{ checkout: 'checkout', upsell: OFFER[slug] || 'special-offer', receipt: 'thank-you' }[page]}/` : `${base}/${slug}/${page}/`;
const ITEM = { item_id: 'cdkh', item_name: 'Rodent Repellent Pouches', item_variant_id: '37', item_category: 'x', price: 15.99, quantity: 3, discount: 34 };
let pass = 0, fail = 0;
const ok = (n, p, d = '') => { p ? pass++ : fail++; console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };

(async () => {
  const b = await chromium.launch();
  for (const [slug, cta] of FUNNELS) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 800 }, isMobile: true, hasTouch: true });
    await ctx.route(/axon\.ai|albss\.com|applovin/, r => r.abort());
    const calls = [];
    await ctx.exposeFunction('__axonRec', s => { calls.push(JSON.parse(s)); });
    await ctx.addInitScript(() => { window.axon = function () { try { window.__axonRec(JSON.stringify([].slice.call(arguments))); } catch (e) {} }; });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const tracks = name => calls.filter(c => c[0] === 'track' && (!name || c[1] === name));
    const user = c => (c[2] || {}).user_data || {};

    // product page
    await p.goto(url(slug, ''), { waitUntil: 'load' }); await p.waitForTimeout(800);
    const pv = tracks('page_view')[0], vi = tracks('view_item')[0];
    const id = pv ? user(pv).user_id : '';
    ok(`[${slug}] product page: page_view and view_item carry user_data with one user_id of 6+ characters`, !!pv && !!vi && typeof id === 'string' && id.length >= 6 && user(vi).user_id === id, id ? id.slice(0, 8) + '…' : 'none');
    const it = vi && vi[2] && vi[2].items && vi[2].items[0] || {};
    ok(`[${slug}] view_item: currency, value and a complete item (id, name, variant, category number, .png image, price, quantity)`,
      !!vi && vi[2].currency === 'USD' && vi[2].value > 0 && !!it.item_id && !!it.item_name && !!it.item_variant_id && typeof it.item_category_id === 'number' && /\.(png|jpe?g)$/.test(it.image_url || '') && it.price > 0 && it.quantity > 0, JSON.stringify(it).slice(0, 200));
    await Promise.all([p.waitForURL(/checkout/), p.locator(cta).first().click()]);
    const atc = tracks('add_to_cart')[0];
    ok(`[${slug}] add_to_cart: items + the same user_id`, !!atc && atc[2].items.length > 0 && user(atc).user_id === id);

    // checkout: the SDK's own events through the adapter
    await p.waitForFunction(() => typeof window.NextDataLayerTransformFn === 'function' && window.NextForwarder, null, { timeout: 30000 });
    await p.waitForTimeout(6000);
    const co = tracks().slice(tracks().indexOf(atc) + 1);
    ok(`[${slug}] checkout: every event the SDK sends carries the same user_id`, co.length >= 2 && co.every(c => user(c).user_id === id), co.map(c => c[1] + (user(c).user_id === id ? '' : '!')).join(','));
    ok(`[${slug}] checkout: begin_checkout has currency, value and items`, co.some(c => c[1] === 'begin_checkout' && c[2].currency && c[2].value > 0 && (c[2].items || []).length > 0), co.map(c => c[1]).join(','));

    // a purchase as the SDK reports it (phone typed without a country code), handed to the forwarder; nothing leaves the browser
    const fire = (evt) => p.evaluate(e => { window.NextDataLayerTransformFn(e); }, evt);
    await fire({ event: 'dl_purchase', event_id: 'gro-test-' + slug, user_properties: { visitor_type: 'guest', customer_email: ' Test.Buyer@Example.com ', customer_phone: '(415) 555-0147' },
      ecommerce: { transaction_id: 'T-1001', currency: 'USD', value: 47.97, tax: 0, shipping: 0, items: [ITEM] } });
    await p.waitForTimeout(300);
    const pu = tracks('purchase')[0], u = pu ? user(pu) : {};
    ok(`[${slug}] purchase: user_id, email (lowercase), phone as digits with country code, phone_last10_hashed`, !!pu && u.user_id === id && u.email === 'test.buyer@example.com' && u.phone === '14155550147' && /^[0-9a-f]{64}$/.test(u.phone_last10_hashed || ''), JSON.stringify({ ...u, user_id: 'same' }).slice(0, 160));
    ok(`[${slug}] purchase: transaction_id, value, tax, shipping, currency, items, discount_applications`, !!pu && pu[2].transaction_id === 'T-1001' && pu[2].value === 47.97 && pu[2].tax === 0 && pu[2].shipping === 0 && pu[2].currency === 'USD' && pu[2].items[0].item_category_id === 7137 && Array.isArray(pu[2].discount_applications));

    // offer page: the SDK's upsell purchase arrives with visitor_type only
    await p.goto(url(slug, 'upsell'), { waitUntil: 'load' });
    await p.waitForFunction(() => typeof window.NextDataLayerTransformFn === 'function' && window.NextForwarder, null, { timeout: 30000 }); await p.waitForTimeout(1500);
    await fire({ event: 'dl_upsell_purchase', event_id: 'gro-test-up-' + slug, user_properties: { visitor_type: 'guest' },
      ecommerce: { transaction_id: 'T-1001-US1', currency: 'USD', value: 14.98, tax: 0, shipping: 0, items: [{ ...ITEM, item_variant_id: '7', price: 14.98, quantity: 1 }] } });
    await p.waitForTimeout(300);
    const up = tracks('purchase')[1], uu = up ? user(up) : {};
    ok(`[${slug}] offer-page purchase: same user_id, and the email and phone given at checkout`, !!up && up[2].transaction_id === 'T-1001-US1' && uu.user_id === id && uu.email === 'test.buyer@example.com' && uu.phone === '14155550147');

    // thank-you page
    const before = calls.length;
    await p.goto(url(slug, 'receipt'), { waitUntil: 'load' }); await p.waitForTimeout(4000);
    const ty = calls.slice(before).filter(c => c[0] === 'track');
    ok(`[${slug}] thank-you page: events keep the user_id, email and phone`, ty.length >= 1 && ty.every(c => user(c).user_id === id && user(c).email === 'test.buyer@example.com' && user(c).phone === '14155550147'), ty.map(c => c[1]).join(','));
    ok(`[${slug}] no page JS errors`, errs.length === 0, errs.slice(0, 2).join(' | '));
    await ctx.close();
  }
  await b.close();
  console.log(`\n${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
})();
