/* GRO: who this browser is, for AppLovin's user_data. Inlined right after the Axon base code on every funnel page
 * (build_checkout.py -> _includes/analytics-head.html, build_lp.py, replica/build_replica.mjs). Edit this file only.
 *
 * AppLovin wants user_data on events: user_id (at least 6 characters), email, phone (digits with country code).
 *   - user_id: a random first-party id kept in localStorage (gro_uid), the same on every event of the journey, from
 *     the first page view to the last offer-page purchase.
 *   - email / phone: what the shopper gave at checkout, remembered for this tab (sessionStorage) so the purchases
 *     recorded on the offer pages and the events on the thank-you page carry them too. The SDK's own upsell events
 *     arrive without them.
 * Everything here is off unless the campaign sets axon_send_user_data: "true" (window.__axonSendUserData === true). */
(function (w) {
  var K = 'gro_axon_user', I = 'gro_uid', mem = {};
  function rid() {
    var a = '';
    try { var b = new Uint8Array(8); crypto.getRandomValues(b); for (var i = 0; i < 8; i++) a += (b[i] < 16 ? '0' : '') + b[i].toString(16); }
    catch (e) { a = Math.random().toString(16).slice(2, 10) + Date.now().toString(16).slice(-8); }
    return 'gro-' + a;
  }
  function uid() {
    try { var v = localStorage.getItem(I); if (!v || v.length < 6) { v = rid(); localStorage.setItem(I, v); } return v; }
    catch (e) { return mem.id || (mem.id = rid()); }
  }
  function saved() {
    try { var o = JSON.parse(sessionStorage.getItem(K) || '{}'); return o && typeof o === 'object' ? o : {}; }
    catch (e) { return mem.u || {}; }
  }
  w.groAxonUser = {
    // { user_id[, email][, phone] } or undefined when user data is switched off for the campaign
    get: function () {
      if (w.__axonSendUserData !== true) return undefined;
      var o = { user_id: uid() }, s = saved();
      if (s.email) o.email = s.email;
      if (s.phone) o.phone = s.phone;
      return o;
    },
    remember: function (u) {
      if (w.__axonSendUserData !== true || !u) return;
      var s = saved(), changed = false;
      if (u.email && u.email !== s.email) { s.email = u.email; changed = true; }
      if (u.phone && u.phone !== s.phone) { s.phone = u.phone; changed = true; }
      if (!changed) return;
      mem.u = s;
      try { sessionStorage.setItem(K, JSON.stringify(s)); } catch (e) { /* private mode: this page only */ }
    }
  };
})(window);
