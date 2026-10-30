// The thank-you page: under each order line, its terms (the page's renewals, by SKU: what the pack refills at, or that an add-on is bought once),
// and in "what happens next" the gifts in her box (the page's gifts, by SKU, joined for the lines the order has).
// The SDK renders the lines after the order loads, so both are filled as the lines appear. The shipping total the
// SDK writes as $0.00 reads "Free" (the campaign's one method is free, and the checkout said so).
(function () {
  const holder = document.querySelector('[data-sf-renewals]');
  if (!holder) return;
  let renewals, giftMap = {};
  try { renewals = JSON.parse(holder.getAttribute('data-sf-renewals')); } catch (e) { return; }
  try { giftMap = JSON.parse(holder.getAttribute('data-sf-gift-map') || '{}'); } catch (e) { giftMap = {}; }
  let packImages = {};
  try { packImages = JSON.parse(holder.getAttribute('data-sf-pack-images') || '{}'); } catch (e) { packImages = {}; }
  const giftLine = document.querySelector('[data-sf-gift-line]');
  const join = (xs) => xs.length < 2 ? xs.join('') : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];
  const fill = () => {
    const num = document.querySelector('[data-next-display="order.number"]');
    if (num && num.textContent.trim()) document.documentElement.classList.remove('sf-no-order');   // an order after all
    const skus = [];
    document.querySelectorAll('.sf-line-renew[data-sf-sku]').forEach((el) => {
      const sku = el.getAttribute('data-sf-sku'); skus.push(sku);
      const text = renewals[sku];
      if (text && el.textContent !== text) el.textContent = text;
      // a pack that renews is named by its bottles, its gifts on a first-order line (as on the checkout, live review 10)
      const title = el.parentElement && el.parentElement.querySelector('.cart-item__title');
      if (title && text && /^Then /.test(text)) {
        const m = (title.textContent || '').match(/^(.+? - \d+ bottles?) \+ (.+)$/);
        if (m) { title.textContent = m[1]; const n = document.createElement('div'); n.className = 'sf-first-order'; n.textContent = 'With this first order only: + ' + m[2] + '. Refills are the bottles.'; title.insertAdjacentElement('afterend', n); }
      }
    });
    // each line's own picture (two bottles for the 2-pack, not the campaign's one-bottle image on every line)
    document.querySelectorAll('img[data-sf-sku-img]').forEach((img) => {
      const src = packImages[img.getAttribute('data-sf-sku-img')];
      if (src && img.getAttribute('src') !== src) img.setAttribute('src', src);
    });
    if (giftLine && skus.length) {
      const gifts = []; skus.forEach((k) => (giftMap[k] || []).forEach((g) => { if (!gifts.includes(g)) gifts.push(g); }));
      const strong = giftLine.querySelector('strong'), span = giftLine.querySelector('[data-sf-gifts]');
      const title = gifts.length ? 'Your gifts are in the box.' : 'Everything ships in one package.';
      const body = gifts.length ? join(gifts).replace(/^./, (c) => c.toUpperCase()) + (gifts.length > 1 ? ' ship' : ' ships') + ' in the same package as your foundation, free.' : 'Your order ships in 1 business day, with tracking.';
      if (strong && strong.textContent !== title) strong.textContent = title;
      if (span && span.textContent !== body) span.textContent = body;
    }
    document.querySelectorAll('[data-sf-shipping]').forEach((el) => {
      const v = el.querySelector('[data-next-display]');
      if (v && /^\s*\$0(?:\.00)?\s*$/.test(v.textContent)) v.textContent = 'Free';
    });
  };
  new MutationObserver(fill).observe(document.body, { childList: true, subtree: true, characterData: true });
  fill();
})();

// Opened without an order (no or a wrong ref_id in the address), the receipt would show "Thank you," and empty rows:
// after 8 s with no order line, say so at the top; if the order comes in later (a slow connection), take it down again
// (funnel review 2).
(function () {
  const note = document.querySelector('[data-sf-no-order]');
  if (!note) return;
  // everything that speaks of an order: the heading, the confirmed card and the sections under it, both summaries
  // (live review 7: "Your order is confirmed" and a $0.00 desktop summary stayed under the note)
  const head = () => document.querySelectorAll('.receipt_head, .receipt_section, .order-summary-mobile, .summary-desktop');
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

// The range under the order: the EGF serum's card goes for an order shipping to Europe (EU, EEA, UK, Switzerland: its EGF
// is not allowed in cosmetics sold there; the store's offer gate skips it the same way), once the SDK writes the country.
(function () {
  const country = document.querySelector('.sf-more [data-sf-ship-country]');
  if (!country) return;
  const EUROPE = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU',
    'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'IS', 'LI', 'NO', 'CH', 'GB', 'UK'];
  const NAMES = ['austria', 'belgium', 'bulgaria', 'croatia', 'cyprus', 'czechia', 'czech republic', 'denmark', 'estonia',
    'finland', 'france', 'germany', 'greece', 'hungary', 'ireland', 'italy', 'latvia', 'lithuania', 'luxembourg', 'malta',
    'netherlands', 'poland', 'portugal', 'romania', 'slovakia', 'slovenia', 'spain', 'sweden', 'iceland', 'liechtenstein',
    'norway', 'switzerland', 'united kingdom'];
  const check = () => {
    const c = (country.textContent || '').trim();
    if (!c) return;
    if (EUROPE.includes(c.toUpperCase()) || NAMES.includes(c.toLowerCase())) {
      document.querySelectorAll('.sf-more [data-sf-not-europe]').forEach((el) => { el.hidden = true; });
    }
    obs.disconnect();
  };
  const obs = new MutationObserver(check);
  obs.observe(country, { childList: true, characterData: true, subtree: true });
  check();
})();
