#!/usr/bin/env python3
"""
Print the current AutoTikTok live-lane dependency inventory.
"""

from __future__ import annotations

import json
import sys

from live_lane_dependency_inventory import build_live_lane_dependency_inventory


def main() -> int:
    payload = build_live_lane_dependency_inventory()
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
