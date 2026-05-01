#!/usr/bin/env bash
set -euo pipefail

# Download a TikTok video by URL using yt-dlp.
# Saves: video.mp4 + info.json + thumbnail
#
# Usage:
#   download-video.sh "https://www.tiktok.com/@user/video/123" --out /tmp/videos/

usage() {
  cat >&2 <<'EOF'
Usage:
  download-video.sh <tiktok-url> --out <output-dir> [--cookies-from-browser <browser>]

Examples:
  download-video.sh "https://www.tiktok.com/@user/video/7234567890" --out /tmp/videos/
  download-video.sh "https://www.tiktok.com/@user/video/7234567890" --out /tmp/videos/ --cookies-from-browser chrome
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

url="${1}"
shift

out=""
cookies_browser=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      out="${2:-}"
      shift 2
      ;;
    --cookies-from-browser)
      cookies_browser="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      ;;
  esac
done

if [[ -z "$out" ]]; then
  echo "Missing --out" >&2
  usage
fi

if ! command -v yt-dlp &>/dev/null; then
  echo "Error: yt-dlp not found. Install with: pip install yt-dlp" >&2
  exit 1
fi

mkdir -p "$out"

cookie_args=()
if [[ -n "$cookies_browser" ]]; then
  cookie_args=(--cookies-from-browser "$cookies_browser")
fi

yt-dlp \
  --write-info-json \
  --write-thumbnail \
  --output "${out}/%(id)s.%(ext)s" \
  --sleep-interval 2 \
  --no-overwrites \
  --merge-output-format mp4 \
  "${cookie_args[@]}" \
  "$url"

echo "Downloaded to: $out" >&2
