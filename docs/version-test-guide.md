# Version Test Guide

This guide provides copy-and-paste commands for testing every implemented
version of Private AI Architect. Start with the included synthetic documents.
Do not use private company files, credentials, keystores, `.env` files, or
secret-containing configuration.

## Version Status

| Version | Status | What this guide verifies |
| --- | --- | --- |
| v0.1 | Implemented and preserved | Dry-run planning, validation, readiness checks, and retrieval |
| v0.2.0 | Released | Optional local Ollama answers, citations, refusal, and fallback |
| v0.2.1 | Released | BM25, evaluation, grounding checks, and bounded code ingestion |
| v0.3 | Implemented on development branch | Guided journeys, normalized blueprint, review documents, and validation |
| v0.4+ | Planned | Commands will be added only after the feature is implemented |

## One-Time Setup

### Windows PowerShell

```powershell
git clone https://github.com/samasaikumarreddy/private-ai-architect.git
cd private-ai-architect

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

For an existing checkout:

```powershell
cd "C:\path\to\private-ai-architect"
git pull
python -m pip install -e .
```

### macOS Or Linux

```bash
git clone https://github.com/samasaikumarreddy/private-ai-architect.git
cd private-ai-architect

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Confirm the installed version:

```bash
private-ai --version
```

## Test v0.1: Safe Planning Foundation

These commands verify the v0.1 behavior that remains supported in later
versions.

List the available planning modes:

```bash
private-ai modes
```

Generate a local-developer plan without applying infrastructure:

```bash
private-ai init --dry-run --mode local-developer --project-name private-ai-demo --company-name local --output-dir generated/dry-run --force
```

Validate the generated review files:

```bash
private-ai validate generated/dry-run
```

Inspect local readiness:

```bash
private-ai doctor
```

Expected results:

- `modes` lists the supported planning profiles.
- `init --dry-run` creates proposed files under `generated/dry-run`.
- `validate` reports `Status: PASS`.
- `doctor` reports available tools and warnings without changing the machine.
- No service, firewall rule, cloud resource, or infrastructure is applied.

## Test v0.2: Retrieval-Only RAG

Build an index from the repository's synthetic sample documents:

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
```

Ask a question without invoking a model:

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json
```

Expected results:

- Three synthetic files are indexed.
- The response heading is `Retrieval-only response`.
- Every result includes a source path and chunk number.
- No model is contacted.

## Test v0.2: Local Ollama Answer

Ollama is optional. Install it separately, then list locally installed models:

```bash
ollama list
```

The following is an explicit operator-controlled example download:

```bash
ollama pull llama3.2:1b
```

`private-ai` never runs that download command automatically.

Request a local model-generated answer:

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json --model llama3.2:1b
```

Expected results:

- The response heading is `Local model RAG response`.
- The answer uses facts from retrieved sample documents.
- Claims contain source numbers such as `[1]`.
- The `Sources` section maps those numbers to local files and chunks.

If Ollama or the model is unavailable, the command safely returns a
retrieval-only response instead.

## Test v0.2: Unsupported Question Refusal

```bash
private-ai chat "What minerals are present on the moon?" --index generated/index/index.json --model llama3.2:1b
```

Expected result:

```text
Local RAG refusal

I cannot answer this question from the approved indexed sources.
```

The evidence check should refuse before invoking Ollama.

## Test v0.2: Citation Integrity

Limit retrieval to one source:

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json --model llama3.2:1b --top-k 1
```

Expected results:

- Generated claims may cite `[1]`.
- The answer must not cite `[2]` or a larger number.
- Missing or unknown citations cause a warning and retrieval-only fallback.
- An invalid generated answer is never presented as a valid cited answer.

## Optional: Test Approved Personal Documentation

Do not index an entire software project. Build an index from a small,
human-reviewed documentation set:

```powershell
$project = "C:\path\to\your-project"

private-ai ingest `
  "$project\README.md" `
  "$project\documentation\decisions" `
  "$project\documentation\technical" `
  --collection personal-project-docs `
  --output-dir generated/personal-project-index `
  --force
```

Ask a focused question:

```powershell
private-ai chat "What are the main components of this project?" `
  --index generated/personal-project-index/index.json `
  --model llama3.2:1b `
  --top-k 1
