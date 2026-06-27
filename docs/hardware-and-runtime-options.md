# Hardware And Runtime Options

The project should support a range of environments. A developer laptop, a small company server, a GPU workstation, DGX Spark, and a larger enterprise AI server should all follow the same planning and safety model, even when runtime choices differ.

This document avoids hardcoding exact hardware specifications. Model sizes, memory needs, and vendor runtimes change quickly, so implementation should validate the actual machine during `private-ai doctor` and `private-ai validate`.

## Hardware Tiers

| Tier | Example environment | Best first use |
| --- | --- | --- |
| CPU-only local | Developer laptop or small VM | Dry-run, config generation, small document tests |
| Small GPU | Workstation or small company server | Local RAG with modest models |
| GPU server | Dedicated internal server | Multi-user RAG and larger document sets |
| DGX Spark | Compact ARM64 AI system | Local development, pilots, and reviewed shared services |
| DGX-class systems | Purpose-built AI infrastructure | Larger managed AI workloads |
| Hybrid private plus cloud gateway | Private server plus remote access gateway | Remote access with explicit cloud transit policy |

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

## DGX Spark Compatibility

DGX Spark is not a larger version of a normal x86 workstation. Its target
profile must validate:

- ARM64 container and package availability
- NVIDIA driver, container runtime, and runtime version
- Models and profiles verified for the selected NIM or vLLM version
- Model download and storage requirements
- Unified-memory and concurrency assumptions
- Network interface and private ingress configuration

A configuration is not verified merely because a container name exists.
Target-specific smoke, inference, load, failure, and recovery tests are
required.

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

The current `private-ai doctor` command checks basic operating-system, Git,
Docker, Ollama, and NVIDIA readiness. Future target-aware checks should also
inspect:

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
- CPU architecture and container image architecture
- Target runtime and model compatibility

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

A single device should not be described as highly available. Production sizing
must also consider redundancy, maintenance, failure recovery, queue depth,
request admission control, and acceptable degradation.

## Hybrid Capacity Rule

Cloud WAF and rate limiting reduce public exposure, but they do not protect the
private model from every expensive authenticated request. The on-premises
ingress must enforce token budgets, concurrency limits, queue limits, timeouts,
and circuit breakers.

## Optional Memory Optimization

The guided architect may later detect supported vector-index and KV-cache
optimizations. It must prefer database-native and runtime-native capabilities
over project-specific implementations.

As of the recorded design snapshot:

- Qdrant 1.18 documents TurboQuant vector indexing.
- vLLM Metal documents TurboQuant KV-cache compression for Apple Silicon.
- NVIDIA NIM documents KV-cache reuse and supported host-memory offload.

One target's support does not imply another target is compatible. Retrieval,
answer quality, long-context behavior, memory use, and rollback must be tested
before enabling lossy compression. See
[Knowledge Workspace And Memory Optimization](knowledge-workspace-and-memory-optimization.md).

## Primary Hardware References

- [NVIDIA DGX Spark User Guide](https://docs.nvidia.com/dgx/dgx-spark/index.html)
- [DGX Spark system overview](https://docs.nvidia.com/dgx/dgx-spark/system-overview.html)
- [NVIDIA NIM certified support matrix](https://docs.nvidia.com/nim/large-language-models/latest/deploy-on-dgx-spark.html)
- [DGX Spark NGC guidance](https://docs.nvidia.com/dgx/dgx-spark/ngc.html)
