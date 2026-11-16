// End-to-end check of the Get Rid Of 9-reason listicle funnel (/mice-9-reasons/, campaign 2796). Places no order.
//   node tools/funnel/getridof/nine_check.cjs [baseUrl] [outDir]
// Local build:  http://localhost:8765  -> /mice-9-reasons/, /mice-9-reasons/checkout/, /mice-9-reasons/upsell/ ...
// Store:        https://getridof.shop  -> /mice-9-reasons/, /mice-9-reasons-checkout/, /mice-9-reasons-home-plan/ ...
// Listicle: first screen, nine reasons (each with "Why it works"), the labelled Amazon quotes, the linked sources,
//           no invented expert, no prices, every button -> this funnel's checkout.
// Checkout: names on one row, short address form that opens when an address is typed, totals against the live cart.
// Offers:   the home quiz picks the plan card, the SDK prices every card, accept / decline go to the right pages.
const { chromium } = require('playwright');
const zlib = require('zlib');
const base = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
const out = process.argv[3] || '.';
const SLUG = 'mice-9-reasons';
const LOCAL = /localhost|127\.0\.0\.1/.test(base);
const STORE = { checkout: 'checkout', upsell: 'home-plan', downsell: 'last-offer', receipt: 'thank-you' };
const url = (page) => page ? (LOCAL ? `${base}/${SLUG}/${page}/` : `${base}/${SLUG}-${STORE[page]}/`) : `${base}/${SLUG}/`;
const CHECKOUT = new RegExp(SLUG + '(\\/|-)checkout\\/');
let pass = 0, fail = 0;
const ok = (n, p, d = '') => { p ? pass++ : fail++; console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };
const money = (s) => /^\$\d+\.\d\d$/.test((s || '').trim());

