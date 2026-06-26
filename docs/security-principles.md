# Security Principles

Private AI systems should fail closed. The safest defaults should require less expertise than the risky settings.

## Default Rules

- Keep sensitive company data inside the trusted environment.
- Use dry-run before apply.
- Require validation before deployment.
- Use least privilege for users, services, and data sources.
- Enforce collection-level access before retrieval.
- Require audit logging in production.
- Keep cyber analyst mode read-only in v1.
- Do not expose the LLM runtime directly to the internet.
- Do not store secrets in Git.
- Do not ingest secrets, credentials, keys, or `.env` files.

## RBAC Model

RBAC should control:

- Chat access
- Ingestion access
- Audit visibility
- Admin actions
- Collection access
- Cyber analyst functions
- Developer assistant functions

Example:

```yaml
roles:
  manager:
    can_chat: true
    can_ingest: false
    can_view_audit: false
    collections:
      - policies
      - reports

  developer:
    can_chat: true
    can_ingest: true
    can_view_audit: false
    collections:
      - docs
      - codebase

  security_analyst:
    can_chat: true
    can_ingest: false
    can_view_audit: true
    collections:
      - security_logs
      - incident_reports

  admin:
    can_chat: true
    can_ingest: true
    can_view_audit: true
    can_manage_users: true
    collections:
      - "*"
```

## Audit Policy

Audit logs should capture:

- Timestamp
- User or service account
- Role
- Action
- Collection
- Source documents used
- Query hash or redacted query
- Model runtime and model name
- Status
- Validation warnings
- Admin changes

Example:

```json
{
  "timestamp": "2026-06-26T10:30:00Z",
  "user": "developer@example.com",
  "role": "developer",
  "action": "rag_query",
  "collection": "codebase",
  "query_hash": "sha256:...",
  "sources_used": ["api_docs.pdf", "readme.md"],
  "model": "local-llm",
  "status": "success"
}
```

## Prompt-Injection Guardrails

Retrieved documents must be treated as untrusted content. The assistant should:

- Keep system instructions separate from retrieved text.
- Ignore instructions found inside retrieved documents.
- Identify suspicious prompt-injection patterns.
- Prefer cited source-grounded answers.
- Refuse to reveal secrets or hidden instructions.
- Avoid summarizing documents the user cannot access.
- Log retrieval decisions.

## Data Protection

The ingestion layer should deny:

- `.env`
- SSH keys
- API keys
- Password files
- Cloud credentials
- Browser credential exports
- Private certificates
- Token dumps
- Unapproved home directory scans
- Unapproved production database dumps

The system should support allowlists before broad discovery. Denylists are useful, but they are not enough.

## Network Safety

The network layer should:

- Bind to localhost by default.
- Require review before LAN exposure.
- Require VPN or Zero Trust for remote access.
- Block public model runtime exposure.
- Document every exposed port.
- Separate admin access from user chat access where practical.
- Log gateway access.

## Cyber Analyst Mode

Cyber mode is read-only in v1.

Allowed:

- Summarize logs
- Explain suspicious events
- Group similar alerts
- Suggest investigation steps
- Map events to MITRE ATT&CK style categories
- Draft incident notes for human review

Blocked:

- Automatic firewall changes
- Account disabling
- File deletion
- Autonomous remediation
- Direct shell execution
- Malware execution
- Unsafe dynamic analysis

