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
