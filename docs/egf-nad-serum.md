# The EGF + NAD+ Firming Serum

SKINOFAB's fourth product: a light firming serum for face and neck in a matte black dropper bottle and a black carton.
Inspired by Meimei's "NAD+ Firming Serum" (https://officialmeimei.com/products/egf-nad-firming-serum), rebuilt for
SKINOFAB: the Adaptive Peptide Foundation page's structure and look, photos of women past 45 using the serum on white,
SKINOFAB's real wordmark on every bottle and carton, and nothing on the page that we can't stand behind.

Preview: https://skinofab.29next.store/catalogue/egf-nad-firming-serum_206/?preview_theme=34

## Before launch (owner)

- **Formula.** The page names EGF (sh-Oligopeptide-1), NAD+, collagen and glycerin. Meimei's own ingredient list
  (Aqua, Glycerin, 1,2-Hexanediol, Carbomer, Arginine, Nicotinamide Adenine Dinucleotide, Collagen Extract) has **no
  EGF**, though its name and copy say EGF. Check your supplier's INCI list: if sh-Oligopeptide-1 is not in it, change
  the name (`TITLE`, the label in `tools/persona/label_composite.py`) and the EGF lines in
  `tools/persona/serum_copy.py` (`INGREDIENTS`, `TWIN`, `FAQ`) before selling.
- **EU.** sh-Oligopeptide-1 is not allowed in cosmetics sold in the EU. Don't ship the EGF version there.
- **Size and dose.** The page says 30 mL / 1.01 fl oz, two drops for the face and two for the neck, morning and night,
  about two months per bottle (`SIZE`, `BUNDLES` notes, FAQ). Change them if your bottle or dropper differs.
- **Product photos of the real bottle.** The photos are AI-generated with the packaging blank; the label is printed on
  by `label_composite.py` from the real wordmark (`brand/adaptive-peptide-foundation/00-logo.png`). The bottle in them
  is close to, not exactly, the one you will ship. Once the real bottle exists, photograph it on white and swap the
  packshots (`pack`, `tall`, `trio`) first.

## What Meimei's page does, and what we kept

| Meimei device | Here |
|---|---|
| Hero promise "Achieve firm, radiant, glass skin" + four benefit lines | The buy box lead (firmer, smoother, more radiant-looking, face and neck) and gallery 4 "Firmer-looking skin", three facts |
| How to use (cleanse, pearl-sized amount, face & neck, morning + night) | The "How do I use it?" tab, "How does it work?" block and "Two drops, face and neck" cards |
| Ingredient story (EGF, NAD, collagen) | The K-beauty skin science block, the ingredient carousel and gallery 6 "What's inside", cosmetic claims only |
| "What's really causing premature aging" | Problem / root cause / solution, on skin after 45 (collagen after menopause, drier skin, too many heavy steps) |
| "Your nightly anti-aging journey" (first night, week 1, week 2, beyond) | "What to expect": two drops, day 1 (hydrated, smoother: a cosmetic effect), 8 weeks from one bottle |
| FAQ (how often, sensitive skin, with other products, how long, wrinkles) | 10 answers, including retinol and vitamin C, how long a bottle lasts, what the EGF is, pregnancy |
| 30-day money-back guarantee | The store's 30-day money-back guarantee (buy box, tab, card) |
| One bottle at $45 | 1 bottle $34.95 · 2 bottles $59.95 (most popular) · Buy 2, get 1 free $69.90 (exactly 2 × $34.95) |

## What we left out, and why

- **"🇰🇷 #1 Firming Serum"**: no ranking backs it.
- **"Rated 4.9 (based on 137,135 reviews)", "Based on 11,761+ customer reviews", "Join over 10,000+ happy
  customers"**: their counts (and they disagree with each other), not ours. The serum shows "No reviews yet" until
  real SKINOFAB buyers review it, and the reviews near the top are the foundation's, labelled as theirs.
- **"Clinically proven results" (+36.8% hydration, +29.4% fewer lines…)**: from a "consumer self-perception study"
  by their own footnote, so not clinical proof, and not our study.
- **"Clinically recommended", "works at the source", "repair", "stimulate collagen", "prevents premature aging"**:
  claims that need our own tests, or structure/function (drug) claims.
