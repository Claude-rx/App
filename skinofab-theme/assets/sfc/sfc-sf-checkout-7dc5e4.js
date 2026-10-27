// The funnel checkout's own behaviour, on top of checkout.js (the SDK owns the form, the bundle cards and the totals):
// the reviews slider, the pay line's renewal (below), and the exit pop (the _includes/exit-intent-popup.html template) that applies STICK10, the
// campaign's 10%-off exit offer on the stick packs, at most once per visit.
(function initReviewsSliders() {
  if (typeof Swiper === 'undefined') return;
  document.querySelectorAll('[data-component="reviews-swiper"]').forEach((el) => {
    new Swiper(el, {
      // whole cards only (funnel review 1: the second card was cut off at 1440): one on a phone, two from tablet up
      slidesPerView: 1,
      spaceBetween: 16,
      breakpoints: { 768: { slidesPerView: 2 } },
      grabCursor: true,
      observer: true,
      observeParents: true,
      resizeObserver: true,
      scrollbar: { el: el.querySelector('.swiper-scrollbar'), draggable: true },
    });
  });
})();

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
