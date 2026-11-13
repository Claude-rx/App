/* Based on the starter's GENERATED _shared/analytics/js/axon.adapter.js (copy kept at tools/funnel/getridof/axon.adapter.starter.js).
 * Get Rid Of changes (marked GRO): user_data on every event that has it, phone_last10_hashed, per-package category ids,
 * a .png image_url fallback. Re-apply them if the starter copy is ever re-synced. */
/**
 * axon.adapter.js — AppLovin Axon adapter for next-forwarder-core.js (Route C, no GTM).
 *
 * Maps the SDK's dl_* stream to Axon's standard events and sends them with axon('track', …).
 * Generic plumbing (hook, consent ordering, dedup, replay, _willRedirect, page_view, event toggles)
 * lives in next-forwarder-core.js — this file is pure Axon mapping.
 *
 * Load order (all gated on campaign.axon_event_key, on EVERY page incl. receipt/upsell):
 *   1. Axon base code (analytics-head.snippet.html) — defines window.axon + sets window.__axonEventKey
 *   2. next-forwarder-core.js
 *   3. this file
 *
 * Axon specifics that differ from GA4:
 *   - FIXED standard-event list — no custom events. So upsells map to `purchase` (Approach B): each
 *     accepted upsell fires another purchase with a distinct `{orderId}-US{n}` transaction_id. Value
 *     is accurate; purchase COUNT inflates (N upsells = N+1) — brief the media buyer before reading AOV.
 *   - `purchase` REQUIRES currency, items, value, tax, shipping, transaction_id (SDK provides all;
 *     upsells carry tax:0/shipping:0).
 *   - Identifier is an EVENT KEY, not a pixel id.
 *   - item_category_id is an INTEGER category id. The SDK's item_category is the campaign NAME, which
 *     Axon rejects with HTTP 400 — so it is sent only when it is a positive integer, else the campaign's
 *     window.__axonItemCategoryId (campaigns.json axon_item_category_id), else left out.
 *   - image_url must end in .png/.jpg/.jpeg; the SDK's .webp package thumbnails are dropped.
 *   - payment_type is an enum (credit_card / redeemable / deferred / payment_on_delivery / wallet / other);
 *     the SDK's labels ("Credit Card", "Apple Pay", …) are mapped onto it.
 * Enhanced matching: `user_data` (email, phone, user_id) goes on the order and upsell `purchase` only, and
 * only when window.__axonSendUserData === true (campaigns.json axon_send_user_data: "true"). OFF by default,
 * like the applovin-axon storefront app: turn it on only when the store's consent policy covers sharing it
 * with AppLovin. The flag is read on every event, so a consent script can set it. Axon's pixel.js hashes
 * email/phone in the browser, so they are passed normalised but unhashed. Not gated on accepts_marketing.
 * Upsell purchases: the SDK builds dl_upsell_purchase's user_properties from checkout state it resets before
 * the post-checkout redirect, so they arrive with visitor_type only. The page's own dl_user_data (fired
 * first on every page, from the SDK's persisted user data) still carries the email, so an upsell purchase
 * fills any field it lacks from it. It is read from window.NextDataLayer at that moment, only with the flag
 * on, so it works whatever axon_allowed_events / axon_blocked_events say and the adapter keeps no PII.
 *
 * Debug: ?nfdebug=true or localhost, then window.NextForwarder.getStatus().
 */
