# Beginner's Guide

This guide explains Private AI Architect without assuming that
you already understand AI infrastructure, migration, RAG, vector databases, or
GPU servers.

> **Project status:** Dry-run planning, validation, machine checks, document
> indexing, cited local answers, and bounded source-code retrieval are
> released through v0.2.1. The v0.3 development branch adds a guided
> questionnaire, normalized blueprint, and review documents. Hardware
> deployment, cloud discovery, and migration automation remain planned.

## The Project In One Minute

Companies and developers often want AI to answer questions about private files,
code, policies, or logs. Sending those files to an unknown external service may
create privacy and security risks.

This project is building a guided architect that makes the path safer:

1. Choose which files AI is allowed to use.
2. Keep those files and their search index in a trusted environment.
3. Check the user's permission before searching.
4. Find the most relevant information.
5. Ask a locally hosted AI model to answer from that information.
6. Show citations so the answer can be verified.
7. Record important actions in an audit log.
8. For migrations, verify the target and preserve a rollback path before
   production traffic changes.

The current release provides the first working local RAG loop: retrieve
approved local context, optionally ask an installed local model to answer,
validate citations, and refuse unsupported questions. Private hardware and
cloud migration workflows come later.

## Three Ways To Use The Project

```mermaid
flowchart TD
    START["What do you want to do?"]
    START --> LOCAL["Build local RAG"]
    START --> HARDWARE["Configure private GPU hardware"]
    START --> MIGRATE["Migrate from cloud AI"]

    LOCAL --> RTX["CPU, RTX, or approved remote GPU"]
    HARDWARE --> TARGET["DGX Spark or generic GPU server"]
    MIGRATE --> CLOUD["Selected Azure OpenAI or AWS Bedrock workload"]

    RTX --> PLAN["Blueprint, generated artifacts and validation"]
    TARGET --> PLAN
    CLOUD --> PLAN
```

The future questionnaire will branch immediately. A local developer should not
see Azure network questions, while a cloud migration should require source,
identity, compatibility, verification, and rollback decisions.

## What The Important Words Mean

| Term | Simple meaning |
| --- | --- |
| Private AI | AI that runs within an environment you trust and control. |
| LLM | The language model that reads context and writes an answer. |
| RAG | A process that finds relevant private information before asking an LLM to answer. |
| Ingestion | Reading approved files and preparing them for search. |
| Chunk | A small section of a document that can be searched independently. |
| Embedding | A numerical representation used to find text with similar meaning. |
| Vector database | A database designed to store and search embeddings. |
| RBAC | Role-based access control: rules that decide who may access each collection. |
| Audit log | A history of important actions, such as ingestion, searches, and admin changes. |
| Dry run | Generate and inspect a plan without deploying or changing infrastructure. |
| Blueprint | The versioned source of truth containing intent, configuration, unresolved decisions, and owners. |
| Discovery | Read an explicitly approved provider scope without changing it. |
| Cutover | Move controlled production traffic from the old system to the verified target. |

## What Works Today

The current command-line tool provides a safe local preview:

```mermaid
flowchart LR
    U["User"] --> CLI["private-ai CLI"]
    CLI --> PLAN["Generate a dry-run plan"]
    CLI --> CHECK["Check machine readiness"]
    CLI --> INDEX["Index approved local files"]
    PLAN --> VALIDATE["Validate configuration safety"]
    INDEX --> SEARCH["Search document chunks"]
    SEARCH --> EVIDENCE{"Evidence found?"}
    EVIDENCE -->|No| REFUSE["Refuse without calling a model"]
    EVIDENCE -->|Yes, no model| RESULT["Return cited excerpts"]
    EVIDENCE -->|Yes, --model| MODEL["Local Ollama"]
    MODEL --> CITATIONS{"Citations valid?"}
    CITATIONS -->|Yes| ANSWER["Return grounded answer"]
    CITATIONS -->|No| RESULT
```

It can:

- Generate a reviewable deployment plan without applying changes.
- Validate generated files for common unsafe settings.
- Report whether Python, Git, Docker, NVIDIA tools, and Ollama are available.
- Index approved Markdown, text, log, YAML, and JSON files.
- Skip likely secret, credential, key, token, and `.env` files.
- Find relevant excerpts and show where they came from.
- Optionally ask an already-installed local Ollama model to answer from the
  retrieved context.
- Refuse unsupported questions before invoking the model.
- Reject missing or unknown model citations and return cited retrieval results
  instead.

