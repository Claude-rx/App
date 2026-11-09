/* GENERATED from _shared/analytics/js/tiktok.adapter.js, with SKINOFAB LOCAL PATCHes (9 Nov 2026: identity on every event, typed contents, field-entry contact). */
/**
 * tiktok.adapter.js — TikTok Pixel adapter for next-forwarder-core.js (Route C, no GTM).
 *
 * Maps the SDK's dl_* stream to TikTok events via window.ttq.track(name, props, {event_id}).
 * Generic plumbing (hook, consent ordering, dedup, replay, _willRedirect, toggles, onContact) lives
 * in next-forwarder-core.js — this file is pure TikTok mapping.
 *
 * Load order (all gated on campaign.tiktok_pixel_id, on EVERY page incl. receipt/upsell):
 *   1. TikTok base pixel (analytics-head.snippet.html) — defines window.ttq, fires ttq.page(),
 *      sets window.__tiktokPixelId
 *   2. next-forwarder-core.js
 *   3. this file
 *
 * TikTok specifics:
 *   - Current purchase event is `Purchase` (not the legacy `CompletePayment`).
 *   - Base ttq.page() owns the pageview → dl_user_data NOT mapped (like Taboola).
 *   - Upsell = Approach B: dl_upsell_purchase → `Purchase` with a distinct event_id (`{orderId}-US{n}`),
 *     so upsell revenue counts toward TikTok's Purchase optimization (ROAS). Inflates purchase COUNT
 *     (N upsells = N+1) — brief the media buyer. (TikTok supports custom events, so Approach C is
 *     possible if clean count is preferred over optimization — see README.)
 *   - event_id (3rd arg) enables Pixel + Events-API dedup later; harmless without it.
 *   - Advanced Matching (ttq.identify email/phone) is opt-in via tiktok_advanced_matching_enabled →
 *     the core onContact hook. Default off = zero PII (like GA4/Axon/Taboola).
 *     Keeps the core's DEFAULT contact gate (contactRequiresMarketingConsent true, prospect-cart source
 *     only): TikTok advanced matching is marketing use — it builds the ad platform's identity graph and
 *     audiences — so it stays behind the accepts_marketing checkbox. Attribution vendors (Northbeam,
 *     Triple Whale) opt out of that gate; see next-forwarder-core.js.
 *
 * Debug: ?nfdebug=true or localhost, then window.NextForwarder.getStatus(). QA with TikTok Pixel Helper.
 */
