/**
 * Spark Events
 *
 * Small public event helper for Spark storefront adapters. Event names and
 * payload shapes live here so cart, variant, progress, and UI modules do
 * not hand-roll the same CustomEvent contracts.
 */

(function() {
    'use strict';

    function extend(target, source) {
        target = target || {};
        source = source || {};
        Object.keys(source).forEach(function(key) {
            target[key] = source[key];
        });
        return target;
    }

    function dispatch(name, detail, target) {
        (target || document).dispatchEvent(new CustomEvent(name, {
            detail: detail || {},
            bubbles: true
        }));
    }

    function cartDetail(cart, action, detail) {
        detail = extend({}, detail);
        detail.cart = cart || null;
        detail.count = cart && typeof cart.numItems !== 'undefined' ? cart.numItems : 0;
        if (action) detail.action = action;
        return detail;
    }

    var SparkEvents = {
        CART_UPDATED: 'spark:cart:updated',
        CART_ADDED: 'spark:cart:added',
        CART_TOGGLE: 'spark:cart:toggle',
        VARIANT_CHANGED: 'spark:variant:changed',
        PROGRESS_SHIPPING_REACHED: 'spark:progress:shipping-reached',
        PROGRESS_SHIPPING_UNREACHED: 'spark:progress:shipping-unreached',
        PROGRESS_GIFT_REACHED: 'spark:progress:gift-reached',
        PROGRESS_GIFT_UNREACHED: 'spark:progress:gift-unreached',

        dispatch: dispatch,

        cartUpdated: function(cart, action, detail) {
            dispatch(SparkEvents.CART_UPDATED, cartDetail(cart, action, detail));
        },

        cartAdded: function(cart, productId, quantity, detail) {
            detail = cartDetail(cart, 'add', detail);
            detail.productId = productId;
            detail.quantity = quantity || 1;
            dispatch(SparkEvents.CART_ADDED, detail);
        },

        cartToggle: function(detail) {
            dispatch(SparkEvents.CART_TOGGLE, detail || {});
        },

        variantChanged: function(product, variant, selection) {
            dispatch(SparkEvents.VARIANT_CHANGED, {
                product: product || null,
                variant: variant || null,
                selection: selection || {}
            });
        },

        progress: function(name, detail) {
            dispatch(name, detail || {});
        }
    };

    window.SparkEvents = SparkEvents;
})();
