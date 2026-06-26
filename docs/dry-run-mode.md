# Dry-Run Mode

Dry-run mode is the safest first interaction with the project. It should collect setup intent and generate a complete review pack without mutating the machine or touching real company data.

## Command

```bash
private-ai init --dry-run
```

## Guarantees

Dry-run mode must not:

- Start containers
- Modify firewall rules
- Expose ports
- Create operating system users
- Create application users
- Apply VPN configuration
- Connect to production databases
- Ingest real company data
- Download models unless explicitly allowed for local planning
- Write secrets into generated files

Dry-run mode may:

- Ask setup questions
- Validate answer completeness
- Generate proposed config files
- Generate documentation artifacts
- Generate checklists
- Warn about risky selections
- Estimate hardware and network requirements

## Output Directory

```text
generated/
  dry-run/
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

## Wizard Flow

1. Select deployment mode.
2. Identify company, department, and business goal.
3. Identify data types that are allowed and forbidden.
4. Select access pattern: localhost, LAN, VPN, or hybrid gateway.
5. Select model runtime and vector database.
6. Define roles and collections.
7. Define audit requirements.
8. Define ingestion sources.
9. Generate proposed files.
10. Generate validation report.
11. Print next steps.

## Dry-Run Review Gates

The generated pack should be reviewed by:

- Manager or business owner for scope and risk ownership
- Data owner for allowed source approval
- Security engineer for guardrails, RBAC, audit, and threat model
- Network engineer for exposure, ports, DNS, VPN, and gateway choices
- AI engineer for model, embeddings, retrieval, and evaluation settings
- Developer or operator for deployment feasibility

## Example Review Checklist

```text
[ ] Business purpose is documented.
[ ] Production owner is named.
[ ] Data owner approved every ingestion source.
[ ] Forbidden data types are documented.
[ ] Remote access is disabled or reviewed.
[ ] Model runtime is not directly exposed.
[ ] Audit logging is enabled for production.
[ ] Admin role assignment is explicit.
[ ] Secrets are excluded from ingestion.
[ ] Cyber mode is read-only.
[ ] Apply command is blocked until validation passes.
```

## Promotion to Apply

Dry-run output should not automatically become active configuration. Promotion should be explicit:

```bash
private-ai validate generated/dry-run
private-ai apply generated/dry-run
```

`apply` should refuse to run if validation has not passed or if the dry-run pack contains unresolved blocking findings.
