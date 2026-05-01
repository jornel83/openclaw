#!/usr/bin/env python3
import argparse
import asyncio
import html
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from TikTokApi import TikTokApi
except ImportError:
    print(
        "Missing dependency: TikTokApi. Install with `pip install TikTokApi` and `python -m playwright install chromium`.",
        file=sys.stderr,
    )
    sys.exit(1)

OFFICIAL_SOURCE_SPECS = [
    {
        "id": "discover-trending-topics",
        "url": "https://www.tiktok.com/discover/trending-topics?lang=en",
        "label": "TikTok Discover Trending Topics",
    },
    {
        "id": "discover-whats-trending-now",
        "url": "https://www.tiktok.com/discover/whats-trending-now",
        "label": "TikTok Discover What's Trending Now",
    },
    {
        "id": "creative-center-popular-hashtags",
        "url": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en",
        "label": "TikTok Creative Center Popular Hashtags",
    },
]

HASHTAG_RE = re.compile(r"#([A-Za-z0-9_]{2,64})")
TAG_PATH_RE = re.compile(r"/tag/([A-Za-z0-9_-]{2,64})")
TOKEN_CANDIDATE_RE = re.compile(r"#([A-Za-z0-9_]{2,64})|/tag/([A-Za-z0-9_-]{2,64})")
RETRYABLE_HEADFUL_ERROR_PATTERNS = (
    "empty response",
    "detecting you're a bot",
    "consider using a proxy",
)

DEFAULT_MIN_LIKES_BY_WINDOW = {
    "3h": 30000,
    "6h": 20000,
    "24h": 10000,
    "7d": 3000,
    "30d": 1000,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Crawl TikTok hot videos by official trend/topic categories"
    )
    parser.add_argument(
        "--window",
        default="24h",
        choices=["3h", "6h", "24h", "7d", "30d"],
        help="Only include videos published within this time window",
    )
    parser.add_argument(
        "--category-limit",
        type=int,
        default=10,
        help="Maximum number of official categories/topics to crawl",
    )
    parser.add_argument(
        "--per-query",
        type=int,
        default=40,
        help="Maximum number of videos to request from TikTokApi for each discovered category/topic",
    )
    parser.add_argument(
        "--per-category",
        "--count",
        type=int,
        default=10,
        help="Maximum number of top-ranked videos to keep for each category/topic",
    )
    parser.add_argument(
        "--per-author-limit",
        type=int,
        default=2,
        help="Maximum number of retained videos per author within a category",
    )
    parser.add_argument("--min-likes", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--category", default="", help=argparse.SUPPRESS)
    parser.add_argument("--hashtag", action="append", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--creator", action="append", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--region", default="", help="Best-effort region filter, for example US")
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Only discover and rank official categories/topics; skip TikTokApi video crawling",
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
        "--source-timeout",
        type=int,
        default=20,
        help="Timeout in seconds for fetching official source pages",
    )
    parser.add_argument("--out", required=True, help="Output JSON file path")
    args = parser.parse_args()
    if args.category or args.hashtag or args.creator:
        print(
            "Ignoring legacy topic/category inputs. This workflow now uses official TikTok category/topic discovery only.",
            file=sys.stderr,
        )
    return args


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def normalize_token(raw: str) -> str:
    token = raw.strip().lower().lstrip("#@").replace(" ", "")
    token = re.sub(r"[^a-z0-9_]", "", token)
    return token


def is_hex_noise(token: str) -> bool:
    return len(token) in {3, 6, 8} and all(ch in "0123456789abcdef" for ch in token)


def fetch_text(url: str, timeout: int) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="ignore")


def extract_hashtags_from_text(text: str) -> tuple[Counter[str], dict[str, int]]:
    decoded = html.unescape(text)
    hashtags: Counter[str] = Counter()
    first_seen_order: dict[str, int] = {}
    for match in TOKEN_CANDIDATE_RE.finditer(decoded):
        hashtag_match = match.group(1)
        tag_path_match = match.group(2)
        raw_token = hashtag_match or ""
        if tag_path_match:
            raw_token = tag_path_match.replace("-", "")
        token = normalize_token(raw_token)
        if token and not is_hex_noise(token):
            hashtags[token] += 1
            if token not in first_seen_order:
                first_seen_order[token] = len(first_seen_order)
    return hashtags, first_seen_order


