// MedicLab: the monthly plan's terms sit next to the submit button and must be accepted (auto-renewal disclosure and
// affirmative consent). They show, and the checkbox is required, only while the "plan" bundle card is selected; the
// one-bottle card is a one-time purchase and needs no consent. The check runs in the capture phase, before the SDK's
// own submit handler, so an unticked box stops the order before any payment request.
(function () {
  var box = document.querySelector('[data-ml-plan-terms]');
  var tick = document.querySelector('[data-ml-plan-consent]');
  var err = document.querySelector('[data-ml-consent-error]');
  var form = document.querySelector('form[data-next-checkout="form"]');
  if (!box || !tick || !form) return;

  function planCard() { return document.querySelector('[data-next-bundle-card][data-next-bundle-id="plan"]'); }
  function planSelected() {
    var c = planCard();
    if (!c) return false;
    return c.classList.contains('next-selected') || c.getAttribute('data-next-selected') === 'true';
  }
  function render() {
    var on = planSelected();
    box.hidden = !on;
    if (!on && err) err.hidden = true;
  }
  function blocked() {
    if (!planSelected() || tick.checked) return false;
    if (err) err.hidden = false;
    box.scrollIntoView({ behavior: 'smooth', block: 'center' });
    tick.focus();
    return true;
  }
  function guard(e) {
    if (blocked()) { e.preventDefault(); e.stopImmediatePropagation(); }
  }
  form.addEventListener('submit', guard, true);
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('form[data-next-checkout="form"] [type="submit"], form[data-next-checkout="form"] [data-action="submit"]');
    if (b) guard(e);
  }, true);
  tick.addEventListener('change', function () { if (tick.checked && err) err.hidden = true; });

  var sel = document.querySelector('[data-next-bundle-selector]');
  if (sel && 'MutationObserver' in window) {
    new MutationObserver(render).observe(sel, { subtree: true, attributes: true, attributeFilter: ['class', 'data-next-selected'] });
  }
  document.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[data-next-bundle-card]')) setTimeout(render, 0); });
  render();
  window.addEventListener('load', render);
})();
