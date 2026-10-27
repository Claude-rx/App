// The thank-you page: under each order line, what it renews at and how often (the page's renewals, by SKU).
// The SDK renders the lines after the order loads, so the lines are filled as they appear.
(function () {
  const holder = document.querySelector('[data-sf-renewals]');
  if (!holder) return;
  let renewals;
  try { renewals = JSON.parse(holder.getAttribute('data-sf-renewals')); } catch (e) { return; }
  const fill = () => document.querySelectorAll('.sf-line-renew[data-sf-sku]').forEach((el) => {
    const text = renewals[el.getAttribute('data-sf-sku')];
    if (text && el.textContent !== text) el.textContent = text;
  });
  new MutationObserver(fill).observe(document.body, { childList: true, subtree: true });
  fill();
})();

// Opened without an order (no or a wrong ref_id in the address), the receipt would show "Thank you," and empty rows:
// after 8 s with no order line, say so at the top; if the order comes in later (a slow connection), take it down again
// (funnel review 2).
(function () {
  const note = document.querySelector('[data-sf-no-order]');
  if (!note) return;
  const head = () => document.querySelectorAll('.receipt_head, .order-summary-mobile');
  const hasOrder = () => !!document.querySelector('[data-order-line-id]');   // (the loading skeleton is .cart-item too)
  setTimeout(() => {
    if (hasOrder()) return;
    note.hidden = false;
    const wrap = document.querySelector('.main-wrapper') || document.body;
    wrap.insertBefore(note, wrap.firstChild);
    head().forEach((el) => { el.hidden = true; });
    new MutationObserver((_, obs) => {
      if (!hasOrder()) return;
      note.hidden = true; head().forEach((el) => { el.hidden = false; }); obs.disconnect();
    }).observe(document.body, { childList: true, subtree: true });
  }, 8000);
})();
