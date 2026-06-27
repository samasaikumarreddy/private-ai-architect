from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .architect import generate_architect_pack
from .blueprint import (
    ARCHITECT_LOCATIONS,
    ARCHITECT_JOURNEYS,
    DATA_OWNER_APPROVALS,
    DEPLOYMENT_STAGES,
    NETWORK_EXPOSURES,
    RUNTIME_LOCATIONS,
    architect_answers_from_mapping,
    load_answers_file,
    load_blueprint,
    validate_blueprint,
)
from .doctor import run_doctor
from .evaluation import evaluate_index
from .generator import generate_dry_run
from .indexer import DEFAULT_MAX_FILE_BYTES, DEFAULT_MAX_FILES, build_index
from .models import DEPLOYMENT_PROFILES, default_answers, normalize_mode
from .ollama import DEFAULT_OLLAMA_URL, OllamaClient, OllamaError, is_refusal
from .retrieval import (
    format_grounded_answer,
    format_insufficient_evidence_refusal,
    format_retrieval_answer,
    has_sufficient_evidence,
    search_index,
)
from .validator import validate_dry_run


def main(argv: list[str] | None = None) -> int:
    _configure_output_stream(sys.stdout)
    _configure_output_stream(sys.stderr)
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    try:
        return args.handler(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _configure_output_stream(stream: object) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(errors="replace")
    except (OSError, ValueError):
        pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="private-ai",
        description="Plan private AI systems with guided, non-mutating workflows.",
    )
    parser.add_argument("--version", action="version", version=f"private-ai {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Generate a private AI setup plan.")
    init_parser.add_argument("--dry-run", action="store_true", help="Generate review files without applying changes.")
    init_parser.add_argument(
        "--mode",
        default="local-developer",
        help=f"Deployment mode. Options: {', '.join(sorted(DEPLOYMENT_PROFILES))}",
    )
    init_parser.add_argument("--project-name", default="private-ai-demo", help="Project name for generated files.")
    init_parser.add_argument("--company-name", default="example-company", help="Company or workspace name.")
    init_parser.add_argument(
        "--department",
        action="append",
        dest="departments",
        help="Department in scope. Can be passed multiple times.",
    )
    init_parser.add_argument(
        "--data-source",
        action="append",
        dest="data_sources",
        help="Approved data source path. Can be passed multiple times.",
    )
    init_parser.add_argument(
        "--output-dir",
        default="generated/dry-run",
        help="Directory for generated dry-run artifacts.",
    )
    init_parser.add_argument("--force", action="store_true", help="Overwrite generated dry-run files.")
    init_parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for dry-run answers instead of using defaults and flags.",
    )
    init_parser.set_defaults(handler=handle_init)

    modes_parser = subparsers.add_parser("modes", help="List supported deployment modes.")
    modes_parser.set_defaults(handler=handle_modes)

    validate_parser = subparsers.add_parser("validate", help="Validate generated dry-run artifacts.")
    validate_parser.add_argument("path", nargs="?", default="generated/dry-run", help="Dry-run artifact directory.")
    validate_parser.set_defaults(handler=handle_validate)

    doctor_parser = subparsers.add_parser("doctor", help="Inspect local readiness for future deployment work.")
    doctor_parser.set_defaults(handler=handle_doctor)

    ingest_parser = subparsers.add_parser("ingest", help="Build a local retrieval index from approved files.")
    ingest_parser.add_argument("sources", nargs="+", help="Approved files or directories to index.")
    ingest_parser.add_argument("--collection", default="docs", help="Collection name for indexed chunks.")
    ingest_parser.add_argument("--output-dir", default="generated/index", help="Directory for local index output.")
    ingest_parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Directory, file name, or relative glob to exclude. Can be repeated.",
    )
    ingest_parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=DEFAULT_MAX_FILE_BYTES,
        help=f"Maximum size of an indexed file. Default: {DEFAULT_MAX_FILE_BYTES} bytes.",
    )
    ingest_parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"Maximum number of files in one index. Default: {DEFAULT_MAX_FILES}.",
    )
    ingest_parser.add_argument("--force", action="store_true", help="Overwrite an existing local index.")
    ingest_parser.set_defaults(handler=handle_ingest)

    chat_parser = subparsers.add_parser(
        "chat",
        help="Query a local index with retrieval-only output or an optional installed Ollama model.",
    )
    chat_parser.add_argument("query", nargs="?", help="Question or search query.")
    chat_parser.add_argument("--index", default="generated/index/index.json", help="Path to local JSON index.")
    chat_parser.add_argument("--top-k", type=int, default=3, help="Number of cited excerpts to return.")
    chat_parser.add_argument(
        "--model",
        help="Use this already-installed local Ollama model. Models are never downloaded automatically.",
    )
    chat_parser.add_argument(
        "--ollama-url",
        default=DEFAULT_OLLAMA_URL,
        help="Local loopback Ollama URL. Non-loopback addresses are rejected in v0.2.",
    )
    chat_parser.add_argument(
        "--ollama-timeout",
        type=float,
        default=60.0,
        help="Local Ollama request timeout in seconds.",
    )
    chat_parser.set_defaults(handler=handle_chat)

    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Run repeatable retrieval and refusal cases against a local index.",
    )
    evaluate_parser.add_argument("--index", default="generated/index/index.json", help="Path to local JSON index.")
    evaluate_parser.add_argument(
        "--cases",
        default="examples/evaluation/local-rag-cases.json",
        help="Path to retrieval evaluation cases.",
    )
    evaluate_parser.add_argument("--top-k", type=int, default=3, help="Maximum results considered per case.")
    evaluate_parser.set_defaults(handler=handle_evaluate)

    architect_parser = subparsers.add_parser(
        "architect",
        help="Ask guided questions and generate a normalized planning blueprint.",
    )
    architect_parser.add_argument(
        "--journey",
        help=f"Intended journey: {', '.join(ARCHITECT_JOURNEYS)}.",
    )
    architect_parser.add_argument("--project-name", help="Project name.")
    architect_parser.add_argument("--owner-name", help="Company or accountable owner name.")
    architect_parser.add_argument(
        "--architect-location",
        choices=ARCHITECT_LOCATIONS,
        help="Machine or control environment where this planning CLI runs.",
    )
    architect_parser.add_argument(
        "--runtime-location",
        choices=RUNTIME_LOCATIONS,
        help="Planned location for the future model, index, and retrieval runtime.",
    )
    architect_parser.add_argument(
        "--data-location",
        help="Approved data residency for storage and processing.",
    )
    architect_parser.add_argument(
        "--document-source",
        action="append",
        dest="allowed_document_sources",
        help="Approved document source label or path. Can be repeated; files are not read.",
    )
    architect_parser.add_argument("--user-count", type=int, help="Expected number of users.")
    architect_parser.add_argument("--model-preference", help="Preferred model or 'unknown'.")
    architect_parser.add_argument("--runtime-preference", help="Preferred runtime or 'unknown'.")
    architect_parser.add_argument(
        "--hardware-availability",
        help="Available hardware description or 'unknown'.",
    )
    architect_parser.add_argument(
        "--network-exposure",
        choices=NETWORK_EXPOSURES,
        help="Planned network exposure.",
    )
    architect_parser.add_argument(
        "--compliance",
        action="append",
        dest="compliance_concerns",
        help="Compliance concern such as GDPR, HIPAA, SOX, none, or unknown. Can be repeated.",
    )
    architect_parser.add_argument(
        "--authentication-rbac",
        dest="authentication_rbac_needs",
        help="Authentication and RBAC requirement or 'unknown'.",
    )
    architect_parser.add_argument(
        "--audit-logging",
        dest="audit_logging_needs",
        help="Audit and logging requirement or 'unknown'.",
    )
    architect_parser.add_argument(
        "--data-owner-approval",
        choices=DATA_OWNER_APPROVALS,
        help="Approval status for the named document sources.",
    )
    architect_parser.add_argument(
        "--target-hardware",
        help="Private GPU target description. Valid only for private-gpu.",
    )
    architect_parser.add_argument(
        "--deployment-stage",
        choices=DEPLOYMENT_STAGES,
        help="Pilot, shared-internal, production, or unknown. Valid only for private-gpu.",
    )
    architect_parser.add_argument(
        "--source-provider",
        help="Source provider name. Valid only for cloud-migration planning.",
    )
    architect_parser.add_argument(
        "--source-workload",
        help="Source AI workload description. Valid only for cloud-migration planning.",
    )
    architect_parser.add_argument(
        "--rollback-requirement",
        help="Rollback requirement. Valid only for cloud-migration planning.",
    )
    architect_parser.add_argument(
        "--answers-file",
        help="JSON answers file. Secret-bearing and unsupported fields are rejected.",
    )
    architect_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Do not prompt. Use flags and/or --answers-file.",
    )
    architect_parser.add_argument(
        "--output-dir",
        default="generated/architect",
        help="Directory for blueprint and review documents.",
    )
    architect_parser.add_argument("--force", action="store_true", help="Overwrite generated architect files.")
    architect_parser.set_defaults(handler=handle_architect)

    blueprint_parser = subparsers.add_parser(
        "blueprint",
        help="Inspect or validate a normalized guided-architect blueprint.",
    )
    blueprint_subparsers = blueprint_parser.add_subparsers(dest="blueprint_command")
    blueprint_validate_parser = blueprint_subparsers.add_parser(
        "validate",
        help="Validate blueprint JSON without applying changes.",
    )
    blueprint_validate_parser.add_argument(
        "path",
        nargs="?",
        default="generated/architect/blueprint.json",
        help="Blueprint JSON file or generated architect directory.",
    )
    blueprint_validate_parser.set_defaults(handler=handle_blueprint_validate)

    for command in ("apply", "audit"):
        stub = subparsers.add_parser(command, help=f"{command} is planned but not implemented yet.")
        stub.set_defaults(handler=handle_not_implemented)

    return parser


