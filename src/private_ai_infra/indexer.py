from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
from pathlib import Path
import re


SUPPORTED_EXTENSIONS = {".md", ".txt", ".log", ".yaml", ".yml", ".json"}
DENIED_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
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
) -> IngestResult:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.json"
    if index_path.exists() and not force:
        raise FileExistsError(f"index already exists: {index_path}. Use --force to overwrite it.")

    entries: list[dict[str, object]] = []
    skipped: list[str] = []
    indexed_files = 0

    for file_path in _iter_source_files(sources):
        reason = _skip_reason(file_path)
        if reason:
            skipped.append(f"{file_path}: {reason}")
            continue

        text = file_path.read_text(encoding="utf-8", errors="replace")
        chunks = _chunk_text(text, chunk_chars=chunk_chars, overlap_chars=overlap_chars)
        if not chunks:
            skipped.append(f"{file_path}: empty file")
            continue

        indexed_files += 1
        for chunk_index, chunk in enumerate(chunks):
            entries.append(
                {
                    "id": _chunk_id(file_path, chunk_index, chunk),
                    "collection": collection,
                    "source_path": str(file_path),
                    "source_name": file_path.name,
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "terms": sorted(set(_tokenize(chunk))),
                }
            )

    payload = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "collection": collection,
        "sources": [str(source) for source in sources],
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


def _iter_source_files(sources: list[Path]):
    for source in sources:
        resolved = source.resolve()
        if resolved.is_file():
            yield resolved
        elif resolved.is_dir():
            for file_path in sorted(resolved.rglob("*")):
                if file_path.is_file():
                    yield file_path
        else:
            yield resolved


def _skip_reason(file_path: Path) -> str | None:
    if not file_path.exists():
        return "source does not exist"
    for part in file_path.parts:
        for pattern in DENIED_PATTERNS:
            if fnmatch.fnmatch(part.lower(), pattern.lower()):
                return f"denied pattern {pattern}"
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return f"unsupported extension {file_path.suffix or '<none>'}"
    return None


def _chunk_text(text: str, *, chunk_chars: int, overlap_chars: int) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
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
