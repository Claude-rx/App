/* Get Rid Of — Mouse Pouches PDP runtime (no dependencies).
 * The page is a static snapshot of a GemPages/Shopify product page; this file brings back the interactions its
 * own scripts provided and connects the buy box to the Campaigns App funnel:
 *   bundle bars + refill toggle -> ADD TO CART -> /mouse-pouches/checkout[-refill]/?forceBundleId=main:<bundle>
 *   accordions, tabs, product gallery (thumbs, dots, swipe), review carousels (swipe on phones),
 *   "Order within" countdown, info chips.
 * Built into the page by tools/funnel/getridof/build_pdp.mjs. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var CHECKOUT = { one: '/mouse-pouches/checkout/', refill: '/mouse-pouches/checkout/' };   // subscription-only: one checkout

  /* ---------- buy box ---------- */
  var bars = $$('[data-gro-bundle]');
  var refillEl = $('[data-gro-refill]');
  var state = {
    bundle: (bars.filter(function (b) { return b.classList.contains('kaching-bundles__bar--selected'); })[0] || bars[1] || bars[0] || { dataset: {} }).dataset.groBundle || 'buy3',
    refill: refillEl ? refillEl.getAttribute('aria-checked') === 'true' : false
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
  var SUBSCRIPTION_ONLY = true;   // every order is the subscription: the box stays ticked and is not a toggle
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
    q.set('forceBundleId', 'main:' + state.bundle);
    return (state.refill ? CHECKOUT.refill : CHECKOUT.one) + '?' + q.toString();
  }
  window.groCheckoutUrl = checkoutUrl;
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-gro-atc]');
    if (!t) return;
    e.preventDefault(); e.stopPropagation();
    location.href = checkoutUrl();
  }, true);
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
      panels.forEach(function (p, k) { p.style.display = k === i ? 'block' : 'none'; });
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
  var thumbs = $('gp-carousel-v3.carousel-gallery');
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
      wrap.style.transform = 'translate3d(' + (-cur * w) + 'px,0,0)';
      dots.forEach(function (d, k) { d.setAttribute('aria-current', k === cur ? 'true' : 'false'); });
      if (thumbs) $$('.gem-slider-item', thumbs).forEach(function (t, k) { t.classList.toggle('gro-thumb-active', k === cur); });
    };
    if (thumbs) $$('.gem-slider-item', thumbs).forEach(function (t, k) { t.addEventListener('click', function () { go(k); }); });
    dots.forEach(function (d, k) { d.addEventListener('click', function (e) { e.preventDefault(); go(k); }); });
    $$('.gp-carousel-action-back', feat).forEach(function (b) { b.addEventListener('click', function () { go(cur - 1); }); });
    $$('.gp-carousel-action-next', feat).forEach(function (b) { b.addEventListener('click', function () { go(cur + 1); }); });
    var x0 = null;
    feat.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    feat.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) go(cur + (dx < 0 ? 1 : -1)); x0 = null; });
    window.addEventListener('resize', function () { go(cur); });
    go(0);
  }

  /* ---------- other carousels: drop loop clones; swipeable scroller on phones ---------- */
  $$('gp-carousel-v3').forEach(function (c) {
    if (c === feat || c === thumbs) return;
    var wrap = $('.gem-slider-wrapper', c); if (!wrap) return;
    var seen = {};
    Array.prototype.slice.call(wrap.children).forEach(function (s) {
      var k = s.getAttribute('data-index'); if (k === null || k === '') return;
      if (seen[k]) s.remove(); else seen[k] = 1;
    });
    c.classList.add('gro-carousel');
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

/* ---------- long-sales-page sections: real-deadline countdown + offer buttons that pick a bundle ---------- */
(function () {
  document.querySelectorAll('[data-gro-deadline]').forEach(function (box) {
    var end = new Date(box.getAttribute('data-gro-deadline')).getTime();
    var set = function (u, v) { var el = box.querySelector('[data-u="' + u + '"]'); if (el) el.textContent = (v < 10 ? '0' : '') + v; };
    var tick = function () {
      var s = Math.floor((end - Date.now()) / 1000);
      if (s <= 0) { box.style.display = 'none'; return false; }   // real deadline: gone once it has passed
      set('d', Math.floor(s / 86400)); set('h', Math.floor(s % 86400 / 3600)); set('m', Math.floor(s % 3600 / 60)); set('s', s % 60);
      return true;
    };
    if (tick()) var t = setInterval(function () { if (!tick()) clearInterval(t); }, 1000);
  });
  // an offer button may name the bundle it sells (data-gro-bundle-pick); window capture runs before the shared ATC
  // handler (document capture), so the bundle is selected before the checkout URL is built
  window.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-gro-bundle-pick]');
    if (!b) return;
    var bar = document.querySelector('[data-gro-bundle="' + b.getAttribute('data-gro-bundle-pick') + '"]');
    if (bar) bar.click();
  }, true);
})();

/* ---------- subscription pricing in the bundle box (campaign 2362: sub-1/sub-3/sub-5 offers) ----------
   Refills ticked: first order 50% off ($24.99 / $47.97 / $64.95), then $34.99 a pack every 60 days.
   Unticked: one-time prices ($29.99 / $55.98 / $74.95). Compare-at stays the page's ($89 / $178 / $267). */
(function () {
  var PRICES = { buy1: { one: ['$29.99', '66% OFF'], sub: ['$24.99', '72% OFF'] },
                 buy3: { one: ['$55.98', '69% OFF'], sub: ['$47.97', '73% OFF'] },
                 buy5: { one: ['$74.95', '72% OFF'], sub: ['$64.95', '76% OFF'] } };
  var refill = document.querySelector('[data-gro-refill]');
  if (!refill) return;
  var title = refill.querySelector('.kaching-bundles__subscriptions__title');
  var sub = refill.querySelector('.kaching-bundles__subscriptions__subtitle');
  if (title) title.textContent = 'Subscribe & get 50% off your first order';
  if (sub) sub.textContent = 'Then $34.99 a pack every 60 days · Cancel anytime';
  // subscription details under the ADD TO CART button (shown while refills are ticked)
  var atc = document.querySelector('#gro-buy') && document.querySelector('[data-gro-atc]');
  var info = document.createElement('div');
  info.className = 'gro-subinfo';
  info.innerHTML = '<p class="gro-subinfo__line">First order 50% off · then <b>$34.99 a pack every 60 days</b></p>' +
    '<div class="gro-subinfo__row"><span><i>↻</i>Renews every 60 days</span><span><i>✕</i>Cancel anytime</span><span><i>✓</i>30-day money-back</span></div>';
  var box = document.getElementById('gro-buy');
  if (box) box.parentNode.insertBefore(info, box.nextSibling);
  function paint() {
    var on = refill.getAttribute('aria-checked') === 'true';
    document.querySelectorAll('[data-gro-bundle]').forEach(function (bar) {
      var p = PRICES[bar.dataset.groBundle]; if (!p) return;
      var v = on ? p.sub : p.one;
      var price = bar.querySelector('.kaching-bundles__bar-price .money'); if (price) price.textContent = v[0];
      var off = bar.querySelector('.kaching-bundles__bar-subtitle'); if (off) off.textContent = v[1];
    });
    info.style.display = on ? '' : 'none';
  }
  new MutationObserver(paint).observe(refill, { attributes: true, attributeFilter: ['aria-checked'] });
  paint();
})();
