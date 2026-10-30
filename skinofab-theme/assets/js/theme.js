/**
 * Spark Theme - Core JavaScript
 * No jQuery, no frameworks. Self-contained vanilla JS.
 */

(function() {
    'use strict';

    /* Shared body scroll lock */

    window.SparkBodyScrollLock = (function() {
        var lockCount = 0;
        var previousOverflow = '';

        return {
            lock: function() {
                if (lockCount === 0) {
                    previousOverflow = document.body.style.overflow;
                    document.body.style.overflow = 'hidden';
                }
                lockCount += 1;
            },
            unlock: function() {
                if (lockCount === 0) return;
                lockCount -= 1;
                if (lockCount === 0) {
                    document.body.style.overflow = previousOverflow;
                }
            }
        };
    })();

    /* Mobile Navigation */

    const DESKTOP_NAV_MEDIA_QUERY = '(min-width: 48rem)';
    const FOCUSABLE_SELECTOR = [
        'a[href]',
        'button:not([disabled])',
        'input:not([disabled]):not([type="hidden"])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        '[tabindex]:not([tabindex="-1"])'
    ].join(',');

    function visibleFocusable(root) {
        var nodes = root.querySelectorAll(FOCUSABLE_SELECTOR);
        var result = [];
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            if (node.offsetWidth || node.offsetHeight || node.getClientRects().length) {
                result.push(node);
            }
        }
        return result;
    }

    function initMobileNav() {
        const toggleBtn = document.querySelector('[data-toggle="mobile-nav"]');
        const mobileNav = document.getElementById('mobile-nav');
        const desktopNavQuery = window.matchMedia(DESKTOP_NAV_MEDIA_QUERY);
        var mobileNavLockedBody = false;
        var mobileNavFocusTimer = null;
        if (!toggleBtn || !mobileNav) return;

        var panel = mobileNav.querySelector('[data-mobile-nav-panel]') || mobileNav;

        function isOpen() {
            return !mobileNav.classList.contains('hidden');
        }

        function openMobileNav() {
            mobileNav.classList.remove('hidden');
            toggleBtn.setAttribute('aria-expanded', 'true');
            if (!mobileNavLockedBody) {
                window.SparkBodyScrollLock.lock();
                mobileNavLockedBody = true;
            }
            // Match the cart drawer: move focus into the panel once it is visible.
            var closeBtn = mobileNav.querySelector('[data-close="mobile-nav"][type="button"]');
            var target = closeBtn || visibleFocusable(panel)[0];
            if (target) {
                if (mobileNavFocusTimer !== null) clearTimeout(mobileNavFocusTimer);
                mobileNavFocusTimer = setTimeout(function() {
                    mobileNavFocusTimer = null;
                    if (isOpen()) target.focus();
                }, 50);
            }
        }

        function closeMobileNav(options) {
            var wasOpen = isOpen();
            if (mobileNavFocusTimer !== null) {
                clearTimeout(mobileNavFocusTimer);
                mobileNavFocusTimer = null;
            }
            mobileNav.classList.add('hidden');
            toggleBtn.setAttribute('aria-expanded', 'false');
            if (mobileNavLockedBody) {
                window.SparkBodyScrollLock.unlock();
            }
            mobileNavLockedBody = false;
            // Return focus to the toggle unless the viewport just went desktop.
            if (wasOpen && !(options && options.silent)) {
                toggleBtn.focus();
            }
        }

        function trapFocus(e) {
            var focusable = visibleFocusable(panel);
            if (!focusable.length) {
                e.preventDefault();
                return;
            }
            var first = focusable[0];
            var last = focusable[focusable.length - 1];
            var active = document.activeElement;
            if (!panel.contains(active)) {
                e.preventDefault();
                (e.shiftKey ? last : first).focus();
                return;
            }
            if (e.shiftKey && active === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && active === last) {
                e.preventDefault();
                first.focus();
            }
        }

        toggleBtn.addEventListener('click', function() {
            if (isOpen()) {
                closeMobileNav();
            } else {
                openMobileNav();
            }
        });

        // Close buttons and backdrop
        mobileNav.querySelectorAll('[data-close="mobile-nav"]').forEach(function(el) {
            el.addEventListener('click', function() {
                closeMobileNav();
            });
        });

        document.addEventListener('keydown', function(e) {
            if (!isOpen()) return;
            if (e.key === 'Escape') {
                closeMobileNav();
                return;
            }
            if (e.key === 'Tab') {
                trapFocus(e);
            }
        });

        function handleDesktopNavChange(e) {
            if (e.matches) {
                closeMobileNav({ silent: true });
            }
        }

        if (desktopNavQuery.addEventListener) {
            desktopNavQuery.addEventListener('change', handleDesktopNavChange);
        } else {
            desktopNavQuery.addListener(handleDesktopNavChange);
        }
    }

    /* Search Overlay */

    function initSearchOverlay() {
        var overlay = document.getElementById('search-overlay');
        var input = document.getElementById('search-input');
        var searchLockedBody = false;
        if (!overlay) return;

        function openSearch() {
            overlay.classList.add('search-overlay-visible');
            if (!searchLockedBody) {
                window.SparkBodyScrollLock.lock();
                searchLockedBody = true;
            }
            if (input) {
                setTimeout(function() { input.focus(); }, 150);
            }
        }

        function closeSearch() {
            overlay.classList.remove('search-overlay-visible');
            if (searchLockedBody) {
                window.SparkBodyScrollLock.unlock();
                searchLockedBody = false;
            }
        }

        // Open button
        document.querySelectorAll('[data-toggle="search-overlay"]').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                openSearch();
            });
        });

        // Close buttons and backdrop
        overlay.querySelectorAll('[data-close="search-overlay"]').forEach(function(el) {
            el.addEventListener('click', function() {
                closeSearch();
            });
        });

        // Escape key closes search
        overlay.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeSearch();
            }
        });
    }

    /* Side Cart */

    function initSideCart() {
        // Cart icon click dispatches toggle event (handled in side_cart.html)
        document.querySelectorAll('[data-toggle="side-cart"]').forEach(function(el) {
            el.addEventListener('click', function(e) {
                e.preventDefault();
                if (window.SparkEvents) {
                    SparkEvents.cartToggle();
                } else {
                    document.dispatchEvent(new CustomEvent('spark:cart:toggle'));
                }
            });
        });
    }

    /* Product Variant & Cart */

    window.theme = window.theme || {};
    theme.product = {
        productObject: null,
        variantState: null,
        messages: {
            addToCart: window.SparkI18n && window.SparkI18n.addToCart ? window.SparkI18n.addToCart : 'Add to cart',
            unavailable: window.SparkI18n && window.SparkI18n.unavailable ? window.SparkI18n.unavailable : 'Unavailable'
        },
        init: function(options) {
            options = options || {};
            theme.product.messages.addToCart = options.add_to_cart_msg || theme.product.messages.addToCart;
            theme.product.messages.unavailable = options.unavailable_msg || theme.product.messages.unavailable;
            theme.product.initSizeGuideLinks();
            if (typeof SparkVariantState === 'undefined') return;

            var state = SparkVariantState.fromPage();
            if (!state) return;
            theme.product.variantState = state;
            theme.product.productObject = state.product;

            var initialVariant = state.getSelectedVariant() || state.getDefaultVariant();
            if (initialVariant) {
                theme.product.updateForm(initialVariant);
                theme.product.updatePrice(initialVariant);
                state.emitChange(initialVariant);
            }

            theme.product.updateOptionStates();

            state.onChange(function(variant) {
                theme.product.updateForm(variant);
                theme.product.updatePrice(variant);
                theme.product.updateOptionStates();
            });
        },
        getVariantFromSelection: function() {
            return theme.product.variantState ? theme.product.variantState.getSelectedVariant() : null;
        },
        updateForm: function(variant) {
            var form = document.getElementById('add-to-cart');
            if (!form || !variant) return;
            SparkVariantState.updateFormAction(form, variant);

            var btn = form.querySelector('button[type="submit"]');
            if (!btn) return;
            if (!SparkVariantState.isPurchasable(variant)) {
                btn.disabled = true;
                btn.textContent = btn.getAttribute('data-disabled-text') || theme.product.messages.unavailable;
            } else {
                btn.disabled = false;
                btn.textContent = theme.product.messages.addToCart;
            }
        },
        updatePrice: function(variant) {
            if (typeof SparkVariantState === 'undefined') return;
            SparkVariantState.updatePrice(document, variant);
        },
        /**
         * Chips picker only. Marks option values that cannot produce a
         * purchasable variant, and echoes the selected label beside the
         * option name. Never disables the input, so selection behavior and
         * the existing sold-out add-to-cart handling are unchanged.
         */
        updateOptionStates: function() {
            var state = theme.product.variantState;
            if (!state || !state.getOptionAvailability) return;
            var availability = state.getOptionAvailability();

            document.querySelectorAll('[data-variant-option-group]').forEach(function(group) {
                var name = group.getAttribute('data-variant-option-name');
                var values = availability[name] || null;
                var selectedText = '';

                group.querySelectorAll('[data-variant-option]').forEach(function(option) {
                    var value = option.getAttribute('data-variant-option-value');
                    var input = option.querySelector('input');
                    var text = option.querySelector('[data-variant-option-text]');
                    var status = option.querySelector('[data-variant-option-status]');

                    if (values && values[value] === false) {
                        option.setAttribute('data-variant-unavailable', 'true');
                        if (status) status.textContent = theme.product.messages.unavailable;
                    } else {
                        option.removeAttribute('data-variant-unavailable');
                        if (status) status.textContent = '';
                    }

                    if (input && input.checked && text) {
                        selectedText = text.textContent.trim();
                    }
                });

                var echo = group.querySelector('[data-variant-selected-label]');
                if (echo) echo.textContent = selectedText;
            });
        },
        /**
         * Returns a trimmed HTTP(S) or relative storefront URL. Browser URL
         * parsing closes scheme-obfuscation gaps that string prefix checks
         * miss. Protocol-relative URLs are rejected to keep the setting
         * explicit about external destinations.
         */
        normalizeSizeGuideUrl: function(value) {
            var candidate = String(value || '').trim();
            if (!candidate || /^(?:\/\/|\\\\)/.test(candidate)) return null;

            try {
                var parsed = new URL(candidate, window.location.href);
                if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return null;
                return candidate;
            } catch (error) {
                return null;
            }
        },
        initSizeGuideLinks: function() {
            document.querySelectorAll('[data-variant-size-guide-url]').forEach(function(link) {
                var safeUrl = theme.product.normalizeSizeGuideUrl(
                    link.getAttribute('data-variant-size-guide-url')
                );
                if (safeUrl) {
                    link.setAttribute('href', safeUrl);
                    return;
                }
                if (link.parentNode) link.parentNode.removeChild(link);
            });
        }
    };

    function initVariantPicker() {
        // Visual styling for variant labels
        document.querySelectorAll('input[name^="attr_"]').forEach(function(input) {
            input.addEventListener('change', function() {
                var name = input.name;
                document.querySelectorAll('input[name="' + name + '"]').forEach(function(sibling) {
                    var label = sibling.closest('label');
                    if (label) {
                        label.classList.remove('border-slate-800');
                        label.classList.add('border-slate-200');
                    }
                });
                var selectedLabel = input.closest('label');
                if (selectedLabel) {
                    selectedLabel.classList.remove('border-slate-200');
                    selectedLabel.classList.add('border-slate-800');
                }
            });
        });
    }

    /* Announcement Bar Dismiss */

    function initAnnouncementBar() {
        var dismissBtn = document.querySelector('[data-dismiss="announcement-bar"]');
        if (!dismissBtn) return;

        dismissBtn.addEventListener('click', function() {
            var bar = document.getElementById('announcement-bar');
            if (bar) {
                bar.style.display = 'none';
                try {
                    sessionStorage.setItem('spark_ab_dismissed', '1');
                } catch(e) {}
            }
        });

        // Restore dismissed state
        try {
            if (sessionStorage.getItem('spark_ab_dismissed') === '1') {
                var bar = document.getElementById('announcement-bar');
                if (bar) bar.style.display = 'none';
            }
        } catch(e) {}
    }

    /* Reduced Motion */

    function respectReducedMotion() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.style.setProperty('--default-transition-duration', '0ms');
        }
    }

    /* Init */

    document.addEventListener('DOMContentLoaded', function() {
        initMobileNav();
        initSearchOverlay();
        initSideCart();
        initVariantPicker();
        initAnnouncementBar();
        respectReducedMotion();
    });

})();
