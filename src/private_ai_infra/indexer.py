from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Iterator


INDEX_SCHEMA_VERSION = 2
DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_FILES = 10_000
DOCUMENT_EXTENSIONS = {".md", ".txt", ".log", ".yaml", ".yml", ".json"}
SOURCE_CODE_EXTENSIONS = {
    ".c",
    ".cpp",
    ".cs",
    ".dart",
    ".go",
    ".gradle",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".php",
    ".ps1",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".xml",
}
SUPPORTED_EXTENSIONS = DOCUMENT_EXTENSIONS | SOURCE_CODE_EXTENSIONS
DENIED_DIRECTORY_NAMES = {
    ".git",
    ".gradle",
    ".idea",
    ".kotlin",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "packages",
    "pods",
    "target",
    "third_party",
    "tmp",
    "vendor",
    "venv",
}
DENIED_PATTERNS = (
    ".env",
    ".env.*",
    "*.der",
    "*.jks",
    "*.keystore",
    "*.mobileprovision",
    "*.p12",
    "*.pfx",
    "*.pem",
    "*.key",
    "google-services.json",
    "id_rsa",
    "id_ed25519",
    "local.properties",
    "package-lock.json",
    "pnpm-lock.yaml",
    "credentials*",
    "secrets*",
    "*token*",
)


@dataclass(frozen=True)
class IngestResult:
    index_path: Path
    files_indexed: int
    chunks_indexed: int
    skipped_files: tuple[str, ...]

    def to_text(self) -> str:
        lines = [
            f"Index path: {self.index_path}",
            f"Files indexed: {self.files_indexed}",
            f"Chunks indexed: {self.chunks_indexed}",
            "",
            "Skipped files:",
        ]
        lines.extend(f"- {item}" for item in self.skipped_files) if self.skipped_files else lines.append("- None")
        return "\n".join(lines)


def build_index(
    sources: list[Path],
    *,
    output_dir: Path,
    collection: str,
    force: bool = False,
    chunk_chars: int = 1200,
    overlap_chars: int = 120,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
    exclude_patterns: tuple[str, ...] = (),
) -> IngestResult:
    if max_file_bytes <= 0:
        raise ValueError("max_file_bytes must be greater than zero.")
    if max_files <= 0:
        raise ValueError("max_files must be greater than zero.")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.json"
    if index_path.exists() and not force:
        raise FileExistsError(f"index already exists: {index_path}. Use --force to overwrite it.")

    entries: list[dict[str, object]] = []
    skipped: list[str] = []
    indexed_files = 0

    for file_path, traversal_reason in _iter_source_files(
        sources,
        exclude_patterns=exclude_patterns,
        output_dir=output_dir,
    ):
        if indexed_files >= max_files:
            skipped.append(f"index file limit reached: {max_files}")
            break
        reason = traversal_reason or _skip_reason(file_path, max_file_bytes=max_file_bytes)
        if not reason and _is_within(file_path, output_dir):
            reason = "generated output directory"
        if reason:
            skipped.append(f"{file_path}: {reason}")
            continue

        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            detail = exc.strerror or type(exc).__name__
            skipped.append(f"{file_path}: could not read file ({detail})")
            continue
        chunks = _chunk_text(text, chunk_chars=chunk_chars, overlap_chars=overlap_chars)
        if not chunks:
            skipped.append(f"{file_path}: empty file")
            continue

        indexed_files += 1
        for chunk_index, chunk in enumerate(chunks):
            tokens = _tokenize(chunk)
            entries.append(
                {
                    "id": _chunk_id(file_path, chunk_index, chunk),
                    "collection": collection,
                    "source_path": str(file_path),
                    "source_name": file_path.name,
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "terms": sorted(set(tokens)),
                    "term_frequencies": dict(sorted(Counter(tokens).items())),
                    "token_count": len(tokens),
                }
            )

    payload = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "collection": collection,
        "sources": [str(source) for source in sources],
        "exclude_patterns": list(exclude_patterns),
        "max_file_bytes": max_file_bytes,
        "max_files": max_files,
        "files_indexed": indexed_files,
        "chunks_indexed": len(entries),
        "skipped_files": skipped,
        "entries": entries,
    }
    index_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    return IngestResult(
        index_path=index_path,
        files_indexed=indexed_files,
        chunks_indexed=len(entries),
        skipped_files=tuple(skipped),
    )


