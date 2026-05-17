---
name: autotiktok-trending
description: >
  Capture TikTok absolute_hot and fresh_hot public videos using TikTokApi trending-feed
  sampling, then save contract-aligned video sample artifacts for downstream discovery.
  Use when the user wants structured TikTok hot-video recall within windows like 24h,
  7d, or 30d, without downloading media or doing AI replicability filtering. Triggers on
  "TikTok absolute hot", "TikTok fresh hot", "TikTok trending videos", "TikTok 热门视频",
  "TikTok 爆款视频", "找 TikTok 最火视频", "找 TikTok 新热视频".
metadata: { "openclaw": { "emoji": "🎵", "requires": { "anyBins": ["python3", "python"] } } }
---

# TikTok Trending — Absolute Hot / Fresh Hot Video Capture

This skill now treats **absolute_hot** and **fresh_hot** capture as the primary goal.

It uses `scripts/bakeoff.py` as the main runtime so the workflow can:

- sample TikTokApi trending feed in multiple batches
- recover from unstable headless sessions
- rank one retained pool into two views:
  - `absolute_hot`
  - `fresh_hot`
- emit contract-aligned `videoSamples` artifacts based on `video-sample-contract.md`

The old official-category route is no longer the main skill identity. It can still be
kept as an optional comparison route inside `bakeoff.py`, but the skill itself is now
about **capturing globally hot and relatively fresh hot public TikTok videos**.

## Prerequisites

- Python deps: `pip install TikTokApi playwright`
- Install Playwright browser once:
  ```
  python -m playwright install chromium
  ```
- Optional stability token:
  ```
  export TIKTOK_MS_TOKEN="your_ms_token"
  ```
- If the environment blocks headless scraping, add `--headful` and log in manually
  in the browser window when prompted.

## Execution guardrails

- The main collection path is `scripts/bakeoff.py` with `direct-hot` sampling.
- The primary success condition is to retain useful `absolute_hot` and `fresh_hot`
  videos, not to preserve official-category semantics.
- Do not add AI replicability filtering at this stage.
- Do not download media, audio, or captions beyond public metadata already returned
  by the collector.
- Save **video facts**, not topic abstractions.
- Keep ranking and diagnostics outside the canonical `videoSamples[*]` facts whenever
  possible.
- If `topic-first` is used, treat it as a debug / comparison route only.
- Do not switch to unrelated fallback discovery methods in the same run.

## Request Count Scope Rules

- Extract the requested video count `N` from any clear bounded user request, not
  only from the exact phrase `TopN`.
- Treat these as count requests: `Top5`, `Top 5`, `前5`, `5条热门视频`,
  `获取50个热门视频`, `从50个热门视频里`, `分析50条`, `download 10 videos`,
  `analyze 20 trending videos`, and `top 30 samples`.
- When a clear count `N` is present, set `--direct-keep N` and `--top-n N`
  together. `--top-n` is summary-only; never use it by itself to satisfy a
  bounded retained-video request.
- Choose `--direct-count` and `--direct-batches` large enough to have a
  reasonable chance of retaining `N` unique videos. `--direct-keep N` is still a
  maximum, not a guarantee; report the actual retained count when fewer than `N`
  useful videos survive filtering.
- If the user gives two different counts, preserve the distinction. For example,
  "collect 50 and download the top 5" means collector scope `N=50` and
  downstream download / video-understanding scope `N=5`; "collect Top5 and
  analyze those 5" means both scopes are `N=5`.
- If the wording is ambiguous, choose the smallest explicit count as the
  downstream analysis scope, keep any larger explicit count as the broader
  collector scope, and state the chosen scopes in the output.
- If no count is present, use the current default operating point.

## Request Ranking View Scope Rules

- Treat `absolute_hot` and `fresh_hot` as separate ranking views, not as an
  automatic combined candidate pool.
- If the user asks for generic "TopN hot / trending / hottest videos" without
  naming a freshness view, use `absolute_hot` as the downstream scope.
- If the user explicitly asks for fresh or rising videos, use `fresh_hot` as the
  downstream scope.
- If the user asks to compare both views, keep `absolute_hot` and `fresh_hot`
  outputs separate in the report unless they also ask for a merged pool.
- For any run that downloads or understands MP4s, downstream `videoSamples` must
  be built from the same ranking view that was downloaded / understood. Do not
  merge `fresh_hot_video_samples` into an `absolute_hot` TopN run as a fallback
  or supplement.
- If multiple views are intentionally merged before discovery or ranking, every
  sample entering the merged ranking must have a valid downloaded MP4 and
  `analysis_succeeded`. Download and understand the deduped union of
  `absolute_hot_video_samples` and `fresh_hot_video_samples`; do not cap the
  downloader with a global `--max N` at the original per-view TopN count if that
  would leave `fresh_hot` as `download_missing`. Prefer
  `autotiktok-video-download --from-bakeoff ... --bakeoff-view both --per-view-max N`
  for merged TopN runs. If that is not possible, keep the
  metadata-only items in diagnostics and label the run as a mixed metadata-only
  recall lane instead of a video-understanding TopN run.

## Main runtime

- Main script: `skills/autotiktok-trending/scripts/bakeoff.py`
- Main route: `direct-hot`
- Optional debug route: `topic-first`
- Ranking outputs:
  - `videos` = `absolute_hot`
  - `fresh_hot_videos` = `fresh_hot`
- Contract artifacts:
  - `absolute_hot_video_samples`
  - `fresh_hot_video_samples`
- These are separate view artifacts. Choose one for downstream discovery unless
  the user explicitly asks to merge or compare views. If you choose both, the
  downstream download / Gemini understanding scope is the deduped union of both
  artifacts, not just the first `N` absolute-hot URLs.

## Quick start

