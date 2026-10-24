# The PDRN Plumping Balm

SKINOFAB's third product: a matte black press-on balm stick for tired-looking under-eyes, smile lines and lip lines.
Inspired by FEM+'s "Collagen Plump & Repair Volufiline Balm" (https://www.femplus.com/products/fempdrnbalm), rebuilt
for SKINOFAB: the Adaptive Peptide Foundation page's structure and look, photos of women past 45 using the stick on
white, and nothing on the page that we can't stand behind.

Preview: https://skinofab.29next.store/catalogue/pdrn-plumping-balm_202/?preview_theme=34

## Before launch (owner)

- **Formula.** The page names PDRN (salmon DNA), Volufiline™, hydrolyzed collagen, hyaluronic acid and adenosine, the
  standard formula of this product type (FEM+ lists the same). Check them against your supplier's INCI list and change
  `INGREDIENTS` / `ADENOSINE` in `tools/persona/balm_copy.py` if they differ. Volufiline™ is Sederma's trademark: keep the
  name only if it is in the formula.
- **Net weight.** The page says 10 g / 0.35 oz (`NET` in balm_copy.py): change it if yours differs.
- **Balm color.** The photos show a nude-pink balm; if yours is another shade, regenerate the photos with that shade
  in the prompts (`tools/persona/image_prompts.json`).
- **Fish allergy.** PDRN is salmon-derived: the page says so (Key ingredients tab, FAQ). Keep that line.
- **Product photos of the real stick.** The photos are AI-generated from a description of the stick (below): the
  stick in them is close to, not exactly, the one you will ship (proportions, the balm's shade, the label's small
  type). Once the real stick exists, photograph it on white and swap the packshots (`pack`, `tall`) first.

## What FEM+'s page does, and what we kept

| FEM+ device | Here |
|---|---|
| Headline image "The secret to not looking tired all the time" | Gallery 4: "Look less tired" (a woman over 45 pressing it under her eye), three facts |
| Before/after photos | Gallery 3 and 5, the before/after block: illustrations, and they say so on the image ("Image only for illustrative purposes"), as the foundation's illustrations do |
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
| Product page | The Adaptive Peptide Foundation page's structure, section by section (`tools/persona/twin.py`): gallery (13 photos, in the foundation gallery's order: packshot with the Korean badge, a woman holding it, before/after, "Look less tired", the before/after board, what's inside, the science, vs others, four women using it); the foundation's buy box ("Based on Korean beauty innovation", title, price with no "was" on one stick, free shipping, the promise, pack picker, Add to cart with the pack price, "Love it or your money back", the foundation's six tabs); then the foundation's sections in its order: its review strip (the foundation's reviews, labelled as theirs, until the balm has some), "Made for real life after 45" photo cards, problem / root cause / solution, the brand's own note (where the foundation has its dermatologist), K-beauty skin science, the before/after block, "How does it work?", what to expect, Why skinofab? (vs eye creams), what's inside (ingredient carousel), where to use it, FAQ (10), the review wall or an honest "No reviews yet" box, The skinofab difference; sticky bar |
| Homepage | A card in the product shelf after the brush (default list, Bestsellers, New and Face tabs), "New" and "Buy 2, get 1 free" badges |
| Menus | "PDRN Balm" in the desktop and mobile menus (before Lymphatic Brush) and in the footer's Shop column |
| Cart drawer | Second add-on (after the brush; it replaced the under-eye patches), and its own upgrade card, 1 → 2 sticks for $15 (Theme settings → Cart Drawer → Third upgrade) |

## Images

Every photo is on pure white (`docs/white-backgrounds.md`: one white for every product), with women past 45 (several ages, skin tones and hair colours) holding and using the stick,
in the foundation gallery's style. They were made with GPT Image 2.5 through Figma's image generator (the studio's
GPT Image 2 / Nano Banana Pro route could not store results: its Vercel Blob storage is suspended). That route takes
text only, so the stick is described in the prompt: matte black, about four times taller than wide, nude-pink balm
dome, SKINOFAB vertical in a thin serif. Every image was checked for the wordmark's spelling and regenerated when it
was wrong. Prompts: `tools/persona/image_prompts.json`; sources: `brand/pdrn-balm/source/`.

`tools/persona/product_photos.py` lays them out (Playfair Display headlines as on the foundation's gallery,
Montserrat small type, the foundation's Korean badge) into `brand/pdrn-balm/*.jpg`; the page's section images are
crops of the sources made at build time. The before/after photos are illustrations and say so on the image.

```bash
python3 -I tools/persona/product_photos.py      # brand/pdrn-balm/source -> brand/pdrn-balm/*.jpg (and the brush's before/after)
```

## Rebuilding

```bash
# the NEXT product and its bundles (idempotent) -> <work_dir>/balm-offers.json and catalog-rb.json
NEXT_API_TOKEN=... python3 -I tools/persona/setup_brush_offers.py skinofab <work_dir> balm_copy
NEXT_API_TOKEN=... python3 -I tools/persona/upload_gallery.py skinofab 202 <work_dir>/balm-gallery-undo.json \
  brand/pdrn-balm/{card,hero,hold-cheek,before-after,look-less-tired,results-grid,whats-inside,science,vs-others,apply-eye,hold-chin,friends,apply-lips,bag}.jpg
# the theme: apply_persona.py builds the page with product_page(base, balm_copy)
tools/build_store.sh <work_dir>
```

Copy, offer, tabs, FAQ, each section's content (`TWIN`), the shelf card, menus and collections live in
`tools/persona/balm_copy.py`; the sections' markup is the foundation page's own (`tools/persona/twin.py`).
`node tools/theme-qa/offer-e2e.mjs https://skinofab.29next.store 34 /catalogue/adaptive-peptide-foundation_14/ shots/`
checks the balm without placing an order: each pack (variant, price, one-time line, drawer, checkout for 2 sticks with
its line thumbnail), the 1 → 2 sticks upgrade, the page (the foundation's sections in its order, its six tabs, the FAQ,
borrowed reviews labelled as the foundation's, before/after marked as illustrations, no FEM+ name or dropped claim, no
"was" price on one stick, no broken image), the homepage card, the menu links and the sticky bar.
