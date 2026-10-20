/**
 * Spark Cart Loader
 *
 * Keeps the heavy cart drawer stack off the initial page until the shopper
 * asks for the drawer. Saved carts load only the cart client for badge
 * hydration. The cart page and PDP still keep normal form fallbacks.
 */

(function() {
    'use strict';

    var assets = window.SparkCartAssets || {};
    var scriptPromises = {};
    var drawerPromise = null;
    var togglePromise = null;
    var queuedToggle = false;

    function reportError(message, err, level) {
        if (!window.console) return;
        var reporter = console[level] || console.warn || console.error || console.log;
        if (reporter) reporter.call(console, '[spark-cart-loader] ' + message, err);
    }

    function readCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : null;
    }

    function clearCookie(name) {
        document.cookie = name + '=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }

    function getSavedCartId() {
        try {
            var id = sessionStorage.getItem('storefront_cart_id');
            if (id) return id;
        } catch (e) {}
        return readCookie('storefront_cart_id');
    }

    function loadScript(name, globalName) {
        if (globalName && window[globalName]) return Promise.resolve();
        if (scriptPromises[name]) return scriptPromises[name];

        scriptPromises[name] = new Promise(function(resolve, reject) {
            var src = assets[name];
            if (!src) {
                reject(new Error('Missing Spark cart asset: ' + name));
                return;
            }

            var script = document.createElement('script');
            script.src = src;
            script.async = false;
            script.onload = resolve;
            script.onerror = function() {
                delete scriptPromises[name];
                reject(new Error('Unable to load Spark cart asset: ' + name));
            };
            document.head.appendChild(script);
        });

        return scriptPromises[name];
    }

    function loadCartClient() {
        return loadScript('cart', 'SparkCartClient');
    }

    function waitForDrawerUpgrade() {
        if (window.customElements && customElements.whenDefined) {
            return customElements.whenDefined('spark-cart-drawer').then(function() {
                return new Promise(function(resolve) {
                    requestAnimationFrame(resolve);
                });
            });
        }
        return new Promise(function(resolve) {
            setTimeout(resolve, 0);
        });
    }

    function ensureDrawer() {
        if (window.SparkSideCart) return Promise.resolve();
        if (drawerPromise) return drawerPromise;

        drawerPromise = loadCartClient()
            .then(function() { return loadScript('cartRewards', 'SparkCartRewards'); })
            .then(function() { return loadScript('cartRenderer', 'SparkCartDrawerRenderer'); })
            .then(function() { return loadScript('progressBar'); })
            .then(function() { return loadScript('upsellItem'); })
            .then(function() { return loadScript('cartDrawer'); })
            .then(waitForDrawerUpgrade)
            .catch(function(err) {
                drawerPromise = null;
                reportError('drawer stack failed to load', err, 'error');
                throw err;
            });

        return drawerPromise;
    }

    function updateCartBadge(count) {
        var badge = document.getElementById('cart-badge');
        if (!badge) return;
        if (count && count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = '';
            badge.removeAttribute('data-animate');
            void badge.offsetWidth;
            badge.setAttribute('data-animate', '');
        } else {
            badge.style.display = 'none';
        }
    }

    function rememberCart(cart) {
        if (!cart) return;
        window.SparkCartInitialCart = cart;
        updateCartBadge(cart.numItems);

        var drawer = document.querySelector('spark-cart-drawer');
        if (drawer && !drawer._cart) {
            drawer._cart = cart;
            drawer._currencyCode = cart.currency || drawer._currencyCode;
            if (drawer._renderCart) drawer._renderCart();
        }
    }

    function hydrateBadgeFromSavedCart() {
        if (!getSavedCartId()) return;
        loadCartClient().then(function() {
            var client = new SparkCartClient();
            return client.getCart();
        }).then(function(cart) {
            rememberCart(cart);
        }).catch(function(err) {
            reportError('badge hydration failed', err, 'warn');
        });
    }

    function openDrawer() {
        return ensureDrawer().then(function() {
            if (window.SparkSideCart) SparkSideCart.open();
        });
    }

    function toggleDrawer() {
        if (window.SparkSideCart) {
            SparkSideCart.toggle();
            return Promise.resolve();
        }

        queuedToggle = true;
        if (togglePromise) return togglePromise;

        togglePromise = ensureDrawer().then(function() {
            var shouldToggle = queuedToggle;
            queuedToggle = false;
            togglePromise = null;
            if (shouldToggle && window.SparkSideCart) SparkSideCart.toggle();
        }).catch(function(err) {
            queuedToggle = false;
            togglePromise = null;
            throw err;
        });

        return togglePromise;
    }

    document.addEventListener('spark:cart:updated', function(e) {
        var detail = e.detail || {};
        rememberCart(detail.cart);
        updateCartBadge(detail.count);
    });

    document.addEventListener('spark:cart:added', function(e) {
        var detail = e.detail || {};
        rememberCart(detail.cart);
        updateCartBadge(detail.count);

        if (detail.openSideCart === false) return;
        if (window.SparkSideCart) return;

        ensureDrawer().then(function() {
            if (window.SparkSideCart) SparkSideCart.open();
        }).catch(function(err) {
            reportError('drawer load after cart add failed', err, 'error');
        });
    });

    document.addEventListener('spark:cart:toggle', function() {
        if (window.SparkSideCart) return;
        toggleDrawer().catch(function(err) {
            reportError('drawer toggle failed', err, 'error');
        });
    });

    if (readCookie('openSideCart') === '1') {
        // Clear before the delayed open so the drawer does not replay on refresh.
        clearCookie('openSideCart');
        setTimeout(function() {
            openDrawer().catch(function(err) {
                reportError('saved drawer open failed', err, 'error');
            });
        }, 300);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hydrateBadgeFromSavedCart);
    } else {
        hydrateBadgeFromSavedCart();
    }

    window.SparkCartLoader = {
        ensureDrawer: ensureDrawer,
        loadCartClient: loadCartClient,
        open: openDrawer,
        toggle: toggleDrawer,
        updateCartBadge: updateCartBadge
    };
})();
