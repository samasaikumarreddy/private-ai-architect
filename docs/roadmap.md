# Roadmap

The roadmap deliberately separates local runtime proof, guided architecture,
hardware integration, cloud discovery, and production traffic migration. These
stages should not be compressed into one release.

Version labels describe intended scope, not committed release dates.

## v0.1: Safe Planning Foundation

Status: implemented.

Delivered:

- Documentation and repository governance
- Python package and `private-ai` CLI
- `init --dry-run`
- Proposed review-pack generation
- `validate`, `doctor`, and `modes`
- Local file indexing with denied-file rules
- Retrieval-only cited excerpts
- Unit tests and CI

Current limitations:

- The answer model is not yet the normalized blueprint schema.
- Interactive questions are minimal.
- No model-backed answer generation exists.
- No infrastructure is applied.
- No cloud discovery or hardware verification exists.

## v0.2: Working Local RAG Reference

Goal: prove the smallest useful private-AI deployment end to end.

Status: implemented.

Delivered:

- Approved local document ingestion with denied-file rules
- Retrieval-only cited excerpts
- Optional loopback Ollama integration
- Installed-model preflight without automatic downloads
- Model-generated answers with citations
- Citation-range validation and retrieval fallback
- Refusal before model invocation when evidence is missing
- Query-focused Markdown context
- Automated grounding tests
- Documented `llama3.2:1b` RTX smoke test

Exit criteria achieved:

- A developer can clone the project and receive a cited answer from sample
  documents without cloud inference.
- Ollama access is restricted to loopback addresses.
- Denied files remain excluded.
- The flow does not require a GPU and has a documented RTX configuration.

Deferred beyond v0.2:

- Docker Compose runtime stack
- Private API and web UI
- Qdrant and semantic embeddings
- Runtime RBAC and audit storage
- Source-code-aware ingestion

## v0.2.1: Local RAG Quality

Status: development candidate.

Delivered on the development branch:

- BM25 ranking and relative relevance filtering
- Stronger meaningful-term evidence coverage
- Claim-to-cited-source lexical support checks
- Repeatable `private-ai evaluate` cases
- Bounded source-code ingestion
- Default generated, dependency, credential, and signing exclusions
- Operator-defined `--exclude` patterns
- File-count and file-size limits
- Backward compatibility with v0.2 JSON indexes

This remains a lexical implementation. Semantic vector retrieval, runtime
authorization, audit storage, and production deployment are not part of
v0.2.1.

## v0.3: Guided Architect Core

Goal: replace a flat setup wizard with a branching, versioned architecture
workflow.

Deliverables:

- Early intent selection:
  - Build local RAG
  - Configure private hardware
  - Migrate cloud AI
- Question graph with conditional branches
- Normalized blueprint schema
- Explicit unresolved decisions
- Artifact provenance and blueprint checksums
- Owner and approval model
- Framework-aware advisory evidence fields
- Promotion from proposed to validated state

Exit criteria:

- Local users do not see cloud migration questions.
- Cloud migration users receive source-specific questions.
- The same blueprint deterministically produces the same proposed artifact
  pack.
- Critical unknown answers block approval or apply.

## v0.4: Private Hardware Profiles

Goal: help a small business integrate new private GPU hardware.

Deliverables:

- Generic NVIDIA GPU server profile
- DGX Spark ARM64 profile
- Runtime and model compatibility matrix
- NVIDIA NIM and vLLM generation paths
- Capacity questionnaire
- Network, identity, monitoring, backup, and recovery artifacts
- Target verification commands

Exit criteria:

- Generic GPU and DGX Spark configurations are tested on their claimed target
  hardware.
- Unsupported architecture, container, model, and runtime combinations fail
  validation.
- Documentation distinguishes pilot, shared internal service, and
  high-availability production requirements.

Hardware access or trusted hardware maintainers are required before declaring
the DGX Spark profile verified.

## v0.5: Narrow Azure OpenAI Discovery

