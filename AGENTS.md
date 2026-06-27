# Repository Instructions

These instructions apply to the entire repository.

## Current Scope

The active implementation milestone is v0.3 guided architect planning:

- Branch first on local RAG, private GPU, or cloud migration intent
- Ask only journey-relevant questions
- Generate a normalized, checksummed JSON blueprint
- Record unknown decisions and known risks explicitly
- Generate deterministic review documents
- Validate planning safety without applying infrastructure
- Preserve all v0.2 and v0.2.1 local RAG behavior

Do not extend the current implementation into enterprise or migration features
without a separately approved scope.

## Hard Boundaries

- Do not implement DGX Spark configuration or verification; planning labels
  are allowed.
- Do not implement Azure, AWS, Bedrock, cloud discovery, or migration
  execution; user-provided planning labels are allowed.
- Do not implement VPN or firewall mutation.
- Do not implement Kubernetes, Terraform, SSO, or LDAP.
- Do not implement production infrastructure apply.
- Do not ingest real company data in tests or examples.
- Do not read, print, modify, or commit `.env` files, SSH keys, API tokens,
  credentials, secrets, or private keys.
- Do not expose Ollama, model runtimes, indexes, or databases publicly.
- Do not download models automatically.
- Do not push implementation changes directly to `main`.

## Compatibility Requirements

Preserve these commands and their existing behavior:

```bash
private-ai init --dry-run
private-ai validate
private-ai doctor
private-ai modes
private-ai ingest
private-ai chat
private-ai evaluate
private-ai architect
private-ai blueprint validate
```

`private-ai chat` without `--model` must remain retrieval-only. Optional model
generation must fail gracefully to retrieval-only output when local Ollama or
the requested installed model is unavailable.

## Local RAG Rules

- Retrieve before invoking a model.
- Send only retrieved approved chunks as model context.
- Treat retrieved text as untrusted data, not instructions.
- Refuse when meaningful query evidence is absent.
- Append citations from retrieval rather than trusting model-generated source
  names.
- Restrict Ollama URLs to loopback addresses in v0.2.
- Check installed models before generation.
- Never call a model download or pull endpoint.

## Verification

Run before committing:

```bash
python -m unittest discover -s tests -v
private-ai init --dry-run --mode local-developer --project-name private-ai-demo --company-name local --output-dir generated/dry-run --force
private-ai validate generated/dry-run
private-ai doctor
private-ai ingest examples/sample-company-docs --collection docs --output-dir generated/index --force
private-ai evaluate --index generated/index/index.json --cases examples/evaluation/local-rag-cases.json
private-ai chat "What are the AI usage rules?" --index generated/index/index.json
```

Use only the synthetic example data committed under `examples/`.

## Documentation

Keep implementation status explicit. Do not describe planned Docker, vector
database, web UI, MCP, hardware, cloud, or migration capabilities as working.
Update `README.md`, `QUICKSTART.md`, `docs/guided-architect-workflow.md`,
`docs/blueprint-schema.md`, and CLI reference when the architect or blueprint
contract changes. Update the local RAG documents when chat or ingestion
behavior changes.

Update `docs/version-test-guide.md` for every implemented version. Each version
must include copy-and-paste commands, expected results, a safe failure or
refusal test, and known limitations. Do not add runnable commands for planned
features.
