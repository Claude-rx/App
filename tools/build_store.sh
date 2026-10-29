#!/usr/bin/env bash
# Build the SKINOFAB theme end to end: persona copy + images -> fresh alpha names -> classic PDP pass -> theme
# build -> speed pass -> gates. Every step is deterministic, so the same inputs give the same theme.
#
# usage: tools/build_store.sh <work_dir>
# <work_dir> holds the build inputs (kept outside git; see tools/persona and tools/rebrand for how they are made):
#   rel2/skinofab-site      rebranded export (before persona)     rb/groups.json          rebrand image groups
#   rel3/skinofab-site      export with the CCF offers applied    alpha-renames2.json     alpha rename map
#   persona-img2/           persona + bottle-swap images           ccf-offers.json         NEXT offer mapping
#   spark/                  Spark starter checkout                 catalog-rb.json         NEXT catalog mapping
#   brush-offers.json       Lymphatic Brush bundle pks (tools/persona/setup_brush_offers.py)
#   brush/media/            Lymphatic Brush videos (tools/persona/brush_assets.py; its images are in brand/lymphatic-brush/)
#   reviews/                imported reviews of the foundation, if any (tools/reviews/import_reviews.py)
# Output: skinofab-theme/ (ntk push from there; with the funnel's templates, tools/funnel/), skinofab-handoff/, theme-build-report.json, theme-optimize-report.json,
#   docs/checkout-policies/ (the store policies to paste into NEXT: docs/company-details.md)
set -euo pipefail
W=$(cd "$1" && pwd)
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

python3 -I tools/persona/apply_persona.py "$W/rel3/skinofab-site" "$W/rel4/skinofab-site" "$W/ccf-offers.json" "$W/persona-img2" | tail -30   # its summary: on a failure, what it missed
python3 -I tools/persona/policy_texts.py "$W/rel4/skinofab-site" docs/checkout-policies   # paste-ready checkout policies
python3 -I tools/rebrand/fresh_alpha_names.py "$W/rb/groups.json" "$W/rel2/skinofab-site" "$W/rel4/skinofab-site" "$W/alpha-renames2.json"
python3 -I tools/persona/apf_pages.py "$W/rel4/skinofab-site" tools/persona/apf-images.json --classic | tail -2
SF_CATALOG="$W/catalog-rb.json" python3 -I tools/theme-build/build_theme.py "$W/rel4/skinofab-site" "$W/spark" skinofab-theme skinofab-handoff
python3 -I tools/theme-build/optimize_theme.py skinofab-theme
# the two funnels (Campaign Page Kit project campaigns/skinofab): the Adaptive Foundation Stick's (docs/stick-funnel.md)
# and the Adaptive Peptide Foundation's (docs/apf-funnel.md): their generated copy, pages and images, one Page Kit build,
# the theme templates the store serves at /<page>/ (each funnel its own slug and asset folder), then each funnel's checks
python3 -I tools/funnel/copy_includes.py && python3 -I tools/funnel/upsell_pages.py > /dev/null
python3 -I tools/funnel/funnel_images.py "$W" > /dev/null
python3 -I tools/funnel/apf/images.py "$W" > /dev/null
python3 -I tools/funnel/apf/offer_pages.py > /dev/null && python3 -I tools/funnel/apf/copy_deck.py > /dev/null
(cd campaigns/skinofab && { [ -d node_modules ] || npm ci --no-audit --no-fund > /dev/null; } && npx --no-install campaign-build > /dev/null 2>&1)
python3 -I tools/funnel/deploy_theme.py campaigns/skinofab/_site/stick-funnel skinofab-theme
python3 -I tools/funnel/check_funnel.py skinofab-theme      # prices, renewal terms, refs, routes, claims
FUNNEL=apf python3 -I tools/funnel/deploy_theme.py campaigns/skinofab/_site/apf-funnel skinofab-theme
python3 -I tools/funnel/apf/check_apf.py skinofab-theme     # prices, refill and one-time terms, refs, routes, claims

cd skinofab-theme
python3 scripts/check-dtl.py --require
python3 scripts/check-templates.py
python3 scripts/check-theme-contract.py
python3 scripts/check-settings-parity.py
python3 -I ../tools/theme-qa/video_brand_gate.py .
