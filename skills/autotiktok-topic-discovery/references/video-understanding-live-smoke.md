# Video Understanding Live-ish Smoke

Use this runbook when you want to test the AutoTikTok MP4 understanding lane with real downloaded videos while keeping cost and blast radius controlled.

## Default Safe Gate

Run deterministic fixture gates first. These do not call paid model providers:

```bash
python3 skills/autotiktok-topic-discovery/scripts/validate_video_content_analysis_batch_runner.py
python3 skills/autotiktok-topic-discovery/scripts/validate_enriched_signal_items.py
python3 skills/autotiktok/scripts/validate_enriched_discovery_ranking_integration.py
```

## Small Live-ish Batch

Only run live-ish video understanding with an explicit `--limit`, cache directory, and output path:

```bash
python3 skills/autotiktok-topic-discovery/scripts/run_video_content_analysis_batch.py \
  --download-manifest <normalized-video-download-manifest.json> \
  --provider google \
  --model gemini-3-flash-preview \
  --limit 1 \
  --cache-dir <cache-dir> \
  --continue-on-error \
  --output <video-content-analysis.json>
```

This runner is the only official live-ish MP4 understanding entry point. It
must call `openclaw infer video describe` for each downloaded MP4 that has a
`downloaded` manifest status. The selected OpenClaw model must resolve to
`google/gemini-3-flash-preview`; direct one-off smoke checks must include
`--model google/gemini-3-flash-preview` rather than relying on automatic
provider selection.

If the live run materializes both `absolute_hot` and `fresh_hot` into discovery
or ranking, first download the deduped union of both views. Do not cap the raw
download step at the original per-view TopN count if that leaves `fresh_hot`
samples as `download_missing`; either analyze both views or keep the un-analyzed
view out of the final recommendation pool.

For a merged TopN smoke, prefer the downloader's per-view cap:

```bash
python3 skills/autotiktok-video-download/scripts/download.py \
  --from-bakeoff <tiktok-trending-bakeoff.json> \
  --bakeoff-view both \
  --per-view-max <N> \
  --out-dir <download-dir> \
  --manifest <raw-download-manifest.json>
```

Do not extract frames with `ffmpeg`, call `openclaw infer image describe`, call
`openclaw infer model run --file` on JPEG frames, or write one-off report
scripts as a replacement for this lane. Those approaches analyze still images,
not the native video stream, and must be labeled approximate debugging output if
the user explicitly requests them.

Then enrich signal items and run the focused integration gate:

```bash
python3 skills/autotiktok-topic-discovery/scripts/build_enriched_signal_items.py \
  --signal-items <metadata-only-signal-items.json> \
  --video-content-analysis <video-content-analysis.json> \
  --output <signal-items.enriched.json>
```

For the committed sample path, use:

```bash
python3 skills/autotiktok/scripts/validate_enriched_discovery_ranking_integration.py
```

## Model Selection

The default is configured in `skills/autotiktok-topic-discovery/config/video-understanding.v1.json`:

- provider: `google`
- model: `gemini-3-flash-preview`
- OpenClaw model ref: `google/gemini-3-flash-preview`

Use `--provider` and `--model` only for explicit experiments. The business logic must not hardcode a provider-specific model outside the config and CLI override path.

## Cost And Failure Boundaries

- Do not run broad paid analysis by default.
- Use `--limit 1` for the first live-ish run.
- Always use `--cache-dir` before increasing the limit.
- Keep `--continue-on-error` enabled so one model failure cannot block metadata-only discovery / ranking.
- Treat `download_missing`, `download_error`, `invalid_file`, model timeout, and provider errors as fallback statuses, not fatal pipeline failures.
- For video-understood TopN recommendations, keep fallback statuses out of the
  final ranking pool unless the report explicitly labels them as a separate
  metadata-only recall lane.
