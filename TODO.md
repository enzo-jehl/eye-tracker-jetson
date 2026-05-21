# TODO — Eye Tracker Jetson

Master task list for the project. Check items off as they ship. Don't delete completed items — keep them as a log. See [CLAUDE.md](CLAUDE.md) for the rules each task must follow.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked

---

## Phase 0 — Bootstrap (project skeleton & tooling)

Goal: a clean, lint-clean, test-running empty project before any feature code lands.

- [x] Create the directory tree from [CLAUDE.md](CLAUDE.md) (`src/eye_tracker/{capture,calibration,detection,geometry,tracking,ai,utils}/`, `tests/`, `scripts/`, `configs/`, `docs/`, `data/`)
- [x] Add `__init__.py` in every Python package
- [x] Write `pyproject.toml` with `black`, `ruff`, `mypy --strict`, `pytest` config
- [x] Write `requirements.txt` (pinned versions, aarch64 / Python 3.6 compatible)
- [x] Write `requirements-dev.txt` for dev-machine-only tooling (lint, type-check, training)
- [x] Add `.editorconfig`
- [x] Update `.gitignore` to also ignore `data/`, `*.engine`, `*.onnx`, `*.pt`, `runs/`, manifests, calibration outputs
- [x] Set up `pre-commit` hook running black + ruff + mypy + pytest on staged files
- [x] Set up GitHub Actions CI (lint + type-check + tests on every push)
- [x] Write `Makefile` (or `justfile`) with `make check`, `make test`, `make bench`, `make run`
- [x] Write `scripts/benchmark.py` skeleton (entry point for FPS / latency measurements)
- [x] Write `configs/perf.yaml` with target metrics (≥120 FPS, ≤8.3 ms/frame, target accuracy, head-pose robustness window)
- [x] Write a real `README.md` (project pitch, hardware, how to install, how to run, how to test)
- [x] Set up structured `logging` config in `src/eye_tracker/utils/logging.py`
- [x] Set up run-manifest writer in `src/eye_tracker/utils/manifest.py` (git hash, config, seeds, timestamps)
- [~] First green CI run on `main` — pending: install dev deps (`make install-dev`) and push to GitHub to trigger `.github/workflows/ci.yml`. Locally verified that utils import and a manifest round-trips; full `make check` requires `requirements-dev.txt` to be installed.

## Phase 1 — Math baseline (geometric gaze estimation)

Goal: a working, measurable pipeline from CSI capture to a gaze point, with no AI involved.

### 1.1 Capture

- [ ] Document the exact Arducam model and its supported resolutions / FPS modes (especially: does it deliver 120 FPS, and at what resolution?)
- [ ] Confirm both cameras are detected on the Jetson (`nvgstcapture-1.0`, `v4l2-ctl --list-devices`)
- [ ] Build a `nvarguscamerasrc` GStreamer pipeline for a single CSI camera, NVMM buffers
- [ ] Extend to stereo: two `nvarguscamerasrc` instances with hardware-synchronized capture
- [ ] Wrap the pipeline in `src/eye_tracker/capture/stereo.py` with a clean Python API (`iter_frames() -> Iterator[StereoFrame]`)
- [ ] Add `configs/cameras.yaml` (sensor IDs, resolution, FPS, exposure, gain)
- [ ] Benchmark sustained stereo FPS without any processing → record in `configs/perf.yaml`
- [ ] Script `scripts/record_dataset.py` to save synchronized IR pairs + timestamps to disk
- [ ] Tests with synthetic / file-based input (no real cameras required in CI)

### 1.2 Calibration

- [ ] Print / acquire a calibration target (checkerboard or ChArUco, IR-friendly)
- [ ] Write `scripts/calibrate_intrinsics.py` (per-camera intrinsics + distortion)
- [ ] Write `scripts/calibrate_stereo.py` (extrinsics between left/right camera)
- [ ] Write `scripts/calibrate_user.py` (per-user gaze calibration, e.g. 9-point or 13-point)
- [ ] Define on-disk calibration format (YAML with versioning, units explicit) in `src/eye_tracker/calibration/io.py`
- [ ] Synthetic-fixture tests with ideal cameras (no real images)
- [ ] Document the physical calibration protocol in `docs/calibration_protocol.md`

### 1.3 Detection

- [ ] Implement pupil detection (CDF-based / Starburst / ElSe — pick one, justify in PR) in `src/eye_tracker/detection/pupil.py`
- [ ] Implement corneal reflection (glint / Purkinje) detection in `src/eye_tracker/detection/glint.py`
- [ ] Sub-pixel refinement of pupil center and glint center
- [ ] Robustness to partial occlusion (eyelids, eyelashes)
- [ ] Unit tests with synthetic IR eye images
- [ ] Visual debug overlay tool (`scripts/visualize_detection.py`)

### 1.4 Geometry & gaze estimation

