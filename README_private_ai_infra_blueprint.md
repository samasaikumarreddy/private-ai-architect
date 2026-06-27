# Private AI Infrastructure Blueprint

> **Historical concept document:** This was the original long-form project
> proposal. The canonical product definition, current status, scope, and
> sequencing now live in [README.md](README.md) and the [docs](docs/) folder.
> In particular, see
> [Guided Architect Workflow](docs/guided-architect-workflow.md) and
> [Roadmap](docs/roadmap.md). Where this document conflicts with those files,
> the canonical documentation takes precedence.

> Documentation status: this original long-form blueprint has been split into the canonical project README and focused docs under `docs/`. Keep this file as the source blueprint/history, and use `README.md` as the entry point for readers.

A guided, role-based, security-first reference architecture for deploying private company AI systems such as RAG assistants, developer assistants, and SOC/cyber analyst assistants on local Linux machines, GPU servers, DGX-class hardware, or hybrid cloud/on-prem environments.

This project is **not just another RAG app**.

It is a configurable deployment blueprint that helps companies, developers, network engineers, security teams, and AI engineers set up private AI infrastructure in a structured sequence.

---

## Project Vision

Companies want AI assistants, but they often face problems like:

- Sensitive files cannot be sent directly to public AI tools.
- Teams do not know how to structure RAG deployments securely.
- Networking, VPN, access control, logging, and data permissions are confusing.
- Developers may have access to company files but not enterprise hardware.
- Small companies may not own DGX Spark or GPU servers.
- Management, networking, security, data, and development teams often lack a step-by-step deployment flow.
- Teams want to test the setup before applying changes to real infrastructure.

This project solves that by providing:

> A guided enterprise AI deployment workflow with architecture docs, setup wizard, dry-run mode, generated configs, security guardrails, and modular deployment options.

---

## What This Project Supports

### 1. Local Developer Mode

For a developer who has access to company files and wants to build or test a private AI assistant on a Linux machine.

Example use cases:

- Ask questions from company PDFs, docs, manuals, and notes.
- Search internal documentation privately.
- Build a dev assistant over codebase/docs.
- Test RAG locally before asking for enterprise approval.

Recommended stack:

- Linux
- Docker Compose
- Ollama or vLLM
- Chroma / Qdrant
- FastAPI
- Streamlit / React UI
- Local folders as data source

---

### 2. Small Company Mode

For small businesses that do not have DGX Spark or enterprise GPU hardware.

Example use cases:

- HR policy assistant
- Internal document search
- Invoice/document Q&A
- Basic IT support assistant
- Controlled file-based RAG

Recommended stack:

- CPU or small GPU server
- Docker Compose
- Local authentication
- Role-based access
- Audit logs
- Optional VPN access

---

### 3. GPU Server / DGX Mode

For companies with stronger hardware such as a GPU workstation, DGX Spark, or enterprise AI server.

Example use cases:

- Large document RAG
- Multiple departments
- SOC investigation assistant
- Log summarization
- Internal knowledge AI
- Multi-user access

Recommended stack:

- GPU server / DGX-class device
- vLLM / NVIDIA NIM / Ollama
- Qdrant / Milvus
- Postgres
- SSO / LDAP / OAuth
- VPN / Zero Trust tunnel
- Central audit logging

---

### 4. Hybrid Cloud Gateway Mode

For companies that want cloud-like access without exposing private data directly to the cloud.

Cloud layer handles:

- Authentication
- Access gateway
- API gateway
- Rate limits
- Audit forwarding
- Admin dashboard
- Secure tunnel coordination

Private/on-prem layer handles:

- Company documents
- Vector database
- Local LLM inference
- Embeddings
- Logs
- RAG retrieval
- Sensitive processing

High-level flow:

```text
User
  ->
Cloud Gateway / Auth / Access Control
  ->
Secure Tunnel / VPN
  ->
Private AI Server
  ->
Vector DB + Local LLM + Company Data
```

---

## Key Principle

Sensitive company data should remain inside the company's trusted environment unless explicitly configured otherwise.

This project should default to:

```text
Private by default
Dry-run before apply
Least privilege access
Role-based configuration
Audit everything
Human approval for risky actions
```

---

## Core Modes

The setup wizard should support these modes:

```text
[1] Local Developer Mode
[2] Small Company Mode
[3] GPU Server Mode
[4] DGX / Enterprise Mode
[5] Hybrid Cloud Gateway Mode
[6] Dry-Run Architecture Planning Only
```

---

## Dry-Run / Pre-Init Mode

This is one of the most important features.

