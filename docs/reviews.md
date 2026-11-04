# Product page reviews

The product page has a review wall after the FAQ: the average, the 5 to 1 star breakdown, filters (with photos, by
star), sorting, "Show more", photo thumbnails with a lightbox, and **Write a review**. It shows two sources, both real:

1. **NEXT reviews.** Shoppers write them with the store's own form (`/catalogue/adaptive-peptide-foundation_14/reviews/add/`).
   They appear once approved in the dashboard (Catalogue → Reviews).
2. **Imported reviews of the same formula** from the Smooche store, word for word, with their own ratings, dates
   and verified flags.

**Write a review** opens NEXT's form page, whose breadcrumb is Home / Shop / product (not the product's first NEXT
category), with no price (the product page's refill and pack prices are what it sells at) and, while it has no NEXT
reviews yet, a link back to the product page's wall. The link has no `href` until the wall's script sets it: the
theme cancels clicks on every `a[href="#"]` it finds when the page loads.

The cart drawer quotes one review, an imported verified one the product page shows word for word (Lora Z., 65), and
only while the foundation is in the bag (Theme settings > Cart Drawer > Review is about).

While there are no reviews the wall stays hidden. The Lymphatic Brush's page has the same wall (and its stars under
the buyers line appear with the first review); its imports go to `<work_dir>/reviews-brush`.

## Importing the Smooche reviews

1. In the Smooche Shopify admin, export the reviews from the review app (Loox: Reviews → Export; Judge.me, Okendo,
   Yotpo and Stamped CSV exports work too).
2. Run the importer on the export (the work dir is the one `tools/build_store.sh` uses):

   ```bash
   python3 -I tools/reviews/import_reviews.py smooche-reviews.csv <work_dir> --download-photos
   ```

   It keeps only the foundation's published reviews, shows names as "First L.", and leaves out any review that
   names the old brand in any spelling (Smooch, Smooche, Smoochie), its support team, SPF or sunscreen
   (`EXCLUDE_DEFAULT`; `--exclude-text` replaces it) instead of editing it. It prints how many were
   kept and skipped, and the average and distribution.
3. Photos: open `<work_dir>/reviews/photos-sheet.jpg` and list, one id per line, the photos to publish in
   `<work_dir>/reviews/photos-approved.txt`: skin, results, or the SKINOFAB bottle. Leave out any photo showing the
   old bottle; customer photos are never edited. Run step 2 again.
4. Rebuild and push (`tools/build_store.sh <work_dir>`, then push the changed theme files).

What the page shows of them: up to 1,000 reviews (every photo review, every review under 4 stars, then the rest), and
the totals of all of them. A review about something this page does not sell or say stays out of that list, whatever
its rating, and still counts in the totals (`apply_persona.OFF_TOPIC`): the free brush that came with the earlier
store's orders ("the brush is easy to use"), an SPF the formula does not have ("SF 15"), and other brands by name.
Of 9,855 imported reviews that is 213 (161 five-star, 52 four-star); none is edited. The testimonial cards
(`apf_copy.TESTIMONIALS`) must pass the same rule, or the build stops.

## The Lymphatic Brush

Two real sources can fill its page; both appear in the same green Trustpilot-style boxes as the foundation's.

