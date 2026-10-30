import fs from 'node:fs'; import vm from 'node:vm'; import assert from 'node:assert/strict'; import test from 'node:test';
const SRC = fs.readFileSync(process.argv[2] || process.env.ADAPTER, 'utf8');
function load(win = {}) {
  const calls = []; let adapter;
  const window = Object.assign({ __axonEventKey: 'k', axon: (...a) => calls.push(JSON.parse(JSON.stringify(a))),
    NextForwarder: { DEFAULT_MAIN_EVENTS: null, register: (a) => { adapter = a; } } }, win);
  vm.runInNewContext(SRC, { window, console });
  return { calls, adapter };
}
// The reported order #101614, as the SDK builds dl_purchase (user_properties from order.user).
const ec = { currency: 'USD', value: 39, transaction_id: '101614', tax: 0, shipping: 0,
  items: [{ item_id: 'SKF-APF-1', item_name: 'Adaptive Peptide Foundation - 1 bottle', price: 39, quantity: 1,
    item_brand: 'SKINOFAB Adaptive Peptide Foundation Funnel', item_variant_id: '15', item_category: 'SKINOFAB Adaptive Peptide Foundation Funnel',
    item_image: 'https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg' }] };
const evt = (up) => ({ event: 'dl_purchase', ecommerce: ec, user_properties: up });

test('purchase carries user_data (the AppLovin error)', () => {
  const { calls, adapter } = load();
  adapter.send('purchase', ec, evt({ visitor_type: 'logged_in', customer_email: '  Jane.Doe@Example.COM ', customer_phone: '+18123158899', customer_id: '1234567' }));
  const [, name, p] = calls[0];
  assert.equal(name, 'purchase');
  assert.deepEqual(p.user_data, { email: 'jane.doe@example.com', phone: '18123158899', user_id: '1234567' });
  // Everything that already passed stays identical.
  assert.equal(p.transaction_id, '101614'); assert.equal(p.tax, 0); assert.equal(p.shipping, 0); assert.equal(p.value, 39);
  assert.equal(p.items[0].item_id, 'SKF-APF-1'); assert.equal(p.items[0].item_category_id, 2765);
});
test('short user ids and non-E.164 phones are left out', () => {
  const { calls, adapter } = load();
  adapter.send('purchase', ec, evt({ customer_email: 'a@b.co', customer_phone: '812-315-8899', customer_id: '5' }));
  assert.deepEqual(calls[0][2].user_data, { email: 'a@b.co' });
});
test('phone alone is enough', () => {
  const { calls, adapter } = load();
  adapter.send('purchase', ec, evt({ customer_phone: '+447700900123' }));
  assert.deepEqual(calls[0][2].user_data, { phone: '447700900123' });
});
test('no identity -> no user_data key, event still sent', () => {
  const { calls, adapter } = load();
  adapter.send('purchase', ec, evt({ visitor_type: 'guest', customer_email: 'not-an-email' }));
  assert.equal('user_data' in calls[0][2], false); assert.equal(calls.length, 1);
});
test('checkout events also carry user_data', () => {
  const { calls, adapter } = load();
  adapter.send('begin_checkout', ec, evt({ customer_email: 'x@y.com' }));
  adapter.send('add_payment_info', ec, evt({ customer_email: 'x@y.com' }));
  assert.deepEqual(calls.map(c => c[2].user_data), [{ email: 'x@y.com' }, { email: 'x@y.com' }]);
});
test('browse events carry user_data once the shopper is known; page_view stays bare', () => {
  const { calls, adapter } = load();
  adapter.send('view_item', ec, evt({ customer_email: 'x@y.com' }));
  adapter.send('add_to_cart', ec, evt({}));
  adapter.send('page_view', {}, evt({ customer_email: 'x@y.com' }));
  assert.deepEqual(calls[0][2].user_data, { email: 'x@y.com' });
  assert.equal('user_data' in calls[1][2], false);
  assert.deepEqual(calls[2], ['track', 'page_view']);
});
test('kill switch window.__axonSendUserData = false', () => {
  for (const off of [false, 'false']) {
    const { calls, adapter } = load({ __axonSendUserData: off });
    adapter.send('purchase', ec, evt({ customer_email: 'x@y.com' }));
    assert.equal(calls[0][2].user_data, undefined);
  }
});
test('missing user_properties does not throw', () => {
  const { calls, adapter } = load();
  adapter.send('purchase', ec, { event: 'dl_purchase' }); adapter.send('purchase', ec, undefined);
  assert.equal(calls.length, 2);
});

