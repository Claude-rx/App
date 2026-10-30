/**
 * <spark-subscription> Web Component
 *
 * Handles subscription options on product page:
 * - One-time purchase
 * - Subscribe with delivery frequency
 *
 * Features:
 * - Accepts intervals from backend via data-intervals
 * - Exposes .value and .intervalCount for spark-add-to-cart
 *
 * Attributes:
 *   data-intervals     JSON array of [value, text] pairs (required for subscribe)
 *   data-interval      Base interval type (e.g. "day", "month", "year")
 *
 * Public Properties:
 *   value              "one-time" or "subscribe"
 *   interval           "day" | "week" | "month" | "year"...
 *   intervalCount      Selected frequency number (e.g. 30, 60, 90)
 *
 * Events:
 *   change             Dispatched when user changes option or frequency
 *
 * Usage Example:
 *   <spark-subscription
 *       id="subscription-selector"
 *       data-interval="{{ product.get_interval }}"
 *       data-intervals='[
 *           ["30", "Every 30 days"],
 *           ["60", "Every 60 days"]
 *       ]'>
 *   </spark-subscription>
 */

(function() {
    'use strict';

    const TEMPLATE = document.createElement('template');
    TEMPLATE.innerHTML = `
        <style>
            :host {
                --spark-subscription-border: var(--border-color, #E2E8F0);
                --spark-subscription-surface-hover: var(--surface-muted, #F8FAFC);
                --spark-subscription-muted: var(--muted-color, #64748B);
                --spark-subscription-success: var(--success-color, #059669);
                display: block;
            }
            .subscription-options {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .option {
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 14px 16px;
                border: 1px solid var(--spark-subscription-border);
                border-radius: 8px;
                cursor: pointer;
                transition: all 150ms ease-out;
            }
            .option:hover {
                border-color: var(--primary-color, #1E293B);
                background: var(--spark-subscription-surface-hover);
            }
            .option input[type="radio"] {
                margin-top: 4px;
                accent-color: var(--primary-color, #1E293B);
            }
            .option-content { flex: 1; }
            .option-title { font-weight: 500; }
            .option-subtitle { font-size: 0.875rem; color: var(--spark-subscription-muted); margin-top: 2px; }
            .option-subtitle-success { color: var(--spark-subscription-success); }
            .frequency-wrapper { margin-top: 16px; }
            .frequency {
                margin-top: 12px;
                padding: 10px 12px;
                border: 1px solid var(--spark-subscription-border);
                border-radius: 6px;
                width: 100%;
                font-size: 0.9rem;
            }
            .hidden { display: none; }
        </style>

        <div class="subscription-options">
            <label class="option">
                <input type="radio" name="subscription_option" value="one-time" checked>
                <div class="option-content">
                    <div class="option-title" data-label="one-time-title">One-time purchase</div>
                    <div class="option-subtitle" data-label="one-time-subtitle">Buy once, no commitment</div>
                </div>
            </label>

            <label class="option">
                <input type="radio" name="subscription_option" value="subscribe" aria-controls="frequency-wrapper">
                <div class="option-content">
                    <div class="option-title" data-label="subscribe-title">Subscribe & Save</div>
                    <div class="option-subtitle option-subtitle-success" data-label="subscribe-subtitle">Recurring delivery</div>
                    
                    <div id="frequency-wrapper" class="frequency-wrapper hidden">
                        <select id="interval-select" name="interval_count" class="frequency" aria-label="Delivery frequency"></select>
                    </div>
                </div>
            </label>
        </div>
    `;

    class SparkSubscription extends HTMLElement {
        constructor() {
            super();
            this.attachShadow({ mode: 'open' });
            this.shadowRoot.appendChild(TEMPLATE.content.cloneNode(true));
        }

        connectedCallback() {
            this._oneTime = this.shadowRoot.querySelector('input[value="one-time"]');
            this._subscribe = this.shadowRoot.querySelector('input[value="subscribe"]');
            this._wrapper = this.shadowRoot.getElementById('frequency-wrapper');
            this._select = this.shadowRoot.getElementById('interval-select');

            this._applyLabels();
            this._bindEvents();
            this._loadIntervals();
        }

        _label(name, fallback) {
            return this.getAttribute('data-' + name) || fallback;
        }

        _applyLabels() {
            const labels = {
                'one-time-title': this._label('one-time-title', 'One-time purchase'),
                'one-time-subtitle': this._label('one-time-subtitle', 'Buy once, no commitment'),
                'subscribe-title': this._label('subscribe-title', 'Subscribe & Save'),
                'subscribe-subtitle': this._label('subscribe-subtitle', 'Recurring delivery')
            };

            Object.keys(labels).forEach((name) => {
                const el = this.shadowRoot.querySelector('[data-label="' + name + '"]');
                if (el) el.textContent = labels[name];
            });

            if (this._select) {
                this._select.setAttribute('aria-label', this._label('frequency-label', 'Delivery frequency'));
            }
        }

        _bindEvents() {
            const update = () => this.dispatchEvent(new Event('change', { bubbles: true, composed: true }));

            this._subscribe.addEventListener('change', () => {
                this._wrapper.classList.remove('hidden');
                update();
            });

            this._oneTime.addEventListener('change', () => {
                this._wrapper.classList.add('hidden');
                update();
            });

            this._select.addEventListener('change', update);
        }

        _loadIntervals() {
            const data = this.getAttribute('data-intervals');
            if (!data) return;

            try {
                const intervals = JSON.parse(data);
                if (!Array.isArray(intervals)) {
                    console.error('Subscription intervals must be an array');
                    return;
                }

                this._select.innerHTML = '';
                intervals.forEach((entry) => {
                    if (!Array.isArray(entry) || entry.length < 2 || entry[0] === null || entry[0] === undefined) {
                        return;
                    }
                    const value = entry[0];
                    const text = entry[1] === null || entry[1] === undefined ? String(value) : entry[1];
                    const opt = document.createElement('option');
                    opt.value = value;
                    opt.textContent = text;
                    this._select.appendChild(opt);
                });
            } catch (e) {
                console.error('Failed to parse intervals', e);
            }
        }

        get value() {
            const checked = this.shadowRoot.querySelector('input[name="subscription_option"]:checked');
            return checked ? checked.value : 'one-time';
        }

        get interval() {
            return this.getAttribute('data-interval') || 'day';
        }

        get intervalCount() {
            return this._select ? this._select.value : null;
        }
    }

    if (!customElements.get('spark-subscription')) {
        customElements.define('spark-subscription', SparkSubscription);
    }
})();