Before applying anything, the project must support a safe planning mode:

```bash
./private-ai init --dry-run
```

Dry-run mode should:

- Ask all setup questions.
- Generate proposed configuration files.
- Generate architecture summary.
- Generate stakeholder checklist.
- Generate network requirements.
- Generate security checklist.
- Generate deployment plan.
- NOT start containers.
- NOT modify firewall.
- NOT expose ports.
- NOT ingest real company data.
- NOT create users.
- NOT apply VPN configs.

Output example:

```text
generated/
  dry-run/
    architecture-plan.md
    stakeholder-checklist.md
    network-requirements.md
    security-review.md
    proposed-docker-compose.yml
    proposed-rbac.yaml
    proposed-env.example
    data-source-plan.md
```

Only after review should the user run:

```bash
./private-ai apply
```

---

## Role-Based Deployment Workflow

The project should guide different stakeholders step-by-step.

### CEO / Manager

Defines business intent.

Questions:

- What is the goal of this AI system?
- Which departments will use it?
- What data types are allowed?
- What data is forbidden?
- Who approves production deployment?
- Who owns the risk?
- Should this be internal-only or remotely accessible?

Outputs:

```text
company-ai-charter.md
department-scope.md
risk-ownership.md
```

---

### Developer

Builds and tests the system.

Questions:

- Is this a local dev setup or production setup?
- What files or folders are allowed for ingestion?
- Which model runtime should be used?
- Is GPU available?
- Which UI should be enabled?
- Should code/document RAG be enabled?
- Should dev tools be read-only or action-capable?

Outputs:

```text
.env
docker-compose.yml
rag-config.yaml
developer-mode.md
```

---

### Network Engineer

Configures access.

Questions:

- Is access local-only, LAN-only, VPN-only, or hybrid cloud?
- Which ports are allowed?
- What private IP range is used?
- Is WireGuard/OpenVPN/Tailscale/Zero Trust preferred?
- Is DNS required?
- Should public internet access be blocked?
- Should outbound model downloads be allowed?

Outputs:

```text
network-plan.md
firewall-rules.md
vpn-template.conf
allowed-ports.md
```

---

### Security Engineer

Defines guardrails.

Questions:

- What roles exist?
- Which users can access which collections?
- Should audit logging be immutable?
- Should prompts and responses be logged?
- Should file names be masked?
- What actions require approval?
- Should SOC mode be read-only?
- Should prompt-injection filters be enabled?

Outputs:

```text
rbac.yaml
audit-policy.yaml
guardrails.yaml
security-review.md
```

---

### Data Engineer

Connects data sources.

Questions:

- Which data sources are allowed?
- PDF/doc folders?
- Databases?
- File servers?
- Logs?
- Ticketing systems?
- Code repositories?
- How often should ingestion run?
- Should deleted files be removed from index?

Outputs:

```text
data-sources.yaml
ingestion-plan.md
chunking-policy.yaml
metadata-policy.yaml
```

---

### AI Engineer

Configures models and retrieval.

Questions:

- Which LLM runtime?
- Which model?
- Which embedding model?
- Which vector database?
- Chunk size?
- Hybrid search enabled?
- Reranker enabled?
- Citations required?
- Should answers be blocked if confidence is low?

Outputs:

```text
model-config.yaml
retrieval-config.yaml
embedding-config.yaml
eval-plan.md
```

---

## Recommended MVP

Version 1 should stay focused.

Build this first:

```text
User
  ->
Web UI
  ->
Auth / Role Check
  ->
FastAPI Backend
  ->
RAG Pipeline
  ->
Vector DB
  ->
Local LLM
  ->
Answer with citations
```

MVP features:

- Guided setup wizard
- Dry-run mode
- Docker Compose deployment
- Local document ingestion
- Local RAG Q&A
- Role-based access config
- Audit logs
- Basic admin panel or config summary
- Sample company documents
- Sample cyber logs
- Basic cyber log summarizer
- Safe read-only mode

---

## Suggested Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Postgres

### RAG

- LangChain or LlamaIndex
- Qdrant or Chroma
- Sentence Transformers / BGE embeddings
- Local LLM through Ollama, vLLM, or NVIDIA NIM

### UI

- Streamlit for MVP
- React later for production-style UI

### Deployment

- Docker Compose for v1
- Ansible later
- Terraform later
- Kubernetes later

### Security

- RBAC through YAML config
- JWT/session auth for MVP
- OAuth/LDAP/SSO later
- Audit logs in Postgres
- Optional immutable log export

### Networking

