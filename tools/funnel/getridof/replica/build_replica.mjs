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
//  - what differs from the source, on purpose: the money-back guarantee is this brand's 90 days, the dispatch line
//    quotes this brand's shipping time, the payment marks are the ones this checkout takes, and the "as seen in"
//    press logos are left out (they are not this brand's)
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../../..');
const SLUG = 'mouse-repellent-pouches';
const SRC = path.join(ROOT, 'exports/sofyre/offline');
const CAMP = path.join(ROOT, 'campaigns/getridof/src', SLUG);
const OUT_ASSETS = path.join(CAMP, 'assets/pdp');
const STORE = 'https://getridof.shop';   // every visible link goes to the main domain
const ASSET_URL = `/${SLUG}/pdp/`;
// brand colour = the new packaging's green (sampled from brand/getridof/new-pack.png); replaces the reference page's lime
const BRAND_GREEN = '#7EA254';
const recolor = t => t.replace(/#ccf46f/gi, BRAND_GREEN).replace(/(rgba?\(\s*)204(\s*,\s*)244(\s*,\s*)111/gi, '$1126$2162$384');

// 1. assets
fs.mkdirSync(OUT_ASSETS, { recursive: true });
// The funnel folder arrives with src/mouse-pouches/assets/pdp (build_replica.py): the same files with the Get Rid Of
// packaging and the 90-day guarantee already in the images. Only what is missing there is taken from the export.
let fresh = 0;
for (const f of fs.readdirSync(path.join(SRC, 'assets'))) if (!/sofyre/i.test(f) && !fs.existsSync(path.join(OUT_ASSETS, f))) { fs.copyFileSync(path.join(SRC, 'assets', f), path.join(OUT_ASSETS, f)); fresh++; }
const freshImages = fs.readdirSync(path.join(SRC, 'assets')).filter(f => /\.(png|jpe?g|webp|gif|avif)$/i.test(f) && !/sofyre/i.test(f) && !fs.existsSync(path.join(ROOT, 'campaigns/getridof/src/mouse-pouches/assets/pdp', f)));
if (freshImages.length) throw new Error('images that never went through the brand swap: ' + freshImages.join(', '));
for (const [name, url] of [['gro-logo.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo.svg`],
                           ['gro-logo-white.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo-white.svg`]]) {
  const r = await fetch(url); if (!r.ok) throw new Error(`logo ${url}: ${r.status}`);
  fs.writeFileSync(path.join(OUT_ASSETS, name), Buffer.from(await r.arrayBuffer()));
}
const PRICES = JSON.parse(fs.readFileSync(path.join(HERE, 'prices.json'), 'utf8'));   // what the bundle box shows
fs.writeFileSync(path.join(OUT_ASSETS, 'pdp.js'), fs.readFileSync(path.join(HERE, 'pdp.js'), 'utf8').replaceAll('@@SLUG@@', SLUG).replace('@@PRICES@@', JSON.stringify(PRICES)));
fs.copyFileSync(path.join(HERE, 'pdp.css'), path.join(OUT_ASSETS, 'pdp.css'));
for (const f of fs.readdirSync(OUT_ASSETS)) if (f.endsWith('.css')) { const fp = path.join(OUT_ASSETS, f); fs.writeFileSync(fp, recolor(fs.readFileSync(fp, 'utf8'))); }

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
const FOOTER = fs.readFileSync(path.join(HERE, 'footer.html'), 'utf8').replace(/<!--[\s\S]*?-->/, '').trim();
const COST_DAY = '$0.25';   // "Cost per day of protection": one pack with Automatic Refills, $22.49 over its 90 days
const report = await page.evaluate(({ STORE, FOOTER, COST_DAY, SLUG, PRICES }) => {
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
  const later = [];   // edits that replace nodes wait until the walk is over
  for (let t; (t = tw.nextNode());) {
    const pe = t.parentElement; if (!pe || ['SCRIPT'].includes(pe.tagName)) continue;
    if (pe.tagName === 'STYLE') { if (/sofyre/i.test(t.data)) t.data = t.data.replace(/sofyre-/gi, 'gro-'); continue; }
    if (/sofyre/i.test(t.data)) { t.data = swap(t.data); count('text-brand'); }
    if (/30[\s-]?days?\b/i.test(t.data) && /money|guarantee|refund|leave within/i.test(pe.closest('section, div, li, p').textContent)) { t.data = t.data.replace(/30([\s-]?days?\b)/gi, '90$1'); count('guarantee-90'); }
    // "UP TO 72% OFF" (banner and the badge on the first photo) stays: this campaign's deepest discount is 74%
    if (/an 8% concentration formula/.test(t.data)) { t.data = t.data.replace('an 8% concentration formula', 'a 40% peppermint formula'); count('formula-40'); }   // the page states 40% everywhere else
    if (t.data.trim() === 'Today' && /^Ships/.test(pe.parentElement.textContent.trim())) { const line = pe.parentElement; later.push(() => { line.innerHTML = 'Ships in<br><strong>1 Day</strong>'; line.style.whiteSpace = 'nowrap'; line.parentElement.style.overflow = 'visible'; count('ships'); }); }   // the page's own shipping terms
    if (/perimetereter/.test(t.data)) { t.data = t.data.replace(/perimetereter/g, 'perimeter'); count('typo'); }
    if (t.data.trim() === '$0.33') { t.data = t.data.replace('$0.33', COST_DAY); count('cost-per-day'); }
  }
  later.forEach(f => f());
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
  // prices with Automatic Refills ticked, Buy 2 Get 1 Free selected, and the refill terms under the box
  if (sub) sub.setAttribute('aria-checked', 'true');
  bars.forEach((bar, i) => {
    const p = PRICES[ids[i]], set = (sel, v) => { const e = bar.querySelector(sel); if (!e) throw new Error('bundle bar: ' + sel + ' not found'); e.textContent = v; };
    set('.kaching-bundles__bar-price .money', p.sub[0]); set('.kaching-bundles__bar-full-price .money', p.full); set('.kaching-bundles__bar-subtitle', p.sub[1]);
    bar.classList.toggle('kaching-bundles__bar--selected', ids[i] === 'buy3'); count('bundle-price');
  });
  if (box) {
    const info = document.createElement('div'); info.className = 'gro-subinfo';
    info.innerHTML = `<p class="gro-subinfo__line"><span data-gro-firstoff>First order ${PRICES.buy3.sub[0]}</span> · then <b>$34.99 a pack</b>, <span data-gro-renew>${PRICES.buy3.renew}</span></p>` +
      '<div class="gro-subinfo__row"><span><i>↻</i>Skip anytime</span><span><i>✕</i>Cancel anytime</span><span><i>✓</i>90-day money-back</span></div>';
    box.parentNode.insertBefore(info, box.nextSibling); count('refill-terms');
  }
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

  // "as seen in" press logos: coverage of the sister brand, not this one
  const main = document.querySelector('#MainContent');
  const buzz = [...main.querySelectorAll('p, h2, h3, span, div')].find(x => /BUZZ/i.test(x.textContent) && !x.children.length);
  if (buzz) {
    // the band = the smallest block around that line that also holds the logos, and nothing else
    let box = buzz; while (box.parentElement && box.parentElement !== main && box.querySelectorAll('img').length < 3) box = box.parentElement;
    const sec = box.closest('section'); if (sec && sec.textContent.trim().length < 600) box = sec;
    if (box.textContent.trim().length > 600) throw new Error('press band not isolated');
    box.remove(); count('press-bar-removed');
  }

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
  // miniatures under the main photo (the source page's phone layout shows them; its captured desktop markup holds
  // them in a hidden slider frozen at zero size). A plain row of buttons takes that slider's place: small files made
  // by build_replica.py, the first one marked as current; pdp.js moves the gallery when one is tapped.
  document.querySelectorAll('.gallery-wrapper.gp-product-images-gallery').forEach(e => { if (e.querySelector('gp-carousel-v3.carousel-gallery')) { e.parentNode.removeChild(e); count('old-thumb-slider'); } });
  const dotsEl = document.querySelector('.exp-atf__dots');
  if (!dotsEl) throw new Error('gallery dots not found');
  const row = document.createElement('div'); row.className = 'gro-thumbs'; row.setAttribute('role', 'group'); row.setAttribute('aria-label', 'Product photos');
  row.innerHTML = slides.map((_, i) => `<button type="button" class="gro-thumb${i ? '' : ' gro-thumb-active'}" aria-label="Photo ${i + 1} of ${slides.length}"><img src="/${SLUG}/pdp/gro-thumb-${i + 1}.webp" alt="" width="128" height="128" decoding="async"></button>`).join('');
  dotsEl.parentNode.insertBefore(row, dotsEl.nextSibling); count('thumbs', slides.length);
  // the header menu's two pictures: small files, fetched when the menu is opened
  document.querySelectorAll('.header-mobile-menu img').forEach(img => {
    const s = img.getAttribute('src') || '';
    if (/P_1_1-/.test(s)) img.setAttribute('src', `/${SLUG}/lp/thumb.webp`); else if (/Buy_3-/.test(s)) img.setAttribute('src', `/${SLUG}/pdp/gro-menu-banner.webp`); else return;
    img.setAttribute('loading', 'lazy'); img.setAttribute('decoding', 'async'); count('menu-img');
  });

  // moving photo strips: a strip that was hidden when the page was captured has no pace (0s = it never moves);
  // give every strip a phone-sized default, which pdp.js then sets from the real width
  document.querySelectorAll('gp-marquee .rfm-marquee').forEach(m => { m.style.setProperty('--duration', '26.7s'); m.style.setProperty('--play', 'running'); count('strip-pace'); });

  // payment marks under the button: only what this checkout takes (no Shop Pay, Diners or Maestro)
  document.querySelectorAll('img[src*="ShopPay-"], img[src*="DinersClub-"], img[src*="Maestro-"]').forEach(img => {
    let box = img.closest('[class*="gp-group/image"]') || img; const par = box.parentElement; box.remove();
    if (par && !par.children.length && !par.textContent.trim()) par.remove(); count('pay-mark-removed');
  });

  // footer: the source store's footer (newsletter signup, its own policy list) gives way to the brand footer
  const oldFooter = document.querySelector('footer.footer');
  if (oldFooter) { const t = document.createElement('template'); t.innerHTML = FOOTER; oldFooter.parentElement.insertBefore(t.content.firstElementChild, oldFooter); oldFooter.remove(); count('footer'); }

  // header button: "Track Order" becomes the sticky "Shop Now" CTA (the header stays on top; it scrolls to the bundle box)
  document.querySelectorAll('a.header__icons-btn').forEach(a => { a.textContent = 'Shop Now'; a.setAttribute('href', '#gro-buy'); a.classList.add('gro-shop-cta'); count('shop-cta'); });

  // countdown hook
  document.querySelectorAll('gp-countdown-timer').forEach(t => { t.setAttribute('data-gro-countdown', ''); count('countdown'); });
  return n;
}, { STORE, FOOTER, COST_DAY, SLUG, PRICES });

let html = await page.evaluate(() => '<!doctype html>\n' + document.documentElement.outerHTML);
await browser.close();

// 3. text pass: asset paths, leftovers
html = recolor(html.replace(/(["'(])assets\//g, `$1${ASSET_URL}`));
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
html = html.replace('<head>', '<head>\n' + AXON_HEAD);
// The campaign on the product page: the same campaign config + Campaign Cart SDK as the checkout, and the same
// next-funnel name, so the campaign sees the page as its product step (page view, view_item, UTM / click-id
// attribution captured at landing and carried into the checkout). The loader is a module script (deferred).
// Deferred scripts run in document order: pdp.js first (the page's own interactions must not wait for the SDK's
// module graph), then config.js, then the loader.
const CAMPAIGN_HEAD = `<script src="${ASSET_URL}pdp.js" defer></script>\n<script src="/${SLUG}/config.js" defer></script>\n<meta name="next-funnel" content="${CAMPAIGN.name}">\n<meta name="next-page-type" content="product">\n<script src="https://cdn.jsdelivr.net/gh/NextCommerceCo/campaign-cart@v${CAMPAIGN.sdk_version}/dist/loader.js" type="module"></script>\n`;
html = html.replace('</head>', CAMPAIGN_HEAD + '</head>');
html = html.replace('</head>', `<link rel="stylesheet" href="${ASSET_URL}pdp.css">\n<link rel="icon" href="${ASSET_URL}gro-logo.svg">\n</head>`);
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
