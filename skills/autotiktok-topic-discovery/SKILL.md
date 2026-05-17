---
name: autotiktok-topic-discovery
description: >
  Discover and package TikTok topic candidates from trend, search, and
  public-video signals. Use when defining or refining signal ingestion, topic
  abstraction, candidate generation, dedupe and merge rules, search-evidence
  packaging, execution-profile packaging, module-1 delivery scope, AutoTikTok
  video understanding, downloaded TikTok MP4 analysis, "download + understand
  video", or enriched Top topic generation. For AutoTikTok video understanding,
  read this skill first; the official path must call openclaw infer video
  describe through run_video_content_analysis_batch.py with
  google/gemini-3-flash-preview as the default model and must not use ffmpeg
  frame extraction, image-description tools, auto-selected alternate models, or
  one-off report scripts as the video-understanding substitute.
---

# AutoTikTok Topic Discovery

Use this skill when the task is about turning raw TikTok signals into structured topic candidates.

## What This Skill Owns

- signal-source strategy
- snapshot-based collection assumptions
- `signal -> evidence_bundle -> topic_candidate`
- topic abstraction and merge behavior
- `topicFingerprint`
- `searchEvidence`
- `executionProfile`

## Read First

- Read [references/discovery-scope.md](references/discovery-scope.md) for signal strategy, collector boundaries, storage objects, and module-1 pipeline shape.
- Read [references/video-sample-contract.md](references/video-sample-contract.md) when you need the current collector-facing field contract for `videoSamples`.
- Read [references/topic-candidate-contract.md](references/topic-candidate-contract.md) for the discovery-owned `topicCandidate` contract and freeze checklist.
- Read [references/merge-and-evidence.md](references/merge-and-evidence.md) for the current merge, dedupe, and evidence-packaging rules.
- Read [references/discovery-dry-run.md](references/discovery-dry-run.md) for the mock discovery runner, sample signal inputs, and generated artifacts.
- Read [references/discovery-delivery.md](references/discovery-delivery.md) for owner split, milestones, and integration risks.
- Read [references/video-download-manifest-contract.md](references/video-download-manifest-contract.md) when you need to normalize `autotiktok-video-download` output and join it to `videoSamples`.
- Read [references/video-content-analysis-contract.md](references/video-content-analysis-contract.md) when you need the MP4 multimodal sidecar contract for enriching `signalItems`.
- Read [references/video-understanding-live-smoke.md](references/video-understanding-live-smoke.md) before running live-ish MP4 understanding against real downloaded videos.
- Read [../autotiktok/docs/热门题材策略模块开发需求.md](../autotiktok/docs/热门题材策略模块开发需求.md) when you need the original product framing for candidate generation.

## Working Rules

- Keep module boundaries strict:
  - discovery produces `topicCandidate`
  - ranking consumes `topicCandidate`
- Treat official TikTok web products as the primary signal source.
- Keep outputs snapshot-based so replay and offline evaluation remain possible.
- Preserve evidence chains instead of collapsing candidates into freeform titles.
- Do not design ranking weights or reward logic here unless the discovery output contract must change.
- For live Top topic runs, build the full discovery input set for the selected
  request scope before video enrichment: `source-snapshots.from-trending.json`,
  `video-samples.from-trending.json`, and
  `signal-items.from-trending.synthetic.json`. A cleaned `videoSamples` file is
  not enough for the standard artifact pipeline because enrichment needs the
  metadata-only `signalItems` input and discovery needs all three snapshot
  inputs.
- Preserve the count scope selected by `autotiktok-trending`. If the user asked
  for `N` videos and no broader collector pool was requested, downstream
  `videoSamples`, `signalItems`, `video-download-manifest.json`,
  `video-content-analysis.json`, `signal-items.enriched.json`,
  `discovery-dry-run.json`, and `ranking-dry-run.json` should all use that same
  `N` scope.
