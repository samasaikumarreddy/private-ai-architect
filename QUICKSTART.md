# Quickstart

This quickstart uses only the synthetic documents included in the repository.
Do not use real company files until the data owner and security team approve
the deployment and source paths.

For copy-and-paste checks organized by release, see the
[Version Test Guide](docs/version-test-guide.md).

## Requirements

- Python 3.11 or newer
- Git
- Ollama only if you want optional local model-generated answers

A GPU is not required. Ollama can use a supported CPU configuration, although
generation will usually be slower.

## Install

Clone and enter the repository:

```bash
git clone https://github.com/samasaikumarreddy/private-ai-architect.git
cd private-ai-architect
```

Create a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Check Local Readiness

```bash
private-ai doctor
```

Docker, Ollama, and NVIDIA tools are reported as readiness signals. They are
not required for dry-run planning or retrieval-only search.

## Generate And Validate A Safe Plan

```bash
private-ai init --dry-run --mode local-developer --project-name private-ai-demo --company-name local --output-dir generated/dry-run --force
private-ai validate generated/dry-run
```

This generates proposed files only. It does not start services, modify the
firewall, expose ports, create users, or apply infrastructure.

## Build The Local Sample Index

```bash
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
```

The ingester supports approved documents and common source-code formats. It
prunes generated and dependency directories, rejects likely secret and signing
file names, does not follow symbolic links, and enforces file-count and
file-size limits. Use repeatable `--exclude` flags for project-specific paths.

## Retrieval-Only Chat

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json
```

This is the default and backward-compatible behavior. It returns matching
source excerpts with citations and does not call a model.

## Optional Local Ollama Answer

Install Ollama separately and confirm that the model you chose is already
present:

```bash
ollama list
```

For example, this explicit operator command installs the small model used by
the maintainers for the Windows smoke test:

```bash
ollama pull llama3.2:1b
```

This download is performed by Ollama only when you run the command. The
`private-ai` application never downloads a model.

Then pass that exact local model name:

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json --model llama3.2:1b
```

The command:

1. Searches the approved local index.
2. Refuses before model invocation when no meaningful evidence matches.
3. Checks `/api/tags` to verify the model is already installed.
4. Sends only query-matching sections from the retrieved chunks to the local
   Ollama chat API.
5. Prints the generated answer and citations from retrieval.

`private-ai` never calls Ollama's model-pull endpoint. If Ollama or the requested
model is unavailable, the command prints a warning and returns the normal
retrieval-only result.

The v0.2 client accepts only these local endpoints:

- `http://127.0.0.1:<port>`
- `http://localhost:<port>`
- `http://[::1]:<port>`

Remote Ollama servers and Ollama cloud models are outside this milestone.

## Evaluate Retrieval Quality

```bash
private-ai evaluate --index generated/index/index.json --cases examples/evaluation/local-rag-cases.json
```

The included suite checks three supported questions and one unsupported
question. All four must pass.

## Run Tests

```bash
python -m unittest discover -s tests -v
```

## Current Limitations

- Retrieval uses local BM25 scoring, not embeddings or Qdrant.
- Grounding is enforced through retrieval, evidence checks, prompting, and
  citations; model output can still be incorrect and must be verified.
- No web interface, MCP server, runtime RBAC, or production audit database is
  included.
- No infrastructure `apply`, firewall changes, cloud migration, or DGX
  configuration is implemented.

Read [Local RAG MVP](docs/local-rag-mvp.md) for the detailed behavior and
security contract. Development details for BM25, evaluation, and bounded code
ingestion are in
[RAG Quality And Code Ingestion v0.2.1](docs/rag-quality-v0.2.1.md).
