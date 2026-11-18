/* TikTok pixel for the lean sales pages (build_lp.py, build_listicle.py, build_nine.py, replica/build_replica.mjs).
 * These pages have no Campaign Cart SDK forwarder, so the page sends its own events; the checkout, offer and thank-you
 * pages use the page kit's tiktok.adapter.js instead (same event names and content shape).
 *   - the official base code; ttq.load + ttq.page wait for the page's load event, so the pixel file never competes with
 *     the first screen (calls made before that wait in ttq's queue);
 *   - window.groTT(name, data): lp.js / pdp.js call it next to their AppLovin events with the same payload
 *     ({currency, value, items:[{item_id, item_name, price, quantity}]}): view_item -> ViewContent, add_to_cart -> AddToCart.
 *     content_id is the SKU, as on the checkout, so TikTok sees one product across the funnel.
 * %ID% is replaced with campaigns.json tiktok_pixel_id by the builders. */
!function (w, d, t) {
  w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie","holdConsent","revokeConsent","grantConsent"],ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e},ttq.load=function(e,n){var r="https://analytics.tiktok.com/i18n/pixel/events.js",o=n&&n.partner;ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=r,ttq._t=ttq._t||{},ttq._t[e]=+new Date,ttq._o=ttq._o||{},ttq._o[e]=n||{};n=document.createElement("script");n.type="text/javascript",n.async=!0,n.src=r+"?sdkid="+e+"&lib="+t;e=document.getElementsByTagName("script")[0];e.parentNode.insertBefore(n,e)};
  var go = function () { ttq.load('%ID%'); ttq.page(); };
  'complete' === d.readyState ? go() : w.addEventListener('load', go);
}(window, document, 'ttq');
window.groTT = function (name, data) {
  try {
    var ev = { view_item: 'ViewContent', add_to_cart: 'AddToCart' }[name];
    if (!ev || !window.ttq) return;
    var p = { content_type: 'product' };
    if (data) {
      if (data.currency) p.currency = data.currency;
      if (data.value !== undefined && data.value !== null) p.value = data.value;
      p.contents = (data.items || []).map(function (i) {
        var c = { content_id: String(i.item_id) };
        if (i.item_name) c.content_name = i.item_name;
        if (i.item_brand) c.brand = i.item_brand;
        if (i.price !== undefined) c.price = i.price;
        if (i.quantity !== undefined) c.quantity = i.quantity;
        return c;
      });
    }
    window.ttq.track(ev, p);
  } catch (e) { /* never block the page */ }
};