(function () {
  'use strict';

  if (!window.NextForwarder) {
    if (window.console) console.warn('[tiktok.adapter] next-forwarder-core.js must load first');
    return;
  }

  // dl_* -> TikTok standard event. No dl_user_data (base ttq.page() owns pageview). No TikTok standard
  // event for view_cart / view_item_list / select_item / remove_from_cart / add_shipping_info / login.
  var MAP = {
    dl_view_item:            'ViewContent',
    dl_add_to_cart:          'AddToCart',
    dl_begin_checkout:       'InitiateCheckout',
    dl_add_payment_info:     'AddPaymentInfo',
    dl_purchase:             'Purchase',
    dl_upsell_purchase:      'Purchase',         // Approach B — distinct event_id keeps it a separate txn
    dl_view_search_results:  'Search',
    dl_sign_up:              'CompleteRegistration',
    dl_subscribe:            'Subscribe'
  };

  var ADV_MATCHING = /^(true|1|yes)$/i.test(window.__tiktokAdvancedMatching || '');

  function str(v) { return (v === undefined || v === null) ? v : String(v); }

  // SDK items -> TikTok `contents` objects.
  // LOCAL PATCH (SKINOFAB, 9 Nov 2026): every content carries content_type and the brand, and price and quantity go
  // as numbers (TikTok reads a string price as no price).
  function num(v) { var n = parseFloat(v); return isNaN(n) ? undefined : n; }
  function mapContents(items) {
    return (items || []).map(function (it) {
      var c = { content_type: 'product', brand: it.item_brand || 'SKINOFAB' };
      if (it.item_id !== undefined && it.item_id !== null && it.item_id !== '') c.content_id = str(it.item_id);
      if (it.item_name) c.content_name = it.item_name;
      if (it.item_category) c.content_category = it.item_category;
      if (num(it.price) !== undefined) c.price = num(it.price);
      c.quantity = num(it.quantity) || 1;
      return c;
    });
  }

  // LOCAL PATCH (SKINOFAB, 9 Nov 2026: "send all user data"): the buyer's identity on every event that knows it. The
  // SDK puts user_properties (the checkout's email, phone, name, city, state, ZIP, country, customer id) on each dl_*
  // event, on the checkout and after it (the offers, the thank-you page), so the Purchase a redirect leaves on the
  // first offer page is matched too. ttq.identify takes them plain and the pixel SHA-256-hashes them before they leave
  // the browser. Sent once per page per identity.
  var lastId = '';
  function e164(p) {
    var d = String(p || '').replace(/[^\d+]/g, '');
    if (!d) return '';
    if (d.charAt(0) === '+') return d;
    if (d.length === 10) return '+1' + d;
    if (d.length === 11 && d.charAt(0) === '1') return '+' + d;
    return '+' + d;
  }
  function identify(u) {
    if (!u || !window.ttq || !window.ttq.identify) return;
    var email = String(u.customer_email || u.email || '').trim().toLowerCase();
    var phone = e164(u.customer_phone || u.phone);
    if (!email && !phone) return;
    var id = {};
    if (email) id.email = email;
    if (phone) id.phone_number = phone;
    var more = { first_name: u.customer_first_name, last_name: u.customer_last_name, city: u.customer_city,
      state: u.customer_province_code || u.customer_province, country: u.customer_country, zip_code: u.customer_zip };
    Object.keys(more).forEach(function (k) { var v = more[k]; if (v) id[k] = String(v).trim().toLowerCase(); });
    var key = JSON.stringify(id);
    if (key === lastId) return;
    lastId = key;
    window.ttq.identify(id);
    // external_id (the customer id, else the email): the pixel sends it as given, so it is hashed here first
    var ext = String(u.customer_id || email || '').trim().toLowerCase();
    if (ext && window.crypto && window.crypto.subtle && window.TextEncoder) {
      window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(ext)).then(function (buf) {
        var hex = Array.prototype.map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
        window.ttq.identify({ external_id: hex });
      }).catch(function () {});
    }
  }

  // Toggles (comma-separated dl_* or TikTok names).
  function parseList(raw) {
    return (raw || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean);
  }
  var blocked = parseList(window.__tiktokBlockedEvents);
  var allowedRaw = parseList(window.__tiktokAllowedEvents);
  var allowed = (allowedRaw.length === 1 && (allowedRaw[0] === 'all' || allowedRaw[0] === '*'))
    ? null
    : (allowedRaw.length ? allowedRaw : window.NextForwarder.DEFAULT_MAIN_EVENTS);

  var reg = {
    name: 'tiktok',
    isActive: function () {
      return !!window.__tiktokPixelId && !!(window.ttq && window.ttq.track);
    },
    map: MAP,
    allowedEvents: allowed,
    blockedEvents: blocked,
    send: function (name, ec, evt) {
      if (ADV_MATCHING) identify(evt && evt.user_properties);
      var props = { content_type: 'product', currency: ec.currency || 'USD' };
      if (num(ec.value) !== undefined) props.value = num(ec.value); // incremental for upsell
      var contents = mapContents(ec.items);
      if (contents.length) props.contents = contents;
      if (name === 'Purchase' && ec.coupon) props.query = ec.coupon;
      if (name === 'Search' && evt.search_term) props.query = evt.search_term;
      // 3rd arg event_id: transaction_id for purchases ({orderId}-US{n} for upsells), else the SDK id.
      var opts = evt.event_id ? { event_id: evt.event_id } : undefined;
      window.ttq.track(name, props, opts);
    }
  };

  // Advanced Matching (opt-in): fire ttq.identify on the core's onContact (prospect-cart source, default
  // accepts_marketing gate — see header).
  // TikTok links the browser via its cookie, so subsequent Purchase attributes to the matched identity.
  // LOCAL PATCH (SKINOFAB, 9 Nov 2026): the owner's instruction is to send the buyer's data, so the contact is taken as
  // soon as a valid email or phone is in the checkout's fields (contactOnFieldEntry) and is not held behind the
  // newsletter box (contactRequiresMarketingConsent false). Global Privacy Control and the privacy-choices opt-out
  // still stop all of it: the base code defines no pixel then and this adapter stays inactive.
  if (ADV_MATCHING) {
    reg.contactRequiresMarketingConsent = false;
    reg.contactOnFieldEntry = true;
    reg.onContact = function (c) { identify({ email: c.email, phone: c.phone }); };
  }

  window.NextForwarder.register(reg);
})();
