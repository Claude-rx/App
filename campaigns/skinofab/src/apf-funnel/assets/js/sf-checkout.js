// The funnel checkout's own behaviour, on top of checkout.js (the SDK owns the form, the bundle cards and the totals):
// the pay line's renewal (below) and the exit pop (the _includes/exit-intent-popup.html template) that applies the page's exit code (APF10 here, the
// campaign's 10%-off exit offer on the foundation packs; STICK10 on the stick funnel), at most once per visit: on a
// computer when the pointer leaves through the top, on a phone on a fast scroll back up toward the address bar once she
// has been past the order button and is above it again (opened by this page; the SDK's own trigger fires at half the page).
window.addEventListener('next:initialized', function () {
  if (!window.next || typeof window.next.exitIntent !== 'function') return;
  var base = { template: 'exit-intent', showCloseButton: true, maxTriggers: 1 };
  var coarse = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
  if (!coarse) { window.next.exitIntent(base); return; }
  // a phone: the SDK's own scroll trigger fires once the page is half scrolled, which is the order button, while she is
  // still filling in the form (live review 4), and only below half the page, where the order button is not (it sits at
  // 35-43 % on a phone). So the pop is set up without it, and opened here, once per visit, by a fast scroll back up
  // (toward the address bar or the back button): at least 300 px up within 400 ms, after she has seen the order button,
  // once she is above it again. A slow scroll back up, or one from the reviews below the button back to it, is someone
  // going to pay, not leaving (live review 5: 220 px at 50 px/s opened it).
  var setup = Promise.resolve(window.next.exitIntent(Object.assign({ disableOnMobile: false, mobileScrollTrigger: false }, base)));
  var btn = document.querySelector('[data-next-checkout="form"] button[type="submit"]');
  var steps = [], last = window.scrollY, seenPay = false, armed = false, lastField = 0;
  document.addEventListener('focusout', function (e) { if (e.target && /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) lastField = Date.now(); }, true);
  var open = function () {
    setup.then(function () {
      var ex = window.next.popupsState && window.next.popupsState.exitIntentEnhancer;
      if (ex && typeof ex.triggerExitIntent === 'function' && !ex.popupElement && ex.triggerCount < ex.maxTriggers) ex.triggerExitIntent();
    });
  };
  var onScroll = function () {
    var y = window.scrollY, t = Date.now(), d = last - y;                 // d > 0: scrolling up
    last = y;
    var r = btn ? btn.getBoundingClientRect() : null;
    if (r && r.top < window.innerHeight && r.bottom > 0) seenPay = true;
    steps.push([t, d]);
    while (steps.length && t - steps[0][0] > 400) steps.shift();
    var up = 0; for (var k = 0; k < steps.length; k++) up += steps[k][1];   // net upward distance in the last 400 ms
    // ...and only when the flick ends near the top of the page (toward the address bar) with no field in use: a flick
    // mid-form, back to a field above, is someone checking her details (live review 7)
    var typing = document.activeElement && /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName) || Date.now() - lastField < 3000;
    if (!armed && r && seenPay && r.top > window.innerHeight && up >= 300 && y < window.innerHeight * 0.6 && !typing) {   // the order button is below her now
      armed = true; window.removeEventListener('scroll', onScroll); open();
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
});

// The exit pop for the keyboard and a screen reader (live review 7): when the SDK shows it, its close button is named
// and moved inside the dialog, focus moves to the offer's button and Tab stays in the dialog, the page behind is inert
// and does not scroll (live review 8; the body too, for iOS Safari, live review 9), Escape closes it, and focus returns to
// where she was, or to the order button when nothing had focus (live review 9: it went to the body, the top of the page).
window.addEventListener('next:initialized', function () {
  if (!window.next || typeof window.next.on !== 'function') return;
  var before = null;
  window.next.on('exit-intent:shown', function () {
    before = document.activeElement;
    setTimeout(function () {
      var dlg = document.querySelector('.exit-intent-popup__dialog');
      if (!dlg) return;
      var root = dlg.parentElement && dlg.parentElement.parentElement ? dlg.parentElement.parentElement : document.body;
      Array.prototype.forEach.call(root.querySelectorAll('button, [role="button"]'), function (b) {
        if (!b.getAttribute('aria-label') && (/close/i.test(b.className) || /^[×✕✖x]$/i.test((b.textContent || '').trim()))) b.setAttribute('aria-label', 'Close');
      });
      var x = root.querySelector('[aria-label="Close"]');
      if (x && !dlg.contains(x)) dlg.appendChild(x);          // in the dialog: read with it, and in its Tab order
      var top = dlg; while (top.parentElement && top.parentElement !== document.body) top = top.parentElement;
      // the SDK's dark overlay is a body child of its own: it stays live, so a tap outside the box closes the pop (live review 11)
      var made = Array.prototype.filter.call(document.body.children, function (el) { return el !== top && !el.inert && !/^(SCRIPT|STYLE|TEMPLATE)$/.test(el.tagName) && !/exit-intent/.test(String(el.className)) && !el.hasAttribute('data-exit-intent'); });
      made.forEach(function (el) { el.inert = true; });
      var overflow = document.documentElement.style.overflow, bodyOverflow = document.body.style.overflow;
      document.documentElement.style.overflow = 'hidden'; document.body.style.overflow = 'hidden';
      var cta = dlg.querySelector('.exit-intent-popup__cta'); if (cta) cta.focus();
      var esc = function (e) {
        if (e.key === 'Escape') { var close = root.querySelector('[aria-label="Close"]'); if (close) close.click(); return; }
        if (e.key !== 'Tab') return;
        var f = Array.prototype.filter.call(dlg.querySelectorAll('button, a[href], [tabindex]:not([tabindex="-1"])'), function (el) { return el.offsetParent !== null; });
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        else if (!dlg.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
      };
      document.addEventListener('keydown', esc);
      var outside = function (e) {
        if (!document.contains(dlg) || dlg.contains(e.target)) return;
        var close = root.querySelector('[aria-label="Close"]'); if (close) close.click();
      };
      document.addEventListener('click', outside);
      var gone = new MutationObserver(function () {
        if (document.querySelector('.exit-intent-popup__dialog')) return;
        gone.disconnect(); document.removeEventListener('keydown', esc); document.removeEventListener('click', outside);
        made.forEach(function (el) { el.inert = false; });
        document.documentElement.style.overflow = overflow; document.body.style.overflow = bodyOverflow;
        var back = before && before !== document.body && before !== document.documentElement && document.contains(before) ? before
          : document.querySelector('.submit-section__button .submit-button');
        if (back && back.focus) back.focus({ preventScroll: true });
      });
      gone.observe(document.body, { childList: true, subtree: true });
    }, 60);
  });
});

// The pay line by the express buttons and the order button: today's total is the SDK's; what the pack is (or, on the stick
// funnel, what renews) follows the chosen pack card (the SDK marks it next-selected), from the page's pay_terms.
(function initPayTerms() {
  const line = document.querySelector('[data-sf-pay-terms]');
  if (!line) return;
  let terms;
  try { terms = JSON.parse(line.getAttribute('data-sf-pay-terms')); } catch (e) { return; }
  const cards = document.querySelectorAll('[data-next-bundle-card]');
  const sync = () => {
    const on = document.querySelector('[data-next-bundle-card].next-selected');
    const text = on && terms[on.getAttribute('data-next-bundle-id')];
    if (text) document.querySelectorAll('[data-sf-renew]').forEach((el) => { el.textContent = text; });
    const box = document.querySelector('[data-sf-renew-short]');
    let short = {};
    try { short = JSON.parse(box ? box.getAttribute('data-sf-renew-short') : '{}'); } catch (e) { short = {}; }
    const s = on && short[on.getAttribute('data-next-bundle-id')];
    if (s) document.querySelectorAll('[data-sf-renew-short-text]').forEach((el) => { el.textContent = s; });
    const pk = document.querySelector('[data-sf-picked]');
    let picked = {};
    try { picked = JSON.parse(pk ? pk.getAttribute('data-sf-picked') : '{}'); } catch (e) { picked = {}; }
    const pt = on && picked[on.getAttribute('data-next-bundle-id')];
    if (pt) document.querySelectorAll('[data-sf-picked-text]').forEach((el) => { el.textContent = pt; });
  };
  const watch = new MutationObserver(sync);
  cards.forEach((c) => watch.observe(c, { attributes: true, attributeFilter: ['class'] }));
  sync();
})();

// The pack cards from the keyboard: the SDK's cards are div[role=button] it binds a click to, so Tab reaches them,
// Enter or Space picks one, and aria-pressed says which is chosen (checkout review 2).
(function initCardKeys() {
  const cards = document.querySelectorAll('[data-next-bundle-card]');
  if (!cards.length) return;
  const mark = () => cards.forEach((c) => c.setAttribute('aria-pressed', c.classList.contains('next-selected') ? 'true' : 'false'));
  cards.forEach((c) => {
    if (!c.hasAttribute('tabindex')) c.setAttribute('tabindex', '0');
    c.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); c.click(); } });
    new MutationObserver(mark).observe(c, { attributes: true, attributeFilter: ['class'] });
  });
  mark();
})();