(async () => {
  const b = await chromium.launch();
  for (const vp of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 390, height: 664, isMobile: true, hasTouch: true }]) {
    const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, hasTouch: !!vp.hasTouch });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const external = []; p.on('request', r => { const u = r.url(); if (/^https?:\/\/[^/]*(sofyre\.com|shopify|gemcommerce|pagedeck)/.test(u)) external.push(u); });
    const T = `[${vp.name}]`;

    // ---------- the listicle ----------
    const resp = await p.goto(url('') + '?utm_source=test', { waitUntil: 'load' });
    const html = await resp.text();
    await p.waitForTimeout(600);
    ok(`${T} listicle loads`, resp.status() === 200 && /9 Reasons/.test(await p.title()), String(resp.status()));
    const gz = zlib.gzipSync(Buffer.from(html)).length;
    ok(`${T} page is lean (HTML under 85 KB compressed)`, gz < 85 * 1024, Math.round(gz / 1024) + ' KB compressed, ' + Math.round(html.length / 1024) + ' KB raw');
    ok(`${T} no SoFyre text, no links to the other funnels`, !/sofyre/i.test(html) && !/mouse-pouches|mice-5-reasons|mouse-repellent-pouches/.test(html));
    ok(`${T} part of the campaign (next-funnel, page type product, SDK loader)`, /name="next-funnel" content="[^"]+"/.test(html) && /name="next-page-type" content="product"/.test(html) && /campaign-cart@v[\d.]+\/dist\/loader\.js/.test(html));
    const first = await p.evaluate(() => { const vis = s => [...document.querySelectorAll(s)].some(e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.top >= 0 && r.top < innerHeight; });
      return { h1: vis('h1'), by: vis('.by'), img: vis('.lh__m img'), overflow: document.documentElement.scrollWidth > innerWidth + 1 }; });
    ok(`${T} first screen: headline, byline and the hero image`, first.h1 && first.by && first.img, JSON.stringify(first));
    ok(`${T} no sideways scroll`, !first.overflow);
    const body = await p.evaluate(() => ({ reasons: [...document.querySelectorAll('.rs h2')].map(h => h.textContent.trim().slice(0, 24)), nums: [...document.querySelectorAll('.rs__n')].map(n => n.textContent).join(''),
      why: [...document.querySelectorAll('.rs .ok > b')].filter(x => /why it works/i.test(x.textContent)).length, quotes: document.querySelectorAll('.rs .qt').length,
      demo: !!document.querySelector('#r1 .demo svg .m1'), anim: getComputedStyle(document.querySelector('.demo .m1')).animationName,
      check: document.querySelectorAll('#r6 .chk li').length, plan: document.querySelectorAll('#r7 .pl li').length,
      wall: document.querySelectorAll('.wall .wc').length, thread: document.querySelectorAll('.thr .cm').length, faq: document.querySelectorAll('.faq details').length,
      fit: document.querySelectorAll('.fit__y li').length + '/' + document.querySelectorAll('.fit__n li').length }));
    ok(`${T} nine numbered reasons, each with a "Why it works" box`, body.nums === '123456789' && body.why === 9, body.nums + ' | ' + body.why + ' boxes');
    ok(`${T} root solution: the how-it-works animation is in reason 1 and runs`, body.demo && body.anim && body.anim !== 'none', body.anim);
    const rootS = await p.evaluate(() => ({ root: document.querySelectorAll('#root .root__p, #root .root__s').length, jump: !!document.querySelector('#root a[href="#r2"]'),
      cards: [...document.querySelectorAll('#r2 .whys .why')].map(c => (c.querySelector('.why__j') || {}).textContent + ' | ' + (c.querySelector('.why__h b') || {}).textContent + ' | ' + (c.querySelector('.why__r') ? 'result' : '') + ' | ' + (c.querySelector('figure svg') ? 'anim' : '')) }));
    ok(`${T} root problem and root solution are stated before the reasons, with a jump to the ingredients`, rootS.root === 2 && rootS.jump);
    ok(`${T} reason 2: one card per ingredient (peppermint, cinnamon, cedarwood, castor), each with its job, what it does, the result and an animation`,
      rootS.cards.length === 4 && ['Peppermint', 'Cinnamon', 'Cedarwood', 'Castor'].every((n, i) => rootS.cards[i].includes(n)) && rootS.cards.every(c => /Job \d/.test(c) && /result/.test(c) && /anim/.test(c)), rootS.cards.map(c => c.split(' | ')[0]).join(' ; '));
    ok(`${T} the 14-day check (3 steps) and the plan for mice already inside (4 steps)`, body.check === 3 && body.plan === 4, `${body.check} / ${body.plan}`);
    ok(`${T} reviews, comment thread, "is this for you" and questions are on the page`, body.wall >= 5 && body.thread >= 6 && body.faq >= 5 && body.fit === '3/3', `${body.wall} review cards, ${body.thread} comments, ${body.faq} questions, fit ${body.fit}`);
    // honesty rules
    const honest = await p.evaluate(() => { const t = document.body.innerText; const aq = document.querySelector('.aq');
      return { amazon: !!aq && aq.querySelectorAll('blockquote').length === 3 && /not reviews of Get Rid Of/i.test(aq.innerText),
        sources: [...document.querySelectorAll('#research .rsrc a')].map(a => a.href), blank: [...document.querySelectorAll('#research .rsrc a')].every(a => a.target === '_blank' && /noopener/.test(a.rel)),
        noEndorse: /do not endorse Get Rid Of/i.test(document.querySelector('#research').innerText), expert: document.querySelectorAll('.xp').length,
        banned: (t.match(/as seen on|100% (working|guaranteed to work)|kills? (mice|rodents)|#1 expert|doctor recommended/gi) || []), notFor: /groundhogs/i.test(t) && /will not evict/i.test(t) }; });
    ok(`${T} Amazon quotes are labelled as other brands' reviews`, honest.amazon);
    ok(`${T} six sources, each an outside https link that opens in a new tab; "do not endorse" note`, honest.sources.length === 6 && honest.sources.every(h => /^https:\/\/[^/]*\.(edu|gov|com)\//.test(h)) && honest.blank && honest.noEndorse, honest.sources.map(h => new URL(h).hostname).join(' '));
    ok(`${T} no invented expert, no TV or "100%" claims; says what it does not do`, honest.expert === 0 && honest.banned.length === 0 && honest.notFor, 'expert blocks ' + honest.expert + ' ' + honest.banned.join(','));
    const tall = await p.evaluate(() => [...document.querySelectorAll('.sbx')].filter(e => e.offsetParent && e.getBoundingClientRect().height > 44).length);
    ok(`${T} star rows are one line high`, tall === 0);
    const priced = await p.evaluate(() => ({ box: !!document.querySelector('[data-gro-bundle], [data-gro-sub], [data-p], [data-total]'),
      amounts: (document.querySelector('main').innerText.match(/\$(22\.49|34\.99|47\.97|69\.99|64\.95|104\.95|49\.99|149\.97|15\.99|14\.98|48\.95|38\.95)/g) || []).length,
      card: !!document.querySelector('#gro-buy.ofr [data-gro-atc]'), hrefs: [...document.querySelectorAll('main a.btn, .sb a.btn')].map(a => a.getAttribute('href')) }));
    ok(`${T} no prices and no buy box; offer card present`, !priced.box && priced.amounts === 0 && priced.card, JSON.stringify({ box: priced.box, amounts: priced.amounts, card: priced.card }));
    ok(`${T} every button points at this funnel's checkout`, priced.hrefs.length >= 7 && priced.hrefs.every(h => CHECKOUT.test(h)), priced.hrefs.length + ' buttons');
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } });
    await p.waitForFunction(() => [...document.images].filter(i => i.offsetParent !== null).every(i => i.complete), null, { timeout: 15000 }).catch(() => {});
    const imgs = await p.evaluate(() => [...document.images].filter(i => i.offsetParent !== null && (!i.complete || i.naturalWidth === 0)).map(i => (i.getAttribute('src') || '').slice(-40)));
    ok(`${T} all images load`, imgs.length === 0, imgs.slice(0, 4).join(' '));
    await p.screenshot({ path: `${out}/nine-${vp.name}.png`, fullPage: false }).catch(() => {});

    // ---------- the checkout ----------
    await p.evaluate(() => scrollTo(0, 0));
    await Promise.all([p.waitForURL(CHECKOUT), p.locator('.lh [data-gro-atc]').click()]);
    const u = new URL(p.url());
    ok(`${T} hero button -> this funnel's checkout on Buy 2, Get 1 FREE + utm kept`, u.searchParams.get('forceBundleId') === 'main:buy3' && u.searchParams.get('utm_source') === 'test', u.pathname + u.search);
    await p.waitForFunction(() => /47\.97/.test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), null, { timeout: 30000 }).catch(() => {});
    const total = (await p.locator('[data-next-cart-summary]').first().innerText().catch(() => '')).replace(/\s+/g, ' ');
    ok(`${T} checkout: Buy 2, Get 1 FREE subscribed by default, $47.97 from the live cart`, /47\.97/.test(total), total.slice(-50));
    const terms = () => p.evaluate(() => { const e = document.querySelector('.gro-sw__s .gro-sw__r'); return e && e.offsetParent !== null ? e.innerText.replace(/\s+/g, ' ') : ''; });
    const t3 = await terms();
    await p.locator('.gro-mode [data-gro-mode="ot"]').click(); await p.waitForTimeout(600); const tOne = await terms();
    await p.locator('.gro-mode [data-gro-mode="buy"]').click();
    await p.waitForFunction(() => /47\.97/.test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), null, { timeout: 30000 }).catch(() => {});
    ok(`${T} Subscribe & Save states its refill size, schedule and price where it is chosen; a one-time purchase shows none`, /3 packs every 90 days for \$104\.97/.test(t3) && /until you cancel/.test(t3) && tOne === '', t3.slice(0, 90) + ' | one-time: "' + tOne + '"');
    // a reload must keep the buyer's own choice, although ?forceBundleId=main:buy3 is still in the address
    await p.locator('.gro-mode [data-gro-mode="ot"]').click(); await p.waitForTimeout(400);
    await p.locator('[data-next-bundle-id="ot1"]').click();
    await p.waitForFunction(() => /34\.99/.test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), null, { timeout: 30000 }).catch(() => {});
    await p.reload({ waitUntil: 'load' });
    await p.waitForFunction(() => /34\.99/.test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), null, { timeout: 30000 }).catch(() => {});
    const kept = await p.evaluate(() => ({ sel: [...document.querySelectorAll('[data-next-bundle-card].next-selected')].map(c => c.getAttribute('data-next-bundle-id')).join(), sum: ((document.querySelector('[data-next-cart-summary]') || {}).innerText || '').replace(/\s+/g, ' ').slice(-40), terms: (() => { const e = document.querySelector('.gro-sw__s .gro-sw__r'); return e && e.offsetParent !== null; })() }));
    ok(`${T} a reload keeps a one-time, 1-pack choice (no switch back to the subscription)`, /ot1/.test(kept.sel) && /34\.99/.test(kept.sum) && !kept.terms, JSON.stringify(kept));
    await p.locator('.gro-mode [data-gro-mode="buy"]').click(); await p.waitForTimeout(400);
    await p.locator('[data-next-bundle-id="buy3"]').click();
    await p.waitForFunction(() => /47\.97/.test((document.querySelector('[data-next-cart-summary]') || {}).innerText || ''), null, { timeout: 30000 }).catch(() => {});
    await p.waitForSelector('[data-next-address="shipping"][data-next-address-state="ready"]', { timeout: 30000 }).catch(() => {});
    const vis = () => p.evaluate(() => { const v = f => { const e = document.querySelector('#combo_form [data-next-checkout-field="' + f + '"]'); return !!e && e.offsetHeight > 0; };
      const r = f => document.querySelector('[data-next-checkout-field="' + f + '"]').getBoundingClientRect();
      return { fname: v('fname'), lname: v('lname'), country: v('country'), address1: v('address1'), city: v('city'), postal: v('postal'), phone: v('phone'), sameRow: Math.abs(r('fname').top - r('lname').top) < 2 && r('lname').left > r('fname').right }; });
    let f = await vis();
    ok(`${T} shipping step: first and last name on one row, then country and the address line only`, f.fname && f.lname && f.sameRow && f.country && f.address1 && !f.city && !f.postal && !f.phone, JSON.stringify(f));
    await p.fill('[data-next-checkout-field="address1"]', '123 Main St'); await p.waitForTimeout(400); f = await vis();
    ok(`${T} typing an address opens city, ZIP and phone`, f.city && f.postal && f.phone, JSON.stringify({ city: f.city, postal: f.postal, phone: f.phone }));
    // payment readiness: card fields load, the form fills, the button stops on the missing phone. Never submits an order.
    await p.waitForFunction(() => document.querySelector('[data-next-checkout-field="cc-number"] iframe') && document.querySelector('[data-next-checkout-field="cvv"] iframe'), null, { timeout: 45000 }).catch(() => {});
    await p.waitForTimeout(2500);
    const pay = await p.evaluate(() => { const ex = document.querySelector('[data-next-express-checkout="container"]');
      return { card: !!document.querySelector('[data-next-checkout-field="cc-number"] iframe'), cvv: !!document.querySelector('[data-next-checkout-field="cvv"] iframe'),
        express: ex ? [...ex.querySelectorAll('button, .payment-btn')].map(e => String(e.className)).join(' ') : '', radios: [...document.querySelectorAll('[data-next-payment-method]')].filter(r => r.offsetParent).map(r => r.getAttribute('data-next-payment-method') || r.value) }; });
    ok(`${T} card number and CVV fields load; PayPal express button and card option are shown`, pay.card && pay.cvv && /cc-paypal/.test(pay.express) && pay.radios.includes('credit'), pay.radios.join(','));
    const fill = async (sel, v) => { const el = p.locator(sel).first(); if (await el.count()) { await el.fill(v); await el.blur().catch(() => {}); } };
    await fill('[data-next-checkout-field="fname"]', 'Test'); await fill('[data-next-checkout-field="lname"]', 'Buyer'); await fill('[data-next-checkout-field="email"]', 'qa-test@getridof.shop');
    await fill('[data-next-checkout-field="city"]', 'New York');
    const prov = p.locator('[data-next-checkout-field="province"]').first(); if (await prov.count()) await prov.selectOption('NY').catch(() => {});
    await fill('[data-next-checkout-field="postal"]', '10118'); await p.waitForTimeout(1200);
    const orderPosts = []; p.on('request', r => { if (r.method() === 'POST' && /\/api\/v1\/orders/.test(r.url())) orderPosts.push(r.url()); });
    const btn = await p.evaluate(() => { const s = document.querySelector('.submit-button'); return s ? { text: s.innerText.trim(), disabled: s.disabled } : null; });
    await p.locator('.submit-button').click(); await p.waitForTimeout(2500);
    const stop = await p.evaluate(() => document.activeElement && document.activeElement.id);
    ok(`${T} order button is enabled and stops on the empty phone field (no order sent)`, btn && !btn.disabled && stop === 'phone' && orderPosts.length === 0, `focus=${stop} orderPosts=${orderPosts.length}`);
    const links = await p.evaluate(() => ({ success: (document.querySelector('meta[name="next-success-url"]') || {}).content || '', other: /mouse-pouches|mice-5-reasons/.test(document.documentElement.innerHTML) }));
    ok(`${T} checkout continues to this funnel's home-plan offer`, /mice-9-reasons(\/upsell|-home-plan)\//.test(links.success) && !links.other, links.success);

    // ---------- the home-plan offer (quiz) ----------
    await p.evaluate(() => { sessionStorage.setItem('gro_bundle', 'buy3'); sessionStorage.removeItem('gro_plan_tier'); });
    await p.goto(url('upsell'), { waitUntil: 'load' });
    await p.waitForFunction(() => { const e = [...document.querySelectorAll('#gro-plan .next-bundle-tier-grid [data-next-bundle-display="price"]')]; return e.length === 4 && e.every(x => /\$\d/.test(x.textContent)); }, null, { timeout: 30000 }).catch(() => {});
    const cards = () => p.evaluate(() => [...document.querySelectorAll('#gro-plan .next-bundle-tier-grid [data-next-bundle-card]')].map(e => ({ id: e.getAttribute('data-next-bundle-id'), sel: e.classList.contains('next-selected'), rec: e.hasAttribute('data-gq-rec'), price: (e.querySelector('[data-next-bundle-display="price"]') || {}).textContent || '' })));
    let cs = await cards();
    const num = (s) => parseFloat(String(s).replace(/[^0-9.]/g, ''));
    ok(`${T} offer page: four plan cards (1, 2, 3, 5 packs), each priced by the campaign`, cs.map(c => c.id).join() === 'home-plan-1,home-plan-2,home-plan-3,home-plan-5' && cs.every(c => money(c.price)), cs.map(c => c.price).join(' '));
    ok(`${T} prices make sense: 2 packs = 2 x 1 pack, 5 packs cost less per pack than 3`, Math.abs(num(cs[1].price) - 2 * num(cs[0].price)) < 0.02 && num(cs[3].price) / 5 < num(cs[2].price) / 3, cs.map(c => c.price).join(' '));
    await p.locator('[data-gro-quiz]').scrollIntoViewIfNeeded();
    await p.waitForFunction(() => [...document.querySelectorAll('[data-gro-quiz] [data-gq-home] img')].every(i => i.complete && i.naturalWidth > 0), null, { timeout: 15000 }).catch(() => {});
    const quiz = await p.evaluate(() => ({ homes: document.querySelectorAll('[data-gro-quiz] [data-gq-home]').length, imgs: [...document.querySelectorAll('[data-gro-quiz] [data-gq-home] img')].every(i => i.complete && i.naturalWidth > 0), q2: document.querySelector('[data-gq="2"]').hidden, r: document.querySelector('[data-gq="r"]').hidden }));
    ok(`${T} quiz: question 1 shows four homes with photos; question 2 and the result are hidden`, quiz.homes === 4 && quiz.imgs && quiz.q2 && quiz.r, JSON.stringify(quiz));
    await p.click('[data-gq-name="a two-story house"]'); await p.waitForTimeout(200); await p.click('[data-gq="2"] [data-gq-extra="1"] >> nth=0');
    await p.waitForFunction(() => { const c = document.querySelector('#gro-plan [data-next-bundle-id="home-plan-2"]'); return c && c.classList.contains('next-selected'); }, null, { timeout: 15000 }).catch(() => {});
    cs = await cards();
    const res = await p.evaluate(() => ({ total: document.querySelector('[data-gq-total]').textContent, ordered: document.querySelector('[data-gq-ordered]').textContent, gap: document.querySelector('[data-gq-gap]').textContent,
      cta: [...document.querySelectorAll('#gro-plan [data-next-upsell-action="add"]')].map(e => e.textContent.replace(/\s+/g, ' ').trim())[0] || '' }));
    ok(`${T} quiz: two-story house + garage, 3 packs ordered -> 5-pack plan (the brand guide's figure), 2 open, the 2-pack card is selected and marked`, res.total === '5 packs' && res.ordered === '3 packs' && res.gap === '2 packs' && cs.filter(c => c.sel).map(c => c.id).join() === 'home-plan-2' && cs.find(c => c.id === 'home-plan-2').rec, JSON.stringify(res));
    ok(`${T} the accept button carries the selected plan's price`, res.cta.includes(cs[1].price), res.cta);
    const no = await p.evaluate(() => { const a = document.querySelector('#gro-plan [data-next-upsell-action="add"]'), d = [...document.querySelectorAll('#gro-plan [data-next-upsell-action="skip"]')].find(e => e.offsetParent !== null);
      return d ? { text: d.textContent.trim(), gap: Math.round(d.getBoundingClientRect().top - a.getBoundingClientRect().bottom) } : null; });
    ok(`${T} the "No thanks" link is visible right under the accept button`, !!no && no.gap >= 0 && no.gap < 400 && /No thanks/.test(no.text), JSON.stringify(no));
    await p.click('[data-gq="r"] [data-gq-again]'); await p.click('[data-gq-name="an apartment or condo"]'); await p.click('[data-gq="2"] [data-gq-extra="0"]');
    await p.waitForFunction(() => { const c = document.querySelector('#gro-plan [data-next-bundle-id="home-plan-1"]'); return c && c.classList.contains('next-selected'); }, null, { timeout: 15000 }).catch(() => {});
    const enough = await p.evaluate(() => ({ line: document.querySelector('[data-gq-line]').textContent, gapHidden: document.querySelector('[data-gq-gapwrap]').hidden, sel: [...document.querySelectorAll('#gro-plan .next-bundle-tier-grid .next-selected')].map(e => e.getAttribute('data-next-bundle-id')).join(), rec: document.querySelectorAll('#gro-plan [data-gq-rec]').length }));
    ok(`${T} quiz: apartment with 3 packs ordered -> says the order already covers it and nothing more is needed; no card is marked as "sized for your home"`, /already covers this plan/.test(enough.line) && /don.t need more today/.test(enough.line) && /refills keep/.test(enough.line) && enough.gapHidden && enough.sel === 'home-plan-1' && enough.rec === 0, enough.line.slice(0, 110));
    const route = await p.evaluate(() => ({ accept: (document.querySelector('meta[name="next-upsell-accept-url"]') || {}).content || '', decline: (document.querySelector('meta[name="next-upsell-decline-url"]') || {}).content || '',
      offers: document.querySelectorAll('[data-next-upsell="offer"]').length, skip: document.querySelectorAll('[data-next-upsell-action="skip"], [data-upsell-proxy="skip"]').length }));
    ok(`${T} one SDK offer; yes -> thank-you, no -> the smaller offer`, route.offers === 1 && route.skip >= 1 && /mice-9-reasons(\/receipt|-thank-you)\//.test(route.accept) && /mice-9-reasons(\/downsell|-last-offer)\//.test(route.decline), route.accept + ' | ' + route.decline);
    const over = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
    ok(`${T} offer page: no sideways scroll`, !over);
    await p.screenshot({ path: `${out}/nine-offer-${vp.name}.png`, fullPage: false }).catch(() => {});

    // ---------- the smaller offer ----------
    await p.evaluate(() => sessionStorage.setItem('gro_plan_tier', '1'));
    await p.goto(url('downsell'), { waitUntil: 'load' });
    await p.waitForFunction(() => { const e = [...document.querySelectorAll('#gro-plan .next-bundle-tier-grid [data-next-bundle-display="price"]')]; return e.length === 2 && e.every(x => /\$\d/.test(x.textContent)); }, null, { timeout: 30000 }).catch(() => {});
    await p.waitForTimeout(1500);
    let ds = await cards();
    ok(`${T} smaller offer: 1 pack (selected) or the whole-home 5 packs, both priced by the campaign`, ds.map(c => c.id).join() === 'home-plan-last-1,home-plan-last-5' && ds.every(c => money(c.price)) && ds[0].sel && !ds[1].sel, ds.map(c => c.id + (c.sel ? '*' : '') + ' ' + c.price).join(' ; '));
    ok(`${T} the 5 packs cost less here than on the first offer`, num(ds[1].price) < num(cs[3].price), ds[1].price + ' < ' + cs[3].price);
    await p.evaluate(() => sessionStorage.setItem('gro_plan_tier', '5'));
    await p.reload({ waitUntil: 'load' });
    await p.waitForFunction(() => { const c = document.querySelector('#gro-plan [data-next-bundle-id="home-plan-last-5"]'); return c && c.classList.contains('next-selected'); }, null, { timeout: 30000 }).catch(() => {});
    ds = await cards();
    ok(`${T} when the quiz said whole home, the 5 packs are the default here`, ds[1].sel && !ds[0].sel, ds.map(c => c.id + (c.sel ? '*' : '')).join(' '));
    const r2 = await p.evaluate(() => ({ accept: (document.querySelector('meta[name="next-upsell-accept-url"]') || {}).content || '', decline: (document.querySelector('meta[name="next-upsell-decline-url"]') || {}).content || '', quiz: document.querySelectorAll('[data-gro-quiz]').length }));
    ok(`${T} smaller offer: no quiz; yes and no both -> thank-you`, r2.quiz === 0 && /mice-9-reasons(\/receipt|-thank-you)\//.test(r2.accept) && /mice-9-reasons(\/receipt|-thank-you)\//.test(r2.decline), r2.accept + ' | ' + r2.decline);

    ok(`${T} no requests to the source store`, external.length === 0, external.slice(0, 2).join(' '));
    ok(`${T} no page JS errors`, errs.length === 0, errs.slice(0, 2).join(' | '));
    await ctx.close();
  }
  await b.close();
  console.log(`\n${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
})();
