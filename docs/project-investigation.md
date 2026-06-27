# Project Investigation

Last updated: 2026-06-27

This file records the verified repository state and the product decisions made
during the documentation and implementation investigation.

## Product Finding

The project is not primarily another local chat interface. Its intended product
is a guided private-AI architect:

```text
workflow-specific questions
  + narrow approved discovery
  -> normalized blueprint
  -> proposed artifacts
  -> validation
  -> human review
  -> future apply and verification
  -> future staged migration and evidence
```

The local RAG stack is the first reference target. It proves that generated
runtime configuration can produce a useful cited answer. Private GPU hardware
and cloud migration paths come after that proof.

## Primary Workflows

1. A developer builds local RAG using a CPU, RTX GPU, or approved company GPU
   endpoint.
2. A small business configures newly purchased DGX Spark or generic private GPU
   hardware.
3. A cloud-integrated company assesses and migrates a selected Azure OpenAI or
   AWS Bedrock workload while retaining approved identity, gateway, and
   monitoring services.

The questionnaire must branch immediately so users do not receive irrelevant
questions.

## Verified Repository State

The repository is a local Git repository on branch `main` with three baseline
commits created before this documentation revision.

Implemented:

- Python package and `private-ai` command
- Dry-run review-pack generation
- Machine-readable dry-run answers and summary
- Configuration validation
- Local environment readiness checks
- Deployment-mode listing
- Local JSON document indexing
- Retrieval-only search with cited excerpts
- Denied-file and likely-secret filtering
- Synthetic sample documents and logs
- Unit tests and GitHub Actions CI
- Apache 2.0 license and community governance files

Not implemented:

- Normalized blueprint schema
- Complete branching question graph
- Docker RAG runtime
- Vector database writes and embeddings
- Local model inference
- Model-generated cited answers
- Runtime RBAC and audit store
- Cloud provider discovery
- Hardware-verified DGX Spark target
- Infrastructure apply, verification, shadowing, cutover, or rollback

No public GitHub repository or remote has been confirmed.

## Documentation Decisions

- `README.md` is the canonical entry point.
- `docs/vision.md` defines the guided architect product.
- `docs/guided-architect-workflow.md` defines the three user journeys and
  controlled lifecycle.
- `docs/architecture.md` separates question, discovery, blueprint, generation,
  validation, apply, verification, and evidence layers.
- `docs/configuration-reference.md` proposes the normalized blueprint and
  governance model.
- `docs/deployment-modes.md` separates workflow intent from deployment target.
- `docs/mvp-scope.md` keeps the first runtime proof to local RAG.
- `docs/roadmap.md` gives discovery, hardware targets, and production traffic
  migration separate releases.
- `docs/security-principles.md` and `docs/threat-model.md` cover cloud transit,
  discovery credentials, GPU exhaustion, migration safety, and false compliance
  assurance.

The original `README_private_ai_infra_blueprint.md` remains a historical concept
document. Current scope and sequencing come from the canonical README and
`docs/`.

## Key Engineering Boundaries

- Discovery is provider-specific, read-only, and scope-limited.
- The first cloud scope is selected Azure OpenAI deployment metadata, not a
  complete subscription inventory.
- Unknown facts remain unresolved rather than guessed.
- Storage, processing, transit, logging, and telemetry locations are distinct.
- A framework label activates advisory checks; it does not certify compliance.
- DGX Spark configurations require ARM64 and model/runtime compatibility tests.
- Cloud WAF protection does not replace private ingress admission control.
- Production shadowing, canary, and rollback come after the target and provider
  paths are proven.

## Immediate Build Priority

The next implementation should remain:

```text
local developer questions
  -> local blueprint
  -> Docker Compose
  -> approved sample ingestion
  -> embeddings and vector retrieval
  -> local model answer with citations
  -> refusal and audit tests
```

Cloud discovery and migration work should not begin by weakening or skipping
this reference implementation.

## Previous Verification

Before this documentation revision:

- `python -m unittest discover -s tests -v` passed 13 tests.
- Dry-run generation and validation passed.
- `private-ai doctor` completed.
- Sample document ingestion completed.
- Retrieval-only cited search completed.
- Markdown links, code fences, and ASCII checks passed.

Documentation-only changes in this revision require fresh Markdown and link
validation but do not change runtime behavior.
