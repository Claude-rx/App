// Preview (default) or send the TikTok Purchase events for one order: the same code path as the webhook function.
//   NEXT_ADMIN_TOKEN=... node tools/tiktok-events/send-order.mjs 100629                       preview (hashed user data)
//   ... TIKTOK_ACCESS_TOKEN=... node tools/tiktok-events/send-order.mjs 100629 --send --test-code TEST12345
// --send without --test-code sends live events (counted in reporting); --any-age ignores the 40-hour window.
import { buildEvents, sendToTikTok, fetchOrder } from './lib/relay.mjs';

const args = process.argv.slice(2);
const number = args.find((a) => /^\d+$/.test(a));
const flag = (n) => args.includes(n);
const val = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : ''; };
if (!number) { console.error('usage: send-order.mjs <order number> [--send] [--test-code CODE] [--any-age]'); process.exit(2); }

const storeUrl = process.env.NEXT_STORE_URL || 'https://getridof.29next.store';
const order = await fetchOrder(number, { storeUrl, adminToken: process.env.NEXT_ADMIN_TOKEN || 'proxy-injected' });
const { events, skipped } = buildEvents(order, { storeUrl: process.env.PAGE_URL || 'https://getridof.shop', windowHours: flag('--any-age') ? 1e6 : undefined });
if (!events.length) { console.log(`order ${number}: nothing to send (${skipped})`); process.exit(0); }
const shown = events.map((e) => ({ ...e, user: Object.fromEntries(Object.entries(e.user).map(([k, v]) => [k, ['ip', 'user_agent'].includes(k) ? '(set)' : v.slice(0, 12) + '…'])) }));
console.log(JSON.stringify(shown, null, 2));
if (!flag('--send')) { console.log('\npreview only: add --send (and --test-code CODE to keep it out of reporting)'); process.exit(0); }
const r = await sendToTikTok(events, { token: process.env.TIKTOK_ACCESS_TOKEN, pixelId: process.env.TIKTOK_PIXEL_ID || 'DBUORJRC77UCDH70RUD0', testEventCode: val('--test-code') });
console.log(r.ok ? `sent: ${events.map((e) => e.event_id).join(', ')}${val('--test-code') ? ' (test events)' : ''}` : `TikTok refused: ${r.status} ${r.code} ${r.message}`);
process.exit(r.ok ? 0 : 1);
