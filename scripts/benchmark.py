"""End-to-end benchmark entry point.

Measures sustained FPS and per-stage latency of the eye-tracking pipeline
against the budget defined in ``configs/perf.yaml``.

This is a skeleton — wire each stage as it lands (capture → detection →
geometry → tracking → AI). Run from the repo root:

    python scripts/benchmark.py --config configs/perf.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running directly without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eye_tracker.utils.logging import configure_logging, get_logger

LOG = get_logger("benchmark")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Eye-tracker end-to-end benchmark.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/perf.yaml"),
        help="Path to perf budget YAML.",
    )
    parser.add_argument(
        "--duration-s",
        type=float,
        default=10.0,
        help="Benchmark duration in seconds.",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    LOG.info("Benchmark skeleton — pipeline stages not yet implemented.")
    LOG.info("Config: %s", args.config)
    LOG.info("Duration: %.1f s", args.duration_s)
    # TODO(phase-1): instantiate pipeline, run for args.duration_s, report FPS + p50/p95 latency.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
