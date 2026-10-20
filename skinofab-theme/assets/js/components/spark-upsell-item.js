/**
 * Spark Theme - Upsell Item Web Component
 *
 * Renders a single upsell product slot in the side cart.
 * Hidden by default; the cart drawer shows/hides based on
 * product metadata (cart_upsell_slots).
 *
 * DTL template renders product data (image, title, price, variant select).
 * JS handles the "Add" button click via SparkCartClient.
 */

(function() {
    'use strict';

    class SparkUpsellItemEl extends HTMLElement {

    connectedCallback() {
        var self = this;
        this._client = window.SparkCartClient ? new SparkCartClient() : null;
        this._addBtn = this.querySelector('[data-upsell-add-btn]');
        this._variantSelect = this.querySelector('[data-upsell-variant-select]');
        this._priceEl = this.querySelector('[data-upsell-price]');

        // Update price on variant change
        if (this._variantSelect && this._variantSelect.tagName === 'SELECT') {
            this._variantSelect.addEventListener('change', function() {
                self._updateDisplayPrice();
            });
        }

        // Add to cart on button click
        if (this._addBtn) {
            this._addBtn.addEventListener('click', function() {
                self._addSelectedVariant();
            });
        }
    };

    _getSelectedProductPk() {
        if (!this._variantSelect) return null;
        return Number(this._variantSelect.value) || null;
    };

    _updateDisplayPrice() {
        if (!this._variantSelect || !this._priceEl) return;
        var option = this._variantSelect.options
            ? this._variantSelect.options[this._variantSelect.selectedIndex]
            : null;
        if (option) {
            var price = option.getAttribute('data-price');
            var currency = option.getAttribute('data-currency') || 'USD';
            if (price && window.SparkCartClient) {
                this._priceEl.textContent = SparkCartClient.formatMoney(Number(price), currency);
            }
        }
    };

    _addSelectedVariant() {
        var self = this;
        var pk = this._getSelectedProductPk();
        if (!pk || !this._client) return;

        var cartId = this._client.getCartId();
        if (!cartId) return;

        this._setLoading(true);
        this._client.addToCart(pk, 1, false)
            .then(function(result) {
                self._setLoading(false);
                // Cart drawer will re-render and hide this upsell if product now in cart
            }).catch(function() {
                self._setLoading(false);
            });
    };

    _setLoading(loading) {
        this.setAttribute('data-loading', loading ? 'true' : 'false');
        if (this._addBtn) this._addBtn.disabled = loading;
    }

    } /* end class SparkUpsellItemEl */

    if (typeof customElements !== 'undefined' && !customElements.get('spark-upsell-item')) {
        customElements.define('spark-upsell-item', SparkUpsellItemEl);
    }

})();
