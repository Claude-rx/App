/* GENERATED from _shared/analytics/js/axon.adapter.js — edit the source and run `npm run sync:shared`. Do not edit this copy. */
/* SKINOFAB LOCAL PATCH (29 Oct 2026): mapItems() sends item_category_id only when numeric (Axon answered 400 to the
   SDK's text category). tools/funnel/apf/check_apf.py and tools/funnel/check_funnel.py fail a build without it.
   SKINOFAB LOCAL PATCH (29 Oct 2026): user_data (email/phone/user_id) is sent on checkout and purchase events from the
   SDK's user_properties — AXON flags purchase without user_data as an error. Keep it when re-syncing.
   SKINOFAB LOCAL PATCH (30 Oct 2026): AXON requires a numeric item_category_id on every item (Pixel Helper warns once
   per item without it). Falls back to window.__axonItemCategoryId, else 2765 (Google product taxonomy: Health & Beauty >
   Personal Care > Cosmetics > Makeup > Face Makeup > Foundations & Concealers). Keep it when re-syncing.
   SKINOFAB LOCAL PATCH (30 Oct 2026): image_url must end in .png/.jpg/.jpeg (AXON Pixel Helper structures.yaml); the
   SDK sends .webp thumbnails, so each variant maps to its store JPG. item_brand defaults to SKINOFAB, and user_data rides
   on every ecommerce event once the shopper is known. Keep it when re-syncing.
   SKINOFAB LOCAL PATCH (30 Oct 2026): payment_type is mapped to AXON's enum (credit_card / redeemable / deferred /
   payment_on_delivery / wallet / other); the SDK sends labels like "Credit Card". Items without item_variant_id (an
   upsell the SDK builds from the package) get it, and their image, from the SKU. Keep it when re-syncing. */
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
 * Enhanced matching: `user_data` is sent on USER_DATA_EVENTS from the SDK's user_properties (customer_email,
 * customer_phone, customer_id). AXON's pixel.js hashes email/phone in the browser before sending, so they are
 * passed in plaintext: email trimmed + lowercased, phone as E.164 digits without '+', user_id only when >= 6 chars.
 * Disable per campaign with window.__axonSendUserData = false.
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

  // Events that carry user_data when the shopper is known (AXON: required on purchase, optional elsewhere). It is
  // only ever the shopper's own email/phone/id, so it rides on every ecommerce event; page_view stays bare.
  var USER_DATA_EVENTS = { purchase: 1, begin_checkout: 1, add_payment_info: 1, view_item: 1, add_to_cart: 1,
    remove_from_cart: 1, view_cart: 1, subscribe: 1, login: 1, sign_up: 1, search: 1 };

  function userData(evt) {
    if (window.__axonSendUserData === false || window.__axonSendUserData === 'false') return undefined;
    var up = (evt && evt.user_properties) || {};
    var out = {};
    var email = typeof up.customer_email === 'string' ? up.customer_email.trim().toLowerCase() : '';
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) out.email = email;
    var phone = typeof up.customer_phone === 'string' ? up.customer_phone.replace(/[\s()-]/g, '') : '';
    if (/^\+[1-9]\d{7,14}$/.test(phone)) out.phone = phone.slice(1);
    var id = up.customer_id !== undefined && up.customer_id !== null ? String(up.customer_id) : '';
    if (id.length >= 6) out.user_id = id;
    return out.email || out.phone ? out : undefined;
  }

  // AXON item_category_id: an integer from Google's product taxonomy, required on every item.
  var DEFAULT_ITEM_CATEGORY_ID = 2765; // Foundations & Concealers — both SKINOFAB funnels sell foundation
  function categoryId(raw) {
    var s = raw === undefined || raw === null ? '' : String(raw).trim();
    return /^\d+$/.test(s) && Number(s) > 0 ? Number(s) : undefined;
  }
  var fallbackCategoryId = categoryId(window.__axonItemCategoryId) || DEFAULT_ITEM_CATEGORY_ID;

  // AXON image_url must be a .png/.jpg/.jpeg URL (Pixel Helper warns on anything else). The SDK's package images are
  // .webp thumbnails, so each store variant maps to its product's JPG on the store CDN (Admin API, 30 Oct 2026).
  var IMAGE_RE = /^https?:\/\/(?:[\w-]+\.)+[\w-]+(?:\/[\w-./?%&=]*)?\.(png|jpe?g)(?:[?#].*)?$/i;
  var IMAGE_BY_VARIANT = {
    "15":"https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg",
    "103":"https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg",
    "268":"https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg",
    "269":"https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg",
    "270":"https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg",
    "301":"https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-a241ad.jpg",
    "170":"https://cdn.29next.store/media/skinofab/images/products/2026/10/card-642f9f.jpg",
    "171":"https://cdn.29next.store/media/skinofab/images/products/2026/10/card-642f9f.jpg",
    "172":"https://cdn.29next.store/media/skinofab/images/products/2026/10/card-642f9f.jpg",
    "271":"https://cdn.29next.store/media/skinofab/images/products/2026/10/card-642f9f.jpg",
    "203":"https://cdn.29next.store/media/skinofab/images/products/2026/10/hero-f163d1.jpg",
    "204":"https://cdn.29next.store/media/skinofab/images/products/2026/10/hero-f163d1.jpg",
    "205":"https://cdn.29next.store/media/skinofab/images/products/2026/10/hero-f163d1.jpg",
    "207":"https://cdn.29next.store/media/skinofab/images/products/2026/10/card-97ecd1.jpg",
    "208":"https://cdn.29next.store/media/skinofab/images/products/2026/10/card-97ecd1.jpg",
    "209":"https://cdn.29next.store/media/skinofab/images/products/2026/10/card-97ecd1.jpg",
    "236":"https://cdn.29next.store/media/skinofab/images/products/2026/10/duo-ends-1743e5.jpg",
    "237":"https://cdn.29next.store/media/skinofab/images/products/2026/10/duo-ends-1743e5.jpg"
  };
  function imageUrl(it) {
    if (typeof it.item_image === 'string' && IMAGE_RE.test(it.item_image)) return it.item_image;
    var v = variantId(it);
    var mapped = v ? IMAGE_BY_VARIANT[v] : undefined;
    if (mapped) return mapped;
    var fallback = window.__axonItemImage;
    return typeof fallback === 'string' && IMAGE_RE.test(fallback) ? fallback : undefined;
  }
  // An upsell item the SDK builds from the package carries the SKU as item_id but no item_variant_id.
  var VARIANT_BY_SKU = {
    "SKF-APF-1":"15",
    "SKF-APF-2-GIFTS":"103",
    "SKF-APF-3-GIFTS":"268",
    "SKF-APF-2":"269",
    "SKF-APF-6-BRUSH":"270",
    "SKF-APF-1-ADD":"301",
    "SKF-LYB-1":"170",
    "SKF-LYB-2":"171",
    "SKF-LYB-3":"172",
    "SKF-LYB-1T":"271",
    "SKF-PDB-1":"203",
    "SKF-PDB-2":"204",
    "SKF-PDB-3":"205",
    "SKF-ENS-1":"207",
    "SKF-ENS-2":"208",
    "SKF-ENS-3":"209",
    "SKF-AFS-1":"236",
    "SKF-AFS-2":"237"
  };
  function variantId(it) {
    if (it.item_variant_id !== undefined && it.item_variant_id !== null && it.item_variant_id !== '') return String(it.item_variant_id);
    return it.item_id !== undefined && it.item_id !== null ? VARIANT_BY_SKU[String(it.item_id)] : undefined;
  }
  var DEFAULT_BRAND = 'SKINOFAB';

  // AXON payment_type is an enum; the SDK sends display labels (paymentMethodLabel: "Credit Card", "Apple Pay", ...).
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
    if (raw === undefined || raw === null || raw === '') return undefined;
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
      out.item_brand = it.item_brand || window.__axonItemBrand || DEFAULT_BRAND;
      var vid = variantId(it);
      if (vid) out.item_variant_id = vid;
      // Axon: item_category_id is an integer id. The SDK's item_category is the campaign's name, which Axon rejects
      // with HTTP 400 for the whole event (view_item, begin_checkout, purchase: live review 6, 29 Oct 2026), so it is
      // sent only when it is a whole number. LOCAL PATCH over the generated copy: keep it when re-syncing.
      // Otherwise the store-wide fallback, so the required field is never missing.
      out.item_category_id = categoryId(it.item_category) || fallbackCategoryId;
      var img = imageUrl(it);
      if (img) out.image_url = img;                                    // Axon: image_url (.png/.jpg/.jpeg only)
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
      // page_view is not an ecommerce event — send it bare.
      if (name === 'page_view') { window.axon('track', 'page_view'); return; }

      var params = {};
      if (ec.currency) params.currency = ec.currency;
      if (ec.value !== undefined && ec.value !== null) params.value = ec.value;

      var items = mapItems(ec.items);
      if (items.length) params.items = items;

      // search_term lives on the envelope for dl_view_search_results
      if (name === 'search' && evt.search_term) params.search_term = evt.search_term;

      copy(ec, params, EXTRA[name] || []);
      if (params.payment_type !== undefined) params.payment_type = paymentType(params.payment_type);
      if (USER_DATA_EVENTS[name]) {
        var user = userData(evt);
        if (user) params.user_data = user;
      }
      window.axon('track', name, params);
    }
  });
})();
