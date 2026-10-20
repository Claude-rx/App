/** Accessible preview-session indicator. Ordinary storefront visits are untouched. */
(function(root) {
    'use strict';

    function readPreviewTheme(cookie) {
        var match = String(cookie || '').match(/(?:^|;\s*)preview_theme=([^;]+)/);
        if (!match) return null;
        try {
            var value = decodeURIComponent(match[1]);
            return /^[A-Za-z0-9_-]+$/.test(value) ? value : null;
        } catch (error) {
            return null;
        }
    }

    function buildExitPreviewUrl(location) {
        var pathname = String(location && location.pathname || '/');
        var search = String(location && location.search || '').replace(/^\?/, '');
        var hash = String(location && location.hash || '');
        var params = new root.URLSearchParams(search);

        params.delete('preview_theme');
        params.set('deactivate-theme', 'true');

        var query = params.toString();
        return pathname + (query ? '?' + query : '') + hash;
    }

    function createPreviewIndicator(doc, themeId, location) {
        var existing = doc.getElementById('spark-preview-indicator');
        if (existing) return existing;

        var indicator = doc.createElement('aside');
        indicator.id = 'spark-preview-indicator';
        indicator.className = 'spark-preview-indicator';
        indicator.setAttribute('role', 'status');
        indicator.setAttribute('aria-live', 'polite');
        indicator.setAttribute('aria-label', 'Theme preview session');

        var message = doc.createElement('span');
        message.className = 'spark-preview-indicator__message';
        message.textContent = 'Previewing theme ' + themeId;

        var exitLink = doc.createElement('a');
        exitLink.className = 'spark-preview-indicator__exit';
        exitLink.href = buildExitPreviewUrl(location);
        exitLink.textContent = 'Exit preview';

        indicator.appendChild(message);
        indicator.appendChild(exitLink);
        doc.body.appendChild(indicator);
        return indicator;
    }

    function initPreviewIndicator(doc, location) {
        if (!doc || !doc.body) return null;
        var themeId = readPreviewTheme(doc.cookie);
        return themeId ? createPreviewIndicator(doc, themeId, location) : null;
    }

    var api = {
        readPreviewTheme: readPreviewTheme,
        buildExitPreviewUrl: buildExitPreviewUrl,
        createPreviewIndicator: createPreviewIndicator,
        initPreviewIndicator: initPreviewIndicator
    };

    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    root.SparkPreview = api;

    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                initPreviewIndicator(document, root.location);
            }, { once: true });
        } else {
            initPreviewIndicator(document, root.location);
        }
    }
})(typeof window !== 'undefined' ? window : globalThis);
