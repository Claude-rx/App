/**
 * Spark Platform Compatibility Layer
 *
 * Replaces platform's core_js (which depends on jQuery) with vanilla JS
 * equivalents. This allows Spark to run without jQuery entirely.
 *
 * What this replaces from core_js:
 * - core.refresh_csrf() - CSRF token refresh (already vanilla in platform)
 * - core.language_switcher.init() - Language select auto-submit
 * - core.currency_switcher.init() - Currency select auto-submit
 * - core.subscription.init() - Subscription option handling
 * - core.delete_confirmation.init() - Delete confirmation dialogs
 * - core.cart.init() - Cart page quantity/frequency auto-submit and line removal
 * - funnel.init() / funnel.basket.init() - Cart open on add, basket callbacks
 *
 * What was already vanilla in platform and is NOT replaced:
 * - side_cart.js uses vanilla JS + GraphQL internally
 * - cart.js basic cart operations
 *
 * What is intentionally dropped:
 * - jquery.validate.min.js - Use HTML5 validation instead
 * - core.variant.init() - Was empty function, Spark has its own variant picker
 * - core.theme_settings_preview - Theme-editor iframe behavior remains platform-owned
 *
 * Preview-session visibility is provided separately by spark-preview.js.
 */

(function() {
    'use strict';

    // --- CSRF Token Refresh ---
    // Fetches a fresh CSRF token and updates all hidden inputs
    async function refreshCSRF() {
        try {
            var response = await fetch('/csrf/', { credentials: 'same-origin' });
            var data = await response.json();
            var inputs = document.querySelectorAll('input[name="csrfmiddlewaretoken"][type="hidden"]');
            inputs.forEach(function(input) {
                input.value = data.csrfToken;
            });
        } catch(e) {
            // Non-critical - forms will still work with existing token
        }
    }

    // --- Language Switcher ---
    // Auto-submit language form when select changes
    function initLanguageSwitcher() {
        var select = document.querySelector('form#set-language select[name="language"]');
        if (!select) return;
        select.addEventListener('change', function(e) {
            e.preventDefault();
            var form = document.getElementById('set-language');
            if (form) form.submit();
        });
    }

    // --- Currency Switcher ---
    // Auto-submit currency form when select changes
    function initCurrencySwitcher() {
        var select = document.querySelector('select[name="currency"]');
        if (!select) return;
        select.addEventListener('change', function(e) {
            e.preventDefault();
            var form = document.getElementById('set-currency');
            if (form) form.submit();
        });
    }

    // --- Delete Confirmation ---
    // Confirm before deleting items (account pages, etc.)
    function initDeleteConfirmation() {
        document.addEventListener('click', function(e) {
            var el = e.target.closest(':not(form)[data-delete-id]');
            if (!el) return;
            var messages = window.SparkI18n || {};
            if (!confirm(messages.deleteConfirm || 'Are you sure you want to delete?')) {
                e.stopImmediatePropagation();
                e.preventDefault();
                return;
            }
            // Add hidden ID input and submit parent form
            var form = el.closest('form');
            if (form) {
                var input = form.querySelector('input[name="id"]');
                if (!input) {
                    input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'id';
                    form.appendChild(input);
                }
                input.value = el.getAttribute('data-delete-id');
                form.submit();
            }
        });
    }

    // --- Subscription Options ---
    // Handle subscription vs one-time purchase toggle on PDP
    function initSubscription() {
        var options = document.getElementById('id_subscription_options');
        if (!options) return;

        // Show/hide subscription options based on product option selection
        var oneTimeBtn = document.getElementById('product-option-1');
        var subscriptionBtn = document.getElementById('product-option-2');

        if (oneTimeBtn) {
            oneTimeBtn.addEventListener('click', function() {
                if (options) options.style.display = 'none';
                // Clear subscription interval when switching to one-time
                var intervalInput = document.querySelector('input[name="subscription_interval"]');
                if (intervalInput) intervalInput.value = '';
            });
        }

        if (subscriptionBtn) {
            subscriptionBtn.addEventListener('click', function() {
                if (options) options.style.display = '';
                // Set default subscription interval
                var firstOption = options.querySelector('input[type="radio"]');
                if (firstOption) firstOption.checked = true;
            });
        }

        // Label clicks within subscription options
        options.addEventListener('click', function(e) {
            var label = e.target.closest('label');
            if (!label) return;
            var radio = label.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                // Update hidden field if present
                var hidden = document.querySelector('input[name="subscription_option"]');
                if (hidden) hidden.value = radio.value;
            }
        });

        // Subscription range (frequency) select changes
        var subLineForm = document.getElementById('subscription_line_form');
        if (subLineForm) {
            subLineForm.addEventListener('change', function(e) {
                if (e.target.tagName === 'SELECT') {
                    // Auto-submit subscription frequency changes
                    subLineForm.submit();
                }
            });
        }

        // Price update on subscription change
        var priceInputs = document.querySelectorAll('input[name="prod-price"]');
        priceInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                var priceDisplay = document.querySelector('[data-subscription-price]');
                if (priceDisplay) priceDisplay.textContent = input.value;
            });
        });
    }

    // --- Cart Modal Integration ---
    // Replace funnel.basket.init() cart-open behavior
    // Spark's SparkSideCart and spark:cart:added handle this instead
    function initCartIntegration() {
        // Check if side cart should open on page load (openSideCart cookie)
        try {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var c = cookies[i].trim();
                if (c.indexOf('openSideCart=1') === 0) {
                    // Clear the cookie
                    document.cookie = 'openSideCart=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
                    // Open side cart after a short delay for page to render
                    setTimeout(function() {
                        if (window.SparkSideCart) SparkSideCart.open();
                    }, 300);
                    break;
                }
            }
        } catch(e) {}

        // Handle remove buttons in side cart (platform renders these)
        document.addEventListener('click', function(e) {
            var removeBtn = e.target.closest('button[data-behaviours~="remove"]');
            if (!removeBtn) return;
            var span = e.target.closest('[data-id]');
            if (span && span.getAttribute('aria-hidden') === 'false') {
                var lineId = span.getAttribute('data-id');
                if (lineId && window.sidecart && sidecart.basket) {
                    sidecart.basket.removeBasketLine(lineId);
                }
            }
            e.preventDefault();
        });
    }

    // --- Cart Page Formset ---
    // The cart page renders one formset row per line. A quantity or
    // subscription frequency change submits the form; the remove link ticks
    // the row's hidden DELETE checkbox and submits.
    function initCartFormset() {
        var form = document.getElementById('cart_formset');
        if (!form) return;
        form.addEventListener('change', function(e) {
            var field = e.target;
            if (field && field.name && /-(quantity|subscription_range)$/.test(field.name)) {
                form.submit();
            }
        });
        form.addEventListener('click', function(e) {
            var link = e.target && e.target.closest ? e.target.closest('.remove-from-cart') : null;
            if (!link) return;
            e.preventDefault();
            var box = link.querySelector('input[type="checkbox"]');
            if (!box) return;
            box.checked = true;
            form.submit();
        });
    }

    // --- Storefront Switcher ---
    // Multi-storefront selector (if present)
    function initStorefrontSwitcher() {
        var select = document.querySelector('select[name="storefront"]');
        if (!select) return;
        select.addEventListener('change', function() {
            var form = select.closest('form');
            if (form) form.submit();
        });
    }

    // --- Init ---
    // Run after DOM is ready (this script loads after the DOM)
    refreshCSRF();
    initLanguageSwitcher();
    initCurrencySwitcher();
    initDeleteConfirmation();
    initSubscription();
    initCartIntegration();
    initCartFormset();
    initStorefrontSwitcher();

})();