def handle_init(args: argparse.Namespace) -> int:
    if not args.dry_run:
        print("Only dry-run init is implemented. Use: private-ai init --dry-run")
        return 2

    answers = _prompt_for_answers(args) if args.interactive else _answers_from_args(args)
    output_dir = Path(args.output_dir)
    generated = generate_dry_run(output_dir, answers, force=args.force)

    print(f"Generated dry-run plan: {output_dir}")
    for filename in sorted(generated):
        print(f"- {filename}")
    print("")
    print(f"Next: private-ai validate {output_dir}")
    return 0


def handle_validate(args: argparse.Namespace) -> int:
    result = validate_dry_run(Path(args.path))
    print(result.to_text())
    return 0 if result.ok else 1


def handle_doctor(args: argparse.Namespace) -> int:
    report = run_doctor()
    print(report.to_text())
    return 0


def handle_ingest(args: argparse.Namespace) -> int:
    result = build_index(
        [Path(source) for source in args.sources],
        output_dir=Path(args.output_dir),
        collection=args.collection,
        force=args.force,
        max_file_bytes=args.max_file_bytes,
        max_files=args.max_files,
        exclude_patterns=tuple(args.exclude),
    )
    print(result.to_text())
    print("")
    print(f"Next: private-ai chat \"your question\" --index {result.index_path}")
    return 0


