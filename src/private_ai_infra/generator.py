from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .models import DryRunAnswers, get_profile
from .validator import REQUIRED_DRY_RUN_FILES, validate_dry_run


def generate_dry_run(
    output_dir: Path,
    answers: DryRunAnswers,
    *,
    force: bool = False,
) -> dict[str, Path]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = {name: output_dir / name for name in REQUIRED_DRY_RUN_FILES}
    existing = [path for path in targets.values() if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"dry-run output already exists: {names}. Use --force to overwrite generated files."
        )

    writers = {
        "architecture-plan.md": _architecture_plan,
        "stakeholder-checklist.md": _stakeholder_checklist,
        "network-requirements.md": _network_requirements,
        "security-review.md": _security_review,
        "proposed-docker-compose.yml": _proposed_compose,
        "proposed-rbac.yaml": _proposed_rbac,
        "proposed-env.example": _proposed_env,
        "data-source-plan.md": _data_source_plan,
        "model-plan.md": _model_plan,
    }

    for filename, writer in writers.items():
        targets[filename].write_text(writer(answers), encoding="utf-8")

    validation = validate_dry_run(output_dir)
    targets["validation-report.md"].write_text(validation.to_markdown(), encoding="utf-8")
    return targets


def _comma(values: tuple[str, ...]) -> str:
    return ", ".join(values)


def _architecture_plan(answers: DryRunAnswers) -> str:
    profile = get_profile(answers.mode)
    return f"""# Architecture Plan

Generated: {answers.created_at}

Project: {answers.project_name}
Company / workspace: {answers.company_name}
Mode: {profile.title}
Audience: {profile.audience}

## Summary

This dry-run proposes a private AI deployment plan. It does not apply infrastructure changes, create users, expose ports, start containers, or ingest real company data.

## Proposed Flow

```text
User
  -> Web UI or CLI
  -> API backend
  -> Auth and RBAC
  -> RAG pipeline
  -> Vector database ({answers.vector_db})
  -> Local model runtime ({answers.llm_runtime})
  -> Cited answer
  -> Audit log
```

## Deployment Defaults

- Network exposure: {answers.remote_access}
- LLM runtime: {answers.llm_runtime}
- Vector database: {answers.vector_db}
- Embedding model: {answers.embedding_model}
- Departments: {_comma(answers.departments)}
- Audit logging required: {str(answers.audit_logging_required).lower()}

## Safety Notes

{_bullet_list(profile.safety_notes)}

## Next Review

Run:

```bash
private-ai validate {Path('generated/dry-run').as_posix()}
```

Then review every generated file before using `private-ai apply`. The apply command is intentionally not implemented in this early release.
"""


def _stakeholder_checklist(answers: DryRunAnswers) -> str:
    profile = get_profile(answers.mode)
    reviews = "\n".join(f"- [ ] {review.title()} review complete" for review in profile.required_reviews)
    return f"""# Stakeholder Checklist

Generated: {answers.created_at}

Project: {answers.project_name}
Mode: {profile.title}

## Required Reviews

{reviews}

## Business Scope

- [ ] Business goal is documented.
- [ ] Departments are approved: {_comma(answers.departments)}.
- [ ] Production owner is named.
- [ ] Risk owner is named.

## Data Scope

- [ ] Allowed data sources are approved.
- [ ] Forbidden data types are documented.
- [ ] Secrets and credentials are excluded.
- [ ] Deleted-source behavior is defined.

## Security Scope

- [ ] RBAC roles are reviewed.
- [ ] Audit policy is reviewed.
- [ ] Admin access is explicit.
- [ ] Prompt-injection handling is enabled or tracked.

## Network Scope

- [ ] Exposure mode is reviewed: {answers.remote_access}.
- [ ] Ports are documented.
- [ ] Remote access is disabled or explicitly approved.
- [ ] Model runtime is not directly exposed.
"""


