# Eye Tracker Jetson

Stereo infrared eye tracker running on an NVIDIA Jetson Nano. The goal is to
build **the most accurate eye tracker possible**, holding accuracy under small
head movements (±15° rotation, ±5 cm translation).

The system is built in two stages:

1. **Mathematical baseline** — synchronized stereo IR capture → pupil and
   corneal-reflection (Purkinje) detection → 3D eye model + gaze
   triangulation (PCCR) → screen mapping.
2. **AI correction layer** — a small neural network refines the geometric
   gaze estimate from the eye crops + the math prediction. Trained on a dev
   box, deployed to the Jetson as a quantized TensorRT engine.

See [CLAUDE.md](CLAUDE.md) for the engineering rules and [TODO.md](TODO.md)
for the phased task plan.

## Hardware

- NVIDIA Jetson Nano Developer Kit (B01)
- 2 × Arducam IR cameras on CSI ports (15-pin)
- JetPack 4.6.1 (L4T 32.7.1) — Ubuntu 18.04, Python 3.6, CUDA 10.2, cuDNN 8.2,
  TensorRT 8.2, OpenCV 4.1.1 (NVIDIA CUDA build)

> ⚠️ The NVIDIA-shipped OpenCV is CUDA-enabled. **Do not** `pip install
> opencv-python` — it overwrites the CUDA build.

## Install

On a dev machine (x86, used for lint / type-check / training):

```bash
make install-dev
```

On the Jetson (runtime only):

```bash
make install
```

PyTorch wheels for the Jetson are taken from
[NVIDIA's official aarch64 builds](https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048),
not PyPI.

## Run

```bash
make run         # live gaze tracking with overlay (Phase 1+)
make bench       # measure FPS / latency against configs/perf.yaml
```

## Develop

```bash
make check       # ruff + black --check + mypy --strict + pytest
make fmt         # auto-format with black
make test        # pytest
```

`pre-commit` runs the same checks on staged files at commit time:

```bash
pre-commit install
```

## Layout

See the **Target project structure** section of [CLAUDE.md](CLAUDE.md).
Each module has a single responsibility; tests mirror `src/` under `tests/`.

## Performance targets

Recorded in [configs/perf.yaml](configs/perf.yaml). Every PR reports measured
impact on:

- Angular accuracy (mean + p95 in degrees)
- Head-pose robustness window
- End-to-end latency (ms)
- Sustained FPS on the Jetson Nano (target: ≥120 FPS — Phase 3)
