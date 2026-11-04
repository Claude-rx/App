#!/usr/bin/env bash
# Live guard: every funnel page on try.skinofab.com must load an AXON adapter that sends user_data on purchase
# a numeric item_category_id and a .jpg/.png image_url on every item. A funnel deploy that regenerates the theme from stale sources
# would silently undo both (AppLovin then flags purchase as an error). Exit 1 on any page that regressed.
# Usage: tools/funnel/check_live_axon.sh [base-url]        (default https://try.skinofab.com)
set -uo pipefail
BASE="${1:-https://try.skinofab.com}"
PAGES=(adaptive-foundation-offer foundation-checkout foundation-offer-1 foundation-offer-2 foundation-offer-2b lymphatic-brush-offer foundation-thank-you foundation-stick-offer stick-checkout stick-special-1 stick-special-2 stick-special-3 stick-special-4 stick-thank-you
       trial-checkout trial-offer-1 trial-offer-2 trial-offer-2b trial-brush-offer trial-brush-offer-b trial-thank-you)
bad=0
# The flash trial's product page is a store page: its own script sends view_item/add_to_cart with a full item.
pdp=$(curl -fsSL -m 30 "$BASE/adaptive-foundation-trial/?axon_guard=$RANDOM") || { echo "FAIL adaptive-foundation-trial: page did not load"; bad=1; }
if [ -n "${pdp:-}" ]; then
  if grep -qE 'item_variant_id: c\.getAttribute\("data-item-variant"\), item_category_id: [0-9]+, image_url: "https://[^"]+\.(png|jpe?g)"' <<<"$pdp" \
     && grep -qE 'data-item-sku="SKF-[A-Z0-9-]+" data-item-variant="[0-9]+"' <<<"$pdp"; then echo "ok   adaptive-foundation-trial"
  else echo "FAIL adaptive-foundation-trial: product page item lacks variant, category or .jpg image"; bad=1; fi
fi
for p in "${PAGES[@]}"; do
  html=$(curl -fsSL -m 30 "$BASE/$p/?axon_guard=$RANDOM") || { echo "FAIL $p: page did not load"; bad=1; continue; }
  url=$(grep -oE 'https://[^"]+-axon-adapter-[^"]+' <<<"$html" | head -1)
  [ -n "$url" ] || { echo "FAIL $p: no AXON adapter on the page"; bad=1; continue; }
  js=$(curl -fsSL -m 30 "$url") || { echo "FAIL $p: adapter did not load ($url)"; bad=1; continue; }
  missing=()
  grep -q 'params.user_data = user' <<<"$js" || missing+=("user_data on purchase")
  grep -q "'sf-' + hash53(" <<<"$js" || missing+=("user_id from email")
  grep -q 'categoryId(it.item_category) || fallbackCategoryId' <<<"$js" || missing+=("numeric item_category_id")
  grep -q 'IMAGE_BY_SKU_FAMILY' <<<"$js" || missing+=(".jpg image_url for every item")
  grep -q 'params.payment_type = paymentType(' <<<"$js" || missing+=("payment_type enum")
  if [ ${#missing[@]} -gt 0 ]; then joined=$(printf '%s, ' "${missing[@]}"); echo "FAIL $p: adapter lacks ${joined%, } — ${url##*/}"; bad=1
  else echo "ok   $p"; fi
done
exit $bad
