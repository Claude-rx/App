# SoFyre — Rodent Repellent Pouches page export

Source: https://sofyre.com/products/mouse-repellent-pouches (captured 2026-11-09, desktop 1440px)

| File | What it is |
|---|---|
| `mouse-repellent-pouches.single-file.html` | **Everything in one file** (16 MB): HTML + all CSS, fonts, images as data URIs. Works offline. |
| `offline/index.html` + `offline/assets/` | Same page as a folder: HTML + 250 local assets (images, fonts, CSS). Easiest to edit. |
| `offline/copy.md` | All page copy as text (incl. collapsed accordion/FAQ answers) + every image's alt text and source URL. |
| `mouse-repellent-pouches.rendered.html` | Rendered DOM, assets still pointing at sofyre.com. |
| `mouse-repellent-pouches.raw.html` | Original server HTML, untouched. |
| `*.png` | Full-page screenshots of the live page. |

Notes:
- Static snapshot: scripts, trackers and the "Mystery Discount" popup are removed. Layout and content match the live page;
  carousels, tabs and accordions are frozen in their default state (accordion text is still in the HTML).
- GemPages ships section CSS as `type="text/disabled-css"`; the exporter enables it so every section renders without JS.

Re-run:
```bash
node tools/full.js "$PWD/offline"                                   # capture + download assets
python3 tools/inline.py offline mouse-repellent-pouches.single-file.html   # build single file
node tools/verify.js "$PWD/offline/index.html" /tmp/check.png        # offline check (blocks all network)
```
