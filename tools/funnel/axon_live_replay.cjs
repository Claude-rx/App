// Live AXON replay: runs both funnels on try.skinofab.com in Chromium, captures every axon(track) call and grades it
// with AXON Pixel Helper 1.3.6 rules (GREEN / ORANGE / RED). Usage: [CHROMIUM_PATH=...] node tools/funnel/axon_live_replay.cjs
// Run both live funnels, capture axon('track', ...) calls, validate each against AXON Pixel Helper 1.3.6 rules.
const { chromium } = require(require('path').join(__dirname, '../../campaigns/skinofab/node_modules/playwright'));
const fs = require('fs');
const FX = require('path').join(__dirname, '../../fixes/axon-purchase-user-data/fixtures/');
const SCHEMA = JSON.parse(fs.readFileSync(FX + 'axon-structures.json', 'utf8')).events;
const CATS = new Set(JSON.parse(fs.readFileSync(FX + 'axon-category-ids.json', 'utf8')).ids);
const IMG = /^https?:\/\/(?:[\w-]+\.)+[\w-]+(?:\/[\w-./?%&=]*)?\.(png|jpe?g)(?:[?#].*)?$/i;
function validate(struct, value, path = '', out = { errors: [], warnings: [] }) {
  for (const [key, rule] of Object.entries(struct || {})) {
    const v = value ? value[key] : undefined, p = path + key;
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
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  let bad = 0;
  const FUNNELS = [['APF', 'adaptive-foundation-offer'], ['STICK', 'foundation-stick-offer'], ['TRIAL', 'adaptive-foundation-trial']]
    .filter(([label]) => !process.env.ONLY || process.env.ONLY.split(',').includes(label));
  for (const [label, start] of FUNNELS) {
    const page = await (await browser.newContext({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36' })).newPage();
    await page.addInitScript(() => {
      window.__ax = []; let real;
      Object.defineProperty(window, 'axon', { configurable: true, get() { return real; },
        set(fn) { real = function () { try { window.__ax.push(JSON.parse(JSON.stringify([...arguments]))); } catch (e) {} return fn.apply(this, arguments); }; Object.assign(real, fn); } });
    });
    const seen = [];
    const grab = async (where) => { for (const c of await page.evaluate(() => window.__ax.splice(0))) if (c[0] === 'track') seen.push([where, c[1], c[2] || {}]); };
    for (let attempt = 0; attempt < 3; attempt++) {
      try { await page.goto(`https://try.skinofab.com/${start}/?r=${Date.now()}`, { waitUntil: 'networkidle', timeout: 60000 }); break; }
      catch (e) { if (attempt === 2) throw e; }
    }
    await page.waitForTimeout(4000); await grab('offer');
    const cta = page.locator('a[href*="checkout"], [data-next-checkout], button[data-next-action]').first();
    if (await cta.count()) { await Promise.all([page.waitForURL(/checkout/, { timeout: 30000 }).catch(() => {}), cta.click().catch(() => {})]); await page.waitForTimeout(6000); await grab('checkout'); }
    // Type the shopper's email the way a visitor does, then check events carry user_data where AXON allows it.
    const email = page.locator('[data-next-checkout-field="email"], input[type="email"]').first();
    if (await email.count()) { await email.fill('pixel.check@example.com').catch(() => {}); await email.blur().catch(() => {}); await page.waitForTimeout(2500); await grab('checkout+email'); }
    console.log(`\n== ${label} (${page.url().replace(/\?.*/, '')})`);
    for (const [where, name, params] of seen) {
      if (name === 'page_view') { console.log(`  ${where.padEnd(15)} page_view            OK (bare)`); continue; }
      const r = validate(SCHEMA[name], params);
      const status = r.errors.length ? 'RED' : r.warnings.length ? 'ORANGE' : 'GREEN';
      if (status !== 'GREEN') bad++;
      const it = (params.items || [])[0] || {};
      console.log(`  ${where.padEnd(15)} ${name.padEnd(20)} ${status}  ${[...r.errors, ...r.warnings].join('; ')}`);
      console.log(`      item: id=${it.item_id} variant=${it.item_variant_id} cat=${it.item_category_id} brand=${it.item_brand} img=${(it.image_url || '').split('/').pop()} | user_data=${params.user_data ? Object.keys(params.user_data).join('+') : 'none'}`);
    }
    await page.context().close();
  }
  await browser.close();
  console.log(`\n${bad ? bad + ' event(s) not green' : 'ALL CAPTURED EVENTS GREEN'}`);
})().catch(e => { console.error(e); process.exit(1); });
