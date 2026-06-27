# Private AI Infrastructure Blueprint

Status: early open-source guided architect with a working dry-run CLI, local
retrieval, and optional Ollama-backed cited answers. Semantic vector retrieval,
hardware deployment, and cloud migration paths are not implemented yet.

Plan, generate, validate, and eventually migrate private AI systems across
developer machines, GPU servers, DGX Spark, and hybrid cloud environments.

Private AI Infrastructure Blueprint is an open-source guided architect. It asks
workflow-specific questions, records unknown decisions instead of guessing,
builds a normalized blueprint, generates proposed configuration and migration
artifacts, validates known risks, and produces evidence for human review.

The product supports three journeys:

1. Build local RAG with a CPU, RTX GPU, or approved company GPU endpoint.
2. Configure newly purchased private hardware such as DGX Spark or a generic
   NVIDIA GPU server.
3. Migrate selected Azure OpenAI or AWS Bedrock workloads to private
   infrastructure while retaining useful cloud identity, gateway, and
   monitoring services.

The project started documentation-led and now includes its first usable CLI
milestone: `private-ai init --dry-run` generates a proposed review pack without
applying infrastructure changes.

**New to private AI?** Start with the [Beginner's Guide](docs/beginner-guide.md).
It uses simple explanations and diagrams to show what works today and what the
project will build next.

**Ready to run it?** Follow [QUICKSTART.md](QUICKSTART.md) using the included
synthetic documents.

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

- Developers building local AI assistants over approved docs or code.
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

- Python package skeleton
- `private-ai init --dry-run`
- Dry-run artifact generator
- Machine-readable dry-run metadata
- `private-ai validate`
- `private-ai doctor`
- `private-ai modes`
- `private-ai ingest` for local JSON indexing
- `private-ai chat` for retrieval-only cited excerpts
- Optional `private-ai chat --model <installed-model>` for local
  Ollama-generated answers with retrieval citations
- Evidence-based refusal and graceful retrieval fallback
- Optional interactive dry-run prompts
- Safety stubs for not-yet-implemented commands
- Unit tests

Not implemented yet:

- Normalized blueprint and complete branching questionnaire
- Real Docker images
- Vector database writes
- Semantic embeddings and vector retrieval
- Web UI
- Cloud provider discovery
- Hardware-verified DGX Spark profile
- `apply`, verification, shadowing, and cutover

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

Try the retrieval-only local preview:

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
private-ai chat "what are the AI usage rules?" --index generated/index/index.json
```

This invocation returns cited source excerpts from a local JSON index without
calling a model.

Optionally use an already-installed local Ollama model:

```bash
private-ai chat "what are the AI usage rules?" --index generated/index/index.json --model <installed-model>
```

The command verifies the model is installed and never downloads one. If local
Ollama is unavailable, it returns the retrieval-only result with a warning.
Only loopback Ollama URLs are accepted in v0.2.

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

## MVP Target

The first implementation should stay narrow:

```text
User
  -> Web UI or CLI
  -> Auth and role check
  -> FastAPI backend
  -> RAG pipeline
  -> Vector database
  -> Local LLM runtime
  -> Answer with citations
```

MVP capabilities:

- Local developer question branch
- Dry-run mode that generates plans but applies nothing
- Docker Compose local deployment
- Local document ingestion from approved paths
- RAG Q&A with citations
- Refusal when evidence is missing
- Basic collection permissions
- Redacted local audit events
- Automated CPU and documented RTX smoke tests

Cloud discovery, DGX Spark verification, hybrid gateways, and production
cutover are later milestones. See the [Roadmap](docs/roadmap.md).

## Documentation Map

- [Quickstart](QUICKSTART.md)
- [Beginner's Guide](docs/beginner-guide.md)
- [Vision](docs/vision.md)
- [Guided Architect Workflow](docs/guided-architect-workflow.md)
- [Open-Source Mission](docs/open-source-mission.md)
- [GitHub Growth Strategy](docs/github-growth-strategy.md)
- [Launch Checklist](docs/launch-checklist.md)
- [CLI Reference](docs/cli-reference.md)
- [Developer Workflow](docs/developer-workflow.md)
- [Project Investigation](docs/project-investigation.md)
- [Architecture](docs/architecture.md)
- [Local RAG MVP](docs/local-rag-mvp.md)
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
