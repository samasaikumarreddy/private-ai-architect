# Blueprint Schema

v0.3 writes a normalized machine-readable plan to `blueprint.json`. The
current schema version is `1.0`.

The blueprint is a planning record. It is not a deployment configuration,
cloud inventory, hardware compatibility report, approval, or compliance
certificate.

## Generate And Validate

```bash
private-ai architect --answers-file examples/architect/local-rag-answers.json --output-dir generated/architect --force
private-ai blueprint validate generated/architect
```

Passing a directory makes the validator read its `blueprint.json`. A direct
file path also works:

```bash
private-ai blueprint validate generated/architect/blueprint.json
```

Validation reads only that generated JSON file. It does not inspect document
sources, call a cloud API, contact hardware, or apply infrastructure.

## Top-Level Contract

| Field | Type | Purpose |
| --- | --- | --- |
| `schema_version` | string | Blueprint contract version; currently `1.0`. |
| `blueprint_checksum` | string | SHA-256 over normalized content except the checksum field. |
| `provenance` | object | Generator command and package version. |
| `project` | object | Project name and company or accountable owner. |
| `journey` | string | `local-rag`, `private-gpu`, or `cloud-migration`. |
| `requirements` | object | Normalized requirements shared by every journey. |
| `journey_details` | object | Only the fields relevant to the selected journey. |
| `unresolved_decisions` | string array | Unknown or unapproved decisions that humans must resolve. |
| `known_risks` | string array | Deterministically generated review flags. |
| `out_of_scope` | string array | Operations v0.3 explicitly does not perform. |
| `safety` | object | Machine-readable proof of the planning-only execution contract. |

Unknown top-level fields, missing fields, invalid field types, an invalid
journey, or a mismatched checksum fail validation.

## Shared Requirements

Every blueprint has these `requirements` fields:

| Field | Type | Unknown representation |
| --- | --- | --- |
| `architect_location` | string | `"unknown"` |
| `runtime_location` | string | `"unknown"` |
| `data_location` | string | `"unknown"` |
| `allowed_document_sources` | string array | empty array |
| `user_count` | integer or null | `null` |
| `model_preference` | string | `"unknown"` |
| `runtime_preference` | string | `"unknown"` |
| `hardware_availability` | string | `"unknown"` |
| `network_exposure` | string | `"unknown"` |
| `compliance_concerns` | string array | empty array or `["unknown"]` |
| `authentication_rbac_needs` | string | `"unknown"` |
| `audit_logging_needs` | string | `"unknown"` |
| `data_owner_approval` | string | `"unknown"` or `"pending"` |

`architect_location` records where the planning CLI runs:

- `developer-workstation`
- `admin-workstation`
- `bastion-host`
- `ci-runner`
- `target-machine`
- `unknown`

`runtime_location` records where the future model, index, retrieval process,
and related storage are intended to run:

- `same-machine`
- `local-gpu-workstation`
- `company-gpu-server`
- `dgx-spark`
- `dgx-server`
- `cloud-gpu`
- `mac-cluster`
- `hybrid`
- `unknown`

`data_location` is the approved data-residency statement for storage and
processing. It is free text because real policies may identify a site,
jurisdiction, company environment, or separately reviewed hybrid boundary.

Allowed network values are `localhost`, `private-network`, `vpn-only`,
`public`, and `unknown`. Data owner approval is `approved`, `pending`, or
`unknown`.

Use `"none"` for compliance only after an accountable reviewer has confirmed
that no listed framework applies. `"unknown"` remains unresolved.

## Control Machine, Runtime, And Data

These locations are deliberately separate:

```text
developer or admin machine
  -> runs private-ai architect
  -> produces blueprint and review documents

approved target machine
  -> may run ingestion, index, model, and retrieval in a later milestone

approved data residency
  -> determines where ingestion, indexing, models, and storage may operate
```

Running the architect on a laptop does not authorize copying company documents
to that laptop. Ingestion and indexing must run where the data owner permits
the data to exist. v0.3 only records this plan; it does not connect to or
install anything on the target.

## Journey Details

`local-rag` has an empty `journey_details` object. It never receives cloud
provider, cloud workload, or rollback fields.

`private-gpu` has:

```json
{
  "deployment_stage": "pilot",
  "target_hardware": "DGX Spark planning input"
}
```

These are unverified planning inputs. v0.3 does not configure or verify DGX or
other GPU hardware.

`cloud-migration` has:

```json
{
  "rollback_requirement": "define rollback before implementation",
  "source_provider": "user-provided provider name",
  "source_workload": "user-provided workload description"
}
```

These values come only from the operator. v0.3 does not authenticate to a
provider, discover resources, inspect workloads, or perform migration.

Providing journey-specific fields for the wrong journey is rejected.

## Safety Object

Every valid v0.3 blueprint must contain:

```json
{
  "data_ingested": false,
  "discovery_performed": false,
  "infrastructure_changes": false,
  "planning_only": true,
  "secrets_collected": false
}
```

Changing any of these values fails validation. The required `out_of_scope`
list also preserves the no-deployment, no-discovery, no-hardware-configuration,
no-network-mutation, no-secret, and no-production-migration boundaries.

## Warnings

Schema validation can pass while producing warnings. Warnings identify review
work; they are not approvals.

The validator flags:

- public exposure
- missing or pending data owner approval
- unknown model choice
- unknown runtime choice
- unknown architect CLI or target runtime location
- private GPU or DGX inputs as planning-only
- cloud GPU targets as planning-only and subject to explicit data approval
- cloud migration inputs as planning-only and not discovered

Invalid schema structure fails validation. Unresolved planning decisions remain
valid data because recording uncertainty is safer than inventing an answer.

## Checksum And Determinism

The checksum uses canonical sorted JSON without `blueprint_checksum`.
Generating the same answers with the same package version produces the same
blueprint and review documents. Editing any normalized blueprint content
invalidates the checksum.

Regenerate the pack after changing answers. Do not manually replace the
checksum to make an unreviewed edit appear generated.

## Answers Files

Answers files are flat JSON objects using the field names documented above and
the journey-specific names. Examples are under `examples/architect/`.

Command-line flags override matching answers-file values. `--answers-file`
automatically disables prompts. `--non-interactive` can be used with flags
alone.

Do not put passwords, API keys, tokens, credentials, private keys, or secret
values in an answers file. Secret-bearing field names and unsupported fields
are rejected. The blueprint is intended to be reviewable and safe to commit
only when its planning labels are not confidential.

## Versioning Rule

Additive or breaking contract changes require a documented schema-version
decision. Readers must reject unsupported versions rather than guess how to
interpret them.
