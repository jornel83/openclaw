# Video Download Manifest Contract

`videoDownloadManifest` is the stage-8 adapter artifact that joins canonical `videoSamples` with raw `autotiktok-video-download` output.

## Scope

- Input 1: canonical `videoSamples`.
- Input 2: raw downloader manifest emitted by `skills/autotiktok-video-download/scripts/download.py`.
- Output: normalized `videoDownloadManifest`, one entry per `videoSamples[*]`.
- Join rule: `platformVideoId` first, `shareUrl` second, file stem fallback.
- Fallback rule: missing, failed, invalid, or duplicate downloads do not stop the metadata-only lane.

## Statuses

- `downloaded`: matched to a usable non-empty MP4.
- `download_missing`: no raw download record matched the video sample.
- `download_error`: downloader returned `status=error`.
- `invalid_file`: downloader returned a record, but the file metadata is not a usable MP4.

Duplicate raw download records are tracked through `duplicateRawDownloadIndexes` and warnings on the kept entry.

## Validation

Run:

```bash
python3 skills/autotiktok-topic-discovery/scripts/validate_video_download_manifest_adapter.py
```

The validator rebuilds `fixtures/video-download-manifest.sample.json` from:

- `fixtures/video-samples.download-adapter.sample.json`
- `fixtures/video-download-raw.sample.json`

It then checks the normalized contract, status counts, duplicate handling, and fallback safety.
