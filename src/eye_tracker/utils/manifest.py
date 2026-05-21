"""Run-manifest writer.

Every reproducible run (calibration, dataset capture, training, benchmark)
writes a manifest documenting *what code produced these artifacts*: git hash,
loaded config, RNG seeds, timestamps, host info.

Output is JSON next to the artifacts: ``run_<UTC-timestamp>.json``.
"""

from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Manifest:
    """A reproducibility manifest for a single run."""

    name: str
    timestamp_utc: str
    git_hash: Optional[str]
    git_dirty: bool
    python_version: str
    platform: str
    hostname: str
    config: Dict[str, Any] = field(default_factory=dict)
    seeds: Dict[str, int] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, sort_keys=True, default=str)


def _git(args: List[str]) -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", *args], stderr=subprocess.DEVNULL, cwd=Path(__file__).resolve().parent
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.decode("utf-8", errors="replace").strip()


def build_manifest(
    name: str,
    config: Optional[Dict[str, Any]] = None,
    seeds: Optional[Dict[str, int]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Manifest:
    """Collect environment + git info into a :class:`Manifest`."""
    git_hash = _git(["rev-parse", "HEAD"])
    diff = _git(["status", "--porcelain"])
    return Manifest(
        name=name,
        timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        git_hash=git_hash,
        git_dirty=bool(diff),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        hostname=socket.gethostname(),
        config=dict(config or {}),
        seeds=dict(seeds or {}),
        extra=dict(extra or {}),
    )


def write_manifest(manifest: Manifest, out_dir: os.PathLike[str]) -> Path:
    """Write ``run_<timestamp>.json`` under ``out_dir``. Returns the file path."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    stem = f"run_{manifest.timestamp_utc.replace(':', '').replace('-', '')}.json"
    file_path = out_path / stem
    file_path.write_text(manifest.to_json(), encoding="utf-8")
    return file_path
