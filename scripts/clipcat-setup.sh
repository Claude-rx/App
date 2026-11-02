#!/usr/bin/env bash
# Clipcat CLI bootstrap for this repo (AI TikTok selling-video generation).
#
# - Installs the clipcat binary to ~/.local/bin if it is missing (macOS/Linux, amd64/arm64).
#   Downloads the binary directly instead of piping a remote installer into bash; the skill
#   itself is committed at .claude/skills/clipcat/SKILL.md, so nothing else is fetched.
# - If CLIPCAT_API_KEY is set (store it as an environment secret, NEVER commit it), saves it
#   to ~/.clipcat/config.toml so the CLI works even where env vars are filtered.
# - Idempotent and non-fatal: safe to run on every session start.
#
# Usage:
#   scripts/clipcat-setup.sh           install + configure (quiet when already set up)
#   scripts/clipcat-setup.sh --check   report status; exit 1 if CLI missing or no key configured
#   scripts/clipcat-setup.sh --update  force re-download of the latest binary
#
# Env overrides: CLIPCAT_INSTALL_DIR (default ~/.local/bin), CLIPCAT_BASE_URL (default https://clipcat.ai),
#                CLIPCAT_DOWNLOAD_BASE (default https://static.clipcat.ai/public/cli/latest)

set -uo pipefail

MODE="${1:-install}"
INSTALL_DIR="${CLIPCAT_INSTALL_DIR:-$HOME/.local/bin}"
BASE_URL="${CLIPCAT_BASE_URL:-https://clipcat.ai}"
DOWNLOAD_BASE="${CLIPCAT_DOWNLOAD_BASE:-https://static.clipcat.ai/public/cli/latest}"
BIN="$INSTALL_DIR/clipcat"

log() { printf '[clipcat-setup] %s\n' "$*"; }

platform_asset() {
  local os arch
  os="$(uname -s)"; arch="$(uname -m)"
  case "$os" in
    Linux)  os=linux ;;
    Darwin) os=darwin ;;
    *) return 1 ;;
  esac
  case "$arch" in
    x86_64|amd64)  arch=amd64 ;;
    aarch64|arm64) arch=arm64 ;;
    *) return 1 ;;
  esac
  printf 'clipcat_%s_%s' "$os" "$arch"
}

install_binary() {
  local asset tmp
  asset="$(platform_asset)" || { log "unsupported platform $(uname -s)/$(uname -m); install manually: https://clipcat.ai/cli"; return 1; }
  command -v curl >/dev/null 2>&1 || { log "curl is required"; return 1; }
  mkdir -p "$INSTALL_DIR"
  tmp="$(mktemp "$INSTALL_DIR/.clipcat.XXXXXX")" || return 1
  if ! curl -fsSL --retry 3 --retry-delay 2 "$DOWNLOAD_BASE/$asset" -o "$tmp" || [ ! -s "$tmp" ]; then
    rm -f "$tmp"; log "download failed: $DOWNLOAD_BASE/$asset"; return 1
  fi
  chmod +x "$tmp"
  if ! "$tmp" version >/dev/null 2>&1; then
    rm -f "$tmp"; log "downloaded binary did not run; aborting"; return 1
  fi
  mv -f "$tmp" "$BIN"
  [ "$(uname -s)" = Darwin ] && xattr -d com.apple.quarantine "$BIN" >/dev/null 2>&1
  log "installed $("$BIN" version 2>/dev/null | tr -d '\n ' | sed -E 's/.*"version":"([^"]+)".*/v\1/') -> $BIN"
}

key_configured() {
  [ -n "${CLIPCAT_API_KEY:-}" ] && return 0
  "$BIN" config --show 2>/dev/null | grep -Eiq '"api_?key"[[:space:]]*:[[:space:]]*"sk-'
}

case ":$PATH:" in *":$INSTALL_DIR:"*) ;; *) export PATH="$INSTALL_DIR:$PATH" ;; esac

case "$MODE" in
  --check)
    status=0
    if [ -x "$BIN" ]; then log "CLI: $("$BIN" version 2>/dev/null | tr -d '\n ' | sed -E 's/.*"version":"([^"]+)".*/v\1/')"; else log "CLI: missing (run scripts/clipcat-setup.sh)"; status=1; fi
    if [ -x "$BIN" ] && key_configured; then log "API key: configured"; else log "API key: NOT configured (set CLIPCAT_API_KEY secret or run: clipcat config --api-key <key> --base-url $BASE_URL)"; status=1; fi
    exit "$status"
    ;;
  --update) install_binary || exit 0 ;;
  install|"") [ -x "$BIN" ] || install_binary || exit 0 ;;
  *) log "unknown option: $MODE"; exit 2 ;;
esac

if [ -n "${CLIPCAT_API_KEY:-}" ]; then
  "$BIN" config --api-key "$CLIPCAT_API_KEY" --base-url "$BASE_URL" >/dev/null 2>&1 \
    && log "API key saved from CLIPCAT_API_KEY" \
    || log "could not save API key"
elif ! key_configured; then
  log "no API key yet: add a CLIPCAT_API_KEY environment secret, or run: clipcat config --api-key <key> --base-url $BASE_URL"
fi

case ":$(bash -lc 'echo $PATH' 2>/dev/null):" in
  *":$INSTALL_DIR:"*) ;;
  *) log "note: $INSTALL_DIR is not on your login PATH; add: export PATH=\"$INSTALL_DIR:\$PATH\"" ;;
esac
exit 0
