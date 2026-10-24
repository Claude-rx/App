# The Lymphatic Brush

SKINOFAB's second main product, built from the owner's Solena page (https://thesolena.com/products/the-lymphatic-brush):
Solena's offer and structure, under the SKINOFAB name and in the store's black-and-white look, with every claim nothing
backs taken out (below).

Preview: https://skinofab.29next.store/catalogue/the-lymphatic-brush_169/?preview_theme=34

## What is on the site

| Where | What |
|---|---|
| NEXT product 169 | "The Lymphatic Brush", public, one-time purchase (no refills), template `the-lymphatic-brush`, 5 gallery images (the brush and case card first: the cart and checkout thumbnail) |
| Bundles (variants) | 170: 1 brush + free case, $24.95 (was $49.90) · 171: 2 brushes + 2 free cases, $39.95 (was $99.80), chosen by default · 172: 3 brushes + 3 free cases + free body brush, $49.90 (was $149.70) |
| Product page | The Adaptive Peptide Foundation page's structure, section by section (`tools/persona/twin.py`): gallery (hero, case, how to use, features, vs other tools); the foundation's buy box (stars once there are reviews, title and price, free shipping badge, the promise, bundle picker, Add to cart with the bundle price, "Love it or your money back", the foundation's six tabs); then the foundation's sections in its order: its review strip (the foundation's reviews, labelled as theirs, until the brush has some), "A fresher face in 3 minutes" photo cards, problem / root cause / solution (a 45+ woman with a puffy morning face), the brand's own note (where the foundation has its dermatologist), how it works, the before/after block (an illustration, labelled), "How does it work?", what to expect, Why skinofab? (vs other tools), what's in the box, the creator clips, FAQ (10 answers), the review wall or an honest "No reviews yet" box, The skinofab difference; sticky bar |
| Homepage | A product card in the shelf like the other products (default list, Bestsellers, New and Face tabs), next to the gua sha and face roller, with a "New" badge |
| Collections | Accessories, Face, Skin and Bestsellers in NEXT, as the gua sha and the face roller |
| Menus | "Lymphatic Brush" in the desktop and mobile menus (before Bestsellers) and in the footer's Shop column, on every page |
| Cart drawer | First add-on (shown while the brush is not in the bag) and its own upgrade card, 1 brush → 2 brushes for $15 |

## What changed from Solena's page, and why

- **Claims.** The brush is sold as a light, dry facial massage for the look of morning puffiness, not as drainage:
  no "soft bristles drain fluid out of your face", no "puffiness goes down after the first use" as a promise, no
  "water retention" or "supports drainage" (re-set in the same Montserrat in the features and vs-tools images).
  The "what to expect" section says the effect is temporary and that it won't erase wrinkles or reshape a face.
- **Structure.** Since October 2026 the page is built like the foundation's (same sections, same order, same look),
  with the brush's copy in `TWIN` (`tools/persona/brush_copy.py`). Two new photos with no product in them, made with
  GPT Image 2.5 (prompts in `tools/persona/image_prompts.json`): the problem portrait and the before/after
  illustration (`brand/lymphatic-brush/source/`, laid out by `tools/persona/product_photos.py`).
- **Gallery.** Gallery 1 is new: the real brush and its SKINOFAB case with an honest headline and the guarantee seal
  (no model; a 45+ persona photo takes it once generated, [persona-image-shots.md](persona-image-shots.md) B1).
  Solena's before/after (a face whose wrinkles vanish, which a brush cannot do) and its "Loved by 5,000+" board of
  before/afters are not used. The NEXT product's images were replaced the same way (old ones in
  `<work_dir>/brush-gallery-undo.json`).
- **Creator clips.** "POV: Shaving 10 years off in 5 mins" and "The lazy girl's secret to a sculpted face" are left
  out; the four others stay, the woman in her 50s first, under "Three minutes, every morning" (they are creators,
  not verified buyers, so not "Real people, real results").
- **The buyers line ("Nicole and 5,000+ others purchased"): removed.** The brush is new at SKINOFAB.
- **The free body brush** is a "Body Dry Brush", not "Anti-Cellulite".

- **The name.** "Solena" is gone everywhere: the case logo on gallery image 5 and on the case gift photo is now the
  SKINOFAB wordmark, "THE SOLENA" on the comparison chart (gallery 6) is now "THE SKINOFAB", the how-to video has the
  spoken and captioned "from Solena" cut (0.85 s), and the copy says SKINOFAB. Returns go to hello@skinofab.com.
- **Reviews: not carried over.** Solena's 152 published Judge.me reviews of the brush are dated 2 Nov 2024 to
  23 Feb 2026. Solena's first product went up on 21 Nov 2025 and the brush on 2 Mar 2026, so none of them can be
  from a Solena buyer of this brush. Judge.me marks every one "collected from another provider", with no verified
  buyer, and their photos were all uploaded together on 4 Mar 2026. Publishing them as SKINOFAB customer reviews
  would break the FTC's rule on consumer reviews (16 CFR 465). The rating line "4.8/5 · 154 reviews" goes with them.
- **The three short reviews under the button: not carried over.** Solena's own markup labels them as placeholders
  ("Avis 2 : à remplacer", photo alt "PRENOM 2").
- **"+10,000 Happy Customers" on the guarantee card: left out.** The same page says "5,000+ others purchased".
  Give the real number and it can go back in (the page's guarantee lines are in `tools/persona/brush_copy.py`).
- **The "As seen in" press logos** (Cosmopolitan, Allure, Elle, Marie Claire…): left out unless the brush really was
  featured in them.

Until then the page says so ("No reviews yet", with the 30-day guarantee as the proof, and a "Write the first
review" link when NEXT allows it). Two real outside sources can be added, both described in [reviews.md](reviews.md): verified
Solena buyers of this brush (from a dashboard export; the public reviews are all unverified and older than the
product), and the rating of the owner's own Amazon listing (totals and a link, never copied review text; another
seller's listing is refused). As soon as real reviews exist, the stars and the review wall appear on their own
(and the box hides itself): SKINOFAB buyers' reviews through
NEXT (approve them in the dashboard), or an export of real reviews imported with `tools/reviews/import_reviews.py`
(see [reviews.md](reviews.md)).

## Fulfilment

The free cases and the body brush are not cart lines: the variant name says what to pack ("2 brushes + 2 free
cases", "3 brushes + 3 free cases + free body brush"). The shipping tab promises Solena's terms: packed within 2–4
business days, delivered worldwide in 5–8 business days after shipping, free shipping. Change the tab
(`brush_copy.tabs()`) if SKINOFAB ships differently.

## Rebuilding

The work dir is the one `tools/build_store.sh` uses.

```bash
# 1. sources from Solena -> brand/lymphatic-brush/ (images, committed) and <work_dir>/brush/media/ (videos)
python3 -I tools/persona/brush_assets.py <work_dir>
# 2. the NEXT product and its bundles (idempotent) -> <work_dir>/brush-offers.json and catalog-rb.json
NEXT_API_TOKEN=... python3 -I tools/persona/setup_brush_offers.py skinofab <work_dir>
NEXT_API_TOKEN=... python3 -I tools/persona/upload_gallery.py skinofab 169 <work_dir>/brush-gallery-undo.json \
  brand/lymphatic-brush/{card,hero,how-to-use,features,vs-tools}.jpg
# 3. the theme (apply_persona.py builds the brush page from tools/persona/brush_copy.py)
tools/build_store.sh <work_dir>
```

Copy, offer, tabs, FAQ, the shelf card and the collections live in `tools/persona/brush_copy.py`.

`node tools/theme-qa/offer-e2e.mjs https://skinofab.29next.store 34 /catalogue/adaptive-peptide-foundation_14/ shots/`
checks the brush without placing an order:

- each bundle: its variant and price, a one-time line, the drawer, and checkout for the 2-brush bundle;
- the drawer's 1 → 2 brushes upgrade;
- the page: section order, no "Solena", the tabs, the FAQ, the prices, no stars or review wall without reviews;
- the homepage shelf card and the menu links.
