# Developer Workflow

This page explains how to work on the project locally.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

## Run Tests

```bash
python -m unittest discover -s tests -v
```

Or, if `make` is available:

```bash
make test
```

## Run A Dry-Run Smoke Test

```bash
private-ai init --dry-run --mode local-developer --project-name private-ai-demo --company-name local --output-dir generated/dry-run --force
private-ai validate generated/dry-run
```

Or:

```bash
make dry-run
make validate
```

## Local Readiness Check

```bash
private-ai doctor
```

The doctor command reports missing tools as warnings. Docker, Ollama, and NVIDIA tooling are not required for documentation or dry-run development.

## Contribution Focus

High-impact early contributions:

- Add wizard question files.
- Improve validation rules.
- Add config schema tests.
- Add more safe example configs.
- Improve generated review docs.
- Add the local RAG MVP in small pieces.

