// The special offers' two rules, applied once the SDK has the order (the page shows nothing of the offer meanwhile):
//   - an order that can't take a one-click offer (order.supports_post_purchase_upsells is false: its payment method
//     can't be charged again) goes straight to the thank-you page, with its order reference;
//   - on special offer 4 (its gate has data-sf-ship-country), an order shipping to Europe goes where a decline goes: the
//     serum's EGF, sh-Oligopeptide-1, is not allowed in cosmetics sold in the EU, and the UK, Switzerland and the EEA
//     follow the same list (docs/egf-nad-serum.md).
//   - on the brush offers (their gate has data-sf-skip-skus), an order whose lines already include a brush (the
//     3-bottle pack, the 6-bottle pack: their SKUs) goes where a decline goes, to the thank-you page: the order's lines
//     are read from the gate's hidden order-items list ([data-sf-sku], the SDK fills it from the order).
// It also puts her first name after "Just for you" ([data-sf-name], sf-upsell-reserved.html) once the order has one.
(function () {
  const EUROPE = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU',
    'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'IS', 'LI', 'NO', 'CH', 'GB', 'UK'];
  const NAMES = ['austria', 'belgium', 'bulgaria', 'croatia', 'cyprus', 'czechia', 'czech republic', 'denmark', 'estonia',
    'finland', 'france', 'germany', 'greece', 'hungary', 'ireland', 'italy', 'latvia', 'lithuania', 'luxembourg', 'malta',
    'netherlands', 'poland', 'portugal', 'romania', 'slovakia', 'slovenia', 'spain', 'sweden', 'iceland', 'liechtenstein',
    'norway', 'switzerland', 'united kingdom'];
  // the "Confirming your order…" line under the clock goes once the SDK has drawn the page (the offer sat behind a
  // blank band for ~2 s, live review 1)
  const noteOff = () => document.querySelectorAll('[data-sf-await-note]').forEach((e) => { e.hidden = true; });
  document.addEventListener('next:initialized', noteOff);
  window.addEventListener('next:initialized', noteOff);
  setTimeout(noteOff, 8000);
  const gate = document.querySelector('[data-sf-offer-gate]');
  if (!gate) return;
  const ok = gate.querySelector('[data-sf-upsell-ok]');
  const country = gate.querySelector('[data-sf-ship-country]');
  const thankYou = gate.getAttribute('data-sf-thank-you');
  const skipSkus = (gate.getAttribute('data-sf-skip-skus') || '').split(',').map((x) => x.trim()).filter(Boolean);
  let done = false;
  const hide = () => document.documentElement.classList.add('sf-skipping');
  const check = () => {
    if (done) return;
    const can = (ok.textContent || '').trim().toLowerCase();
    if (!can) return;                                     // the order is not loaded yet
    noteOff();
    document.documentElement.classList.remove('sf-no-order');   // an order after all (the page's no-order note goes)
    // (the SDK writes the flag as "Yes" / "No")
    if ((can === 'no' || can === 'false') && thankYou) { done = true; hide(); location.replace(thankYou + location.search); return; }
    if (skipSkus.length) {
      const skus = Array.from(gate.querySelectorAll('[data-sf-sku]')).map((e) => e.getAttribute('data-sf-sku'));
      if (!skus.length) return;                              // the lines are not drawn yet
      done = true;
      if (skus.some((k) => skipSkus.includes(k)) && thankYou) { hide(); location.replace(thankYou + location.search); }
      return;
    }
    if (!country) { done = true; return; }
    const c = (country.textContent || '').trim();
    if (!c) return;
    done = true;
    if (EUROPE.includes(c.toUpperCase()) || NAMES.includes(c.toLowerCase())) {
      // where a decline goes (the page's own next-upsell-decline-url), with the order reference: the SDK's skip link
      // may not be bound yet when the order arrives
      const decline = document.querySelector('meta[name="next-upsell-decline-url"]');
      if (decline) { hide(); location.replace(decline.getAttribute('content') + location.search); }
    }
  };
  new MutationObserver(check).observe(gate, { childList: true, characterData: true, subtree: true });
  check();
  const first = gate.querySelector('[data-sf-first-name]');
  const name = () => {
    const n = (first && first.textContent || '').trim();
    if (n) document.querySelectorAll('[data-sf-name]').forEach((e) => { e.textContent = ', ' + n; });
  };
  if (first) { new MutationObserver(name).observe(first, { childList: true, characterData: true, subtree: true }); name(); }
})();
