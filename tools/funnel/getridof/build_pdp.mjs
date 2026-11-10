// Builds the Get Rid Of Mouse Pouches product page (campaigns/getridof/src/mouse-pouches/index.html) from the offline
// export of the reference PDP (exports/sofyre/offline/). Re-runnable: it always starts from the export.
//
//   node tools/funnel/getridof/build_pdp.mjs
//
// What it does, in a browser DOM (Playwright, network off), then as text:
//  - brand: every "SoFyre" in the copy, titles and alt text becomes "Get Rid Of"; the header/footer logo is the
//    store's own logo (cdn.cachebucket.com, copied locally); links to sofyre.com point at getridof.29next.store
//  - removes what only works on the source store: Shopify JSON-LD and meta, Shop Pay / dynamic checkout buttons,
//    cart drawer, search, social links, the newsletter form, hidden upsell popups, the Kaching app's config payload
//  - the bundle box (Buy 1 / Buy 2 Get 1 / Buy 3 Get 2 + "Save 30% with automatic refills") and every ADD TO CART
//    button become the funnel's: pdp.js sends the shopper to the checkout with the chosen bundle preselected
//    (?forceBundleId=), the one-time checkout or the Auto-Refill one
//  - the 5-pack price shows $74.95, the amount campaign 2362 charges (74.97 is not reachable with 5 equal units)
//  - assets: the export's 250 files are copied to src/mouse-pouches/assets/pdp/ and referenced as /mouse-pouches/pdp/
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const SRC = path.join(ROOT, 'exports/sofyre/offline');
const CAMP = path.join(ROOT, 'campaigns/getridof/src/mouse-pouches');
const OUT_ASSETS = path.join(CAMP, 'assets/pdp');
const STORE = 'https://getridof.29next.store';
const ASSET_URL = '/mouse-pouches/pdp/';

// 1. assets
fs.mkdirSync(OUT_ASSETS, { recursive: true });
for (const f of fs.readdirSync(path.join(SRC, 'assets'))) fs.copyFileSync(path.join(SRC, 'assets', f), path.join(OUT_ASSETS, f));
for (const [name, url] of [['gro-logo.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo.svg`],
                           ['gro-logo-white.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo-white.svg`]]) {
  const r = await fetch(url); if (!r.ok) throw new Error(`logo ${url}: ${r.status}`);
  fs.writeFileSync(path.join(OUT_ASSETS, name), Buffer.from(await r.arrayBuffer()));
}
fs.copyFileSync(path.join(ROOT, 'tools/funnel/getridof/pdp.js'), path.join(OUT_ASSETS, 'pdp.js'));
fs.copyFileSync(path.join(ROOT, 'tools/funnel/getridof/pdp.css'), path.join(OUT_ASSETS, 'pdp.css'));

// favicon + touch icon for the checkout/receipt layout (the starter shipped NEXT's): the store logo on white, square
{
  const svg = fs.readFileSync(path.join(OUT_ASSETS, 'gro-logo.svg'), 'utf8');
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 180, height: 180 } });
  await pg.setContent(`<html><body style="margin:0;width:180px;height:180px;display:flex;align-items:center;justify-content:center;background:#fff"><div style="width:164px">${svg.replace('<svg', '<svg style="width:100%;height:auto;display:block"')}</div></body></html>`);
  for (const f of ['favicon.png', 'webclip.png']) await pg.screenshot({ path: path.join(CAMP, 'assets/images', f) });
  await b.close();
}

