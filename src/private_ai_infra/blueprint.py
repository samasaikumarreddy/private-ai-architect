from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from . import __version__


BLUEPRINT_SCHEMA_VERSION = "1.0"
ARCHITECT_JOURNEYS = ("local-rag", "private-gpu", "cloud-migration")
NETWORK_EXPOSURES = ("localhost", "private-network", "vpn-only", "public", "unknown")
DATA_OWNER_APPROVALS = ("approved", "pending", "unknown")
DEPLOYMENT_STAGES = ("pilot", "shared-internal", "production", "unknown")

ANSWER_FIELDS = frozenset(
    {
        "journey",
        "project_name",
        "owner_name",
        "data_location",
        "allowed_document_sources",
        "user_count",
        "model_preference",
        "runtime_preference",
        "hardware_availability",
        "network_exposure",
        "compliance_concerns",
        "authentication_rbac_needs",
        "audit_logging_needs",
        "data_owner_approval",
        "target_hardware",
        "deployment_stage",
        "source_provider",
        "source_workload",
        "rollback_requirement",
    }
)

OUT_OF_SCOPE_ITEMS = (
    "hardware configuration, including DGX",
    "cloud provider discovery or API access",
    "infrastructure deployment or mutation",
    "VPN and firewall changes",
    "Kubernetes and Terraform generation or apply",
    "SSO and LDAP integration",
    "production migration, traffic cutover, or rollback automation",
    "company data ingestion",
    "secret collection or storage",
)

REQUIRED_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "blueprint_checksum",
        "provenance",
        "project",
        "journey",
        "requirements",
        "journey_details",
        "unresolved_decisions",
        "known_risks",
        "out_of_scope",
        "safety",
    }
)

REQUIRED_REQUIREMENT_KEYS = frozenset(
    {
        "data_location",
        "allowed_document_sources",
        "user_count",
        "model_preference",
        "runtime_preference",
        "hardware_availability",
        "network_exposure",
        "compliance_concerns",
        "authentication_rbac_needs",
        "audit_logging_needs",
        "data_owner_approval",
    }
)

JOURNEY_DETAIL_KEYS = {
    "local-rag": frozenset(),
    "private-gpu": frozenset({"target_hardware", "deployment_stage"}),
    "cloud-migration": frozenset({"source_provider", "source_workload", "rollback_requirement"}),
}

_SECRET_FIELD_TERMS = (
    "password",
    "secret",
    "token",
    "credential",
    "private_key",
    "api_key",
)


@dataclass(frozen=True)
class ArchitectAnswers:
    journey: str
    project_name: str
    owner_name: str
    data_location: str
    allowed_document_sources: tuple[str, ...]
    user_count: int | None
    model_preference: str
    runtime_preference: str
    hardware_availability: str
    network_exposure: str
    compliance_concerns: tuple[str, ...]
    authentication_rbac_needs: str
    audit_logging_needs: str
    data_owner_approval: str
    target_hardware: str = "unknown"
    deployment_stage: str = "unknown"
    source_provider: str = "unknown"
    source_workload: str = "unknown"
    rollback_requirement: str = "unknown"


@dataclass(frozen=True)
class BlueprintValidationResult:
    path: Path | None
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_text(self) -> str:
        location = str(self.path) if self.path is not None else "in-memory blueprint"
        lines = [
            f"Blueprint validation: {location}",
            f"Status: {'PASS' if self.ok else 'FAIL'}",
            "",
            "Errors:",
        ]
        lines.extend(f"- {item}" for item in self.errors) if self.errors else lines.append("- None")
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in self.warnings) if self.warnings else lines.append("- None")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        location = str(self.path) if self.path is not None else "in-memory blueprint"
        errors = "\n".join(f"- {item}" for item in self.errors) or "- None"
        warnings = "\n".join(f"- {item}" for item in self.warnings) or "- None"
        return f"""# Blueprint Validation

Blueprint: `{location}`

Status: **{'PASS' if self.ok else 'FAIL'}**

## Errors

{errors}

## Warnings

{warnings}
"""