- Localhost mode
- LAN mode
- VPN template mode
- Hybrid cloud gateway mode later

---

## Repository Structure

```text
private-ai-infra-blueprint/
|-- README.md
|-- docs/
|   |-- vision.md
|   |-- architecture.md
|   |-- deployment-modes.md
|   |-- threat-model.md
|   |-- dry-run-mode.md
|   |-- stakeholder-workflow.md
|   `-- security-principles.md
|
|-- wizard/
|   |-- cli.py
|   |-- questions/
|   |   |-- manager.yaml
|   |   |-- developer.yaml
|   |   |-- network.yaml
|   |   |-- security.yaml
|   |   |-- data.yaml
|   |   `-- ai.yaml
|   `-- generators/
|       |-- env_generator.py
|       |-- compose_generator.py
|       |-- rbac_generator.py
|       |-- network_generator.py
|       `-- report_generator.py
|
|-- app/
|   |-- backend/
|   |   |-- main.py
|   |   |-- auth/
|   |   |-- rag/
|   |   |-- audit/
|   |   |-- ingestion/
|   |   `-- cyber/
|   `-- ui/
|       `-- streamlit_app.py
|
|-- configs/
|   |-- examples/
|   |   |-- local-dev.env.example
|   |   |-- small-company.env.example
|   |   |-- gpu-server.env.example
|   |   |-- rbac.example.yaml
|   |   |-- rag-config.example.yaml
|   |   `-- audit-policy.example.yaml
|
|-- deployment/
|   |-- docker-compose.yml
|   |-- docker-compose.dev.yml
|   |-- nginx/
|   |-- wireguard/
|   `-- scripts/
|
|-- examples/
|   |-- sample-company-docs/
|   |-- sample-cyber-logs/
|   `-- sample-codebase-docs/
|
|-- generated/
|   `-- .gitkeep
|
|-- tests/
|   |-- test_wizard.py
|   |-- test_rbac.py
|   |-- test_ingestion.py
|   |-- test_audit.py
|   `-- test_dry_run.py
|
|-- Makefile
|-- pyproject.toml
|-- .env.example
`-- LICENSE
```

---

## CLI Design

The project should expose a simple CLI:

```bash
private-ai init
private-ai init --dry-run
private-ai apply
private-ai validate
private-ai ingest
private-ai chat
private-ai audit
private-ai doctor
```

### Commands

#### `private-ai init`

Starts guided setup.

#### `private-ai init --dry-run`

Runs setup wizard and generates files without applying anything.

#### `private-ai apply`

Applies generated configuration.

#### `private-ai validate`

Checks config safety before deployment.

#### `private-ai ingest`

Ingests approved documents into the vector database.

#### `private-ai chat`

Starts local CLI chat for testing.

#### `private-ai audit`

Shows recent audit logs.

#### `private-ai doctor`

Checks system readiness.

---

## Safety Rules

The system must refuse or block unsafe deployment actions by default.

Examples:

- Do not expose LLM directly to the internet.
- Do not ingest folders outside approved paths.
- Do not allow admin role to be assigned accidentally.
- Do not allow production mode without audit logging.
- Do not allow cyber mode to execute remediation actions in v1.
- Do not allow config apply without validation.
- Do not store secrets in Git.
- Do not enable remote access without network review.

---

## RBAC Example

```yaml
roles:
  manager:
    can_chat: true
    can_ingest: false
    can_view_audit: false
    collections:
      - policies
      - reports

  developer:
    can_chat: true
    can_ingest: true
    can_view_audit: false
    collections:
      - docs
      - codebase

  security_analyst:
    can_chat: true
    can_ingest: false
    can_view_audit: true
    collections:
      - security_logs
      - incident_reports

  admin:
    can_chat: true
    can_ingest: true
    can_view_audit: true
    can_manage_users: true
    collections:
      - "*"
```

---

## Audit Log Example

Every user action should create an audit entry.

```json
{
  "timestamp": "2026-06-26T10:30:00Z",
  "user": "developer@example.com",
  "role": "developer",
  "action": "rag_query",
  "collection": "codebase",
  "query_hash": "sha256:...",
  "sources_used": ["api_docs.pdf", "readme.md"],
  "model": "local-llm",
  "status": "success"
}
```

---

## RAG Guardrails

The assistant should:

- Answer only from approved sources when source-grounded mode is enabled.
- Provide citations.
- Say when it does not know.
- Refuse to expose secrets.
- Refuse to summarize files the user is not allowed to access.
- Detect prompt injection in retrieved documents.
- Keep system instructions separate from retrieved text.
- Log all retrieval actions.

---

## Cyber Analyst Mode

Cyber mode should start as read-only.

Allowed v1 functions:

- Summarize logs.
- Explain suspicious events.
- Group similar alerts.
- Suggest investigation steps.
- Map events to MITRE ATT&CK style categories.
- Generate human-readable incident notes.

Blocked v1 functions:

- No automatic firewall changes.
- No automatic account disabling.
- No automatic deletion.
- No autonomous remediation.
- No direct shell execution.
- No malware execution or unsafe analysis.

Example flow:

```text
Security Logs
  ->
