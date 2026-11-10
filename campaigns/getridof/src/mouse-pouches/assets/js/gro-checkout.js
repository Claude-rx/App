/* Get Rid Of checkout: exit-intent offer (GROMOUSE10, 10% off the pouches) from the template in the page. */
window.addEventListener('next:initialized', function () {
  if (typeof initExitIntentTemplate === 'function') initExitIntentTemplate('exit-intent');
});
