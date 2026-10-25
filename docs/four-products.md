# Four products, nothing else

The store sells SKINOFAB's four products and nothing else:

| Product | NEXT id | Page |
|---|---|---|
| Adaptive Peptide Foundation | 14 | `/catalogue/adaptive-peptide-foundation_14/` |
| The Lymphatic Brush | 169 | `/catalogue/the-lymphatic-brush_169/` |
| PDRN Plumping Balm | 202 | `/catalogue/pdrn-plumping-balm_202/` |
| EGF + NAD+ Firming Serum | 206 | `/catalogue/egf-nad-firming-serum_206/` |

Every other product the old store carried (lip plumpers, lip stains and glosses, brow and lash products, the
reverse-time serum, the lifting mask, the under-eye patches, the gua sha and face roller, the old bundles, the
blender and the gift card, the hidden foundation duo and complexion set: 28 in all) is deleted from NEXT. So are the
15 pages that sold only those (the brow, lip and collagen-mask advertorials, the shade and plumper quizzes, the
old bundle builder and checkout funnel, the how-to guide for the old range). The 9 categories they left empty (Lips,
Lashes, Brows, Bundles, Serums, Homepage, Canal Products, Stick & Stay Peel-off Lip Stain, Example Category) hold
nothing and no page links to them; NEXT's API cannot delete a category (405), so they go from the dashboard:
Catalogue → Categories.

## In NEXT

`tools/persona/prune_catalog.py` keeps products 14, 169, 202 and 206 with their variants, and deletes the rest. Every
record it deletes is saved first, in full, to the backup file it is given; the one from 25 Oct 2026 is
`docs/catalog-backup/2026-10-25-removed-products-pages.json` (28 products with their variants, prices and images, 15
pages, 9 categories), so any one can be recreated from it.

```bash
NEXT_API_TOKEN=... python3 -I tools/persona/prune_catalog.py skinofab <work_dir>/catalog/prune-backup.json           # the plan
NEXT_API_TOKEN=... python3 -I tools/persona/prune_catalog.py skinofab <work_dir>/catalog/prune-backup.json --apply   # do it
```

The foundation's 2-bottle pack still says it comes with a free blender and a mystery gift: those are part of that
variant ("2 bottles + free gifts"), packed with the order, not products in the store.

## In the theme

`apply_persona.only_our_products()` runs at build time, after the photos are done:

- the other products' pages and data, the 15 pages and the empty collections are deleted from the export, so the
  theme has no template, setting or product picker for them;
- every card, menu item, slide or tile that links to something gone is removed (the largest element around the link
  that holds no link to our products and no prose of its own); a link inside prose is unwrapped, its words stay;
- the homepage drops Shop by Category, Bundle & Save and Essentials, and the shelf's Lips, Lashes and Brows tabs; the
  Reverse-time serum story becomes the EGF + NAD+ Firming Serum's and the lifting mask's "New arrivals" banner the
  PDRN Plumping Balm's (`home_features()`);
- the menus drop Accessories and Sale; the footer's Shop column lists the four products;
- FAQ answers about the other products go, and the brand's own words that named them (the About page, the
  disclaimer, the retailer post) now name the four.

The build fails if any page still links to another product. `build_theme.py` only writes settings for products and
collections the theme still has.

NEXT's Theme Kit cannot delete files from a theme, so the old templates stay on the server unused: no product or page
uses them once the products and pages are deleted.