- **Their testimonials** (Elena G., 23; Megan K., 40 …): their customers, not ours (16 CFR 465); several describe "this
  cream" and another product ("Madeca Time Reverse Cream").
- **Madecassoside, Centella, peptides, niacinamide**: named in their copy, missing from their ingredient list.
- **The Meimei name and look**: the serum is SKINOFAB black, with the foundation's label system.

## What is on the site

| Where | What |
|---|---|
| NEXT product 206 | "EGF + NAD+ Firming Serum", public, one-time purchase, template `egf-nad-firming-serum`, Face / Skin / Bestsellers |
| Bundles (variants) | 207: 1 bottle $34.95 · 208: 2 bottles $59.95 (default; compare $69.90) · 209: 3 bottles (buy 2, get 1 free) $69.90 (compare $104.85) |
| Product page | The Adaptive Peptide Foundation page's structure, section by section (`tools/persona/twin.py`): gallery (13 photos, in the foundation gallery's order: packshot and carton with the Korean badge, a woman holding it, before/after, "Firmer-looking skin", the before/after board, what's inside, the science, vs others, five photos of women using it and the three-bottle pack); the foundation's buy box; then the foundation's sections in its order: its review strip (the foundation's reviews, labelled as theirs), "Made for real life after 45" photo cards, problem / root cause / solution, the brand's own note (where the foundation has its dermatologist), K-beauty skin science, the before/after block, "How does it work?", what to expect, Why skinofab? (vs basic serums), what's inside, how to use it, FAQ (10), an honest "No reviews yet" box, The skinofab difference; sticky bar |
| Homepage | A card in the product shelf after the balm (default list, Bestsellers, New and Face tabs), "New" and "Buy 2, get 1 free" badges |
| Menus | "Firming Serum" in the desktop and mobile menus (before PDRN Balm) and in the footer's Shop column (after it) |
| Cart drawer | Third add-on (after the brush and the balm), and its own upgrade card, 1 → 2 bottles for $25 (Theme settings → Cart Drawer → Fourth upgrade) |

## Images

Every photo is on pure white, with women past 45 (several ages, skin tones and hair colours) holding and using the
serum, in the foundation gallery's style. They were made with GPT Image 2.5 through Figma's image generator, with the
bottle and carton **blank**: `tools/persona/label_composite.py` then prints SKINOFAB's real wordmark and label on
every bottle (wrapped around the cylinder, shaded by the bottle's own light, behind the fingers that hold it) and on
the carton's front, so the logo is ours to the pixel instead of an AI's guess. The before/after photos are
illustrations and say so on the image. Prompts: `tools/persona/image_prompts.json`; sources:
`brand/egf-nad-serum/source/`.

## Rebuilding

```bash
# images: the label on every bottle, white backdrops, the gallery layouts -> brand/egf-nad-serum/*.jpg
python3 -I tools/persona/product_photos.py serum
# the NEXT product and its bundles (idempotent) -> <work_dir>/serum-offers.json and catalog-rb.json
NEXT_API_TOKEN=... python3 -I tools/persona/setup_brush_offers.py skinofab <work_dir> serum_copy
NEXT_API_TOKEN=... python3 -I tools/persona/upload_gallery.py skinofab 206 <work_dir>/serum-gallery-undo.json \
  brand/egf-nad-serum/{card,hero,hold-cheek,before-after,look-firmer,results-grid,whats-inside,science,vs-others,drop,hold-black,friends,apply-neck,trio}.jpg
# the theme: apply_persona.py builds the page with product_page(base, serum_copy)
tools/build_store.sh <work_dir>
```

Copy, offer, tabs, FAQ, each section's content (`TWIN`), the shelf card, menus and collections live in
`tools/persona/serum_copy.py`; the sections' markup is the foundation page's own (`tools/persona/twin.py`).
`node tools/theme-qa/offer-e2e.mjs https://skinofab.29next.store 34 /catalogue/adaptive-peptide-foundation_14/ shots/`
checks the serum without placing an order: each pack (variant, price, one-time line, drawer, checkout for 2 bottles
with its line thumbnail), the 1 → 2 bottles upgrade, the page (the foundation's sections in its order, its six tabs,
the FAQ, borrowed reviews labelled as the foundation's, before/after marked as illustrations, no Meimei name or dropped
claim, no "was" price on one bottle, no broken image), the homepage card, the menu links and the sticky bar.
