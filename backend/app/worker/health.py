"""Lightweight health probe; do not import the application or database toolchain."""

import sys
import time
from pathlib import Path

HEARTBEAT = Path("/tmp/galene-worker-heartbeat")
INTERVAL_SECONDS = 5


def main() -> None:
    try:
        healthy = time.time() - HEARTBEAT.stat().st_mtime < INTERVAL_SECONDS * 3
    except FileNotFoundError:
        healthy = False
    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()
