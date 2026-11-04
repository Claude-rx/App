// The order summary's toggle (checkout and thank-you page) names the panel it opens. The SDK (0.4.43,
// accordion.enhancer.ts) sets the toggle's aria-controls to the accordion's name, the panel's id to "<name>-content" and
// the panel's aria-labelledby to the name, so the toggle pointed at nothing (live review 14, F7). The pages give the
// toggle the name as its id (the panel is then labelled by its toggle) and the panel the id the SDK gives it; each time
// the SDK writes aria-controls, it is pointed back at the panel's id.
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('[data-next-accordion-trigger]'), function (trig) {
    var name = trig.getAttribute('data-next-accordion-trigger');
    var panel = document.querySelector('[data-next-accordion-panel="' + name + '"]');
    if (!panel) return;
    var fix = function () { if (panel.id && trig.getAttribute('aria-controls') !== panel.id) trig.setAttribute('aria-controls', panel.id); };
    new MutationObserver(fix).observe(trig, { attributes: true, attributeFilter: ['aria-controls'] });
    new MutationObserver(fix).observe(panel, { attributes: true, attributeFilter: ['id'] });
    fix();
  });
})();
