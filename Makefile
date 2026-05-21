PY ?= python3
PIP ?= pip3

.PHONY: help install install-dev fmt lint typecheck test check bench run clean

help:
	@echo "Targets:"
	@echo "  install       Install runtime deps (Jetson)"
	@echo "  install-dev   Install dev + runtime deps (dev box)"
	@echo "  fmt           Run black"
	@echo "  lint          Run ruff"
	@echo "  typecheck     Run mypy --strict on src/"
	@echo "  test          Run pytest"
	@echo "  check         lint + format-check + typecheck + test"
	@echo "  bench         Run scripts/benchmark.py"
	@echo "  run           Run scripts/run_live.py"
	@echo "  clean         Remove caches and build artifacts"

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	pre-commit install

fmt:
	black src tests scripts

lint:
	ruff check src tests scripts

typecheck:
	mypy

test:
	pytest

check:
	ruff check src tests scripts
	black --check src tests scripts
	mypy
	pytest

bench:
	$(PY) scripts/benchmark.py

run:
	$(PY) scripts/run_live.py

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
