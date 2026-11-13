// Builds the Get Rid Of Mouse Pouches product page (campaigns/getridof/src/mouse-pouches/index.html) from the offline
// export of the reference PDP (exports/sofyre/offline/). Re-runnable: it always starts from the export.
//
//   node tools/funnel/getridof/build_pdp.mjs
//
// What it does, in a browser DOM (Playwright, network off), then as text:
//  - brand: every "SoFyre" in the copy, titles and alt text becomes "Get Rid Of"; the header/footer logo is the
//    store's own logo (cdn.cachebucket.com, copied locally); links to sofyre.com point at getridof.shop
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
const STORE = 'https://getridof.shop';   // every visible link goes to the main domain
const ASSET_URL = '/mouse-pouches/pdp/';
// brand colour = the new packaging's green (sampled from brand/getridof/new-pack.png); replaces the reference page's lime
const BRAND_GREEN = '#7EA254';
const recolor = t => t.replace(/#ccf46f/gi, BRAND_GREEN).replace(/(rgba?\(\s*)204(\s*,\s*)244(\s*,\s*)111/gi, '$1126$2162$384');

// 1. assets
fs.mkdirSync(OUT_ASSETS, { recursive: true });
for (const f of fs.readdirSync(path.join(SRC, 'assets'))) if (!/sofyre/i.test(f)) fs.copyFileSync(path.join(SRC, 'assets', f), path.join(OUT_ASSETS, f));
for (const [name, url] of [['gro-logo.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo.svg`],
                           ['gro-logo-white.svg', `https://cdn.cachebucket.com/media/getridof/themes/11/assets/assets/img/gro/logo-white.svg`]]) {
  const r = await fetch(url); if (!r.ok) throw new Error(`logo ${url}: ${r.status}`);
  fs.writeFileSync(path.join(OUT_ASSETS, name), Buffer.from(await r.arrayBuffer()));
}
fs.copyFileSync(path.join(ROOT, 'tools/funnel/getridof/pdp.js'), path.join(OUT_ASSETS, 'pdp.js'));
fs.copyFileSync(path.join(ROOT, 'tools/funnel/getridof/pdp.css'), path.join(OUT_ASSETS, 'pdp.css'));
for (const f of fs.readdirSync(OUT_ASSETS)) if (f.endsWith('.css')) { const fp = path.join(OUT_ASSETS, f); fs.writeFileSync(fp, recolor(fs.readFileSync(fp, 'utf8'))); }

// favicon + touch icon for the checkout/receipt layout (the starter shipped NEXT's): the store logo on white, square
{
  const svg = fs.readFileSync(path.join(OUT_ASSETS, 'gro-logo.svg'), 'utf8');
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 180, height: 180 } });
  await pg.setContent(`<html><body style="margin:0;width:180px;height:180px;display:flex;align-items:center;justify-content:center;background:#fff"><div style="width:164px">${svg.replace('<svg', '<svg style="width:100%;height:auto;display:block"')}</div></body></html>`);
  for (const f of ['favicon.png', 'webclip.png']) await pg.screenshot({ path: path.join(CAMP, 'assets/images', f) });
  await b.close();
}

// long-sales-page sections (tools/funnel/getridof/sections.html, copy from campaigns/getridof/sales-page/copy-deck.md)
const SECTIONS = Object.fromEntries([...fs.readFileSync(path.join(ROOT, 'tools/funnel/getridof/sections.html'), 'utf8')
  .matchAll(/<!--@([\w-]+)-->([\s\S]*?)<!--@end-->/g)].map(m => [m[1], m[2].trim()]));
for (const f of fs.readdirSync(path.join(ROOT, 'brand/getridof/sections'))) fs.copyFileSync(path.join(ROOT, 'brand/getridof/sections', f), path.join(OUT_ASSETS, f));

