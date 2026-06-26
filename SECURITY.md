# Security Policy

This project is about private AI infrastructure, so security reports are important even while the repository is documentation-first.

## Supported Versions

No released implementation exists yet. Security review currently applies to documentation, examples, generated configuration designs, and future code.

## Reporting A Vulnerability

When this project is published on GitHub, enable GitHub private vulnerability reporting. Use that channel for vulnerabilities that could expose private data, weaken access control, bypass validation, or create unsafe network exposure.

Until a private reporting channel is configured, do not publish exploit details, real secrets, private company data, or live infrastructure information in public issues.

## What To Report

Please report:

- RBAC bypasses
- Audit logging bypasses
- Secret ingestion paths
- Prompt-injection handling failures
- Unsafe default network exposure
- Direct public model runtime exposure
- Validation bypasses
- Cyber mode actions that could perform remediation in v1
- Documentation examples that encourage unsafe deployment

## Security Defaults

The project should default to:

- Localhost binding
- Dry-run before apply
- Validation before deploy
- Approved data-source allowlists
- Secret filtering
- RBAC before retrieval
- Audit logging for sensitive actions
- Read-only cyber analyst mode
- No public exposure of model runtimes

## Data Handling

Do not include real company documents, credentials, private keys, tokens, logs, or secrets in issues, pull requests, examples, tests, screenshots, or generated outputs.

