/**
 * SKINOFAB cart drawer
 *
 * Spark's <spark-cart-drawer> owns cart state, GraphQL mutations, focus, gifts and events. It renders its markup
 * through window.SparkCartDrawerRenderer; this module is that renderer (same API: escapeHtml, createCartItemEl,
 * createItemsFragment, voucherHtml, footerHtml, emptyHtml), loaded by spark-cart-loader in its place
 * (SparkCartAssets.cartRenderer). It also styles the drawer through its open shadow root.
 *
 * The drawer's job is the last step before payment: reassure, raise the order value, get to checkout.
 *   - the drawer sits above the store's sticky header (its title and close button were hidden under it);
 *   - "Your bag (n)" header and a free-shipping note when the store ships for free;
 *   - lines show the product, its pack (variant) and the price; a refill line says how often it ships, on its own line;
 *   - the upgrades: with the 1-bottle pack in the bag, one tap swaps it for 2 bottles + free gifts (same quantity,
 *     same refill choice), for the price difference the card names (Theme settings > Cart Drawer > Upgrade); a
 *     second one does the same for the brush (1 -> 2 brushes, Second upgrade); the first that applies is shown;
 *   - "Complete your routine": two add-ons not yet in the bag, out of three (Theme settings product pickers), one tap to add, loaded from the
 *     storefront API when the drawer first opens (no cost on page render), hidden once they are in the bag;
 *   - a trust card: the money-back guarantee and a customer review;
 *   - the discount code folds away behind "Have a discount code?" (opens on its own when a code is applied);
 *   - the footer: totals, a full-width secure checkout button, the cards the checkout accepts;
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
        seal: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M12 1.6l2.3 1.7 2.8-.3 1.1 2.6 2.6 1.1-.3 2.8 1.7 2.5-1.7 2.3.3 2.8-2.6 1.1-1.1 2.6-2.8-.3L12 22.4l-2.3-1.7-2.8.3-1.1-2.6-2.6-1.1.3-2.8L1.6 12l1.7-2.3-.3-2.8 2.6-1.1 1.1-2.6 2.8.3z"/><path d="M7.9 12.3l2.7 2.7 5.5-5.7" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        truck: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M1 4h14v12H1z"/><path d="M15 9h4l3 3v4h-7"/><circle cx="6" cy="18.5" r="1.8"/><circle cx="18" cy="18.5" r="1.8"/></svg>',
        lock: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
        shield: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
        star: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="currentColor" d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>',
        gift: '<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5"/></svg>',
        tag: '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
        close: '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
    };

    /* how often a refill line ships: "Refills every 28 days" (its own line, so the price row stays short on phones) */
    function cadence(line) {
        var count = parseInt(line.intervalCount, 10) || 1;
        var unit = String(line.interval || '').toLowerCase().replace(/s$/, '');
        return (cfg.refillText || 'Refills every') + ' ' + (count === 1 ? unit : count + ' ' + unit + 's');
    }

    /* "Adaptive Peptide Foundation - 1 bottle": product name and pack on separate lines */
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
        var maxQty = SparkCartClient.MAX_QTY_PER_LINE || 15;
        var removeLabel = fill(label(labels, 'removeItemLabel', 'Remove {title}'), { title: product.title || '' });

        var html = '<a class="spark-drawer-item-image" href="' + escapeHtml(product.url || '#') + '" tabindex="-1" aria-hidden="true">' +
            (image ? '<img src="' + escapeHtml(image) + '" alt="" width="88" height="88" loading="lazy" />' : '') +
            '</a>' +
            '<div class="spark-drawer-item-details">' +
            '<a href="' + escapeHtml(product.url || '#') + '" class="spark-drawer-item-title">' + escapeHtml(names.name) + '</a>' +
            (names.variant ? '<div class="sf-item-variant">' + escapeHtml(names.variant) + '</div>' : '') +
            (props ? '<div class="sf-item-variant">' + escapeHtml(props) + '</div>' : '') +
            (line.interval ? '<div class="sf-item-variant sf-item-every">' + escapeHtml(cadence(line)) + '</div>' : '') +
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
                    : '<span>' + money(discounted, currency) + '</span>') +
            '</div></div>';
        if (!isGift) {
            html += '<button type="button" class="sf-item-remove" data-action="remove" aria-label="' + escapeHtml(removeLabel) + '">' +
                escapeHtml(cfg.removeText || 'Remove') + '</button>';
        }
        html += '</div>';
        item.innerHTML = html;
        return item;
    }

    /* ---------- add-ons: storefront API, loaded once, rendered on every drawer render ---------- */

    var upsellData = null, upsellPromise = null, currentLines = [];

    function csrf() {
        var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : '';
    }

    function loadUpsells() {
        if (upsellPromise) return upsellPromise;
        var pks = (cfg.upsellPks || []).map(function(p) { return parseInt(p, 10); }).filter(function(p) { return p > 0; });
        if (!pks.length) { upsellData = []; return (upsellPromise = Promise.resolve([])); }
        var query = '{ products(pks: [' + pks.join(', ') + ']) { edges { node { pk title url structure ' +
            'primaryImage { thumbnail: url(transform: { maxWidth: 160, maxHeight: 160, format: webp, crop: center }) } ' +
            'purchaseInfo { price { value } priceRetail { value } availableForSale } ' +
            'children { pk purchaseInfo { availableForSale } } } } } }';
        upsellPromise = fetch((window.SFStore && window.SFStore.graphqlUrl) || '/api/graphql/', {
            method: 'POST', credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
            body: JSON.stringify({ query: query })
        }).then(function(r) { return r.json(); }).then(function(d) {
            var nodes = ((((d || {}).data || {}).products || {}).edges || []).map(function(e) { return e.node; });
            upsellData = pks.map(function(pk) { return nodes.filter(function(n) { return n.pk === pk; })[0]; })
                .filter(function(n) { return n && n.purchaseInfo && n.purchaseInfo.availableForSale; })
                .map(function(n) {
                    var child = (n.children || []).filter(function(c) { return c.purchaseInfo && c.purchaseInfo.availableForSale; })[0];
                    return {
                        pk: n.pk, addPk: child ? child.pk : n.pk, ids: [n.pk].concat((n.children || []).map(function(c) { return c.pk; })),
                        title: n.title, url: String(n.url || '').replace(/^https?:\/\/[^\/]+/, ''),
                        image: n.primaryImage ? n.primaryImage.thumbnail : '',
                        price: num(n.purchaseInfo.price && n.purchaseInfo.price.value, 0),
                        retail: num(n.purchaseInfo.priceRetail && n.purchaseInfo.priceRetail.value, 0)
                    };
                });
            return upsellData;
        }).catch(function() { upsellData = []; return []; });
        return upsellPromise;
    }

    function upsellHtml(currency) {
        if (!upsellData) return '';
        var inBag = {};
        currentLines.forEach(function(l) {
            var p = l.product || {};
            inBag[p.pk] = true;
            if (p.parent) inBag[p.parent.pk] = true;
        });
        var offers = upsellData.filter(function(u) { return !u.ids.some(function(id) { return inBag[id]; }); }).slice(0, 2);
        if (!offers.length) return '';
        return '<section class="sf-upsell" aria-label="' + escapeHtml(cfg.upsellTitle || 'Complete your routine') + '">' +
            '<h3 class="sf-upsell-title">' + escapeHtml(cfg.upsellTitle || 'Complete your routine') + '</h3>' +
            offers.map(function(u) {
                return '<div class="sf-upsell-item">' +
                    '<a class="sf-upsell-img" href="' + escapeHtml(u.url) + '" tabindex="-1" aria-hidden="true">' +
                    (u.image ? '<img src="' + escapeHtml(u.image) + '" alt="" width="64" height="64" loading="lazy" />' : '') + '</a>' +
                    '<div class="sf-upsell-info"><a class="sf-upsell-name" href="' + escapeHtml(u.url) + '">' + escapeHtml(u.title) + '</a>' +
                    '<span class="sf-upsell-price">' + (u.retail > u.price ? '<s>' + money(u.retail, currency) + '</s> ' : '') + money(u.price, currency) + '</span></div>' +
                    '<button type="button" class="sf-upsell-add" data-sf-add="' + u.addPk + '" aria-label="' + escapeHtml((cfg.upsellButton || 'Add') + ' ' + u.title) + '">' +
                    '+ ' + escapeHtml(cfg.upsellButton || 'Add') + '</button></div>';
            }).join('') + '</section>';
    }

    /* ---------- the upgrades: 1 bottle -> 2 bottles + free gifts, 1 brush -> 2 brushes ---------- */

    var ups = (cfg.upgrades || [cfg.upgrade]).filter(function(u) { return u && u.from && u.to && u.title; });

    /* the first upgrade whose smaller pack is in the bag (and its bigger pack is not), with that line */
    function upgradeFor() {
        var has = function(pk) { return currentLines.filter(function(l) { return String((l.product || {}).pk) === String(pk); })[0]; };
        for (var i = 0; i < ups.length; i++) {
            if (has(ups[i].to)) continue;
            var line = has(ups[i].from);
            if (line) return { up: ups[i], line: line };
        }
        return null;
    }

    function upgradeHtml() {
        var hit = upgradeFor();
        if (!hit) return '';
        var up = hit.up;
        return '<div class="sf-upgrade">' + ICON.gift +
            '<p><strong>' + escapeHtml(up.title) + '</strong>' + (up.text ? '<span>' + escapeHtml(up.text) + '</span>' : '') + '</p>' +
            '<button type="button" class="sf-upgrade-btn" data-sf-upgrade="' + escapeHtml(hit.line.pk) + '" data-sf-upgrade-to="' + escapeHtml(up.to) + '">' +
            escapeHtml(up.button || 'Upgrade') + '</button></div>';
    }

    /* the refill choice of a cart line, in the shape addToCart takes ("Every 28 days" stays every 28 days) */
    function planOf(line) {
        if (!line.interval) return null;
        return { subscriptionOption: 'subscribe', interval: String(line.interval).toLowerCase().replace(/s$/, ''),
                 intervalCount: String(parseInt(line.intervalCount, 10) || 1) };
    }

    function upgrade(btn) {
        var drawer = document.querySelector('spark-cart-drawer');
        var client = drawer && drawer._client, cart = drawer && drawer._cart;
        var line = cart && (cart.lines || []).filter(function(l) { return String(l.pk) === btn.getAttribute('data-sf-upgrade'); })[0];
        var up = ups.filter(function(u) { return String(u.to) === btn.getAttribute('data-sf-upgrade-to'); })[0];
        if (!client || !line || !up) return;
        btn.setAttribute('aria-busy', 'true');
        btn.textContent = cfg.upsellAdding || 'Adding...';
        var show = function(next) {
            if (next) document.dispatchEvent(new CustomEvent('spark:cart:updated', { detail: { cart: next, action: 'update' }, bubbles: true }));
        };
        /* add the 2-bottle pack first, then drop the 1-bottle line: a failure never leaves the bag empty */
        client.addToCart(Number(up.to), parseInt(line.quantity, 10) || 1, false, planOf(line)).then(function(added) {
            if (!added || added.success === false || !added.cart) throw new Error('add');
            return client.removeCartLines(added.cart.id, [line.pk]).then(function(removed) {
                show((removed && removed.cart) || added.cart);
            }, function() { show(added.cart); });
        }).catch(function() {
            btn.removeAttribute('aria-busy');
            btn.textContent = up.button || 'Upgrade';
            var err = document.createElement('span');
            err.className = 'sf-muted';
            err.setAttribute('role', 'alert');
            err.textContent = cfg.upsellError || 'Could not add it. Please try again.';
            btn.parentNode.appendChild(err);
        });
    }

    function trustHtml() {
        var html = '';
        if (cfg.guaranteeTitle) {
            html += '<div class="sf-trust-row">' + ICON.seal + '<p><strong>' + escapeHtml(cfg.guaranteeTitle) + '</strong>' +
                (cfg.guaranteeText ? '<span>' + escapeHtml(cfg.guaranteeText) + '</span>' : '') + '</p></div>';
        }
        if (cfg.reviewText) {
            html += '<figure class="sf-review"><div class="sf-stars" aria-label="5 out of 5 stars">' + ICON.star + ICON.star + ICON.star + ICON.star + ICON.star + '</div>' +
                '<blockquote>&ldquo;' + escapeHtml(cfg.reviewText) + '&rdquo;</blockquote>' +
                (cfg.reviewName ? '<figcaption>' + escapeHtml(cfg.reviewName) + '</figcaption>' : '') + '</figure>';
        }
        return html ? '<div class="sf-trust">' + html + '</div>' : '';
    }

    function createItemsFragment(lines, currency, doc, labels) {
        currentLines = lines || [];
        var frag = doc.createDocumentFragment();
        for (var i = 0; i < currentLines.length; i++) frag.appendChild(createCartItemEl(currentLines[i], currency, doc, labels));
        var wrap = doc.createElement('div');
        wrap.className = 'sf-extras';
        wrap.setAttribute('data-currency', currency || '');
        wrap.innerHTML = upgradeHtml() + '<div data-sf-upsell>' + upsellHtml(currency) + '</div>' + trustHtml();
        frag.appendChild(wrap);
        if (!upsellData) loadUpsells().then(paintUpsells);
        return frag;
    }

    /* fill the add-on slot of the rendered drawer once the data has arrived */
    function paintUpsells() {
        var drawer = document.querySelector('spark-cart-drawer');
        var slot = drawer && drawer.shadowRoot && drawer.shadowRoot.querySelector('[data-sf-upsell]');
        if (!slot) return;
        var wrap = slot.closest('.sf-extras');
        slot.innerHTML = upsellHtml(wrap ? wrap.getAttribute('data-currency') : '');
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

        var html = '<div class="spark-drawer-totals">' +
            '<div class="spark-drawer-total-row"><span>' + escapeHtml(labels.subtotalText) + '</span><span>' + money(subtotal, currency) + '</span></div>';
        if (discount > 0) {
            html += '<div class="spark-drawer-total-row discount"><span>' + escapeHtml(labels.discountText) + '</span><span>-' + money(discount, currency) + '</span></div>';
        }
        html += '<div class="spark-drawer-total-row"><span>' + escapeHtml(label(labels, 'shippingLabel', 'Shipping')) + '</span>' +
            (cfg.shippingFree ? '<span class="sf-free">' + escapeHtml(label(labels, 'freeText', 'Free')) + '</span>'
                              : '<span class="sf-muted">' + escapeHtml(labels.shippingText) + '</span>') + '</div>' +
            '<div class="spark-drawer-total-row grand"><span>' + escapeHtml(label(labels, 'totalLabel', 'Total')) + '</span><span>' + money(total, currency) + '</span></div>' +
            '</div>' +
            '<a href="' + escapeHtml(labels.checkoutUrl) + '" class="spark-drawer-checkout">' + ICON.lock + '<span>' + escapeHtml(cfg.checkoutText || labels.checkoutText) + '</span></a>';
        if ((cfg.payIcons || []).length) {
            html += '<ul class="sf-pay" aria-label="' + escapeHtml(cfg.payLabel || 'Accepted payment methods') + '">' +
                cfg.payIcons.map(function(p) { return '<li><img src="' + escapeHtml(p.src) + '" alt="' + escapeHtml(p.alt) + '" width="38" height="24" /></li>'; }).join('') + '</ul>';
        }
        if (cfg.secureText) html += '<p class="sf-secure">' + ICON.shield + '<span>' + escapeHtml(cfg.secureText) + '</span></p>';
        html += '<button type="button" class="spark-drawer-continue" data-action="close">' + escapeHtml(labels.continueCta) + '</button>';
        return html;
    }

    function emptyHtml(labels) {
        labels = labels || {};
        currentLines = [];
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

    /* ---------- drawer chrome: styles in the shadow root, header count, shipping note, add-on buttons ---------- */

    var STYLES = [
        /* above the store's sticky header and announcement bar */
        '.spark-drawer-backdrop { z-index: 2147483000; background: rgba(21,21,21,.45); }',
        '.spark-drawer-panel { z-index: 2147483001; max-width: 440px; color: #151515; box-shadow: -12px 0 40px rgba(0,0,0,.12); transition: transform 260ms cubic-bezier(.22,1,.36,1); }',
        /* the add in flight (skinofab-commerce.js): the drawer opens at the click with the product, the line fills in when
           the server answers; the totals wait for it */
        '.sf-pending { display: flex; align-items: center; gap: 14px; padding: 18px 0; border-bottom: 1px solid #ececec; animation: sf-in 180ms ease-out; }',
        '.sf-pending img { flex: none; width: 88px; height: 88px; border-radius: 10px; object-fit: cover; background: #f4f2ee; }',
        '.sf-pending div { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }',
        '.sf-pending b { font-size: 15px; font-weight: 600; color: #151515; line-height: 1.3; }',
        '.sf-pending small { font-size: 13px; color: #6a6a6a; }',
        '.sf-pending span { margin-top: 4px; font-size: 13px; color: #1f7a3f; }',
        '.sf-pending i { flex: none; width: 20px; height: 20px; border: 2px solid #e3dfd8; border-top-color: #151515; border-radius: 50%; animation: spark-drawer-spin 700ms linear infinite; }',
        ':host(.sf-adding) .spark-drawer-empty, :host(.sf-adding) .spark-drawer-loading { display: none; }',
        ':host(.sf-adding) .spark-drawer-footer { opacity: .5; pointer-events: none; }',
        '.spark-drawer-footer { transition: opacity 150ms; }',
        '@keyframes sf-in { from { opacity: 0; transform: translateY(6px); } }',
        /* buttons: lift on hover, press on tap, ring on keyboard focus */
        '.spark-drawer-checkout, .sf-upgrade-btn, .sf-upsell-add, .spark-drawer-empty-cta { transition: background-color 150ms, color 150ms, box-shadow 150ms, transform 120ms; -webkit-tap-highlight-color: transparent; }',
        '@media (hover: hover) { .spark-drawer-checkout:hover, .spark-drawer-empty-cta:hover, .sf-upgrade-btn:hover { box-shadow: 0 8px 20px rgba(0,0,0,.18); } }',
        '.spark-drawer-checkout:active, .sf-upgrade-btn:active, .sf-upsell-add:active, .spark-drawer-empty-cta:active { transform: scale(.98); box-shadow: none; }',
        '.spark-drawer-checkout:focus-visible, .spark-drawer-empty-cta:focus-visible { outline: 2px solid #151515; outline-offset: 3px; }',
        '@media (prefers-reduced-motion: reduce) { .spark-drawer-panel { transition: none; } .sf-pending { animation: none; } }',
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
        '.spark-drawer-item-bottom { margin-top: 10px; }',
        '.spark-drawer-qty-btn { width: 34px; height: 34px; border-color: #d9d9d9; color: #151515; font-size: 16px; }',
        '.spark-drawer-qty-btn:first-child { border-radius: 8px 0 0 8px; }',
        '.spark-drawer-qty-btn:last-child { border-radius: 0 8px 8px 0; }',
        '.spark-drawer-qty-val { width: 38px; height: 34px; border-color: #d9d9d9; font-size: 14px; }',
        '.spark-drawer-item-price { font-size: 15px; font-weight: 600; }',
        '.spark-drawer-item-price { white-space: nowrap; }',
        '.sf-item-every { display: flex; align-items: center; gap: 5px; }',
        '.sf-item-every:before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: #1f7a3f; }',
        '.sf-item-remove { align-self: flex-start; margin-top: 8px; padding: 2px 0; background: none; border: 0; font: inherit; font-size: 12px; color: #6a6a6a; text-decoration: underline; text-underline-offset: 2px; cursor: pointer; }',
        '.sf-item-remove:hover { color: #151515; }',
        '.sf-item-remove:focus-visible, .sf-upsell-add:focus-visible, .sf-upgrade-btn:focus-visible { outline: 2px solid #151515; outline-offset: 2px; }',
        /* upgrade */
        '.sf-upgrade { margin: 18px 0 0; display: flex; align-items: center; gap: 12px; padding: 14px; border: 2px dashed #151515; border-radius: 12px; background: #fff; }',
        '.sf-upgrade svg { flex: none; color: #151515; }',
        '.sf-upgrade p { flex: 1; min-width: 0; margin: 0; display: flex; flex-direction: column; gap: 2px; font-size: 13px; line-height: 1.4; color: #3b3b3b; }',
        '.sf-upgrade strong { font-size: 14px; font-weight: 600; color: #151515; }',
        '.sf-upgrade-btn { flex: none; padding: 10px 14px; border: 0; border-radius: 8px; background: #151515; color: #fff; font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; }',
        '.sf-upgrade-btn:hover { background: #000; }',
        '.sf-upgrade-btn[aria-busy="true"] { opacity: .6; pointer-events: none; }',
        /* add-ons */
        '.sf-upsell { margin: 18px 0 0; }',
        '.sf-upsell-title { margin: 0 0 10px; font-size: 13px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: #151515; }',
        '.sf-upsell-item { display: flex; align-items: center; gap: 12px; padding: 10px; border: 1px solid #ececec; border-radius: 12px; }',
        '.sf-upsell-item + .sf-upsell-item { margin-top: 8px; }',
        '.sf-upsell-img { flex: none; width: 56px; height: 56px; border-radius: 8px; overflow: hidden; background: #f4f2ee; display: block; }',
        '.sf-upsell-img img { width: 56px; height: 56px; object-fit: cover; display: block; }',
        '.sf-upsell-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }',
        '.sf-upsell-name { font-size: 14px; font-weight: 600; color: #151515; text-decoration: none; line-height: 1.3; }',
        '.sf-upsell-price { font-size: 13px; color: #3b3b3b; }',
        '.sf-upsell-price s { color: #8a8a8a; margin-right: 2px; }',
        '.sf-upsell-add { flex: none; padding: 9px 14px; border: 1px solid #151515; border-radius: 8px; background: #fff; color: #151515; font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; transition: background-color 150ms, color 150ms; }',
        '.sf-upsell-add:hover { background: #151515; color: #fff; }',
        '.sf-upsell-add[aria-busy="true"] { opacity: .6; pointer-events: none; }',
        /* trust */
        '.sf-trust { margin: 18px 0 4px; padding: 14px 16px; border-radius: 12px; background: #f4f2ee; display: grid; gap: 12px; }',
        '.sf-trust-row { display: flex; gap: 10px; align-items: flex-start; }',
        '.sf-trust-row svg { flex: none; color: #151515; }',
        '.sf-trust-row p { margin: 0; font-size: 13px; line-height: 1.4; color: #3b3b3b; display: flex; flex-direction: column; gap: 2px; }',
        '.sf-trust-row strong { color: #151515; font-size: 14px; font-weight: 600; }',
        '.sf-review { margin: 0; padding-top: 12px; border-top: 1px solid #e3dfd8; }',
        '.sf-stars { display: flex; gap: 2px; color: #151515; margin-bottom: 6px; }',
        '.sf-review blockquote { margin: 0; font-size: 13px; line-height: 1.45; color: #2b2b2b; font-style: italic; }',
        '.sf-review figcaption { margin-top: 6px; font-size: 12px; color: #6a6a6a; }',
        /* discount code */
        '.spark-drawer-voucher { border-top: 0; padding: 10px 0 0; }',
        '.sf-voucher summary { cursor: pointer; font-size: 13px; color: #151515; text-decoration: underline; text-underline-offset: 2px; list-style: none; padding: 6px 0; }',
        '.sf-voucher summary::-webkit-details-marker { display: none; }',
        '.sf-voucher[open] summary { margin-bottom: 8px; }',
        '.spark-drawer-voucher-input { border-radius: 8px; border-color: #d9d9d9; padding: 10px 12px; font-size: 14px; }',
        '.spark-drawer-voucher-btn { border-radius: 8px; border-color: #151515; color: #151515; }',
        '.spark-drawer-voucher-tag { color: #1f7a3f; }',
        /* footer */
        '.spark-drawer-footer { padding: 16px 22px 14px; border-top: 1px solid #ececec; box-shadow: 0 -8px 24px rgba(0,0,0,.04); }',
        '.spark-drawer-totals { gap: 7px; margin-bottom: 14px; }',
        '.spark-drawer-total-row { font-size: 14px; color: #3b3b3b; }',
        '.spark-drawer-total-row.grand { font-size: 17px; color: #151515; padding-top: 7px; border-top: 1px solid #ececec; }',
        '.sf-free { color: #1f7a3f; font-weight: 600; }',
        '.sf-muted { color: #8a8a8a; font-size: 12px; }',
        '.spark-drawer-checkout { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 16px; border-radius: 10px; background: #151515; font-size: 16px; font-weight: 600; letter-spacing: .02em; }',
        '.spark-drawer-checkout:hover { opacity: 1; background: #000; }',
        '.sf-pay { list-style: none; margin: 12px 0 0; padding: 0; display: flex; justify-content: center; gap: 6px; }',
        '.sf-pay img { display: block; width: 38px; height: 24px; }',
        '.sf-secure { margin: 8px 0 0; display: flex; align-items: center; justify-content: center; gap: 6px; font-size: 12px; color: #6a6a6a; }',
        '.spark-drawer-continue { margin-top: 6px; color: #151515; text-decoration: underline; text-underline-offset: 2px; }',
        /* empty bag */
        '.spark-drawer-empty { padding: 36px 20px; gap: 6px; }',
        '.sf-empty-img { width: 76px; height: auto; margin-bottom: 14px; filter: drop-shadow(0 10px 14px rgba(0,0,0,.18)); }',
        '.spark-drawer-empty-title { font-size: 20px; font-weight: 600; color: #151515; }',
        '.spark-drawer-empty-sub { font-size: 14px; color: #6a6a6a; max-width: 280px; }',
        '.spark-drawer-empty-cta { margin-top: 18px; padding: 14px 26px; border-radius: 10px; background: #151515; font-size: 15px; font-weight: 600; }'
    ].join('\n');

    function addUpsell(btn) {
        var pk = btn.getAttribute('data-sf-add');
        btn.setAttribute('aria-busy', 'true');
        btn.textContent = cfg.upsellAdding || 'Adding...';
        var done = function() { btn.removeAttribute('aria-busy'); };
        /* through the commerce adapter: same add path as the buy box, so the drawer re-renders with the new cart */
        var add = window.SFCommerce && window.SFCommerce.addItems
            ? window.SFCommerce.addItems([{ id: pk, quantity: 1 }])
            : Promise.reject(new Error('cart unavailable'));
        add.then(done, function() {
            done();
            btn.textContent = '+ ' + (cfg.upsellButton || 'Add');
            var err = document.createElement('span');
            err.className = 'sf-muted';
            err.setAttribute('role', 'alert');
            err.textContent = cfg.upsellError || 'Could not add it. Please try again.';
            btn.parentNode.appendChild(err);
        });
    }

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
        root.addEventListener('click', function(e) {
            var btn = e.target.closest && e.target.closest('[data-sf-add]');
            if (btn) { e.preventDefault(); addUpsell(btn); return; }
            var swap = e.target.closest && e.target.closest('[data-sf-upgrade]');
            if (swap && swap.getAttribute('aria-busy') !== 'true') { e.preventDefault(); upgrade(swap); }
        });
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
        loadUpsells().then(paintUpsells);
    }

    if (window.customElements && customElements.whenDefined) {
        customElements.whenDefined('spark-cart-drawer').then(function() {
            decorate(document.querySelector('spark-cart-drawer'));
        });
    }
})();
