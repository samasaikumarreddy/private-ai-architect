# GitHub Growth Strategy

Target: build a project useful enough to earn 10,000 GitHub stars.

Stars are not the product and cannot be guaranteed. They are a signal that the
project solves a visible problem, works quickly, earns trust, and gives
contributors meaningful extension points.

## Defensible Positioning

One-line pitch:

> Open-source guided architect for local RAG, private GPU and DGX deployments,
> and staged cloud-to-private AI migration.

Expanded pitch:

> Answer relevant architecture questions, generate a versioned private-AI
> blueprint, validate security and compatibility, and produce deployment,
> verification, migration, and rollback artifacts before production changes.

The project should not compete primarily on chat UI polish. Existing local RAG
tools already provide fast chat and document workflows. The differentiator is
the combination of:

- Early workflow branching
- Dry-run architecture generation
- Provider-neutral normalized blueprint
- Security and compatibility validation
- Hardware and cloud migration profiles
- Explicit approvals and unresolved decisions
- Verification, rollback, and evidence

## Audience Segments

| Audience | Immediate problem | Project promise |
| --- | --- | --- |
| Local developer | Use approved private files with local models | A working cited RAG reference on CPU or RTX. |
| Small business | Integrate newly purchased GPU or DGX Spark hardware | Guided compatibility, network, identity, and operations planning. |
| Cloud platform team | Move a selected Azure OpenAI or Bedrock workload | Narrow discovery and staged migration artifacts. |
| Security reviewer | Understand exposure before deployment | Reviewable blueprint, data flow, controls, blockers, and evidence gaps. |
| Infrastructure architect | Avoid rebuilding every checklist and template | Extensible source, target, runtime, gateway, generator, and validator plugins. |
| Contributor | Work on a focused, testable integration | Clear plugin contracts and target-specific acceptance tests. |

## Product Signals Required For Growth

### Signal 1: Trust

- Honest implementation status
- Apache 2.0 license and security policy
- No real credentials or company data
- Clear non-goals and approval boundaries
- No unsupported compliance or production claims

### Signal 2: Ten-Minute Value

- Install without unusual infrastructure
- Run `doctor`
- Generate and validate a useful dry-run pack
- Start the local RAG reference
- Ingest synthetic sample docs
- Receive a cited answer

The local working path is required before serious promotion.

### Signal 3: Distinctive Demonstration

A strong demo should show:

1. Selecting one of the three workflows.
2. Irrelevant questions disappearing.
3. A normalized blueprint being generated.
4. A risky configuration failing validation.
5. A corrected local stack returning a cited answer.
6. A future DGX or Azure migration pack clearly marked proposed.

### Signal 4: Real Hardware Proof

The DGX Spark profile needs:

- Named tested software versions
- ARM64 compatibility evidence
- Reproducible setup and smoke tests
- Measured model and concurrency results
- Failure and recovery notes

Screenshots or generated templates alone are not hardware support.

### Signal 5: Credible Migration Proof

The first Azure path needs:

- Exact read-only permission manifest
- Narrow supported discovery scope
- Redacted snapshot
- Compatibility mapping
- Generated but unapplied gateway and target configuration
- Verification and rollback plan

Shadowing and canary traffic should be promoted only after failure and rollback
tests exist.

## Release And Community Sequence

1. Publish the honest v0.1 dry-run foundation for early contributors.
2. Launch broadly when v0.2 produces a local model answer with valid citations.
3. Recruit NVIDIA and ARM64 contributors for verified hardware profiles.
4. Publish a measured DGX Spark integration report.
5. Recruit Azure infrastructure and security contributors for narrow discovery.
6. Demonstrate a staged migration in a disposable test environment.
7. Add AWS as an independently tested provider path.

## Launch Assets

- Two-minute local RAG demonstration
- Guided architect workflow diagram
- Example generated blueprint
- Validation failure and correction example
- DGX Spark compatibility report when verified
- Cloud migration data-flow diagram
- Explicit comparison with local RAG applications
- Focused contributor issues for each plugin boundary

## Repository Quality Checklist

- [ ] README value is clear in the first screen.
- [ ] Current and planned capabilities are visibly separated.
- [ ] Beginner quickstart works from a clean machine.
- [ ] Documentation links and Mermaid diagrams render.
- [ ] Local RAG provides grounded answers and refusals.
- [ ] Generated artifacts record schema and generator versions.
- [ ] No provider plugin requests undocumented permissions.
- [ ] No target is called supported without target-specific tests.
- [ ] Good first issues are small and reproducible.
- [ ] Architecture issues include acceptance and safety criteria.

## Suggested GitHub Topics

```text
private-ai
rag
local-ai
ai-infrastructure
cloud-migration
llmops
ollama
vllm
nvidia-nim
dgx-spark
qdrant
terraform
azure-openai
aws-bedrock
self-hosted
enterprise-ai
```

## Maintainer Rules

- Ship working artifacts before broad promotion.
- Keep the README synchronized with implementation.
- Publish measurements and limitations with hardware claims.
- Keep discovery permissions narrow and visible.
- Treat repeated setup friction as a workflow or validation improvement.
- Reject provider templates that are not validated.
- Reject compliance and production claims that lack evidence.
- Keep first-time contributor tasks bounded.
- Publish progress, failures, and changed assumptions.

## What Not To Do

- Do not buy stars.
- Do not market the project as an automatic enterprise migration.
- Do not claim data remains entirely on-premises when payloads transit cloud.
- Do not claim full cloud inventory.
- Do not treat AWS as renamed Azure configuration.
- Do not make one DGX Spark sound highly available.
- Do not weaken review or rollback requirements for a cleaner demo.
