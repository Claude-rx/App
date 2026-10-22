# Product page reviews

The product page has a review wall after the FAQ: the average, the 5 to 1 star breakdown, filters (with photos, by
star), sorting, "Show more", photo thumbnails with a lightbox, and **Write a review**. It shows two sources, both real:

1. **NEXT reviews.** Shoppers write them with the store's own form (`/catalogue/adaptive-peptide-foundation_14/reviews/add/`).
   They appear once approved in the dashboard (Catalogue → Reviews).
2. **Imported reviews of the same formula** from the Smooche store, word for word, with their own ratings, dates
   and verified flags.

While there are no reviews the wall stays hidden.

## Importing the Smooche reviews

1. In the Smooche Shopify admin, export the reviews from the review app (Loox: Reviews → Export; Judge.me, Okendo,
   Yotpo and Stamped CSV exports work too).
2. Run the importer on the export (the work dir is the one `tools/build_store.sh` uses):

   ```bash
   python3 -I tools/reviews/import_reviews.py smooche-reviews.csv <work_dir> --download-photos
   ```

   It keeps only the foundation's published reviews, shows names as "First L.", and leaves out any review that
   names another brand (`--exclude-text smooche`, the default) instead of editing it. It prints how many were
   kept and skipped, and the average and distribution.
3. Photos: open `<work_dir>/reviews/photos-sheet.jpg` and list, one id per line, the photos to publish in
   `<work_dir>/reviews/photos-approved.txt`: skin, results, or the SKINOFAB bottle. Leave out any photo showing the
   old bottle; customer photos are never edited. Run step 2 again.
4. Rebuild and push (`tools/build_store.sh <work_dir>`, then push the changed theme files).

The imported reviews ship as one small data script that loads only when a shopper scrolls near the wall, so
hundreds of reviews cost nothing on page load.
