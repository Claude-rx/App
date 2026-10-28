// The checkout, special offers and thank-you page are drawn by the SDK: if it can't load the campaign (its API down,
// or the domain not allowed on the campaign), they would stay blank. After 10 s without the SDK, say what happened
// and what to do, at the top of the page. The page's own data-sf-failsafe text is the message.
// The SDK can be slower than that on a slow phone and still arrive (it was at 5.6 s on a fast connection), so the
// message goes away the moment it does (checkout review: "Checkout didn't load" stayed above a working checkout).
(function () {
  const text = document.querySelector('[data-sf-failsafe]');
  if (!text) return;
  // ready: its event, its window.next.cart, or the class it puts on <html> once it has drawn the page
  const ready = () => !!((window.next && window.next.cart) || document.documentElement.classList.contains('next-display-ready'));
  const hide = () => { if (ready()) text.hidden = true; };
  window.addEventListener('next:initialized', () => { text.hidden = true; });
  new MutationObserver(hide).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  setTimeout(() => {
    if (ready()) return;
    text.hidden = false;
    const wrap = document.querySelector('.main-wrapper') || document.body;
    wrap.insertBefore(text, wrap.firstChild);
  }, 10000);
})();
