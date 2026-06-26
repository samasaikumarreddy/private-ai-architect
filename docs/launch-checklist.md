# Launch Checklist

This checklist defines what should exist before promoting the repository widely.

## Current Stage

Current stage: first dry-run CLI milestone.

The project is not ready for a broad local RAG launch yet because ingestion, model inference, Docker images, and the UI are not implemented. It is ready to be shared as an early blueprint with a working dry-run CLI if the messaging is honest.

## Pre-GitHub Checklist

- [x] Canonical README
- [x] Documentation map
- [x] Open-source mission
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
- [x] Unit tests for the first CLI milestone
- [x] Example config files
- [x] Safe sample docs and sample cyber logs
- [x] GitHub Actions CI
- [x] Makefile for common local commands
- [ ] Git repository initialized
- [ ] First commit created
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
I am building an open-source private AI infrastructure blueprint for devs and companies that want local AI, RAG over approved docs, GPU/DGX deployments, RBAC, audit logs, and dry-run planning before touching real infrastructure.

The repo starts as a docs-first blueprint and is moving toward a CLI plus local RAG MVP.

Looking for contributors interested in:
- local AI
- RAG
- FastAPI
- Ollama/vLLM/NVIDIA NIM
- Qdrant/Chroma
- security validation
- developer tooling

Repo: <link>
```

## 10k-Star Milestones

| Milestone | What must be true |
| --- | --- |
| 100 stars | README and docs resonate with early builders. |
| 500 stars | Dry-run CLI exists and people can generate useful artifacts. |
| 1,000 stars | Local RAG MVP runs from clone to cited answer. |
| 2,500 stars | Contributors add integrations and examples. |
| 5,000 stars | Project has demos, issues, docs, and visible adoption. |
| 10,000 stars | Project is a known starting point for private AI infrastructure. |

## First Issues To Create

- Build Python package skeleton
- Add CLI entry point
- Add dry-run answer schema
- Add manager wizard questions
- Add developer wizard questions
- Add security wizard questions
- Add network wizard questions
- Add RBAC config schema
- Add data-source config schema
- Add dry-run report generator
- Add validator for public bind addresses
- Add validator for secret ingestion patterns
- Add example Qdrant Docker Compose service
- Add example Ollama runtime profile
- Add sample company documents

## Launch Risk

The biggest risk is overclaiming. The project should be explicit:

- Blueprint and dry-run CLI now
- Local RAG MVP after that
- Enterprise features later

Credibility matters more than speed.
