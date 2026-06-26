from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


VALIDATION_INPUT_FILES = (
    "architecture-plan.md",
    "stakeholder-checklist.md",
    "network-requirements.md",
    "security-review.md",
    "proposed-docker-compose.yml",
    "proposed-rbac.yaml",
    "proposed-env.example",
    "data-source-plan.md",
    "model-plan.md",
)


REQUIRED_DRY_RUN_FILES = (
    *VALIDATION_INPUT_FILES,
    "validation-report.md",
)


@dataclass(frozen=True)
class ValidationResult:
    path: Path
    checked_files: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_text(self) -> str:
        lines = [
            f"Validation path: {self.path}",
            f"Status: {'PASS' if self.ok else 'FAIL'}",
            "",
            "Checked files:",
        ]
        lines.extend(f"- {name}" for name in self.checked_files)
        lines.append("")
        lines.append("Errors:")
        lines.extend(f"- {item}" for item in self.errors) if self.errors else lines.append("- None")
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in self.warnings) if self.warnings else lines.append("- None")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        return f"""# Validation Report

Validation path: `{self.path}`

Status: **{'PASS' if self.ok else 'FAIL'}**

## Checked Files

{_bullet_list(self.checked_files) if self.checked_files else '- None'}

## Errors

{_bullet_list(self.errors) if self.errors else '- None'}

## Warnings

{_bullet_list(self.warnings) if self.warnings else '- None'}
"""


def validate_dry_run(path: Path) -> ValidationResult:
    path = path.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked_files: list[str] = []

    if not path.exists():
        return ValidationResult(
            path=path,
            errors=(f"Path does not exist: {path}",),
        )
    if not path.is_dir():
        return ValidationResult(
            path=path,
            errors=(f"Path is not a directory: {path}",),
        )

    for filename in VALIDATION_INPUT_FILES:
        file_path = path / filename
        if file_path.exists():
            checked_files.append(filename)
        else:
            errors.append(f"Missing required dry-run file: {filename}")

    if (path / "validation-report.md").exists():
        checked_files.append("validation-report.md")

    env_path = path / "proposed-env.example"
    if env_path.exists():
        env = _parse_env(env_path.read_text(encoding="utf-8"))
        bind_host = env.get("PRIVATE_AI_BIND_HOST")
        if bind_host in {"0.0.0.0", "::"}:
            errors.append("API/UI bind host is public. Use 127.0.0.1 unless network review is complete.")
        if env.get("AUDIT_LOGGING_REQUIRED", "").lower() != "true":
            errors.append("AUDIT_LOGGING_REQUIRED must be true for generated deployment plans.")
        if env.get("LLM_MODEL") in {"", None, "change-me"}:
            warnings.append("LLM_MODEL is not selected.")
        if "change-me-before-apply" in env.get("AUDIT_DB_URL", ""):
            warnings.append("Audit database password placeholder must be changed before apply.")

    rbac_path = path / "proposed-rbac.yaml"
    if rbac_path.exists():
        rbac_text = rbac_path.read_text(encoding="utf-8")
        if "roles:" not in rbac_text:
            errors.append("proposed-rbac.yaml must define roles.")
        if "requires_explicit_assignment: true" not in rbac_text:
            errors.append("admin role must require explicit assignment.")
        if 'collections:\n      - "*"' not in rbac_text:
            warnings.append("admin wildcard collection access was not found; verify admin scope manually.")

    data_path = path / "data-source-plan.md"
    if data_path.exists():
        data_text = data_path.read_text(encoding="utf-8")
        for pattern in ("**/.env", "**/*.pem", "**/*.key", "**/credentials*", "**/secrets*"):
            if pattern not in data_text:
                errors.append(f"data-source-plan.md missing denied pattern: {pattern}")

    network_path = path / "network-requirements.md"
    if network_path.exists():
        network_text = network_path.read_text(encoding="utf-8").lower()
        if "do not expose the model runtime directly" not in network_text:
            errors.append("network-requirements.md must block direct model runtime exposure.")

    compose_path = path / "proposed-docker-compose.yml"
    if compose_path.exists():
        compose_text = compose_path.read_text(encoding="utf-8")
        if "127.0.0.1:8080:8080" not in compose_text:
            errors.append("proposed Docker Compose must bind API to localhost by default.")
        if "127.0.0.1:8501:8501" not in compose_text:
            errors.append("proposed Docker Compose must bind UI to localhost by default.")
        if "x-private-ai-dry-run:" not in compose_text:
            warnings.append("proposed Docker Compose is missing dry-run metadata.")

    security_path = path / "security-review.md"
    if security_path.exists():
        security_text = security_path.read_text(encoding="utf-8")
        if "No direct public exposure of model runtimes" not in security_text:
            errors.append("security-review.md must include model runtime exposure control.")
        if "private keys" not in security_text:
            warnings.append("security-review.md should mention private-key exclusion.")

    return ValidationResult(
        path=path,
        checked_files=tuple(checked_files),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _parse_env(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _bullet_list(values: tuple[str, ...]) -> str:
    return "\n".join(f"- {value}" for value in values)