// authority figure (section 12): only a real, consenting expert from brand/getridof/expert.json; never generated
const EXPERT = JSON.parse(fs.readFileSync(path.join(ROOT, 'brand/getridof/expert.json'), 'utf8'));
const CERTS = (EXPERT.certifications || []).filter(c => c && c.title && c.issuer);
if (EXPERT.approved === true && ['name', 'credentials', 'bio', 'photo_file', 'quote'].every(k => String(EXPERT[k] || '').trim())) {
  if (!fs.existsSync(path.join(ROOT, 'brand/getridof/sections', EXPERT.photo_file))) throw new Error('expert photo missing: ' + EXPERT.photo_file);
  const certs = CERTS.map(c => `<li><b>${esc(c.title)}</b><span>${esc(c.issuer)}${c.number ? ' · No. ' + esc(c.number) : ''}</span></li>`).join('');
  SECTIONS.expert = `<div class="gro-expert">
    <div class="gro-expert__head"><img src="assets/${esc(EXPERT.photo_file)}" alt="${esc(EXPERT.name)}" width="120" height="120" loading="lazy">
      <div><p class="gro-expert__who"><b>${esc(EXPERT.name)}</b></p><p class="gro-expert__cred">${esc(EXPERT.credentials)}${EXPERT.organization ? ' · ' + esc(EXPERT.organization) : ''}${EXPERT.years_experience ? ' · ' + esc(EXPERT.years_experience) + ' years in the field' : ''}</p></div></div>
    <p class="gro-expert__bio">${esc(EXPERT.bio)}</p>
    ${certs ? `<ul class="gro-expert__certs" aria-label="Certifications">${certs}</ul>` : ''}
    <blockquote>“${esc(EXPERT.quote)}”</blockquote>
    ${EXPERT.disclosure ? `<p class="gro-expert__disc">${esc(EXPERT.disclosure)}</p>` : ''}</div>`;
  console.error('expert: ' + EXPERT.name + ' (' + CERTS.length + ' certifications)');
} else console.error('expert: none approved in brand/getridof/expert.json (section 12 shows the EPA source only)');

// 2. DOM pass
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
await page.goto('file://' + path.join(SRC, 'index.html'), { waitUntil: 'load' });
const report = await page.evaluate(({ STORE, SECTIONS }) => {
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

  // scroll locks frozen in by popups open at capture time (Klaviyo's form left klaviyo-prevent-body-scrolling on body)
  [document.documentElement, document.body].forEach(el => {
    [...el.classList].filter(c => /prevent-body-scroll|no-scroll|overflow-hidden|modal-open|scroll-lock|lock-scroll|menu-open|drawer-open/i.test(c)).forEach(c => { el.classList.remove(c); count('scroll-lock'); });
    el.style.removeProperty('overflow'); el.style.removeProperty('position');
  });

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

  // ---- the 20-step long-sales-page order (campaigns/getridof/sales-page/copy-deck.md) ----
  const frag = html => { const t = document.createElement('template'); t.innerHTML = html; return t.content.firstElementChild; };
  // above the fold (2-4): problem/promise headline, summary, benefit bullets, guarantee, before the product title
  const title = document.querySelector('.exp-atf__product-title');
  if (title) { title.parentElement.insertBefore(frag(SECTIONS.atf), title); count('atf'); }
  const main = document.querySelector('#MainContent');
  const secs = [...main.children].filter(e => e.matches('section, div.shopify-section, .shopify-section'));
  const hero = secs[0];
  // match on the section's own headings (h1-h3 or GemPages heading text), never inside the hero's buy box
  const find = re => secs.find(s => s !== hero && [...s.querySelectorAll('h1,h2,h3,[data-gp-text] p')].some(h => re.test(h.textContent.trim())));
  const S = {
    hero, press: find(/BUZZZ/), timeline: find(/Exactly What Happens/), safe: find(/Safe Home/), props: find(/35,129/),
    reviews: find(/Real Results From/), science: find(/Science of Nature/), directions: find(/Directions Of Use/),
    stack: find(/How We Stack Up/), guarantee: find(/^30 Day Money Back Guarantee$/i), faq: find(/^FAQ$/), help: find(/Still Need help/i) || null,
  };
  const missing = Object.entries(S).filter(([k, v]) => !v && k !== 'help').map(([k]) => k);
  if (missing.length) throw new Error('sections not found: ' + missing.join(', '));
  S.press.remove(); count('press-bar-removed');   // "as seen in" logos: coverage of the sister brand, not this one
  S.guarantee.appendChild(frag(SECTIONS['guarantee-claim']));
  // FAQ extras go into the FAQ's right-hand column, after its last item
  const faqCols = S.faq.querySelectorAll('gp-accordion'); const lastCol = faqCols[faqCols.length - 1];
  lastCol.parentElement.insertBefore(frag(SECTIONS['faq-extra']), lastCol.nextSibling);
  // the GemPages "Still Need help?" box is replaced by the customer-service section (step 20)
  const helpH = [...S.faq.querySelectorAll('h2,h3,p')].find(e => /Still Need help/i.test(e.textContent));
  if (helpH) { let box = helpH; for (let i = 0; i < 6 && box.parentElement; i++) box = box.parentElement; if (box.matches('gp-row')) { box.remove(); count('old-help-box'); } }
  // footer: the store's footer (signup heading without a form, policy list) becomes the brand footer
  const oldFooter = document.querySelector('footer.footer');
  if (oldFooter) { oldFooter.parentElement.insertBefore(frag(SECTIONS.footer), oldFooter); oldFooter.remove(); count('footer'); }
  const rest = secs.filter(x => !Object.values(S).includes(x));   // anything unmapped keeps its place at the end
  const order = [S.hero, 'problem', 'mechanism', 'solution-intro', S.timeline, 'others', S.stack, S.science, S.safe, 'before-after', 'proof', 'dream',
                 S.directions, S.guarantee, 'offer', 'scarcity', S.props, S.reviews, S.faq, 'support', ...(S.help && S.help !== S.faq ? [S.help] : []), ...rest];
  for (const item of order) { main.appendChild(typeof item === 'string' ? frag(SECTIONS[item]) : item); }
  if (SECTIONS.expert) { const auth = main.querySelector('[data-gro-step="12"] .gro-authority'); if (auth) { auth.parentElement.insertBefore(frag(SECTIONS.expert), auth); count('expert'); } }
  count('sections-ordered', order.length);
  // section buttons carry the ATC hook added above only for pre-existing buttons
  main.querySelectorAll('.gro-btn[data-gro-atc]').forEach(() => count('section-cta'));

  // header button: "Track Order" becomes the sticky "Shop Now" CTA (the header stays on top; it scrolls to the bundle box)
  document.querySelectorAll('a.header__icons-btn').forEach(a => { a.textContent = 'Shop Now'; a.setAttribute('href', '#gro-buy'); a.classList.add('gro-shop-cta'); count('shop-cta'); });

  // countdown hook
  document.querySelectorAll('gp-countdown-timer').forEach(t => { t.setAttribute('data-gro-countdown', ''); count('countdown'); });
  return n;
}, { STORE, SECTIONS });

