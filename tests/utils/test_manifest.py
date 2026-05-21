"""Smoke tests for the run-manifest writer."""

from __future__ import annotations

import json
from pathlib import Path

from eye_tracker.utils.manifest import build_manifest, write_manifest


def test_build_manifest_populates_required_fields() -> None:
    manifest = build_manifest(name="unit-test", config={"k": 1}, seeds={"numpy": 42})
    assert manifest.name == "unit-test"
    assert manifest.python_version
    assert manifest.platform
    assert manifest.hostname
    assert manifest.config == {"k": 1}
    assert manifest.seeds == {"numpy": 42}


def test_write_manifest_round_trips(tmp_path: Path) -> None:
    manifest = build_manifest(name="round-trip")
    file_path = write_manifest(manifest, tmp_path)
    assert file_path.exists()
    data = json.loads(file_path.read_text(encoding="utf-8"))
    assert data["name"] == "round-trip"
    assert "timestamp_utc" in data
