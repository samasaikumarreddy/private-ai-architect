# Deployment Modes

The setup wizard should guide the user into one of six modes. Each mode changes defaults, questions, generated files, validation strictness, and deployment expectations.

## Mode Summary

| Mode | Best for | Default exposure | Hardware |
| --- | --- | --- | --- |
| Local Developer | Developer proof of concept | Localhost only | Laptop or workstation |
| Small Company | Internal document assistant | LAN or VPN | CPU or small GPU server |
| GPU Server | Multi-user private AI | LAN or VPN | Dedicated GPU server |
| DGX / Enterprise | Large private AI workloads | Enterprise network | DGX-class or enterprise AI server |
| Hybrid Cloud Gateway | Remote access with private processing | Gateway plus tunnel | Private server plus cloud gateway |
| Dry-Run Planning Only | Review before build | None | No runtime required |

## Local Developer Mode

Use this when a developer has approved access to company files and wants to test a private assistant locally.

Default assumptions:

- Localhost-only access
- Docker Compose
- Local folders as data sources
- Ollama or small vLLM model
- Chroma or Qdrant
- Streamlit UI
- Read-only developer assistant
- No production data unless explicitly approved

Required outputs:

- `.env`
- `docker-compose.yml`
- `rag-config.yaml`
- `developer-mode.md`
- `data-source-plan.md`

Validation must block:

- Ingesting home directories without explicit approved subpaths
- Ingesting `.env`, keys, tokens, or credentials
- Binding services to `0.0.0.0` without network review
- Enabling code modification actions in v1

## Small Company Mode

Use this for an internal assistant over company documents such as HR policies, invoices, SOPs, or IT support notes.

Default assumptions:

- LAN-only or VPN-only access
- Local auth
- Role-based document collections
- Audit logging required
- Docker Compose deployment
- Optional small GPU

Required outputs:

- `company-ai-charter.md`
- `network-plan.md`
- `rbac.yaml`
- `audit-policy.yaml`
- `data-sources.yaml`
- `deployment-plan.md`

Validation must block:

- Production mode without audit logs
- Remote access without network owner approval
- Admin role assignment without explicit confirmation
- Shared accounts for sensitive collections

## GPU Server Mode

Use this when the company has a stronger GPU workstation or server and expects multiple users or larger document sets.

Default assumptions:

- Centralized API backend
- Qdrant, Milvus, or another managed vector database
- Postgres audit store
- vLLM, NVIDIA NIM, or Ollama depending on hardware
- Department-level collections
- VPN or Zero Trust access

Required outputs:

- `gpu-server-plan.md`
- `model-config.yaml`
- `retrieval-config.yaml`
- `resource-sizing.md`
- `network-plan.md`
- `security-review.md`

Validation must check:

- GPU availability and runtime compatibility
- Model memory requirements
- Collection-level RBAC
- Audit retention policy
- Backup and recovery expectations

## DGX / Enterprise Mode

Use this for enterprise AI infrastructure with stronger hardware, formal security review, and multiple departments.

Default assumptions:

- SSO, LDAP, OAuth, or Active Directory integration
- Central audit logging
- Network segmentation
- Separate admin and runtime access
- Change approval before apply
- SIEM forwarding where required

Required outputs:

- `enterprise-architecture.md`
- `sso-plan.md`
- `network-segmentation.md`
- `threat-model.md`
- `audit-forwarding.md`
- `runbook.md`

Validation must block:

- Local-only authentication in production enterprise mode unless approved
- Missing owner for risk, data, or operations
- Remote access without segmented network design
- Shared model runtime without resource controls

## Hybrid Cloud Gateway Mode

Use this when users need remote access but the company wants data and inference to remain private.

Cloud layer may handle:

- Authentication
- Gateway routing
- Rate limits
- Admin dashboard shell
- Audit forwarding
- Secure tunnel coordination

Private layer must handle:

- Company documents
- Embeddings
- Vector database
- Local LLM inference
- RAG retrieval
- Sensitive logs
- Prompt and response handling

Validation must block:

- Uploading private documents to the gateway by default
- Storing embeddings in the gateway by default
- Exposing the private model runtime directly
- Tunnel configuration without named network owner

## Dry-Run Planning Only

Use this when stakeholders want to understand the deployment before any runtime exists.

Default assumptions:

- No containers start
- No firewall changes occur
- No users are created
- No data is ingested
- No ports are exposed
- Generated files are clearly marked proposed

Required outputs:

- `architecture-plan.md`
- `stakeholder-checklist.md`
- `network-requirements.md`
- `security-review.md`
- `proposed-docker-compose.yml`
- `proposed-rbac.yaml`
- `proposed-env.example`
- `data-source-plan.md`

