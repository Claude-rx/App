/* The Adaptive Peptide Foundation funnel: the listicle's and sales page's own behaviour (the SDK owns cart, checkout and
   offers). As the stick funnel's sf-funnel.js, for a one-time purchase:
   - videos marked data-sf-lazy play only while on screen (they load nothing until then), and not at all when the
     device asks for reduced motion (then they show their controls); a clip marked data-sf-sound keeps its controls
     and never autoplays (it has a voice)
   - the sales page: the pack choice (every checkout link opens the checkout on that pack; the price, the saving, the
     button and the sticky bar follow it), the gallery thumbnails, and the sticky bar on phones once the buy button
     scrolls away */
(function () {
  'use strict';

  var videos = document.querySelectorAll('video[data-sf-lazy]');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (still) Array.prototype.forEach.call(videos, function (v) { v.controls = true; });
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
    var first = document.querySelector('.sf-pack input[name=sf_pack]:checked') || document.querySelector('.sf-pack input[name=sf_pack]');
    if (first) sync(first.value);
  }

  var sticky = document.querySelector('[data-sf-sticky]');
  var buyBtn = document.querySelector('[data-sf-sticky-anchor]');
  if (sticky && buyBtn && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var e = entries[0];
      sticky.classList.toggle('is-on', !e.isIntersecting && e.boundingClientRect.top < 0);
    }).observe(buyBtn);
  }
})();
