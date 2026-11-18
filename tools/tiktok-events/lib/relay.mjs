// TikTok Events API (server-to-server) for the Get Rid Of store: turns a NEXT order into TikTok Purchase events whose
// event_ids match the browser pixel's, so TikTok keeps one copy of each purchase (see README.md).
//
//   first purchase  -> event_id = order number            (the Campaign Cart SDK's dl_purchase transaction_id)
//   each upsell     -> event_id = {ref_id}-US{n}          (the SDK's dl_upsell_purchase id; ref_id = metadata.nc_ref_id)
//
// TikTok drops an Events API event whose event + event_id it already received in the last 48 hours, so a webhook that
// fires several times for the same order (order.created, then order.updated after each upsell, payment, ...) is safe as
// long as the order is younger than that. Orders placed more than WINDOW_HOURS ago are skipped for the same reason.
import { createHash } from 'node:crypto';

export const WINDOW_HOURS = 40;
export const EVENTS_URL = 'https://business-api.tiktok.com/open_api/v1.3/event/track/';

const sha256 = (v) => createHash('sha256').update(v, 'utf8').digest('hex');
const money = (v) => Math.round(Number(v || 0) * 100) / 100;

/** Lower-cased, trimmed email, or '' when it is not an email. */
export function normEmail(email) {
  const e = String(email || '').trim().toLowerCase();
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e) ? e : '';
}

/** E.164 (+ and digits), or ''. A 10-digit number is taken as US/CA (+1), as the store ships to the US. */
export function normPhone(phone) {
  const raw = String(phone || '').trim();
  let d = raw.replace(/\D/g, '');
  if (!d) return '';
  if (!raw.startsWith('+')) {
    if (d.length === 10) d = '1' + d;
    else if (d.length === 11 && d.startsWith('1')) { /* already has the country code */ }
    else if (raw.startsWith('00')) d = d.slice(2);
  }
  return d.length >= 8 && d.length <= 15 ? '+' + d : '';
}

/** TikTok "user" object: hashed email / phone / external_id, plus ip and user agent as they are. */
export function tiktokUser(order) {
  const u = order.user || {};
  const user = {};
  const email = normEmail(u.email);
  const phone = normPhone(u.phone_number || (order.billing_address || {}).phone_number || (order.shipping_address || {}).phone_number);
  if (email) user.email = sha256(email);
  if (phone) user.phone = sha256(phone);
  if (u.id !== undefined && u.id !== null) user.external_id = sha256(String(u.id));
  if (u.ip) user.ip = String(u.ip);
  if (u.user_agent) user.user_agent = String(u.user_agent);
  const meta = (order.attribution && order.attribution.metadata) || {};
  if (meta.ttclid) user.ttclid = String(meta.ttclid);
  if (meta.ttp || meta._ttp) user.ttp = String(meta.ttp || meta._ttp);
  return user;
}

function contents(lines) {
  return lines.map((l) => {
    const qty = Number(l.quantity || 1);
    const c = { content_id: String(l.sku || l.product_id || ''), quantity: qty, price: money(Number(l.price_incl_tax || 0) / qty) };
    if (l.product_title) c.content_name = l.product_title;
    return c;
  });
}

/**
 * The Purchase events for one order (already in TikTok's format), or a reason it has none.
 * @param {object} order   NEXT Admin API order (GET /api/admin/orders/{number}/)
 * @param {object} opts    { storeUrl, now (ms), windowHours }
 * @returns {{events: object[], skipped?: string}}
 */
export function buildEvents(order, { storeUrl = 'https://getridof.shop', now = Date.now(), windowHours = WINDOW_HOURS } = {}) {
  if (!order || !order.number) return { events: [], skipped: 'no order' };
  if (order.status === 'canceled' || order.status === 'cancelled') return { events: [], skipped: 'canceled' };
  const placed = Date.parse(order.date_placed || order.created_at || '');
  if (!placed) return { events: [], skipped: 'no date' };
  if (now - placed > windowHours * 3600e3) return { events: [], skipped: `placed more than ${windowHours}h ago` };
  const lines = order.lines || [];
  const base = lines.filter((l) => !l.is_upsell);
  const ups = lines.filter((l) => l.is_upsell).sort((a, b) => Number(a.id) - Number(b.id));
  const currency = order.currency || 'USD';
  const user = tiktokUser(order);
  const page = { url: String(storeUrl).replace(/\/+$/, '') + '/' };
  const updated = Math.min(now, Date.parse(order.updated_at || '') || now);
  const events = [];
  const upTotal = ups.reduce((s, l) => s + Number(l.price_incl_tax || 0), 0);
  if (base.length) {
    events.push({
      event: 'Purchase', event_time: Math.floor(placed / 1000), event_id: String(order.number), user, page,
      properties: { currency, value: money(Number(order.total_incl_tax || 0) - upTotal), content_type: 'product', contents: contents(base), order_id: String(order.number) },
    });
  }
  const ref = (order.metadata || {}).nc_ref_id;
  ups.forEach((l, i) => {
    events.push({
      event: 'Purchase', event_time: Math.floor(updated / 1000), event_id: `${ref || order.number}-US${i + 1}`, user, page,
      properties: { currency, value: money(l.price_incl_tax), content_type: 'product', contents: contents([l]), order_id: String(order.number) },
    });
  });
  return events.length ? { events } : { events: [], skipped: 'no lines' };
}

/** POST the events to the Events API. Returns { ok, status, code, message } (TikTok's code 0 = accepted). */
export async function sendToTikTok(events, { token, pixelId, testEventCode, fetchImpl = fetch } = {}) {
  if (!token) throw new Error('TIKTOK_ACCESS_TOKEN is not set');
  if (!pixelId) throw new Error('TIKTOK_PIXEL_ID is not set');
  const body = { event_source: 'web', event_source_id: pixelId, data: events };
  if (testEventCode) body.test_event_code = testEventCode;
  const res = await fetchImpl(EVENTS_URL, { method: 'POST', headers: { 'Access-Token': token, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  let j = {};
  try { j = await res.json(); } catch { /* not JSON */ }
  return { ok: res.ok && j.code === 0, status: res.status, code: j.code, message: j.message, request_id: j.request_id };
}

/** The order number in a NEXT webhook body, whatever its envelope ({data: order}, {object: order} or the order itself). */
export function orderNumber(body) {
  if (!body || typeof body !== 'object') return '';
  for (const o of [body.data, body.object, body.data && body.data.object, body.order, body]) {
    if (o && typeof o === 'object' && (o.number || o.order_number)) return String(o.number || o.order_number);
  }
  return '';
}

/** GET an order from the NEXT Admin API. */
export async function fetchOrder(number, { storeUrl, adminToken, fetchImpl = fetch } = {}) {
  if (!/^[0-9A-Za-z-]{1,40}$/.test(String(number))) throw new Error('bad order number');
  const res = await fetchImpl(`${String(storeUrl).replace(/\/+$/, '')}/api/admin/orders/${encodeURIComponent(number)}/`, {
    headers: { Authorization: `Bearer ${adminToken}`, 'X-29next-API-Version': '2024-04-01' },
  });
  if (!res.ok) throw new Error(`order ${number}: HTTP ${res.status}`);
  return res.json();
}
