#!/usr/bin/env python3
import argparse
import asyncio
import importlib.util
import json
import os
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


def load_crawl_module() -> ModuleType:
    target = Path(__file__).with_name("crawl-official-categories.py")
    spec = importlib.util.spec_from_file_location("tiktok_trending_crawl", target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load crawl module from {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture TikTok absolute-hot and fresh-hot videos with contract-aligned output")
    parser.add_argument(
        "--route",
        action="append",
        choices=["topic-first", "direct-hot"],
        default=[],
        help="Route(s) to run. Defaults to direct-hot when omitted.",
    )
    parser.add_argument(
        "--window",
        default="24h",
        choices=["3h", "6h", "24h", "7d", "30d"],
        help="Only include videos published within this time window",
    )
    parser.add_argument("--region", default="", help="Best-effort region filter, for example US")
    parser.add_argument(
        "--language",
        default="und",
        help="BCP 47 language tag for saved video sample artifacts, for example en",
    )
    parser.add_argument(
        "--topic-category-limit",
        type=int,
        default=8,
        help="Maximum number of discovered official categories to evaluate in the topic-first route",
    )
    parser.add_argument(
        "--topic-per-query",
        type=int,
        default=50,
        help="Maximum number of raw TikTokApi candidates per discovered category/topic",
    )
    parser.add_argument(
        "--topic-per-category",
        type=int,
        default=10,
        help="Maximum number of retained videos per discovered category/topic",
    )
    parser.add_argument(
        "--direct-count",
        type=int,
        default=100,
        help="Maximum number of raw TikTokApi trending-feed candidates to request",
    )
    parser.add_argument(
        "--direct-batches",
        type=int,
        default=1,
        help="How many trending-feed batches to sample for the direct-hot route",
    )
    parser.add_argument(
        "--direct-batch-pause-seconds",
        type=float,
        default=0.0,
        help="Pause between direct-hot trending-feed batches to reduce identical back-to-back samples",
    )
    parser.add_argument(
        "--direct-keep",
        type=int,
        default=50,
        help="Maximum number of retained videos for the direct-hot route after filtering and ranking",
    )
    parser.add_argument(
        "--per-author-limit",
        type=int,
        default=2,
        help="Maximum number of retained videos per author within a single route",
    )
    parser.add_argument("--min-likes", type=int, default=None, help="Optional minimum likes threshold override")
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="How many top-ranked videos per route to use for overlap and summary calculations",
    )
    parser.add_argument(
        "--browser",
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="Playwright browser to launch for TikTokApi sessions",
    )
    parser.add_argument("--headful", action="store_true", help="Run browser in visible mode")
    parser.add_argument(
        "--ms-token",
        default=os.environ.get("TIKTOK_MS_TOKEN", ""),
        help="Optional TikTok msToken for better stability; defaults to TIKTOK_MS_TOKEN",
    )
    parser.add_argument(
        "--ms-tokens",
        default="",
        help="Comma-separated TikTok msTokens for multi-session direct-hot sampling. Falls back to --ms-token when empty.",
    )
    parser.add_argument(
        "--num-sessions",
        type=int,
        default=1,
        help="Number of TikTokApi sessions to spawn for direct-hot. Each session is an independent recommendation seed.",
    )
    parser.add_argument(
        "--source-timeout",
        type=int,
        default=20,
        help="Timeout in seconds for fetching official source pages used by the topic-first route",
    )
    parser.add_argument("--out", required=True, help="Output JSON file path")
    args = parser.parse_args()
    if not args.route:
        args.route = ["direct-hot"]
    if args.direct_batches < 1:
        parser.error("--direct-batches must be >= 1")
    if args.direct_batch_pause_seconds < 0:
        parser.error("--direct-batch-pause-seconds must be >= 0")
    if args.num_sessions < 1:
        parser.error("--num-sessions must be >= 1")
    return args


def build_base_crawl_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        window=args.window,
        per_author_limit=args.per_author_limit,
        min_likes=args.min_likes,
        category="",
        hashtag=[],
        creator=[],
        region=args.region,
        discover_only=False,
        browser=args.browser,
        headful=args.headful,
        ms_token=args.ms_token,
        source_timeout=args.source_timeout,
        out=args.out,
    )


def make_empty_filter_diagnostics() -> dict[str, int]:
    return {
        "seen": 0,
        "accepted": 0,
        "missing_video_id": 0,
        "live_or_stream": 0,
        "missing_or_old_create_time": 0,
        "region_filtered": 0,
        "below_min_likes": 0,
        "negative_like_count": 0,
        "other_rejected": 0,
    }


def looks_like_live_or_stream(raw: dict[str, Any]) -> bool:
    live_markers = (
        "stream_url",
        "streamData",
        "liveRoom",
        "liveRoomStats",
        "game_tag",
        "owner",
    )
    if any(marker in raw for marker in live_markers):
        return True
    title = raw.get("title")
    description = raw.get("desc") or raw.get("description") or raw.get("video_description")
    if isinstance(title, str) and title.strip() and not description:
        return True
    for value in raw.values():
        if isinstance(value, str) and "pull-hls" in value:
            return True
    return False


def extract_candidate_video_id(raw: dict[str, Any]) -> str:
    return str(raw.get("id") or raw.get("aweme_id") or raw.get("awemeId") or "").strip()


def pick_first_non_empty_string(*candidates: Any) -> str:
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return ""


def extract_author_id(raw: dict[str, Any]) -> str:
    author = raw.get("author") or {}
    for key in ("id", "uid", "authorId", "author_id", "secUid", "sec_uid"):
        value = author.get(key)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized:
            return normalized
    return ""


