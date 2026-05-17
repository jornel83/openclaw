# Video Content Analysis Contract

`videoContentAnalysis` is the stage-8 sidecar artifact that enriches metadata-only TikTok signals with MP4 understanding evidence.

## Scope

- Input: canonical `videoSamples` plus an `autotiktok-video-download` manifest or normalized download manifest.
- Runtime: OpenClaw media understanding via `openclaw infer video describe`.
- Default provider/model: `google/gemini-3-flash-preview`, loaded from `config/video-understanding.v1.json`.
- Contract rule: the model is a configurable default, not a business-logic constant.
- Fallback rule: missing or failed video analysis keeps the metadata-only `signalItems` lane valid.

## Artifact Shape

The committed focused fixture is `fixtures/video-content-analysis.sample.json`.

Required top-level fields:

- `schemaVersion`
- `snapshotId`
- `market`
- `language`
- `capturedAt`
- `videoUnderstanding`
- `generatedFrom`
- `analyses`
- `summary`

Each `analyses[*]` entry must include:

- `analysisId`
- `videoSampleId`
- `platformVideoId`
- `sourceSnapshotId`
- `videoPath`
- `provider`
- `model`
- `status`
- `download`
- `descriptionText`
- `contentSummary`
- `visualEvidence`
- `replicationHints`
- `analysisConfidence`
- `provenance`
- `errors`

Supported statuses:

- `analysis_succeeded`
- `download_missing`
- `analysis_failed`

## Validation

Run:

```bash
python3 skills/autotiktok-topic-discovery/scripts/validate_video_content_analysis_contract.py
python3 skills/autotiktok-topic-discovery/scripts/validate_video_content_analysis_batch_runner.py
```

The validator checks the focused fixture, the default video-understanding config, status counts, required success evidence, error handling, and fallback safety.

## Batch Runner

Run:

```bash
python3 skills/autotiktok-topic-discovery/scripts/run_video_content_analysis_batch.py --download-manifest <path> --cache-dir <dir> --continue-on-error
```

The runner reads a normalized `videoDownloadManifest`, selects the provider/model from `config/video-understanding.v1.json` unless `--provider` or `--model` is passed, invokes `openclaw infer video describe` only for valid downloaded MP4 entries, and emits `download_missing` or `analysis_failed` fallback entries without breaking the metadata-only lane. Use `--cache-dir` to avoid repeated paid calls and `--response-fixture` or `--use-default-response-fixture` for deterministic local validation.

## Signal Item Enrichment

Run:

```bash
python3 skills/autotiktok-topic-discovery/scripts/build_enriched_signal_items.py --signal-items <path> --video-content-analysis <path>
python3 skills/autotiktok-topic-discovery/scripts/validate_enriched_signal_items.py
```

Successful MP4 analysis enriches the existing metadata-only signal item by appending video-derived evidence to `topicSummary`, `contentAngles`, `requiredAssets`, `recommendedFormats`, `requiredCapabilities`, `expandabilityHint`, and `executionNotes`. Missing or failed analysis keeps the metadata-only signal valid and records fallback provenance in `rawMeta.videoContentAnalysisReference`.