def handle_chat(args: argparse.Namespace) -> int:
    if not args.query:
        print("error: query is required for chat", file=sys.stderr)
        return 2
    if not 1 <= args.top_k <= 10:
        print("error: --top-k must be between 1 and 10", file=sys.stderr)
        return 2
    index_path = Path(args.index)
    if not index_path.exists():
        print(f"error: index does not exist: {index_path}. Run private-ai ingest first.", file=sys.stderr)
        return 2
    matches = search_index(index_path, args.query, top_k=args.top_k)
    if not args.model:
        print(format_retrieval_answer(args.query, matches))
        return 0

    if not has_sufficient_evidence(args.query, matches):
        print(format_insufficient_evidence_refusal(args.query))
        return 0

    try:
        answer = OllamaClient(
            base_url=args.ollama_url,
            timeout=args.ollama_timeout,
        ).generate_grounded_answer(args.query, matches, model=args.model)
    except OllamaError as exc:
        print(f"warning: {exc}", file=sys.stderr)
        print("warning: using retrieval-only fallback; no model answer was generated.", file=sys.stderr)
        print(format_retrieval_answer(args.query, matches))
        return 0

    if is_refusal(answer):
        print(format_insufficient_evidence_refusal(args.query))
        return 0

    print(format_grounded_answer(args.query, answer, matches, model=args.model))
    return 0


