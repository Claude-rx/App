// Offer 1's supply cards (_includes/sf-supply-cards.html): every card's Buy now is the SDK's own add action, which adds
// the SELECTED card. A real click (hers, or a test harness's) on a card that is not selected is stopped before the SDK
// sees it, the card is selected (the SDK's own click on the bundle card) and the same button is clicked again for her,
// now for the right card; a proxied click (the closing card's button forwards one, upsells.js) is left alone, so it
// adds the selection, as its copy says. The closing card's picture follows the selected card (its data-sf-image), so
// "Add the pack you chose above?" shows the pack she chose.
(function () {
  'use strict';
  var cards = document.querySelectorAll('[data-sf-supply-card]');
  if (!cards.length) return;
  var closing = document.querySelector('.upsell-closing .upsell-offer__image-column img');
  var mark = function () {
    cards.forEach(function (c) {
      var on = c.classList.contains('next-selected');
      c.setAttribute('aria-current', on ? 'true' : 'false');
      if (on && closing && closing.getAttribute('src') !== c.getAttribute('data-sf-image')) closing.setAttribute('src', c.getAttribute('data-sf-image'));
    });
  };
  document.addEventListener('click', function (e) {
    var buy = e.target && e.target.closest ? e.target.closest('[data-sf-supply-buy]') : null;
    if (!buy || !e.isTrusted) return;
    var card = buy.closest('[data-sf-supply-card]');
    if (!card || card.classList.contains('next-selected')) return;
    e.preventDefault(); e.stopImmediatePropagation();
    card.click();
    setTimeout(function () { buy.click(); }, 80);
  }, true);
  cards.forEach(function (card) {
    new MutationObserver(mark).observe(card, { attributes: true, attributeFilter: ['class'] });
  });
  mark();
})();
