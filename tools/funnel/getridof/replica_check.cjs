// End-to-end check of the Get Rid Of replica funnel (/mouse-repellent-pouches/, campaign 2721). Places no order.
//   node tools/funnel/getridof/replica_check.cjs [baseUrl] [outDir]
// Local build:  http://localhost:8765  -> /mouse-repellent-pouches/ and /mouse-repellent-pouches/checkout/
// Store:        https://getridof.shop  -> /mouse-repellent-pouches/ and /mouse-repellent-pouches-checkout/
// Product page: brand, sections in the source order, buy box prices in both modes, every ADD TO CART -> this funnel's checkout.
// Checkout: each of the six bundles (1 / 3 / 5 packs, with Automatic Refills or one-time) priced by the live cart.
const { chromium } = require('playwright');
const zlib = require('zlib');
const base = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
const out = process.argv[3] || '.';
const SLUG = 'mouse-repellent-pouches';
const CHECKOUT = new RegExp(SLUG + '(\\/|-)checkout\\/');
const SECTIONS = [/Exactly What Happens/i, /Safe Home/i, /Properties Protected/i, /Real Results From/i, /Science of Nature/i, /Directions Of Use/i, /How We Stack Up/i, /90 Day Money Back Guarantee/i, /^FAQ$/i];
// bundle id -> [first-order total, text the refill terms must carry ('' = no refill terms)]
const BUNDLES = { buy1: ['22.49', '1 pack every 30 days for \\$34\\.99'], buy3: ['47.97', '3 packs every 90 days for \\$104\\.97'], buy5: ['64.95', '5 packs every 150 days for \\$174\\.95'],
                  ot1: ['34.99', ''], ot3: ['69.99', ''], ot5: ['104.95', ''] };
const SHOWN = { sub: ['$22.49', '$47.97', '$64.95'], one: ['$34.99', '$69.99', '$104.95'], full: ['$49.99', '$149.97', '$249.95'] };
let pass = 0, fail = 0;
const ok = (n, p, d = '') => { p ? pass++ : fail++; console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };

