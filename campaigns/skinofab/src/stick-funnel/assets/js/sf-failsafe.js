// The checkout, special offers and thank-you page are drawn by the SDK: if it can't load the campaign (its API down,
// or the domain not allowed on the campaign), they would stay blank. After 10 s without the SDK, say what happened
// and what to do, at the top of the page. The page's own data-sf-failsafe text is the message.
(function () {
  let ready = false;
  window.addEventListener('next:initialized', () => { ready = true; });
  setTimeout(() => {
    if (ready || (window.next && window.next.cart)) return;
    const text = document.querySelector('[data-sf-failsafe]');
    if (!text) return;
    text.hidden = false;
    const wrap = document.querySelector('.main-wrapper') || document.body;
    wrap.insertBefore(text, wrap.firstChild);
  }, 10000);
})();
