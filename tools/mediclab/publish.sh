#!/usr/bin/env bash
# Publish the MedicLab Berberine funnel to theme "MedicLab Funnels" on mediclab.29next.store, served at try.mediclab.us.
# Campaign only: the funnel pages are standalone templates (no storefront layout, cart or scripts); every other
# storefront route goes to the sales page.
#
# usage: tools/mediclab/publish.sh [--dry-run]
# needs: ntk (pip install next-theme-kit) and mediclab-theme/config.yml (ntk init/checkout; gitignored, holds the key)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/campaigns/mediclab" && npm run -s build:static
cd "$ROOT"
python3 -I tools/mediclab/check_funnel.py
FUNNEL=mediclab python3 -I tools/funnel/deploy_theme.py campaigns/mediclab/_site/berberine-glp1 mediclab-theme
python3 -I tools/mediclab/theme.py
if [ "${1:-}" = "--dry-run" ]; then echo "dry run: theme written to mediclab-theme/, nothing pushed"; exit 0; fi
[ -f mediclab-theme/config.yml ] || { echo "mediclab-theme/config.yml missing: run ntk checkout -t <theme id> there"; exit 1; }
# assets carry their content hash in their names, so a changed file is a new name and cached pages keep the old one
cd mediclab-theme && ntk push 2>&1 | grep -E "ERROR|Uploading|100.0%" | tail -3
echo "published: https://try.mediclab.us/glp1-support/ (preview an inactive theme with ?preview_theme=<id>)"