- Preserve the ranking view selected by `autotiktok-trending`. If the selected
  view is `absolute_hot`, build discovery inputs from `absolute_hot_video_samples`
  only; if the selected view is `fresh_hot`, build from `fresh_hot_video_samples`
  only. Do not merge both views into one discovery/ranking pool unless the user
  explicitly requested a merged or comparative run.
- Use `build_discovery_inputs_from_trending.py --view absolute_hot` or
  `--view fresh_hot` for single-view TopN runs. Use `--view both` only when the
  downloader and Gemini analysis have covered the deduped union of
  `absolute_hot_video_samples` and `fresh_hot_video_samples`.
- For merged absolute/fresh TopN runs, the expected download command uses
  `autotiktok-video-download --from-bakeoff ... --bakeoff-view both --per-view-max N`
  before video analysis. A global `--max N` is not enough because it can cap the
  merged URL list before `fresh_hot` videos are downloaded.
- For runs that require MP4 understanding, do not let a `download_missing`,
  `analysis_failed`, or metadata-only fallback signal enter the final ranked
  recommendation pool. Keep such items in diagnostics, or rerun download and
  analysis for that sample before including it in `ranking-dry-run.json`.
- If a both-view run has `fresh_hot` samples in `video-samples.from-trending.json`,
  those `fresh_hot` sample IDs must appear as `downloaded` in
  `video-download-manifest.json` and as `analysis_succeeded` in
  `video-content-analysis.json` before ranking.
- If the user explicitly requested a broader collector pool plus a smaller
  download / video-understanding sample, label both scopes in the report. Do not
  describe a mixed run as TopN-only when metadata-only fallback items still enter
  discovery or ranking.
- For MP4 content understanding, the official path is native OpenClaw video
  description only: run `scripts/run_video_content_analysis_batch.py`, which
  calls `openclaw infer video describe` and emits `video-content-analysis.json`.
- Use `google/gemini-3-flash-preview` for AutoTikTok MP4 understanding unless
  the user explicitly asks for a different model. Do not let OpenClaw auto-select
  `moonshot/kimi-k2.6` or another configured video-description model for this
  lane.
- When calling OpenClaw directly for a one-off smoke, include
  `--model google/gemini-3-flash-preview`. When calling the batch runner, use
  the default config or pass `--provider google --model gemini-3-flash-preview`.
- Do not extract frames, call image-description tools, or write ad hoc video
  summaries as a substitute for MP4 understanding. Frame extraction is only an
  explicitly requested debugging aid and must be labeled approximate, not as
  the AutoTikTok video-understanding lane.
- If a downloaded MP4 already exists but the download manifest reports failure,
  first rebuild or correct the normalized `videoDownloadManifest`; do not bypass
  the manifest and analyze the MP4 manually.
- After `video-content-analysis.json` is generated for a live Top topic run,
  continue with `build_enriched_signal_items.py`, `discovery_dry_run.py`, and
  `autotiktok-topic-ranking/scripts/dry_run_ranking.py`. Do not end with a
  one-off Markdown report unless the user explicitly requested a quick report.
- Treat the run as complete only when `signal-items.enriched.json`,
  `discovery-dry-run.json`, and `ranking-dry-run.json` exist. The final report
  should read ranked topics from `ranking-dry-run.json` and use
  `video-content-analysis.json` only as supporting evidence.

## Output Expectations

Discovery work should usually end with one or more of these:

- a candidate schema change proposal
- a merge or dedupe rule
- a snapshot or collector requirement
- a fixture or evidence-packaging update

## Bundled Script

