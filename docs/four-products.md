# Five products, nothing else

The store sells SKINOFAB's five products and nothing else (the stick, added on 26 Oct 2026: `docs/foundation-stick.md`):

| Product | NEXT id | Page |
|---|---|---|
| Adaptive Peptide Foundation | 14 | `/catalogue/adaptive-peptide-foundation_14/` |
| The Lymphatic Brush | 169 | `/catalogue/the-lymphatic-brush_169/` |
| PDRN Plumping Balm | 202 | `/catalogue/pdrn-plumping-balm_202/` |
| EGF + NAD+ Firming Serum | 206 | `/catalogue/egf-nad-firming-serum_206/` |
| Adaptive Foundation Stick | 235 | `/catalogue/adaptive-foundation-stick_235/` |

Every other product the old store carried (lip plumpers, lip stains and glosses, brow and lash products, the
reverse-time serum, the lifting mask, the under-eye patches, the gua sha and face roller, the old bundles, the
blender and the gift card, the hidden foundation duo and complexion set: 28 in all) is deleted from NEXT. So are the
15 pages that sold only those (the brow, lip and collagen-mask advertorials, the shade and plumper quizzes, the
old bundle builder and checkout funnel, the how-to guide for the old range). The 9 categories they left empty (Lips,
Lashes, Brows, Bundles, Serums, Homepage, Canal Products, Stick & Stay Peel-off Lip Stain, Example Category) hold
nothing and no page links to them; NEXT's API cannot delete a category (405), so they go from the dashboard:
Catalogue → Categories.

## In NEXT

`tools/persona/prune_catalog.py` keeps products 14, 169, 202, 206 and 235 with their variants, and deletes the rest. Every
record it deletes is saved first, in full, to the backup file it is given; the one from 25 Oct 2026 is
`docs/catalog-backup/2026-10-25-removed-products-pages.json` (28 products with their variants, prices and images, 15
pages, 9 categories), so any one can be recreated from it.

```bash
NEXT_API_TOKEN=... python3 -I tools/persona/prune_catalog.py skinofab <work_dir>/catalog/prune-backup.json           # the plan
NEXT_API_TOKEN=... python3 -I tools/persona/prune_catalog.py skinofab <work_dir>/catalog/prune-backup.json --apply   # do it
```

### Automatic Refills (subscriptions)

Every product but The Lymphatic Brush is sold with Automatic Refills on by default (the owner's brief of 26 Oct
2026); one-time purchase stays a choice on the cart page. Refills cost 20% less than the one-time price, and each pack
ships again when it runs out:

| Product | Packs: one-time → refill, every | NEXT |
|---|---|---|
| Adaptive Peptide Foundation (14) | 1 $47 → $37 · 2 + gifts $57 → $47, every 28 days | on, 28 days |
| PDRN Plumping Balm (202) | 1 $24.95 → $19.95, 28 days · 2 $39.95 → $31.95, 56 · 3 $49.90 → $39.90, 84 | on, 28/56/84 days |
| EGF + NAD+ Firming Serum (206) | 1 $34.95 → $27.95, 56 days · 2 $59.95 → $47.95, 112 · 3 $69.90 → $55.90, 168 | on, 56/112/168 days |
| Adaptive Foundation Stick (235) | 1 $39 → $31, 28 days · 2 $59 → $47, 56 · 3 $78 → $62, 84 | on, 28/56/84 days |
| The Lymphatic Brush (169) | one-time only (it lasts) | off |

The prices and days live in each product's `*_copy.py` (`BUNDLES[*]['refill']`, `['every']`, `REFILL`);
`setup_brush_offers.py skinofab <work> <module>` writes them to NEXT (`enable_subscription`, `interval`,
`interval_counts`, each variant's subscription price) and the build puts them on the page, in the cart drawer and in
the subscription terms (`policy_texts.py`). The days are estimates of how long a pack lasts: the owner to confirm.

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
- the menus drop Accessories and Sale; the footer's Shop column lists the five products;
- FAQ answers about the other products go, and the brand's own words that named them (the About page, the
  disclaimer, the retailer post) now name the four.

The build fails if any page still links to another product. `build_theme.py` only writes settings for products and
collections the theme still has.

NEXT's Theme Kit cannot delete files from a theme, so the old templates stay on the server unused: no product or page
uses them once the products and pages are deleted.
