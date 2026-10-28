// Offer 1's supply cards (_includes/sf-supply-cards.html): a card's Buy now selects that card (the SDK's own click on
// the bundle card) and then fires the offer's add action, so the order gets the card she pressed, never the one that
// happened to be selected. Enter or Space on a focused card selects it (the SDK binds click only).
(function () {
  'use strict';
  var cards = document.querySelectorAll('[data-sf-supply-card]');
  if (!cards.length) return;
  var add = document.querySelector('[data-next-upsell="offer"] [data-next-upsell-action="add"]');
  var mark = function () {
    cards.forEach(function (c) { c.setAttribute('aria-pressed', c.classList.contains('next-selected') ? 'true' : 'false'); });
  };
  cards.forEach(function (card) {
    var buy = card.querySelector('[data-sf-supply-buy]');
    if (buy) buy.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      if (!card.classList.contains('next-selected')) card.click();
      // the selection is the SDK's own state change; the add reads it on the next tick
      setTimeout(function () { if (add) add.click(); }, 60);
    });
    card.addEventListener('keydown', function (e) {
      if (e.target !== card) return;
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); card.click(); }
    });
    new MutationObserver(mark).observe(card, { attributes: true, attributeFilter: ['class'] });
  });
  mark();
})();
