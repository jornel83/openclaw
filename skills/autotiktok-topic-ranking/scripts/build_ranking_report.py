#!/usr/bin/env python3
"""
Build a Markdown ranking report with local video filenames joined into the score table.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANKING = SKILL_ROOT / "fixtures" / "ranking-dry-run.sample.json"
DEFAULT_DISCOVERY = (
    SKILL_ROOT.parent
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "discovery-dry-run.sample.json"
)
DEFAULT_VIDEO_CONTENT_ANALYSIS = (
    SKILL_ROOT.parent
    / "autotiktok-topic-discovery"
    / "fixtures"
    / "video-content-analysis.sample.json"
)


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def markdown_cell(value: Any) -> str:
    text = str(value if value is not None else "").strip()
    return text.replace("|", "\\|").replace("\n", " ")


def fmt_score(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{float(value):.2f}"
    return markdown_cell(value)


def filename_from_path(value: Any) -> str:
    path = str(value or "").strip()
    if not path:
        return ""
    return Path(path).name


def scores_from_ranking(payload: dict[str, Any]) -> list[dict[str, Any]]:
    scores = payload.get("scores")
    if isinstance(scores, list):
        return [score for score in scores if isinstance(score, dict)]
    handoff = payload.get("optimizerHandoff")
    if isinstance(handoff, dict) and isinstance(handoff.get("scores"), list):
        return [score for score in handoff["scores"] if isinstance(score, dict)]
    raise ValueError("ranking payload must contain scores list")


def index_candidates(discovery_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    candidates = discovery_payload.get("candidates")
    if not isinstance(candidates, list):
        return {}
    return {
        str(candidate.get("topicId")): candidate
        for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("topicId")
    }


def index_evidence_bundles(discovery_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    bundles = discovery_payload.get("evidenceBundles")
    if not isinstance(bundles, list):
        return {}
    return {
        str(bundle.get("topicFingerprint")): bundle
        for bundle in bundles
        if isinstance(bundle, dict) and bundle.get("topicFingerprint")
    }


def index_analyses(video_content_analysis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    analyses = video_content_analysis.get("analyses")
    if not isinstance(analyses, list):
        return {}
    return {
        str(analysis.get("videoSampleId")): analysis
        for analysis in analyses
        if isinstance(analysis, dict) and analysis.get("videoSampleId")
    }


def topic_label(score: dict[str, Any], candidates_by_topic_id: dict[str, dict[str, Any]]) -> str:
    candidate = candidates_by_topic_id.get(str(score.get("topicId")))
    if candidate and candidate.get("topicTitle"):
        return str(candidate["topicTitle"])
    return str(score.get("topicId") or score.get("topicFingerprint") or "")


def video_filenames(
    score: dict[str, Any],
    evidence_by_fingerprint: dict[str, dict[str, Any]],
    analyses_by_video_sample_id: dict[str, dict[str, Any]],
) -> list[str]:
    bundle = evidence_by_fingerprint.get(str(score.get("topicFingerprint")))
    if not bundle:
        return []
    video_sample_ids = bundle.get("videoSampleIds")
    if not isinstance(video_sample_ids, list):
        return []

    names: list[str] = []
    seen: set[str] = set()
    for video_sample_id in video_sample_ids:
        analysis = analyses_by_video_sample_id.get(str(video_sample_id))
        if not analysis:
            continue
        name = filename_from_path(analysis.get("videoPath"))
        if not name:
            status = str(analysis.get("status") or "").strip()
            name = f"[{status}]" if status else ""
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def render_ranking_report(
    ranking_payload: dict[str, Any],
    discovery_payload: dict[str, Any],
    video_content_analysis: dict[str, Any],
    *,
    top: int = 0,
) -> str:
    scores = scores_from_ranking(ranking_payload)
    if top and top > 0:
        scores = scores[:top]
    candidates_by_topic_id = index_candidates(discovery_payload)
    evidence_by_fingerprint = index_evidence_bundles(discovery_payload)
    analyses_by_video_sample_id = index_analyses(video_content_analysis)

    lines = [
        "# 排名分数总表（来自 ranking-dry-run.json）",
        "",
        "| 排名 | Topic | 视频文件 | ScoreTotal | Series | Rewrite | Search | Feasibility |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for index, score in enumerate(scores, start=1):
        breakdown = score.get("scoreBreakdown")
        if not isinstance(breakdown, dict):
            breakdown = {}
        filenames = video_filenames(score, evidence_by_fingerprint, analyses_by_video_sample_id)
        filename_text = ", ".join(f"`{markdown_cell(name)}`" for name in filenames) or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    markdown_cell(topic_label(score, candidates_by_topic_id)),
                    filename_text,
                    fmt_score(score.get("scoreTotal")),
                    fmt_score(breakdown.get("series")),
                    fmt_score(breakdown.get("rewrite")),
                    fmt_score(breakdown.get("searchCapture")),
                    fmt_score(breakdown.get("feasibility")),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranking", type=Path, default=DEFAULT_RANKING)
    parser.add_argument("--discovery", type=Path, default=DEFAULT_DISCOVERY)
    parser.add_argument(
        "--video-content-analysis",
        type=Path,
        default=DEFAULT_VIDEO_CONTENT_ANALYSIS,
    )
    parser.add_argument("--top", type=int, default=0, help="Limit rendered rows (0 = all)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        report = render_ranking_report(
            load_json_object(args.ranking),
            load_json_object(args.discovery),
            load_json_object(args.video_content_analysis),
            top=args.top,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote ranking report to {args.output}")
        return 0

    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
