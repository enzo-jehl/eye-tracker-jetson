# Dev cheat-sheet

Quick reference for everyday commands on the dev box (Windows / PowerShell).
For the project rules and structure, see [CLAUDE.md](../CLAUDE.md).
For the phased task plan, see [TODO.md](../TODO.md).

---

## One-time setup

```powershell
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate it (run every new terminal)
.\.venv\Scripts\Activate.ps1

# 3. Install dev + runtime dependencies
pip install -r requirements-dev.txt

# 4. Install Git hooks (ruff + black + mypy on commit, pytest on push)
pre-commit install
```

If activation fails with *"running scripts is disabled"*, run once as your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## Daily workflow

| Task                      | Command                                  |
|---------------------------|------------------------------------------|
| Activate venv             | `.\.venv\Scripts\Activate.ps1`           |
| Deactivate venv           | `deactivate`                             |
| Format code               | `black src tests scripts`                |
| Lint                      | `ruff check src tests scripts`           |
| Lint + auto-fix           | `ruff check --fix src tests scripts`     |
| Type-check (strict)       | `mypy`                                   |
| Run tests                 | `pytest`                                 |
| Run a single test file    | `pytest tests/utils/test_manifest.py -v` |
| All checks (CI parity)    | `.\scripts\check.ps1` *(Windows)* / `make check` *(Linux / Jetson)* |
| Run benchmark skeleton    | `python scripts/benchmark.py`            |
| Run live tracking         | `python scripts/run_live.py` *(Phase 1+)*|

On Windows, use `.\scripts\check.ps1` — it's the PowerShell equivalent of
`make check`. `make` itself isn't needed on the dev box; the [Makefile](../Makefile)
is for the Jetson (where `make` is built-in).

---

## Git workflow

```powershell
# See what changed
git status
git diff

# Stage + commit (Conventional Commits — see CLAUDE.md)
git add <files>
git commit -m "feat: short imperative subject"

# Push current branch
git push
```

Commit-type prefixes: `feat:` `fix:` `refactor:` `perf:` `test:` `docs:` `chore:`.
Subject in imperative mood, < 72 chars. Body explains the *why*.

Branch naming: `feat/<slug>`, `fix/<slug>`, `exp/<slug>` for AI experiments.

---

## First push to GitHub

```powershell
# One-time: create the repo on https://github.com/new (no README/.gitignore)
git remote add origin https://github.com/<user>/eye-tracker-jetson.git
git branch -M main
git push -u origin main
```

Easiest auth: `winget install GitHub.cli` then `gh auth login`.

After the push, watch CI: repo → **Actions** tab → click the latest run.
Green ✅ = Phase 0 acceptance criterion met.

---

## Jetson workflow (later — Phase 1 onward)

On the device itself:

```bash
git clone <repo-url>
cd eye-tracker-jetson
make install          # runtime deps only — no dev tooling
python scripts/benchmark.py
```

Never run `pip install opencv-python` on the Jetson — it overwrites the
NVIDIA CUDA build. Use the system OpenCV (`import cv2` works out of the box).

---

## Troubleshooting

| Symptom                                             | Fix                                                                                  |
|-----------------------------------------------------|--------------------------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'eye_tracker'`| Activate the venv, or check that you're running from the repo root.                  |
| `pre-commit` slow on first run                      | Normal — it's building isolated envs for each hook. Subsequent runs are cached.      |
| `mypy` complains about a third-party import         | Add the module to the `ignore_missing_imports` list in [pyproject.toml](../pyproject.toml). |
| `black` and pre-commit's `black` disagree           | Versions are out of sync. Reinstall: `pip install -r requirements-dev.txt`.          |
| CRLF / LF noise in `git status`                     | [.editorconfig](../.editorconfig) handles this — confirm your editor reads it.       |

---

## What "done" looks like per phase

- **Phase 0**: `make check` green locally + green CI on `main`. ([TODO.md](../TODO.md) all Phase-0 boxes `[x]`.)
- **Phase 1**: live gaze tracking running end-to-end on the Jetson, ≤ 2° mean angular error, ≥ 60 FPS sustained.
- **Phase 2**: AI layer reduces error vs. math-only baseline, < 2 ms TensorRT FP16 inference.
- **Phase 3**: ≥ 120 FPS sustained for 60+ seconds, perf regression test in CI.
