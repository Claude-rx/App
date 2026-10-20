/**
 * Spark Theme - Progress Bar Web Component
 *
 * Multi-step progress bar for cart milestones (free shipping, free gift).
 * Currency-aware thresholds set via DTL template data attributes.
 * Dispatches events when thresholds are crossed so the cart drawer
 * can auto-add/remove free gifts.
 *
 * Events dispatched:
 *   spark:progress:shipping-reached / spark:progress:shipping-unreached
 *   spark:progress:gift-reached / spark:progress:gift-unreached
 */

(function() {
    'use strict';

    /* --- Light DOM styles (injected once for slotted elements) --- */
    var LIGHT_STYLES_INJECTED = false;
    function injectMsgStyles() {
        if (LIGHT_STYLES_INJECTED) return;
        LIGHT_STYLES_INJECTED = true;
        var s = document.createElement('style');
        s.textContent = [
            '.spark-progress-msg {',
            '  display: none; font-size: 13px; font-weight: 500; color: #475569;',
            '  font-family: var(--font-body, system-ui, -apple-system, sans-serif);',
            '  text-align: center; justify-content: center;',
            '}',
            '.spark-progress-msg.active { display: flex; align-items: center; gap: 6px; }',
            '.spark-progress-step {',
            '  width: 28px; height: 28px; border-radius: 50%;',
            '  background: #E2E8F0; border: 2px solid #fff;',
            '  display: flex; align-items: center; justify-content: center;',
            '  transition: background-color 300ms ease-out; z-index: 1;',
            '  color: #94A3B8;',
            '}',
            '.spark-progress-step[aria-checked="true"] {',
            '  background: var(--primary-color, #1E293B); color: #fff;',
            '}',
            '[data-light-primary] .spark-progress-step[aria-checked="true"] { color: #1E293B; }',
            '.spark-progress-step svg { width: 14px; height: 14px; }'
        ].join('\n');
        document.head.appendChild(s);
    }

    var PROGRESS_STYLES = [
        ':host { display: block; padding: 0 20px; }',

        '.spark-progress-messages { margin-bottom: 10px; min-height: 20px; }',

        '.spark-progress-track {' +
        '  position: relative; height: 6px; background: #E2E8F0; border-radius: 3px;' +
        '  overflow: visible; margin: 0 14px;' +
        '}'  /* margin accounts for step marker radius */,
        '.spark-progress-fill {' +
        '  position: absolute; top: 0; left: 0; height: 100%;' +
        '  background: var(--primary-color, #1E293B); border-radius: 3px;' +
        '  width: var(--position, 0%); transition: width 400ms ease-out;' +
        '}'
    ].join('\n');

    /* --- Template --- */
    var tpl = document.createElement('template');
    tpl.innerHTML = '<style>' + PROGRESS_STYLES + '</style>' +
        '<div class="spark-progress-messages"><slot name="messages"></slot></div>' +
        '<div class="spark-progress-track">' +
        '  <div class="spark-progress-fill"></div>' +
        '  <slot name="steps"></slot>' +
        '</div>';

    class SparkProgressBarEl extends HTMLElement {

    static get observedAttributes() { return ['data-value']; }

    connectedCallback() {
        injectMsgStyles();
        var shadow = this.attachShadow({ mode: 'open' });
        shadow.appendChild(tpl.content.cloneNode(true));

        this._fill = shadow.querySelector('.spark-progress-fill');
        this._currencyCode = this.getAttribute('data-currency-code') || 'USD';
        this._prevShippingReached = null;
        this._prevGiftReached = null;

        // Message/step refs are lazily queried in _ensureRefs
        // because children may not be parsed yet in connectedCallback
        this._shippingMsg = null;
        this._giftMsg = null;
        this._finalMsg = null;
        this._steps = [];
        this._refsReady = false;

        // Initial update (deferred to allow children to parse)
        var self = this;
        requestAnimationFrame(function() {
            self._ensureRefs();
            self._update(self._getValue());
        });
    };

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === 'data-value' && this._fill) {
            this._update(parseFloat(newVal) || 0);
        }
    };

    _getValue() {
        return parseFloat(this.getAttribute('data-value')) || 0;
    };

    _getMin() {
        return parseFloat(this.getAttribute('data-min')) || 0;
    };

    _getMax() {
        return parseFloat(this.getAttribute('data-max')) || 100;
    };

    _ensureRefs() {
        if (this._refsReady) return;
        this._shippingMsg = this.querySelector('[data-shipping]');
        this._giftMsg = this.querySelector('[data-gift]');
        this._finalMsg = this.querySelector('[data-final-goal]');
        this._steps = this.querySelectorAll('[data-step]');
        if (this._shippingMsg || this._finalMsg) this._refsReady = true;
    };

    _update(currentValue) {
        this._ensureRefs();
        var min = this._getMin();
        var max = this._getMax();
        var range = max - min;
        var progress = range > 0 ? Math.max(0, Math.min(100, ((currentValue - min) / range) * 100)) : 0;

        // Update fill bar
        this.style.setProperty('--position', progress + '%');

        // Update step icons
        for (var i = 0; i < this._steps.length; i++) {
            var step = this._steps[i];
            var threshold = parseFloat(step.getAttribute('data-value')) || 0;
            step.setAttribute('aria-checked', currentValue >= threshold ? 'true' : 'false');
        }

        // Shipping threshold events
        if (this._shippingMsg) {
            var shipThreshold = parseFloat(this._shippingMsg.getAttribute('data-value')) || 0;
            var shipReached = currentValue >= shipThreshold;
            if (this._prevShippingReached !== shipReached) {
                var shipEvent = shipReached ? 'spark:progress:shipping-reached' : 'spark:progress:shipping-unreached';
                if (window.SparkEvents) {
                    SparkEvents.progress(shipEvent);
                } else {
                    document.dispatchEvent(new CustomEvent(shipEvent));
                }
                this._prevShippingReached = shipReached;
            }
        }

        // Gift threshold events
        if (this._giftMsg) {
            var giftThreshold = parseFloat(this._giftMsg.getAttribute('data-value')) || 0;
            var giftId = this._giftMsg.getAttribute('data-gift-id') || '';
            var giftReached = currentValue >= giftThreshold;
            if (this._prevGiftReached !== giftReached) {
                var giftEvent = giftReached ? 'spark:progress:gift-reached' : 'spark:progress:gift-unreached';
                if (window.SparkEvents) {
                    SparkEvents.progress(giftEvent, { giftId: giftId });
                } else {
                    document.dispatchEvent(new CustomEvent(giftEvent, { detail: { giftId: giftId } }));
                }
                this._prevGiftReached = giftReached;
            }
        }

        // Update messages
        this._updateMessages(currentValue);
    };

    _updateMessages(currentValue) {
        // Hide all
        var msgs = [this._shippingMsg, this._giftMsg, this._finalMsg];
        for (var i = 0; i < msgs.length; i++) {
            if (msgs[i]) msgs[i].classList.remove('active');
        }

        var shipThreshold = this._shippingMsg ? parseFloat(this._shippingMsg.getAttribute('data-value')) || 0 : 0;
        var giftThreshold = this._giftMsg ? parseFloat(this._giftMsg.getAttribute('data-value')) || 0 : 0;

        if (this._shippingMsg && currentValue < shipThreshold) {
            var remaining = shipThreshold - currentValue;
            this._setMessageText(this._shippingMsg, remaining);
            this._shippingMsg.classList.add('active');
        } else if (this._giftMsg && currentValue < giftThreshold) {
            var giftRemaining = giftThreshold - currentValue;
            this._setMessageText(this._giftMsg, giftRemaining);
            this._giftMsg.classList.add('active');
        } else if (this._finalMsg) {
            this._finalMsg.classList.add('active');
        }
    };

    _setMessageText(el, remaining) {
        var template = el.getAttribute('data-message-template') || '';
        var textEl = el.querySelector('.js-message-text');
        if (textEl && template) {
            var formatted = SparkCartClient.formatMoney(remaining, this._currencyCode);
            textEl.textContent = template.replace('{amount}', formatted);
        }
    }

    } /* end class SparkProgressBarEl */

    if (typeof customElements !== 'undefined' && !customElements.get('spark-progress-bar')) {
        customElements.define('spark-progress-bar', SparkProgressBarEl);
    }

})();