def _network_requirements(answers: DryRunAnswers) -> str:
    return f"""# Network Requirements

Generated: {answers.created_at}

## Proposed Exposure

{answers.remote_access}

## Proposed Ports

| Service | Port | Default bind |
| --- | --- | --- |
| API backend | 8080 | 127.0.0.1 |
| Web UI | 8501 | 127.0.0.1 |
| Qdrant | 6333 | private Docker network |
| Postgres | 5432 | private Docker network |
| Ollama / model runtime | 11434 | private Docker network |

## Blocking Rules

- Do not expose the model runtime directly to the public internet.
- Do not bind API or UI to `0.0.0.0` without network review.
- Do not enable hybrid gateway mode without a named network owner.
- Do not open firewall rules during dry-run mode.

## Review Questions

- Is access localhost-only, LAN-only, VPN-only, or gateway-based?
- Which users or groups can reach the UI?
- Is DNS required?
- Is outbound model download allowed?
- Should the server block public internet egress?
"""


def _security_review(answers: DryRunAnswers) -> str:
    blockers = []
    warnings = []
    if answers.remote_access != "localhost":
        warnings.append("Remote or non-local exposure requires network owner review.")
    if not answers.audit_logging_required:
        blockers.append("Audit logging is required for production-like deployments.")
    if answers.cyber_mode_enabled:
        warnings.append("Cyber analyst mode must remain read-only in v1.")

    blocker_text = "\n".join(f"- {item}" for item in blockers) or "- None in generated defaults."
    warning_text = "\n".join(f"- {item}" for item in warnings) or "- None in generated defaults."

    return f"""# Security Review

Generated: {answers.created_at}

## Blocking Findings

{blocker_text}

## Warnings

{warning_text}

## Required Controls

- RBAC before retrieval
- Audit logging for chat, ingestion, validation, and admin actions
- Approved data-source allowlists
- Secret and credential filtering
- Citations for source-grounded answers
- Prompt-injection detection or documented mitigation
- No direct public exposure of model runtimes
- Human approval for risky actions

## Forbidden Data

{_bullet_list(answers.forbidden_data)}

## Generated Answer Snapshot

```json
{_json_like(asdict(answers))}
```
"""


def _proposed_compose(answers: DryRunAnswers) -> str:
    return f"""# Proposed only. Generated by private-ai init --dry-run.
# This file is not applied by dry-run mode.
services:
  api:
    image: private-ai-infra-api:local
    build:
      context: ../../
      dockerfile: deployment/api.Dockerfile
    env_file:
      - proposed-env.example
    ports:
      - "127.0.0.1:8080:8080"
    depends_on:
      - vector-db
      - audit-db
      - model-runtime

  ui:
    image: private-ai-infra-ui:local
    build:
      context: ../../
      dockerfile: deployment/ui.Dockerfile
    ports:
      - "127.0.0.1:8501:8501"
    depends_on:
      - api

  vector-db:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant-data:/qdrant/storage

  audit-db:
    image: postgres:16
    environment:
      POSTGRES_DB: private_ai
      POSTGRES_USER: private_ai
      POSTGRES_PASSWORD: change-me-before-apply
    volumes:
      - audit-db-data:/var/lib/postgresql/data

  model-runtime:
    image: ollama/ollama:latest
    volumes:
      - model-cache:/root/.ollama

volumes:
  qdrant-data:
  audit-db-data:
  model-cache:

x-private-ai-dry-run:
  project_name: "{answers.project_name}"
  mode: "{answers.mode}"
  llm_runtime: "{answers.llm_runtime}"
  vector_db: "{answers.vector_db}"
  generated: "{answers.created_at}"
"""


def _proposed_rbac(answers: DryRunAnswers) -> str:
    return """# Proposed only. Review before apply.
roles:
  manager:
    can_chat: true
    can_ingest: false
    can_view_audit: false
    can_manage_users: false
    collections:
      - policies
      - reports

  developer:
    can_chat: true
    can_ingest: true
    can_view_audit: false
    can_manage_users: false
    collections:
      - docs
      - codebase

  security_analyst:
    can_chat: true
    can_ingest: false
    can_view_audit: true
    can_manage_users: false
    collections:
      - security_logs
      - incident_reports

  admin:
    can_chat: true
    can_ingest: true
    can_view_audit: true
    can_manage_users: true
    requires_explicit_assignment: true
    collections:
      - "*"
"""