Parser
  ->
Normalizer
  ->
Rule + RAG Context
  ->
Cyber Analyst Assistant
  ->
Human Review
```

---

## Developer Assistant Mode

This mode is for a developer without DGX hardware who has access to company files or code documentation.

Use cases:

- Ask questions about internal codebase docs.
- Search architecture documents.
- Summarize pull request notes.
- Find API usage examples.
- Generate implementation plans from approved docs.
- Create task checklists.

Important restrictions:

- Read-only by default.
- No code modification in v1 unless explicitly enabled.
- No secrets ingestion.
- No `.env`, private keys, tokens, SSH keys, or credentials.
- No pushing to Git automatically.
- No production deployment actions.

---

## Configuration Lifecycle

The project should follow this lifecycle:

```text
Plan
  ->
Dry Run
  ->
Review
  ->
Validate
  ->
Apply
  ->
Test
  ->
Ingest
  ->
Operate
  ->
Audit
```

No production deployment should happen directly from first init.

---

## Example First Run

```bash
git clone https://github.com/yourname/private-ai-infra-blueprint.git
cd private-ai-infra-blueprint

python -m venv .venv
source .venv/bin/activate
pip install -e .

private-ai init --dry-run
private-ai validate
private-ai apply
docker compose up -d
private-ai ingest ./examples/sample-company-docs
private-ai chat
```

---

## Project Roadmap

### Phase 0 - Documentation Blueprint

- README
- Architecture diagrams
- Threat model
- Stakeholder flow
- Security principles
- Deployment modes

### Phase 1 - CLI Wizard

- Ask setup questions
- Generate configs
- Support dry-run
- Generate reports

### Phase 2 - Local RAG MVP

- Document ingestion
- Vector DB
- Local LLM
- Chat UI
- Citations

### Phase 3 - Security Layer

- RBAC
- Audit logs
- Guardrails
- Approved data paths
- Validation command

### Phase 4 - Developer Mode

- Code/document RAG
- Dev task assistant
- Read-only codebase search
- Implementation planning

### Phase 5 - Cyber Analyst Mode

- Sample log ingestion
- Alert summarization
- Incident explanation
- Human review workflow

### Phase 6 - Network Templates

- VPN templates
- Firewall checklist
- Nginx reverse proxy
- Hybrid cloud gateway design

### Phase 7 - Enterprise Extensions

- SSO
- LDAP/Active Directory
- Kubernetes
- Terraform
- SIEM connectors
- Model runtime plugins
- Compliance templates

---

## What This Project Is Not

This project is not:

- A replacement for security engineers.
- A fully autonomous SOC tool.
- A guarantee of compliance.
- A public SaaS product by default.
- A tool for bypassing company policies.
- A system that should ingest secrets or sensitive data without approval.

---

## Design Philosophy

1. Architecture first.
2. Secure by default.
3. Dry-run before apply.
4. Local/private processing where possible.
5. Role-based deployment.
6. Human approval for risky actions.
7. Modular, not locked to one AI provider.
8. Useful without DGX hardware.
9. Scalable to DGX or enterprise servers later.
10. Documentation is part of the product.

---

## Success Criteria for MVP

The MVP is successful when a user can:

- Run a dry-run setup wizard.
- Generate a deployment plan.
- Review generated configs.
- Start a local Docker Compose RAG system.
- Ingest sample docs.
- Ask questions and receive cited answers.
- See audit logs.
- Configure basic roles.
- Run in developer mode without GPU/DGX.
- Summarize sample cyber logs safely.

---

## License

Recommended license: Apache 2.0 or MIT.

Apache 2.0 is recommended if this project may later become serious enterprise infrastructure because it includes explicit patent protection.

---

## Final Positioning

This project should be presented as:

> A guided open-source blueprint for deploying private AI infrastructure across local developer machines, small companies, GPU servers, and DGX-class enterprise environments, with RAG, developer assistant, cyber analyst support, dry-run planning, RBAC, audit logging, and secure networking templates.

