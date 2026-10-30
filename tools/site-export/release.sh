#!/usr/bin/env bash
# Full release: build -> optimize images/videos -> README -> QA (desktop + mobile) -> zip.
# usage: release.sh <out_dir> <zip_path>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="$1"; ZIP="$2"
python3 -I "$HERE/build.py" "$OUT" "$HERE/skinofab.svg" > "$OUT.build.log" 2>&1
grep -E "^pages" "$OUT.build.log"
python3 -I "$HERE/optimize.py" "$OUT"
"$HERE/optimize_video.sh" "$OUT"
cp "$HERE/SITE_README.md" "$OUT/README.md"
node "$HERE/verify.mjs" "$OUT" > "$OUT.qa.log" 2>&1 || true; tail -1 "$OUT.qa.log"
node "$HERE/verify.mjs" "$OUT" --mobile > "$OUT.qa-mobile.log" 2>&1 || true; tail -1 "$OUT.qa-mobile.log"
rm -f "$ZIP"; (cd "$(dirname "$OUT")" && zip -qr -9 "$ZIP" "$(basename "$OUT")")
ls -lh "$ZIP"
