/**
 * Spark Cart Drawer Renderer
 *
 * Markup helpers for <spark-cart-drawer>. The drawer owns state,
 * events, focus, and mutations; this Module owns generated cart markup.
 */

(function() {
    'use strict';

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function money(amount, currency) {
        var parsed = Number(amount);
        return SparkCartClient.formatMoney(isFinite(parsed) ? parsed : 0, currency);
    }

    function numberOrFallback(value, fallback) {
        if (value === null || typeof value === 'undefined' || value === '') return fallback;
        var parsed = Number(value);
        return isFinite(parsed) ? parsed : fallback;
    }

    function label(labels, key, fallback) {
        return labels && labels[key] ? labels[key] : fallback;
    }

    function formatTemplate(template, values) {
        return String(template || '').replace(/\{([a-zA-Z0-9_]+)\}/g, function(match, key) {
            return Object.prototype.hasOwnProperty.call(values, key) ? values[key] : match;
        });
    }

    function createCartItemEl(line, currency, doc, labels) {
        labels = labels || {};
        var item = doc.createElement('div');
        item.className = 'spark-drawer-item';
        item.setAttribute('data-line-id', line.pk);

        var product = line.product || {};
        var image = product.primaryImage ? product.primaryImage.thumbnail : '';
        var title = product.title || '';
        var url = product.url || '#';
        var attrs = line.properties || [];
        var variant = attrs.map(function(a) { return a.key + ': ' + a.value; }).join(', ');
        var linePrice = numberOrFallback(line.linePriceExclTax, 0);
        var discountedLinePrice = numberOrFallback(line.linePriceExclTaxInclDiscounts, linePrice);
        // A 100% line discount renders as $0.00 with the original line total struck through.
        var hasLineDiscount = linePrice > 0 && discountedLinePrice < linePrice;
        var price = money(discountedLinePrice, currency);
        var unitPrice = numberOrFallback(line.unitPriceExclTax, 0);
        var retailInfo = product.purchaseInfo ? product.purchaseInfo.priceRetail : null;
        var retailValue = retailInfo ? numberOrFallback(retailInfo.value, 0) : 0;
        // Line discounts compare against the pre-discount line total; retail compares unit price x quantity.
        var compareValue = hasLineDiscount ? linePrice : retailValue * line.quantity;
        var hasComparePrice = hasLineDiscount || (retailValue > 0 && retailValue > unitPrice);
        var isFreeGift = line.isUpsell;
        var subInfo = {
            interval: line.interval,
            intervalCount: line.intervalCount
        };
        var maxQty = SparkCartClient.MAX_QTY_PER_LINE || 15;

        var safeTitle = escapeHtml(title);
        var safeVariant = escapeHtml(variant);
        var safeUrl = escapeHtml(url);

        var frequencyText = '';
        if (subInfo && subInfo.interval) {
            frequencyText = formatTemplate(label(labels, 'frequencyTemplate', 'Every {count} {interval}'), {
                count: subInfo.intervalCount || '',
                interval: String(subInfo.interval || '').toLowerCase()
            });
        }

        var freeText = label(labels, 'freeText', 'Free');
        var removeLabel = formatTemplate(label(labels, 'removeItemLabel', 'Remove {title}'), {
            title: title
        });

        var html = '<div class="spark-drawer-item-image">' +
            (image ? '<img src="' + escapeHtml(image) + '" alt="' + safeTitle + '" width="80" height="80" loading="lazy" />' : '') +
            '</div>' +
            '<div class="spark-drawer-item-details">' +
            '<a href="' + safeUrl + '" class="spark-drawer-item-title">' + safeTitle + '</a>' +
            (safeVariant ? '<div class="spark-drawer-item-variant">' + safeVariant + '</div>' : '') +
            (frequencyText ? '<div class="spark-drawer-item-sub">' + escapeHtml(frequencyText) + '</div>' : '') +
            '<div class="spark-drawer-item-bottom">';

        if (isFreeGift) {
            html += '<span class="spark-drawer-item-free">' + escapeHtml(freeText) + '</span>';
        } else {
            html += '<div class="spark-drawer-item-qty">' +
                '<button class="spark-drawer-qty-btn" data-action="decrease" aria-label="' + escapeHtml(label(labels, 'decreaseQuantityLabel', 'Decrease quantity')) + '"' +
                (line.quantity <= 1 ? ' disabled' : '') +
                '>&minus;</button>' +
                '<span class="spark-drawer-qty-val" aria-label="' + escapeHtml(label(labels, 'quantityLabel', 'Quantity')) + '">' + line.quantity + '</span>' +
                '<button class="spark-drawer-qty-btn" data-action="increase" aria-label="' + escapeHtml(label(labels, 'increaseQuantityLabel', 'Increase quantity')) + '"' +
                (line.quantity >= maxQty ? ' disabled' : '') +
                '>+</button>' +
                '</div>';
        }

        html += '<div class="spark-drawer-item-price">' +
            (hasComparePrice ? '<span class="spark-drawer-item-compare">' + money(compareValue, currency) + '</span> ' : '') +
            '<span' + (isFreeGift ? ' class="spark-drawer-item-free"' : '') + '>' + (isFreeGift ? escapeHtml(freeText) : price) + '</span>' +
            '</div>' +
            '</div>';

        if (!isFreeGift) {
            html += '<button class="spark-drawer-item-remove" data-action="remove" aria-label="' + escapeHtml(removeLabel) + '">' +
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
                '</button>';
        }

        html += '</div>';
        item.innerHTML = html;
        return item;
    }

    function createItemsFragment(lines, currency, doc, labels) {
        var frag = doc.createDocumentFragment();
        for (var i = 0; i < lines.length; i++) {
            frag.appendChild(createCartItemEl(lines[i], currency, doc, labels));
        }
        return frag;
    }

    function voucherHtml(cart, currency, labels) {
        labels = labels || {};
        var html = '<div class="spark-drawer-voucher">';
        var offers = cart.offerDiscounts || [];
        for (var j = 0; j < offers.length; j++) {
            var offer = offers[j];
            var offerAmount = numberOrFallback(offer.amount, 0);
            if (offerAmount <= 0) continue;

            var offerName = escapeHtml(offer.name || offer.description || labels.discountText || 'Discount');
            html += '<div class="spark-drawer-voucher-applied">' +
                '<span class="spark-drawer-voucher-tag">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg> ' +
                offerName + ' (-' + money(offerAmount, currency) + ')' +
                '</span></div>';
        }
        var vouchers = cart.voucherDiscounts || [];
        for (var i = 0; i < vouchers.length; i++) {
            var vc = vouchers[i];
            var vcode = escapeHtml(vc.voucher ? vc.voucher.code : vc.name);
            var vid = escapeHtml(vc.voucher ? vc.voucher.code : '');
            html += '<div class="spark-drawer-voucher-applied">' +
                '<span class="spark-drawer-voucher-tag">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg> ' +
                vcode + ' (-' + money(vc.amount, currency) + ')' +
                '</span>' +
                '<button class="spark-drawer-voucher-remove" data-action="remove-voucher" data-voucher-id="' + vid + '" aria-label="' + escapeHtml(label(labels, 'removeVoucherLabel', 'Remove voucher')) + '">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
                '</button></div>';
        }
        html += '<div class="spark-drawer-voucher-form">' +
            '<input type="text" class="spark-drawer-voucher-input" placeholder="' + escapeHtml(labels.couponPlaceholder) + '" />' +
            '<button class="spark-drawer-voucher-btn" data-action="apply-voucher">' + escapeHtml(labels.couponBtn) + '</button>' +
            '</div>' +
            '<div class="spark-drawer-voucher-error" style="display:none;"></div>' +
            '</div>';
        return html;
    }

    function footerHtml(cart, currency, labels) {
        labels = labels || {};
        var totalDiscount = Number(cart.totalDiscount || 0);
        var subtotal = Number(cart.totalExclTaxExclDiscounts || cart.totalExclTax || 0);
        var total = Number(cart.totalExclTax || 0);

        var html = '<div class="spark-drawer-totals">' +
            '<div class="spark-drawer-total-row"><span>' + escapeHtml(labels.subtotalText) + '</span><span>' + money(subtotal, currency) + '</span></div>';

        if (totalDiscount > 0) {
            html += '<div class="spark-drawer-total-row discount"><span>' + escapeHtml(labels.discountText) + '</span><span>-' + money(totalDiscount, currency) + '</span></div>';
        }

        html += '<div class="spark-drawer-total-row"><span>' + escapeHtml(label(labels, 'shippingLabel', 'Shipping')) + '</span><span style="color:#94A3B8;font-size:12px;">' + escapeHtml(labels.shippingText) + '</span></div>' +
            '<div class="spark-drawer-total-row grand"><span>' + escapeHtml(label(labels, 'totalLabel', 'Total')) + '</span><span>' + money(total, currency) + '</span></div>' +
            '</div>' +
            '<a href="' + escapeHtml(labels.checkoutUrl) + '" class="spark-drawer-checkout">' + escapeHtml(labels.checkoutText) + '</a>' +
            '<button class="spark-drawer-continue" data-action="close">' + escapeHtml(labels.continueCta) + '</button>';
        return html;
    }

    function emptyHtml(labels) {
        labels = labels || {};
        return '<div class="spark-drawer-empty">' +
            '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">' +
            '<path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>' +
            '<line x1="3" y1="6" x2="21" y2="6"/>' +
            '<path d="M16 10a4 4 0 01-8 0"/>' +
            '</svg>' +
            '<div class="spark-drawer-empty-title">' + escapeHtml(labels.emptyTitle) + '</div>' +
            '<div class="spark-drawer-empty-sub">' + escapeHtml(labels.emptySub) + '</div>' +
            '<a href="' + escapeHtml(labels.continueUrl) + '" class="spark-drawer-empty-cta">' + escapeHtml(labels.continueCta) + '</a>' +
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
})();
