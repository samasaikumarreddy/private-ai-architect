# MVP Scope

The MVP is the working local RAG reference deployment. It proves that the
project can move from guided planning to a useful, private, cited answer without
claiming cloud migration or production readiness.

This runtime is not the whole product. It is the first target generated and
validated by the guided architect.

## Primary User

A developer with:

- Python 3.11 or newer
- Docker
- A CPU or supported RTX-class GPU
- Synthetic sample documents or explicitly approved local files
- No requirement for DGX hardware or cloud credentials

## In Scope

- Local developer question branch
- Dry-run generation and validation
- Docker Compose reference stack
- Private API
- Ollama model runtime
- Qdrant vector storage
- Approved local-folder ingestion
- Secret and denied-path filtering
- Model-generated RAG answers with citations
- Refusal when sources do not support an answer
- Localhost-only defaults
- Basic collection permissions
- Local audit events
- Sample company documents
- Automated installation and smoke tests

The implementation may choose equivalent components when testing reveals a
clear technical reason, but the user-visible acceptance criteria must remain.

## Out Of Scope

- DGX Spark verification
- Cloud provider discovery
- Azure or AWS infrastructure generation
- Production traffic shadowing or canary cutover
- Automatic rollback
- Kubernetes
- Enterprise SSO, LDAP, or Active Directory
- Multi-tenant hosted control plane
- Compliance certification
- Autonomous remediation
- Arbitrary machine-wide ingestion
- Storing real credentials
- Public model or database exposure

## Implementation Milestones

1. Preserve existing dry-run and validation behavior.
2. Define the local branch of the normalized blueprint.
3. Add the Docker Compose service topology.
4. Integrate Ollama and a supported default model.
5. Integrate Qdrant and local embeddings.
6. Add safe ingestion into the vector store.
7. Add grounded answer generation with citations and refusal behavior.
8. Add local identity or session boundaries and collection checks.
9. Add redacted audit events.
10. Add smoke, retrieval, grounding, failure, and denied-file tests.
11. Document supported CPU and RTX paths.

## Acceptance Criteria

MVP is complete when a new user can:

1. Run the readiness check.
2. Generate a local developer blueprint and proposed deployment pack.
3. Validate the pack.
4. Start the reference stack with one documented command.
5. Ingest the included synthetic documents.
6. Ask a question and receive a model-generated answer with valid citations.
7. Ask an unsupported question and receive an appropriate refusal.
8. Confirm denied files were not indexed.
9. Confirm services are not publicly exposed.
10. Inspect redacted audit events for ingestion and chat.
11. Stop and remove the test stack without losing control of source files.

## Test Requirements

- Question-branch selection
- Blueprint parsing and schema validation
- Deterministic generation
- Unsafe bind-address blocker
- Denied-path and secret-file filtering
- Collection authorization
- Vector ingestion and deletion
- Citation source integrity
- Unsupported-answer refusal
- Prompt-injection test cases
- Audit redaction
- Clean start and stop
- CPU smoke test
- Documented RTX smoke test

## Current v0.2 Progress

Implemented:

- Python package and CLI
- Dry-run review-pack generation
- Configuration validation
- Local readiness checks
- Local JSON indexing
- Retrieval-only cited excerpts
- Optional local Ollama-backed answers over retrieved chunks
- Installed-model preflight with no automatic downloads
- Evidence-based refusal and graceful retrieval fallback
- Denied-file patterns
- Unit tests

Not implemented:

- Normalized blueprint schema
- Full branching questionnaire
- Docker runtime stack
- Vector database writes
- Embedding model
- Semantic retrieval
- Runtime RBAC and audit storage

## Safety Gate

Hybrid cloud gateway and migration automation must not delay the local MVP, but
they also must not reuse unverified local configuration as production
infrastructure. Every later target gets its own compatibility, security, and
verification tests.
