#!/usr/bin/env python3
"""
Smoke tests for the video-download manifest adapter validator.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestVideoDownloadManifestAdapterAlignment(TestCase):
    def test_video_download_manifest_adapter_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_video_download_manifest_adapter_alignment.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Video download manifest adapter fixture is aligned.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