def discover_official_categories(category_limit: int, timeout: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    discovered: dict[str, dict[str, Any]] = {}
    source_reports: list[dict[str, Any]] = []

    for source_index, spec in enumerate(OFFICIAL_SOURCE_SPECS):
        try:
            text = fetch_text(spec["url"], timeout=timeout)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            source_reports.append(
                {
                    "source_id": spec["id"],
                    "label": spec["label"],
                    "url": spec["url"],
                    "status": "error",
                    "error": str(exc),
                    "hashtags_found": 0,
                }
            )
            continue

        counts, first_seen_orders = extract_hashtags_from_text(text)
        source_reports.append(
            {
                "source_id": spec["id"],
                "label": spec["label"],
                "url": spec["url"],
                "status": "ok",
                "error": "",
                "hashtags_found": len(counts),
                "top_hashtags_preview": [
                    f"#{token}"
                    for token, _ in sorted(first_seen_orders.items(), key=lambda item: item[1])[:5]
                ],
            }
        )
        for token, mentions in counts.items():
            entry = discovered.setdefault(
                token,
                {
                    "category_id": token,
                    "category_name": f"#{token}",
                    "query_value": token,
                    "source_ids": [],
                    "source_urls": [],
                    "source_labels": [],
                    "mentions": 0,
                    "first_seen_source_index": source_index,
                    "first_seen_source_id": spec["id"],
                    "first_seen_source_label": spec["label"],
                    "first_seen_source_order": first_seen_orders[token],
                },
            )
            entry["mentions"] += mentions
            if spec["id"] not in entry["source_ids"]:
                entry["source_ids"].append(spec["id"])
                entry["source_urls"].append(spec["url"])
                entry["source_labels"].append(spec["label"])
            if (source_index, first_seen_orders[token]) < (
                entry["first_seen_source_index"],
                entry["first_seen_source_order"],
            ):
                entry["first_seen_source_index"] = source_index
                entry["first_seen_source_id"] = spec["id"]
                entry["first_seen_source_label"] = spec["label"]
                entry["first_seen_source_order"] = first_seen_orders[token]

    categories = list(discovered.values())
    categories.sort(
        key=lambda item: (
            -len(item["source_ids"]),
            item["first_seen_source_index"],
            item["first_seen_source_order"],
            -item["mentions"],
        )
    )
    return categories[:category_limit], source_reports


def window_to_delta(raw: str) -> timedelta:
    if raw.endswith("h"):
        return timedelta(hours=int(raw[:-1]))
    if raw.endswith("d"):
        return timedelta(days=int(raw[:-1]))
    raise ValueError(f"Unsupported window: {raw}")


def extract_video_dict(video: Any) -> dict[str, Any] | None:
    raw = getattr(video, "as_dict", None)
    if callable(raw):
        raw = raw()
    if isinstance(raw, dict):
        return raw
    if isinstance(video, dict):
        return video
    return None


def extract_stats(raw: dict[str, Any]) -> dict[str, int]:
    stats = raw.get("statsV2") or raw.get("stats") or {}
    return {
        "likes": int(
            stats.get("diggCount")
            or stats.get("digg_count")
            or stats.get("likeCount")
            or stats.get("like_count")
            or 0
        ),
        "shares": int(stats.get("shareCount") or stats.get("share_count") or 0),
        "comments": int(stats.get("commentCount") or stats.get("comment_count") or 0),
        "plays": int(
            stats.get("playCount")
            or stats.get("play_count")
            or stats.get("viewCount")
            or stats.get("view_count")
            or 0
        ),
    }


def extract_author(raw: dict[str, Any]) -> str:
    author = raw.get("author") or {}
    for key in ("uniqueId", "unique_id", "nickname", "username"):
        value = author.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def extract_region(raw: dict[str, Any]) -> str:
    candidates = [
        raw.get("region"),
        raw.get("regionCode"),
        raw.get("locationCreated"),
        (raw.get("author") or {}).get("region"),
        (raw.get("author") or {}).get("regionCode"),
    ]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip().upper()
    return ""


def extract_hashtags(raw: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        cleaned = normalize_token(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            tags.append(cleaned)

    for item in raw.get("challenges") or []:
        if isinstance(item, dict):
            add(str(item.get("title") or item.get("chaName") or ""))
    for item in raw.get("textExtra") or []:
        if isinstance(item, dict):
            add(str(item.get("hashtagName") or item.get("hashtag_name") or ""))
    description = raw.get("desc") or raw.get("description") or raw.get("video_description") or ""
    if isinstance(description, str):
        for match in HASHTAG_RE.findall(description):
            add(match)
    return tags


def extract_create_time(raw: dict[str, Any]) -> str:
    value = raw.get("createTime") or raw.get("create_time")
    if isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            return value.strip()
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def parse_create_time(raw: dict[str, Any]) -> datetime | None:
    normalized = extract_create_time(raw)
    if not normalized:
        return None
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def build_video_url(raw: dict[str, Any], author: str, video_id: str) -> str:
    for key in ("shareUrl", "share_url"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    share_info = raw.get("shareInfo") or raw.get("share_info") or {}
    for key in ("shareUrl", "share_url"):
        value = share_info.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    if author:
        return f"https://www.tiktok.com/@{author}/video/{video_id}"
    return f"https://www.tiktok.com/video/{video_id}"


def build_metrics(stats: dict[str, int], created_at: datetime, now: datetime) -> dict[str, float]:
    age_hours = max((now - created_at).total_seconds() / 3600.0, 1 / 60)
    engagement = float(stats["likes"]) + float(stats["comments"]) * 2.5 + float(stats["shares"]) * 4.0
    quality = engagement / max(float(stats["plays"]), 1.0)
    velocity = engagement / max(age_hours, 1.0)
    return {
        "age_hours": round(age_hours, 3),
        "engagement": round(engagement, 3),
        "quality": round(quality, 6),
        "velocity": round(velocity, 3),
        "score_exposure": math.log1p(max(stats["plays"], 0)),
        "score_engagement": math.log1p(max(engagement, 0.0)),
        "score_velocity": math.log1p(max(velocity, 0.0)),
        "score_quality": quality,
    }


def normalize_score(value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        return 1.0
    return (value - minimum) / (maximum - minimum)


def rank_entries(entries: list[dict[str, Any]], keep: int, per_author_limit: int) -> list[dict[str, Any]]:
    if not entries:
        return []

    score_fields = [
        "score_exposure",
        "score_engagement",
        "score_velocity",
        "score_quality",
    ]
    bounds = {
        field: (
            min(float(item[field]) for item in entries),
            max(float(item[field]) for item in entries),
        )
        for field in score_fields
    }

    for item in entries:
        hot_score = (
            0.30 * normalize_score(item["score_exposure"], *bounds["score_exposure"])
            + 0.30 * normalize_score(item["score_engagement"], *bounds["score_engagement"])
            + 0.25 * normalize_score(item["score_velocity"], *bounds["score_velocity"])
            + 0.15 * normalize_score(item["score_quality"], *bounds["score_quality"])
        )
        item["hot_score"] = round(hot_score, 6)

    entries.sort(
        key=lambda item: (
            -item["hot_score"],
            -item["engagement"],
            -item["view_count"],
            item["age_hours"],
        )
    )

    kept: list[dict[str, Any]] = []
    by_author: Counter[str] = Counter()
    for item in entries:
        author = item.get("author") or ""
        if author and by_author[author] >= per_author_limit:
            continue
        if author:
            by_author[author] += 1
        kept.append(item)
        if len(kept) >= keep:
            break

    for index, item in enumerate(kept, start=1):
        item["rank_in_category"] = index
        item.pop("score_exposure", None)
        item.pop("score_engagement", None)
        item.pop("score_velocity", None)
        item.pop("score_quality", None)
    return kept


def build_entry(raw: dict[str, Any], category: dict[str, Any], region_filter: str, min_created_at: datetime, now: datetime) -> dict[str, Any] | None:
    video_id = str(raw.get("id") or raw.get("aweme_id") or raw.get("awemeId") or "").strip()
    if not video_id:
        return None

    created_at = parse_create_time(raw)
    if created_at is None or created_at < min_created_at:
        return None

    author = extract_author(raw)
    region = extract_region(raw)
    if region_filter and region and region != region_filter:
        return None

    stats = extract_stats(raw)
    if stats["likes"] < 0:
        return None
    metrics = build_metrics(stats, created_at, now)
    description = raw.get("desc") or raw.get("description") or raw.get("video_description") or ""
    if not isinstance(description, str):
        description = str(description)

    return {
        "video_id": video_id,
        "url": build_video_url(raw, author, video_id),
        "description": description,
        "author": author,
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
        "hashtags": extract_hashtags(raw),
        "age_hours": metrics["age_hours"],
        "engagement": metrics["engagement"],
        "quality": metrics["quality"],
        "velocity": metrics["velocity"],
        "score_exposure": metrics["score_exposure"],
        "score_engagement": metrics["score_engagement"],
        "score_velocity": metrics["score_velocity"],
        "score_quality": metrics["score_quality"],
    }


async def collect_hashtag(api: TikTokApi, hashtag: str, per_query: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    source = api.hashtag(name=hashtag)
    async for video in source.videos(count=per_query):
        raw = extract_video_dict(video)
        if isinstance(raw, dict):
            results.append(raw)
    return results


async def crawl_category(
    api: TikTokApi,
    category: dict[str, Any],
    args: argparse.Namespace,
    min_created_at: datetime,
    now: datetime,
    min_likes_threshold: int,
) -> tuple[dict[str, Any], bool]:
    try:
        raws = await collect_hashtag(api, category["query_value"], args.per_query)
    except Exception as exc:
        error_text = str(exc)
        return (
            {
                "category_id": category["category_id"],
                "category_name": category["category_name"],
                "status": "query_failed",
                "query_value": category["query_value"],
                "first_seen_source_index": category["first_seen_source_index"],
                "first_seen_source_id": category["first_seen_source_id"],
                "first_seen_source_label": category["first_seen_source_label"],
                "first_seen_source_order": category["first_seen_source_order"],
                "source_ids": list(category["source_ids"]),
                "source_labels": list(category["source_labels"]),
                "mentions": category["mentions"],
                "total_candidates_seen": 0,
                "total_candidates_eligible": 0,
                "error": error_text,
                "top_videos": [],
            },
            should_retry_with_headful(error_text),
        )

    region_filter = args.region.strip().upper()
    merged: dict[str, dict[str, Any]] = {}
    seen = len(raws)
    for raw in raws:
        entry = build_entry(raw, category, region_filter, min_created_at, now)
        if not entry:
            continue
        if entry["like_count"] < min_likes_threshold:
            continue
        current = merged.get(entry["video_id"])
        if current is None or entry["engagement"] > current["engagement"]:
            merged[entry["video_id"]] = entry

    ranked = rank_entries(list(merged.values()), args.per_category, args.per_author_limit)
    return (
        {
            "category_id": category["category_id"],
            "category_name": category["category_name"],
            "status": "ok" if ranked else "no_results",
            "query_value": category["query_value"],
            "first_seen_source_index": category["first_seen_source_index"],
            "first_seen_source_id": category["first_seen_source_id"],
            "first_seen_source_label": category["first_seen_source_label"],
            "first_seen_source_order": category["first_seen_source_order"],
            "source_ids": list(category["source_ids"]),
            "source_labels": list(category["source_labels"]),
            "source_urls": list(category["source_urls"]),
            "mentions": category["mentions"],
            "total_candidates_seen": seen,
            "total_candidates_eligible": len(merged),
            "error": "",
            "top_videos": ranked,
        },
        False,
    )


def should_retry_with_headful(error_text: str) -> bool:
    lowered = error_text.lower()
    return any(pattern in lowered for pattern in RETRYABLE_HEADFUL_ERROR_PATTERNS)


def build_session_kwargs(args: argparse.Namespace, headful: bool) -> dict[str, Any]:
    session_kwargs: dict[str, Any] = {
        "num_sessions": 1,
        "sleep_after": 3,
        "browser": args.browser,
        "headless": not headful,
    }
    if args.ms_token:
        session_kwargs["ms_tokens"] = [args.ms_token]
    return session_kwargs


async def open_api_session(args: argparse.Namespace, headful: bool) -> TikTokApi:
    api = TikTokApi()
    await api.create_sessions(**build_session_kwargs(args, headful))
    return api


async def close_api_session(api: TikTokApi | None) -> None:
    if api is None:
        return
    close_sessions = getattr(api, "close_sessions", None)
    if callable(close_sessions):
        maybe_result = close_sessions()
        if asyncio.iscoroutine(maybe_result):
            await maybe_result


def resolve_effective_min_likes(args: argparse.Namespace) -> tuple[int, str]:
    if args.min_likes is not None:
        return max(args.min_likes, 0), "manual_min_likes_override"
    return DEFAULT_MIN_LIKES_BY_WINDOW[args.window], "adaptive_min_likes_by_window"


def build_discovery_only_result(category: dict[str, Any], discovery_rank: int) -> dict[str, Any]:
    return {
        "category_id": category["category_id"],
        "category_name": category["category_name"],
        "status": "discovered",
        "discovery_rank": discovery_rank,
        "query_value": category["query_value"],
        "first_seen_source_index": category["first_seen_source_index"],
        "first_seen_source_id": category["first_seen_source_id"],
        "first_seen_source_label": category["first_seen_source_label"],
        "first_seen_source_order": category["first_seen_source_order"],
        "source_ids": list(category["source_ids"]),
        "source_labels": list(category["source_labels"]),
        "source_urls": list(category["source_urls"]),
        "mentions": category["mentions"],
        "total_candidates_seen": 0,
        "total_candidates_eligible": 0,
        "error": "",
        "top_videos": [],
    }


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    categories, source_reports = discover_official_categories(args.category_limit, args.source_timeout)
    if not categories:
        print("No official categories/topics could be discovered from TikTok surfaces.", file=sys.stderr)
        sys.exit(1)

    min_created_at = now_utc() - window_to_delta(args.window)
    effective_min_likes, threshold_mode = resolve_effective_min_likes(args)
    effective_thresholds = {"min_likes": effective_min_likes}
    if args.discover_only:
        return {
            "run_mode": "official_category_discovery_only",
            "observed_at": now_utc().isoformat().replace("+00:00", "Z"),
            "window": args.window,
            "window_start": min_created_at.isoformat().replace("+00:00", "Z"),
            "region": args.region.strip().upper() or "GLOBAL",
            "discover_only": True,
            "category_sort_mode": "source_coverage_then_official_page_order_then_mentions",
            "threshold_mode": threshold_mode,
            "effective_thresholds": effective_thresholds,
            "session_mode_requested": "not_used",
            "session_mode_effective": "not_used",
            "session_fallback_applied": False,
            "session_fallback_category_id": "",
            "session_fallback_reason": "",
            "category_limit": args.category_limit,
            "per_query": args.per_query,
            "per_category": args.per_category,
            "per_author_limit": args.per_author_limit,
            "official_sources": source_reports,
            "categories_discovered": len(categories),
            "categories_succeeded": len(categories),
            "categories": [
                build_discovery_only_result(category, index + 1)
                for index, category in enumerate(categories)
            ],
        }

    requested_headful = args.headful
    effective_headful = requested_headful
    fallback_applied = False
    fallback_reason = ""
    fallback_category_id = ""
    api = await open_api_session(args, effective_headful)
    try:
        observed_at = now_utc()
        category_results: list[dict[str, Any]] = []
        for category in categories:
            print(
                f"Collecting official category/topic {category['category_name']} via hashtag={category['query_value']}...",
                file=sys.stderr,
            )
            result, retry_with_headful = await crawl_category(
                api,
                category,
                args,
                min_created_at,
                observed_at,
                effective_min_likes,
            )
            if retry_with_headful and not effective_headful:
                fallback_applied = True
                fallback_reason = result["error"]
                fallback_category_id = category["category_id"]
                print(
                    (
                        "  detected retryable TikTokApi bot/empty-response failure; "
                        "retrying this and remaining categories with headful sessions..."
                    ),
                    file=sys.stderr,
                )
                await close_api_session(api)
                api = await open_api_session(args, True)
                effective_headful = True
                result, _ = await crawl_category(
                    api,
                    category,
                    args,
                    min_created_at,
                    observed_at,
                    effective_min_likes,
                )
                result["retried_with_headful"] = True
            else:
                result["retried_with_headful"] = False
            result["session_mode"] = "headful" if effective_headful else "headless"
            category_results.append(result)
            print(
                f"  status={result['status']} seen={result['total_candidates_seen']} eligible={result['total_candidates_eligible']}",
                file=sys.stderr,
            )
    finally:
        await close_api_session(api)

    succeeded = sum(1 for item in category_results if item["status"] == "ok")
    return {
        "run_mode": "official_first_with_tiktokapi_fallback",
        "observed_at": now_utc().isoformat().replace("+00:00", "Z"),
        "window": args.window,
        "window_start": min_created_at.isoformat().replace("+00:00", "Z"),
        "region": args.region.strip().upper() or "GLOBAL",
        "discover_only": False,
        "category_sort_mode": "source_coverage_then_official_page_order_then_mentions",
        "session_mode_requested": "headful" if requested_headful else "headless",
        "session_mode_effective": "headful" if effective_headful else "headless",
        "session_fallback_applied": fallback_applied,
        "session_fallback_category_id": fallback_category_id,
        "session_fallback_reason": fallback_reason,
        "category_limit": args.category_limit,
        "per_query": args.per_query,
        "per_category": args.per_category,
        "per_author_limit": args.per_author_limit,
        "official_sources": source_reports,
        "categories_discovered": len(categories),
        "categories_succeeded": succeeded,
        "threshold_mode": threshold_mode,
        "effective_thresholds": effective_thresholds,
        "categories": category_results,
    }


def main() -> None:
    args = parse_args()
    payload = asyncio.run(main_async(args))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    result_label = "discovered categories" if payload.get("discover_only") else "successful category results"
    print(
        (
            f"Saved {payload['categories_succeeded']} {result_label} "
            f"out of {payload['categories_discovered']} discovered categories to {args.out}"
        ),
        file=sys.stderr,
    )
    if payload["categories_succeeded"] == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
