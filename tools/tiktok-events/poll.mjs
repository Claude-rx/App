// Scheduled TikTok Events API sender (GitHub Actions, .github/workflows/tiktok-events.yml): the no-server alternative
// to the webhook function. Every run reads the store's recent orders and sends their Purchase / upsell Purchase events
// (lib/relay.mjs: same event_ids as the browser pixel, so TikTok keeps one copy of each).
//
// Which orders: placed in the last 40 hours AND changed in the last LOOKBACK_MINUTES (default 60). A run every 10
// minutes therefore sends a new order (and each upsell added to it) a few times at most; TikTok drops the repeats
// (same event + event_id within 48 hours). Orders older than 40 hours are never sent.
//
// Environment: TIKTOK_ACCESS_TOKEN, NEXT_ADMIN_TOKEN (repository secrets), optional TIKTOK_TEST_EVENT_CODE,
// TIKTOK_PIXEL_ID (default DBUORJRC77UCDH70RUD0), NEXT_STORE_URL, PAGE_URL, LOOKBACK_MINUTES.
//   node tools/tiktok-events/poll.mjs              send
//   node tools/tiktok-events/poll.mjs --dry-run    list what would be sent (no TikTok token needed)
import { buildEvents, sendToTikTok, fetchOrder, WINDOW_HOURS } from './lib/relay.mjs';

const DRY = process.argv.includes('--dry-run');
const env = (k, d = '') => process.env[k] || d;
const STORE = env('NEXT_STORE_URL', 'https://getridof.29next.store').replace(/\/+$/, '');
const ADMIN = env('NEXT_ADMIN_TOKEN');
const TOKEN = env('TIKTOK_ACCESS_TOKEN');
const TEST = env('TIKTOK_TEST_EVENT_CODE');
const LOOKBACK = Number(env('LOOKBACK_MINUTES', '60'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const gh = process.env.GITHUB_ACTIONS === 'true';

if (!ADMIN || (!DRY && !TOKEN)) {
  const msg = 'TikTok Events API: secrets TIKTOK_ACCESS_TOKEN and NEXT_ADMIN_TOKEN are not set yet; nothing sent.';
  console.log(gh ? `::warning::${msg}` : msg);
  process.exit(0);
}

async function admin(path, tries = 4) {
  for (let i = 0; ; i++) {
    const res = await fetch(`${STORE}/api/admin/${path}`, { headers: { Authorization: `Bearer ${ADMIN}`, 'X-29next-API-Version': '2024-04-01' } });
    if (res.status === 429 && i < tries) { await sleep(5000 * (i + 1)); continue; }
    if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
    return res.json();
  }
}

const now = Date.now();
const oldest = now - WINDOW_HOURS * 3600e3, changedSince = now - LOOKBACK * 60e3;
const recent = [];
let page = 'orders/?limit=100';
while (page) {
  const d = await admin(page);
  const rows = d.results || [];
  for (const o of rows) {
    const placed = Date.parse(o.date_placed || o.created_at || '');
    const changed = Date.parse(o.updated_at || '') || placed;
    if (placed >= oldest && changed >= changedSince && (!o.is_test || TEST)) recent.push(o.number);
  }
  const last = rows[rows.length - 1];
  const more = d.next && last && Date.parse(last.date_placed || last.created_at || '') >= oldest;
  page = more ? String(d.next).replace(/^.*\/api\/admin\//, '') : '';
}

const events = [], log = [];
for (const number of recent) {
  let order;
  for (let i = 0; ; i++) {
    try { order = await fetchOrder(number, { storeUrl: STORE, adminToken: ADMIN }); break; }
    catch (e) { if (i >= 3 || !/HTTP 429/.test(String(e.message))) throw e; await sleep(5000 * (i + 1)); }
  }
  const r = buildEvents(order, { storeUrl: env('PAGE_URL', 'https://getridof.shop'), now });
  if (r.events.length) { events.push(...r.events); log.push(`${number}: ${r.events.map((e) => e.event_id).join(', ')}`); }
  else log.push(`${number}: skipped (${r.skipped})`);
  await sleep(700);   // stay under the Admin API rate limit
}

console.log(`orders placed in the last ${WINDOW_HOURS}h and changed in the last ${LOOKBACK} min: ${recent.length}`);
log.forEach((l) => console.log('  ' + l));
if (!events.length) process.exit(0);
if (DRY) { console.log(`dry run: ${events.length} event(s) not sent`); process.exit(0); }

let failed = 0;
for (let i = 0; i < events.length; i += 500) {
  const chunk = events.slice(i, i + 500);
  const r = await sendToTikTok(chunk, { token: TOKEN, pixelId: env('TIKTOK_PIXEL_ID', 'DBUORJRC77UCDH70RUD0'), testEventCode: TEST });
  if (r.ok) console.log(`sent ${chunk.length} event(s) to TikTok${TEST ? ' as test events' : ''} (request ${r.request_id})`);
  else { failed++; console.log(`${gh ? '::error::' : ''}TikTok refused: HTTP ${r.status} code ${r.code} ${r.message}`); }
}
process.exit(failed ? 1 : 0);
