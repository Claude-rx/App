/* Get Rid Of — funnel step events for the checkout, offer and thank-you pages (build_checkout.py writes this file).
 * Pushes gro_* events to window.dataLayer and, when their tags are on (campaigns.json clarity_id / ga4_id), to Microsoft
 * Clarity and GA4. The sales page sends its own (lp/lp.js). No personal data: field names only, never values. */
(function () {
  'use strict';
  var meta = document.querySelector('meta[name="next-page-type"]');
  var type = (meta && meta.content) || 'page';
  var sent = {};
  window.dataLayer = window.dataLayer || [];
  function track(name, props, once) {
    if (once) { if (sent[name]) return; sent[name] = 1; }
    try {
      var e = { event: 'gro_' + name, gro_page: type, gro_bundle: window.groBundle || '' };
      for (var k in props || {}) e['gro_' + k] = props[k];
      window.dataLayer.push(e);
      if (typeof window.clarity === 'function') window.clarity('event', 'gro_' + name);
      if (typeof window.gtag === 'function') window.gtag('event', 'gro_' + name, props || {});
    } catch (err) { /* never block the page */ }
  }
  window.groTrack = track;
  track(type + '_view', null, true);
  // prices: reveal once the SDK has replaced the placeholder numbers (see gro-checkout.css)
  (function () {
    var root = document.documentElement, els = document.querySelectorAll('[data-next-display^="bundle."][data-next-display$=".price"]');
    if (!els.length) { root.classList.add('gro-prices'); return; }
    var first = []; for (var i = 0; i < els.length; i++) first.push(els[i].textContent);
    var n = 0, iv = setInterval(function () {
      var real = false; for (var j = 0; j < els.length; j++) if (els[j].textContent !== first[j] && /[1-9]/.test(els[j].textContent)) real = true;
      if (real || ++n > 100) { clearInterval(iv); root.classList.add('gro-prices'); if (!real) track('prices_timeout'); }
    }, 100);
  })();
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-next-upsell-action], .submit-button') : null;
    if (!t) return;
    if (t.hasAttribute('data-next-upsell-action')) { track('offer_' + (t.getAttribute('data-next-upsell-action') === 'add' ? 'accept' : 'decline')); return; }
    track('submit_click');
    setTimeout(function () {
      var bad = document.querySelector('.next-error-field');
      if (bad) track('submit_blocked', { field: bad.getAttribute('data-next-checkout-field') || bad.name || bad.id || 'field' });
    }, 700);
  }, true);
  if (type !== 'checkout') return;
  document.addEventListener('focusin', function (e) { if (e.target.matches && e.target.matches('input, select')) track('form_start', null, true); });
  document.addEventListener('change', function (e) {
    var t = e.target; if (!t || !t.matches || !t.matches('input, select')) return;
    if (t.name === 'payment_method') { track('payment_method', { method: t.value }); return; }
    var id = t.getAttribute('data-next-checkout-field') || t.name || t.id;
    if (id && t.value) track('field_' + id.replace(/[^a-z0-9]+/gi, '_').toLowerCase(), null, true);
  }, true);
  // card fields live in iframes: a tap on their wrapper is the signal
  document.addEventListener('pointerdown', function (e) { if (e.target.closest && e.target.closest('[data-next-checkout-field="cc-number"], [data-next-checkout-field="cvv"]')) track('card_field_tap', null, true); }, true);
  // payment errors shown by the SDK
  var errs = document.querySelectorAll('[data-next-component$="-error"]');
  if (errs.length && 'MutationObserver' in window) {
    var mo = new MutationObserver(function () { for (var i = 0; i < errs.length; i++) if (errs[i].offsetParent !== null) { track('payment_error'); break; } });
    for (var i = 0; i < errs.length; i++) mo.observe(errs[i], { attributes: true, childList: true, subtree: true });
  }
})();
