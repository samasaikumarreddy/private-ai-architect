# Security Principles

Private AI systems should fail closed. The safest defaults should require less expertise than the risky settings.

## Default Rules

- Record storage, processing, transit, telemetry, and backup locations
  separately.
- Keep sensitive company data inside the approved boundaries.
- Use dry-run before apply.
- Require validation before deployment.
- Use least privilege for users, services, and data sources.
- Enforce collection-level access before retrieval.
- Require audit logging in production.
- Keep cyber analyst mode read-only in v1.
- Do not expose the LLM runtime directly to the internet.
- Do not store secrets in Git.
- Do not ingest secrets, credentials, keys, or `.env` files.
- Do not persist cloud discovery credentials.
- Do not claim regulatory compliance from configuration checks.
- Keep discovery, generation, approval, apply, verification, and cutover as
  separate permissions.

## Guided Architect Safety

- Select workflow intent before asking target-specific questions.
- Treat unresolved critical answers as blockers.
- Require discovery plugins to publish exact read permissions.
- Restrict discovery to allowlisted providers, resources, and fields.
- Avoid reading provider prompt, response, or document content by default.
- Bind every approval to an exact blueprint revision.
- Mark generated infrastructure as proposed until an apply implementation
  records otherwise.
- Require verification before calling a target operational.
- Require explicit rollback criteria before changing production traffic.

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
- Apply on-premises admission control even when a cloud WAF is present.
- Disable cloud payload logging by default when prompts or responses transit a
  managed gateway.

## Framework-Aware Evidence

Governance framework selections may activate relevant questions, checks, and
evidence requirements. Reports must use these states:

- Control detected
- Control missing
- Requires human evidence
- Not evaluated

The tool must not issue compliance certifications. Legal applicability,
administrative safeguards, physical controls, policies, contracts, and risk
acceptance require authorized human review.

## Derived Knowledge Safety

An optional generated wiki must preserve the distinction between evidence and
synthesis:

- Raw sources remain immutable.
- Generated pages are labeled derived.
- Every generated claim retains source and chunk provenance.
- Effective access is the intersection of contributing source permissions.
- Source changes or deletion mark dependent pages stale.
- Sensitive changes enter a review queue before publication.
- Agent read and write tools remain separate.

Vector or KV-cache compression must fail closed when runtime support is unknown
and must require a quality benchmark before activation.

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
