#!/usr/bin/env python3

import runpy
import sys
from pathlib import Path


def main() -> None:
    target = Path(__file__).with_name("crawl-official-categories.py")
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
