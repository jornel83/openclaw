#!/usr/bin/env python3
"""Unit tests for the Markdown ranking report builder."""

from __future__ import annotations

import unittest

from build_ranking_report import render_ranking_report


class RankingReportTests(unittest.TestCase):
    def test_report_table_includes_downloaded_video_filename(self) -> None:
        report = render_ranking_report(
            {
                "scores": [
                    {
                        "topicId": "topic-1",
                        "topicFingerprint": "fp.topic.1",
                        "scoreTotal": 2.75,
                        "scoreBreakdown": {
                            "series": 3.81,
                            "rewrite": 3.5,
                            "searchCapture": 3.55,
                            "feasibility": 3.02,
                        },
                    }
                ]
            },
            {
                "candidates": [
                    {
                        "topicId": "topic-1",
                        "topicTitle": "#cutecat #cartoons #catstory",
                    }
                ],
                "evidenceBundles": [
                    {
                        "topicFingerprint": "fp.topic.1",
                        "videoSampleIds": ["tt:7630000000000000000"],
                    }
                ],
            },
            {
                "analyses": [
                    {
                        "videoSampleId": "tt:7630000000000000000",
                        "videoPath": "tiktok-downloads/top_0517_01/7630000000000000000.mp4",
                        "status": "analysis_succeeded",
                    }
                ]
            },
        )

        self.assertIn("| 排名 | Topic | 视频文件 | ScoreTotal |", report)
        self.assertIn("`7630000000000000000.mp4`", report)
        self.assertNotIn("tiktok-downloads/top_0517_01", report)

    def test_report_table_marks_missing_video_analysis_status(self) -> None:
        report = render_ranking_report(
            {
                "scores": [
                    {
                        "topicId": "topic-1",
                        "topicFingerprint": "fp.topic.1",
                        "scoreTotal": 2.75,
                        "scoreBreakdown": {},
                    }
                ]
            },
            {
                "candidates": [{"topicId": "topic-1", "topicTitle": "Missing sample"}],
                "evidenceBundles": [
                    {
                        "topicFingerprint": "fp.topic.1",
                        "videoSampleIds": ["tt:missing"],
                    }
                ],
            },
            {"analyses": [{"videoSampleId": "tt:missing", "status": "download_missing"}]},
        )

        self.assertIn("`[download_missing]`", report)


if __name__ == "__main__":
    unittest.main()
