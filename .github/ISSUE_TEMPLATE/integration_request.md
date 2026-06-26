---
name: Integration request
about: Request support for a runtime, vector database, deployment target, or data source
title: "[Integration]: "
labels: integration
assignees: ""
---

## Integration

What should this project integrate with?

Examples: Ollama, vLLM, NVIDIA NIM, Qdrant, Chroma, Milvus, pgvector, Docker Compose, Kubernetes, WireGuard, Tailscale, LDAP, SSO.

## Use Case

Who needs this and why?

## Deployment Mode

- [ ] Local Developer
- [ ] Small Company
- [ ] GPU Server
- [ ] DGX / Enterprise
- [ ] Hybrid Gateway
- [ ] Dry-Run Planning Only

## Safety Requirements

How should this integration preserve:

- Dry-run before apply
- Validation before deploy
- RBAC before retrieval
- Audit logging
- Approved data-source rules
- No direct public model runtime exposure

## Proposed Config Shape

Optional example:

```yaml
integration:
  name:
  mode:
  required_settings: []
```

## Additional Context

Do not include real company data, secrets, tokens, private keys, or sensitive logs.