(async () => {
  const b = await chromium.launch();
  for (const vp of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 390, height: 664, isMobile: true, hasTouch: true }]) {
    const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, hasTouch: !!vp.hasTouch });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const external = [], broken = [];
    p.on('request', r => { const u = r.url(); if (/^https?:\/\/[^/]*(sofyre\.com|myshopify|shopify\.com|shopifycdn|gemcommerce|gempages|kachingappz|klaviyo)/.test(u)) external.push(u); });
    p.on('response', r => { if (r.status() >= 400 && new RegExp(SLUG + '|gromrp').test(r.url())) broken.push(r.status() + ' ' + r.url().slice(-60)); });
    const page = `${base}/${SLUG}/?utm_source=test`;
    const resp = await p.goto(page, { waitUntil: 'load' });
    const html = await resp.text();
    await p.waitForTimeout(600);
    ok(`[${vp.name}] product page loads`, resp.status() === 200 && /Rodent Repellent Pouches/.test(await p.title()), String(resp.status()));
    const gz = zlib.gzipSync(Buffer.from(html)).length;
    ok(`[${vp.name}] HTML under 260 KB compressed`, gz < 260 * 1024, Math.round(gz / 1024) + ' KB compressed, ' + Math.round(html.length / 1024) + ' KB raw');
    ok(`[${vp.name}] no old brand name anywhere in the page, no links to the other funnels`, !/sofyre/i.test(html) && !/\/(mouse-pouches|mice-5-reasons)[\/-]/.test(html));
    ok(`[${vp.name}] part of the campaign (next-funnel, page type product, SDK loader)`, /name="next-funnel" content="[^"]+"/.test(html) && /name="next-page-type" content="product"/.test(html) && /campaign-cart@v[\d.]+\/dist\/loader\.js/.test(html));
    const first = await p.evaluate(() => { const vis = s => [...document.querySelectorAll(s)].some(e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.top >= 0 && r.top < innerHeight; });
      return { logo: vis('img.header__heading-logo'), photo: vis('gp-carousel-v3.gp-feature-image-carousel img, .gp-feature-image-carousel img'), overflow: document.documentElement.scrollWidth > innerWidth + 1,
        title: (document.querySelector('.exp-atf__product-title') || {}).textContent || '' }; });
    ok(`[${vp.name}] first screen: Get Rid Of logo and the product photo; title carries the brand`, first.logo && first.photo && /Get Rid Of Rodent Repellent Pouches/.test(first.title), JSON.stringify(first));
    ok(`[${vp.name}] no sideways scroll`, !first.overflow);
    const body = await p.evaluate(S => { const heads = [...document.querySelectorAll('#MainContent h1, #MainContent h2, #MainContent h3, #MainContent [data-gp-text] p')].map(h => h.textContent.replace(/\s+/g, ' ').trim());
      const at = S.map(src => heads.findIndex(h => new RegExp(src, 'i').test(h)));
      return { at, text: document.body.innerText, footer: !!document.querySelector('.gro-footer a[href*="/privacy/"]') && !!document.querySelector('.gro-footer a[href*="/terms/"]'),
        pay: [...document.querySelectorAll('img')].map(i => i.getAttribute('src') || '').filter(s => /ShopPay|DinersClub|Maestro/.test(s)).length,
        menu: [...document.querySelectorAll('.header-mobile-menu__items a.header-items__link')].map(a => a.textContent.replace(/\s+/g, ' ').trim().slice(0, 30)) }; }, SECTIONS.map(r => r.source));
    ok(`[${vp.name}] the source page's nine sections, in its order`, body.at.every(i => i >= 0) && body.at.every((v, i) => i === 0 || v > body.at[i - 1]), body.at.join(','));
    ok(`[${vp.name}] 90-day guarantee everywhere (no 30-day left), no press logos`, !/30[\s-]?day/i.test(body.text) && /90-Day Money Back Guarantee/i.test(body.text) && !/BUZZ|as seen/i.test(body.text));
    ok(`[${vp.name}] brand footer with policy links; payment marks and menu limited to this store`, body.footer && body.pay === 0 && body.menu.length === 1 && /Rodent Repellent Pouches/.test(body.menu[0]), JSON.stringify(body.menu));
    // buy box: three bundles, Automatic Refills ticked on arrival, prices of both modes
    const box = () => p.evaluate(() => ({ ids: [...document.querySelectorAll('[data-gro-bundle]')].map(x => x.dataset.groBundle + (x.classList.contains('kaching-bundles__bar--selected') ? '*' : '')).join(','),
      price: [...document.querySelectorAll('[data-gro-bundle] .kaching-bundles__bar-price .money')].map(x => x.textContent.trim()), full: [...document.querySelectorAll('[data-gro-bundle] .kaching-bundles__bar-full-price .money')].map(x => x.textContent.trim()),
      refill: (document.querySelector('[data-gro-refill]') || { getAttribute: () => null }).getAttribute('aria-checked'), terms: (() => { const e = document.querySelector('.gro-subinfo'); return e && e.offsetParent !== null ? e.innerText.replace(/\s+/g, ' ') : ''; })() }));
    let s = await box();
    ok(`[${vp.name}] buy box: Buy 1 / Buy 2 Get 1 Free (selected) / Buy 3 Get 2 Free, refills ticked, subscriber prices + their terms`, s.ids === 'buy1,buy3*,buy5' && s.refill === 'true' && s.price.join() === SHOWN.sub.join() && s.full.join() === SHOWN.full.join() && /First order \$47\.97 · then \$34\.99 a pack, 3 packs every 90 days/.test(s.terms), JSON.stringify(s));
    await p.locator('[data-gro-refill]').click(); s = await box();
    ok(`[${vp.name}] buy box: refills unticked -> one-time prices, no refill terms`, s.refill === 'false' && s.price.join() === SHOWN.one.join() && s.terms === '', JSON.stringify(s));
    await p.locator('[data-gro-refill]').click();
    // interactions the page's own scripts used to provide
    const acc = p.locator('gp-accordion .gp-accordion-item').first();
    await acc.locator('.gp-accordion-item_header').click(); await p.waitForTimeout(200);
    const tabs = await p.evaluate(() => { const t = [...document.querySelectorAll('gp-tab li.gp-tab-item')].find(l => /Week 3/i.test(l.textContent)); if (t) t.click(); const f = [...document.querySelectorAll('gp-tab li.gp-tab-item')].find(l => /Farmers/i.test(l.textContent)); if (f) f.click();
      const shown = [...document.querySelectorAll('gp-tab .gp-tab-item')].filter(x => x.tagName !== 'LI' && getComputedStyle(x).display !== 'none').map(x => x.textContent); return { week3: shown.some(x => /KNOW NOT TO RETURN|THEY'VE LEFT/i.test(x)), farmers: shown.some(x => /Farmer ·|Farmer\b/.test(x)) }; });
    ok(`[${vp.name}] accordion opens; timeline and review tabs switch`, await acc.evaluate(i => i.classList.contains('gro-open')) && tabs.week3 && tabs.farmers, JSON.stringify(tabs));
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } });
    await p.waitForFunction(() => [...document.images].filter(i => i.offsetParent !== null).every(i => i.complete), null, { timeout: 20000 }).catch(() => {});
    const imgs = await p.evaluate(() => [...document.images].filter(i => i.offsetParent !== null && (!i.complete || i.naturalWidth === 0)).map(i => (i.getAttribute('src') || '').slice(-40)));
    ok(`[${vp.name}] all images load, no broken funnel files`, imgs.length === 0 && broken.length === 0, imgs.concat(broken).slice(0, 4).join(' '));
    await p.screenshot({ path: `${out}/replica-${vp.name}.png`, fullPage: false }).catch(() => {});
    // each bundle, with and without refills -> this funnel's checkout, priced by the live cart
    const summary = async (re) => { await p.waitForFunction(r => new RegExp(r).test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), re, { timeout: 30000 }).catch(() => {}); return (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' '); };
    for (const [id, [total, terms]] of Object.entries(BUNDLES)) {
      await p.goto(page, { waitUntil: 'load' });
      if (id.startsWith('ot')) await p.locator('[data-gro-refill]').click();
      await p.locator(`[data-gro-bundle="${id.replace('ot', 'buy')}"]`).click();
      await Promise.all([p.waitForURL(CHECKOUT), p.locator('#gro-buy').locator('xpath=following::*[@data-gro-atc][1]').click()]);
      const u = new URL(p.url());
      const t = await summary(total.replace('.', '\\.'));
      const st = await p.evaluate(() => ({ cards: [...document.querySelectorAll('[data-next-bundle-card]')].filter(c => c.offsetParent).map(c => c.getAttribute('data-next-bundle-id') + (c.classList.contains('next-selected') ? '*' : '')).join(','),
        terms: (() => { const e = document.querySelector('.gro-refill-terms'); return e && e.offsetParent !== null ? e.innerText.replace(/\s+/g, ' ') : ''; })(), other: /\/(mouse-pouches|mice-5-reasons)[\/-]/.test(document.documentElement.innerHTML),
        success: (document.querySelector('meta[name="next-success-url"]') || {}).content || '' }));
      const mode = id.startsWith('ot') ? 'ot' : 'buy';
      ok(`[${vp.name}] ${id}: ADD TO CART -> checkout, $${total}, three options of that purchase type, ${terms ? 'its refill terms' : 'no refill terms'}`,
        u.searchParams.get('forceBundleId') === 'main:' + id && u.searchParams.get('utm_source') === 'test' && new RegExp(total.replace('.', '\\.')).test(t) && st.cards === [1, 3, 5].map(n => mode + n + (mode + n === id ? '*' : '')).join(',') &&
        (terms ? new RegExp(terms).test(st.terms) : st.terms === '') && !st.other && new RegExp(SLUG).test(st.success), `${u.search} | ${st.cards} | ${t.slice(-34)}`);
    }
    ok(`[${vp.name}] no requests to the source store or its apps`, external.length === 0, external.slice(0, 2).join(' '));
    ok(`[${vp.name}] no page JS errors`, errs.length === 0, errs.slice(0, 2).join(' | '));
    await ctx.close();
  }
  await b.close();
  console.log(`\n${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
})();
