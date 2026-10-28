// The funnel checkout's own behaviour, on top of checkout.js (the SDK owns the form, the bundle cards and the totals):
// the pay line's renewal (below) and the exit pop (the _includes/exit-intent-popup.html template) that applies the page's exit code (APF10 here, the
// campaign's 10%-off exit offer on the foundation packs; STICK10 on the stick funnel), at most once per visit: on a
// computer when the pointer leaves through the top, on a phone on a scroll back up toward the address bar (the SDK's
// own mobile trigger; without it phone buyers, most of the traffic, never saw the offer).
window.addEventListener('next:initialized', function () {
  if (!window.next || typeof window.next.exitIntent !== 'function') return;
  window.next.exitIntent({ template: 'exit-intent', showCloseButton: true, maxTriggers: 1, disableOnMobile: false, mobileScrollTrigger: true });
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

// the pay line before the SDK answers: its fallback amount is the pack the URL asks for (?forceBundleId=apf-3 showed
// $57.00 for ~4 s; live review 1), read from the bundles' prices on the element
(function initPayFallback() {
  const e = document.querySelector('[data-sf-pay-fallback]');
  if (!e) return;
  let prices = {};
  try { prices = JSON.parse(e.getAttribute('data-sf-prices') || '{}'); } catch (_) { return; }
  const id = (new URLSearchParams(location.search).get('forceBundleId') || '').split(':').pop();
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
    const price = prices[(card.getAttribute('data-next-bundle-id') || '').split(':').pop()];
    if (!price || couponOn()) return;
    if (fb) fb.textContent = price;
    const live = document.querySelector('[data-next-show="cart.hasItems"] [data-next-display="cart.total"]');
    if (live) live.textContent = price;
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
