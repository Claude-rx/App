#!/usr/bin/env bash
# Refresh the vendored Supliful agent skill in .claude/skills/supliful-api from upstream:
#   https://github.com/Supliful/agent-skills  (same content as `npx skills add supliful/agent-skills`)
# Usage: scripts/update-supliful-skill.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$ROOT/.claude/skills/supliful-api"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

git clone -q --depth 1 https://github.com/Supliful/agent-skills.git "$WORK/src"
COMMIT="$(git -C "$WORK/src" rev-parse HEAD)"
rm -rf "$TARGET"
mkdir -p "$TARGET"
cp -r "$WORK/src/skills/supliful-api/." "$TARGET/"
cp "$WORK/src/LICENSE" "$TARGET/LICENSE"
printf 'Vendored from https://github.com/Supliful/agent-skills (skills/supliful-api), MIT.\nCommit: %s, fetched %s.\nUpdate: scripts/update-supliful-skill.sh. Do not edit here: upstream overwrites PRs.\n' "$COMMIT" "$(date -u +%F)" > "$TARGET/UPSTREAM.md"
echo "supliful-api skill updated to $COMMIT. Review: git diff -- .claude/skills/supliful-api"
