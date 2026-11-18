// Netlify Function: NEXT order webhook -> TikTok Events API (Purchase + upsell Purchases). See ../../README.md.
// Environment (Netlify > Site configuration > Environment variables; never in the repository):
//   TIKTOK_ACCESS_TOKEN     Events API access token (TikTok Events Manager > the pixel > Settings)
//   TIKTOK_PIXEL_ID         default DBUORJRC77UCDH70RUD0
//   TIKTOK_TEST_EVENT_CODE  optional: while set, events go to Events Manager's Test Events tab only
//   NEXT_ADMIN_TOKEN        NEXT Admin API token with orders read access (the order is read from the store, not trusted from the body)
//   NEXT_STORE_URL          default https://getridof.29next.store (Admin API host)
//   PAGE_URL                default https://getridof.shop (the "page" TikTok sees on server events)
//   RELAY_KEY               a long random string; the webhook URL carries it as ?key=..., other calls get 401
import { timingSafeEqual } from 'node:crypto';
import { buildEvents, sendToTikTok, orderNumber, fetchOrder } from '../../lib/relay.mjs';

const env = (k, d = '') => (globalThis.Netlify && Netlify.env.get(k)) || process.env[k] || d;
const json = (status, obj) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });

function keyOk(given, want) {
  if (!want || !given) return false;
  const a = Buffer.from(String(given)), b = Buffer.from(String(want));
  return a.length === b.length && timingSafeEqual(a, b);
}

export default async (req) => {
  if (req.method !== 'POST') return json(405, { error: 'POST only' });
  if (!keyOk(new URL(req.url).searchParams.get('key'), env('RELAY_KEY'))) return json(401, { error: 'bad key' });
  let body;
  try { body = await req.json(); } catch { return json(400, { error: 'body is not JSON' }); }
  const number = orderNumber(body);
  if (!number) return json(202, { skipped: 'no order in this webhook' });
  const storeUrl = env('NEXT_STORE_URL', 'https://getridof.29next.store');
  let order;
  try {
    order = await fetchOrder(number, { storeUrl, adminToken: env('NEXT_ADMIN_TOKEN') });
  } catch (e) {
    console.error('tiktok-events: order lookup failed', number, String(e && e.message));
    return json(502, { error: 'order lookup failed' });   // non-2xx: NEXT retries the webhook
  }
  const testCode = env('TIKTOK_TEST_EVENT_CODE');
  if (order.is_test && !testCode) return json(200, { order: number, skipped: 'test order' });
  const { events, skipped } = buildEvents(order, { storeUrl: env('PAGE_URL', 'https://getridof.shop') });
  if (!events.length) return json(200, { order: number, skipped });
  const r = await sendToTikTok(events, { token: env('TIKTOK_ACCESS_TOKEN'), pixelId: env('TIKTOK_PIXEL_ID', 'DBUORJRC77UCDH70RUD0'), testEventCode: testCode });
  console.log('tiktok-events', number, events.map((e) => e.event_id).join(','), r.ok ? 'sent' : `failed ${r.status} ${r.code} ${r.message}`);
  return json(r.ok ? 200 : 502, { order: number, event_ids: events.map((e) => e.event_id), tiktok: { code: r.code, message: r.message } });
};

export const config = { path: '/tiktok-events' };
