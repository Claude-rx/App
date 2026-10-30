# Spark Design System

Spark is a storefront theme for Next Commerce. This document is the single source of truth for all visual decisions. Read this before making any UI change.

**Aesthetic:** Everlane / Aesop / Apple Store — clean commerce, products-are-the-design.

---

## Typography

**Font stack:** System fonts — zero load time, native feel.

```
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

Merchants can override body and heading fonts via dashboard settings (`font_body`, `font_header`). The system stack is the default.

### Heading scale

| Utility | Default size |
|---------|--------------|
| `text-h3` | 1.25rem |
| `text-h2` | 1.5rem |
| `text-h1` / `md:text-h1-md` | 1.875rem / 2.25rem |
| `text-display` / `md:text-display-md` | 1.875rem / 3rem |

Each heading token carries Tailwind's line-height ratio. The `heading_scale` setting in Theme Settings > Style > Type Scale multiplies these sizes through `--heading-scale`: small is 0.875, default is 1, and large is 1.125. Body copy stays on the utility scale. The `body_size` setting accepts 15px through 18px and sets the body font-size through `--body-size`; its 16px default is the browser default. The page background comes from `body_bg_color` through `--body-bg-color`.

| Role | Size | Weight | Line-height | Usage |
|------|------|--------|-------------|-------|
| Page heading | text-2xl / text-3xl | 600 (semibold) | 1.2 | h1 on category, PDP, blog post |
| Section heading | text-2xl | 600 | 1.2 | Homepage sections, support |
| Body text | text-sm (0.875rem) | 400 | 1.6 | Descriptions, form labels, nav links |
| Product title (card) | text-sm (0.875rem) | 500 (medium) | 1.6 | Product grid cards |
| Product price | text-sm (0.875rem) | 400 | 1.6 | Below title in cards |
| Price (PDP) | text-lg | 500 | 1.6 | Product detail page |
| Breadcrumbs | text-xs (0.75rem) | 400 | 1.6 | Navigation path |
| Footer headers | text-sm | 600 | 1.2 | Uppercase + tracking-wider |
| Footer body | text-sm | 400 | relaxed (1.625) | Links, address, contact |
| Copyright | text-xs | 400 | 1.6 | Bottom of footer |
| Button text | text-sm (0.875rem) | 500 | 1.25rem | All buttons |
| Cart badge | 10px | 600 | 1 | Header cart count |

**Letter spacing:** `tracking-wider` (0.125em) only on footer section headers. Nowhere else.

---

## Color

### Neutral palette (Slate)

| Token | Hex | Usage |
|-------|-----|-------|
| slate-800 | #1E293B | Primary text, headings, body default |
| slate-600 | #475569 | Secondary text, nav links, product price, icon default |
| slate-500 | #64748B | Tertiary text, footer links, muted content |
| slate-400 | — | Breadcrumb separators, strikethrough prices |
| slate-300 | — | Placeholder text (no-image states) |
| slate-200 | #E2E8F0 | Borders, dividers (header, footer, cards, forms) |
| slate-100 | #F1F5F9 | Image placeholder backgrounds, skeleton shimmer base |
| slate-50 | #F8FAFC | Footer background, secondary button hover, card image bg |
| white | #FFFFFF | Page background, button text on primary |

### Brand colors (merchant-configurable)

| Property | Default | Source |
|----------|---------|--------|
| `--primary-color` | #1E293B | `store.branding.primary_color` via dashboard |
| `--accent-color` | #475569 | `store.branding.accent_color` via dashboard |
| `--primary-color-lighter` | computed | `color-mix(in srgb, var(--primary-color), #fff 15%)` |
| `--primary-color-darker` | computed | `color-mix(in srgb, var(--primary-color), #000 15%)` |

### Status colors (hardcoded — NOT merchant-customizable)

| Token | Hex | Usage |
|-------|-----|-------|
| success | #22C55E | Add-to-cart success state, coupon applied |
| error | #EF4444 | Error messages, validation, add-to-cart error |
| warning | #F59E0B | Warnings (reserved) |

These are functional signals, not brand expression. Never let merchants change them.

### Opacity scale

| Value | Usage |
|-------|-------|
| 0.9 | Button hover |
| 0.8 | Link hover, general hover |
| 0.7 | Footer secondary text, contact info |
| 0.5 | Disabled buttons, copyright, disclaimer |
| 0.3 | Backdrop overlay (black/30) |

---

## Spacing

**Base unit:** 4px (Tailwind default).

| Scale | Value | Common usage |
|-------|-------|-------------|
| 1 | 4px | Micro spacing |
| 2 | 8px | Icon gaps, tight spacing |
| 3 | 12px | Product card margins, inline gaps |
| 4 | 16px | Container padding (mobile), section spacing |
| 6 | 24px | Container padding (desktop), product grid gap |
| 8 | 32px | Section padding, footer grid gaps, PDP column gap |
| 12 | 48px | Major section padding (py-12) |
| 16 | 64px | Footer top margin (mt-16) |

### Section rhythm and content gap (merchant-adjustable)

Standard sections use 3rem vertical padding and 4rem at 768px and above. The promo band uses 4rem and 5rem at the same breakpoint. The default content gap is 1.5rem; its `sm`, `md`, and `lg` steps use 2/3, 4/3, and 2x ratios.

Theme Settings > Style > Layout controls these values. `section_padding` sets `--section-padding-y` to compact (2rem), default (3rem), or roomy (5rem). `content_gap` sets `--content-gap` to tight (1rem), default (1.5rem), or loose (2rem).

### Container

**Max-width:** 1280px default; `container_max_width` offers 1120px / 1280px / 1440px via `--container-max`.

**Gutters:** 1rem (mobile) → 1.5rem (768px+). Margin remains auto (centered).

---

## Borders & Radius

**Default:** Sharp corners. Spark does not round things.

| Element | Radius | Rationale |
|---------|--------|-----------|
| Buttons (`.btn`) | 4px default, `radius_control` (0-16px) via `--control-radius` | Subtle, functional rounding |
| Form inputs | 4px (0.25rem), literal | Matches the button default; not yet on the token |
| Product cards, featured image, category tiles | 0 default, `radius_card` (0-16px) via `--card-radius` | Sharp by default |
| Everything else | 0 | Sharp, architectural feel |

**Border style:** 1px solid slate-200 (`#E2E8F0`) for all layout dividers — header bottom, footer sections, form fields, card boundaries. `border_color` via `--border-color` drives the secondary button and bordered product cards today; the other dividers stay literal until they move onto the token.

**Box shadow:** Almost never. Clean flat aesthetic. Exception: side cart legacy CSS (platform dependency).

---

## Buttons

| Variant | Background | Text | Border | Hover |
|---------|-----------|------|--------|-------|
| `.btn-primary` | `var(--primary-color)` | white | `var(--primary-color)` | opacity 0.9 |
| `.btn-secondary` | transparent | `var(--primary-color)` | slate-200 | bg slate-50 |

```
Base: inline-flex, items-center, justify-center
Padding: 0.625rem 1.5rem (10px 24px)
Font: 0.875rem / 500 weight
Radius: 0.25rem (4px)
Transition: opacity 150ms ease-out
Disabled: opacity 0.5, cursor not-allowed
```

### Contrast auto-detection

When `--primary-color` is light (luminance > 0.6), `.btn-primary` text flips to dark (#1E293B) via `data-light-primary` attribute on `<html>`. JS in base.html measures luminance and toggles the attribute.

---

## Product Card

```
Layout: flex column
Image: aspect-ratio 1:1, object-fit cover, bg slate-50
Title: text-sm, font-medium (500), slate-800, mt-3
Price: text-sm, slate-600 (--accent-color), mt-1
Sale price: strikethrough in slate-400, text-xs, ml-1
Hover: title color → slate-600 (group-hover)
No-image: aspect-square, bg slate-100, centered slate-300 text
```

No badges. No rating stars. No "New!" tags. No hover zoom. No shadow lift. Products are the design — let the photography speak.

---

## Product Grid

```
Mobile (<768px):  1 column
Tablet (768px+):  2 columns
Desktop (1024px+): 3 columns
Gap: 1.5rem (24px)
```

---

## Layout Patterns

### Header (sticky)
```
Height: 64px (h-16)
Background: white (or settings.navbar_bg_color)
Border: 1px bottom, slate-200
Z-index: z-50
Nav links: text-sm, font-medium, slate-600, hover slate-900
Mobile toggle: left side, md:hidden
Logo: center-left, flex-shrink-0
Right icons: search, account (md:only), cart — gap-4
```

### Footer
```
Background: slate-50 (or settings.footer_bg_color)
Border: 1px top, slate-200
Top margin: mt-16 (64px)
Grid: 1 col (mobile) → 4 col (768px+)
Section headers: text-sm, semibold, uppercase, tracking-wider
Links: text-sm, slate-500, hover opacity 0.8
```

### PDP Layout
```
Mobile: stacked (images → info)
Desktop (768px+): 5-column grid, images 3-span, info 2-span
Info sidebar: sticky, top-24
```

### Catalogue Layout
```
Mobile (<1024px): filter trigger above the grid, so filters remain reachable
                  for empty and short result sets. A supplemental sticky filter
                  bar appears while scrolling long grids and slides out again
                  before the pagination.
Desktop (1024px+): 15rem filter rail (sticky, top-22) + product grid.
Filter drawer: bottom sheet, max-height 85vh, slide up 250ms ease-out.
               Backdrop black/30, fade 200ms. Escape and backdrop close.
Controls: 44px minimum height, 4px radius (form-control rounding).
```

---

## Motion Language

**Principle:** Purposeful, not decorative. Every animation communicates state change.

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| micro | 150ms | ease-out | Hover, opacity, focus |
| small | 250ms | ease-out (in) / ease-in (out) | Panel slide, fade, dropdown |
| medium | 300ms | ease-out | Badge scale, button state transition |
| large | 400ms | ease-out | Shake, error feedback |
| spinner | 800ms | linear | Continuous rotation |
| shimmer | 1500ms | ease-in-out | Skeleton loading loop |

### Banned motion patterns
- bounce
- elastic / spring physics
- parallax
- scroll-triggered animations
- decorative entrance animations (elements "flying in")

---

## Interaction States

### Add-to-Cart Button

| State | Visual |
|-------|--------|
| Idle | btn-primary, full-width, "Add to Cart" |
| Loading | Same dimensions, text replaced by 16px CSS spinner (2px border, white border-top, 800ms linear rotate) |
| Success | Background → #22C55E, text → "✓ Added". Hold 2s, crossfade 200ms back to idle |
| Error | Shake (translateX 0→4→-4→2→-2→0, 400ms ease-out), red border flash. Error text below button: text-sm, #EF4444 |

### Side Cart Panel

| State | Visual |
|-------|--------|
| Opening | Slide from right (translateX 100%→0), 250ms ease-out. Backdrop: black/30, fade 200ms |
| Closing | Reverse. Triggered by: Escape key, backdrop click, close button |
| Empty | Centered: shopping bag SVG (48px, slate-300) + "Your cart is empty" (text-lg, slate-600) + "Add items to get started" (text-sm, slate-400) + "Continue Shopping" btn-primary |
| With items | Header (sticky) + scrollable items + sticky footer (subtotal + checkout CTA) |

**Responsive:** Full-width on mobile (<768px). 400px panel on tablet+.
**Focus trap:** Tab cycles through cart items, close button, checkout. Focus returns to cart icon on close.
**ARIA:** `role="dialog"`, `aria-label="Shopping cart"`, `aria-modal="true"`.

### Cart Badge

| State | Visual |
|-------|--------|
| Hidden | count = 0, not rendered |
| Visible | 16px circle, top-right of cart icon (-4px/-4px offset), bg primary-color, white text, 10px/600 |
| Update | Scale 1.0→1.3→1.0, 300ms ease-out. Only on count change, not page load |

### Quantity Stepper

```
Layout: [-] | input | [+]
Buttons: 36px square, border slate-200, text slate-600, hover bg slate-50
Input: 48px wide, text-center, no browser spin buttons
At min (1): minus → opacity 0.3, not-allowed
At max: plus → opacity 0.3, not-allowed
ARIA: role="spinbutton", aria-valuenow/min/max on input
      aria-label on buttons
```

### Skeleton Loading

```
Placeholder cards match product-grid columns (1/2/3 per viewport)
Each: gray rect (1:1 ratio, bg #F1F5F9) + two text bars (60%/40% width, 12px height)
Shimmer: linear-gradient(90deg, #F1F5F9, #E2E8F0, #F1F5F9)
Animation: translateX(-100%→100%), 1.5s infinite ease-in-out
```

---

## Z-Index Layers

```
z-40: Announcement bar
z-50: Sticky header, PDP sticky ATC bar, catalogue filter bar
z-60: Search overlay + backdrop, Mobile nav + backdrop, Filter drawer + backdrop
z-70: Side cart + backdrop (highest — always accessible)
```

The two bottom bars share z-50 and never appear on the same page: the sticky
ATC is PDP-only, the catalogue bar is category-only. Both hide from
1024px up.

**Panel rule:** One panel at a time. Opening any panel auto-closes others.

---

## Accessibility

### Focus visible
```
outline: 2px solid var(--primary-color)
outline-offset: 2px
```
Applied to all interactive elements via `:focus-visible`. Sharp, matches Spark corners.

### Keyboard navigation
- Tab through product grid cards → Enter navigates to PDP
- Escape closes: side cart, mobile nav, search overlay
- Side cart and mobile nav trap focus when open

### Touch targets
Minimum 44px on mobile for all interactive elements (buttons, links, form controls).

### Color contrast
JS in base.html measures `--primary-color` luminance. If light (>0.6), adds `data-light-primary` to `<html>`. `.btn-primary` text flips to dark (#1E293B).

---

## Anti-Slop Rules

These patterns are banned. If you see them in a PR, reject it.

1. **3-column icon feature grids** — generic SaaS layout. Products are the feature.
2. **Centered-everything layout** — left-align text. Only center: empty states, footer copyright.
3. **Generic hero text** — "Welcome to our store." The hero IS a product image.
4. **Decorative gradients or blobs** — zero decorative elements.
5. **Rounded-everything** — the default is 0px for cards and 4px for controls. Merchant radius settings are the sanctioned way to add rounding.
6. **Drop shadows for depth** — flat aesthetic. Borders for separation.
7. **Ratings/badges/tags on product cards** — image + title + price. Nothing else.
8. **Hover zoom on product images** — let photos breathe. group-hover:text-slate-600 on title is enough.

---

## Empty States

Every empty state must have: (1) visual context, (2) warmth, (3) a primary action.

| Context | Heading | Subtext | Action |
|---------|---------|---------|--------|
| Empty cart | "Your cart is empty" | "Add items to get started" | "Continue Shopping" btn-primary |
| No products (category) | "No products found" | — | "Back to home" btn-secondary |
| No search results | "No results for '{query}'" | — | "Try a different search" |
| No product image | — | — | Gray placeholder (slate-100, centered slate-300 text) |

---

## Print Stylesheet

```css
@media print {
    header, footer, .announcement-bar, .side-cart { display: none; }
    .container { max-width: 100%; padding: 0; }
    body { font-size: 12pt; color: #000; }
    a { color: #000; text-decoration: underline; }
    img { max-width: 100%; }
}
```

Applied to support articles and cart page. Hide chrome, clean layout, readable typography.

---

## Merchant-Configurable Settings

| Setting | Type | Default | Affects |
|---------|------|---------|---------|
| `font_script` | HTML | — | Custom font embed (Google Fonts, etc.) |
| `font_body` | text | system stack | Body font-family |
| `font_header` | text | system stack | Heading font-family |
| `body_text_color` | color | #1E293B | Body text |
| `body_header_color` | color | #1E293B | Headings |
| `body_link_color` | color | primary | Links |
| `body_bg_color` | color | #FFFFFF | Page background via `--body-bg-color` |
| `border_color` | color | #E2E8F0 | Secondary button and bordered product card borders via `--border-color` |
| `radius_control` | select | 4px | Button (`.btn`) radius via `--control-radius` |
| `radius_card` | select | 0 | Product card, featured image, and category tile radius via `--card-radius` |
| `section_padding` | select | default (3rem) | Homepage section and promo-band vertical rhythm via `--section-padding-y` |
| `content_gap` | select | default (1.5rem) | Product grids, category grids, and content-column gaps via `--content-gap` |
| `container_max_width` | select | 1280px | Container maximum width via `--container-max` |
| `heading_scale` | select | default (1) | Display and section heading tokens via `--heading-scale` |
| `body_size` | select | 16px | Body font-size via `--body-size` |
| `navbar_bg_color` | color | white | Header background |
| `navbar_link_color` | color | #475569 | Nav icon/link color |
| `footer_bg_color` | color | #F8FAFC | Footer background |
| `footer_text_color` | color | — | Footer body text |
| `footer_link_color` | color | #64748B | Footer links |

These settings are applied via inline `style` attributes in templates, using CSS custom properties where possible.