def _proposed_env(answers: DryRunAnswers) -> str:
    return f"""# Proposed only. Copy to .env only after review.
PRIVATE_AI_PROJECT_NAME={answers.project_name}
PRIVATE_AI_COMPANY_NAME={answers.company_name}
PRIVATE_AI_MODE={answers.mode}
PRIVATE_AI_BIND_HOST=127.0.0.1
PRIVATE_AI_API_PORT=8080
PRIVATE_AI_UI_PORT=8501

VECTOR_DB={answers.vector_db}
VECTOR_DB_URL=http://vector-db:6333

LLM_RUNTIME={answers.llm_runtime}
LLM_BASE_URL=http://model-runtime:11434
LLM_MODEL=select-model-before-apply
EMBEDDING_MODEL={answers.embedding_model}

AUDIT_DB_URL=postgresql://private_ai:change-me-before-apply@audit-db:5432/private_ai
AUDIT_LOGGING_REQUIRED={str(answers.audit_logging_required).lower()}

DEVELOPER_MODE_ENABLED={str(answers.developer_mode_enabled).lower()}
CYBER_MODE_ENABLED={str(answers.cyber_mode_enabled).lower()}
"""


def _data_source_plan(answers: DryRunAnswers) -> str:
    return f"""# Data Source Plan

Generated: {answers.created_at}

## Approved Sources

{_bullet_list(answers.allowed_data_sources)}

## Forbidden Data

{_bullet_list(answers.forbidden_data)}

## Denied Patterns

```text
**/.env
**/.env.*
**/*.pem
**/*.key
**/id_rsa
**/id_ed25519
**/credentials*
**/secrets*
**/*token*
```

## Ingestion Rules

- Ingest only approved paths.
- Skip denied patterns before chunking or embedding.
- Record skipped files in audit logs without storing secret contents.
- Require data-owner review before adding new production sources.
- Track source path, collection, owner, timestamp, and checksum metadata.
"""


def _model_plan(answers: DryRunAnswers) -> str:
    return f"""# Model Plan

Generated: {answers.created_at}

## Proposed Runtime

- Runtime: {answers.llm_runtime}
- Embedding model: {answers.embedding_model}
- Vector database: {answers.vector_db}

## Runtime Notes

- Ollama is a practical default for local developer mode.
- vLLM is a stronger fit for GPU servers and concurrent usage.
- NVIDIA NIM can be used for NVIDIA-focused enterprise deployments.
- DGX Spark and DGX-class systems should still keep the model runtime behind the application backend.

## Evaluation Requirements

- At least 10 source-grounded questions per collection.
- At least 5 refusal tests for missing or forbidden information.
- Citation checks for every answer.
- Prompt-injection tests using sample hostile documents.
- RBAC tests proving users cannot retrieve disallowed collections.

## Open Decisions

- Final LLM model
- Final embedding model
- Context window target
- Reranker requirement
- Hybrid search requirement
- Low-confidence refusal threshold
"""


def _bullet_list(values: tuple[str, ...]) -> str:
    return "\n".join(f"- {value}" for value in values)


def _json_like(values: dict[str, object]) -> str:
    lines = ["{"]
    items = list(values.items())
    for index, (key, value) in enumerate(items):
        comma = "," if index < len(items) - 1 else ""
        if isinstance(value, tuple):
            rendered = "[" + ", ".join(f'"{item}"' for item in value) + "]"
        elif isinstance(value, bool):
            rendered = str(value).lower()
        else:
            rendered = f'"{value}"'
        lines.append(f'  "{key}": {rendered}{comma}')
    lines.append("}")
    return "\n".join(lines)

