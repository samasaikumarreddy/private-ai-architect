# Hardware And Runtime Options

The project should support a range of environments. A developer laptop, a small company server, a GPU workstation, DGX Spark, and a larger enterprise AI server should all follow the same planning and safety model, even when runtime choices differ.

This document avoids hardcoding exact hardware specifications. Model sizes, memory needs, and vendor runtimes change quickly, so implementation should validate the actual machine during `private-ai doctor` and `private-ai validate`.

## Hardware Tiers

| Tier | Example environment | Best first use |
| --- | --- | --- |
| CPU-only local | Developer laptop or small VM | Dry-run, config generation, small document tests |
| Small GPU | Workstation or small company server | Local RAG with modest models |
| GPU server | Dedicated internal server | Multi-user RAG and larger document sets |
| DGX Spark / DGX-class | Purpose-built AI hardware | Stronger local inference and enterprise pilots |
| Hybrid private plus cloud gateway | Private server plus remote access gateway | Remote access while private data stays on-prem |

## Runtime Options

| Runtime | Good for | Notes |
| --- | --- | --- |
| Ollama | Developer mode and simple local deployment | Easy first runtime for local testing. |
| vLLM | Higher-throughput GPU serving | Better fit for GPU servers and multi-user use. |
| NVIDIA NIM | NVIDIA-focused enterprise deployments | Useful where NVIDIA runtime support is part of the platform decision. |
| External enterprise runtime | Existing approved company model platform | Must preserve data, audit, and access-control boundaries. |

## Vector Database Options

| Vector DB | Good for | Notes |
| --- | --- | --- |
| Chroma | Local developer mode | Simple local setup. |
| Qdrant | Local to small company production path | Strong default candidate for MVP. |
| Milvus | Larger deployments | Consider later for heavier enterprise use. |
| pgvector | Postgres-centered teams | Useful when teams already operate Postgres deeply. |

## Recommended Defaults By Mode

| Mode | Runtime default | Vector default | Deployment default |
| --- | --- | --- | --- |
| Local Developer | Ollama | Chroma or Qdrant | Docker Compose, localhost |
| Small Company | Ollama or vLLM | Qdrant | Docker Compose, LAN or VPN |
| GPU Server | vLLM or NVIDIA NIM | Qdrant or Milvus | Docker Compose first, orchestration later |
| DGX / Enterprise | vLLM or NVIDIA NIM | Qdrant, Milvus, or approved enterprise DB | Enterprise network, SSO later |
| Hybrid Gateway | Private runtime only | Private vector DB only | Gateway plus tunnel |

## Design Rule

Hardware should improve capacity, not change the safety model.

The same controls should apply everywhere:

- Approved data sources
- RBAC before retrieval
- Audit logging
- Prompt-injection handling
- Citations
- Dry-run before apply
- Validation before deployment
- No direct public exposure of model runtimes

## Doctor Checks

The future `private-ai doctor` command should inspect:

- Operating system
- Docker availability
- GPU availability
- GPU memory
- NVIDIA driver and container runtime availability where relevant
- CPU and RAM
- Disk space
- Open ports
- Model runtime connectivity
- Vector database connectivity
- Audit database connectivity

The command should not assume a DGX-class machine. It should report what exists and recommend a compatible mode.

## Sizing Guidance

Sizing should be generated from actual choices:

- Number of users
- Number of documents
- Average document size
- Embedding model
- LLM model
- Context window
- Expected query concurrency
- Retention policy
- Audit policy

The validator should warn when the selected model and expected workload do not fit the available machine.