(function () {
  'use strict';

  if (!window.NextForwarder) {
    if (window.console) console.warn('[axon.adapter] next-forwarder-core.js must load first');
    return;
  }

  // dl_* event -> Axon standard event name. Axon events are GA4-shaped.
  // Intentionally NOT mapped (no Axon equivalent): dl_view_item_list, dl_select_item, dl_add_shipping_info.
  var MAP = {
    dl_user_data:            'page_view',       // SDK's real pageview signal (see core); sent bare
    dl_view_item:            'view_item',
    dl_add_to_cart:          'add_to_cart',
    dl_remove_from_cart:     'remove_from_cart',
    dl_view_cart:            'view_cart',
    dl_begin_checkout:       'begin_checkout',
    dl_add_payment_info:     'add_payment_info',
    dl_view_search_results:  'search',          // Axon uses `search` with `search_term`
    dl_subscribe:            'subscribe',
    dl_purchase:             'purchase',
    dl_upsell_purchase:      'purchase',         // Approach B — Axon has no custom events (see header)
    dl_login:                'login',
    dl_sign_up:              'sign_up'
  };

  // Event-level params Axon accepts per event (beyond currency/value/items). purchase requires
  // tax+shipping; the SDK always provides them (0 on upsells), so they're always present.
  var EXTRA = {
    purchase:         ['transaction_id', 'tax', 'shipping'],
    add_payment_info: ['payment_type'],
    search:           ['search_term']
  };

  var DEBUG = /[?&]nfdebug=true/.test(window.location.search) ||
    /^(localhost|127\.0\.0\.1)$/.test(window.location.hostname);
  var warnedUserData = false;

  var EMAIL_RE = window.NextForwarder.EMAIL_RE || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  // email trimmed + lowercased; phone as E.164 digits without '+' (the SDK only sets E.164 with '+');
  // user_id only when >= 6 chars. Undefined when none of the three is usable.
  function userData(evt) {
    var up = (evt && evt.user_properties) || {};
    var out = {};
    var email = typeof up.customer_email === 'string' ? up.customer_email.trim().toLowerCase() : '';
    if (EMAIL_RE.test(email)) out.email = email;
    var phone = typeof up.customer_phone === 'string' ? up.customer_phone.replace(/[\s().-]/g, '') : '';
    if (/^\+[1-9]\d{7,14}$/.test(phone)) out.phone = phone.slice(1);
    var id = up.customer_id !== undefined && up.customer_id !== null ? String(up.customer_id).trim() : '';
    // GRO: Axon wants user_id >= 6 chars; store customer ids are short (e.g. 133), so send a stable prefixed id
    if (id && id !== '0' && id.length < 6) id = 'getridof-' + id;
    if (id.length >= 6) out.user_id = id;
    return out.email || out.phone || out.user_id ? out : undefined;
  }

  // The shopper as this page's latest usable dl_user_data reported it. The SDK pushes dl_user_data to
  // window.NextDataLayer before it replays the queued dl_upsell_purchase, whose own user_properties come from
  // already-reset checkout state. NextDataLayer holds every event that survived the consent transform,
  // whether or not this adapter forwarded it.
  function pageUserData() {
    var dl = window.NextDataLayer;
    if (!dl || typeof dl.length !== 'number') return undefined;
    for (var i = dl.length - 1; i >= 0; i--) {
      var user = dl[i] && dl[i].event === 'dl_user_data' ? userData(dl[i]) : undefined;
      if (user) return user;
    }
    return undefined;
  }

  // Per field: the event's own value wins, the page fills the gaps.
  function mergeUser(page, own) {
    if (!page) return own;
    var out = {}, k;
    for (k in page) out[k] = page[k];
    for (k in own || {}) out[k] = own[k];
    return out;
  }

  // GRO: SHA-256 (hex), synchronous so events keep their order; used for phone_last10_hashed only
  function sha256(ascii) {
    function r(v, n) { return (v >>> n) | (v << (32 - n)); }
    var K = [], H = [], p = 0, c = 2, i, j, w, a, b, t1, t2;
    for (; p < 64; c++) { for (i = 2; i * i <= c; i++) if (c % i === 0) break; if (i * i > c) { if (p < 8) H[p] = (Math.pow(c, .5) * 4294967296) | 0; K[p++] = (Math.pow(c, 1 / 3) * 4294967296) | 0; } }
    var words = [], bits = ascii.length * 8;
    ascii += '\x80'; while (ascii.length % 64 - 56) ascii += '\x00';
    for (i = 0; i < ascii.length; i++) words[i >> 2] |= ascii.charCodeAt(i) << ((3 - i) % 4) * 8;
    words[words.length] = (bits / 4294967296) | 0; words[words.length] = bits;
    for (j = 0; j < words.length;) {
      w = words.slice(j, j += 16); var h = H.slice(0);
      for (i = 0; i < 64; i++) {
        if (i >= 16) { var w15 = w[i - 15], w2 = w[i - 2]; w[i] = (w[i - 16] + (r(w15, 7) ^ r(w15, 18) ^ (w15 >>> 3)) + w[i - 7] + (r(w2, 17) ^ r(w2, 19) ^ (w2 >>> 10))) | 0; }
        a = h[0]; b = h[4];
        t1 = h[7] + (r(b, 6) ^ r(b, 11) ^ r(b, 25)) + ((b & h[5]) ^ (~b & h[6])) + K[i] + w[i];
        t2 = (r(a, 2) ^ r(a, 13) ^ r(a, 22)) + ((a & h[1]) ^ (a & h[2]) ^ (h[1] & h[2]));
        h = [(t1 + t2) | 0].concat(h); h[4] = (h[4] + t1) | 0; h.length = 8;
      }
      for (i = 0; i < 8; i++) H[i] = (H[i] + h[i]) | 0;
    }
    var out = ''; for (i = 0; i < 8; i++) for (j = 3; j + 1; j--) { var bt = (H[i] >> (j * 8)) & 255; out += (bt < 16 ? '0' : '') + bt.toString(16); }
    return out;
  }
  // GRO: AppLovin's phone_last10_hashed: last 10 digits, no country code, SHA-256 hex; only for >= 10 digits
  function withLast10(user) {
    if (user && user.phone && !user.phone_last10_hashed) {
      var d = String(user.phone).replace(/\D/g, '');
      if (d.length >= 10) user.phone_last10_hashed = sha256(d.slice(-10));
    }
    return user;
  }
  // GRO: category per product, keyed by the SDK's item_id (SKU) or item_variant_id (campaigns.json axon_category_by_package)
  var categoryByPackage = {};
  String(window.__axonCategoryByPackage || '').split(',').forEach(function (pair) {
    var kv = pair.split(':'); if (kv.length === 2 && /^\d+$/.test(kv[1].trim())) categoryByPackage[kv[0].trim()] = Number(kv[1].trim());
  });
  // GRO: Axon needs .png/.jpg; the campaign's package images are .webp, so a .png product shot stands in
  var fallbackImage = String(window.__axonImageUrl || '');

  // item_category_id: a positive integer or nothing.
  function categoryId(raw) {
    var s = raw === undefined || raw === null ? '' : String(raw).trim();
    return /^\d+$/.test(s) && Number.isSafeInteger(Number(s)) && Number(s) > 0 ? Number(s) : undefined;
  }
  var fallbackCategoryId = categoryId(window.__axonItemCategoryId);

  var IMAGE_RE = /^https?:\/\/[^\s?#]+\.(png|jpe?g)(?:[?#].*)?$/i;

  // Axon payment_type enum; the SDK sends display labels (paymentMethodLabel). Unknown labels → 'other'.
  var PAYMENT_TYPES = { credit_card: 1, redeemable: 1, deferred: 1, payment_on_delivery: 1, wallet: 1, other: 1 };
  var PAYMENT_TYPE_BY_KEY = {
    creditcard: 'credit_card', card: 'credit_card', cardtoken: 'credit_card', savedcard: 'credit_card', debitcard: 'credit_card',
    applepay: 'wallet', googlepay: 'wallet', paypal: 'wallet', shoppay: 'wallet', link: 'wallet', swish: 'wallet', twint: 'wallet',
    venmo: 'wallet', amazonpay: 'wallet', cashapp: 'wallet',
    klarna: 'deferred', affirm: 'deferred', afterpay: 'deferred', clearpay: 'deferred', sezzle: 'deferred', zip: 'deferred',
    giftcard: 'redeemable', voucher: 'redeemable', storecredit: 'redeemable',
    cashondelivery: 'payment_on_delivery', cod: 'payment_on_delivery'
  };
  function paymentType(raw) {
    var s = String(raw).trim();
    if (PAYMENT_TYPES[s]) return s;
    return PAYMENT_TYPE_BY_KEY[s.toLowerCase().replace(/[^a-z]/g, '')] || 'other';
  }

  // Map an SDK EcommerceItem to Axon's item object (mostly GA4-shaped; a couple of renames).
  function mapItems(items) {
    return (items || []).map(function (it) {
      var out = {};
      if (it.item_id !== undefined && it.item_id !== null && it.item_id !== '') out.item_id = it.item_id;
      if (it.item_name) out.item_name = it.item_name;
      if (it.price !== undefined && it.price !== null) out.price = it.price;
      if (it.quantity !== undefined && it.quantity !== null) out.quantity = it.quantity;
      out.item_brand = it.item_brand || 'Get Rid Of';                  // GRO: brand on every item
      if (it.item_variant_id) out.item_variant_id = it.item_variant_id;
      var pkg = it.item_id !== undefined && it.item_id !== null ? String(it.item_id) : '';
      var cat = categoryId(it.item_category) || categoryByPackage[pkg] || categoryByPackage[String(it.item_variant_id || '')] || fallbackCategoryId;
      if (cat) out.item_category_id = cat;                            // Axon: integer item_category_id
      if (typeof it.item_image === 'string' && IMAGE_RE.test(it.item_image)) out.image_url = it.item_image;
      else if (IMAGE_RE.test(fallbackImage) && /^GRO-MOUSE-/.test(String(it.item_id || ''))) out.image_url = fallbackImage;  // GRO: pouch photo, pouch SKUs only
      if (it.discount !== undefined && it.discount !== null && it.discount !== '') out.discount = it.discount;
      return out;
    });
  }

  function copy(from, to, keys) {
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (from[k] !== undefined && from[k] !== null && from[k] !== '') to[k] = from[k];
    }
  }

  // Per-campaign event toggles (comma-separated dl_* or Axon names from campaigns.json).
  function parseList(raw) {
    return (raw || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean);
  }
  var blocked = parseList(window.__axonBlockedEvents);
  var allowedRaw = parseList(window.__axonAllowedEvents);
  // allowlist: "" / absent → default main events; "all"/"*" → every mapped event; else the given subset.
  var allowed = (allowedRaw.length === 1 && (allowedRaw[0] === 'all' || allowedRaw[0] === '*'))
    ? null
    : (allowedRaw.length ? allowedRaw : window.NextForwarder.DEFAULT_MAIN_EVENTS);

  window.NextForwarder.register({
    name: 'axon',
    isActive: function () {
      return !!window.__axonEventKey && typeof window.axon === 'function';
    },
    map: MAP,
    allowedEvents: allowed,
    blockedEvents: blocked,
    send: function (name, ec, evt) {
      // page_view is not an ecommerce event; it carries user_data only (GRO), once the shopper is known.
      if (name === 'page_view') {
        var pvUser = window.__axonSendUserData === true ? withLast10(mergeUser(pageUserData(), userData(evt))) : undefined;
        if (pvUser) window.axon('track', 'page_view', { user_data: pvUser }); else window.axon('track', 'page_view');
        return;
      }

      var params = {};
      if (ec.currency) params.currency = ec.currency;
      if (ec.value !== undefined && ec.value !== null) params.value = ec.value;

      var items = mapItems(ec.items);
      if (items.length) params.items = items;

      // search_term lives on the envelope for dl_view_search_results
      if (name === 'search' && evt.search_term) params.search_term = evt.search_term;

      copy(ec, params, EXTRA[name] || []);
      if (params.payment_type !== undefined) params.payment_type = paymentType(params.payment_type);
      var user;
      if (window.__axonSendUserData === true) {
        // GRO: every event, not only purchase. The event's own fields win; the page's latest dl_user_data fills gaps.
        user = withLast10(mergeUser(pageUserData(), userData(evt)));
      }
      if (user) params.user_data = user;
      if (name === 'purchase') {
        // GRO: discount_applications (Axon: "pass an empty array when no promotions applied")
        var apps = [], seen = {};
        String(ec.coupon || '').split(',').forEach(function (c) { c = c.trim(); if (c && !seen[c]) { seen[c] = 1; apps.push({ code: c, title: 'Promo code ' + c }); } });
        var offerDiscount = (ec.items || []).some(function (it) { return Number(it && it.discount) > 0; });
        if (offerDiscount && !apps.length) apps.push({ title: 'Get Rid Of offer discount' });
        params.discount_applications = apps;
        if (!user && DEBUG && !warnedUserData && window.console) {
          warnedUserData = true;
          console.warn('[axon.adapter] purchase sent without user_data (' +
            (window.__axonSendUserData === true ? 'no usable email, phone or customer_id' : 'axon_send_user_data is off') + ')');
        }
      }
      window.axon('track', name, params);
    }
  });
})();
