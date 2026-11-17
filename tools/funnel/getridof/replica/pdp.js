/* Get Rid Of — replica product page runtime (no dependencies). @@SLUG@@ is the funnel slug (build_replica.mjs).
 * The page is a static snapshot of a GemPages/Shopify product page; this file brings back the interactions its
 * own scripts provided and connects the buy box to the Campaigns App funnel:
 *   bundle bars + Automatic Refills toggle -> ADD TO CART -> /@@SLUG@@/checkout/?forceBundleId=main:<bundle>
 *     (buy1 / buy3 / buy5 with refills, ot1 / ot3 / ot5 for a one-time purchase)
 *   accordions, tabs, product gallery (thumbs, dots, swipe), review carousels (swipe on phones),
 *   "Order within" countdown, info chips.
 * Built into the page by tools/funnel/getridof/replica/build_replica.mjs. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var CHECKOUT = '/@@SLUG@@/checkout/';

  /* ---------- buy box ---------- */
  var bars = $$('[data-gro-bundle]');
  var refillEl = $('[data-gro-refill]');
  var state = {
    bundle: (bars.filter(function (b) { return b.classList.contains('kaching-bundles__bar--selected'); })[0] || bars[1] || bars[0] || { dataset: {} }).dataset.groBundle || 'buy3',
    refill: true   // Automatic Refills are ticked on arrival, as on the source page; the shopper can untick them
  };
  function renderBox() {
    bars.forEach(function (b) {
      var on = b.dataset.groBundle === state.bundle;
      b.classList.toggle('kaching-bundles__bar--selected', on);
      var r = $('input[type="radio"]', b); if (r) r.checked = on;
    });
    if (refillEl) refillEl.setAttribute('aria-checked', state.refill ? 'true' : 'false');
  }
  bars.forEach(function (b) {
    b.addEventListener('click', function (e) { e.preventDefault(); state.bundle = b.dataset.groBundle; renderBox(); });
    var main = $('.kaching-bundles__bar-main', b);
    if (main) main.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); state.bundle = b.dataset.groBundle; renderBox(); } });
  });
  var SUBSCRIPTION_ONLY = false;  // the box is a real toggle: unticked = one-time purchase
  if (SUBSCRIPTION_ONLY) { state.refill = true; if (refillEl) { refillEl.setAttribute('aria-disabled', 'true'); refillEl.classList.add('gro-locked'); } }
  if (refillEl && !SUBSCRIPTION_ONLY) {
    var flip = function (e) { e.preventDefault(); state.refill = !state.refill; renderBox(); };
    refillEl.addEventListener('click', flip);
    refillEl.addEventListener('keydown', function (e) { if (e.key === ' ' || e.key === 'Enter') flip(e); });
  }
  renderBox();

  function checkoutUrl() {
    var q = new URLSearchParams(location.search);
    q.delete('forceBundleId'); q.delete('forcePackageId');
    q.set('forceBundleId', 'main:' + (state.refill ? state.bundle : state.bundle.replace('buy', 'ot')));
    return CHECKOUT + '?' + q.toString();
  }
  window.groCheckoutUrl = checkoutUrl;
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-gro-atc]');
    if (!t) return;
    e.preventDefault(); e.stopPropagation();
    var url = checkoutUrl();
    axonTrack('add_to_cart', axonPayload());
    setTimeout(function () { location.href = url; }, window.axon ? 300 : 0);   // let the pixel send before leaving
  }, true);

  /* ---------- AppLovin Axon (no SDK on this page: events are sent here) ----------
   * Same item shape as axon.adapter.js on the checkout: item_id = SKU of the subscription variant (package 2,
   * SKU cdkh-16-1s; subscription variants 8 / 37 / 38 for the 1 / 3 / 5-pack), item_category_id 7137 = Animal & Pet Repellents, image_url must be .png/.jpg. */
  var AXON_TIERS = { buy1: { qty: 1, unit: 22.49, variant: '8' }, buy3: { qty: 3, unit: 15.99, variant: '37' }, buy5: { qty: 5, unit: 12.99, variant: '38' },
                     ot1: { qty: 1, unit: 34.99, variant: '7' }, ot3: { qty: 3, unit: 23.33, variant: '7' }, ot5: { qty: 5, unit: 20.99, variant: '7' } };
  var AXON_RETAIL = 49.99;
  function axonPayload() {
    var t = AXON_TIERS[state.refill ? state.bundle : state.bundle.replace('buy', 'ot')] || AXON_TIERS.buy3;
    var item = { item_id: 'cdkh-16-1s', item_name: 'Mouse Repellent Pouches', item_variant_id: t.variant, item_brand: 'Get Rid Of',
                 item_category_id: 7137, price: t.unit, quantity: t.qty, discount: Math.round((AXON_RETAIL - t.unit) * 100) / 100 };
    if (window.__axonImageUrl) item.image_url = window.__axonImageUrl;
    return { currency: 'USD', value: Math.round(t.unit * t.qty * 100) / 100, items: [item] };
  }
  function axonTrack(name, data) {
    try {
      if (typeof window.axon !== 'function') return;
      var user = window.groAxonUser ? window.groAxonUser.get() : undefined;   // user_id always; email / phone once the shopper gave them
      if (user) { data = data || {}; data.user_data = user; }
      data ? window.axon('track', name, data) : window.axon('track', name);
    } catch (err) { /* never block the page */ }
  }
  window.groAxonPayload = axonPayload;
  axonTrack('page_view');
  axonTrack('view_item', axonPayload());
  // links to the buy box scroll to it
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href="#gro-buy"]');
    if (!a || a.hasAttribute('data-gro-atc')) return;
    var box = document.getElementById('gro-buy'); if (!box) return;
    e.preventDefault(); box.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  /* ---------- accordions (GemPages: body max-height 0 when closed) ---------- */
  $$('gp-accordion .gp-accordion-item').forEach(function (item) {
    var head = $('.gp-accordion-item_header', item), body = $('.gp-accordion-item_body', item);
    if (!head || !body) return;
    var setOpen = function (open) {
      body.style.maxHeight = open ? 'none' : '0px';
      item.classList.toggle('gro-open', open);
      head.setAttribute('aria-expanded', open ? 'true' : 'false');
      var inner = $('[style*="--o:0"]', body); if (inner && open) inner.style.setProperty('--o', '1');
    };
    setOpen(body.style.maxHeight !== '0px' && getComputedStyle(body).maxHeight !== '0px');
    head.setAttribute('role', 'button'); head.setAttribute('tabindex', '0');
    var toggle = function () { setOpen(!item.classList.contains('gro-open')); };
    head.addEventListener('click', toggle);
    head.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
  });
  function openAccordionByText(re) {
    var hit = $$('gp-accordion .gp-accordion-item').filter(function (i) { var h = $('.gp-accordion-item_header', i); return h && re.test(h.textContent); })[0];
    if (!hit) return false;
    if (!hit.classList.contains('gro-open')) $('.gp-accordion-item_header', hit).click();
    hit.scrollIntoView({ behavior: 'smooth', block: 'center' }); return true;
  }

  /* ---------- tabs ---------- */
  $$('gp-tab').forEach(function (tab) {
    var navs = $$('li.gp-tab-item', tab);
    var panels = $$('.gp-tab-item[class*="gp-child-item-"]', tab).filter(function (p) { return p.tagName !== 'LI'; });
    // keep only top-level panels of this tab (not panels of a nested tab)
    panels = panels.filter(function (p) { return p.parentElement && p.parentElement.closest('gp-tab') === tab && !p.parentElement.closest('.gp-tab-item[class*="gp-child-item-"]'); });
    if (!navs.length || !panels.length) return;
    var visible = function (el) { return getComputedStyle(el).display !== 'none'; };
    var active = Math.max(0, panels.findIndex(visible));
    var onStyle = navs[active].getAttribute('style') || '';
    var offStyle = (navs[active === 0 ? 1 : 0] || navs[active]).getAttribute('style') || '';
    var show = function (i) {
      navs.forEach(function (n, k) { n.setAttribute('style', k === i ? onStyle : offStyle); n.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
      // a panel that was closed when the page was captured carries visibility:hidden, position:absolute, height:0
      // and overflow:hidden inline: the open one gets the open panel's values, not only display
      panels.forEach(function (p, k) {
        var on = k === i;
        p.style.display = on ? 'block' : 'none';
        p.style.visibility = on ? 'visible' : 'hidden';
        p.style.position = on ? 'relative' : 'absolute';
        p.style.height = on ? 'auto' : '0px';
        p.style.overflow = on ? 'visible' : 'hidden';
        p.style.setProperty('--v', on ? 'visible' : 'hidden'); p.style.setProperty('--pos', on ? 'relative' : 'absolute');
      });
      if (typeof loadDeferred === 'function') setTimeout(function () { window.dispatchEvent(new Event('scroll')); }, 0);   // lazy photos in the newly shown panel
    };
    navs.forEach(function (n, i) {
      n.setAttribute('role', 'tab'); n.setAttribute('tabindex', '0');
      n.addEventListener('click', function () { show(i); });
      n.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(i); } });
    });
    show(active);
  });

  /* ---------- product gallery: featured carousel + thumbs + mobile dots ---------- */
  var feat = $('gp-carousel-v3.gp-feature-image-carousel');
  var thumbs = $$('.gro-thumb');   // the row of miniatures under the photo
  var dots = $$('.exp-atf__dot');
  if (feat) {
    var wrap = $('.gem-slider-wrapper', feat);
    var slides = wrap ? Array.prototype.slice.call(wrap.children) : [];
    var cur = 0;
    var go = function (i) {
      if (!slides.length) return;
      cur = (i + slides.length) % slides.length;
      // size every slide to the visible stage (the snapshot froze them at the 631px desktop width)
      var stage = wrap.parentElement, w = stage.clientWidth || feat.getBoundingClientRect().width;
      slides.forEach(function (s) { s.style.setProperty('width', w + 'px', 'important'); s.style.setProperty('min-width', w + 'px', 'important'); s.style.setProperty('max-width', w + 'px', 'important'); s.style.setProperty('height', w + 'px', 'important'); });
      wrap.style.setProperty('width', (w * slides.length) + 'px', 'important');
      wrap.style.transition = 'transform 300ms ease';
      // the slides sit a few pixels apart, so the shift is the slide's own offset in the track, not cur * width
      var shift = slides[cur].getBoundingClientRect().left - slides[0].getBoundingClientRect().left;
      wrap.style.transform = 'translate3d(' + (-shift) + 'px,0,0)';
      dots.forEach(function (d, k) { d.setAttribute('aria-current', k === cur ? 'true' : 'false'); });
      thumbs.forEach(function (t, k) {
        t.classList.toggle('gro-thumb-active', k === cur);
        if (k === cur && t.parentNode.scrollWidth > t.parentNode.clientWidth) t.parentNode.scrollTo({ left: t.offsetLeft - (t.parentNode.clientWidth - t.offsetWidth) / 2, behavior: 'smooth' });
      });
    };
    thumbs.forEach(function (t, k) { t.addEventListener('click', function () { if (typeof loadDeferred === 'function') loadDeferred(); go(k); }); });
    dots.forEach(function (d, k) { d.addEventListener('click', function (e) { e.preventDefault(); go(k); }); });
    $$('.gp-carousel-action-back', feat).forEach(function (b) { b.addEventListener('click', function () { go(cur - 1); }); });
    $$('.gp-carousel-action-next', feat).forEach(function (b) { b.addEventListener('click', function () { go(cur + 1); }); });
    var x0 = null;
    feat.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    feat.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) go(cur + (dx < 0 ? 1 : -1)); x0 = null; });
    window.addEventListener('resize', function () { go(cur); });
    go(0);
  }

  /* ---------- gallery photos 2-7 and the thumbnails: fetched once the page has loaded, or on the first touch ---------- */
  var deferredDone = false;
  function loadDeferred() {
    if (deferredDone) return; deferredDone = true;
    $$('img[data-gro-src]').forEach(function (i) { i.src = i.getAttribute('data-gro-src'); i.removeAttribute('data-gro-src'); });
  }
  ['pointerdown', 'touchstart', 'keydown', 'wheel', 'scroll'].forEach(function (ev) { addEventListener(ev, loadDeferred, { once: true, passive: true }); });
  var afterLoad = function (f, ms) { if (document.readyState === 'complete') setTimeout(f, ms); else addEventListener('load', function () { setTimeout(f, ms); }); };
  afterLoad(loadDeferred, 1500);
  // the first photo arrives inside the HTML at phone size; on wider screens the full file replaces it after load
  afterLoad(function () {
    var hero = $('img[data-gro-hd]'); if (!hero || hero.getBoundingClientRect().width <= 420) return;
    var full = new Image(); full.onload = function () { hero.src = full.src; }; full.src = hero.getAttribute('data-gro-hd');
  }, 300);

  /* ---------- moving photo strips: the same speed as the source page (40 px a second) ----------
   * Each strip is two copies of one track sliding by its own width; the time for one pass follows the track's width,
   * which differs per screen. The HTML carries a phone-sized default so the strip moves before this runs. */
  function paceStrips() {
    $$('gp-marquee .rfm-marquee').forEach(function (m) {
      var w = m.getBoundingClientRect().width;
      if (w > 0) m.style.setProperty('--duration', (Math.round(w / 40 * 10) / 10) + 's');
    });
  }
  paceStrips(); addEventListener('load', paceStrips); addEventListener('resize', paceStrips);

  /* ---------- other carousels: drop loop clones; swipeable scroller on phones ---------- */
  $$('gp-carousel-v3').forEach(function (c) {
    if (c === feat) return;
    var wrap = $('.gem-slider-wrapper', c); if (!wrap) return;
    var seen = {};
    Array.prototype.slice.call(wrap.children).forEach(function (s) {
      var k = s.getAttribute('data-index'); if (k === null || k === '') return;
      if (seen[k]) s.remove(); else seen[k] = 1;
    });
    c.classList.add('gro-carousel');
    if (wrap.parentElement) wrap.parentElement.classList.add('gro-scroller');   // the box the cards slide in (pdp.css lets it scroll on phones)
    wrap.style.setProperty('transform', 'none', 'important');
    wrap.style.setProperty('width', 'auto', 'important');
  });

  /* ---------- countdown: time left today ---------- */
  $$('[data-gro-countdown]').forEach(function (t) {
    var nums = $$('.gp-countdown-number', t);
    if (nums.length < 3) return;
    var pad = function (v) { return (v < 10 ? '0' : '') + v; };
    var tick = function () {
      var now = new Date(), end = new Date(now); end.setHours(23, 59, 59, 999);
      var s = Math.max(0, Math.floor((end - now) / 1000));
      nums[0].textContent = pad(Math.floor(s / 3600)); nums[1].textContent = pad(Math.floor(s % 3600 / 60)); nums[2].textContent = pad(s % 60);
    };
    tick(); setInterval(tick, 1000);
  });

  /* ---------- info chips -> the section that answers them ---------- */
  $$('.exp-atf__chip').forEach(function (chip) {
    chip.addEventListener('click', function (e) {
      e.preventDefault();
      var label = chip.textContent.trim();
      if (/place/i.test(label) && openAccordionByText(/where to place/i)) return;
      if (/days|works/i.test(label) && openAccordionByText(/how it works/i)) return;
      var safe = $$('h1,h2,h3,p').filter(function (h) { return /Safe Home/i.test(h.textContent); })[0];
      if (safe) safe.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
  $$('.exp-atf__reviews-link, .exp-atf__rating-link').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var r = $$('h1,h2,h3,p').filter(function (h) { return /Real Results From/i.test(h.textContent); })[0];
      if (r) { e.preventDefault(); r.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

  /* ---------- header: mobile menu ---------- */
  $$('.header__icon--menu, [class*="header-mobile-menu__toggle"], .header-burger, [aria-controls*="menu-drawer"]').forEach(function (b) {
    b.addEventListener('click', function (e) {
      var m = $('.header-mobile-menu'); if (!m) return;
      e.preventDefault(); document.body.classList.toggle('gro-menu-open');
    });
  });
})();

/* ---------- prices in the bundle box (campaign 2721, a copy of 2362) ----------
   Automatic Refills ticked: first order $22.49 / $47.97 / $64.95 (then $34.99 a pack; the terms are on the checkout).
   Unticked: one-time $34.99 / $69.99 / $104.95. Compare-at is the pack's regular price, $49.99 each.
   LADDER holds the lines of the offer-ladder cards for both states (price, % OFF, Save $, price per pouch), computed
   by build_replica.mjs from replica/prices.json, which build_replica.py checks against the checkout. The ticked
   state is already in the HTML, so the first paint needs no script. */
(function () {
  var PRICES = @@PRICES@@;
  var LADDER = @@LADDER@@;
  var refill = document.querySelector('[data-gro-refill]');
  if (!refill) return;
  function paint() {
    var on = refill.getAttribute('aria-checked') === 'true';
    document.querySelectorAll('[data-gro-bundle]').forEach(function (bar) {
      var id = bar.dataset.groBundle, p = PRICES[id], row = LADDER[id]; if (!p || !row) return;
      var v = on ? p.sub : p.one, side = on ? row.sub : row.one;
      var set = function (sel, text) { var e = bar.querySelector(sel); if (e) e.textContent = text; };
      // the card the shopper sees
      set('.exp-ol-price', side.price); set('.exp-ol-compare', row.full); set('.exp-ol-pill', side.off); set('.exp-ol-save', side.save); set('.exp-ol-each', side.each);
      // the bar's own (hidden) lines, kept in step
      set('.kaching-bundles__bar-price .money', v[0]); set('.kaching-bundles__bar-full-price .money', p.full); set('.kaching-bundles__bar-subtitle', v[1]);
    });
  }
  new MutationObserver(paint).observe(refill, { attributes: true, attributeFilter: ['aria-checked'] });
  paint();
})();
