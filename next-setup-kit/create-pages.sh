#!/usr/bin/env bash
# Create every SKINOFAB page in NEXT with its theme template (Admin API, needs a token with content:write).
# usage: STORE=<subdomain> ADMIN_TOKEN=<token> ./create-pages.sh
set -euo pipefail
: "${STORE:?set STORE to the store subdomain}" "${ADMIN_TOKEN:?set ADMIN_TOKEN}"
cd "$(dirname "$0")"
python3 - <<'PY'
import json, os, urllib.request
store, token = os.environ["STORE"], os.environ["ADMIN_TOKEN"]
for page in json.load(open("pages.json")):
    req = urllib.request.Request(f"https://{store}.29next.store/api/admin/pages/", method="POST",
        data=json.dumps(page).encode(), headers={"Authorization": f"Bearer {token}",
        "X-29next-API-Version": "2024-04-01", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r: print("created", page["slug"], r.status)
    except urllib.error.HTTPError as e:
        print("FAILED", page["slug"], e.code, e.read()[:200])
PY