def _iter_source_files(
    sources: list[Path],
    *,
    exclude_patterns: tuple[str, ...],
    output_dir: Path,
) -> Iterator[tuple[Path, str | None]]:
    for source in sources:
        absolute = Path(os.path.abspath(source))
        source_root = absolute if absolute.is_dir() else absolute.parent
        if _is_within(absolute, output_dir):
            yield absolute, "generated output directory"
        elif _matches_user_exclusion(absolute, source_root, exclude_patterns):
            yield absolute, "user exclusion pattern"
        elif absolute.is_symlink():
            yield absolute, "symbolic links are not followed"
        elif absolute.is_file():
            yield absolute, None
        elif absolute.is_dir():
            denied_reason = _denied_directory_reason(absolute)
            if denied_reason:
                yield absolute, denied_reason
                continue
            for root, directory_names, file_names in os.walk(absolute, topdown=True, followlinks=False):
                root_path = Path(root)
                allowed_directories: list[str] = []
                for name in sorted(directory_names):
                    directory_path = root_path / name
                    reason = (
                        "generated output directory"
                        if _is_within(directory_path, output_dir)
                        else "symbolic links are not followed"
                        if directory_path.is_symlink()
                        else _denied_directory_reason(directory_path)
                    )
                    if not reason and _matches_user_exclusion(directory_path, source_root, exclude_patterns):
                        reason = "user exclusion pattern"
                    if reason:
                        yield directory_path, reason
                    else:
                        allowed_directories.append(name)
                directory_names[:] = allowed_directories
                for name in sorted(file_names):
                    file_path = root_path / name
                    reason = (
                        "generated output directory"
                        if _is_within(file_path, output_dir)
                        else "user exclusion pattern"
                        if _matches_user_exclusion(file_path, source_root, exclude_patterns)
                        else None
                    )
                    yield file_path, reason
        else:
            yield absolute, None


def _skip_reason(file_path: Path, *, max_file_bytes: int) -> str | None:
    if file_path.is_symlink():
        return "symbolic links are not followed"
    if not file_path.exists():
        return "source does not exist"
    for part in file_path.parts:
        for pattern in DENIED_PATTERNS:
            if fnmatch.fnmatch(part.lower(), pattern.lower()):
                return f"denied pattern {pattern}"
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return f"unsupported extension {file_path.suffix or '<none>'}"
    try:
        file_size = file_path.stat().st_size
    except OSError as exc:
        detail = exc.strerror or type(exc).__name__
        return f"could not inspect file ({detail})"
    if file_size > max_file_bytes:
        return f"file exceeds {max_file_bytes} byte limit"
    return None


def _denied_directory_reason(path: Path) -> str | None:
    if path.name.lower() in DENIED_DIRECTORY_NAMES:
        return f"denied directory {path.name}"
    return None


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory)
    except ValueError:
        return False
    return True


def _matches_user_exclusion(path: Path, source_root: Path, patterns: tuple[str, ...]) -> bool:
    if not patterns:
        return False
    try:
        relative = path.relative_to(source_root).as_posix()
    except ValueError:
        relative = path.name
    parts = tuple(part.lower() for part in Path(relative).parts)
    for raw_pattern in patterns:
        pattern = raw_pattern.strip().replace("\\", "/").strip("/")
        if not pattern:
            continue
        lowered = pattern.lower()
        if "/" in lowered:
            prefix = lowered.removesuffix("/**").rstrip("/")
            if fnmatch.fnmatch(relative.lower(), lowered) or relative.lower() == prefix:
                return True
            if prefix and relative.lower().startswith(f"{prefix}/"):
                return True
        elif any(fnmatch.fnmatch(part, lowered) for part in parts):
            return True
    return False


def _chunk_text(text: str, *, chunk_chars: int, overlap_chars: int) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    if not normalized:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_chars, len(normalized))
        chunks.append(normalized[start:end].strip())
        if end == len(normalized):
            break
        start = max(end - overlap_chars, start + 1)
    return chunks


def _chunk_id(path: Path, chunk_index: int, text: str) -> str:
    digest = hashlib.sha256(f"{path}:{chunk_index}:{text}".encode("utf-8")).hexdigest()[:16]
    return f"chunk-{digest}"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())
