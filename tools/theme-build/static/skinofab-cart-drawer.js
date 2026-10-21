/**
 * SKINOFAB cart drawer
 *
 * Spark's <spark-cart-drawer> owns cart state, GraphQL mutations, focus, gifts and events. It renders its markup
 * through window.SparkCartDrawerRenderer; this module is that renderer (same API: escapeHtml, createCartItemEl,
 * createItemsFragment, voucherHtml, footerHtml, emptyHtml), loaded by spark-cart-loader in its place
 * (SparkCartAssets.cartRenderer). It also styles the drawer through its open shadow root.
 *
 * What changes for the shopper:
 *   - the drawer sits above the store's sticky header (its title and close button were hidden under it);
 *   - "Your bag (n)" header, a free-shipping note when the store ships for free;
 *   - lines show the base and the plan in words ("Monthly refill", not "Every 1 month") and the price per month;
 *   - a plan card under a subscription line: refill reminder, cancel any time, money-back guarantee;
 *   - the discount code folds away behind "Have a discount code?" (opens on its own when a code is applied);
 *   - the footer says what is due today and what renews, on a full-width secure checkout button;
 *   - an empty bag shows the bottle and a way straight back to it.
 * Text comes from Theme settings > SKINOFAB > Cart Drawer (window.SFCart). Plain ASCII only (the platform runs
 * every theme file through its template engine).
 */