- [ ] Implement a 3D eye model (cornea center, eyeball center, optical vs. visual axis) in `src/eye_tracker/geometry/eye_model.py`
- [ ] Implement gaze-vector estimation from pupil + glints (PCCR — Pupil-Center Corneal Reflection)
- [ ] Triangulate gaze in 3D using the stereo setup
- [ ] Map 3D gaze to screen coordinates (using user calibration)
- [ ] Handle head pose: estimate head translation/rotation and compensate (the system must hold accuracy under ±15° / ±5 cm — see [CLAUDE.md](CLAUDE.md))
- [ ] Document the coordinate frames in `docs/coordinate_frames.md` (with diagrams)
- [ ] Synthetic-fixture tests: ideal eye geometry → known gaze point, verify error < ε

### 1.5 Tracking (temporal filtering)

- [ ] Implement OneEuro filter on gaze output in `src/eye_tracker/tracking/filters.py`
- [ ] (Optional) Kalman filter with constant-velocity model
- [ ] Saccade vs. fixation detection (so the filter doesn't smear during saccades)
- [ ] Tests on recorded sequences

### 1.6 End-to-end pipeline

- [ ] Wire everything together in `src/eye_tracker/pipeline.py`
- [ ] `scripts/run_live.py` — live gaze tracking with on-screen overlay
- [ ] `scripts/evaluate.py` — measure angular accuracy + p95 on a recorded dataset
- [ ] Hit Phase 1 acceptance metrics (see bottom of file)

## Phase 2 — AI correction layer

Goal: a learned residual that takes eye crops + math prediction and outputs a refined gaze point.

- [ ] Record a labeled dataset (subject looks at known on-screen targets while the pipeline captures stereo frames + math predictions)
- [ ] Define the dataset format and split (train / val / test, per-user holdout)
- [ ] Implement `src/eye_tracker/ai/dataset.py` (PyTorch `Dataset`)
- [ ] Design the model architecture in `src/eye_tracker/ai/model.py` — small enough to run at 120 FPS on Jetson (target: < 2 ms inference in TensorRT FP16)
- [ ] Implement training loop in `src/eye_tracker/ai/train.py` (runs on dev machine, not Jetson)
- [ ] Log experiments (tensorboard or simple JSON + matplotlib)
- [ ] Export the trained model to ONNX
- [ ] Convert ONNX → TensorRT engine (FP16 first, then INT8 if accuracy holds)
- [ ] Implement `src/eye_tracker/ai/infer.py` — TensorRT wrapper with explicit input/output bindings
- [ ] Integrate the AI step into `pipeline.py` (configurable on/off)
- [ ] Measure accuracy delta vs. math-only baseline → record in PR description
- [ ] Tests: model loads, inference shape contract is respected, baseline vs. AI numbers reproducible

## Phase 3 — Hit the 120 FPS target

Goal: sustained ≥120 FPS, end-to-end, on the Jetson Nano. Only attack this after Phase 1 (and ideally Phase 2) is functionally correct.

- [ ] Profile end-to-end with `nsys` and `cProfile` — find the top 3 bottlenecks
- [ ] Move detection to GPU using OpenCV CUDA module where applicable
- [ ] Eliminate CPU↔GPU copies in the capture → detection path (stay in NVMM / GpuMat)
- [ ] Run capture and detection on separate threads/processes if it helps latency
- [ ] Quantize the AI model to INT8 if accuracy holds
- [ ] Verify 120 FPS sustained for 60+ seconds (no thermal throttling)
- [ ] Lock perf budget: each pipeline stage gets a documented ms budget in `configs/perf.yaml`
- [ ] Add a regression test that fails CI if benchmark drops > 10%

## Cross-cutting / ongoing

- [ ] Keep [CLAUDE.md](CLAUDE.md) up to date whenever conventions or structure change
- [ ] Keep `TODO.md` (this file) up to date — add new items as they appear, check off when done
- [ ] Keep `requirements.txt` pins valid for Jetson aarch64 + Python 3.6
- [ ] Every PR records measured impact on the four metrics (accuracy, head-pose robustness, latency, FPS)
- [ ] Backups: calibration files and trained models are stored outside git, with documented hashes

---

## Acceptance criteria per phase

**Phase 0 done when:** CI is green on `main`; `make check` passes locally; project structure matches [CLAUDE.md](CLAUDE.md).

**Phase 1 done when:** live gaze tracking runs end-to-end on the Jetson; angular accuracy ≤ 2° mean on a validation set; robust to ±15° head rotation and ±5 cm translation; sustained ≥60 FPS (full 120 FPS is a Phase 3 target).

**Phase 2 done when:** AI layer reduces angular error by a measurable, repeatable margin vs. math-only baseline; TensorRT inference < 2 ms FP16.

**Phase 3 done when:** sustained ≥120 FPS end-to-end for 60+ seconds with all stages active; perf regression test in CI.
