#!/usr/bin/env bash
# Convert the Playwright recording (scripts/record_demo.cjs) into the README hero GIF:
# a cinematic 2.39:1 widescreen (1200x502) center-letterbox crop of the scrolling dashboard.
#
# Usage:
#   scripts/record_demo.cjs  ->  /tmp/demo_rec/<page>.webm     (record first; see that file's header)
#   scripts/make_demo_gif.sh [INPUT_WEBM] [OUTPUT_GIF]
# Defaults: newest *.webm in /tmp/demo_rec  ->  docs/demo.gif
#
# Requires: ffmpeg + gifski (both on PATH).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
IN="${1:-$(ls -t /tmp/demo_rec/*.webm 2>/dev/null | head -1)}"
OUT="${2:-$REPO/docs/demo.gif}"

# Trim window. record_demo.cjs writes the exact top->bottom scroll window to markers.env next
# to the webm; source it so the GIF starts on the page top and ends at the bottom (no guessing).
# Env vars (SS/DUR) still win; the hardcoded values are a last-resort fallback for standalone use.
MARKERS="$(dirname "${IN:-/tmp/demo_rec/x}")/markers.env"
[ -f "$MARKERS" ] && . "$MARKERS"
SS="${SS:-${GIF_SS:-2.4}}"   # start of the scroll window (page top, into the top hold)
DUR="${DUR:-${GIF_DUR:-5.2}}" # full scroll + bottom hold
FPS=16      # ~16.7fps reference cadence; ~5.5s x 16 ~= 88 frames
# Cinematic 2.39:1 band: from the 1280x860 capture take a centered 1280x536 strip, scale to 1200x502.
VF="crop=1280:536:0:162,scale=1200:502:flags=lanczos"

if [ -z "${IN:-}" ] || [ ! -f "$IN" ]; then
  echo "No input webm found. Record first (scripts/record_demo.cjs) or pass a path." >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Input : $IN"
echo "Output: $OUT"
ffmpeg -loglevel error -ss "$SS" -t "$DUR" -i "$IN" -vf "$VF,fps=$FPS" "$TMP/f_%04d.png"
gifski --fps "$FPS" --width 1200 --height 502 --quality 84 -o "$OUT" "$TMP"/f_*.png

echo "Done."
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,nb_frames -of default=noprint_wrappers=1 "$OUT"
du -h "$OUT"
