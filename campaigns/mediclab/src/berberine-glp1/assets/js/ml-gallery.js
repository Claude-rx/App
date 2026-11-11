// MedicLab checkout: start the product gallery (swiper-gallery.html, sw1). The starter's checkout.js defines
// initSwiperGalleries() but the checkout never called it (only the upsell script does), which left the slides stacked.
(function () {
  function start() { if (typeof initSwiperGalleries === 'function') initSwiperGalleries(6); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
