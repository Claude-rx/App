// End-to-end check of the Get Rid Of listicle funnel (/mice-5-reasons/). Places no order.
//   node tools/funnel/getridof/listicle_check.cjs [baseUrl] [outDir]
// Local build:  http://localhost:8765  -> /mice-5-reasons/ and /mice-5-reasons/checkout/
// Store:        https://getridof.shop  -> /mice-5-reasons/ and /mice-5-reasons-checkout/
// Listicle: first screen, the five reasons, the how-it-works animation, no prices, every button -> this funnel's checkout.
// Checkout: Subscribe & Save / One-time switch, 1x and Buy 2 Get 1 FREE, gifts box lock state, totals against the live cart.
const { chromium } = require('playwright');
const zlib = require('zlib');
const base = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
const out = process.argv[3] || '.';
const SLUG = 'mice-5-reasons';
const CHECKOUT = new RegExp(SLUG + '(\\/|-)checkout\\/');
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
    // no prices on the listicle; every button goes to this funnel's checkout
    const priced = await p.evaluate(() => ({ box: !!document.querySelector('[data-gro-bundle], [data-gro-sub], [data-p], [data-total]'),
      amounts: (document.body.innerText.match(/\$(22\.49|34\.99|47\.97|69\.99|64\.95|104\.95|49\.99|149\.97|15\.99|23\.33|1\.08)/g) || []).length,
      card: !!document.querySelector('#gro-buy.ofr [data-gro-atc]'), hrefs: [...document.querySelectorAll('main a.btn, .sb a.btn')].map(a => a.getAttribute('href')), scroll: document.querySelectorAll('main [data-gro-scroll]').length }));
    ok(`[${vp.name}] no prices and no buy box; offer card present`, !priced.box && priced.amounts === 0 && priced.card && priced.scroll === 0, JSON.stringify({ box: priced.box, amounts: priced.amounts, card: priced.card }));
    ok(`[${vp.name}] every button points at this funnel's checkout`, priced.hrefs.length >= 5 && priced.hrefs.every(h => CHECKOUT.test(h)), priced.hrefs.join(' '));
    // images: scroll the page, nothing broken
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } });
    await p.waitForFunction(() => [...document.images].filter(i => i.offsetParent !== null).every(i => i.complete), null, { timeout: 15000 }).catch(() => {});
    const imgs = await p.evaluate(() => [...document.images].filter(i => i.offsetParent !== null && (!i.complete || i.naturalWidth === 0)).map(i => (i.getAttribute('src') || '').slice(-40)));
    ok(`[${vp.name}] all images load`, imgs.length === 0, imgs.slice(0, 4).join(' '));
    await p.screenshot({ path: `${out}/listicle-${vp.name}.png`, fullPage: false }).catch(() => {});
    // hero button -> this funnel's checkout, tracking parameters kept
    await p.evaluate(() => scrollTo(0, 0));
    await Promise.all([p.waitForURL(CHECKOUT), p.locator('.lh [data-gro-atc]').click()]);
    let u = new URL(p.url());
    ok(`[${vp.name}] "Shop now" -> this funnel's checkout on Buy 2, Get 1 FREE + utm kept`, u.searchParams.get('forceBundleId') === 'main:buy3' && u.searchParams.get('utm_source') === 'test', u.pathname + u.search);
    // the offer is chosen in the checkout: Subscribe & Save / One-time switch, 1x and Buy 2 Get 1 FREE, gifts box
    const summary = async (re) => { await p.waitForFunction(r => new RegExp(r).test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), re, { timeout: 30000 }).catch(() => {}); return (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' '); };
    const st = () => p.evaluate(() => ({ cards: [...document.querySelectorAll('[data-next-bundle-card]')].filter(c => c.offsetParent).map(c => c.getAttribute('data-next-bundle-id') + (c.classList.contains('next-selected') ? '*' : '')).join(','),
      locked: [...document.querySelectorAll('.gro-gift__t i em')].filter(e => getComputedStyle(e).display !== 'none').length, terms: (() => { const e = document.querySelector('.gro-refill-terms'); return e && e.offsetParent !== null ? e.innerText.replace(/\s+/g, ' ') : ''; })() }));
    let t = await summary('47\\.97'); let s = await st();
    ok(`[${vp.name}] checkout: Buy 2, Get 1 FREE subscribed by default, $47.97, gifts unlocked, 3-pack refill terms`, /47\.97/.test(t) && s.cards === 'buy1,buy3*' && s.locked === 0 && /3 packs every 90 days for \$104\.97/.test(s.terms), s.cards + ' | locked ' + s.locked + ' | ' + t.slice(-40));
    await p.locator('[data-next-bundle-id="buy1"]').click(); t = await summary('22\\.49'); s = await st();
    ok(`[${vp.name}] checkout: 1x subscribed $22.49, the two bonus gifts lock, 1-pack refill terms`, /22\.49/.test(t) && s.cards === 'buy1*,buy3' && s.locked === 2 && /1 pack every 30 days for \$34\.99/.test(s.terms), s.cards + ' | locked ' + s.locked);
    await p.locator('.gro-mode [data-gro-mode="ot"]').click(); t = await summary('34\\.99'); s = await st();
    ok(`[${vp.name}] checkout: switch to one-time -> 1x $34.99, no refill terms`, /34\.99/.test(t) && s.cards === 'ot1*,ot3' && s.terms === '' && await p.evaluate(() => { const d = document.querySelector('.submit-section__disclaimer'); return !!d && !/Automatic Refills/.test(d.innerText); }), s.cards + ' | ' + t.slice(-40));
    await p.locator('[data-next-bundle-id="ot3"]').click(); t = await summary('69\\.99'); s = await st();
    ok(`[${vp.name}] checkout: one-time Buy 2, Get 1 FREE $69.99, gifts unlocked`, /69\.99/.test(t) && s.cards === 'ot1,ot3*' && s.locked === 0, s.cards + ' | locked ' + s.locked);
    await p.locator('.gro-sw__o [data-gro-mode="buy"]').click(); t = await summary('47\\.97'); s = await st();
    ok(`[${vp.name}] checkout: "Switch to Subscribe & Save" -> $47.97 with refill terms`, /47\.97/.test(t) && s.cards === 'buy1,buy3*' && /3 packs every 90 days/.test(s.terms), s.cards);
    const links = await p.evaluate(() => ({ success: (document.querySelector('meta[name="next-success-url"]') || {}).content || '', other: /mouse-pouches/.test(document.documentElement.innerHTML) }));
    ok(`[${vp.name}] checkout stays in this funnel (success url, no links to the other funnel)`, new RegExp(SLUG).test(links.success) && !links.other, links.success);
    ok(`[${vp.name}] no requests to the source store`, external.length === 0, external.slice(0, 2).join(' '));
    ok(`[${vp.name}] no page JS errors`, errs.length === 0, errs.slice(0, 2).join(' | '));
    await ctx.close();
  }
  await b.close();
  console.log(`\n${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
})();
