// Phone layout audit for every step of the Get Rid Of funnel (places no order).
//   node tools/funnel/getridof/mobile_audit.cjs [baseUrl] [outDir] [--store]
// For each page at 320 / 360 / 390 / 430 px wide it checks: no sideways scroll, nothing sticking out of the screen,
// no unreadably small text, no undersized buy / pay buttons, no broken visible image, no script error.
// --store uses the store routes (/mouse-pouches-checkout/ ...) instead of the local build routes.
const { chromium } = require('playwright');
const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const base = (args[0] || 'http://127.0.0.1:8765').replace(/\/$/, '');
const out = args[1] || 'campaigns/getridof/runs/mobile';
const store = process.argv.includes('--store');
const R = store
  ? { sales: '/mouse-pouches/', checkout: '/mouse-pouches-checkout/', up1: '/mouse-pouches-special-offer/', down1: '/mouse-pouches-exclusive-offer/', up2: '/mouse-pouches-special-offer-2/', down2: '/mouse-pouches-exclusive-offer-2/', receipt: '/mouse-pouches-thank-you/' }
  : { sales: '/mouse-pouches/', checkout: '/mouse-pouches/checkout/', up1: '/mouse-pouches/upsell/', down1: '/mouse-pouches/downsell/', up2: '/mouse-pouches/upsell-2/', down2: '/mouse-pouches/downsell-2/', receipt: '/mouse-pouches/receipt/' };
const PAGES = [
  ['sales', R.sales], ['checkout-3pack', R.checkout + '?forceBundleId=main:buy3'], ['checkout-onetime', R.checkout + '?forceBundleId=main:ot1'],
  ['offer-1', R.up1], ['offer-1-no', R.down1], ['offer-2', R.up2], ['offer-2-no', R.down2], ['receipt', R.receipt],
];
const WIDTHS = [320, 360, 390, 430];
let pass = 0, fail = 0;
const ok = (n, p, d = '') => { p ? pass++ : fail++; console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + d : '')); };

(async () => {
  const b = await chromium.launch();
  for (const [name, path] of PAGES) {
    for (const w of WIDTHS) {
      const ctx = await b.newContext({ viewport: { width: w, height: 760 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2,
        userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36' });
      const p = await ctx.newPage(); const errs = [];
      p.on('pageerror', e => errs.push(String(e.message).slice(0, 120)));
      await p.goto(base + path, { waitUntil: 'load', timeout: 60000 });
      await p.waitForTimeout(name === 'sales' ? 1200 : 4500);
      // scroll through so lazy images and scroll-in sections settle
      await p.evaluate(async () => { for (let y = 0; y < document.documentElement.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
      await p.waitForTimeout(900);
      const r = await p.evaluate(() => {
        const vw = innerWidth, seen = e => { const s = getComputedStyle(e); return s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
        const clipped = e => { for (let a = e.parentElement; a && a !== document.body; a = a.parentElement) { const s = getComputedStyle(a); if (/(auto|scroll|hidden|clip)/.test(s.overflowX)) return true; } return false; };
        const tag = e => (e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (typeof e.className === 'string' && e.className ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '')).slice(0, 60);
        const all = [...document.querySelectorAll('body *')].filter(e => e.offsetParent !== null || getComputedStyle(e).position === 'fixed');
        const wide = [], small = [], taps = [];
        for (const e of all) {
          const q = e.getBoundingClientRect(); if (!q.width || !q.height || !seen(e)) continue;
          if ((q.right > vw + 2 || q.left < -2) && !clipped(e) && getComputedStyle(e).position !== 'fixed') wide.push(tag(e) + ' ' + Math.round(q.left) + '..' + Math.round(q.right));
          const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2);
          if (own && parseFloat(getComputedStyle(e).fontSize) < 10 && !e.closest('svg')) small.push(tag(e) + ' ' + getComputedStyle(e).fontSize + ' "' + e.textContent.trim().slice(0, 24) + '"');
          if (e.matches('button, a[class*="btn"], a[data-gro-atc], [data-next-checkout] button, [data-next-action], .cta, [type="submit"]') && (q.height < 40 || q.width < 40) && !e.matches('[data-gro-gal], .gal__a, [data-gro-hc-x], [aria-label="Close"]')) taps.push(tag(e) + ' ' + Math.round(q.width) + 'x' + Math.round(q.height));
        }
        const broken = [...document.images].filter(i => i.offsetParent !== null && i.getBoundingClientRect().top < scrollY + innerHeight * 2 && i.complete && i.naturalWidth === 0 && i.getAttribute('src')).map(i => (i.getAttribute('src') || '').slice(-40));
        return { sw: document.documentElement.scrollWidth, vw, wide: [...new Set(wide)].slice(0, 5), small: [...new Set(small)].slice(0, 5), taps: [...new Set(taps)].slice(0, 6), broken: broken.slice(0, 4) };
      });
      const id = `[${name} @${w}]`;
      ok(`${id} no sideways scroll`, r.sw <= r.vw + 1, `page ${r.sw}px wide on a ${r.vw}px screen`);
      ok(`${id} nothing sticks out of the screen`, r.wide.length === 0, r.wide.join(' | '));
      ok(`${id} no text under 10px`, r.small.length === 0, r.small.join(' | '));
      ok(`${id} buttons are at least 40px`, r.taps.length === 0, r.taps.join(' | '));
      ok(`${id} no broken image`, r.broken.length === 0, r.broken.join(' '));
      ok(`${id} no script error`, errs.length === 0, errs.slice(0, 2).join(' | '));
      if (w === 390) await p.screenshot({ path: `${out}/${name}.png`, fullPage: true }).catch(() => {});
      await ctx.close();
    }
  }
  await b.close();
  console.log(`\n${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
})();
