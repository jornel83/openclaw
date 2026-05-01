#!/usr/bin/env python3
"""
Smoke test for runtime profile rollout policy rule-routing validation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[3]


class TestRuntimeProfileRolloutPolicyRuleRouting(TestCase):
    def test_runtime_profile_rollout_policy_rule_routing_validator_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/autotiktok/scripts/validate_runtime_profile_rollout_policy_rule_routing.py",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Runtime profile rollout policy rule routing validation passed.",
            result.stdout,
        )


if __name__ == "__main__":
    main()