def handle_evaluate(args: argparse.Namespace) -> int:
    if not 1 <= args.top_k <= 10:
        print("error: --top-k must be between 1 and 10", file=sys.stderr)
        return 2
    index_path = Path(args.index)
    cases_path = Path(args.cases)
    if not index_path.exists():
        print(f"error: index does not exist: {index_path}. Run private-ai ingest first.", file=sys.stderr)
        return 2
    if not cases_path.exists():
        print(f"error: evaluation cases do not exist: {cases_path}.", file=sys.stderr)
        return 2
    report = evaluate_index(index_path, cases_path, top_k=args.top_k)
    print(report.to_text())
    return 0 if report.ok else 1


def handle_architect(args: argparse.Namespace) -> int:
    values: dict[str, object] = {}
    if args.answers_file:
        values.update(load_answers_file(Path(args.answers_file)))

    for field in (
        "journey",
        "project_name",
        "owner_name",
        "architect_location",
        "runtime_location",
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
    ):
        value = getattr(args, field)
        if value is not None:
            values[field] = value

    if args.non_interactive or args.answers_file:
        if not values.get("journey"):
            raise ValueError("--journey is required in non-interactive mode")
        answers = architect_answers_from_mapping(values)
    else:
        answers = _prompt_for_architect_answers(values)

    result = generate_architect_pack(
        Path(args.output_dir),
        answers,
        force=args.force,
    )
    print("Generated guided architecture pack")
    print(f"Journey: {answers.journey}")
    print(f"Output: {result.output_dir}")
    for filename in result.generated_files:
        print(f"- {filename}")
    print("")
    print(result.validation.to_text())
    print("")
    print(f"Next: private-ai blueprint validate {result.output_dir}")
    print("No infrastructure changes were performed.")
    return 0


def handle_blueprint_validate(args: argparse.Namespace) -> int:
    requested_path = Path(args.path)
    blueprint_path = requested_path / "blueprint.json" if requested_path.is_dir() else requested_path
    blueprint = load_blueprint(requested_path)
    result = validate_blueprint(blueprint, path=blueprint_path)
    print(result.to_text())
    return 0 if result.ok else 1


def handle_modes(args: argparse.Namespace) -> int:
    for mode, profile in sorted(DEPLOYMENT_PROFILES.items()):
        print(f"{mode}: {profile.title}")
        print(f"  Audience: {profile.audience}")
        print(f"  Runtime: {profile.default_runtime}")
        print(f"  Vector DB: {profile.default_vector_db}")
    return 0


def handle_not_implemented(args: argparse.Namespace) -> int:
    print(
        f"`private-ai {args.command}` is intentionally not implemented yet. "
        "The project currently supports guided architecture planning, dry-run generation, "
        "validation, bounded local indexing, retrieval evaluation, and optional local "
        "Ollama-backed chat."
    )
    return 2


def _answers_from_args(args: argparse.Namespace):
    mode = normalize_mode(args.mode)
    return default_answers(
        mode=mode,
        project_name=args.project_name,
        company_name=args.company_name,
        departments=tuple(args.departments) if args.departments else None,
        allowed_data_sources=tuple(args.data_sources) if args.data_sources else None,
    )


def _prompt_for_answers(args: argparse.Namespace):
    print("Private AI dry-run wizard. Press Enter to accept defaults.")
    mode = _ask("Mode", args.mode)
    normalized_mode = normalize_mode(mode)
    project_name = _ask("Project name", args.project_name)
    company_name = _ask("Company or workspace name", args.company_name)
    departments = _split_csv(_ask("Departments", ",".join(args.departments or ["engineering", "security"])))
    data_sources = _split_csv(
        _ask("Approved data sources", ",".join(args.data_sources or ["./examples/sample-company-docs"]))
    )
    return default_answers(
        mode=normalized_mode,
        project_name=project_name,
        company_name=company_name,
        departments=tuple(departments),
        allowed_data_sources=tuple(data_sources),
    )


