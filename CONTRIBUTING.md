# Contributing

Thanks for considering a contribution. This project is intended to become a practical open-source blueprint for private AI infrastructure, so contributions should improve safety, clarity, or deployability.

## Current Project State

The repository is currently documentation-first. There is no implementation yet. Good early contributions include:

- Improving docs
- Adding examples
- Refining deployment modes
- Defining wizard questions
- Designing config schemas
- Adding validation rules
- Creating test plans

## Contribution Principles

- Keep private data private by default.
- Preserve dry-run before apply.
- Preserve validation before deployment.
- Do not add features that ingest secrets.
- Do not expose model runtimes directly to the public internet.
- Keep cyber analyst mode read-only in v1.
- Prefer vendor-neutral interfaces where practical.
- Make examples runnable on a normal developer machine when possible.

## Development Workflow

1. Fork the repository.
2. Create a focused branch.
3. Make the smallest coherent change.
4. Update docs when behavior changes.
5. Add or update tests once implementation exists.
6. Open a pull request with a clear summary and risk notes.

## Pull Request Checklist

- [ ] The change has a clear purpose.
- [ ] Documentation was updated if needed.
- [ ] No real secrets, company documents, credentials, tokens, or private keys are included.
- [ ] Unsafe deployment behavior is blocked or documented as out of scope.
- [ ] Security-sensitive behavior has validation or tests.
- [ ] The change does not weaken RBAC, audit logging, dry-run mode, or validation.

## Documentation Style

- Be direct and implementation-oriented.
- Prefer explicit examples over abstract claims.
- Separate MVP behavior from future enterprise behavior.
- Mark unresolved decisions as unresolved instead of guessing.
- Avoid vendor lock-in unless the file is explicitly about that vendor path.

## Security-Sensitive Contributions

Security-sensitive changes include:

- Auth
- RBAC
- Audit logging
- Data ingestion
- Network exposure
- Model runtime access
- Prompt handling
- Cyber analyst behavior
- Gateway or tunnel behavior

For these changes, include:

- Threat considered
- Safe default
- Validation rule
- Test plan
- Residual risk

