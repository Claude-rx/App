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
# Output: skinofab-theme/ (ntk push from there), skinofab-handoff/, theme-build-report.json, theme-optimize-report.json,
#   docs/checkout-policies/ (the store policies to paste into NEXT: docs/company-details.md)
set -euo pipefail
W=$(cd "$1" && pwd)
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

python3 -I tools/persona/apply_persona.py "$W/rel3/skinofab-site" "$W/rel4/skinofab-site" "$W/ccf-offers.json" "$W/persona-img2" | tail -3
python3 -I tools/persona/policy_texts.py "$W/rel4/skinofab-site" docs/checkout-policies   # paste-ready checkout policies
python3 -I tools/rebrand/fresh_alpha_names.py "$W/rb/groups.json" "$W/rel2/skinofab-site" "$W/rel4/skinofab-site" "$W/alpha-renames2.json"
python3 -I tools/persona/apf_pages.py "$W/rel4/skinofab-site" tools/persona/apf-images.json --classic | tail -2
SF_CATALOG="$W/catalog-rb.json" python3 -I tools/theme-build/build_theme.py "$W/rel4/skinofab-site" "$W/spark" skinofab-theme skinofab-handoff
python3 -I tools/theme-build/optimize_theme.py skinofab-theme

cd skinofab-theme
python3 scripts/check-dtl.py --require
python3 scripts/check-templates.py
python3 scripts/check-theme-contract.py
python3 scripts/check-settings-parity.py
python3 -I ../tools/theme-qa/video_brand_gate.py .
