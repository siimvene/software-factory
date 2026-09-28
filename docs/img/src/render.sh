#!/usr/bin/env bash
# Render docs/img/src/*.html to docs/img/*.png with headless Chrome (macOS path; set CHROME elsewhere).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
for src in "$here"/*.html; do
  name="$(basename "$src" .html)"
  height="$(sed -n 's/.*data-height="\([0-9]*\)".*/\1/p' "$src" | head -1)"
  "$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1.35 \
    --window-size=1600,"${height:-1200}" --screenshot="$here/../$name.png" "file://$src" 2>/dev/null
  echo "rendered $name.png"
done
