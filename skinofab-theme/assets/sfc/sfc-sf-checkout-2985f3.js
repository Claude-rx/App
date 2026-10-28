// The funnel checkout's own behaviour, on top of checkout.js (the SDK owns the form, the bundle cards and the totals):
// the pay line's renewal (below) and the exit pop (the _includes/exit-intent-popup.html template) that applies STICK10, the
// campaign's 10%-off exit offer on the stick packs, at most once per visit.
window.addEventListener('next:initialized', function () {
  if (!window.next || typeof window.next.exitIntent !== 'function') return;
  window.next.exitIntent({ template: 'exit-intent', showCloseButton: true, maxTriggers: 1 });
});

// The pay line by the express buttons and the order button: today's total is the SDK's; what renews follows the chosen
// pack card (the SDK marks it next-selected), from the page's pay_terms (stick-checkout.html).
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
