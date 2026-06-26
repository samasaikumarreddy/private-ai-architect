# Configuration Reference

This reference defines the planned configuration artifacts. File names may change during implementation, but the responsibilities should remain stable.

## Generated Files

| File | Purpose |
| --- | --- |
| `.env` | Runtime environment settings for local deployment. |
| `docker-compose.yml` | Service topology for local or small company deployment. |
| `rbac.yaml` | Roles, permissions, and collection access. |
| `rag-config.yaml` | Retrieval, chunking, citation, and confidence behavior. |
| `data-sources.yaml` | Approved ingestion sources and denied paths. |
| `audit-policy.yaml` | Audit events, retention, redaction, and export settings. |
| `network-plan.md` | Ports, bind addresses, DNS, VPN, and gateway notes. |
| `security-review.md` | Risks, blockers, warnings, and approvals. |
| `model-config.yaml` | LLM runtime, model, embedding model, and resource expectations. |
| `eval-plan.md` | Test questions, expected citations, refusal checks, and safety tests. |

## Example Environment

```dotenv
PRIVATE_AI_MODE=local_developer
PRIVATE_AI_BIND_HOST=127.0.0.1
PRIVATE_AI_API_PORT=8080
PRIVATE_AI_UI_PORT=8501

VECTOR_DB=qdrant
VECTOR_DB_URL=http://qdrant:6333

LLM_RUNTIME=ollama
LLM_BASE_URL=http://ollama:11434
LLM_MODEL=llama3.1

AUDIT_DB_URL=postgresql://private_ai:change-me@postgres:5432/private_ai
AUDIT_LOGGING_REQUIRED=true
```

Generated examples must never contain real secrets.

## Example Data Sources

```yaml
sources:
  - name: company_policies
    type: folder
    path: ./examples/sample-company-docs/policies
    collection: policies
    approved_by: data-owner@example.com
    schedule: manual

denied_patterns:
  - "**/.env"
  - "**/*.pem"
  - "**/*.key"
  - "**/id_rsa"
  - "**/credentials*"
  - "**/secrets*"
```

## Example Retrieval Config

```yaml
retrieval:
  chunk_size: 800
  chunk_overlap: 120
  top_k: 6
  hybrid_search: false
  reranker_enabled: false
  citations_required: true
  low_confidence_behavior: refuse
  prompt_injection_detection: warn_and_filter
```

## Validation Rules

Validation should produce blocking errors for:

- Public bind address in production without network approval
- Missing audit policy in production
- Missing RBAC file
- Admin role assigned without explicit approval
- Data source outside approved paths
- Secret-like files included in ingestion
- Cyber remediation actions enabled in v1
- `apply` attempted before `validate`

Validation should produce warnings for:

- CPU-only deployment with large model
- Missing evaluation set
- No backup plan
- No audit export
- Broad wildcard collections
- Query text logging enabled without redaction review

## Configuration Lifecycle

```text
Plan
  -> Dry run
  -> Review
  -> Validate
  -> Apply
  -> Test
  -> Ingest
  -> Operate
  -> Audit
```

Configuration should be treated as a controlled artifact. Production changes should be reviewable, repeatable, and auditable.

