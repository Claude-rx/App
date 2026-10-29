// A special offer's countdown (sf-upsell-hero.html, [data-sf-timer]): an honest clock. The deadline is set the first
// time she sees the page for this order and kept in localStorage (sessionStorage when that is blocked), so a reload, a
// Back or a new tab does not restart it (live review 9); at 0:00 the page declines the offer itself (the SDK's own
// skip action, which goes where a decline goes, with her order reference) and the offer is gone, as the line under
// the clock says. An offer whose decline leads to its downsell goes past it (data-sf-timer-to): waiting out the clock
// is never the way to the lower price (live review 9). If she is accepting when the clock runs out
// (she pressed the button in the last seconds), the page waits for the SDK to finish rather than pull the offer away.
(function () {
  'use strict';
  var box = document.querySelector('[data-sf-timer]');
  if (!box) return;
  var secs = parseInt(box.getAttribute('data-sf-timer'), 10) || 600;
  var ref = '';
  try { ref = new URLSearchParams(location.search).get('ref_id') || ''; } catch (e) {}
  var key = 'sf-timer:' + location.pathname + ':' + ref;
  var deadline = 0;
  var store = null;
  try { store = window.localStorage; store.setItem('sf-t', '1'); store.removeItem('sf-t'); } catch (e) { try { store = window.sessionStorage; } catch (e2) { store = null; } }
  try { deadline = parseInt(store && store.getItem(key), 10) || 0; } catch (e) {}
  if (!deadline) {
    deadline = Date.now() + secs * 1000;
    try { if (store) store.setItem(key, String(deadline)); } catch (e) {}
  }
  var past = box.getAttribute('data-sf-timer-to') || '';          // past the downsell, at 0:00
  var displays = box.querySelectorAll('[data-sf-timer-display]');
  var acceptAt = 0, left = false;
  // she pressed an accept (the offer's own, a closing-card proxy, a supply card's Buy now): give the SDK 20 s
  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('[data-next-upsell-action="add"], [data-upsell-proxy="add"], [data-sf-supply-buy]') : null;
    if (t) acceptAt = Date.now();
  }, true);
  var decline = function () {
    var meta = document.querySelector('meta[name="next-upsell-decline-url"]');
    return meta ? meta.getAttribute('content') : '';
  };
  var leave = function () {
    if (left) return;
    if (acceptAt && Date.now() - acceptAt < 20000) return;        // an accept is in flight
    left = true;
    document.documentElement.classList.add('sf-skipping');
    if (past) { location.replace(past + location.search); return; }
    var skip = document.querySelector('[data-next-upsell="offer"] [data-next-upsell-action="skip"]');
    if (skip && window.next) skip.click();
    // the SDK's skip navigates; if it has not within 3 s (not loaded, or an error), go the same way ourselves
    setTimeout(function () { var d = decline(); if (d) location.replace(d + location.search); }, skip && window.next ? 3000 : 0);
  };
  var tick = function () {
    var s = Math.max(0, Math.round((deadline - Date.now()) / 1000));
    var m = Math.floor(s / 60), r = s % 60;
    var text = (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
    displays.forEach(function (d) { if (d.textContent !== text) d.textContent = text; });
    box.classList.toggle('is-ending', s <= 60);
    if (s <= 0) leave();
  };
  tick();
  setInterval(tick, 1000);
})();
