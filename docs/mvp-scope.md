# MVP Scope

The MVP should prove that the project can safely guide a private local RAG deployment from planning to operation.

## In Scope

- CLI setup wizard
- Dry-run generation
- Validation command
- Docker Compose local deployment
- FastAPI backend
- Streamlit UI
- Local auth or simple session auth
- YAML RBAC
- Local folder ingestion
- Secret and denied-path filtering
- Qdrant or Chroma vector storage
- Ollama or vLLM local model runtime
- RAG Q&A with citations
- Postgres audit log
- Basic admin/config summary
- Sample company documents
- Sample cyber logs
- Read-only cyber log summarization
- Read-only developer assistant over approved docs

## Out Of Scope For MVP

- Autonomous remediation
- Public SaaS hosting
- Kubernetes
- Terraform
- Full SSO/LDAP/Active Directory
- Multi-tenant hosted control plane
- Production compliance certification
- Direct shell execution from cyber mode
- Automatic code modification in developer mode
- Ingesting arbitrary machine-wide folders
- Storing real secrets

## Implementation Milestones

1. Project skeleton and packaging - started
2. CLI command shell - started
3. Wizard questions and answer model - started
4. Dry-run generators - started
5. Config validator - started
6. Docker Compose MVP stack
7. Backend auth and RBAC enforcement
8. Ingestion pipeline
9. RAG query path with citations
10. Audit logging
11. Streamlit UI
12. Sample cyber log summarizer
13. Tests and documentation updates

## Acceptance Criteria

MVP is done when a user can:

- Run `private-ai init --dry-run`
- Answer setup questions for local developer mode
- Review generated config and documentation artifacts
- Run `private-ai validate`
- Run `private-ai apply` only after validation passes
- Start the Docker Compose stack
- Ingest sample documents
- Ask questions and get cited answers
- See audit records for ingestion and chat
- Confirm denied files were skipped
- Run cyber log summarization without remediation actions

## Test Coverage Targets

Minimum tests:

- Wizard answer parsing
- Dry-run output generation
- Validation blockers
- RBAC collection filtering
- Denied-path ingestion filtering
- Audit event writing
- RAG citation formatting
- Cyber mode action blocking

## Recommended First Build Path

Build the non-networked local developer path first:

```text
CLI wizard
  -> dry-run files
  -> validator
  -> local Docker Compose
  -> sample ingestion
  -> cited chat
  -> audit log
```

Do not build hybrid cloud gateway mode before the local private path works.

## Current v0.1 Progress

Implemented:

- Python package skeleton
- `private-ai init --dry-run`
- Dry-run review pack generation
- `private-ai validate`
- `private-ai doctor`
- `private-ai ingest` for local JSON indexing
- `private-ai chat` for retrieval-only cited excerpts
- Unit tests for the first CLI milestone

Not implemented:

- Full role-specific interactive wizard
- Real Docker images
- Vector database writes
- Local model inference
- Web UI
- Runtime audit log storage
