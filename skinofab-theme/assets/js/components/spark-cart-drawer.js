/**
 * Spark Theme - Cart Drawer Web Component
 *
 * Custom side cart replacing platform's side_cart.js.
 * Uses SparkCartClient for all GraphQL operations.
 * Shadow DOM for encapsulation, Tailwind in light DOM shell.
 *
 * Events listened:
 *   spark:cart:added   - Opens drawer + updates with cart data
 *   spark:cart:toggle  - Toggles drawer open/close
 *   spark:cart:updated - Re-renders cart UI
 *
 * Events dispatched:
 *   spark:cart:updated - After quantity/remove/voucher mutations
 */

(function() {
    'use strict';

    /* --- Drawer styles (injected into Shadow DOM) --- */

    var DRAWER_STYLES = [
        ':host { display: block; }',
        /* Shadow DOM does not inherit document box-sizing. Without this reset,  */
        /* width:100% + padding on .spark-drawer-checkout (and the voucher form) */
        /* renders wider than the footer content area and overflows past the     */
        /* panel's right edge.                                                   */
        '*, *::before, *::after { box-sizing: border-box; }',
        ':host([data-open="false"]) .spark-drawer-backdrop { opacity: 0; pointer-events: none; }',
        ':host([data-open="false"]) .spark-drawer-panel { transform: translateX(100%); }',
        ':host([data-open="true"]) .spark-drawer-backdrop { opacity: 1; }',
        ':host([data-open="true"]) .spark-drawer-panel { transform: translateX(0); }',

        '.spark-drawer-backdrop {' +
        '  position: fixed; inset: 0; z-index: 70; background: rgba(0,0,0,0.3);' +
        '  transition: opacity 200ms ease-out; cursor: pointer;' +
        '}',

        '.spark-drawer-panel {' +
        '  position: fixed; top: 0; right: 0; bottom: 0; z-index: 71;' +
        '  width: 100%; max-width: 400px; background: #fff;' +
        '  display: flex; flex-direction: column;' +
        '  transition: transform 250ms ease-out;' +
        '  transform: translateX(100%);' +
        '  font-family: var(--font-body, system-ui, -apple-system, sans-serif);' +
        '  color: #1E293B;' +
        '}',

        '@media (max-width: 767px) { .spark-drawer-panel { max-width: 100%; } }',

        /* Header */
        '.spark-drawer-header {' +
        '  display: flex; align-items: center; justify-content: space-between;' +
        '  padding: 16px 20px; border-bottom: 1px solid #E2E8F0;' +
        '  flex-shrink: 0;' +
        '}',
        '.spark-drawer-header-title {' +
        '  font-size: 18px; font-weight: 600; margin: 0;' +
        '  font-family: var(--font-header, var(--font-body, system-ui, -apple-system, sans-serif));' +
        '}',
        '.spark-drawer-close {' +
        '  background: none; border: none; cursor: pointer; padding: 8px;' +
        '  color: #475569; transition: color 150ms ease-out; line-height: 0;' +
        '}',
        '.spark-drawer-close:hover { color: #1E293B; }',
        /* Inset focus outline so the focus ring never extends past the panel's */
        /* right edge (the close button auto-focuses on drawer open).            */
        '.spark-drawer-close:focus-visible { outline: 2px solid var(--primary-color, #1E293B); outline-offset: -2px; }',

        /* Body */
        '.spark-drawer-body {' +
        '  flex: 1 1 auto; overflow-y: auto; padding: 16px 20px;' +
        '}',

        /* Empty state */
        '.spark-drawer-empty {' +
        '  display: flex; flex-direction: column; align-items: center; justify-content: center;' +
        '  text-align: center; padding: 48px 20px; gap: 8px;' +
        '}',
        '.spark-drawer-empty svg { color: #CBD5E1; margin-bottom: 8px; }',
        '.spark-drawer-empty-title { font-size: 18px; color: #475569; font-weight: 500; }',
        '.spark-drawer-empty-sub { font-size: 14px; color: #94A3B8; }',
        '.spark-drawer-empty-cta {' +
        '  margin-top: 16px; display: inline-block; padding: 10px 24px;' +
        '  background: var(--primary-color, #1E293B); color: #fff; text-decoration: none;' +
        '  font-size: 14px; font-weight: 500; border-radius: 4px;' +
        '  transition: opacity 150ms ease-out;' +
        '}',
        '[data-light-primary] .spark-drawer-empty-cta { color: #1E293B; }',
        '.spark-drawer-empty-cta:hover { opacity: 0.9; }',

        /* Loading */
        '.spark-drawer-loading {' +
        '  display: flex; align-items: center; justify-content: center; padding: 48px;' +
        '}',
        '@keyframes spark-drawer-spin { to { transform: rotate(360deg); } }',
        '.spark-drawer-spinner {' +
        '  width: 24px; height: 24px; border: 2px solid #E2E8F0;' +
        '  border-top-color: var(--primary-color, #1E293B);' +
        '  border-radius: 50%; animation: spark-drawer-spin 800ms linear infinite;' +
        '}',

        /* Cart items */
        '.spark-drawer-items { display: flex; flex-direction: column; gap: 0; }',
        '.spark-drawer-item {' +
        '  display: flex; gap: 12px; padding: 16px 0;' +
        '  border-bottom: 1px solid #E2E8F0; position: relative;' +
        '}',
        '.spark-drawer-item:last-child { border-bottom: none; }',
        '.spark-drawer-item[data-loading="true"] { opacity: 0.5; pointer-events: none; }',
        '.spark-drawer-item-image { flex-shrink: 0; width: 80px; height: 80px; }',
        '.spark-drawer-item-image img { width: 80px; height: 80px; object-fit: cover; border-radius: 2px; }',
        /* Reserve 28px on the right so the absolute-positioned remove X never  */
        /* overlaps the title/variant text (long variant-suffixed titles can be */
        /* much longer than a single line).                                     */
        '.spark-drawer-item-details { flex: 1; display: flex; flex-direction: column; gap: 4px; min-width: 0; padding-right: 28px; }',
        '.spark-drawer-item-title {' +
        '  font-size: 14px; font-weight: 500; color: #1E293B; text-decoration: none;' +
        '  line-height: 1.35; word-break: break-word; overflow-wrap: anywhere;' +
        '}',
        '.spark-drawer-item-title:hover { color: #475569; }',
        '.spark-drawer-item-variant { font-size: 12px; color: #94A3B8; }',
        '.spark-drawer-item-sub { font-size: 12px; color: #64748B; }',
        '.spark-drawer-item-bottom { display: flex; align-items: center; justify-content: space-between; margin-top: auto; }',
        '.spark-drawer-item-qty { display: inline-flex; align-items: center; gap: 0; }',
        '.spark-drawer-qty-btn {' +
        '  width: 28px; height: 28px; border: 1px solid #E2E8F0; background: transparent;' +
        '  color: #475569; font-size: 14px; cursor: pointer; display: inline-flex;' +
        '  align-items: center; justify-content: center; padding: 0;' +
        '  transition: background-color 150ms ease-out;' +
        '}',
        '.spark-drawer-qty-btn:hover:not(:disabled) { background-color: #F8FAFC; }',
        '.spark-drawer-qty-btn:disabled { opacity: 0.3; cursor: not-allowed; }',
        '.spark-drawer-qty-btn:focus-visible { outline: 2px solid var(--primary-color, #1E293B); outline-offset: 2px; }',
        '.spark-drawer-qty-val {' +
        '  width: 36px; height: 28px; display: inline-flex; align-items: center; justify-content: center;' +
        '  font-size: 13px; border-top: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;' +
        '}',
        '.spark-drawer-item-price { font-size: 14px; font-weight: 500; text-align: right; white-space: nowrap; }',
        '.spark-drawer-item-compare { text-decoration: line-through; color: #94A3B8; font-weight: 400; font-size: 12px; }',
        '.spark-drawer-item-free { color: #22C55E; font-weight: 600; font-size: 13px; }',
        '.spark-drawer-item-remove {' +
        '  position: absolute; top: 16px; right: 0; background: none; border: none;' +
        '  cursor: pointer; padding: 4px; color: #94A3B8;' +
        '  transition: color 150ms ease-out; line-height: 0;' +
        '}',
        '.spark-drawer-item-remove:hover { color: #EF4444; }',
        /* Inset focus outline so the focus ring stays inside the panel even */
        /* when the remove button is flush with the body's right edge.       */
        '.spark-drawer-item-remove:focus-visible { outline: 2px solid var(--primary-color, #1E293B); outline-offset: -2px; }',

        /* Voucher */
        '.spark-drawer-voucher { padding: 12px 0; border-top: 1px solid #E2E8F0; }',
        '.spark-drawer-voucher-form { display: flex; gap: 8px; }',
        '.spark-drawer-voucher-input {' +
        '  flex: 1; padding: 8px 12px; border: 1px solid #E2E8F0; font-size: 13px;' +
        '  font-family: var(--font-body, inherit); color: #1E293B;' +
        '}',
        '.spark-drawer-voucher-input:focus { outline: 2px solid var(--primary-color, #1E293B); outline-offset: -2px; }',
        '.spark-drawer-voucher-btn {' +
        '  padding: 8px 16px; background: transparent; border: 1px solid #E2E8F0;' +
        '  font-size: 13px; font-weight: 500; cursor: pointer; color: #1E293B;' +
        '  font-family: var(--font-body, inherit); transition: background-color 150ms ease-out;' +
        '}',
        '.spark-drawer-voucher-btn:hover { background: #F8FAFC; }',
        '.spark-drawer-voucher-btn:focus-visible { outline: 2px solid var(--primary-color, #1E293B); outline-offset: 2px; }',
        '.spark-drawer-voucher-btn:disabled { opacity: 0.5; cursor: not-allowed; }',
        '.spark-drawer-voucher-error { font-size: 12px; color: #EF4444; margin-top: 4px; }',
        '.spark-drawer-voucher-applied { display: flex; align-items: center; justify-content: space-between; padding: 4px 0; font-size: 13px; }',
        '.spark-drawer-voucher-tag { display: inline-flex; align-items: center; gap: 4px; color: #22C55E; }',
        '.spark-drawer-voucher-remove {' +
        '  background: none; border: none; cursor: pointer; color: #94A3B8; padding: 2px;' +
        '  line-height: 0; transition: color 150ms ease-out;' +
        '}',
        '.spark-drawer-voucher-remove:hover { color: #EF4444; }',

        /* Footer */
        '.spark-drawer-footer {' +
        '  flex-shrink: 0; padding: 16px 20px; border-top: 1px solid #E2E8F0;' +
        '  background: #fff;' +
        '}',
        '.spark-drawer-totals { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }',
        '.spark-drawer-total-row { display: flex; justify-content: space-between; font-size: 14px; }',
        '.spark-drawer-total-row.discount { color: #22C55E; }',
        '.spark-drawer-total-row.grand { font-weight: 600; font-size: 16px; }',
        '.spark-drawer-checkout {' +
        '  display: block; width: 100%; padding: 12px; text-align: center;' +
        '  background: var(--primary-color, #1E293B); color: #fff; text-decoration: none;' +
        '  font-size: 15px; font-weight: 500; border: none; border-radius: 4px;' +
        '  cursor: pointer; transition: opacity 150ms ease-out;' +
        '  font-family: var(--font-body, inherit);' +
        '}',
        '[data-light-primary] .spark-drawer-checkout { color: #1E293B; }',
        '.spark-drawer-checkout:hover { opacity: 0.9; }',
        '.spark-drawer-checkout:focus-visible { outline: 2px solid var(--primary-color, #1E293B); outline-offset: 2px; }',
        '.spark-drawer-continue {' +
        '  display: block; text-align: center; margin-top: 10px; font-size: 13px;' +
        '  color: #475569; text-decoration: none; cursor: pointer; background: none; border: none;' +
        '  font-family: var(--font-body, inherit); padding: 4px;' +
        '}',
        '.spark-drawer-continue:hover { color: #1E293B; }',
        '.spark-drawer-announcement {' +
        '  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;' +
        '  overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;' +
        '}'
    ].join('\n');

    /* --- SparkCartDrawer Web Component --- */

    var template = document.createElement('template');
    template.innerHTML = '<style>' + DRAWER_STYLES + '</style>' +
        '<div class="spark-drawer-backdrop" data-action="close"></div>' +
        '<div class="spark-drawer-panel" role="document">' +
        '  <div class="spark-drawer-header">' +
        '    <h2 class="spark-drawer-header-title"></h2>' +
        '    <button class="spark-drawer-close" data-action="close">' +
        '      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
        '    </button>' +
        '  </div>' +
        '  <div class="spark-drawer-announcement" role="status" aria-live="polite"></div>' +
        '  <slot name="progress"></slot>' +
        '  <div class="spark-drawer-body"></div>' +
        '  <slot name="upsells"></slot>' +
        '  <div class="spark-drawer-footer" style="display:none;"></div>' +
        '</div>';

    class SparkCartDrawerEl extends HTMLElement {

    connectedCallback() {
        var self = this;
        this._cart = null;
        this._isOpen = false;
        this._isLoading = false;

        // Read data attributes from host (set by DTL template)
        this._checkoutUrl = this.getAttribute('data-checkout-url') || '/checkout/';
        this._headerTitle = this.getAttribute('data-header-title') || 'Your Cart';
        this._emptyTitle = this.getAttribute('data-empty-title') || 'Your cart is empty';
        this._emptySub = this.getAttribute('data-empty-sub') || 'Add items to get started';
        this._continueCta = this.getAttribute('data-continue-text') || 'Continue Shopping';
        this._continueUrl = this.getAttribute('data-continue-url') || '/';
        this._checkoutText = this.getAttribute('data-checkout-text') || 'Proceed to Checkout';
        this._subtotalText = this.getAttribute('data-subtotal-text') || 'Subtotal';
        this._discountText = this.getAttribute('data-discount-text') || 'Discount';
        this._shippingText = this.getAttribute('data-shipping-text') || 'Calculated at checkout';
        this._couponPlaceholder = this.getAttribute('data-coupon-placeholder') || 'Coupon code';
        this._couponBtn = this.getAttribute('data-coupon-btn') || 'Apply';
        this._closeCartLabel = this.getAttribute('data-close-cart-label') || 'Close cart';
        this._freeText = this.getAttribute('data-free-text') || 'Free';
        this._frequencyTemplate = this.getAttribute('data-frequency-template') || 'Every {count} {interval}';
        this._decreaseQuantityLabel = this.getAttribute('data-decrease-quantity-label') || 'Decrease quantity';
        this._quantityLabel = this.getAttribute('data-quantity-label') || 'Quantity';
        this._increaseQuantityLabel = this.getAttribute('data-increase-quantity-label') || 'Increase quantity';
        this._removeItemLabel = this.getAttribute('data-remove-item-label') || 'Remove {title}';
        this._removeVoucherLabel = this.getAttribute('data-remove-voucher-label') || 'Remove voucher';
        this._shippingLabel = this.getAttribute('data-shipping-label') || 'Shipping';
        this._totalLabel = this.getAttribute('data-total-label') || 'Total';
        this._invalidCouponText = this.getAttribute('data-invalid-coupon-text') || 'Invalid coupon code';
        var messages = window.SparkI18n || {};
        this._itemRemovedAnnouncement = messages.cartItemRemoved || 'Item removed from cart.';
        this._quantityUpdatedAnnouncement = messages.cartQuantityUpdated || 'Cart quantity updated.';
        this._giftProductId = this.getAttribute('data-gift-product-id') || '';
        this._currencyCode = this.getAttribute('data-currency') || 'USD';
        this._openOnAdd = this.getAttribute('data-open-on-add') !== 'false';
        this._labels = {
            checkoutUrl: this._checkoutUrl,
            headerTitle: this._headerTitle,
            emptyTitle: this._emptyTitle,
            emptySub: this._emptySub,
            continueCta: this._continueCta,
            continueUrl: this._continueUrl,
            checkoutText: this._checkoutText,
            subtotalText: this._subtotalText,
            discountText: this._discountText,
            shippingText: this._shippingText,
            couponPlaceholder: this._couponPlaceholder,
            couponBtn: this._couponBtn,
            freeText: this._freeText,
            frequencyTemplate: this._frequencyTemplate,
            decreaseQuantityLabel: this._decreaseQuantityLabel,
            quantityLabel: this._quantityLabel,
            increaseQuantityLabel: this._increaseQuantityLabel,
            removeItemLabel: this._removeItemLabel,
            removeVoucherLabel: this._removeVoucherLabel,
            shippingLabel: this._shippingLabel,
            totalLabel: this._totalLabel,
            invalidCouponText: this._invalidCouponText
        };

        // Attach shadow DOM
        var shadow = this.attachShadow({ mode: 'open' });
        shadow.appendChild(template.content.cloneNode(true));

        // Cache references
        this._backdrop = shadow.querySelector('.spark-drawer-backdrop');
        this._panel = shadow.querySelector('.spark-drawer-panel');
        this._titleEl = shadow.querySelector('.spark-drawer-header-title');
        this._body = shadow.querySelector('.spark-drawer-body');
        this._footer = shadow.querySelector('.spark-drawer-footer');
        this._closeBtn = shadow.querySelector('.spark-drawer-close');
        this._announcementEl = shadow.querySelector('.spark-drawer-announcement');

        this._titleEl.textContent = this._headerTitle;
        if (this._closeBtn) this._closeBtn.setAttribute('aria-label', this._closeCartLabel);
        this.removeAttribute('hidden');
        this.setAttribute('data-open', 'false');

        // Progress bar reference (slotted from light DOM)
        this._progressBar = this.querySelector('spark-progress-bar');

        // Mutation guard - prevents concurrent GraphQL calls from rapid clicks
        this._isMutating = false;

        // Track gift state. Gift bookkeeping is reconciled against every
        // cart snapshot (see _reconcileGift), not just threshold edges.
        this._giftLineId = null;
        this._isCartContainsGift = false;
        this._giftMutationInFlight = false;
        this._giftDeclined = false;
        this._giftAutoAttempts = 0;
        // Bumped whenever a cart snapshot is applied; in-flight gift
        // mutations use it to detect that their result is stale
        this._cartVersion = 0;

        // Get cart client
        this._client = window.SparkCartClient ? new SparkCartClient() : null;

        // Click handler (delegation)
        shadow.addEventListener('click', function(e) {
            var target = e.target.closest('[data-action]');
            if (!target) return;
            var action = target.getAttribute('data-action');

            if (action === 'close') {
                self.closeCart();
            } else if (action === 'decrease') {
                self._handleQtyChange(target, -1);
            } else if (action === 'increase') {
                self._handleQtyChange(target, 1);
            } else if (action === 'remove') {
                self._handleRemove(target);
            } else if (action === 'apply-voucher') {
                self._handleApplyVoucher();
            } else if (action === 'remove-voucher') {
                var vid = target.getAttribute('data-voucher-id');
                if (vid) self._handleRemoveVoucher(vid);
            }
        });

        // Voucher form enter key
        shadow.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.target.classList.contains('spark-drawer-voucher-input')) {
                e.preventDefault();
                self._handleApplyVoucher();
            }
        });

        // Global event listeners
        this._onCartAdded = function(e) {
            var detail = e.detail || {};
            if (detail.cart) {
                self._cart = detail.cart;
                self._cartVersion++;
                self._resetGiftAttemptsForExternalSnapshot();
                self._currencyCode = detail.cart.currency || self._currencyCode;
                self._renderCart();
            }
            if (self._openOnAdd && detail.openSideCart !== false) {
                self.openCart();
            }
        };

        this._onCartToggle = function() {
            self.toggleCart();
        };

        this._onCartUpdated = function(e) {
            var detail = e.detail || {};
            self._announceCartUpdate(detail.action);
            if (detail.cart) {
                self._cart = detail.cart;
                self._cartVersion++;
                self._resetGiftAttemptsForExternalSnapshot();
                self._currencyCode = detail.cart.currency || self._currencyCode;
                self._renderCart();
            }
        };

        this._onKeydown = function(e) {
            if (e.key === 'Escape' && self._isOpen) {
                self.closeCart();
            }
        };

        // Gift threshold listeners (from progress bar). Edges are only a
        // wake-up signal; the reconciler recomputes desired state from the
        // current cart snapshot so a stale edge cannot double-apply.
        // Intentional: only the drawer's configured gift program (host
        // attribute or its own progress bar's [data-gift] child) is
        // reconciled; e.detail.giftId from unrelated progress bars is
        // ignored to avoid cross-program cart mutations
        this._onGiftReached = function() {
            self._reconcileGift();
        };
        this._onGiftUnreached = function() {
            // Dropping below the threshold resets a shopper's explicit
            // decline; the offer is presented fresh on the next crossing
            self._giftDeclined = false;
            self._reconcileGift();
        };

        document.addEventListener('spark:cart:added', this._onCartAdded);
        document.addEventListener('spark:cart:toggle', this._onCartToggle);
        document.addEventListener('spark:cart:updated', this._onCartUpdated);
        document.addEventListener('keydown', this._onKeydown);
        document.addEventListener('spark:progress:gift-reached', this._onGiftReached);
        document.addEventListener('spark:progress:gift-unreached', this._onGiftUnreached);

        // Expose SparkSideCart API for backward compat
        var drawer = this;
        window.SparkSideCart = {
            open: function() { drawer.openCart(); },
            close: function() { drawer.closeCart(); },
            toggle: function() { drawer.toggleCart(); },
            isOpen: function() { return drawer._isOpen; }
        };

        if (window.SparkCartInitialCart) {
            this._cart = window.SparkCartInitialCart;
            this._currencyCode = this._cart.currency || this._currencyCode;
            this._renderCart();
        }
    };

    disconnectedCallback() {
        this._cancelAnnounce();
        document.removeEventListener('spark:cart:added', this._onCartAdded);
        document.removeEventListener('spark:cart:toggle', this._onCartToggle);
        document.removeEventListener('spark:cart:updated', this._onCartUpdated);
        document.removeEventListener('keydown', this._onKeydown);
        document.removeEventListener('spark:progress:gift-reached', this._onGiftReached);
        document.removeEventListener('spark:progress:gift-unreached', this._onGiftUnreached);
    };

    /* --- Open / Close / Toggle --- */

    openCart() {
        if (this._isOpen) return;
        this._isOpen = true;
        this.setAttribute('data-open', 'true');
        this.setAttribute('aria-expanded', 'true');
        document.body.classList.add('sidecart-open');

        // Load cart if we don't have data
        if (!this._cart) {
            this._loadCart();
        }

        // Focus close button
        var closeBtn = this._closeBtn;
        if (closeBtn) {
            var btn = closeBtn;
            setTimeout(function() { btn.focus(); }, 50);
        }
    };

    closeCart() {
        if (!this._isOpen) return;
        this._isOpen = false;
        this.setAttribute('data-open', 'false');
        this.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('sidecart-open');

        // Return focus to cart icon
        var cartIcon = document.getElementById('cart-icon');
        if (cartIcon) cartIcon.focus();
    };

    toggleCart() {
        if (this._isOpen) {
            this.closeCart();
        } else {
            this.openCart();
        }
    };

    /* --- Load cart via GraphQL --- */

    _loadCart() {
        var self = this;
        if (!this._client) return;

        this._setLoading(true);
        this._client.getCart().then(function(cart) {
            self._cart = cart;
            self._cartVersion++;
            self._resetGiftAttemptsForExternalSnapshot();
            if (cart) {
                self._currencyCode = cart.currency || self._currencyCode;
            }
            self._renderCart();
            self._setLoading(false);
        }).catch(function() {
            self._setLoading(false);
            self._renderEmpty();
        });
    };

    /* --- Rendering --- */

    _announceCartUpdate(action) {
        if (!this._announcementEl) return;
        var message = '';
        if (action === 'remove') {
            message = this._itemRemovedAnnouncement;
        } else if (action === 'update') {
            message = this._quantityUpdatedAnnouncement;
        }
        this._cancelAnnounce();
        this._announcementEl.textContent = '';
        if (!message) return;
        /* Defer the set so a repeated identical message is not coalesced into a
           single accessibility-tree update. Double requestAnimationFrame lets the
           cleared region commit in one paint before the message lands in the next,
           which some screen readers require to re-announce; fall back to a task
           when rAF is unavailable (SSR / test env). */
        var self = this;
        if (typeof requestAnimationFrame === 'function') {
            this._announceRaf = requestAnimationFrame(function() {
                self._announceRaf = requestAnimationFrame(function() {
                    self._announceRaf = null;
                    self._announcementEl.textContent = message;
                });
            });
        } else {
            this._announceTimer = setTimeout(function() {
                self._announceTimer = null;
                self._announcementEl.textContent = message;
            }, 0);
        }
    };

    _cancelAnnounce() {
        if (this._announceTimer) {
            clearTimeout(this._announceTimer);
            this._announceTimer = null;
        }
        if (this._announceRaf && typeof cancelAnimationFrame === 'function') {
            cancelAnimationFrame(this._announceRaf);
            this._announceRaf = null;
        }
    };

    _setLoading(loading) {
        this._isLoading = loading;
        if (loading) {
            this._body.innerHTML = '<div class="spark-drawer-loading"><div class="spark-drawer-spinner"></div></div>';
            this._footer.style.display = 'none';
        }
    };

    _renderCart() {
        var cart = this._cart;
        if (!cart || !cart.lines || cart.lines.length === 0) {
            this._renderEmpty();
            return;
        }

        var currency = this._currencyCode;
        // Render items
        var lines = cart.lines || [];
        var renderer = window.SparkCartDrawerRenderer;
        var frag = renderer.createItemsFragment(lines, currency, document, this._labels);

        this._body.innerHTML = '';
        var itemsContainer = document.createElement('div');
        itemsContainer.className = 'spark-drawer-items';
        itemsContainer.appendChild(frag);
        this._body.appendChild(itemsContainer);
        this._body.insertAdjacentHTML('beforeend', renderer.voucherHtml(cart, currency, this._labels));

        // Footer with totals
        var total = Number(cart.totalExclTax || 0);

        this._footer.innerHTML = renderer.footerHtml(cart, currency, this._labels);
        this._footer.style.display = '';

        // Update progress bar value (lazy query - children may not be ready in connectedCallback)
        if (!this._progressBar) {
            this._progressBar = this.querySelector('spark-progress-bar');
        }

        // Track gift state BEFORE updating the progress bar: the bar emits
        // threshold events synchronously, and their handlers must see this
        // snapshot's gift bookkeeping, not the previous snapshot's
        this._trackGiftState(cart);

        if (window.SparkCartRewards) {
            SparkCartRewards.updateProgressBar(this._progressBar, total);
        } else if (this._progressBar) {
            this._progressBar.setAttribute('data-value', String(total));
        }

        // Update upsell visibility
        this._updateUpsellVisibility(cart);

        // Repair gift drift that produces no threshold edge (external
        // add/remove between snapshots on the same side of the threshold)
        this._reconcileGift();
    };

    _renderEmpty() {
        this._body.innerHTML = SparkCartDrawerRenderer.emptyHtml(this._labels);
        this._footer.style.display = 'none';

        // Reset gift bookkeeping; stale flags must not survive an emptied
        // cart or they suppress the auto-add on the next eligible cart
        this._isCartContainsGift = false;
        this._giftLineId = null;
        this._giftDeclined = false;
        this._giftAutoAttempts = 0;

        // Hide upsells and reset progress bar when empty
        if (window.SparkCartRewards) {
            SparkCartRewards.hideUpsells(this);
        } else {
            var upsells = this.querySelectorAll('spark-upsell-item');
            for (var i = 0; i < upsells.length; i++) {
                upsells[i].style.display = 'none';
            }
        }
        if (!this._progressBar) {
            this._progressBar = this.querySelector('spark-progress-bar');
        }
        if (window.SparkCartRewards) {
            SparkCartRewards.updateProgressBar(this._progressBar, 0);
        } else if (this._progressBar) {
            this._progressBar.setAttribute('data-value', '0');
        }
    };

    /* --- Item interactions --- */

    _handleQtyChange(btn, delta) {
        var self = this;
        if (this._isMutating) return;
        var itemEl = btn.closest('.spark-drawer-item');
        if (!itemEl || !this._client || !this._cart) return;

        var lineId = itemEl.getAttribute('data-line-id');
        var line = this._findLine(lineId);
        if (!line) return;

        var newQty = line.quantity + delta;
        if (newQty <= 0) {
            return this._handleRemoveByLineId(lineId, itemEl);
        }

        this._isMutating = true;
        itemEl.setAttribute('data-loading', 'true');
        this._client.updateCartLines(this._cart.id, [{ lineId: lineId, quantity: newQty }])
            .then(function(result) {
                self._isMutating = false;
                if (result && result.cart) {
                    self._cart = result.cart;
                    self._cartVersion++;
                    self._renderCart();
                }
            }).catch(function() {
                self._isMutating = false;
                itemEl.setAttribute('data-loading', 'false');
            });
    };

    _handleRemove(btn) {
        var itemEl = btn.closest('.spark-drawer-item');
        if (!itemEl) return;
        var lineId = itemEl.getAttribute('data-line-id');
        this._handleRemoveByLineId(lineId, itemEl);
    };

    _handleRemoveByLineId(lineId, itemEl) {
        var self = this;
        if (this._isMutating || !this._client || !this._cart) return;

        // Removing the gift line by hand is an explicit decline; the
        // reconciler must not force the gift back while the cart stays
        // above the threshold. Dropping below the threshold resets this.
        // Deliberately NOT rolled back if the removal request fails: the
        // flag records shopper intent, and the reconciler completes the
        // failed removal on the next snapshot instead of silently
        // keeping a gift the shopper asked to remove
        if (this._giftLineId && String(lineId) === String(this._giftLineId)) {
            this._giftDeclined = true;
        }

        this._isMutating = true;
        if (itemEl) itemEl.setAttribute('data-loading', 'true');
        this._client.removeCartLines(this._cart.id, [lineId])
            .then(function(result) {
                self._isMutating = false;
                if (result && result.cart) {
                    self._cart = result.cart;
                    self._cartVersion++;
                    self._renderCart();
                }
            }).catch(function() {
                self._isMutating = false;
                if (itemEl) itemEl.setAttribute('data-loading', 'false');
            });
    };

    _findLine(lineId) {
        if (!this._cart || !this._cart.lines) return null;
        for (var i = 0; i < this._cart.lines.length; i++) {
            if (String(this._cart.lines[i].pk) === String(lineId)) return this._cart.lines[i];
        }
        return null;
    };

    /* --- Gift auto-management --- */

    /* The corrective-mutation cap is per external snapshot: a fresh snapshot
       from outside a gift mutation (page event, other component, recovered
       API) re-arms auto-management. Mutation-produced snapshots must NOT
       reset it, or a cart that never converges would be mutated forever.
       Gift-mutation results dispatch spark:cart:updated while the mutation
       is still in flight, which is what the guard below distinguishes. */
    _resetGiftAttemptsForExternalSnapshot() {
        if (!this._giftMutationInFlight) {
            this._giftAutoAttempts = 0;
        }
    };

    /* Track containsGift / giftLineId bookkeeping from a cart snapshot */
    _trackGiftState(cart) {
        var config = this._giftConfig();
        var trackId = (config && config.productId) || this._giftProductId;
        if (window.SparkCartRewards && trackId) {
            var giftState = SparkCartRewards.giftState(cart, trackId);
            this._isCartContainsGift = giftState.containsGift;
            this._giftLineId = giftState.lineId;
        } else {
            this._isCartContainsGift = false;
            this._giftLineId = null;
        }
    };

    /* Gift product id + threshold, from the host attribute and the progress
       bar's [data-gift] child. Null when no gift program is configured. */
    _giftConfig() {
        if (!this._progressBar) {
            this._progressBar = this.querySelector('spark-progress-bar');
        }
        var productId = this._giftProductId;
        var threshold = NaN;
        var giftMsg = this._progressBar ? this._progressBar.querySelector('[data-gift]') : null;
        if (giftMsg) {
            threshold = parseFloat(giftMsg.getAttribute('data-value'));
            if (!productId) productId = giftMsg.getAttribute('data-gift-id') || '';
        }
        if (!productId || isNaN(threshold)) return null;
        return { productId: productId, threshold: threshold };
    };

    /* Desired-state reconciler: compares what the current cart snapshot
       SHOULD contain (total vs threshold, minus an explicit shopper decline)
       with what it DOES contain, and issues at most one corrective mutation.
       Runs on every render and after every gift mutation settles, so drift
       converges regardless of whether a threshold edge fired. */
    _reconcileGift() {
        if (!this._client || !window.SparkCartRewards) return;
        if (this._giftMutationInFlight) return;
        var config = this._giftConfig();
        if (!config) return;

        var cart = this._cart;
        var hasLines = !!(cart && cart.lines && cart.lines.length);
        var total = hasLines ? Number(cart.totalExclTax || 0) : 0;
        var desired = hasLines && total >= config.threshold && !this._giftDeclined;
        if (desired === this._isCartContainsGift) {
            this._giftAutoAttempts = 0;
            return;
        }
        // Cap consecutive corrective mutations so a snapshot that never
        // converges (e.g. an API that drops the gift line) cannot storm
        // the GraphQL endpoint. The cap is per external snapshot: see
        // _resetGiftAttemptsForExternalSnapshot
        if (this._giftAutoAttempts >= 3) return;
        this._giftAutoAttempts++;
        this._toggleGift(desired, config.productId);
    };

    _toggleGift(shouldAdd, giftProductId) {
        var self = this;
        if (!this._client || !this._cart) return;
        if (this._giftMutationInFlight) return;

        if (shouldAdd && this._isCartContainsGift) return;
        if (!shouldAdd && (!this._isCartContainsGift || !this._giftLineId)) return;

        var startVersion = this._cartVersion;
        this._giftMutationInFlight = true;

        var promise = window.SparkCartRewards
            ? SparkCartRewards.toggleGift(this._client, this._cart, shouldAdd, giftProductId, this._giftLineId)
            : (shouldAdd
                ? this._client.addToCart(Number(giftProductId), 1, true)
                : this._client.removeCartLines(this._cart.id, [this._giftLineId]));

        promise.then(function(result) {
            self._giftMutationInFlight = false;
            if (self._cartVersion !== startVersion) {
                // A newer cart snapshot arrived while this mutation was in
                // flight; its result is stale. Drop it and reconcile against
                // the current snapshot instead of overwriting it
                self._reconcileGift();
                return;
            }
            if (result && result.cart) {
                self._cart = result.cart;
                self._cartVersion++;
                self._renderCart();
            }
        }).catch(function() {
            self._giftMutationInFlight = false;
        });
    };

    /* --- Upsell visibility --- */

    _updateUpsellVisibility(cart) {
        if (window.SparkCartRewards) {
            SparkCartRewards.updateUpsellVisibility(this, cart);
        }
    };

    /* --- Voucher interactions --- */

    _handleApplyVoucher() {
        var self = this;
        if (this._isMutating || !this._client || !this._cart) return;

        var input = this.shadowRoot.querySelector('.spark-drawer-voucher-input');
        var errorEl = this.shadowRoot.querySelector('.spark-drawer-voucher-error');
        var btn = this.shadowRoot.querySelector('.spark-drawer-voucher-btn');
        if (!input) return;

        var code = input.value.trim();
        if (!code) return;

        this._isMutating = true;
        if (btn) btn.disabled = true;
        if (errorEl) { errorEl.style.display = 'none'; errorEl.textContent = ''; }

        this._client.addVoucher(this._cart.id, code)
            .then(function(result) {
                self._isMutating = false;
                if (btn) btn.disabled = false;
                if (result && result.errors && result.errors.length) {
                    if (errorEl) {
                        errorEl.textContent = result.errors[0];
                        errorEl.style.display = '';
                    }
                    return;
                }
                if (result && result.cart) {
                    self._cart = result.cart;
                    self._cartVersion++;
                    self._renderCart();
                }
            }).catch(function(err) {
                self._isMutating = false;
                if (btn) btn.disabled = false;
                if (errorEl) {
                    errorEl.textContent = err.message || self._labels.invalidCouponText;
                    errorEl.style.display = '';
                }
            });
    };

    _handleRemoveVoucher(voucherId) {
        var self = this;
        if (!this._client || !this._cart) return;

        this._client.removeVoucher(this._cart.id, voucherId)
            .then(function(result) {
                if (result && result.cart) {
                    self._cart = result.cart;
                    self._cartVersion++;
                    self._renderCart();
                }
            }).catch(function() {
                // Silently fail - voucher may already be removed
            });
    }

    } /* end class SparkCartDrawerEl */

    if (typeof customElements !== 'undefined' && !customElements.get('spark-cart-drawer')) {
        customElements.define('spark-cart-drawer', SparkCartDrawerEl);
    }

})();