let html = await page.evaluate(() => '<!doctype html>\n' + document.documentElement.outerHTML);
await browser.close();

// 3. text pass: asset paths, leftovers
html = recolor(html.replace(/(["'(])assets\//g, `$1${ASSET_URL}`));
html = html.replace(/(https?:)?\/\/sofyre\.com\/cdn\/[^"' )]+/g, '');      // stray CDN refs (badge template etc.)
// AppLovin Axon base pixel (same event key as the checkout pages, from campaigns.json). The PDP has no Campaign Cart
// SDK, so pdp.js sends page_view / view_item / add_to_cart itself (see its "AppLovin Axon" block).
const CAMPAIGN = JSON.parse(fs.readFileSync(path.join(ROOT, 'campaigns/getridof/_data/campaigns.json'), 'utf8'))['mouse-pouches'];
const AXON_KEY = CAMPAIGN.axon_event_key || '';
if (AXON_KEY && !/^[0-9a-f-]{36}$/i.test(AXON_KEY)) throw new Error('axon_event_key is not an event key');
const AXON_HEAD = AXON_KEY ? `<script>!function(e,r){var t=["https://s.axon.ai/pixel.js","https://c.albss.com/p/l/loader.iife.js"];if(!e.axon){var a=e.axon=function(){a.performOperation?a.performOperation.apply(a,arguments):a.operationQueue.push(arguments)};a.operationQueue=[],a.ts=Date.now(),a.eventKey="${AXON_KEY}";for(var n=r.getElementsByTagName("script")[0],o=0;o<t.length;o++){var i=r.createElement("script");i.async=!0,i.src=t[o],n.parentNode.insertBefore(i,n)}}}(window,document);axon("init");window.__axonEventKey="${AXON_KEY}";window.__axonImageUrl=${JSON.stringify(CAMPAIGN.axon_image_url || '')};</script>\n` : '';
html = html.replace('<head>', '<head>\n' + AXON_HEAD);
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

// 5. step 1 copied the reference page's packaging shots: put the new-packaging images back over them, every run
//    (skipping this once shipped the old photos; see swap_images.py)
const { execFileSync } = await import('node:child_process');
execFileSync('python3', [path.join(ROOT, 'tools/funnel/getridof/swap_images.py')], { stdio: 'inherit' });
