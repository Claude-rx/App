#!/usr/bin/env bash
# Install the Clipcat CLI for Claude Code (OpenClaw's auto-install does not run here).
# Usage: install-cli.sh [version]   (default: the version pinned in SKILL.md)
# Env:   CLIPCAT_INSTALL_DIR (default ~/.local/bin), CLIPCAT_API_KEY (optional, configures the CLI)
set -euo pipefail

VERSION="${1:-1.0.24}"
DEST="${CLIPCAT_INSTALL_DIR:-$HOME/.local/bin}"
BASE="https://static.clipcat.ai/public/cli/v${VERSION}"

case "$(uname -s)" in
  Linux)  os=linux ;;
  Darwin) os=darwin ;;
  *) echo "clipcat: unsupported OS $(uname -s); on Windows download ${BASE}/clipcat_windows_amd64.zip manually" >&2; exit 1 ;;
esac
case "$(uname -m)" in
  x86_64|amd64)  arch=amd64 ;;
  arm64|aarch64) arch=arm64 ;;
  *) echo "clipcat: unsupported arch $(uname -m)" >&2; exit 1 ;;
esac

url="${BASE}/clipcat_${os}_${arch}.tar.gz"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

echo "Downloading ${url}"
code="$(curl -sSL -o "$tmp/clipcat.tgz" -w '%{http_code}' "$url" || true)"
if [ "$code" != "200" ]; then
  echo "clipcat: download failed (HTTP ${code}). Check https://clipcat.ai for the current CLI version and rerun: $0 <version>" >&2
  exit 2
fi

tar -xzf "$tmp/clipcat.tgz" -C "$tmp"
bin="$(find "$tmp" -type f -name clipcat | head -n1)"
[ -n "$bin" ] || { echo "clipcat: archive has no clipcat binary" >&2; exit 3; }

mkdir -p "$DEST"
install -m 0755 "$bin" "$DEST/clipcat"
echo "Installed to $DEST/clipcat"
case ":$PATH:" in *":$DEST:"*) ;; *) echo "Note: add $DEST to PATH" ;; esac

if [ -n "${CLIPCAT_API_KEY:-}" ]; then
  "$DEST/clipcat" config --api-key "$CLIPCAT_API_KEY" --base-url https://clipcat.ai
  echo "Configured API key from CLIPCAT_API_KEY"
else
  echo "Next: clipcat config --api-key <key> --base-url https://clipcat.ai  (key: https://clipcat.ai/workspace?modal=settings&tab=apikeys)"
fi
