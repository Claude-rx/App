#!/usr/bin/env bash
# Refresh the vendored Next Commerce skills in .claude/skills from upstream:
#   https://github.com/NextCommerceCo/skills        (store ops, themes, campaigns)
#   @nextcommerce/campaigns-os on npm                (campaign build lifecycle)
# Usage: scripts/update-nextcommerce-skills.sh [campaigns-os-version]   (default: npm latest)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$ROOT/.claude/skills"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

command -v rsync >/dev/null || { echo "rsync is required (apt-get install rsync / brew install rsync)" >&2; exit 1; }
mkdir -p "$TARGET"

echo "== NextCommerceCo/skills =="
git clone -q --depth 1 https://github.com/NextCommerceCo/skills.git "$WORK/skills"
"$WORK/skills/skills.sh" install --target "$TARGET" all

echo "== @nextcommerce/campaigns-os =="
VERSION="${1:-$(npm view @nextcommerce/campaigns-os version)}"
(cd "$WORK" && npm init -y >/dev/null && npm i -s --save-exact --omit=optional "@nextcommerce/campaigns-os@$VERSION")
(cd "$WORK" && npx --no-install campaigns-os install-skills --target "$TARGET")

echo "Done (campaigns-os $VERSION). Restart the agent session to load updated skills."
