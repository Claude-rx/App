# Funnel 2 (parked): Natural GLP-1 weight-loss supplement

**Not built, not served.** Berberine and the Natural GLP-1 weight-loss supplement are two different products. This folder
keeps the first sales page, which positioned Berberine as natural GLP-1 support for weight loss, as the starting point
for funnel 2:

| File | What |
|---|---|
| `copy-deck.md`, `persona-weight-segment.md` | the copy deck and persona as delivered (they name Berberine as the ingredient; rework for product 2's formula) |
| `sales-page.source.html`, `img/` | the delivered sales page and its images |
| `sales-page.page-kit.html`, `sales.css` | the Page Kit conversion in the mediclab.us brand (`tools/mediclab/build_sales_page.py`) |

To build funnel 2 we need product 2: name, SKU, price and plan, Supplement Facts / label, images, and the claims it may
make. Then: import it, plan its campaign (`next-campaigns-create`), give it its own Page Kit campaign and store pages.
Known fix to carry over: the two offer blocks shared one radio group (`name="offer"`), so the top block loaded with no
selection; the Berberine page uses one group per block.
