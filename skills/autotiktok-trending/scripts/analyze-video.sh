#!/usr/bin/env bash
set -euo pipefail

# Analyze a downloaded TikTok video: extract key frames, audio, and metadata.
#
# Usage:
#   analyze-video.sh /path/to/video.mp4 --out /tmp/analysis/video_id/
#
# Output structure:
#   frames/          - Key frames (1/sec + scene change detection)
#   audio.mp3        - Extracted audio track
#   metadata.json    - Video technical metadata (resolution, fps, etc.)
#   structure.json   - Scene timestamps, frame count summary

usage() {
  cat >&2 <<'EOF'
Usage:
  analyze-video.sh <video-file> --out <output-dir>

Examples:
  analyze-video.sh /tmp/videos/7234567890.mp4 --out /tmp/analysis/7234567890/
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

in="${1}"
shift

out=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      out="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      ;;
  esac
done

if [[ ! -f "$in" ]]; then
  echo "File not found: $in" >&2
  exit 1
fi

if [[ -z "$out" ]]; then
  echo "Missing --out" >&2
  usage
fi

if ! command -v ffmpeg &>/dev/null; then
  echo "Error: ffmpeg not found." >&2
  exit 1
fi

if ! command -v ffprobe &>/dev/null; then
  echo "Error: ffprobe not found." >&2
  exit 1
fi

mkdir -p "${out}/frames"

echo "Extracting key frames..." >&2
# Extract 1 frame per second + frames at scene changes (threshold 0.3)
ffmpeg -hide_banner -loglevel error -y \
  -i "$in" \
  -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,1)+gt(scene\,0.3)',scale=640:-1" \
  -vsync vfr \
  "${out}/frames/frame_%03d.jpg"

echo "Extracting audio..." >&2
# Extract audio track (skip if no audio stream)
ffmpeg -hide_banner -loglevel error -y \
  -i "$in" -vn -acodec libmp3lame -q:a 4 \
  "${out}/audio.mp3" 2>/dev/null || echo "No audio stream found, skipping." >&2

echo "Extracting metadata..." >&2
# Video technical metadata via ffprobe
ffprobe -v quiet -print_format json -show_format -show_streams "$in" \
| jq '{
    duration: (.format.duration | tonumber | . * 100 | round / 100),
    resolution: "\(.streams[0].width)x\(.streams[0].height)",
    fps: .streams[0].r_frame_rate,
    codec: .streams[0].codec_name,
    size_bytes: (.format.size | tonumber),
    format: .format.format_name
  }' > "${out}/metadata.json"

echo "Building structure analysis..." >&2
# Scene change detection timestamps
scene_times=$(ffprobe -v quiet -show_entries frame=pts_time \
  -select_streams v -of csv=p=0 \
  -f lavfi "movie=$in,select=gt(scene\,0.3)" 2>/dev/null || echo "")

frame_count=$(ls -1 "${out}/frames/" 2>/dev/null | wc -l | tr -d ' ')

# Build structure.json
jq -n \
  --argjson fc "$frame_count" \
  --arg scenes "$scene_times" \
  --slurpfile meta "${out}/metadata.json" \
  '{
    frame_count: $fc,
    scene_change_timestamps: ($scenes | split("\n") | map(select(. != "")) | map(tonumber)),
    metadata: $meta[0]
  }' > "${out}/structure.json"

echo "Analysis complete: $out" >&2
echo "  Frames: $frame_count" >&2
echo "  Scene changes: $(echo "$scene_times" | grep -c . || echo 0)" >&2
echo "$out"
