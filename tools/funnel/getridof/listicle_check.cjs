// End-to-end check of the Get Rid Of listicle funnel (/mice-5-reasons/). Places no order.
//   node tools/funnel/getridof/listicle_check.cjs [baseUrl] [outDir]
// Local build:  http://localhost:8765  -> /mice-5-reasons/ and /mice-5-reasons/checkout/
// Store:        https://getridof.shop  -> /mice-5-reasons/ and /mice-5-reasons-checkout/
// Listicle: first screen, the five reasons, the how-it-works animation, the offer box (3 bundles x subscribe / one-time),
// every in-article button reaching the offer, ADD TO CART -> this funnel's checkout with the right bundle and total.
const { chromium } = require('playwright');
const zlib = require('zlib');
const base = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
const out = process.argv[3] || '.';
const SLUG = 'mice-5-reasons';
const CHECKOUT = new RegExp(SLUG + '(\\/|-)checkout\\/');
const PRICES = { buy1: ['22.49', '34.99'], buy3: ['47.97', '69.99'], buy5: ['64.95', '104.95'] };   // [subscribe, one-time]
let pass = 0, fail = 0;
const ok = (n, p, d = '') => { p ? pass++ : fail++; console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };

(async () => {
  const b = await chromium.launch();
  for (const vp of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 390, height: 664, isMobile: true, hasTouch: true }]) {
    const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, hasTouch: !!vp.hasTouch });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const external = []; p.on('request', r => { const u = r.url(); if (/^https?:\/\/[^/]*(sofyre\.com|shopify|gemcommerce|pagedeck)/.test(u)) external.push(u); });
    const resp = await p.goto(`${base}/${SLUG}/?utm_source=test`, { waitUntil: 'load' });
    const html = await resp.text();
    await p.waitForTimeout(600);
    ok(`[${vp.name}] listicle loads`, resp.status() === 200 && /5 Reasons/.test(await p.title()), String(resp.status()));
    const gz = zlib.gzipSync(Buffer.from(html)).length;
    ok(`[${vp.name}] page is lean (HTML under 85 KB compressed)`, gz < 85 * 1024, Math.round(gz / 1024) + ' KB compressed, ' + Math.round(html.length / 1024) + ' KB raw');
    ok(`[${vp.name}] no SoFyre text, no links to the other funnel`, !/sofyre/i.test(html) && !/mouse-pouches/.test(html));
    ok(`[${vp.name}] part of the campaign (next-funnel, page type product, SDK loader)`, /name="next-funnel" content="[^"]+"/.test(html) && /name="next-page-type" content="product"/.test(html) && /campaign-cart@v[\d.]+\/dist\/loader\.js/.test(html));
    const first = await p.evaluate(() => { const vis = s => [...document.querySelectorAll(s)].some(e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.top >= 0 && r.top < innerHeight; });
      return { h1: vis('h1'), rating: vis('.rate'), img: vis('.lh__m img'), overflow: document.documentElement.scrollWidth > innerWidth + 1 }; });
    ok(`[${vp.name}] first screen: headline, rating and the hero image`, first.h1 && first.rating && first.img, JSON.stringify(first));
    ok(`[${vp.name}] no sideways scroll`, !first.overflow);
    const body = await p.evaluate(() => ({ reasons: [...document.querySelectorAll('.rs h2')].map(h => h.textContent.trim().slice(0, 28)), nums: [...document.querySelectorAll('.rs__n')].map(n => n.textContent).join(''),
      instead: document.querySelectorAll('.rs .ok').length, quotes: document.querySelectorAll('.rs .qt').length, demo: !!document.querySelector('.rs .demo svg .m1'), anim: getComputedStyle(document.querySelector('.demo .m1')).animationName,
      wall: document.querySelectorAll('.wall .wc').length, thread: document.querySelectorAll('.thr .cm').length, faq: document.querySelectorAll('.faq details').length }));
    ok(`[${vp.name}] five numbered reasons, each with "what works instead" and a customer quote`, body.nums === '12345' && body.instead === 5 && body.quotes >= 5, JSON.stringify(body.reasons));
    ok(`[${vp.name}] root solution: the how-it-works animation is in reason 2 and runs`, body.demo && body.anim && body.anim !== 'none', body.anim);
    ok(`[${vp.name}] reviews, comment thread and questions are on the page`, body.wall >= 5 && body.thread >= 6 && body.faq >= 4, `${body.wall} review cards, ${body.thread} comments, ${body.faq} questions`);
    const tall = await p.evaluate(() => [...document.querySelectorAll('.sbx')].filter(e => e.offsetParent && e.getBoundingClientRect().height > 44).length);
    ok(`[${vp.name}] star rows are one line high`, tall === 0);
    // every in-article button brings the offer box into view
    const hrefs = await p.evaluate(() => [...document.querySelectorAll('main a.btn')].map(a => a.getAttribute('href')));
    ok(`[${vp.name}] in-article buttons point at the offer box`, hrefs.length >= 4 && hrefs.every(h => h === '#gro-buy'), hrefs.join(' '));
    await p.locator('.lh a.btn').click(); await p.waitForTimeout(1300);
    ok(`[${vp.name}] "Shop now" scrolls to the offer`, await p.evaluate(() => { const r = document.getElementById('gro-buy').getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; }));
    ok(`[${vp.name}] default = Buy 2 Get 1 Free, subscribed`, await p.evaluate(() => document.querySelector('[data-gro-bundle="buy3"]').classList.contains('on') && document.querySelector('[data-gro-sub]').checked));
    let priceOk = true; const seen = [];
    for (const mode of [0, 1]) {
      if (mode === 1) await p.locator('[data-gro-sub]').uncheck();
      for (const id of ['buy1', 'buy3', 'buy5']) { const t = await p.locator(`[data-gro-bundle="${id}"] [data-p]`).innerText(); seen.push(t); if (!t.includes(PRICES[id][mode])) priceOk = false; }
    }
    ok(`[${vp.name}] offer prices: subscribe 22.49 / 47.97 / 64.95, one-time 34.99 / 69.99 / 104.95`, priceOk, seen.join(' '));
    await p.locator('[data-gro-sub]').check();
    // images: scroll the page, nothing broken
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } });
    await p.waitForFunction(() => [...document.images].filter(i => i.offsetParent !== null).every(i => i.complete), null, { timeout: 15000 }).catch(() => {});
    const imgs = await p.evaluate(() => [...document.images].filter(i => i.offsetParent !== null && (!i.complete || i.naturalWidth === 0)).map(i => (i.getAttribute('src') || '').slice(-40)));
    ok(`[${vp.name}] all images load`, imgs.length === 0, imgs.slice(0, 4).join(' '));
    await p.screenshot({ path: `${out}/listicle-${vp.name}.png`, fullPage: false }).catch(() => {});
    // subscribed 5-pack -> this funnel's checkout
    await p.locator('[data-gro-bundle="buy5"]').scrollIntoViewIfNeeded(); await p.locator('[data-gro-bundle="buy5"]').click();
    await Promise.all([p.waitForURL(CHECKOUT), p.locator('#gro-buy [data-gro-atc]').click()]);
    let u = new URL(p.url());
    ok(`[${vp.name}] ADD TO CART -> this funnel's checkout with buy5 + utm kept`, u.searchParams.get('forceBundleId') === 'main:buy5' && u.searchParams.get('utm_source') === 'test', u.pathname + u.search);
    const summary = async (re) => { await p.waitForFunction(r => new RegExp(r).test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), re, { timeout: 30000 }).catch(() => {}); return (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' '); };
    let t = await summary('64\\.95');
    ok(`[${vp.name}] checkout: 5 subscribed packs, first order $64.95`, /64\.95/.test(t), t.slice(-90));
    const links = await p.evaluate(() => ({ success: (document.querySelector('meta[name="next-success-url"]') || {}).content || '', other: /mouse-pouches/.test(document.documentElement.innerHTML) }));
    ok(`[${vp.name}] checkout stays in this funnel (success url, no links to the other funnel)`, new RegExp(SLUG).test(links.success) && !links.other, links.success);
    // one-time single pack
    await p.goto(`${base}/${SLUG}/`, { waitUntil: 'load' }); await p.waitForTimeout(400);
    await p.locator('[data-gro-bundle="buy1"]').scrollIntoViewIfNeeded(); await p.locator('[data-gro-bundle="buy1"]').click();
    await p.locator('[data-gro-sub]').uncheck();
    await Promise.all([p.waitForURL(CHECKOUT), p.locator('#gro-buy [data-gro-atc]').click()]);
    u = new URL(p.url()); t = await summary('34\\.99');
    ok(`[${vp.name}] one-time 1 pack -> main:ot1, total $34.99`, u.searchParams.get('forceBundleId') === 'main:ot1' && /34\.99/.test(t), u.search + ' | ' + t.slice(-70));
    ok(`[${vp.name}] no requests to the source store`, external.length === 0, external.slice(0, 2).join(' '));
    ok(`[${vp.name}] no page JS errors`, errs.length === 0, errs.slice(0, 2).join(' | '));
    await ctx.close();
  }
  await b.close();
  console.log(`\n${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
})();
