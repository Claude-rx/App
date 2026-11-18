// Builds the replica funnel's product page, /mouse-repellent-pouches/ (campaign 2721): the brand's proven product page
// (offline export in exports/sofyre/offline/) rebuilt as Get Rid Of, section for section, in the source order.
// Run through build_replica.py, which first copies the checkout / offer / thank-you pages into the funnel folder.
//
//   node tools/funnel/getridof/replica/build_replica.mjs
//
// What it does, in a browser DOM (Playwright, network off), then as text:
//  - brand: every "SoFyre" in the copy, titles and alt text becomes "Get Rid Of"; the header/footer logo is the
//    store's own logo; links to sofyre.com point at getridof.shop; packaging photos are swapped for the Get Rid Of
//    packaging (swap_images.py)
//  - removes what only works on the source store: Shopify JSON-LD and meta, Shop Pay / dynamic checkout buttons,
//    cart drawer, search, social links, the newsletter form, hidden upsell popups, the Kaching app's config payload
//  - the bundle box (Buy 1 / Buy 2 Get 1 Free / Buy 3 Get 2 Free + Automatic Refills) and every ADD TO CART button
//    become the funnel's: pdp.js shows campaign 2721's prices and sends the shopper to the checkout with the chosen
//    bundle preselected (?forceBundleId=main:buy1|buy3|buy5 with refills, ot1|ot3|ot5 without)
//  - what differs from the source, and nothing else: the brand name and logo, the product photos (Get Rid Of
//    packaging), this campaign's prices in the bundle box, and the 90-day guarantee. The owner asked for an exact
//    copy: no copy edits, no added sections, the source's colours, header button and press band as they are.
//    One later request: a fuller footer (replica/footer.html) with every policy and the shop / help links.
//  - what cannot be copied because it only works on the source store: the Shop Pay button, cart, search, the
//    newsletter form, social links, the discount pop-up, and the menu's links to that store's other products.
//  - the bundle box is the "offer ladder" version the source store shows part of its visitors (12 / 36 / 60 Pouches,
//    % OFF pill, Save $, price per pouch); its markup and stylesheet were captured to exports/sofyre/live-bundle-box/.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../../..');
const SLUG = 'mouse-repellent-pouches';
const SRC = path.join(ROOT, 'exports/sofyre/live-desktop');   // the source page as captured on 15 Nov 2026 (exports/sofyre/tools/full.js)
const CAMP = path.join(ROOT, 'campaigns/getridof/src', SLUG);
const OUT_ASSETS = path.join(CAMP, 'assets/pdp');
const STORE = 'https://getridof.shop';   // every visible link goes to the main domain
const ASSET_URL = `/${SLUG}/pdp/`;

