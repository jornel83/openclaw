#!/usr/bin/env python3
"""Unit tests for the AutoTikTok video downloader helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from download import collect_urls_from_bakeoff


def tiktok_url(video_id: str) -> str:
    return f"https://www.tiktok.com/@creator/video/{video_id}"


class DownloadBakeoffUrlTests(unittest.TestCase):
    def write_payload(self, payload: dict) -> Path:
        temp_dir = tempfile.TemporaryDirectory(prefix="autotiktok-download-test-")
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "bakeoff.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_collect_urls_from_bakeoff_caps_each_view_before_merging(self) -> None:
        path = self.write_payload(
            {
                "routes": [
                    {
                        "absolute_hot_video_samples": {
                            "videoSamples": [
                                {"shareUrl": tiktok_url("100")},
                                {"shareUrl": tiktok_url("101")},
                                {"shareUrl": tiktok_url("102")},
                            ]
                        },
                        "fresh_hot_video_samples": {
                            "videoSamples": [
                                {"shareUrl": tiktok_url("200")},
                                {"shareUrl": tiktok_url("201")},
                                {"shareUrl": tiktok_url("202")},
                            ]
                        },
                    }
                ]
            }
        )

        urls = collect_urls_from_bakeoff(path, view="both", per_view_max=2)

        self.assertEqual(
            urls,
            [
                tiktok_url("100"),
                tiktok_url("101"),
                tiktok_url("200"),
                tiktok_url("201"),
            ],
        )

    def test_collect_urls_from_bakeoff_can_select_fresh_view_only(self) -> None:
        path = self.write_payload(
            {
                "routes": [
                    {
                        "absolute_hot_video_samples": {
                            "videoSamples": [{"shareUrl": tiktok_url("100")}]
                        },
                        "fresh_hot_video_samples": {
                            "videoSamples": [{"shareUrl": tiktok_url("200")}]
                        },
                    }
                ]
            }
        )

        self.assertEqual(
            collect_urls_from_bakeoff(path, view="fresh_hot"),
            [tiktok_url("200")],
        )

    def test_collect_urls_from_bakeoff_supports_top_level_artifacts(self) -> None:
        path = self.write_payload(
            {
                "absolute_hot_video_samples": {
                    "videoSamples": [{"shareUrl": tiktok_url("100")}]
                },
                "fresh_hot_video_samples": {
                    "videoSamples": [{"shareUrl": tiktok_url("200")}]
                },
            }
        )

        self.assertEqual(
            collect_urls_from_bakeoff(path, view="both"),
            [tiktok_url("100"), tiktok_url("200")],
        )


if __name__ == "__main__":
    unittest.main()