(function() {
    'use strict';

    var cfg = window.SFCart || {};

    function escapeHtml(str) {
        if (str === null || typeof str === 'undefined') return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function money(amount, currency) {
        var n = Number(amount);
        return SparkCartClient.formatMoney(isFinite(n) ? n : 0, currency);
    }

    function num(value, fallback) {
        if (value === null || typeof value === 'undefined' || value === '') return fallback;
        var n = Number(value);
        return isFinite(n) ? n : fallback;
    }

    function label(labels, key, fallback) {
        return labels && labels[key] ? labels[key] : fallback;
    }

    function fill(template, values) {
        return String(template || '').replace(/\{([a-zA-Z0-9_]+)\}/g, function(m, key) {
            return Object.prototype.hasOwnProperty.call(values, key) ? values[key] : m;
        });
    }

    var ICON = {
        renew: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>',
        bell: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>',
        cancel: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.7 9.7 0 0 0-6.7 2.7L3 8"/><path d="M3 3v5h5"/><path d="m9.5 9.5 5 5m0-5-5 5"/></svg>',
        seal: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12 1.6l2.3 1.7 2.8-.3 1.1 2.6 2.6 1.1-.3 2.8 1.7 2.5-1.7 2.3.3 2.8-2.6 1.1-1.1 2.6-2.8-.3L12 22.4l-2.3-1.7-2.8.3-1.1-2.6-2.6-1.1.3-2.8L1.6 12l1.7-2.3-.3-2.8 2.6-1.1 1.1-2.6 2.8.3z"/><path d="M7.9 12.3l2.7 2.7 5.5-5.7" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        truck: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M1 4h14v12H1z"/><path d="M15 9h4l3 3v4h-7"/><circle cx="6" cy="18.5" r="1.8"/><circle cx="18" cy="18.5" r="1.8"/></svg>',
        lock: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
        tag: '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
        close: '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
    };

    /* "Every 1 month" -> "Monthly refill"; anything else keeps the plain cadence */
    function planName(line) {
        var count = parseInt(line.intervalCount, 10) || 1;
        var unit = String(line.interval || '').toLowerCase().replace(/s$/, '');
        var single = { day: 'Daily', week: 'Weekly', month: 'Monthly', year: 'Yearly' }[unit];
        if (count === 1 && single) return single + ' refill';
        return 'Refill every ' + count + ' ' + unit + (count === 1 ? '' : 's');
    }

    function perUnit(line) {
        var count = parseInt(line.intervalCount, 10) || 1;
        var unit = String(line.interval || '').toLowerCase().replace(/s$/, '');
        var abbr = { day: 'day', week: 'wk', month: 'mo', year: 'yr' }[unit] || unit;
        return count === 1 ? '/' + abbr : ' every ' + count + ' ' + unit + 's';
    }

    /* "Adaptive Peptide Foundation - Light-Medium": product name and base on separate lines */
    function splitTitle(product) {
        var title = product.title || '';
        var parent = product.parent && product.parent.title;
        if (parent && title.indexOf(parent) === 0 && title.length > parent.length) {
            return { name: parent, variant: title.slice(parent.length).replace(/^\s*[-\u2013\u2014:|]\s*/, '') };
        }
        var cut = title.lastIndexOf(' - ');
        return cut > 0 ? { name: title.slice(0, cut), variant: title.slice(cut + 3) } : { name: title, variant: '' };
    }

    function createCartItemEl(line, currency, doc, labels) {
        labels = labels || {};
        var item = doc.createElement('div');
        item.className = 'spark-drawer-item';
        item.setAttribute('data-line-id', line.pk);

        var product = line.product || {};
        var image = product.primaryImage ? product.primaryImage.thumbnail : '';
        var names = splitTitle(product);
        var props = (line.properties || []).map(function(a) { return a.key + ': ' + a.value; }).join(', ');
        var linePrice = num(line.linePriceExclTax, 0);
        var discounted = num(line.linePriceExclTaxInclDiscounts, linePrice);
        var hasLineDiscount = linePrice > 0 && discounted < linePrice;
        var unitPrice = num(line.unitPriceExclTax, 0);
        var retail = product.purchaseInfo && product.purchaseInfo.priceRetail ? num(product.purchaseInfo.priceRetail.value, 0) : 0;
        var compare = hasLineDiscount ? linePrice : retail * line.quantity;
        var hasCompare = hasLineDiscount || (retail > 0 && retail > unitPrice);
        var isGift = line.isUpsell;
        var isPlan = !!line.interval;
        var maxQty = SparkCartClient.MAX_QTY_PER_LINE || 15;
        var removeLabel = fill(label(labels, 'removeItemLabel', 'Remove {title}'), { title: product.title || '' });

        var html = '<a class="spark-drawer-item-image" href="' + escapeHtml(product.url || '#') + '" tabindex="-1" aria-hidden="true">' +
            (image ? '<img src="' + escapeHtml(image) + '" alt="" width="88" height="88" loading="lazy" />' : '') +
            '</a>' +
            '<div class="spark-drawer-item-details">' +
            '<a href="' + escapeHtml(product.url || '#') + '" class="spark-drawer-item-title">' + escapeHtml(names.name) + '</a>' +
            (names.variant ? '<div class="sf-item-variant">' + escapeHtml(names.variant) + (cfg.variantSuffix ? ' ' + escapeHtml(cfg.variantSuffix) : '') + '</div>' : '') +
            (props ? '<div class="sf-item-variant">' + escapeHtml(props) + '</div>' : '') +
            (isPlan ? '<div class="sf-plan-pill">' + ICON.renew + '<span>' + escapeHtml(planName(line)) + '</span></div>' : '') +
            '<div class="spark-drawer-item-bottom">';

        if (isGift) {
            html += '<span class="spark-drawer-item-free">' + escapeHtml(label(labels, 'freeText', 'Free')) + '</span>';
        } else {
            html += '<div class="spark-drawer-item-qty" role="group" aria-label="' + escapeHtml(label(labels, 'quantityLabel', 'Quantity')) + '">' +
                '<button type="button" class="spark-drawer-qty-btn" data-action="decrease" aria-label="' + escapeHtml(label(labels, 'decreaseQuantityLabel', 'Decrease quantity')) + '"' +
                (line.quantity <= 1 ? ' disabled' : '') + '>&minus;</button>' +
                '<span class="spark-drawer-qty-val" aria-live="polite">' + line.quantity + '</span>' +
                '<button type="button" class="spark-drawer-qty-btn" data-action="increase" aria-label="' + escapeHtml(label(labels, 'increaseQuantityLabel', 'Increase quantity')) + '"' +
                (line.quantity >= maxQty ? ' disabled' : '') + '>+</button>' +
                '</div>';
        }
        html += '<div class="spark-drawer-item-price">' +
            (hasCompare ? '<s class="spark-drawer-item-compare">' + money(compare, currency) + '</s> ' : '') +
            (isGift ? '<span class="spark-drawer-item-free">' + escapeHtml(label(labels, 'freeText', 'Free')) + '</span>'
                    : '<span>' + money(discounted, currency) + (isPlan ? '<small>' + escapeHtml(perUnit(line)) + '</small>' : '') + '</span>') +
            '</div></div>';
        if (!isGift) {
            html += '<button type="button" class="sf-item-remove" data-action="remove" aria-label="' + escapeHtml(removeLabel) + '">' +
                escapeHtml(cfg.removeText || 'Remove') + '</button>';
        }
        html += '</div>';
        item.innerHTML = html;
        return item;
    }

    function planCard() {
        var rows = [['bell', cfg.reminderTitle, cfg.reminderText], ['cancel', cfg.cancelTitle, cfg.cancelText], ['seal', cfg.guaranteeTitle, cfg.guaranteeText]];
        var html = '';
        rows.forEach(function(r) {
            if (!r[1]) return;
            html += '<li>' + ICON[r[0]] + '<span><strong>' + escapeHtml(r[1]) + '</strong>' + (r[2] ? ' ' + escapeHtml(r[2]) : '') + '</span></li>';
        });
        return html ? '<ul class="sf-plan-card">' + html + '</ul>' : '';
    }

    function createItemsFragment(lines, currency, doc, labels) {
        var frag = doc.createDocumentFragment();
        var hasPlan = false;
        for (var i = 0; i < lines.length; i++) {
            frag.appendChild(createCartItemEl(lines[i], currency, doc, labels));
            if (lines[i].interval) hasPlan = true;
        }
        if (hasPlan) {
            var wrap = doc.createElement('div');
            wrap.innerHTML = planCard();
            if (wrap.firstChild) frag.appendChild(wrap.firstChild);
        }
        return frag;
    }

    function voucherHtml(cart, currency, labels) {
        labels = labels || {};
        var applied = '';
        (cart.offerDiscounts || []).forEach(function(offer) {
            var amount = num(offer.amount, 0);
            if (amount <= 0) return;
            applied += '<div class="spark-drawer-voucher-applied"><span class="spark-drawer-voucher-tag">' + ICON.tag + ' ' +
                escapeHtml(offer.name || offer.description || labels.discountText || 'Discount') + ' (-' + money(amount, currency) + ')</span></div>';
        });
        (cart.voucherDiscounts || []).forEach(function(vc) {
            var code = vc.voucher ? vc.voucher.code : vc.name;
            applied += '<div class="spark-drawer-voucher-applied"><span class="spark-drawer-voucher-tag">' + ICON.tag + ' ' +
                escapeHtml(code) + ' (-' + money(vc.amount, currency) + ')</span>' +
                '<button type="button" class="spark-drawer-voucher-remove" data-action="remove-voucher" data-voucher-id="' + escapeHtml(vc.voucher ? vc.voucher.code : '') +
                '" aria-label="' + escapeHtml(label(labels, 'removeVoucherLabel', 'Remove voucher')) + '">' + ICON.close + '</button></div>';
        });
        return '<div class="spark-drawer-voucher">' + applied +
            '<details class="sf-voucher"' + (applied ? ' open' : '') + '><summary>' + escapeHtml(cfg.couponToggle || 'Have a discount code?') + '</summary>' +
            '<div class="spark-drawer-voucher-form">' +
            '<input type="text" class="spark-drawer-voucher-input" autocomplete="off" aria-label="' + escapeHtml(labels.couponPlaceholder) + '" placeholder="' + escapeHtml(labels.couponPlaceholder) + '" />' +
            '<button type="button" class="spark-drawer-voucher-btn" data-action="apply-voucher">' + escapeHtml(labels.couponBtn) + '</button>' +
            '</div><div class="spark-drawer-voucher-error" role="alert" style="display:none;"></div></details></div>';
    }

    function footerHtml(cart, currency, labels) {
        labels = labels || {};
        var discount = num(cart.totalDiscount, 0);
        var subtotal = num(cart.totalExclTaxExclDiscounts, num(cart.totalExclTax, 0));
        var total = num(cart.totalExclTax, 0);
        var plans = (cart.lines || []).filter(function(l) { return l.interval; });
        var renew = plans.reduce(function(sum, l) { return sum + num(l.linePriceExclTaxInclDiscounts, num(l.linePriceExclTax, 0)); }, 0);

        var html = '<div class="spark-drawer-totals">' +
            '<div class="spark-drawer-total-row"><span>' + escapeHtml(labels.subtotalText) + '</span><span>' + money(subtotal, currency) + '</span></div>';
        if (discount > 0) {
            html += '<div class="spark-drawer-total-row discount"><span>' + escapeHtml(labels.discountText) + '</span><span>-' + money(discount, currency) + '</span></div>';
        }
        html += '<div class="spark-drawer-total-row"><span>' + escapeHtml(label(labels, 'shippingLabel', 'Shipping')) + '</span>' +
            (cfg.shippingFree ? '<span class="sf-free">' + escapeHtml(label(labels, 'freeText', 'Free')) + '</span>'
                              : '<span class="sf-muted">' + escapeHtml(labels.shippingText) + '</span>') + '</div>' +
            '<div class="spark-drawer-total-row grand"><span>' + escapeHtml(plans.length ? (cfg.dueTodayText || 'Due today') : label(labels, 'totalLabel', 'Total')) +
            '</span><span>' + money(total, currency) + '</span></div>';
        if (plans.length && cfg.renewText) {
            html += '<p class="sf-renews">' + escapeHtml(fill(cfg.renewText, { amount: money(renew, currency) + perUnit(plans[0]) })) + '</p>';
        }
        html += '</div>' +
            '<a href="' + escapeHtml(labels.checkoutUrl) + '" class="spark-drawer-checkout">' + ICON.lock + '<span>' + escapeHtml(cfg.checkoutText || labels.checkoutText) + '</span></a>' +
            (cfg.secureText ? '<p class="sf-secure">' + escapeHtml(cfg.secureText) + '</p>' : '') +
            '<button type="button" class="spark-drawer-continue" data-action="close">' + escapeHtml(labels.continueCta) + '</button>';
        return html;
    }

    function emptyHtml(labels) {
        labels = labels || {};
        return '<div class="spark-drawer-empty">' +
            (cfg.emptyImage ? '<img class="sf-empty-img" src="' + escapeHtml(cfg.emptyImage) + '" alt="" width="114" height="320" />' : '') +
            '<div class="spark-drawer-empty-title">' + escapeHtml(cfg.emptyTitle || labels.emptyTitle) + '</div>' +
            '<div class="spark-drawer-empty-sub">' + escapeHtml(cfg.emptyText || labels.emptySub) + '</div>' +
            '<a href="' + escapeHtml(cfg.shopUrl || labels.continueUrl) + '" class="spark-drawer-empty-cta">' + escapeHtml(cfg.shopText || labels.continueCta) + '</a>' +
            '</div>';
    }

    window.SparkCartDrawerRenderer = {
        escapeHtml: escapeHtml,
        createCartItemEl: createCartItemEl,
        createItemsFragment: createItemsFragment,
        voucherHtml: voucherHtml,
        footerHtml: footerHtml,
        emptyHtml: emptyHtml
    };

    /* ---------- drawer chrome: styles in the shadow root, header count, shipping note ---------- */

    var STYLES = [
        /* above the store's sticky header and announcement bar */
        '.spark-drawer-backdrop { z-index: 2147483000; background: rgba(21,21,21,.45); }',
        '.spark-drawer-panel { z-index: 2147483001; max-width: 440px; color: #151515; box-shadow: -12px 0 40px rgba(0,0,0,.12); }',
        '@media (max-width: 767px) { .spark-drawer-panel { max-width: 100%; } }',
        '.spark-drawer-header { padding: 18px 22px; border-bottom: 1px solid #ececec; }',
        '.spark-drawer-header-title { font-size: 20px; font-weight: 600; letter-spacing: -.01em; }',
        '.sf-count { font-weight: 400; color: #6a6a6a; }',
        '.spark-drawer-close { color: #151515; margin-right: -8px; }',
        '.sf-ship-note { display: flex; align-items: center; justify-content: center; gap: 8px; margin: 0; padding: 10px 22px; background: #f4f2ee; font-size: 13px; letter-spacing: .02em; color: #151515; }',
        '.spark-drawer-body { padding: 6px 22px 16px; }',
        '.spark-drawer-item { gap: 14px; padding: 18px 0; border-bottom: 1px solid #ececec; }',
        '.spark-drawer-item-image { width: 88px; height: 88px; border-radius: 10px; background: #f4f2ee; overflow: hidden; display: block; }',
        '.spark-drawer-item-image img { width: 88px; height: 88px; border-radius: 0; object-fit: cover; display: block; }',
        '.spark-drawer-item-details { padding-right: 0; gap: 3px; }',
        '.spark-drawer-item-title { font-size: 15px; font-weight: 600; color: #151515; line-height: 1.3; }',
        '.sf-item-variant { font-size: 13px; color: #6a6a6a; }',
        '.sf-plan-pill { display: inline-flex; align-self: flex-start; align-items: center; gap: 6px; margin-top: 4px; padding: 4px 10px; border-radius: 999px; background: #151515; color: #fff; font-size: 12px; font-weight: 600; letter-spacing: .02em; }',
        '.spark-drawer-item-bottom { margin-top: 10px; }',
        '.spark-drawer-qty-btn { width: 34px; height: 34px; border-color: #d9d9d9; color: #151515; font-size: 16px; }',
        '.spark-drawer-qty-btn:first-child { border-radius: 8px 0 0 8px; }',
        '.spark-drawer-qty-btn:last-child { border-radius: 0 8px 8px 0; }',
        '.spark-drawer-qty-val { width: 38px; height: 34px; border-color: #d9d9d9; font-size: 14px; }',
        '.spark-drawer-item-price { font-size: 15px; font-weight: 600; }',
        '.spark-drawer-item-price small { font-size: 12px; font-weight: 400; color: #6a6a6a; margin-left: 1px; }',
        '.sf-item-remove { align-self: flex-start; margin-top: 8px; padding: 2px 0; background: none; border: 0; font: inherit; font-size: 12px; color: #6a6a6a; text-decoration: underline; text-underline-offset: 2px; cursor: pointer; }',
        '.sf-item-remove:hover { color: #151515; }',
        '.sf-item-remove:focus-visible { outline: 2px solid #151515; outline-offset: 2px; }',
        '.sf-plan-card { list-style: none; margin: 16px 0 4px; padding: 14px 16px; display: grid; gap: 10px; border-radius: 12px; background: #f4f2ee; }',
        '.sf-plan-card li { display: flex; gap: 10px; align-items: flex-start; font-size: 13px; line-height: 1.4; color: #3b3b3b; }',
        '.sf-plan-card svg { flex: none; color: #151515; margin-top: 1px; }',
        '.sf-plan-card strong { color: #151515; font-weight: 600; }',
        '.spark-drawer-voucher { border-top: 0; padding: 10px 0 0; }',
        '.sf-voucher summary { cursor: pointer; font-size: 13px; color: #151515; text-decoration: underline; text-underline-offset: 2px; list-style: none; padding: 6px 0; }',
        '.sf-voucher summary::-webkit-details-marker { display: none; }',
        '.sf-voucher[open] summary { margin-bottom: 8px; }',
        '.spark-drawer-voucher-input { border-radius: 8px; border-color: #d9d9d9; padding: 10px 12px; font-size: 14px; }',
        '.spark-drawer-voucher-btn { border-radius: 8px; border-color: #151515; color: #151515; }',
        '.spark-drawer-voucher-tag { color: #1f7a3f; }',
        '.spark-drawer-footer { padding: 16px 22px 18px; border-top: 1px solid #ececec; box-shadow: 0 -8px 24px rgba(0,0,0,.04); }',
        '.spark-drawer-totals { gap: 7px; margin-bottom: 14px; }',
        '.spark-drawer-total-row { font-size: 14px; color: #3b3b3b; }',
        '.spark-drawer-total-row.grand { font-size: 17px; color: #151515; padding-top: 7px; border-top: 1px solid #ececec; }',
        '.sf-free { color: #1f7a3f; font-weight: 600; }',
        '.sf-muted { color: #8a8a8a; font-size: 12px; }',
        '.sf-renews { margin: 0; font-size: 12px; color: #6a6a6a; text-align: right; }',
        '.spark-drawer-checkout { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 16px; border-radius: 10px; background: #151515; font-size: 16px; font-weight: 600; letter-spacing: .02em; }',
        '.spark-drawer-checkout:hover { opacity: 1; background: #000; }',
        '.sf-secure { margin: 10px 0 0; font-size: 12px; color: #6a6a6a; text-align: center; }',
        '.spark-drawer-continue { color: #151515; text-decoration: underline; text-underline-offset: 2px; }',
        '.spark-drawer-empty { padding: 36px 20px; gap: 6px; }',
        '.sf-empty-img { width: 76px; height: auto; margin-bottom: 14px; filter: drop-shadow(0 10px 14px rgba(0,0,0,.18)); }',
        '.spark-drawer-empty-title { font-size: 20px; font-weight: 600; color: #151515; }',
        '.spark-drawer-empty-sub { font-size: 14px; color: #6a6a6a; max-width: 280px; }',
        '.spark-drawer-empty-cta { margin-top: 18px; padding: 14px 26px; border-radius: 10px; background: #151515; font-size: 15px; font-weight: 600; }'
    ].join('\n');

    function decorate(drawer) {
        var root = drawer && drawer.shadowRoot;
        if (!root || root.querySelector('style[data-sf]')) return;
        var style = document.createElement('style');
        style.setAttribute('data-sf', '');
        style.textContent = STYLES;
        root.appendChild(style);
        var header = root.querySelector('.spark-drawer-header');
        if (cfg.shippingNote && header) {
            var note = document.createElement('p');
            note.className = 'sf-ship-note';
            note.innerHTML = ICON.truck + '<span>' + escapeHtml(cfg.shippingNote) + '</span>';
            header.parentNode.insertBefore(note, header.nextSibling);
        }
        var title = root.querySelector('.spark-drawer-header-title');
        var base = title ? title.textContent : '';
        function count() {
            var lines = (drawer._cart && drawer._cart.lines) || [];
            var n = lines.reduce(function(sum, l) { return sum + (parseInt(l.quantity, 10) || 0); }, 0);
            if (title) title.innerHTML = escapeHtml(base) + (n ? ' <span class="sf-count">(' + n + ')</span>' : '');
        }
        ['spark:cart:updated', 'spark:cart:added'].forEach(function(name) {
            document.addEventListener(name, function() { setTimeout(count, 0); });
        });
        /* the drawer re-renders its body after its own mutations without an event: follow the body */
        var body = root.querySelector('.spark-drawer-body');
        if (body && window.MutationObserver) new MutationObserver(count).observe(body, { childList: true });
        count();
    }

    if (window.customElements && customElements.whenDefined) {
        customElements.whenDefined('spark-cart-drawer').then(function() {
            decorate(document.querySelector('spark-cart-drawer'));
        });
    }
})();