### 1. Capture direct-hot absolute_hot and fresh_hot videos

```bash
python3 {baseDir}/scripts/bakeoff.py \
  --route direct-hot \
  --window 24h \
  --region US \
  --language en \
  --direct-count 30 \
  --direct-batches 3 \
  --direct-batch-pause-seconds 1.0 \
  --direct-keep 20 \
  --top-n 10 \
  --out /tmp/tiktok-hot-bakeoff.json
```

Useful options:

- `--window`: `3h`, `6h`, `24h`, `7d`, `30d`
- `--route`: defaults to `direct-hot`; add `--route topic-first` only for comparison
- `--direct-count`: requested raw trending-feed batch size
- `--direct-batches`: number of trending-feed batches to sample
- `--direct-batch-pause-seconds`: pause between batches
- `--direct-keep`: max retained results per ranking view; set this from a clear
  user-requested count `N`
- `--per-author-limit`: avoid one creator dominating a category/topic
- `--region`: best-effort region filter
- `--language`: language tag for output video sample artifacts
- `--min-likes`: optional compatibility filter for low-signal videos
- `--headful`: useful when headless trending-feed sampling returns empty results
- `--top-n`: summary / overlap slice only; pair it with `--direct-keep N` for
  any bounded TopN request

Output JSON:

```json
{
  "experiment_type": "tiktok_hot_video_bakeoff",
  "window": "24h",
  "region": "US",
  "language": "en",
  "routes": [
    {
      "route_id": "direct-hot",
      "status": "ok",
      "videos": [
        {
          "video_id": "7234567890",
          "author": "creatorname",
          "author_id": "7123456789",
          "author_display_name": "Creator Demo",
          "create_time": "2026-04-13T09:30:00Z",
          "view_count": 2400000,
          "like_count": 152000,
          "comment_count": 3200,
          "share_count": 8900,
          "duration_sec": 19,
          "cover_url": "https://example.com/cover.jpg",
          "share_url": "https://www.tiktok.com/@creator_demo/video/7234567890",
          "hot_score": 0.913244,
          "ranking_mode": "absolute_hot"
        }
      ],
      "fresh_hot_videos": [],
      "absolute_hot_video_samples": {
        "schemaVersion": "discovery-video-samples.v1",
        "snapshotId": "snap.tiktok.direct-hot.absolute_hot.us.20260420t051200z",
        "market": "US",
        "language": "en",
        "capturedAt": "2026-04-20T05:12:00Z",
        "videoSamples": []
      }
    }
  ]
}
```

## Ranking views

- `engagement = like_count + 2.5 * comment_count + 4 * share_count`
- `velocity = engagement / age_hours`
- `quality = engagement / max(view_count, 1)`
- `absolute_hot` emphasizes exposure, engagement, and overall dominance
- `fresh_hot` emphasizes velocity and freshness on top of exposure and engagement
- The workflow may relax the requested window to `30d` or any-age fallback when
  TikTokApi trending feed does not yield enough recent candidates

## Contract-aligned saved fields

The saved video sample artifacts should align with `video-sample-contract.md`.

Required collector facts per sample:

- `videoSampleId`
- `platformVideoId`
- `sourceSnapshotId`
- `publishedAt`
- `title`
- `desc`
- `hashtags`
- `authorId`
- `metrics.views`
- `metrics.likes`
- `metrics.shares`

Recommended fields that this skill now attempts to fill when TikTokApi provides them:

- `authorHandle`
- `authorDisplayName`
- `durationSec`
- `coverUrl`
- `shareUrl`
- `metrics.comments`
- `metrics.favorites`
- `metrics.bookmarks`
- `audio.audioId`
- `audio.title`
- `audio.isOriginal`
- `region`
- `rawMeta`

Collector rule:

- keep **video facts** inside `videoSamples`
- keep ranking, diagnostics, and bakeoff-only metadata outside `videoSamples`

## Debug comparison workflow

Use this only when you explicitly want to compare `direct-hot` against the older
official-topic route:

```bash
python3 {baseDir}/scripts/bakeoff.py \
  --route direct-hot \
  --route topic-first \
  --window 24h \
  --direct-count 30 \
  --direct-batches 3 \
  --direct-batch-pause-seconds 1.0 \
  --direct-keep 20 \
  --topic-category-limit 8 \
  --topic-per-query 50 \
  --topic-per-category 10 \
  --per-author-limit 2 \
  --out /tmp/tiktok-hot-bakeoff.json
```

## Output interpretation

- `videos` is the retained `absolute_hot` list
- `fresh_hot_videos` is the retained `fresh_hot` list
- `absolute_hot_video_samples` and `fresh_hot_video_samples` are the downstream
  discovery-facing artifacts
- `candidate_age_distribution` explains the age mix of raw candidates returned by
  TikTokApi
- `retained_age_distribution` explains what survived filtering and ranking
- `rejection_preview` helps diagnose why candidates were discarded
- `sampling.batch_reports` shows whether more batches are still expanding the pool
- `sampling.sampling_strategy` shows whether the run used the requested batch plan
  or a stability fallback

## Notes

- The current default operating point is `direct-count=30`, `direct-batches=3`,
  `direct-batch-pause-seconds=1.0` because that has been the best stability /
  unique-coverage balance so far.
- `fetch-candidates.py` and `fetch-trending.py` remain legacy aliases for the old
  official-category crawler and are not the main path for this skill anymore.
- `absolute_hot` and `fresh_hot` still mostly reorder the same candidate pool today.
  To separate them further, the next improvement should expand candidate diversity,
  not just tweak ranking weights.
- `TIKTOK_MS_TOKEN` and `--headful` can help when TikTokApi sessions are blocked.
- Respect TikTok ToS: use data for research/analysis, not redistribution.
