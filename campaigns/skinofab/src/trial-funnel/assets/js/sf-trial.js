// The flash trial's clock on the checkout (the owner, 4 Nov 2026: "ends at her midnight"): the deadline is midnight, her
// time, of the day she first saw the offer, kept in localStorage (sf_trial_end) on try.skinofab.com, where the product
// page set it (the product page and this page share the key). The page's first inline script (in the body, before the
// SDK reads the URL) already marked <html> sf-trial-over after the deadline and put the right card in ?forceBundleId:
// "trial" (FLASH50, $19.97 today) or "trial-regular" (no code, $39.97). This file ticks the clock in the trial bar and,
// when midnight passes while she is on the page, switches to the regular card (the SDK removes FLASH50 with the card),
// so the code is never applied after the deadline.
(function () {
  var end = window.sfTrialEnd || 0;
  if (!end) return;
  var clocks = document.querySelectorAll('[data-sf-trial-clock]');
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var over = function () {
    document.documentElement.classList.add('sf-trial-over');
    var pick = function () {
      var reg = document.querySelector('[data-next-bundle-card][data-next-bundle-id="trial-regular"]');
      if (reg && !reg.classList.contains('next-selected')) reg.click();
    };
    pick();
    window.addEventListener('next:initialized', pick);
    document.addEventListener('next:initialized', pick);
  };
  var tick = function () {
    var left = Math.max(0, Math.floor((end - Date.now()) / 1000));
    var h = Math.floor(left / 3600), m = Math.floor((left % 3600) / 60), s = left % 60;
    var text = pad(h) + ':' + pad(m) + ':' + pad(s);
    clocks.forEach(function (c) { c.textContent = text; c.setAttribute('aria-label', h + ' hours ' + m + ' minutes'); });
    if (left === 0) { clearInterval(t); over(); }
  };
  if (Date.now() >= end) { over(); return; }
  var t = setInterval(tick, 1000);
  tick();
})();
