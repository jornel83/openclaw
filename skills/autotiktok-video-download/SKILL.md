---
name: tiktok-video-download
description: >
  Download a public TikTok video to a local file from one or more video URLs using
  yt-dlp. Writes the media file and a JSON manifest with id, path, size, duration,
  and basic metadata. Use when the user has a TikTok video URL or a list of URLs
  (for example from the tiktok-trending skill output) and wants the actual MP4
  saved locally for downstream review or analysis. Triggers on
  "下载 TikTok 视频", "保存 TikTok 视频", "download TikTok video",
  "save this TikTok url", "TikTok 视频下载".
metadata: { "openclaw": { "emoji": "⬇️", "requires": { "anyBins": ["python3", "python"] } } }
---

# TikTok Video Download

Downloads one or more public TikTok videos to a local directory using `yt-dlp`,
and emits a small JSON manifest describing each saved file. This skill is the
natural pair for `tiktok-trending`: feed it a `url` from the trending samples
and you get the actual MP4 on disk.

## Prerequisites

- Python deps: `pip install yt-dlp`
- The video URL must be publicly accessible (no login-walled content).
- Optional: `ffmpeg` on `PATH` improves merging when yt-dlp picks split streams.

## Usage

Single URL:

```
python {baseDir}/scripts/download.py \
  --url https://www.tiktok.com/@user/video/123 \
  --out-dir .openclaw/tiktok-downloads \
  --manifest .openclaw/tiktok-downloads/manifest.json
```

Batch (one URL per line in a text file):

```
python {baseDir}/scripts/download.py \
  --urls-file urls.txt \
  --out-dir .openclaw/tiktok-downloads \
  --manifest .openclaw/tiktok-downloads/manifest.json
```

Direct from a `tiktok-trending` JSON output (auto-extracts URLs from
`absolute_hot_video_samples` and `fresh_hot_video_samples`):

```
python {baseDir}/scripts/download.py \
  --from-bakeoff .openclaw/tiktok-multisession-4x.json \
  --out-dir .openclaw/tiktok-downloads \
  --manifest .openclaw/tiktok-downloads/manifest.json \
  --max 5
```

## Flags

- `--url <url>` Single TikTok video URL. Repeatable.
- `--urls-file <path>` Text file with one URL per line.
- `--from-bakeoff <path>` Read URLs from a `tiktok-trending` bakeoff JSON.
- `--out-dir <dir>` Output directory. Created if missing.
- `--manifest <path>` JSON manifest written after the run.
- `--max <n>` Optional hard cap on URLs to process.
- `--format <yt-dlp-format>` Override yt-dlp `format` selector (default: `best`).
- `--filename-template <tmpl>` yt-dlp `outtmpl` (default: `%(id)s.%(ext)s`).
- `--overwrite` Re-download even if the target file already exists.
- `--quiet` Suppress yt-dlp progress output.

## Output

Each entry in `manifest.json` looks like:

```json
{
  "url": "https://www.tiktok.com/@user/video/123",
  "video_id": "123",
  "author": "user",
  "status": "ok",
  "file": ".openclaw/tiktok-downloads/123.mp4",
  "size_bytes": 1234567,
  "duration_sec": 18,
  "title": "...",
  "format_id": "..."
}
```

`status` is `ok`, `skipped` (already exists), or `error` (with `error` field).

## Execution guardrails

- Only public TikTok video URLs.
- This skill **does not** strip watermarks, re-encode, or upload anywhere; it only
  saves the file yt-dlp returns.
- Treat downloaded files as untrusted media; do not auto-open or auto-process.
