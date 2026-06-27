# CLI Reference

The CLI supports dry-run planning, validation, local readiness inspection,
safe local indexing, retrieval-only citations, and optional local
Ollama-backed answers.

## Install For Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

On Linux or macOS, activate with:

```bash
source .venv/bin/activate
```

## Commands

```bash
private-ai --help
private-ai --version
private-ai modes
private-ai init --dry-run
private-ai validate
private-ai doctor
private-ai ingest
private-ai chat
```

Planned but not implemented:

```bash
private-ai apply
private-ai audit
```

Those commands return a non-zero exit code because production-impacting
behavior should not exist until validation, approval, and runtime code are
ready.

The longer-term guided lifecycle also includes provider-specific discovery,
blueprint generation, verification, evidence export, shadowing, cutover, and
rollback. Command names for those stages are not stable and must not be treated
as implemented.

## Generate A Dry-Run Plan

```bash
private-ai init --dry-run --mode local-developer --project-name private-ai-demo --output-dir generated/dry-run --force
```

Generated files:

```text
generated/dry-run/
  architecture-plan.md
  stakeholder-checklist.md
  network-requirements.md
  security-review.md
  proposed-docker-compose.yml
  proposed-rbac.yaml
  proposed-env.example
  data-source-plan.md
  model-plan.md
  answers.json
  dry-run-summary.json
  validation-report.md
```

Dry-run mode does not:

- Start containers
- Modify firewall rules
- Create users
- Apply VPN configuration
- Ingest real company data
- Download models
- Expose ports

## Validate A Dry-Run Plan

```bash
private-ai validate generated/dry-run
```

Validation checks include:

- Required dry-run files exist.
- API and UI bind to localhost by default.
- Audit logging is required.
- Admin role requires explicit assignment.
- Secret and credential denied patterns are documented.
- Network requirements block direct model runtime exposure.
- Security review includes model runtime exposure controls.

## Doctor

```bash
private-ai doctor
```

The doctor command reports local readiness signals:

- Python version
- OS and CPU architecture
- Git availability
- Docker availability
- Ollama availability
- NVIDIA GPU tooling availability

Missing Docker, Ollama, or NVIDIA tooling is reported as a warning, not an immediate failure. CPU-only local planning is still valid.

## Local Retrieval And Optional Ollama

Build a local JSON index:

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
```

Ask a retrieval-only question:

```bash
private-ai chat "what are the AI usage rules?" --index generated/index/index.json
```

This returns cited source excerpts from the local index. Without `--model`, it
does not call an LLM, write to a vector database, or generate a model answer.

Ingestion skips denied secret patterns such as `.env`, private keys, credentials files, and token-like file names.

To request a local model-generated answer, pass a model that is already
installed in Ollama:

```bash
private-ai chat "what are the AI usage rules?" --index generated/index/index.json --model <installed-model>
```

Additional options:

```text
--ollama-url http://127.0.0.1:11434
--ollama-timeout 60
--top-k 3
```

The v0.2 client:

- Accepts only loopback Ollama URLs.
- Checks the installed-model list before generation.
- Never downloads a model.
- Refuses without model invocation when retrieval evidence is absent.
- Sends only retrieved chunks as context.
- Appends citations from retrieval.
- Falls back to retrieval-only output when Ollama is unavailable.

The index remains a lexical JSON index in v0.2. Vector database writes and
semantic embeddings are not implemented.

## List Modes

```bash
private-ai modes
```

This prints the supported deployment modes with their default runtime and vector database.

## Optional Interactive Wizard

```bash
private-ai init --dry-run --interactive
```

The interactive path prompts for mode, project name, company/workspace name, departments, and approved data sources. It still performs dry-run generation only.

This is not yet the planned branching question graph. Future versions will
select local RAG, private hardware, or cloud migration intent before asking
target-specific questions.

## Deployment Modes

Supported mode names and aliases:

| Canonical mode | Useful aliases |
| --- | --- |
| `local-developer` | `local`, `local-dev`, `developer` |
| `small-company` | `small` |
| `gpu-server` | `gpu` |
| `dgx-enterprise` | `dgx`, `dgx-spark`, `enterprise` |
| `hybrid-gateway` | `hybrid` |
| `dry-run-only` | `dry-run`, `planning` |

## Test Command

```bash
python -m unittest discover -s tests -v
```
