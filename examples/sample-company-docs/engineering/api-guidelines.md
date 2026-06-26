# API Guidelines

Internal APIs should be designed for clear ownership, observability, and safe failure behavior.

## Standards

- Every API must have an owner.
- Authentication is required for non-public endpoints.
- Authorization must be checked before returning data.
- Requests should include a request ID for tracing.
- Errors should be explicit without exposing secrets.

## AI Integration Notes

AI assistants that answer questions about APIs must cite approved documentation. They should refuse to answer when the requested endpoint or behavior is not present in the approved source set.