1. **Real Solena buyers of this brush** (the owner's sister store). Export the reviews from Solena's dashboard
   (Judge.me: Reviews → Export) and import only verified buyers from the day the brush went on sale there:

   ```bash
   python3 -I tools/reviews/import_reviews.py solena-brush-export.csv <work_dir> --product the-lymphatic-brush \
     --exclude-text solena --verified-only --since 2026-03-02 --note "of the same brush from our sister store" \
     --out reviews-brush --download-photos
   ```

   The wall says "Includes N verified reviews of the same brush from our sister store", the stars appear next to
   the title, and the "No reviews yet" box hides itself. As of 23 Oct 2026 the public widget has 152 reviews, all
   unverified and all dated before 2 Mar 2026, so this keeps none of them; only a dashboard export with real orders
   can add some.
2. **The owner's own Amazon listing of this brush.** Only its totals, never review text (Amazon's reviews belong to
   their writers and to Amazon):

   ```bash
   node tools/reviews/amazon_rating.mjs <ASIN or listing URL> <work_dir>/amazon-brush.json --brand "<your brand on Amazon>"
   ```

   It writes the file only when the listing's brand is yours (another seller's brush is a different product, and
   its ratings are not this brush's). The page then shows "Rated on Amazon: 4.6 out of 5 from N Amazon ratings of
   this brush, sold there by <brand>", the date it was checked and a link to the listing, plus a line in the buy
   box. Run it again to refresh the numbers.

Rebuild and push after either (`tools/build_store.sh <work_dir>`). A store's published Judge.me reviews can also
be read without the dashboard export: `python3 -I tools/reviews/fetch_judgeme.py <shop>.myshopify.com <product id> out.csv`
writes the same columns. Check where the reviews come from before importing them. Solena's brush reviews were not
imported: every one predates the product and the store, and none is a verified buyer
([lymphatic-brush.md](lymphatic-brush.md)).

The imported reviews ship as one small data script that loads only when a shopper scrolls near the wall, so
hundreds of reviews cost nothing on page load.

## Trustpilot's look and colours, everywhere (the owner, 2 Nov 2026)

"Keep all the reviews Trustpilot style with exact Trustpilot colors." Every rating on the store and on both funnels
is a row of white stars in square boxes, lit in Trustpilot's colour for the rating, with no review site's name or logo
(the reviews still say they are ours, "from our earlier store"):

| Rating | Lit boxes | Rule |
|---|---|---|
| 5, or an average of 4.3 and up | `#00B67A` | `apf_copy.tp_tier()`, `sf-stars.html` (no class) |
| 4, or 3.8 to 4.2 | `#73CF11` | `.sfr-tp--t4` / `.sf-tp-t4` / `i.t4` |
| 3, or 2.8 to 3.7 | `#FFCE00` | `t3` |
| 2, or 1.8 to 2.7 | `#FF8622` | `t2` |
| 1 | `#FF3722` | `t1` |
| unlit | `#DCDCE6` | the empty boxes, the rating bars' track |

A fraction lights part of a box (4.8: four boxes and 80 % of the fifth). The 5-to-1 rating bars take their row's
colour. Where each lives:

- **Store** (`tools/persona/apf_copy.py`, `apply_persona.py`, `tools/theme-build/build_theme.py`,
  `static/skinofab-cart-drawer.js`): the review wall and its cards, the review strip, the title rating
  (`rating_block`), the buy box's rating (`brush_rating`, recoloured when NEXT's own reviews move the average), the
  testimonial carousel, the sticky bar's star, the shelf cards and the homepage hero (`shelf_tp`), NEXT's review pages
  and the write-a-review picker (grey boxes; the chosen score and those under it lit in its colour), the cart drawer's
  quote, and the store's other pages (`tp_legacy()`: the quiz, the advertorials, the VIP and tracking pages).
- **Funnels** (`campaigns/skinofab/src/*/_includes/sf-stars.html`, `sf-apf.css`, `sf-funnel.css`,
  `checkout-brand.css`): every star row through `sf-stars.html` (a 4-star review: four `#73CF11` boxes and an empty
  one); the stick funnel's gold text stars are gone. **Kept by the owner's earlier decision:** the APF sales page's
  hero rating and its checkout's top rating stay plain black, centred stars (29 Oct 2026).
- **Gates:** `check_apf.py` and `check_funnel.py` fail a funnel CSS without the six colours or with the old greys, a
  row of text stars, a hand-drawn half star, a 4-star review not in four light-green boxes, or a rating bar without its
  row (`data-s`).
