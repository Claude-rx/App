// node --test tools/tiktok-events/test/*.test.mjs   (synthetic orders only: no customer data)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { buildEvents, normEmail, normPhone, tiktokUser, orderNumber, sendToTikTok, WINDOW_HOURS } from '../lib/relay.mjs';

const sha = (v) => createHash('sha256').update(v).digest('hex');
const NOW = Date.parse('2026-11-18T12:00:00Z');
const order = (over = {}) => ({
  number: '100432', status: 'open', currency: 'USD', is_test: false,
  date_placed: '2026-11-18T10:00:00Z', updated_at: '2026-11-18T10:03:00Z', total_incl_tax: '62.95',
  metadata: { nc_ref_id: 'REF123abc' },
  user: { id: 42, email: ' Buyer@Example.COM ', phone_number: '(217) 555-0100', ip: '203.0.113.9', user_agent: 'Mozilla/5.0' },
  attribution: { metadata: {} },
  lines: [
    { id: 265, sku: 'cdkh-16-1s', quantity: 3, price_incl_tax: '47.97', product_title: 'Mouse Repellent Pouches', is_upsell: false },
    { id: 266, sku: 'cdkh-16-1s', quantity: 1, price_incl_tax: '14.98', product_title: 'Mouse Repellent Pouches', is_upsell: true },
  ],
  ...over,
});

test('first purchase uses the order number, the upsell {ref_id}-US1 (the pixel ids)', () => {
  const { events } = buildEvents(order(), { now: NOW });
  assert.deepEqual(events.map((e) => e.event_id), ['100432', 'REF123abc-US1']);
  assert.ok(events.every((e) => e.event === 'Purchase'));
});

test('values: the first purchase excludes the upsell, the upsell is its own line', () => {
  const [p, u] = buildEvents(order(), { now: NOW }).events;
  assert.equal(p.properties.value, 47.97);
  assert.equal(u.properties.value, 14.98);
  assert.deepEqual(p.properties.contents, [{ content_id: 'cdkh-16-1s', quantity: 3, price: 15.99, content_name: 'Mouse Repellent Pouches' }]);
  assert.equal(p.properties.currency, 'USD');
  assert.equal(p.event_time, Math.floor(Date.parse('2026-11-18T10:00:00Z') / 1000));
});

test('two upsells are numbered in the order they were added', () => {
  const o = order();
  o.lines.push({ id: 270, sku: 'cdkh-16-1s', quantity: 5, price_incl_tax: '38.95', is_upsell: true }, { id: 268, sku: 'GRO-COPPER', quantity: 1, price_incl_tax: '9.99', is_upsell: true });
  assert.deepEqual(buildEvents(o, { now: NOW }).events.map((e) => e.event_id), ['100432', 'REF123abc-US1', 'REF123abc-US2', 'REF123abc-US3']);
  assert.equal(buildEvents(o, { now: NOW }).events[2].properties.contents[0].content_id, 'GRO-COPPER');   // id 268 before 270
});

test('user data: email and phone hashed after normalising, ip and user agent as they are', () => {
  const u = tiktokUser(order());
  assert.equal(u.email, sha('buyer@example.com'));
  assert.equal(u.phone, sha('+12175550100'));
  assert.equal(u.external_id, sha('42'));
  assert.equal(u.ip, '203.0.113.9');
  assert.equal(u.user_agent, 'Mozilla/5.0');
  assert.ok(!JSON.stringify(u).includes('Example'));
});

test('phone and email normalisation', () => {
  assert.equal(normPhone('+44 20 7946 0018'), '+442079460018');
  assert.equal(normPhone('1-217-555-0100'), '+12175550100');
  assert.equal(normPhone('12'), '');
  assert.equal(normEmail('not an email'), '');
});

test('orders older than the dedup window, canceled orders and empty orders are skipped', () => {
  assert.match(buildEvents(order({ date_placed: '2026-11-16T10:00:00Z' }), { now: NOW }).skipped, new RegExp(`${WINDOW_HOURS}h`));
  assert.equal(buildEvents(order({ status: 'canceled' }), { now: NOW }).skipped, 'canceled');
  assert.equal(buildEvents(order({ lines: [] }), { now: NOW }).skipped, 'no lines');
});

test('without a ref_id the upsell falls back to the order number', () => {
  assert.equal(buildEvents(order({ metadata: {} }), { now: NOW }).events[1].event_id, '100432-US1');
});

test('webhook envelopes', () => {
  assert.equal(orderNumber({ data: { number: 100629 } }), '100629');
  assert.equal(orderNumber({ object: { number: '7' } }), '7');
  assert.equal(orderNumber({ number: '9', lines: [] }), '9');
  assert.equal(orderNumber({ event: 'order.created' }), '');
});

test('send: TikTok request shape, test code, and the reply', async () => {
  let seen;
  const fake = async (url, init) => { seen = { url, init }; return { ok: true, status: 200, json: async () => ({ code: 0, message: 'OK' }) }; };
  const r = await sendToTikTok(buildEvents(order(), { now: NOW }).events, { token: 'tok', pixelId: 'PIX', testEventCode: 'TEST1', fetchImpl: fake });
  assert.ok(r.ok);
  assert.equal(seen.url, 'https://business-api.tiktok.com/open_api/v1.3/event/track/');
  assert.equal(seen.init.headers['Access-Token'], 'tok');
  const b = JSON.parse(seen.init.body);
  assert.equal(b.event_source, 'web'); assert.equal(b.event_source_id, 'PIX'); assert.equal(b.test_event_code, 'TEST1'); assert.equal(b.data.length, 2);
});

test('send: a TikTok error code is not ok', async () => {
  const fake = async () => ({ ok: false, status: 401, json: async () => ({ code: 40105, message: 'Access token is incorrect' }) });
  const r = await sendToTikTok([{}], { token: 'x', pixelId: 'P', fetchImpl: fake });
  assert.equal(r.ok, false); assert.equal(r.code, 40105);
});
