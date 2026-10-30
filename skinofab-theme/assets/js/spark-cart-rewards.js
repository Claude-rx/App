/**
 * Spark Cart Rewards
 *
 * Localizes free-gift and upsell visibility rules for the side cart.
 * The drawer remains the UI Adapter; this Module owns cart reward
 * interpretation so metadata and fallback-slot rules stay in one place.
 */

(function() {
    'use strict';

    function parseMetadata(meta) {
        if (!meta) return {};
        if (typeof meta === 'string') {
            try {
                return JSON.parse(meta) || {};
            } catch (e) {
                return {};
            }
        }
        return meta;
    }

    function splitSlots(slots) {
        var result = {};
        String(slots || '').split(',').forEach(function(slot) {
            var clean = slot.trim();
            if (clean) result[clean] = true;
        });
        return result;
    }

    function productIdsInCart(cart) {
        var ids = {};
        var lines = cart && cart.lines ? cart.lines : [];
        for (var i = 0; i < lines.length; i++) {
            var product = lines[i].product;
            if (!product) continue;
            ids[String(product.pk)] = true;
            if (product.parent) ids[String(product.parent.pk)] = true;
        }
        return ids;
    }

    function activeUpsellSlots(cart) {
        var slots = {};
        var lines = cart && cart.lines ? cart.lines : [];
        for (var i = 0; i < lines.length; i++) {
            var product = lines[i].product;
            if (!product) continue;
            var meta = parseMetadata(product.metadata || (product.parent ? product.parent.metadata : null));
            var productSlots = splitSlots(meta.cart_upsell_slots || '');
            Object.keys(productSlots).forEach(function(slot) {
                slots[slot] = true;
            });
        }
        return slots;
    }

    function hasKeys(obj) {
        return Object.keys(obj || {}).length > 0;
    }

    function findGiftLine(cart, giftProductId) {
        if (!giftProductId || !cart || !cart.lines) return null;
        for (var i = 0; i < cart.lines.length; i++) {
            var line = cart.lines[i];
            if (line.isUpsell && line.product && String(line.product.pk) === String(giftProductId)) {
                return line;
            }
        }
        return null;
    }

    var SparkCartRewards = {
        parseMetadata: parseMetadata,
        splitSlots: splitSlots,
        productIdsInCart: productIdsInCart,
        activeUpsellSlots: activeUpsellSlots,
        findGiftLine: findGiftLine,

        giftState: function(cart, giftProductId) {
            var line = findGiftLine(cart, giftProductId);
            return {
                containsGift: !!line,
                lineId: line ? line.pk : null
            };
        },

        toggleGift: function(client, cart, shouldAdd, giftProductId, giftLineId) {
            if (!client || !cart || !giftProductId) return Promise.resolve(null);
            if (shouldAdd) {
                return client.addToCart(Number(giftProductId), 1, true);
            }
            if (giftLineId) {
                return client.removeCartLines(cart.id, [giftLineId]);
            }
            return Promise.resolve(null);
        },

        updateProgressBar: function(progressBar, total) {
            if (progressBar) {
                progressBar.setAttribute('data-value', String(total || 0));
            }
        },

        hideUpsells: function(root) {
            var upsells = root.querySelectorAll('spark-upsell-item');
            for (var i = 0; i < upsells.length; i++) {
                upsells[i].style.display = 'none';
            }
        },

        updateUpsellVisibility: function(root, cart) {
            var upsells = root.querySelectorAll('spark-upsell-item');
            if (!upsells.length) return;

            var cartProductPks = productIdsInCart(cart);
            var activeSlots = activeUpsellSlots(cart);
            var hasActiveSlots = hasKeys(activeSlots);

            for (var i = 0; i < upsells.length; i++) {
                var upsell = upsells[i];
                var slot = upsell.getAttribute('data-upsell-slot');
                var productId = upsell.getAttribute('data-product-id');
                var slotsToCheck = activeSlots;

                if (productId && cartProductPks[String(productId)]) {
                    upsell.style.display = 'none';
                    continue;
                }

                if (!hasActiveSlots) {
                    slotsToCheck = splitSlots(upsell.getAttribute('data-fallback-slots') || '1,2');
                }

                if (!slot || slotsToCheck[slot]) {
                    upsell.style.display = '';
                } else {
                    upsell.style.display = 'none';
                }
            }
        }
    };

    window.SparkCartRewards = SparkCartRewards;
})();
