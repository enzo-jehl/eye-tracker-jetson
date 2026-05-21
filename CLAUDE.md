# Eye Tracker Jetson

## Project goal

Build **the most accurate eye tracker possible** using two infrared cameras, embedded on a Jetson Nano. The system must stay accurate despite **small head movements** (rotation + translation).

The approach is two-staged:

1. **Mathematical pipeline (baseline)** — eye isolation and geometric gaze estimation from the two IR streams. Output: a gaze point `(x, y)` + eye crops.
2. **AI correction layer** — a model takes the eye crops + the geometric prediction as input and **refines** the gaze point to exceed the baseline's accuracy.

The AI layer is trained only after the math baseline is stable and the data (crops + math prediction + ground truth) has been collected cleanly.

## Target hardware & system

- **Board**: NVIDIA Jetson Nano Developer Kit (B01)
- **OS**: Ubuntu 18.04.6 LTS (Bionic)
- **NVIDIA stack**: JetPack 4.6.1 (L4T 32.7.1)
- **Architecture**: `aarch64` (ARM 64-bit)
- **Cameras**: 2 × Arducam IR over CSI ports (15 pins)
- **Python**: 3.6 (Bionic default — hard constraint)
- **CUDA**: 10.2 (shipped with JetPack 4.6.1)
- **cuDNN**: 8.2
- **TensorRT**: 8.2

> ⚠️ **Never propose**: Python ≥ 3.7 as a hard requirement, recent PyTorch/TensorFlow versions that don't have aarch64 + JetPack 4.6 wheels, OpenCV ≥ 4.6 (NVIDIA's shipped build is 4.1.1 with CUDA). Always verify aarch64 + JetPack 4.6 compatibility before suggesting a dependency.

## Recommended tech stack