// The express buttons the SDK builds carry no name a screen reader can say (Apple Pay's is an unlabelled icon).
(function initExpressNames() {
  const box = document.querySelector('[data-next-express-checkout="container"]');
  if (!box) return;
  const names = { 'cc-paypal': 'PayPal', 'cc-apple-pay': 'Apple Pay', 'cc-google-pay': 'Google Pay', 'cc-link': 'Link', 'cc-shop-pay': 'Shop Pay' };
  const name = () => box.querySelectorAll('button, [role="button"]').forEach((b) => {
    if (b.getAttribute('aria-label')) return;
    const key = Object.keys(names).find((k) => b.classList.contains(k));
    if (key) b.setAttribute('aria-label', 'Pay with ' + names[key]);
  });
  new MutationObserver(name).observe(box, { childList: true, subtree: true });
  name();
})();

// the order summary's stand-in (before the SDK has the campaign): the pack, its price and the total for a pack id
window.sfSummaryFallback = function (id) {
  const box = document.querySelector('[data-sf-sumfb]');
  if (!box) return;
  let packs = {};
  try { packs = JSON.parse(box.getAttribute('data-sf-sumfb') || '{}'); } catch (_) { return; }
  const p = packs[id];
  if (!p) return;
  box.querySelector('[data-sf-sumfb-name]').textContent = p.name;
  box.querySelector('[data-sf-sumfb-price]').textContent = p.price;
  box.querySelector('[data-sf-sumfb-total]').textContent = p.price;
  box.querySelector('[data-sf-sumfb-img]').setAttribute('src', p.image);
};