def extract_author_handle(crawl: ModuleType, raw: dict[str, Any]) -> str:
    author = raw.get("author") or {}
    handle = pick_first_non_empty_string(
        author.get("uniqueId"),
        author.get("unique_id"),
        author.get("username"),
    )
    if handle:
        return handle
    return crawl.extract_author(raw)


def extract_author_display_name(raw: dict[str, Any]) -> str:
    author = raw.get("author") or {}
    return pick_first_non_empty_string(
        author.get("nickname"),
        author.get("displayName"),
        author.get("display_name"),
        author.get("name"),
    )


def extract_video_title(raw: dict[str, Any]) -> str:
    return pick_first_non_empty_string(raw.get("title"), raw.get("video_title"))


def extract_video_description(raw: dict[str, Any]) -> str:
    description = raw.get("desc") or raw.get("description") or raw.get("video_description") or ""
    if not isinstance(description, str):
        return str(description)
    return description


def coerce_optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_duration_sec(raw: dict[str, Any]) -> int:
    video = raw.get("video") or {}
    for candidate in (
        video.get("duration"),
        raw.get("duration"),
        raw.get("video_duration"),
    ):
        normalized = coerce_optional_int(candidate)
        if normalized is not None and normalized >= 0:
            return normalized
    return 0


def extract_url_value(candidate: Any) -> str:
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip()
    if isinstance(candidate, list):
        for item in candidate:
            extracted = extract_url_value(item)
            if extracted:
                return extracted
        return ""
    if isinstance(candidate, dict):
        for key in ("url", "uri"):
            extracted = extract_url_value(candidate.get(key))
            if extracted:
                return extracted
        for key in ("urlList", "url_list", "urls"):
            extracted = extract_url_value(candidate.get(key))
            if extracted:
                return extracted
    return ""


def extract_cover_url(raw: dict[str, Any]) -> str:
    video = raw.get("video") or {}
    image_post = raw.get("imagePost") or raw.get("image_post") or {}
    for candidate in (
        video.get("originCover"),
        video.get("cover"),
        video.get("dynamicCover"),
        image_post.get("cover"),
        raw.get("cover"),
    ):
        extracted = extract_url_value(candidate)
        if extracted:
            return extracted
    return ""


def extract_audio(raw: dict[str, Any]) -> dict[str, Any]:
    music = raw.get("music") or raw.get("musicInfo") or raw.get("music_info") or {}
    if not isinstance(music, dict):
        return {}
    audio_id = pick_first_non_empty_string(
        str(music.get("id") or "") if music.get("id") is not None else "",
        str(music.get("musicId") or "") if music.get("musicId") is not None else "",
        str(music.get("mid") or "") if music.get("mid") is not None else "",
    )
    title = pick_first_non_empty_string(music.get("title"), music.get("songName"), music.get("originalSoundTitle"))
    original_value = music.get("isOriginal")
    if original_value is None:
        original_value = music.get("is_original")
    if original_value is None and isinstance(music.get("original"), bool):
        original_value = music.get("original")
    if isinstance(original_value, str):
        is_original = original_value.strip().lower() in {"1", "true", "yes"}
    else:
        is_original = bool(original_value)
    if not audio_id and not title and original_value is None:
        return {}
    return {
        "audioId": audio_id,
        "title": title,
        "isOriginal": is_original,
    }


def extract_metrics_snapshot(raw: dict[str, Any], stats: dict[str, int]) -> dict[str, int]:
    stats_source = raw.get("statsV2") or raw.get("stats") or {}
    metrics = {
        "views": int(stats["plays"]),
        "likes": int(stats["likes"]),
        "shares": int(stats["shares"]),
        "comments": int(stats["comments"]),
    }
    favorites = None
    for key in ("collectCount", "collect_count", "favoriteCount", "favorite_count", "favouriteCount"):
        favorites = coerce_optional_int(stats_source.get(key))
        if favorites is not None:
            metrics["favorites"] = favorites
            break
    bookmarks = None
    for key in ("bookmarkCount", "bookmark_count", "saveCount", "save_count"):
        bookmarks = coerce_optional_int(stats_source.get(key))
        if bookmarks is not None:
            metrics["bookmarks"] = bookmarks
            break
    return metrics


def build_video_sample(
    raw: dict[str, Any],
    crawl: ModuleType,
    video_id: str,
    author_handle: str,
    author_display_name: str,
    author_id: str,
    created_at: Any,
    region: str,
    stats: dict[str, int],
    share_url: str,
    hashtags: list[str],
) -> dict[str, Any]:
    sample = {
        "videoSampleId": f"tt:{video_id}",
        "platformVideoId": video_id,
        "sourceSnapshotId": "",
        "publishedAt": created_at.isoformat().replace("+00:00", "Z"),
        "title": extract_video_title(raw),
        "desc": extract_video_description(raw),
        "hashtags": list(hashtags),
        "authorId": author_id,
        "authorHandle": author_handle,
        "authorDisplayName": author_display_name,
        "durationSec": extract_duration_sec(raw),
        "coverUrl": extract_cover_url(raw),
        "shareUrl": share_url,
        "metrics": extract_metrics_snapshot(raw, stats),
        "region": region,
        "rawMeta": {},
    }
    audio = extract_audio(raw)
    if audio:
        sample["audio"] = audio
    return sample


def build_snapshot_id(route_id: str, ranking_mode: str, market: str, captured_at: str) -> str:
    compact_captured_at = (
        captured_at.strip()
        .lower()
        .replace("-", "")
        .replace(":", "")
        .replace(".", "")
    )
    return f"snap.tiktok.{route_id}.{ranking_mode}.{market.lower()}.{compact_captured_at}"