```

Before ingestion, exclude:

- `.env` and credentials
- Keystores and private keys
- Cloud service configuration containing tokens or API keys
- `.git`, `build`, `.gradle`, and dependency directories
- Generated datasets, temporary output, and large logs

v0.2 does not index Kotlin, Java, Python, JavaScript, XML, or Gradle source
files. v0.2.1 adds bounded source-code ingestion.

## Test v0.2.1: Retrieval Evaluation

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
private-ai evaluate --index generated/index/index.json --cases examples/evaluation/local-rag-cases.json
```

Expected result: `Passed: 4/4`.

## Test v0.2.1: Bounded Source-Code Ingestion

```powershell
$project = "C:\path\to\your-project"

private-ai ingest $project `
  --collection project-code `
  --output-dir generated/project-code-index `
  --exclude vendor `
  --exclude third_party `
  --exclude generated `
  --max-files 5000 `
  --max-file-bytes 1048576 `
  --force
```

Review every skipped path and the generated index metadata before asking
questions. Never ingest a repository root without reviewing its secret,
generated, dependency, and dataset locations.

## Test v0.3: Guided Architect Journeys

Generate all three planning-only examples:

```bash
private-ai architect --answers-file examples/architect/local-rag-answers.json --output-dir generated/architect-local --force
private-ai architect --answers-file examples/architect/private-gpu-answers.json --output-dir generated/architect-gpu --force
private-ai architect --answers-file examples/architect/cloud-migration-answers.json --output-dir generated/architect-cloud --force
```

Expected results:

- Each command writes `blueprint.json` and five Markdown review files.
- Each blueprint separates architect CLI location, target runtime location,
  and data residency.
- Local RAG output has no cloud migration detail fields.
- Private GPU output warns that DGX or GPU choices are planning-only.
- Cloud migration output says no provider discovery was performed.
- Every blueprint records `infrastructure_changes: false`.
- No source document, cloud API, or hardware endpoint is opened.

Validate each generated blueprint:

```bash
private-ai blueprint validate generated/architect-local
private-ai blueprint validate generated/architect-gpu
private-ai blueprint validate generated/architect-cloud
```

Schema validation must pass. Planning warnings are expected for unresolved,
private GPU, and cloud migration choices.

## Test v0.3: Safe Invalid-Journey Failure

```bash
private-ai architect --non-interactive --journey deploy-production --output-dir generated/invalid
```

Expected result:

```text
error: invalid journey 'deploy-production'. Allowed journeys: local-rag, private-gpu, cloud-migration
```

The command must exit non-zero and generate no deployment or infrastructure
changes.

## Run The Automated Test Suite

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m pip check
```

All commands must exit successfully before a version is considered ready.

## Troubleshooting

### `private-ai` Is Not Recognized

Activate the virtual environment and reinstall the editable package:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

### Ollama Is Unavailable

Check the local service and installed model:

```bash
private-ai doctor
ollama list
```

Do not replace the loopback Ollama URL with a public or remote address.

### An Index Already Exists

Use `--force` only when you intend to replace that generated index:

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
```

### The Model Answer Is Replaced By Retrieval Results

This is a safety fallback. It means Ollama was unavailable, the requested
model was missing, the response was invalid, or citations failed validation.
Read the warning printed immediately before the retrieval response.

## Test Report Template

Use this template in an issue or pull request:

```text
Version:
Operating system:
Python version:
Ollama version:
Model:
GPU or CPU:

Dry-run generation: PASS / FAIL
Validation: PASS / FAIL
Retrieval-only chat: PASS / FAIL
Model-backed chat: PASS / FAIL / NOT RUN
Unsupported-question refusal: PASS / FAIL / NOT RUN
Citation integrity: PASS / FAIL / NOT RUN
Retrieval evaluation: PASS / FAIL / NOT RUN
Source-code exclusions: PASS / FAIL / NOT RUN
Local architect journey: PASS / FAIL / NOT RUN
Private GPU planning journey: PASS / FAIL / NOT RUN
Cloud migration planning journey: PASS / FAIL / NOT RUN
Blueprint validation: PASS / FAIL / NOT RUN
Automated tests: PASS / FAIL

Notes:
```

## Adding A Future Version

Every implemented release must add a new section to this document with:

1. Version number and implementation status.
2. Prerequisites.
3. Exact copy-and-paste commands.
4. Expected successful output.
5. At least one safe refusal or failure test.
6. Cleanup or rollback commands when state is changed.
7. Known limitations.

Planned features must not receive runnable commands until their implementation
and tests exist.
