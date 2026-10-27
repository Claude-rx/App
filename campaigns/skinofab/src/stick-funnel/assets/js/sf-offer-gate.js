// The special offers' two rules, applied once the SDK has the order (the page shows nothing of the offer meanwhile):
//   - an order that can't take a one-click offer (order.supports_post_purchase_upsells is false: its payment method
//     can't be charged again) goes straight to the thank-you page, with its order reference;
//   - on special offer 4 (its gate has data-sf-ship-country), an order shipping to Europe goes where a decline goes: the
//     serum's EGF, sh-Oligopeptide-1, is not allowed in cosmetics sold in the EU, and the UK, Switzerland and the EEA
//     follow the same list (docs/egf-nad-serum.md).
(function () {
  const EUROPE = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU',
    'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'IS', 'LI', 'NO', 'CH', 'GB', 'UK'];
  const NAMES = ['austria', 'belgium', 'bulgaria', 'croatia', 'cyprus', 'czechia', 'czech republic', 'denmark', 'estonia',
    'finland', 'france', 'germany', 'greece', 'hungary', 'ireland', 'italy', 'latvia', 'lithuania', 'luxembourg', 'malta',
    'netherlands', 'poland', 'portugal', 'romania', 'slovakia', 'slovenia', 'spain', 'sweden', 'iceland', 'liechtenstein',
    'norway', 'switzerland', 'united kingdom'];
  const gate = document.querySelector('[data-sf-offer-gate]');
  if (!gate) return;
  const ok = gate.querySelector('[data-sf-upsell-ok]');
  const country = gate.querySelector('[data-sf-ship-country]');
  const thankYou = gate.getAttribute('data-sf-thank-you');
  let done = false;
  const hide = () => document.documentElement.classList.add('sf-skipping');
  const check = () => {
    if (done) return;
    const can = (ok.textContent || '').trim().toLowerCase();
    if (!can) return;                                     // the order is not loaded yet
    // (the SDK writes the flag as "Yes" / "No")
    if ((can === 'no' || can === 'false') && thankYou) { done = true; hide(); location.replace(thankYou + location.search); return; }
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
})();
