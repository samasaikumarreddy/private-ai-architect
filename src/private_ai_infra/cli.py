from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .doctor import run_doctor
from .generator import generate_dry_run
from .models import DEPLOYMENT_PROFILES, default_answers, normalize_mode
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
    init_parser.set_defaults(handler=handle_init)

    validate_parser = subparsers.add_parser("validate", help="Validate generated dry-run artifacts.")
    validate_parser.add_argument("path", nargs="?", default="generated/dry-run", help="Dry-run artifact directory.")
    validate_parser.set_defaults(handler=handle_validate)

    doctor_parser = subparsers.add_parser("doctor", help="Inspect local readiness for future deployment work.")
    doctor_parser.set_defaults(handler=handle_doctor)

    for command in ("apply", "ingest", "chat", "audit"):
        stub = subparsers.add_parser(command, help=f"{command} is planned but not implemented yet.")
        stub.set_defaults(handler=handle_not_implemented)

    return parser


def handle_init(args: argparse.Namespace) -> int:
    if not args.dry_run:
        print("Only dry-run init is implemented in v0.1. Use: private-ai init --dry-run")
        return 2

    mode = normalize_mode(args.mode)
    answers = default_answers(
        mode=mode,
        project_name=args.project_name,
        company_name=args.company_name,
        departments=tuple(args.departments) if args.departments else None,
        allowed_data_sources=tuple(args.data_sources) if args.data_sources else None,
    )
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


def handle_not_implemented(args: argparse.Namespace) -> int:
    print(
        f"`private-ai {args.command}` is intentionally not implemented yet. "
        "The project currently supports dry-run planning and validation."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

