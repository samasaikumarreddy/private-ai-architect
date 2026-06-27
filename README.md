# Private AI Architect

[![CI](https://github.com/samasaikumarreddy/private-ai-architect/actions/workflows/ci.yml/badge.svg)](https://github.com/samasaikumarreddy/private-ai-architect/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/samasaikumarreddy/private-ai-architect)](LICENSE)

Status: v0.2.1 local RAG quality is released. The CLI safely indexes approved
documents and bounded source code, uses BM25 retrieval, evaluates retrieval
and refusal cases, optionally generates cited answers with an installed
loopback Ollama model, and refuses unsupported questions.

The v0.3 development branch adds a guided, branching architect that produces a
normalized checksummed blueprint and review documents. It performs no cloud
discovery, hardware configuration, migration, or infrastructure changes.

Plan, generate, validate, and eventually migrate private AI systems across
developer machines, GPU servers, DGX Spark, and hybrid cloud environments.

Private AI Architect is an open-source, security-first path from useful local
RAG to guided private AI infrastructure. Today it provides a safe local RAG
CLI, local RAG, dry-run planning, and a planning-only guided architect. The
architect asks workflow-specific questions, records unknown decisions instead
of guessing, and builds a normalized blueprint plus review documents.

The product supports three journeys:

1. Build local RAG with a CPU, RTX GPU, or approved company GPU endpoint.
2. Plan the integration of newly purchased private hardware such as DGX Spark
   or a generic NVIDIA GPU server.
3. Plan a future migration of selected cloud AI workloads to private
   infrastructure while identifying identity, gateway, monitoring, and
   rollback requirements.

The project started documentation-led and now includes its first usable CLI
milestone: `private-ai init --dry-run` generates a proposed review pack without
applying infrastructure changes.

**New to private AI?** Start with the [Beginner's Guide](docs/beginner-guide.md).
It uses simple explanations and diagrams to show what works today and what the
project will build next.

**Ready to run it?** Follow [QUICKSTART.md](QUICKSTART.md) using the included
synthetic documents, or use the copy-and-paste
[Version Test Guide](docs/version-test-guide.md).

## Why Star This Project

Star this repo if you want an open-source path for:

- Adding AI to a developer workspace without exposing private files.
- Building RAG over approved company documents.
- Running local AI with Ollama, vLLM, NVIDIA NIM, or similar runtimes.
- Integrating GPU servers or DGX Spark through guided compatibility,
  networking, identity, and operations questions.
- Planning staged cloud-to-private AI migration with verification and rollback.
- Generating dry-run configs before touching real infrastructure.
- Adding RBAC, audit logs, and safe ingestion from day one.
- Helping build a provider-neutral blueprint and plugin ecosystem.

The 10k-star goal is not cosmetic. It means enough developers care about private, useful, security-aware AI infrastructure that the ecosystem can grow around it.

## Open-Source Mission

The goal is to help developers and companies integrate AI into real workspaces safely:

- A developer should be able to test private AI over approved local files.
- A small company should be able to run a private document assistant without enterprise hardware.
- A small business with new GPU hardware should receive a guided integration
  and verification plan.
- An enterprise team should be able to assess one approved cloud AI workload
  and generate a reviewable migration and rollback plan.

This should become a practical open-source starting point, not a vendor-locked demo.

## Who This Is For

- Developers building local AI assistants over approved documents, with
  bounded source-code ingestion in v0.2.1.
- Teams adding RAG to internal knowledge bases.
- Startups and small companies that need private document search.
- Security teams reviewing AI before company rollout.
- Infra teams deploying on GPU servers or DGX-class hardware.
- Cloud teams moving selected Azure OpenAI or AWS Bedrock workloads.
- AI engineers choosing model, embedding, and retrieval architecture.
- Open-source contributors who want private AI to be easier and safer.

## What This Project Is

Private AI Infrastructure Blueprint is a guided architecture and migration
system for:

- Local private RAG
- Small-company GPU integration
- Generic NVIDIA GPU servers
- DGX Spark and later DGX-class targets
- Hybrid cloud/private architecture
- Staged migration from supported cloud AI providers

The intended product lifecycle is:

```text
choose workflow
  -> answer relevant questions
  -> optional narrow read-only discovery
  -> normalized blueprint
  -> generate
  -> validate
  -> human review
  -> apply
  -> verify
  -> controlled migration and evidence
```

Current implementation:

- `private-ai architect` branching across local RAG, private GPU planning, and
  cloud migration planning
- Stable schema `1.0` JSON blueprint with checksum, unknowns, risks, and
  explicit out-of-scope items
- `private-ai blueprint validate`
- Deterministic `summary.md`, `decisions-needed.md`, `security-risks.md`, and
  `next-steps.md`
- Python package skeleton
- `private-ai init --dry-run`
- Dry-run artifact generator
- Machine-readable dry-run metadata
- `private-ai validate`
- `private-ai doctor`
- `private-ai modes`
- `private-ai ingest` for local JSON indexing
- Bounded source-code ingestion with default and operator-defined exclusions
- `private-ai chat` for retrieval-only cited excerpts
- Optional `private-ai chat --model <installed-model>` for local
  Ollama-generated answers with retrieval citations
- Evidence-based refusal and graceful retrieval fallback
- Citation-range validation that rejects missing or invented source numbers
- Lexical claim-to-cited-source validation
- BM25 ranking with relative relevance filtering
- `private-ai evaluate` for repeatable retrieval and refusal cases
- Query-focused Markdown sections to reduce unrelated model context
- Loopback-only Ollama access with installed-model preflight
- Verified `llama3.2:1b` smoke test on an RTX 3060 Laptop GPU
- Optional interactive dry-run prompts
- Safety stubs for not-yet-implemented commands
- 50 unit tests; GitHub CI runs on Python 3.11 and 3.12

Not implemented yet:

- Real Docker images
- Vector database writes
- Semantic embeddings and vector retrieval
- Web UI
- Cloud provider discovery
- Hardware-verified DGX Spark profile
- `apply`, verification, shadowing, and cutover

The private GPU and cloud migration journeys collect user-provided planning
requirements only. They do not configure DGX systems, call provider APIs, or
perform migration work.

## Quickstart

Requirements:

- Python 3.11+

Install locally:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Generate a safe dry-run plan:

```bash
private-ai init --dry-run --mode local-developer --project-name private-ai-demo --output-dir generated/dry-run --force
```

Validate the generated review pack:

```bash
private-ai validate generated/dry-run
```

Inspect local readiness:

```bash
private-ai doctor
```

Generate and validate a v0.3 guided architecture pack without reading the
named document sources:

```bash
private-ai architect --answers-file examples/architect/local-rag-answers.json --output-dir generated/architect --force
private-ai blueprint validate generated/architect
```

Run `private-ai architect` without `--answers-file` for beginner-friendly
interactive prompts. The first question selects `local-rag`, `private-gpu`, or
`cloud-migration`; irrelevant journey questions are omitted.

Try the retrieval-only local preview:

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
private-ai chat "what are the AI usage rules?" --index generated/index/index.json
```

This invocation returns cited source excerpts from a local JSON index without
calling a model.

Optionally use an already-installed local Ollama model:

```bash
ollama pull llama3.2:1b
private-ai chat "what are the AI usage rules?" --index generated/index/index.json --model llama3.2:1b
```

The model download occurs only because the operator explicitly runs
`ollama pull`. The `private-ai` command verifies the model is installed and
never downloads one. If local Ollama is unavailable or generated citations
are invalid, it returns the retrieval-only result with a warning. Only
loopback Ollama URLs are accepted in v0.2.

Run tests:

```bash
python -m unittest discover -s tests -v
```

Dry-run output is written under `generated/dry-run/` and is intentionally ignored by Git except for `generated/.gitkeep`.

## Core Principles

- Private by default
- Dry-run before apply
- Least privilege access
- Explicit data-source approval
- Role-based configuration
- Human approval for risky actions
- Audit every sensitive action
- No direct internet exposure of model runtimes
- Narrow, read-only provider discovery
- Storage, processing, and cloud transit modeled separately
- No compliance certification claims
- Verification and rollback before production cutover

## Local RAG v0.2.1 Flow

The implemented local flow stays narrow:

```text
User
  -> private-ai CLI
  -> approved local documents
  -> denied-file filtering
  -> local BM25 JSON index
  -> evidence check
  -> retrieval-only excerpts or local Ollama
  -> citation validation
  -> cited answer, safe fallback, or refusal
```

Implemented local capabilities:

- Dry-run mode that generates plans but applies nothing
- Local document ingestion from approved paths
- Bounded source-code ingestion with generated/dependency directory pruning
- RAG Q&A with citations
- Refusal when evidence is missing
- Retrieval fallback when Ollama or its response is unavailable
- Rejection of missing or out-of-range generated citations
- Rejection of claims without lexical support in their cited source
- Repeatable retrieval evaluation cases
- Localhost-only model access
- Automated tests and a documented RTX smoke test

Semantic embeddings, vector storage, runtime RBAC, audit storage, web UI,
cloud discovery, DGX Spark verification, hybrid gateways, and production
cutover are later milestones. See the
[Roadmap](docs/roadmap.md).

## Documentation Map

- [Quickstart](QUICKSTART.md)
- [Version Test Guide](docs/version-test-guide.md)
- [Beginner's Guide](docs/beginner-guide.md)
- [Vision](docs/vision.md)
- [Guided Architect Workflow](docs/guided-architect-workflow.md)
- [Blueprint Schema](docs/blueprint-schema.md)
- [Open-Source Mission](docs/open-source-mission.md)
- [GitHub Growth Strategy](docs/github-growth-strategy.md)
- [Launch Checklist](docs/launch-checklist.md)
- [CLI Reference](docs/cli-reference.md)
- [Developer Workflow](docs/developer-workflow.md)
- [Project Investigation](docs/project-investigation.md)
- [Architecture](docs/architecture.md)
- [Local RAG MVP](docs/local-rag-mvp.md)
- [RAG Quality And Code Ingestion v0.2.1](docs/rag-quality-v0.2.1.md)
- [Knowledge Workspace And Memory Optimization](docs/knowledge-workspace-and-memory-optimization.md)
- [Deployment Modes](docs/deployment-modes.md)
- [Hardware And Runtime Options](docs/hardware-and-runtime-options.md)
- [Dry-Run Mode](docs/dry-run-mode.md)
- [Stakeholder Workflow](docs/stakeholder-workflow.md)
- [Security Principles](docs/security-principles.md)
- [Threat Model](docs/threat-model.md)
- [Configuration Reference](docs/configuration-reference.md)
- [MVP Scope](docs/mvp-scope.md)
- [Roadmap](docs/roadmap.md)

The original long-form blueprint remains available at [README_private_ai_infra_blueprint.md](README_private_ai_infra_blueprint.md).

## CLI Status

Implemented:

```bash
private-ai init --dry-run
private-ai validate
private-ai doctor
private-ai modes
private-ai ingest
private-ai chat
private-ai evaluate
private-ai architect
private-ai blueprint validate
```

Planned but intentionally blocked:

```bash
private-ai apply
private-ai audit
```

No production-impacting command should run before validation, review, and
approval of the exact blueprint revision.

## Launch Readiness

This project should not be promoted heavily until it has at least:

- A clear README and docs
- Apache 2.0 license
- Contributing and security policy
- Dry-run CLI skeleton
- Example generated config pack
- Local RAG MVP plan
- Safe default deployment story
- Issue templates for contributors

The launch plan is tracked in [docs/launch-checklist.md](docs/launch-checklist.md).

## Contributing And Security

- Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
- Read [SECURITY.md](SECURITY.md) before reporting security-sensitive issues.
- Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) in project spaces.
- Do not commit real company data, credentials, logs, secrets, or private keys.
- Keep examples runnable on normal developer machines unless the example is explicitly for GPU or DGX-class deployments.

## Suggested Repository Shape

```text
private-ai-infra-blueprint/
  README.md
  docs/
  wizard/
  app/
    backend/
    ui/
  configs/
    examples/
  deployment/
  examples/
  generated/
  tests/
  pyproject.toml
```

The current repository contains documentation plus the first Python CLI implementation. The application runtime structure above is the planned next implementation path.

## License Recommendation

This project uses the Apache License 2.0. That license is a good fit for open-source infrastructure because it includes explicit patent protection.