def build_video_samples_artifact(
    entries: list[dict[str, Any]],
    route_id: str,
    ranking_mode: str,
    market: str,
    language: str,
    captured_at: str,
) -> dict[str, Any]:
    snapshot_id = build_snapshot_id(route_id, ranking_mode, market, captured_at)
    video_samples: list[dict[str, Any]] = []
    for entry in entries:
        sample = dict(entry.get("video_sample") or {})
        if not sample:
            continue
        sample["sourceSnapshotId"] = snapshot_id
        video_samples.append(sample)
    return {
        "schemaVersion": "discovery-video-samples.v1",
        "snapshotId": snapshot_id,
        "market": market,
        "language": language,
        "capturedAt": captured_at,
        "videoSamples": video_samples,
    }


def strip_internal_video_samples(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for entry in entries:
        candidate = dict(entry)
        candidate.pop("video_sample", None)
        cleaned.append(candidate)
    return cleaned


def make_empty_age_distribution() -> dict[str, int]:
    return {
        "unknown": 0,
        "lte_24h": 0,
        "lte_3d": 0,
        "lte_7d": 0,
        "lte_30d": 0,
        "gt_30d": 0,
    }


def bucket_age_hours(age_hours: float) -> str:
    if age_hours <= 24:
        return "lte_24h"
    if age_hours <= 24 * 3:
        return "lte_3d"
    if age_hours <= 24 * 7:
        return "lte_7d"
    if age_hours <= 24 * 30:
        return "lte_30d"
    return "gt_30d"


def build_age_distribution_from_raws(crawl: ModuleType, raws: list[dict[str, Any]], now: Any) -> dict[str, int]:
    distribution = make_empty_age_distribution()
    for raw in raws:
        created_at = crawl.parse_create_time(raw)
        if created_at is None:
            distribution["unknown"] += 1
            continue
        age_hours = max((now - created_at).total_seconds() / 3600.0, 0.0)
        distribution[bucket_age_hours(age_hours)] += 1
    return distribution


def build_age_distribution_from_entries(entries: list[dict[str, Any]]) -> dict[str, int]:
    distribution = make_empty_age_distribution()
    for entry in entries:
        try:
            age_hours = float(entry.get("age_hours", 0.0) or 0.0)
        except (TypeError, ValueError):
            distribution["unknown"] += 1
            continue
        distribution[bucket_age_hours(age_hours)] += 1
    return distribution


def build_rejection_preview(crawl: ModuleType, raw: dict[str, Any], reason: str) -> dict[str, Any]:
    stats = crawl.extract_stats(raw)
    preview_text = raw.get("desc") or raw.get("description") or raw.get("title") or raw.get("video_description") or ""
    if not isinstance(preview_text, str):
        preview_text = str(preview_text)
    return {
        "reason": reason,
        "video_id": extract_candidate_video_id(raw),
        "author": crawl.extract_author(raw),
        "create_time": crawl.extract_create_time(raw),
        "like_count": stats["likes"],
        "view_count": stats["plays"],
        "share_count": stats["shares"],
        "has_stream_markers": looks_like_live_or_stream(raw),
        "preview": preview_text[:160],
    }


def classify_candidate(
    crawl: ModuleType,
    raw: dict[str, Any],
    category: dict[str, Any],
    region_filter: str,
    min_created_at: Any,
    now: Any,
    min_likes_threshold: int,
    enforce_time_window: bool = True,
) -> tuple[dict[str, Any] | None, str]:
    video_id = extract_candidate_video_id(raw)
    if not video_id:
        return None, "missing_video_id"
    if looks_like_live_or_stream(raw):
        return None, "live_or_stream"

    created_at = crawl.parse_create_time(raw)
    if created_at is None:
        return None, "missing_or_old_create_time"
    if enforce_time_window and created_at < min_created_at:
        return None, "missing_or_old_create_time"

    region = crawl.extract_region(raw)
    if region_filter and region and region != region_filter:
        return None, "region_filtered"

    stats = crawl.extract_stats(raw)
    if stats["likes"] < 0:
        return None, "negative_like_count"
    if stats["likes"] < min_likes_threshold:
        return None, "below_min_likes"

    author = extract_author_handle(crawl, raw)
    author_display_name = extract_author_display_name(raw)
    author_id = extract_author_id(raw)
    metrics = crawl.build_metrics(stats, created_at, now)
    description = extract_video_description(raw)
    hashtags = crawl.extract_hashtags(raw)
    share_url = crawl.build_video_url(raw, author, video_id)
    video_sample = build_video_sample(
        raw,
        crawl,
        video_id,
        author,
        author_display_name,
        author_id,
        created_at,
        region,
        stats,
        share_url,
        hashtags,
    )
    entry = {
        "video_id": video_id,
        "url": share_url,
        "description": description,
        "author": author,
        "author_id": author_id,
        "author_display_name": author_display_name,
        "category_id": category["category_id"],
        "category_name": category["category_name"],
        "source_ids": list(category["source_ids"]),
        "source_labels": list(category["source_labels"]),
        "create_time": created_at.isoformat().replace("+00:00", "Z"),
        "region": region,
        "view_count": stats["plays"],
        "like_count": stats["likes"],
        "comment_count": stats["comments"],
        "share_count": stats["shares"],
        "hashtags": hashtags,
        "duration_sec": video_sample["durationSec"],
        "cover_url": video_sample["coverUrl"],
        "share_url": video_sample["shareUrl"],
        "video_sample": video_sample,
        "age_hours": metrics["age_hours"],
        "engagement": metrics["engagement"],
        "quality": metrics["quality"],
        "velocity": metrics["velocity"],
        "score_exposure": metrics["score_exposure"],
        "score_engagement": metrics["score_engagement"],
        "score_velocity": metrics["score_velocity"],
        "score_quality": metrics["score_quality"],
    }
    return entry, "accepted"


def make_metric_summary(videos: list[dict[str, Any]], top_n: int) -> dict[str, Any]:
    if not videos:
        return {
            "retained_videos": 0,
            "top_slice": 0,
            "unique_authors": 0,
            "unique_top_authors": 0,
            "median_view_count": 0,
            "median_like_count": 0,
            "median_comment_count": 0,
            "median_share_count": 0,
            "median_engagement": 0.0,
            "median_hot_score": 0.0,
            "median_age_hours": 0.0,
        }
    top_videos = videos[: min(top_n, len(videos))]

    def median_int(field: str) -> int:
        return int(statistics.median(int(item.get(field, 0) or 0) for item in top_videos))

    def median_float(field: str) -> float:
        return round(statistics.median(float(item.get(field, 0.0) or 0.0) for item in top_videos), 6)

    return {
        "retained_videos": len(videos),
        "top_slice": len(top_videos),
        "unique_authors": len({item.get("author") for item in videos if item.get("author")}),
        "unique_top_authors": len({item.get("author") for item in top_videos if item.get("author")}),
        "median_view_count": median_int("view_count"),
        "median_like_count": median_int("like_count"),
        "median_comment_count": median_int("comment_count"),
        "median_share_count": median_int("share_count"),
        "median_engagement": median_float("engagement"),
        "median_hot_score": median_float("hot_score"),
        "median_age_hours": median_float("age_hours"),
    }


def normalize_score(value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        return 1.0
    return (value - minimum) / (maximum - minimum)


def score_direct_hot_candidates(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not entries:
        return []
    scored = [dict(entry) for entry in entries]
    bounds = {
        field: (
            min(float(item.get(field, 0.0) or 0.0) for item in scored),
            max(float(item.get(field, 0.0) or 0.0) for item in scored),
        )
        for field in (
            "score_exposure",
            "score_engagement",
            "score_velocity",
            "score_quality",
            "age_hours",
        )
    }
    for item in scored:
        exposure = normalize_score(float(item.get("score_exposure", 0.0) or 0.0), *bounds["score_exposure"])
        engagement = normalize_score(float(item.get("score_engagement", 0.0) or 0.0), *bounds["score_engagement"])
        velocity = normalize_score(float(item.get("score_velocity", 0.0) or 0.0), *bounds["score_velocity"])
        quality = normalize_score(float(item.get("score_quality", 0.0) or 0.0), *bounds["score_quality"])
        freshness = 1.0 - normalize_score(float(item.get("age_hours", 0.0) or 0.0), *bounds["age_hours"])
        item["absolute_hot_score"] = round(
            0.40 * exposure + 0.35 * engagement + 0.15 * velocity + 0.10 * quality,
            6,
        )
        item["fresh_hot_score"] = round(
            0.20 * exposure + 0.25 * engagement + 0.30 * velocity + 0.10 * quality + 0.15 * freshness,
            6,
        )
    return scored


def rank_direct_hot_candidates(
    entries: list[dict[str, Any]],
    keep: int,
    per_author_limit: int,
    mode: str,
) -> list[dict[str, Any]]:
    if not entries:
        return []
    score_field = "absolute_hot_score" if mode == "absolute_hot" else "fresh_hot_score"
    candidates = [dict(entry) for entry in entries]
    candidates.sort(
        key=lambda item: (
            -float(item.get(score_field, 0.0) or 0.0),
            -float(item.get("engagement", 0.0) or 0.0),
            -int(item.get("view_count", 0) or 0),
            float(item.get("age_hours", 0.0) or 0.0),
        )
    )
    kept: list[dict[str, Any]] = []
    by_author: dict[str, int] = {}
    for item in candidates:
        author = str(item.get("author") or "")
        if author and by_author.get(author, 0) >= per_author_limit:
            continue
        if author:
            by_author[author] = by_author.get(author, 0) + 1
        candidate = dict(item)
        candidate["hot_score"] = round(float(candidate.get(score_field, 0.0) or 0.0), 6)
        candidate["ranking_mode"] = mode
        kept.append(candidate)
        if len(kept) >= keep:
            break
    for index, item in enumerate(kept, start=1):
        item["ranking_rank"] = index
        if mode == "absolute_hot":
            item["route_rank"] = index
        item.pop("score_exposure", None)
        item.pop("score_engagement", None)
        item.pop("score_velocity", None)
        item.pop("score_quality", None)
    return kept


def route_sort_key(video: dict[str, Any]) -> tuple[float, float, int, float]:
    return (
        float(video.get("hot_score", 0.0) or 0.0),
        float(video.get("engagement", 0.0) or 0.0),
        int(video.get("view_count", 0) or 0),
        -float(video.get("age_hours", 0.0) or 0.0),
    )


def dedupe_route_videos(videos: list[dict[str, Any]], route_id: str) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for original in videos:
        video = dict(original)
        video_id = str(video.get("video_id") or "").strip()
        if not video_id:
            continue
        current = merged.get(video_id)
        categories = set(video.get("matched_categories") or [])
        category_name = video.get("topic_category_name") or video.get("category_name") or ""
        if category_name:
            categories.add(category_name)
        source_ids = set(video.get("source_ids") or [])
        source_labels = set(video.get("source_labels") or [])
        if current is None:
            candidate = dict(video)
            candidate["matched_categories"] = sorted(categories)
            candidate["source_ids"] = sorted(source_ids)
            candidate["source_labels"] = sorted(source_labels)
            candidate["route_id"] = route_id
            merged[video_id] = candidate
            continue
        current_categories = set(current.get("matched_categories") or [])
        current_categories.update(categories)
        current["matched_categories"] = sorted(current_categories)
        current_source_ids = set(current.get("source_ids") or [])
        current_source_ids.update(source_ids)
        current["source_ids"] = sorted(current_source_ids)
        current_source_labels = set(current.get("source_labels") or [])
        current_source_labels.update(source_labels)
        current["source_labels"] = sorted(current_source_labels)
        if route_sort_key(video) > route_sort_key(current):
            replacement = dict(video)
            replacement["matched_categories"] = sorted(current_categories)
            replacement["source_ids"] = sorted(current_source_ids)
            replacement["source_labels"] = sorted(current_source_labels)
            replacement["route_id"] = route_id
            merged[video_id] = replacement
    ranked = sorted(merged.values(), key=route_sort_key, reverse=True)
    for index, video in enumerate(ranked, start=1):
        video["route_rank"] = index
    return ranked


def pairwise_overlap(routes: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for index, left in enumerate(routes):
        for right in routes[index + 1 :]:
            left_top = {
                str(video.get("video_id"))
                for video in left.get("videos", [])[: min(top_n, len(left.get("videos", [])))]
                if video.get("video_id")
            }
            right_top = {
                str(video.get("video_id"))
                for video in right.get("videos", [])[: min(top_n, len(right.get("videos", [])))]
                if video.get("video_id")
            }
            overlap = sorted(left_top & right_top)
            reports.append(
                {
                    "left_route_id": left["route_id"],
                    "right_route_id": right["route_id"],
                    "left_top_n": len(left_top),
                    "right_top_n": len(right_top),
                    "shared_top_n": len(overlap),
                    "shared_video_ids": overlap,
                }
            )
    return reports


def normalize_route_error(exc: BaseException) -> str:
    if isinstance(exc, SystemExit):
        code = exc.code
        if isinstance(code, str) and code.strip():
            return code.strip()
        if code not in (None, 0):
            return f"SystemExit({code})"
        return "SystemExit"
    message = str(exc).strip()
    if message:
        return message
    return exc.__class__.__name__


async def run_topic_first(crawl: ModuleType, args: argparse.Namespace) -> dict[str, Any]:
    crawl_args = build_base_crawl_args(args)
    crawl_args.category_limit = args.topic_category_limit
    crawl_args.per_query = args.topic_per_query
    crawl_args.per_category = args.topic_per_category
    try:
        payload = await crawl.main_async(crawl_args)
    except BaseException as exc:
        return {
            "route_id": "topic-first",
            "route_label": "Official topic-first via discovered categories",
            "status": "query_failed",
            "strategy_type": "topic-first",
            "observed_at": crawl.now_utc().isoformat().replace("+00:00", "Z"),
            "window": args.window,
            "region": args.region.strip().upper() or "GLOBAL",
            "raw_payload": {},
            "raw_candidates_seen": 0,
            "eligible_candidates": 0,
            "threshold_mode": "",
            "effective_thresholds": {},
            "filter_diagnostics": make_empty_filter_diagnostics(),
            "error": normalize_route_error(exc),
            "videos": [],
            "summary": make_metric_summary([], args.top_n),
        }
    flattened: list[dict[str, Any]] = []
    for category in payload.get("categories", []):
        for video in category.get("top_videos", []):
            item = dict(video)
            item["topic_category_id"] = category.get("category_id", "")
            item["topic_category_name"] = category.get("category_name", "")
            flattened.append(item)
    deduped = dedupe_route_videos(flattened, "topic-first")
    return {
        "route_id": "topic-first",
        "route_label": "Official topic-first via discovered categories",
        "status": "ok" if payload.get("categories_succeeded", 0) > 0 else "empty",
        "strategy_type": "topic-first",
        "observed_at": payload.get("observed_at", ""),
        "window": payload.get("window", args.window),
        "region": payload.get("region", args.region.strip().upper() or "GLOBAL"),
        "raw_payload": payload,
        "raw_candidates_seen": sum(int(category.get("total_candidates_seen", 0) or 0) for category in payload.get("categories", [])),
        "eligible_candidates": sum(int(category.get("total_candidates_eligible", 0) or 0) for category in payload.get("categories", [])),
        "threshold_mode": payload.get("threshold_mode", ""),
        "effective_thresholds": payload.get("effective_thresholds", {}),
        "filter_diagnostics": {
            "seen": sum(int(category.get("total_candidates_seen", 0) or 0) for category in payload.get("categories", [])),
            "accepted": sum(int(category.get("total_candidates_eligible", 0) or 0) for category in payload.get("categories", [])),
            "missing_video_id": 0,
            "live_or_stream": 0,
            "missing_or_old_create_time": 0,
            "region_filtered": 0,
            "below_min_likes": 0,
            "negative_like_count": 0,
            "other_rejected": 0,
        },
        "error": "",
        "videos": deduped,
        "summary": make_metric_summary(deduped, args.top_n),
    }


async def collect_direct_hot_raws(
    crawl: ModuleType,
    api: Any,
    count: int,
    session_index: int | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    kwargs: dict[str, Any] = {}
    if session_index is not None:
        kwargs["session_index"] = session_index
    async for video in api.trending.videos(count=count, **kwargs):
        raw = crawl.extract_video_dict(video)
        if isinstance(raw, dict):
            results.append(raw)
    return results


def summarize_session_contribution(batch_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: dict[int, dict[str, int]] = {}
    for report in batch_reports:
        idx = int(report.get("session_index", 0))
        bucket = summary.setdefault(
            idx,
            {"session_index": idx, "batches": 0, "raw_candidates_seen": 0, "new_unique_video_ids": 0},
        )
        bucket["batches"] += 1
        bucket["raw_candidates_seen"] += int(report.get("raw_candidates_seen", 0))
        bucket["new_unique_video_ids"] += int(report.get("new_unique_video_ids", 0))
    return [summary[k] for k in sorted(summary.keys())]


async def collect_direct_hot_raw_batches(
    crawl: ModuleType,
    api: Any,
    batch_size: int,
    batches: int,
    pause_seconds: float,
    num_sessions: int = 1,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    raws: list[dict[str, Any]] = []
    batch_reports: list[dict[str, Any]] = []
    unique_ids: set[str] = set()
    effective_sessions = max(1, num_sessions)
    for index in range(batches):
        session_index = index % effective_sessions
        batch = await collect_direct_hot_raws(
            crawl,
            api,
            batch_size,
            session_index=session_index if effective_sessions > 1 else None,
        )
        raws.extend(batch)
        batch_ids = {video_id for video_id in (extract_candidate_video_id(raw) for raw in batch) if video_id}
        previous_unique_count = len(unique_ids)
        unique_ids.update(batch_ids)
        batch_reports.append(
            {
                "batch_index": index + 1,
                "session_index": session_index,
                "raw_candidates_seen": len(batch),
                "unique_video_ids_in_batch": len(batch_ids),
                "new_unique_video_ids": len(unique_ids) - previous_unique_count,
            }
        )
        if pause_seconds > 0 and index + 1 < batches:
            await asyncio.sleep(pause_seconds)
    return raws, batch_reports, len(unique_ids)


async def collect_direct_hot_with_recovery(
    crawl: ModuleType,
    crawl_args: argparse.Namespace,
    api: Any,
    effective_headful: bool,
    requested_headful: bool,
    direct_count: int,
    direct_batches: int,
    direct_batch_pause_seconds: float,
    num_sessions: int = 1,
    reopen_api: Any = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, Any, bool, str, str]:
    raws, batch_reports, raw_unique_ids = await collect_direct_hot_raw_batches(
        crawl,
        api,
        direct_count,
        direct_batches,
        direct_batch_pause_seconds,
        num_sessions=num_sessions,
    )
    sampling_strategy = "requested_batches"
    fallback_applied = False
    fallback_reason = ""

    if not raws and not effective_headful and not requested_headful:
        fallback_applied = True
        fallback_reason = "empty trending feed in headless mode"
        await crawl.close_api_session(api)
        if reopen_api is not None:
            api = await reopen_api(True)
        else:
            api = await crawl.open_api_session(crawl_args, True)
        effective_headful = True
        raws, batch_reports, raw_unique_ids = await collect_direct_hot_raw_batches(
            crawl,
            api,
            direct_count,
            direct_batches,
            direct_batch_pause_seconds,
            num_sessions=num_sessions,
        )
        sampling_strategy = "headful_retry_after_empty_headless"

    safe_batch_size = min(direct_count, 30)
    if not raws and direct_count > safe_batch_size:
        raws, batch_reports, raw_unique_ids = await collect_direct_hot_raw_batches(
            crawl,
            api,
            safe_batch_size,
            direct_batches,
            direct_batch_pause_seconds,
            num_sessions=num_sessions,
        )
        sampling_strategy = f"safe_batch_size_retry_{safe_batch_size}"

    return raws, batch_reports, raw_unique_ids, api, effective_headful, fallback_applied, fallback_reason, sampling_strategy


def evaluate_direct_hot_candidates(
    crawl: ModuleType,
    raws: list[dict[str, Any]],
    route_category: dict[str, Any],
    region_filter: str,
    min_created_at: Any,
    observed_at_dt: Any,
    effective_min_likes: int,
    enforce_time_window: bool,
) -> tuple[dict[str, dict[str, Any]], dict[str, int], dict[str, list[dict[str, Any]]]]:
    merged: dict[str, dict[str, Any]] = {}
    diagnostics = make_empty_filter_diagnostics()
    rejection_preview: dict[str, list[dict[str, Any]]] = {}
    diagnostics["seen"] = len(raws)
    for raw in raws:
        entry, reason = classify_candidate(
            crawl,
            raw,
            route_category,
            region_filter,
            min_created_at,
            observed_at_dt,
            effective_min_likes,
            enforce_time_window=enforce_time_window,
        )
        diagnostics[reason] = diagnostics.get(reason, 0) + 1
        if not entry:
            if reason != "accepted":
                bucket = rejection_preview.setdefault(reason, [])
                if len(bucket) < 3:
                    bucket.append(build_rejection_preview(crawl, raw, reason))
            continue
        current = merged.get(entry["video_id"])
        if current is None or entry["engagement"] > current["engagement"]:
            merged[entry["video_id"]] = entry
    return merged, diagnostics, rejection_preview


async def run_direct_hot(crawl: ModuleType, args: argparse.Namespace) -> dict[str, Any]:
    crawl_args = build_base_crawl_args(args)
    crawl_args.category_limit = 0
    crawl_args.per_query = args.direct_count
    crawl_args.per_category = args.direct_keep
    effective_min_likes, threshold_mode = crawl.resolve_effective_min_likes(crawl_args)
    min_created_at = crawl.now_utc() - crawl.window_to_delta(args.window)
    region_filter = args.region.strip().upper()
    requested_headful = args.headful
    effective_headful = requested_headful
    fallback_applied = False
    fallback_reason = ""
    seen = 0
    raw_unique_ids = 0
    merged: dict[str, dict[str, Any]] = {}
    diagnostics = make_empty_filter_diagnostics()
    age_window_mode = "requested_window_strict"
    batch_reports: list[dict[str, Any]] = []
    rejection_preview: dict[str, list[dict[str, Any]]] = {}
    raw_age_distribution = make_empty_age_distribution()
    sampling_strategy = "requested_batches"
    captured_at = ""
    route_category = {
        "category_id": "trendingfeed",
        "category_name": "Trending Feed",
        "source_ids": ["tiktokapi-trending-feed"],
        "source_labels": ["TikTokApi Trending Feed"],
    }
    ms_tokens_csv = (args.ms_tokens or "").strip()
    if ms_tokens_csv:
        ms_token_list = [tok.strip() for tok in ms_tokens_csv.split(",") if tok.strip()]
    elif args.ms_token:
        ms_token_list = [args.ms_token]
    else:
        ms_token_list = []
    num_sessions = max(1, args.num_sessions)

    async def open_api(headful: bool) -> Any:
        if num_sessions <= 1:
            return await crawl.open_api_session(crawl_args, headful)
        api_instance = crawl.TikTokApi()
        session_kwargs: dict[str, Any] = {
            "num_sessions": num_sessions,
            "sleep_after": 3,
            "browser": args.browser,
            "headless": not headful,
        }
        if ms_token_list:
            session_kwargs["ms_tokens"] = ms_token_list
        await api_instance.create_sessions(**session_kwargs)
        return api_instance

    api = await open_api(effective_headful)
    try:
        observed_at_dt = crawl.now_utc()
        captured_at = observed_at_dt.isoformat().replace("+00:00", "Z")
        try:
            raws, batch_reports, raw_unique_ids, api, recovered_headful, recovered_fallback_applied, recovered_fallback_reason, sampling_strategy = await collect_direct_hot_with_recovery(
                crawl,
                crawl_args,
                api,
                effective_headful,
                requested_headful,
                args.direct_count,
                args.direct_batches,
                args.direct_batch_pause_seconds,
                num_sessions=num_sessions,
                reopen_api=open_api,
            )
            effective_headful = recovered_headful
            fallback_applied = fallback_applied or recovered_fallback_applied
            if recovered_fallback_reason:
                fallback_reason = recovered_fallback_reason
        except Exception as exc:
            error_text = str(exc)
            if crawl.should_retry_with_headful(error_text) and not effective_headful:
                fallback_applied = True
                fallback_reason = error_text
                await crawl.close_api_session(api)
                api = await open_api(True)
                effective_headful = True
                raws, batch_reports, raw_unique_ids, api, recovered_headful, recovered_fallback_applied, recovered_fallback_reason, sampling_strategy = await collect_direct_hot_with_recovery(
                    crawl,
                    crawl_args,
                    api,
                    effective_headful,
                    requested_headful,
                    args.direct_count,
                    args.direct_batches,
                    args.direct_batch_pause_seconds,
                    num_sessions=num_sessions,
                    reopen_api=open_api,
                )
                effective_headful = recovered_headful
                fallback_applied = fallback_applied or recovered_fallback_applied
                if recovered_fallback_reason:
                    fallback_reason = recovered_fallback_reason
            else:
                market = region_filter or "GLOBAL"
                return {
                    "route_id": "direct-hot",
                    "route_label": "Direct absolute-hot and fresh-hot videos via TikTokApi trending feed",
                    "status": "query_failed",
                    "strategy_type": "direct-hot",
                    "observed_at": captured_at or crawl.now_utc().isoformat().replace("+00:00", "Z"),
                    "window": args.window,
                    "region": region_filter or "GLOBAL",
                    "raw_payload": {},
                    "raw_candidates_seen": 0,
                    "raw_candidates_unique_ids": 0,
                    "eligible_candidates": 0,
                    "threshold_mode": threshold_mode,
                    "effective_thresholds": {"min_likes": effective_min_likes},
                    "filter_diagnostics": diagnostics,
                    "sampling": {"batch_reports": [], "direct_batches": args.direct_batches, "direct_batch_pause_seconds": args.direct_batch_pause_seconds, "sampling_strategy": sampling_strategy},
                    "session_mode_requested": "headful" if requested_headful else "headless",
                    "session_mode_effective": "headful" if effective_headful else "headless",
                    "session_fallback_applied": fallback_applied,
                    "session_fallback_reason": fallback_reason,
                    "error": error_text,
                    "videos": [],
                    "absolute_hot_video_samples": build_video_samples_artifact([], "direct-hot", "absolute_hot", market, args.language, captured_at or crawl.now_utc().isoformat().replace("+00:00", "Z")),
                    "fresh_hot_videos": [],
                    "fresh_hot_video_samples": build_video_samples_artifact([], "direct-hot", "fresh_hot", market, args.language, captured_at or crawl.now_utc().isoformat().replace("+00:00", "Z")),
                    "fresh_hot_summary": make_metric_summary([], args.top_n),
                    "candidate_age_distribution": make_empty_age_distribution(),
                    "retained_age_distribution": make_empty_age_distribution(),
                    "rejection_preview": {},
                    "summary": make_metric_summary([], args.top_n),
                }
        seen = len(raws)
        raw_age_distribution = build_age_distribution_from_raws(crawl, raws, observed_at_dt)
        merged, diagnostics, rejection_preview = evaluate_direct_hot_candidates(
            crawl,
            raws,
            route_category,
            region_filter,
            min_created_at,
            observed_at_dt,
            effective_min_likes,
            True,
        )
        if not merged:
            fallback_min_created_at = observed_at_dt - crawl.window_to_delta("30d")
            relaxed_merged, relaxed_diagnostics, relaxed_preview = evaluate_direct_hot_candidates(
                crawl,
                raws,
                route_category,
                region_filter,
                fallback_min_created_at,
                observed_at_dt,
                effective_min_likes,
                True,
            )
            if relaxed_merged:
                merged = relaxed_merged
                diagnostics = relaxed_diagnostics
                rejection_preview = relaxed_preview
                age_window_mode = "fallback_30d"
            else:
                any_age_merged, any_age_diagnostics, any_age_preview = evaluate_direct_hot_candidates(
                    crawl,
                    raws,
                    route_category,
                    region_filter,
                    fallback_min_created_at,
                    observed_at_dt,
                    effective_min_likes,
                    False,
                )
                if any_age_merged:
                    merged = any_age_merged
                    diagnostics = any_age_diagnostics
                    rejection_preview = any_age_preview
                    age_window_mode = "fallback_any_age"
        scored_candidates = score_direct_hot_candidates(list(merged.values()))
        absolute_hot = rank_direct_hot_candidates(scored_candidates, args.direct_keep, args.per_author_limit, "absolute_hot")
        fresh_hot = rank_direct_hot_candidates(scored_candidates, args.direct_keep, args.per_author_limit, "fresh_hot")
    finally:
        await crawl.close_api_session(api)
    retained_age_distribution = build_age_distribution_from_entries(absolute_hot)
    market = region_filter or "GLOBAL"
    absolute_hot_video_samples = build_video_samples_artifact(
        absolute_hot,
        "direct-hot",
        "absolute_hot",
        market,
        args.language,
        captured_at or crawl.now_utc().isoformat().replace("+00:00", "Z"),
    )
    fresh_hot_video_samples = build_video_samples_artifact(
        fresh_hot,
        "direct-hot",
        "fresh_hot",
        market,
        args.language,
        captured_at or crawl.now_utc().isoformat().replace("+00:00", "Z"),
    )
    absolute_hot_public = strip_internal_video_samples(absolute_hot)
    fresh_hot_public = strip_internal_video_samples(fresh_hot)
    raw_payload = {
        "run_mode": "direct_hot_tiktokapi_trending_feed",
        "window": args.window,
        "age_window_mode": age_window_mode,
        "region": market,
        "language": args.language,
        "requested_count": args.direct_count,
        "direct_batches": args.direct_batches,
        "direct_batch_pause_seconds": args.direct_batch_pause_seconds,
        "kept_count": args.direct_keep,
        "raw_candidates_seen": seen,
        "raw_candidates_unique_ids": raw_unique_ids,
        "eligible_candidates": len(merged),
        "threshold_mode": threshold_mode,
        "effective_thresholds": {"min_likes": effective_min_likes},
        "filter_diagnostics": diagnostics,
        "candidate_age_distribution": raw_age_distribution,
        "retained_age_distribution": retained_age_distribution,
        "rejection_preview": rejection_preview,
        "sampling": {
            "batch_reports": batch_reports,
            "sampling_strategy": sampling_strategy,
            "num_sessions": num_sessions,
            "ms_tokens_count": len(ms_token_list),
            "session_contribution": summarize_session_contribution(batch_reports),
        },
        "session_mode_requested": "headful" if requested_headful else "headless",
        "session_mode_effective": "headful" if effective_headful else "headless",
        "session_fallback_applied": fallback_applied,
        "session_fallback_reason": fallback_reason,
    }
    return {
        "route_id": "direct-hot",
        "route_label": "Direct absolute-hot and fresh-hot videos via TikTokApi trending feed",
        "status": "ok" if absolute_hot_public else "empty",
        "strategy_type": "direct-hot",
        "observed_at": captured_at or crawl.now_utc().isoformat().replace("+00:00", "Z"),
        "window": args.window,
        "age_window_mode": age_window_mode,
        "region": market,
        "language": args.language,
        "raw_payload": raw_payload,
        "raw_candidates_seen": seen,
        "raw_candidates_unique_ids": raw_unique_ids,
        "eligible_candidates": len(merged),
        "threshold_mode": threshold_mode,
        "effective_thresholds": {"min_likes": effective_min_likes},
        "filter_diagnostics": diagnostics,
        "candidate_age_distribution": raw_age_distribution,
        "retained_age_distribution": retained_age_distribution,
        "rejection_preview": rejection_preview,
        "sampling": {
            "direct_batches": args.direct_batches,
            "direct_batch_pause_seconds": args.direct_batch_pause_seconds,
            "sampling_strategy": sampling_strategy,
            "batch_reports": batch_reports,
        },
        "session_mode_requested": raw_payload["session_mode_requested"],
        "session_mode_effective": raw_payload["session_mode_effective"],
        "session_fallback_applied": fallback_applied,
        "session_fallback_reason": fallback_reason,
        "error": "",
        "videos": absolute_hot_public,
        "absolute_hot_video_samples": absolute_hot_video_samples,
        "fresh_hot_videos": fresh_hot_public,
        "fresh_hot_video_samples": fresh_hot_video_samples,
        "fresh_hot_summary": make_metric_summary(fresh_hot_public, args.top_n),
        "summary": make_metric_summary(absolute_hot_public, args.top_n),
    }


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    crawl = load_crawl_module()
    routes: list[dict[str, Any]] = []
    if "topic-first" in args.route:
        routes.append(await run_topic_first(crawl, args))
    if "direct-hot" in args.route:
        routes.append(await run_direct_hot(crawl, args))
    ranked_route_summaries = sorted(
        [
            {
                "route_id": route["route_id"],
                "route_label": route["route_label"],
                "status": route["status"],
                **route["summary"],
            }
            for route in routes
        ],
        key=lambda item: (
            int(item.get("retained_videos", 0) or 0),
            float(item.get("median_hot_score", 0.0) or 0.0),
            int(item.get("median_view_count", 0) or 0),
        ),
        reverse=True,
    )
    return {
        "experiment_type": "tiktok_hot_video_bakeoff",
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "window": args.window,
        "region": args.region.strip().upper() or "GLOBAL",
        "language": args.language,
        "routes_requested": list(args.route),
        "top_n": args.top_n,
        "routes": routes,
        "comparison": {
            "ranked_route_summaries": ranked_route_summaries,
            "pairwise_top_n_overlap": pairwise_overlap(routes, args.top_n),
        },
    }


def main() -> None:
    args = parse_args()
    payload = asyncio.run(main_async(args))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print(
        f"Saved bake-off results for {len(payload['routes'])} route(s) to {args.out}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
