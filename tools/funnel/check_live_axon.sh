#!/usr/bin/env bash
# Live guard: every funnel page on try.skinofab.com must load an AXON adapter that sends user_data on purchase
# a numeric item_category_id and a .jpg/.png image_url on every item. A funnel deploy that regenerates the theme from stale sources
# would silently undo both (AppLovin then flags purchase as an error). Exit 1 on any page that regressed.
# Usage: tools/funnel/check_live_axon.sh [base-url]        (default https://try.skinofab.com)
set -uo pipefail
BASE="${1:-https://try.skinofab.com}"
PAGES=(adaptive-foundation-offer foundation-checkout foundation-thank-you foundation-stick-offer stick-checkout stick-thank-you)
bad=0
for p in "${PAGES[@]}"; do
  html=$(curl -fsSL -m 30 "$BASE/$p/?axon_guard=$RANDOM") || { echo "FAIL $p: page did not load"; bad=1; continue; }
  url=$(grep -oE 'https://[^"]+-axon-adapter-[^"]+' <<<"$html" | head -1)
  [ -n "$url" ] || { echo "FAIL $p: no AXON adapter on the page"; bad=1; continue; }
  js=$(curl -fsSL -m 30 "$url") || { echo "FAIL $p: adapter did not load ($url)"; bad=1; continue; }
  missing=()
  grep -q 'params.user_data = user' <<<"$js" || missing+=("user_data on purchase")
  grep -q 'categoryId(it.item_category) || fallbackCategoryId' <<<"$js" || missing+=("numeric item_category_id")
  grep -q 'IMAGE_BY_VARIANT' <<<"$js" || missing+=(".jpg image_url")
  if [ ${#missing[@]} -gt 0 ]; then joined=$(printf '%s, ' "${missing[@]}"); echo "FAIL $p: adapter lacks ${joined%, } — ${url##*/}"; bad=1
  else echo "ok   $p"; fi
done
exit $bad
