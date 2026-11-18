// The webhook endpoint, with fake network calls (no store, no TikTok).
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';

process.env.RELAY_KEY = 'k'.repeat(32);
process.env.TIKTOK_ACCESS_TOKEN = 'tok';
process.env.NEXT_ADMIN_TOKEN = 'adm';
const { default: handler } = await import('../netlify/functions/tiktok-events.mjs');

const placed = new Date(Date.now() - 3600e3).toISOString();
const ORDER = { number: '555', status: 'open', currency: 'USD', is_test: false, date_placed: placed, updated_at: placed, total_incl_tax: '47.97',
  metadata: { nc_ref_id: 'R1' }, user: { id: 1, email: 'a@b.co' }, lines: [{ id: 1, sku: 'cdkh-16-1s', quantity: 3, price_incl_tax: '47.97', is_upsell: false }] };
let calls, order, tiktokReply;
beforeEach(() => {
  calls = []; order = { ...ORDER }; tiktokReply = { code: 0, message: 'OK' };
  globalThis.fetch = async (url, init = {}) => {
    calls.push({ url: String(url), init });
    if (String(url).includes('/api/admin/orders/')) return { ok: true, status: 200, json: async () => order };
    return { ok: tiktokReply.code === 0, status: tiktokReply.code === 0 ? 200 : 400, json: async () => tiktokReply };
  };
});
const post = (body, key = process.env.RELAY_KEY) => handler(new Request(`https://x.test/tiktok-events?key=${key}`, { method: 'POST', body: JSON.stringify(body) }));

test('wrong key: 401, nothing fetched', async () => {
  const r = await post({ data: { number: '555' } }, 'nope');
  assert.equal(r.status, 401); assert.equal(calls.length, 0);
});

test('GET: 405', async () => {
  assert.equal((await handler(new Request(`https://x.test/tiktok-events?key=${process.env.RELAY_KEY}`))).status, 405);
});

test('a webhook without an order: 202, nothing sent', async () => {
  const r = await post({ event: 'customer.created', data: { id: 3 } });
  assert.equal(r.status, 202); assert.equal(calls.length, 0);
});

test('an order: read from the Admin API, then one Purchase sent to TikTok', async () => {
  const r = await post({ event_type: 'order.created', data: { number: '555' } });
  const j = await r.json();
  assert.equal(r.status, 200); assert.deepEqual(j.event_ids, ['555']);
  assert.match(calls[0].url, /\/api\/admin\/orders\/555\/$/);
  assert.equal(calls[0].init.headers.Authorization, 'Bearer adm');
  assert.equal(calls[1].url, 'https://business-api.tiktok.com/open_api/v1.3/event/track/');
  assert.equal(JSON.parse(calls[1].init.body).event_source_id, 'DBUORJRC77UCDH70RUD0');
});

test('a test order is skipped without a test event code', async () => {
  order.is_test = true;
  const r = await post({ data: { number: '555' } });
  assert.equal((await r.json()).skipped, 'test order'); assert.equal(calls.length, 1);
});

test('TikTok refuses: 502, so NEXT retries', async () => {
  tiktokReply = { code: 40105, message: 'Access token is incorrect' };
  assert.equal((await post({ data: { number: '555' } })).status, 502);
});
