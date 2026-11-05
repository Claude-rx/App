/* GENERATED from _shared/analytics/js/axon.adapter.js — edit the source and run `npm run sync:shared`. Do not edit this copy. */
/* SKINOFAB LOCAL PATCH (29 Oct 2026): mapItems() sends item_category_id only when numeric (Axon answered 400 to the
   SDK's text category). tools/funnel/apf/check_apf.py and tools/funnel/check_funnel.py fail a build without it. */
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
 * Enhanced matching (`user_data` hashed email/phone) is NOT sent — see README (needs hashing+consent).
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
    // LOCAL PATCH (speed pass, 5 Nov 2026): no dl_user_data -> page_view. The head's base code sends page_view the
    // moment the page starts (_includes/sf-axon-first.html); the SDK's dl_user_data came seconds later, after visitors
    // who had already left (one page_view per page either way)
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

  // LOCAL PATCH over the generated copy (keep it when re-syncing), 4 Nov 2026, AppLovin's Pixel Helper: Axon requires
  // item_variant_id, image_url (.png, .jpg or .jpeg) and an integer item_category_id (a Google product category) on every
  // item. The SDK's image is the campaign's .webp thumbnail and its item_category is the campaign's name, so both come
  // from SKINOFAB's catalogue here, by SKU: 2765 Foundations & Concealers, 543597 Manual Massage Tools (the brush), each
  // product's own photo from the store.
  var MEDIA = 'https://cdn.29next.store/media/skinofab/images/products/2026/10/';
  var CATALOG = [
    { sku: /^SKF-LYB/, category: 543597, image: MEDIA + 'card-642f9f.jpg' },
    { sku: /^SKF-AFS/, category: 2765, image: MEDIA + 'duo-ends-1743e5.jpg' },
    { sku: /./, category: 2765, image: MEDIA + '01-front-a241ad.jpg' }
  ];
  function catalog(it) {
    var key = String(it.item_sku || it.item_id || '');
    for (var i = 0; i < CATALOG.length; i++) if (CATALOG[i].sku.test(key)) return CATALOG[i];
    return CATALOG[CATALOG.length - 1];
  }

  // Map an SDK EcommerceItem to Axon's item object (mostly GA4-shaped; a couple of renames).
  function mapItems(items) {
    return (items || []).map(function (it) {
      var out = {}, cat = catalog(it);
      if (it.item_id !== undefined && it.item_id !== null && it.item_id !== '') out.item_id = it.item_id;
      if (it.item_name) out.item_name = it.item_name;
      if (it.price !== undefined && it.price !== null) out.price = it.price;
      if (it.quantity !== undefined && it.quantity !== null) out.quantity = it.quantity;
      if (it.item_brand) out.item_brand = it.item_brand;
      out.item_variant_id = String(it.item_variant_id || it.item_id || '');
      // Axon: item_category_id is an integer id. The SDK's item_category is the campaign's name, which Axon rejects
      // with HTTP 400 for the whole event (view_item, begin_checkout, purchase: live review 6, 29 Oct 2026): a whole
      // number is kept, anything else gets the product's Google category.
      out.item_category_id = (it.item_category !== undefined && it.item_category !== null && /^\d+$/.test(String(it.item_category))) ? Number(it.item_category) : cat.category;
      out.image_url = it.item_image && /\.(png|jpe?g)(\?|$)/i.test(String(it.item_image)) ? it.item_image : cat.image;   // Axon: image_url
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
      window.axon('track', name, params);
    }
  });
})();
