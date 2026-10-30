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