Goal: inspect one approved Azure OpenAI workload without promising full cloud
inventory.

Deliverables:

- Permission-manifest preflight
- Customer-controlled read-only authentication
- Allowlisted discovery of selected deployments, endpoint metadata, API
  versions, regions, quotas, and configuration
- Redacted discovery snapshot with provenance
- Source API and model compatibility assessment
- No prompt, response, document, or secret collection by default

Exit criteria:

- The plugin documents every requested permission and provider API.
- Scope cannot silently expand beyond approved resources.
- Tokens are not persisted.
- Partial permissions produce explicit unknowns instead of guessed inventory.

## v0.6: Azure-To-Private Migration Planning

Goal: generate a reviewable Azure-to-private design without changing
production traffic.

Deliverables:

- Azure source to private target mapping
- Cloud-relayed and cloud-control-plane gateway options
- VPN or private connectivity plan
- Entra identity integration plan
- Payload logging and telemetry checks
- Application compatibility checklist
- Evaluation, migration, verification, and rollback plans
- Proposed infrastructure-as-code with static validation

Exit criteria:

- Storage, processing, transit, and telemetry locations are explicit.
- Generated cloud configuration passes provider and policy validation.
- The project still performs no automatic production cutover.

## v0.7: Shadow, Canary, And Rollback

Goal: support controlled migration of production workloads only after earlier
targets are proven.

Deliverables:

- Shadow request comparison
- Source and target health checks
- Quality, latency, error-rate, and capacity thresholds
- Request admission control and backpressure
- Reviewed traffic-splitting integration
- Automatic and manual fallback criteria
- Cutover and rollback audit trail

Exit criteria:

- Target responses can be compared without serving them to users.
- Failure tests demonstrate rollback.
- Traffic changes require named operators and explicit approval.
- No generic cutover claim is made for unsupported application architectures.

## v0.8: AWS Bedrock Path

Goal: add AWS as a separate, tested provider path.

Deliverables:

- Narrow Bedrock discovery plugin
- Exact IAM permission manifest
- Source-to-target compatibility assessment
- AWS edge, identity, VPC, and private-connectivity options
- Proposed infrastructure-as-code
- Migration, verification, and rollback artifacts

AWS must not be implemented as renamed Azure templates. Provider permissions,
networking, identity, APIs, and failure modes require independent tests.

## v1.0: Reviewable Migration System

The first stable release should provide:

- A tested local RAG reference
- A versioned guided architect workflow
- At least one verified private hardware target
- At least one tested cloud migration path
- Explicit approval boundaries
- Repeatable verification and rollback
- Evidence reports that distinguish automated checks from human review

## Optional Research Track: Knowledge And Memory

This track is recorded but must not delay the local RAG, guided architect,
hardware, or migration milestones.

Possible deliverables:

- Hybrid RAG plus reviewed Markdown wiki
- Immutable raw-source and derived-knowledge boundaries
- Source/chunk provenance and access inheritance
- Review queue, contradiction detection, and freshness checks
- Read-only MCP knowledge tools
- Optional human knowledge workspace
- Qdrant TurboQuant capability detection and retrieval benchmark
- Runtime-specific KV-cache optimization adapters

Entry criteria:

- The local RAG source, chunk, citation, deletion, and RBAC contracts are stable.
- MCP retrieval is read-only by default.
- Generated wiki pages cannot broaden source access.
- Optimization adapters expose exact supported versions and rollback.

The detailed design and acceptance criteria are maintained in
[Knowledge Workspace And Memory Optimization](knowledge-workspace-and-memory-optimization.md).

## Later Extensions

- Additional model runtimes and GPU targets
- Kubernetes and enterprise orchestration
- SSO and directory integrations
- Additional cloud and API providers
- SIEM and immutable evidence export
- High-availability and disaster-recovery profiles
- Data-source connectors with permission synchronization
- Community-maintained policy and target plugins
