// Purchase replay without an order and without telling AppLovin anything: opens a funnel's first upsell page with an
// existing order's ref_id (the SDK loads that order from the Campaigns API and builds its real dl_purchase), blocks every
// request to AppLovin, records the axon('track', ...) calls the page makes, and grades them with AXON Pixel Helper 1.3.6.
// usage: [CHROMIUM_PATH=...] node tools/funnel/axon_purchase_replay.cjs <first-upsell-page> <order ref_id> [label]
const path = require('path'), fs = require('fs');
const { chromium } = require(path.join(__dirname, '../../campaigns/skinofab/node_modules/playwright'));
const FX = path.join(__dirname, '../../fixes/axon-purchase-user-data/fixtures/');
const SCHEMA = JSON.parse(fs.readFileSync(FX + 'axon-structures.json', 'utf8')).events;
const CATS = new Set(JSON.parse(fs.readFileSync(FX + 'axon-category-ids.json', 'utf8')).ids);
const IMG = /^https?:\/\/(?:[\w-]+\.)+[\w-]+(?:\/[\w-./?%&=]*)?\.(png|jpe?g)(?:[?#].*)?$/i;
function validate(struct, value, p0 = '', out = { errors: [], warnings: [] }) {
  for (const [key, rule] of Object.entries(struct || {})) {
    const v = value ? value[key] : undefined, p = p0 + key;
    if (v === undefined || v === null) { if (rule.requirement === 0) out.errors.push(p + ' missing'); else if (rule.requirement === 1) out.warnings.push(p + ' missing'); continue; }
    const s = rule.struct;
    if (Array.isArray(s)) { (Array.isArray(v) ? v : []).forEach((el, i) => validate(s[0], el, `${p}[${i}].`, out)); continue; }
    if (s && typeof s === 'object') { validate(s, v, p + '.', out); continue; }
    if (s === 'image_url') { if (typeof v !== 'string') out.errors.push(p); else if (!IMG.test(v)) out.warnings.push(p + ' not .png/.jpg'); }
    else if (s === 'enum') { if (!rule.enum.includes(v)) out.warnings.push(`${p}="${v}" not in enum`); }
    else if (s === 'product_category_id') { if (isNaN(Number(v))) out.errors.push(p); else if (!CATS.has(Number(v))) out.warnings.push(p + ' unknown'); }
    else if (s === 'string') { if (typeof v !== 'string' && isNaN(Number(v))) out.errors.push(p); }
    else if (s === 'number') { if (Array.isArray(v) || isNaN(Number(v))) out.errors.push(p); }
  }
  return out;
}
(async () => {
  const [page, ref, label = page] = process.argv.slice(2);
  if (!page || !ref) { console.error('usage: node axon_purchase_replay.cjs <first-upsell-page> <order ref_id> [label]'); process.exit(2); }
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const ctx = await browser.newContext({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36' });
  let blocked = 0;
  await ctx.route(/(axon\.ai|applovin\.com)/, (r) => { blocked++; return r.abort(); });   // nothing reaches AppLovin
  const tab = await ctx.newPage();
  await tab.addInitScript(() => {
    window.__ax = []; let real;
    Object.defineProperty(window, 'axon', { configurable: true, get() { return real; },
      set(fn) { real = function () { try { window.__ax.push(JSON.parse(JSON.stringify([...arguments]))); } catch (e) {} return fn.apply(this, arguments); }; Object.assign(real, fn); } });
  });
  await tab.goto(`https://try.skinofab.com/${page}/?ref_id=${encodeURIComponent(ref)}&r=${Date.now()}`, { waitUntil: 'networkidle', timeout: 60000 });
  await tab.waitForTimeout(8000);
  const calls = (await tab.evaluate(() => window.__ax)).filter(c => c[0] === 'track');
  console.log(`== ${label}: ${tab.url().replace(/ref_id=[^&]+/, 'ref_id=…')}  (AppLovin requests blocked: ${blocked})`);
  let purchases = 0, bad = 0;
  for (const [, name, params = {}] of calls) {
    if (name === 'page_view') { console.log('  page_view            OK (bare)'); continue; }
    const r = validate(SCHEMA[name], params);
    const status = r.errors.length ? 'RED' : r.warnings.length ? 'ORANGE' : 'GREEN';
    if (name === 'purchase') purchases++;
    if (status !== 'GREEN') bad++;
    console.log(`  ${name.padEnd(20)} ${status}  ${[...r.errors, ...r.warnings].join('; ')}`);
    if (name === 'purchase') {
      const ud = params.user_data || {};
      console.log(`      transaction_id=${params.transaction_id} value=${params.value} tax=${params.tax} shipping=${params.shipping} items=${(params.items || []).length}`);
      for (const it of params.items || []) console.log(`      item ${it.item_id} variant=${it.item_variant_id} cat=${it.item_category_id} img=${String(it.image_url || '').split('/').pop()} price=${it.price} qty=${it.quantity} brand=${it.item_brand}`);
      console.log(`      user_data: ${Object.keys(ud).map(k => k === 'user_id' ? 'user_id=' + ud[k] : k).join(', ') || 'none'}`);
    }
  }
  await browser.close();
  console.log(purchases ? (bad ? `${bad} event(s) not green` : 'PURCHASE GREEN') : 'NO PURCHASE FIRED');
  process.exit(purchases && !bad ? 0 : 1);
})().catch(e => { console.error(e); process.exit(1); });
