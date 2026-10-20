/**
 * Spark Variant State
 *
 * Owns PDP selected-variant knowledge for radio and select pickers.
 * Adapters can listen for spark:variant:changed instead of re-parsing
 * product data, attribute controls, and child product matching.
 */

(function() {
    'use strict';

    var DEFAULT_DATA_ID = 'product-data';
    var DEFAULT_CONTROL_SELECTOR = '[name^="attr_"]';

    function parseJsonScript(id) {
        var el = document.getElementById(id || DEFAULT_DATA_ID);
        if (!el) return null;
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            return null;
        }
    }

    function readValue(control) {
        if (!control) return null;
        if ((control.type === 'radio' || control.type === 'checkbox') && !control.checked) {
            return null;
        }
        var raw = control.value;
        var parsed = parseInt(raw, 10);
        return isNaN(parsed) ? raw : parsed;
    }

    function valuesMatch(left, right) {
        return String(left) === String(right);
    }

    function basename(url) {
        var path = (url || '').split('?')[0].split('#')[0];
        return path.split('/').pop();
    }

    function SparkVariantState(options) {
        options = options || {};
        this.root = options.root || document;
        this.product = options.product || parseJsonScript(options.dataId || DEFAULT_DATA_ID);
        this.controlSelector = options.controlSelector || DEFAULT_CONTROL_SELECTOR;
        this._boundControls = [];
    }

    SparkVariantState.fromPage = function(options) {
        var state = new SparkVariantState(options || {});
        return state.product ? state : null;
    };

    SparkVariantState.getVariantImageUrl = function(variant) {
        if (!variant) return null;
        if (variant.primary_image && variant.primary_image.original) return variant.primary_image.original;
        if (variant.images && variant.images.length && variant.images[0].original) return variant.images[0].original;
        return null;
    };

    SparkVariantState.sameImageUrl = function(left, right) {
        if (!left || !right) return false;
        return left === right || basename(left) === basename(right);
    };

    SparkVariantState.isPurchasable = function(variant) {
        if (!variant || !variant.purchase_info) return true;
        var availability = variant.purchase_info.availability;
        return availability !== 'outofstock' && availability !== 'unavailable';
    };

    SparkVariantState.updateFormAction = function(form, variant) {
        if (!form || !variant || !variant.id) return;
        var action = form.getAttribute('action') || '';
        var next = action.replace(/(cart\/add\/)\d+/, '$1' + variant.id);
        form.setAttribute('action', next);
    };

    SparkVariantState.updatePrice = function(root, variant) {
        if (!root || !variant || !variant.purchase_info) return;

        var priceEl = root.querySelector('[data-price]');
        var retailEl = root.querySelector('[data-price-retail]');
        var price = variant.purchase_info.price;
        var retail = variant.purchase_info.price_retail;

        if (priceEl && price && price.format) {
            priceEl.textContent = price.format;
        }

        if (!retailEl) return;
        if (retail && price && Number(retail.price) > Number(price.price) && retail.format) {
            retailEl.textContent = retail.format;
            retailEl.hidden = false;
        } else {
            retailEl.textContent = '';
            retailEl.hidden = true;
        }
    };

    SparkVariantState.prototype.getControls = function() {
        return Array.prototype.slice.call(this.root.querySelectorAll(this.controlSelector));
    };

    SparkVariantState.prototype.getSelection = function() {
        var selected = {};
        this.getControls().forEach(function(control) {
            var value = readValue(control);
            if (value !== null && value !== '') {
                selected[control.name] = value;
            }
        });
        return selected;
    };

    SparkVariantState.prototype.getDefaultVariant = function() {
        if (!this.product || !this.product.children || !this.product.children.length) return null;
        return this.product.children[0];
    };

    SparkVariantState.prototype.getVariantFromSelection = function(selection) {
        var product = this.product;
        if (!product || !product.children || !product.children.length) return null;
        selection = selection || this.getSelection();

        return product.children.find(function(child) {
            if (!child.variant_attribute_values || !child.variant_attribute_values.length) return true;
            return child.variant_attribute_values.every(function(attr) {
                return valuesMatch(selection['attr_' + attr.code], attr.id);
            });
        }) || null;
    };

    SparkVariantState.prototype.getSelectedVariant = function() {
        return this.getVariantFromSelection(this.getSelection());
    };

    /**
     * Availability of every option value, given the rest of the current
     * selection. Returns { 'attr_<code>': { '<value id>': true|false } }.
     * A value is available when at least one purchasable child carries it
     * while matching every other selected attribute.
     */
    SparkVariantState.prototype.getOptionAvailability = function(selection) {
        var result = {};
        var product = this.product;
        if (!product || !product.children || !product.children.length) return result;
        selection = selection || this.getSelection();

        product.children.forEach(function(child) {
            var attributes = child.variant_attribute_values || [];
            var purchasable = SparkVariantState.isPurchasable(child);

            attributes.forEach(function(attribute) {
                var name = 'attr_' + attribute.code;
                if (!result[name]) result[name] = {};
                if (result[name][attribute.id] === undefined) {
                    result[name][attribute.id] = false;
                }

                var othersMatch = attributes.every(function(other) {
                    if (other.code === attribute.code) return true;
                    var chosen = selection['attr_' + other.code];
                    if (chosen === undefined || chosen === null || chosen === '') return true;
                    return valuesMatch(chosen, other.id);
                });
                if (!othersMatch) return;

                result[name][attribute.id] = result[name][attribute.id] || purchasable;
            });
        });

        return result;
    };

    SparkVariantState.prototype.emitChange = function(variant) {
        if (!variant) return;
        if (window.SparkEvents) {
            SparkEvents.variantChanged(this.product, variant, this.getSelection());
            return;
        }
        document.dispatchEvent(new CustomEvent('spark:variant:changed', {
            detail: {
                product: this.product,
                variant: variant,
                selection: this.getSelection()
            },
            bubbles: true
        }));
    };

    SparkVariantState.prototype.onChange = function(callback) {
        var self = this;
        var controls = this.getControls();
        this._boundControls = controls;
        controls.forEach(function(control) {
            control.addEventListener('change', function() {
                var variant = self.getSelectedVariant();
                if (!variant) return;
                if (callback) callback(variant, self.getSelection());
                self.emitChange(variant);
            });
        });
    };

    window.SparkVariantState = SparkVariantState;
})();
