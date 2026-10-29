/* The Adaptive Peptide Foundation funnel: the listicle's and sales page's own behaviour (the SDK owns cart, checkout and
   offers). As the stick funnel's sf-funnel.js, for a one-time purchase:
   - videos marked data-sf-lazy play only while on screen (they load nothing until then), and not at all when the
     device asks for reduced motion (then they show their controls); a clip marked data-sf-sound keeps its controls
     and never autoplays (it has a voice); the clip cards play on a tap
   - the sales page: the pack choice (every checkout link opens the checkout on that pack; the price, the saving, the
     button and the sticky bar follow it), the gallery thumbnails, and the sticky bar on phones once the buy button
     scrolls away */
(function () {
  'use strict';

  var videos = document.querySelectorAll('video[data-sf-lazy]');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (still) Array.prototype.forEach.call(videos, function (v) { v.controls = true; });
  // a clip the page autoplays itself (the brush offer's loop, upsell/video.html): for anyone who asks their device
  // for less motion it waits for a tap instead, with its controls
  if (still) Array.prototype.forEach.call(document.querySelectorAll('video[autoplay]:not([data-sf-lazy])'), function (v) {
    v.removeAttribute('autoplay'); v.controls = true; try { v.pause(); } catch (e) {}
  });
  if (videos.length && !still && 'IntersectionObserver' in window) {
    var vo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } else { v.pause(); }
      });
    }, { rootMargin: '200px 0px' });
    Array.prototype.forEach.call(videos, function (v) { vo.observe(v); });
  }
  // a clip with a voice: loads its first seconds when it comes near, plays on her tap
  Array.prototype.forEach.call(document.querySelectorAll('video[data-sf-sound]'), function (v) {
    v.controls = true;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries, obs) {
        if (entries[0].isIntersecting) { v.preload = 'metadata'; obs.disconnect(); }
      }, { rootMargin: '300px 0px' }).observe(v);
    }
  });

  // the clip cards (_includes/sf-vrow.html): a tap plays the clip where it stands, one at a time; the one with a voice
  // gets its controls and sound, a silent one pauses on a second tap
  var cards = document.querySelectorAll('[data-sf-vcard]');
  Array.prototype.forEach.call(cards, function (card) {
    var v = card.querySelector('video'), btn = card.querySelector('.sf-vcard__play');
    var sound = card.hasAttribute('data-sf-vcard-sound');
    btn.addEventListener('click', function () {
      Array.prototype.forEach.call(cards, function (o) { if (o !== card) { var ov = o.querySelector('video'); if (!ov.paused) ov.pause(); } });
      if (sound) { v.controls = true; v.muted = false; }
      card.classList.add('is-playing');
      var p = v.play(); if (p && p.catch) p.catch(function () { card.classList.remove('is-playing'); });
    });
    if (!sound) v.addEventListener('click', function () { v.pause(); });
    v.addEventListener('pause', function () { if (!sound || v.ended) card.classList.remove('is-playing'); });
    v.addEventListener('ended', function () { card.classList.remove('is-playing'); });
  });

  var gallery = document.querySelector('[data-sf-gallery]');
  if (gallery) {
    var track = gallery.querySelector('.sf-gallery__track');
    var thumbs = gallery.querySelectorAll('.sf-gallery__thumbs button');
    var mark = function (i) { Array.prototype.forEach.call(thumbs, function (b, k) { b.setAttribute('aria-current', k === i ? 'true' : 'false'); }); };
    Array.prototype.forEach.call(thumbs, function (b, i) {
      b.addEventListener('click', function () { track.scrollTo({ left: i * track.clientWidth, behavior: 'smooth' }); mark(i); });
    });
    var t;
    track.addEventListener('scroll', function () {
      clearTimeout(t);
      t = setTimeout(function () { mark(Math.round(track.scrollLeft / Math.max(1, track.clientWidth))); }, 80);
    }, { passive: true });
  }

  // the pack choice: every picker on the page (the offer near the top and the one at the end) shows the same pack
  var pickers = document.querySelectorAll('[data-sf-packs]');
  if (pickers.length) {
    var set = function (sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); };
    var sync = function (id) {
      var card = document.querySelector('.sf-pack[data-pack="' + id + '"]');
      if (!card) return;
      var price = card.getAttribute('data-price'), compare = card.getAttribute('data-compare'), save = card.getAttribute('data-save');
      Array.prototype.forEach.call(document.querySelectorAll('.sf-pack'), function (c) {
        var on = c.getAttribute('data-pack') === id;
        c.classList.toggle('is-on', on);
        var input = c.querySelector('input'); if (input) input.checked = on;
      });
      set('[data-sf-cta]', function (a) { a.href = a.href.replace(/forceBundleId=[^&#]*/, 'forceBundleId=' + id); });
      set('[data-sf-price]', function (e) { e.textContent = price; });
      set('[data-sf-compare]', function (e) { e.textContent = compare; });
      set('[data-sf-save]', function (e) { e.textContent = save; });
      set('[data-sf-label]', function (e) { e.textContent = card.getAttribute('data-label'); });
      set('[data-sf-btn-price]', function (e) { e.textContent = '| ' + price; });
      set('[data-sf-sticky-pack]', function (e) { e.textContent = card.getAttribute('data-short'); });
      set('[data-sf-sticky-price]', function (e) { e.textContent = price + ' · one-time · free shipping'; });
    };
    Array.prototype.forEach.call(pickers, function (p) {
      p.addEventListener('change', function (e) {
        var input = e.target; if (input && input.name === 'sf_pack') sync(input.value);
      });
    });
    // the pack the URL names comes first (the listicle's launch offer is the 3-bottle pack: ?pack=apf-3), then the page's own
    var asked = (new URLSearchParams(location.search).get('pack') || '').replace(/[^a-z0-9-]/g, '');
    var wanted = asked && document.querySelector('.sf-pack input[name=sf_pack][value="' + asked + '"]');
    var first = wanted || document.querySelector('.sf-pack input[name=sf_pack]:checked') || document.querySelector('.sf-pack input[name=sf_pack]');
    if (first) sync(first.value);
  }

  // the sticky bar on phones: on once the buy button has scrolled above the viewport, off again when it is back below
  // or in view. Read on every scroll (an observer alone misses a jump from far below to the top: the button is out
  // of view both times, so nothing intersects and the bar stayed on, funnel review 2).
  var sticky = document.querySelector('[data-sf-sticky]');
  var buyBtn = document.querySelector('[data-sf-sticky-anchor]');
  // Off only while the pack chooser or its own button is on screen (not over them, live review 4), so the value
  // list beside them keeps a way to buy (live review 6: three screens with nothing to tap).
  var chooser = document.querySelector('[data-sf-packs]');
  var packBtn = document.querySelector('.sf-offerbox .sf-buy__btn');
  var inView = function (el) { if (!el) return false; var r = el.getBoundingClientRect(); return r.top < window.innerHeight && r.bottom > 0; };
  if (sticky && buyBtn) {
    var ticking = false;
    var place = function () {
      ticking = false;
      var on = buyBtn.getBoundingClientRect().bottom < 0;
      if (on && (inView(chooser) || inView(packBtn))) on = false;
      sticky.classList.toggle('is-on', on);
      document.body.classList.toggle('sf-has-sticky', on);     // room for the footer's last line under the bar
    };
    var ask = function () { if (!ticking) { ticking = true; requestAnimationFrame(place); } };
    window.addEventListener('scroll', ask, { passive: true });
    window.addEventListener('resize', ask);
    place();
  }
})();

// The checkout buttons ([data-sf-cta]): the pack they name is reported as an add to cart first (next.trackAddToCart: the
// SDK's own tracking call, which pushes its dl_add_to_cart, the add_to_cart the ad pixels read, and leaves the cart
// alone), then the link is followed and the checkout builds the cart from the pack its forceBundleId names. Never a
// cart add here: the checkout's pack selector keeps every line it did not add itself, so a pack put in the cart on this
// page would be bought twice. The link wins whenever the event cannot go first: the SDK not ready, a click that opens
// a new tab, an error, or 1.2 s.
(function () {
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[data-sf-cta]') : null;
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var sdk = window.next;
    if (!sdk || typeof sdk.trackAddToCart !== 'function') return;
    var m = /forceBundleId=([^&#]+)/.exec(a.href);
    var card = m && document.querySelector('.sf-pack[data-pack="' + m[1] + '"]');
    var pkg = card ? parseInt(card.getAttribute('data-package'), 10) : NaN;
    if (!pkg) return;
    e.preventDefault();
    var href = a.href, gone = false;
    var go = function () { if (!gone) { gone = true; window.location.href = href; } };
    setTimeout(go, 1200);
    var from = (window.NextDataLayer || []).length;
    Promise.resolve(sdk.trackAddToCart(pkg, 1))
      .then(function () {
        (function wait(n) {                                  // the SDK pushes dl_add_to_cart a microtask later
          var l = window.NextDataLayer || [];
          for (var i = from; i < l.length; i++) if (l[i] && l[i].event === 'dl_add_to_cart') { setTimeout(go, 200); return; }
          if (n > 0) setTimeout(function () { wait(n - 1); }, 25); else go();
        })(40);
      })
      .catch(go);
  }, true);
})();

// A link that lands on a section (the listicle's ?pack=apf-3#offer) stays on it while the page above settles: the
// browser scrolls to the anchor before the photos and fonts above it are in, so the section slid ~840 px away and
// jumped back about a second later (live review 5). Until she touches, scrolls or presses a key, every layout change
// until 1.5 s after the page has loaded (6 s at most) puts the section back at the top, without an animation.
(function keepAnchor() {
  var id = decodeURIComponent((location.hash || '').slice(1));
  var el = id && document.getElementById(id);
  if (!el || !('ResizeObserver' in window)) return;
  var done = false, stop = function () { done = true; ro.disconnect(); };
  var fix = function () {
    if (done) return;
    var y = el.getBoundingClientRect().top + window.scrollY - (parseFloat(getComputedStyle(el).scrollMarginTop) || 0);
    if (Math.abs(window.scrollY - y) > 2) window.scrollTo({ top: y, behavior: 'instant' });
  };
  var ro = new ResizeObserver(fix);
  ro.observe(document.body);
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (t) { window.addEventListener(t, stop, { passive: true, once: true }); });
  window.addEventListener('load', function () { fix(); setTimeout(stop, 1500); });
  setTimeout(stop, 6000);
})();