// the pay line before the SDK answers: its fallback amount is the pack the URL asks for (?forceBundleId=apf-3 showed
// $57.00 for ~4 s; live review 1), read from the bundles' prices on the element
(function initPayFallback() {
  const e = document.querySelector('[data-sf-pay-fallback]');
  if (!e) return;
  let prices = {};
  try { prices = JSON.parse(e.getAttribute('data-sf-prices') || '{}'); } catch (_) { return; }
  const id = (new URLSearchParams(location.search).get('forceBundleId') || '').split(':').pop();
  if (id) window.sfSummaryFallback(id);
  if (id && prices[id]) {
    e.textContent = prices[id];
    const live = e.previousElementSibling && e.previousElementSibling.querySelector('[data-next-display="cart.total"]');
    if (live && !live.textContent.startsWith('$0')) live.textContent = prices[id];
  }
})();

// the order summary shows its lines once the SDK has the campaign (an empty frame for ~4 s before, live review 1)
(function initSummaryReady() {
  const box = document.querySelector('[data-sf-summary-box]');
  if (!box) return;
  const ready = () => box.classList.add('sf-co-ready');
  document.addEventListener('next:initialized', ready);
  window.addEventListener('next:initialized', ready);
  const lines = box.querySelector('[data-summary-lines]');
  if (lines) new MutationObserver(() => { if (lines.textContent.trim()) ready(); }).observe(lines, { childList: true, subtree: true, characterData: true });
  setTimeout(ready, 8000);
})();