- **Main language**: Python 3.6 for high-level logic; C++17 + CUDA for performance-critical sections (introduce only when profiling justifies it).
- **Vision**: OpenCV 4.1.1 (NVIDIA's CUDA-enabled build — do not reinstall via pip).
- **CSI capture**: GStreamer via `nvarguscamerasrc` (NVIDIA pipeline, zero-copy GPU possible).
- **Numerical computing**: NumPy, SciPy (linalg, optimization for calibration).
- **AI (phase 2)**: PyTorch 1.10 (NVIDIA's official wheel for JetPack 4.6) → ONNX export → TensorRT FP16/INT8 inference.
- **Tests**: `pytest`.
- **Lint / format**: `ruff` (lint) + `black` (format). Type hints everywhere, `mypy` in CI.
- **Build / deps**: versioned `requirements.txt`. No Conda on the Jetson.

## Target project structure

```
eye-tracker-jetson/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── pyproject.toml              # black / ruff / mypy config
├── src/
│   └── eye_tracker/
│       ├── __init__.py
│       ├── capture/            # CSI acquisition, stereo sync, GStreamer
│       ├── calibration/        # camera intrinsics + stereo + user calibration
│       ├── detection/          # pupil / corneal reflection (Purkinje) detection
│       ├── geometry/           # 3D eye model, triangulation, gaze estimation
│       ├── tracking/           # temporal filtering (Kalman, OneEuro)
│       ├── ai/                 # correction model (phase 2)
│       │   ├── dataset.py
│       │   ├── model.py
│       │   ├── train.py
│       │   └── infer.py        # TensorRT wrapper
│       ├── pipeline.py         # math → AI orchestrator
│       └── utils/
├── tests/                      # mirrors src/
├── scripts/                    # CLI tools (calibrate, record dataset, benchmark)
├── data/                       # gitignored — raw datasets, models, calibrations
├── configs/                    # YAML: camera params, thresholds, hyperparams
└── docs/                       # optical diagrams, calibration notes, protocols
```

Any new feature must fit into an existing module; create a new module only when the responsibility is genuinely distinct.

## Code principles (non-negotiable)

1. **Separation of concerns** — each module above has ONE responsibility. Capture doesn't do detection. Detection doesn't do temporal filtering.
2. **No magic** — no globals, no hidden state. Dependencies are passed through constructors / arguments.
3. **Type hints everywhere** — full signatures, including returns. `mypy --strict` must pass on `src/`.
4. **Externalized configs** — no thresholds, camera IDs, crop sizes, or hyperparameters hardcoded. Everything in `configs/*.yaml`, loaded through a typed dataclass.
5. **Reproducibility** — every run (calibration, dataset capture, training) writes a manifest (`run_<timestamp>.json`) with versions, configs, seeds, git hash.
6. **Tests** — every module under `src/` has a mirror under `tests/`. Geometry and calibration are tested with synthetic fixtures (ideal cameras) before touching real data.
7. **No print** — `logging` with proper levels. User-facing output goes through a configured logger.
8. **Measured performance, not guessed** — before optimizing, profile (`cProfile`, `nsys` for CUDA). Target FPS / latency are recorded in `configs/perf.yaml` and regressions are caught against it.

## Success metrics

For every PR or meaningful iteration, justify the impact on:

- **Angular accuracy** (degrees) — mean and p95 error on the validation dataset.
- **Head pose robustness** — accuracy preserved over ±15° rotation and ±5 cm translation.
- **End-to-end latency** (ms) — capture → final gaze point.
- **Sustained FPS** on Jetson Nano (**initial target: ≥120 FPS** for fluid prediction).

These metrics live in `configs/perf.yaml` and a `scripts/benchmark.py` measures them reproducibly.

> ⚠️ **120 FPS is aggressive on Jetson Nano with stereo IR**. It implies: capture pipeline must run on GPU (NVMM buffers, no CPU copies), detection should leverage CUDA OpenCV or a small TensorRT model, AI correction must be quantized (FP16/INT8) and lightweight. Plan for this early — it is not a "we'll optimize later" target. Also verify your Arducam modules can actually deliver 120 FPS at the chosen resolution (most IMX219-based modules cap at 120 FPS only in 720p mode).

## Conventions

- **Commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `perf:`, `test:`, `docs:`, `chore:`). Subject in imperative, < 72 characters. Body explains the *why*.
- **Branches**: `feat/<slug>`, `fix/<slug>`, `exp/<slug>` for AI experiments.
- **PRs**: description with context + measured impact on the metrics above.
- **Naming**: `snake_case` Python, `UPPER_SNAKE` constants, `PascalCase` classes. No obscure abbreviations (`pup_ctr` → `pupil_center`).
- **Units explicit in names**: `distance_mm`, `angle_deg`, `latency_ms`, `gaze_xy_px`. Never ambiguous units.
- **3D frames**: document the frame (left camera / world / screen) in every function manipulating 3D coordinates.

## Specific guidance for Claude

- **Always read [TODO.md](TODO.md) at the start of a task** — it is the master task list. Locate where the current request fits and respect the phase priorities.
- **Always update [TODO.md](TODO.md) when finishing a task** — check off `[x]` items, mark `[~]` for in-progress, `[!]` for blocked, and add new items that surface during the work. Do not delete completed items — they serve as a project log.
- **Always validate Jetson Nano + JetPack 4.6 + Python 3.6 compatibility** before suggesting a library. If unsure: say so and propose a verification step — don't make it up.
- **Don't reinstall OpenCV via `pip install opencv-python`** — it overwrites the NVIDIA CUDA build. Use the system one or recompile with CUDA.
- **Prefer NVIDIA GStreamer pipelines** for CSI capture (`nvarguscamerasrc`) over raw `cv2.VideoCapture` — fewer CPU↔GPU copies.
- **For the AI phase**: training on a dev machine (x86 + GPU); on the Jetson we only do **TensorRT inference**. Don't suggest training on the Jetson.
- **Before introducing a heavy dependency** (new framework, pretrained model), ask: is it justified by the metrics above, or is it a shortcut that will hurt maintainability?
- **Refuse to "fill in code"** without understanding the underlying geometry. If an equation is unclear (e.g. cornea model, ray-eye intersection), flag it and ask for a reference rather than improvising.
- **No over-engineering** — don't create abstractions or interfaces "for later". Add them when the second use case appears, not before.
- **Mind the 120 FPS budget** (~8.3 ms per stereo frame, full pipeline). Any new step must be benchmarked against that budget.
- **Reply in English by default**.

## When you add a new dependency

- **Verify aarch64 + JetPack 4.6 + Python 3.6 compatibility** before installing. Wheel must exist, or you need a build plan.
- **Pin the version** in `requirements.txt` (`==`, not `>=`).
- **Justify in the commit message** — why this dep, why not stdlib/existing dep, what's the size/perf cost.
- **Don't `pip install opencv-python`** — it kills the NVIDIA CUDA build.

## When you add a new feature / module

- **Create the test file at the same time** — empty or with a placeholder if needed, but the file exists.
- **Add a config section** in `configs/*.yaml` if it introduces parameters.
- **Update CLAUDE.md** if the module layout, conventions, or constraints change.
- **Measure the perf impact** — does it fit in the 8.3 ms/frame budget? Record before/after in the PR description.

## Standard workflow for a task

1. Read the relevant modules (`src/eye_tracker/...`) before proposing code.
2. Identify where the change belongs in the structure above.
3. Propose a short plan (modules touched, tests to write, metric impact) before writing.
4. Implement with types + tests.
5. Update the config if a new parameter is introduced.
6. State how to verify the result on the Jetson (exact command).

## Current state

Project at `Initial commit` — only `.gitignore` (Python) and an empty `README.md`. The structure above is to be built **incrementally**, starting with synchronized stereo CSI capture + an end-to-end test that saves an IR image pair.
