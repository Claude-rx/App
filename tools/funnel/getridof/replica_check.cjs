// End-to-end check of the Get Rid Of replica funnel (/mouse-repellent-pouches/, campaign 2721). Places no order.
//   node tools/funnel/getridof/replica_check.cjs [baseUrl] [outDir]
// Local build:  http://localhost:8765  -> /mouse-repellent-pouches/ and /mouse-repellent-pouches/checkout/
// Store:        https://getridof.shop  -> /mouse-repellent-pouches/ and /mouse-repellent-pouches-checkout/
// Product page: an exact copy of the source page (15 Nov 2026 capture) with this brand, its prices and the 90-day guarantee:
// sections in the source order, the offer-ladder bundle box in both states, tabs, photo strips, miniatures, every ADD TO CART.
// Checkout: each of the six bundles (1 / 3 / 5 packs, with Automatic Refills or one-time) priced by the live cart.
const { chromium } = require('playwright');
const zlib = require('zlib');
const base = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
const out = process.argv[3] || '.';
const SLUG = 'mouse-repellent-pouches';
const CHECKOUT = new RegExp(SLUG + '(\\/|-)checkout\\/');
const SECTIONS = [/Place These Pouches Anywhere Mice Hide/i, /Properties Protected/i, /Real Results From/i, /Exactly What Happens/i, /Science of Nature/i, /Safe Home/i, /Directions Of Use/i, /How We Stack Up/i, /90 Day Money Back Guarantee/i, /^FAQ$/i];
// bundle id -> [first-order total, text the refill terms must carry ('' = no refill terms)]
const BUNDLES = { buy1: ['22.49', '1 pack every 30 days for \\$34\\.99'], buy3: ['47.97', '3 packs every 90 days for \\$104\\.97'], buy5: ['64.95', '5 packs every 150 days for \\$174\\.95'],
                  ot1: ['34.99', ''], ot3: ['69.99', ''], ot5: ['104.95', ''] };