test('every item gets a numeric item_category_id (Pixel Helper item warning)', () => {
  const { calls, adapter } = load();
  const two = { ...ec, items: [ec.items[0], { ...ec.items[0], item_id: 'SKF-APF-2', item_category: undefined }] };
  for (const name of ['view_item', 'add_to_cart', 'begin_checkout', 'purchase']) adapter.send(name, two, evt({}));
  for (const c of calls) assert.deepEqual(c[2].items.map(i => i.item_category_id), [2765, 2765]);
});
test('numeric SDK category wins; configured fallback overrides default; junk config ignored', () => {
  let r = load(); r.adapter.send('view_item', { ...ec, items: [{ ...ec.items[0], item_category: '473' }] }, evt({}));
  assert.equal(r.calls[0][2].items[0].item_category_id, 473);
  r = load({ __axonItemCategoryId: '567' }); r.adapter.send('view_item', ec, evt({}));
  assert.equal(r.calls[0][2].items[0].item_category_id, 567);
  r = load({ __axonItemCategoryId: 'Skin Care' }); r.adapter.send('view_item', ec, evt({}));
  assert.equal(r.calls[0][2].items[0].item_category_id, 2765);
});

// AXON Pixel Helper 1.3.6 rules (https://s.axon.ai/_assets/pixel-helper/structures.yaml + its image_url check):
// every AxonItem field below is Recommended (orange when missing or malformed); purchase also requires user_data.email.
const ITEM_RECOMMENDED = ['item_variant_id', 'item_id', 'item_name', 'item_category_id', 'image_url', 'price', 'quantity'];
const AXON_IMAGE_RE = /^https?:\/\/(?:[\w-]+\.)+[\w-]+(?:\/[\w-./?%&=]*)?\.(png|jpe?g)(?:[?#].*)?$/i;
const itemWarnings = (it) => ITEM_RECOMMENDED.filter(k => it[k] === undefined || it[k] === null || it[k] === '')
  .concat(it.image_url !== undefined && !AXON_IMAGE_RE.test(it.image_url) ? ['image_url format'] : [])
  .concat(typeof it.item_category_id !== 'number' ? ['item_category_id type'] : []);
// What the live SDK sent on 30 Oct 2026 (captured on try.skinofab.com): a .webp package thumbnail and no brand.
const liveItem = { item_id: 'SKF-APF-3-GIFTS', item_name: 'Adaptive Peptide Foundation', price: 75, quantity: 1, item_variant_id: '268',
  item_category: 'SKINOFAB Adaptive Peptide Foundation Funnel', item_image: 'https://d1w87fp8j98gad.cloudfront.net/media/thumbnails/269c586ec01f40a7b8849828c9a21cec.webp' };
test('live items pass every AXON Pixel Helper item rule (no orange)', () => {
  const { calls, adapter } = load();
  const live = { currency: 'USD', value: 75, items: [liveItem], transaction_id: '101700', tax: 0, shipping: 0 };
  for (const name of ['view_item', 'add_to_cart', 'begin_checkout', 'purchase']) adapter.send(name, live, evt({ customer_email: 'a@b.co' }));
  for (const [, name, p] of calls) {
    assert.deepEqual(itemWarnings(p.items[0]), [], name);
    assert.equal(p.items[0].image_url, 'https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg');
    assert.equal(p.items[0].item_brand, 'SKINOFAB');
  }
  assert.equal(calls[3][2].user_data.email, 'a@b.co');
});
test('a .jpg from the SDK is kept; unknown variant falls back to window.__axonItemImage or is left out', () => {
  let r = load(); r.adapter.send('view_item', { ...ec, items: [{ ...liveItem, item_image: 'https://x.example.com/p.jpg' }] }, evt({}));
  assert.equal(r.calls[0][2].items[0].image_url, 'https://x.example.com/p.jpg');
  r = load({ __axonItemImage: 'https://x.example.com/f.png' }); r.adapter.send('view_item', { ...ec, items: [{ ...liveItem, item_variant_id: '99999' }] }, evt({}));
  assert.equal(r.calls[0][2].items[0].image_url, 'https://x.example.com/f.png');
  r = load(); r.adapter.send('view_item', { ...ec, items: [{ ...liveItem, item_variant_id: '99999' }] }, evt({}));
  assert.equal(r.calls[0][2].items[0].image_url, undefined);
});
test('every store variant maps to a .jpg/.png', () => {
  for (const v of ['15', '103', '268', '269', '270', '301', '170', '171', '172', '271', '203', '204', '205', '207', '208', '209', '236', '237']) {
    const { calls, adapter } = load(); adapter.send('view_item', { ...ec, items: [{ ...liveItem, item_variant_id: v }] }, evt({}));
    assert.match(calls[0][2].items[0].image_url, AXON_IMAGE_RE, v);
  }
});

// ---- Full replay against AXON Pixel Helper 1.3.6's own rules (fixtures/ are its structures.yaml and category ids) ----
const here = new URL('.', import.meta.url);
const SCHEMA = JSON.parse(fs.readFileSync(new URL('fixtures/axon-structures.json', here), 'utf8')).events;
const CATEGORY_IDS = new Set(JSON.parse(fs.readFileSync(new URL('fixtures/axon-category-ids.json', here), 'utf8')).ids);
const REQUIRED = 0, RECOMMENDED = 1;
// Mirrors the extension's validator: missing Required = error, missing Recommended = warning; then per struct type.
function validate(struct, value, path = '', out = { errors: [], warnings: [] }) {
  for (const [key, rule] of Object.entries(struct || {})) {
    const v = value ? value[key] : undefined, p = path + key;
    if (v === undefined || v === null) {
      if (rule.requirement === REQUIRED) out.errors.push(p + ' missing');
      else if (rule.requirement === RECOMMENDED) out.warnings.push(p + ' missing');
      continue;
    }
    const s = rule.struct;
    if (Array.isArray(s)) { (Array.isArray(v) ? v : []).forEach((el, i) => validate(s[0], el, `${p}[${i}].`, out)); continue; }
    if (s && typeof s === 'object') { validate(s, v, p + '.', out); continue; }
    if (s === 'image_url') { if (typeof v !== 'string') out.errors.push(p + ' not a string'); else if (!AXON_IMAGE_RE.test(v)) out.warnings.push(p + ' not .png/.jpg/.jpeg'); }
    else if (s === 'enum') { if (!(typeof v === 'string' && rule.enum.includes(v))) out.warnings.push(`${p} "${v}" not in ${rule.enum.join('/')}`); }
    else if (s === 'product_category_id') { if (isNaN(Number(v))) out.errors.push(p + ' not a number'); else if (!CATEGORY_IDS.has(Number(v))) out.warnings.push(p + ' unknown category'); }
    else if (s === 'string') { if (typeof v !== 'string' && isNaN(Number(v))) out.errors.push(p + ' not a string'); }
    else if (s === 'number') { if (Array.isArray(v) || isNaN(Number(v))) out.errors.push(p + ' not a number'); }
  }
  return out;
}
// The SDK's events as it builds them (campaign-cart 0.4.43): catalog items carry the variant and a .webp thumbnail;
// dl_purchase takes the buyer from order.user; an upsell built from the package has the SKU and no variant or image.
const buyer = { visitor_type: 'guest', customer_email: 'Buyer@Example.com', customer_phone: '+18123158899', customer_id: '1234567' };
const catalogItem = { ...liveItem };
const upsellItem = { item_id: 'SKF-LYB-1', item_name: 'The Lymphatic Brush', item_brand: 'The Lymphatic Brush',
  item_category: 'SKINOFAB Adaptive Peptide Foundation Funnel', item_variant: '', price: 19, quantity: 1, currency: 'USD' };
const FLOW = [
  ['view_item', { currency: 'USD', value: 75, items: [catalogItem] }, {}],
  ['add_to_cart', { currency: 'USD', value: 75, items: [catalogItem] }, {}],
  ['begin_checkout', { currency: 'USD', value: 75, items: [catalogItem] }, {}],
  ['add_payment_info', { currency: 'USD', value: 75, items: [catalogItem], payment_type: 'Credit Card' }, buyer],
  ['purchase', { currency: 'USD', value: 75, items: [catalogItem], transaction_id: '101700', tax: 0, shipping: 0 }, buyer],
  ['purchase', { currency: 'USD', value: 19, items: [upsellItem], transaction_id: '101700-US1', tax: 0, shipping: 0, affiliation: 'Upsell' }, buyer]
];
test('whole funnel passes AXON Pixel Helper: no errors, no warnings (all green)', () => {
  const { calls, adapter } = load();
  for (const [name, ecom, up] of FLOW) adapter.send(name, ecom, evt(up));
  calls.forEach(([, name, params], i) => {
    const r = validate(SCHEMA[name], params);
    assert.deepEqual(r, { errors: [], warnings: [] }, `${FLOW[i][0]} #${i}: ${JSON.stringify(r)}`);
  });
  const [, , purchase] = calls[4];
  assert.deepEqual(purchase.user_data, { email: 'buyer@example.com', phone: '18123158899', user_id: '1234567' });
  const [, , upsell] = calls[5];
  assert.equal(upsell.items[0].item_variant_id, '170');
  assert.equal(upsell.items[0].image_url, 'https://cdn.29next.store/media/skinofab/images/products/2026/10/card-642f9f.jpg');
  assert.equal(upsell.transaction_id, '101700-US1');
});
test('the validator reproduces the warnings seen in Pixel Helper on the earlier adapters', () => {
  const raw = (ecom) => ({ ...ecom, items: ecom.items.map(({ item_image, item_category, ...it }) => ({ ...it, image_url: item_image })) });
  const r1 = validate(SCHEMA.add_payment_info, { ...raw(FLOW[3][1]) });
  assert.ok(r1.warnings.some(w => w.includes('payment_type "Credit Card"')), JSON.stringify(r1));
  assert.ok(r1.warnings.some(w => w.includes('image_url not .png/.jpg/.jpeg')));
  const r2 = validate(SCHEMA.purchase, raw(FLOW[4][1]));
  assert.ok(r2.errors.includes('user_data missing'), JSON.stringify(r2));
});
test('payment_type maps every SDK label to the AXON enum', () => {
  const cases = { 'Credit Card': 'credit_card', 'Saved Card': 'credit_card', 'Apple Pay': 'wallet', 'Google Pay': 'wallet',
    PayPal: 'wallet', 'Shop Pay': 'wallet', Link: 'wallet', Swish: 'wallet', Twint: 'wallet', Klarna: 'deferred', Affirm: 'deferred',
    iDEAL: 'other', 'SEPA Direct Debit': 'other', Sofort: 'other', Giropay: 'other', Bancontact: 'other', External: 'other',
    credit_card: 'credit_card', 'Gift Card': 'redeemable', 'Cash on Delivery': 'payment_on_delivery' };
  for (const [label, want] of Object.entries(cases)) {
    const { calls, adapter } = load();
    adapter.send('add_payment_info', { currency: 'USD', value: 1, payment_type: label }, evt({}));
    assert.equal(calls[0][2].payment_type, want, label);
  }
});