// 2. DOM pass
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
await page.goto('file://' + path.join(SRC, 'index.html'), { waitUntil: 'load' });
const report = await page.evaluate(({ STORE }) => {
  const n = {}; const count = (k, v = 1) => (n[k] = (n[k] || 0) + v);
  const rm = (sel, k) => document.querySelectorAll(sel).forEach(e => { e.remove(); count(k || sel); });

  // head: Shopify/social metadata of the source store
  rm('script[type="application/ld+json"]', 'json-ld');
  rm('link[rel~="icon"], link[rel="apple-touch-icon"], link[href*="sofyre"], link[rel="buy"], link[rel="canonical"], link[rel="alternate"], meta[name="google-site-verification"], meta#shopify-digital-wallet, meta[name="shopify-checkout-api-token"], meta[name="shopify-digital-wallet"]', 'head-meta');
  document.title = 'Rodent Repellent Pouches – Get Rid Of';
  document.querySelectorAll('meta[property^="og:"], meta[name^="twitter:"]').forEach(m => {
    const p = m.getAttribute('property') || m.getAttribute('name');
    if (/(:url|og:site_name)$/.test(p)) m.setAttribute('content', p.endsWith('site_name') ? 'Get Rid Of' : STORE);
    if (/image/.test(p)) m.remove();
  });

  // source-store-only widgets
  rm('shopify-accelerated-checkout, shopify-accelerated-checkout-cart, shop-pay-wallet-button, more-payment-options-link, .shopify-payment-button, shop-cart-sync', 'shop-pay');
  rm('cart-drawer, cart-drawer-upsell, cart-drawer-items, #CartDrawer, .cart-drawer, #shopify-section-cart-drawer', 'cart-drawer');
  rm('details-modal.header__search, predictive-search, .header__icon--cart, a[href$="/cart"].header__icon', 'search-cart');
  rm('template', 'template');
  rm('.list-social, .footer__list-social, .footer-block--newsletter, .footer__newsletter, form[action*="/contact"]', 'social-newsletter');
  // hidden "add another bag" upsell popup and similar modal shells
  document.querySelectorAll('.popup-subtitle').forEach(p => { const box = p.closest('[class*="popup"]:not(body)'); if (box) { (box.parentElement.closest('[class*="popup"]') || box).remove(); count('upsell-popup'); } });

  // Kaching: drop the app payload (store token, product JSON), keep the rendered markup
  document.querySelectorAll('kaching-bundles-block').forEach(k => { for (const a of [...k.attributes]) if (a.value.length > 100) k.removeAttribute(a.name); count('kaching-attrs'); });

  // brand in text, alt/title/content attributes
  const swap = s => s.replace(/SOFYRE/g, 'GET RID OF').replace(/sofyre/gi, 'Get Rid Of');
  const tw = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT);
  for (let t; (t = tw.nextNode());) {
    const pe = t.parentElement; if (!pe || ['SCRIPT'].includes(pe.tagName)) continue;
    if (pe.tagName === 'STYLE') { if (/sofyre/i.test(t.data)) t.data = t.data.replace(/sofyre-/gi, 'gro-'); continue; }
    if (/sofyre/i.test(t.data)) { t.data = swap(t.data); count('text-brand'); }
  }
  document.querySelectorAll('[alt],[title],[aria-label],meta[content]').forEach(e => ['alt', 'title', 'aria-label', 'content'].forEach(a => {
    const v = e.getAttribute(a); if (v && /sofyre/i.test(v) && !/^https?:|^\/\//.test(v)) { e.setAttribute(a, swap(v)); count('attr-brand'); }
  }));
  document.querySelectorAll('[data-sofyre-managed]').forEach(e => e.removeAttribute('data-sofyre-managed'));

  // logos
  document.querySelectorAll('img.header__heading-logo, .footer img[class*="logo"], img[class*="logo"]').forEach(img => {
    const white = !!img.closest('footer, .footer'); img.setAttribute('src', 'assets/' + (white ? 'gro-logo-white.svg' : 'gro-logo.svg'));
    img.setAttribute('alt', 'Get Rid Of'); img.removeAttribute('srcset'); img.setAttribute('width', '200'); img.setAttribute('height', '31'); count('logo');
  });

  // wordmark images (file name SoFyre_*): the store's logo, sized to the box the wordmark had
  document.querySelectorAll('img[src*="SoFyre_"], img[srcset*="SoFyre_"], img[src*="Screenshot_2025-07-23_at_33736_PM"], img[srcset*="Screenshot_2025-07-23_at_33736_PM"]').forEach(img => {
    img.setAttribute('src', 'assets/gro-logo.svg'); img.removeAttribute('srcset'); img.setAttribute('alt', 'Get Rid Of');
    img.style.objectFit = 'contain'; count('wordmark-img');
  });

  // links: source store -> this store
  const map = [[/policies\/contact-information|\/pages\/contact/, '/contact/'], [/policies\/privacy-policy/, '/privacy/'], [/policies\/refund-policy/, '/refund-policy/'],
               [/policies\/terms-of-service/, '/terms/'], [/policies\/subscription-policy/, '/auto-refill-terms/'], [/policies\/shipping-policy/, '/shipping-policy/'],
               [/apps\/parcelpanel|track/i, '/contact/'], [/account|subscriptions|refill/i, '/accounts/subscriptions/'], [/cookie/i, '/cookie-policy/']];
  document.querySelectorAll('a[href]').forEach(a => {
    const h = a.getAttribute('href');
    if (/mouse-repellent-pouches(?!-\d)/.test(h)) { a.setAttribute('href', '#gro-buy'); count('link-self'); return; }
    if (/^https?:\/\/(www\.)?sofyre\.com|^\/(?!\/)/.test(h) || /^\/$/.test(h)) {
      const m = map.find(([re]) => re.test(h)); a.setAttribute('href', STORE + (m ? m[1] : '/')); count('link-store');
    } else if (/facebook\.com|instagram\.com|tiktok\.com/.test(h)) { a.remove(); count('link-social'); }
  });
  // footer FYI "Search" link: the funnel has no search
  document.querySelectorAll('footer a, .footer a').forEach(a => { if (a.textContent.trim() === 'Search') { (a.closest('li') || a).remove(); count('footer-search'); } });
  // form posts to the source store
  document.querySelectorAll('form[action]').forEach(f => { if (/sofyre|^\//.test(f.getAttribute('action'))) { f.removeAttribute('action'); f.setAttribute('onsubmit', 'return false'); count('form-inert'); } });

  // bundle box hooks
  const bars = [...document.querySelectorAll('.kaching-bundles__bar[data-deal-bar-id]')];
  const ids = ['buy1', 'buy3', 'buy5'];
  bars.forEach((bar, i) => { bar.setAttribute('data-gro-bundle', ids[i]); count('bundle-bar'); });
  const p5 = bars[2] && bars[2].querySelector('.kaching-bundles__bar-price .money');
  if (p5 && p5.textContent.trim() === '$74.97') { p5.textContent = '$74.95'; count('price-74.95'); }
  const sub = document.querySelector('.kaching-bundles__subscriptions [role="checkbox"]');
  if (sub) { sub.setAttribute('data-gro-refill', ''); count('refill-toggle'); }
  const box = document.querySelector('kaching-bundles-block'); if (box) box.id = 'gro-buy';

  // every ADD TO CART / add-to-cart style button
  const isAtc = el => /add\s*to\s*cart/i.test(el.textContent || '');
  document.querySelectorAll('button, a, gp-button, gp-product-button, [role="button"]').forEach(el => {
    if (!isAtc(el)) return;
    if (el.querySelector('button, a') && el.tagName.startsWith('GP-')) return; // the inner control gets it
    el.setAttribute('data-gro-atc', ''); if (el.tagName === 'A') el.setAttribute('href', '#gro-buy');
    el.removeAttribute('disabled'); if (el.tagName === 'BUTTON') el.setAttribute('type', 'button'); count('atc');
  });
  document.querySelectorAll('gp-product-button, gp-button').forEach(g => { g.removeAttribute('gp-href'); });
  document.querySelectorAll('product-form form').forEach(f => { f.removeAttribute('action'); f.setAttribute('onsubmit', 'return false'); });

  // countdown hook
  document.querySelectorAll('gp-countdown-timer').forEach(t => { t.setAttribute('data-gro-countdown', ''); count('countdown'); });
  return n;
}, { STORE });

let html = await page.evaluate(() => '<!doctype html>\n' + document.documentElement.outerHTML);
await browser.close();

// 3. text pass: asset paths, leftovers
html = html.replace(/(["'(])assets\//g, `$1${ASSET_URL}`);
html = html.replace(/(https?:)?\/\/sofyre\.com\/cdn\/[^"' )]+/g, '');      // stray CDN refs (badge template etc.)
html = html.replace('</head>', `<link rel="stylesheet" href="${ASSET_URL}pdp.css">\n<link rel="icon" href="${ASSET_URL}gro-logo.svg">\n</head>`);
html = html.replace('</body>', `<script src="${ASSET_URL}pdp.js" defer></script>\n</body>`);
html = html.replace(/<!-- Offline snapshot[^>]*-->/, '');
const left = (html.match(/sofyre/gi) || []).length;

// 4. page with front matter; the body is raw HTML (no Liquid inside)
const front = `---\npage_layout: pdp.html\ntitle: "Rodent Repellent Pouches – Get Rid Of"\npage_type: product\n# Generated by tools/funnel/getridof/build_pdp.mjs from exports/sofyre/offline/ — edit the builder, not this file.\n---\n`;
fs.writeFileSync(path.join(CAMP, 'index.html'), front + '{% raw %}' + html + '{% endraw %}\n');
fs.mkdirSync(path.join(CAMP, '_layouts'), { recursive: true });
fs.writeFileSync(path.join(CAMP, '_layouts/pdp.html'), '{{ content }}\n');
console.log(JSON.stringify(report), '\nleft "sofyre" mentions (URLs/ids only):', left, '\nwrote', path.join(CAMP, 'index.html'), (html.length / 1e6).toFixed(2) + ' MB');
