from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .blueprint import (
    ArchitectAnswers,
    BlueprintValidationResult,
    build_blueprint,
    validate_blueprint,
)


ARCHITECT_OUTPUT_FILES = (
    "blueprint.json",
    "summary.md",
    "decisions-needed.md",
    "security-risks.md",
    "next-steps.md",
    "validation-report.md",
)


@dataclass(frozen=True)
class ArchitectGenerationResult:
    output_dir: Path
    generated_files: tuple[str, ...]
    validation: BlueprintValidationResult


def generate_architect_pack(
    output_dir: Path,
    answers: ArchitectAnswers,
    *,
    force: bool = False,
) -> ArchitectGenerationResult:
    output_dir = output_dir.resolve()
    targets = {name: output_dir / name for name in ARCHITECT_OUTPUT_FILES}
    existing = [path for path in targets.values() if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"architect output already exists: {names}. Use --force to overwrite generated files."
        )

    blueprint = build_blueprint(answers)
    validation = validate_blueprint(blueprint, path=Path("blueprint.json"))
    if not validation.ok:
        raise ValueError("generated blueprint failed internal schema validation")

    contents = {
        "blueprint.json": json.dumps(blueprint, indent=2, sort_keys=True) + "\n",
        "summary.md": _summary(blueprint),
        "decisions-needed.md": _decisions_needed(blueprint),
        "security-risks.md": _security_risks(blueprint),
        "next-steps.md": _next_steps(blueprint),
        "validation-report.md": validation.to_markdown(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in contents.items():
        targets[filename].write_text(content, encoding="utf-8")

    return ArchitectGenerationResult(
        output_dir=output_dir,
        generated_files=ARCHITECT_OUTPUT_FILES,
        validation=validation,
    )


def _summary(blueprint: dict[str, Any]) -> str:
    project = blueprint["project"]
    requirements = blueprint["requirements"]
    details = blueprint["journey_details"]
    detail_rows = "\n".join(
        f"| {_label(key)} | {_inline(value)} |" for key, value in details.items()
    )
    if detail_rows:
        detail_section = f"""## Journey Details

| Requirement | Recorded answer |
| --- | --- |
{detail_rows}

"""
    else:
        detail_section = ""

    sources = _bullets(requirements["allowed_document_sources"], empty="None approved yet.")
    compliance = _bullets(requirements["compliance_concerns"], empty="Not confirmed.")
    return f"""# Guided Architecture Summary

> Planning only: this review pack did not deploy, discover, configure, migrate,
> ingest data, collect secrets, or change infrastructure.

## Project

- Project: {_inline(project["name"])}
- Company or owner: {_inline(project["owner_name"])}
- Journey: `{blueprint["journey"]}`
- Schema: `{blueprint["schema_version"]}`
- Checksum: `{blueprint["blueprint_checksum"]}`

## Normalized Requirements

| Requirement | Recorded answer |
| --- | --- |
| Architect CLI location | {_inline(requirements["architect_location"])} |
| Target runtime location | {_inline(requirements["runtime_location"])} |
| Data residency | {_inline(requirements["data_location"])} |
| User count | {_inline(requirements["user_count"])} |
| Model preference | {_inline(requirements["model_preference"])} |
| Runtime preference | {_inline(requirements["runtime_preference"])} |
| Hardware availability | {_inline(requirements["hardware_availability"])} |
| Network exposure | {_inline(requirements["network_exposure"])} |
| Authentication / RBAC | {_inline(requirements["authentication_rbac_needs"])} |
| Audit / logging | {_inline(requirements["audit_logging_needs"])} |
| Data owner approval | {_inline(requirements["data_owner_approval"])} |

### Allowed Document Sources

{sources}

### Compliance Concerns

{compliance}

{detail_section}## Safety Record

- Planning only: yes
- Infrastructure changes: none
- Cloud discovery: none
- Data ingestion: none
- Secrets collected: none

## Placement Rule

Ingestion, indexing, models, and vector storage must run only where the data is
approved to exist. Running the architect CLI on a developer or admin machine
does not authorize copying company data to that machine.
"""


def _decisions_needed(blueprint: dict[str, Any]) -> str:
    decisions = _bullets(blueprint["unresolved_decisions"], empty="No unresolved decisions recorded.")
    return f"""# Decisions Needed

These decisions must be resolved by accountable humans before implementation
or production approval.

{decisions}

## Approval Rule

Updating this document alone does not approve a decision. Record the answer in
a new blueprint revision, validate it, and obtain the required owner review.
"""


def _security_risks(blueprint: dict[str, Any]) -> str:
    risks = _bullets(blueprint["known_risks"], empty="No generated risks. Human review is still required.")
    out_of_scope = _bullets(blueprint["out_of_scope"])
    return f"""# Security Risks

## Generated Risk Flags

{risks}

## Enforced Planning Boundaries

{out_of_scope}

## Human Review

The flags are deterministic checks, not a security certification. Security,
data, network, legal, and operational owners must review the blueprint before
any separately approved implementation work.
"""


def _next_steps(blueprint: dict[str, Any]) -> str:
    journey = blueprint["journey"]
    common = [
        "Resolve every item in `decisions-needed.md`.",
        "Confirm data owner approval for each named document source.",
        "Confirm that runtime and ingestion placement follows the recorded data residency.",
        "Review public or remote exposure with security and network owners.",
        "Regenerate the pack and validate the new `blueprint.json` checksum.",
    ]
    if journey == "local-rag":
        journey_steps = [
            "Use the existing v0.2 local RAG commands only with separately approved sample or local data.",
            "Evaluate retrieval, refusal, and citation behavior before expanding sources.",
        ]
    elif journey == "private-gpu":
        journey_steps = [
            "Inventory hardware manually without changing it.",
            "Wait for a verified hardware-profile milestone before treating compatibility as proven.",
            "Do not interpret this pack as DGX or GPU configuration.",
        ]
    else:
        journey_steps = [
            "Have the workload owner document the exact source workload and rollback expectations.",
            "Do not provide cloud credentials; this release performs no discovery.",
            "Wait for a reviewed provider-specific milestone before attempting migration.",
        ]
    steps = "\n".join(
        f"{index}. {item}" for index, item in enumerate((*common, *journey_steps), start=1)
    )
    return f"""# Next Steps

{steps}

## Stop Condition

Do not deploy, discover, configure hardware, mutate networks, or migrate
production traffic from this blueprint. v0.3 generates planning evidence only.
"""


def _label(value: str) -> str:
    return value.replace("_", " ").title()


def _inline(value: Any) -> str:
    if value is None:
        rendered = "unknown"
    else:
        rendered = str(value)
    return f"`{rendered.replace('`', '')}`"


def _bullets(values: list[str], *, empty: str = "None.") -> str:
    if not values:
        return f"- {empty}"
    return "\n".join(f"- {_inline(value)}" for value in values)
