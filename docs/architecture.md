# Architecture

The architecture separates planning, configuration generation, application runtime, data ingestion, model inference, and audit evidence. The safest deployment path is to keep company data, vector indexes, prompts, responses, and logs inside a trusted local or on-premises environment.

## High-Level Components

```text
User
  -> Web UI or CLI
  -> API backend
  -> Auth and RBAC
  -> RAG service
  -> Retrieval layer
  -> Vector database
  -> Local model runtime
  -> Audit log
```

## Component Responsibilities

| Component | Responsibility |
| --- | --- |
| Setup wizard | Ask role-specific questions and produce configuration artifacts. |
| Config generator | Render `.env`, Docker Compose, RBAC, data-source, network, and policy files. |
| Validator | Check for unsafe or incomplete configuration before apply. |
| Web UI | Provide chat, admin summary, ingestion status, and audit views. |
| API backend | Enforce auth, roles, retrieval permissions, and audit logging. |
| RAG pipeline | Chunk, embed, retrieve, rerank, ground, and cite approved sources. |
| Vector database | Store embeddings and metadata for approved document collections. |
| Model runtime | Run local LLM inference through Ollama, vLLM, NVIDIA NIM, or another approved runtime. |
| Audit store | Record setup, ingestion, retrieval, chat, admin, and validation events. |

## Trust Boundaries

The main trust boundaries are:

- User device to private AI application
- Application to data-source connectors
- Application to vector database
- Application to model runtime
- Private environment to optional cloud gateway
- Admin/configuration plane to runtime plane

Each boundary should have an explicit access rule, log event, and owner.

## MVP Runtime Architecture

```text
Browser or CLI
  -> FastAPI backend
  -> Session/JWT auth
  -> YAML RBAC policy
  -> RAG orchestration
  -> Qdrant or Chroma
  -> Ollama or vLLM
  -> Postgres audit log
```

MVP deployment should use Docker Compose so a local developer or small company can run the system without Kubernetes.

## Hybrid Gateway Architecture

Hybrid mode keeps sensitive processing on the private side. The cloud side should only coordinate access.

```text
Remote user
  -> Cloud gateway
  -> Auth, rate limits, admin shell, audit forwarding
  -> Secure tunnel or VPN
  -> Private AI server
  -> Vector DB, local LLM, company data, audit store
```

The gateway must not become the system of record for private documents, embeddings, prompts, or responses unless the company explicitly approves that design.

## Data Flow

1. A data owner approves a folder, repository, database, or log source.
2. The ingestion job scans only approved paths.
3. Files are filtered for denied extensions, secrets, and unsupported content.
4. Documents are chunked and tagged with metadata.
5. Embeddings are generated inside the trusted environment.
6. Vectors and metadata are stored in the vector database.
7. A user query is checked against RBAC.
8. Retrieval only searches collections allowed for that role.
9. The answer is generated from retrieved context.
10. Citations and audit events are returned.

## Audit Flow

Every sensitive operation should write an audit event:

- Setup wizard answers
- Config generation
- Validation results
- Apply attempts
- Login and logout
- Ingestion start, finish, failure, and skipped files
- Retrieval query hash
- Collections searched
- Model used
- Admin changes
- Remote access changes

Audit records should avoid storing raw secrets. Query text may need hashing or redaction depending on company policy.

## Recommended Technology Defaults

| Area | MVP default | Later options |
| --- | --- | --- |
| Backend | FastAPI | Service mesh, background workers |
| UI | Streamlit | React |
| Vector DB | Qdrant or Chroma | Milvus, pgvector |
| Local LLM | Ollama | vLLM, NVIDIA NIM |
| Embeddings | Sentence Transformers or BGE | Enterprise embedding service |
| Audit | Postgres | Immutable export, SIEM forwarding |
| Deployment | Docker Compose | Ansible, Kubernetes, Terraform |
| Auth | Local session/JWT | OAuth, SSO, LDAP, Active Directory |

## Architecture Rules

- The LLM runtime must not be exposed directly to the public internet.
- Retrieval must enforce role and collection permissions before context is passed to the model.
- The application must not ingest denied paths or secret files.
- Production mode must require audit logging.
- Remote access must require network review.
- Cyber analyst mode must remain read-only in v1.
- Dry-run mode must not mutate infrastructure or ingest real company data.

