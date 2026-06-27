# CLI Reference

The CLI supports guided architecture planning, blueprint validation, dry-run
planning, local readiness inspection, safe local indexing, retrieval-only
citations, and optional local Ollama-backed answers.

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
private-ai evaluate
private-ai architect
private-ai blueprint validate
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
verification, evidence export, shadowing, cutover, and rollback. Command names
for those stages are not stable and must not be treated as implemented.

## Guided Architect

Start the interactive branching questionnaire:

```bash
private-ai architect
```

The first prompt selects `local-rag`, `private-gpu`, or `cloud-migration`.
Questions that belong only to the other journeys are omitted.

Run without prompts using reviewed flags:

```bash
private-ai architect \
  --non-interactive \
  --journey local-rag \
  --project-name private-ai-demo \
  --owner-name local \
  --architect-location developer-workstation \
  --runtime-location same-machine \
  --data-location local-workstation \
  --document-source ./examples/sample-company-docs \
  --user-count 1 \
  --model-preference llama3.2:1b \
  --runtime-preference ollama \
  --hardware-availability "local workstation" \
  --network-exposure localhost \
  --compliance none \
  --authentication-rbac "single approved local user" \
  --audit-logging "local reviewed logs" \
  --data-owner-approval approved \
  --output-dir generated/architect \
  --force
```

On PowerShell, use a JSON answers file to avoid shell line-continuation
differences:

```powershell
private-ai architect `
  --answers-file examples/architect/local-rag-answers.json `
  --output-dir generated/architect `
  --force
```

`--answers-file` is non-interactive. Matching command-line flags override file
values. Source names are recorded as planning labels but are not opened or
ingested.

Placement options:

```text
--architect-location developer-workstation|admin-workstation|bastion-host|ci-runner|target-machine|unknown
--runtime-location same-machine|local-gpu-workstation|company-gpu-server|dgx-spark|dgx-server|cloud-gpu|mac-cluster|hybrid|unknown
```

`--data-location` separately records the approved data residency. Ingestion
and indexing must eventually run where that data is allowed to exist; the
architect command itself does not contact the target or read the source.

Generated files:

```text
generated/architect/
  blueprint.json
  summary.md
  decisions-needed.md
  security-risks.md
  next-steps.md
  validation-report.md
```

Validate the file or its containing directory:

```bash
private-ai blueprint validate generated/architect
private-ai blueprint validate generated/architect/blueprint.json
```

Warnings flag public exposure, missing data-owner approval, unknown model or
runtime choices, and planning-only hardware or cloud choices. Invalid schema,
journey, checksum, or safety fields fail validation.

The command never configures DGX or other hardware, calls Azure/AWS/Bedrock,
discovers resources, changes a network, ingests company data, or applies
infrastructure.

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

v0.2.1 ingestion options:

```text
--exclude <name-or-relative-glob>  Repeatable project-specific exclusion
--max-files 10000                 Maximum files added to one index
--max-file-bytes 2097152          Maximum size of one indexed file
```

Common source-code formats are supported in v0.2.1. Generated, dependency,
cache, signing, key, credential, and environment paths are denied by default.
Symbolic links are not followed. Operators must still review project-specific
paths and use `--exclude`.

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

The local Ollama client:

- Accepts only loopback Ollama URLs.
- Checks the installed-model list before generation.
- Never downloads a model.
- Refuses without model invocation when retrieval evidence is absent.
- Sends only retrieved chunks as context.
- Appends citations from retrieval.
- Falls back to retrieval-only output when Ollama is unavailable.

v0.2.1 uses BM25 over the local JSON index and remains backward compatible with
v0.2 indexes. Vector database writes and semantic embeddings are not
implemented.

## Evaluate Retrieval

```bash
private-ai evaluate --index generated/index/index.json --cases examples/evaluation/local-rag-cases.json
```

Options:

```text
--index <path>   Local JSON index to evaluate
--cases <path>   JSON file containing supported and unsupported query cases
--top-k <1-10>   Maximum retrieved chunks considered for each case
```

The command exits `0` only when every case passes. It evaluates retrieval and
pre-model refusal behavior; it does not invoke Ollama.

## List Modes

```bash
private-ai modes
```

This prints the supported deployment modes with their default runtime and vector database.

## Legacy Dry-Run Interactive Wizard

```bash
private-ai init --dry-run --interactive
```

The interactive path prompts for mode, project name, company/workspace name, departments, and approved data sources. It still performs dry-run generation only.

This legacy prompt path remains for v0.1 dry-run compatibility. Use
`private-ai architect` for the v0.3 branching question graph.

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
