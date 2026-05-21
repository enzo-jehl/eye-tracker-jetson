"""Pytest bootstrap — add ``src/`` to sys.path so tests import the package
without requiring a prior ``pip install -e .``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
