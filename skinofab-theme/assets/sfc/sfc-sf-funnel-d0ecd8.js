/* SKINOFAB funnel: the listicle's and product page's own behaviour (the SDK owns cart, checkout and offers).
   - videos marked data-sf-lazy play only while on screen (they load nothing until then), and not at all when the
     device asks for reduced motion (then they show their controls)
   - the product page: gallery thumbnails, the pack choice (the checkout links open the checkout on that pack, and the
     price, refill row and terms follow it), and the sticky bar on phones once the buy button scrolls away */
(function () {
  'use strict';

  var videos = document.querySelectorAll('video[data-sf-lazy]');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // asked for less motion: no autoplay, the player's own controls instead (its poster shows until she taps play)
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

  var packs = document.querySelector('[data-sf-packs]');
  if (packs) {
    var set = function (sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); };
    var sync = function () {
      var input = packs.querySelector('input[name=sf_pack]:checked');
      if (!input) return;
      var card = input.closest('.sf-pack');
      var id = card.getAttribute('data-pack'), price = card.getAttribute('data-price');
      var every = card.getAttribute('data-every'), compare = card.getAttribute('data-compare');
      Array.prototype.forEach.call(packs.querySelectorAll('.sf-pack'), function (c) { c.classList.toggle('is-on', c === card); });
      set('[data-sf-cta]', function (a) { a.href = a.href.replace(/forceBundleId=[^&#]*/, 'forceBundleId=' + id); });
      set('[data-sf-price]', function (e) { e.textContent = price; });
      set('[data-sf-compare]', function (e) { e.textContent = compare; });
      set('[data-sf-label]', function (e) { e.textContent = card.getAttribute('data-label'); });
      set('[data-sf-btn-price]', function (e) { e.textContent = '| ' + price; });
      set('[data-sf-renew]', function (e) { e.textContent = 'Renews at ' + price + ' every ' + every + ' days'; });
      set('[data-sf-terms]', function (e) {
        e.textContent = 'You pay ' + price + ' today, then ' + price + ' every ' + every + ' days until you cancel. We email you ' +
          'before every refill. To skip or cancel, just email hello@skinofab.com: a person replies within one business day. ' +
          'No minimum, no fees.';
      });
      set('[data-sf-sticky-pack]', function (e) { e.textContent = id === 'stick-2' ? '2 sticks + free brush' : '1 stick'; });
      set('[data-sf-sticky-price]', function (e) { e.textContent = price + ' · every ' + every + ' days'; });
    };
    packs.addEventListener('change', sync);
    sync();
  }

  var sticky = document.querySelector('[data-sf-sticky]');
  var buyBtn = document.querySelector('.sf-buy__btn');
  if (sticky && buyBtn && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var e = entries[0];
      sticky.classList.toggle('is-on', !e.isIntersecting && e.boundingClientRect.top < 0);
    }).observe(buyBtn);
  }
})();
