---
name: supliful-labels
description: This skill should be used when the user wants to design, create, edit or export supplement label artwork for Supliful private-label products (Mediclab brand), check a label before printing, or change a label's name, claim, count, size or brand details. Trigger phrases include "design a label", "make the label for", "label artwork", "print-ready label", "update the label", "label for Supliful".
---

# Mediclab label artwork for Supliful

Produce print-ready label files that the user uploads in Supliful's label editor. Use the
`supliful_label_specs`, `supliful_refresh_label_copy` and `supliful_render_labels` tools.

## How a label is built

- **Front panel** (from the spec): MEDICLAB wordmark, product name, one-line claim, key-amount pill,
  statement of identity ("Dietary Supplement", plus flavor), net quantity on a colour band.
- **Info panel** (from the product's own Shopify copy, so the label matches the product page):
  directions, warnings ending with "Keep out of reach of children.", the FDA disclaimer, distributor and SKU.
  Serious cautions are never dropped.
- **Supplement Facts zone**: left blank. The guides show where it goes on the proof only. Ask the user to confirm in
  Supliful's editor whether Supliful prints the facts panel and barcode there; if not, the zone must be filled
  before printing.
- Layouts: `wrap` (bottle, gummy bottle, dropper: info | front | facts) and `pouch` (2 pages: front, back).
- Type shrinks to fit. Anything under 6 pt (21 CFR 101.105) or overflowing is reported.

## Workflow

1. `supliful_label_specs` without arguments lists the line, the containers and the workspace folder.
   For a new product, first make sure its copy is in Shopify, then `supliful_refresh_label_copy`, then add a
   spec with `sku` + `set` (name, claim, key, form, net, container, accent; `flavor` optional).
   Keep claims to structure/function language ending in `*`; never claim to treat, cure or prevent a disease.
2. `supliful_render_labels` with `out_dir` set to the user's working folder (and `skus` for a subset).
3. **Look at the proof images** before replying. Check the name fits, nothing overlaps the colour band,
   and the pill reads on one line.
4. Relay every entry of each label's `issues`, in plain language:
   - "net quantity ... is inferred": confirm the count on the Supliful product, then set `net` and `netVerified: true`.
   - "size ... is provisional": take the label dimensions from Supliful's label editor for that product, then
     `supliful_label_specs` with `container` + `set: {widthIn, heightIn, verified: true}`.
   - "distributorAddress is empty": FDA labeling needs the distributor's name and place of business. Set it with `brand`.
   - "info text is ... pt (under 6 pt)": suggest a larger label, a fold-out label, or an outer carton.
5. Hand over the `-print.pdf` files (trim + bleed, no guides) for upload, and the `index.html` contact sheet.
   Recommend a claims and regulatory review before the first print run.

## Edits

Change any front-panel field with `supliful_label_specs` (`sku` + `set`), brand colours or details with
`brand`, then re-render only the affected SKUs. Accent names: metabolic, longevity, sleep, energy, liver,
bone, beauty, women, lymph, circulation, minerals, joint, gut, muscle, hydration, stress, focus, greens,
omega, cellular.

If Playwright is not installed, the render tool writes print-ready HTML instead. Explain the note it
returns (open in Chrome, Print, Save as PDF, margins None, background graphics on).