def _prompt_for_architect_answers(initial: dict[str, object]):
    print("Private AI guided architect. Press Enter to accept each displayed default.")
    print("Planning only: this command never deploys, discovers cloud resources, or reads document sources.")

    journey = _ask("Journey (local-rag, private-gpu, cloud-migration)", str(initial.get("journey") or "local-rag"))
    normalized_journey = architect_answers_from_mapping(
        {"journey": journey}
    ).journey
    network_default = "localhost" if normalized_journey == "local-rag" else "private-network"
    runtime_default = "same-machine" if normalized_journey == "local-rag" else "unknown"

    values: dict[str, object] = {
        "journey": normalized_journey,
        "project_name": _ask("Project name", str(initial.get("project_name") or "private-ai-plan")),
        "owner_name": _ask("Company or accountable owner", str(initial.get("owner_name") or "unknown")),
        "architect_location": _ask(
            f"Architect CLI location ({', '.join(ARCHITECT_LOCATIONS)})",
            str(initial.get("architect_location") or "developer-workstation"),
        ),
        "runtime_location": _ask(
            f"Target runtime location ({', '.join(RUNTIME_LOCATIONS)})",
            str(initial.get("runtime_location") or runtime_default),
        ),
        "data_location": _ask(
            "Data residency for storage and processing",
            str(initial.get("data_location") or "unknown"),
        ),
        "allowed_document_sources": _split_csv(
            _ask(
                "Approved document source labels or paths (not read)",
                _join_answer_list(initial.get("allowed_document_sources")),
            )
        ),
        "user_count": _ask("Expected user count", str(initial.get("user_count") or "unknown")),
        "model_preference": _ask("Model preference", str(initial.get("model_preference") or "unknown")),
        "runtime_preference": _ask("Runtime preference", str(initial.get("runtime_preference") or "unknown")),
        "hardware_availability": _ask(
            "Hardware availability",
            str(initial.get("hardware_availability") or "unknown"),
        ),
        "network_exposure": _ask(
            f"Network exposure ({', '.join(NETWORK_EXPOSURES)})",
            str(initial.get("network_exposure") or network_default),
        ),
        "compliance_concerns": _split_csv(
            _ask(
                "Compliance concerns (use 'none' when reviewed)",
                _join_answer_list(initial.get("compliance_concerns")),
            )
        ),
        "authentication_rbac_needs": _ask(
            "Authentication and RBAC needs",
            str(initial.get("authentication_rbac_needs") or "unknown"),
        ),
        "audit_logging_needs": _ask(
            "Audit and logging needs",
            str(initial.get("audit_logging_needs") or "unknown"),
        ),
        "data_owner_approval": _ask(
            f"Data owner approval ({', '.join(DATA_OWNER_APPROVALS)})",
            str(initial.get("data_owner_approval") or "unknown"),
        ),
    }

    if normalized_journey == "private-gpu":
        values["target_hardware"] = _ask(
            "Private GPU target hardware",
            str(initial.get("target_hardware") or "unknown"),
        )
        values["deployment_stage"] = _ask(
            f"Deployment stage ({', '.join(DEPLOYMENT_STAGES)})",
            str(initial.get("deployment_stage") or "unknown"),
        )
    elif normalized_journey == "cloud-migration":
        values["source_provider"] = _ask(
            "Source cloud provider",
            str(initial.get("source_provider") or "unknown"),
        )
        values["source_workload"] = _ask(
            "Source AI workload",
            str(initial.get("source_workload") or "unknown"),
        )
        values["rollback_requirement"] = _ask(
            "Rollback requirement",
            str(initial.get("rollback_requirement") or "unknown"),
        )

    return architect_answers_from_mapping(values)


def _ask(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _join_answer_list(value: object) -> str:
    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)
    if isinstance(value, str):
        return value
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