// a pack tapped before the SDK has bound the cards (the first ~3 s) was lost (live review 2): the tap is shown at
// once (the card marked, the pay line's amount), kept, and replayed on the card once the SDK is ready. After the
// SDK is ready, a tap still shows the card's price at once instead of the ~0.7 s the recalculation takes, unless a
// coupon is on (then the total is the SDK's alone).
(function initEarlyPick() {
  const sel = document.querySelector('[data-next-bundle-selector]');
  const fb = document.querySelector('[data-sf-pay-fallback]');
  if (!sel) return;
  let prices = {};
  try { prices = JSON.parse((fb && fb.getAttribute('data-sf-prices')) || '{}'); } catch (_) {}
  let ready = false, pending = null;
  const couponOn = () => !!document.querySelector('[data-next-discounts="voucher"].next-discounts-has-items');
  const show = (card) => {
    sel.querySelectorAll('[data-next-bundle-card]').forEach((c) => { const on = c === card; c.classList.toggle('next-selected', on); c.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    const bid = (card.getAttribute('data-next-bundle-id') || '').split(':').pop();
    window.sfSummaryFallback(bid);
    const price = prices[bid];
    if (!price || couponOn()) return;
    if (fb) fb.textContent = price;
    document.querySelectorAll('[data-next-display="cart.total"]').forEach((el) => { el.textContent = price; });
  };
  sel.addEventListener('click', (e) => {
    const card = e.target.closest('[data-next-bundle-card]');
    if (!card) return;
    if (!ready) pending = card;
    show(card);
  }, true);
  const onReady = () => {
    if (ready) return;
    ready = true;
    if (pending) { const c = pending; pending = null; setTimeout(() => { c.click(); }, 80); }
  };
  document.addEventListener('next:initialized', onReady);
  window.addEventListener('next:initialized', onReady);
})();

// a pack that renews is named by what renews: the SDK's line name is the store variant's ("… - 3 bottles + free gifts + free
// Lymphatic Brush"), which sat on the line marked "Refills: Every 84 days" while every term says the gifts come with the
// first order only (live review 10): the bottles stay in the name, the gifts go to a "with this first order only" line
window.sfSplitGiftName = function (title) {
  const m = (title.textContent || '').match(/^(.+? - \d+ bottles?) \+ (.+)$/);
  if (!m) return;
  title.textContent = m[1];
  const note = document.createElement('div'); note.className = 'sf-first-order';
  note.textContent = 'With this first order only: + ' + m[2] + '. Refills are the bottles.';
  // under the line's header row, full width: beside the name it was a 64 px column at 390 (live review 11)
  (title.closest('.cart-item__header') || title).insertAdjacentElement('afterend', note);
};
(function initRenewingNames() {
  const box = document.querySelector('[data-next-cart-summary]');
  if (!box) return;
  const fix = () => box.querySelectorAll('.cart-item').forEach((line) => {
    const f = line.querySelector('.cart-item__frequency'), t = line.querySelector('.cart-item__title');
    if (t && f && /^\s*Refills:/.test(f.textContent || '')) window.sfSplitGiftName(t);
  });
  new MutationObserver(fix).observe(box, { childList: true, subtree: true });
  fix();
})();

