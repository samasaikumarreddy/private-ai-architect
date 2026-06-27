# Starting RAG From Scratch

Private AI Architect is not only for companies considering a cloud migration.
It can also help a developer, team, or company start from zero and design a
safe Retrieval-Augmented Generation system.

> Current status: local RAG works through the v0.2.1 CLI. v0.3 generates a
> planning blueprint and review documents. AWS-native, Azure-native, private
> GPU, DGX, cloud GPU, Mac cluster, hybrid, and migration targets are planning
> directions only unless a later milestone explicitly implements and verifies
> them.

## RAG In Simple Terms

RAG means Retrieval-Augmented Generation:

1. Choose which files and data sources are approved.
2. Index only that approved information.
3. Let a user ask a question.
4. Retrieve the most relevant approved passages.
5. Ask a model to answer from those passages.
6. Include citations so the user can inspect the evidence.
7. Refuse when the approved sources do not contain enough evidence.

The model should not receive every file, invent missing facts, or silently
expand its data access.

## Start With The Data Boundary

The first question is not:

> Which GPU should I buy?

The first question is:

> Where is the data allowed to be stored and processed?

Possible answers include:

- a developer machine
- a company file server
- an existing AWS environment
- an existing Azure or Microsoft 365 environment
- an internal GPU server
- a DGX system
- an approved cloud GPU environment
- a Mac workstation or cluster
- a reviewed hybrid boundary
- unknown, pending data-owner or security review

Private AI Architect should work with an organization's approved environment,
not assume that every workload must move to local hardware.

## Planner, Runtime, And Data May Be Separate

The guided architect CLI may run on a developer laptop or admin workstation.
The future RAG runtime may run somewhere else.

```text
developer or admin machine
  -> runs private-ai architect
  -> creates blueprint and review documents

approved runtime target
  -> may later run ingestion, index, retrieval, and model

approved data residency
  -> controls where those data-processing components may operate
```

Running the planning CLI on a laptop does not authorize copying company data
to that laptop.

## Common Starting Paths

### 1. Local-First RAG

Use this path when:

- learning how RAG works
- working with approved local project documents
- keeping the first version on one machine
- starting with one developer or a small experiment

A small target may contain local files, the local JSON index, an installed
Ollama model, cited answers, and refusal when evidence is missing.

This is the first working reference path in the current project.

### 2. AWS-Native RAG Planning

Consider this path when:

- approved company data already lives in AWS
- AWS is already inside the organization's trust boundary
- IAM, logging, retention, and governance are already established
- moving data elsewhere would add risk without a clear benefit

A future AWS-specific planning path may evaluate approved AWS data sources,
identity-aware retrieval, audit requirements, and managed or self-hosted model
choices.

The current CLI does not call AWS APIs, inspect S3, modify IAM, or generate an
AWS deployment.

### 3. Azure-Native RAG Planning

Consider this path when:

- approved data already lives in Azure or Microsoft 365
- Azure is already inside the organization's trust boundary
- the team wants to preserve existing identity, governance, and monitoring

A future Azure-specific planning path may evaluate approved data sources,
identity boundaries, retrieval options, and model/runtime choices.

The current CLI does not call Azure APIs, inspect Microsoft 365, modify Entra,
or deploy Azure resources.

### 4. Private GPU Or DGX Planning

Consider this path when:

- data must remain in a company-controlled environment
- cloud inference is not approved
- model and runtime control are important
- performance or concurrency may justify private GPU hardware

v0.3 can record the target and risks. It does not configure DGX, install a
runtime, test compatibility, or verify capacity.

### 5. Hybrid RAG Planning

Consider this path when:

- some data is approved for cloud processing
- other data must remain on-premises
- departments have different access or residency rules
- an existing cloud control plane must coexist with private compute

A safe hybrid design must describe storage, processing, transit, telemetry,
identity, and logging separately. Saying that data "never leaves the building"
would be incorrect when prompts or responses transit a cloud service.

Hybrid implementation is not part of the current CLI.

## Read-Only First

The safest first RAG version is usually read-only.

Read-only RAG may:

- answer questions
- summarize documents
- explain approved code
- compare policies
- analyze approved files
- generate reports with citations

It should not immediately:

- update databases
- delete records
- change permissions
- modify production systems
- trigger payments
- change infrastructure

Write actions require a later, separately reviewed milestone with explicit
authorization, audit logs, validation, rollback, and human approval.

## What The Blueprint Should Explain

Before infrastructure changes, the planning blueprint should make these facts
reviewable:

- where the architect CLI runs
- where data is allowed to live
- who owns and approves the data
- which sources are allowed
- who needs access
- whether cloud inference is allowed
- where the future runtime should run
- which model and runtime are preferred or unknown
- which authentication and RBAC controls are needed
- which audit and compliance concerns apply
- whether the first version is read-only
- which risks and unresolved decisions remain
- which architecture path is recommended
- which operations remain explicitly out of scope

The current v0.3 schema implements most of this planning foundation. Dedicated
cloud-allowance, use-case, access-model, read-only-intent, and
recommended-architecture fields are design candidates for a reviewed schema
revision; they are not silently implied by existing fields.

## Recommendation Principle

A future vendor-aware recommendation engine should prefer:

- AWS-native planning when data is already in approved AWS boundaries
- Azure-native planning when data is already in approved Azure boundaries
- local or private RAG when cloud inference is prohibited
- local RAG for a first-time developer working on one approved machine
- private GPU or DGX planning when control and performance justify it
- hybrid planning and security review when boundaries are mixed
- migration planning only when the user explicitly chooses migration

These recommendations must be based on user-provided, reviewed answers in the
planning milestone. They must not trigger provider discovery or deployment.

## Try The Current Safe Flow

Generate a local-first planning pack from synthetic answers:

```bash
private-ai architect --answers-file examples/architect/local-rag-answers.json --output-dir generated/architect --force
private-ai blueprint validate generated/architect
```

Then inspect:

- `blueprint.json`
- `summary.md`
- `decisions-needed.md`
- `security-risks.md`
- `next-steps.md`

No named document source is opened by the architect command.

## Core Direction

Private AI Architect should not fight existing infrastructure. It should help
users choose the safest RAG architecture for the environment they already
trust.

**Blueprint first. Deployment later.**