// 1. assets
fs.mkdirSync(OUT_ASSETS, { recursive: true });
// The funnel folder arrives with src/mouse-pouches/assets/pdp (build_replica.py): the same files with the Get Rid Of
// packaging and the 90-day guarantee already in the images. Only what is missing there is taken from the export.
let fresh = 0;
const RASTER = /\.(png|jpe?g|webp|gif|avif)$/i;   // stylesheets, fonts and vector files are always the capture's own (source colours)
for (const f of fs.readdirSync(path.join(SRC, 'assets'))) if (!/sofyre/i.test(f) && (!RASTER.test(f) || !fs.existsSync(path.join(OUT_ASSETS, f)))) { fs.copyFileSync(path.join(SRC, 'assets', f), path.join(OUT_ASSETS, f)); fresh++; }
fs.copyFileSync(path.join(ROOT, 'exports/sofyre/live-bundle-box/experiment.css'), path.join(OUT_ASSETS, 'offer-ladder.css'));
// the header menu's bag icon: a plain icon whose file name carries the old brand, copied under a neutral name
fs.copyFileSync(path.join(SRC, 'assets/Sofyre_Rodent_Repellent-e5561d.svg'), path.join(OUT_ASSETS, 'gro-menu-icon.svg'));
const freshImages = fs.readdirSync(path.join(SRC, 'assets')).filter(f => /\.(png|jpe?g|webp|gif|avif)$/i.test(f) && !/sofyre/i.test(f) && !fs.existsSync(path.join(ROOT, 'campaigns/getridof/src/mouse-pouches/assets/pdp', f)));
if (freshImages.length) throw new Error('images that never went through the brand swap: ' + freshImages.join(', '));
for (const [name, url] of [['gro-logo.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo.svg`],
                           ['gro-logo-white.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo-white.svg`]]) {
  const r = await fetch(url); if (!r.ok) throw new Error(`logo ${url}: ${r.status}`);
  fs.writeFileSync(path.join(OUT_ASSETS, name), Buffer.from(await r.arrayBuffer()));
}
const PRICES = JSON.parse(fs.readFileSync(path.join(HERE, 'prices.json'), 'utf8'));   // what the bundle box shows
fs.copyFileSync(path.join(HERE, 'pdp.css'), path.join(OUT_ASSETS, 'pdp.css'));

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
// the offer ladder's lines, from prices.json: % off, the saving and the price per pouch against the regular price
const money = v => '$' + v.toFixed(2);
const ladderSide = (price, full, packs) => ({ price: money(price), off: Math.round((1 - price / full) * 100) + '% OFF', save: 'Save ' + money(full - price), each: money(price / (12 * packs)) + ' Each Pouch' });
const LADDER = Object.fromEntries(Object.entries(PRICES).map(([id, r]) => { const n = Number(id.slice(3)), full = Number(r.full.slice(1));
  return [id, { title: `${12 * n} Pouches`, pack: `(${n} Pack${n > 1 ? 's' : ''})`, full: money(full), sub: ladderSide(Number(r.sub[0].slice(1)), full, n), one: ladderSide(Number(r.one[0].slice(1)), full, n),
    badge: n === 3 ? ['best', 'BEST SELLER'] : n === 5 ? ['lowest', 'LOWEST PRICE EVER'] : null }]; }));
fs.writeFileSync(path.join(OUT_ASSETS, 'pdp.js'), fs.readFileSync(path.join(HERE, 'pdp.js'), 'utf8').replaceAll('@@SLUG@@', SLUG).replace('@@PRICES@@', JSON.stringify(PRICES)).replace('@@LADDER@@', () => JSON.stringify(LADDER)));
const FOOTER = fs.readFileSync(path.join(HERE, 'footer.html'), 'utf8').replace(/<!--[\s\S]*?-->/, '').replaceAll('@@SLUG_ROOT@@', `/${SLUG}/`).trim();
const COST_DAY = '$0.25';   // "Cost per day of protection": one pack with Automatic Refills, $22.49 over its 90 days
const report = await page.evaluate(({ STORE, COST_DAY, SLUG, PRICES, LADDER, FOOTER }) => {
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
  // the newsletter block (heading, line and form) and the social links: they belong to the source store
  document.querySelectorAll('.footer-block').forEach(b => { if (b.querySelector('form.footer__newsletter, form.newsletter-form')) { b.parentNode.removeChild(b); count('newsletter-block'); } });
  rm('.list-social, .footer__list-social, .footer-block--newsletter, .footer__newsletter, form[action*="/contact"]', 'social-newsletter');
  // hidden "add another bag" upsell popup and similar modal shells
  document.querySelectorAll('.popup-subtitle').forEach(p => { const box = p.closest('[class*="popup"]:not(body)'); if (box) { (box.parentElement.closest('[class*="popup"]') || box).remove(); count('upsell-popup'); } });

  // Kaching: drop the app payload (store token, product JSON), keep the rendered markup
  document.querySelectorAll('kaching-bundles-block').forEach(k => { for (const a of [...k.attributes]) if (a.value.length > 100) k.removeAttribute(a.name); count('kaching-attrs'); });

  // brand in text, alt/title/content attributes
  const swap = s => s.replace(/SOFYRE/g, 'GET RID OF').replace(/sofyre/gi, 'Get Rid Of');
  const tw = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT);
  const later = [];   // edits that replace nodes wait until the walk is over
  for (let t; (t = tw.nextNode());) {
    const pe = t.parentElement; if (!pe || ['SCRIPT'].includes(pe.tagName)) continue;
    if (pe.tagName === 'STYLE') { if (/sofyre/i.test(t.data)) t.data = t.data.replace(/sofyre-/gi, 'gro-'); continue; }
    if (/sofyre/i.test(t.data)) { t.data = swap(t.data); count('text-brand'); }
    if (/30[\s-]?days?\b/i.test(t.data) && /money|guarantee|refund|leave within/i.test(pe.closest('section, div, li, p').textContent)) { t.data = t.data.replace(/30([\s-]?days?\b)/gi, '90$1'); count('guarantee-90'); }
    if (t.data.trim() === '$0.33') { t.data = t.data.replace('$0.33', COST_DAY); count('cost-per-day'); }
  }
  later.forEach(f => f());
  document.querySelectorAll('[alt],[title],[aria-label],meta[content]').forEach(e => ['alt', 'title', 'aria-label', 'content'].forEach(a => {
    const v = e.getAttribute(a); if (v && /sofyre/i.test(v) && !/^https?:|^\/\//.test(v)) { e.setAttribute(a, swap(v)); count('attr-brand'); }
  }));
  document.querySelectorAll('[data-sofyre-managed]').forEach(e => e.removeAttribute('data-sofyre-managed'));

  // logos. The source header's wordmark is text; here it is the brand's logo.
  document.querySelectorAll('a.header__heading-link').forEach(a => { if (a.querySelector('img')) return;
    a.innerHTML = '<img src="assets/gro-logo.svg" alt="Get Rid Of" width="200" height="31" class="header__heading-logo gro-logo">'; count('logo-text'); });
  document.querySelectorAll('img[src*="Sofyre_Rodent_Repellent-"]').forEach(img => { img.setAttribute('src', 'assets/gro-menu-icon.svg'); count('menu-icon'); });
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

  // scroll locks frozen in by popups open at capture time (Klaviyo's form left klaviyo-prevent-body-scrolling on body)
  [document.documentElement, document.body].forEach(el => {
    [...el.classList].filter(c => /prevent-body-scroll|no-scroll|overflow-hidden|modal-open|scroll-lock|lock-scroll|menu-open|drawer-open/i.test(c)).forEach(c => { el.classList.remove(c); count('scroll-lock'); });
    el.style.removeProperty('overflow'); el.style.removeProperty('position');
  });

  // bundle box hooks
  const bars = [...document.querySelectorAll('.kaching-bundles__bar[data-deal-bar-id]')];
  const ids = ['buy1', 'buy3', 'buy5'];
  bars.forEach((bar, i) => { bar.setAttribute('data-gro-bundle', ids[i]); count('bundle-bar'); });
  const sub = document.querySelector('.kaching-bundles__subscriptions [role="checkbox"]');
  if (sub) { sub.setAttribute('data-gro-refill', ''); count('refill-toggle'); }
  const box = document.querySelector('kaching-bundles-block'); if (box) box.id = 'gro-buy';
  // the state the page opens in is written into the HTML, so the first paint needs no script: this campaign's
  // prices with Automatic Refills ticked and the 36-pouch bundle selected
  if (sub) sub.setAttribute('aria-checked', 'true');
  bars.forEach((bar, i) => {
    const p = PRICES[ids[i]], set = (sel, v) => { const e = bar.querySelector(sel); if (!e) throw new Error('bundle bar: ' + sel + ' not found'); e.textContent = v; };
    set('.kaching-bundles__bar-price .money', p.sub[0]); set('.kaching-bundles__bar-full-price .money', p.full); set('.kaching-bundles__bar-subtitle', p.sub[1]);
    bar.classList.toggle('kaching-bundles__bar--selected', ids[i] === 'buy3'); count('bundle-price');
  });
  // the "offer ladder" layer, exactly as the source store's experiment script builds it (exports/sofyre/live-bundle-box)
  document.documentElement.classList.add('exp-pdp-offer-ladder-treatment');
  const barsBox = box && box.querySelector('.kaching-bundles__bars');
  if (!barsBox) throw new Error('bundle bars not found');
  const urgency = document.createElement('p'); urgency.className = 'exp-ol-urgency';
  urgency.innerHTML = '<span class="exp-ol-urgency__icon" aria-hidden="true">🔥</span> <strong class="">High Demand</strong> — Selling Fast Due To Rodent Season';
  barsBox.parentNode.insertBefore(urgency, barsBox);
  bars.forEach((bar, i) => {
    const row = LADDER[ids[i]], main = bar.querySelector('.kaching-bundles__bar-main'), label = bar.querySelector('label.kaching-bundles__bar-container');
    if (!main || !label) throw new Error('bundle bar: main / label not found');
    const card = document.createElement('div'); card.className = 'exp-ol-card';
    card.innerHTML = `<div class="exp-ol-left"><div class="exp-ol-title-row"><span class="exp-ol-title">${row.title}</span><span class="exp-ol-pill">${row.sub.off}</span></div><span class="exp-ol-pack">${row.pack}</span><span class="exp-ol-save">${row.sub.save}</span></div>` +
      `<div class="exp-ol-right"><span class="exp-ol-price">${row.sub.price}</span><s class="exp-ol-compare">${row.full}</s><span class="exp-ol-each">${row.sub.each}</span></div>`;
    main.appendChild(card);
    if (row.badge) { const b = document.createElement('span'); b.className = 'exp-ol-badge exp-ol-badge--' + row.badge[0]; b.innerHTML = '<span class="exp-ol-badge__icon" aria-hidden="true">🔥</span> ' + row.badge[1]; label.appendChild(b); }
    count('ladder-card');
  });
  // the gallery stage gets a hook for its sizing rule (pdp.css)
  const track = document.querySelector('gp-carousel-v3.gp-feature-image-carousel .gem-slider-wrapper');
  if (!track) throw new Error('gallery track not found'); track.parentElement.classList.add('gro-stage');
  // the snapshot's frozen desktop sizes (inline, some !important) would beat that rule: they go
  [track, ...track.children].forEach(e => ['width', 'min-width', 'max-width', 'height', 'transform'].forEach(k => e.style.removeProperty(k)));

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

  const main = document.querySelector('#MainContent');

  // header menu: the source store's other products are not sold here; the menu keeps this product and Contact Us
  document.querySelectorAll('.header-mobile-menu__items a.header-items__link').forEach(a => {
    if (/Rodent Repellent Pouches/i.test(a.textContent)) return;
    const par = a.parentElement; a.remove(); if (par && !par.children.length) par.remove(); count('menu-other-product');
  });

  // first-screen weight. The gallery's photos come from the funnel's optimised set (lp/hero-N.webp, made by
  // build_lp.py from the same files); only the first loads with the page (build_replica.py then embeds it in the
  // HTML). Photos 2-7 and the thumbnails are fetched once the page has loaded or on the first touch (pdp.js).
  const PX = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
  const defer = (img, src) => { img.setAttribute('data-gro-src', src); img.setAttribute('src', PX); img.removeAttribute('srcset'); img.removeAttribute('fetchpriority'); img.removeAttribute('loading'); count('img-deferred'); };
  const slides = [...document.querySelectorAll('gp-carousel-v3.gp-feature-image-carousel img:not(.seasonal-badge)')];
  if (slides.length !== 7) throw new Error('gallery: expected 7 photos, found ' + slides.length);
  slides.forEach((img, i) => {
    const src = `/${SLUG}/lp/hero-${i + 1}.webp`;
    if (i) return defer(img, src);
    img.setAttribute('src', src); img.removeAttribute('srcset'); img.setAttribute('fetchpriority', 'high'); img.setAttribute('data-gro-hero', ''); count('hero');
  });
  // miniatures under the main photo: the source shows them in a slider its own script drives (frozen in the capture).
  // A plain row of buttons takes that slider's place, five to a row as on the source: small files made by
  // build_replica.py, the first one marked as current; pdp.js moves the gallery when one is tapped.
  const oldThumbs = [...document.querySelectorAll('.gallery-wrapper.gp-product-images-gallery')].find(e => e.querySelector('gp-carousel-v3.carousel-gallery'));
  if (!oldThumbs) throw new Error('thumbnail slider not found');
  const row = document.createElement('div'); row.className = 'gro-thumbs'; row.setAttribute('role', 'group'); row.setAttribute('aria-label', 'Product photos');
  row.innerHTML = slides.map((_, i) => `<button type="button" class="gro-thumb${i ? '' : ' gro-thumb-active'}" aria-label="Photo ${i + 1} of ${slides.length}"><img src="/${SLUG}/pdp/gro-thumb-${i + 1}.webp" alt="" width="128" height="128" decoding="async"></button>`).join('');
  oldThumbs.parentNode.insertBefore(row, oldThumbs); oldThumbs.parentNode.removeChild(oldThumbs); count('thumbs', slides.length);
  // the header menu's two pictures: small files, fetched when the menu is opened
  document.querySelectorAll('.header-mobile-menu img').forEach(img => {
    const s = img.getAttribute('src') || '';
    if (/P_1_1-/.test(s)) img.setAttribute('src', `/${SLUG}/lp/thumb.webp`); else if (/Buy_3-/.test(s)) img.setAttribute('src', `/${SLUG}/pdp/gro-menu-banner.webp`); else return;
    img.setAttribute('loading', 'lazy'); img.setAttribute('decoding', 'async'); count('menu-img');
  });

  // moving photo strips: a strip that was hidden when the page was captured has no pace (0s = it never moves);
  // give every strip a phone-sized default, which pdp.js then sets from the real width
  document.querySelectorAll('gp-marquee .rfm-marquee').forEach(m => { m.style.setProperty('--duration', '26.7s'); m.style.setProperty('--play', 'running'); count('strip-pace'); });

  // footer: the owner's fuller footer (replica/footer.html) in place of the captured one; the FAQ section gets the
  // anchor its Help link points at
  const oldFooter = document.querySelector('footer.footer');
  if (!oldFooter) throw new Error('footer not found');
  { const t = document.createElement('template'); t.innerHTML = FOOTER; oldFooter.parentNode.insertBefore(t.content.firstElementChild, oldFooter); oldFooter.parentNode.removeChild(oldFooter); count('footer'); }
  const faqHead = [...document.querySelectorAll('#MainContent h1, #MainContent h2, #MainContent h3')].find(h => /^\s*FAQ\s*$/.test(h.textContent));
  if (!faqHead) throw new Error('FAQ heading not found');
  (faqHead.closest('section') || faqHead).id = 'gro-faq';

  // countdown hook
  document.querySelectorAll('gp-countdown-timer').forEach(t => { t.setAttribute('data-gro-countdown', ''); count('countdown'); });
  return n;
}, { STORE, COST_DAY, SLUG, PRICES, LADDER, FOOTER });

let html = await page.evaluate(() => '<!doctype html>\n' + document.documentElement.outerHTML);
await browser.close();

// 3. text pass: asset paths, leftovers
html = html.replace(/(["'(])assets\//g, `$1${ASSET_URL}`);
html = html.replace(/(https?:)?\/\/sofyre\.com\/cdn\/[^"' )]+/g, '');      // stray CDN refs (badge template etc.)
// AppLovin Axon base pixel (same event key as the checkout pages, from campaigns.json). The PDP has no Campaign Cart
// SDK, so pdp.js sends page_view / view_item / add_to_cart itself (see its "AppLovin Axon" block).
const CAMPAIGN = JSON.parse(fs.readFileSync(path.join(ROOT, 'campaigns/getridof/_data/campaigns.json'), 'utf8'))[SLUG];
const AXON_KEY = CAMPAIGN.axon_event_key || '';
if (AXON_KEY && !/^[0-9a-f-]{36}$/i.test(AXON_KEY)) throw new Error('axon_event_key is not an event key');
// The pixel files are fetched once the page has loaded (as on the sales page): events called before that wait in
// its queue. axon-user.js gives every event its user_data (see that file).
const AXON_USER = fs.readFileSync(path.join(ROOT, 'tools/funnel/getridof/axon-user.js'), 'utf8').replace(/\/\*[\s\S]*?\*\//, '').trim();
const AXON_FLAG = String(CAMPAIGN.axon_send_user_data).toLowerCase() === 'true' ? 'window.__axonSendUserData=true;' : '';
const AXON_HEAD = AXON_KEY ? `<script>!function(e,r){var t=["https://s.axon.ai/pixel.js","https://c.albss.com/p/l/loader.iife.js"];if(!e.axon){var a=e.axon=function(){a.performOperation?a.performOperation.apply(a,arguments):a.operationQueue.push(arguments)};a.operationQueue=[],a.ts=Date.now(),a.eventKey="${AXON_KEY}";var g=function(){for(var n=r.getElementsByTagName("script")[0],o=0;o<t.length;o++){var i=r.createElement("script");i.async=!0,i.src=t[o],n.parentNode.insertBefore(i,n)}};"complete"===r.readyState?g():e.addEventListener("load",g)}}(window,document);axon("init");window.__axonEventKey="${AXON_KEY}";window.__axonImageUrl=${JSON.stringify(CAMPAIGN.axon_image_url || '')};${AXON_FLAG}${AXON_USER}</script>\n` : '';
// TikTok pixel (tools/funnel/getridof/tiktok-head.js, as on the other sales pages): base code + window.groTT, which
// pdp.js calls next to its AppLovin events.
const TT_ID = CAMPAIGN.tiktok_pixel_id || '';
if (TT_ID && !/^[A-Z0-9]{20}$/.test(TT_ID)) throw new Error('tiktok_pixel_id is not a TikTok pixel id');
const TIKTOK_HEAD = TT_ID ? '<script>' + fs.readFileSync(path.join(ROOT, 'tools/funnel/getridof/tiktok-head.js'), 'utf8').replace(/\/\*[\s\S]*?\*\//, '').trim().replace('%ID%', TT_ID) + '</script>\n' : '';
html = html.replace('<head>', '<head>\n' + AXON_HEAD + TIKTOK_HEAD);
// The campaign on the product page: the same campaign config + Campaign Cart SDK as the checkout, and the same
// next-funnel name, so the campaign sees the page as its product step (page view, view_item, UTM / click-id
// attribution captured at landing and carried into the checkout). The loader is a module script (deferred).
// Deferred scripts run in document order: pdp.js first (the page's own interactions must not wait for the SDK's
// module graph), then config.js, then the loader.
const CAMPAIGN_HEAD = `<script src="${ASSET_URL}pdp.js" defer></script>\n<script src="/${SLUG}/config.js" defer></script>\n<meta name="next-funnel" content="${CAMPAIGN.name}">\n<meta name="next-page-type" content="product">\n<script src="https://cdn.jsdelivr.net/gh/NextCommerceCo/campaign-cart@v${CAMPAIGN.sdk_version}/dist/loader.js" type="module"></script>\n`;
html = html.replace('</head>', CAMPAIGN_HEAD + '</head>');
html = html.replace('</head>', `<link rel="stylesheet" href="${ASSET_URL}offer-ladder.css">\n<link rel="stylesheet" href="${ASSET_URL}pdp.css">\n<link rel="icon" href="${ASSET_URL}gro-logo.svg">\n</head>`);
html = html.replace(/<!-- Offline snapshot[^>]*-->/, '');
const left = (html.match(/sofyre/gi) || []).length;

// 4. page with front matter; the body is raw HTML (no Liquid inside)
const front = `---\npage_layout: pdp.html\ntitle: "Rodent Repellent Pouches – Get Rid Of"\npage_type: product\n# Generated by tools/funnel/getridof/replica/build_replica.mjs from exports/sofyre/offline/ — edit the builder, not this file.\n---\n`;
fs.writeFileSync(path.join(CAMP, 'index.html'), front + '{% raw %}' + html + '{% endraw %}\n');
fs.mkdirSync(path.join(CAMP, '_layouts'), { recursive: true });
fs.writeFileSync(path.join(CAMP, '_layouts/pdp.html'), '{{ content }}\n');
console.log(JSON.stringify(report), '\nleft "sofyre" mentions (URLs/ids only):', left, '\nwrote', path.join(CAMP, 'index.html'), (html.length / 1e6).toFixed(2) + ' MB');

const { execFileSync } = await import('node:child_process');
// desktop fonts TTF/OTF -> WOFF2 (the exported page shipped a 311 KB TTF that every visitor downloads)
execFileSync('python3', ['-I', path.join(ROOT, 'tools/funnel/getridof/optimize_fonts.py'), SLUG], { stdio: 'inherit' });
// below-the-fold images lazy-load (first screen + buy box stay eager)
execFileSync('python3', ['-I', path.join(ROOT, 'tools/funnel/getridof/lazy_images.py'), SLUG], { stdio: 'inherit' });
