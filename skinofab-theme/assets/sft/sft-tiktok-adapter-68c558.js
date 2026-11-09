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
  // The identity is kept for the rest of the visit (sessionStorage sf_ttq_am, as SHA-256 hashes; city, state and country
  // as TikTok takes them): the SDK stops carrying the buyer's details after the order, so without it the offer pages'
  // Purchase went with no email (live test order 102182, 9 Nov 2026). Every page re-identifies from it first.
  var AM_KEY = 'sf_ttq_am', HASHED = ['email', 'phone_number', 'first_name', 'last_name', 'zip_code', 'external_id'];
  function saved() { try { return JSON.parse(window.sessionStorage.getItem(AM_KEY) || 'null'); } catch (e) { return null; } }
  function sha(v) {
    return window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(v)).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    });
  }
  function remember(id) {
    if (!(window.crypto && window.crypto.subtle && window.TextEncoder)) return;
    var keep = saved() || {}, jobs = [];
    Object.keys(id).forEach(function (k) {
      if (HASHED.indexOf(k) < 0) { keep[k] = id[k]; return; }
      jobs.push(sha(id[k]).then(function (h) { keep[k] = h; }));
    });
    Promise.all(jobs).then(function () {
      try { window.sessionStorage.setItem(AM_KEY, JSON.stringify(keep)); } catch (e) {}
      // external_id goes only hashed (the pixel sends that field as given)
      if (keep.external_id && id.external_id) window.ttq.identify({ external_id: keep.external_id });
    }).catch(function () {});
  }
  // TikTok's email rules (its pixel labelled a typed Gmail address "invalid: address_format" and suggested the hash of
  // the address without its dots, 9 Nov 2026): trimmed, lowercased, and for gmail.com / googlemail.com no dots and no
  // "+tag" in the name part; a placeholder ("null", "undefined", example.com) or a malformed address is not sent at all
  function normEmail(v) {
    var e = String(v || '').trim().toLowerCase();
    var at = e.lastIndexOf('@');
    if (at < 1 || at === e.length - 1) return '';
    var local = e.slice(0, at), dom = e.slice(at + 1);
    if (!/^[^\s@]+$/.test(local) || !/^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(dom)) return '';
    if (/^(null|undefined|none|test)$/.test(local) || /(^|\.)example\.(com|org|net)$/.test(dom)) return '';
    if (dom === 'gmail.com' || dom === 'googlemail.com') local = local.split('+')[0].replace(/\./g, '');
    return local ? local + '@' + dom : '';
  }
  function e164(p) {
    var d = String(p || '').replace(/[^\d+]/g, '');
    if (!d) return '';
    if (d.charAt(0) === '+') return d;
    if (d.length === 10) return '+1' + d;
    if (d.length === 11 && d.charAt(0) === '1') return '+' + d;
    return '+' + d;
  }
  function identify(u) {
    if (!window.ttq || !window.ttq.identify) return;
    u = u || {};
    var email = normEmail(u.customer_email || u.email);
    var phone = e164(u.customer_phone || u.phone);
    if (!email && !phone) {                       // this event knows no buyer: the one kept from earlier in the visit
      var kept = saved();
      if (kept && (kept.email || kept.phone_number) && lastId !== 'kept') { lastId = 'kept'; window.ttq.identify(kept); }
      return;
    }
    var id = {};
    if (email) id.email = email;
    if (phone) id.phone_number = phone;
    var more = { first_name: u.customer_first_name, last_name: u.customer_last_name, city: u.customer_city,
      state: u.customer_province_code || u.customer_province, country: u.customer_country, zip_code: u.customer_zip };
    Object.keys(more).forEach(function (k) { var v = more[k]; if (v) id[k] = String(v).trim().toLowerCase(); });
    var key = JSON.stringify(id);
    if (key === lastId) return;
    lastId = key;
    window.ttq.identify(id);                      // the pixel hashes these before they leave the browser
    var ext = String(u.customer_id || email || '').trim().toLowerCase();
    var all = {}; Object.keys(id).forEach(function (k) { all[k] = id[k]; });
    if (ext) all.external_id = ext;
    remember(all);
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

  if (ADV_MATCHING && window.__tiktokPixelId) identify(null);
  window.NextForwarder.register(reg);
})();
