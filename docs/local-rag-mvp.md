# Local RAG MVP

Status: v0.2 implementation.

The local RAG MVP adds optional model-generated answers to the existing local
retrieval flow. It intentionally uses the existing lexical JSON index so the
grounding and fallback contract can be proven without adding cloud services,
automatic model downloads, Docker deployment, or production infrastructure.

## Architecture

```mermaid
flowchart LR
    USER["private-ai chat"] --> SEARCH["Local lexical retrieval"]
    SEARCH --> EVIDENCE{"Meaningful evidence?"}
    EVIDENCE -->|No| REFUSE["Local refusal"]
    EVIDENCE -->|Yes, no model requested| EXCERPTS["Cited source excerpts"]
    EVIDENCE -->|Yes, model requested| PREFLIGHT["Check local Ollama and installed model"]
    PREFLIGHT -->|Unavailable| EXCERPTS
    PREFLIGHT -->|Available| MODEL["Local Ollama chat API"]
    MODEL --> ANSWER["Answer plus retrieval citations"]
```

## CLI Contract

Retrieval-only behavior remains the default:

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json
```

Optional local generation requires an explicit installed model:

```bash
private-ai chat "What are the AI usage rules?" --index generated/index/index.json --model <installed-model>
```

Optional flags:

| Flag | Default | Behavior |
| --- | --- | --- |
| `--model` | unset | Enables local Ollama generation only when explicitly supplied. |
| `--ollama-url` | `http://127.0.0.1:11434` | Must resolve to a loopback hostname in v0.2. |
| `--ollama-timeout` | `60` | Local API timeout in seconds. |
| `--top-k` | `3` | Maximum retrieved chunks supplied as evidence; accepted range is 1 through 10. |

## Grounding Flow

1. Load the existing local index.
2. Score chunks using the existing lexical retrieval behavior.
3. Remove common query stop words for the evidence decision.
4. Refuse without invoking Ollama when no meaningful query term matches.
5. Query local Ollama `/api/tags`.
6. Continue only if the requested model is already installed.
7. Send a system instruction, the question, and numbered retrieved chunks to
   `/api/chat` with streaming disabled.
8. Instruct the model to use only supplied sources and return a fixed refusal
   token if support is insufficient.
9. Append source paths and chunk numbers from retrieval to the final output.

The client never calls `/api/pull`.

## Localhost Boundary

Accepted hosts:

- `127.0.0.1`
- `localhost`
- `::1`

The client rejects:

- Remote IP addresses
- Non-HTTP schemes
- URLs containing credentials
- URLs containing API paths, queries, or fragments
- Ollama cloud model names

The HTTP client also disables proxy use for local Ollama calls.

## Failure And Refusal Behavior

| Condition | Result |
| --- | --- |
| No `--model` | Retrieval-only cited excerpts |
| No meaningful retrieved evidence | Refusal; Ollama is not called |
| Ollama unavailable | Warning plus retrieval-only fallback |
| Requested model not installed | Warning plus retrieval-only fallback |
| Invalid Ollama response | Warning plus retrieval-only fallback |
| Model returns the refusal token | User-facing insufficient-evidence refusal |
| Model returns an answer | Model answer plus citations generated from retrieval |

Fallback is successful command behavior and returns exit code `0`. Invalid user
configuration, such as a non-loopback Ollama URL, returns a CLI usage error.

## Safety Properties

- No GPU requirement
- No model download
- No cloud endpoint or credentials
- No public network binding
- No firewall changes
- No production apply
- No change to denied-file ingestion rules
- No model invocation without retrieved evidence
- No model-provided source path trusted as a citation

## Tests

The v0.2 tests cover:

- Installed-model preflight before chat
- No automatic model download
- Cited model-answer output
- Unsupported-question refusal without model invocation
- Ollama-unavailable retrieval fallback
- Non-loopback and cloud-model rejection
- Denied-file exclusion
- Existing dry-run and validation behavior
- Existing retrieval-only chat behavior

## Limitations

- Lexical retrieval is not semantic retrieval.
- A matching term does not prove that retrieved evidence fully answers a
  question.
- Prompt grounding reduces hallucination risk but cannot eliminate it.
- Absolute local privacy depends on the selected Ollama model actually being
  local; v0.2 rejects known cloud model suffixes but cannot inspect arbitrary
  custom model internals.
- Runtime authentication, user RBAC, vector storage, embeddings, deletion
  propagation, and production audit storage remain future work.

## Primary Ollama References

- [Ollama chat API](https://docs.ollama.com/api/chat)
- [Ollama installed-model API](https://docs.ollama.com/api/tags)
- [Ollama API errors](https://docs.ollama.com/api/errors)
- [Ollama streaming behavior](https://docs.ollama.com/api/streaming)
