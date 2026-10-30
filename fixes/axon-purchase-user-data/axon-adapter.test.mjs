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
test('browse events never carry user_data; page_view stays bare', () => {
  const { calls, adapter } = load();
  adapter.send('view_item', ec, evt({ customer_email: 'x@y.com' }));
  adapter.send('add_to_cart', ec, evt({ customer_email: 'x@y.com' }));
  adapter.send('page_view', {}, evt({ customer_email: 'x@y.com' }));
  assert.equal(calls[0][2].user_data, undefined); assert.equal(calls[1][2].user_data, undefined);
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
