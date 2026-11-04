#!/bin/bash
# Publish the funnels' Campaign Page Kit project (campaigns/skinofab) to its own repo, which a static host builds
# (Netlify, Vercel or Cloudflare Pages: campaigns/skinofab/README.md). The folder goes with its history
# (git subtree split), so the funnels repo's main is always this repo's committed state of the folder, nothing else.
#
# usage: bash tools/funnel/publish_funnels.sh            (FUNNELS_REMOTE / FUNNELS_BRANCH override the defaults)
#
# Run it after the full build and its checks pass and campaigns/skinofab is committed: it refuses uncommitted changes
# in the folder, so what the host builds is always a commit you can find here.
set -euo pipefail
REMOTE=${FUNNELS_REMOTE:-https://github.com/Claude-rx/skinofab-funnels.git}
BRANCH=${FUNNELS_BRANCH:-main}
cd "$(git rev-parse --show-toplevel)"
if ! git diff --quiet HEAD -- campaigns/skinofab || [ -n "$(git ls-files --others --exclude-standard campaigns/skinofab)" ]; then
  echo "publish_funnels: campaigns/skinofab has uncommitted changes: commit them first" >&2; exit 1
fi
split=$(git subtree split --prefix=campaigns/skinofab HEAD 2>/dev/null | tail -1)
echo "publish_funnels: campaigns/skinofab at $(git rev-parse --short HEAD) is $split"
for i in 1 2 3 4; do
  git push "$REMOTE" "$split:refs/heads/$BRANCH" && { echo "publish_funnels: pushed to $REMOTE $BRANCH"; exit 0; }
  sleep $((2 ** i))
done
echo "publish_funnels: the push failed" >&2; exit 1
