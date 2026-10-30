/**
 * <spark-add-to-cart> Web Component
 *
 * Progressive enhancement for the add-to-cart form. Wraps the existing DTL
 * <form> - intercepts submit and uses GraphQL via SparkCartClient instead
 * of a full page reload.
 *
 * No-JS fallback: If this component fails to load, the DTL form submits
 * normally via traditional POST.
 *
 * Attributes:
 *   product-id   -The product PK (extracted from form action if not set)
 *   graphql-url  -GraphQL endpoint (default: /api/graphql/)
 *
 * States: idle -> loading -> success -> idle (or idle -> loading -> error -> idle)
 *
 * CSS custom properties inherited from host:
 *   --primary-color, --font-body
 *
 * Usage (in DTL template):
 *   <spark-add-to-cart product-id="PRODUCT_PK" graphql-url="GRAPHQL_URL">
 *     <form action="/cart/add/PRODUCT_PK/" method="post">
 *       ...existing form fields...
 *       <button type="submit">Add to Cart</button>
 *     </form>
 *   </spark-add-to-cart>
 */

(function() {
    'use strict';

    var SUCCESS_DURATION = 2000;  // Hold success state for 2s
    var SUCCESS_COLOR = '#22C55E';
    var ERROR_COLOR = '#EF4444';

    var STYLES = [
        '<style>',
        '  :host { display: block; }',
        '  ::slotted(form) { margin: 0; }',
        '',
        '  .spark-atc-error {',
        '    color: ' + ERROR_COLOR + ';',
        '    font-size: 0.875rem;',
        '    margin-top: 0.5rem;',
        '    opacity: 0;',
        '    transition: opacity 200ms ease-out;',
        '    font-family: var(--font-body, inherit);',
        '  }',
        '  .spark-atc-error.visible { opacity: 1; }',
        '</style>'
    ].join('\n');

    var TEMPLATE = document.createElement('template');
    TEMPLATE.innerHTML = STYLES + '<slot></slot><div class="spark-atc-error" role="alert" aria-live="polite"></div>';

    /* ---Spinner CSS (injected into light DOM once) ---*/
    var SPINNER_INJECTED = false;
    function injectSpinnerCSS() {
        if (SPINNER_INJECTED) return;
        SPINNER_INJECTED = true;
        var style = document.createElement('style');
        style.textContent = [
            '@keyframes spark-spinner { to { transform: rotate(360deg); } }',
            '.spark-atc-spinner {',
            '  display: inline-block;',
            '  width: 16px; height: 16px;',
            '  border: 2px solid rgba(255,255,255,0.3);',
            '  border-top-color: #fff;',
            '  border-radius: 50%;',
            '  animation: spark-spinner 800ms linear infinite;',
            '  vertical-align: middle;',
            '}',
            '[data-light-primary] .spark-atc-spinner {',
            '  border-color: rgba(30,41,59,0.3);',
            '  border-top-color: #1E293B;',
            '}',
            '@keyframes spark-shake {',
            '  0%, 100% { transform: translateX(0); }',
            '  15% { transform: translateX(4px); }',
            '  30% { transform: translateX(-4px); }',
            '  55% { transform: translateX(2px); }',
            '  75% { transform: translateX(-2px); }',
            '}',
            '.spark-atc-shake { animation: spark-shake 400ms ease-out; }'
        ].join('\n');
        document.head.appendChild(style);
    }

    class SparkAddToCart extends HTMLElement {
        constructor() {
            super();
            this.attachShadow({ mode: 'open' });
            this.shadowRoot.appendChild(TEMPLATE.content.cloneNode(true));
            this._errorEl = this.shadowRoot.querySelector('.spark-atc-error');
            this._client = null;
            this._form = null;
            this._button = null;
            this._originalText = '';
            this._labels = {};
            this._state = 'idle'; // idle | loading | success | error
        }

        connectedCallback() {
            injectSpinnerCSS();

            // Find the slotted form
            this._form = this.querySelector('form');
            if (!this._form) return;

            this._button = this._form.querySelector('button[type="submit"]');
            if (this._button) {
                this._originalText = this._button.textContent.trim();
            }
            this._labels = this._readLabels();

            // Initialize cart client
            var graphqlUrl = this.getAttribute('graphql-url') || '/api/graphql/';
            if (typeof SparkCartClient !== 'undefined') {
                this._client = new SparkCartClient(graphqlUrl);
            }

            // Intercept form submission
            var self = this;
            this._form.addEventListener('submit', function(e) {
                if (!self._client) return; // No client -fall through to normal form submit
                e.preventDefault();
                if (self._state === 'loading') return;
                self._handleSubmit();
            });
        }

        _getProductId() {
            // Prefer form action (updated by variant picker JS for parent products)
            if (this._form) {
                var action = this._form.getAttribute('action') || '';
                var match = action.match(/cart\/add\/(\d+)/);
                if (match) return parseInt(match[1]);
            }

            // Fall back to explicit attribute
            var id = this.getAttribute('product-id');
            if (id) return parseInt(id);

            return null;
        }

        _getQuantity() {
            if (!this._form) return 1;
            // Look for quantity input (platform uses id_quantity or name=quantity)
            var qtyInput = this._form.querySelector('input[name="quantity"]') ||
                           this._form.querySelector('#id_quantity') ||
                           this._form.querySelector('spark-quantity');
            if (qtyInput) {
                var val = parseInt(qtyInput.getAttribute('value') || qtyInput.value);
                if (!isNaN(val) && val > 0) return val;
            }
            return 1;
        }

        _getSubscription() {
            var subscriptionEl = this.querySelector('spark-subscription');
        
            if (!subscriptionEl) {
                return null;
            }
        
            if (subscriptionEl.value !== 'subscribe') {
                return null;
            }
        
            return {
                subscriptionOption: 'subscribe',
                interval: subscriptionEl.interval,
                intervalCount: subscriptionEl.intervalCount
            };
        }

        _readLabels() {
            var btn = this._button;
            function attr(name, fallback) {
                return btn ? (btn.getAttribute(name) || fallback) : fallback;
            }
            return {
                success: attr('data-success-text', 'Added'),
                productNotFound: attr('data-error-product-not-found', 'Product not found'),
                addError: attr('data-error-add-to-cart', 'Could not add to cart'),
                generic: attr('data-error-generic', 'Something went wrong - please try again'),
                connection: attr('data-error-connection', 'Connection issue - please try again'),
                unavailable: attr('data-error-unavailable', 'This item is unavailable'),
                subscriptionFrequency: attr('data-error-subscription-frequency', 'Please choose a valid subscription frequency.')
            };
        }

        _handleSubmit() {
            var productId = this._getProductId();
            if (!productId) {
                this._showError(this._labels.productNotFound);
                return;
            }

            var quantity = this._getQuantity();
            var subscriptionData = this._getSubscription();
            var self = this;

            if (subscriptionData && !subscriptionData.intervalCount) {
                this._showError(this._labels.subscriptionFrequency);
                return;
            }

            this._setState('loading');
            this._clearError();

            this._client.addToCart(productId, quantity, false, subscriptionData)
            .then(function(result) {
                if (result && result.success && result.cart) {
                    self._setState('success');
                    if (window.SparkEvents) {
                        SparkEvents.cartAdded(result.cart, self._getProductId(), quantity);
                    } else {
                        document.dispatchEvent(new CustomEvent('spark:cart:added', {
                            detail: {
                                cart: result.cart,
                                count: result.cart ? result.cart.numItems : 0,
                                productId: self._getProductId(),
                                quantity: quantity
                            },
                            bubbles: true
                        }));
                    }
                    setTimeout(function() {
                        if (self._state === 'success') {
                            self._setState('idle');
                        }
                    }, SUCCESS_DURATION);
                } else {
                    self._setState('error');
                    var errorMsg = self._labels.addError;
                    if (result && result.errors && result.errors.length) {
                        errorMsg = result.errors.join('. ');
                    }
                    self._showError(errorMsg);
                }
            }).catch(function(err) {
                self._setState('error');
                var msg = self._labels.generic;
                if (err.message) {
                    if (err.message.toLowerCase().indexOf('timeout') !== -1) {
                        msg = self._labels.connection;
                    } else if (err.message.toLowerCase().indexOf('unavailable') !== -1 ||
                               err.message.toLowerCase().indexOf('out of stock') !== -1) {
                        msg = self._labels.unavailable;
                    } else if (err.graphqlErrors) {
                        msg = err.message;
                    }
                }
                self._showError(msg);
                console.error('[spark-add-to-cart]', err);
            });
        }

        _setState(state) {
            this._state = state;
            if (!this._button) return;

            switch (state) {
                case 'loading':
                    this._button.disabled = true;
                    this._button.innerHTML = '<span class="spark-atc-spinner"></span>';
                    break;

                case 'success':
                    this._button.disabled = false;
                    this._button.textContent = this._labels.success;
                    this._button.style.backgroundColor = SUCCESS_COLOR;
                    this._button.style.borderColor = SUCCESS_COLOR;
                    break;

                case 'error':
                    this._button.disabled = false;
                    this._button.textContent = this._originalText;
                    this._button.style.backgroundColor = '';
                    this._button.style.borderColor = '';
                    // Shake animation
                    this._button.classList.add('spark-atc-shake');
                    var btn = this._button;
                    setTimeout(function() {
                        btn.classList.remove('spark-atc-shake');
                    }, 400);
                    break;

                case 'idle':
                default:
                    this._button.disabled = false;
                    this._button.textContent = this._originalText;
                    this._button.style.backgroundColor = '';
                    this._button.style.borderColor = '';
                    break;
            }
        }

        _showError(msg) {
            if (!this._errorEl) return;
            this._errorEl.textContent = msg;
            this._errorEl.classList.add('visible');
        }

        _clearError() {
            if (!this._errorEl) return;
            this._errorEl.textContent = '';
            this._errorEl.classList.remove('visible');
        }
    }

    if (!customElements.get('spark-add-to-cart')) {
        customElements.define('spark-add-to-cart', SparkAddToCart);
    }

})();
