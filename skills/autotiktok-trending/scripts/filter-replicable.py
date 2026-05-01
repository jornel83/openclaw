#!/usr/bin/env python3
"""
Filter TikTok videos by AI replicability.

Reads JSON output from fetch-candidates.py and scores each video on how suitable
it is for AI video generation, excluding categories and signals that indicate
the content cannot be meaningfully replicated by AI.

Usage:
  python3 filter-replicable.py /tmp/trending.json --strict --out /tmp/replicable.json
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Category base scores (0-100): how inherently replicable is this category?
# ---------------------------------------------------------------------------
CATEGORY_SCORES = {
    "motion_graphics": 95,
    "slideshow": 90,
    "satisfying": 85,
    "educational": 80,
    "cooking": 80,
    "tutorial": 75,
    "product_review": 70,
    "scenery": 70,
    "pet": 60,
}

# Categories that are fundamentally not AI-replicable
EXCLUDED_CATEGORIES = {
    "vlog", "dance", "choreography", "live_event", "news",
    "duet", "stitch", "interview", "podcast", "challenge",
}

# ---------------------------------------------------------------------------
# Hashtag signal weights (added/subtracted from base score)
# ---------------------------------------------------------------------------
POSITIVE_HASHTAGS = {
    "tutorial": 8, "howto": 8, "diy": 7, "recipe": 7,
    "lifehack": 6, "tips": 5, "satisfying": 6, "asmr": 5,
    "animation": 8, "motiondesign": 8, "3d": 7,
    "slideshow": 7, "learnontiktok": 6, "edutok": 6,
    "foodtiktok": 5, "easyrecipe": 6, "baking": 5,
    "drone": 5, "nature": 4, "scenery": 5,
}

NEGATIVE_HASHTAGS = {
    "pov": -15, "duet": -20, "stitch": -20,
    "vlog": -20, "grwm": -18, "storytime": -15,
    "dance": -20, "choreography": -20,
    "fyp": -2, "foryou": -2,
    "ootd": -10, "getreadywithme": -18,
    "reaction": -15, "challenge": -12,
    "live": -15, "news": -15, "interview": -15,
}

# ---------------------------------------------------------------------------
# Strict mode: hashtag patterns that strongly indicate face-dependent content
# ---------------------------------------------------------------------------
FACE_DEPENDENT_HASHTAGS = {
    "vlog", "grwm", "getreadywithme", "storytime", "pov",
    "makeuptutorial", "skincare", "ootd", "fitcheck",
    "talkinghead", "reaction", "dayinmylife",
}


def compute_replicability_score(video: dict, strict: bool) -> int:
    """
    Compute a 0-100 replicability score for a video.

    Factors:
      1. Category base score
      2. Hashtag positive/negative signals
      3. Duration sweet spot (15-60s best for AI generation)
      4. Strict mode: penalize face-dependent hashtag signals
    """
    category = video.get("category", "").lower()

    # Start with category base score; unknown categories get 50
    score = CATEGORY_SCORES.get(category, 50)

    # Hashtag adjustments
    hashtags = [h.lower().replace("#", "") for h in video.get("hashtags", [])]
    for tag in hashtags:
        if tag in POSITIVE_HASHTAGS:
            score += POSITIVE_HASHTAGS[tag]
        if tag in NEGATIVE_HASHTAGS:
            score += NEGATIVE_HASHTAGS[tag]

    # Duration sweet spot: 15-60s is ideal for AI video generation
    duration = video.get("duration_sec", 0)
    if 15 <= duration <= 60:
        score += 10
    elif 10 <= duration <= 90:
        score += 5
    elif duration > 180:
        score -= 10
    elif duration < 5:
        score -= 15

    # Strict mode: penalize face-dependent content
    if strict:
        face_signals = set(hashtags) & FACE_DEPENDENT_HASHTAGS
        if face_signals:
            score -= 15 * len(face_signals)

    # Clamp to 0-100
    return max(0, min(100, score))


def filter_videos(videos: list, strict: bool, min_score: int) -> list:
    """Filter and score videos for AI replicability."""
    results = []

    for v in videos:
        category = v.get("category", "").lower()

        # Exclude fundamentally non-replicable categories
        if category in EXCLUDED_CATEGORIES:
            continue

        score = compute_replicability_score(v, strict)

        if score < min_score:
            continue

        v["replicability_score"] = score
        results.append(v)

    # Sort by score descending, then by likes
    results.sort(key=lambda x: (-x["replicability_score"], -x.get("likes", 0)))
    return results


def main():
    parser = argparse.ArgumentParser(description="Filter TikTok videos by AI replicability")
    parser.add_argument("input", help="Input JSON file from fetch-candidates.py")
    parser.add_argument("--strict", action="store_true",
                        help="Enable strict mode: also penalize face-dependent hashtag signals")
    parser.add_argument("--min-score", type=int, default=40,
                        help="Minimum replicability score to include (default: 40)")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        videos = json.load(f)

    print(f"Input: {len(videos)} videos", file=sys.stderr)

    results = filter_videos(videos, args.strict, args.min_score)

    print(f"After filtering: {len(results)} replicable videos (min_score={args.min_score}, strict={args.strict})",
          file=sys.stderr)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved to {args.out}", file=sys.stderr)

    # Print score distribution summary
    if results:
        scores = [v["replicability_score"] for v in results]
        print(f"Score range: {min(scores)}-{max(scores)}, avg: {sum(scores)//len(scores)}", file=sys.stderr)


if __name__ == "__main__":
    main()