// the offer-ladder cards: price, compare-at, % OFF pill, saving and price per pouch, with and without Automatic Refills
const SHOWN = { full: ['$49.99', '$149.97', '$249.95'],
  sub: { price: ['$22.49', '$47.97', '$64.95'], off: ['55% OFF', '68% OFF', '74% OFF'], save: ['Save $27.50', 'Save $102.00', 'Save $185.00'], each: ['$1.87 Each Pouch', '$1.33 Each Pouch', '$1.08 Each Pouch'] },
  one: { price: ['$34.99', '$69.99', '$104.95'], off: ['30% OFF', '53% OFF', '58% OFF'], save: ['Save $15.00', 'Save $79.98', 'Save $145.00'], each: ['$2.92 Each Pouch', '$1.94 Each Pouch', '$1.75 Each Pouch'] } };
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
      const hero = document.querySelector('.gro-stage img'); const st = document.querySelector('.gro-stage').getBoundingClientRect();
      return { logo: vis('.header__heading-link img.gro-logo'), photo: !!hero && hero.naturalWidth > 0 && Math.abs(hero.getBoundingClientRect().width - st.width) < 2 && Math.abs(st.height - st.width) < 2, thumbs: vis('.gro-thumb'), overflow: document.documentElement.scrollWidth > innerWidth + 1,
        h1: (document.querySelector('#MainContent h1') || {}).textContent || '', brand: document.title }; });
    ok(`[${vp.name}] first screen: Get Rid Of logo, the square product photo filling its stage, miniatures, the source headline`, first.logo && first.photo && first.thumbs && /Place These Pouches Anywhere Mice Hide/.test(first.h1) && /Get Rid Of/.test(first.brand), JSON.stringify(first));
    ok(`[${vp.name}] no sideways scroll`, !first.overflow);
    const body = await p.evaluate(S => { const heads = [...document.querySelectorAll('#MainContent h1, #MainContent h2, #MainContent h3, #MainContent [data-gp-text] p')].map(h => h.textContent.replace(/\s+/g, ' ').trim());
      const at = S.map(src => heads.findIndex(h => new RegExp(src, 'i').test(h)));
      return { at, text: document.body.innerText, footer: ['/terms/', '/privacy/', '/refund-policy/', '/shipping-policy/', '/auto-refill-terms/', '/cookie-policy/', '/privacy-choices/', '/accessibility/', '/contact/', '/accounts/subscriptions/', '/product-safety/', '/mice/', '/groundhogs/'].every(x => !!document.querySelector('footer.gro-footer a[href*="' + x + '"]')) && !document.querySelector('footer form')
          && !!document.querySelector('footer.gro-footer a[href="#gro-faq"]') && !!document.querySelector('#gro-faq') && document.querySelectorAll('.gro-footer__pay img').length === 6,
        press: /BUZZ/i.test(document.querySelector('#MainContent').textContent), shopPay: document.querySelectorAll('shopify-accelerated-checkout, shop-pay-wallet-button, .shopify-payment-button').length,
        added: document.querySelectorAll('.gro-subinfo').length, track: [...document.querySelectorAll('a.header__icons-btn')].map(a => a.textContent.trim() + '>' + a.getAttribute('href')).join(),
        menu: [...document.querySelectorAll('.header-mobile-menu__items a.header-items__link')].map(a => a.textContent.replace(/\s+/g, ' ').trim().slice(0, 30)) }; }, SECTIONS.map(r => r.source));
    ok(`[${vp.name}] the source page's sections, in its order`, body.at.every(i => i >= 0) && body.at.every((v, i) => i === 0 || v > body.at[i - 1]), body.at.join(','));
    ok(`[${vp.name}] 90-day guarantee everywhere (no 30-day left); "Ships Today" and the press band as on the source`, !/30[\s-]?day/i.test(body.text) && /90-Day Money Back Guarantee/i.test(body.text) && /Ships\s+Today/.test(body.text) && body.press);
    ok(`[${vp.name}] the fuller footer: every policy, shop and help link, FAQ anchor, the six payment marks this checkout takes; no refill-terms line added; no Shop Pay button; "Track Order" goes to the store`, body.footer && body.added === 0 && body.shopPay === 0 && /^Track Order>https:\/\/getridof\.shop\//.test(body.track) && body.menu.length === 1, JSON.stringify({ footer: body.footer, added: body.added, track: body.track, menu: body.menu }));
    // bundle box = the source's offer ladder: 12 / 36 / 60 Pouches, 36 selected, Automatic Refills ticked, this campaign's numbers
    const box = () => p.evaluate(() => { const col = sel => [...document.querySelectorAll('[data-gro-bundle] ' + sel)].filter(e => e.getBoundingClientRect().height > 0).map(x => x.textContent.trim());
      return { ids: [...document.querySelectorAll('[data-gro-bundle]')].map(x => x.dataset.groBundle + (x.classList.contains('kaching-bundles__bar--selected') ? '*' : '')).join(','), title: col('.exp-ol-title').join('|'), pack: col('.exp-ol-pack').join('|'),
        price: col('.exp-ol-price'), full: col('.exp-ol-compare'), off: col('.exp-ol-pill'), save: col('.exp-ol-save'), each: col('.exp-ol-each'), badges: [...document.querySelectorAll('.exp-ol-badge')].map(x => x.textContent.replace(/\s+/g, ' ').trim()).join('|'),
        urgency: (document.querySelector('.exp-ol-urgency') || {}).textContent || '', old: [...document.querySelectorAll('[data-gro-bundle] .kaching-bundles__bar-content')].filter(e => e.getBoundingClientRect().height > 0).length,
        refill: (document.querySelector('[data-gro-refill]') || { getAttribute: () => null }).getAttribute('aria-checked'), refillText: (document.querySelector('.kaching-bundles__subscriptions') || {}).innerText || '' }; });
    const same = (a, b) => a.join() === b.join();
    let s = await box();
    ok(`[${vp.name}] bundle box layout: 12 / 36 / 60 Pouches with (1 Pack) / (3 Packs) / (5 Packs), High Demand line, BEST SELLER and LOWEST PRICE EVER badges, refills box`,
      s.ids === 'buy1,buy3*,buy5' && s.title === '12 Pouches|36 Pouches|60 Pouches' && s.pack === '(1 Pack)|(3 Packs)|(5 Packs)' && /High Demand — Selling Fast Due To Rodent Season/.test(s.urgency) && s.badges === '🔥 BEST SELLER|🔥 LOWEST PRICE EVER' && s.old === 0 && /Save 30% With Automatic Refills\.\s+Zero Commitment, Cancel Anytime/i.test(s.refillText), JSON.stringify({ ids: s.ids, badges: s.badges, old: s.old, refillText: s.refillText.replace(/\s+/g, ' ') }));
    ok(`[${vp.name}] bundle box, refills ticked: subscriber price, compare-at, % OFF, saving and price per pouch`, s.refill === 'true' && same(s.price, SHOWN.sub.price) && same(s.full, SHOWN.full) && same(s.off, SHOWN.sub.off) && same(s.save, SHOWN.sub.save) && same(s.each, SHOWN.sub.each), JSON.stringify([s.price, s.off, s.save, s.each]));
    await p.locator('[data-gro-refill]').click(); s = await box();
    ok(`[${vp.name}] bundle box, refills unticked: one-time price, % OFF, saving and price per pouch`, s.refill === 'false' && same(s.price, SHOWN.one.price) && same(s.full, SHOWN.full) && same(s.off, SHOWN.one.off) && same(s.save, SHOWN.one.save) && same(s.each, SHOWN.one.each), JSON.stringify([s.price, s.off, s.save, s.each]));
    await p.locator('[data-gro-refill]').click();
    // interactions the page's own scripts used to provide
    const acc = p.locator('gp-accordion .gp-accordion-item').first();
    await acc.locator('.gp-accordion-item_header').click(); await p.waitForTimeout(200);
    // miniatures under the main photo: seven, the first marked current; tapping the fourth moves the gallery to photo 4
    await p.evaluate(() => scrollTo(0, 0));
    const th0 = await p.evaluate(() => [...document.querySelectorAll('.gro-thumb')].filter(t => t.getBoundingClientRect().width > 30 && t.querySelector('img').naturalWidth > 0).length + ':' + [...document.querySelectorAll('.gro-thumb')].map(t => t.classList.contains('gro-thumb-active') ? 1 : 0).join(''));
    await p.locator('.gro-thumb').nth(3).click(); await p.waitForTimeout(700);
    const th1 = await p.evaluate(() => { const st = document.querySelector('.gro-stage').getBoundingClientRect(); const s4 = document.querySelectorAll('.gro-stage .gem-slider-wrapper > *')[3]; const r = s4.getBoundingClientRect(); const im = s4.querySelector('img');
      return { active: [...document.querySelectorAll('.gro-thumb')].map(t => t.classList.contains('gro-thumb-active') ? 1 : 0).join(''), aligned: Math.abs(r.left - st.left) < 2, loaded: im.naturalWidth > 100 }; });
    ok(`[${vp.name}] miniatures: seven under the photo; tapping one shows that photo`, th0 === '7:1000000' && th1.active === '0001000' && th1.aligned && th1.loaded, th0 + ' -> ' + JSON.stringify(th1));
    await p.locator('.gro-thumb').nth(0).click();
    // every tab of both tab groups opens a panel that is really on screen (not only display:block)
    const opened = [];
    for (const label of ['Week 1', 'Week 2', 'Week 3', 'Hours 1', 'RV Owner', 'Farmers', 'Homeowners']) {
      const li = p.locator('gp-tab li.gp-tab-item', { hasText: new RegExp(label, 'i') }).first(); await li.scrollIntoViewIfNeeded(); await li.click(); await p.waitForTimeout(250);
      opened.push(await li.evaluate((l, label) => { const tab = l.closest('gp-tab'); const panels = [...tab.querySelectorAll('.gp-tab-item')].filter(x => x.tagName !== 'LI' && x.parentElement.closest('gp-tab') === tab);
        const open = panels.filter(x => { const c = getComputedStyle(x); return c.display !== 'none' && c.visibility !== 'hidden' && x.getBoundingClientRect().height > 150; });
        const t = open.length === 1 ? open[0].innerText : ''; const want = { 'Week 1': /WEEK 1/, 'Week 2': /WEEK 2/, 'Week 3': /KNOW NOT TO RETURN/i, 'Hours 1': /HOUR 1-72/, 'RV Owner': /RV/, 'Farmers': /Farmer|feed|barn|bins/i, 'Homeowners': /Homeowner/ }[label];
        return (open.length === 1 && want.test(t) ? '' : '!') + label; }, label));
    }
    ok(`[${vp.name}] accordion opens; all four timeline tabs and all three review tabs show their content`, await acc.evaluate(i => i.classList.contains('gro-open')) && opened.every(x => x[0] !== '!'), opened.join(', '));
    // moving strips, as on the source page: the customer photos (one strip on wide screens, two on phones in opposite
    // directions) and, on phones, the press band above them
    const strips = await p.evaluate(() => [...document.querySelectorAll('gp-marquee')].filter(m => m.getBoundingClientRect().height > 20).map(m => { const c = getComputedStyle(m.querySelector('.rfm-marquee')); return (/BUZZ/i.test((m.closest('section') || m.parentElement).textContent) ? 'press' : 'photos') + ':' + c.animationName + '/' + parseFloat(c.animationDuration) + '/' + c.animationDirection + '/' + c.animationPlayState; }));
    const photos = strips.filter(x => x.startsWith('photos:'));
    ok(`[${vp.name}] photo strip${vp.isMobile ? 's (two, opposite directions) and the press band' : ''} moving`, strips.every(x => /:gp-merquee-scroll\/([1-9]\d*(\.\d+)?)\/(normal|reverse)\/running$/.test(x)) && photos.length === (vp.isMobile ? 2 : 1) && (!vp.isMobile || (/\/normal\//.test(photos[0]) && /\/reverse\//.test(photos[1]) && strips.length === 3)), strips.join(' | '));
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
      await Promise.all([p.waitForURL(CHECKOUT), p.locator('[data-gro-atc]').first().click()]);
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
