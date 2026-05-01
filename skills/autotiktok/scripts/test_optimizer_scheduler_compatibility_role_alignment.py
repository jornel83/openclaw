#!/usr/bin/env python3
"""
Smoke test for scheduler compatibility-role alignment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = (
    ROOT
    / "skills"
    / "autotiktok"
    / "scripts"
    / "validate_optimizer_scheduler_compatibility_role_alignment.py"
)


class TestOptimizerSchedulerCompatibilityRoleAlignment(TestCase):
    def test_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    main()