By default, `private-ai chat` returns retrieval-only cited excerpts and does not
invoke a model. If the user explicitly passes `--model` with an
already-installed local Ollama model, the command can generate an answer using
retrieved context.

## Working v0.2 And The Full Planned Runtime

v0.2 proves the local retrieval, model, citation, fallback, and refusal path
with a lexical JSON index. This is the fuller runtime architecture the project
is working toward:

```mermaid
flowchart TD
    OWNER["Data owner approves a source"] --> FILTER["File and secret safety checks"]
    FILTER --> CHUNK["Split documents into chunks"]
    CHUNK --> EMBED["Create local embeddings"]
    EMBED --> DB[("Private vector database")]

    USER["User asks a question"] --> AUTH["Authentication and RBAC check"]
    AUTH --> RETRIEVE["Retrieve only permitted chunks"]
    DB --> RETRIEVE
    RETRIEVE --> MODEL["Local LLM runtime"]
    MODEL --> ANSWER["Answer with source citations"]

    AUTH --> AUDIT[("Audit log")]
    RETRIEVE --> AUDIT
    MODEL --> AUDIT
```

The central rule is simple: a model must receive only information that the
current user is allowed to access.

The v0.2 RAG runtime is the first working reference, not the entire product.
Authentication, runtime RBAC, semantic vector retrieval, audit storage, and
production deployment remain future work. Once those local foundations are
reliable, the blueprint and validation engine can expand to private hardware
and migration configurations.

## Where The System Runs

The same design can support several sizes of deployment:

```mermaid
flowchart LR
    CODE["One guided architect and blueprint model"]
    CODE --> LAPTOP["Developer laptop"]
    CODE --> COMPANY["Small company server"]
    CODE --> GPU["GPU workstation or server"]
    CODE --> DGX["DGX Spark or DGX-class system"]
    CODE --> HYBRID["Private server with secure remote gateway"]
```

| Deployment | Intended use |
| --- | --- |
| Developer laptop | Learning, prototyping, and searching a small approved folder. |
| Small company server | A shared internal assistant for a small team. |
| GPU workstation/server | Faster models and more concurrent users. |
| DGX-class system | Larger models, higher throughput, and enterprise workloads. |
| Hybrid gateway | Cloud-integrated remote access with explicit data-transit rules. |

Expensive hardware is not required to start. A normal computer can run the
dry-run, retrieval-only chat, and a sufficiently small local model. Model speed
and model size determine when a GPU becomes useful.

## Security Boundaries

Private AI is not secure merely because it runs locally. Permissions, network
controls, secret filtering, and auditing are still required.

```mermaid
flowchart LR
    INTERNET["Public or remote network"]
    GATEWAY["Authenticated gateway"]

    subgraph TRUSTED["Trusted private environment"]
        APP["Private AI application"]
        POLICY["RBAC policies"]
        DATA[("Approved company data")]
        VECTOR[("Vector database")]
        LLM["Local model runtime"]
        LOG[("Audit store")]
    end

    INTERNET -. "Optional controlled access" .-> GATEWAY
    GATEWAY --> APP
    POLICY --> APP
    APP --> DATA
    APP --> VECTOR
    APP --> LLM
    APP --> LOG
```

The model runtime and databases should not be exposed directly to the public
internet. Remote access should pass through an authenticated gateway.

When a managed cloud gateway proxies requests, prompts and responses transit
the cloud even if documents, embeddings, models, and storage stay on-premises.
The project must show storage, processing, transit, logging, and telemetry
locations separately.

## Try The Current Version

### 1. Install

You need Python 3.11 or newer.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### 2. Check Your Computer

```bash
private-ai doctor
```

A warning about Ollama is expected if it is not installed. Ollama is not needed
for dry-run planning or retrieval-only search. It is needed only when the user
explicitly passes `--model` for a local generated answer.

### 3. Generate A Safe Plan

```bash
private-ai init --dry-run --mode local-developer --project-name my-private-ai --output-dir generated/dry-run --force
private-ai validate generated/dry-run
```

This creates documentation and example configuration under
`generated/dry-run/`. It does not start containers, change firewall rules,
connect to company systems, or deploy a model.

### 4. Index The Included Sample Documents

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
```

Only use the included sample files or other data you are authorized to process.
Never test with real credentials or confidential company data.

### 5. Search Without A Model

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json
```

This default command returns relevant excerpts and their source paths. It does
not invoke a model.

### 6. Optionally Generate A Local Answer

Install Ollama separately. Confirm which models are already installed:

```bash
ollama list
```

