/* The Adaptive Peptide Foundation funnel: the listicle's and sales page's own behaviour (the SDK owns cart, checkout and
   offers). As the stick funnel's sf-funnel.js:
   - videos marked data-sf-lazy play only while on screen (they load nothing until then), and not at all when the
     device asks for reduced motion (then they show their controls); a clip marked data-sf-sound keeps its controls
     and never autoplays (it has a voice); the clip cards play on a tap
   - the sales page: the pack choice (every checkout link opens the checkout on that pack; the price, what it renews
     at, the button and the sticky bar follow it), the gallery thumbnails, and the sticky bar on phones once the buy button
     scrolls away */
(function () {
  'use strict';

  // the posters of videos down the page wait until a video comes within about a screen: loaded at once they took the
  // phone's bandwidth from the hero picture (live review 10); a lazy loop loads its first seconds then too
  var near = document.querySelectorAll('video[data-sf-poster]');
  var wake = function (v) { if (!v.getAttribute('poster')) v.setAttribute('poster', v.getAttribute('data-sf-poster')); if (v.hasAttribute('data-sf-lazy') && v.preload === 'none') v.preload = 'metadata'; };
  if ('IntersectionObserver' in window) {
    var po = new IntersectionObserver(function (entries) { entries.forEach(function (e) { if (e.isIntersecting) { wake(e.target); po.unobserve(e.target); } }); }, { rootMargin: '900px 0px' });
    Array.prototype.forEach.call(near, function (v) { po.observe(v); });
  } else Array.prototype.forEach.call(near, wake);

  var videos = document.querySelectorAll('video[data-sf-lazy]');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // (the lazy loops no longer carry autoplay, live review 10; any that still does is stopped here, live review 8)
  if (still) Array.prototype.forEach.call(videos, function (v) { v.removeAttribute('autoplay'); v.controls = true; try { v.pause(); } catch (e) {} });
  // a clip the page autoplays itself (the brush offer's loop, upsell/video.html): for anyone who asks their device
  // for less motion it waits for a tap instead, with its controls
  if (still) Array.prototype.forEach.call(document.querySelectorAll('video[autoplay]:not([data-sf-lazy])'), function (v) {
    v.removeAttribute('autoplay'); v.controls = true; try { v.pause(); } catch (e) {}
  });
  if (videos.length && !still && 'IntersectionObserver' in window) {
    var vo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { if (v.sfHeld) return; var p = v.play(); if (p && p.catch) p.catch(function () {}); } else { v.pause(); }
      });
    }, { rootMargin: '200px 0px' });
    Array.prototype.forEach.call(videos, function (v) { vo.observe(v); });
  }
  // a pause button on every loop that plays by itself (motion longer than 5 s must be stoppable, WCAG 2.2.2; live review
  // 8): a loop she paused stays paused when it scrolls back into view (sfHeld)
  // Set up once the page has loaded and the phone is idle (speed pass, 5 Nov 2026): placing each button measures its
  // video, which made the browser lay out the whole long page before its first paint (178 ms on a slowed phone); the
  // loops play only when scrolled to, long after.
  var loops = document.querySelectorAll('video[data-sf-lazy], video[data-upsell-video][loop]');
  var afterLoad = function (fn) {
    var go = function () { if ('requestIdleCallback' in window) requestIdleCallback(fn, { timeout: 1500 }); else setTimeout(fn, 200); };
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go);
  };
  if (loops.length && !still) afterLoad(function () {
    var css = document.createElement('style');
    css.textContent = '.sf-vpause{position:absolute;right:10px;bottom:10px;z-index:3;width:44px;height:44px;padding:0;border:0;border-radius:50%;'
      + 'background:rgba(21,21,21,.72);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center}'
      + '.sf-vpause svg{width:16px;height:16px;fill:currentColor}.sf-vpause:focus-visible{outline:2px solid #fff;outline-offset:2px}';
    document.head.appendChild(css);
    var PAUSE = '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2" width="3.5" height="12" rx="1"/><rect x="9.5" y="2" width="3.5" height="12" rx="1"/></svg>';
    var PLAY = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9.5-5.5z"/></svg>';
    Array.prototype.forEach.call(loops, function (v) {
      var box = v.parentElement; if (!box) return;
      if (getComputedStyle(box).position === 'static') box.style.position = 'relative';
      var b = document.createElement('button'); b.type = 'button'; b.className = 'sf-vpause';
      var draw = function () { var on = !v.paused; b.setAttribute('aria-label', on ? 'Pause the video' : 'Play the video'); b.innerHTML = on ? PAUSE : PLAY; };
      b.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        if (v.paused) { v.sfHeld = false; var p = v.play(); if (p && p.catch) p.catch(function () {}); } else { v.sfHeld = true; v.pause(); }
      });
      v.addEventListener('play', draw); v.addEventListener('pause', draw);
      // on the video's own top-right corner, wherever the video sits in its card: at the card's corner it sat on a
      // caption (live review 10) and, in a two-column card, a column away from its video; at the video's bottom corner
      // it covered the clip's own burned-in label (live review 11)
      var place = function () {
        var bb = box.getBoundingClientRect(), vb = v.getBoundingClientRect();
        if (!vb.width) return;
        b.style.bottom = 'auto'; b.style.right = 'auto';
        b.style.top = Math.round(vb.top - bb.top - box.clientTop + 8) + 'px';
        // a clip whose top-right holds what it shows (the day's timeline, the dropper bottle) names its clear corner:
        // data-sf-pause-corner="tl" (live review 13, F7)
        var left = v.getAttribute('data-sf-pause-corner') === 'tl';
        b.style.left = Math.round((left ? vb.left : vb.right - 44 - 16) - bb.left - box.clientLeft + 8) + 'px';
      };
      box.appendChild(b); draw(); place();
      v.addEventListener('loadedmetadata', place);
      if ('ResizeObserver' in window) { var ro = new ResizeObserver(place); ro.observe(box); ro.observe(v); } else window.addEventListener('resize', place);
    });
  });

  // a clip with a voice: loads its first seconds when it comes near, plays on her tap
  Array.prototype.forEach.call(document.querySelectorAll('video[data-sf-sound]'), function (v) {
    v.controls = true;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries, obs) {
        if (entries[0].isIntersecting) { v.preload = 'metadata'; obs.disconnect(); }
      }, { rootMargin: '300px 0px' }).observe(v);
      new IntersectionObserver(function (entries) {                // and pauses once she scrolls away from it
        if (!entries[0].isIntersecting && !v.paused) v.pause();
      }, { threshold: 0.15 }).observe(v);
    }
  });

  // the video carousel's arrows (from 900 px): a card's width a tap, each arrow hidden at its end of the row
  document.querySelectorAll('.sf-vcar').forEach(function (car) {
    var row = car.querySelector('.sf-vrow'), prev = car.querySelector('[data-sf-vcar="-1"]'), next = car.querySelector('[data-sf-vcar="1"]');
    if (!row || !prev || !next) return;
    function ends() { prev.disabled = row.scrollLeft < 8; next.disabled = row.scrollLeft + row.clientWidth > row.scrollWidth - 8; }
    [prev, next].forEach(function (b) {
      b.addEventListener('click', function () {
        var card = row.querySelector('.sf-vcard');
        row.scrollBy({ left: (+b.getAttribute('data-sf-vcar')) * ((card ? card.offsetWidth : 250) + 12), behavior: 'smooth' });
      });
    });
    row.addEventListener('scroll', function () { window.requestAnimationFrame(ends); }, { passive: true });
    ends();
  });
  // the clip cards (_includes/sf-vrow.html): a tap plays the clip where it stands, one at a time; the one with a voice
  // gets its controls and sound, a silent one pauses on a second tap; any pauses once it is scrolled off the screen
  var cards = document.querySelectorAll('[data-sf-vcard]');
  Array.prototype.forEach.call(cards, function (card) {
    var v = card.querySelector('video'), btn = card.querySelector('.sf-vcard__play');
    var sound = card.hasAttribute('data-sf-vcard-sound');
    // a silent clip keeps its button while it plays, a pause button now, so Enter or Space stops the loop she started
    // (live review 14, F7: the button went invisible and only a tap on the video paused it)
    var base = (btn.getAttribute('aria-label') || '').replace(/^Play: /, '');
    var label = function () { btn.setAttribute('aria-label', (card.classList.contains('is-playing') ? 'Pause: ' : 'Play: ') + base); };
    btn.addEventListener('click', function () {
      if (!sound && card.classList.contains('is-playing')) { v.pause(); return; }
      Array.prototype.forEach.call(cards, function (o) { if (o !== card) { var ov = o.querySelector('video'); if (!ov.paused) ov.pause(); } });
      if (sound) { v.controls = true; v.muted = false; }
      card.classList.add('is-playing'); label();
      var p = v.play(); if (p && p.catch) p.catch(function () { card.classList.remove('is-playing'); label(); });
    });
    if (!sound) v.addEventListener('click', function () { v.pause(); });
    v.addEventListener('pause', function () { if (!sound || v.ended) card.classList.remove('is-playing'); label(); });
    v.addEventListener('ended', function () { card.classList.remove('is-playing'); label(); });
    // a card she scrolls away from pauses, so its voice does not play over the offer (live review 7)
    if ('IntersectionObserver' in window) new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting && !v.paused) v.pause();
    }, { threshold: 0.15 }).observe(card);
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

  // the pack choice: every picker on the page (the offer near the top and the one at the end) shows the same pack.
  // Black Friday (_includes/sf-bf.html): while html.sf-trial-over is off a card shows its sale price (data-price); after
  // the sale's end its regular one (data-price-over) and its buttons open the checkout on its regular card
  // (data-bundle-over); a refill's amount is data-renew-price when it differs from today's
  var pickers = document.querySelectorAll('[data-sf-packs]');
  var sync = function () {};
  if (pickers.length) {
    var set = function (sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); };
    sync = function (id) {
      var card = document.querySelector('.sf-pack[data-pack="' + id + '"]');
      if (!card) return;
      var over = document.documentElement.classList.contains('sf-trial-over');
      var price = (over && card.getAttribute('data-price-over')) || card.getAttribute('data-price'), every = card.getAttribute('data-every'), renew = card.getAttribute('data-renew') || '';
      var renewPrice = card.getAttribute('data-renew-price') || price, bundle = (over && card.getAttribute('data-bundle-over')) || id;
      Array.prototype.forEach.call(document.querySelectorAll('.sf-pack'), function (c) {
        var on = c.getAttribute('data-pack') === id;
        c.classList.toggle('is-on', on);
        var input = c.querySelector('input'); if (input) input.checked = on;
      });
      set('[data-sf-cta]', function (a) { a.href = a.href.replace(/forceBundleId=[^&#]*/, 'forceBundleId=' + bundle); });
      set('[data-sf-price]', function (e) { e.textContent = price; });
      // what the chosen pack renews at (Automatic Refills): under the button, "$99.97 today, then $99.97 every 140 days, until you cancel"
      set('[data-sf-renew-line] strong', function (e) { e.textContent = price + ' today'; });
      set('[data-sf-renew-text]', function (e) { e.textContent = renew.charAt(0).toLowerCase() + renew.slice(1); });
      set('[data-sf-label]', function (e) { e.textContent = card.getAttribute('data-label'); });
      if (card.hasAttribute('data-renew-short')) set('[data-sf-renew-short]', function (e) { e.textContent = card.getAttribute('data-renew-short'); });
      set('[data-sf-btn-price]', function (e) { e.textContent = '| ' + price; });
      set('[data-sf-sticky-pack]', function (e) { e.textContent = card.getAttribute('data-short'); });
      set('[data-sf-sticky-price]', function (e) { e.textContent = price + ' today, then ' + renewPrice + ' every ' + every; });   // the amount too (live review 13, F2)
    };
    Array.prototype.forEach.call(pickers, function (p) {
      p.addEventListener('change', function (e) {
        var input = e.target; if (input && input.name === 'sf_pack') sync(input.value);
      });
    });
    // the pack the URL names comes first (the listicle's offer is the 5-bottle pack: ?pack=trial-5), then the page's own;
    // a card answers to its old name too (data-alias: ?pack=apf-5 from a link made before Black Friday)
    var asked = (new URLSearchParams(location.search).get('pack') || '').replace(/[^a-z0-9-]/g, '');
    var aka = asked && document.querySelector('.sf-pack[data-alias="' + asked + '"]');
    if (aka) asked = aka.getAttribute('data-pack');
    var wanted = asked && document.querySelector('.sf-pack input[name=sf_pack][value="' + asked + '"]');
    var first = wanted || document.querySelector('.sf-pack input[name=sf_pack]:checked') || document.querySelector('.sf-pack input[name=sf_pack]');
    if (first) sync(first.value);
  }

  // the Black Friday clocks ([data-sf-bf-clock]: the bar above the page, the banner over the packs) count down to the
  // sale's one end (window.sfTrialEnd, _includes/sf-bf.html); at the end the page turns to the regular prices where she
  // is, and the chosen pack's buttons with it
  var clocks = document.querySelectorAll('[data-sf-bf-clock]');
  if (clocks.length && window.sfTrialEnd) {
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    var tick = function () {
      var left = Math.max(0, Math.floor((window.sfTrialEnd - Date.now()) / 1000));
      if (!left) {
        document.documentElement.classList.add('sf-trial-over');
        var on = document.querySelector('.sf-pack input[name=sf_pack]:checked');
        if (on) sync(on.value);
        return false;
      }
      var h = Math.floor(left / 3600), m = Math.floor((left % 3600) / 60), sec = left % 60, d = Math.floor(h / 24);
      h = h % 24;
      var txt = (d ? d + 'd ' : '') + pad(h) + ':' + pad(m) + ':' + pad(sec);
      Array.prototype.forEach.call(clocks, function (c) { c.textContent = txt; c.setAttribute('aria-label', (d ? d + ' days ' : '') + h + ' hours ' + m + ' minutes'); });
      return true;
    };
    if (tick()) { var clockTimer = setInterval(function () { if (!tick()) clearInterval(clockTimer); }, 1000); }
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
  // Axon's item category and photo for the Black Friday cards (funnels/trial.py AXON_CATEGORY, AXON_IMAGE)
  var AXON_CATEGORY = 2765, AXON_IMAGE = 'https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg';
  var axonItem = function (name, card) {
    if (!window.__axonEventKey || typeof window.axon !== 'function') return false;
    var v = parseFloat((document.documentElement.classList.contains('sf-trial-over') && card.getAttribute('data-axon-value-over')) || card.getAttribute('data-axon-value'));
    try {
      window.axon('track', name, { currency: 'USD', value: v, items: [{ item_id: card.getAttribute('data-axon-sku'),
        item_name: card.getAttribute('data-axon-name'), item_brand: 'SKINOFAB', item_variant_id: card.getAttribute('data-axon-variant'),
        item_category_id: AXON_CATEGORY, image_url: AXON_IMAGE, price: v, quantity: 1 }] });
    } catch (err) {}
    return true;
  };
  // view_item: the plan the page opens on (the SDK's next-analytics-view-item tag would name the APF campaign's package)
  var opened = document.querySelector('.sf-pack input[name=sf_pack]:checked');
  var openedCard = opened && opened.closest('.sf-pack');
  if (openedCard && openedCard.hasAttribute('data-axon-sku')) axonItem('view_item', openedCard);
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[data-sf-cta]') : null;
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var sdk = window.next;
    var m = /forceBundleId=([^&#]+)/.exec(a.href);
    var card = m && (document.querySelector('.sf-pack[data-pack="' + m[1] + '"]') || document.querySelector('.sf-pack[data-bundle-over="' + m[1] + '"]'));
    var pkg = card ? parseInt(card.getAttribute('data-package'), 10) : NaN;
    if (!pkg) return;
    e.preventDefault();
    var href = a.href, gone = false;
    var go = function () { if (!gone) { gone = true; window.location.href = href; } };
    setTimeout(go, 1200);
    // Black Friday: the card's own item, the seven fields AppLovin's Axon asks for (as the trial funnel's product page
    // sends them), then the link; the trial funnel's checkout sends begin_checkout and purchase with its own SDK
    if (card.hasAttribute('data-axon-sku')) {
      if (axonItem('add_to_cart', card)) setTimeout(go, 350); else go();
      return;
    }
    if (!sdk || typeof sdk.trackAddToCart !== 'function') { go(); return; }
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

// A link that lands on a section (the listicle's ?pack=apf-5#offer) stays on it while the page above settles: the
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

// the offers' controls the SDK binds are links (<a href="#"> with role="button" in the markup, live review 11): Space
// presses them as it presses a button (Enter already does)
document.addEventListener('keydown', function (e) {
  if (e.key !== ' ' && e.key !== 'Spacebar') return;
  var a = e.target && e.target.closest && e.target.closest('a[role="button"]');
  if (!a) return;
  e.preventDefault();
  if (a.getAttribute('aria-disabled') !== 'true') a.click();
});

// The ad's parameters ride along (speed pass, 5 Nov 2026): the SDK now loads after the page, so its UTM transfer may come
// after her tap; every link to another funnel page (a root-relative link, not an anchor) carries the landing URL's
// parameters (utm_*, click ids) that it does not set itself; ?pack= stays on this page. (Links on this host only; the pack
// picker writes its buttons' href as absolute URLs, so the host is compared, not the href's first character.)
(function () {
  var q = new URLSearchParams(location.search);
  q.delete('pack');
  if (!Array.from(q.keys()).length) return;
  Array.prototype.forEach.call(document.querySelectorAll('a[href]'), function (a) {
    try {
      var raw = a.getAttribute('href');
      if (!raw || raw.charAt(0) === '#' || /^(mailto|tel|javascript):/i.test(raw)) return;
      var u = new URL(raw, location.href);
      if (u.origin !== location.origin || u.pathname === location.pathname) return;
      q.forEach(function (v, k) { if (!u.searchParams.has(k)) u.searchParams.set(k, v); });
      a.setAttribute('href', u.pathname + u.search + u.hash);
    } catch (e) {}
  });
})();
