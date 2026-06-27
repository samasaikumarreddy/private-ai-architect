# Vision

Private AI Infrastructure Blueprint is an open-source guided architect for
designing RAG and private AI inside an environment the user already trusts.

It asks the questions an experienced infrastructure architect would ask,
records unresolved decisions instead of guessing, generates reviewable
configuration and migration artifacts, validates known risks, and eventually
helps an approved operator deploy and verify the target system.

The project does not try to replace an architect, security engineer, cloud
engineer, or compliance reviewer. It makes their decisions explicit,
repeatable, and easier to review.

## Problem

Private AI projects are difficult for reasons that extend beyond running a
model:

- A small business may buy a DGX Spark or GPU server but lack a clear migration
  and integration plan.
- A developer may have an RTX GPU and approved company documents but no safe,
  repeatable local RAG setup.
- A cloud-integrated company may be safer using cloud-native RAG because its
  approved data, identity, logging, and governance already live there.
- Another company may have a specific reason to move inference from a cloud
  service while retaining useful identity, gateway, monitoring, and security
  investments.
- Source permissions do not automatically become retrieval permissions.
- Runtime, model, network, data, identity, audit, and rollback decisions are
  spread across different teams.
- Broad infrastructure discovery requires sensitive credentials and varies
  substantially between customers.
- Production cutover requires capacity checks, traffic control, health checks,
  fallback criteria, and human approval.

Teams need a guided process that separates what can be automated from what must
be decided and approved by people.

## Product Definition

> An open-source guided architect that starts with data residency and trust
> boundaries, builds a normalized private-AI blueprint, recommends a safe
> architecture path, validates risks, and produces evidence for human review.

The product direction covers three broad workflows:

1. **Start RAG safely:** help a first-time user choose local-first,
   cloud-native, private, or hybrid RAG based on data location and approved
   trust boundaries.
2. **Plan private hardware:** help a small business prepare to integrate a DGX
   Spark, generic NVIDIA GPU server, or another supported target.
3. **Plan an explicit migration:** help a company assess and gradually move a
   selected workload only when migration is the user's stated intent.

These workflows share one blueprint and validation engine, but their
questionnaires and generated artifacts must branch early. A local developer
must not be asked enterprise VPC questions, and a cloud migration must not be
treated like a clean local installation.

## Product Responsibilities

The project should:

- Ask only questions relevant to the selected workflow.
- Support unknown and unresolved answers without inventing values.
- Perform provider-specific, read-only discovery with least-privilege
  credentials.
- Produce a normalized, versioned blueprint as the source of truth.
- Generate Docker, runtime, model, network, RBAC, audit, cloud, migration, and
  rollback artifacts when relevant.
- Validate unsafe, incompatible, incomplete, and unreviewed choices.
- Require explicit approval before any infrastructure mutation.
- Verify the deployed system against the approved blueprint.
- Produce an evidence pack containing decisions, checks, warnings, approvals,
  and test results.

## What Success Looks Like

A user should be able to follow a controlled lifecycle:

```text
Choose workflow
  -> Answer relevant questions
  -> Optionally run narrow read-only discovery
  -> Generate normalized blueprint
  -> Generate proposed artifacts
  -> Validate
  -> Review and approve
  -> Apply with explicit permission
  -> Verify
  -> Migrate or cut over gradually
  -> Export evidence
```

The first proof is smaller: a developer can generate and validate a plan,
index approved sample documents, and receive cited local answers. The same
blueprint model then expands to vendor-aware RAG recommendations, private
hardware, provider-specific planning, and explicit migration workflows.

## Trust And Compliance Position

The tool can generate framework-aware checks and evidence requirements. It
cannot certify that an organization complies with GDPR, HIPAA, SOX, or any
other legal or regulatory framework.

Generated reports must distinguish:

- Control detected
- Control missing
- Requires human evidence
- Not evaluated

Applicability remains unverified until the organization's authorized legal,
privacy, security, and compliance reviewers confirm it.

## Non-Goals

This project is not:

- A replacement for qualified architects or reviewers.
- A guarantee or certification of compliance.
- A promise to inventory an entire cloud account.
- A one-command production migration with no review.
- A public SaaS product by default.
- A fully autonomous security or remediation system.
- A tool for bypassing company policy.
- A system that should ingest secrets, credentials, or private keys.
- A deployment process that hides risk to make migration look easier.
