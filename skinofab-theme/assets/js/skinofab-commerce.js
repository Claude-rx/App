

(function() {
    'use strict';

    var store = window.SFStore || {};
    var currency = store.currency || 'USD';
    var symbol = store.symbol || '$';
    var graphqlUrl = store.graphqlUrl || '/api/graphql/';

     

    function moneyText(amount) {
        var n = Number(amount);
        if (isNaN(n)) return '';
        var s = (Math.round(n * 100) % 100 === 0) ? String(Math.round(n)) : n.toFixed(2);
        return symbol + s + ' ' + currency;
    }
    function cents(amount) { var n = Number(amount); return isNaN(n) ? 0 : Math.round(n * 100); }

    function applyMoneyFormat() {
        var t = window.theme;
        if (!t) return;
        var open = String.fromCharCode(123, 123), close = String.fromCharCode(125, 125);
        t.moneyFormat = symbol + open + 'amount_no_decimals' + close;
        t.moneyWithCurrencyFormat = symbol + open + 'amount_no_decimals' + close + ' ' + currency;
        if (t.routes) {
            t.routes.cart_url = '/cart/';
            t.routes.root = '/';
        }
    }
    applyMoneyFormat();

     

    var clientPromise = null;
    function loadScript(src) {
        return new Promise(function(resolve, reject) {
            var s = document.createElement('script');
            s.src = src; s.async = false;
            s.onload = resolve; s.onerror = reject;
            document.head.appendChild(s);
        });
    }
    function client() {
        if (clientPromise) return clientPromise;
        clientPromise = (window.SparkCartClient ? Promise.resolve() :
            loadScript((window.SparkCartAssets || {}).cart)).then(function() {
            return new window.SparkCartClient(graphqlUrl);
        });
        return clientPromise;
    }
    function emit(name, detail) {
        document.dispatchEvent(new CustomEvent(name, { detail: detail || {}, bubbles: true }));
    }

    function toShopifyCart(cart) {
        cart = cart || {};
        var lines = cart.lines || [];
        return {
            token: cart.id || '',
            note: null,
            attributes: {},
            currency: cart.currency || currency,
            item_count: cart.numItems || 0,
            total_price: cents(cart.totalExclTax),
            original_total_price: cents(cart.totalExclTaxExclDiscounts || cart.totalExclTax),
            items_subtotal_price: cents(cart.totalExclTaxExclDiscounts || cart.totalExclTax),
            total_discount: cents(cart.totalDiscount),
            requires_shipping: true,
            cart_level_discount_applications: [],
            items: lines.map(function(line) {
                var p = line.product || {};
                var img = p.primaryImage && p.primaryImage.thumbnail;
                return {
                    id: p.pk, variant_id: p.pk, key: String(line.pk), quantity: line.quantity,
                    title: p.title, product_title: (p.parent && p.parent.title) || p.title,
                    price: cents(line.unitPriceExclTax), final_price: cents(line.unitPriceExclTax),
                    line_price: cents(line.linePriceExclTaxInclDiscounts || line.linePriceExclTax),
                    final_line_price: cents(line.linePriceExclTaxInclDiscounts || line.linePriceExclTax),
                    url: p.url, image: img || null, featured_image: img ? { url: img } : null,
                    properties: {}, product_id: (p.parent && p.parent.pk) || p.pk
                };
            })
        };
    }

    function currentCart() {
        return client().then(function(c) {
            var id = c.getCartId && c.getCartId();
            if (!id) return { lines: [], numItems: 0, totalExclTax: 0, currency: currency };
            return c.getCart(id);
        });
    }

     
    function nextPk(id) {
        var key = String(id);
        var handle = (window.SFVariantHandle || {})[key];
        var pk = handle && (window.SFHandlePk || {})[handle];
        return pk ? parseInt(pk, 10) : parseInt(key, 10);
    }

    

    function planFor(pk, chosen) {
        var has = function(cfg) { return cfg && cfg.pks && cfg.pks.indexOf(String(pk)) >= 0; };
        var cfg = has(window.SFSubscriptionOnly) ? window.SFSubscriptionOnly
                : (!chosen && has(window.SFDefaultPlan)) ? window.SFDefaultPlan : null;
        return cfg ? { subscriptionOption: 'subscribe', interval: cfg.interval, intervalCount: cfg.intervalCount } : null;
    }

    function addItems(items) {
        var last = null;
        return client().then(function(c) {
            var chain = Promise.resolve();
            items.forEach(function(item) {
                chain = chain.then(function() {
                    var pk = nextPk(item.id);
                    var plan = item.subscription || planFor(pk, item.subscription !== undefined);
                    return c.addToCart(pk, parseInt(item.quantity, 10) || 1, false, plan).then(function(result) {
                        if (!result || result.success === false) {
                            var err = new Error(((result && result.errors) || ['Unable to add to cart'])[0]);
                            err.status = 422; throw err;
                        }
                        last = result;
                        emit('spark:cart:added', { cart: result.cart, count: result.cart && result.cart.numItems,
                            action: 'add', productId: item.id, quantity: item.quantity, openSideCart: true });
                        return result;
                    });
                });
            });
            return chain.then(function() { return last; });
        });
    }

    function changeLine(key, quantity) {
        return client().then(function(c) {
            return currentCart().then(function(cart) {
                var lines = cart.lines || [];
                var line = lines.filter(function(l) {
                    return String(l.pk) === String(key) || String(l.product && l.product.pk) === String(key);
                })[0] || lines[parseInt(key, 10) - 1];
                if (!line) return cart;
                var op = quantity > 0 ? c.updateCartLines(cart.id, [{ lineId: line.pk, quantity: quantity }])
                                      : c.removeCartLines(cart.id, [line.pk]);
                return op.then(function(r) { return (r && r.cart) || cart; });
            });
        });
    }

     

    function readBody(init) {
        var body = init && init.body;
        var out = { items: [] };
        if (!body) return out;
        var get = function(k) { return null; };
        if (typeof FormData !== 'undefined' && body instanceof FormData) {
            get = function(k) { return body.get(k); };
        } else if (typeof body === 'string') {
            try {
                var json = JSON.parse(body);
                if (json.items) out.items = json.items;
                else if (json.id) out.items = [{ id: json.id, quantity: json.quantity || 1 }];
                out.updates = json.updates; out.line = json.line; out.quantity = json.quantity; out.id = json.id;
                return out;
            } catch (e) {
                var params = new URLSearchParams(body);
                get = function(k) { return params.get(k); };
            }
        } else if (body instanceof URLSearchParams) {
            get = function(k) { return body.get(k); };
        }
        if (get('id')) out.items = [{ id: get('id'), quantity: get('quantity') || 1 }];
        out.line = get('line'); out.quantity = get('quantity'); out.id = get('id');
        return out;
    }

    function jsonResponse(obj, status) {
        return new Response(JSON.stringify(obj), { status: status || 200, headers: { 'Content-Type': 'application/json' } });
    }
    function notFound() { return Promise.resolve(new Response('', { status: 404 })); }

     

    var nativeFetch = window.fetch && window.fetch.bind(window);
    window.fetch = function(input, init) {
        var url = typeof input === 'string' ? input : (input && input.url) || '';
        var path = url.replace(/^https?:\/\/[^\/]+/, '').split('#')[0];
        var bare = path.split('?')[0].replace(/\/+$/, '');

        if (/^\/api\//.test(bare)) return nativeFetch(input, init);

        if (/^\/cart\/add(\.js)?$/.test(bare)) {
            var req = readBody(init);
            return addItems(req.items).then(function(result) {
                var cart = toShopifyCart(result && result.cart);
                var added = req.items[0] || {};
                var item = cart.items.filter(function(i) { return String(i.id) === String(added.id); })[0] || cart.items[0] || {};
                return jsonResponse(req.items.length > 1 ? { items: cart.items } : item);
            }, function(err) {
                return jsonResponse({ status: 422, message: 'Cart Error', description: err.message }, 422);
            });
        }
        if (/^\/cart(\.js)?$/.test(bare) && !/[?&]sections?=|[?&]section_id=|[?&]view=/.test(path)) {
            return currentCart().then(function(cart) { return jsonResponse(toShopifyCart(cart)); });
        }
        if (/^\/cart\/(change|update)(\.js)?$/.test(bare)) {
            var body = readBody(init);
            var key, qty;
            if (body.updates && typeof body.updates === 'object') {
                key = Object.keys(body.updates)[0]; qty = parseInt(body.updates[key], 10);
            } else {
                key = body.id || body.line; qty = parseInt(body.quantity, 10);
            }
            return changeLine(key, isNaN(qty) ? 0 : qty).then(function(cart) {
                emit('spark:cart:updated', { cart: cart, count: cart.numItems, action: 'update' });
                return jsonResponse(toShopifyCart(cart));
            });
        }
        if (/^\/cart\/clear(\.js)?$/.test(bare)) {
            return client().then(function(c) {
                return currentCart().then(function(cart) {
                    var ids = (cart.lines || []).map(function(l) { return l.pk; });
                    return (ids.length ? c.removeCartLines(cart.id, ids) : Promise.resolve({ cart: cart })).then(function(r) {
                        return jsonResponse(toShopifyCart((r && r.cart) || cart));
                    });
                });
            });
        }
        var productJs = bare.match(/^\/products\/([a-z0-9][a-z0-9-]*)\.js$/);
        if (productJs) {
            var src = (window.SFProductJson || {})[productJs[1]];
            return src ? nativeFetch(src) : notFound();
        }
        if (/^\/recommendations/.test(bare)) {
             
            return Promise.resolve(new Response('<div data-related-products></div><div data-complementary-products></div>',
                { status: 200, headers: { 'Content-Type': 'text/html' } }));
        }
        if (/[?&]sections?=|[?&]section_id=/.test(path) || /^\/search\/suggest/.test(bare) ||
            /browsing_context_suggestions/.test(bare)) {
            return notFound();
        }
        return nativeFetch(input, init);
    };

     

    function isProductForm(form) {
        return form && form.tagName === 'FORM' && form.querySelector('input[name="id"]') &&
            (form.matches('[data-sf-product-form], .product__form, [data-product-form], [data-cart-form], [id^="AddToCartForm"], [action*="/cart/add"]'));
    }

     
    

    var pending = 0;
    function escText(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function(c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }
    function pendingHtml(form) {
        var scope = form.closest('.product-single__wrapper, .shopify-section--product, main') || document;
        var title = ((scope.querySelector('.product__title, h1') || {}).textContent || '').replace(/\s+/g, ' ').trim();
        var img = scope.querySelector('[data-product-single-media-wrapper] img, .product__media img');
        var src = img ? (img.currentSrc || img.src || '') : '';
        var pack = form.querySelector('input[name="sf_pack"]:checked');
        var name = pack && pack.closest('label') && pack.closest('label').querySelector('.sfo-name');
        var packName = name && name.firstChild ? String(name.firstChild.textContent || '').trim() : '';
        return '<div class="sf-pending" role="status" aria-live="polite">' +
            (src ? '<img src="' + escText(src) + '" alt="" width="64" height="64">' : '') +
            '<div><b>' + escText(title) + '</b>' + (packName ? '<small>' + escText(packName) + '</small>' : '') +
            '<span>Adding to your bag\u2026</span></div><i aria-hidden="true"></i></div>';
    }
    function openPending(form) {
        pending++;
        var html = pendingHtml(form);
        function show() {
            if (!pending) return;
            var d = document.querySelector('spark-cart-drawer');
            if (!d || !window.SparkSideCart) return;
            d.classList.add('sf-adding');
            if (!d._isOpen) {
                 
                var own = Object.prototype.hasOwnProperty.call(d, '_loadCart'), load = d._loadCart;
                d._loadCart = function() {};
                try { window.SparkSideCart.open(); } finally { if (own) d._loadCart = load; else delete d._loadCart; }
            }
            var body = d.shadowRoot && d.shadowRoot.querySelector('.spark-drawer-body');
            if (body && !body.querySelector('.sf-pending')) body.insertAdjacentHTML('afterbegin', html);
        }
        if (window.SparkSideCart) show();
        else if (window.SparkCartLoader && window.SparkCartLoader.ensureDrawer) window.SparkCartLoader.ensureDrawer().then(show, function() {});
    }
    function closePending(ok) {
        pending = Math.max(0, pending - 1);
        if (pending) return;
        var d = document.querySelector('spark-cart-drawer');
        if (!d) return;
        d.classList.remove('sf-adding');
        var p = d.shadowRoot && d.shadowRoot.querySelector('.sf-pending');
        if (p) p.parentNode.removeChild(p);
        if (!ok && !d._cart && window.SparkSideCart) window.SparkSideCart.close();
    }

    function addFromForm(form) {
        var idEl = form.querySelector('input[name="id"]:checked') || form.querySelector('[name="id"]');
        var qtyEl = form.querySelector('[name="quantity"]');
        var btn = form.querySelector('[type="submit"], [data-add-to-cart]');
        if (btn) btn.setAttribute('aria-busy', 'true');
        var shown = form.querySelector('.sf-atc-error');
        if (shown) shown.hidden = true;
        

        var plan = form.querySelector('input[name="sf_purchase"]:checked');
        var subscription = plan && plan.value === 'subscribe' ? { subscriptionOption: 'subscribe',
            interval: plan.getAttribute('data-interval'), intervalCount: plan.getAttribute('data-interval-count') }
            : form.querySelector('input[name="sf_purchase"]') ? null : undefined;
        openPending(form);
        addItems([{ id: idEl && idEl.value, quantity: qtyEl ? qtyEl.value : 1, subscription: subscription }]).then(function() {
            if (btn) btn.removeAttribute('aria-busy');
            closePending(true);
        }, function(err) {
            if (btn) btn.removeAttribute('aria-busy');
            closePending(false);
            

            var msg = 'Sorry, we could not add this to your bag. Please check your connection and try again.';
            var box = null;           
            if (btn) {
                box = form.querySelector('.sf-atc-error');
                if (!box) {
                    box = document.createElement('p');
                    box.className = 'sf-atc-error';
                    box.setAttribute('role', 'alert');
                    box.style.cssText = 'margin:10px 0 0;font-size:14px;line-height:1.4;color:#b42318';
                    btn.parentNode.insertBefore(box, btn.nextSibling);
                }
            }
            if (box) { box.textContent = msg; box.hidden = false; box.style.display = ''; }
            if (window.console) console.warn('[skinofab] add to cart failed', err);
        });
    }

    

    document.addEventListener('submit', function(e) {
        if (!isProductForm(e.target)) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        addFromForm(e.target);
    }, true);
    document.addEventListener('click', function(e) {
        var btn = e.target && e.target.closest && e.target.closest('[data-add-to-cart], button[name="add"], [type="submit"]');
        var form = btn && btn.closest('form');
        if (!btn || !isProductForm(form) || btn.disabled || btn.getAttribute('aria-disabled') === 'true') return;
        e.preventDefault();
        e.stopImmediatePropagation();
        addFromForm(form);
    }, true);

    document.addEventListener('click', function(e) {
        var t = e.target && e.target.closest && e.target.closest('[data-cart-drawer-toggle], a[href="#cart-modal"]');
        if (!t) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        emit('spark:cart:toggle');
    }, true);

    function paintCount(count) {
        var n = parseInt(count, 10) || 0;
        document.querySelectorAll('[data-cart-count], .cart__toggle [data-cart-items-count], #cart-badge').forEach(function(el) {
            el.textContent = n > 0 ? String(n) : '';
            el.style.display = n > 0 ? '' : 'none';
        });
        document.querySelectorAll('.cart__toggle').forEach(function(el) {
            el.classList.toggle('cart__toggle--has-items', n > 0);
        });
    }
    ['spark:cart:updated', 'spark:cart:added'].forEach(function(name) {
        document.addEventListener(name, function(e) {
            var d = e.detail || {};
            paintCount(d.count != null ? d.count : (d.cart && d.cart.numItems));
        });
    });

     

    function readJson(id) {
        var el = document.getElementById(id);
        if (!el) return null;
        try { return JSON.parse(el.textContent); } catch (e) { return null; }
    }

    function rekeyProductJson() {
        var next = readJson('product-data');
        var optionsDef = {};
        (readJson('sf-variant-options') || []).forEach(function(o) { if (o && o.code) optionsDef[o.code] = o; });
        var nodes = document.querySelectorAll('script[data-product-json]');
        if (!next || !nodes.length) return;
        var labels = {};  
        Object.keys(optionsDef).forEach(function(code) {
            labels[code] = {};
            (optionsDef[code].choices || []).forEach(function(c) { labels[code][String(c[0])] = String(c[1]); });
        });
        var children = (next.children && next.children.length) ? next.children : [next];
        function norm(s) { return String(s || '').trim().toLowerCase(); }
        function childLabels(child) {
            return (child.variant_attribute_values || []).map(function(a) {
                return norm((labels[a.code] || {})[String(a.id)] || a.value || a.name || a.id);
            });
        }
        nodes.forEach(function(node) {
            var data;
            try { data = JSON.parse(node.textContent); } catch (e) { return; }
            if (!data || !data.variants) return;
            data.variants.forEach(function(v, index) {
                var opts = (v.options || [v.option1, v.option2, v.option3]).filter(function(o) { return o != null; }).map(norm);
                var match = children.filter(function(child) {
                    var ls = childLabels(child);
                    return opts.every(function(o) { return ls.indexOf(o) !== -1; });
                })[0] || (children.length === data.variants.length ? children[index] : null) ||
                    (data.variants.length === 1 ? children[0] : null);
                if (!match) { v.available = false; return; }
                var info = match.purchase_info || {};
                var price = info.price || {}, retail = info.price_retail || {};
                v.id = match.id;
                if (price.price != null) v.price = cents(price.price);
                v.compare_at_price = (retail.price != null && Number(retail.price) > Number(price.price)) ? cents(retail.price) : null;
                v.available = info.availability ? (info.availability !== 'outofstock' && info.availability !== 'unavailable') : true;
            });
            if (data.variants[0]) {
                data.price = data.variants[0].price;
                data.compare_at_price = data.variants[0].compare_at_price;
            }
            node.textContent = JSON.stringify(data);
        });
        document.querySelectorAll('form input[name="id"][data-sf-next-default]').forEach(function(input) {
            input.value = input.getAttribute('data-sf-next-default');
        });
    }

    function onReady() {
        applyMoneyFormat();
        rekeyProductJson();
        client().then(function(c) {
            if (c.getCartId && c.getCartId()) {
                return currentCart().then(function(cart) { paintCount(cart.numItems); });
            }
            paintCount(0);
        }).catch(function() {});
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', onReady);
    else onReady();

     
    function addPermalink(spec) {
        var items = String(spec || '').replace(/^\/?cart\//, '').split('?')[0].split(',').map(function(pair) {
            var bits = pair.split(':');
            return { id: bits[0], quantity: parseInt(bits[1], 10) || 1 };
        }).filter(function(i) { return i.id; });
        return addItems(items).catch(function(err) { if (window.console) console.warn('[skinofab] permalink add failed', err); });
    }

    window.SFCommerce = { moneyText: moneyText, addItems: addItems, addPermalink: addPermalink, nextPk: nextPk, toShopifyCart: toShopifyCart };
})();
