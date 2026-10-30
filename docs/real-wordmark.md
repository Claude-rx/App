# SKINOFAB's real wordmark on every product

Every SKINOFAB bottle, stick and case in the store's photos carries the brand's own wordmark: the owner's
vector file, `brand/logo/skinofab-wordmark.svg`. Before, most of them didn't:

| Product | What was printed | Now |
|---|---|---|
| Adaptive Peptide Foundation | a stand-in serif (Trajan-like) on the product-sheet renders, the composites and every photo made from them; "SKINOFAS" on two AI photos | the SVG wordmark, found and replaced on 6 renders and composites and 16 page photos (all their widths) |
| PDRN Plumping Balm | AI-drawn wordmarks, a different serif on each photo, spaced out on one ("S K I N O F A B") | the SVG wordmark on all 14 photos of the stick |
| EGF + NAD+ Firming Serum | the real wordmark, but very large and stretched by the wrap, on a round-shouldered bottle and a carton | the foundation's bottle and label: a straight matte black cylinder with a full-width cap and a dropper, the wordmark set vertically at the foundation's size, the product lines under it; no carton, like the other products |
| Lymphatic Brush | already the real wordmark on the case (the checkout logo file) | unchanged; the checkout logo is now generated from the SVG |

## The files

`tools/persona/brand_logo.py` makes every logo file from the SVG (rendered in Chromium, exact to the vector):

| File | What it is |
|---|---|
| `brand/logo/skinofab-wordmark-black.png` | black on transparent, 3902 px wide: what `label_composite.py` prints on the products |
| `brand/checkout/skinofab-logo-1200.png` | the checkout and email logo, 1200 × 198 |
| `brand/checkout/skinofab-icon-512.png` | the favicon and checkout tab icon: the wordmark's own S, white on a black rounded square |

## How a print is replaced

`tools/persona/relabel_bottles.py` says where each bottle is; `tools/persona/label_composite.py` does the work:

1. **Find the old print.** Either automatically on the bottle (`composite(relabel=True)`: the bottle's black body,
   the bright strokes on it, grouped into the label's column), or in a box drawn around it (`measure_print`: the
   strokes that are brighter than the bottle around them, ringed by black, inside the box; their main axis is the
   print's line, and a point at the first letter says which way it reads). Skin (a fingertip at the edge), the white
   backdrop, a white sleeve, grey hair and an eye's catchlight are left out.
2. **Erase it.** The letters are inpainted from the black around them; the small product lines under the wordmark
   ("ADAPTIVE PEPTIDE FOUNDATION", "PLUMPING BALM") stay.
3. **Print the real one.** The SVG wordmark at the old print's place, length and angle, in the old print's own ink
   colour (wrapped around the cylinder on upright bottles), softened to the photo's sharpness; fingers in front of it
   stay in front.

Every result was checked by eye against the original: `docs/screenshots/wordmark-before-after.jpg` (each pair is
before | after: the 16 foundation page photos, the 14 balm photos, two renders). The live shelf with the four cards at
one size: `docs/screenshots/shelf-even-cards.png`.

## Where it runs

- **Foundation renders and composites** (`01-front`, `02-three-quarter-left`, `03-three-quarter-right`,
  `composites/two-bottles`, `duo-square`, `label-detail`): in place, `python3 -I tools/persona/relabel_bottles.py renders`.
  The originals are kept in `brand/adaptive-peptide-foundation/source/renders/` and every run starts from them. The
  gallery's "vs. others" board and the NEXT gallery (`next/`) are made from them: `product_photos.py foundation`.
- **Foundation page photos** (the hero, the packshots, the women holding the bottle, the mega pack, the "difference"
  close-up …): at build time, `apply_persona.relabel_bottles_on_pages()` after the white backdrops. Each photo's
  largest copy at its reference size is relabelled and every other width (the srcset, the thumbnails) is that result
  resized, so all sizes agree. New names `<stem>-l<hash>` (NEXT's CDN caches by name); cached in
  `<work_dir>/relabel-cache`.
- **Balm photos**: `product_photos.py balm` relabels each source photo of the stick first
  (`relabel_bottles.BALM` → `brand/pdrn-balm/labelled/`), then lays out the gallery; the page's section crops take
  the labelled photo when there is one (`apply_persona.twin_context`).
- **Serum photos**: `product_photos.py serum` prints the label on the blank bottles (`SERUM_LABELS`).

```bash
python3 -I tools/persona/brand_logo.py                 # logo files from the SVG
python3 -I tools/persona/relabel_bottles.py renders    # foundation renders and composites
python3 -I tools/persona/product_photos.py foundation balm serum
python3 -I tools/persona/relabel_bottles.py sheet <work_dir>/rel4/skinofab-site <out_dir>   # before/after of every page photo
tools/build_store.sh <work_dir>                        # page photos, then the theme
```

**A small PDRN line set bold** (`label_fix.bold_line_rot`, the `'boldrot'` op in `relabel_bottles.SITE`): where a
photo shows the bottle so small that its own PDRN line, a few pixels tall, reads PORN, the line is erased and set
again in a heavy weight, along the label's slant. The foundation gallery's photos `21_`, `22_`, `24_`, `412bfd2c` and
the comparison card `8_87ca3242` (review 5) carry one, as do the packshot, `2_221c6006` and the "Soft on fine lines"
poster. Homepage photos get the same from `home_images.py` (`held()` sets `--pdrn bold`; the one-shade photo, the
formulas photo and the phenomenon cards `--pdrn xl` or a bold line), and so does the empty cart's bottle
(`tools/theme-build/static/skinofab-cart-bottle.png`, at 3x its 76 px width).

A new photo of a foundation bottle with the old print: add its file-name prefix, reference size and bottle to
`relabel_bottles.SITE` (`'box'` with a box around the print and a point at its first letter is the simplest), run
`sheet`, check the crop, rebuild.

## Not covered

Nothing on sale: the older products in the old design's pink packaging are no longer in the store
(`docs/four-products.md`).

## Formulated in Korea

Every product says where it is formulated, never "made in Korea": the buy box's line on the foundation, balm and serum
pages (`ccf_copy.ORIGIN`: "🇰🇷 Formulated in Korea · Advanced K-beauty formula"), the flag badge on the gallery photos
("Formulated in Korea / Advanced formula": `label_composite.ORIGIN_LINES`, drawn by `product_photos.korea_badge` and,
on the foundation's packshot, rewritten by `relabel_bottles` `'badge'`), the homepage's
formulas section and the advertorials. The brush is a tool, not a formula: it makes no origin claim.
