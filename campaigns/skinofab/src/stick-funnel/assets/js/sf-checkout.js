// The funnel checkout's own behaviour, on top of checkout.js (the SDK owns the form, the bundle cards and the totals):
// the reviews slider, and the exit pop (the _includes/exit-intent-popup.html template) that applies STICK10, the
// campaign's 10%-off exit offer on the stick packs, at most once per visit.
(function initReviewsSliders() {
  if (typeof Swiper === 'undefined') return;
  document.querySelectorAll('[data-component="reviews-swiper"]').forEach((el) => {
    new Swiper(el, {
      slidesPerView: 'auto',
      spaceBetween: 16,
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
