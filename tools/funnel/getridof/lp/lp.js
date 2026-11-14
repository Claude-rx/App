/* Get Rid Of — lean sales page runtime (no dependencies). Inlined by build_lp.py.
 * Buy box: bundle (buy1 / buy3 / buy5) + "Subscribe & save" tick (on by default, optional).
 *   subscribed -> /mouse-pouches/checkout/?forceBundleId=main:buy1|buy3|buy5   (campaign packages 2 / 5 / 6)
 *   one-time   -> /mouse-pouches/checkout/?forceBundleId=main:ot1|ot3|ot5      (campaign package 1 x 1 / 3 / 5)
 * Prices are the campaign's (Cart API calculate, 14 Nov 2026); polish_checks.cjs fails if they drift from the checkout.
 * Events: AppLovin Axon (page_view, view_item, add_to_cart) + funnel steps on window.dataLayer / Clarity (groTrack). */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var T = {
    buy1: { n: 'Buy 1', packs: 1, was: 49.99, sub: 22.49, one: 24.99, renew: '1 pack ($34.99) every 30 days', v: { sub: '8', one: '7' } },
    buy3: { n: 'Buy 2, Get 1 Free', packs: 3, was: 149.97, sub: 47.97, one: 49.98, renew: '3 packs ($104.97) every 90 days', v: { sub: '37', one: '7' } },
    buy5: { n: 'Buy 3, Get 2 Free', packs: 5, was: 249.95, sub: 64.95, one: 69.95, renew: '5 packs ($174.95) every 150 days', v: { sub: '38', one: '7' } }
  };
  var state = { bundle: 'buy3', sub: true };
  var money = function (n) { return '$' + n.toFixed(2); };
  var price = function (id) { return T[id][state.sub ? 'sub' : 'one']; };

  /* ---------- funnel events (dataLayer + Microsoft Clarity when configured) ---------- */
  window.dataLayer = window.dataLayer || [];
  var sent = {};
  function track(name, props, once) {
    if (once) { if (sent[name]) return; sent[name] = 1; }
    try {
      var e = { event: 'gro_' + name, gro_bundle: state.bundle, gro_sub: state.sub };
      for (var k in props || {}) e['gro_' + k] = props[k];
      window.dataLayer.push(e);
      if (typeof window.clarity === 'function') window.clarity('event', 'gro_' + name);
      if (typeof window.gtag === 'function') window.gtag('event', 'gro_' + name, props || {});
    } catch (err) { /* never block the page */ }
  }
  window.groTrack = track;

  /* ---------- buy box ---------- */
  var opts = $$('[data-gro-bundle]');
  var subEl = $('[data-gro-sub]');
  function paint() {
    opts.forEach(function (o) {
      var id = o.getAttribute('data-gro-bundle'), t = T[id], p = price(id), on = id === state.bundle;
      o.classList.toggle('on', on);
      var r = $('input', o); if (r) r.checked = on;
      $('[data-p]', o).textContent = money(p);
      $('[data-pp]', o).textContent = money(p / (t.packs * 12)) + '/pouch';
      $('[data-off]', o).textContent = Math.round((1 - p / t.was) * 100) + '% OFF';
    });
    var t = T[state.bundle], p = price(state.bundle);
    $$('[data-total]').forEach(function (e) { e.textContent = money(p); });
    $$('[data-sb-name]').forEach(function (e) { e.textContent = t.n; });
    var was = $('[data-sb-was]'); if (was) was.textContent = money(t.was);
    var title = $('[data-sub-title]'), terms = $('[data-sub-terms]');
    if (title) title.textContent = state.sub ? 'Subscribe & save: pay ' + money(t.sub) + ' today' : 'Subscribe & save ' + money(t.one - t.sub) + ' on this order';
    if (terms) terms.textContent = state.sub
      ? 'Then ' + t.renew + ' at $34.99 a pack, free shipping. Skip or cancel anytime. Untick for a one-time purchase (' + money(t.one) + ').'
      : 'One-time purchase: ' + money(t.one) + ', no refills. Tick to pay ' + money(t.sub) + ' today, then ' + t.renew + '. Skip or cancel anytime.';
    if (subEl) subEl.checked = state.sub;
  }
  function pick(id, why) { if (!T[id] || id === state.bundle) return; state.bundle = id; paint(); track('bundle_select', { src: why || 'card' }); }
  opts.forEach(function (o) {
    o.addEventListener('click', function (e) { e.preventDefault(); pick(o.getAttribute('data-gro-bundle')); });
  });
  if (subEl) subEl.addEventListener('change', function () { state.sub = subEl.checked; paint(); track('sub_toggle', { on: state.sub }); });
  paint();

  function bundleId() { return state.sub ? state.bundle : 'ot' + T[state.bundle].packs; }
  function checkoutUrl() {
    var q = new URLSearchParams(location.search);
    q.delete('forceBundleId'); q.delete('forcePackageId');
    q.set('forceBundleId', 'main:' + bundleId());
    return '/mouse-pouches/checkout/' + '?' + q.toString();
  }
  window.groCheckoutUrl = checkoutUrl;
  window.groState = state;

  /* ---------- AppLovin Axon: same item shape as axon.adapter.js on the checkout ---------- */
  function axonPayload() {
    var t = T[state.bundle], p = price(state.bundle), unit = Math.round(p / t.packs * 100) / 100;
    var item = { item_id: 'cdkh', item_name: 'Mouse Repellent Pouches', item_variant_id: t.v[state.sub ? 'sub' : 'one'], item_brand: 'Get Rid Of',
                 item_category_id: 7137, price: unit, quantity: t.packs, discount: Math.round((49.99 - unit) * 100) / 100 };
    if (window.__axonImageUrl) item.image_url = window.__axonImageUrl;
    return { currency: 'USD', value: p, items: [item] };
  }
  function axon(name, data) {
    try { if (typeof window.axon === 'function') data ? window.axon('track', name, data) : window.axon('track', name); } catch (err) { /* never block the page */ }
  }
  window.groAxonPayload = axonPayload;
  axon('page_view'); axon('view_item', axonPayload());
  track('lp_view', { ref: document.referrer ? 'yes' : 'no' }, true);

  /* ---------- clicks: add to cart, pack picks, scroll links ---------- */
  var leaving = false;
  /* ---------- video reviews: the file loads only when its card is tapped ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-gro-video]') : null;
    if (!b) return;
    var v = document.createElement('video');
    v.src = b.getAttribute('data-gro-video'); v.controls = true; v.autoplay = true; v.playsInline = true; v.setAttribute('playsinline', '');
    var poster = b.querySelector('img'); if (poster) v.poster = poster.currentSrc || poster.src;
    b.innerHTML = ''; b.appendChild(v); b.removeAttribute('data-gro-video');
    track('video_play', { n: b.getAttribute('data-n') || '' });
  });
  var hcx = $('[data-gro-hc-x]'); if (hcx) hcx.addEventListener('click', function () { var hc = $('[data-gro-hc]'); hc.hidden = true; hc.parentNode.classList.add('nohc'); track('formula_badge_close'); });
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-gro-pick],[data-gro-atc],[data-gro-scroll]') : null;
    if (!t) return;
    if (t.hasAttribute('data-gro-pick')) pick(t.getAttribute('data-gro-pick'), 'guide');
    if (t.hasAttribute('data-gro-atc')) {
      e.preventDefault();
      if (leaving) return; leaving = true;
      t.classList.add('is-busy');
      var url = checkoutUrl();
      axon('add_to_cart', axonPayload());
      track('add_to_cart', { src: t.getAttribute('data-gro-src') || 'cta', value: price(state.bundle) });
      setTimeout(function () { location.href = url; }, window.axon ? 250 : 0);   // let the pixel send before leaving
      setTimeout(function () { leaving = false; t.classList.remove('is-busy'); }, 4000);   // back button / bfcache
      return;
    }
    if (t.hasAttribute('data-gro-pick') || t.hasAttribute('data-gro-scroll')) {
      e.preventDefault();
      var box = document.getElementById('gro-buy'); if (box) box.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
  window.addEventListener('pageshow', function () { leaving = false; $$('.is-busy').forEach(function (b) { b.classList.remove('is-busy'); }); });

  /* ---------- sticky bar: hidden while the buy box button is on screen ---------- */
  var bar = $('[data-gro-sticky]'), mainBtn = $('#gro-buy [data-gro-atc]');
  if (bar && mainBtn && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (en) { bar.classList.toggle('off', en.isIntersecting); if (en.isIntersecting) track('buybox_view', null, true); });
    }, { threshold: 0.6 }).observe(mainBtn);
  }

  /* ---------- gallery dots + sharper first image on wide screens ---------- */
  var gal = $('[data-gro-gallery]');
  if (gal) {
    var dots = $$('.gal__d i'), tick = 0;
    gal.addEventListener('scroll', function () {
      if (tick) return; tick = 1;
      requestAnimationFrame(function () {
        tick = 0; var i = Math.round(gal.scrollLeft / gal.clientWidth);
        dots.forEach(function (d, n) { d.classList.toggle('on', n === i); });
        if (i > 0) track('gallery_swipe', null, true);
      });
    }, { passive: true });
    var go = function (i) { i = Math.max(0, Math.min(dots.length - 1, i)); gal.scrollTo({ left: i * gal.clientWidth, behavior: 'smooth' }); };
    dots.forEach(function (d, n) { d.addEventListener('click', function () { go(n); }); });
    $$('[data-gro-gal]').forEach(function (b) { b.addEventListener('click', function () { go(Math.round(gal.scrollLeft / gal.clientWidth) + Number(b.getAttribute('data-gro-gal'))); }); });
    var first = $('img[data-hd]', gal);
    if (first && (window.devicePixelRatio > 1.4 || innerWidth > 700)) {
      var swap = function () { var im = new Image(); im.onload = function () { first.src = im.src; }; im.src = first.getAttribute('data-hd'); };
      if (document.readyState === 'complete') setTimeout(swap, 300); else window.addEventListener('load', function () { setTimeout(swap, 300); });
    }
  }
  /* ---------- tabs (reviews by customer type, week-by-week timeline) ---------- */
  $$('[data-gro-tabs]').forEach(function (bar) {
    var btns = $$('button', bar), scope = bar.parentNode;
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (x) { x.classList.toggle('on', x === b); });
        $$('[data-pane]', scope).forEach(function (pn) { pn.hidden = pn.getAttribute('data-pane') !== b.getAttribute('data-tab'); });
        track('tab_' + bar.getAttribute('data-gro-tabs'), { tab: b.getAttribute('data-tab') });
      });
    });
  });
  var revs = $('.revs'); if (revs) revs.addEventListener('scroll', function () { track('reviews_swipe', null, true); }, { passive: true });
  $$('.faq details').forEach(function (d) { d.addEventListener('toggle', function () { if (d.open) track('faq_open', { q: ($('summary', d).textContent || '').slice(0, 40) }); }); });

  /* ---------- customer photo strip: an endless left-scrolling row (40 px a second, pauses under the finger or pointer) ----------
     The page ships the four photos once. When the strip is about to scroll into view they are copied five more times
     (same files, so nothing new downloads) and the row slides by exactly one copy, which makes the loop seamless. */
  var mq = $('[data-gro-mq]');
  if (mq && 'IntersectionObserver' in window && !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) {
    var mqo = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      mqo.disconnect();
      var row = $('.ugc__t', mq), set = $$('img', row), ready = 0;
      var go = function () {
        for (var k = 0; k < 5; k++) set.forEach(function (im) { var c = im.cloneNode(false); c.removeAttribute('loading'); c.alt = ''; c.setAttribute('aria-hidden', 'true'); row.appendChild(c); });
        mq.classList.add('on');
      };
      var one = function () { if (++ready === set.length) go(); };
      set.forEach(function (im) { im.loading = 'eager'; if (im.complete) one(); else { im.addEventListener('load', one); im.addEventListener('error', one); } });
    }, { rootMargin: '600px 0px' });
    mqo.observe(mq);
  }

  /* ---------- sections fade up as they scroll into view ---------- */
  if ('IntersectionObserver' in window && !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) (window.requestIdleCallback || function (f) { setTimeout(f, 300); })(function () {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.tile, .stepi li, .card, .fam figure, .baps figure, .ba figure, .agi div, .pack, .rev').forEach(function (el, n) {
      if (el.getBoundingClientRect().top < innerHeight) return;   // already on screen: leave it visible
      el.classList.add('rv'); el.style.transitionDelay = (n % 3) * 70 + 'ms'; io.observe(el);
    });
  });   // set up when the browser is idle: it measures every card, which must not delay the first paint

  /* ---------- scroll depth ---------- */
  var marks = [25, 50, 75, 100], st = 0;
  window.addEventListener('scroll', function () {
    if (st) return; st = 1;
    setTimeout(function () {
      st = 0; var h = document.documentElement.scrollHeight - innerHeight; if (h <= 0) return;
      var pct = (scrollY / h) * 100;
      while (marks.length && pct >= marks[0] - 1) track('scroll_' + marks.shift(), null, true);
    }, 250);
  }, { passive: true });

  /* ---------- Black Friday deadline (a real date; the block hides itself once it has passed) ---------- */
  $$('[data-gro-deadline]').forEach(function (box) {
    var end = new Date(box.getAttribute('data-gro-deadline')).getTime();
    var u = {}; $$('[data-u]', box).forEach(function (e) { u[e.getAttribute('data-u')] = e; });
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    (function tickDl() {
      var s = Math.floor((end - Date.now()) / 1000);
      if (s <= 0) { box.style.display = 'none'; return; }
      var v = { d: Math.floor(s / 86400), h: Math.floor(s % 86400 / 3600), m: Math.floor(s % 3600 / 60), s: s % 60 };
      for (var k in v) if (u[k]) u[k].textContent = pad(v[k]);
      setTimeout(tickDl, 1000);
    })();
  });
})();
