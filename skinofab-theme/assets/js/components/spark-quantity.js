/**
 * <spark-quantity> Web Component
 *
 * Shadow DOM quantity stepper: [-] | input | [+]
 * Progressive enhancement -wraps or replaces a plain <input type="number">.
 *
 * Attributes:
 *   min     -Minimum value (default: 1)
 *   max     -Maximum value (default: 99)
 *   value   -Current value (default: 1)
 *
 * Events:
 *   change  -Dispatched when value changes, with detail.value
 *
 * CSS custom properties inherited from host:
 *   --primary-color, --font-body
 *
 * Usage:
 *   <spark-quantity min="1" max="10" value="1"></spark-quantity>
 */

(function() {
    'use strict';

    var TEMPLATE = document.createElement('template');
    TEMPLATE.innerHTML = [
        '<style>',
        '  :host { display: inline-flex; align-items: center; }',
        '  button {',
        '    width: 36px; height: 36px;',
        '    border: 1px solid #E2E8F0;',
        '    background: transparent;',
        '    color: #475569;',
        '    font-size: 16px;',
        '    line-height: 1;',
        '    cursor: pointer;',
        '    display: inline-flex;',
        '    align-items: center;',
        '    justify-content: center;',
        '    padding: 0;',
        '    transition: background-color 150ms ease-out;',
        '    font-family: var(--font-body, inherit);',
        '  }',
        '  button:hover:not(:disabled) { background-color: #F8FAFC; }',
        '  button:disabled { opacity: 0.3; cursor: not-allowed; }',
        '  button:focus-visible {',
        '    outline: 2px solid var(--primary-color, #1E293B);',
        '    outline-offset: 2px;',
        '  }',
        '  input {',
        '    width: 48px; height: 36px;',
        '    text-align: center;',
        '    border: 1px solid #E2E8F0;',
        '    border-left: none; border-right: none;',
        '    font-size: 14px;',
        '    font-family: var(--font-body, inherit);',
        '    color: #1E293B;',
        '    -moz-appearance: textfield;',
        '    margin: 0; padding: 0;',
        '  }',
        '  input::-webkit-outer-spin-button,',
        '  input::-webkit-inner-spin-button {',
        '    -webkit-appearance: none; margin: 0;',
        '  }',
        '  input:focus-visible {',
        '    outline: 2px solid var(--primary-color, #1E293B);',
        '    outline-offset: 2px;',
        '  }',
        '</style>',
        '<button type="button" id="dec" aria-label="Decrease quantity">&minus;</button>',
        '<input type="text" id="qty" role="spinbutton" />',
        '<button type="button" id="inc" aria-label="Increase quantity">+</button>'
    ].join('\n');

    class SparkQuantity extends HTMLElement {
        static get observedAttributes() {
            return ['min', 'max', 'value'];
        }

        constructor() {
            super();
            this.attachShadow({ mode: 'open' });
            this.shadowRoot.appendChild(TEMPLATE.content.cloneNode(true));
            this._input = this.shadowRoot.getElementById('qty');
            this._dec = this.shadowRoot.getElementById('dec');
            this._inc = this.shadowRoot.getElementById('inc');
        }

        connectedCallback() {
            this._updateFromAttributes();
            this._bindEvents();

            // Create a hidden input in light DOM for form submission
            var name = this.getAttribute('name');
            if (name) {
                this._hidden = document.createElement('input');
                this._hidden.type = 'hidden';
                this._hidden.name = name;
                this._hidden.value = this._value;
                this.appendChild(this._hidden);
            }
        }

        attributeChangedCallback() {
            if (this._input) this._updateFromAttributes();
        }

        get _min() { return parseInt(this.getAttribute('min')) || 1; }
        get _max() { return parseInt(this.getAttribute('max')) || 99; }
        get _value() { return parseInt(this.getAttribute('value')) || 1; }

        _updateFromAttributes() {
            var val = this._clamp(this._value);
            this._input.value = val;
            this._input.setAttribute('aria-valuenow', val);
            this._input.setAttribute('aria-valuemin', this._min);
            this._input.setAttribute('aria-valuemax', this._max);
            this._updateButtons(val);
        }

        _clamp(v) {
            return Math.min(Math.max(v, this._min), this._max);
        }

        _setValue(v) {
            var clamped = this._clamp(v);
            this.setAttribute('value', clamped);
            this._input.value = clamped;
            this._input.setAttribute('aria-valuenow', clamped);
            this._updateButtons(clamped);
            if (this._hidden) this._hidden.value = clamped;
            this.dispatchEvent(new CustomEvent('change', {
                detail: { value: clamped },
                bubbles: true,
                composed: true
            }));
        }

        _updateButtons(val) {
            this._dec.disabled = val <= this._min;
            this._inc.disabled = val >= this._max;
        }

        _bindEvents() {
            var self = this;

            this._dec.addEventListener('click', function() {
                self._setValue(parseInt(self._input.value) - 1);
            });

            this._inc.addEventListener('click', function() {
                self._setValue(parseInt(self._input.value) + 1);
            });

            this._input.addEventListener('change', function() {
                var v = parseInt(self._input.value);
                if (isNaN(v)) v = self._min;
                self._setValue(v);
            });

            this._input.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    self._setValue(parseInt(self._input.value) + 1);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    self._setValue(parseInt(self._input.value) - 1);
                }
            });
        }
    }

    if (!customElements.get('spark-quantity')) {
        customElements.define('spark-quantity', SparkQuantity);
    }

})();
