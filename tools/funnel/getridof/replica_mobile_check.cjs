// Phone test of the replica product page (/mouse-repellent-pouches/) on three phone sizes. Places no order.
//   node tools/funnel/getridof/replica_mobile_check.cjs [baseUrl]      (default http://localhost:8765; or https://getridof.shop)
// Every accordion item, the menu, swiping the photo, the review cards, the countdown, the sticky header, every ADD TO CART
// button (tappable and reaching the checkout) and the footer / header links.
const { chromium, devices } = require('playwright');
const base = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
let pass = 0, fail = 0; const ok = (n, p, d = '') => { p ? pass++ : fail++; console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };
(async () => { const b = await chromium.launch();
  for (const dev of ['iPhone 13', 'Pixel 7', 'iPhone SE']) { const ctx = await b.newContext({ ...devices[dev] }); const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    const url = `${base}/mouse-repellent-pouches/`;
    await p.goto(url, { waitUntil: 'load' }); await p.waitForTimeout(700);
    // accordions: every item opens and shows its text
    const acc = await p.evaluate(async () => { const out = []; for (const it of document.querySelectorAll('gp-accordion .gp-accordion-item')) { const h = it.querySelector('.gp-accordion-item_header'), bd = it.querySelector('.gp-accordion-item_body'); if (!h || !bd || h.getBoundingClientRect().height === 0) continue;
        h.click(); await new Promise(r => setTimeout(r, 60)); const r = bd.getBoundingClientRect(); const txt = bd.innerText.replace(/\s+/g, ' ').trim(); out.push((r.height > 20 && txt.length > 20 && getComputedStyle(bd).visibility !== 'hidden' ? '' : '!') + h.textContent.trim().slice(0, 22)); } return out; });
    ok(`[${dev}] every accordion item opens with its text (${acc.length})`, acc.length >= 12 && acc.every(x => x[0] !== '!'), acc.filter(x => x[0] === '!').join(', '));
    // menu
    await p.evaluate(() => scrollTo(0, 0)); await p.locator('.mobile-menu__hamburger').first().click(); await p.waitForTimeout(400);
    const m1 = await p.evaluate(() => { const m = document.querySelector('.header-mobile-menu'); const r = m.getBoundingClientRect(); const a = m.querySelector('a.header-items__link'); const c = getComputedStyle(m); return { open: r.height > 100 && c.display !== 'none' && c.visibility !== 'hidden' && r.top < innerHeight && r.left < innerWidth && r.right > 0, link: a ? a.getAttribute('href') : null, contact: [...m.querySelectorAll('a')].map(x => x.textContent.trim() + '>' + x.getAttribute('href')).filter(x => /Contact/.test(x)).join() }; });
    await p.locator('.mobile-menu__hamburger').first().click(); await p.waitForTimeout(400);
    const m2 = await p.evaluate(() => { const m = document.querySelector('.header-mobile-menu'); const r = m.getBoundingClientRect(); const c = getComputedStyle(m); return !(r.height > 100 && c.display !== 'none' && c.visibility !== 'hidden' && r.top < innerHeight && r.left < innerWidth && r.right > 0 && +c.opacity > 0); });
    ok(`[${dev}] menu opens, lists this product and Contact Us, closes again`, m1.open && m2 && !!m1.link && /getridof\.shop\/contact/.test(m1.contact), JSON.stringify(m1) + ' closed=' + m2);
    // swipe the gallery
    const st = await p.locator('.gro-stage').boundingBox();
    await p.evaluate(({ x, y }) => { const el = document.querySelector('gp-carousel-v3.gp-feature-image-carousel'); const t = (type, cx) => { const touch = new Touch({ identifier: 1, target: el, clientX: cx, clientY: y }); el.dispatchEvent(new TouchEvent(type, { bubbles: true, cancelable: true, touches: type === 'touchend' ? [] : [touch], changedTouches: [touch] })); }; t('touchstart', x + 250); t('touchend', x + 60); }, { x: st.x, y: st.y + st.height / 2 });
    await p.waitForTimeout(700);
    const sw = await p.evaluate(() => ({ active: [...document.querySelectorAll('.gro-thumb')].map(t => t.classList.contains('gro-thumb-active') ? 1 : 0).join(''), loaded: document.querySelectorAll('.gro-stage img:not(.seasonal-badge)')[1].naturalWidth > 100 }));
    ok(`[${dev}] swiping the photo moves to the next one (and it loads)`, sw.active === '0100000' && sw.loaded, JSON.stringify(sw));
    // review cards scroll sideways; countdown ticks; sticky header
    const misc = await p.evaluate(async () => { const car = [...document.querySelectorAll('gp-carousel-v3.gro-carousel .gro-scroller')].filter(e => e.getBoundingClientRect().width > 0); const sc = car.filter(e => e.scrollWidth > e.clientWidth + 20).length;
      const nums = () => [...document.querySelectorAll('[data-gro-countdown] .gp-countdown-number')].map(n => n.textContent).join(':'); const a = nums(); await new Promise(r => setTimeout(r, 1300)); const bb = nums();
      scrollTo(0, 3000); await new Promise(r => setTimeout(r, 300)); const hd = document.querySelector('sticky-header, .header-wrapper').getBoundingClientRect();
      return { carousels: car.length, scrollable: sc, countdown: a + ' -> ' + bb, ticking: a !== bb && /^\d\d:\d\d:\d\d$/.test(bb), sticky: hd.top >= -1 && hd.top < 60 && hd.height > 30, overflow: document.documentElement.scrollWidth - innerWidth }; });
    ok(`[${dev}] review cards scroll sideways, countdown ticks, header stays on top, no sideways page scroll`, misc.carousels >= 1 && misc.scrollable >= 1 && misc.ticking && misc.sticky && misc.overflow <= 1, JSON.stringify(misc));
    // every ADD TO CART button reaches the checkout with the selected bundle
    const n = await p.evaluate(() => [...document.querySelectorAll('[data-gro-atc]')].filter(e => e.getBoundingClientRect().height > 0).length);
    const bad = [];
    for (let i = 0; i < n; i++) { await p.goto(url, { waitUntil: 'load' }); await p.waitForTimeout(300);
      const hit = await p.evaluate(i => { const e = [...document.querySelectorAll('[data-gro-atc]')].filter(x => x.getBoundingClientRect().height > 0)[i]; e.scrollIntoView({ block: 'center', behavior: 'instant' }); const r = e.getBoundingClientRect(); const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return { tappable: !!top && (top === e || e.contains(top) || top.contains(e)), h: Math.round(r.height) }; }, i);
      const nav = p.waitForURL(/checkout/, { timeout: 8000 }).then(() => true).catch(() => false);
      await p.evaluate(i => { [...document.querySelectorAll('[data-gro-atc]')].filter(x => x.getBoundingClientRect().height > 0)[i].click(); }, i);
      if (!(await nav) || !/forceBundleId=main%3Abuy3/.test(p.url()) || !hit.tappable || hit.h < 40) bad.push(i + ':' + JSON.stringify(hit) + ' ' + p.url().slice(-50)); }
    ok(`[${dev}] all ${n} ADD TO CART buttons are tappable (40px+) and open the checkout`, n >= 6 && bad.length === 0, bad.join(' | '));
    ok(`[${dev}] no JS errors`, errs.length === 0, errs.slice(0, 2).join(' | '));
    await ctx.close(); }
  // footer and header links answer
  const ctx = await b.newContext(); const p = await ctx.newPage(); await p.goto(`${base}/mouse-repellent-pouches/`, { waitUntil: 'load' });
  const links = await p.evaluate(() => [...new Set([...document.querySelectorAll('footer a[href], a.header__icons-btn, .header-mobile-menu a[href]')].map(a => a.href).filter(h => /^https?:/.test(h)))]);
  const res = []; for (const l of links) { const r = await ctx.request.get(l, { maxRedirects: 5 }).catch(() => null); res.push((r && r.status() < 400 ? '' : '!') + l.replace(/^https?:\/\/[^/]+/, '') + ':' + (r ? r.status() : 'x')); }
  ok(`footer / header links answer (${links.length})`, res.every(x => x[0] !== '!'), res.join(' '));
  await b.close(); console.log(`\n${pass}/${pass + fail} passed`); })();
