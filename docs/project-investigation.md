# Project Investigation

Date: 2026-06-26

This file records the current state of the workspace and the documentation decisions made during the first investigation pass.

## Workspace Inventory

Current files:

```text
.gitignore
CODE_OF_CONDUCT.md
CONTRIBUTING.md
LICENSE
Makefile
NOTICE
README.md
README_private_ai_infra_blueprint.md
SECURITY.md
pyproject.toml
docs/
  architecture.md
  cli-reference.md
  configuration-reference.md
  deployment-modes.md
  dry-run-mode.md
  developer-workflow.md
  github-growth-strategy.md
  hardware-and-runtime-options.md
  launch-checklist.md
  mvp-scope.md
  open-source-mission.md
  project-investigation.md
  roadmap.md
  security-principles.md
  stakeholder-workflow.md
  threat-model.md
  vision.md
generated/
  .gitkeep
configs/
  examples/
    audit-policy.example.yaml
    data-sources.example.yaml
    model-config.example.yaml
    rag-config.example.yaml
    rbac.example.yaml
examples/
  README.md
  sample-company-docs/
  sample-cyber-logs/
src/
  private_ai_infra/
    __init__.py
    __main__.py
    cli.py
    doctor.py
    generator.py
    models.py
    validator.py
tests/
  __init__.py
  test_cli.py
  test_generator_validator.py
  test_models.py
```

The workspace is not currently a git repository.

## Current State

The project now has documentation plus a first Python CLI milestone. It can generate and validate a dry-run review pack, and it has unit tests.

There is still no application runtime, Docker image, real local RAG ingestion, vector database write path, model inference path, web UI, or production apply flow.

The original file, `README_private_ai_infra_blueprint.md`, is a strong long-form concept document. It defines the product direction, modes, stakeholder roles, safety expectations, and roadmap. The main problem was that it described a documentation tree that did not exist.

## Documentation Work Completed

The long blueprint was converted into a navigable documentation set:

- `README.md` now acts as the canonical entry point.
- `docs/open-source-mission.md` defines the GitHub/open-source positioning and contribution boundaries.
- `docs/github-growth-strategy.md` defines the 10k-star growth strategy and the product signals needed to earn it.
- `docs/launch-checklist.md` defines what must exist before GitHub setup, first public push, and serious launch.
- `docs/cli-reference.md` defines the implemented v0.1 CLI behavior.
- `docs/developer-workflow.md` defines local install, test, dry-run, validation, and contribution workflow.
- `docs/vision.md` defines the problem, target users, success criteria, and non-goals.
- `docs/architecture.md` defines components, data flow, trust boundaries, audit flow, and architecture rules.
- `docs/deployment-modes.md` defines mode-specific assumptions, outputs, and validation blockers.
- `docs/hardware-and-runtime-options.md` defines CPU, GPU, DGX Spark, DGX-class, runtime, and vector database paths without hardcoding fast-changing hardware specs.
- `docs/dry-run-mode.md` defines dry-run guarantees, outputs, review gates, and promotion to apply.
- `docs/stakeholder-workflow.md` defines role-specific questions and generated artifacts.
- `docs/security-principles.md` defines defaults, RBAC, audit policy, prompt-injection handling, data protection, network safety, and cyber mode limits.
- `docs/threat-model.md` defines assets, actors, trust boundaries, threats, mitigations, abuse cases, and residual risks.
- `docs/configuration-reference.md` defines planned generated files, example config shapes, and validation rules.
- `docs/mvp-scope.md` defines MVP in-scope work, out-of-scope work, milestones, acceptance criteria, and test targets.
- `docs/roadmap.md` defines phased delivery.

## Key Finding

The project should not start by building the full enterprise platform. The lowest-risk implementation path is:

```text
CLI wizard
  -> dry-run files
  -> validator
  -> local Docker Compose stack
  -> sample ingestion
  -> cited local chat
  -> audit log
```

Hybrid cloud, SSO, Kubernetes, Terraform, SIEM export, and enterprise integrations should remain later phases.

The first CLI step is now implemented as a non-mutating dry-run generator.

## Immediate Implementation Gaps

Before the local RAG MVP starts, the project still needs these decisions:

- Default vector database: Qdrant or Chroma
- Default local model runtime: Ollama or vLLM
- MVP UI choice confirmation: Streamlit first, React later
- Audit storage choice: Postgres only or file-based dev mode plus Postgres

Decisions already made for v0.1:

- Package name: `private-ai-infra-blueprint`
- Python package import: `private_ai_infra`
- CLI entry point: `private-ai`
- License: Apache 2.0
- Initial default vector database: Qdrant
- Initial local runtime default: Ollama
- Generated runtime output: ignored under `generated/*` except `.gitkeep`

## Verification Performed

- Created the planned documentation tree.
- Added GitHub-ready open-source files: `LICENSE`, `NOTICE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.gitignore`, issue templates, and a pull request template.
- Added a Python package skeleton and first CLI implementation.
- Added tests for modes, generation, validation, and CLI behavior.
- Added committed example configs and safe synthetic sample docs/logs.
- Added GitHub Actions CI and a Makefile.
- Checked local Markdown links from `README.md`.
- Checked Markdown code fences for balance.
- Confirmed every docs page has a top-level H1 heading.
- Confirmed newly added documentation is ASCII-only.

Runtime verification:

- `python -m unittest discover -s tests -v` passed.
- `python -m private_ai_infra init --dry-run --mode local-developer --project-name smoke-test --company-name local --output-dir generated/dry-run --force` passed.
- `python -m private_ai_infra validate generated/dry-run` passed.
- `python -m private_ai_infra doctor` ran and reported local environment checks.
