/**
 * Spark Membership Pricing
 *
 * Presents member pricing from logged-in customer metadata. This is display
 * logic only; checkout enforcement must come from platform pricing rules.
 */

(function() {
    'use strict';

    var config = window.SparkMembershipPricingConfig || {};
    if (!config.enabled) return;

    var QUERY_ME = 'query SparkMembershipPricingMe { me { id pk metadata } }';
    var CSRF_COOKIE = 'csrftoken';
    var SURFACE_SELECTOR = '[data-spark-membership-price]';
    var OBSERVER_DEBOUNCE_MS = 100;
    var ERROR_RETRY_DELAY_MS = 30000;
    var state = {
        status: 'idle',
        active: false,
        user: null
    };
    var observer = null;
    var observerScheduled = false;
    var pendingSurfaces = [];
    var lastRefreshAttemptAt = 0;

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : null;
    }

    function normalize(value) {
        if (value === null || typeof value === 'undefined') return '';
        return String(value).trim().toLowerCase();
    }

    function numberFromConfig(value, fallback) {
        if (value === null || typeof value === 'undefined' || value === '') return fallback;
        var parsed = Number(value);
        return isFinite(parsed) ? parsed : fallback;
    }

    function parseAmount(value) {
        if (typeof value === 'number') return value;
        if (value === null || typeof value === 'undefined') return NaN;

        var cleaned = String(value).trim().replace(/\s/g, '').replace(/[^0-9,.-]/g, '');
        if (!cleaned) return NaN;
        if (/^-?\d+$/.test(cleaned)) return Number(cleaned);

        var lastComma = cleaned.lastIndexOf(',');
        var lastDot = cleaned.lastIndexOf('.');
        if (lastComma !== -1 && lastDot !== -1) {
            var decimalSeparator = lastComma > lastDot ? ',' : '.';
            var thousandsSeparator = decimalSeparator === ',' ? '.' : ',';
            cleaned = cleaned.split(thousandsSeparator).join('').replace(decimalSeparator, '.');
            return Number(cleaned);
        }

        if (lastComma !== -1) return Number(normalizeSingleSeparatorAmount(cleaned, ','));
        if (/^-?\d+\.\d{1,2}$/.test(cleaned)) return Number(cleaned);
        if (lastDot !== -1) return Number(normalizeSingleSeparatorAmount(cleaned, '.'));
        return Number(cleaned);
    }

    function normalizeSingleSeparatorAmount(value, separator) {
        var parts = value.split(separator);
        if (parts.length === 2) {
            if (parts[1].length === 3 && parts[0].length <= 3) return parts[0] + parts[1];
            if (parts[1].length <= 2) return parts[0] + '.' + parts[1];
            return NaN;
        }
        if (parts.length > 2) {
            var allThousandsGroups = true;
            for (var i = 1; i < parts.length; i++) {
                if (parts[i].length !== 3) {
                    allThousandsGroups = false;
                    break;
                }
            }
            if (allThousandsGroups) return parts.join('');

            var decimalPart = parts.pop();
            return parts.join('') + '.' + decimalPart;
        }
        return value;
    }

    function formatMoney(amount, currency) {
        currency = currency || 'USD';
        try {
            return new Intl.NumberFormat(getDisplayLocale(), {
                style: 'currency',
                currency: currency
            }).format(amount);
        } catch (e) {
            return currency + ' ' + Number(amount).toFixed(2);
        }
    }

    function getDisplayLocale() {
        if (config.locale) return config.locale;
        if (document.documentElement && document.documentElement.getAttribute('lang')) {
            return document.documentElement.getAttribute('lang');
        }
        if (window.navigator && window.navigator.language) return window.navigator.language;
        return 'en-US';
    }

    function requestMe() {
        var headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        var csrf = getCookie(CSRF_COOKIE);
        if (csrf) headers['X-CSRFToken'] = csrf;

        return fetch(config.graphqlUrl || '/api/graphql/', {
            method: 'POST',
            headers: headers,
            credentials: 'same-origin',
            body: JSON.stringify({ query: QUERY_ME, variables: {} })
        }).then(function(response) {
            if (!response.ok) {
                throw new Error('Membership GraphQL request failed: ' + response.status);
            }
            return response.json();
        }).then(function(json) {
            if (json.errors && json.errors.length) {
                throw new Error(json.errors[0].message || 'GraphQL error');
            }
            return json.data || {};
        });
    }

    function metadataMatches(metadata) {
        metadata = metadata || {};
        var key = config.statusMetadataKey || 'member_status';
        var activeValue = normalize(config.activeStatusValue || 'active');
        var value = metadata[key];

        if (Array.isArray(value)) {
            return value.map(normalize).indexOf(activeValue) !== -1;
        }
        return normalize(value) === activeValue;
    }

    function setDocumentState(nextState) {
        document.documentElement.setAttribute('data-spark-membership-state', nextState.status);
        document.documentElement.classList.toggle('spark-member-active', !!nextState.active);
    }

    function dispatchState() {
        var detail = {
            status: state.status,
            active: state.active,
            user: state.user
        };
        if (window.SparkEvents) {
            SparkEvents.dispatch('spark:membership:updated', detail);
            return;
        }
        document.dispatchEvent(new CustomEvent('spark:membership:updated', {
            detail: detail,
            bubbles: true
        }));
    }

    function findMemberBlock(surface) {
        var children = surface.children || [];
        for (var i = 0; i < children.length; i++) {
            if (children[i].classList && children[i].classList.contains('spark-member-price')) {
                return children[i];
            }
        }
        return null;
    }

    function ensureMemberBlock(surface) {
        var block = findMemberBlock(surface);
        if (block) return block;

        block = document.createElement('span');
        block.className = 'spark-member-price';

        var label = document.createElement('span');
        label.className = 'spark-member-price-label';
        block.appendChild(label);

        var value = document.createElement('span');
        value.className = 'spark-member-price-value';
        block.appendChild(value);

        var detail = document.createElement('span');
        detail.className = 'spark-member-price-detail';
        block.appendChild(detail);

        surface.appendChild(block);
        return block;
    }

    function removeMemberBlock(surface) {
        var block = findMemberBlock(surface);
        if (block) block.remove();
        surface.removeAttribute('data-membership-active');
    }

    function renderSurface(surface) {
        if (!state.active) {
            removeMemberBlock(surface);
            return;
        }

        var basePrice = parseAmount(surface.getAttribute('data-base-price'));
        if (!isFinite(basePrice)) {
            removeMemberBlock(surface);
            return;
        }

        var discountPercent = Math.min(100, Math.max(0, numberFromConfig(config.discountPercent, 25)));
        var memberPrice = basePrice * (1 - discountPercent / 100);
        var currency = surface.getAttribute('data-currency') || 'USD';
        var layout = surface.getAttribute('data-spark-membership-layout') || '';
        var block = ensureMemberBlock(surface);
        var label = block.querySelector('.spark-member-price-label');
        var value = block.querySelector('.spark-member-price-value');
        var detail = block.querySelector('.spark-member-price-detail');

        surface.setAttribute('data-membership-active', 'true');
        label.textContent = config.label || 'Member price';
        value.textContent = formatMoney(memberPrice, currency);

        if (detail) {
            if (layout === 'pdp' || layout === 'featured') {
                detail.textContent = config.detailText || '';
                detail.hidden = !detail.textContent;
            } else {
                detail.textContent = '';
                detail.hidden = true;
            }
        }
    }

    function renderAll() {
        var surfaces = document.querySelectorAll(SURFACE_SELECTOR);
        for (var i = 0; i < surfaces.length; i++) {
            renderSurface(surfaces[i]);
        }
    }

    function hasSurfaces() {
        return !!document.querySelector(SURFACE_SELECTOR);
    }

    function collectSurfaces(node, surfaces) {
        if (!node || node.nodeType !== 1) return;
        if (node.matches && node.matches(SURFACE_SELECTOR)) surfaces.push(node);

        if (!node.querySelectorAll) return;
        var nested = node.querySelectorAll(SURFACE_SELECTOR);
        for (var i = 0; i < nested.length; i++) {
            surfaces.push(nested[i]);
        }
    }

    function renderAddedSurfaces(surfaces) {
        if (!surfaces.length) return;
        if (state.status === 'idle' || shouldRetryAfterError()) {
            refresh();
            return;
        }
        if (state.status === 'checking' || state.status === 'error') return;

        for (var i = 0; i < surfaces.length; i++) {
            renderSurface(surfaces[i]);
        }
    }

    function currentTime() {
        return Date.now ? Date.now() : new Date().getTime();
    }

    function shouldRetryAfterError() {
        return state.status === 'error' && currentTime() - lastRefreshAttemptAt >= ERROR_RETRY_DELAY_MS;
    }

    function flushPendingSurfaces() {
        var surfaces = pendingSurfaces;
        pendingSurfaces = [];
        observerScheduled = false;
        renderAddedSurfaces(surfaces);
    }

    function scheduleAddedSurfaces(surfaces) {
        if (!surfaces.length) return;
        for (var i = 0; i < surfaces.length; i++) {
            pendingSurfaces.push(surfaces[i]);
        }
        if (observerScheduled) return;

        observerScheduled = true;
        setTimeout(flushPendingSurfaces, OBSERVER_DEBOUNCE_MS);
    }

    function startObserver() {
        if (observer || !window.MutationObserver || !document.body) return;

        observer = new MutationObserver(function(records) {
            var surfaces = [];
            for (var i = 0; i < records.length; i++) {
                var added = records[i].addedNodes || [];
                for (var j = 0; j < added.length; j++) {
                    collectSurfaces(added[j], surfaces);
                }
            }
            scheduleAddedSurfaces(surfaces);
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    function readPriceObject(price) {
        if (!price) return null;
        return {
            amount: price.price || price.value,
            currency: price.currency,
            format: price.format
        };
    }

    function handleVariantChanged(event) {
        var variant = event && event.detail ? event.detail.variant : null;
        if (!variant || !variant.purchase_info) return;

        var price = readPriceObject(variant.purchase_info.price);
        if (!price || typeof price.amount === 'undefined') return;

        var surfaces = document.querySelectorAll('[data-spark-membership-variant-price]');
        for (var i = 0; i < surfaces.length; i++) {
            var surface = surfaces[i];
            surface.setAttribute('data-base-price', price.amount);
            if (price.currency) surface.setAttribute('data-currency', price.currency);

            var publicPrice = surface.querySelector('[data-spark-public-price]');
            if (publicPrice && price.format && !publicPrice.hasAttribute('data-price')) {
                publicPrice.textContent = price.format;
            }
            renderSurface(surface);
        }
    }

    function refresh() {
        if (!hasSurfaces()) {
            state = {
                status: 'idle',
                active: false,
                user: null
            };
            setDocumentState(state);
            dispatchState();
            return Promise.resolve(state);
        }

        state = {
            status: 'checking',
            active: false,
            user: null
        };
        setDocumentState(state);

        return Promise.resolve().then(requestMe).then(function(data) {
            lastRefreshAttemptAt = currentTime();
            var user = data.me || null;
            state.user = user;
            state.active = !!(user && metadataMatches(user.metadata));
            state.status = user ? (state.active ? 'active' : 'inactive') : 'anonymous';
            setDocumentState(state);
            renderAll();
            dispatchState();
            return state;
        }).catch(function() {
            lastRefreshAttemptAt = currentTime();
            state = {
                status: 'error',
                active: false,
                user: null
            };
            setDocumentState(state);
            renderAll();
            dispatchState();
            return state;
        });
    }

    document.addEventListener('spark:variant:changed', handleVariantChanged);

    window.SparkMembershipPricing = {
        refresh: refresh,
        render: renderAll,
        isActive: function() {
            return !!state.active;
        }
    };

    function init() {
        startObserver();
        refresh();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