- Run `python3 {baseDir}/scripts/validate_raw_signals.py` to validate the raw-signal fixture shape before packaging.
- Pass `--input <path>` to validate another raw-signal fixture file.
- Run `python3 {baseDir}/scripts/validate_discovery_snapshot_materialization.py` to validate the snapshot-materialization fixture that discovery now uses by default.
- Pass `--input <path>` to validate another snapshot-materialization fixture file.
- Run `python3 {baseDir}/scripts/validate_trending_discovery_adapter_contract.py` to validate focused `autotiktok-trending` output fixtures before building discovery inputs from them.
- Run `python3 {baseDir}/scripts/validate_video_download_manifest_adapter.py` to validate raw `autotiktok-video-download` output normalization and `videoSamples` join behavior.
- Run `python3 {baseDir}/scripts/validate_video_content_analysis_contract.py` to validate the focused `videoContentAnalysis` sidecar fixture and default video-understanding config.
- Run `python3 {baseDir}/scripts/validate_video_content_analysis_batch_runner.py` to validate that the MP4 understanding batch runner still regenerates the committed `videoContentAnalysis` fixture from a normalized download manifest.
- Run `python3 {baseDir}/scripts/validate_enriched_signal_items.py` to validate `videoContentAnalysis -> enriched signalItems` behavior and metadata-only fallback safety.
- Run `python3 {baseDir}/scripts/validate_video_understanding_live_smoke_docs.py` to validate the live-ish smoke runbook and cost-control guidance.
- Run `python3 {baseDir}/scripts/build_video_download_manifest.py --video-samples <path> --raw-manifest <path>` to build the normalized `videoDownloadManifest` sidecar input.
- Run `python3 {baseDir}/scripts/run_video_content_analysis_batch.py --download-manifest <path> --config <path> --cache-dir <dir> --continue-on-error` to call `openclaw infer video describe --model google/gemini-3-flash-preview` for downloaded MP4s and emit the `videoContentAnalysis` sidecar.
- Run `python3 {baseDir}/scripts/build_enriched_signal_items.py --signal-items <path> --video-content-analysis <path>` to enrich metadata-only synthetic `signalItems` with MP4 understanding evidence.
- Run `python3 {baseDir}/scripts/build_trending_source_snapshots.py --input <path>` to build `sourceSnapshots` from an `autotiktok-trending` output.
- Run `python3 {baseDir}/scripts/build_trending_video_samples.py --input <path>` to normalize `autotiktok-trending` output into canonical `videoSamples`.
- Run `python3 {baseDir}/scripts/build_trending_signal_items.py --input <path>` to build metadata-only synthetic `signalItems` from normalized trending `videoSamples`.
- Run `python3 {baseDir}/scripts/build_discovery_inputs_from_trending.py --input <path> --view absolute_hot --output-dir <dir>` to produce the full `sourceSnapshots + videoSamples + signalItems` discovery input set for one selected view. Use `--view fresh_hot` for fresh-only runs and `--view both` only when both views will be downloaded and video-understood.
- Run `python3 {baseDir}/scripts/build_discovery_snapshot_materialization.py` when you want to materialize `sourceSnapshots + signalItems + videoSamples` into the committed snapshot-materialization artifact.
- Run `python3 {baseDir}/scripts/check_topic_candidate_contract.py` to validate the shared candidate fixture against the discovery-owned contract.
- Pass `--input <path>` to validate another candidate fixture file.
- Run `python3 {baseDir}/scripts/discovery_dry_run.py` to turn a snapshot-materialization or raw-signal input into evidence bundles, merge groups, and packaged candidates.
- The committed discovery output now also freezes `normalizedSignals` and `topicAbstractions`, so normalization / abstraction regressions can be checked before ranking starts.
- The committed discovery output now also freezes merge / packaging semantics such as `mergeClassification`, `dedupeDecision`, `searchEvidenceSummary`, and `executionEvidenceSummary`, so merge regressions can be checked before ranking starts.
- Pass `--input <path>`, `--signals <path>`, `--source-snapshots <path>`, `--signal-items <path>`, `--video-samples <path>`, `--policy <path>`, or `--output <path>` to replay another discovery input fixture or write a sample artifact file.
- The reusable discovery core now lives in `scripts/discovery_lib.py`, while `config/discovery-policy.v1.json` holds source-priority, merge, and packaging knobs.

## Related Skills

- Use `autotiktok-topic-ranking` for feature scoring, ranking, rerank, and score outputs.
- Use `autotiktok-strategy-optimizer` for reward, backfill, daily review, and champion/challenger work.