For the documented small-model example, the operator can explicitly run:

```bash
ollama pull llama3.2:1b
```

`private-ai` never downloads a model automatically. After the model is
installed, request a local answer:

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json --model llama3.2:1b
```

The command sends retrieved context only to the loopback Ollama API. A valid
answer includes numbered citations and a matching `Sources` section. If Ollama
is unavailable or citations are invalid, the command safely returns
retrieval-only excerpts.

### 7. Verify Unsupported-Question Refusal

```bash
private-ai chat "What minerals are present on the moon?" --index generated/index/index.json --model llama3.2:1b
```

Because the approved sample documents do not support that question, the
command refuses before invoking Ollama.

## Current And Future Capabilities

| Capability | Status |
| --- | --- |
| Dry-run architecture and configuration generation | Working |
| Generated configuration validation | Working |
| Local environment checks | Working |
| Local file indexing with denied-file rules | Working |
| Retrieval with source citations | Working |
| Three-journey branching questionnaire foundation | Working in v0.3 development |
| Normalized versioned blueprint and review documents | Working in v0.3 development |
| Optional local Ollama-generated answers | Working in v0.2 |
| Unsupported-question refusal before model invocation | Working in v0.2 |
| Invalid or missing model-citation fallback | Working in v0.2 |
| BM25 ranking and retrieval evaluation | Working in released v0.2.1 |
| Bounded source-code ingestion | Working in released v0.2.1 |
| Semantic embedding and vector database | Planned |
| Web chat and administration interface | Planned |
| Login, SSO, and production RBAC enforcement | Planned |
| Production audit database | Planned |
| Docker deployment | Planned |
| Tested DGX deployment profile | Planned |
| Narrow Azure OpenAI discovery | Planned after hardware profiles |
| Production shadowing, canary, and rollback | Later milestone |

## What We Will Build Next

The basic local RAG loop now works. The next local priorities are:

1. Expand retrieval and grounding evaluation.
2. Add local embeddings and a vector database.
3. Add natural-language entailment checks for grounded claims.
4. Add runtime authentication, RBAC, and audit storage.
5. Package a later service stack only after its safety contract is tested.

After that foundation is reliable, the project can add a web interface,
authentication, stronger RBAC, richer blueprint approval workflows, GPU
server profiles, tested DGX Spark deployment guidance, narrow cloud discovery,
and staged migration tooling.

An optional later extension may combine normal RAG with a reviewed Markdown
wiki that accumulates linked knowledge over time. The project may also detect
supported vector or model-memory compression, but only after quality
benchmarks. See
[Knowledge Workspace And Memory Optimization](knowledge-workspace-and-memory-optimization.md).

## Frequently Asked Questions

### Does this send my files to an external AI service?

The current ingestion and retrieval commands operate locally. Optional v0.2
generation accepts only a loopback Ollama URL and rejects known Ollama cloud
model names. `private-ai` does not upload files or download models. Future
cloud-relayed gateways may carry prompts and responses through cloud
infrastructure, so transit and logging must be explicit rather than described
as fully on-premises.

### Is it production-ready?

No. It is an early implementation with working planning, retrieval, and
optional local model answers. It does not yet provide production
authentication, RBAC, semantic retrieval, audit storage, or deployment
automation. Do not use it as a production security boundary.

### Do I need a DGX system?

No. Start on a developer machine. DGX-class hardware is relevant when model
size, speed, or the number of users requires substantially more GPU capacity.

### Can I use real company documents?

Only after the data owner and security team approve the source and deployment.
Use synthetic sample data while evaluating the current early release.

### Why are citations important?

An AI answer can sound confident and still be wrong. Citations let users inspect
the exact source material and decide whether the answer is trustworthy.

### Why start with a dry run?

AI infrastructure touches private data, networks, models, and access controls.
A dry run gives developers, security teams, and data owners something concrete
to review before any infrastructure is changed.

### Can it certify HIPAA, GDPR, or another framework?

No. Framework selections can activate questions, checks, and evidence
requirements. Authorized legal, privacy, security, and compliance reviewers
must determine applicability and compliance.

## Where To Read Next

- [CLI Reference](cli-reference.md) for every available command.
- [Guided Architect Workflow](guided-architect-workflow.md) for the three user journeys.
- [Architecture](architecture.md) for engineering-level component details.
- [Security Principles](security-principles.md) for mandatory safety rules.
- [Deployment Modes](deployment-modes.md) for environment choices.
- [Roadmap](roadmap.md) for planned implementation stages.
