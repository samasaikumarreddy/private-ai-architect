# Launch Checklist

This checklist defines what should exist before promoting the repository widely.

## Current Stage

Current stage: v0.1 safe planning foundation and retrieval preview.

The project is not ready for a broad local RAG launch yet because ingestion, model inference, Docker images, and the UI are not implemented. It is ready to be shared as an early blueprint with a working dry-run CLI if the messaging is honest.

## Pre-GitHub Checklist

- [x] Canonical README
- [x] Documentation map
- [x] Open-source mission
- [x] Guided architect workflow
- [x] Normalized blueprint proposal
- [x] Architecture docs
- [x] Deployment modes
- [x] Hardware/runtime options
- [x] Security principles
- [x] Threat model
- [x] MVP scope
- [x] Roadmap
- [x] Apache 2.0 license
- [x] Notice file
- [x] Contributing guide
- [x] Security policy
- [x] Code of conduct
- [x] Issue templates
- [x] Pull request template
- [x] Gitignore for secrets and generated output
- [x] Python package skeleton
- [x] `private-ai --help`
- [x] `private-ai init --dry-run`
- [x] `private-ai validate`
- [x] `private-ai doctor`
- [x] `private-ai modes`
- [x] Unit tests for the first CLI milestone
- [x] Machine-readable dry-run metadata
- [x] Retrieval-only local indexing preview
- [x] Retrieval-only cited query preview
- [x] Example config files
- [x] Safe sample docs and sample cyber logs
- [x] GitHub Actions CI
- [x] Makefile for common local commands
- [x] Git repository initialized
- [x] Baseline commits created
- [ ] GitHub repository created
- [ ] Repository description set
- [ ] Repository topics set
- [ ] Private vulnerability reporting enabled

## Before First Public Push

- [ ] Confirm project name.
- [ ] Confirm GitHub organization or personal account.
- [ ] Confirm license owner text if needed.
- [ ] Review README first screen.
- [ ] Check for secrets.
- [ ] Check for accidental private company references.
- [ ] Confirm all links work.
- [ ] Add initial issues for contributors.

## Before First Serious Launch

These should exist before asking large communities to try the project:

- [x] CLI package skeleton
- [x] `private-ai --help`
- [x] `private-ai init --dry-run`
- [x] Generated dry-run example
- [x] Example RBAC config
- [x] Example data-source config
- [x] Example Docker Compose output
- [x] Config validator skeleton
- [x] Machine-readable dry-run summary
- [x] Local JSON index preview
- [x] GitHub Actions CI
- [x] Safe synthetic sample docs
- [ ] Screenshots or terminal recording
- [ ] One short demo video or GIF
- [ ] "Good first issue" labels
- [ ] At least five good first issues
- [ ] At least three architecture tasks for experienced contributors

## Launch Message

Use this structure:

```text
I am building an open-source guided architect for private AI.

It asks workflow-specific questions, generates and validates a versioned
blueprint, and is designed to support:
- local RAG on CPU or RTX
- new GPU and DGX Spark integration
- staged Azure OpenAI and AWS Bedrock migration

The current release has safe dry-run generation and a retrieval preview. The
next milestone is a working local RAG reference with cited answers. Cloud
discovery and production migration are later, separately tested stages.

Repo: <link>
```

## 10k-Star Milestones

| Milestone | What must be true |
| --- | --- |
| 100 stars | README and docs resonate with early builders. |
| 500 stars | Dry-run CLI exists and people can generate useful artifacts. |
| 1,000 stars | Local RAG MVP runs from clone to cited answer. |
| 2,500 stars | A generic GPU and DGX Spark profile have reproducible target tests. |
| 5,000 stars | One narrow cloud migration path is demonstrated in a test environment. |
| 10,000 stars | The project is a trusted guided architect with active provider and target contributors. |

## First Issues To Create

- Build Python package skeleton
- Add CLI entry point
- Add versioned blueprint schema
- Add workflow intent question graph
- Add local developer question branch
- Add private hardware question branch
- Add cloud migration question branch
- Add RBAC config schema
- Add data-source config schema
- Add dry-run report generator
- Add validator for public bind addresses
- Add validator for secret ingestion patterns
- Add example Qdrant Docker Compose service
- Add example Ollama runtime profile
- Add sample company documents
- Add unresolved-decision validation
- Define Azure OpenAI discovery permission manifest
- Define DGX Spark ARM64 compatibility test matrix

## Launch Risk

The biggest risk is overclaiming. The project should be explicit:

- Dry-run and retrieval preview now
- Working local RAG next
- Guided blueprint and verified hardware profiles after that
- Narrow provider discovery and migration later

Credibility matters more than speed.
