#!/usr/bin/env python3
"""
Preview-first wrapper for the optimizer stage-matrix runner.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ranking_optimizer_contract_lib import (
    RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
    RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
)


ROOT = Path(__file__).resolve().parents[3]
TARGET_SCRIPT = ROOT / "skills" / "autotiktok" / "scripts" / "run_optimizer_stage_matrix.py"
USE_CURRENT_LANE_FLAG = "--use-current-lane"


def main() -> int:
    incoming_args = list(sys.argv[1:])
    use_current_lane = False
    filtered_args: list[str] = []
    saw_contract_version = False
    saw_validation_mode = False

    for arg in incoming_args:
        if arg == USE_CURRENT_LANE_FLAG:
            use_current_lane = True
            continue
        if arg == "--ranking-contract-version":
            saw_contract_version = True
        if arg == "--ranking-contract-validation-mode":
            saw_validation_mode = True
        filtered_args.append(arg)

    command = [sys.executable, str(TARGET_SCRIPT)]
    if not use_current_lane and not saw_contract_version and not saw_validation_mode:
        command.extend(
            [
                "--ranking-contract-version",
                RANKING_OPTIMIZER_CONTRACT_PREVIEW_VERSION,
                "--ranking-contract-validation-mode",
                RANKING_OPTIMIZER_CONTRACT_VALIDATION_MODE,
            ]
        )
    command.extend(filtered_args)

    result = subprocess.run(command, cwd=ROOT, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
