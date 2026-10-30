/**
 * Spark Gallery - Product image gallery with thumbnails
 *
 * Progressive enhancement: without JS, all images display stacked.
 * With JS, shows one main image + clickable thumbnail strip.
 *
 * Layouts (set via data-layout on .spark-gallery):
 *   "bottom"  - thumbnails below main image (default)
 *   "left"    - thumbnails to the left of main image (desktop)
 *
 * Variant linking: listens for spark:variant:changed and advances
 * the gallery to the matching variant image.
 *
 * Keyboard: ArrowLeft/ArrowRight to navigate, Home/End for first/last.
 *
 * ASCII-only - no unicode, no template syntax in this file.
 */

(function() {
    'use strict';

    var FADE_MS = 180;

    function SparkGallery(el) {
        this.el = el;
        this.main = el.querySelector('.spark-gallery-main');
        this.mainImg = el.querySelector('.spark-gallery-hero');
        this.thumbs = el.querySelectorAll('.spark-gallery-thumb');
        this.prevBtn = el.querySelector('.spark-gallery-prev');
        this.nextBtn = el.querySelector('.spark-gallery-next');
        this.current = 0;
        this.total = this.thumbs.length;
        this._fading = false;

        if (this.total < 2) {
            // Single image - hide nav controls
            if (this.prevBtn) this.prevBtn.style.display = 'none';
            if (this.nextBtn) this.nextBtn.style.display = 'none';
            this._bindVariantState();
            return;
        }

        this._bindEvents();
        this._bindVariantState();
    }

    SparkGallery.prototype._bindEvents = function() {
        var self = this;

        // Thumbnail clicks
        this.thumbs.forEach(function(thumb, i) {
            thumb.addEventListener('click', function() {
                self.goTo(i);
            });
        });

        // Prev/Next buttons
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', function() {
                self.prev();
            });
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', function() {
                self.next();
            });
        }

        // Keyboard navigation when gallery is focused
        this.el.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                self.prev();
            } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                self.next();
            } else if (e.key === 'Home') {
                e.preventDefault();
                self.goTo(0);
            } else if (e.key === 'End') {
                e.preventDefault();
                self.goTo(self.total - 1);
            }
        });

        // Swipe support for touch devices
        var touchStartX = 0;
        var touchStartY = 0;
        this.main.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        this.main.addEventListener('touchend', function(e) {
            var dx = e.changedTouches[0].clientX - touchStartX;
            var dy = e.changedTouches[0].clientY - touchStartY;
            // Only swipe if horizontal movement > vertical and > 50px
            if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
                if (dx < 0) {
                    self.next();
                } else {
                    self.prev();
                }
            }
        }, { passive: true });
    };

    /**
     * Variant integration: the PDP variant state Module owns product data
     * parsing and selected child matching. The gallery is only an Adapter
     * that reacts to spark:variant:changed with image behavior.
     */
    SparkGallery.prototype._bindVariantState = function() {
        var self = this;
        document.addEventListener('spark:variant:changed', function(e) {
            var detail = e.detail || {};
            var variant = detail.variant;
            if (!variant || typeof SparkVariantState === 'undefined') return;

            var url = SparkVariantState.getVariantImageUrl(variant);
            if (!url) return;

            var targetIdx = -1;
            for (var j = 0; j < self.thumbs.length; j++) {
                var full = self.thumbs[j].getAttribute('data-full') || '';
                if (SparkVariantState.sameImageUrl(full, url)) { targetIdx = j; break; }
            }
            if (targetIdx !== -1) {
                self.goTo(targetIdx);
            } else if (self.mainImg) {
                self.mainImg.src = url;
            }
        });
    };

    SparkGallery.prototype.goTo = function(index) {
        if (this._fading) return;
        if (index < 0) index = this.total - 1;
        if (index >= this.total) index = 0;
        if (index === this.current) return;

        var self = this;
        var thumb = this.thumbs[index];
        if (!this.mainImg || !thumb) return;

        // Fade out, swap, fade in
        this._fading = true;
        this.mainImg.classList.add('spark-gallery-fading');

        setTimeout(function() {
            self.mainImg.src = thumb.getAttribute('data-full');
            self.current = index;

            // Update active thumbnail
            self.thumbs.forEach(function(t, i) {
                if (i === index) {
                    t.classList.add('spark-gallery-thumb-active');
                    t.setAttribute('aria-current', 'true');
                    t.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
                } else {
                    t.classList.remove('spark-gallery-thumb-active');
                    t.removeAttribute('aria-current');
                }
            });

            // Fade in once the new image loads (or immediately if cached)
            if (self.mainImg.complete) {
                self.mainImg.classList.remove('spark-gallery-fading');
                self._fading = false;
            } else {
                self.mainImg.onload = function() {
                    self.mainImg.classList.remove('spark-gallery-fading');
                    self._fading = false;
                    self.mainImg.onload = null;
                };
                // Safety timeout in case onload never fires
                setTimeout(function() {
                    self.mainImg.classList.remove('spark-gallery-fading');
                    self._fading = false;
                }, 500);
            }
        }, FADE_MS);
    };

    SparkGallery.prototype.prev = function() {
        this.goTo(this.current - 1);
    };

    SparkGallery.prototype.next = function() {
        this.goTo(this.current + 1);
    };

    // Auto-init all galleries on page
    function initGalleries() {
        document.querySelectorAll('.spark-gallery').forEach(function(el) {
            if (el._sparkGallery) return;
            var gallery = new SparkGallery(el);
            el._sparkGallery = gallery;
        });
    }

    // Export for external use
    window.SparkGallery = SparkGallery;

    initGalleries();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGalleries);
    }

})();
