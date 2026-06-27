# Configuration Reference

The normalized blueprint is the planned source of truth for all generated
artifacts. The current v0.1 CLI emits a smaller dry-run answer model; the schema
below defines the direction for the guided architect and will be introduced
incrementally with explicit schema versions.

## Blueprint Principles

- Provider-neutral at the core
- Versioned and machine-readable
- No embedded credentials or secrets
- Unknown values represented explicitly
- Multiple governance frameworks supported
- Storage, processing, and transit modeled separately
- Proposed and applied state distinguishable
- Human ownership and approval recorded

## Proposed Blueprint Shape

```yaml
api_version: private-ai.dev/v1alpha1
kind: PrivateAIBlueprint

metadata:
  name: company-private-ai
  environment: pilot
  status: proposed

workflow:
  intent: migrate-cloud-ai
  source: azure-openai

source:
  provider: azure
  service: azure-openai
  discovery_scope:
    subscription_ids: ["redacted-reference"]
    resource_groups: ["approved-ai-group"]
    resource_types:
      - deployments
      - endpoints
  discovery_mode: read-only

target:
  type: dgx-spark
  architecture: arm64
  runtime: nvidia-nim
  model: unresolved

gateway:
  provider: azure
  pattern: cloud-relayed-data-plane
  private_connectivity: vpn
  cloud_payload_logging: false

data:
  classifications:
    - confidential
    - personal-data
  residency:
    storage: on-premises
    processing: on-premises
    cloud_transit_allowed: true
  retention_days: 90

governance:
  frameworks:
    - gdpr
  applicability: unverified
  assurance_mode: advisory
  required_reviews:
    - security
    - privacy
    - legal

migration:
  strategy: plan-only
  shadow_required: true
  rollback_required: true
  acceptance_criteria:
    quality: unresolved
    latency: unresolved
    error_rate: unresolved

ownership:
  business: unresolved
  security: unresolved
  network: unresolved
  data: unresolved
  operations: unresolved
```

The schema must not accept `compliance: hipaa` as proof of compliance.
Framework selections activate relevant questions, validation rules, and
evidence requirements. Authorized reviewers determine applicability and
compliance outside the tool.

## Optional Knowledge And Optimization Fields

Future schema versions may add:

```yaml
knowledge:
  mode: hybrid
  source_authority: immutable
  wiki:
    writes: propose-and-review
    access_derivation: source-acl-intersection
    require_chunk_citations: true
    stale_on_source_change: true

optimization:
  mode: auto
  vector_index:
    preferred_quantization: turboquant
    require_retrieval_benchmark: true
    fallback: uncompressed
  model_runtime:
    kv_cache_strategy: runtime-native
    turboquant: only-if-adapter-supported
    require_quality_benchmark: true
```

These are optional proposed fields, not current CLI inputs. `auto` selects only
verified adapter capabilities. See
[Knowledge Workspace And Memory Optimization](knowledge-workspace-and-memory-optimization.md)
for the complete security and benchmark contract.

## Workflow Values

Initial planned values:

| Value | Meaning |
| --- | --- |
| `build-local-rag` | Build a local or company-private RAG deployment. |
| `configure-private-hardware` | Integrate new DGX or GPU infrastructure. |
| `migrate-cloud-ai` | Assess and migrate a selected cloud AI workload. |

Workflow intent selects a question branch. It is separate from the target
deployment profile.

## State Values

| State | Meaning |
| --- | --- |
| `proposed` | Generated but not approved or applied. |
| `validated` | Automated checks passed; human review may remain. |
| `approved` | Required owners approved the exact blueprint revision. |
| `applied` | Approved changes were applied by an implementation that supports apply. |
| `verified` | Target tests passed against recorded acceptance criteria. |
| `retired` | Blueprint is no longer an active target. |

The current v0.1 implementation only produces proposed dry-run artifacts.

## Generated Files

Artifact packs vary by workflow and target.

| File | Purpose |
| --- | --- |
| `blueprint.yaml` | Normalized versioned intent and configuration. |
| `discovery-snapshot.json` | Redacted facts from an approved read-only provider scope. |
| `unresolved-decisions.md` | Critical questions that must not be guessed. |
| `docker-compose.yml` | Proposed local or small-company service topology. |
| `rbac.yaml` | Roles, permissions, and collection access. |
| `rag-config.yaml` | Retrieval, citation, refusal, and grounding behavior. |
| `data-sources.yaml` | Approved ingestion sources and denied paths. |
| `audit-policy.yaml` | Events, retention, redaction, and export settings. |
| `network-plan.md` | Bind addresses, ingress, DNS, VPN, gateway, and trust boundaries. |
| `security-review.md` | Risks, blockers, warnings, owners, and approvals. |
| `model-config.yaml` | Runtime, model, embeddings, architecture, and resource expectations. |
| `compatibility-report.md` | Source API, target runtime, model, and hardware compatibility. |
| `migration-plan.md` | Staged migration sequence and application changes. |
| `verification-plan.md` | Functional, quality, performance, access, and failure tests. |
| `rollback-plan.md` | Triggers, actions, owners, and recovery checks. |
| `evidence-report.md` | Controls detected, missing, unevaluated, or requiring human evidence. |

## Validation Classes

Blocking errors include:

- Public model or database exposure
- Missing required audit policy
- Missing RBAC policy for shared deployments
- Data source outside approved paths
- Secret-like files included in ingestion
- Discovery scope broader than the approved plugin contract
- Persisted cloud credentials
- Cloud transit contradicting residency policy
- Unsupported target architecture or runtime combination
- Unknown critical owner or rollback requirement before apply
- `apply` attempted against an unapproved blueprint revision
- Generated wiki access broader than any contributing source
- Compression requested without a supported adapter and required benchmark

Warnings include:

- Capacity has not been load tested
- Model mapping has not been quality evaluated
- No backup or restore test
- No audit export
- Broad wildcard collections
- Query or payload logging enabled
- Governance framework selected but applicability unverified
- Required human evidence is missing
- Derived knowledge is stale or missing source-level citations

## Configuration Lifecycle

```text
Questions and approved discovery
  -> blueprint
  -> generate
  -> validate
  -> human review
  -> approve exact revision
  -> apply
  -> verify
  -> optional migration stages
  -> evidence
```

Production configuration is a controlled artifact. Changes must be
reproducible, attributable, reviewable, and tied to a blueprint revision.

## Governance References

Framework support must be based on current primary guidance and reviewed as
that guidance changes:

- [HHS HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [HHS guidance on risk analysis](https://www.hhs.gov/hipaa/for-professionals/security/guidance/guidance-risk-analysis/index.html)
- [European Data Protection Supervisor DPIA guidance](https://www.edps.europa.eu/data-protection-impact-assessment-dpia_en)
- [SEC internal control over financial reporting guidance](https://www.sec.gov/rule-release/33-8212)
