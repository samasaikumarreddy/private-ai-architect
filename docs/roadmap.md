# Roadmap

The roadmap is ordered to reduce risk early. Documentation, dry-run behavior, validation, and local private operation come before enterprise networking.

## Phase 0: Documentation Blueprint

Deliverables:

- README
- Architecture docs
- Deployment modes
- Dry-run behavior
- Stakeholder workflow
- Security principles
- Threat model
- MVP scope
- Roadmap

Exit criteria:

- A developer can understand what to build first.
- A security reviewer can understand the intended guardrails.
- A manager can understand business purpose and non-goals.

## Phase 1: CLI Wizard

Status: started.

Deliverables:

- `private-ai init`
- `private-ai init --dry-run`
- Role-specific questions
- Answer schema
- Generated config files
- Generated review documents

Exit criteria:

- Dry-run produces a complete review pack.
- Dry-run does not mutate infrastructure.
- Generated files are deterministic enough to test.

Implemented in v0.1:

- Python package skeleton
- `private-ai init --dry-run`
- `private-ai validate`
- `private-ai doctor`
- `private-ai modes`
- Generated dry-run review pack
- Machine-readable dry-run metadata
- Unit tests

Still needed:

- More complete interactive wizard prompts
- Richer answer schema
- More role-specific question sets
- More validation rules
- Pack promotion workflow

## Phase 2: Local RAG MVP

Deliverables:

- Docker Compose stack
- FastAPI backend
- Streamlit UI
- Local model runtime integration
- Vector database integration
- Document ingestion
- Cited answers

Exit criteria:

- User can ingest sample docs and ask cited questions locally.
- System works without DGX-class hardware.
- Services bind to localhost by default.

## Phase 3: Security Layer

Deliverables:

- YAML RBAC enforcement
- Audit logging
- Approved data paths
- Secret filtering
- Prompt-injection handling
- Validation blockers

Exit criteria:

- Users cannot retrieve collections outside their role.
- Production config without audit logging is blocked.
- Unsafe network exposure is blocked by validation.

## Phase 4: Developer Assistant Mode

Deliverables:

- Code/document RAG
- Internal architecture search
- Task checklist generation
- Read-only developer workflow

Exit criteria:

- Developer assistant can answer from approved code/docs.
- No code modification or Git push is performed by default.

## Phase 5: Cyber Analyst Mode

Deliverables:

- Sample log ingestion
- Alert summarization
- Suspicious event explanation
- Incident note drafting
- Human review workflow

Exit criteria:

- Cyber mode summarizes and explains logs.
- Cyber mode cannot execute remediation actions.

## Phase 6: Network Templates

Deliverables:

- VPN templates
- Firewall checklist
- Nginx reverse proxy template
- Allowed-port documentation
- Hybrid gateway design

Exit criteria:

- Remote access paths are documented and reviewable.
- Direct public model exposure remains blocked.

## Phase 7: Enterprise Extensions

Deliverables:

- SSO
- LDAP or Active Directory integration
- Kubernetes manifests
- Terraform templates
- SIEM export
- Model runtime plugins
- Compliance-oriented templates

Exit criteria:

- Enterprise teams can integrate identity, network, logging, and deployment automation without changing the core safety model.