def normalize_journey(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("journey must be a string")
    normalized = _normalize_text(value).lower().replace("_", "-").replace(" ", "-")
    if normalized not in ARCHITECT_JOURNEYS:
        allowed = ", ".join(ARCHITECT_JOURNEYS)
        raise ValueError(f"invalid journey '{value}'. Allowed journeys: {allowed}")
    return normalized


def load_answers_file(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.exists():
        raise ValueError(f"answers file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"answers path is not a file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"answers file is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("answers file must contain one JSON object")
    _reject_secret_fields(payload)
    return payload


def architect_answers_from_mapping(values: Mapping[str, Any]) -> ArchitectAnswers:
    _reject_secret_fields(values)
    unknown_fields = set(values) - ANSWER_FIELDS
    if unknown_fields:
        names = ", ".join(sorted(unknown_fields))
        raise ValueError(f"unsupported architect answer fields: {names}")

    journey = normalize_journey(values.get("journey") or "")
    project_name = _normalize_text(values.get("project_name"), default="private-ai-plan")
    owner_name = _normalize_text(values.get("owner_name"), default="unknown")
    data_location = _normalize_text(values.get("data_location"), default="unknown")
    allowed_document_sources = _normalize_list(values.get("allowed_document_sources"))
    user_count = _normalize_user_count(values.get("user_count"))
    model_preference = _normalize_text(values.get("model_preference"), default="unknown")
    runtime_preference = _normalize_text(values.get("runtime_preference"), default="unknown")
    hardware_availability = _normalize_text(values.get("hardware_availability"), default="unknown")
    network_exposure = _normalize_choice(
        values.get("network_exposure"),
        allowed=NETWORK_EXPOSURES,
        default="unknown",
        field="network_exposure",
    )
    compliance_concerns = _normalize_list(values.get("compliance_concerns"))
    authentication_rbac_needs = _normalize_text(
        values.get("authentication_rbac_needs"),
        default="unknown",
    )
    audit_logging_needs = _normalize_text(values.get("audit_logging_needs"), default="unknown")
    data_owner_approval = _normalize_choice(
        values.get("data_owner_approval"),
        allowed=DATA_OWNER_APPROVALS,
        default="unknown",
        field="data_owner_approval",
    )

    target_hardware = _normalize_text(values.get("target_hardware"), default="unknown")
    deployment_stage = _normalize_choice(
        values.get("deployment_stage"),
        allowed=DEPLOYMENT_STAGES,
        default="unknown",
        field="deployment_stage",
    )
    source_provider = _normalize_text(values.get("source_provider"), default="unknown")
    source_workload = _normalize_text(values.get("source_workload"), default="unknown")
    rollback_requirement = _normalize_text(values.get("rollback_requirement"), default="unknown")

    if journey != "private-gpu" and (
        "target_hardware" in values or "deployment_stage" in values
    ):
        raise ValueError("target_hardware and deployment_stage are only valid for private-gpu")
    if journey != "cloud-migration" and (
        "source_provider" in values
        or "source_workload" in values
        or "rollback_requirement" in values
    ):
        raise ValueError(
            "source_provider, source_workload, and rollback_requirement are only valid "
            "for cloud-migration"
        )

    return ArchitectAnswers(
        journey=journey,
        project_name=project_name,
        owner_name=owner_name,
        data_location=data_location,
        allowed_document_sources=allowed_document_sources,
        user_count=user_count,
        model_preference=model_preference,
        runtime_preference=runtime_preference,
        hardware_availability=hardware_availability,
        network_exposure=network_exposure,
        compliance_concerns=compliance_concerns,
        authentication_rbac_needs=authentication_rbac_needs,
        audit_logging_needs=audit_logging_needs,
        data_owner_approval=data_owner_approval,
        target_hardware=target_hardware,
        deployment_stage=deployment_stage,
        source_provider=source_provider,
        source_workload=source_workload,
        rollback_requirement=rollback_requirement,
    )


def build_blueprint(answers: ArchitectAnswers) -> dict[str, Any]:
    requirements = {
        "data_location": answers.data_location,
        "allowed_document_sources": list(answers.allowed_document_sources),
        "user_count": answers.user_count,
        "model_preference": answers.model_preference,
        "runtime_preference": answers.runtime_preference,
        "hardware_availability": answers.hardware_availability,
        "network_exposure": answers.network_exposure,
        "compliance_concerns": list(answers.compliance_concerns),
        "authentication_rbac_needs": answers.authentication_rbac_needs,
        "audit_logging_needs": answers.audit_logging_needs,
        "data_owner_approval": answers.data_owner_approval,
    }
    if answers.journey == "local-rag":
        journey_details: dict[str, Any] = {}
    elif answers.journey == "private-gpu":
        journey_details = {
            "target_hardware": answers.target_hardware,
            "deployment_stage": answers.deployment_stage,
        }
    else:
        journey_details = {
            "source_provider": answers.source_provider,
            "source_workload": answers.source_workload,
            "rollback_requirement": answers.rollback_requirement,
        }

    blueprint: dict[str, Any] = {
        "schema_version": BLUEPRINT_SCHEMA_VERSION,
        "provenance": {
            "generator": "private-ai architect",
            "generator_version": __version__,
        },
        "project": {
            "name": answers.project_name,
            "owner_name": answers.owner_name,
        },
        "journey": answers.journey,
        "requirements": requirements,
        "journey_details": journey_details,
        "unresolved_decisions": list(_unresolved_decisions(answers)),
        "known_risks": list(_known_risks(answers)),
        "out_of_scope": list(OUT_OF_SCOPE_ITEMS),
        "safety": {
            "planning_only": True,
            "infrastructure_changes": False,
            "discovery_performed": False,
            "data_ingested": False,
            "secrets_collected": False,
        },
    }
    blueprint["blueprint_checksum"] = calculate_blueprint_checksum(blueprint)
    return blueprint


def calculate_blueprint_checksum(blueprint: Mapping[str, Any]) -> str:
    content = {key: value for key, value in blueprint.items() if key != "blueprint_checksum"}
    serialized = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def load_blueprint(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if path.is_dir():
        path = path / "blueprint.json"
    if not path.exists():
        raise ValueError(f"blueprint does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"blueprint is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("blueprint must contain one JSON object")
    return payload


def validate_blueprint(
    blueprint: Mapping[str, Any],
    *,
    path: Path | None = None,
) -> BlueprintValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    actual_keys = set(blueprint)
    missing_keys = REQUIRED_TOP_LEVEL_KEYS - actual_keys
    extra_keys = actual_keys - REQUIRED_TOP_LEVEL_KEYS
    errors.extend(f"Missing required blueprint field: {key}" for key in sorted(missing_keys))
    errors.extend(f"Unsupported top-level blueprint field: {key}" for key in sorted(extra_keys))

    if blueprint.get("schema_version") != BLUEPRINT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {BLUEPRINT_SCHEMA_VERSION}")

    journey = blueprint.get("journey")
    if journey not in ARCHITECT_JOURNEYS:
        errors.append(f"journey must be one of: {', '.join(ARCHITECT_JOURNEYS)}")

    _validate_object_keys(
        blueprint.get("project"),
        {"name", "owner_name"},
        "project",
        errors,
    )
    project = blueprint.get("project")
    if isinstance(project, dict):
        _validate_non_empty_strings(project, ("name", "owner_name"), "project", errors)
    requirements = blueprint.get("requirements")
    _validate_object_keys(requirements, REQUIRED_REQUIREMENT_KEYS, "requirements", errors)

    if journey in JOURNEY_DETAIL_KEYS:
        journey_details = blueprint.get("journey_details")
        _validate_object_keys(
            journey_details,
            JOURNEY_DETAIL_KEYS[journey],
            "journey_details",
            errors,
        )
        if isinstance(journey_details, dict):
            _validate_non_empty_strings(
                journey_details,
                tuple(sorted(JOURNEY_DETAIL_KEYS[journey])),
                "journey_details",
                errors,
            )
    elif not isinstance(blueprint.get("journey_details"), dict):
        errors.append("journey_details must be an object")

    for field in ("unresolved_decisions", "known_risks", "out_of_scope"):
        if not _is_string_list(blueprint.get(field)):
            errors.append(f"{field} must be a list of strings")

    safety = blueprint.get("safety")
    required_safety = {
        "planning_only": True,
        "infrastructure_changes": False,
        "discovery_performed": False,
        "data_ingested": False,
        "secrets_collected": False,
    }
    _validate_object_keys(safety, set(required_safety), "safety", errors)
    if isinstance(safety, dict):
        for key, expected in required_safety.items():
            if safety.get(key) is not expected:
                errors.append(f"safety.{key} must be {str(expected).lower()}")

    provenance = blueprint.get("provenance")
    _validate_object_keys(
        provenance,
        {"generator", "generator_version"},
        "provenance",
        errors,
    )
    if isinstance(provenance, dict):
        _validate_non_empty_strings(
            provenance,
            ("generator", "generator_version"),
            "provenance",
            errors,
        )

    out_of_scope = blueprint.get("out_of_scope")
    if isinstance(out_of_scope, list):
        for item in OUT_OF_SCOPE_ITEMS:
            if item not in out_of_scope:
                errors.append(f"out_of_scope is missing required safety boundary: {item}")

    checksum = blueprint.get("blueprint_checksum")
    if not isinstance(checksum, str) or checksum != calculate_blueprint_checksum(blueprint):
        errors.append("blueprint_checksum does not match the normalized blueprint content")

    if isinstance(requirements, dict):
        _validate_requirements(requirements, errors, warnings)

    if journey == "private-gpu":
        target = ""
        details = blueprint.get("journey_details")
        if isinstance(details, dict):
            target = str(details.get("target_hardware", ""))
        if "dgx" in target.lower():
            warnings.append("DGX is recorded as planning-only; no DGX configuration was generated.")
        else:
            warnings.append("Private GPU hardware is planning-only; compatibility is not verified.")
    elif journey == "cloud-migration":
        warnings.append("Cloud migration is planning-only; no provider API or discovery was called.")

    return BlueprintValidationResult(
        path=path,
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _unresolved_decisions(answers: ArchitectAnswers) -> tuple[str, ...]:
    decisions: list[str] = []
    checks = (
        (answers.owner_name == "unknown", "Name the company or accountable owner."),
        (answers.data_location == "unknown", "Decide where approved data may be stored and processed."),
        (not answers.allowed_document_sources, "Approve the document sources that may be used."),
        (answers.user_count is None, "Estimate the number of users."),
        (answers.model_preference == "unknown", "Select or evaluate a model."),
        (answers.runtime_preference == "unknown", "Select or evaluate a model runtime."),
        (answers.hardware_availability == "unknown", "Confirm available hardware and capacity."),
        (answers.network_exposure == "unknown", "Decide the allowed network exposure."),
        (
            _compliance_is_unknown(answers.compliance_concerns),
            "Confirm applicable compliance requirements or record none.",
        ),
        (
            answers.authentication_rbac_needs == "unknown",
            "Define authentication and RBAC requirements.",
        ),
        (answers.audit_logging_needs == "unknown", "Define audit and logging requirements."),
        (
            answers.data_owner_approval != "approved",
            "Obtain explicit data owner approval for every allowed document source.",
        ),
    )
    decisions.extend(text for condition, text in checks if condition)

    if answers.journey == "private-gpu":
        if answers.target_hardware == "unknown":
            decisions.append("Identify the private GPU hardware target.")
        if answers.deployment_stage == "unknown":
            decisions.append("Decide whether the target is a pilot, shared service, or production.")
    elif answers.journey == "cloud-migration":
        if answers.source_provider == "unknown":
            decisions.append("Identify the source cloud provider.")
        if answers.source_workload == "unknown":
            decisions.append("Define the exact source AI workload in scope.")
        if answers.rollback_requirement == "unknown":
            decisions.append("Define rollback requirements before migration planning.")

    return tuple(decisions)


def _known_risks(answers: ArchitectAnswers) -> tuple[str, ...]:
    risks: list[str] = []
    if answers.network_exposure == "public":
        risks.append("Public exposure can reveal private AI services and requires formal network review.")
    if answers.data_owner_approval != "approved":
        risks.append("Document sources lack recorded data owner approval.")
    if answers.model_preference == "unknown" or answers.runtime_preference == "unknown":
        risks.append("Unknown model or runtime choices prevent compatibility and capacity validation.")
    if answers.authentication_rbac_needs == "unknown":
        risks.append("Undefined authentication or RBAC can allow unauthorized retrieval.")
    if answers.audit_logging_needs == "unknown":
        risks.append("Undefined audit requirements can leave access and changes untraceable.")
    if _compliance_is_unknown(answers.compliance_concerns):
        risks.append("Compliance applicability has not been confirmed.")
    if answers.journey == "private-gpu":
        risks.append("Private GPU and DGX choices are unverified planning inputs only.")
    if answers.journey == "cloud-migration":
        risks.append("Cloud workload details are user-provided and were not discovered or verified.")
        risks.append("No migration, cutover, or rollback action is implemented.")
    return tuple(risks)


def _validate_requirements(
    requirements: Mapping[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    if not _is_string_list(requirements.get("allowed_document_sources")):
        errors.append("requirements.allowed_document_sources must be a list of strings")
    if not _is_string_list(requirements.get("compliance_concerns")):
        errors.append("requirements.compliance_concerns must be a list of strings")
    _validate_non_empty_strings(
        requirements,
        (
            "data_location",
            "model_preference",
            "runtime_preference",
            "hardware_availability",
            "network_exposure",
            "authentication_rbac_needs",
            "audit_logging_needs",
            "data_owner_approval",
        ),
        "requirements",
        errors,
    )
    user_count = requirements.get("user_count")
    if user_count is not None and (not isinstance(user_count, int) or isinstance(user_count, bool) or user_count < 1):
        errors.append("requirements.user_count must be null or a positive integer")
    if requirements.get("network_exposure") not in NETWORK_EXPOSURES:
        errors.append(f"requirements.network_exposure must be one of: {', '.join(NETWORK_EXPOSURES)}")
    if requirements.get("data_owner_approval") not in DATA_OWNER_APPROVALS:
        errors.append(
            "requirements.data_owner_approval must be one of: "
            f"{', '.join(DATA_OWNER_APPROVALS)}"
        )

    if requirements.get("network_exposure") == "public":
        warnings.append("Public network exposure requires formal security and network approval.")
    if requirements.get("data_owner_approval") != "approved":
        warnings.append("Data owner approval is missing or pending.")
    if requirements.get("model_preference") == "unknown":
        warnings.append("Model preference is unresolved.")
    if requirements.get("runtime_preference") == "unknown":
        warnings.append("Runtime preference is unresolved.")


def _validate_object_keys(
    value: Any,
    expected_keys: set[str] | frozenset[str],
    field: str,
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return
    actual = set(value)
    for key in sorted(expected_keys - actual):
        errors.append(f"Missing required {field} field: {key}")
    for key in sorted(actual - expected_keys):
        errors.append(f"Unsupported {field} field: {key}")


def _validate_non_empty_strings(
    values: Mapping[str, Any],
    fields: tuple[str, ...],
    prefix: str,
    errors: list[str],
) -> None:
    for field in fields:
        value = values.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.{field} must be a non-empty string")


def _normalize_text(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError("text answers must be strings")
    normalized = " ".join(value.strip().split())
    return normalized or default


def _normalize_list(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raw_values = value.split(",")
    elif isinstance(value, (list, tuple)):
        raw_values = value
    else:
        raise ValueError("list answers must be JSON arrays or comma-separated strings")
    if not all(isinstance(item, str) for item in raw_values):
        raise ValueError("list answers must contain only strings")
    normalized = [_normalize_text(item) for item in raw_values]
    return tuple(dict.fromkeys(item for item in normalized if item))


def _normalize_user_count(value: Any) -> int | None:
    if value in (None, "", "unknown"):
        return None
    if isinstance(value, bool):
        raise ValueError("user_count must be a positive integer or unknown")
    try:
        count = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("user_count must be a positive integer or unknown") from exc
    if count < 1:
        raise ValueError("user_count must be a positive integer or unknown")
    return count


def _normalize_choice(
    value: Any,
    *,
    allowed: tuple[str, ...],
    default: str,
    field: str,
) -> str:
    normalized = _normalize_text(value, default=default).lower().replace("_", "-").replace(" ", "-")
    if normalized not in allowed:
        raise ValueError(f"{field} must be one of: {', '.join(allowed)}")
    return normalized


def _reject_secret_fields(values: Mapping[str, Any]) -> None:
    for key, value in values.items():
        normalized = str(key).strip().lower().replace("-", "_")
        if any(term in normalized for term in _SECRET_FIELD_TERMS):
            raise ValueError("architect answers must not contain secret-bearing fields")
        if isinstance(value, dict):
            _reject_secret_fields(value)


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _compliance_is_unknown(values: tuple[str, ...]) -> bool:
    return not values or all(value.strip().lower() == "unknown" for value in values)
