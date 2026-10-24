# The PDRN Plumping Balm

SKINOFAB's third product: a matte black press-on balm stick for tired-looking under-eyes, smile lines and lip lines.
Inspired by FEM+'s "Collagen Plump & Repair Volufiline Balm" (https://www.femplus.com/products/fempdrnbalm), rebuilt
for SKINOFAB: the foundation's packaging system, women past 45, and nothing on the page that we can't stand behind.

Preview: https://skinofab.29next.store/catalogue/pdrn-plumping-balm_202/?preview_theme=34

## Before launch (owner)

- **Formula.** The page names PDRN (salmon DNA), Volufiline™, hydrolyzed collagen, hyaluronic acid and adenosine, the
  standard formula of this product type (FEM+ lists the same). Check them against your supplier's INCI list and change
  `INGREDIENTS` / `ADENOSINE` in `tools/persona/balm_copy.py` if they differ. Volufiline™ is Sederma's trademark: keep the
  name only if it is in the formula.
- **Net weight and size.** The label and the page say 10 g / 0.35 oz and the renders are a 22.6 mm × 100 mm stick. Change
  `NET` in balm_copy.py and `R`, `Z_CAP1` in balm_render.py if yours differ.
- **Balm color.** Rendered as a translucent warm nude; set the color in balm_render.py `mat_balm()` to your real balm.
- **Fish allergy.** PDRN is salmon-derived: the page says so (Key ingredients tab, FAQ). Keep that line.
- **Lifestyle photos.** The gallery is product-only (3D renders). A woman over 45 using the stick needs an image route;
  the shots are in [persona-image-shots.md](persona-image-shots.md) (P1–P4).

## What FEM+'s page does, and what we kept

| FEM+ device | Here |
|---|---|
| Headline image "The secret to not looking tired all the time" | Gallery 1: "Look less tired in 10 seconds" (the time it takes to apply), the open stick, three facts, the 30-day seal |
| Bundles 1 / 2 / 3 packs, "30/60/90-day supply" | 1 stick $24.95 · 2 sticks $39.95 (most popular) · 3 sticks $49.90 ("Buy 2, get 1 free", exactly 2 × $24.95) |
| Ingredient cards (PDRN, Volufiline, collagen, hyaluronic acid) | Same four, our words, cosmetic claims, + adenosine and oils |
| "Why a press-on stick works where a cream does not" | Our own six-row comparison (stick vs. a jar of cream), and a gallery image of it |
| "5 reasons you still look tired" | "Why you look tired, even when you're not": four cards on skin after 45 (collagen loss after menopause, drier skin, concealer creasing, the mirror vs. photos) |
| Objection FAQ ("greasy?", "under makeup?", "with retinol?", "how long?") | 10 answers, including how long a stick lasts and the fish-allergy note |
| Day 1 / 7 / 14 / 30 timeline | "What to expect": right away, with daily use, and what it won't do (not a filler, won't change dark-circle color) |
| 30-day "results or it's free" | The store's 30-day money-back guarantee (buy box, tab, card, seal) |
| Sticky add-to-cart | The site's sticky bar |

## What we left out, and why

- **"96% sold", "1M+ units sold", "30K+ bought last month", "300+ bought today"**: invented scarcity and counts (FTC Act §5).
- **"77% said under-eyes looked less hollow"** and the other percentages: no study of our own behind them.
- **The countdown timer and "Halloween sale, up to 75% off"**: a fake deadline, and a "was" price ($37, $111) the
  product was never sold at (16 CFR 233). Our bundle savings compare with buying single sticks.
- **"Dermatologist tested", "Backed by clinically studied ingredients", "Supports collagen production"**: the first two
  need our own test reports; the third is a structure/function (drug) claim.
- **Their testimonials and reviews** (@rachel 32, Carrie K. …): their customers, not ours (16 CFR 465). The balm shows
  "No reviews yet" until real SKINOFAB buyers review it, as the brush does.
- **The pink pack and FEM+ name**: the stick is SKINOFAB black, with the foundation's label system.

## What is on the site

| Where | What |
|---|---|
| NEXT product 202 | "PDRN Plumping Balm", public, one-time purchase, template `pdrn-plumping-balm`, Face / Skin / Bestsellers |
| Bundles (variants) | 203: 1 stick $24.95 · 204: 2 sticks $39.95 (default; compare $49.90) · 205: 3 sticks (buy 2, get 1 free) $49.90 (compare $74.85) |
| Product page | Gallery (7 renders), eyebrow, title, price (no "was" on one stick), free shipping, the promise, 4 chips, pack picker, Add to cart with the pack price, guarantee, 5 tabs; then why you look tired, four actives, stick vs. jar, where & how to use it, what to expect, the foundation for after, FAQ (10), guarantee card, "No reviews yet", sticky bar |
| Homepage | A card in the product shelf after the brush (default list, Bestsellers, New and Face tabs), "New" and "Buy 2, get 1 free" badges |
| Menus | "PDRN Balm" in the desktop and mobile menus (before Lymphatic Brush) and in the footer's Shop column |
| Cart drawer | Second add-on (after the brush; it replaced the under-eye patches), and its own upgrade card, 1 → 2 sticks for $15 (Theme settings → Cart Drawer → Third upgrade) |

## Images

All product images are 3D renders of the stick in Blender (`tools/persona/balm_render.py`): soft-touch matte black,
the white SKINOFAB wordmark vertical (S at the top), "PLUMPING BALM", "PDRN · VOLUFILINE" and the weight in Montserrat,
a cool grey studio sweep, as on the foundation's product sheet. The label is printed through the shader, so it is
sharp and correct at any size (no AI lettering). `tools/persona/balm_assets.py` lays out the gallery in the store's
black-on-grey style.

```bash
S=<work dir>
python3 -m venv $S/bpyenv && $S/bpyenv/bin/pip install bpy==5.2.3 numpy pillow     # Blender as a Python module
$S/bpyenv/bin/python tools/persona/balm_render.py $S/balm-final front card open bullet duo trio tilt jar   # ~8 min a shot on 4 CPUs
python3 -I tools/persona/balm_assets.py $S/balm-final        # -> brand/pdrn-balm/*.jpg
```

## Rebuilding

```bash
# the NEXT product and its bundles (idempotent) -> <work_dir>/balm-offers.json and catalog-rb.json
NEXT_API_TOKEN=... python3 -I tools/persona/setup_brush_offers.py skinofab <work_dir> balm_copy
NEXT_API_TOKEN=... python3 -I tools/persona/upload_gallery.py skinofab 202 <work_dir>/balm-gallery-undo.json \
  brand/pdrn-balm/{card,hero,ingredients,stick-vs-cream,where,how-to-use,texture,duo}.jpg
# the theme: apply_persona.py builds the page with product_page(base, balm_copy)
tools/build_store.sh <work_dir>
```

Copy, offer, tabs, FAQ, sections, the shelf card, menus and collections live in `tools/persona/balm_copy.py`.
`node tools/theme-qa/offer-e2e.mjs https://skinofab.29next.store 34 /catalogue/adaptive-peptide-foundation_14/ shots/`
checks the balm without placing an order: each pack (variant, price, one-time line, drawer, checkout for 2 sticks with
its line thumbnail), the 1 → 2 sticks upgrade, the page (section order, tabs, FAQ, no FEM+ name or dropped claim, no
"was" price on one stick, broken images), the homepage card, the menu links and the sticky bar.
