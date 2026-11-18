/* Corrects mislabeled items in the Campaign Cart SDK's analytics events before any pixel adapter sends them
 * (inlined into analytics-head.html by build_checkout.py, next to axon-user.js).
 * Why: the SDK (v0.4.43) names an event item with packages.find(p => p.ref_id == id || p.external_id == id). In these
 * campaigns package 3 (Package Protection) has external_id 5, and it comes before package 5 (the 3-pack, variant 37), so
 * the 3-pack is reported as "Package Protection" / GRO-PROTECT / variant 5 while its price, quantity and item_sku are the
 * 3-pack's. TikTok and AppLovin then see the wrong product (and AppLovin's category map misses it).
 * Fix: an item whose item_sku differs from its item_id was mislabeled; it takes its name, SKU, product and variant from the
 * campaign package of the matching cart line (same index, else the cart line with that SKU). Nothing else is changed.
 * Registered as the SDK's user transform (the forwarder core runs it before the adapters); the SDK clears that slot when it
 * starts, so it is set again on next:initialized and for the first seconds of the page. */
(function () {
  function fix(evt) {
    try {
      var items = evt && evt.ecommerce && evt.ecommerce.items;
      if (!items || !items.length || !window.next) return evt;
      var camp = window.next.getCampaignData && window.next.getCampaignData();
      var cart = window.next.getCartData && window.next.getCartData();
      var pkgs = (camp && camp.packages) || [], lines = (cart && cart.cartLines) || [];
      items.forEach(function (it, i) {
        if (!it || !it.item_sku || String(it.item_sku) === String(it.item_id)) return;
        var line = lines[typeof it.index === 'number' ? it.index : i];
        if (!line || !line.product || line.product.sku !== it.item_sku) line = lines.filter(function (l) { return l.product && l.product.sku === it.item_sku; })[0];
        var p = line && pkgs.filter(function (k) { return String(k.ref_id) === String(line.packageId); })[0];
        if (!p) { it.item_id = it.item_sku; return; }
        it.item_id = p.product_sku || it.item_sku;
        it.item_name = p.product_name || p.name || it.item_name;
        if (p.product_id !== undefined) it.item_product_id = String(p.product_id);
        if (p.product_variant_id !== undefined) it.item_variant_id = String(p.product_variant_id);
        if (it.item_variant !== undefined && p.product_variant_name) it.item_variant = p.product_variant_name;
      });
    } catch (e) { /* never block the data layer */ }
    return evt;
  }
  window.__groItemsFix = fix;
  function arm() { if (window.NextDataLayerTransformFn !== fix) window.NextDataLayerTransformFn = fix; }
  arm();
  document.addEventListener('next:initialized', arm);
  var n = 0, t = setInterval(function () { arm(); if (++n > 40) clearInterval(t); }, 100);
})();
