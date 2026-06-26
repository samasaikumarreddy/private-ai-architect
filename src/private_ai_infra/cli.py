from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .doctor import run_doctor
from .generator import generate_dry_run
from .indexer import build_index
from .models import DEPLOYMENT_PROFILES, default_answers, normalize_mode
from .retrieval import format_retrieval_answer, search_index
from .validator import validate_dry_run


def main(argv: list[str] | None = None) -> int:
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="private-ai",
        description="Plan private AI infrastructure with dry-run safety.",
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
    ingest_parser.add_argument("--force", action="store_true", help="Overwrite an existing local index.")
    ingest_parser.set_defaults(handler=handle_ingest)

    chat_parser = subparsers.add_parser("chat", help="Run retrieval-only query over a local index.")
    chat_parser.add_argument("query", nargs="?", help="Question or search query.")
    chat_parser.add_argument("--index", default="generated/index/index.json", help="Path to local JSON index.")
    chat_parser.add_argument("--top-k", type=int, default=3, help="Number of cited excerpts to return.")
    chat_parser.set_defaults(handler=handle_chat)

    for command in ("apply", "audit"):
        stub = subparsers.add_parser(command, help=f"{command} is planned but not implemented yet.")
        stub.set_defaults(handler=handle_not_implemented)

    return parser


def handle_init(args: argparse.Namespace) -> int:
    if not args.dry_run:
        print("Only dry-run init is implemented in v0.1. Use: private-ai init --dry-run")
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
    )
    print(result.to_text())
    print("")
    print(f"Next: private-ai chat \"your question\" --index {result.index_path}")
    return 0


def handle_chat(args: argparse.Namespace) -> int:
    if not args.query:
        print("error: query is required for retrieval-only chat", file=sys.stderr)
        return 2
    index_path = Path(args.index)
    if not index_path.exists():
        print(f"error: index does not exist: {index_path}. Run private-ai ingest first.", file=sys.stderr)
        return 2
    matches = search_index(index_path, args.query, top_k=args.top_k)
    print(format_retrieval_answer(args.query, matches))
    return 0


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
        "The project currently supports dry-run planning, validation, and retrieval-only local preview."
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


def _ask(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
